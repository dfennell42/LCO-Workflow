"""
Update command for workflow
Author: Dorothea Fennell
Changelog: 
    8-6-25: Created, comments added.
"""
#import modules
from . import version
import os
import shutil
import subprocess as sp
#define functions
def get_new_vrsn():
    '''Gets version of whl file in WF-Files.'''
    dirname = '/hpcgpfs01/scratch/dfennell/WF-Files'
    whl_files = []
    for root, dirs, files in os.walk(dirname):
        for file in files:
            if file.endswith('.whl'):
                whl_files.append(file)
   
    if not whl_files:
        print('No .whl files found.')
        return 
    
    whl_files.sort()
    latest_file = whl_files[-1]
    vname = latest_file.split('-')[1]
    return vname, latest_file

def check_vrsn():
    '''checks current version vs WF-Files. Installs new version if necessary.'''
    current_vrsn = version
    new_vrsn, latest_file = get_new_vrsn()
    if current_vrsn == new_vrsn:
        print('Workflow is up to date!')
        return
    elif current_vrsn != new_vrsn:
        input_dir = os.path.join('/hpcgpfs01/scratch/dfennell/WF-Files',latest_file)
        output_dir = os.path.expanduser('~/')
        shutil.copy(input_dir,output_dir)
        os.chdir(output_dir)
        sp.check_call(['pip','install',f'{latest_file}'])
