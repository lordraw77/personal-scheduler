import importlib
import util.common as common
import json
import os


def get_method(module,method):
    mymethod = getattr(importlib.import_module(module), method)
    return mymethod

def retrieve_jobs_to_schedule():
    cwd = os.getcwd()
    jobs = []
    jobfolder="job.d"
    jobfolderd = os.path.join(cwd,jobfolder)
    for file in os.listdir(jobfolderd):
        if file.endswith(".json"):
            with open(os.path.join(jobfolderd, file),'r') as file:
                jobs.extend(json.load(file))

    return jobs


jobs = retrieve_jobs_to_schedule()
for job in jobs: 
    print(job)
    libs = common.check_parma_and_load(job,"lib")
    for lib in libs.split(","):
        common.install_and_import(lib)
    paramd = {}
    paramd = common.check_parma_and_load(job,'param')
    methodtoexecute = get_method(job['module'],job['method'])
    retval= methodtoexecute(paramd) 
    print(retval)
    




# import pkg_resources

# installed = {pkg.key for pkg in pkg_resources.working_set}

# if "pandas" in installed:
#     print("pandas is installed")
# else:
#     print("pandas is not installed")
#     common.install_and_import("pandas")
    
# print("1")
# try:  
#     print("2")
#     import pandas as pd
#     print("pandas work")
#     print("3")
# except:
#     print("pandas non c'è")
    
    
# installed2 = {pkg.key for pkg in pkg_resources.working_set}

# if "pandas" in installed2:
#     print("pandas is installed")
# else:
#     print("pandas is not installed")
    