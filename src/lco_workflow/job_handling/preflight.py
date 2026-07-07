#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Runs pre-calculation checks and verifies input files. 
Author: Dorothea Fennell
Changelog:
    6-23-26: File created, comments added
    6-24-26: Command finished, added Rich for printing.
"""
#import modules
import os
import warnings
import pandas as pd
from rich import print as rprint
from pymatgen.io.vasp.inputs import Poscar, Incar, Kpoints, Potcar
from tabulate import TableFormat,Line,DataRow
#def functions
def get_dirs(base_dir):
    '''Gets list of calculation directories.'''
    calc_dirs = []
    for root, dirs, files in os.walk(base_dir):
        dir_names = ('VASP_inputs','_Added','_Removed','PDOS')
        if root.endswith((dir_names)):
            calc_dirs.append(root)
    return calc_dirs

def check_inputs(base_dir,calc_dir):
    '''Checks VASP input files.'''
    calc_name = calc_dir.replace(f'{base_dir}','.')
    err_list = []
    #check POSCAR
    try:
        poscar = Poscar.from_file(f'{calc_dir}/POSCAR')
    except Exception as e:
        if type(e) == ValueError and str(e).startswith('default_names'):
            err_list.append({'Calc Dir':calc_name,'File':'POTCAR','Error':"Species in POSCAR & POTCAR don't match"})
        else:
            err_list.append({'Calc Dir':calc_name,'File':'POSCAR','Error':e.args[1]})
    
    #check incar
    try:
        incar = Incar.from_file(f'{calc_dir}/INCAR')
    except Exception as e:
        err_list.append({'Calc Dir':calc_name,'File':'INCAR','Error':e.args[1]})
    else:
        with warnings.catch_warnings(record=True) as w:
            incar.check_params()
        incar_errs = [i.message.args[0] for i in w]
        if len(incar_errs) >0:
            err_list.append({'Calc Dir':calc_name,'File':'INCAR','Error':f'Parameter Error(s):{incar_errs}'})
    
    #check POTCAR
    try:
        potcar = Potcar.from_file(f'{calc_dir}/POTCAR')
    except Exception as e:
        err_list.append({'Calc Dir':calc_name,'File':'POTCAR','Error':e.args[1]})
                
    #check KPOINTS
    try:
        kpoints = Kpoints.from_file(f'{calc_dir}/KPOINTS')
    except Exception as e:
        err_list.append({'Calc Dir':calc_name,'File':'KPOINTS','Error':e.args[1]})
    
    #dict to series
    err_ser = pd.DataFrame(err_list)
    return err_ser

def print_preflight():
    '''Gets dirs, checks input and prints any errors to command line.'''
    base_dir = os.getcwd()
    #get dirs
    calc_dirs = get_dirs(base_dir)
    def sort_dirs(data):
        path_list = data.split('/')
        for p in path_list:
            if p.startswith('Modification_'):
                num = p.split('_')[1]
                return int(num)
    calc_dirs.sort(key=sort_dirs)
    #get errors
    err_list = []
    for calc in calc_dirs:
        err_ser = check_inputs(base_dir, calc)
        #check to make sure series isn't empty
        if not err_ser.empty:
            err_list.append(err_ser)
    #check if list is empty
    if not err_list:
        rprint('[green]Preflight check passed! Calculations are ready to submit.[/green]')
        return
    #convert to df
    df = pd.concat(err_list)
    #custom table format
    table = TableFormat(
        lineabove=Line("", "", "", ""),
        linebelowheader=Line("", "─", "┼", ""),
        linebetweenrows=None,
        linebelow=None,
        headerrow=DataRow("", "│", ""),
        datarow=DataRow("", "│", ""),
        padding=2,
        with_header_hide=None,
        )
    rprint('\n[red1]Preflight check failed. Please fix following errors before submitting.[/]')
    print(df.to_markdown(index=False,tablefmt=table))
    
    