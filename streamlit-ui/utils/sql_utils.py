import sqlite3

def execute_sql_file(db_path, sql_file_path):
    with open(sql_file_path, 'r', encoding='utf-8') as f:
        sql = f.read()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.executescript(sql)
    conn.commit()
    conn.close() 