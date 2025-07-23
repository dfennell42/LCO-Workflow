#import modules
import typer
from typing_extensions import Annotated
import os
import sys
import shutil
#import from files
#bash script run-all
from .modifyLCO import modify_lco
from .MagMom_recursive import process_poscar_files
from .POTCAR_cat import process_directories
from .VASP_input import generate_vasp_inputs_in_dir
from .modINCAR import update_incar_files_with_magmom
#bash script run-removal
from .remove_li_o_pairs import process_vasp_inputs
from .removed_pairs_INCARmod import process_pairs_removed_dirs
#bash script process data
from .get_e_pristine import get_all_e
from .Calc_Evac import process_e_vac
#bash script run pdos
from .createPDOS import process_vasp_inputs as pdos_vasp_inputs
from .pdos_INCARmod import process_pdos_dirs
#bash script process pdos
from .vasp_pdos import process_pdos_dirs as parse_pdos_dirs
from .integrate_pdos import integrate_all_pdos
#plot pdos
from .PDOS_plotter import plot_pdos
#initialize
from .intialize import init_settings
#error check
from .err_check import err_fix

#create app
app = typer.Typer(context_settings={"help_option_names": ["-h", "--help"]})

#create commands
@app.command()
def init():
    '''Initializes workflow settings.'''
    pot_path = init_settings()
    return pot_path

@app.command()
def modify(pot_path):
    '''Modifies LCO structure based on user input. Needs Mods.txt '''
    modify_lco()
    process_poscar_files()
    process_directories(pot_path, vac = False)
    generate_vasp_inputs_in_dir(os.getcwd())
    update_incar_files_with_magmom(os.getcwd(),comment_ldau=True)

@app.command()
def removepairs(pot_path):
    '''Removes Li/O pairs from structures '''
    choice = process_vasp_inputs(os.getcwd())
    process_pairs_removed_dirs(os.getcwd(),choice)
    process_directories(pot_path, vac = True)
@app.command()
def gete():
    '''Gets pristine E and E vac '''
    get_all_e(os.getcwd())
    process_e_vac(os.getcwd())
    
@app.command()
def pdos():
    '''sets up PDOS calculations'''
    pdos_vasp_inputs(os.getcwd())
    process_pdos_dirs(os.getcwd())
    
@app.command()
def parse():
    '''Parses PDOS data into individual files and integrates '''
    parse_pdos_dirs(os.getcwd())
    integrate_all_pdos(os.getcwd())
    
@app.command()
def integrate():
    '''Integrates the PDOS files. Note: Files must be parsed before integration. The parse command parses AND integrates, so this command is only if integration needs to be performed on already parsed files. '''
    integrate_all_pdos(os.getcwd())
    
@app.command()
def plot():
    '''Plots PDOS'''
    plot_pdos(os.getcwd())
   
@app.command()
def submit(
        calc: Annotated[str, typer.Argument(help='The type of calculation to submit. Options: struc: Pristine or vacancy surface calculations. pdos: PDOS calculations')] = 'struc',
        vac:Annotated[bool,typer.Option("--vac","-v",help='Run only vacancy calculations. Does not work with calc = pdos')] = False,
        ):
    '''Submits vasp calculations.'''
    pkgdir = sys.modules['delafossite_wf'].__path__[0]
    filedir = os.path.expanduser('~/wf-user-files')
    fullpath = os.path.join(filedir, 'vasp.sh')
    shutil.copy(fullpath, os.getcwd())
    if calc.lower() == 'struc':
        if vac:
            fpath = os.path.join(pkgdir,'submitvacancy-vasp.sh')
        else:
            fpath = os.path.join(pkgdir,'submitall-vasp.sh')
        os.system(f'bash {fpath}')
    elif calc.lower() == 'pdos':
        fpath = os.path.join(pkgdir,'submitpdos-vasp.sh')
        os.system(f'bash {fpath}')
        
@app.command()
def check(
        submit:Annotated[bool,typer.Option("--no-submit","-n",help='Use -n or --no-submit to run check without autosubmitting calculations')] = True
        ):
    '''Checks vasp.out for errors and fixes and resubmits calculations if possible.'''
    err_fix(os.getcwd(),submit)
    