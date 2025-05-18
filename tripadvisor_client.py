from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from tripadvisor_client import TripAdvisorClient


# Клас для параметрів інструменту пошуку
class TravelSearchSchema(BaseModel):
    location: str = Field(description="Назва туристичного напрямку для пошуку")

# Інструмент для пошуку локацій
class TripAdvisorSearchTool(BaseTool):
    name = "tripadvisor_search"
    description = "Шукає інформацію про туристичні напрямки на TripAdvisor"
    args_schema = TravelSearchSchema
    
    def __init__(self, api_key: str, mcp_server_url: str = "http://localhost:8000"):
        super().__init__()
        self.client = TripAdvisorClient(api_key=api_key, mcp_server_url=mcp_server_url)
    
    def _run(self, location: str) -> Dict[str, Any]:
        """Запуск інструменту пошуку."""
        locations = self.client.search_locations(location)
        
        if not locations:
            return {"error": f"Не знайдено інформації про {location}"}
        
        location_data = locations[0]
        location_id = location_data.get("location_id")
        
        if not location_id:
            return {"error": f"Не знайдено location_id для {location}"}
        
        details = self.client.get_location_details(location_id)
        return {
            "location_id": location_id,
            "details": details,
            "name": location_data.get("name", ""),
            "location_string": location_data.get("location_string", "")
        }

# Клас для параметрів інструменту отримання готелів
class HotelsSchema(BaseModel):
    location_id: str = Field(description="Ідентифікатор локації на TripAdvisor")

# Інструмент для отримання готелів
class TripAdvisorHotelsTool(BaseTool):
    name = "tripadvisor_hotels"
    description = "Отримує список найкращих готелів для заданої локації на TripAdvisor"
    args_schema = HotelsSchema
    
    def __init__(self, api_key: str, mcp_server_url: str = "http://localhost:8000"):
        super().__init__()
        self.client = TripAdvisorClient(api_key=api_key, mcp_server_url=mcp_server_url)
    
    def _run(self, location_id: str) -> Dict[str, Any]:
        """Запуск інструменту для отримання готелів."""
        hotels = self.client.get_hotels(location_id)
        return {
            "hotels": hotels[:10],  # Повертаємо 10 найкращих готелів
            "total": len(hotels)
        }

# Схема для інструменту отримання ресторанів
class RestaurantsSchema(BaseModel):
    location_id: str = Field(description="Ідентифікатор локації на TripAdvisor")

# Інструмент для отримання ресторанів
class TripAdvisorRestaurantsTool(BaseTool):
    name = "tripadvisor_restaurants"
    description = "Отримує список найкращих ресторанів для заданої локації на TripAdvisor"
    args_schema = RestaurantsSchema
    
    def __init__(self, api_key: str, mcp_server_url: str = "http://localhost:8000"):
        super().__init__()
        self.client = TripAdvisorClient(api_key=api_key, mcp_server_url=mcp_server_url)
    
    def _run(self, location_id: str) -> Dict[str, Any]:
        """Запуск інструменту для отримання ресторанів."""
        restaurants = self.client.get_restaurants(location_id)
        return {
            "restaurants": restaurants[:10],  # Повертаємо 10 найкращих ресторанів
            "total": len(restaurants)
        }

# Схема для інструменту отримання визначних місць
class AttractionsSchema(BaseModel):
    location_id: str = Field(description="Ідентифікатор локації на TripAdvisor")

# Інструмент для отримання визначних місць
class TripAdvisorAttractionsTool(BaseTool):
    name = "tripadvisor_attractions"
    description = "Отримує список найкращих визначних місць для заданої локації на TripAdvisor"
    args_schema = AttractionsSchema
    
    def __init__(self, api_key: str, mcp_server_url: str = "http://localhost:8000"):
        super().__init__()
        self.client = TripAdvisorClient(api_key=api_key, mcp_server_url=mcp_server_url)
    
    def _run(self, location_id: str) -> Dict[str, Any]:
        """Запуск інструменту для отримання визначних місць."""
        attractions = self.client.get_attractions(location_id)
        return {
            "attractions": attractions[:10],  # Повертаємо 10 найкращих атракцій
            "total": len(attractions)
        }

# Схема для інструменту отримання відгуків
class ReviewsSchema(BaseModel):
    location_id: str = Field(description="Ідентифікатор локації на TripAdvisor")
    review_type: str = Field(description="Тип відгуків (hotel, restaurant, attraction)")

# Інструмент для отримання відгуків
class TripAdvisorReviewsTool(BaseTool):
    name = "tripadvisor_reviews"
    description = "Отримує відгуки для заданої локації на TripAdvisor"
    args_schema = ReviewsSchema
    
    def __init__(self, api_key: str, mcp_server_url: str = "http://localhost:8000"):
        super().__init__()
        self.client = TripAdvisorClient(api_key=api_key, mcp_server_url=mcp_server_url)
    
    def _run(self, location_id: str, review_type: str = "hotel") -> Dict[str, Any]:
        """Запуск інструменту для отримання відгуків."""
        if review_type not in ["hotel", "restaurant", "attraction"]:
            return {"error": f"Непідтримуваний тип відгуків: {review_type}"}
        
        reviews = self.client.get_reviews(location_id, review_type)
        return {
            "reviews": reviews[:5],  # Повертаємо 5 найкращих відгуків
            "total": len(reviews)
        }