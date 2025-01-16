import sqlite3
import pytest
import json
from datetime import datetime
from src.dimensional_modelling import create_dimensional_tables, populate_dim_date, populate_dim_book, populate_dim_list, populate_book_rankings

@pytest.fixture
def test_db_with_json():
    """
    Create an in-memory SQLite database, ingest JSON data, and populate all tables.
    """
    conn = sqlite3.connect(":memory:")
    create_dimensional_tables(conn)
    
    # Load JSON test data
    with open("tests/sample_data.json", "r") as f:
        raw_data = json.load(f)

    # Populate DimDate table
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 1, 8)  # Cover one week for simplicity
    populate_dim_date(conn, start_date, end_date)
    
    # Populate DimBook, DimList, and BookRankings tables
    populate_dim_book(conn, raw_data)
    populate_dim_list(conn, raw_data)
    populate_book_rankings(conn, raw_data)
    
    yield conn
    conn.close()

def test_dim_date_population(test_db_with_json):
    """
    Test that DimDate table is populated correctly.
    """
    cursor = test_db_with_json.cursor()
    cursor.execute("SELECT * FROM DimDate WHERE date_key = 20230101")
    result = cursor.fetchone()
    assert result is not None
    assert result[1] == "2023-01-01"  # full_date
    assert result[2] == 2023          # year
    assert result[3] == 1             # quarter
    assert result[4] == 1             # month
    assert result[5] == 52            # week
    assert result[6] == 7             # day_of_week

def test_dim_book_population(test_db_with_json):
    """
    Test that DimBook table is populated correctly.
    """
    cursor = test_db_with_json.cursor()
    cursor.execute("SELECT * FROM DimBook WHERE isbn = '1234567890'")
    result = cursor.fetchone()
    assert result is not None
    assert result[2] == "Book A"        # title
    assert result[3] == "Author A"      # author
    assert result[4] == "Publisher A"   # publisher

def test_dim_list_population(test_db_with_json):
    """
    Test that DimList table is populated correctly.
    """
    cursor = test_db_with_json.cursor()
    cursor.execute("SELECT * FROM DimList WHERE list_name = 'list_1'")
    result = cursor.fetchone()
    assert result is not None
    assert result[1] == "list_1"      # list_name
    assert result[2] == "List 1"      # display_name

def test_book_rankings_population(test_db_with_json):
    """
    Test that BookRankings table is populated correctly.
    """
    cursor = test_db_with_json.cursor()
    cursor.execute("SELECT * FROM BookRankings WHERE rank = 1")
    result = cursor.fetchone()
    assert result is not None
    assert result[1] == 1             # book_key
    assert result[2] == 1             # list_key
    assert result[3] == 20230101      # date_key
    assert result[4] == 1             # rank
    assert result[5] == 0             # rank_last_week
    assert result[6] == 1             # weeks_on_list