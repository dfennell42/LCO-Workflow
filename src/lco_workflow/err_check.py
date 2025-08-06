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
    err_msg = 'Exited with exit code'
    canc_msg = 'CANCELLED'
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
            timeout = True
        else:
            timeout = False
        #check for other errors
        if text.find(err_msg) != -1:
            slurm_err = True
        else:
            slurm_err = False
        if text.find(canc_msg) != -1 and timeout == False:
            cancelled = True
        else:
            cancelled = False
    return timeout, slurm_err, cancelled

def continue_calc(file):
    """Copies CONTCAR to POSCAR to continue calculation."""
    dirname = os.path.dirname(file)
    if os.path.exists(f'{dirname}/CONTCAR'):
        with open(f'{dirname}/CONTCAR','r') as c:
            clines = c.readlines()
            if clines:
                shutil.copy(os.path.join(dirname,'CONTCAR'),os.path.join(dirname,'POSCAR'))
            elif not clines:
                print(f'CONTCAR in {dirname} empty. Skipping copying...')
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
    
    print(f'Submitting calculation in {dirname}...')
    wd = os.getcwd()
    os.chdir(dirname)
    sp.run(['sbatch','vasp.sh'], check=True)
    os.chdir(wd)
    
def err_fix(base_dir,submit=True):
    """ Fixes errors if possible or prints error if not."""
    #gets error files
    output_files = find_files(base_dir)
    err_files = []
    timeout_msg = {'errors':['timeout'],'actions':None}
    slurm_msg = {'errors':['slurm_error'],'actions':None}
    canc_msg = {'errors':['cancelled'],'actions':None}
    subset = list(VaspErrorHandler.error_msgs.keys())
    subset.remove('eddrmm')
    for file in output_files:
        handler = VaspErrorHandler(file, errors_subset_to_catch=subset)
        err_chk = handler.check(os.path.dirname(file))
        if err_chk == True:
            msg = handler.correct(os.path.dirname(file))
            del_backups(file)
            err_files.append((file,msg))
        elif err_chk != True:
            t_chk,slurm_chk,canc_chk = time_chk(file)
            if t_chk == True:
                err_files.append((file,timeout_msg))
            elif slurm_chk == True:
                err_files.append((file,slurm_msg))
            elif canc_chk == True:
                err_files.append((file,canc_msg))
    
    if not err_files:
        print('No errors found. All calculations complete.')
        return
    
    #fix errors
    for file,msg in err_files:
        dirname = os.path.dirname(file)
        err_msgs = msg.get('errors')
        fixable =['pricelv','zbrent','fexcf','timeout','slurm_error','cancelled']
        for err in err_msgs:
            if err in fixable:
                if err =='pricelv':
                    print(f'Error: {err} in {dirname}.')
                    fix_sym(file)
                elif err =='zbrent':
                    print(f'Error: {err} in {dirname}.')
                    continue_calc(file)
                elif err == 'fexcf':
                    print(f'Error: {err} in {dirname}.')
                    continue_calc(file)
                elif err =='timeout':
                    print(f'Error: Calculation in {dirname} timed out.')
                    continue_calc(file)
                elif err =='cancelled':
                    print(f'Error: Calculation in {dirname} cancelled.')
                    continue_calc(file)
                elif err == 'slurm_error':
                    print(f'Error: Slurm output file in {dirname} shows calculation exited with error code. Check output file for more info.')
            else:
                print(f'Error: {err} for calculation in {dirname}. Must be fixed by hand.')
        if submit == True:
            submit_calcs(file)
    if submit != True:
        print('Errors fixed if possible, but calculations not submitted.')
#run in terminal
#if __name__ == "__main__":
   # base_dir = os.getcwd()
   # err_fix(base_dir)