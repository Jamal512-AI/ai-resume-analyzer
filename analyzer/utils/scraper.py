"""
LinkedIn job scraper using HTTP Requests and BeautifulSoup.
Fully optimized for Vercel's serverless environment (No Selenium/Chrome required).
"""
import time
import json
import urllib.parse
import urllib.request

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None


def scrape_linkedin_jobs(job_titles, job_location, job_count):
    """Main entry point: scrape LinkedIn jobs globally using HTTP requests."""
    
    if not BeautifulSoup:
        return {'error': 'BeautifulSoup is not installed. Vercel backend needs beautifulsoup4 and requests.'}

    import requests

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }

    try:
        keywords = urllib.parse.quote(' '.join(job_titles))
        location = urllib.parse.quote(job_location)

        # Base LinkedIn public jobs search URL
        url = f"https://www.linkedin.com/jobs/search?keywords={keywords}&location={location}&f_TPR=r604800&position=1&pageNum=0"
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        job_cards = soup.find_all('div', class_='base-search-card', limit=job_count)
        
        if not job_cards:
            job_cards = soup.find_all('li', limit=job_count) # Fallback

        results = []
        for card in job_cards:
            try:
                # Title
                title_elem = card.find(['h3', 'span'], class_=lambda x: x and 'title' in x.lower())
                title = title_elem.text.strip() if title_elem else "Unknown Title"

                # Company
                comp_elem = card.find(['h4', 'a'], class_=lambda x: x and 'subtitle' in x.lower())
                company = comp_elem.text.strip() if comp_elem else "Unknown Company"

                # Location
                loc_elem = card.find('span', class_=lambda x: x and 'location' in x.lower())
                loc = loc_elem.text.strip() if loc_elem else job_location

                # URL
                link_elem = card.find('a', href=True)
                job_url = link_elem['href'].split('?')[0] if link_elem else ""

                if not job_url:
                    continue

                results.append({
                    'title': title,
                    'company': company,
                    'location': loc,
                    'url': job_url,
                    'description': f"Apply for {title} directly using the link below! Detailed descriptions require an active LinkedIn session."
                })
                
                if len(results) >= job_count:
                    break
                    
            except Exception:
                continue

        return results

    except Exception as e:
        return {'error': f'Failed to scrape LinkedIn: {str(e)}'}
