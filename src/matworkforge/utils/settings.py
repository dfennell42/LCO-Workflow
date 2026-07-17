#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create/Read calculation-specific settings. 
Author: Dorothea Fennell
Changelog:
    7-8-26: File created, comments added.
"""
#import modules
import tomllib
import os

#def functions
def read_settings():
    '''Reads settings from settings.toml file and returns dictionary.'''
    base_dir = os.getcwd()
    #set defaults
    default = {'poscar-file':'POSCAR',
               'mods-file': 'Mods.txt',
               'spin-file':'SpinPairs.txt',
               'submit-file':'vasp.sh',
               'ignore-symmetry':False,
               'incar-params':{},
               'pdos-params':{}
               }
    
    #get settings
    if os.path.exists(f'{base_dir}/settings.toml'):
        with open(f'{base_dir}/settings.toml','rb') as s:
            settings = tomllib.load(s)
    
    #if settings file doesn't exist
    if not settings:
        settings = default.copy()
    
    #if keys are missing
    for k in default.keys():
        settings.setdefault(k, default[k])
    
    #return settings
    return settings