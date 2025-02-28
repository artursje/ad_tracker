import schedule
import time
from datetime import datetime
import sys
import traceback

from config import load_config
from database import setup_database, get_new_ads
from scraper import scrape_autoplius, scrape_skelbiu, scrape_aruodas
from notifications import send_email_notification
from utils import setup_logging

logger = setup_logging()

def match_criteria(ad, criteria):
    """Check if ad matches our criteria"""
    # Basic matching logic - expand as needed
    if 'max_price' in criteria:
        try:
            # Extract numbers from price string
            price_text = ''.join(filter(str.isdigit, ad['price']))
            if price_text:
                price = int(price_text)
                if price > criteria['max_price']:
                    return False
        except (ValueError, TypeError) as e:
            logger.warning(f"Error parsing price for ad {ad['id']}: {e}")
        
    if 'min_price' in criteria:
        try:
            price_text = ''.join(filter(str.isdigit, ad['price']))
            if price_text:
                price = int(price_text)
                if price < criteria['min_price']:
                    return False
        except (ValueError, TypeError) as e:
            logger.warning(f"Error parsing price for ad {ad['id']}: {e}")
            
    if 'keywords' in criteria and criteria['keywords']:
        title_lower = ad['title'].lower()
        if not any(keyword.lower() in title_lower for keyword in criteria['keywords']):
            return False
            
    return True

def process_source(source_name, source_config, db_conn):
    if not source_config.get('enabled', True):
        logger.info(f"Skipping disabled source: {source_name}")
        return []
    
    all_matching_ads = []
    
    for search in source_config.get('urls', []):
        search_name = search.get('name', 'Unnamed search')
        search_url = search.get('url')
        criteria = search.get('criteria', {})
        
        if not search_url:
            logger.warning(f"Missing URL for search {search_name}")
            continue
            
        logger.info(f"Processing {source_name} search: {search_name}")
        
        # Choose the appropriate scraper based on source
        if source_name == 'autoplius':
            ads = scrape_autoplius(search_url)
        elif source_name == 'skelbiu':
            ads = scrape_skelbiu(search_url)
        elif source_name == 'aruodas':
            ads = scrape_aruodas(search_url)
        else:
            logger.warning(f"Unknown source: {source_name}")
            continue
            
        # Tag ads with source
        for ad in ads:
            ad['source'] = source_name
            ad['search_name'] = search_name
            
        logger.info(f"Found {len(ads)} total ads")
        
        # Get new ads
        new_ads = get_new_ads(ads, db_conn)
        logger.info(f"Found {len(new_ads)} new ads")
        
        # Match criteria
        matching_ads = [ad for ad in new_ads if match_criteria(ad, criteria)]
        logger.info(f"Found {len(matching_ads)} matching ads")
        
        all_matching_ads.extend(matching_ads)
    
    return all_matching_ads

def run_tracker():
    try:
        # Load configuration
        config = load_config()
        
        # Setup database connection
        db_conn = setup_database()
        
        all_matching_ads = []
        
        # Process each source
        for source_name, source_config in config.get('sources', {}).items():
            matching_ads = process_source(source_name, source_config, db_conn)
            all_matching_ads.extend(matching_ads)
        
        # Send notifications if needed
        if all_matching_ads and config.get('email', {}).get('enabled', True):
            send_email_notification(all_matching_ads, config['email'])
        
        db_conn.close()
        logger.info(f"Completed tracking run at {datetime.now().isoformat()}")
        
    except Exception as e:
        logger.error(f"Error in tracker run: {e}")
        logger.error(traceback.format_exc())

def main():
    logger.info("Starting Ad Tracker")
    
    # Run once immediately
    run_tracker()
    
    # Load schedule configuration
    config = load_config()
    interval_hours = config.get('schedule', {}).get('interval_hours', 1)
    
    # Schedule to run periodically
    logger.info(f"Setting up schedule to run every {interval_hours} hours")
    schedule.every(interval_hours).hours.do(run_tracker)
    
    # Keep the script running
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("Stopping Ad Tracker")
        sys.exit(0)

if __name__ == "__main__":
    main() 