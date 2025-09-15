#!/usr/bin/env python3
"""
LinkedIn Comments Scraper

This script scrapes comments made by a specific LinkedIn user on posts within the last 24 hours.
It extracts comment content, engagement metrics, and information about the original posts.

Usage:
    python3 scrape_comments.py

Environment Variables Required:
    LINKEDIN_EMAIL - Your LinkedIn email
    LINKEDIN_PASSWORD - Your LinkedIn password

Output:
    - Console display of found comments
    - JSON file with all comment data
    - Text file with human-readable format
"""

import sys
import os
import json
from datetime import datetime

# Add the linkedin_scraper directory to the path
sys.path.append('linkedin_scraper')

from linkedin_scraper import Person, Comment
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configuration
PROFILE_URL = "https://www.linkedin.com/in/shashank-n-security/"  # Change this to target profile
COMMENT_LIMIT = 5  # Get the latest 5 comments

def setup_driver():
    """Setup Chrome driver with appropriate options"""
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    
    # Uncomment the next line for headless mode
    # chrome_options.add_argument('--headless')
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        print(f"Error setting up Chrome driver: {e}")
        print("Make sure ChromeDriver is installed and in your PATH")
        sys.exit(1)

def login_to_linkedin(driver):
    """Login to LinkedIn using environment variables"""
    email = os.getenv('LINKEDIN_EMAIL')
    password = os.getenv('LINKEDIN_PASSWORD')
    
    if not email or not password:
        print("Error: Please set LINKEDIN_EMAIL and LINKEDIN_PASSWORD environment variables")
        print("Example:")
        print("  export LINKEDIN_EMAIL='your-email@example.com'")
        print("  export LINKEDIN_PASSWORD='your-password'")
        sys.exit(1)
    
    try:
        print("Logging into LinkedIn...")
        driver.get('https://www.linkedin.com/login')
        
        # Wait for login form and fill credentials
        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        password_field = driver.find_element(By.ID, "password")
        
        email_field.send_keys(email)
        password_field.send_keys(password)
        
        # Submit login form
        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        login_button.click()
        
        # Wait for successful login (check for feed or profile)
        WebDriverWait(driver, 15).until(
            EC.any_of(
                EC.presence_of_element_located((By.CLASS_NAME, "feed-shared-update-v2")),
                EC.presence_of_element_located((By.CLASS_NAME, "pv-top-card")),
                EC.url_contains("/feed/")
            )
        )
        
        print("✅ Successfully logged into LinkedIn")
        return True
        
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return False

def scrape_comments(profile_url, comment_limit=5):
    """Main function to scrape comments from a LinkedIn profile"""
    driver = setup_driver()
    
    try:
        # Login to LinkedIn
        if not login_to_linkedin(driver):
            return None
        
        print(f"\nScraping comments from: {profile_url}")
        print(f"Looking for the latest {comment_limit} comments...\n")
        
        # Create Person object and scrape comments
        person = Person(linkedin_url=profile_url, driver=driver, scrape=False)
        person.get_comments(comment_limit=comment_limit)
        
        return person
        
    except Exception as e:
        print(f"Error during scraping: {e}")
        return None
    finally:
        driver.quit()

def display_comments(person, comment_limit=5):
    """Display comments in a readable format"""
    if not person or not person.comments:
        print("No comments found.")
        return
    
    print(f"\n{'='*60}")
    print(f"LATEST {min(len(person.comments), comment_limit)} COMMENTS")
    print(f"{'='*60}")
    print(f"Total comments found: {len(person.comments)}\n")
    
    for i, comment in enumerate(person.comments, 1):
        print(f"Comment {i}:")
        print(f"Content: {comment.content[:200]}{'...' if len(comment.content) > 200 else ''}")
        print(f"Commented: {comment.commented_date}")
        print(f"Engagement: {comment.likes_count} likes, {comment.replies_count} replies")
        
        if comment.post_author:
            print(f"Original Post by: {comment.post_author}")
        
        if comment.post_content_preview:
            print(f"Post Preview: {comment.post_content_preview}")
        
        if comment.comment_url:
            print(f"Comment URL: {comment.comment_url}")
        
        if comment.post_url:
            print(f"Post URL: {comment.post_url}")
        
        print("-" * 40)

def save_comments_to_files(person, comment_limit=5):
    """Save comments to JSON and text files"""
    if not person or not person.comments:
        print("No comments to save.")
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save as JSON
    json_filename = f"linkedin_comments_{timestamp}.json"
    json_data = {
        "scrape_date": datetime.now().isoformat(),
        "profile_url": person.linkedin_url,
        "comment_limit": comment_limit,
        "total_comments": len(person.comments),
        "comments": [
            {
                "content": comment.content,
                "commented_date": comment.commented_date,
                "likes_count": comment.likes_count,
                "replies_count": comment.replies_count,
                "comment_url": comment.comment_url,
                "post_url": comment.post_url,
                "post_author": comment.post_author,
                "post_content_preview": comment.post_content_preview,
                "commenter_name": comment.commenter_name,
                "commenter_url": comment.commenter_url
            }
            for comment in person.comments
        ]
    }
    
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)
    
    # Save as readable text
    txt_filename = f"linkedin_comments_{timestamp}.txt"
    with open(txt_filename, 'w', encoding='utf-8') as f:
        f.write(f"LinkedIn Comments Scrape Results\n")
        f.write(f"{'='*50}\n")
        f.write(f"Profile: {person.linkedin_url}\n")
        f.write(f"Scrape Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Latest Comments: {comment_limit}\n")
        f.write(f"Total Comments: {len(person.comments)}\n\n")
        
        if person.comments:
            f.write(f"LATEST {min(len(person.comments), comment_limit)} COMMENTS:\n")
            f.write(f"{'='*50}\n\n")
            
            for i, comment in enumerate(person.comments, 1):
                f.write(f"Comment {i}:\n")
                f.write(f"Content: {comment.content}\n")
                f.write(f"Commented: {comment.commented_date}\n")
                f.write(f"Engagement: {comment.likes_count} likes, {comment.replies_count} replies\n")
                
                if comment.post_author:
                    f.write(f"Original Post by: {comment.post_author}\n")
                
                if comment.post_content_preview:
                    f.write(f"Post Preview: {comment.post_content_preview}\n")
                
                if comment.comment_url:
                    f.write(f"Comment URL: {comment.comment_url}\n")
                
                if comment.post_url:
                    f.write(f"Post URL: {comment.post_url}\n")
                
                f.write(f"Commenter: {comment.commenter_name} ({comment.commenter_url})\n")
                f.write("-" * 40 + "\n\n")
        else:
            f.write("No comments found.\n")
    
    print(f"\n📁 Results saved to:")
    print(f"   JSON: {json_filename}")
    print(f"   Text: {txt_filename}")

def main():
    """Main execution function"""
    print("LinkedIn Comments Scraper")
    print("========================")
    print(f"Target Profile: {PROFILE_URL}")
    print(f"Latest Comments: {COMMENT_LIMIT}\n")
    
    # Scrape comments
    person = scrape_comments(PROFILE_URL, COMMENT_LIMIT)
    
    if person:
        # Display results
        display_comments(person, COMMENT_LIMIT)
        
        # Save to files
        save_comments_to_files(person, COMMENT_LIMIT)
        
        print("\n✅ Comment scraping completed successfully!")
    else:
        print("\n❌ Comment scraping failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()