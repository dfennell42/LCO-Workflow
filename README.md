# `LCO-Workflow`

**Usage**:

```console
$ LCO-Workflow [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `-v, --version`
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
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

## `LCO-Workflow init`

Initializes workflow settings.

**Usage**:

```console
$ LCO-Workflow init [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `LCO-Workflow modify`

Modifies LCO structure based on user input. Needs ModsCo.txt

**Usage**:

```console
$ LCO-Workflow modify [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `LCO-Workflow removepairs`

Removes Li/O pairs from structures

**Usage**:

```console
$ LCO-Workflow removepairs [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `LCO-Workflow gete`

Gets pristine E and E vac

**Usage**:

```console
$ LCO-Workflow gete [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `LCO-Workflow pdos`

sets up PDOS calculations

**Usage**:

```console
$ LCO-Workflow pdos [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `LCO-Workflow parse`

Parses PDOS data into individual files and integrates

**Usage**:

```console
$ LCO-Workflow parse [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `LCO-Workflow integrate`

Integrates the PDOS files. Note: Files must be parsed before integration. The parse command parses AND integrates, so this command is only if integration needs to be performed on already parsed files.

**Usage**:

```console
$ LCO-Workflow integrate [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `LCO-Workflow plot`

Plots PDOS

**Usage**:

```console
$ LCO-Workflow plot [OPTIONS]
```

**Options**:

* `-n, --no-show-image`: Do not display plot in X11 window after running command.
* `--help`: Show this message and exit.

## `LCO-Workflow extract`

Gets ML descriptors from PDOS and optimization calculations.

**Usage**:

```console
$ LCO-Workflow extract [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `LCO-Workflow submit`

Submits vasp calculations.

**Usage**:

```console
$ LCO-Workflow submit [OPTIONS] [CALC]
```

**Arguments**:

* `[CALC]`: The type of calculation to submit. Options: struc: Pristine or vacancy surface calculations. pdos: PDOS calculations  [default: struc]

**Options**:

* `-v, --vac`: Run only vacancy calculations. Does not work with calc = pdos
* `--help`: Show this message and exit.

## `LCO-Workflow check`

Checks vasp.out for errors and fixes and resubmits calculations if possible.

**Usage**:

```console
$ LCO-Workflow check [OPTIONS]
```

**Options**:

* `-n, --no-submit`: Use -n or --no-submit to run check without autosubmitting calculations
* `--help`: Show this message and exit.

## `LCO-Workflow collect`

Collects all CONTCAR files in Structures directory.

**Usage**:

```console
$ LCO-Workflow collect [OPTIONS]
```

**Options**:

* `-f, --force`: Forces file copying, replacing existing files.
* `-p, --parent TEXT`: Force set the name of the parent structure
* `-g, --group TEXT`: Force set the name of the group of calculations
* `--help`: Show this message and exit.

## `LCO-Workflow update`

Checks workflow version and updates if necessary.

**Usage**:

```console
$ LCO-Workflow update [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.
