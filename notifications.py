import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

logger = logging.getLogger('ad_tracker')

def send_email_notification(matching_ads, email_config):
    """Send email notification about new matching ads"""
    if not matching_ads:
        return
        
    sender_email = email_config['sender_email']
    receiver_email = email_config['receiver_email']
    password = email_config['password']
    smtp_server = email_config.get('smtp_server', 'smtp.gmail.com')
    smtp_port = email_config.get('smtp_port', 587)
    
    # Create message
    message = MIMEMultipart("alternative")
    message["Subject"] = f"New matching ads found: {len(matching_ads)}"
    message["From"] = sender_email
    message["To"] = receiver_email
    
    # Format HTML content
    html = f"""
    <html>
    <body>
        <h2>New matching ads found ({len(matching_ads)})</h2>
        <ul>
    """
    
    for ad in matching_ads:
        search_name = ad.get('search_name', 'Unnamed search')
        source = ad.get('source', 'Unknown source')
        
        html += f"""
        <li>
            <h3><a href="{ad['link']}">{ad['title']}</a></h3>
            <p>Price: {ad['price']}</p>
            <p>Source: {source} - {search_name}</p>
            {f'<img src="{ad["image_url"]}" style="max-width: 200px;">' if ad.get('image_url') else ''}
        </li>
        """
    
    html += """
        </ul>
    </body>
    </html>
    """
    
    # Attach HTML content
    part = MIMEText(html, "html")
    message.attach(part)
    
    try:
        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
            
        logger.info(f"Email notification sent for {len(matching_ads)} new matching ads")
    except Exception as e:
        logger.error(f"Failed to send email notification: {e}") 