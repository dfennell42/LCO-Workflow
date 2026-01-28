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
    magnetic_moments = {
        "Li": 0.0,
        "Ni": 0.7,
        "Co": 0.01,
        "O": 0.0,
        "Mn": 2.0,
        "Fe": 0.9,
    }
    magmom = [magnetic_moments.get(element, 0.0) for element in atom_to_element]  # Default all moments

    for (atom1, atom2), spin in spin_pairs.items():
        moment1 = magnetic_moments.get(atom_to_element[atom1 - 1], 0.0)  # Atom1 moment
        moment2 = magnetic_moments.get(atom_to_element[atom2 - 1], 0.0)  # Atom2 moment

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
    poscar_files = find_files_recursive("POSCAR_modified_")
    poscar_files = [file for file in poscar_files if file.endswith(".vasp")]

    if not poscar_files:
        print("No POSCAR_modified_*.vasp files found!")
        return

    print(f"Found {len(poscar_files)} files.")
    #copy SpinPairs file to dir
    pkgdir = sys.modules['lco_workflow'].__path__[0]
    fullpath = os.path.join(pkgdir, 'SpinPairs.txt')
    shutil.copy(fullpath, os.getcwd())
    
    spin_file = "SpinPairs.txt"
    if not os.path.exists(spin_file):
        print(f"SpinPairs.txt not found in the directory.")
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
