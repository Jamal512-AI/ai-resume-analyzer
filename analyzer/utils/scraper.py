"""
LinkedIn job scraper using Selenium.
Optimized for global job searching and robust element detection.
"""
import time
import numpy as np
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException


def webdriver_setup():
    """Configure and return a headless Chrome WebDriver."""
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    # Add user agent to avoid detection
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    driver = webdriver.Chrome(options=options)
    return driver


def build_url(job_title_list, job_location):
    """Build a global LinkedIn search URL."""
    # Encode keywords
    keywords = '%20'.join([t.strip() for t in job_title_list])
    location = job_location.replace(' ', '%20')
    
    # Use global www subdomain instead of in.linkedin.com
    # Removed geoId to allow LinkedIn to resolve location naturally
    url = (
        f"https://www.linkedin.com/jobs/search?"
        f"keywords={keywords}&location={location}"
        f"&f_TPR=r604800&position=1&pageNum=0"
    )
    return url


def open_link(driver, link):
    """Open a LinkedIn URL with robust waiting."""
    try:
        driver.get(link)
        # Wait for either the job list or a known element
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_list_nodes((By.CSS_SELECTOR, 'li'))
        )
        time.sleep(2)
        return True
    except TimeoutException:
        # even if it times out, we might have some content
        return True
    except Exception:
        return False


def scroll_page(driver, link, job_count):
    """Open link and scroll to load more job listings."""
    if not open_link(driver, link):
        return

    # Scroll multiple times to trigger lazy loading
    for _ in range(max(1, job_count // 5)):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        
        # Try to click 'See more jobs' button if it appears
        try:
            see_more = driver.find_element(By.CSS_SELECTOR, "button[aria-label='See more jobs']")
            driver.execute_script("arguments[0].click();", see_more)
            time.sleep(2)
        except Exception:
            pass


def scrape_company_data(driver, job_title_input, job_location):
    """Scrape job cards with multiple fallback selectors."""
    
    # Try multiple common selectors for title, company, location
    title_selectors = ['h3.base-search-card__title', '.job-search-card__title', 'h3']
    company_selectors = ['h4.base-search-card__subtitle', '.job-search-card__subtitle', 'h4']
    location_selectors = ['span.job-search-card__location', '.job-search-card__location', 'span.job-result-card__location']
    
    titles = []
    companies = []
    locations = []
    urls = []

    # Get all job card elements first
    cards = driver.find_elements(By.CSS_SELECTOR, '.base-card, .job-search-card, li')
    
    for card in cards:
        try:
            # Find title
            title_text = ""
            for selector in title_selectors:
                elements = card.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    title_text = elements[0].text.strip()
                    break
            
            # Find company
            company_text = ""
            for selector in company_selectors:
                elements = card.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    company_text = elements[0].text.strip()
                    break

            # Find location
            location_text = ""
            for selector in location_selectors:
                elements = card.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    location_text = elements[0].text.strip()
                    break
            
            # Find Link
            link_el = card.find_elements(By.TAG_NAME, 'a')
            link = link_el[0].get_attribute('href') if link_el else ""

            if title_text and link and "/jobs/view/" in link:
                titles.append(title_text)
                companies.append(company_text or "Unknown Company")
                locations.append(location_text or job_location)
                urls.append(link)
        except Exception:
            continue

    df = pd.DataFrame({
        'company': companies,
        'title': titles,
        'location': locations,
        'url': urls,
    })

    # Deduplicate
    df = df.drop_duplicates(subset=['url']).reset_index(drop=True)
    return df


def scrape_job_descriptions(driver, df, job_count):
    """Scrape individual job descriptions."""
    results = []
    total_to_scrape = min(len(df), job_count * 2) # Scrape extra to ensure we meet count
    
    for i in range(total_to_scrape):
        row = df.iloc[i]
        try:
            driver.get(row['url'])
            time.sleep(2)
            
            # Try to click show more button
            try:
                show_more = driver.find_element(By.CSS_SELECTOR, 'button[data-tracking-control-name="public_jobs_show-more-html-btn"]')
                driver.execute_script("arguments[0].click();", show_more)
                time.sleep(1)
            except Exception:
                pass

            # Extract description
            desc_selectors = [
                'div.show-more-less-html__markup',
                '.description__text',
                '.job-description'
            ]
            description = "Description not available."
            for selector in desc_selectors:
                els = driver.find_elements(By.CSS_SELECTOR, selector)
                if els:
                    description = els[0].text.strip()
                    break
            
            results.append({
                'company': row['company'],
                'title': row['title'],
                'location': row['location'],
                'url': row['url'],
                'description': description[:1000] + "..." if len(description) > 1000 else description
            })
            
            if len(results) >= job_count:
                break
        except Exception:
            continue

    return results


def scrape_linkedin_jobs(job_titles, job_location, job_count):
    """Main entry point: scrape LinkedIn jobs globally."""
    driver = None
    try:
        driver = webdriver_setup()
        url = build_url(job_titles, job_location)
        scroll_page(driver, url, job_count)
        
        # Get raw data
        df = scrape_company_data(driver, job_titles, job_location)
        
        if df.empty:
            return []
            
        # Get detailed descriptions
        results = scrape_job_descriptions(driver, df, job_count)
        return results

    except Exception as e:
        return {'error': str(e)}

    finally:
        if driver:
            driver.quit()
