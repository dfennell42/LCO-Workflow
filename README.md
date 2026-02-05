# LCO Modification Workflow CLI
#### Author: Dorothea Fennell (dfennell1@bnl.gov, dfennell37@gmail.com)
**Version**: 0.10.2

---
### Important Note:
This version, as the original, was designed to work on a specific computing cluster. As such, there are specific paths/commands that will not work if you upload this to a different cluster. There is another, generalized version of this workflow that does not have that issue. It can be found here: [Delafossite-Workflow](https://github.com/dfennell42/Delafossite-Workflow/)

However, if you prefer to use this version, follow the instructions for the editable installation below. 

---

A command line interface tool designed to simplify running VASP calculations for LCO. This workflow can:
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
* `--help`: Show this message and exit.

**Commands**:

* `init`: Initializes workflow settings.
* `modify`: Modifies LCO structure based on user input.
* `removepairs`: Removes Li/O pairs from structures
* `gete`: Gets pristine E and E vac
* `pdos`: sets up PDOS calculations
* `parse`: Parses PDOS data into individual files and...
* `integrate`: Integrates the PDOS files.
* `plot`: Plots PDOS
* `extract`: Gets ML descriptors from PDOS and...
* `submit`: Submits vasp calculations.
* `check`: Checks vasp.out for errors and fixes and...
* `collect`: Collects all CONTCAR files in Structures...
* `update`: Checks workflow version and updates if...
* `extall`: Runs descriptor extraction for all directories.

## `wf init`

Initializes workflow settings.

**Usage**:

```console
$ wf init [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `wf modify`

Modifies LCO structure based on user input. Needs ModsCo.txt

**Usage**:

```console
$ wf modify [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `wf removepairs`

Removes Li/O pairs from structures

**Usage**:

```console
$ wf removepairs [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `wf gete`

Gets pristine E and E vac

**Usage**:

```console
$ wf gete [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `wf pdos`

sets up PDOS calculations

**Usage**:

```console
$ wf pdos [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `wf parse`

Parses PDOS data into individual files and integrates

**Usage**:

```console
$ wf parse [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `wf integrate`

Integrates the PDOS files. Note: Files must be parsed before integration. The parse command parses AND integrates, so this command is only if integration needs to be performed on already parsed files.

**Usage**:

```console
$ wf integrate [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `wf plot`

Plots PDOS

**Usage**:

```console
$ wf plot [OPTIONS]
```

**Options**:

* `-n, --no-show-image`: Do not display plot in X11 window after running command.
* `--help`: Show this message and exit.

## `wf extract`

Gets ML descriptors from PDOS and optimization calculations.

**Usage**:

```console
$ wf extract [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `wf submit`

Submits vasp calculations.

**Usage**:

```console
$ wf submit [OPTIONS] [CALC]
```

**Arguments**:

* `[CALC]`: The type of calculation to submit. Options: struc: Pristine or vacancy surface calculations. pdos: PDOS calculations  [default: struc]

**Options**:

* `-v, --vac`: Run only vacancy calculations. Does not work with calc = pdos
* `--help`: Show this message and exit.

## `wf check`

Checks vasp.out for errors and fixes and resubmits calculations if possible.

**Usage**:

```console
$ wf check [OPTIONS]
```

**Options**:

* `-n, --no-submit`: Use -n or --no-submit to run check without autosubmitting calculations
* `--help`: Show this message and exit.

## `wf collect`

Collects all CONTCAR files in Structures directory.

**Usage**:

```console
$ wf collect [OPTIONS]
```

**Options**:

* `-f, --force`: Forces file copying, replacing existing files.
* `-p, --parent TEXT`: Force set the name of the parent structure
* `-g, --group TEXT`: Force set the name of the group of calculations
* `--help`: Show this message and exit.

## `wf update`

Checks workflow version and updates if necessary.

**Usage**:

```console
$ wf update [OPTIONS]
```

**Options**:
* `-e, --editable`: Install the workflow as an editable package. 
* `--help`: Show this message and exit.

## `wf extall`

Runs descriptor extraction for all directories.

**Usage**:

```console
$ wf extall [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.