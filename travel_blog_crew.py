from crewai import Agent, Task, Crew, Process
from crewai.tools import BaseTool
import os
from dotenv import load_dotenv
from tripadvisor_client import TripAdvisorClient
from typing import Optional, Type, Any, Dict, List, Callable
from pydantic import BaseModel, Field
import logging
import json

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get API keys from environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
TRIPADVISOR_API_KEY = os.getenv('TRIPADVISOR_API_KEY')

if not OPENAI_API_KEY or not TRIPADVISOR_API_KEY:
    raise ValueError("Missing required API keys in .env file")

# Initialize TripAdvisor client
tripadvisor = TripAdvisorClient(TRIPADVISOR_API_KEY)

class SearchTravelInfoInput(BaseModel):
    query: str = Field(description="The search query for travel information")
    description: Optional[str] = Field(None, description="Alternative description of what to search for")

class SearchTravelInfoTool(BaseTool):
    name: str = "search_travel_info"
    description: str = "Search for travel information and places"
    args_schema: Type[BaseModel] = SearchTravelInfoInput
    
    def _run(self, query: str = None, description: str = None) -> str:
        try:
            # Use description if query is not provided
            search_query = query if query else description
            if not search_query:
                return "No search query provided"
            
            logger.info(f"Searching for location: {search_query}")
            
            # Search locations
            locations = tripadvisor.search_locations(search_query)
            logger.info(f"Raw locations response: {json.dumps(locations, indent=2)}")
            
            if not locations or not isinstance(locations, list):
                return f"No information found for {search_query}"
            
            logger.info(f"Found {len(locations)} locations")
            
            # Перевіряємо, чи знайдена локація відповідає запиту
            location_id = None
            location_name = None
            
            for loc in locations:
                if not isinstance(loc, dict):
                    continue
                    
                loc_name = loc.get('name', '')
                logger.info(f"Checking location: {loc_name}")
                
                if search_query.lower() in loc_name.lower():
                    location_id = loc.get('location_id')
                    location_name = loc_name
                    logger.info(f"Found matching location: {location_name}")
                    break
            
            if not location_id:
                if locations and isinstance(locations[0], dict):
                    location_id = locations[0].get('location_id')
                    location_name = locations[0].get('name', 'Unknown')
                    logger.warning(f"Using first found location instead of exact match: {location_name}")
                else:
                    return f"Could not find valid location information for {search_query}"
            
            # Get location details
            logger.info(f"Getting details for location ID: {location_id}")
            details = tripadvisor.get_location_details(location_id)
            logger.info(f"Location details received: {bool(details)}")
            
            if not details or not isinstance(details, dict):
                return f"Could not get details for {location_name}"
            
            # Get hotels
            logger.info("Getting hotels information")
            hotels = tripadvisor.get_hotels(location_id)
            if not isinstance(hotels, list):
                hotels = []
            logger.info(f"Found {len(hotels)} hotels")
            
            # Get restaurants
            logger.info("Getting restaurants information")
            restaurants = tripadvisor.get_restaurants(location_id)
            if not isinstance(restaurants, list):
                restaurants = []
            logger.info(f"Found {len(restaurants)} restaurants")
            
            # Get attractions
            logger.info("Getting attractions information")
            attractions = tripadvisor.get_attractions(location_id)
            if not isinstance(attractions, list):
                attractions = []
            logger.info(f"Found {len(attractions)} attractions")
            
            # Format response
            response = f"""
            Information about {location_name}:
            
            Main Information:
            {details.get('description', 'No description available')}
            
            Top Hotels:
            {', '.join([hotel.get('name', 'Unknown') for hotel in hotels[:3]]) if hotels else 'No hotels found'}
            
            Top Restaurants:
            {', '.join([restaurant.get('name', 'Unknown') for restaurant in restaurants[:3]]) if restaurants else 'No restaurants found'}
            
            Attractions:
            {', '.join([attraction.get('name', 'Unknown') for attraction in attractions[:3]]) if attractions else 'No attractions found'}
            """
            
            return response
        except Exception as e:
            logger.error(f"Error in SearchTravelInfoTool: {str(e)}")
            return f"Error while searching for information: {str(e)}"

class GetReviewsInput(BaseModel):
    location_id: str = Field(description="The location ID to get reviews for")

class GetHotelReviewsTool(BaseTool):
    name: str = "get_hotel_reviews"
    description: str = "Get hotel reviews"
    args_schema: Type[BaseModel] = GetReviewsInput
    
    def _run(self, location_id: str) -> str:
        try:
            reviews = tripadvisor.get_reviews(location_id, "hotel")
            return "\n".join([f"- {review['title']}: {review['text'][:200]}..." for review in reviews])
        except Exception as e:
            return f"Error while getting reviews: {str(e)}"

class GetRestaurantReviewsTool(BaseTool):
    name: str = "get_restaurant_reviews"
    description: str = "Get restaurant reviews"
    args_schema: Type[BaseModel] = GetReviewsInput
    
    def _run(self, location_id: str) -> str:
        try:
            reviews = tripadvisor.get_reviews(location_id, "restaurant")
            return "\n".join([f"- {review['title']}: {review['text'][:200]}..." for review in reviews])
        except Exception as e:
            return f"Error while getting reviews: {str(e)}"

class GetAttractionReviewsTool(BaseTool):
    name: str = "get_attraction_reviews"
    description: str = "Get attraction reviews"
    args_schema: Type[BaseModel] = GetReviewsInput
    
    def _run(self, location_id: str) -> str:
        try:
            reviews = tripadvisor.get_reviews(location_id, "attraction")
            return "\n".join([f"- {review['title']}: {review['text'][:200]}..." for review in reviews])
        except Exception as e:
            return f"Error while getting reviews: {str(e)}"

# Create tools
tools = [
    SearchTravelInfoTool(),
    GetHotelReviewsTool(),
    GetRestaurantReviewsTool(),
    GetAttractionReviewsTool()
]

# Create agents with tools
researcher = Agent(
    role='Travel Researcher',
    goal='Gather detailed and accurate information about travel destinations',
    backstory="""You are a travel expert with extensive experience in researching different countries and cultures.
    You know how to find the most interesting places and events. Your expertise helps create comprehensive travel guides.""",
    tools=tools,
    verbose=True
)

writer = Agent(
    role='Travel Blogger',
    goal='Create engaging and informative travel blogs',
    backstory="""You are a professional blogger with years of experience writing travel articles.
    You know how to make content interesting and useful for readers. Your writing style is engaging and personal.""",
    verbose=True
)

editor = Agent(
    role='Content Editor',
    goal='Review and improve content quality',
    backstory="""You are an experienced editor specializing in travel content.
    You help make text clearer and more appealing. Your attention to detail ensures high-quality content.""",
    verbose=True
)

# Create tasks
research_task = Task(
    description="""Research the travel destination and gather important information:
    1. Main attractions and landmarks
    2. Local culture and traditions
    3. Best places to stay
    4. Local cuisine
    5. Transportation options
    6. Best time to visit
    7. Tourist reviews of hotels, restaurants, and attractions""",
    agent=researcher,
    expected_output="""A comprehensive research report containing:
    1. Detailed information about main attractions and landmarks
    2. Insights about local culture and traditions
    3. List of recommended accommodations
    4. Overview of local cuisine and food options
    5. Transportation information and tips
    6. Best time to visit recommendations
    7. Curated selection of tourist reviews"""
)

writing_task = Task(
    description="""Write an engaging travel blog based on the researched information:
    1. Create an attractive title
    2. Write an introduction that captures readers' interest
    3. Structure information in logical sections
    4. Add personal observations and recommendations
    5. Include real tourist reviews
    6. End with an appealing conclusion""",
    agent=writer,
    expected_output="""A well-structured travel blog post that includes:
    1. An engaging title
    2. Captivating introduction
    3. Well-organized sections with detailed information
    4. Personal insights and recommendations
    5. Relevant tourist reviews
    6. Strong conclusion"""
)

editing_task = Task(
    description="""Edit and improve the blog:
    1. Check grammar and punctuation
    2. Improve structure and readability
    3. Ensure information is accurate and up-to-date
    4. Verify proper citation of reviews
    5. Add recommendations for improvement""",
    agent=editor,
    expected_output="""A polished and professional blog post that is:
    1. Grammatically correct
    2. Well-structured and easy to read
    3. Factually accurate
    4. Properly cited
    5. Enhanced with editorial recommendations"""
)

# Create crew
crew = Crew(
    agents=[researcher, writer, editor],
    tasks=[research_task, writing_task, editing_task],
    verbose=True,
    process=Process.sequential
)

# Run crew
if __name__ == "__main__":
    result = crew.kickoff()
    print("\nCrew work result:")
    print(result) 