# Personal Job Scheduler
# This script implements a scheduler system that executes jobs based on cron expressions
# It supports both module-based jobs and task-based jobs defined in YAML files

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


# Dictionary to track scheduled jobs
scheduled_jobs_map = {}

# Load environment variables from .env file
load_dotenv()  

# Add task directory to system path for importing modules
cwd = os.getcwd()
modulepath = os.path.join(cwd,"task")
if os.path.exists(modulepath):
    sys.path.append(modulepath)

# Initialize configuration from YAML file
CONFIG = config.Config("./config.yaml")        
print(CONFIG.conf)

# Configure logging system
logger = logging.getLogger()
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

# Set up file handler with log rotation
handler = TimedRotatingFileHandler(CONFIG.LOGFILEPATH+"/personal-scheduler.log", 
                                   when='midnight',
                                   backupCount=int(CONFIG.LOGBACKUPSIZE))
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.getLevelName(CONFIG.LOGLEVEL)) 

# Configure console logging
logFormatter = logging.Formatter ("%(asctime)s %(levelname)-8s %(filename)s:%(funcName)s %(message)s")
consoleHandler = logging.StreamHandler(sys.stdout)
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)

logger.info("starting personal scheduler")
logger.info("config loaded")
logger.info(CONFIG.conf)

# Initialize database
db_path = CONFIG.DB_PATH
db.create_sqlite_database(db_path)
exists, is_valid = db.check_sqlite_db_exists(db_path)

if exists and is_valid:
    logger.info(f"'{db_path}' exists and is a valid SQLite database.")
elif exists and not is_valid:
    logger.error(f"'{db_path}' exists but is not a valid SQLite database.")
else:
    logger.error(f"'{db_path}' does not exist.")
 
# Initialize database CRUD objects
crudconf = CronConfCrud.CronConf(db_path)
crudprefdata = PerfdataCrud.Perfdata(db_path)
        

def get_method(module, method):
    """
    Dynamically import a module and get a method from it
    
    Args:
        module: Module name to import
        method: Method name to retrieve from the module
        
    Returns:
        The requested method object
    """
    mymethod = getattr(importlib.import_module(module), method)
    return mymethod


def schedule_jobs(scheduler):
    """
    Schedule jobs from configuration files
    
    Args:
        scheduler: APScheduler instance to schedule jobs with
    """
    jobs = retrieve_jobs_to_schedule()
    for job in jobs: 
        logger.info(job['id'])
        enable_job = int(job['enable'])
        if enable_job == 0: 
            # Remove disabled jobs
            remove_job_scheduler(scheduler, job)
            try:
                crudconf.delete_job(job["id"])
            except:
                pass
        else:        
            # Add new jobs and update existing ones
            add_job_if_applicable(job, scheduler)
            update_job_if_applicable(job, scheduler)

@common.silent_execution
def remove_job_list(jobs, job):
    """
    Remove a job from a job list with error handling
    
    Args:
        jobs: List of jobs
        job: Job to remove
    """
    jobs.remove(job)
            
@common.silent_execution
def remove_job_scheduler(scheduler, job):
    """
    Remove a job from the scheduler with error handling
    
    Args:
        scheduler: APScheduler instance
        job: Job to remove
    """
    scheduler.remove_job(job["id"])

def retrieve_jobs_to_schedule():
    """
    Load jobs from JSON files in the job.d directory
    
    Returns:
        List of job configurations
    """
    cwd = os.getcwd()
    jobs = []
    jobfolder = "job.d"
    jobfolderd = os.path.join(cwd, jobfolder)
    for file in os.listdir(jobfolderd):
        if file.endswith(".json"):
            logger.info(f"load job {file}")
            with open(os.path.join(jobfolderd, file), 'r') as file:
                jobs.extend(json.load(file))
                logger.info(len(jobs))
    return jobs


def add_job_if_applicable(job, scheduler): 
    """
    Add a job to the scheduler if it's not already scheduled
    
    Args:
        job: Job configuration
        scheduler: APScheduler instance
    """
    job_id = str(job['id'])
    if (job_id not in scheduled_jobs_map):
        scheduled_jobs_map[job_id] = job
        scheduler.add_job(lambda: execute_job(job), 
                         CronTrigger.from_crontab(job['cron_expression'], 
                                                 timezone=pytz.timezone(CONFIG.TIMEZONE)), 
                         id=job_id)
        message = "added job with id: " + str(job_id) + " " + job['cron_expression'] + "  " + common.crondecode(job['cron_expression'])
        crudconf.create_job(job_id, job['cron_expression'], common.crondecode(job['cron_expression']), job)
        
        logger.info(message)

            

def update_job_if_applicable(job, scheduler):
    """
    Update a job in the scheduler if it's already scheduled and has changed
    
    Args:
        job: Job configuration
        scheduler: APScheduler instance
    """

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
    if (bool(job == scheduled_jobs_map[job_id]) == False):
        scheduled_jobs_map[job_id]['version'] = current_version
        scheduler.remove_job(job_id)
        scheduler.add_job(lambda: execute_job(job), 
                         CronTrigger.from_crontab(job['cron_expression'], 
                                                timezone=pytz.timezone(CONFIG.TIMEZONE)), 
                         id=job_id)
        message = "updated job with id: " + str(job_id) + " " + job['cron_expression'] + "  " + common.crondecode(job['cron_expression'])
        crudconf.upsert_job(job_id, job['cron_expression'], common.crondecode(job['cron_expression']), job)
        
        logger.info(message)
 
def execute_job(job):
    """
    Execute a job based on its type
    
    Args:
        job: Job configuration to execute
    """
    jobtype = "None"
    try:
        jobtype = job["jobtype"]
    except:
        pass
    if "module" in jobtype.lower():
        execute_job_module(job)
    elif "task" in jobtype.lower():
        execute_job_task(job)
        

def execute_job_task(job):
    """
    Execute a task-based job defined in a YAML file
    
    Args:
        job: Task job configuration
    """
    gdict = {}
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
                logger.info("\n")
                logger.info(f"exec task \"{name}\"  task {currtask} of {sizetask}")
                
                logger.info(f"\t{key} {task.get(key)}") 
                if "." in key:
                    # For module.function format
                    m = __import__(key.split('.')[0])
                    mfunc = getattr(m, "setgdict")
                    mfunc(m, gdict)
                    func = getattr(m, key.split('.')[1])
                    func(m, task.get(key))
                    
                else:
                    # For global function
                    func = globals()[key]
                    func(task.get(key))
                currtask = currtask + 1 
            else:
                name = common.effify(task.get(key), gdict)


def execute_job_module(job):
    """
    Execute a module-based job
    
    Args:
        job: Module job configuration
    """
    message = f"{datetime.now()} executing job with id:  {str(job['id'])} {job['module']}  {job['method']}"
        
    logger.info(message)
        
    methodtoexecute = get_method(job['module'], job['method'])
    paramd = {}
    paramd = common.check_parma_and_load(job, 'param')
    notify = common.check_parma_and_load(job, 'notify')
    notifymessage = common.check_parma_and_load(job, 'notifymessage')
    notifymethod = common.check_parma_and_load(job, 'notifymethod', "telegram")
    storedb = common.check_parma_and_load(job, "storedb")
    libs = common.check_parma_and_load(job, "lib")
    needlogger = common.check_parma_and_load(job, "needlogger", False)
    
    common.mng_library(libs)
    retval = ""
    
    # Execute method with or without logger based on configuration
    if paramd and needlogger.lower() == "true":
        paramd.update(CONFIG.conf)
        retval = methodtoexecute(paramd, logger)  
        message = f"executed {job['id']} {job['module']} {job['method']} the result are {retval}"
        logger.info(message)
    elif paramd and needlogger.lower() == "false":
        paramd.update(CONFIG.conf)
        retval = methodtoexecute(paramd)  
        message = f"executed {job['id']} {job['module']} {job['method']} the result are {retval}"
        logger.info(message)
    else:
        retval = methodtoexecute()  
        message = f"executed {job['id']} {job['module']} {job['method']} the result are {retval}"
        logger.info(message)
    
    # Handle notifications and database storage
    if retval != "":  
        if notifymethod:
            logger.info(notifymethod)
            for _notifymet in notifymethod.split(","):
                logger.debug(_notifymet)
                if _notifymet.lower() == "telegram":
                    mng_telegram_notify(paramd, notify, notifymessage, retval)
                    # Additional notification methods could be added here
                    
        if bool(storedb) == True:
            crudprefdata.create_perfdata(job['id'], retval, CONFIG)

    if retval:
        logger.info(f"job {job['id']} executed retval={retval}")
    else:
        logger.info(f"job {job['id']} executed {datetime.now()}")


def mng_telegram_notify(paramd, notify, notifymessage, retval):
    """
    Send notification via Telegram
    
    Args:
        paramd: Parameters dictionary
        notify: Notification condition
        notifymessage: Message to send
        retval: Execution result value
    """
    if notify and notifymessage:
        globals()['retval'] = retval
        globals().update(paramd)
        if bool(common.check_for_notify(notify)):
            mes = common.effify(notifymessage, globals())
            sendtelegram(CONFIG, mes)


# Initialize and start the scheduler
now = datetime.now()

from apscheduler.schedulers import background
job_defaults = {
    'coalesce': False,
    'max_instances': 10
}

scheduler = background.BlockingScheduler(job_defaults=job_defaults, jobstores=jobstores,timezone=pytz.timezone(CONFIG.TIMEZONE))

# Add a job to check for scheduler updates every 60 seconds
scheduler.add_job(lambda: schedule_jobs(scheduler), 'interval', seconds=60, next_run_time=datetime.now(), id='scheduler-job-id')
scheduler.start() 