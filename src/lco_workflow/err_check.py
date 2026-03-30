"""
Error checker
Author: Dorothea Fennell
Changelog:
    7-2-25: Created, comments added
    7-7-25: Fixed time_chk so it only checks most recent slurm output
    2-27-26: Updated to include checking CONTCAR file for correct structure.
    3-17-26: Added additional ZBRENT error message that Custodian wasn't catching.
    3-27-26: Rewrote completely to use new custom error handler.
"""
#import modules
import os
from .err_handler import ErrorHandler

#define functions
def find_files(base_dir):
    """
    Recursively find output files """
    matched_files = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file =='OUTCAR':
                matched_files.append(os.path.join(root, file))
    return matched_files
   
def err_fix(base_dir,no_submit=False):
    """ Fixes errors if possible or prints error if not."""
    #gets error files
    output_files = find_files(base_dir)
    err_files = []
    #set up error handler
    handler = ErrorHandler()
    for file in output_files:
        dirname = os.path.dirname(file)
        err_chk = handler.check(dirname)
        if err_chk == True:
            handler.correct(dirname)
            err_files.append(file)
            if no_submit == False:
                handler.submit(dirname)
            
    if not err_files:
        print('No errors found. All calculations complete.')
        return
            
    if len(err_files) >0 and no_submit == True:
        print('Errors fixed, but calculations not submitted.')
