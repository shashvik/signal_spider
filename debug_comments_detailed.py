#!/usr/bin/env python3
"""
Detailed LinkedIn Comments Debug Script
Analyzes different URLs and approaches to find comment elements
"""

import time
import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Add the linkedin_scraper directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'linkedin_scraper'))

from linkedin_scraper import actions

def setup_driver():
    """Setup Chrome driver with stealth options"""
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def test_url_and_selectors(driver, url, url_name):
    """Test a specific URL with various selectors"""
    print(f"\n{'='*60}")
    print(f"TESTING: {url_name}")
    print(f"URL: {url}")
    print(f"{'='*60}")
    
    driver.get(url)
    time.sleep(5)
    
    # Scroll to load content
    print("\nScrolling to load content...")
    for i in range(5):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
    
    # Test various selectors
    selectors_to_test = [
        # Comment-specific selectors
        ".comments-comment-entity",
        "article.comments-comment-entity",
        ".comments-comment-item",
        "[data-id*='comment']",
        ".feed-shared-update-v2 .comments-comment-entity",
        ".comments-comments-list .comments-comment-entity",
        ".comments-comment-list__container .comments-comment-entity",
        # Activity selectors
        ".feed-shared-update-v2",
        ".activity-item",
        "[data-urn*='activity']",
        ".pvs-list__item",
        ".artdeco-card",
        # General content selectors
        "[data-urn]",
        ".scaffold-layout__main .artdeco-card",
        "main .pvs-list__item"
    ]
    
    found_elements = {}
    for selector in selectors_to_test:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            count = len(elements)
            found_elements[selector] = count
            if count > 0:
                print(f"✅ {selector}: {count} elements")
                # Get sample text from first element
                if count > 0:
                    try:
                        sample_text = elements[0].text.strip()[:100]
                        if sample_text:
                            print(f"   Sample text: {sample_text}...")
                    except:
                        pass
            else:
                print(f"❌ {selector}: 0 elements")
        except Exception as e:
            print(f"⚠️  {selector}: Error - {e}")
    
    # Check for comment-related text in page source
    page_source = driver.page_source.lower()
    comment_indicators = ['comment', 'comments-comment', 'data-id="urn:li:comment']
    
    print(f"\nPage source analysis:")
    for indicator in comment_indicators:
        count = page_source.count(indicator)
        print(f"  '{indicator}': {count} occurrences")
    
    # Save page source for analysis
    filename = f"linkedin_page_source_{url_name.lower().replace(' ', '_')}.html"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(driver.page_source)
    print(f"\n💾 Page source saved to: {filename}")
    
    return found_elements

def main():
    """Main debug function"""
    # Get credentials from environment
    email = os.getenv('LINKEDIN_EMAIL')
    password = os.getenv('LINKEDIN_PASSWORD')
    
    if not email or not password:
        print("❌ Please set LINKEDIN_EMAIL and LINKEDIN_PASSWORD environment variables")
        return
    
    profile_url = "https://www.linkedin.com/in/shashank-n-security"
    
    driver = setup_driver()
    
    try:
        # Login to LinkedIn
        print("🔐 Logging into LinkedIn...")
        actions.login(driver, email, password)
        print("✅ Login successful")
        time.sleep(3)
        
        # Test different URLs
        urls_to_test = [
            (f"{profile_url}/recent-activity/comments/", "Comments Activity Page"),
            (f"{profile_url}/recent-activity/all/", "All Activity Page"),
            (f"{profile_url}/recent-activity/", "Recent Activity Page"),
            (profile_url, "Profile Page")
        ]
        
        all_results = {}
        
        for url, name in urls_to_test:
            try:
                results = test_url_and_selectors(driver, url, name)
                all_results[name] = results
            except Exception as e:
                print(f"❌ Error testing {name}: {e}")
                all_results[name] = {}
        
        # Summary
        print(f"\n{'='*60}")
        print("SUMMARY OF FINDINGS")
        print(f"{'='*60}")
        
        for page_name, results in all_results.items():
            print(f"\n{page_name}:")
            if results:
                # Show selectors that found elements
                found_selectors = {k: v for k, v in results.items() if v > 0}
                if found_selectors:
                    for selector, count in found_selectors.items():
                        print(f"  ✅ {selector}: {count} elements")
                else:
                    print(f"  ❌ No elements found with any selector")
            else:
                print(f"  ⚠️  Error occurred during testing")
        
        print(f"\n🎯 Debug session completed!")
        
    except Exception as e:
        print(f"❌ Error during debug session: {e}")
    
    finally:
        driver.quit()

if __name__ == "__main__":
    main()