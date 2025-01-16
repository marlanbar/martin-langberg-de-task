import sqlite3
from sqlite3 import Error

def create_connection(database_path):
    conn = None
    try:
        conn = sqlite3.connect(database_path)
        print("SQLite database connection successful")
        return conn
    except Error as e:
        print(f"Error: {e}")
    
    return conn


def database_setup(database_path):    
    conn = create_connection(database_path=database_path)
    
    if conn is not None:
        conn.close()
    else:
        print("Error! Cannot create the database connection.")

if __name__ == '__main__':
    database_setup(database_path='nyt_bestsellers.db')
