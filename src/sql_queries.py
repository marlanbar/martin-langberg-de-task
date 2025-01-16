import sqlite3
import csv
import os

# Define queries as constants
QUERY_1 = """
    SELECT b.title, COUNT(*) AS days_in_top_3
    FROM BookRankings br
        JOIN DimBook b ON br.book_key = b.book_key
        JOIN DimDate d ON br.date_key = d.date_key
    WHERE d.year = 2022 AND br.rank <= 3
    GROUP BY b.book_key
    ORDER BY days_in_top_3 DESC
    LIMIT 1;
"""

QUERY_2 = """
    SELECT l.list_name, COUNT(DISTINCT br.book_key) AS unique_books
    FROM BookRankings br
        JOIN DimList l ON br.list_key = l.list_key
    GROUP BY l.list_key
    ORDER BY unique_books ASC
    LIMIT 3;
"""

QUERY_3 = """
    WITH publisher_points AS (
        SELECT 
            b.publisher,
            d.year,
            d.quarter,
            SUM(CASE 
            WHEN br.rank = 1 THEN 5
            WHEN br.rank = 2 THEN 4
            WHEN br.rank = 3 THEN 3
            WHEN br.rank = 4 THEN 2
            WHEN br.rank = 5 THEN 1
            ELSE 0
            END) AS points,
            ROW_NUMBER() OVER (PARTITION BY d.year, d.quarter ORDER BY SUM(CASE 
            WHEN br.rank = 1 THEN 5
            WHEN br.rank = 2 THEN 4
            WHEN br.rank = 3 THEN 3
            WHEN br.rank = 4 THEN 2
            WHEN br.rank = 5 THEN 1
            ELSE 0
            END) DESC) AS rank
        FROM BookRankings br
            JOIN DimBook b ON br.book_key = b.book_key
            JOIN DimDate d ON br.date_key = d.date_key
        WHERE d.year BETWEEN 2021 AND 2023
        GROUP BY b.publisher, d.year, d.quarter
            )
    SELECT publisher, year, quarter, points, rank
    FROM publisher_points
    WHERE rank <= 5
    ORDER BY year, quarter, rank;

"""

QUERY_4 = """
    WITH jake_books AS (
        SELECT DISTINCT b.title AS jake_book
        FROM BookRankings br
            JOIN DimBook b ON br.book_key = b.book_key
            JOIN DimDate d ON br.date_key = d.date_key
        WHERE d.year = 2023 AND br.rank = 1
        ),
        pete_books AS (
        SELECT DISTINCT b.title AS pete_book
        FROM BookRankings br
            JOIN DimBook b ON br.book_key = b.book_key
            JOIN DimDate d ON br.date_key = d.date_key
        WHERE d.year = 2023 AND br.rank = 3
        )
    SELECT 
    COALESCE(j.jake_book, p.pete_book) AS book_title,
    CASE 
        WHEN j.jake_book IS NOT NULL AND p.pete_book IS NULL THEN 'Jake''s team'
        WHEN j.jake_book IS NULL AND p.pete_book IS NOT NULL THEN 'Pete''s team'
        ELSE 'Shared'
    END AS bought_by
    FROM jake_books j
        FULL OUTER JOIN pete_books p ON j.jake_book = p.pete_book
    ORDER BY bought_by, book_title;
"""

def execute_query(query, database_path):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

def export_to_csv(results, filename):
    output_dir = 'output'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    filepath = os.path.join(output_dir, filename)
    with open(filepath, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(results)

def run_queries(database_path):
    queries = [
        (QUERY_1, "query1_result.csv"),
        (QUERY_2, "query2_result.csv"),
        (QUERY_3, "query3_result.csv"),
        (QUERY_4, "query4_result.csv")
    ]
    
    for query, filename in queries:
        results = execute_query(query, database_path)
        export_to_csv(results, filename)

if __name__ == "__main__":
    database_path = os.environ.get('DATABASE_PATH', 'nyt_bestsellers.db')
    run_queries(database_path)
