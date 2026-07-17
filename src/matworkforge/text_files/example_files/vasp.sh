#!/bin/bash
#SBATCH --account=rem317140
#SBATCH --nodes=1
#SBATCH --ntasks=36
#SBATCH --time=24:00:00
#SBATCH --partition=remix
#SBATCH --qos=remix

module load vasp6/6.2.1 oneapi/2023.1.0 mkl/2023.1.0 mpi/2021.9.0
export OMP_NUM_THREADS=1
export I_MPI_PMI_LIBRARY=/usr/lib64/libpmi.so
srun -n 36 vasp_std > vasp.out

exit
