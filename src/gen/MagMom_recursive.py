import os
import sys
import shutil
# Define element-specific magnetic moments

def read_poscar(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()

    # Extract element names and counts
    elements = lines[5].split()
    num_atoms = list(map(int, lines[6].split()))

    # Map each atom index to its element
    atom_to_element = []
    for elem, count in zip(elements, num_atoms):
        atom_to_element.extend([elem] * count)

    return elements, num_atoms, atom_to_element

def read_spin_pairs(filename):
    spin_pairs = {}
    with open(filename, 'r') as f:
        for line in f:
            parts = line.strip().split(',')
            atom1, atom2 = int(parts[0]), int(parts[1])
            spin = parts[2].strip()
            spin_pairs[(atom1, atom2)] = spin
    return spin_pairs

def assign_magnetic_moments(atom_to_element, spin_pairs):
    """
    Assign magnetic moments to atoms based on spin pairs and element type.
    """
    pkgdir = sys.modules['delafossite_wf'].__path__[0]
    with open(os.path.join(pkgdir,'MagMom_dict.txt'),'r') as mm:
        mm_lines = mm.readlines()
        
    magnetic_moments = {}
    for x in mm_lines:
        x_split = x.split(':')
        y = x_split[1].strip('\n')
        magnetic_moments.update({f'{x_split[0]}':float(f'{y}')})
        
    magmom = [magnetic_moments.get(element, 0.6) for element in atom_to_element]  # Default all moments

    for (atom1, atom2), spin in spin_pairs.items():
        moment1 = magnetic_moments.get(atom_to_element[atom1 - 1], 0.6)  # Atom1 moment
        moment2 = magnetic_moments.get(atom_to_element[atom2 - 1], 0.6)  # Atom2 moment

        if spin == "up":
            magmom[atom1 - 1] = moment1
            magmom[atom2 - 1] = moment2
        elif spin == "down":
            magmom[atom1 - 1] = -moment1
            magmom[atom2 - 1] = -moment2

    return magmom

def generate_magmom_line(elements, num_atoms, magmom):
    """
    Create the `MAGMOM` line preserving the element order in POSCAR.
    """
    magmom_line = []
    index = 0

    for elem, count in zip(elements, num_atoms):
        element_moments = magmom[index:index + count]

        # Group consecutive identical moments
        group_start = 0
        while group_start < len(element_moments):
            group_moment = element_moments[group_start]
            group_count = 0

            for i in range(group_start, len(element_moments)):
                if element_moments[i] == group_moment:
                    group_count += 1
                else:
                    break

            magmom_line.append(f"{group_count}*{group_moment:.1f}")
            group_start += group_count

        index += count

    return " ".join(magmom_line)

def find_files_recursive(pattern):
    """
    Recursively find files matching the given pattern.
    """
    matched_files = []
    for root, dirs, files in os.walk("."):
        for file in files:
            if pattern in file:
                matched_files.append(os.path.join(root, file))
    return matched_files

def process_poscar_files():
    # Find all POSCAR files with the pattern POSCAR_modified_*.vasp
    poscar_files = find_files_recursive("POSCAR_")
    poscar_files = [file for file in poscar_files if file.endswith(".vasp")]

    if not poscar_files:
        print("No POSCAR_*.vasp files found!")
        return

    print(f"Found {len(poscar_files)} files.")
    #copy SpinPairs file to dir
    userdir = os.path.expanduser('~/wf-user-files')
    fullpath = os.path.join(userdir, 'SpinPairs.txt')
    shutil.copy(fullpath, os.getcwd())
    
    spin_file = "SpinPairs.txt"
    if not os.path.exists(spin_file):
        print("SpinPairs.txt not found in the directory.")
        return

    for poscar_file in poscar_files:
        print(f"Processing {poscar_file}...")

        # Read POSCAR and SpinPairs
        elements, num_atoms, atom_to_element = read_poscar(poscar_file)
        spin_pairs = read_spin_pairs(spin_file)

        # Assign magnetic moments
        magmom = assign_magnetic_moments(atom_to_element, spin_pairs)

        # Generate MAGMOM line
        magmom_line = generate_magmom_line(elements, num_atoms, magmom)

        # Write output MAGMOM line to file
        output_file = f"{poscar_file.replace('.vasp', '_MAGMOM.txt')}"
        with open(output_file, "w") as f:
            f.write(f"MAGMOM = {magmom_line}\n")
        
        print(f"Generated MAGMOM line saved to {output_file}.")
        
def process_pair_rem_files():
    # Find all POSCAR files with the pattern POSCAR_modified_*.vasp
    def get_dirs():
        '''Runs through all directories in base directory and returns list of vacancy directories.'''
        vac_dirs=[]
        for root, dirs, files in os.walk(os.getcwd()):
            if root.endswith('Removed') and 'INCAR' in os.listdir(root):
                vac_dirs.append(root)
        vac_dirs.sort()
        return vac_dirs
    vac_dirs = get_dirs()
    poscar_files = []
    for vac_dir in vac_dirs:
        for root, dirs, files in os.walk(vac_dir):
            for file in files:
                if "POSCAR_" in file:
                    poscar_files.append(os.path.join(root, file))
    poscar_files = [file for file in poscar_files if file.endswith(".vasp")]

    if not poscar_files:
        print("No POSCAR_*.vasp files found!")
        return

    print(f"Found {len(poscar_files)} files.")
    #copy SpinPairs file to dir
    userdir = os.path.expanduser('~/wf-user-files')
    fullpath = os.path.join(userdir, 'SpinPairs.txt')
    shutil.copy(fullpath, os.getcwd())
    
    spin_file = "SpinPairs.txt"
    if not os.path.exists(spin_file):
        print("SpinPairs.txt not found in the directory.")
        return

    for poscar_file in poscar_files:
        print(f"Processing {poscar_file}...")

        # Read POSCAR and SpinPairs
        elements, num_atoms, atom_to_element = read_poscar(poscar_file)
        spin_pairs = read_spin_pairs(spin_file)

        # Assign magnetic moments
        magmom = assign_magnetic_moments(atom_to_element, spin_pairs)

        # Generate MAGMOM line
        magmom_line = generate_magmom_line(elements, num_atoms, magmom)

        # Write output MAGMOM line to file
        output_file = f"{poscar_file.replace('.vasp', '_MAGMOM.txt')}"
        with open(output_file, "w") as f:
            f.write(f"MAGMOM = {magmom_line}\n")
        
        print(f"Generated MAGMOM line saved to {output_file}.")