#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Remove atoms while ignoring symmetry
Author: Dorothea Fennell
Changelog: 
    2-26-26: Created, comments added
    3-2-26: Modified for delafossite wf
"""
#import modules
import os
import shutil
import copy
from ase.io import read, write

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
    """Asks the user to select pairs for removal."""
    print(f"\nAvailable {element_name} indices:")
    for idx in indices:
        print(f"{idx}")

    indices_to_remove = input(f"Enter the indices of {element_name} atoms to remove (comma-separated): ")
    return [int(idx) for idx in indices_to_remove.split(',') if idx.isdigit()]

def remove_selected_atoms(atoms, indices,selected_indices):
    """Removes the selected pairs from the atom structure."""
    modified_atoms = copy.deepcopy(atoms)
    for idx in selected_indices:
        modified_atoms[idx].symbol = "X"  # Mark atoms for removal

    # Remove atoms marked for deletion
    return modified_atoms[[atom.symbol != "X" for atom in modified_atoms]]

def process_removal(vasp_dir,indices,selected_indices, element_name):
    """Creates POSCAR files with removed pairs, saves it, and copies it to new directory along with required files."""
    print(f"\nProcessing: {vasp_dir}")

    poscar_path = os.path.join(vasp_dir, "POSCAR")
    atoms = read(poscar_path)
    modified_atoms = remove_selected_atoms(atoms, indices, selected_indices)
    name = f'{element_name}_Atoms'

    # Save the modified POSCAR
    output_dir = os.path.join(vasp_dir, f'{name}_Removed')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"POSCAR_removed_{name}.vasp")
    write(output_file, modified_atoms, format="vasp")
    print(f"Saved modified POSCAR: {output_file}")

    # Copy the modified POSCAR as just "POSCAR" for VASP
    final_poscar_path = os.path.join(output_dir, "POSCAR")
    shutil.copy2(output_file, final_poscar_path)
    print(f"Copied {output_file} to {final_poscar_path} for VASP.")

    # Copy required VASP files
    copy_vasp_files(vasp_dir, output_dir)

def process_vasp_inputs_nosym(base_directory):
    """Processes all VASP_inputs directories recursively, applying the same modifications to each."""
    all_dirs = []

    # Collect all VASP_inputs directories
    for root, dirs, files in os.walk(base_directory):
        if "VASP_inputs" in root and "POSCAR" in files:
            all_dirs.append(root)

    if not all_dirs:
        print("No VASP_inputs directories found.")
        return
    
    #ask user which structures they want to add to
    print("\nWould you like to remove pairs from pristine, vacancy, or adsorption structures?")
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
    sample_poscar = os.path.join(vasp_dirs[0], "POSCAR")
    atoms = read(sample_poscar)
    
    print('Which species would you like to remove?')
    species_list = atoms.symbols.species()
    i = 1
    for element in species_list:
        print(f'{i}:{element}')
        i += 1
    choice = input("Enter the number of your choice: ")
    
    for i,element in enumerate(species_list,1):
        if float(choice) == i:
            element_name = element.split('_')[0].capitalize()
            indices = get_indices(atoms, element_name)
            selected_indices = get_user_selection(indices, element_name)
            
    # Apply the same modifications to all VASP_inputs directories
    for vasp_dir in vasp_dirs:
        process_removal(vasp_dir,indices,selected_indices,element_name)
    
    return choice

