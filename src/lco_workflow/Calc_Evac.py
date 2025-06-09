"""
Calculate Evac O and Li
Author: Dorothea Fennell
Changelog: 
    5-2-25: Created, comments added 
    5-5-25: Finished functions to get all values of E, calculate e-vac, and run the calc recursively.
    5-9-25: Reworked to add functionality for more than one pair removal.
    5-14-25: Made minor modifications to the section that pulls the modifications from ModsCo.txt so the csv didn't separate it weirdly
    5-21-25: Added function to get pristine energy from E_pristine.csv if OUTCAR for pristine structure can't be found. If more than one element has been removed, script calculates
            e-vac from pristine structure and from previous structure
    5-30-25: Modified get_pair_numbers in case of 0 Li or O. 
"""
#import modules
import os
import sys
#define functions
def get_dirs(mod_dir):
    '''Runs through all directories in base directory and returns list of vacancy directories.'''
    vac_dirs=[]
    for root, dirs, files in os.walk(mod_dir):
        if root.endswith('Removed') and 'OUTCAR' in os.listdir(root):
            vac_dirs.append(root)
    vac_dirs.sort()
    return vac_dirs

def read_file(r_dir, file):
    '''Reads given file in directory and returns list of lines'''
    F = open(os.path.join(r_dir,file),'r')
    lines = F.readlines()
    F.close
    return lines

def get_pair_numbers(vac_dir):
    '''Get number of pairs removed.'''
    pos = read_file(vac_dir,'POSCAR')
    if pos[5].split()[0].strip()=='Li':
        li_num = pos[6].split()[0]
    else:
        li_num = 0
    if pos[5].split()[-1].strip()=='O':
        o_num = pos[6].split()[-1]
    else:
        o_num = 0
    li = 18 - float(li_num)
    o = (36 - float(o_num))
    return li, o 

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
    
def get_ep(base_dir,mod_dir):
    '''If pristine structures are not calculated. '''
    if "E_pristine.csv" in os.listdir(base_dir):
        lp = read_file(base_dir,'E_pristine.csv')
        mod_name = os.path.basename(mod_dir)
        for ep in lp:
            sep = ep.split(',')
            if f'{sep[0]}' == f'{mod_name}':
                e_p = float(sep[2])
                return e_p
    else:
        print("Pristine structures or E_pristine.csv not found. If pristine structures haven't been calculated, copy E_pristine.csv into this directory.")
        print('Exiting...')
        sys.exit()
        
def get_all_e(mod_dir,mods,base_dir):
    '''Gets total energy of pristine and vacancy surfaces.Returns list of vacancy energies.'''
    #get total energy of pristine surface
    p = os.path.join(mod_dir,'VASP_inputs/')
    e_p = get_e(p)
    
    if e_p == None:
        e_p = get_ep(base_dir,mod_dir)
        
    #gets all vacancy dirs
    vac_dirs = get_dirs(mod_dir)
    #stops the program in no vacancy directories are found
    if not vac_dirs:
        print('No vacancy directories found. Exiting...')
        sys.exit()
    
    mod_name = os.path.basename(mod_dir)
    #gets e_vac for vac dirs
    vac_tot = []
    for vac_dir in vac_dirs:
        vac = get_e(vac_dir)
        li, o = get_pair_numbers(vac_dir)
        e_vac = calc_e_vac(e_p,vac,vac_dir,li,o)
        pair = os.path.basename(vac_dir).split('_')[1]
        element = os.path.basename(vac_dir).split('_')[0]
        dirname = os.path.dirname(vac_dir)
        if dirname.endswith('VASP_inputs'):
            for i, mod in enumerate(mods,1):
                if f'Modification_{i}' == f'{mod_name}':
                    mod = mod.strip('-')
                    vac_tot.append(f'\n{mod_name}/{mod},{element}_{pair},{vac},{e_vac},,{li},{o}')
        elif dirname.endswith('Removed'):
            prev_el = os.path.basename(dirname).split('_')[0]
            prev_pair = os.path.basename(dirname).split('_')[1]
            #get evac relative to previous structure 
            prev = get_e(dirname)
            if os.path.basename(dirname).startswith('O_Pair'):
                o = 0
            elif os.path.basename(dirname).startswith('Li_Pair'):
                li = 0
            ev_from_prev = calc_e_vac(prev, vac, vac_dir,li,o)
            for i, mod in enumerate(mods,1):
                if f'Modification_{i}' == f'{mod_name}':
                    mod = mod.strip('-')
                    vac_tot.append(f'\n{mod_name}/{mod},{prev_el}_{prev_pair}/{element}_{pair},{vac},{e_vac},{ev_from_prev},{li},{o}')
    
    return vac_tot
    
def calc_e_vac(e_p,vac,vac_dir,li,o):
    '''Calculates vacancy energy'''
    li_bulk = -1.9072204
    o2 = -9.03
    ev = (vac+(li * li_bulk) + (o2 * (o/2)) - e_p)/2
    return ev

def process_e_vac(base_dir):
    '''Gets e_vac recursively for all dirs and returns it in one csv '''
    mod_dirs = []
    for root, dirs, files in os.walk(base_dir):
        if os.path.basename(root).startswith('Modification_'):
            mod_dirs.append(root)
    mod_dirs.sort()
    if not mod_dirs:
        print('No modification directories found.')
        return
    
    #get modifications from ModsCo.txt
    mods = read_file(base_dir, 'ModsCo.txt')
    #convert the commas to dashes so the csv won't separate incorrectly
    mods_str = []
    for m in mods:
        ml= m.strip('\n').split(',')
        ms = ''
        for i in ml:
            ms += f'{i}-'
        mods_str.append(ms)
    mods = mods_str  

    #Calculate E_vac in each modification directory in 
    e_vac_tot = []
    for mod_dir in mod_dirs:
        ev = get_all_e(mod_dir,mods,base_dir)
        for e in ev:
            e_vac_tot.append(e)
    
    #check e_vac_tot for values      
    if e_vac_tot == None:
        print('No values found. Exiting...')
        sys.exit()
    
    #write file
    with open(f'{base_dir}/E_vac.csv','w',encoding=None) as f:
        f.write('Modification,Atom Pair,Total E,E_vac (pristine),E_vac (from prev vacancy),# of Li removed, # of O removed')
        f.writelines(e_vac_tot)
        f.close
