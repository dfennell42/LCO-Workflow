#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Add single atoms while ignoring symmetry
Author: Dorothea Fennell
Changelog: 
    2-26-26: Created, comments added
    3-2-26: Added to delafossite wf
"""
#import modules
from ase.io import read, write
from ase.build import add_adsorbate, add_vacuum
import os
import shutil
import copy

#define functions
def copy_vasp_files(source_dir, dest_dir):
    """Copies essential VASP input files from source to destination."""
    os.makedirs(dest_dir, exist_ok=True)  # Ensure the target directory exists
    #list of files to copy
    FILES_TO_COPY = ["INCAR", "KPOINTS", "POTCAR"]
    for file in FILES_TO_COPY:
        src_file = os.path.join(source_dir, file)
        dest_file = os.path.join(dest_dir, file)
        if os.path.exists(src_file):
            shutil.copy2(src_file, dest_file)
            print(f"Copied {file} to {dest_dir}")
        else:
            print(f"Warning: {file} not found in {source_dir}, skipping.")

def get_indices(atoms, element):
    """Identifies atoms for a given element."""
    indices = [i for i, atom in enumerate(atoms) if atom.symbol == element]
    return [indices[i] for i in range(0, len(indices))]

def get_user_selection(indices, element_name):
    """Asks the user to select atoms to add atoms to."""
    print(f"\nAvailable {element_name} indices:")
    for idx in indices:
        print(f"{idx}")
    
    print('Please note, only one new atom is added to each site. If you would like to attach multiple new atoms to the same site, you must run this command multiple times.')
    sel_indices = input(f"Enter the indices of {element_name} atoms to attach the new atoms to (comma-separated): ")
    return [int(idx) for idx in sel_indices.split(',') if idx.isdigit()]

def add_atoms(atoms, indices, species, offset, selected_indices):
    '''Adds new atoms to the structure.'''
    #create structure to be modified and add vacuum to allow for new atoms
    mod_atoms = copy.deepcopy(atoms)
    add_vacuum(mod_atoms,2)
    
    #set offset
    ols = offset.split(',')
    offtup = tuple((float(ols[0]),float(ols[1])))

    #center atoms about 0 to determine the height from the surface
    mod_atoms.center(about=(0.,0.,0.,))
    #add adsorbate
    for idx in selected_indices:
        a = mod_atoms[idx]
        if a.z > 0:
            a_h = 2
        elif a.z < 0:
            a_h = -2
        add_adsorbate(mod_atoms,species,a_h,(a.x,a.y),offset=offtup)
    
    #recenter cell
    mod_atoms.center()
    
    return mod_atoms

def process_addition(vasp_dir, indices, species, offset, selected_indices):
    """Creates POSCAR files with added atoms, saves it, and copies it to new directory along with required files."""
    print(f"\nProcessing: {vasp_dir}")
    
    #get poscar
    poscar_path = os.path.join(vasp_dir, "POSCAR")
    atoms = read(poscar_path)
    #modify poscar
    mod_atoms = add_atoms(atoms,indices,species,offset, selected_indices)
    
    # Save the modified POSCAR
    output_dir = os.path.join(vasp_dir, f'{species}_Atoms_Added')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"POSCAR_added_{species}.vasp")
    write(output_file, mod_atoms, format="vasp")
    print(f"Saved modified POSCAR: {output_file}")

    # Copy the modified POSCAR as just "POSCAR" for VASP
    final_poscar_path = os.path.join(output_dir, "POSCAR")
    shutil.copy2(output_file, final_poscar_path)
    print(f"Copied {output_file} to {final_poscar_path} for VASP.")

    # Copy required VASP files
    copy_vasp_files(vasp_dir, output_dir)

def process_vasp_dirs_nosym(base_dir):
    """Processes all VASP_inputs directories recursively, applying the same modifications to each."""
    all_dirs = []

    # Collect all VASP_inputs directories
    for root, dirs, files in os.walk(base_dir):
        if "VASP_inputs" in root and "POSCAR" in files:
            all_dirs.append(root)

    if not all_dirs:
        print("No VASP_inputs directories found.")
        return
    
    #ask user which structures they want to add to
    print("\nWould you like to add atoms to pristine, vacancy, or adsorption structures?")
    print("1: Pristine")
    print("2: Vacancy")
    print("3: Adsorption")
    struc = input("Enter the number of your choice: ")
    vasp_dirs=[]
    
    for i in all_dirs:
        if struc == '1':
            if i.endswith('VASP_inputs'):
                vasp_dirs.append(i)
        elif struc == '2':
            if i.endswith('_Removed'):
                vasp_dirs.append(i)
        elif struc == '3':
            if i.endswith('_Added'):
                vasp_dirs.append(i)
                
    # Use the first POSCAR to get the pairs and user selection
    sample_poscar = os.path.join(base_dir, "POSCAR")
    atoms = read(sample_poscar)
    
    #Ask user which species they want to add relative to
    print("\nWhich element would you like to attach the new atoms to?")
    species_list = atoms.symbols.species()
    i = 1
    for element in species_list:
        print(f'{i}:{element}')
        i += 1
    choice = input("Enter the number of your choice: ")
    
    #Ask user which pairs they want to attach atoms to
    for i,element in enumerate(species_list,1):
        if float(choice) == i:
            element_name = element.split('_')[0].capitalize()
            indices = get_indices(atoms, element_name)
            selected_indices = get_user_selection(indices, element_name)
    
    #Ask user for species of new atoms
    print('\nWhat element would you like the new atoms to be?')
    species = input('Enter element symbol:').capitalize()
    
    #Ask user whether they want the atoms on top or offset
    print('\nPlease enter the X & Y offset for the new atoms, in number of unit cells. Default is 0,0. If entering an offset, please enter both numbers, even if one is zero.')
    offset = input('Enter the offset (comma separated): ')
    
    for vasp_dir in vasp_dirs:
        process_addition(vasp_dir, indices, species, offset, selected_indices)
   
    return element_name