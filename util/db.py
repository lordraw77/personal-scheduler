import os
import sqlite3
import logging
logger = logging.getLogger()

def create_sqlite_database(db_path):
    try:
        conn = sqlite3.connect(db_path)
        print(f"Database SQLite '{db_path}' creato/connesso con successo.")
        return conn
    except sqlite3.Error as e:
        print(f"Errore durante la creazione del database: {e}")
        return None

def check_sqlite_db_exists(db_path):
    file_exists = os.path.isfile(db_path)    
    if not file_exists:
        return False, False
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT sqlite_version();")
        conn.close()
        return True, True
    except sqlite3.Error:
        return True, False
    
def check_table_exists(db_path, table_name):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT count(name) FROM sqlite_master 
            WHERE type='table' AND name='{table_name}'
        """)
        if cursor.fetchone()[0] == 1:
            return True
        else:
            return False
    except sqlite3.Error as e:
        logger.error(f"Errore SQLite: {e}")
        return False
    finally:
        if conn:
            conn.close()

def create_cronconf_table(db_path):

    try:
        conn = sqlite3.connect(db_path)
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
        logger.info("Tabella 'cronconf' creata con successo o già esistente.")
        return True
        
    except sqlite3.Error as e:
        logger.error(f"Errore durante la creazione della tabella: {e}")
        return False
    finally:
        if conn:
            conn.close()