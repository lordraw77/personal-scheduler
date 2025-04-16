import sqlite3
import json
from typing import Dict, List, Optional, Any, Union

class CronConf:

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.create_table()
    
    def create_table(self) -> bool:
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS cronconf (
                jobid TEXT NOT NULL,
                cronexpr TEXT,
                crondecode TEXT,
                conf TEXT,
                
                CONSTRAINT cronconf_pk PRIMARY KEY (jobid)
            );
            ''')
            
            conn.commit()
            return True
            
        except sqlite3.Error as e:
            print(f"Errore durante la creazione della tabella: {e}")
            return False
        finally:
            if conn:
                conn.close()
    
    # CREATE
    def create_job(self, jobid: str, cronexpr: str, crondecode: str, conf: Dict[str, Any]) -> bool:
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT jobid FROM cronconf WHERE jobid = ?", (jobid,))
            if cursor.fetchone():
                print(f"Job con ID '{jobid}' esiste già. Usa la funzione update_job per aggiornarlo.")
                return False
            conf_json = json.dumps(conf)
            cursor.execute('''
            INSERT INTO cronconf (jobid, cronexpr, crondecode, conf)
            VALUES (?, ?, ?, ?)
            ''', (jobid, cronexpr, crondecode, conf_json))
            
            conn.commit()
            return True
            
        except sqlite3.Error as e:
            print(f"Errore durante l'inserimento del job: {e}")
            return False
        finally:
            if conn:
                conn.close()
    def read_job(self, jobid: str) -> Optional[Dict[str, Any]]:
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Per accedere alle colonne per nome
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT jobid, cronexpr, crondecode, conf
            FROM cronconf
            WHERE jobid = ?
            ''', (jobid,))
            
            row = cursor.fetchone()
            
            if row:
                conf_dict = json.loads(row['conf']) if row['conf'] else {}
                
                return {
                    'jobid': row['jobid'],
                    'cronexpr': row['cronexpr'],
                    'crondecode': row['crondecode'],
                    'conf': conf_dict
                }
            else:
                return None
                
        except sqlite3.Error as e:
            print(f"Errore durante la lettura del job: {e}")
            return None
        finally:
            if conn:
                conn.close()
    
    # READ ALL
    def read_all_jobs(self) -> List[Dict[str, Any]]:
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT jobid, cronexpr, crondecode, conf FROM cronconf')
            
            jobs = []
            for row in cursor.fetchall():
                # Converte la stringa JSON in dizionario
                conf_dict = json.loads(row['conf']) if row['conf'] else {}
                
                jobs.append({
                    'jobid': row['jobid'],
                    'cronexpr': row['cronexpr'],
                    'crondecode': row['crondecode'],
                    'conf': conf_dict
                })
                
            return jobs
                
        except sqlite3.Error as e:
            print(f"Errore durante la lettura dei job: {e}")
            return []
        finally:
            if conn:
                conn.close()
    
    # UPDATE
    def update_job(self, jobid: str, cronexpr: Optional[str] = None, 
                  crondecode: Optional[str] = None, conf: Optional[Dict[str, Any]] = None) -> bool:
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            current_job = self.read_job(jobid)
            if not current_job:
                print(f"Job con ID '{jobid}' non trovato.")
                return False
            new_cronexpr = cronexpr if cronexpr is not None else current_job['cronexpr']
            new_crondecode = crondecode if crondecode is not None else current_job['crondecode']
            new_conf = conf if conf is not None else current_job['conf']
            conf_json = json.dumps(new_conf)
            
            cursor.execute('''
            UPDATE cronconf
            SET cronexpr = ?, crondecode = ?, conf = ?
            WHERE jobid = ?
            ''', (new_cronexpr, new_crondecode, conf_json, jobid))
            
            if cursor.rowcount == 0:
                print(f"Nessun job aggiornato con ID '{jobid}'.")
                return False
                
            conn.commit()
            return True
            
        except sqlite3.Error as e:
            print(f"Errore durante l'aggiornamento del job: {e}")
            return False
        finally:
            if conn:
                conn.close()
    
    # DELETE
    def delete_job(self, jobid: str) -> bool:
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM cronconf WHERE jobid = ?', (jobid,))
            
            if cursor.rowcount == 0:
                print(f"Nessun job trovato con ID '{jobid}'.")
                return False
                
            conn.commit()
            return True
            
        except sqlite3.Error as e:
            print(f"Errore durante l'eliminazione del job: {e}")
            return False
        finally:
            if conn:
                conn.close()
    
    # UPSERT (INSERT OR UPDATE)
    def upsert_job(self, jobid: str, cronexpr: str, crondecode: str, conf: Dict[str, Any]) -> bool:
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Converti il dizionario conf in stringa JSON
            conf_json = json.dumps(conf)
            
            cursor.execute('''
            INSERT OR REPLACE INTO cronconf (jobid, cronexpr, crondecode, conf)
            VALUES (?, ?, ?, ?)
            ''', (jobid, cronexpr, crondecode, conf_json))
            
            conn.commit()
            return True
            
        except sqlite3.Error as e:
            print(f"Errore durante l'inserimento/aggiornamento del job: {e}")
            return False
        finally:
            if conn:
                conn.close()
    
    # SEARCH
    def search_jobs(self, search_term: str) -> List[Dict[str, Any]]:
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Prepara il termine di ricerca per LIKE
            search_pattern = f"%{search_term}%"
            
            cursor.execute('''
            SELECT jobid, cronexpr, crondecode, conf
            FROM cronconf
            WHERE jobid LIKE ? OR cronexpr LIKE ? OR crondecode LIKE ?
            ''', (search_pattern, search_pattern, search_pattern))
            
            jobs = []
            for row in cursor.fetchall():
                # Converte la stringa JSON in dizionario
                conf_dict = json.loads(row['conf']) if row['conf'] else {}
                
                jobs.append({
                    'jobid': row['jobid'],
                    'cronexpr': row['cronexpr'],
                    'crondecode': row['crondecode'],
                    'conf': conf_dict
                })
                
            return jobs
                
        except sqlite3.Error as e:
            print(f"Errore durante la ricerca dei job: {e}")
            return []
        finally:
            if conn:
                conn.close()


if __name__ == "__main__":
    db_path = "database.db"  # Sostituisci con il tuo percorso
    crud = CronConfCrud(db_path)
    
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