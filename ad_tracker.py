import logging
from logging.handlers import RotatingFileHandler
import traceback

# Set up logging
def setup_logging():
    logger = logging.getLogger('ad_tracker')
    logger.setLevel(logging.INFO)
    
    # Create rotating file handler (10MB max size, keep 5 backup files)
    handler = RotatingFileHandler('ad_tracker.log', maxBytes=10*1024*1024, backupCount=5)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    # Add console handler too
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logging()

# Then modify the scrape function to use logging
def scrape_autoplius(search_url):
    """Scrape car listings from Autoplius.lt"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        logger.info(f"Scraping Autoplius: {search_url}")
        response = requests.get(search_url, headers=headers)
        
        if response.status_code != 200:
            logger.error(f"Failed to fetch data: {response.status_code}")
            return []
        
        # ... rest of the function as before ...
        
    except Exception as e:
        logger.error(f"Error scraping Autoplius: {e}")
        logger.error(traceback.format_exc())
        return [] 