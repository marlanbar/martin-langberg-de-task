import sqlite3
from datetime import datetime, timedelta
import json

def create_dimensional_tables(conn):
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS DimDate (
        date_key INTEGER PRIMARY KEY,
        full_date TEXT,
        year INTEGER,
        quarter INTEGER,
        month INTEGER,
        week INTEGER,
        day_of_week INTEGER
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS DimBook (
        book_key INTEGER PRIMARY KEY,
        isbn TEXT,
        title TEXT NOT NULL,
        author TEXT,
        publisher TEXT,
        description TEXT,
        amazon_product_url TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS DimList (
        list_key INTEGER PRIMARY KEY,
        list_name TEXT NOT NULL,
        display_name TEXT NOT NULL,
        list_name_encoded TEXT NOT NULL,
        updated_frequency TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS BookRankings (
        ranking_id INTEGER PRIMARY KEY,
        book_key INTEGER,
        list_key INTEGER,
        date_key INTEGER,
        rank INTEGER,
        rank_last_week INTEGER,
        weeks_on_list INTEGER,
        FOREIGN KEY (book_key) REFERENCES DimBook (book_key),
        FOREIGN KEY (list_key) REFERENCES DimList (list_key),
        FOREIGN KEY (date_key) REFERENCES DimDate (date_key)
    )
    ''')
    
    conn.commit()

def populate_dim_date(conn, start_date, end_date):
    cursor = conn.cursor()
    current_date = start_date
    while current_date <= end_date:
        date_key = int(current_date.strftime('%Y%m%d'))
        cursor.execute('''
        INSERT OR IGNORE INTO DimDate (date_key, full_date, year, quarter, month, week, day_of_week)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            date_key,
            current_date.strftime('%Y-%m-%d'),
            current_date.year,
            (current_date.month - 1) // 3 + 1,
            current_date.month,
            current_date.isocalendar()[1],
            current_date.weekday() + 1
        ))
        current_date += timedelta(days=1)
    conn.commit()

def populate_dim_book(conn, raw_data):
    cursor = conn.cursor()
    for data in raw_data:
        for list_data in data['results']['lists']:
            for book in list_data['books']:
                cursor.execute('''
                INSERT OR IGNORE INTO DimBook (isbn, title, author, publisher, description, amazon_product_url)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    book.get('primary_isbn13', ''),
                    book['title'],
                    book['author'],
                    book['publisher'],
                    book.get('description', ''),
                    book.get('amazon_product_url', '')
                ))
    conn.commit()

def populate_dim_list(conn, raw_data):
    cursor = conn.cursor()
    for data in raw_data:
        for list_data in data['results']['lists']:
            cursor.execute('''
            INSERT OR IGNORE INTO DimList (list_name, display_name, list_name_encoded, updated_frequency)
            VALUES (?, ?, ?, ?)
            ''', (
                list_data['list_name'],
                list_data['display_name'],
                list_data['list_name_encoded'],
                list_data['updated']
            ))
    conn.commit()

def populate_book_rankings(conn, raw_data):
    cursor = conn.cursor()
    for data in raw_data:
        date_key = int(datetime.strptime(data['results']['published_date'], '%Y-%m-%d').strftime('%Y%m%d'))
        for list_data in data['results']['lists']:
            list_key = cursor.execute('SELECT list_key FROM DimList WHERE list_name = ?', (list_data['list_name'],)).fetchone()[0]
            for book in list_data['books']:
                book_key = cursor.execute('SELECT book_key FROM DimBook WHERE isbn = ?', (book['primary_isbn13'],)).fetchone()[0]
                cursor.execute('''
                INSERT INTO BookRankings (book_key, list_key, date_key, rank, rank_last_week, weeks_on_list)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    book_key,
                    list_key,
                    date_key,
                    book['rank'],
                    book.get('rank_last_week', 0),
                    book['weeks_on_list']
                ))
    conn.commit()

def create_dimensional_model(database_path, raw_data_path, start_date, end_date):
    conn = sqlite3.connect(database_path)
    create_dimensional_tables(conn)
    
    with open(raw_data_path, 'r') as f:
        raw_data = json.load(f)
    
    populate_dim_date(conn, start_date, end_date)
    populate_dim_book(conn, raw_data)
    populate_dim_list(conn, raw_data)
    populate_book_rankings(conn, raw_data)
    
    conn.close()

if __name__ == '__main__':
    database_path = 'nyt_bestsellers.db'
    raw_data_path = '../data/nyt_bestsellers_raw.json'
    create_dimensional_model(database_path, raw_data_path)
