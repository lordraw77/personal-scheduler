
 
crud = PerfdataCrud.Perfdata(db_path)

# Esempio di creazione di alcuni record
print("Creazione record di performance...")

# Crea alcuni record di esempio
record1_id = crud.create_perfdata("cpu_load", "42.5")
record2_id = crud.create_perfdata("memory_usage", "1248.6")
record3_id = crud.create_perfdata("disk_io", "156.7")
record4_id = crud.create_perfdata("cpu_load", "38.9")

print(f"Record creati con ID: {record1_id}, {record2_id}, {record3_id}, {record4_id}")

# Lettura di un record specifico
print("\nLettura di un record specifico:")
record = crud.read_perfdata(record1_id)
if record:
    print(f"ID: {record['id']}")
    print(f"Job: {record['jobname']}")
    print(f"Valore: {record['value']}")
    print(f"Timestamp: {record['utctsins']}")

# Lettura di tutti i record
print("\nTutti i record (ultimi 100):")
all_records = crud.read_all_perfdata(limit=100)
for record in all_records:
    print(f"ID: {record['id']}, Job: {record['jobname']}, Valore: {record['value']}")

# Lettura dei record per jobname
print("\nRecord per il job 'cpu_load':")
cpu_records = crud.read_perfdata_by_jobname("cpu_load")
for record in cpu_records:
    print(f"ID: {record['id']}, Valore: {record['value']}, Timestamp: {record['utctsins']}")

# Aggiornamento di un record
print("\nAggiornamento di un record...")
crud.update_perfdata(record1_id, value="45.2")

# Verifica aggiornamento
updated_record = crud.read_perfdata(record1_id)
print("\nRecord aggiornato:")
if updated_record:
    print(f"ID: {updated_record['id']}")
    print(f"Job: {updated_record['jobname']}")
    print(f"Valore: {updated_record['value']}")
    print(f"Timestamp: {updated_record['utctsins']}")

# Conteggio per jobname
print("\nConteggio record per jobname:")
counts = crud.count_perfdata_by_jobname()
for job, count in counts.items():
    print(f"{job}: {count} record")

# Statistiche
print("\nStatistiche per tutti i job (ultimi 30 giorni):")
stats = crud.get_perfdata_statistics()
print(f"Numero totale: {stats['count']}")
print(f"Valore minimo: {stats['min_value']}")
print(f"Valore massimo: {stats['max_value']}")
print(f"Valore medio: {stats['avg_value']}")

# Eliminazione di un record
print("\nEliminazione di un record...")
crud.delete_perfdata(record3_id)

# Eliminazione per jobname
print("\nEliminazione record per jobname...")
deleted = crud.delete_perfdata_by_jobname("memory_usage")
print(f"Eliminati {deleted} record per 'memory_usage'")

# Verifica eliminazione
print("\nTutti i record dopo eliminazione:")
remaining_records = crud.read_all_perfdata()
for record in remaining_records:
    print(f"ID: {record['id']}, Job: {record['jobname']}, Valore: {record['value']}")
    crud.delete_perfdata(record['id'])
    
    
    
# crud = CronConfCrud.CronConf(db_path)

# # Esempio di creazione
# job1 = {
#     "jobid": "backup_daily",
#     "cronexpr": "0 0 * * *",
#     "crondecode": "Ogni giorno a mezzanotte",
#     "conf": {
#         "command": "/usr/bin/backup.sh",
#         "timeout": 3600,
#         "notify_email": "admin@example.com"
#     }
# }

# job2 = {
#     "jobid": "cleanup_weekly",
#     "cronexpr": "0 0 * * 0",
#     "crondecode": "Ogni domenica a mezzanotte",
#     "conf": {
#         "command": "/usr/bin/cleanup.sh",
#         "timeout": 7200,
#         "notify_email": "admin@example.com"
#     }
# }

# # Creazione job
# print("Creazione job...")
# crud.create_job(job1["jobid"], job1["cronexpr"], job1["crondecode"], job1["conf"])
# crud.create_job(job2["jobid"], job2["cronexpr"], job2["crondecode"], job2["conf"])

# # Lettura job
# print("\nLettura job 'backup_daily':")
# job = crud.read_job("backup_daily")
# if job:
#     print(f"ID: {job['jobid']}")
#     print(f"Cron: {job['cronexpr']}")
#     print(f"Decodifica: {job['crondecode']}")
#     print(f"Configurazione: {job['conf']}")

# # Lettura di tutti i job
# print("\nTutti i job:")
# all_jobs = crud.read_all_jobs()
# for job in all_jobs:
#     print(f"ID: {job['jobid']}, Cron: {job['cronexpr']}")

# # Aggiornamento job
# print("\nAggiornamento job 'backup_daily'...")
# updated_conf = {
#     "command": "/usr/bin/backup.sh",
#     "timeout": 4800,  # Modificato
#     "notify_email": "admin@example.com",
#     "compress": True  # Aggiunto
# }
# crud.update_job("backup_daily", cronexpr="0 0 * * *", conf=updated_conf)

# # Verifica aggiornamento
# print("\nJob aggiornato:")
# updated_job = crud.read_job("backup_daily")
# if updated_job:
#     print(f"ID: {updated_job['jobid']}")
#     print(f"Configurazione: {updated_job['conf']}")

# # Upsert (inserimento o aggiornamento)
# print("\nUpsert job 'system_hourly'...")
# new_job = {
#     "jobid": "system_hourly",
#     "cronexpr": "0 * * * *",
#     "crondecode": "Ogni ora",
#     "conf": {
#         "command": "/usr/bin/system_check.sh",
#         "timeout": 300
#     }
# }
# crud.upsert_job(new_job["jobid"], new_job["cronexpr"], new_job["crondecode"], new_job["conf"])

# # Ricerca job
# print("\nRicerca job con 'daily':")
# search_results = crud.search_jobs("daily")
# for job in search_results:
#     print(f"ID: {job['jobid']}, Decodifica: {job['crondecode']}")

# # Eliminazione job
# print("\nEliminazione job 'cleanup_weekly'...")
# crud.delete_job("cleanup_weekly")

# # Verifica eliminazione
# print("\nTutti i job dopo eliminazione:")
# remaining_jobs = crud.read_all_jobs()
# for job in remaining_jobs:
#     print(f"ID: {job['jobid']}, Cron: {job['cronexpr']}")
#     print(f"delete {job['jobid']}")
#     crud.delete_job(job['jobid'])
