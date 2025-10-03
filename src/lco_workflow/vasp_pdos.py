'''
Create pdos .dat files for each atom recursively
Author: Dorothea Fennell
Modified from Blake's vasp_pdos.py script
Changelog: 
    4-30-25: Created, comments added. Broke original script up into functions so it can be applied recursively. 
    8-6-25: Modified fermi_energy to split accordingly
'''
#import modules
import numpy as np
import os

#define functions
def fermi_energy(pdos_dir):
    '''
    Determining fermi energy from given OUTCAR file. 
    Note: TotalDos and Atom files with individual orbitals are not fermi shifted but atom_total files are
    '''
    line=""
    for l in open(f'{pdos_dir}/OUTCAR',"r").readlines():
        if "Fermi energy:" in l:
            line=l
    if line.startswith(' BZINTS'):
        fermi = float(line.split()[3].strip(';'))
    else:
        fermi=float(line.split()[2])
    return fermi

def read_files(pdos_dir):
    ''' Reads POSCAR and DOSCAR and returns linesP and linesD'''
    D = open(f"{pdos_dir}/DOSCAR", "r")
    P = open(f"{pdos_dir}/POSCAR", "r")
    linesP = P.readlines()
    linesD = D.readlines()
    P.close()
    D.close()
    return linesP, linesD

def tdos(pdos_dir,linesD):
    '''
    Constructs the Total Density of States and saves it to TotalDos.dat. File has 5 columns: Energy(eV), DOS(up), DOS(down), Integrated DOS(up), and Integrated DOS(down).
    '''
    TDos = open(f"{pdos_dir}/TotalDos.dat", "a")
    x = linesD[5]          
    x = x.split()                              
    loop = int(x[2])                   
    s = ""         
    s = s.join(linesD[6:6+loop])
    TDos.write('#Energy(eV)  DOS(up)       DOS(down)      Int_DOS(up)    Int_DOS(down)')
    TDos.write('\n')
    TDos.write(s)
    TDos.close()

def pdos(pdos_dir,linesP,linesD,fermi):
   '''Creates .dat and _total.dat files for each atom. _total.dat files have the orbitals summed (all p orbitals together, etc.), and the energy is fermi shifted.'''
   #List of Atom types and the most of each atom type
   atom_types = linesP[5]
   atom_types = atom_types.split()
   atom_numbers = linesP[6]
   atom_numbers = atom_numbers.split()
   atom_numbers = [int(i) for i in atom_numbers]
   tot_atoms = [int(i) for i in atom_numbers]
   tot_atoms = sum(tot_atoms)
   l = linesD[5]
   l = l.split()
   loop = int(l[2])

   #Loop through and create the different PDOS for each atom
   a=1
   b=2
   count=0
 
   for x in atom_numbers:
       for i in range(x):
           index1 = 6 + a + a*loop
           index2 = 6 + a + b*loop
           Pdos = open(f'{pdos_dir}/{atom_types[count]}{a-1}.dat', "a")
           collect = ""
           collect = collect.join(linesD[index1:index2])
           Pdos.write('#Energy(eV)  s(up) s(down)   p{y}(up)  p{y}(down)   p{z}(up) p{z}(down)   p{x}(up) p{x}(down)   d{xy}(up)   d{xy}(down)     d{yz}(up)   d{yz}(down)    d{z2}(up)  d{z2}(down)    d{xz}(up)  d{xz}(down)     d{x2-y2}(up)    d{x2-y2}(down)')
           Pdos.write('\n')
           Pdos.write(collect)
           Pdos.close()
           
           #load file to create summed pdos file
           data = np.loadtxt(f'{pdos_dir}/{atom_types[count]}{a-1}.dat',unpack=True)
           dfermi = data[0]-fermi
           dup = data[9] + data[11] + data[13] + data[15] + data[17] 
           ddown = (data[10] + data[12] + data[14] + data[16] + data[18])*-1 
           pup = data[3] + data[5] + data[7]  
           pdown = (data[4] + data[6] + data[8])*-1 
           sup = data[1] 
           sdown = data[2]*-1 
           added = [dfermi, sup, sdown, pup, pdown, dup,  ddown] 
           np.savetxt(f'{pdos_dir}/{atom_types[count]}{a-1}_total.dat', added, header="Energy(eV)              s(up)                    s(down)                  p(up)                    p(down)                  d(up)                    d(down)")
           a+=1
           b+=1
       count+=1
        

def process_pdos_dirs(base_dir):
    """Finds all PDOS directories and processes POSCAR & DOSCAR into a file for each individual atom."""
    pdos_dirs=[]
    for root, dirs, files in os.walk(base_dir):
        if root.endswith("/PDOS") and "DOSCAR" in files:
            pdos_dirs.append(root)
        elif root.endswith("/PDOS") and "DOSCAR" not in files:
            print("PDOS calculations haven't been run yet.")
            
    if not pdos_dirs:
        print('No PDOS directories found. Exiting...')
        return
    
    for pdos_dir in pdos_dirs:
        print(f'Processing {pdos_dir}')
        #open DOSCAR & POSCAR
        linesP, linesD = read_files(pdos_dir)

        #construct tdos
        tdos(pdos_dir,linesD)

        #get fermi energy
        fermi = fermi_energy(pdos_dir)

        #construct pdos for each atom
        pdos(pdos_dir, linesP, linesD, fermi)
        print(f'PDOS files created for {pdos_dir}')
        
