#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Custom error handler for workflow based on Custodian
Author: Dorothea Fennell
Changelog:
    3-26-26: Created, comments added. 
    3-27-26: Wrote correct method, updated errors to check for, updated run 
    3-30-26: Removed eddrmm error, updated to actually write new INCAR file. 
"""
#import modules
import os
import shutil
import subprocess as sp
from typing import ClassVar
from pymatgen.io.vasp.inputs import Incar
from .check_contcar import check_contcar
#def functions
def copy_contcar(dirname):
    """Copies CONTCAR to POSCAR to continue calculation."""
    if os.path.exists(f'{dirname}/CONTCAR'):
        with open(f'{dirname}/CONTCAR','r') as c:
            clines = c.readlines()
            if len(clines) >0:
                check_contcar(dirname)
                shutil.copy(os.path.join(dirname,'CONTCAR'),os.path.join(dirname,'POSCAR'))
#def class
class ErrorHandler:
    '''
    Custom VASP error handler based on Custodian's version. This version is significantly stripped down, as Custodian tends to overcorrect. The error handler also checks the SLURM output files. 
    '''
    vasp_msgs: ClassVar = {
        "tet": ["Tetrahedron method fails","tetrahedron method fails","Routine TETIRR needs special values","Tetrahedron method fails (number of k-points < 4)",],
        "ksymm": ["Fatal error detecting k-mesh","Fatal error: unable to match k-point",],
        "inv_rot_mat": ["rotation matrix was not found (increase SYMPREC)"],
        "brions": ["BRIONS problems: POTIM should be increased"],
        "pricel": ["internal error in subroutine PRICEL"],
        "zbrent": ["ZBRENT: fatal internal in", "ZBRENT: fatal error in bracketing","ZBRENT: fatal error: bracketing interval incorrect"],
        "pssyevx": ["ERROR in subspace rotation PSSYEVX"],
        "pdsyevx": ["ERROR in subspace rotation PDSYEVX"],
        "edddav": ["Error EDDDAV: Call to ZHEGV failed"],
        "zheev": ["ERROR EDDIAG: Call to routine ZHEEV failed!"],
        "eddiag": ["ERROR in EDDIAG: call to ZHEEV/ZHEEVX/DSYEV/DSYEVX failed"],
        "rhosyg": ["RHOSYG"],
        "posmap": ["POSMAP"],
        "point_group": ["group operation missing"],
        "pricelv": ["PRICELV: current lattice and primitive lattice are incommensurate"],
        "symprec_noise": ["determination of the symmetry of your systems shows a strong"],
        "bravais": ["Inconsistent Bravais lattice"],
        "hnform": ["HNFORM: k-point generating"],
        "set_core_wf": ["internal error in SET_CORE_WF"],
        "read_error": ["Error reading item", "Error code was IERR= 5"],
        "ibzkpt": ["not all point group operations"],
        "fexcf": ["supplied exchange-correlation table"],
        "spin_polarized_harris": ["Spin polarized Harris functional dynamics is a good joke"],
        }
    
    slurm_msgs: ClassVar = {
        "timeout": "DUE TO TIME LIMIT",
        "cancelled": "CANCELLED",
        }
    
    def __init__(self):
        '''
        Initialize error handler.
        '''
        self.output_file = 'OUTCAR'
        self.vasp_errors = dict(ErrorHandler.vasp_msgs)
        self.slurm_errors = dict(ErrorHandler.slurm_msgs)
        self.error_code = 'Exited with exit code'
        self.errors: set[str] = set()
    
    def check(self,dirname = "./"):
        '''Checks for errors in OUTCAR and checks SLURM output file.'''
        #get files
        slurm_files=[]
        for file in os.listdir(dirname):
            if file.startswith('slurm-'):
                slurm_files.append(os.path.join(dirname,file))

        if not slurm_files:
            return
        
        slurm_files.sort()
        latest_file = slurm_files[-1]
        
        self.errors = set()
        #check slurm output
        with open(latest_file,'r') as sfile:
            stext = sfile.read()
            
            #err check
            for err,msg in self.slurm_errors.items():
                if stext.find(msg) != -1:
                    if err == "cancelled" and "timeout" in self.errors:
                        continue
                    else:
                        self.errors.add(err)
        
        #check vasp output file
        with open(os.path.join(dirname,self.output_file),'rt') as file:
            text = file.read()
            
            #check for vasp errors
            for err in self.vasp_errors:
                for msg in self.vasp_errors[err]:
                    if text.find(msg) != -1:
                        self.errors.add(err)
                    
        #checks for slurm exiting with exit code 1 (vasp error not caught above)
        if not self.errors:
            if stext.find(self.error_code) != -1:
                self.errors.add('error_code')
                
        #check if calc is still running
        filename = os.path.basename(latest_file)
        jid = filename.split('-')[1].split('.')[0]
        try:
            codes = sp.check_output(['sacct','-n','-j',f'{jid}','-o','State'],stderr=sp.DEVNULL,text=True)
        except:
            pass
        
        if codes:
            state = codes.split('\n')[0].strip()
            if state.lower() == 'running':
                self.running = True
                print(f'Calculation in {dirname} still running.')
            elif state.lower() == 'pending':
                self.pending = True
                print(f'Calculation in {dirname} is pending.')
            else:
                self.running = False
                self.pending = False
        else:
            self.running = False
            self.pending = False
    
        #return
        return len(self.errors) >0
    
    def correct(self,dirname = "./"):
        "Corrects errors."
        #get 
        try:
            incar = Incar.from_file(f'{dirname}/INCAR').as_dict()
        except:
            print('Error reading INCAR. Skipping...')
            return
        #define set of errors where CONTCAR is copied to POSCAR
        copied = {'brions', 'edddav', 'zheev', 'eddiag','zbrent','fexcf','timeout','cancelled'}
        
        #copy contcar
        if self.errors & copied:
            copy_contcar(dirname)
        
        if self.errors & {'fexcf','zbrent'}:
            #best fix is to copy CONTCAR to POSCAR and restart calculation
            pass
        
        if 'brions' in self.errors:
            #increase POTIM by 0.1
            potim = (incar.get('POTIM',0.5)+0.1)
            incar.update({'POTIM':potim})
        
        if self.errors & {'eddiag','zheev','edddav','pssyevx', 'pdsyevx'}:
            #set algo to normal
            if incar.get('ALGO','Normal').lower() != 'normal':
                incar.update({'ALGO':'Normal'})
            elif incar.get('ALGO','Normal').lower() == 'normal':
                if 'edddav' in self.errors:
                    #remove CHGCAR
                    if os.path.exists(f'{dirname}/CHGCAR'):
                        try:
                            os.remove(f'{dirname}/CHGCAR')
                        except:
                            pass
        
        if self.errors & {'bravais','ksymm','posmap','pricelv','rhosyg','pricel','int_rot_mat','symprec_noise'}:
            #adjust symprec
            symprec = incar.get('SYMPREC',1e-5)
            #pricel & int_rot_mat
            if self.errors & {'pricel','int_rot_mat'} and symprec > 1e-8:
                incar.update({'SYMPREC':1e-8})
                if 'pricel' in self.errors:
                    incar.update({'ISYM':0})
            #symprec noise
            elif "symprec_noise" in self.errors:
                if symprec > 1e-6:
                    incar.update({'SYMPREC':1e-6})
                else:
                    incar.update({'ISYM':0})
            #rhosyg
            elif "rhosyg" in self.errors:
                if symprec < 1e-4:
                    incar.update({'SYMPREC':1e-4})
                else:
                    incar.update({'ISYM':0})
            #bravais,ksymm,posmap & pricelv
            else:
                if symprec < 1e-6:
                    incar.update({'SYMPREC':1e-6})
                elif symprec < 1e-4:
                    if self.errors & {'posmap','pricelv'}:
                        #for pricelv see https://www.vasp.at/forum/viewtopic.php?p=25608
                        if symprec < 1e-5:
                            #increase symprec by two orders of magnitude. 
                            incar.update({'SYMPREC':float(f'{symprec*100:.1e}')})
                        elif symprec >= 1e-5:
                            #decrease by an order of magnitude.
                            incar.update({'SYMPREC':float(f'{symprec/10:.1e}')})
                    else:
                        #for bravais & ksymm See https://www.vasp.at/forum/viewtopic.php?f=3&t=19109
                        #increase by an order of magnitude
                        incar.update({'SYMPREC':float(f'{symprec*10:.1e}')})
                else:
                    # if symprec >= 1e-4
                    incar.update({'ISYM':0})
        
        if self.errors & {'ibzkpt','hnform','point_group'}:
            #for ibzkpt see https://www.vasp.at/forum/viewtopic.php?p=24485
            if incar.get('ISYM',2) > 0:
                incar.update({'ISYM':0})
            elif 'ibzkpt' in self.errors and incar.get('SYMPREC',1e-5) > 1e-6:
                incar.update({'SYMPREC':1e-6})
                
        if "tet" in self.errors:
            incar.update({'ISMEAR':0,'SIGMA':0.05})
        
        #write new incar
        new_incar = Incar.from_dict(incar)
        new_incar.write_file(f'{dirname}/INCAR')
        #print errors to terminal
        for err in self.errors:
            #set messages
            if err in ['fexcf','zbrent']:
                fix_msg = 'CONTCAR copied to POSCAR'
            elif err in ['eddiag','zheev','edddav','pssyevx', 'pdsyevx']:
                fix_msg = 'ALGO set to Normal'
            elif err in ['bravais','ksymm','posmap','pricelv','rhosyg','pricel','int_rot_mat','symprec_noise']:
                fix_msg = 'SYMPREC adjusted and/or ISYM set to 0'
            elif err in ['ibzkpt','hnform','point_group']:
                fix_msg = 'ISYM set to 0'
            elif err == 'brions':
                fix_msg = 'POTIM increased by 0.1'
            elif err == 'tet':
                fix_msg = 'ISMEAR set to 0 and SIGMA set to 0.05'
            elif err == 'spin_polarized_harris':
                fix_msg = 'Calculation cannot be run with current parameters and must be fixed by hand. Try setting NSW = 0.'
            elif err == 'read_error':
                fix_msg = 'VASP cannot read one of the input files. Must be fixed by hand.'
            elif err == 'set_core_wf':
                fix_msg = 'Try a newer version of POTCAR to resolve.'
            
            #print errors
            if err == 'timeout':
                print(f'Error: Calculation in {dirname} timed out. CONTCAR copied to POSCAR and calculation ready to be resubmitted.')
            elif err == 'cancelled':
                print(f'Error: Calculation in {dirname} cancelled. CONTCAR copied to POSCAR and calculation ready to be resubmitted.')
            elif err == 'error_code':
                print(f'Error: Slurm output file in {dirname} shows calculation exited with error code. Check VASP output file for more info.')
            elif err in ['spin_polarized_harris','read_error','set_core_wf']:
                print(f'Error: {err} in {dirname}. {fix_msg}')
            else:
                print(f'Error: {err} in {dirname}. {fix_msg} and calculation ready to be resubmitted.')
            
    def submit(self,dirname = "./"):
        '''Submits corrected calculations'''
        #check if submission script is there
        if os.path.exists(os.path.join(dirname,'vasp.sh')):
            pass
        else:
            filedir = os.path.expanduser('~/wf-user-files')
            fullpath = os.path.join(filedir, 'vasp.sh')
            shutil.copy(fullpath, dirname)
        
        if not self.errors & {'spin_polarized_harris','read_error','set_core_wf','error_code'}:
            print(f'Submitting calculation in {dirname}...')
            wd = os.getcwd()
            os.chdir(dirname)
            sp.run(['sbatch','vasp.sh'], check=True)
            os.chdir(wd)
