import requests
from typing import Dict, List, Optional
from datetime import datetime
import json

class TripAdvisorClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://tripadvisor-mcp.p.rapidapi.com"
        self.headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "tripadvisor-mcp.p.rapidapi.com"
        }

    def search_locations(self, query: str) -> List[Dict]:
        """Пошук локацій за запитом."""
        url = f"{self.base_url}/location/search"
        params = {
            "query": query,
            "limit": 5
        }
        response = requests.get(url, headers=self.headers, params=params)
        return response.json()

    def get_location_details(self, location_id: str) -> Dict:
        """Отримання детальної інформації про локацію."""
        url = f"{self.base_url}/location/details"
        params = {
            "location_id": location_id
        }
        response = requests.get(url, headers=self.headers, params=params)
        return response.json()

    def get_hotels(self, location_id: str) -> List[Dict]:
        """Отримання списку готелів у локації."""
        url = f"{self.base_url}/hotel/search"
        params = {
            "location_id": location_id,
            "limit": 10
        }
        response = requests.get(url, headers=self.headers, params=params)
        return response.json()

    def get_restaurants(self, location_id: str) -> List[Dict]:
        """Отримання списку ресторанів у локації."""
        url = f"{self.base_url}/restaurant/search"
        params = {
            "location_id": location_id,
            "limit": 10
        }
        response = requests.get(url, headers=self.headers, params=params)
        return response.json()

    def get_attractions(self, location_id: str) -> List[Dict]:
        """Отримання списку визначних місць у локації."""
        url = f"{self.base_url}/attraction/search"
        params = {
            "location_id": location_id,
            "limit": 10
        }
        response = requests.get(url, headers=self.headers, params=params)
        return response.json()

    def get_reviews(self, location_id: str, review_type: str = "hotel") -> List[Dict]:
        """Отримання відгуків про локацію."""
        url = f"{self.base_url}/review/search"
        params = {
            "location_id": location_id,
            "review_type": review_type,
            "limit": 5
        }
        response = requests.get(url, headers=self.headers, params=params)
        return response.json() 