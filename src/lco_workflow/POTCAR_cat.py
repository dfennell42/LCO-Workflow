import os

def find_vasp_files(vac = False):
    """
    Recursively find all .vasp files in subdirectories and group them by directory.
    """
    vasp_files_by_dir = {}
    for root, _, files in os.walk("."):
        for file in files:
            if file.endswith(".vasp"):
                if vac == False:
                    vasp_files_by_dir.setdefault(root, []).append(file)
                elif vac == True:
                    if root.endswith('Removed'):
                        vasp_files_by_dir.setdefault(root, []).append(file)
    return vasp_files_by_dir

def read_element_names(filepath):
    """
    Read the 5th line of the POSCAR file to extract element names.
    """
    with open(filepath, 'r') as f:
        lines = f.readlines()
    if len(lines) < 6:
        raise ValueError(f"File {filepath} does not have enough lines to extract element names.")
    elements = lines[5].strip().split()  # 5th line (0-based index 4)
    return elements

def concatenate_potcar(elements, potcar_base_path, output_filepath):
    """
    Concatenate POTCAR files for the given elements into a single POTCAR file.
    """
    with open(output_filepath, 'w') as master_potcar:
        for element in elements:
            potcar_path = os.path.join(potcar_base_path, element, "POTCAR")
            if not os.path.exists(potcar_path):
                raise FileNotFoundError(f"POTCAR file for {element} not found at {potcar_path}.")
            with open(potcar_path, 'r') as element_potcar:
                master_potcar.write(element_potcar.read())
    print(f"Created POTCAR file: {output_filepath}")

def process_directories(potcar_base_path,vac):
    """
    Process each directory containing .vasp files, extract elements, and create a POTCAR file.
    """
    vasp_files_by_dir = find_vasp_files(vac)

    if not vasp_files_by_dir:
        print("No .vasp files found!")
        return

    print(f"Found {len(vasp_files_by_dir)} directories with .vasp files.")

    for directory, files in vasp_files_by_dir.items():
        print(f"\nProcessing directory: {directory}")
        all_elements = []  # Use a list to preserve the order of elements

        for file in files:
            filepath = os.path.join(directory, file)
            print(f"  Reading {filepath}...")
            elements = read_element_names(filepath)
            print(f"  Elements: {', '.join(elements)}")
            all_elements.extend(elements)  # Add elements in the order they appear

        # Concatenate POTCAR for this directory
        output_filepath = os.path.join(directory, "POTCAR")
        concatenate_potcar(all_elements, potcar_base_path, output_filepath)

# Configuration
POTCAR_BASE_PATH = "/hpcgpfs01/ic2software/vasp6/6.4.2/PSEUDOPOTENTIAL/PBE/"  # Path for VASP potentials on IC2


