from datetime import datetime
import pytz
import yaml 
from util.comunication import sendtelegram
import importlib
import json
from logging.handlers import TimedRotatingFileHandler
import util.common as common
import util.config as config
import util.cronConfCrud as CronConfCrud
import util.perfdataCrud as PerfdataCrud
import util.db as db
import logging
import sys
import os
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv


scheduled_jobs_map = {}

load_dotenv()  
cwd = os.getcwd()
modulepath = os.path.join(cwd,"task")
if os.path.exists(modulepath):
    sys.path.append(modulepath)
CONFIG =  config.Config("./config.yaml")        
print(CONFIG.conf)
logger = logging.getLogger()

#formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')


handler = TimedRotatingFileHandler(CONFIG.LOGFILEPATH+"/personal-scheduler.log", 
                                   when='midnight',
                                   backupCount=int(CONFIG.LOGBACKUPSIZE))
handler.setFormatter(formatter)
logger.addHandler(handler)
 
logger.setLevel(logging.getLevelName(CONFIG.LOGLEVEL)) 

#logFormatter = logging.Formatter ("%(name)-12s %(asctime)s %(levelname)-8s %(filename)s:%(funcName)s %(message)s")
logFormatter = logging.Formatter ("%(asctime)s %(levelname)-8s %(filename)s:%(funcName)s %(message)s")

consoleHandler = logging.StreamHandler(sys.stdout) #set streamhandler to stdout
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)

logger.info("starting personal scheduler")
logger.info("config loaded")
logger.info(CONFIG.conf)

db_path = CONFIG.DB_PATH
db.create_sqlite_database(db_path)
exists, is_valid = db.check_sqlite_db_exists(db_path)

if exists and is_valid:
    logger.info(f"'{db_path}' exists and is a valid SQLite database.")
elif exists and not is_valid:
    logger.error(f"'{db_path}' exists but is not a valid SQLite database.")
else:
    logger.error(f"'{db_path}' does not exist.")
 
crudconf = CronConfCrud.CronConf(db_path)
crudprefdata= PerfdataCrud.Perfdata(db_path)
        

def get_method(module,method):
    mymethod = getattr(importlib.import_module(module), method)
    return mymethod


def schedule_jobs(scheduler):
    jobs = retrieve_jobs_to_schedule()
    for job in jobs: 
        print(job['id'])
        enable_job=int(job['enable'])
        if enable_job == 0: 
            remove_job_scheduler(scheduler, job)
            try:
                crudconf.delete_job(job["id"])
            except:
                pass
        else:        
            add_job_if_applicable(job, scheduler)
            update_job_if_applicable(job, scheduler)

@common.silent_execution
def remove_job_list(jobs, job):
    jobs.remove(job)
            
@common.silent_execution
def remove_job_scheduler(scheduler, job):
    scheduler.remove_job(job["id"])

def retrieve_jobs_to_schedule():
    cwd = os.getcwd()
    jobs = []
    jobfolder="job.d"
    jobfolderd = os.path.join(cwd,jobfolder)
    for file in os.listdir(jobfolderd):
        if file.endswith(".json"):
            logger.info(f"load job {file}")
            with open(os.path.join(jobfolderd, file),'r') as file:
                jobs.extend(json.load(file))
                print(len(jobs))
    return jobs


def add_job_if_applicable(job, scheduler): 
    job_id = str(job['id'])
    if (job_id not in scheduled_jobs_map):
        scheduled_jobs_map[job_id] = job
        scheduler.add_job(lambda: execute_job(job), CronTrigger.from_crontab(job['cron_expression'], timezone=pytz.timezone(CONFIG.TIMEZONE)), id=job_id)
        message = "added job with id: " + str(job_id) + " "+ job['cron_expression'] + "  " + common.crondecode(job['cron_expression'])
        crudconf.create_job(job_id, job['cron_expression'], common.crondecode(job['cron_expression']), job)
        
        logger.info(message)

            

def update_job_if_applicable(job, scheduler):
    job_id = str(job['id'])
    if (job_id not in scheduled_jobs_map):
        return
    disabled = False
    try:
        disabled = bool(scheduled_jobs_map[job_id]['disabled'])
    except:
        pass
    
    last_version = scheduled_jobs_map[job_id]['version']
    current_version = job['version']
    if (disabled == True):
        scheduler.remove_job(job_id)
        crudconf.delete_job(str(job['id']))
        return
    if (bool(job == scheduled_jobs_map[job_id])==False):
        scheduled_jobs_map[job_id]['version'] = current_version
        scheduler.remove_job(job_id)
        scheduler.add_job(lambda: execute_job(job), CronTrigger.from_crontab(job['cron_expression'], timezone=pytz.timezone(CONFIG.TIMEZONE)), id=job_id)
        message = "updated job with id: " + str(job_id) + " "+ job['cron_expression'] + "  " + common.crondecode(job['cron_expression'])
        crudconf.upsert_job(job_id, job['cron_expression'], common.crondecode(job['cron_expression']), job)
        
        logger.info(message)
 
def execute_job(job):
    jobtype="None"
    try:
        jobtype=job["jobtype"]
    except:
        pass
    if "module" in jobtype.lower():
        execute_job_module(job)
    elif "task" in jobtype.lower():
        execute_job_task(job)
        

def execute_job_task(job):
    gdict={}
    gdict.update(globals())
    gdict.update(locals())
    
    message = f"{datetime.now()} executing job with id:  {str(job['id'])} {job['task']}"
    logger.info(message)
    tasksfile = f"task.d/{job['task']}.yaml"
    with open(tasksfile) as file:
        conf = yaml.load(file, Loader=yaml.FullLoader)
    
    tasks = conf[0]['tasks']
    sizetask = len(tasks)
    currtask = 1 
    for task in tasks:
        for key in task.keys():
            if "name" != key:
                print("\n")
                print(f"exec task \"{name}\"  task {currtask} of {sizetask}")
                
                print(f"\t{key} {task.get(key)}") 
                if "." in key:
                    m = __import__(key.split('.')[0])
                    mfunc = getattr(m,"setgdict")
                    mfunc(m,gdict)
                    func = getattr(m,key.split('.')[1])
                    func(m,task.get(key))
                    
                else:
                    func = globals()[key]
                    func(task.get(key))
                currtask = currtask +1 
            else:
                name = common.effify(task.get(key),gdict)


    pass

def execute_job_module(job):
    message = f"{datetime.now()} executing job with id:  {str(job['id'])} {job['module']}  {job['method']}"
        
    logger.info(message)
        
    methodtoexecute = get_method(job['module'],job['method'])
    paramd = {}
    paramd = common.check_parma_and_load(job,'param')
    notify =  common.check_parma_and_load(job,'notify')
    notifymessage =  common.check_parma_and_load(job,'notifymessage')
    notifymethod =  common.check_parma_and_load(job,'notifymethod',"telegram")
    storedb = common.check_parma_and_load(job,"storedb")
    libs = common.check_parma_and_load(job,"lib")
    needlogger=common.check_parma_and_load(job,"needlogger",False)
    
    common.mng_library(libs)
    retval =""
    if paramd and  needlogger.lower() == "true":
        paramd.update(CONFIG.conf)
        retval= methodtoexecute(paramd,logger)  
        message= f"executed {job['id']} {job['module']} {job['method']} the result are {retval}"
        logger.info(message)
    elif paramd and  needlogger.lower() == "false":
        paramd.update(CONFIG.conf)
        retval= methodtoexecute(paramd)  
        message= f"executed {job['id']} {job['module']} {job['method']} the result are {retval}"
        logger.info(message)
    else:
        retval= methodtoexecute()  
        message= f"executed {job['id']} {job['module']} {job['method']} the result are {retval}"
        logger.info(message)
    if retval != "":  
        if notifymethod:
            logger.info(notifymethod)
            for _notifymet in notifymethod.split(","):
                logger.debug(_notifymet)
                if _notifymet.lower() == "telegram":
                    mng_telegram_notify(paramd, notify, notifymessage, retval)
                                #notifyservice.sendtelegram(mes,logger,config,job['id'],notifyforced)
                    # elif _notifymet.lower() =="mail":   
                    #     globals()['retval']=retval
                    #     globals().update(paramd)
                    #     if bool(common.check_for_notify(notify)):
                    #         mes = common.effify(notifymessage)
                    #         subject = f"output {job['id']}"
                    #         if notifysubject:
                    #             subject =notifysubject 
                    #         #notifyservice.sendmail(mes,subject,logger,config,job['id'],notifyforced)
        if bool(storedb) == True:
            crudprefdata.create_perfdata(job['id'],retval,CONFIG)

    if retval:
        logger.info(f"job {job['id']} executed retval={retval}")
    else:
        logger.info(f"job {job['id']} executed {datetime.now()}")



def mng_telegram_notify(paramd, notify, notifymessage, retval):
    if notify and notifymessage:
        globals()['retval']=retval
        globals().update(paramd)
        if bool(common.check_for_notify(notify)):
            mes = common.effify(notifymessage,globals())
            sendtelegram(CONFIG,mes)


#notifyservice.sendtelegram(f"start openmonitoring with {json.dumps(config)}",logger,config,forced=True)

now = datetime.now()
#notifyservice.sendtelegram(f"start  at {now}",logger,config,forced=True)

from apscheduler.schedulers import background
job_defaults = {
    'coalesce': False,
    'max_instances': 10
}
#sendtelegram(CONFIG,"start")

scheduler = background.BlockingScheduler(job_defaults=job_defaults,timezone=pytz.timezone(CONFIG.TIMEZONE))

scheduler.add_job(lambda: schedule_jobs(scheduler), 'interval', seconds=60, next_run_time=datetime.now(), id='scheduler-job-id')
scheduler.start()
