#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sets up band structure calculations
Author: Dorothea Fennell
Changelog: 
    2-6-26: Created, comments added.
"""
#import modules
from pymatgen.io.vasp import Kpoints, Incar 
from pymatgen.core.structure import Structure
from pymatgen.symmetry.bandstructure import HighSymmKpath
import os
import shutil

#define functions
def gen_inputs(band_dir, band_params, k):
    '''Generates input files for band structure calculations.'''
    #get structure & incar
    struc = Structure.from_file(f'{band_dir}/POSCAR')
    incar = Incar.from_file(f'{band_dir}/INCAR')
    
    #update incar
    incar.update(band_params)
    
    #create kpoints_opt file
    hsk = HighSymmKpath(struc)
    kp = Kpoints.automatic_linemode(int(k), hsk)
    
    #write files
    incar.write_file(f'{band_dir}/INCAR')
    kp.write_file(f'{band_dir}/KPOINTS_OPT')
    

def get_incar_params():
    '''Gets custom incar parameters from wf-user-files directory'''
    userdir = os.path.expanduser('~/wf-user-files')
    param_file = os.path.join(userdir,'bands_incar_params.txt')
    bands_incar_params = {}
    with open(param_file, 'r') as file:
        for line in file:
            key, value = line.strip().split('=', 1)
            bands_incar_params[key.strip()] = value.strip()
    return bands_incar_params

def copy_vasp_files(source_dir, dest_dir):
    """Copies essential VASP input files from source to destination."""
    os.makedirs(dest_dir, exist_ok=True)  # Ensure the target directory exists
    #list of files to copy
    FILES_TO_COPY = ["KPOINTS", "POTCAR", "CONTCAR","WAVECAR"]
    for file in FILES_TO_COPY:
        src_file = os.path.join(source_dir, file)
        dest_file = os.path.join(dest_dir, file)
        if os.path.exists(src_file):
            shutil.copy2(src_file, dest_file)
            print(f"Copied {file} to {dest_dir}")
        else:
            print(f"Warning: {file} not found in {source_dir}, skipping.")

def create_bands(input_dir,base_dir,band_params,k):
    '''Creates directory for band structure calculations and copies files.'''
    #make dirs
    output_dir = os.path.join(input_dir,'Band_struc')
    os.makedirs(output_dir, exist_ok=True)
    
    # Copy required VASP files
    copy_vasp_files(input_dir, output_dir)
    
    #Rename CONTCAR to POSCAR
    if os.path.exists(f'{input_dir}/PDOS/CONTCAR'):
        os.rename(f'{input_dir}/PDOS/CONTCAR',f'{input_dir}/PDOS/POSCAR')
    
    #Check for ISYM
    with open(f'{input_dir}/INCAR','r') as f:
        incar_lines = f.readlines()
    
    for line in incar_lines:
        if line.strip().startswith('ISYM'):
            key, value = line.strip().split('=', 1)
            band_params[key.strip()] = value.strip()
    
    #Generate input files
    gen_inputs(output_dir, band_params, k)

def create_all_bands(base_dir, k):
    '''Processes all VASP_inputs dirs recursively.'''
    input_dirs = []
    #get input dirs
    for root, dirs, files in os.walk(base_dir):
        if root.endswith("VASP_inputs") and "WAVECAR" in files:
            if os.path.getsize(f'{root}/WAVECAR') != 0:
                input_dirs.append(root)
        
    if not input_dirs:
        print("No input directories found. Have you run the initial calculations?")
        return
    
    # Apply the same modifications to all VASP_inputs directories
    for input_dir in input_dirs:
        create_bands(input_dir, base_dir, k)
