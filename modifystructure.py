from ase.io import read, write
import os
import copy
import shutil
import sys

# Save pairs to text files
def save_pairs_to_file(pairs, filename):
    with open(filename, 'w') as file:
        for pair in pairs:
            file.write(f"{pair[0]},{pair[1]}\n")

# Replace Co according to ModsCo.txt
def modify_pairs(atoms,atom_pairs):
    def read_modifications(filename):
        modifications = []
        with open(filename, 'r') as file:
            for line in file:
                parts = line.strip().replace(" ", "").split(',')
                pair_indices = list(map(int, parts[:-len(parts) // 2]))
                new_elements = parts[-len(parts) // 2:]
                modifications.append((pair_indices, new_elements))
        return modifications

    modifications = read_modifications("Mods.txt")

    for mod_index, (pair_indices, new_elements) in enumerate(modifications):
        modified_atoms = copy.deepcopy(atoms)
        for i, pair_index in enumerate(pair_indices):
            if pair_index < len(atom_pairs):
                index1, index2 = atom_pairs[pair_index]
                modified_atoms[index1].symbol = new_elements[i]
                modified_atoms[index2].symbol = new_elements[i]
        
        # Make new directory for each new structure
        directory_name = f"Modification_{mod_index + 1}"
        os.makedirs(directory_name, exist_ok=True)
        
        output_filename = os.path.join(directory_name, f"POSCAR_modified_{mod_index + 1}.vasp")
        write(output_filename, modified_atoms, format="vasp")
        print(f"Modified POSCAR saved in directory {directory_name} as {output_filename}.")

def modify():
    '''Modifies structures based of user input. '''
    pkgdir = sys.modules['amelia_wf'].__path__[0]
    fullpath = os.path.join(pkgdir, 'POSCAR')
    shutil.copy(fullpath, os.getcwd())
    # Read POSCAR 
    atoms = read(os.path.join(os.getcwd(),'POSCAR'))

    # Define number of each element in POSCAR
    with open(os.path.join(os.getcwd(),'POSCAR'), 'r') as P:
        P_lines = P.readlines()
    
    e_line = P_lines[5]
    elements = e_line.split()
    c_line = P_lines[6]
    counts = c_line.split()
    element_counts = {}
    pairs = {}
    for i,element in enumerate(elements):
        element_counts.update({f'{element}':float(f'{counts[i]}')})
        pairs.update({f'{element}_pairs':[]})
    # Store pairs by element
    index = 0  

    # Loop through each element and its count
    for element, count in element_counts.items():
        # Pair consecutive atoms of this element
        for i in range(count // 2):
            # Append the pair to the appropriate list based on the element type
            pair = (index, index + 1)
            if f'{element}_pairs' in pairs:
                pairs[f'{element}_pairs'].append(pair)

            index += 2  # Move to the next pair
    #save pairs to file
    for element in pairs.keys(): 
        save_pairs_to_file(pairs[f'{element}'], f'{element}.txt')
        print(f"Pairs saved to {element}.txt.")
    
    #modify based on input
    print('Which element would you like to modify?')
    for i,element in enumerate(elements):
        print(f'{i+1}:{element}')
    choice = input("Enter the number of your choice: ")
    
    