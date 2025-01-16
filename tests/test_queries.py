import sqlite3
import pytest
from datetime import datetime
from src.dimensional_modelling import create_dimensional_tables
from src.sql_queries import QUERY_1, QUERY_2, QUERY_3, QUERY_4

@pytest.fixture
def test_db():
    """
    Create an in-memory SQLite database for testing.
    """
    cursor = sqlite3.connect(":memory:")
    create_dimensional_tables(cursor)
    
    # Populate the tables with minimal test data
    cursor.executemany('''
    INSERT INTO DimDate (date_key, full_date, year, quarter, month, week, day_of_week)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', [
        (20220101, '2022-01-01', 2022, 1, 1, 1, 1),
        (20230101, '2023-01-01', 2023, 1, 1, 1, 1),
        (20230108, '2023-01-08', 2023, 1, 1, 2, 1)
    ])

    cursor.executemany('''
    INSERT INTO DimBook (book_key, isbn, title, author, publisher, description, amazon_product_url)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', [
        (1, '1234567890', 'Book A', 'Author A', 'Publisher A', 'Description A', 'http://example.com/a'),
        (2, '0987654321', 'Book B', 'Author B', 'Publisher B', 'Description B', 'http://example.com/b'),
        (3, '1357924680', 'Book C', 'Author C', 'Publisher C', 'Description C', 'http://example.com/c')
    ])

    cursor.executemany('''
    INSERT INTO DimList (list_key, list_name, display_name, list_name_encoded, updated_frequency)
    VALUES (?, ?, ?, ?, ?)
    ''', [
        (0, 'list_0', 'List 0', 'list_0_encoded', 'DAILY'),
        (1, 'list_1', 'List 1', 'list_1_encoded', 'WEEKLY')
    ])

    cursor.executemany('''
    INSERT INTO BookRankings (ranking_id, book_key, list_key, date_key, rank, rank_last_week, weeks_on_list)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', [
        (0, 3, 0, 20220101, 1, 0, 1),
        (1, 1, 1, 20230101, 1, 0, 1),
        (2, 2, 1, 20230101, 3, 0, 1)
    ])
    
    cursor.commit()
    yield cursor
    cursor.close()

def test_query_1(test_db):
    """
    Test query for finding the book that remained in the top 3 the longest in 2022.
    """
    cursor = test_db.cursor()
    cursor.execute(QUERY_1)
    results = cursor.fetchall()
    assert len(results) == 1
    assert results[0][0] == 'Book C'  # Expected title
    assert results[0][1] == 1         # Expected days in top 3

def test_query_2(test_db):
    """
    Test query for finding the top 3 lists with the least number of unique books.
    """
    cursor = test_db.cursor()
    cursor.execute(QUERY_2)
    results = cursor.fetchall()
    assert len(results) == 2
    assert results[0][0] == 'list_0'  # Expected list name
    assert results[0][1] == 1         # Expected unique books

def test_query_3(test_db):
    """
    Test query for finding publisher rankings based on points.
    """
    cursor = test_db.cursor()
    cursor.execute(QUERY_3)
    results = cursor.fetchall()
    assert len(results) == 3  # Three publishers in the test data
    assert results[0][0] == 'Publisher C'
    assert results[0][4] == 1  # Rank 1 for Publisher C

def test_query_4(test_db):
    """
    Test query for Jake's and Pete's book purchases.
    """
    cursor = test_db.cursor()
    cursor.execute(QUERY_4)
    results = cursor.fetchall()
    assert len(results) == 2  # Two books in the test data
    assert results[0][1] == "Jake's team"
    assert results[1][1] == "Pete's team"