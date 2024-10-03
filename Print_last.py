#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
This is a Python script for RASPA after simulations.
This script will read last prints of [code] Trend_raspa.py results.
Mr_Chem.py and Work_Dictionary.txt is required to execute this script
Highly recommend to use Script_raspa.py to implement simulations.
Author: Mingrui.Zuo19@student.xjtlu.edu.cn
Lifeng.Ding's group, department of Chemistry, school of Science, XJTLU
last edited: 2024/10/01
"""


import os
import re
import datetime
import sys
import shutil
pf_path = r"/public3/home/scg7092/Mingrui/Code/Database/"  # The filepath of "Mr_Chem.py"
sys.path.append(pf_path)
import Mr_Chem as mr


# Use regex to match last line of a file
def find_last_match(match_file):
    last_match = None

    with open(match_file, "r") as txt:
        for line in txt:
            match = re.search(pattern, line)
            if match:
                last_match = match.groups()

    return last_match


# Regex of last print
pattern = r"(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)"
# [mol/uc], [mol/kg], [mg/g], [cm^3 STP/g], [cm^3 STP/cm^3]
exec_py = r"Trend_raspa.py"


# Make new directories
if "Trends" not in os.listdir(os.getcwd()):
    os.system(r"mkdir \Trends")
else:
    os.system(r"rm -rf Trends")

if "Analysis" not in os.listdir(os.getcwd()):
    os.system(r"mkdir \Analysis")


# Create a "txt" file and list the table titles
script_name = os.path.basename(os.path.abspath(__file__))
report_name = "Updating_Uptake.txt"
with open(report_name, "w") as rp:
    rp.writelines("\n#.Code information\n")
    rp.writelines("================================\n")
    rp.writelines(f"State statistics were generated through: //{script_name}// [version: 241001]\n")
    rp.writelines("Script coded by: Mingrui.Zuo19@student.xjtlu.edu.cn\n")
    rp.writelines(f"Date: {datetime.datetime.now()}\n")
    rp.writelines("\n0.Last print of adsorption trend\n")
    rp.writelines("================================\n")
    rp.writelines("CIF " + "Gas " + "Temperature[K] " + "Pressure[Pa] " + "[molecules/cell] " + "[mmol/g] " + "[mg/g] " + "[cm^3/g] " + "[cm^3/cm^3]\n")
    rp.writelines("----------------------------------------------------------------------------------------------------------------\n")


# Read Work_Dictionary.txt
wd_path = os.path.join(os.getcwd(), "Work_Dictionary.txt")
file_list = mr.File.file2list(wd_path)["Content"]
for work_path in file_list:
    # The head is information of isotherm table
    head = {"cif": work_path.split("/")[-4],
            "gas": work_path.split("/")[-3],
            "temperature": work_path.split("/")[-2],
            "pressure": work_path.split("/")[-1].strip("\n")}

    output_dir = os.path.join(work_path, "Output/System_0")

    if os.path.exists(output_dir):
        for file_name in os.listdir(os.path.join(work_path, "Output/System_0")):
            if file_name.endswith(".data"):
                output_path = os.path.join(work_path, "Output/System_0", file_name)
                os.system(f"python {exec_py} {output_path}")
                print(f"writing the [trend] of {file_name}\n")
                trend_filename = "Trend_"+head["gas"]+"_"+os.path.basename(output_path).strip(".data").strip("output_") + ".txt"
                result = find_last_match(trend_filename)

                report_line = " ".join((value for value in head.values())) + " " + " ".join(result) + "\n"
                with open(report_name, "a") as rp:
                    rp.writelines(report_line)

                shutil.move(trend_filename, fr"Trends/{trend_filename}")

    else:
        report_line = " ".join(value for value in head.values()) + " - - - - -\n"
        with open(report_name, "a") as rp:
            rp.writelines(report_line)

shutil.move(report_name, fr"Analysis/{report_name}")








