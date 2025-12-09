# LCO Workflow Guide
This guide will assist in running the python-based workflow designed to assist in setting up, submitting, and processing VASP calculations for LCO and LCO-derivatives. The workflow uses Atomic Simulation Environment (ASE) and Pymatgen to create/modify structures and generate VASP input files. The workflow was built into a command-line interface (CLI) with Typer and then into a package with Poetry. 

As of right now, the workflow only supports SLURM for job submission. Any commands that submit calculations ***will not work*** with other workload managers. 

## Installing the Workflow:
The workflow can be installed in multiple ways, depending on your needs. If you want to use the workflow as-is, you can install it like any other package. This can be done by using the GitHub link and pip or by downloading the WHL file and installing it manually. 

For the LCO workflow, ***the following editable installation is recommended.*** This is due to the fact that the workflow was written to work on a specific computing cluster, and as such, some paths are hardcoded, which means they will not work if the package is installed as-is. If using the generalized Delafossite workflow, either installation is fine. 

To create an editable installation, you will first need to install Poetry, which the workflow uses as a package builder and dependency manager. The Poetry docs are linked in the README for reference. After installing Poetry, run `poetry self update`. This is the best way to make sure Poetry is up to date before setting up the installation. 

You can then install the workflow by either cloning the GitHub repository or by downloading the tar.gz file and un-tarring it in your home directory. Cloning the repository is probably the easiest way to get any updates made, but I (as of writing this) have not tried that method. It should work, but if you want to be one hundred percent certain it will work, I would recommend using the tar file. 

After installing the workflow, go into the package's head directory, which contains the *pyproject.toml* and *poetry.lock* files. Then run `poetry install` to install the workflow as a package and all necessary dependencies. If Poetry returns an error, run `poetry self update` and then try again. 

## Using the Workflow:
The following guide explains the process of using the workflow, regardless of installation type. 
### Setting Up the Workflow:
To set up the workflow, run `wf init`. This command creates a new directory in the user's home directory called `~/wf-user-files`. The workflow will then copy several files to the directory.

If running the LCO workflow, the workflow will copy four files to the directory: A POSCAR file of a 3x2, half-Li terminated, inversion symmetric LCO supercell, a text file assigning the spin pairs to the cell called "SpinPairs.txt", a text file containing the parameters for the PDOS calculations called "PDOS_INCAR.txt", and a Bash submission script for SLURM called "vasp.sh". 

If running the Delafossite workflow, the workflow will copy the above files, as well as three additional files. The first is "BulkE_dict.txt", which contains the ground state energy for a single atom of various atomic species in the bulk state. These energies are used to calculate the vacancy energy in later steps. This file contains energies for H and O as well, which ***are already corrected.*** The next file is "MagMom_dict.txt" which contains base magnetic moment values for a number of species. If a species is not listed in the file, the workflow assigns a base value of 0.6. The final is "custom_incar_params.txt" which contains the INCAR parameters for the optimization calculations. The POSCAR, SpinPairs.txt, and vasp.sh files are in a subdirectory called `./example_files`. 

If running the Delafossite workflow, the command will also ask you to provide the path to the folder containing the VASP pseudopotentials and sets it as an environment variable. 

### Preparing to Run Calculations:
Before running any calculations, a series of files must be provided by the user. These are as follows:
1. A base POSCAR file that is **inversion symmetric**. This is important not only for reducing calculation time, but all structural modifications made by the workflow are *done in pairs.*
2. A file denoting the spin pairs of the cell, titled “SpinPairs.txt”. This is necessary due to the antiferromagnetic ordering of LCO and delafossites, and allows the calculations to run spin polarized. 
3. A submission script to submit the calculations to the SLURM job queue, ***titled vasp.sh***. The file must be titled "vasp.sh" or the submission command ***will not*** work. 

Examples of all three files are provided in the workflow package and are copied to the user’s `~/wf-user-files` directory. 

### Setting Up Calculations:
The workflow is designed to run recursively, and will process a whole set of calculations at a time. To organize calculations, it's recommended to create a new directory for each set. The following guide will assume you're starting in an empty directory and setting up a new set of calculations.

#### Mods File:
To prepare a set of calculations, the user provides a file that lists the new structures the user wishes to create, one per line. Each line contains indices of the pairs to be changed, followed by the replacement species. These indices are of the atom **pairs**, not the index of the individual atoms. This is due to the inversion symmetry of the supercell. The file should look like this:

>1,2,Ni,Mn  
2,5,8,Ni,Ni,Al  
3,4,5,7,Ni,Fe,Al,Mn  

Each line creates a modification directory. If there are blank lines in the file, the workflow will interpret those as modifications as well, even if there are no modifications listed.

If running the LCO workflow, the file must be titled **"ModsCo.txt"**.  
If running the Delafossite workflow, the file must be titled **"Mods.txt"**. 

If you're not certain of the pair indices, create a blank mods file, then run command `wf modify` which will generate text files listing the atom pairs. 

#### Modifying Structures:
Following the creation of the Mods file, run command `wf modify`. The LCO workflow will automatically modify the Co atoms, while the Delafossite version will prompt the user as to which element pairs they want to replace. The workflow will create a new directory for each modification, titled `/Modification_{#}` where {#} is replaced by the line number in the Mods file. It then modifies the base POSCAR using Atomic Simulation Environment (ASE) and generates the VASP input files using Pymatgen in subdirectory `/VASP_inputs`. 

#### Creating Vacancies:
In addition to replacing atoms, the workflow can also create vacancies. To create vacancies, run command `wf removepairs`. The workflow will then prompt the user to determine if the new vacancies should be generated from the pristine structures or from existing vacancy structures, which species should be removed, and the index of the pair(s) to be removed. The workflow then modifies the structures and generates the input files in a new subdirectory under `VASP_inputs` called `{Element}_Pairs_Removed` where {Element} is the symbol of the species removed. 

This command can be used repeatedly to create multiple vacancies. 

### Running Calculations:
Once the set of structures has been created and all desired vacancy structures have been generated, the user executes the command `wf submit`. This command copies the Bash submission script to each directory, then submits each calculation to the scheduling queue. By default, the workflow will submit all structural optimization calculations for pristine and vacancy structures. However, if the user wishes to only submit calculations for the vacancy structures, the command can be executed with `--vac` or `-v`. 

To check if the calculations have completed properly, the user can execute `wf check`. Any errors returned are printed to the command line. In addition to VASP errors, the workflow will also check if the calculations are still running, were cancelled, or timed out. 

The workflow will also fix certain errors. For cancelation, timeout, 'ZBRENT', or 'FEXCF' errors, the workflow will copy CONTCAR to POSCAR or for 'PRICELV' errors, the workflow will add 'ISYM = -1' to INCAR. It will then resubmit any fixed calculations. If you want to check calculations without submitting any calculations, execute the command with `--no-submit` or `-n`. 

If no errors are found, the workflow will return "No errors found. All calculations complete.”

### Calculating Vacancy Energies
Following structural optimization, the user can execute command `wf gete`. This command extracts the ground state energies from the output files and produces two CSV files: "E_pris.csv" and "E_vac.csv". The first contains the modification directory, the modification (as read from the Mods file), and the ground state energies (eV) of the pristine structures. The second contains the modification directory, the modification, which species was removed, the number of atoms removed, the ground state energy (eV), and the vacancy energy (eV) of all vacancy structures. If the vacancy in question is a secondary vacancy (i.e. an oxygen vacancy following a lithium vacancy) the workflow calculates the vacancy energy from the previous vacancy structure rather than the pristine surface. 

The vacancy energy is calculated as follows:

$$E_{vac}=(E_{vs}+N_a*E_a)-E_{pris}$$
