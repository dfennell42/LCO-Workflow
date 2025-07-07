"""
Get total energy of pristine structures
Author: Dorothea Fennell
Changelog:
    5-14-25: Created, comments added.
"""
#import modules
import os
import sys
#define functions
def read_file(r_dir, file):
    '''Reads given file in directory and returns list of lines'''
    F = open(os.path.join(r_dir,file),'r')
    lines = F.readlines()
    F.close
    return lines

def get_e(e_dir):
    '''Gets final energy from OUTCAR file.'''
    if 'OUTCAR' in os.listdir(e_dir):
        lines = read_file(e_dir,'OUTCAR')
        toten = []
        for l in lines:
            if "TOTEN" in l:
                toten.append(l)
        e = toten[-1].split()
        e = float(e[4])
        return e

def get_all_e(base_dir):
    '''Gets total energy of pristine surfaces.Returns file of pristine energies.'''
    #Checks for existing E_pristine.csv 
    if 'E_pristine.csv' in os.listdir(base_dir):
        print('E_pristine.csv already exists.')
        sys.exit()
    
    mod_dirs = []
    for root, dirs, files in os.walk(base_dir):
        if os.path.basename(root).startswith('Modification_'):
            mod_dirs.append(root)
    mod_dirs.sort()
    if not mod_dirs:
        print('No modification directories found.')
        return
    
    mods = read_file(base_dir, 'Mods.txt')
    #convert the commas to dashes so the csv won't separate incorrectly
    mods_str = []
    for m in mods:
        ml= m.strip('\n').split(',')
        ms = ''
        for i in ml:
            ms += f'{i}-'
        mods_str.append(ms)
    mods = mods_str
    #get total energy of pristine surface
    e_list = []
    for mod_dir in mod_dirs:
        p = os.path.join(mod_dir,'VASP_inputs/')
        e_p = get_e(p)
        mod_name = os.path.basename(mod_dir)
        for i, mod in enumerate(mods,1):
            if f'Modification_{i}' == f'{mod_name}':
                mod = mod.strip('-')
                e_list.append(f'\n{mod_name},{mod},{e_p}')
    
    #check there are values in e_list
    if e_list == None:
        print('No values found. Exiting...')
        sys.exit()
    
    #write file
    with open(f'{base_dir}/E_pristine.csv','w',encoding=None) as f:
        f.write('Mod dir,Mod,Total E')
        f.writelines(e_list)
        f.close

