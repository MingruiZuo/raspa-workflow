import os
import re

def kill_jobs_in_directory(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".out"):
                match = re.search(r'slurm-(\d+)\.out', file)
                if match:
                    jobid = match.group(1)
                    print(f"Killing job: {jobid}")
                    os.system(f"bkill {jobid}")
                else:
                    print(f"Skipping file: {file} (no jobid found)")

directory_path = os.path.join(os.path.dirname(os.getcwd()), "Work")

kill_jobs_in_directory(directory_path)