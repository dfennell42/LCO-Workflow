"""
Script to integrate PDOS for metal atoms
Author: Dorothea Fennell - dfennell1@bnl.gov
Changelog: 
    5-5-25: Created, comments added.
    5-9-25: Changed integration section based on Blake's script
    7-8-25: Changed script to pull selected data for M1, M2, and M3, adjusting indexes based on number of Li. Also added function to sort data 
            by index.
    7-23-25: Changed script to automatically add aluminum to csv of metal data with tot_e, spin, and hd/p = 0 and os = 3.
NOTE: While this script uses 'integrate' to describe what's occuring, this is not technically an integration. The script takes
      the sum of the pdos from the lower limit of integration to positive infinity, divides each value in the integration window by this
      sum, then multiplies it by 5 to account for all 5 d orbitals. This is due to the need to normalize the occupied and unoccupied states
      (ask Blake for more details).
"""
#import modules
import os
import numpy as np
from pymatgen.core.periodic_table import Element
#define functions so program can operate recursively
def get_dirs(base_dir):
    '''Runs through all directories in base directory and returns list of pdos directories.'''
    pdos_dirs=[]
    for root, dirs, files in os.walk(base_dir):
        if root.endswith("PDOS") and "TotalDos.dat" in files:
            pdos_dirs.append(root)
        elif root.endswith("PDOS") and "TotalDos.dat" not in files:
            print("PDOS data hasn't been parsed yet.")
    return pdos_dirs

def get_files(pdos_dir):
    '''Gets files of all atoms from pdos directory'''
    m_filelist = []
    for file in os.listdir(pdos_dir):
        if file.endswith('_total.dat'):
            filepath = os.path.join(pdos_dir,file)
            atom = file.split('_')[0]
            atom = atom.strip('0123456789')
            ele = Element(atom)
            if ele.Z > 20:
                m_filelist.append(filepath)
    m_filelist.sort()
    return m_filelist

def int_pdos(data,up_idx,down_idx,lower,upper, diff=True):
    """Integrates PDOS in specified windows."""
    #slice arrays
    energy = data[:,0]
    up = data[:,up_idx]
    down = data[:,down_idx]
    #set up variables for next section
    up_e = 0.0
    down_e = 0.0
    tot_e = 0.0
    up_sum = 0.0
    down_sum = 0.0
    #integrate
    for x in range(len(energy)):
        if energy[x] > lower:
            up_sum += up[x]
            down_sum += down[x]
            
    for x in range(len(energy)):
        if energy[x] > lower and energy[x] < upper:
            up_e += up[x]/up_sum * 5
            down_e += down[x]/down_sum * 5
            tot_e += up[x]/up_sum * 5 + down[x]/down_sum * 5
    if diff == True:
        diff = np.abs(up_e-down_e)
        return tot_e, diff
    else:
        tota = tot_e
        return tota
    
def get_os(ele,e_tot):
    """Gets oxidation state of metal."""
    valence = ele.valence[1]
    oxs = valence - e_tot
    return oxs

def int_d_states(filelist):
    """Integrates the d states of the metal atoms for the total number of electrons and d/p hybridization. """
    #create data lists
    m_data = []
    for file in filelist:
        #determine atom
        filename = os.path.basename(file)
        atom = filename.split('_')
        index = ''
        for char in atom:
            if char.isdigit():
                index +=f'{char}'
        ele = atom.strip('0123456789')
        ele = Element(ele)
        #the atom_total.dat files have to be unpacked because they're made with np.savetext
        data = np.genfromtxt(file,skip_header=1,unpack=True)
        
        #integrate from -2 to 0 to get total # of electrons and net spin
        e_tot, spin = int_pdos(data,5,6,-2,0)
        
        #integrate from -8 to -2 to get d/p hybridization
        tot_win = int_pdos(data,5,6,-8,0,diff=False)
        hdp = tot_win - e_tot
        #get os
        ox = get_os(ele,e_tot)
        #append data to list
        m_data.append(f'\n{ele},{index},{e_tot},{ox},{spin},{hdp}')
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
    
    for pdos_dir in pdos_dirs:
        #get filelists
        m_filelist, o_filelist, li_filelist = get_files(pdos_dir)
        #integrate d states
        m_data = int_d_states(m_filelist)
        
        #print data to csv
        mod_header = 'Element,Atom index,e_tot,OS,spin,H d/p'
        m_data.sort(key=sort_by_index)
        print_data(pdos_dir,m_data,'integrated-pdos',mod_header)

def sort_by_index(data):
    '''For sorting the lists of data by the atom index rather than by element'''
    data_list = data.split(',')
    if len(data_list) == 6:
        index = int(data_list[1])
        return index
    elif len(data_list) == 7:
        index = int(data_list[2])
        dirname = data_list[0].strip('\n')
        dir_num = dirname.split('_')[1]
        num = int(dir_num)
        return (index, num)
