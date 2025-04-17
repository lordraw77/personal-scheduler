from datetime import datetime, timezone
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

db_path = "ps.db"
exists, is_valid = db.check_sqlite_db_exists(db_path)

if exists and is_valid:
    logger.info(f"'{db_path}' exists and is a valid SQLite database.")
elif exists and not is_valid:
    logger.error(f"'{db_path}' exists but is not a valid SQLite database.")
else:
    logger.error(f"'{db_path}' does not exist.")

table_cronconf = "cronconf"

if db.check_table_exists(db_path, table_cronconf):
    logger.info(f" the table '{table_cronconf}'  exists ")
else:
    logger.error(f"the table '{table_cronconf}' don't exists")
    db.create_cronconf_table(db_path)
    
crudconf = CronConfCrud.CronConf(db_path)
crudprefdata= PerfdataCrud.Perfdata(db_path)
        

def get_method(module,method):
    mymethod = getattr(importlib.import_module(module), method)
    return mymethod

def schedule_jobs(scheduler):
    jobs = retrieve_jobs_to_schedule()
    for job in jobs: 
        add_job_if_applicable(job, scheduler)
        update_job_if_applicable(job, scheduler)

    #logger.info(f"{datetime.now()} refreshed scheduled jobs")

def retrieve_jobs_to_schedule():
    cwd = os.getcwd()
    jobs = []
    jobfolder="job.d"
    jobfolderd = os.path.join(cwd,jobfolder)
    for file in os.listdir(jobfolderd):
        if file.endswith(".json"):
            logger.debug(f"load job {file}")
            with open(os.path.join(jobfolderd, file),'r') as file:
                jobs.extend(json.load(file))

    return jobs


def add_job_if_applicable(job, scheduler): 
    job_id = str(job['id'])
    if (job_id not in scheduled_jobs_map):
        scheduled_jobs_map[job_id] = job
        scheduler.add_job(lambda: execute_job(job), CronTrigger.from_crontab(job['cron_expression'], timezone=timezone("Europe/Rome")), id=job_id)
        message = "added job with id: " + str(job_id) + " "+ job['cron_expression'] + "  " + common.crondecode(job['cron_expression'])
        crudconf.create_job(job_id, job['cron_expression'], common.crondecode(job['cron_expression']), job)
        #print(message)
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
        scheduler.add_job(lambda: execute_job(job), CronTrigger.from_crontab(job['cron_expression'], timezone=timezone("Europe/Rome")), id=job_id)
        message = "updated job with id: " + str(job_id) + " "+ job['cron_expression'] + "  " + common.crondecode(job['cron_expression'])
        crudconf.upsert_job(job_id, job['cron_expression'], common.crondecode(job['cron_expression']), job)
        #print(message)
        logger.info(message)
 
def execute_job(job):
    message = f"{datetime.now()} executing job with id:  {str(job['id'])} {job['module']}  {job['method']}"
    #print(message)
    logger.info(message)
    methodtoexecute = get_method(job['module'],job['method'])
    paramd = {}
    paramd = common.check_parma_and_load(job,'param')
    notify =  common.check_parma_and_load(job,'notify')
    notifymessage =  common.check_parma_and_load(job,'notifymessage')
    notifymethod =  common.check_parma_and_load(job,'notifymethod')
    notifysubject=  common.check_parma_and_load(job,'notifysubject')
    storedb=  common.check_parma_and_load(job,'storedb')
    notifyforced = common.check_parma_and_load(job,'notifyforced')
    paramd.update( config)
    retval =""
    if paramd:
        retval= methodtoexecute(paramd,logger)   
        message= f"executed {job['id']} {job['module']} {job['method']} the result are {retval}"
        logger.info(message)
    else:
        methodtoexecute(datetime.now())  
    if retval != "":  
        if notifymethod:
            logger.info(notifymethod)
            for _notifymet in notifymethod.split(","):
                logger.debug(_notifymet)
                if _notifymet.lower() == "telegram":
                    if notify and notifymessage:
                        globals()['retval']=retval
                        globals().update(paramd)
                        if bool(common.check_for_notify(notify)):
                            mes = common.effify(notifymessage)
                            #notifyservice.sendtelegram(mes,logger,config,job['id'],notifyforced)
                elif _notifymet.lower() =="mail":   
                    globals()['retval']=retval
                    globals().update(paramd)
                    if bool(common.check_for_notify(notify)):
                        mes = common.effify(notifymessage)
                        subject = f"output {job['id']}"
                        if notifysubject:
                            subject =notifysubject 
                        #notifyservice.sendmail(mes,subject,logger,config,job['id'],notifyforced)
        if bool(storedb) == True:
            #edb.insertperfdata(config,logger,job['id'],retval)
            crudprefdata.create_perfdata(job['id'],retval)
         

    if retval:
        logger.info(f"job {job['id']} executed retval={retval}")
    else:
        logger.info(f"job {job['id']} executed {datetime.now()}")


#notifyservice.sendtelegram(f"start openmonitoring with {json.dumps(config)}",logger,config,forced=True)

now = datetime.now()
#notifyservice.sendtelegram(f"start  at {now}",logger,config,forced=True)

from apscheduler.schedulers import background
job_defaults = {
    'coalesce': False,
    'max_instances': 10
}


#scheduler = BackgroundScheduler(timezone=timezone("Europe/Rome"))
scheduler = background.BlockingScheduler(job_defaults=job_defaults,timezone=timezone("Europe/Rome"))
# scheduler.configure( job_defaults=job_defaults)

scheduler.add_job(lambda: schedule_jobs(scheduler), 'interval', seconds=5, next_run_time=datetime.now(), id='scheduler-job-id')
scheduler.start()









common.sendtelegram(CONFIG,"start")
