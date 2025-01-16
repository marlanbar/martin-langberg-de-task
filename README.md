# NYT Bestseller Analysis

This project analyzes New York Times bestseller lists data from 2021 to 2023, providing insights into book rankings, publisher performance, and list characteristics.

## Project Structure

```
martin-langberg-de-task/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── README.md
├── config/
│   └── .env.dev
├── src/
│   ├── main.py
│   ├── data_retrieval.py
│   ├── database_setup.py
│   ├── dimensional_modeling.py
│   └── sql_queries.py
├── tests/
|   └── sample_data.json
|   └── test_ingestion.py
│   └── test_queries.py
├── data/
└── output/
```


## Setup and Installation

1. Clone the repository:

```
git clone https://github.com/marlanbar/martin-langberg-de-task.git
cd martin-langberg-de-task
```

2. Add your NYT API key to the config/.env.dev file:
```
NYT_API_KEY=your_api_key_here
```


3. Build and run the Docker container:

```
docker compose --env-file config/.env.dev up --build
```

## Usage

The application will automatically:

1. Retrieve data from the NYT Books API
2. Set up a SQLite database
3. Create a dimensional model of the data
4. Execute SQL queries to analyze the data
5. Export results as CSV files in the output/ directory

## SQL Queries

The project answers the following questions:

1. Identify the book that remained in the top 3 ranks for the longest time in 2022.
2. Determine the top 3 lists with the least number of unique books in their rankings.
3. Create a quarterly ranking of publishers from 2021 to 2023, based on their books' performance.
4. For 2023, determine which books were bought by Jake's team (reviewing books ranked first on every list) and Pete's team (reviewing books ranked third).

The results will be stored in the output/ folder.

## Testing

To run the tests:

```
docker compose run nyt-books-api pytest tests
```

## Dimensional Model

The project uses a star schema with the following tables:
- DimDate
- DimBook
- DimList
- BookRankings (Fact Table)

## Output

Results of the SQL queries are exported as CSV files in the output/ directory.

## Dependencies

- Python 3.9
- SQLite
- Requests
- Pandas
- Pytest

For a complete list of dependencies, see requirements.txt.

## License

This project is licensed under the MIT License.
