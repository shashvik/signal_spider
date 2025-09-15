#!/usr/bin/env python3
"""
LinkedIn Posts Scraper for Shashank N Security
This script scrapes posts from the last 24 hours from: https://www.linkedin.com/in/shashank-n-security/
"""

import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import datetime

# Add the linkedin_scraper module to the path
sys.path.append('./linkedin_scraper')

from linkedin_scraper import Person, actions

def setup_chrome_driver():
    """Setup Chrome driver with appropriate options"""
    try:
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver
    except Exception as e:
        print(f"Error setting up Chrome driver: {e}")
        print("Make sure ChromeDriver is installed and in your PATH")
        return None

def scrape_posts(profile_url, hours_limit=24, email=None, password=None):
    """Scrape LinkedIn posts from the last specified hours"""
    driver = setup_chrome_driver()
    if not driver:
        return None
    
    try:
        # Get credentials from environment variables if not provided
        if not email:
            email = os.getenv("LINKEDIN_EMAIL")
        if not password:
            password = os.getenv("LINKEDIN_PASSWORD")
        
        # Login to LinkedIn (required for posts)
        if email and password:
            print("Logging into LinkedIn...")
            actions.login(driver, email, password)
            print("Login successful!")
        else:
            print("No credentials provided. You may need to login manually.")
            print("Set LINKEDIN_EMAIL and LINKEDIN_PASSWORD environment variables")
            print("or the script will prompt you for credentials.")
            actions.login(driver, email, password)  # Will prompt for credentials
        
        # Create person object and scrape posts
        print(f"Scraping posts from: {profile_url}")
        print(f"Looking for posts from the last {hours_limit} hours...")
        
        person = Person(profile_url, driver=driver, scrape=False)  # Don't scrape full profile
        person.get_posts(hours_limit=hours_limit)
        
        return person
        
    except Exception as e:
        print(f"Error during scraping: {e}")
        return None
    finally:
        if driver:
            driver.quit()

def display_posts_info(person):
    """Display scraped posts information"""
    if not person:
        print("No data to display.")
        return
    
    print("\n" + "=" * 60)
    print("LINKEDIN POSTS SCRAPING RESULTS")
    print("=" * 60)
    
    if person.posts:
        print(f"\nFound {len(person.posts)} posts from the last 24 hours:")
        print("-" * 50)
        
        for i, post in enumerate(person.posts, 1):
            print(f"\nPost #{i}:")
            print(f"  Posted: {post.posted_date}")
            print(f"  Author: {post.author_name}")
            print(f"  Media Type: {post.media_type}")
            print(f"  Content: {post.content[:200]}{'...' if len(post.content) > 200 else ''}")
            print(f"  Engagement:")
            print(f"    - Likes: {post.likes_count}")
            print(f"    - Comments: {post.comments_count}")
            print(f"    - Shares: {post.shares_count}")
            if post.post_url:
                print(f"  URL: {post.post_url}")
    else:
        print("\nNo posts found from the last 24 hours.")
        print("This could be because:")
        print("  - The user hasn't posted recently")
        print("  - The posts are not publicly visible")
        print("  - LinkedIn's structure has changed")
    
    print("\n" + "=" * 60)

def save_posts_to_file(person, filename=None):
    """Save posts data to a file"""
    if not person or not person.posts:
        print("No posts data to save.")
        return
    
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"linkedin_posts_{timestamp}.txt"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"LinkedIn Posts Scraping Results\n")
            f.write(f"Profile: {person.linkedin_url}\n")
            f.write(f"Scraped on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total posts found: {len(person.posts)}\n")
            f.write("=" * 60 + "\n\n")
            
            for i, post in enumerate(person.posts, 1):
                f.write(f"Post #{i}:\n")
                f.write(f"Posted: {post.posted_date}\n")
                f.write(f"Author: {post.author_name}\n")
                f.write(f"Media Type: {post.media_type}\n")
                f.write(f"\nContent:\n{post.content}\n\n")
                f.write(f"Engagement:\n")
                f.write(f"  - Likes: {post.likes_count}\n")
                f.write(f"  - Comments: {post.comments_count}\n")
                f.write(f"  - Shares: {post.shares_count}\n")
                if post.post_url:
                    f.write(f"URL: {post.post_url}\n")
                f.write("\n" + "-" * 50 + "\n\n")
        
        print(f"\nPosts data saved to: {filename}")
        
    except Exception as e:
        print(f"Error saving to file: {e}")

def main():
    """Main function"""
    # Target profile URL
    profile_url = "https://www.linkedin.com/in/shashank-n-security/"
    
    print("LinkedIn Posts Scraper")
    print(f"Target Profile: {profile_url}")
    print("-" * 50)
    
    # You can set your LinkedIn credentials here or use environment variables
    # email = "your-email@example.com"
    # password = "your-password"
    
    # Scrape posts from the last 24 hours
    person = scrape_posts(profile_url, hours_limit=24)
    
    # Display the results
    display_posts_info(person)
    
    # Save to file
    if person and person.posts:
        save_posts_to_file(person)
    
if __name__ == "__main__":
    main()