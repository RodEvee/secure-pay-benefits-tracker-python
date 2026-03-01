import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'tracker.db')

DEFAULT_SETTINGS = {
    "salary": {
        "hourlyRate": 25.0,
        "otThreshold": 40.0,
        "otMultiplier": 1.5
    },
    "deductions": {
        "healthEmployee": 50.0,
        "healthEmployer": 150.0,
        "dentalEmployee": 10.0,
        "dentalEmployer": 30.0,
        "visionEmployee": 5.0,
        "visionEmployer": 15.0,
        "k401EmployeeAmount": 0.0,
        "k401EmployeePercent": 5.0,
        "k401EmployerMatchPercent": 100.0,
        "isK401Percent": True
    },
    "isBiometricEnabled": True,
    "is2FAEnabled": False
}

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create User Settings table (key-value store for simplicity)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    
    # Create Time Entries table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS time_entries (
            id TEXT PRIMARY KEY,
            day TEXT,
            startTime TEXT,
            endTime TEXT,
            duration INTEGER
        )
    ''')
    
    conn.commit()
    conn.close()
    
    # Initialize default settings if empty
    if not get_settings():
        save_settings(DEFAULT_SETTINGS)

def get_settings():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT value FROM settings WHERE key = ?', ('user_settings',))
    row = cursor.fetchone()
    conn.close()
    if row:
        return json.loads(row[0])
    return None

def save_settings(settings):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO settings (key, value)
        VALUES (?, ?)
        ON CONFLICT(key) DO UPDATE SET value=excluded.value
    ''', ('user_settings', json.dumps(settings)))
    conn.commit()
    conn.close()

def save_time_entry(entry):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO time_entries (id, day, startTime, endTime, duration)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            day=excluded.day,
            startTime=excluded.startTime,
            endTime=excluded.endTime,
            duration=excluded.duration
    ''', (
        entry.get('id'),
        entry.get('day'),
        entry.get('startTime'),
        entry.get('endTime'),
        entry.get('duration')
    ))
    conn.commit()
    conn.close()

def get_time_entries():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, day, startTime, endTime, duration FROM time_entries ORDER BY day DESC, startTime DESC')
    rows = cursor.fetchall()
    conn.close()
    
    entries = []
    for row in rows:
        entries.append({
            'id': row[0],
            'day': row[1],
            'startTime': row[2],
            'endTime': row[3],
            'duration': row[4]
        })
    return entries

def delete_time_entry(entry_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM time_entries WHERE id = ?', (entry_id,))
    conn.commit()
    conn.close()
