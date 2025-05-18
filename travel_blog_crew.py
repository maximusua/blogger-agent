import os
from langchain.tools import BaseTool
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
import logging
from contentgeo_client import (
    ContentGeoSearchTool,
    ContentGeoHotelsTool,
    ContentGeoRestaurantsTool,
    ContentGeoAttractionsTool,
    ContentGeoReviewsTool
)

# Логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("travel_blog_crew")

# Завантаження змінних середовища
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set in environment variables!")

# Створення інструментів
search_tool = ContentGeoSearchTool()
hotels_tool = ContentGeoHotelsTool()
restaurants_tool = ContentGeoRestaurantsTool()
attractions_tool = ContentGeoAttractionsTool()
reviews_tool = ContentGeoReviewsTool()

# Створення агента-дослідника
researcher = Agent(
    role='Travel Researcher',
    goal='Find and summarize the most important travel information about the destination',
    backstory='Expert in travel research, always finds the best and most up-to-date information.',
    tools=[
        search_tool,
        hotels_tool,
        restaurants_tool,
        attractions_tool,
        reviews_tool
    ],
    verbose=True,
    llm_config={"api_key": OPENAI_API_KEY}
)

# Агент-письменник
writer = Agent(
    role='Travel Blogger',
    goal='Write an engaging and informative travel blog post based on the research',
    backstory='Professional travel blogger with a passion for storytelling.',
    verbose=True
)

# Агент-редактор
editor = Agent(
    role='Content Editor',
    goal='Edit and improve the travel blog post for clarity, style, and accuracy',
    backstory='Experienced editor specializing in travel content.',
    verbose=True
)

# Завдання
research_task = Task(
    description='Research the travel destination and gather important information:\n    1. Main attractions and landmarks\n    2. Local culture and traditions\n    3. Best places to stay\n    4. Local cuisine\n    5. Transportation options\n    6. Best time to visit\n    7. Tourist reviews of hotels, restaurants, and attractions',
    expected_output='A structured research report with all the requested information.',
    agent=researcher
)

writing_task = Task(
    description='Write an engaging travel blog based on the researched information:\n    1. Create an attractive title\n    2. Write an introduction that captures readers\' interest\n    3. Structure information in logical sections\n    4. Add personal observations and recommendations\n    5. Include real tourist reviews\n    6. End with an appealing conclusion',
    expected_output='A complete travel blog post in Markdown format.',
    agent=writer,
    depends_on=[research_task]
)

editing_task = Task(
    description='Edit and improve the blog:\n    1. Check grammar and punctuation\n    2. Improve structure and readability\n    3. Ensure information is accurate and up-to-date\n    4. Verify proper citation of reviews\n    5. Add recommendations for improvement',
    expected_output='A polished and publication-ready travel blog post.',
    agent=editor,
    depends_on=[writing_task]
)

# Crew
crew = Crew(
    agents=[researcher, writer, editor],
    tasks=[research_task, writing_task, editing_task],
    process=Process.sequential,
    verbose=True,
)

# Run crew
if __name__ == "__main__":
    result = crew.kickoff()
    print("\nCrew work result:")
    print(result) 