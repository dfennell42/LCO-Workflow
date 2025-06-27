import os
from .MagMom_recursive import process_pair_rem_files

def read_file(r_dir, file):
    '''Reads given file in directory and returns list of lines'''
    F = open(os.path.join(r_dir,file),'r')
    lines = F.readlines()
    F.close
    return lines

def find_magmom_file(modification_dir):
    # Look for the _MAGMOM.txt file in the current directory
    for file in os.listdir(modification_dir):
        if file.endswith("_MAGMOM.txt"):
            return os.path.join(modification_dir, file)
    return None

def modify_incar(incar_path, root):
    """Edits the MAGMOM line in INCAR based on the modification type."""
    with open(incar_path, "r") as f:
        lines = f.readlines()

    magmom_file = find_magmom_file(root)  # Find the _MAGMOM.txt in the current Modification_# directory
    if not magmom_file:
        print(f"No _MAGMOM.txt file found in {root}")
        return
    
    with open(magmom_file, "r") as magmom:
        magmom_line = magmom.read().strip()
 
    modified_lines = []
    for line in lines:
        if line.strip().startswith("MAGMOM"):
            modified_lines.append(magmom_line)
        else:
            modified_lines.append(line)

    with open(incar_path, "w") as f:
        f.writelines(modified_lines)

    print(f"Updated INCAR in {os.path.dirname(incar_path)}")

def process_pairs_removed_dirs(base_directory):
    """Finds all *_Pairs_Removed directories and edits their INCAR files."""
    for root, dirs, files in os.walk(base_directory):
        if "INCAR" in files and root.endswith('_Removed'):
            process_pair_rem_files()
            modify_incar(os.path.join(root, "INCAR"),root)