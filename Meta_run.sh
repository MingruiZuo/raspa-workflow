#!/bin/bash
#SBATCH -p amd_512
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -J water
source /public3/soft/modules/module.sh 
module load mpi/intel/17.0.7-thc
export RASPA_DIR=${HOME}/RASPA2_GC-TMMC/RASPA2_GC-TMMC-master/install
export DYLD_LIBRARY_PATH=${RASPA_DIR}/lib
export LD_LIBRARY_PATH=${RASPA_DIR}/lib

NP=1

srun -n $NP $RASPA_DIR/bin/simulate -i simulation.input