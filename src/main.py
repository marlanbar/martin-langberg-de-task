from datetime import datetime
import os
from data_retrieval import fetch_and_store_data
from database_setup import database_setup
from dimensional_modelling import create_dimensional_model
from sql_queries import run_queries

def main():
    # Set up environment variables
    database_path = os.environ.get('DATABASE_PATH', 'data/nyt_bestsellers.db')
    raw_data_path = os.environ.get('RAW_DATA_PATH', 'data/nyt_bestsellers_raw.json')
    start_date = datetime(2021, 1, 1)
    end_date = datetime(2023, 12, 31)

    # Fetch and store data
    fetch_and_store_data(start_date, end_date)

    # Set up database
    database_setup(database_path)

    # Create dimensional model
    create_dimensional_model(database_path, raw_data_path, start_date, end_date)

    # Run SQL queries and export results
    run_queries(database_path)

if __name__ == '__main__':
    main()
