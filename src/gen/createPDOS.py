"""
Create directories and copy files for PDOS calculations
Author: Dorothea Fennell
Changelog: 
    4-23-25: Created, comments added 
    4-30-25: Changed POSCAR to CONTCAR and added a couple lines to rename CONTCAR to POSCAR in new PDOS dir.
    5-7-25: Added ability to set up pdos for pristine or vacancy structures based on user input
    6-2025: Modified to generalize script.
    6-25-25: Modified to pull PDOS_INCAR.txt from user directory
"""

#import modules
import os
import shutil


def copy_vasp_files(source_dir, dest_dir):
    """Copies essential VASP input files from source to destination."""
    os.makedirs(dest_dir, exist_ok=True)  # Ensure the target directory exists
    # List of files to copy
    FILES_TO_COPY = ["INCAR", "KPOINTS", "POTCAR", "CONTCAR"]
    for file in FILES_TO_COPY:
        src_file = os.path.join(source_dir, file)
        dest_file = os.path.join(dest_dir, file)
        if os.path.exists(src_file):
            shutil.copy2(src_file, dest_file)
            print(f"Copied {file} to {dest_dir}")
        else:
            print(f"Warning: {file} not found in {source_dir}, skipping.")
        
def create_pdos(input_dir,base_directory):
    '''Creates PDOS directory and copies files to new directory. '''         
    print(f"\nProcessing: {input_dir}")
    
    #create directories for PDOS
    output_dir = os.path.join(input_dir, "PDOS")
    os.makedirs(output_dir, exist_ok=True)
    
    # Copy required VASP files
    copy_vasp_files(input_dir, output_dir)
    
    #Rename CONTCAR to POSCAR
    if os.path.exists(f'{input_dir}/PDOS/CONTCAR'):
        os.rename(f'{input_dir}/PDOS/CONTCAR',f'{input_dir}/PDOS/POSCAR')
    
    #Copy PDOS_INCAR.txt file - has to be separate as it is not in Modification_# dir
    #copy from package to base dir
    userdir = os.path.expanduser('~/wf-user-files')
    fullpath = os.path.join(userdir, 'PDOS_INCAR.txt')
    shutil.copy(fullpath, base_directory)
    #copy from base dir to mod dir
    for file in os.listdir(base_directory):
        if file == "PDOS_INCAR.txt":
            src_file = os.path.join(base_directory, file)
            dest_file = os.path.join(output_dir, file)
            shutil.copy2(src_file, dest_file)
            
def process_vasp_inputs(base_directory):
    """Processes all VASP_inputs directories recursively, applying the same modifications to each."""
    input_dirs = []
    #ask user if they would like to remove pairs from one structure or do separate structures
    print('\nWould you like to create PDOS for pristine or vacancy structures?')
    print('1: Pristine')
    print('2: Vacancy')
    input_choice = input("Enter the number of your choice: ")
    # Collect all VASP_inputs directories
    for root, dirs, files in os.walk(base_directory):
        if input_choice == '1':
            if root.endswith("VASP_inputs") and "CONTCAR" in files:
                input_dirs.append(root)
        elif input_choice == '2':
            if root.endswith("_Removed") and "CONTCAR" in files:
                input_dirs.append(root)
    
    if not input_dirs:
        print("No input directories found. Have you run the initial calculations?")
        return

    # Apply the same modifications to all VASP_inputs directories
    for input_dir in input_dirs:
        create_pdos(input_dir, base_directory)

