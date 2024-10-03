#!/bin/bash 
#SBATCH -p amd_512   
#SBATCH -N 1  
#SBATCH -n 128   
#SBATCH -J GhSwap   
source /public3/soft/modules/module.sh 
module load mpi/intel/17.0.7-thc
export RASPA_DIR=${HOME}/RASPA2_GC-TMMC/RASPA2_GC-TMMC-master/install
export DYLD_LIBRARY_PATH=${RASPA_DIR}/lib
export LD_LIBRARY_PATH=${RASPA_DIR}/lib
$RASPA_DIR/bin/simulate -i simulation.input

function check_lower_128()
{
    num=`ps -ef |grep simulate | wc -l`
    #echo $num
    #num=128
    if [ $num -gt 128 ] ;then
        return 0
    else
        return 1
    fi
}

# Starting directory
starting_dir="/public3/home/scg7092/Mingrui/water_adsorption/240925/"
# Working directory
DIR="Work"

# Set the RASPA_DIR environment variable if needed
# RASPA_DIR="path/to/raspa"

# Function to perform the simulation
run_simulation() {
  echo $RASPA_DIR/bin/simulate -i simulation.input
  $RASPA_DIR/bin/simulate -i simulation.input &
}

# Use 'find' to recursively list all deepest subdirectories under $DIR
subdirectories=$(find "$starting_dir/$DIR" -type d)

for sub_dir in $subdirectories
do
  echo $sub_dir
  cd "$sub_dir"
  sub=0
  while [ $sub -ne 1 ]
  do
    check_lower_128
    if [ $? -eq 1 ]; then
      run_simulation
      cd "$starting_dir"  # Go back to the starting directory
      sub=1
    else
      sleep 5
    fi
  done
done

wait
 
