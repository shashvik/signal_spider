#!/usr/bin/env python3
"""
Debug script to identify why comment scraping is not working.
This version provides multiple debugging approaches including offline analysis.
"""

import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

# Configuration
PROFILE_URL = "https://www.linkedin.com/in/shashank-n-security/"

def setup_driver():
    """Setup Chrome driver with appropriate options."""
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def analyze_linkedin_selectors():
    """Analyze common LinkedIn selectors and provide debugging info."""
    print("=== LINKEDIN COMMENT SCRAPING DEBUG ANALYSIS ===")
    print()
    
    print("🔍 POTENTIAL ISSUES WITH CURRENT APPROACH:")
    print("1. LinkedIn frequently changes their CSS selectors")
    print("2. The selector '[data-urn*=\"comment\"]' may be outdated")
    print("3. LinkedIn's recent-activity/comments page might have different structure")
    print("4. Comments might be loaded dynamically and require different timing")
    print()
    
    print("📋 COMMON LINKEDIN SELECTORS TO TRY:")
    selectors = [
        "[data-urn*='comment']",  # Current selector
        ".feed-shared-update-v2",  # General feed items
        ".feed-shared-comment",   # Direct comment selector
        "[data-test-id*='comment']",  # Test ID based
        ".comments-comment-item",  # Comment item class
        ".activity-item",  # Activity items
        ".feed-shared-mini-update-v2",  # Mini updates
        "article[data-urn]",  # Article elements with data-urn
        "[role='article']",  # ARIA role articles
        ".feed-shared-activity"  # Activity containers
    ]
    
    for i, selector in enumerate(selectors, 1):
        status = "✅ CURRENT" if selector == "[data-urn*='comment']" else "🔄 ALTERNATIVE"
        print(f"{i:2d}. {status} {selector}")
    
    print()
    print("🛠️  DEBUGGING STEPS TO TRY:")
    print("1. Check if the profile has any recent comments")
    print("2. Manually visit the comments page and inspect elements")
    print("3. Try different wait times for page loading")
    print("4. Check if LinkedIn requires different authentication")
    print("5. Verify the URL format is correct")
    print()
    
    print("🔧 QUICK FIXES TO IMPLEMENT:")
    print("1. Add more robust element waiting")
    print("2. Try multiple selectors in sequence")
    print("3. Add better error logging")
    print("4. Implement fallback selectors")
    print()
    
    print("📝 URL BEING ACCESSED:")
    activity_url = f"{PROFILE_URL.rstrip('/')}/recent-activity/comments/"
    print(f"   {activity_url}")
    print()
    
    print("⚠️  POSSIBLE REASONS FOR 0 COMMENTS:")
    print("1. The profile genuinely has no recent comments")
    print("2. Comments are private/not visible to scrapers")
    print("3. LinkedIn changed their page structure")
    print("4. The CSS selector is incorrect")
    print("5. Comments require additional scrolling/loading")
    print()

def create_improved_selector_test():
    """Create an improved version of the comment detection logic."""
    print("🚀 CREATING IMPROVED COMMENT DETECTION LOGIC...")
    
    improved_code = '''
# IMPROVED COMMENT DETECTION - Add this to person.py get_comments method

# Try multiple selectors in order of preference
comment_selectors = [
    "[data-urn*='comment']",
    ".feed-shared-update-v2",
    ".feed-shared-comment",
    "article[data-urn]",
    "[data-test-id*='comment']",
    ".activity-item",
    ".feed-shared-mini-update-v2"
]

comment_elements = []
for selector in comment_selectors:
    try:
        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
        if elements:
            print(f"✅ Found {len(elements)} elements with selector: {selector}")
            comment_elements = elements
            break
        else:
            print(f"❌ No elements found with selector: {selector}")
    except Exception as e:
        print(f"⚠️  Error with selector {selector}: {e}")
        continue

if not comment_elements:
    print("🔍 No comment elements found with any selector. Checking page content...")
    try:
        page_source = self.driver.page_source
        if "No activity yet" in page_source or "hasn\'t shared anything" in page_source:
            print("📝 Profile has no recent activity")
        elif "comment" in page_source.lower():
            print("📝 Page contains 'comment' text but elements not found")
        else:
            print("📝 Page loaded but structure unclear")
    except Exception as e:
        print(f"Error checking page source: {e}")
'''
    
    print(improved_code)
    print()
    
    return improved_code

def main():
    """Main debug function."""
    analyze_linkedin_selectors()
    improved_code = create_improved_selector_test()
    
    print("💡 NEXT STEPS:")
    print("1. Manually check the LinkedIn profile for recent comments")
    print("2. If comments exist, implement the improved selector logic above")
    print("3. Test with credentials using: export LINKEDIN_EMAIL=your_email")
    print("4. Run the original scraper to see detailed selector results")
    print()
    
    # Save the improved code to a file
    with open('improved_comment_detection.py', 'w') as f:
        f.write(f"# Improved Comment Detection Logic\n# Generated by debug_comments.py\n\n{improved_code}")
    
    print("📁 Saved improved detection logic to: improved_comment_detection.py")
    print("   You can copy this code into the person.py get_comments method")

if __name__ == "__main__":
    main()