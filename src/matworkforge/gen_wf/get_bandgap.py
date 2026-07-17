#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Calculate band gap, e_fermi, CBM & VBM
Author: Dorothea Fennell
Changelog: 
    2-9-26: Created, comments added
"""
#import modules
from pymatgen.io.vasp import Vasprun
import pandas as pd
import os

#define functions
def read_file(r_dir, file):
    '''Reads given file in directory and returns list of lines'''
    F = open(os.path.join(r_dir,file),'r')
    lines = F.readlines()
    F.close
    return lines

def get_BG(vasprun, mod):
    '''Calculates band gap, E_fermi, CBM & VBM'''
    # Get band structure and band gap
    band_struc = vasprun.get_band_structure()
    band_gap = band_struc.get_band_gap()
    fermi = band_struc.efermi
    cbm = band_struc.get_cbm()['energy']
    vbm = band_struc.get_vbm()['energy']
    bg_ser = pd.Series({'Modification':mod,'Band gap':band_gap['energy'],'E_fermi':fermi,'VBM':vbm,'CBM':cbm})
    return bg_ser

def get_band_data(base_dir):
    '''Gets band gap data for all modification directories.'''
    band_dirs=[]
    for root, dirs, files in os.walk(base_dir):
        if root.endswith('Band_struc') and 'vasprun.xml' in files:
            band_dirs.append(root)
    
    if not band_dirs:
        print('No directories found. Have band structure calculations been run?')
    
    band_dirs.sort()
    #get modifications from ModsCo.txt
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
    
    bg_data = []
    
    for band_dir in band_dirs:
        vpr = Vasprun(f'{band_dir}/vasprun.xml')
        for i,mod in enumerate(mods,1):
            if f'Modification_{i}/' in band_dir:
                mod.strip('-')
                bg = get_BG(vpr, mod)
                bg_data.append(bg)
    
    #create df 
    bg_df = pd.DataFrame(bg_data)
    bg_df.set_index('Modification',inplace=True)
    #export df to csv
    bg_df.to_csv(f'{base_dir}/band_gap.csv')
    print('Band gap data exported to band_gap.csv')