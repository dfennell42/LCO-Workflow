# Materials WorkForge CLI
#### Author: Dorothea Fennell (dfennell1@bnl.gov, dfennell37@gmail.com)
**Version**: 0.15.0

---
### Important Note:
This package is in the process of being generalized & made ready for v1.0. As such, the documentation is currently out of date. Commands may be changed, removed, or added. 

---

A command line interface tool designed to simplify running VASP calculations for LCO. This workflow can:
- Create surface structures
- Modify composition
- Create vacancies
- Submit calculations
- Calculate vacancy energy
- Set up PDOS calculations
- Parse, integrate and plot PDOS
- Check calculations for errors, timeouts, and cancellations, fixes minor errors, and resubmits calculations
- Extract descriptors for machine learning
- Collect all relaxed structure files in one directory.

## Installing the Workflow:
The workflow can be installed in multiple ways, depending on your needs. If you want to use the workflow as-is, you can install it like any other package. This can be done by using the GitHub link and pip or by downloading the WHL file and installing it manually. 

For the LCO workflow, ***the following editable installation is recommended.*** This is due to the fact that the workflow was written to work on a specific computing cluster, and as such, some paths are hardcoded, which means they will not work if the package is installed as-is. If using the generalized Delafossite workflow, either installation is fine. 

| Note: It is *highly recommended* to install and use the workflow in a separate environment to minimize potential dependency conflicts.|
|:---|

**Editable Installation:**  
To create an editable installation, you will first need to install Poetry, which the workflow uses as a package builder and dependency manager. The Poetry docs are linked here for reference: [Poetry Docs](https://python-poetry.org/docs/). After installing Poetry, run `poetry self update`. This is the best way to make sure Poetry is up to date before setting up the installation. 

You can then install the workflow by either cloning the GitHub repository or by downloading the tar.gz file and un-tarring it in your home directory. Cloning the repository is probably the easiest way to get any updates made, but I (as of writing this) have not tried that method. It should work, but if you want to be one hundred percent certain it will work, I would recommend using the tar file. 

After installing the workflow, go into the package's head directory, which contains the *pyproject.toml* and *poetry.lock* files. Then run `poetry install` to install the workflow as a package and all necessary dependencies. If Poetry returns an error, run `poetry self update` and then try again. 

### Updating the Workflow
***Note:*** This command requires the installation of GitHub's CLI package `gh` and due to the way it's packaged, Poetry cannot add it as a dependency (believe me, I tried). The package and installation instructions are available here: [GitHub CLI](https://github.com/cli/cli). 

To update the workflow to the latest version, use command `wf update`. This command will download the latest version of the workflow from GitHub and install it. The workflow uses pip to install the new version, so if pip is not installed on your system, it will simply download the wheel file to your home directory. 

If you prefer to install the workflow as an editable package, use option `--editable` or `-e` to download the tar file instead. 

## Using the Workflow:  
### See the workflow guide here: [Workflow Guide](Workflow_Guide.md)

## Workflow Commands (`wf`):

**Usage**:

```console
$ wf [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `-v, --version`
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `init`: Initializes workflow settings.
* `generate`: Generates surface structure based on bulk structure and user input.
* `modify`: Modifies LCO structure based on user input.
* `heo`: Generates random modifications for HEO...
* `removepairs`: Removes Li/O pairs from structures.
* `removeatoms`: Removes single Li or O atoms, ignoring...
* `addpairs`: Adds pairs of atoms to structures.
* `addatoms`: Adds single atoms to structures.
* `gete`: Generates E_pristine, E_vac, and E_ads CSV...
* `pdos`: Sets up PDOS calculations.
* `parse`: Parses PDOS data into individual files and...
* `integrate`: Integrates already parsed PDOS files.
* `plot`: Plots PDOS based on user input.
* `chgdiff`: Generates CHGDIFF.cube file and plots charge difference.
* `extract`: Gets ML descriptors from PDOS and...
* `submit`: Submits VASP calculations.
* `check`: Checks vasp.out for errors and fixes and...
* `collect`: Collects all CONTCAR files in Structures...
* `update`: Checks workflow version and updates if...
* `extall`: Runs descriptor extraction for all...

## `init`

Initializes workflow settings.

**Usage**:

```console
$ init [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `generate`

Generates surface structure based on bulk structure and user input. Bulk structure can be given as a file or as a Materials Project ID. Workflow will also prompt for supercell size and Miller index.
    
If command line options are provided, workflow will bypass input sections for the provided information. 
    
Note: If using Materials Project, an API key MUST be provided.

**Usage**:

```console
$ generate [OPTIONS]
```

**Options**:

* `-b, --bulk TEXT`: Path to bulk file or Material Project ID.
* `-s, --sc-size TEXT`: Supercell size given as set of vectors or list of scaling factors.
* `-m, --miller TEXT`: Miller index of facet, given as comma-separated list.
* `-v, --vacuum INTEGER`: Thickness of vacuum layer, in angstrom (Å). Default is 10 Å.
* `--help`: Show this message and exit.

## `modify`

Modifies LCO structure based on user input. Needs ModsCo.txt

**Usage**:

```console
$ modify [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `heo`

Generates random modifications for HEO structures based on user input, ignoring symmetry.

**Usage**:

```console
$ heo [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `removepairs`

Removes Li/O pairs from structures.

**Usage**:

```console
$ removepairs [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `removeatoms`

Removes single Li or O atoms, ignoring symmetry.

**Usage**:

```console
$ removeatoms [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `addpairs`

Adds pairs of atoms to structures.

**Usage**:

```console
$ addpairs [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `addatoms`

Adds single atoms to structures.

**Usage**:

```console
$ addatoms [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `gete`

Generates E_pristine, E_vac, and E_ads CSV files.

**Usage**:

```console
$ gete [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `pdos`

Sets up PDOS calculations.

**Usage**:

```console
$ pdos [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `parse`

Parses PDOS data into individual files and integrates.

**Usage**:

```console
$ parse [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `integrate`

Integrates the PDOS files. 
    
Note: Files MUST be parsed before integration. The parse command parses AND integrates, so this command should only be used if integration needs to be performed on already parsed files.

**Usage**:

```console
$ integrate [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `plot`

Plots PDOS based on user input.

**Usage**:

```console
$ plot [OPTIONS]
```

**Options**:

* `-n, --no-show-image`: Do not display plot in X11 window after running command.
* `--help`: Show this message and exit.

## `chgdiff`

Generates CHGDIFF.cube file from pristine and vacancy CHGCAR files and visualizes the charge difference. 
Note: CHGCAR files MUST have the same size real space grids.

**Usage**:

```console
$ chgdiff [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `extract`

Gets ML descriptors from PDOS and optimization calculations.

**Usage**:

```console
$ extract [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `submit`

Submits VASP calculations.

**Usage**:

```console
$ submit [OPTIONS] [CALC]
```

**Arguments**:

* `[CALC]`: The type of calculation to submit. Options: struc: Pristine or vacancy surface calculations. pdos: PDOS calculations  [default: struc]

**Options**:

* `-v, --vac`: Run only vacancy calculations. Does not work with calc = pdos
* `-a, --add`: Run only adsorption calculations. Does not work with calc = pdos
* `-f, --force`: Submits ALL calculations, including those that have been run before.
* `--help`: Show this message and exit.

## `check`

Checks vasp.out for errors and fixes and resubmits calculations if possible.

**Usage**:

```console
$ check [OPTIONS]
```

**Options**:

* `-n, --no-submit`: Use -n or --no-submit to run check without autosubmitting calculations
* `--help`: Show this message and exit.

## `collect`

Collects all CONTCAR files in Structures directory.

**Usage**:

```console
$ collect [OPTIONS]
```

**Options**:

* `-f, --force`: Forces file copying, replacing existing files.
* `-p, --parent TEXT`: Force set the name of the parent structure
* `-g, --group TEXT`: Force set the name of the group of calculations
* `--help`: Show this message and exit.

## `update`

Checks workflow version and updates if necessary.

**Usage**:

```console
$ update [OPTIONS]
```

**Options**:

* `-e, --editable`: Install the workflow as an editable package.
* `--help`: Show this message and exit.

## `extall`

Runs descriptor extraction for all directories.

**Usage**:

```console
$ extall [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.
