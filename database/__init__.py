import sqlite3
import os

file = os.path.join('database', 'history.db')
if __name__ == '__main__':
    file = 'history.db'

history = sqlite3.connect(file, check_same_thread=False)
# history.row_factory = sqlite3.Row

with history:
    history.executescript("""
    CREATE TABLE IF NOT EXISTS request(
        req_id INTEGER PRIMARY KEY AUTOINCREMENT , -- уникальный номер запроса
        user INTEGER NOT NULL,                     -- ID пользователя
        date DATETIME DEFAULT CURRENT_TIMESTAMP,   -- дата, время запроса
        city INTEGER,                              -- ID запрошенной локации
        checkin DATE,                              -- дата заезда
        checkout DATE,                             -- дата выезда 
        sort TEXT                                  -- порядок сортировки
       );
    CREATE TABLE IF NOT EXISTS city(
        id   INTEGER  PRIMARY KEY NOT NULL,
        name TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS history(
        req_id INTEGER NOT NULL,
        id INTEGER,
        url TEXT,
        name TEXT,
        address TEXT,
        price TEXT,
        latitude REAL,
        longitude REAL,
        FOREIGN KEY (req_id) REFERENCES request (req_id) ON DELETE CASCADE
       );
    """)
