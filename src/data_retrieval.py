import requests
import json
from datetime import datetime, timedelta
import os
import time
import random

class NYTBooksAPI:
    def __init__(self):
        self.api_key = os.environ.get('NYT_API_KEY')
        self.base_url = "https://api.nytimes.com/svc/books/v3"
        self.session = requests.Session()

    def get_lists_overview(self, date):
        endpoint = f"{self.base_url}/lists/overview.json"
        params = {
            "api-key": self.api_key,
            "published_date": date
        }
        
        max_retries = 5
        for attempt in range(max_retries):
            try:
                response = self.session.get(endpoint, params=params)
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After', 60))
                    print(f"Rate limit hit. Waiting for {retry_after} seconds.")
                    time.sleep(retry_after)
                else:
                    print(f"Error fetching data for {date}: {response.status_code}")
                    return None
            except requests.exceptions.RequestException as e:
                print(f"Request failed: {e}")
            
            # Exponential backoff
            wait_time = (2 ** attempt) + random.random()
            print(f"Retrying in {wait_time:.2f} seconds...")
            time.sleep(wait_time)
        
        print(f"Failed to fetch data for {date} after {max_retries} attempts")
        return None

def fetch_and_store_data(start_date, end_date):
    api = NYTBooksAPI()
    current_date = start_date
    all_data = []

    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        print(f"Fetching data for {date_str}")
        data = api.get_lists_overview(date_str)
        if data:
            all_data.append(data)
        current_date += timedelta(days=7)  # NYT updates weekly
        time.sleep(12)  # Respect rate limit of 5 requests per minute

    # Store raw data
    if not os.path.exists('data'):
        os.makedirs('data')
    with open('data/nyt_bestsellers_raw.json', 'w') as f:
        json.dump(all_data, f)

    print("Data retrieval complete. Raw data stored in data/nyt_bestsellers_raw.json")

if __name__ == "__main__":
    start_date = datetime(2021, 1, 1)
    end_date = datetime(2023, 12, 31)
    fetch_and_store_data(start_date, end_date)
