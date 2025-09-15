#!/usr/bin/env python3
"""
LinkedIn Selector Debug Script
This script logs into LinkedIn and inspects the DOM structure of the comments activity page
to identify the correct CSS selectors for comment elements.
"""

import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

# Add the linkedin_scraper directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'linkedin_scraper'))

from linkedin_scraper import actions

def setup_driver():
    """Setup Chrome driver with appropriate options"""
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def debug_page_structure(driver, profile_url):
    """Debug the page structure to find comment elements"""
    print("\n" + "="*60)
    print("DEBUGGING LINKEDIN COMMENTS PAGE STRUCTURE")
    print("="*60)
    
    # Navigate to comments activity page
    comments_url = f"{profile_url.rstrip('/')}/recent-activity/comments/"
    print(f"\nNavigating to: {comments_url}")
    driver.get(comments_url)
    time.sleep(3)
    
    # Scroll to load content
    print("\nScrolling to load content...")
    for i in range(3):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
    
    print("\n" + "-"*50)
    print("ANALYZING PAGE STRUCTURE")
    print("-"*50)
    
    # Check page title and URL
    print(f"Page Title: {driver.title}")
    print(f"Current URL: {driver.current_url}")
    
    # Look for activity-related elements
    activity_selectors = [
        "main",
        "[data-view-name='profile-activity']",
        ".scaffold-layout__main",
        ".profile-activity",
        ".activity-feed",
        ".feed-container",
        ".artdeco-card",
        "[data-urn]",
        "article",
        ".feed-shared-update-v2",
        ".activity-item",
        ".pvs-list",
        ".pvs-list__item"
    ]
    
    print("\n🔍 SEARCHING FOR ACTIVITY CONTAINERS:")
    for selector in activity_selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                print(f"  ✅ {selector}: {len(elements)} elements")
                # Get sample element info
                if len(elements) <= 5:
                    for i, elem in enumerate(elements[:3]):
                        try:
                            classes = elem.get_attribute('class') or 'no-class'
                            data_urn = elem.get_attribute('data-urn') or 'no-urn'
                            print(f"    [{i+1}] class='{classes[:100]}...' data-urn='{data_urn[:50]}...'")
                        except:
                            pass
            else:
                print(f"  ❌ {selector}: 0 elements")
        except Exception as e:
            print(f"  ⚠️  {selector}: Error - {e}")
    
    # Look for comment-specific patterns
    comment_patterns = [
        "comment",
        "Comment",
        "COMMENT",
        "reply",
        "Reply",
        "REPLY"
    ]
    
    print("\n🔍 SEARCHING FOR COMMENT-RELATED TEXT:")
    page_source = driver.page_source.lower()
    for pattern in comment_patterns:
        count = page_source.count(pattern.lower())
        if count > 0:
            print(f"  ✅ '{pattern}': {count} occurrences")
        else:
            print(f"  ❌ '{pattern}': 0 occurrences")
    
    # Look for elements containing comment-related text
    print("\n🔍 SEARCHING FOR ELEMENTS WITH COMMENT TEXT:")
    try:
        # Find elements containing "comment" text
        comment_text_elements = driver.find_elements(By.XPATH, "//*[contains(translate(text(), 'COMMENT', 'comment'), 'comment')]")
        print(f"  Elements with 'comment' text: {len(comment_text_elements)}")
        
        for i, elem in enumerate(comment_text_elements[:5]):
            try:
                tag_name = elem.tag_name
                classes = elem.get_attribute('class') or 'no-class'
                text = elem.text[:100].replace('\n', ' ') if elem.text else 'no-text'
                print(f"    [{i+1}] <{tag_name}> class='{classes[:50]}...' text='{text}...'")
            except:
                pass
    except Exception as e:
        print(f"  Error searching comment text: {e}")
    
    # Check for specific LinkedIn activity structures
    print("\n🔍 SEARCHING FOR LINKEDIN ACTIVITY STRUCTURES:")
    linkedin_selectors = [
        "[data-view-name]",
        "[data-test-id]",
        "[data-urn*='activity']",
        "[data-urn*='comment']",
        "[data-urn*='ugcPost']",
        ".feed-shared-activity",
        ".feed-shared-update",
        ".update-components-text",
        ".activity-item__commentary",
        ".feed-shared-text"
    ]
    
    for selector in linkedin_selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                print(f"  ✅ {selector}: {len(elements)} elements")
                # Show sample attributes
                for i, elem in enumerate(elements[:2]):
                    try:
                        attrs = []
                        for attr in ['class', 'data-urn', 'data-test-id', 'data-view-name']:
                            val = elem.get_attribute(attr)
                            if val:
                                attrs.append(f"{attr}='{val[:30]}...'")
                        print(f"    [{i+1}] {' '.join(attrs)}")
                    except:
                        pass
            else:
                print(f"  ❌ {selector}: 0 elements")
        except Exception as e:
            print(f"  ⚠️  {selector}: Error - {e}")
    
    # Save page source for manual inspection
    try:
        with open('linkedin_comments_page_source.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print(f"\n💾 Page source saved to: linkedin_comments_page_source.html")
    except Exception as e:
        print(f"\n⚠️  Could not save page source: {e}")
    
    print("\n" + "="*60)
    print("DEBUG ANALYSIS COMPLETE")
    print("="*60)

def main():
    # Get credentials from environment variables
    email = os.getenv('LINKEDIN_EMAIL')
    password = os.getenv('LINKEDIN_PASSWORD')
    profile_url = "https://www.linkedin.com/in/shashank-n-security/"
    
    if not email or not password:
        print("❌ Error: Please set LINKEDIN_EMAIL and LINKEDIN_PASSWORD environment variables")
        print("Example:")
        print("export LINKEDIN_EMAIL='your-email@example.com'")
        print("export LINKEDIN_PASSWORD='your-password'")
        return
    
    print("LinkedIn Comments Page Structure Debugger")
    print("==========================================")
    print(f"Target Profile: {profile_url}")
    print("\nInitializing Chrome driver...")
    
    driver = setup_driver()
    
    try:
        print("\nLogging into LinkedIn...")
        actions.login(driver, email, password)
        print("✅ Successfully logged into LinkedIn")
        
        # Debug the page structure
        debug_page_structure(driver, profile_url)
        
    except Exception as e:
        print(f"❌ Error during debugging: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("\nClosing browser...")
        driver.quit()
        print("✅ Debug session completed!")

if __name__ == "__main__":
    main()