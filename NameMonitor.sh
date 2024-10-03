#!/bin/bash
#SBATCH -p amd_512
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -J NaMo

python_script="State_raspa.py"
result_script="Reader_raspa.py"

interval=300
job_name="water"  # jobname

echo "Checking for job with name: $job_name"

while true; do

    job_status=$(squeue --name "$job_name" | grep "$job_name")

    if [ -n "$job_status" ]; then

        echo "Job with name $job_name is still running. Executing Python script."
        python "$python_script"
        sleep "$interval"
    else

        echo "No job with name $job_name is running. Executing Python script one last time."
        python "$python_script"
        python "$result_script"
        break
    fi
done
