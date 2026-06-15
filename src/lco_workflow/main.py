#import modules
import typer
from typing_extensions import Annotated
import os
import sys
import shutil
#import from files
from . import version
#bash script run-all
from .modifyLCO import modify_lco
from .MagMom_recursive import process_poscar_files
from .POTCAR_cat import process_directories
from .VASP_input import generate_vasp_inputs_in_dir
from .modINCAR import update_incar_files_with_magmom
#modify heo
from .gen_random_mods import generate_mods_file
from .modify_heo import modify_without_sym
#bash script run-removal
from .remove_li_o_pairs import process_vasp_inputs
from .removed_pairs_INCARmod import process_pairs_mod_dirs
#remove atoms
from .remove_atoms import process_vasp_inputs_nosym
#add pairs
from .add_pairs import process_vasp_dirs
#add atoms
from .add_atoms import process_vasp_dirs_nosym
#bash script process data
from .get_e_pristine import get_all_e
from .Calc_Evac import process_e_vac
from .calc_Eads import process_e_ads
#bash script run pdos
from .createPDOS import process_vasp_inputs as pdos_vasp_inputs
from .pdos_INCARmod import process_pdos_dirs
#bash script process pdos
from .vasp_pdos import process_pdos_dirs as parse_pdos_dirs
from .integrate_pdos import integrate_all_pdos
from .tot_int import get_all_data
#plot pdos
from .PDOS_plotter import plot_pdos
#initialize
from .initialize import init_settings
#error check
from .err_check import err_fix
#descriptor extraction
from .get_descriptors import extract_desc
from .collect_descriptors import collect_descriptors
#collecting CONTCAR files
from .collect_contcar import copy_all_files
#update command
from .wf_update import check_vrsn
#chg diff
from .chg_diff import get_chgdiff
#generate structures
from .bulk_to_sc import create_structure
#create app
app = typer.Typer(context_settings={"help_option_names": ["-h", "--help"]})

#create callback for version
@app.callback(invoke_without_command=True)
def vrsn_callback(
        ctx: typer.Context,
        vrsn: Annotated[bool, typer.Option("--version", '-v')] = False
         ):
    if ctx.invoked_subcommand is None and vrsn == True:
        print(f'LCO workflow version is {version}')
#create commands
@app.command()
def init():
    '''Initializes workflow settings.'''
    init_settings()

@app.command(short_help='Generates surface structure based on bulk structure and user input.')
def generate(
        bulk: Annotated[str | None, typer.Option('--bulk','-b', help='Path to bulk file or Material Project ID.',show_default=False)] = None,
        sc_size: Annotated[str | None, typer.Option('--sc-size','-s', help='Supercell size given as set of vectors or list of scaling factors.',show_default=False)] = None,
        miller: Annotated[str | None, typer.Option('--miller','-m', help='Miller index of facet, given as comma-separated list.',show_default=False)] = None, 
        vacuum: Annotated[int, typer.Option('--vacuum','-v',help='Thickness of vacuum layer, in angstrom (Å). Default is 10 Å.',show_default=False)] = 10,
        ):
    '''
    Generates surface structure based on bulk structure and user input. Bulk structure can be given as a file or as a Materials Project ID. Workflow will also prompt for supercell size and Miller index.
    \nIf command line options are provided, workflow will bypass input sections for the provided information. 
    \nNote: If using Materials Project, an API key MUST be provided. 
    '''
    create_structure(bulk,sc_size,miller,vacuum)

@app.command()
def modify():
    '''Modifies LCO structure based on user input. Needs ModsCo.txt '''
    modify_lco()
    process_poscar_files(mod=None,ignore_sym=False)
    process_directories("/hpcgpfs01/ic2software/vasp6/6.4.2/PSEUDOPOTENTIAL/PBE/", vac = False, add=False)
    generate_vasp_inputs_in_dir(os.getcwd(),custom_incar_params = {
        "ENCUT": 520,
        "ISIF": 3,
        "ISMEAR": 0,
        "SIGMA": 0.05,
        "EDIFF": 1e-5,
        "EDIFFG": -0.02,
        "LWAVE": False,
        "LCHARG": False,
    })
    update_incar_files_with_magmom(os.getcwd(),comment_ldau=True,ignore_sym=False)

@app.command()
def heo():
    '''Generates random modifications for HEO structures based on user input, ignoring symmetry.'''
    generate_mods_file()
    modify_without_sym(os.getcwd())
    process_poscar_files(mod=None, ignore_sym=True)
    process_directories("/hpcgpfs01/ic2software/vasp6/6.4.2/PSEUDOPOTENTIAL/PBE/", vac = False, add=False)
    generate_vasp_inputs_in_dir(os.getcwd(),frozen=True,custom_incar_params = {
        "ENCUT": 520,
        "ISIF": 2,
        "ISMEAR": 0,
        "SIGMA": 0.05,
        "EDIFF": 1e-5,
        "EDIFFG": -0.02,
        "LWAVE": False,
        "LCHARG": False,
    })
    update_incar_files_with_magmom(os.getcwd(),comment_ldau=True,ignore_sym=True)

@app.command()
def removepairs():
    '''Removes Li/O pairs from structures. '''
    element_name = process_vasp_inputs(os.getcwd())
    process_pairs_mod_dirs(os.getcwd(),element_name, 'Removed', ignore_sym=False)
    process_directories("/hpcgpfs01/ic2software/vasp6/6.4.2/PSEUDOPOTENTIAL/PBE/", vac = True, add=False)

@app.command()
def removeatoms():
    '''Removes single Li or O atoms, ignoring symmetry.'''
    element_name = process_vasp_inputs_nosym(os.getcwd())
    process_pairs_mod_dirs(os.getcwd(), element_name, 'Removed',ignore_sym= True)
    process_directories("/hpcgpfs01/ic2software/vasp6/6.4.2/PSEUDOPOTENTIAL/PBE/", vac = True, add=False)

@app.command()
def addpairs():
    '''Adds pairs of atoms to structures.'''
    element_name = process_vasp_dirs(os.getcwd())
    process_pairs_mod_dirs(os.getcwd(), element_name, 'Added',ignore_sym=False)
    process_directories("/hpcgpfs01/ic2software/vasp6/6.4.2/PSEUDOPOTENTIAL/PBE/", vac=False, add=True)

@app.command()
def addatoms():
    '''Adds single atoms to structures.'''
    element_name = process_vasp_dirs_nosym(os.getcwd())
    process_pairs_mod_dirs(os.getcwd(), element_name, 'Added',ignore_sym=True)
    process_directories("/hpcgpfs01/ic2software/vasp6/6.4.2/PSEUDOPOTENTIAL/PBE/", vac=False, add=True)

@app.command()
def gete():
    '''Generates E_pristine, E_vac, and E_ads CSV files.'''
    get_all_e(os.getcwd())
    process_e_vac(os.getcwd())
    process_e_ads(os.getcwd())
    
@app.command()
def pdos():
    '''Sets up PDOS calculations.'''
    pdos_vasp_inputs(os.getcwd())
    process_pdos_dirs(os.getcwd())
    
@app.command()
def parse():
    '''Parses PDOS data into individual files and integrates.'''
    parse_pdos_dirs(os.getcwd())
    integrate_all_pdos(os.getcwd())
    get_all_data(os.getcwd())
    
@app.command(short_help='Integrates already parsed PDOS files.')
def integrate():
    '''
    Integrates the PDOS files. 
    \nNote: Files MUST be parsed before integration. The parse command parses AND integrates, so this command should only be used if integration needs to be performed on already parsed files.
    '''
    integrate_all_pdos(os.getcwd())
    get_all_data(os.getcwd())
    
@app.command()
def plot(
        no_show:Annotated[bool,typer.Option('--no-show-image','-n',help='Do not display plot in X11 window after running command.',show_default=False)] = False,
        ):
    '''Plots PDOS based on user input.'''
    plot_pdos(os.getcwd(),no_show)

@app.command(short_help='Generates CHGDIFF.cube file and plots charge difference.')
def chgdiff(
        no_show:Annotated[bool,typer.Option('--no-show-image','-n',help='Do not display plot in X11 window after running command.',show_default=False)] = False,
        ):
    '''
    Generates CHGDIFF.cube file from pristine and vacancy CHGCAR files and visualizes the charge difference. 
    Note: CHGCAR files MUST have the same size real space grids.
    '''
    get_chgdiff(no_show)
    
@app.command()
def extract():
    '''Gets ML descriptors from PDOS and optimization calculations.'''
    extract_desc(os.getcwd())
    
@app.command()
def submit(
        calc: Annotated[str, typer.Argument(help='The type of calculation to submit. Options: struc: Pristine or vacancy surface calculations. pdos: PDOS calculations')] = 'struc',
        vac:Annotated[bool,typer.Option("--vac","-v",help='Run only vacancy calculations. Does not work with calc = pdos')] = False,
        add: Annotated[bool,typer.Option("--add","-a",help='Run only adsorption calculations. Does not work with calc = pdos')] = False,
        force: Annotated[bool, typer.Option("--force","-f",help="Submits ALL calculations, including those that have been run before.")] = False,
        ):
    '''Submits VASP calculations.'''
    pkgdir = sys.modules['lco_workflow'].__path__[0]
    filedir = os.path.expanduser('~/wf-user-files')
    fullpath = os.path.join(filedir, 'vasp.sh')
    shutil.copy(fullpath, os.getcwd())
    fpath = os.path.join(pkgdir,'submitall-vasp.sh')
    if calc.lower() == 'struc':
        if vac:
            calc_type = "*_Removed"
        elif add:
            calc_type = "*_Added"
        else:
            calc_type = "all"
    elif calc.lower() == 'pdos':
        calc_type = "PDOS"
    if force == True:
        force = "true"
    elif force == False:
        force = "false"
    os.system(f'bash {fpath} {calc_type} {force}')
        
@app.command()
def check(
        no_submit:Annotated[bool,typer.Option("--no-submit","-n",help='Use -n or --no-submit to run check without autosubmitting calculations',show_default=False)] = False
        ):
    '''Checks vasp.out for errors and fixes and resubmits calculations if possible.'''
    err_fix(os.getcwd(),no_submit)

@app.command()
def collect(
        force:Annotated[bool,typer.Option("--force", "-f",help='Forces file copying, replacing existing files.')] = False,
        parent:Annotated[str,typer.Option("--parent","-p",help='Force set the name of the parent structure')] = None,
        group:Annotated[str,typer.Option("--group","-g",help='Force set the name of the group of calculations')] = None,
        ):
    '''Collects all CONTCAR files in Structures directory.'''
    copy_all_files(os.getcwd(),force,parent,group)

@app.command()
def update(
        editable:Annotated[bool,typer.Option("--editable",'-e',help='Install the workflow as an editable package.')] = False,
):
    '''Checks workflow version and updates if necessary.'''
    if editable == True:
        suffix = '.tar.gz'
    elif editable == False:
        suffix = '.whl'
    check_vrsn(suffix)
    
@app.command()
def extall():
    '''Runs descriptor extraction for all directories.'''
    collect_descriptors()
