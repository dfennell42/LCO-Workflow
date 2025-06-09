"""
Modify INCAR for PDOS calculations
Author: Dorothea Fennell
Changelog: 
    4-23-25: Created, comments added 
"""
#import modules
import os

# Find PDOS_INCAR.txt file in the PDOS directory
def find_incar_file(modification_dir):
    # Look for the _INCAR.txt file in the current directory
    for file in os.listdir(modification_dir):
        if file.endswith("_INCAR.txt"):
            return os.path.join(modification_dir, file)
    return None

#Modify the INCAR file for PDOS calculations
def modify_incar(incar_path, pdos_incar_file):
    """Modifies the INCAR file for PDOS calculations"""
    with open(incar_path, "r") as incar:
        incar_lines = incar.readlines()
    
    #Gets correct lines from PDOS_INCAR.txt file
    with open(pdos_incar_file, "r") as pdos:
        pdos_lines = pdos.readlines()
    
    #Saves magmom line from current INCAR file
    for line in incar_lines:
        if line.strip().startswith("MAGMOM"):
            magmom_line = line.strip()
   

    #adds the magmom line to pdos_lines
    pdos_lines.append(f"\n{magmom_line}")

    #write correct INCAR file
    with open(incar_path, "w") as incar:
        incar.writelines(pdos_lines)
    
    print(f"Updated INCAR in {incar_path}")
    #print(magmom_line)

#Modify all INCAR files recursively
def process_pdos_dirs(base_directory):
    """Finds all PDOS directories and edits their INCAR files."""
    for root, dirs, files in os.walk(base_directory):
        if "INCAR" in files:
            if root.endswith("PDOS"):
                pdos_incar_file = find_incar_file(root)
                if pdos_incar_file:
                    modify_incar(os.path.join(root, "INCAR"), pdos_incar_file)
                else:
                    print(f"_INCAR.txt file not found in {root}")
