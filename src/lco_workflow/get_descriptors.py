"""
Extract electronic and structural decriptors for ML
Author: Dorothea Fennell
Changelog:
    7-9-25: Created, comments added
    7-11-25: Added funcs for electronegativity, band center, bond lengths and formation energy.
    7-14-25: Added funcs for t2g/e_g resolved dos and getting pdos data. Set most funcs to return pandas series and began extract.
    7-16-25: Finished extract function and finished script.
    8-20-25: Added function to extract ionization energy and polarizability. Added ability to get difference between O2p band center and conduction band minimum
"""
#import modules
from pymatgen.io.vasp import Vasprun
from pymatgen.electronic_structure.core import OrbitalType
import os
from ase.io import read
from ase.formula import Formula
import numpy as np
import pandas as pd
#define functions
def read_file(r_dir, file):
    '''Reads given file in directory and returns list of lines'''
    F = open(os.path.join(r_dir,file),'r')
    lines = F.readlines()
    F.close
    return lines

def sort_mods(data):
    num = data.split('_')[1]
    return int(num)

def get_dirs(base_dir):
    '''Gets list of PDOS directories.'''
    pdos_dirs=[]
    for root, dirs, files in os.walk(base_dir):
        if root.endswith("VASP_inputs/PDOS") and 'integrated-pdos.csv' in files:
            pdos_dirs.append(root)
        elif root.endswith("VASP_inputs/PDOS") and "integrated-pdos.csv" not in files:
            print("PDOS calculations haven't been integrated yet.")
    def sort_dirs(data):
        path_list = data.split('/')
        for p in path_list:
            if p.startswith('Modification_'):
                num = p.split('_')[1]
                return int(num)
    pdos_dirs.sort(key=sort_dirs)
    return pdos_dirs

def get_atoms(file):
    '''Determine atome indices'''
    #read file
    atoms = read(file)
    #get formula
    sym = atoms.get_chemical_formula()
    f = Formula(sym)
    atom_counts = f.count()
    #determine number of removed atoms
    if 'Li' in atom_counts.keys():
        li = 18 - atom_counts.get('Li')
    else:
        li = 18
    if 'O' in atom_counts.keys():
        o = 36 - atom_counts.get('O')
    else:
        o = 36
    atom_rem = li + o
    #determine indices
    o_idx = 43 - atom_rem
    m_idxs = [(21- atom_rem), (23- atom_rem), (25 - atom_rem)]
    
    return atoms, o_idx, m_idxs

def band_gap(vasprun):
    '''Gets the band gap for the vasprun.xml file.'''
    # Get band structure and band gap
    band_struc = vasprun.get_band_structure()
    band_gap = band_struc.get_band_gap()
    fermi = band_struc.efermi
    cbm = band_struc.get_cbm()['energy']
    vbm = band_struc.get_vbm()['energy']
    return band_gap['energy'],fermi,cbm,vbm

def get_form_en(vasprun):
    '''Computes energy of formation.'''
    # Reference energies in eV/atom
    ref_energies = {
        "O": -9.03 / 2,  # O2 molecule → per atom
        "Li": -1.9072204,
        "Ni": -5.469965403,
        "Mn": -8.998062074,
        "Co": -6.8377063,
        "Fe": -8.243958785,
        "Al": -3.764685413,
    }
    #read vasprun.xml, get final structure, energy & composition
    struc = vasprun.final_structure
    tot_en = vasprun.final_energy
    comp = struc.composition
    
    #get ref energy
    ref_energy = sum([amt * ref_energies[el.symbol] for el, amt in comp.items()])
    #get form energy
    form_en = tot_en - ref_energy
    return form_en

def get_band_center(vasprun,m_idxs,o_idx,cbm):
    '''Gets d_band centers from vasprun.xml'''
    #get structure
    struc = vasprun.final_structure
    all_sites = struc.sites
    #get dos
    dos = vasprun.complete_dos
    #get sites & band centers 
    band_centers = {}
    for i, site in enumerate(all_sites):
        if i in m_idxs:
            if site.label == 'Al':
                site_list=[site]
                bc = dos.get_band_center(band=OrbitalType(1),sites=site_list)
                bc_occ = dos.get_band_center(band=OrbitalType(1),sites=site_list,erange=(float('-inf'),0))
                bc_unocc = dos.get_band_center(band=OrbitalType(1),sites=site_list,erange=(0,float('inf')))
                band_width = dos.get_band_width(band=OrbitalType(1),sites=site_list)
                occ_bw = dos.get_band_width(band=OrbitalType(1),sites=site_list, erange=(float('-inf'),0))
                band_centers.update({f'{i}_bc_full':bc,f'{i}_bc_occ':bc_occ,f'{i}_bc_unocc':bc_unocc,f'{i}_band_width':band_width, f'{i}_occ_bw':occ_bw})
            else:
                site_list=[site]
                bc = dos.get_band_center(sites=site_list)
                bc_occ = dos.get_band_center(sites=site_list,erange=(float('-inf'),0))
                bc_unocc = dos.get_band_center(sites=site_list,erange=(0,float('inf')))
                band_width = dos.get_band_width(sites=site_list)
                occ_bw = dos.get_band_width(sites=site_list, erange=(float('-inf'),0))
                band_centers.update({f'{i}_bc_full':bc,f'{i}_bc_occ':bc_occ,f'{i}_bc_unocc':bc_unocc,f'{i}_band_width':band_width,f'{i}_occ_bw':occ_bw})
        if i == o_idx:
            site_list=[site]
            bc = dos.get_band_center(band=OrbitalType(1),sites=site_list)
            bc_occ = dos.get_band_center(band=OrbitalType(1),sites=site_list,erange=(float('-inf'),0))
            bc_unocc = dos.get_band_center(band=OrbitalType(1),sites=site_list,erange=(0,float('inf')))
            band_width = dos.get_band_width(band=OrbitalType(1),sites=site_list)
            occ_bw = dos.get_band_width(band=OrbitalType(1),sites=site_list, erange=(float('-inf'),0))
            bc_cbm_diff = cbm - bc
            band_centers.update({'O(p)_bc_full':bc,'O(p)_bc_occ':bc_occ,'O(p)_bc_unocc':bc_unocc, 'O(p)_cbm_diff':bc_cbm_diff,'O(p)_band_width':band_width, 'O(p)_occ_bw':occ_bw})
    #adding in covalent mixing term
    for num, i in enumerate(m_idxs,1):
        widths = band_centers[f'{i}_band_width']*band_centers['O(p)_band_width']
        width_term = np.sqrt(widths)
        bc_diff = band_centers[f'{i}_bc_full']-band_centers['O(p)_bc_full']
        bc_term = np.abs(bc_diff)
        mix_term = width_term / bc_term
        band_centers.update({f'O_M{num}_mix':mix_term})
    bc_ser = pd.Series(band_centers)
    return bc_ser

def get_eln(atoms, m_idxs):
    '''Gets electronegativity descriptors'''
    # Descriptor table (no d-electrons)
    metal_data = {
        'Li': {'Z': 3,  'chi': 0.98, 'radius': 1.28},
        'Al': {'Z': 13, 'chi': 1.61, 'radius': 1.21},
        'Mn': {'Z': 25, 'chi': 1.55, 'radius': 1.39},
        'Fe': {'Z': 26, 'chi': 1.83, 'radius': 1.32},
        'Co': {'Z': 27, 'chi': 1.88, 'radius': 1.26},
        'Ni': {'Z': 28, 'chi': 1.91, 'radius': 1.24}
    }
    #base variables
    chi_O = 3.44
    eln_data = {}
    eln_sum = 0
    #calculate delta chi
    for idx in m_idxs:
        symbol = atoms[idx].symbol
        props = metal_data[symbol]
        delta_chi = chi_O - props['chi']
        eln_data.update({f'{idx}_chi':delta_chi})
    
    #get string & sum
    for x in eln_data.values():
        eln_sum += float(x)
    #get average
    eln_avg = eln_sum/3
    eln_data.update({'sum_chi':eln_sum,'avg_chi':eln_avg})
    eln = pd.Series(eln_data)
    return eln

def bond_lengths(atoms, o_idx, m_idxs):
    '''Get bond lengths between oxygen and three bonded metals.'''
    bond_lengths = {}
    for i in m_idxs:
        dist = atoms.get_distance(o_idx, i, mic=False)
        bond_lengths.update({f'O_M{i}':dist})
    
    bl_sum = 0
    for i in bond_lengths.values():
        bl_sum += float(i)
    bl_avg = bl_sum/3
    bond_lengths.update({'BL_avg':bl_avg})
    bl_ser = pd.Series(bond_lengths)
    return bl_ser

def int_pdos(energy, up, down, num):
    """Integrates PDOS in specified windows."""
    #set up variables for next section
    up_e = 0.0
    down_e = 0.0
    tot_e = 0.0
    up_sum = 0.0
    down_sum = 0.0
    #integrate
    for x in range(len(energy)):
        if energy[x] > -2:
            up_sum += up[x]
            down_sum += down[x]
            
    for x in range(len(energy)):
        if energy[x] > -2 and energy[x] < 0:
            up_e += up[x]/up_sum * num
            down_e += down[x]/down_sum * num
            tot_e += up[x]/up_sum * num + down[x]/down_sum * num
        
    return tot_e

def t2g_eg_dos(vasprun,m_idxs):
    '''Gets site t2g & e_g projected DOS and integrates.'''
    #get data from vasprun
    struc = vasprun.final_structure
    all_sites = struc.sites
    dos = vasprun.complete_dos
    
    #set up list
    t2g_eg_dict ={}
    al_dict = {}
    #get dos data
    for i, site in enumerate(all_sites):
        if i in m_idxs:
            if site.label == 'Al':
                al_dict.update({f'{i}_t2g':0,f'{i}_eg':0})
            else: 
                bc = dos.get_site_t2g_eg_resolved_dos(site=site)
                t2g = bc['t2g'].as_dict()
                eg = bc['e_g'].as_dict()
                #integrate data
                t2g_en = np.subtract(t2g['energies'],t2g['efermi'])
                t2g_data = t2g['densities']
                eg_data = eg['densities']
                eg_en = np.subtract(eg['energies'],eg['efermi'])
                t2g_tot_e = int_pdos(t2g_en, t2g_data['1'], t2g_data['-1'],3)
                eg_tot_e = int_pdos(eg_en,eg_data['1'],eg_data['-1'],2)
                t2g_eg_dict.update({f'{i}_t2g':t2g_tot_e,f'{i}_eg':eg_tot_e})
    
    if len(t2g_eg_dict) < 6:
        t2g_eg_dict.update(al_dict)
    t2g_eg = pd.Series(t2g_eg_dict)
    return t2g_eg
    
def get_pdos_data(pdos_dir,m_idxs):
    '''Gets data from integrated-pdos.csv'''
    #read csv
    if os.path.exists(os.path.join(pdos_dir,'integrated-pdos.csv')): 
        df = pd.read_csv(os.path.join(pdos_dir,'integrated-pdos.csv'))
    else:
        print('PDOS not integrated. Please integrate data before continuing.')
        return
    #if atom index column not in df
    if 'Atom index' not in df.columns:
        elements = []
        idxs = []
        for atom in df['Atom']:
            index = ''
            for char in atom:
                if char.isdigit():
                    index +=f'{char}'
            ele = atom.strip('0123456789')
            elements.append(ele)
            idxs.append(float(index))
        df.insert(1,'Element',elements)
        df.insert(2,'Atom index',idxs)
    
    sel_df = df.query('`Atom index` in @m_idxs')      
    sel_sum = sel_df.sum(numeric_only=True)
    sums = df.sum(numeric_only=True) 
    elements = sel_df['Element']
    atomic_numbers = {
        'Al':13,
        'Mn':25,
        'Fe':26,
        'Co':27,
        'Ni':28
        }
    Z_sum=0
    #get 3Z
    for e in elements:
        if e in atomic_numbers.keys():
            Z_sum += atomic_numbers[f'{e}']
            
    #create series for 3z
    Z = pd.Series(data={'3Z':Z_sum})
    #drop unnecessary items
    sel_sum =sel_sum.drop(index=['Atom index','e_tot'])
    sums = sums.drop(index='Atom index')
    #reindex
    sel_sum = sel_sum.rename({'OS':'3OS','spin':'3S','H d/p':'3Hdp'})
    sums = sums.rename({'OS':'tot_OS','spin':'tot_S','H d/p':'tot_Hdp'})
    #concatenate pd Series
    pdos_data = pd.concat([sel_sum,Z,sums])
    return pdos_data

def get_ion_e_pol(vasprun,m_idxs):
    '''Gets first ionization energy and polarizability'''
    struc = vasprun.final_structure
    all_sites = struc.sites
    
    pol_dict={
        'Al':{'val':57.8, 'stddev':1.0},
        'Mn':{'val':68, 'stddev':9},
        'Fe':{'val':62, 'stddev':4},
        'Co':{'val':55, 'stddev':4},
        'Ni':{'val':49, 'stddev':3}
        }
    ion_pol_data = {}
    for i,site in enumerate(all_sites):
        if i in m_idxs:
            ele = site.specie
            ion_e = ele.ionization_energy
            if site.label in pol_dict.keys():
                pol_data = pol_dict[site.label]
                val = pol_data['val']
                stddev = pol_data['stddev']
                min_pol = val - stddev
                max_pol = val + stddev
            ion_pol_data.update({f'{i}_ion_e':ion_e,f'{i}_min_pol':min_pol,f'{i}_pol':val,f'{i}_max_pol':max_pol})
    ion_pol_ser = pd.Series(ion_pol_data)
    return ion_pol_ser
    
def extract_desc(base_dir):
    '''Extract descriptors.'''
    #get directories
    pdos_dirs = get_dirs(base_dir)
    
    if not pdos_dirs:
        print('No PDOS directories found. Exiting...')
        return
    
    #get modifications from ModsCo.txt
    if os.path.exists(os.path.join(base_dir,'ModsCo.txt')):
        mods = read_file(base_dir, 'ModsCo.txt')
        #convert the commas to dashes so the csv won't separate incorrectly
        mods_str = []
        for m in mods:
            ml= m.strip('\n').split(',')
            ms = ''
            for i in ml:
                ms += f'{i}-'
            ms = ms.strip('-')
            mods_str.append(ms)
        mods = mods_str
    else:
        #if no ModsCo.txt file, pulls mod dir names
        mods = []
        for root, dirs, files in os.walk(base_dir):
            if os.path.basename(root).startswith('Modification_'):
                mods.append(os.path.basename(root))
        mods.sort(key=sort_mods)
    
    mod_data_list = []
    for pdos_dir in pdos_dirs:
        for i, mod in enumerate(mods,1):
            if f'Modification_{i}/' in pdos_dir:
                opt_dir = os.path.dirname(pdos_dir)
                #get atoms and indices from CONTCAR
                atoms, o_idx, m_idxs = get_atoms(os.path.join(opt_dir,'CONTCAR'))
                #get integrated pdos data 
                pdos_data = get_pdos_data(pdos_dir, m_idxs)
                #get electronegativty data
                eln = get_eln(atoms,m_idxs)
                #get bond lengths
                bl_ser = bond_lengths(atoms, o_idx, m_idxs)
                #get vasprun for form energy, band gap, band center and t2g/eg dos
                #use optimization for form_en & band gap, pdos for band center & t2g/eg 
                opt_vpr = Vasprun(os.path.join(opt_dir,'vasprun.xml'))
                pdos_vpr = Vasprun(os.path.join(pdos_dir,'vasprun.xml'))
                #get formation energy
                form_en = get_form_en(opt_vpr)
                #get band gap & fermi energy
                bg_e,fermi,cbm,vbm = band_gap(pdos_vpr)
                #check cbm
                if cbm == None:
                    dos = pdos_vpr.complete_dos
                    fermi = dos.efermi
                    cbm,vbm = dos.get_cbm_vbm()
                #get band centers
                bc_ser = get_band_center(pdos_vpr, m_idxs,o_idx,cbm)
                #get t2g/eg dos
                t2g_eg = t2g_eg_dos(pdos_vpr, m_idxs)
                #get ionization e and polarizability
                ion_pol_ser = get_ion_e_pol(opt_vpr, m_idxs)
                #create pandas series with modification and single value returns
                e_ser = pd.Series(data={'Modification':mod,'E_form':form_en,'E_fermi':fermi,'E_bg':bg_e,'VBM':vbm,'CBM':cbm})
                #concatenate all series
                mod_ser = pd.concat([e_ser,pdos_data,bl_ser,eln,bc_ser,t2g_eg,ion_pol_ser])
                #append series to list
                mod_data_list.append(mod_ser)
    
    #create data frame from mod_data_list
    mod_data = pd.DataFrame(data=mod_data_list)
    #reindex dataframe to use modification
    mod_data = mod_data.set_index('Modification')
    #print data to csv
    mod_data.to_csv(os.path.join(base_dir,'descriptors.csv'))
    print('Descriptors extracted and descriptors.csv created.')
    
