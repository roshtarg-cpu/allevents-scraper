"""
AllEvents.in Event Scraper
Scrapes events from AllEvents.in by city
"""
import asyncio
import os
from urllib.parse import urljoin
from apify import Actor
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup


async def main():
    async with Actor:
        Actor.log.info("AllEvents Scraper starting...")
        
        # Get input
        actor_input = await Actor.get_input() or {}
        city = actor_input.get('city', 'washington')
        category = actor_input.get('category', '')
        max_results = actor_input.get('maxResults', 50)
        use_proxy = actor_input.get('useProxy', False)
        
        Actor.log.info(f"Scraping {city}, category: {category or 'all'}, max: {max_results}")
        
        # Build URL
        if category:
            url = f"https://allevents.in/{city}/{category}"
        else:
            url = f"https://allevents.in/{city}"
        
        Actor.log.info(f"Target URL: {url}")
        
        # Setup proxy if needed
        proxy_config = None
        if use_proxy:
            proxy_password = os.getenv('APIFY_PROXY_PASSWORD')
            if proxy_password:
                proxy_config = {
                    "server": "http://proxy.apify.com:8000",
                    "username": "auto",
                    "password": proxy_password
                }
                Actor.log.info("Using Apify proxy")
        
        # Launch browser
        async with async_playwright() as p:
            launch_options = {
                'headless': True,
                'args': [
                    '--disable-blink-features=AutomationControlled',
                    '--disable-web-security'
                ]
            }
            
            context_options = {
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                'viewport': {'width': 1920, 'height': 1080}
            }
            
            if proxy_config:
                context_options['proxy'] = proxy_config
            
            browser = await p.chromium.launch(**launch_options)
            context = await browser.new_context(**context_options)
            
            # Add stealth scripts
            await context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {get: () => false});
                Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3]});
            """)
            
            page = await context.new_page()
            
            try:
                # Navigate to page
                Actor.log.info(f"Loading {url}")
                await page.goto(url, wait_until='networkidle', timeout=60000)
                await page.wait_for_timeout(3000)
                
                # Get page content
                content = await page.content()
                soup = BeautifulSoup(content, 'html.parser')
                
                # Extract events
                events = []
                
                # Find event containers - try multiple selectors
                containers = []
                
                # Strategy 1: Look for event cards with data attributes
                containers = soup.find_all(attrs={'data-event-id': True})
                if not containers:
                    # Strategy 2: Look for article tags
                    containers = soup.find_all('article')
                if not containers:
                    # Strategy 3: Look for divs with 'event' in class
                    containers = soup.find_all('div', class_=lambda x: x and 'event' in x.lower())
                if not containers:
                    # Strategy 4: Look for any clickable cards
                    containers = soup.find_all('a', href=lambda x: x and '/event/' in x if x else False)
                
                Actor.log.info(f"Found {len(containers)} potential event containers")
                
                for container in containers[:max_results]:
                    try:
                        event_data = {}
                        
                        # Extract title
                        title_elem = container.find(['h1', 'h2', 'h3', 'h4'])
                        if title_elem:
                            event_data['title'] = title_elem.get_text(strip=True)
                        
                        # Extract URL
                        link = container.find('a', href=True)
                        if link:
                            href = link['href']
                            event_data['url'] = urljoin(url, href)
                        elif container.name == 'a' and container.get('href'):
                            event_data['url'] = urljoin(url, container['href'])
                        
                        # Extract date/time - look for time tags or date classes
                        date_elem = container.find('time') or container.find(class_=lambda x: x and 'date' in x.lower() if x else False)
                        if date_elem:
                            event_data['date'] = date_elem.get_text(strip=True)
                        
                        # Extract location
                        location_elem = container.find(class_=lambda x: x and ('location' in x.lower() or 'venue' in x.lower()) if x else False)
                        if location_elem:
                            event_data['location'] = location_elem.get_text(strip=True)
                        
                        # Extract price
                        price_elem = container.find(class_=lambda x: x and 'price' in x.lower() if x else False)
                        if price_elem:
                            event_data['price'] = price_elem.get_text(strip=True)
                        
                        # Extract category
                        category_elem = container.find(class_=lambda x: x and ('category' in x.lower() or 'tag' in x.lower()) if x else False)
                        if category_elem:
                            event_data['category'] = category_elem.get_text(strip=True)
                        
                        # Only save if we have at least title and URL
                        if event_data.get('title') and event_data.get('url'):
                            events.append(event_data)
                            Actor.log.info(f"Extracted: {event_data['title']}")
                    
                    except Exception as e:
                        Actor.log.warning(f"Error extracting event: {e}")
                        continue
                
                Actor.log.info(f"Extracted {len(events)} events")
                
                # Save data
                for event in events:
                    await Actor.push_data(event)
                
                Actor.log.info("✅ Scraping completed successfully")
            
            except Exception as e:
                Actor.log.error(f"Error during scraping: {e}")
                raise
            
            finally:
                await browser.close()


if __name__ == '__main__':
    asyncio.run(main())
