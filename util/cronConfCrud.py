import logging
import sqlite3
import json
from typing import Dict, List, Optional, Any, Union
logger = logging.getLogger()

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
            logger.error(f"Error create table: {e}")
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
                logger.info(f"Job with ID '{jobid}' exist")
                return False
            conf_json = json.dumps(conf)
            cursor.execute('''
            INSERT INTO cronconf (jobid, cronexpr, crondecode, conf)
            VALUES (?, ?, ?, ?)
            ''', (jobid, cronexpr, crondecode, conf_json))
            
            conn.commit()
            return True
            
        except sqlite3.Error as e:
            logger.error(f"Error insert job: {e}")
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
            logger.error(f"Erorr during job: {e}")
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
            logger.error(f"Error reading job: {e}")
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
                logger.info(f"Job with ID '{jobid}' not found.")
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
                logger.info(f"no job fonund with ID '{jobid}'.")
                return False
                
            conn.commit()
            return True
            
        except sqlite3.Error as e:
            logger.error(f"erorr update job: {e}")
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
                logger.info(f"job don't found by ID '{jobid}'.")
                return False
                
            conn.commit()
            return True
            
        except sqlite3.Error as e:
            logger.error(f"error delete job: {e}")
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
            logger.error(f"error insert/update job: {e}")
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
                conf_dict = json.loads(row['conf']) if row['conf'] else {}
                
                jobs.append({
                    'jobid': row['jobid'],
                    'cronexpr': row['cronexpr'],
                    'crondecode': row['crondecode'],
                    'conf': conf_dict
                })
                
            return jobs
                
        except sqlite3.Error as e:
            logger.error(f"error during search job: {e}")
            return []
        finally:
            if conn:
                conn.close()

