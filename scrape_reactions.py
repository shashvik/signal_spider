#!/usr/bin/env python3
"""
LinkedIn Reactions Scraper

This script scrapes the last 5 posts that a LinkedIn user reacted to.
It uses the linkedin_scraper library to navigate to the user's reactions activity page
and extract reaction data.

Usage:
    python3 scrape_reactions.py

Environment Variables:
    LINKEDIN_EMAIL: Your LinkedIn email
    LINKEDIN_PASSWORD: Your LinkedIn password
    TARGET_PROFILE_URL: The LinkedIn profile URL to scrape reactions from

Example:
    export LINKEDIN_EMAIL="your-email@example.com"
    export LINKEDIN_PASSWORD="your-password"
    export TARGET_PROFILE_URL="https://www.linkedin.com/in/shashank-n-security/"
    python3 scrape_reactions.py
"""

import os
import json
import sys
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Add the linkedin_scraper directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'linkedin_scraper'))

from linkedin_scraper.person import Person
from linkedin_scraper import actions

def setup_driver():
    """Setup Chrome driver with appropriate options"""
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    # Uncomment the next line to run in headless mode
    # chrome_options.add_argument('--headless')
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def scrape_reactions():
    """Main function to scrape LinkedIn reactions"""
    # Get environment variables
    email = os.getenv('LINKEDIN_EMAIL')
    password = os.getenv('LINKEDIN_PASSWORD')
    target_profile_url = os.getenv('TARGET_PROFILE_URL', 'https://www.linkedin.com/in/shashank-n-security/')
    
    if not email or not password:
        print("❌ Error: Please set LINKEDIN_EMAIL and LINKEDIN_PASSWORD environment variables")
        print("Example:")
        print('export LINKEDIN_EMAIL="your-email@example.com"')
        print('export LINKEDIN_PASSWORD="your-password"')
        return
    
    print(f"🚀 Starting LinkedIn reactions scraper...")
    print(f"📧 Email: {email}")
    print(f"🎯 Target Profile: {target_profile_url}")
    
    driver = None
    try:
        # Setup driver
        driver = setup_driver()
        print("✅ Chrome driver initialized")
        
        # Login to LinkedIn
        print("🔐 Logging into LinkedIn...")
        actions.login(driver, email, password)
        print("✅ Successfully logged in")
        
        # Create Person object
        person = Person(target_profile_url, driver=driver, scrape=False)
        print(f"👤 Created person object for: {target_profile_url}")
        
        # Scrape reactions (last 5 posts)
        print("🔍 Scraping reactions...")
        reactions = person.get_reactions(reaction_limit=5)
        
        if not reactions:
            print("❌ No reactions found")
            return
        
        print(f"✅ Successfully scraped {len(reactions)} reactions")
        
        # Generate timestamp for filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save to JSON file
        json_filename = f"linkedin_reactions_{timestamp}.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(reactions, f, indent=2, ensure_ascii=False)
        print(f"💾 Reactions saved to: {json_filename}")
        
        # Save to text file for easy reading
        txt_filename = f"linkedin_reactions_{timestamp}.txt"
        with open(txt_filename, 'w', encoding='utf-8') as f:
            f.write(f"LinkedIn Reactions Scraper Results\n")
            f.write(f"Target Profile: {target_profile_url}\n")
            f.write(f"Scraped on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total reactions found: {len(reactions)}\n")
            f.write("=" * 80 + "\n\n")
            
            for i, reaction in enumerate(reactions, 1):
                f.write(f"Reaction #{i}\n")
                f.write(f"Post Preview: {reaction.get('post_preview', 'N/A')}\n")
                f.write(f"Post Author: {reaction.get('post_author', 'N/A')}\n")
                f.write(f"Post URL: {reaction.get('post_url', 'N/A')}\n")
                f.write(f"Reaction Type: {reaction.get('reaction_type', 'N/A')}\n")
                f.write(f"Reacted Date: {reaction.get('reacted_date', 'N/A')}\n")
                f.write(f"Reactor: {reaction.get('reactor_name', 'N/A')}\n")
                f.write("-" * 40 + "\n\n")
        
        print(f"📄 Human-readable results saved to: {txt_filename}")
        
        # Print summary
        print("\n📊 SCRAPING SUMMARY:")
        print(f"   • Total reactions scraped: {len(reactions)}")
        print(f"   • JSON file: {json_filename}")
        print(f"   • Text file: {txt_filename}")
        
        # Print first few reactions as preview
        print("\n🔍 PREVIEW (First 3 reactions):")
        for i, reaction in enumerate(reactions[:3], 1):
            print(f"   {i}. {reaction.get('post_preview', 'N/A')[:60]}...")
            print(f"      Author: {reaction.get('post_author', 'N/A')}")
            print(f"      Reaction: {reaction.get('reaction_type', 'N/A')}")
            print()
        
    except Exception as e:
        print(f"❌ Error during scraping: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        if driver:
            print("🔄 Closing browser...")
            driver.quit()
            print("✅ Browser closed")

if __name__ == "__main__":
    scrape_reactions()