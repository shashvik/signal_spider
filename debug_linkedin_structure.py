#!/usr/bin/env python3

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time

def debug_linkedin_structure():
    """Debug LinkedIn job page structure"""
    
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        
        print("Navigating to LinkedIn jobs page...")
        driver.get('https://www.linkedin.com/jobs/search/?keywords=security%20engineer')
        time.sleep(5)
        
        # Try different selectors
        selectors = [
            '.job-card-container',
            '.jobs-search-results__list-item',
            '[data-job-id]',
            '.job-card-list__item',
            '.jobs-search__results-list li'
        ]
        
        for selector in selectors:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            print(f"\nSelector '{selector}': Found {len(elements)} elements")
            
            if elements:
                print("First element HTML (first 500 chars):")
                html = elements[0].get_attribute('outerHTML')
                print(html[:500] + "..." if len(html) > 500 else html)
                break
        
        driver.quit()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_linkedin_structure()