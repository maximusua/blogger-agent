from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
import requests
import logging

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Клас для параметрів інструменту пошуку
class TravelSearchSchema(BaseModel):
    location: str = Field(description="Назва туристичного напрямку для пошуку")

# Інструмент для пошуку локацій
class ContentGeoSearchTool(BaseTool):
    name = "contentgeo_search"
    description = "Шукає інформацію про туристичні напрямки на ContentGeo"
    args_schema = TravelSearchSchema
    
    def __init__(self, mcp_server_url: str = "http://localhost:8001"):
        super().__init__()
        self.client = ContentGeoClient(mcp_server_url=mcp_server_url)
    
    def _run(self, location: str) -> Dict[str, Any]:
        """Запуск інструменту пошуку."""
        try:
            # Використовуємо landmarks для пошуку місць
            result = self.client.get_landmarks(lat=50.4113658, lon=30.5113545)
            features = result.get("features", [])
            
            if not features:
                return {"error": f"Не знайдено інформації про {location}"}
            
            # Знаходимо найбільш підходяще місце
            location_data = features[0]
            location_id = location_data.get("id")
            
            if not location_id:
                return {"error": f"Не знайдено location_id для {location}"}
            
            # Отримуємо детальну інформацію
            details = self.client.get_landmark_info(location_id)
            return {
                "location_id": location_id,
                "details": details,
                "name": location_data.get("properties", {}).get("Name", ""),
                "location_string": location_data.get("properties", {}).get("Address", "")
            }
        except Exception as e:
            logger.error(f"Помилка при пошуку локації: {str(e)}")
            return {"error": str(e)}

# Клас для параметрів інструменту отримання готелів
class HotelsSchema(BaseModel):
    lat: float = Field(description="Широта")
    lon: float = Field(description="Довгота")

# Інструмент для отримання готелів
class ContentGeoHotelsTool(BaseTool):
    name = "contentgeo_hotels"
    description = "Отримує список найкращих готелів для заданої локації на ContentGeo"
    args_schema = HotelsSchema
    
    def __init__(self, mcp_server_url: str = "http://localhost:8001"):
        super().__init__()
        self.client = ContentGeoClient(mcp_server_url=mcp_server_url)
    
    def _run(self, lat: float, lon: float) -> Dict[str, Any]:
        """Запуск інструменту для отримання готелів."""
        try:
            hotels = self.client.get_restaurants(lat=lat, lon=lon)
            return {
                "hotels": hotels[:10],  # Повертаємо 10 найкращих готелів
                "total": len(hotels)
            }
        except Exception as e:
            logger.error(f"Помилка при отриманні готелів: {str(e)}")
            return {"error": str(e)}

# Схема для інструменту отримання ресторанів
class RestaurantsSchema(BaseModel):
    lat: float = Field(description="Широта")
    lon: float = Field(description="Довгота")

# Інструмент для отримання ресторанів
class ContentGeoRestaurantsTool(BaseTool):
    name = "contentgeo_restaurants"
    description = "Отримує список найкращих ресторанів для заданої локації на ContentGeo"
    args_schema = RestaurantsSchema
    
    def __init__(self, mcp_server_url: str = "http://localhost:8001"):
        super().__init__()
        self.client = ContentGeoClient(mcp_server_url=mcp_server_url)
    
    def _run(self, lat: float, lon: float) -> Dict[str, Any]:
        """Запуск інструменту для отримання ресторанів."""
        try:
            restaurants = self.client.get_restaurants(lat=lat, lon=lon)
            return {
                "restaurants": restaurants[:10],  # Повертаємо 10 найкращих ресторанів
                "total": len(restaurants)
            }
        except Exception as e:
            logger.error(f"Помилка при отриманні ресторанів: {str(e)}")
            return {"error": str(e)}

# Схема для інструменту отримання визначних місць
class AttractionsSchema(BaseModel):
    lat: float = Field(description="Широта")
    lon: float = Field(description="Довгота")

# Інструмент для отримання визначних місць
class ContentGeoAttractionsTool(BaseTool):
    name = "contentgeo_attractions"
    description = "Отримує список найкращих визначних місць для заданої локації на ContentGeo"
    args_schema = AttractionsSchema
    
    def __init__(self, mcp_server_url: str = "http://localhost:8001"):
        super().__init__()
        self.client = ContentGeoClient(mcp_server_url=mcp_server_url)
    
    def _run(self, lat: float, lon: float) -> Dict[str, Any]:
        """Запуск інструменту для отримання визначних місць."""
        try:
            attractions = self.client.get_geo_objects(lat=lat, lon=lon)
            return {
                "attractions": attractions[:10],  # Повертаємо 10 найкращих атракцій
                "total": len(attractions)
            }
        except Exception as e:
            logger.error(f"Помилка при отриманні атракцій: {str(e)}")
            return {"error": str(e)}

# Схема для інструменту отримання відгуків
class ReviewsSchema(BaseModel):
    ids: str = Field(description="ID об'єкту для отримання відгуків")

# Інструмент для отримання відгуків
class ContentGeoReviewsTool(BaseTool):
    name = "contentgeo_reviews"
    description = "Отримує відгуки для заданого об'єкту на ContentGeo"
    args_schema = ReviewsSchema
    
    def __init__(self, mcp_server_url: str = "http://localhost:8001"):
        super().__init__()
        self.client = ContentGeoClient(mcp_server_url=mcp_server_url)
    
    def _run(self, ids: str) -> Dict[str, Any]:
        """Запуск інструменту для отримання відгуків."""
        try:
            info = self.client.get_geo_object_info(ids=ids)
            return {
                "info": info,
                "reviews": info.get("reviews", [])[:5]  # Повертаємо 5 найкращих відгуків
            }
        except Exception as e:
            logger.error(f"Помилка при отриманні відгуків: {str(e)}")
            return {"error": str(e)}

class ContentGeoClient:
    def __init__(self, mcp_server_url: str = "http://localhost:8001"):
        """
        Ініціалізація клієнта для роботи з ContentGeo MCP сервером.
        
        Args:
            mcp_server_url: URL MCP сервера
        """
        self.mcp_server_url = mcp_server_url
        logger.info(f"Ініціалізовано клієнт з MCP сервером: {mcp_server_url}")

    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """
        Виконання запиту до MCP сервера.
        
        Args:
            endpoint: Назва ендпоінту
            params: Параметри запиту
            
        Returns:
            Відповідь від сервера у форматі JSON
        """
        try:
            url = f"{self.mcp_server_url}/{endpoint}"
            logger.info(f"Запит до {url} з параметрами: {params}")
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Помилка при виконанні запиту до {endpoint}: {str(e)}")
            return {"error": str(e)}

    def get_landmarks(self, lat: float, lon: float) -> Dict:
        """
        Отримання списку визначних місць.
        
        Args:
            lat: Широта
            lon: Довгота
            
        Returns:
            Список визначних місць
        """
        return self._make_request("landmarks", {"lat": lat, "lon": lon})

    def get_landmark_info(self, ids: str) -> Dict:
        """
        Отримання інформації про визначне місце.
        
        Args:
            ids: ID визначного місця
            
        Returns:
            Інформація про визначне місце
        """
        return self._make_request("landmarkinfo", {"ids": ids})

    def get_restaurants(self, lat: float, lon: float) -> List[Dict]:
        """
        Отримання списку ресторанів.
        
        Args:
            lat: Широта
            lon: Довгота
            
        Returns:
            Список ресторанів
        """
        result = self._make_request("restaurants", {"lat": lat, "lon": lon})
        return result.get("features", [])

    def get_restaurant_info(self, ids: str) -> Dict:
        """
        Отримання інформації про ресторан.
        
        Args:
            ids: ID ресторану
            
        Returns:
            Інформація про ресторан
        """
        return self._make_request("restaurantinfo", {"ids": ids})

    def get_geo_objects(self, lat: float, lon: float, distance: Optional[float] = None) -> List[Dict]:
        """
        Отримання геооб'єктів.
        
        Args:
            lat: Широта
            lon: Довгота
            distance: Відстань у кілометрах (опціонально)
            
        Returns:
            Список геооб'єктів
        """
        params = {"lat": lat, "lon": lon}
        if distance:
            params["distance"] = distance
        result = self._make_request("geo_objects", params)
        return result.get("features", [])

    def get_geo_object_info(self, ids: str) -> Dict:
        """
        Отримання інформації про геооб'єкт.
        
        Args:
            ids: ID геооб'єкту
            
        Returns:
            Інформація про геооб'єкт
        """
        return self._make_request("geo_object_info", {"ids": ids}) 