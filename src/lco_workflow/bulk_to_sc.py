#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create supercell given bulk structure
Author: Dorothea Fennell
Changelog:
    6-10-26: File created, comments added.
    6-11-26: Converted script to functions for workflow implementation.
    6-12-26: Rewrote functions to work for more crystal structures, added functions to pull from Mat. Proj API, rewrote layer check, changed write spin pairs. 
    6-15-26: Wrote user input section.
"""
#import
import os
import sys
import dotenv
import numpy as np
from ase.io import write
from ase.build import cut,stack,add_vacuum
from ase.build.tools import IncompatibleCellError
from ase.geometry import get_layers
from pymatgen.core.structure import Structure
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
from pymatgen.ext.matproj import MPRester

#define functions
def check_input(user_input):
    if user_input.lower() == 'exit':
        print('Exiting...')
        sys.exit()

def z_coord(site):
    en = site.species.average_electroneg
    z = site.coords[2]
    return (en,z)

def set_mp_api():
    '''If MP API key can't be found, sets it in an dotenv env variable.'''
    pkgdir = sys.modules['lco_workflow'].__path__[0]
    print('Please input your Materials Project API key or type "exit" to quit.')
    api = input('Key:')
    check_input(api)
    dotenv.set_key(os.path.join(pkgdir,'.env'),'MP_API', api)
    
def get_from_mp(mp_id):
    '''Gets pymatgen Structure object directly from the Materials Project. Requires API key and material id.'''
    dotenv.load_dotenv()
    api_key = os.getenv('MP_API')
    if api_key == None:
        print('API key not found.')
        set_mp_api()
        dotenv.load_dotenv()
        print('Reloaded environment variables.')
        api_key = os.getenv('MP_API')
        if api_key == None:
            print('API key not found after reloading. Try setting explicitly using "export".')
            print('Exiting...')
            sys.exit()
    else:
        mpi = MPRester(os.getenv('MP_API'))
        struc = mpi.get_structure_by_material_id(mp_id)
        return struc

def get_idx_pairs(eq_idxs):
    '''Gets list of inversion symmetric index pairs.'''
    #pair off indices
    idx_pairs = []
    for eq in eq_idxs:
        #get number of values in set
        n = len(eq)
        if n % 2 != 0:
            print('Odd number of sites in set. Sites will be paired with the exception of the middle site.')
            h = n // 2
            for i in range(h):
                idx_pairs.append([eq[i],eq[-i-1]])
            #append middle site
            idx_pairs.append([eq[h]])
        #pair values
        else:
            for i in range(int(n/2)):
                idx_pairs.append([eq[i],eq[-i-1]])
    return idx_pairs

def chk_layers(struc,miller):
    '''Checks if top & bottom layers of the structure are inversion symmetric.'''
    cell = struc.to_ase_atoms()
    #get number of layers
    layer_idx,layer_dist = get_layers(cell, miller)
    #check if top & bottom layer are the same element
    #get top layer index, we know bottom layer is 0
    l_max = layer_idx.max()
    #get distance of top layer from origin
    max_dist = layer_dist[l_max]
    #get list of periodic sites for top & bottom layers
    layer1 = []
    layer2 = []
    for s in struc.sites:
        x,y,z = s.coords
        if z == float(0):
            layer1.append(s)
        elif z == max_dist:
            layer2.append(s)
    spg_ops = SpacegroupAnalyzer(struc).get_space_group_operations()
    sym = spg_ops.are_symmetrically_equivalent(layer1, layer2)
    if sym == False:
        layer = cut(cell,nlayers=1,tolerance=0.001)
        try:
            new_cell = stack(cell,layer)
        except IncompatibleCellError:
            print('Error raised. A layer of atoms added to the structure to keep inversion symmetry is incompatible with the current cell.')
            print('If the layer is added, structure may be overly strained. If the layer is not added, structure may not be inversion symmetric.')
            print("Would you like to add the layer? Please answer 'yes' or 'no', or 'exit' if you'd like to quit.")
            add_layer = input()
            check_input(add_layer)
            if add_layer.lower() == 'yes':
                new_cell = stack(cell,layer,maxstrain=None)
            elif add_layer.lower() == 'no':
                new_cell = cell
        new_struc = Structure.from_ase_atoms(new_cell)
        return new_struc
    elif sym == True:
        return
    
def get_supercell(bulk,sc_size,miller):
    '''Generates supercell based on user input and bulk structure.'''
    #read in file or pull from materials project
    if os.path.exists(bulk):
        struc = Structure.from_file(bulk)
    elif bulk.startswith('mp-'):
        struc = get_from_mp(bulk)
    else:
        print('Bulk structure not found, either as file or on the Materials Project. Please try again. \nExiting...')
        sys.exit()
    
    #get refined structure
    ref_struc = SpacegroupAnalyzer(struc).get_refined_structure()
    #make supercell
    cell = ref_struc.make_supercell(sc_size,in_place=False)
    #check layers
    chk = chk_layers(cell,miller)
    if chk != None:
        cell = chk
    #get sites
    sites = cell.sites
    #sort structure by layer
    cell.sort(key=z_coord)
    #get symmetrized structure
    spga = SpacegroupAnalyzer(cell)
    sym_cell = spga.get_symmetrized_structure()
    eq_idxs = sym_cell.equivalent_indices
    #get idx pairs
    idx_pairs = get_idx_pairs(eq_idxs)
    #reorder sites
    site_list = []
    for [i,j] in idx_pairs:
        site_list.append(sites[i])
        site_list.append(sites[j])
    #create reordered cell
    reordered_cell = Structure.from_sites(site_list)
    return reordered_cell

def get_slab(reordered_cell,vacuum):
    '''Gets slab from reordered cell & writes POSCAR file.'''
    ase_cell = reordered_cell.to_ase_atoms()
    add_vacuum(ase_cell,vacuum)
    formula = ase_cell.get_chemical_formula(empirical=True)
    filename = f'{formula}-slab.vasp'
    write(filename,ase_cell,format='vasp')
    return filename

def write_spin_pairs(base_dir,reordered_cell):
    '''Writes spin pairs file given organized structure. NOTE: Only writes the indices of the pairs, does not assign spin states.'''
    sites = reordered_cell.sites
    #get indices of non-alkali & non-alkaline metals
    indices = []
    for i,s in enumerate(sites):
        if s.specie.is_metal == True:
            if s.specie.is_alkali == False and s.specie.is_alkaline == False:
                indices.append(i)
    
    #get spin pairs
    spin_pairs = [(indices[i], indices[i + 1]) for i in range(0, len(indices), 2)] if len(indices) % 2 == 0 else []
    
    #check spin pairs isn't empty
    if not spin_pairs:
        print('Odd number of metals, cannot write create SpinPairs file.')
        return
    
    with open(f'{base_dir}/SpinPairs.txt','w') as f:
        f.writelines(spin_pairs)

def create_structure(bulk=None,sc_size=None,miller=None,vacuum=10):
    '''Generates surface structure based on bulk structure and user input. Bulk structure can be given as a file or as a Materials Project ID. Note: If using Materials Project, an API key MUST be provided. User input can be provided either through input prompts or using command line options.'''
    print('\nIf you would like to exit at any point, type "exit" into any input prompt.')
    base_dir = os.getcwd()
    
    #check if bulk file/ID has been given
    if bulk == None:
        print('\nPlease provide a filepath (relative or absolute) or Materials Project ID for the bulk structure. Material IDs should start with "mp-".')
        bulk = input('Filepath or ID:')
        check_input(bulk)
    
    #check if sc_size has been given
    if sc_size == None:
        print('\nPlease provide the size of the desired supercell.The size can be provided as a full set of lattice vectors or as a list of scaling factors.')
        print('If inputing vectors, please provide a comma-separated list of vectors, with each vector in brackets. eg. [2,1,0],[0,2,0],[0,0,1].')
        print('If inputing scaling factors, please input as a comma-separated list. eg. a,b,c. ')
        #wrap input prompt in a while loop so it can repeat
        while True:
            sc = input('Supercell size:')
            check_input(sc)
            #check length of input to determine 
            sc = sc.strip()
            #if len = 5, it's a list of scaling factors
            if len(sc) == 5:
                sc_size = sc.split(',')
                break
            elif len(sc) == 23:
                sc = sc.strip('[]')
                sc_ls = sc.split('],[')
                vecs = []
                for l in sc_ls:
                    ls = l.split(',')
                    v = [(int(x)) for x in ls]
                    vecs.append(v)
                sc_size = np.fromiter(vecs,dtype=np.dtype((int,3)))
                break
            else:
                print("Given input doesn't match required parameters. Please try again.")
        
    #check for miller index
    if miller == None:
        print("Please provide the Miller index of the cell as a comma-separated list of 3 values. If no input is provided or input isn't a list, index will default to (001).")
        ml_str = input('Miller index:')
        check_input(ml_str)
        if len(ml_str) == 0:
            miller = (0,0,1)
        elif len(ml_str) == 5:
            miller = tuple(int(x) for x in ml_str.split(','))
        else:
            miller = (0,0,1)
    
    #now that all the params are set, build the supercell
    reordered_cell = get_supercell(bulk,sc_size,miller)
    filename = get_slab(reordered_cell, vacuum)
    
    #write spin pairs
    write_spin_pairs(base_dir, reordered_cell)
    #print output
    print(f'POSCAR file {filename} and SpinPairs.txt file created. NOTE: Spin states (up,down) must be assigned by hand!')






