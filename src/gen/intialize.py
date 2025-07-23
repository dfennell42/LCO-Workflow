"""
Script to set up directory of base files for workflow
Author: Dorothea Fennell
Changelog: 
    6-23-25: Created, comments added
"""
#import modules
import os
import shutil
import sys
#define functions
def copy_files(source_dir, dest_dir):
    """Copies files from source to destination."""
    os.makedirs(dest_dir, exist_ok=True)  # Ensure the target directory exists
    # List of files to copy
    FILES_TO_COPY = ["BulkE_dict.txt", "MagMom_dict.txt", "PDOS_INCAR.txt","custom_incar_params.txt"]
    for file in FILES_TO_COPY:
        src_file = os.path.join(source_dir, file)
        dest_file = os.path.join(dest_dir, file)
        if os.path.exists(src_file):
            shutil.copy2(src_file, dest_file)
            #print(f"Copied {file} to {dest_dir}")
        else:
            print(f"Warning: {file} not found in package, skipping.")

def make_wf_dir(source_dir):
    '''Makes directory with base files for workflow tools.'''
    wf_dir = 'wf-user-files'
    os.makedirs(wf_dir,exist_ok=True)
    
    #copy files
    copy_files(source_dir, wf_dir)
    ex_files = os.path.join(source_dir,'example_files')
    wf_ex = os.path.join(wf_dir,'example_files')
    shutil.copytree(ex_files,wf_ex)
def init_settings():
    '''Initialize settings and files'''
    #set up source dir
    pkgdir = sys.modules['delafossite_wf'].__path__[0]
    #get pseudo path
    print('\n Please input path to VASP psuedopotentials.')
    pot_path = input('Path:')
    #print info
    print('\nAll base files (POSCAR, SpinPairs.txt, vasp.sh, etc.) should be added to directory "~/wf-user-files".\nAny edits to these files should be done in that directory.')
    print('\nExample files can be found in ~/wf-user-files/example_files')
    #submission script
    print('\n\nPlease add your vasp submission script to directory ~/wf-user-files. Submission script MUST be titled "vasp.sh" or submit command will not work.')
    #incar params
    print('\n\nIf you would like to customize INCAR parameters for geometry optimization, please edit custom_incar_params.txt')
    print('\nIf you would like to customize INCAR parameters for PDOS calculations, please edit PDOS_INCAR.txt')
    print('Both files can be found in ~/wf-user-files')
    #make dir
    make_wf_dir(pkgdir)
    
    #return pseudo path
    return pot_path
    