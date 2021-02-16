import sqlite3
from datetime import datetime


def select_model(company_id, project_name, model_id):
    conn = sqlite3.connect('database.db')

    c = conn.cursor()

    c.execute("""
    SELECT * FROM files
    WHERE company_id = ? AND project_name = ? AND model_id = ?
    """, (company_id, project_name, model_id))

    existing = c.fetchone()

    if not existing:
        model = None
    
    else:
        model = {
            'company_id': existing[1],
            'project_name': existing[2],
            'model_id': existing[3],
            'model_name': existing[4],
            'model_version': existing[5],
            'time_recieved': existing[6],
        }

    conn.close()

    return model

def update(company_id, project_name, model_id, model_name, model_version):
    conn = sqlite3.connect('database.db')

    c = conn.cursor()

    time_recieved = datetime.strftime(datetime.now(), '%Y-%m-%d(%H%M)')

    # try to update existing record
    c.execute("""
        UPDATE files
        SET model_version = ?, time_recieved = ?
        WHERE company_id = ? AND project_name = ? AND model_id = ?
        """, (model_version, time_recieved, company_id, project_name, model_id))

    if c.rowcount == 0:
        # if no existing record, insert new
        c.execute("""
            INSERT INTO files
            VALUES (NULL, ?, ?, ?, ?, ?, ?)
        """, (company_id, project_name, model_id, model_name, model_version, time_recieved))
    
        if c.rowcount == 0:
            conn.close()
            raise Exception('SQL query error')
    
    conn.commit()
    conn.close()

def file_is_new(_company_id, _project_name, model_info: dict) -> bool:
    existing_file = select_model(_company_id, _project_name, model_info['model_id'])

    if existing_file:
        return model_info['model_version'] > existing_file['model_version']

    else:
        return True
