## LCO Modifications Workflow CLI
#### Author: Dorothea Fennell (dfennell1@bnl.gov)
**Version**: 0.4.1

A command line interface (CLI) tool for the LCO Modifications Workflow built by Jennifer Bjorklund and Dorothea Fennell.

#### Commands:
***Commands must be preceded by wf.***

*init*: Sets up directory ~/wf-user-files for user files (POSCAR, SpinPairs.txt, PDOS_INCAR.txt, vasp.sh) and other settings. These are the versions of the files the workflow will pull from, so if you modify a file, it’ll pull from this directory.

*modify*: Modifies pristine POSCAR, creates Modification_# directories, and sets up pristine surface calculations. Equivalent to bash script **run-all-LCOmod-workflow1-5.sh**. 
***NOTE:*** You must create the ModsCo.txt file yourself. 

*removepairs*: Creates Li or O vacancies in pristine structures and sets up vacancy calculations. Equivalent to bash script **run-removal-from-pristine.sh**.

*check*: Checks calculations for errors. If error is PRICELV, ZBRENT, FEXCF, or a timeout, script will perform the appropriate fix and resubmit the calculations.

*getE*: Processes data from pristine/vacancy calculations and generates two csv files: E_pristine.csv and E_vac.csv. Equivalent to bash script **process-data.sh**.

*pdos*: Sets up PDOS calculations. Equivalent to bash script **run-PDOS.sh**.

*parse*: Parses the data from the PDOS calculations to generate .dat files for each atom and integrates metal d-states. Equivalent to bash script **process-PDOS.sh**.

*integrate*: Integrates the metal d-states without parsing the files first. ***Note:*** Files must be parsed before integration. The parse command parses **AND** integrates, so this command is only if integration needs to be performed on already parsed files.

*plot*: Runs PDOS-plotter.py, which plots PDOS based on user input. 

*submit*: Submits vasp calculations. Takes argument for which type of calculations to submit: *'struc'* for pristine or vacancy structure calculations, or *'pdos'* for PDOS calculations. Default is *'struc'*. Equivalent to bash scripts **submitall-vasp.sh** and **submitpdos-vasp.sh**.

