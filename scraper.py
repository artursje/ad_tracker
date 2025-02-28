import requests
from bs4 import BeautifulSoup
import random
import time
import logging
import traceback
from datetime import datetime

logger = logging.getLogger('ad_tracker')

def get_random_user_agent():
    """Return a random user agent string to avoid detection"""
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0'
    ]
    return random.choice(user_agents)

def scrape_with_delay(url, config=None):
    """Scrape with random delay and rotating user agents"""
    # Add random delay to avoid detection
    delay = 5  # default delay
    if config and 'scraping' in config and 'delay' in config['scraping']:
        delay = config['scraping']['delay']
        
    random_delay = delay + random.uniform(0, 2)
    logger.debug(f"Waiting {random_delay:.2f} seconds before request")
    time.sleep(random_delay)
    
    headers = {
        'User-Agent': get_random_user_agent(),
        'Accept-Language': 'en-US,en;q=0.9,lt;q=0.8',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Referer': 'https://www.google.com/',
        'DNT': '1',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logger.error(f"Request failed: {e}")
        return None

def scrape_autoplius(search_url, config=None):
    """Scrape car listings from Autoplius.lt"""
    try:
        logger.info(f"Scraping Autoplius: {search_url}")
        
        html_content = scrape_with_delay(search_url, config)
        if not html_content:
            return []
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find all ad containers (adjust selector based on actual site structure)
        ad_containers = soup.select('.announcement-item')
        
        if not ad_containers:
            logger.warning("No ad containers found on Autoplius. Site structure may have changed.")
            return []
        
        ads = []
        for container in ad_containers:
            try:
                # Extract details (adjust selectors based on actual HTML structure)
                title_elem = container.select_one('.announcement-title')
                price_elem = container.select_one('.price')
                link_elem = container.select_one('a.announcement-item-link')
                image_elem = container.select_one('img')
                
                # Get ad ID from the container's data attribute or URL
                ad_id = container.get('data-id', '')
                if not ad_id and link_elem and link_elem.get('href'):
                    ad_id = link_elem.get('href', '').split('/')[-1]
                
                if title_elem and price_elem and link_elem:
                    ad = {
                        'id': ad_id,
                        'title': title_elem.text.strip(),
                        'price': price_elem.text.strip(),
                        'link': 'https://autoplius.lt' + link_elem.get('href', '') if not link_elem.get('href', '').startswith('http') else link_elem.get('href', ''),
                        'image_url': image_elem.get('src', '') if image_elem else '',
                        'timestamp': datetime.now().isoformat() if 'datetime' in globals() else None
                    }
                    ads.append(ad)
            except Exception as e:
                logger.error(f"Error parsing Autoplius ad: {e}")
                logger.debug(traceback.format_exc())
        
        logger.info(f"Found {len(ads)} ads on Autoplius")
        return ads
        
    except Exception as e:
        logger.error(f"Error scraping Autoplius: {e}")
        logger.error(traceback.format_exc())
        return []

def scrape_skelbiu(search_url, config=None):
    """Scrape listings from Skelbiu.lt"""
    try:
        logger.info(f"Scraping Skelbiu: {search_url}")
        
        html_content = scrape_with_delay(search_url, config)
        if not html_content:
            return []
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find all ad containers (adjust selector based on actual site structure)
        ad_containers = soup.select('.standard-list-item')
        
        if not ad_containers:
            logger.warning("No ad containers found on Skelbiu. Site structure may have changed.")
            return []
        
        ads = []
        for container in ad_containers:
            try:
                # Extract details (adjust selectors based on actual HTML structure)
                title_elem = container.select_one('.item-title')
                price_elem = container.select_one('.item-price')
                link_elem = container.select_one('a.item-link')
                image_elem = container.select_one('.item-image img')
                
                # Get ad ID
                ad_id = container.get('data-item-id', '')
                if not ad_id and link_elem and link_elem.get('href'):
                    ad_id = link_elem.get('href', '').split('/')[-1].split('.')[0]
                
                if title_elem and link_elem:
                    ad = {
                        'id': ad_id,
                        'title': title_elem.text.strip(),
                        'price': price_elem.text.strip() if price_elem else 'N/A',
                        'link': 'https://www.skelbiu.lt' + link_elem.get('href', '') if not link_elem.get('href', '').startswith('http') else link_elem.get('href', ''),
                        'image_url': image_elem.get('src', '') if image_elem else '',
                        'timestamp': datetime.now().isoformat() if 'datetime' in globals() else None
                    }
                    ads.append(ad)
            except Exception as e:
                logger.error(f"Error parsing Skelbiu ad: {e}")
                logger.debug(traceback.format_exc())
        
        logger.info(f"Found {len(ads)} ads on Skelbiu")
        return ads
        
    except Exception as e:
        logger.error(f"Error scraping Skelbiu: {e}")
        logger.error(traceback.format_exc())
        return []

def scrape_aruodas(search_url, config=None):
    """Scrape listings from Aruodas.lt"""
    try:
        logger.info(f"Scraping Aruodas: {search_url}")
        
        html_content = scrape_with_delay(search_url, config)
        if not html_content:
            return []
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find all ad containers (adjust selector based on actual site structure)
        ad_containers = soup.select('.list-row')
        
        if not ad_containers:
            logger.warning("No ad containers found on Aruodas. Site structure may have changed.")
            return []
        
        ads = []
        for container in ad_containers:
            try:
                # Extract details (adjust selectors based on actual HTML structure)
                title_elem = container.select_one('.list-line-title')
                price_elem = container.select_one('.list-item-price')
                link_elem = container.select_one('a.item-link')
                image_elem = container.select_one('.list-photo img')
                
                # If link_elem is None, try to find any link in the container
                if not link_elem:
                    link_elem = container.select_one('a')
                
                # Get ad ID
                ad_id = container.get('data-id', '')
                if not ad_id and link_elem and link_elem.get('href'):
                    ad_id = link_elem.get('href', '').split('/')[-1].split('.')[0]
                
                if title_elem or link_elem:  # At least one must exist
                    ad = {
                        'id': ad_id,
                        'title': title_elem.text.strip() if title_elem else 'No title',
                        'price': price_elem.text.strip() if price_elem else 'N/A',
                        'link': 'https://www.aruodas.lt' + link_elem.get('href', '') if link_elem and not link_elem.get('href', '').startswith('http') else (link_elem.get('href', '') if link_elem else ''),
                        'image_url': image_elem.get('src', '') if image_elem else '',
                        'timestamp': datetime.now().isoformat() if 'datetime' in globals() else None
                    }
                    ads.append(ad)
            except Exception as e:
                logger.error(f"Error parsing Aruodas ad: {e}")
                logger.debug(traceback.format_exc())
        
        logger.info(f"Found {len(ads)} ads on Aruodas")
        return ads
        
    except Exception as e:
        logger.error(f"Error scraping Aruodas: {e}")
        logger.error(traceback.format_exc())
        return [] 