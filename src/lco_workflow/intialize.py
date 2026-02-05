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
    FILES_TO_COPY = ["POSCAR", "SpinPairs.txt", "vasp.sh", "PDOS_INCAR.txt"]
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
    user_dir = os.path.expanduser('~/')
    wf_dir = f'{user_dir}/wf-user-files'
    os.makedirs(wf_dir,exist_ok=True)
    
    #copy files
    copy_files(source_dir, wf_dir)
    
def init_settings():
    '''Initialize settings and files'''
    #set up source dir
    pkgdir = sys.modules['lco_workflow'].__path__[0]
    #print info
    print('\n All base files (POSCAR, SpinPairs.txt, vasp.sh, etc.) should be added to directory "~/wf-user-files".\n Any edits to these files should be done in that directory.')
    #make dir
    make_wf_dir(pkgdir)