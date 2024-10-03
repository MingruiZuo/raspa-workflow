#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
This is a Python script for RASPA after simulations.
This script will read state files listed in Job_States (generated by [State_raspa.py]).
A [Trend.txt] file will be written for convergence analysis.
[Last_print.py] can execute this script systematically.
Author: Mingrui.Zuo19@student.xjtlu.edu.cn
Lifeng.Ding's group, department of Chemistry, school of Science, XJTLU
last edited: 2024/10/01
"""
import os
import re
import datetime
import shutil

js_path = os.path.join(os.getcwd(), "Job_States")

regex_dict = {
    "Average progress": r"Average Progress:\s+(\d+\.\d+%)",
    "Date time": r"Date:\s+(.+)",
    "Job states": (
        r"None\(No output\)\s+(\d+)\s+(\d+\.\d+)%\s+"
        r"Frozen\(Pending\)\s+(\d+)\s+(\d+\.\d+)%\s+"
        r"Initializing\s+(\d+)\s+(\d+\.\d+)%\s+"
        r"Producing\(Running\)\s+(\d+)\s+(\d+\.\d+)%\s+"
        r"Completed\s+(\d+)\s+(\d+\.\d+)%\s+"
        r"Warning\(Failed\)\s+(\d+)\s+(\d+\.\d+)%"
    )
}

script_name = os.path.basename(os.path.abspath(__file__))
report_name = "Time_progress.txt"

with open(report_name, "w") as tp:
    tp.writelines("\n#.Trivial information\n")
    tp.writelines("================================\n")
    tp.writelines(f"State statistics were generated through: //{script_name}// [version 241001]\n")
    tp.writelines("Script coded by: Mingrui.Zuo19@student.xjtlu.edu.cn\n")
    tp.writelines(f"Date: {datetime.datetime.now()}\n")
    tp.writelines("\n0.Progress data\n")
    tp.writelines("================================\n")
    tp.writelines("{:<12} {:<10} {:<10} {:<6} {:<7} {:<6} {:<7} {:<6} {:<7} {:<6} {:<7} {:<6} {:<7} {:<6} {:<7}\n".format(
        "Date", "Time", "Pro[Avg]", "NOpt", "NOpt%", "Froz", "Froz%", "Init", "Init%", "Prod", "Prod%", "Comp", "Comp%",
        "Warn", "Warn%"))
    # tp.writelines("Date       Time \tPro[Avg] \tNOpt \tNOpt% \tFroz \tFroz% \tInit \tInit% \tProd \tProd% \tComp \tComp% \tWarn \tWarn%\n")
    tp.writelines("--------------------------------------------------------------------------------------------------------------------------\n")

for file in os.listdir(js_path):
    file_path = os.path.join(js_path, file)
    print(f"js_path: {file_path}")

    with open(file_path, "r") as js:
        content = js.read()

        AvgProg, Date = "", ""

        match_dt = re.findall(regex_dict["Date time"], content)
        if match_dt:
            Date = match_dt[0]
        else:
            print("No date information found!")

        match_ap = re.findall(regex_dict["Average progress"], content)
        if match_ap:
            AvgProg = match_ap[0]
        else:
            print("No average progress found!")

        match_js = re.findall(regex_dict["Job states"], content)
        if match_js:
            job_state_data = match_js[0]
            with open(report_name, "a") as tp:
                """
                tp.writelines(f"{Date} \t{AvgProg}"
                              f" \t{job_state_data[0]} \t{job_state_data[1]}%"
                              f" \t{job_state_data[2]} \t{job_state_data[3]}%"
                              f" \t{job_state_data[4]} \t{job_state_data[5]}%"
                              f" \t{job_state_data[6]} \t{job_state_data[7]}%"
                              f" \t{job_state_data[8]} \t{job_state_data[9]}%"
                              f" \t{job_state_data[10]} \t{job_state_data[11]}%\n")
                """
                tp.writelines(
                    "{:<12} {:<10} {:<10} {:<6} {:<7} {:<6} {:<7} {:<6} {:<7} {:<6} {:<7} {:<6} {:<7} {:<6} {:<7}\n".format(
                        Date.split()[0],
                        Date.split()[1].split('.')[0],
                        AvgProg,
                        job_state_data[0],
                        job_state_data[1] + "%",
                        job_state_data[2],
                        job_state_data[3] + "%",
                        job_state_data[4],
                        job_state_data[5] + "%",
                        job_state_data[6],
                        job_state_data[7] + "%",
                        job_state_data[8],
                        job_state_data[9] + "%",
                        job_state_data[10],
                        job_state_data[11] + "%"
                    ))
        else:
            print("No job state information found!")

print("Time_progress has been written.")


"""
Sorting the time sequence.
"""
from datetime import datetime

datetime_format = "%Y-%m-%d %H:%M:%S"
filename = "Time_progress.txt"

progress_pattern = re.compile(r"(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2}:\d{2})\s+(\d+\.\d+%)\s+(\d+)\s+(\d+\.\d+%)\s+(\d+)\s+(\d+\.\d+%)\s+(\d+)\s+(\d+\.\d+%)\s+(\d+)\s+(\d+\.\d+%)\s+(\d+)\s+(\d+\.\d+%)\s+(\d+)\s+(\d+\.\d+%)")

with open(filename, "r") as file:
    lines = file.readlines()

progress_data = []
header = []
for line in lines:
    match = progress_pattern.match(line.strip())
    if match:
        date_str = match.group(1)
        time_str = match.group(2)
        datetime_str = f"{date_str} {time_str}"
        progress_data.append((datetime.strptime(datetime_str, datetime_format), line.strip()))
    else:
        header.append(line)


progress_data.sort(key=lambda x: x[0])
sorted_lines = [header[0]] + header[1:11] + [line[1] + "\n" for line in progress_data] + header[11:]

with open(filename, "w") as file:
    file.writelines(sorted_lines)

print("Progress and states have been sorted on time sequence.")


"""
move file to Analysis
"""

if "Analysis" not in os.listdir(os.getcwd()):
    os.system(r"mkdir \Analysis")

shutil.move(report_name, fr"Analysis/{report_name}")




