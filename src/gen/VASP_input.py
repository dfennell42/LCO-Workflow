import os
import shutil
from pymatgen.io.vasp import Kpoints, Poscar, Incar
from pymatgen.io.vasp.sets import MPRelaxSet
from pymatgen.core.structure import Structure

# Function to generate VASP inputs from a POSCAR file
def generate_vasp_inputs(vasp_file, custom_incar_params=None):
    # Read the structure from the VASP POSCAR file
    structure = Structure.from_file(vasp_file)

    # Prepare the necessary VASP input files
    poscar = Poscar(structure)
    incar = Incar.from_dict(MPRelaxSet(structure).incar)
    kpoints = Kpoints.monkhorst_automatic([4, 4, 1])  # could specify a different kgrid

    # Apply custom INCAR parameters if provided
    if custom_incar_params:
        incar.update(custom_incar_params)

    # Define output directory
    input_dir = os.path.join(os.path.dirname(vasp_file), "VASP_inputs")
    os.makedirs(input_dir, exist_ok=True)

    # Write the files
    poscar.write_file(os.path.join(input_dir, "POSCAR"))
    incar.write_file(os.path.join(input_dir, "INCAR"))
    kpoints.write_file(os.path.join(input_dir, "KPOINTS"))

    # Copy the POTCAR file from the same directory as the POSCAR file to the new VASP_inputs directory
    potcar_file = os.path.join(os.path.dirname(vasp_file), "POTCAR")
    if os.path.exists(potcar_file):
        shutil.copy(potcar_file, os.path.join(input_dir, "POTCAR"))
        print(f"POTCAR copied from {os.path.dirname(vasp_file)} to {input_dir}")
    else:
        print(f"No POTCAR file found in {os.path.dirname(vasp_file)}")

    print(f"VASP inputs generated in: {input_dir}")

# Function to search for .vasp files and generate VASP inputs
def generate_vasp_inputs_in_dir(root_dir, custom_incar_params=None):
    # Walk through all subdirectories of the root directory
    for subdir, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".vasp"):  # Check if file ends with .vasp
                vasp_file = os.path.join(subdir, file)
                generate_vasp_inputs(vasp_file, custom_incar_params)


