"""
This is a Python script for RASPA after simulations.
Mr_Chem.py and Work_Dictionary.txt is required to execute this script
Highly recommend to use Script_raspa.py to implement simulations.
Author: Mingrui.Zuo19@student.xjtlu.edu.cn
Lifeng.Ding's group, department of Chemistry, school of Science, XJTLU
last edited: 2024/09/24
"""


import os
import re
import datetime
import sys
pf_path = r"/public3/home/scg7092/Mingrui/Code/Database/"  # The filepath of "Mr_Chem.py"
sys.path.append(pf_path)
import Mr_Chem as mr


def output_print(output_directory):
    for filename in os.listdir(output_directory):
        print("Files in current directory: " + filename)
        if filename.endswith(".data"):
            file_list = mr.File.file2list(os.path.join(output_directory, filename))["Content"]

            try:
                block_uptake = mr.List.list2block(file_list, hook_up="Number of molecules",
                                                  hook_down="Average Widom Rosenbluth factor")

                block_qst = mr.List.list2block(file_list, hook_up="Enthalpy of adsorption",
                                                  hook_down="heat of adsorption Q=-H")

                with open("Isotherm_Results.txt", "a") as Write_data:
                    Write_data.writelines(diction_list[0] + ' ' + diction_list[1] + ' ' + diction_list[2] + ' ' + diction_list[3] + ' ')

                    # The last term for each line must be '\n'
                    for line in block_qst["Block"]:
                        if "[KJ/MOL]" in line:
                            content_list = line.split()
                            Write_data.writelines(content_list[0] + ' ')
                            Write_data.writelines(content_list[2] + ' ')

                    for line in block_uptake["Block"]:
                        if "Average loading absolute [molecules/unit cell]" in line:
                            content_list = line.split()
                            Write_data.writelines(content_list[5] + ' ')
                        if "Average loading absolute [mol/kg framework]" in line:
                            content_list = line.split()
                            Write_data.writelines(content_list[5] + ' ')
                        if "Average loading absolute [milligram/gram framework]" in line:
                            content_list = line.split()
                            Write_data.writelines(content_list[5] + ' ')
                        if "Average loading absolute [cm^3 (STP)/gr framework]" in line:
                            content_list = line.split()
                            Write_data.writelines(content_list[6] + ' ')
                        if "Average loading absolute [cm^3 (STP)/cm^3 framework]" in line:
                            content_list = line.split()
                            Write_data.writelines(content_list[6] + " " + str(round(100*float(content_list[8])/float(content_list[6]), 2)) + '\n')

            except UnboundLocalError:
                with open("Isotherm_Results.txt", "a") as Write_data:
                    Write_data.writelines(diction_list[0] + ' ')
                    Write_data.writelines(diction_list[1] + ' ')
                    Write_data.writelines(diction_list[2] + ' ')
                    Write_data.writelines(diction_list[3] + ' ')
                    Write_data.writelines('- - - - - - - -\n')


def unfinished(Name):

    un_job = 0
    dic = path+"/"+Name
    with open(dic, "r") as result:
        for line in result.readlines():
            if "- - - - - - - -" in line:
                un_job += 1

    return un_job


# Create a "txt" file and list the table titles
script_name = os.path.basename(os.path.abspath(__file__))
report_name = "Isotherm_Results.txt"
with open(report_name, "w") as rp:
    rp.writelines("\n#.Trivial information\n")
    rp.writelines("================================\n")
    rp.writelines(f"State statistics were generated through: //{script_name}//\n")
    rp.writelines("Script coded by: Mingrui.Zuo19@student.xjtlu.edu.cn\n")
    rp.writelines(f"Date: {datetime.datetime.now()}\n")
    rp.writelines("\n0.Qst and Adsorption amount\n")
    rp.writelines("================================\n")
    rp.writelines("CIF " + "Gas " + "Temperature[K] " + "Pressure[Pa] " + "Qst[kJ/mol] " + "+/- " + "[molecules/cell] " + "[mmol/g] " + "[mg/g] " + "[cm^3/g] " + "[cm^3/cm^3] " + "error% \n")
    rp.writelines("----------------------------------------------------------------------------------------------------------------\n")

path = os.getcwd()
WD = mr.File.file2list("Work_Dictionary.txt")
count = WD["LineNum"]
WD = WD["Content"]

i = 0
m = 0
for diction in WD:  # Each diction is a working path.
    work_dic = mr.clean(diction)  # Remove the "\n" in the end of each diction.
    diction_clear = diction.lstrip(path)
    diction_clear = diction_clear.strip("/Work/")
    diction_list = diction_clear.split("/")
    print("diction list", diction_list)
    output_dic = work_dic + "/Output/System_0/"

    try:
        output_print(output_dic)
        i += 1
        print("The output has been detected.\n                                                         Read Progress: {A}/{B}={C}%\r\n".format(A=i, B=count, C=round(100 * i / count, 3)))
    except FileNotFoundError:
        m += 1
        print("The current directory is not found! Counting number: {c}".format(c=m))

if i == count:
    un_job_number = unfinished("Isotherm_Results.txt")
    print("\nThere are totally {i} jobs been detected.".format(i=i))
    print("{A}/{B}={C}% jobs have finished already.\n".format(A=count-un_job_number, B=count, C=round(100 * (count-un_job_number) / count, 3)))

else:
    print("\nThere should be {a} jobs. But {b} jobs were detected.".format(a=count, b=i))


"""
Return the maximum absolute value and the condition.
"""

file_path = 'Isotherm_Results.txt'


def update_max_value(parts, index, key, condition, max_values):
    if parts[index] != '-' and (max_values[key]["value"] is None or abs(float(parts[index])) > abs(max_values[key]["value"])):
        max_values[key]["value"] = float(parts[index])
        max_values[key]["conditions"] = condition


def process_line(parts, condition, max_values):

    if parts[5] != '-' and parts[6] != '-':
        qst_value = float(parts[5])
        qst_error = float(parts[6])
        if max_values["Qst[kJ/mol]"]["value"] is None or abs(qst_error) > abs(max_values["Qst[kJ/mol]"]["value"]):
            max_values["Qst[kJ/mol]"]["value"] = qst_error
            max_values["Qst[kJ/mol]"]["conditions"] = condition

    other_columns = [
        (4, "Qst[kJ/mol]"),
        (5, "Qst[+/-]"),
        (6, "[molecules/cell]"),
        (7, "[mmol/g]"),
        (8, "[mg/g]"),
        (9, "[cm^3/g]"),
        (10, "[cm^3/cm^3]"),
        (11, "error%")
    ]

    for index, key in other_columns:
        update_max_value(parts, index, key, condition, max_values)

max_values = {
    "Qst[kJ/mol]": {"value": None, "conditions": None},
    "Qst[+/-]": {"value": None, "conditions": None},
    "[molecules/cell]": {"value": None, "conditions": None},
    "[mmol/g]": {"value": None, "conditions": None},
    "[mg/g]": {"value": None, "conditions": None},
    "[cm^3/g]": {"value": None, "conditions": None},
    "[cm^3/cm^3]": {"value": None, "conditions": None},
    "error%": {"value": None, "conditions": None}
}


with open(file_path, 'r') as file:
    lines = file.readlines()
    for line in lines:
        if re.match(r'\S+\s+\S+\s+\d+\s+\d+\.\d+', line):
            parts = line.split()
            condition = f"{parts[0]} {parts[1]} {parts[2]} {parts[3]}"
            process_line(parts, condition, max_values)

with open(file_path, 'a') as file:
    file.write("\n1.Maximum Absolute Value\n")
    file.write("================================\n")
    file.write("Variable        : Value           for CIF Gas Temperature[K] Pressure[Pa]\n")
    file.write("-------------------------------------------------------------------------\n")

    max_key_length = max(len(key) for key in max_values.keys())
    max_value_length = 15

    for key, info in max_values.items():
        if info["value"] is not None:
            file.write(f"{key:<{max_key_length}}: {info['value']:<{max_value_length}} for {info['conditions']}\n")

