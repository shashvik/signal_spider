#!/usr/bin/env python3
"""
LinkedIn Profile Scraper for Shashank N Security
This script scrapes the LinkedIn profile: https://www.linkedin.com/in/shashank-n-security/
"""

import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Add the linkedin_scraper module to the path
sys.path.append('./linkedin_scraper')

from linkedin_scraper import Person, actions

def setup_chrome_driver():
    """Setup Chrome driver with options"""
    chrome_options = Options()
    # Uncomment the next line to run in headless mode (no browser window)
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        print(f"Error setting up Chrome driver: {e}")
        print("Make sure ChromeDriver is installed and in your PATH")
        print("You can download it from: https://chromedriver.chromium.org/")
        return None

def scrape_profile(profile_url, email=None, password=None):
    """Scrape LinkedIn profile"""
    driver = setup_chrome_driver()
    if not driver:
        return None
    
    try:
        # Get credentials from environment variables if not provided
        if not email:
            email = os.getenv("LINKEDIN_EMAIL")
        if not password:
            password = os.getenv("LINKEDIN_PASSWORD")
        
        # Login to LinkedIn (required for most profiles)
        if email and password:
            print("Logging into LinkedIn...")
            actions.login(driver, email, password)
            print("Login successful!")
        else:
            print("No credentials provided. You may need to login manually.")
            print("Set LINKEDIN_EMAIL and LINKEDIN_PASSWORD environment variables")
            print("or the script will prompt you for credentials.")
            actions.login(driver, email, password)  # Will prompt for credentials
        
        # Scrape the profile
        print(f"Scraping profile: {profile_url}")
        person = Person(profile_url, driver=driver, scrape=True)
        
        # Scrape posts from last 24 hours
        print("Scraping posts from last 24 hours...")
        person.get_posts(hours_limit=24)
        
        # Scrape comments from last 24 hours
        print("Scraping comments from last 24 hours...")
        person.get_comments(hours_limit=24)
        
        return person
        
    except Exception as e:
        print(f"Error during scraping: {e}")
        return None
    finally:
        if driver:
            driver.quit()

def display_profile_info(person):
    """Display scraped profile information"""
    if not person:
        print("No profile data to display")
        return
    
    print("\n" + "="*50)
    print("LINKEDIN PROFILE INFORMATION")
    print("="*50)
    
    print(f"Name: {person.name or 'N/A'}")
    print(f"Job Title: {person.job_title or 'N/A'}")
    print(f"Company: {person.company or 'N/A'}")
    print(f"LinkedIn URL: {person.linkedin_url or 'N/A'}")
    
    if person.about:
        print(f"\nAbout:\n{person.about}")
    
    if person.experiences:
        print("\nExperiences:")
        for i, exp in enumerate(person.experiences, 1):
            print(f"  {i}. {exp.position_title} at {exp.institution_name}")
            if hasattr(exp, 'duration') and exp.duration:
                print(f"     Duration: {exp.duration}")
            if hasattr(exp, 'location') and exp.location:
                print(f"     Location: {exp.location}")
            if hasattr(exp, 'description') and exp.description:
                print(f"     Description: {exp.description}")
            print()  # Add blank line between experiences
    
    if person.educations:
        print("\nEducation:")
        for i, edu in enumerate(person.educations, 1):
            print(f"  {i}. {edu.degree} at {edu.institution_name}")
    
    if person.interests:
        print("\nInterests:")
        for i, interest in enumerate(person.interests, 1):
            print(f"  {i}. {interest.title}")
    
    # Display posts from last 24 hours
    if person.posts:
        print(f"\nPosts from Last 24 Hours ({len(person.posts)} found):")
        for i, post in enumerate(person.posts, 1):
            print(f"  {i}. Posted: {post.posted_date}")
            print(f"     Content: {post.content[:100]}{'...' if len(post.content) > 100 else ''}")
            print(f"     Engagement: {post.likes_count} likes, {post.comments_count} comments, {post.shares_count} shares")
            print(f"     Media Type: {post.media_type}")
            if post.post_url:
                print(f"     URL: {post.post_url}")
    
    # Display comments from last 24 hours
    if person.comments:
        print(f"\nComments from Last 24 Hours ({len(person.comments)} found):")
        for i, comment in enumerate(person.comments, 1):
            print(f"  {i}. Commented: {comment.commented_date}")
            print(f"     Content: {comment.content[:100]}{'...' if len(comment.content) > 100 else ''}")
            print(f"     Engagement: {comment.likes_count} likes, {comment.replies_count} replies")
            if comment.post_author:
                print(f"     On post by: {comment.post_author}")
            if comment.post_content_preview:
                print(f"     Post preview: {comment.post_content_preview[:80]}{'...' if len(comment.post_content_preview) > 80 else ''}")
            if comment.comment_url:
                print(f"     Comment URL: {comment.comment_url}")
            print()
    
    print("\n" + "="*50)

def main():
    """Main function"""
    # Target profile URL
    profile_url = "https://www.linkedin.com/in/shashank-n-security/"
    
    print("LinkedIn Profile Scraper")
    print(f"Target Profile: {profile_url}")
    print("-" * 50)
    
    # You can set your LinkedIn credentials here or use environment variables
    # email = "your-email@example.com"
    # password = "your-password"
    
    # Scrape the profile
    person = scrape_profile(profile_url)
    
    # Display the results
    display_profile_info(person)
    
    # Optionally save to file
    if person and person.name:
        filename = f"{person.name.replace(' ', '_')}_linkedin_profile.txt"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"Name: {person.name or 'N/A'}\n")
                f.write(f"Job Title: {person.job_title or 'N/A'}\n")
                f.write(f"Company: {person.company or 'N/A'}\n")
                f.write(f"LinkedIn URL: {person.linkedin_url or 'N/A'}\n")
                if person.about:
                    f.write(f"\nAbout:\n{person.about}\n")
                if person.experiences:
                    f.write("\nExperiences:\n")
                    for i, exp in enumerate(person.experiences, 1):
                        f.write(f"{i}. {exp.position_title} at {exp.institution_name}\n")
                        if hasattr(exp, 'duration') and exp.duration:
                            f.write(f"   Duration: {exp.duration}\n")
                        if hasattr(exp, 'location') and exp.location:
                            f.write(f"   Location: {exp.location}\n")
                        if hasattr(exp, 'description') and exp.description:
                            f.write(f"   Description: {exp.description}\n")
                        f.write("\n")  # Add blank line between experiences
                if person.posts:
                    f.write(f"\nPosts from Last 24 Hours ({len(person.posts)} found):\n")
                    for i, post in enumerate(person.posts, 1):
                        f.write(f"{i}. Posted: {post.posted_date}\n")
                        f.write(f"   Content: {post.content[:100]}{'...' if len(post.content) > 100 else ''}\n")
                        f.write(f"   Engagement: {post.likes_count} likes, {post.comments_count} comments, {post.shares_count} shares\n")
                        f.write(f"   Media Type: {post.media_type}\n")
                        if post.post_url:
                            f.write(f"   URL: {post.post_url}\n")
                        f.write("\n")
                if person.comments:
                    f.write(f"\nComments from Last 24 Hours ({len(person.comments)} found):\n")
                    for i, comment in enumerate(person.comments, 1):
                        f.write(f"{i}. Commented: {comment.commented_date}\n")
                        f.write(f"   Content: {comment.content[:100]}{'...' if len(comment.content) > 100 else ''}\n")
                        f.write(f"   Engagement: {comment.likes_count} likes, {comment.replies_count} replies\n")
                        if comment.post_author:
                            f.write(f"   On post by: {comment.post_author}\n")
                        if comment.post_content_preview:
                            f.write(f"   Post preview: {comment.post_content_preview[:80]}{'...' if len(comment.post_content_preview) > 80 else ''}\n")
                        if comment.comment_url:
                            f.write(f"   Comment URL: {comment.comment_url}\n")
                        f.write("\n")
            print(f"\nProfile data saved to: {filename}")
        except Exception as e:
            print(f"Error saving to file: {e}")

if __name__ == "__main__":
    main()