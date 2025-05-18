from travel_blog_crew import crew
import logging

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting blog creation about Kyiv...")
    result = crew.kickoff()
    logger.info("\nCrew work result:")
    logger.info(result)
    
    # Save result to file
    try:
        with open("kyiv_blog.md", "w", encoding="utf-8") as f:
            f.write(str(result))
        logger.info("\nBlog successfully created and saved to 'kyiv_blog.md'")
    except Exception as e:
        logger.error(f"Error saving blog to file: {str(e)}")

if __name__ == "__main__":
    main() 