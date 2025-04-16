from logging.handlers import TimedRotatingFileHandler
import util.common as common
import util.config as config
import util.cronConfCrud as CronConfCrud
import util.db as db
import logging
import sys
import os


CONFIG =  config.Config("./config.yaml")        

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




crud = CronConfCrud.CronConf(db_path)

# Esempio di creazione
job1 = {
    "jobid": "backup_daily",
    "cronexpr": "0 0 * * *",
    "crondecode": "Ogni giorno a mezzanotte",
    "conf": {
        "command": "/usr/bin/backup.sh",
        "timeout": 3600,
        "notify_email": "admin@example.com"
    }
}

job2 = {
    "jobid": "cleanup_weekly",
    "cronexpr": "0 0 * * 0",
    "crondecode": "Ogni domenica a mezzanotte",
    "conf": {
        "command": "/usr/bin/cleanup.sh",
        "timeout": 7200,
        "notify_email": "admin@example.com"
    }
}

# Creazione job
print("Creazione job...")
crud.create_job(job1["jobid"], job1["cronexpr"], job1["crondecode"], job1["conf"])
crud.create_job(job2["jobid"], job2["cronexpr"], job2["crondecode"], job2["conf"])

# Lettura job
print("\nLettura job 'backup_daily':")
job = crud.read_job("backup_daily")
if job:
    print(f"ID: {job['jobid']}")
    print(f"Cron: {job['cronexpr']}")
    print(f"Decodifica: {job['crondecode']}")
    print(f"Configurazione: {job['conf']}")

# Lettura di tutti i job
print("\nTutti i job:")
all_jobs = crud.read_all_jobs()
for job in all_jobs:
    print(f"ID: {job['jobid']}, Cron: {job['cronexpr']}")

# Aggiornamento job
print("\nAggiornamento job 'backup_daily'...")
updated_conf = {
    "command": "/usr/bin/backup.sh",
    "timeout": 4800,  # Modificato
    "notify_email": "admin@example.com",
    "compress": True  # Aggiunto
}
crud.update_job("backup_daily", cronexpr="0 0 * * *", conf=updated_conf)

# Verifica aggiornamento
print("\nJob aggiornato:")
updated_job = crud.read_job("backup_daily")
if updated_job:
    print(f"ID: {updated_job['jobid']}")
    print(f"Configurazione: {updated_job['conf']}")

# Upsert (inserimento o aggiornamento)
print("\nUpsert job 'system_hourly'...")
new_job = {
    "jobid": "system_hourly",
    "cronexpr": "0 * * * *",
    "crondecode": "Ogni ora",
    "conf": {
        "command": "/usr/bin/system_check.sh",
        "timeout": 300
    }
}
crud.upsert_job(new_job["jobid"], new_job["cronexpr"], new_job["crondecode"], new_job["conf"])

# Ricerca job
print("\nRicerca job con 'daily':")
search_results = crud.search_jobs("daily")
for job in search_results:
    print(f"ID: {job['jobid']}, Decodifica: {job['crondecode']}")

# Eliminazione job
print("\nEliminazione job 'cleanup_weekly'...")
crud.delete_job("cleanup_weekly")

# Verifica eliminazione
print("\nTutti i job dopo eliminazione:")
remaining_jobs = crud.read_all_jobs()
for job in remaining_jobs:
    print(f"ID: {job['jobid']}, Cron: {job['cronexpr']}")
    print(f"delete {job['jobid']}")
    crud.delete_job(job['jobid'])
