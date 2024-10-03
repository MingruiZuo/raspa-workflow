import os
import shutil
import re
import time
import datetime


class raspa_output:

    def __init__(self, filepath):
        """
        The filepath of raspa output file is written in WorkDictionary.
        During initialization, check if the file exists.
        """
        self.filepath = filepath
        self.file_exists = self.check_existence()  # File existence check during instantiation

        if not self.file_exists:
            raise FileNotFoundError(f"Error: File {self.filepath} not found.")

    def check_existence(self):
        """
        Check if the file exists at the given file path.
        """
        return os.path.exists(self.filepath)

    def extract_total_cycles(self):
        """
        Extract the total initializing and production cycles.
        """
        init_cycles_total_pattern = r"Number of initializing cycles: (\d+)"
        prod_cycles_total_pattern = r"Number of cycles: (\d+)"

        init_total = None
        prod_total = None

        with open(self.filepath, 'r') as file:
            for line in file:
                # Match the initializing cycles
                init_match = re.search(init_cycles_total_pattern, line)
                if init_match:
                    init_total = int(init_match.group(1))

                # Match the production cycles
                prod_match = re.search(prod_cycles_total_pattern, line)
                if prod_match:
                    prod_total = int(prod_match.group(1))

        if init_total is None or prod_total is None:
            raise ValueError("Could not find total cycles for initializing or production.")

        return init_total, prod_total

    def extract_progress(self, init_cycles_total, prod_cycles_total):
        """
        Extract and calculate the progress of the cycles, using extract_total_cycles result.
        """

        init_pattern = r"\[Init\] Current cycle: (\d+) out of (\d+)"
        prod_pattern = r"Current cycle: (\d+) out of (\d+)"

        init_progress = 0
        prod_progress = 0

        with open(self.filepath, 'r') as file:
            for line in file:
                # Match the initializing cycle progress
                init_match = re.search(init_pattern, line)
                if init_match:
                    init_progress = int(init_match.group(1))  # Current initializing cycles

                # Match the production cycle progress, only if production has started
                prod_match = re.search(prod_pattern, line)
                if prod_match and not init_match:
                    prod_progress = int(prod_match.group(1))  # Current production cycles
                    init_progress = init_cycles_total

                if "Finishing simulation" in line:
                    init_progress = init_cycles_total
                    prod_progress = prod_cycles_total

        # Calculate the progress based on initialization and production
        total_cycles_completed = init_progress + prod_progress
        total_cycles = init_cycles_total + prod_cycles_total
        progress_percentage = (total_cycles_completed / total_cycles) * 100

        return progress_percentage, init_progress, prod_progress

    def work_state(self, init_progress, prod_progress):

        warning_pattern = r"Simulation finished,  (\d+) warnings"
        new_warn_pattern = r"\s+WARNING: (.+)\n\s+"

        STAT = ["Initialization", "Production", "Completion", "Warning", "Frozen", "NoRunning"]

        warning_numbers = None

        with open(self.filepath, 'r') as file:
            for line in file:
                warn_match = re.search(warning_pattern, line)
                if warn_match:
                    warning_numbers = int(warn_match.group(1))

                new_warn_match = re.search(new_warn_pattern, line)
                if new_warn_match:
                    warning_numbers = 1
                    warning_words = new_warn_match.group(1)
                    with open("warning_report.txt", "a") as wr:
                        wr.writelines(f"filepath: {self.filepath}\n"
                                      f"warnings: {warning_words}\n"
                                      f"=============================\n")

            # Determine the state based on progress first
            if prod_progress > 0:
                state = STAT[1]  # Production in progress
            elif init_progress > 0:
                state = STAT[0]  # Initialization in progress
            else:
                state = STAT[4]  # Not started

            # If warnings exist, change the state to reflect completion
            if warning_numbers is not None:
                if warning_numbers > 0:
                    state = STAT[3]  # Completed with warnings
                else:
                    state = STAT[2]  # Completed without warnings

        return state


# Utilize the class
def single_output(file_path):

    with open("job_state.txt", "a") as js:

        try:
            output = raspa_output(file_path)

            # Extract total cycles
            init_total, prod_total = output.extract_total_cycles()
            print(f"Setting Initial {init_total} cycles and Production {prod_total} cycles.")

            # Extract and print the progress
            progress, init, prod = output.extract_progress(init_total, prod_total)

            # Write the current work state
            current_state = output.work_state(init, prod)

            print(f"Initial cycles = {init}/{init_total}\n"
                  f"Product cycles = {prod}/{prod_total}\n"
                  f"==Current progress: {progress:.2f}%==\n"
                  f"Current state: {current_state} \r\n")

            js.writelines(f"\t{current_state[0:4]} \t{round(progress, 2)} \t{init} \t{init_total} \t{prod} \t{prod_total} \t{file_path} \n")

        except FileNotFoundError as e:
            print(e)

        except ValueError as e:
            print(f"Error extracting cycle information: {e}")


def NOpt_state(file_path):
    with open("job_state.txt", "a") as js:
        js.writelines(f"\tNOpt \t- \t- \t- \t- \t- \t{file_path}")


def job_state_statics(file_path):

    State_Dic = {'Froz': 0, 'Comp': 0, 'Init': 0, 'Prod': 0, 'Warn': 0, 'NOpt': 0}

    with open(file_path, "r") as js:
        js_list = js.readlines()
        for line in js_list:
            if line is not "\n" and line.split()[0] in State_Dic:
                State_Dic[line.split()[0]] += 1

    return State_Dic


def job_state_append(file_path, State_Dic):

    total_jobs = sum(State_Dic.values())

    with open(file_path, "a") as js:
        js.writelines("\n1.Overall job state counting results\n")
        js.writelines("================================\n")
        js.writelines("\n")
        js.writelines(f"\tState               \tjob(s)  percentage\n"
                      f"\t----------------------------------------\n"
                      f"\tNone(No output)     \t{State_Dic['NOpt']} \t{round(State_Dic['NOpt']/total_jobs*100, 2)}%\n"
                      f"\tFrozen(Pending)     \t{State_Dic['Froz']} \t{round(State_Dic['Froz']/total_jobs*100, 2)}%\n"
                      f"\tInitializing        \t{State_Dic['Init']} \t{round(State_Dic['Init']/total_jobs*100, 2)}%\n"
                      f"\tProducing(Running)  \t{State_Dic['Prod']} \t{round(State_Dic['Prod']/total_jobs*100, 2)}%\n"
                      f"\tCompleted           \t{State_Dic['Comp']} \t{round(State_Dic['Comp']/total_jobs*100, 2)}%\n"
                      f"\tWarning(Failed)     \t{State_Dic['Warn']} \t{round(State_Dic['Warn']/total_jobs*100, 2)}%\n"
                      f"\t----------------------------------------\n"
                      f"\tTotal(100%):        \t{total_jobs}\n")


def average_progress(file_path, State_Dic):
    progress = 0
    total_jobs = sum(State_Dic.values())
    with open(file_path, "r") as js:
        for line in js:
            if line != "\n" and line.split()[0] in State_Dic and line.split()[0] != "NOpt":
                progress += float(line.split()[1])
    Average = round(progress/total_jobs, 2)
    with open(file_path, "a") as js:
        js.writelines(f"\t----------------------------------------\n"
                      f"\tAverage Progress:\t{Average}%\n")


start_time = time.time()

with open("job_state.txt", "w") as js:
    js.writelines("\n0.Output job running states\n")
    js.writelines("================================\n")
    js.writelines("\n")
    js.writelines("\tState Progress% RunInit TolInit RunProd TolProd JobLoc \n"
                  "\t------------------------------------------------------\n")

with open("Work_Dictionary.txt", "r") as WD:
    for work_path in WD.readlines():
        output_path = work_path.strip("\n").strip("\r")+"/Output/System_0/"
        if not os.path.exists(output_path):
            NOpt_state(work_path)
        else:
            for filename in os.listdir(output_path):
                if filename.endswith(".data"):
                    output_file = os.path.join(output_path, filename)
                single_output(output_file)


job_path = os.path.join(os.getcwd(), "job_state.txt")
state_dic = job_state_statics(job_path)
average_progress(job_path, state_dic)
job_state_append(job_path, state_dic)

# write the last paragraph of state file
with open("job_state.txt", "a") as js:
    js.writelines("\n#.Trivial information\n")
    js.writelines("================================\n")
    js.writelines("State statistics were generated through: //State_raspa.py// [version 9.12.7]\n")
    js.writelines("Script coded by: Mingrui.Zuo19@student.xjtlu.edu.cn\n")
    js.writelines(f"Date: {datetime.datetime.now()}\n")


end_time = time.time()
elapsed_time = end_time - start_time

print(f"The code elapsed time: {elapsed_time} seconds")

if "Job_States" not in os.listdir(os.getcwd()):
    os.system(r"mkdir \Job_States")
time_label = str(datetime.datetime.now()).split(".")[0].split()[1] + "_" + str(datetime.date.today())
os.rename("job_state.txt", f"job_state_{time_label}.txt")
shutil.move(f"job_state_{time_label}.txt", fr"Job_States/job_state_{time_label}.txt")


