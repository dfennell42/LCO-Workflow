#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix CONTCAR issue with broken symmetry.
Author: Dorothea Fennell
Changelog:
    2-27-26: Created, comments added
"""
#define functions
def get_lines(mod_dir,file):
    '''Gets file and returns list of lines.'''
    with open(f'{mod_dir}/{file}','r') as f:
        lines = f.readlines()    
    return lines

def fix_contcar(clines,plines):
    '''Replaces bad CONTCAR lines with lines from POSCAR'''
    new_lines=[]
    bad_idx = [5,6,7,8]
    for i,line in enumerate(clines):
        if i not in bad_idx:
            new_lines.append(line)
        elif i == 5:
            new_lines.append(plines[5])
        elif i == 7:
            new_lines.append(plines[6])
        elif i == 6 or i == 8:
            pass
    return new_lines

def check_contcar(mod_dir):
    #get CONTCAR
    clines = get_lines(mod_dir,'CONTCAR')
    #get POSCAR
    plines = get_lines(mod_dir,'POSCAR')
    
    #check CONTCAR
    if clines[6].isnumeric():
        return
    else:
        new_lines = fix_contcar(clines, plines)
        with open(f'{mod_dir}/CONTCAR','w') as f:
            f.writelines(new_lines)
