import logging
import sqlite3
import uuid
import datetime
from typing import Dict, List, Optional, Any, Union
import util.common as common
logger = logging.getLogger()

class Perfdata:
  
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        # Assicurati che la tabella esista
        self.create_table()
    
    def create_table(self) -> bool:
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS perfdata (
                id TEXT NOT NULL PRIMARY KEY,
                jobname TEXT NOT NULL,
                value TEXT NOT NULL,
                utctsins TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
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
    def create_perfdata(self, jobname: str, value: str, CONFIG, custom_id: str = None) -> Optional[str]:
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Genera un nuovo UUID se non è stato fornito
            record_id = custom_id if custom_id else str(uuid.uuid4())
            timefomatted = common.calcolateformatted_timestamp(CONFIG)

            
            cursor.execute('''
            INSERT INTO perfdata (id, jobname, value, utctsins)
            VALUES (?, ?, ?, ?)
            ''', (record_id, jobname, value, timefomatted))
            
            conn.commit()
            return record_id
            
        except sqlite3.Error as e:
            logger.error(f"Erorr insert job: {e}")
            return None
        finally:
            if conn:
                conn.close()
    
    # READ ONE
    def read_perfdata(self, record_id: str) -> Optional[Dict[str, Any]]:
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT id, jobname, value, utctsins
            FROM perfdata
            WHERE id = ?
            ''', (record_id,))
            
            row = cursor.fetchone()
            
            if row:
                return {
                    'id': row['id'],
                    'jobname': row['jobname'],
                    'value': row['value'],
                    'utctsins': row['utctsins']
                }
            else:
                return None
                
        except sqlite3.Error as e:
            logger.error(f"Error reading: {e}")
            return None
        finally:
            if conn:
                conn.close()
    
    # READ ALL
    def read_all_perfdata(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT id, jobname, value, utctsins
            FROM perfdata
            ORDER BY utctsins DESC
            LIMIT ? OFFSET ?
            ''', (limit, offset))
            
            records = []
            for row in cursor.fetchall():
                records.append({
                    'id': row['id'],
                    'jobname': row['jobname'],
                    'value': row['value'],
                    'utctsins': row['utctsins']
                })
                
            return records
                
        except sqlite3.Error as e:
            logger.error(f"Erorr reading: {e}")
            return []
        finally:
            if conn:
                conn.close()
    
    # READ BY JOBNAME
    def read_perfdata_by_jobname(self, jobname: str, limit: int = 100) -> List[Dict[str, Any]]:
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT id, jobname, value, utctsins
            FROM perfdata
            WHERE jobname = ?
            ORDER BY utctsins DESC
            LIMIT ?
            ''', (jobname, limit))
            
            records = []
            for row in cursor.fetchall():
                records.append({
                    'id': row['id'],
                    'jobname': row['jobname'],
                    'value': row['value'],
                    'utctsins': row['utctsins']
                })
                
            return records
                
        except sqlite3.Error as e:
            logger.error(f"Error reading: {e}")
            return []
        finally:
            if conn:
                conn.close()
    
    # READ BY DATE RANGE
    def read_perfdata_by_date_range(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:

        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT id, jobname, value, utctsins
            FROM perfdata
            WHERE utctsins BETWEEN ? AND ?
            ORDER BY utctsins DESC
            ''', (start_date, end_date))
            
            records = []
            for row in cursor.fetchall():
                records.append({
                    'id': row['id'],
                    'jobname': row['jobname'],
                    'value': row['value'],
                    'utctsins': row['utctsins']
                })
                
            return records
                
        except sqlite3.Error as e:
            logger.error(f"Error reading: {e}")
            return []
        finally:
            if conn:
                conn.close()
    
    # UPDATE
    def update_perfdata(self, record_id: str, jobname: str = None, value: str = None) -> bool:
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Leggi i valori attuali
            current_record = self.read_perfdata(record_id)
            if not current_record:
                logger.info(f"Record '{record_id}' don't find.")
                return False
            
            # Usa i nuovi valori se specificati, altrimenti mantieni quelli attuali
            new_jobname = jobname if jobname is not None else current_record['jobname']
            new_value = value if value is not None else current_record['value']
            
            cursor.execute('''
            UPDATE perfdata
            SET jobname = ?, value = ?
            WHERE id = ?
            ''', (new_jobname, new_value, record_id))
            
            if cursor.rowcount == 0:
                logger.info(f"No record found ID '{record_id}'.")
                return False
                
            conn.commit()
            return True
            
        except sqlite3.Error as e:
            logger.error(f"Error in update: {e}")
            return False
        finally:
            if conn:
                conn.close()
    
    # DELETE
    def delete_perfdata(self, record_id: str) -> bool:
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM perfdata WHERE id = ?', (record_id,))
            
            if cursor.rowcount == 0:
                logger.info(f"No record found ID '{record_id}'.")
                return False
                
            conn.commit()
            return True
            
        except sqlite3.Error as e:
            logger.error(f"Error in delete: {e}")
            return False
        finally:
            if conn:
                conn.close()
    
    # DELETE BY JOBNAME
    def delete_perfdata_by_jobname(self, jobname: str) -> int:
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM perfdata WHERE jobname = ?', (jobname,))
            deleted_count = cursor.rowcount
            
            conn.commit()
            return deleted_count
            
        except sqlite3.Error as e:
            logger.error(f"Error in delete: {e}")
            return 0
        finally:
            if conn:
                conn.close()
    
    # DELETE OLD DATA
    def delete_old_perfdata(self, days: int) -> int:
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            DELETE FROM perfdata 
            WHERE utctsins < datetime('now', '-' || ? || ' days')
            ''', (days,))
            
            deleted_count = cursor.rowcount
            conn.commit()
            return deleted_count
            
        except sqlite3.Error as e:
            logger.error(f"Error delete old record: {e}")
            return 0
        finally:
            if conn:
                conn.close()
    
    # COUNT BY JOBNAME
    def count_perfdata_by_jobname(self, jobname: str = None) -> Dict[str, int]:
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if jobname:
                cursor.execute('''
                SELECT COUNT(*) as count
                FROM perfdata
                WHERE jobname = ?
                ''', (jobname,))
                
                count = cursor.fetchone()[0]
                return {jobname: count}
            else:
                cursor.execute('''
                SELECT jobname, COUNT(*) as count
                FROM perfdata
                GROUP BY jobname
                ORDER BY jobname
                ''')
                
                result = {}
                for row in cursor.fetchall():
                    result[row[0]] = row[1]
                return result
                
        except sqlite3.Error as e:
            logger.error(f"Error count record: {e}")
            return {}
        finally:
            if conn:
                conn.close()
    
    # GET STATISTICS
    def get_perfdata_statistics(self, jobname: str = None, days: int = 30) -> Dict[str, Any]:
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Costruzione della query in base ai parametri
            query = '''
            SELECT 
                COUNT(*) as count,
                MIN(CAST(value as REAL)) as min_value,
                MAX(CAST(value as REAL)) as max_value,
                AVG(CAST(value as REAL)) as avg_value
            FROM perfdata
            WHERE utctsins >= datetime('now', '-' || ? || ' days')
            '''
            
            params = [days]
            
            if jobname:
                query += " AND jobname = ?"
                params.append(jobname)
            
            cursor.execute(query, params)
            row = cursor.fetchone()
            
            if row:
                return {
                    'count': row[0],
                    'min_value': row[1],
                    'max_value': row[2],
                    'avg_value': row[3]
                }
            else:
                return {
                    'count': 0,
                    'min_value': None,
                    'max_value': None,
                    'avg_value': None
                }
                
        except sqlite3.Error as e:
            logger.error(f"Error in stat: {e}")
            return {
                'count': 0,
                'min_value': None,
                'max_value': None,
                'avg_value': None
            }
        finally:
            if conn:
                conn.close()

