import os

def read_file(r_dir, file):
    '''Reads given file in directory and returns list of lines'''
    F = open(os.path.join(r_dir,file),'r')
    lines = F.readlines()
    F.close
    return lines

def get_pair_numbers(vac_dir):
    '''Get number of li & o .'''
    pos = read_file(vac_dir,'POSCAR')
    if pos[5].split()[0].strip()=='Li':
        li = pos[6].split()[0]
    else:
        li = '0'
    if pos[5].split()[-1].strip()=='O':
        o = pos[6].split()[-1]
    else:
        o = '0'
    return li, o

def modify_incar(incar_path, root):
    """Edits the MAGMOM line in INCAR based on the modification type."""
    with open(incar_path, "r") as f:
        lines = f.readlines()

    modified_lines = []
    for line in lines:
        if line.strip().startswith("MAGMOM"):
            magmom_parts = line.split("=")
            if len(magmom_parts) < 2:
                print(f"Skipping malformed MAGMOM line in {incar_path}")
                modified_lines.append(line)
                continue

            magmom_values = magmom_parts[1].strip().split()
            #get number of li & o removed
            li, o = get_pair_numbers(root)
            # Modify the oxygen entry
            if os.path.basename(root).startswith('O_') and root.endswith('_Removed'):
                if o == '0':
                    magmom_values[-1] = ''
                else:
                    magmom_values[-1] = f'{o}*0.0'
            #Modify the lithium entry
            elif os.path.basename(root).startswith('Li_') and root.endswith('_Removed'):
                if li == '0':
                    magmom_values[0] = ''
                else:
                    magmom_values[0] = f'{li}*0.0'
            # Reconstruct the line
            modified_line = f"MAGMOM ={' '.join(magmom_values)}\n"
            modified_lines.append(modified_line)
        else:
            modified_lines.append(line)

    with open(incar_path, "w") as f:
        f.writelines(modified_lines)

    print(f"Updated INCAR in {os.path.dirname(incar_path)}")

def process_pairs_removed_dirs(base_directory,choice):
    """Finds all *_Pairs_Removed directories and edits their INCAR files."""
    for root, dirs, files in os.walk(base_directory):
        if "INCAR" in files:
            if choice == '1':
                if os.path.basename(root).startswith('Li_') and root.endswith('_Removed'):
                    modify_incar(os.path.join(root, "INCAR"),root)
            elif choice == '2':
                if os.path.basename(root).startswith('O_') and root.endswith('_Removed'):
                    modify_incar(os.path.join(root, "INCAR"),root)