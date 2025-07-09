"""
Error checker
Author: Dorothea Fennell
Changelog:
    7-2-25: Created, comments added
    7-7-25: Fixed time_chk so it only checks most recent slurm output
"""
#import modules
import os
from custodian.vasp.handlers import VaspErrorHandler
import shutil
import subprocess as sp

#define functions
def find_files(base_dir):
    """
    Recursively find output files """
    matched_files = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file =='vasp.out':
                matched_files.append(os.path.join(root, file))
    return matched_files

def del_backups(output_file):
    '''Get rid of backup tar.gz files because ther's no option to turn backups off.'''
    dirname = os.path.dirname(output_file)
    for file in os.listdir(dirname):
        if file.startswith('error') and file.endswith('.tar.gz'):
            os.remove(os.path.join(dirname,file))

def time_chk(output_file):
    '''Checks if calculations timed out.'''
    dirname = os.path.dirname(output_file)
    msg = 'DUE TO TIME LIMIT'
    slurm_files=[]
    #create list of all slurm outputs
    for file in os.listdir(dirname):
        if file.startswith('slurm-'):
            slurm_files.append(os.path.join(dirname,file))
    #sort files in ascending order
    slurm_files.sort()
    #open most recent file
    latest_file = slurm_files[-1]
    with open(latest_file,'r') as sfile:
        text = sfile.read()
        if text.find(msg) != -1:
            return True
        else:
            return False
    
def continue_calc(file):
    """Copies CONTCAR to POSCAR to continue calculation."""
    dirname = os.path.dirname(file)
    if os.path.exists(f'{dirname}/CONTCAR'):
        os.rename(f'{dirname}/CONTCAR',f'{dirname}/POSCAR')
    else:
        print(f'CONTCAR not found in {dirname}.')
        
def fix_sym(file):
    """Appends ISYM = -1 to INCAR"""
    dirname = os.path.dirname(file)
    with open(os.path.join(dirname,"INCAR"),'a') as incar:
        incar.write('\nISYM = -1')

def submit_calcs(file):
    '''Submits corrected calculations'''
    dirname = os.path.dirname(file)
    #check if submission script is there
    if os.path.exists(os.path.join(dirname,'vasp.sh')):
        pass
    else:
        filedir = os.path.expanduser('~/wf-user-files')
        fullpath = os.path.join(filedir, 'vasp.sh')
        shutil.copy(fullpath, dirname)
    
    vasppath = os.path.join(dirname,'vasp.sh')
    print(f'Submitting calculation in f{dirname}...')
    sp.run(['sbatch',f'{vasppath}'], check=True)
    
def err_fix(base_dir):
    """ Fixes errors if possible or prints error if not."""
    #gets error files
    output_files = find_files(base_dir)
    err_files = []
    timeout_msg = {'errors':['timeout'],'actions':None}
    for file in output_files:
        handler = VaspErrorHandler(file)
        err_chk = handler.check(os.path.dirname(file))
        t_chk = time_chk(file)
        if err_chk == True:
            msg = handler.correct(os.path.dirname(file))
            del_backups(file)
            err_files.append((file,msg))
        if t_chk == True:
            err_files.append((file,timeout_msg))
    
    if not err_files:
        print('No errors found. All calculations complete.')
    
    #fix errors
    for file,msg in err_files:
        dirname = os.path.dirname(file)
        err_msgs = msg.get('errors')
        fixable =['pricelv','zbrent','fexcf','timeout']
        for err in err_msgs:
            if err in fixable:
                if err =='pricelv':
                    fix_sym(file)
                elif err =='zbrent':
                    continue_calc(file)
                elif err == 'fexcf':
                    continue_calc(file)
                elif err =='timeout':
                    continue_calc(file)
                submit_calcs(file)
            else:
                print(f'Error: {err} for calculation in {dirname}. Must be fixed by hand.')
        
#run in terminal
#if __name__ == "__main__":
   # base_dir = os.getcwd()
   # err_fix(base_dir)