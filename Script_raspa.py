import math
import sys
pf_path = r"/public3/home/scg7092/Mingrui/Code/Database/"  # The filepath of "Mr_Chem.py"
sys.path.append(pf_path)
import Mr_Chem as mr
import os


### Functions
def ListGen(start, end, num_points):
    interval = (end-start)/num_points
    a_list = [round((i+start/interval)*interval, 3) for i in range(num_points+1)]
    return a_list[1:]


def List_in_List(complex_list):
    """
    united with ListGen() to convert (T, P) to proper Lists
    :param complex_list: normally "Temperature", "Pressure" settings
    :return: the proper Lists with values.
    """
    A_List = []
    for item in complex_list:
        if "=" in item:
            exec(item, globals())  # to make "L" a global variable
            A_List.extend(L)
        else:
            A_List.append(item)
    return A_List


def generate_multi_run(input_file, output_file):
    try:

        with open(input_file, 'r') as infile:
            paths = infile.readlines()

        with open(output_file, 'w') as outfile:
            for path in paths:
                path = path.strip()
                if path:
                    outfile.write(f"cd {path}\n")
                    outfile.write("chmod +x Meta_run.sh\n")
                    outfile.write("sbatch Meta_run.sh\n\n")

        print(f"Multi_run is on-writing: {output_file}")

    except FileNotFoundError:
        print(f"fault:no file '{input_file}'")
    except Exception as e:
        print(f"extra fault: {e}")


### File uploading
Set = mr.File.split_paragraph("Setting.txt")
List_Path = Set["Path"]
List_CIF = [cif.rstrip(".cif") for cif in Set["CIF"]]
List_Gas = [gas.rstrip(".def") for gas in Set["Gas"]]
List_Temperature = List_in_List(Set["Temperature[K]"])
List_Pressure = List_in_List(Set["Pressure[Pa]"])
List_FFs = Set["FFs"]
List_Set = [List_CIF, List_Gas, List_Temperature, List_Pressure]  # Diction structure

### Location
cif_path = List_Path[0].split('=')[1].strip(" ")
ff_path = List_Path[1].split('=')[1].strip(" ")
molecule_path = List_Path[2].split('=')[1].strip(" ")
path = os.getcwd()
os.system("mkdir Work/")

### Count job numbers
num_item = 0
job_count = 1
for i in range(len(List_Set)):
    num_item = len(List_Set[i])
    job_count = job_count*num_item
print("There should be totally {job_count} jobs been submitted.".format(job_count=job_count), "\n")


### Work dictionary generation
with open("Work_Dictionary.txt", "w") as WD:
    i = 0
    for cif in List_Set[0]:
        os.system("mkdir Work/" + f"{cif}")
        for gas in List_Set[1]:
            os.system("mkdir Work/" + f"{cif}/{gas}")
            for temp in List_Set[2]:
                os.system("mkdir Work/" + f"{cif}/{gas}/{temp}")
                for pressure in List_Set[3]:
                    work_path = f"{cif}/{gas}/{temp}/{pressure}"
                    os.system("mkdir Work/" + work_path)
                    temporary_path = os.path.normpath(path + "/Work/" + work_path) + "\r\n"
                    WD.writelines(temporary_path)
                    i += 1
                    print("The working dictionary is being created. "
                          "Progress: {a}/{b}={c}%".format(a=i, b=job_count, c=round(100*i/job_count, 3)))
print("Work Dictionary has been written.\r")


### According to Work_Dictionary to copy files.
with open("Work_Dictionary.txt", "r") as WD:
    i = 0
    m = 0
    q = 0
    for diction in WD:  # Each diction is a working path.
        print("current diction: ", diction, "\r")
        dic = mr.clean(diction)  # Remove the "\n" in the end of each diction.
        diction_clear = diction.strip(path)
        diction_clear = diction_clear.strip("/Work/")
        print("path:", path, "\r")
        print("clear diction:", diction_clear, "\r")
        diction_list = diction_clear.split("/")
        print("diction list", diction_list)
        # Each "diction_list" is a list like 'List_Set': ['CIF', 'Gas', 'Temperature', 'Pressure'].

        # Process CIF file
        CIFpro = mr.cif_process(cif_path + diction_list[0] + ".cif")

        # Move files to the target working path.
        os.system("cp simulation.input " + dic)
        os.system("cp " + cif_path + diction_list[0] + ".cif " + dic)
        the_ff_path = ff_path
        os.system("cp " + the_ff_path + "force_field.def "
                        + the_ff_path + "force_field_mixing_rules.def "
                        + the_ff_path + "pseudo_atoms.def " + dic)
        os.system("cp " + molecule_path + diction_list[1] + ".def " + dic)
        os.system("cp Meta_run.sh " + dic)
        i += 1
        print("Input files has been copy-pasted to the working dictionary. "
              "Progress: {a}/{b}={c}%".format(a=i, b=job_count, c=round(100*i/job_count, 3)))

        # Change the file contents
        mr.File.replace_in_file(dic + "/simulation.input", "replace_unit_cell", CIFpro["Unit Cell Number"])
        mr.File.replace_in_file(dic + "/simulation.input", "replace_CIF", diction_list[0])
        mr.File.replace_in_file(dic + "/simulation.input", "replace_Gas", diction_list[1])
        mr.File.replace_in_file(dic + "/simulation.input", "replace_Temperature", diction_list[2])
        mr.File.replace_in_file(dic + "/simulation.input", "replace_Pressure", diction_list[3])
        mr.File.replace_in_file(dic + "/simulation.input", "replace_FF", mr.String.string2list(the_ff_path.rstrip("/"), hook="/")[-1])
        q += 1
        print("Mr.Chem is editing the current input file.                  "
              "Progress: {a}/{b}={c}%".format(a=q, b=job_count, c=round(100 * q / job_count, 3)))

print("There should be totally {a}[CIF]*{b}[Gas]*{c}[Temp]*{d}[Pres]={job_count} jobs been prepared.".
      format(a=len(List_CIF),b=len(List_Gas),c=len(List_Temperature),d=len(List_Pressure),job_count=job_count), "\n")


### Write the multi_run
input_file = 'Work_Dictionary.txt'
output_file = 'Multi_run'
generate_multi_run(input_file, output_file)










