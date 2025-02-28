import sqlite3
from datetime import datetime

def setup_database():
    """Set up SQLite database for storing ad information"""
    conn = sqlite3.connect('ad_tracker.db')
    cursor = conn.cursor()
    
    # Create tables if they don't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS seen_ads (
        id TEXT PRIMARY KEY,
        title TEXT,
        price TEXT,
        link TEXT,
        image_url TEXT,
        first_seen TEXT,
        source TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ad_id TEXT,
        sent_at TEXT,
        FOREIGN KEY (ad_id) REFERENCES seen_ads (id)
    )
    ''')
    
    conn.commit()
    return conn

def get_new_ads(ads, conn):
    """Filter out only new ads using SQLite database"""
    cursor = conn.cursor()
    new_ads = []
    
    for ad in ads:
        # Check if ad exists
        cursor.execute("SELECT id FROM seen_ads WHERE id = ?", (ad['id'],))
        result = cursor.fetchone()
        
        if not result:
            # This is a new ad
            new_ads.append(ad)
            
            # Store in database
            cursor.execute(
                "INSERT INTO seen_ads (id, title, price, link, image_url, first_seen, source) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (ad['id'], ad['title'], ad['price'], ad['link'], ad.get('image_url', ''), 
                 datetime.now().isoformat(), ad.get('source', 'unknown'))
            )
    
    conn.commit()
    return new_ads 