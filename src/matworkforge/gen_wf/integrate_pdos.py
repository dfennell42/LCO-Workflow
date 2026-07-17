"""
Script to integrate PDOS for metal atoms
Author: Dorothea Fennell - dfennell1@bnl.gov
Changelog: 
    9-10-25: New version of integrate_pdos, using scipy.integrate.simpson instead of Blake's method.
    9-11-25: Updated integration bounds for d-block metals to -6 to 0, added section to integrate both s & p orbitals for p-block elements.
"""
#import modules
import os
import numpy as np
from pymatgen.core.periodic_table import Element
from scipy.integrate import simpson 
#define functions so program can operate recursively
def get_dirs(base_dir):
    '''Runs through all directories in base directory and returns list of pdos directories.'''
    pdos_dirs=[]
    for root, dirs, files in os.walk(base_dir):
        if root.endswith("s/PDOS") and "TotalDos.dat" in files:
            pdos_dirs.append(root)
        elif root.endswith("s/PDOS") and "TotalDos.dat" not in files:
            print("PDOS data hasn't been parsed yet.")
    return pdos_dirs

def get_files(pdos_dir):
    '''Gets files of all atoms from pdos directory'''
    filelist = []
    for file in os.listdir(pdos_dir):
        if file.endswith('_total.dat'):
            filepath = os.path.join(pdos_dir,file)
            filelist.append(filepath)
    filelist.sort()
    return filelist

def int_pdos(data,up_idx,down_idx,lower,upper,block,diff=True):
    """Integrates PDOS in specified windows."""
    #slice arrays
    energy = data[:,0]
    up = data[:,up_idx]
    down = data[:,down_idx]
    #get bottom of integration window
    for x in range(len(energy)):
        if energy[x] >= lower:
            a = x
            break
    #get top of integration window
    for x in range(len(energy)):
        if energy[x] > upper:
            b = x
            break
    
    #split arrays
    els = np.split(energy,[a,b])
    uls = np.split(up,[a,b])
    dls = np.split(down,[a,b])
    e_win = els[1]
    u_win = uls[1]
    d_win = dls[1]
    #integrate
    up_e = simpson(u_win,x=e_win)
    down_e = simpson(d_win, x=e_win)
    tot_e = up_e + np.abs(down_e)
    #if p-block element, integrate s orbitals as well
    if block == 'p':
        s_up = data[:,1]
        s_down = data[:,2]
        s_uls = np.split(s_up,[b])
        s_dls = np.split(s_down,[b])
        se_win = np.concat((els[0],els[1]),axis=None)
        su_win = s_uls[0]
        sd_win = s_dls[0]
        sup_e = simpson(su_win,x=se_win)
        up_e += sup_e
        sdown_e = simpson(sd_win,x=se_win)
        down_e += sdown_e
        tot_e = up_e + np.abs(down_e)
    #get spin
    if diff == True:
        diff = np.abs(up_e+down_e)
        return tot_e, diff
    else:
        tota = tot_e
        return tota
    
def get_os(ele,e_tot):
    """Gets oxidation state of metal."""
    valence = ele.valence[1]
    if ele.block != 's':
        valence += 2
    oxs = valence - e_tot
    return oxs

def int_d_states(filelist):
    """Integrates the d states of the metal atoms for the total number of electrons and d/p hybridization. """
    #create data lists
    m_data = []
    for file in filelist:
        #determine atom
        filename = os.path.basename(file)
        atom = filename.split('_')[0]
        index = ''
        for char in atom:
            if char.isdigit():
                index +=f'{char}'
        ele = atom.strip('0123456789')
        try:
            ele = Element(ele)
        except:
            pass
        else:
            if ele.block =='s':
                up_idx = 1
                down_idx = 2
                e_lower = -20
                block = 's'
            elif ele.block == 'p':
                up_idx = 3
                down_idx = 4
                e_lower = -10
                block = 'p'
            elif ele.block == 'd':
                up_idx = 5
                down_idx = 6
                e_lower = -10
                block = 'd'
            elif ele.block == 'f':
                up_idx = 7
                down_idx = 8
                e_lower = -15
                block = 'f'
                #the atom_total.dat files have to be unpacked because they're made with np.savetext
            data = np.genfromtxt(file,skip_header=1,unpack=True)
            
            #integrate from lower bound to 0 to get total # of electrons and net spin
            e_tot, spin = int_pdos(data,up_idx,down_idx,e_lower,0,block)
            
            #get os
            ox = get_os(ele,e_tot)
            #append data to list
            if ele.block == 'p':
                m_data.append(f'\n{ele},{index},{e_tot},{ox},{spin},{ele.block}')
            else:
                m_data.append(f'\n{ele},{index},{e_tot},{ox},{spin},{ele.block}')
    return m_data

def print_data(pdos_dir,data,fname,header):
    '''Prints data to csv file. '''
    with open(f'{pdos_dir}/{fname}.csv','w',encoding=None) as f:
        f.write(header)
        f.writelines(data)
        f.close
    print(f'{pdos_dir} csv created.')

def integrate_all_pdos(base_dir):
    '''Integrates pdos recursively through directories.'''
    #get pdos directories
    pdos_dirs = get_dirs(base_dir)

    if not pdos_dirs:
        print('No PDOS directories found. Exiting...')
        return
    
    selected_data = []
    for pdos_dir in pdos_dirs:
        #get filelists
        filelist = get_files(pdos_dir)
        #integrate d states
        m_data = int_d_states(filelist)
        #print data to csv
        mod_header = 'Element,Atom index,e_tot,OS,spin,Orbital'
        m_data.sort(key=sort_by_index)
        print_data(pdos_dir,m_data,'integrated-pdos',mod_header)

def sort_by_index(data):
    '''For sorting the lists of data by the atom index rather than by element'''
    data_list = data.split(',')
    if len(data_list) == 6:
        index = int(data_list[1])
        return index


