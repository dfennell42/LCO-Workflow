# LCO Modification Workflow CLI
#### Author: Dorothea Fennell (dfennell1@bnl.gov, dfennell37@gmail.com)
**Version**: 0.8.2

---
### Important Note:
This version, as the original, was designed to work on a specific computing cluster. As such, there are specific paths/commands that will not work if you upload this to a different cluster. There is another, generalized version of this workflow that does not have that issue. It can be found here: [Delafossite-Workflow](https://github.com/dfennell42/Delafossite-Workflow/)

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

The workflow uses Atomic Simulation Environment (ASE) and Pymatgen to create/modify structures and generate VASP input files. As of right now, the workflow only supports SLURM for job submission. Any commands that submit calculations ***will not work*** with other workload managers. 

## Installation
If you would like to use the workflow as a regular installation, install the .whl file from the release. 

If you would like to use the workflow as an editable installation, install the .tar.gz file from the release. The workflow uses Poetry as a package builder and dependency manager. To use the workflow as an editable installation, refer to the [Poetry Docs](https://python-poetry.org/docs/). 

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

* `--help`: Show this message and exit.
