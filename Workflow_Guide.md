# Workflow Guide:
To install the workflow, follow the instructions in [README.md](). The following guide will assist in running the python-based workflow designed to assist in setting up, submitting, and processing VASP calculations for LCO and LCO-derivatives. The workflow uses Atomic Simulation Environment (ASE) and Pymatgen to create/modify structures and generate VASP input files. The workflow was built into a command-line interface (CLI) with Typer and then into a package with Poetry. 

As of right now, the workflow only supports SLURM for job submission. Any commands that submit calculations ***will not work*** with other workload managers. 

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

### Calculating Vacancy Energies:
Following structural optimization, the user can execute command `wf gete`. This command extracts the ground-state energies from the output files and produces two CSV files: "E_pris.csv" and "E_vac.csv". The first contains the modification directory, the modification (as read from the Mods file), and the ground-state energies (eV) of the pristine structures. The second contains the modification directory, the modification, which species was removed, the number of atoms removed, the ground-state energy, and the vacancy energy (eV) of all vacancy structures. If the vacancy in question is a secondary vacancy (i.e. an oxygen vacancy following a lithium vacancy) the workflow calculates the vacancy energy from the previous vacancy structure rather than the pristine surface. 

The vacancy energy is calculated as follows:

$$E_{vac}=(E_{vs}+N_a*E_a)-E_{pris}$$

Where E<sub>vac</sub> is the vacancy energy, E<sub>vs</sub> is the ground-state energy of the vacancy structure, N<sub>a</sub> is the number of atoms removed, E<sub>a</sub> is the ground-state energy of a single atom in the bulk of the removed species, and E<sub>pris</sub> is the ground-state energy of the pristine structure. All energies are given in eV. 

***Important Note:*** *While atoms are removed in pairs due to the cell's inversion symmetry, all vacancy energies are reported **<ins>per atom.</ins>***

### PDOS Calculations:
Once the structural optimizatons are complete, the user can then set up PDOS calculations by executing command `wf pdos`. The workflow will prompt the user on whether to set PDOS up for the pristine or vacancy structures. Following the user's choice, the workflow will create a new subdirectory in the appropriate location, titled `./PDOS`. It will then copy the appropriate input files to the directory, using the CONTCAR from the optimization calculations as POSCAR, and modify INCAR based on "PDOS_INCAR.txt". 

Once the calculations have been set up, the user can submit them using command `wf submit pdos`. 

### PDOS Post-Processing:
#### Parsing & Integration:
After the PDOS commands have finished, the user can execute command `wf parse`. This command processes DOSCAR into individual files for each atom in the structure. It creates two files for each atom, one with the PDOS broken out by individual orbitals (p<sub>x</sub>, p<sub>y</sub>, p<sub>z</sub>, etc.) and one with the orbitals summed by type (all p orbitals summed, etc.). The files are called "{Element}{idx}.dat" and "{Element}{idx}_total.dat" respectively, where {Element} is the symbol for the atomic species and {idx} is the index of the atom. For the files with the summed orbitals, the energies are reported relative to the Fermi energy. The workflow also creates a file called "TotalDos.dat" that contains the DOS for the whole structure. 

After parsing out the files, the workflow will integrate the summed valence orbitals of the PDOS using Simpson's rule, and returns a CSV in each PDOS directory with the atom, atom index, calculated number of valence electrons, oxidation state, spin, and valence orbital. If using the LCO workflow, the integration will also return the hybridization term, which attempts to capture the hybridization of the metal d- and oxygen p-orbitals. The lower bounds are chosen relative to the energies of the valence electrons as given in the pseudopotential files, and the upper bound is zero.
>*Integration windows:*   
s-block: -20 to 0 eV  
p-block: -10 to 0 eV  
d-block: -10 to 0 eV  
f-block: -15 to 0 eV

For the LCO workflow, the workflow only integrates for the transition metals, while in the Delafossite workflow, it will integrate for all atoms in the structure. For the LCO workflow, it will also create a CSV file in the head directory called "selected-int-pdos.csv", which will contain the integration data for the transition metals in sites 21, 23, and 25 (indices from pristine structure) for each modification directory.  

The workflow then creates a CSV file in the head directory titled "tot-int-pdos.csv", which contains the integration data of all the modifications, with the data broken out by modification directory. 

#### Plotting PDOS: 
The workflow can also visualize and plot PDOS using command `wf plot`. The workflow will prompt the user for the following: 
1. Which modification directories to plot for. 
2. Whether to plot all available PDOS, just pristine, or just vacancy PDOS. 
3. Which atoms the user wants to plot, or if they want to plot the total DOS.  
4. If plotting for individual atoms, whether the user wants to plot the individual orbitals (p<sub>x</sub>, p<sub>y</sub>, p<sub>z</sub>, etc.) or summed orbitals (all p summed, etc.).
5. If plotting multiple atoms, whether they want to plot the PDOS individually or in one larger graph with subplots. 
6. If plotting one larger plot, the workflow will prompt the user for a graph title.

Additionally, if the user types "exit" into any of the above prompts, the script will abort. 

Using the given information, the workflow then plots the PDOS, saves it as a PNG file to the PDOS directory, and displays the image in an X11 window. If you wish to plot and save the PDOS without displaying them, the command can be run with option `--no-show-image` or `-n`. 

### Additional Commands: LCO Workflow ONLY
The following two commands are only included in the LCO version of the workflow, due to their specificity.
##### `wf extract`: 
This command extracts descriptors for use in machine learning. This command was not included in the Delafossite workflow because all the extracted descriptors were specific to the research question, and it would be difficult to generalize.

##### `wf collect`:
This command collects all the output structure files (CONTCAR) into a series of directories based on structure type, vacancies, and calculation type. All the filepaths in this command are hard-coded to locations on the computing cluster the workflow was built on, which makes it, again, difficult to generalize. A generalizable version could potentially be made in the future, but it was not a priority when building the delafossite workflow. 
