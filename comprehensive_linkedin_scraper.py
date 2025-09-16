#!/usr/bin/env python3
"""
Comprehensive LinkedIn Profile Scraper

This script scrapes a LinkedIn profile and extracts:
- Person details (name, title, about, experience, education)
- Recent 5 posts
- Recent 5 comments
- Recent 5 reactions

Usage:
    python3 comprehensive_linkedin_scraper.py <linkedin_profile_url>

Example:
    python3 comprehensive_linkedin_scraper.py https://www.linkedin.com/in/shashank-n-security/

Requires:
    - LINKEDIN_EMAIL environment variable
    - LINKEDIN_PASSWORD environment variable
"""

import sys
import os
import json
import argparse
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Add the linkedin_scraper directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'linkedin_scraper'))

from linkedin_scraper import Person, actions

def setup_driver():
    """Setup Chrome driver with stealth options and better timeout handling"""
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--disable-web-security')
    chrome_options.add_argument('--allow-running-insecure-content')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Set timeouts
    chrome_options.add_argument('--timeout=30')
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(30)
        driver.implicitly_wait(10)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver
    except Exception as e:
        print(f"❌ Error setting up Chrome driver: {e}")
        raise

def scrape_comprehensive_profile(profile_url, output_file=None):
    """
    Scrape comprehensive LinkedIn profile data
    
    Args:
        profile_url (str): LinkedIn profile URL
        output_file (str): Optional output file path
    
    Returns:
        dict: Comprehensive profile data
    """
    # Get credentials from environment
    email = os.getenv('LINKEDIN_EMAIL')
    password = os.getenv('LINKEDIN_PASSWORD')
    
    if not email or not password:
        print("❌ Please set LINKEDIN_EMAIL and LINKEDIN_PASSWORD environment variables")
        return None
    
    print(f"\n{'='*60}")
    print("COMPREHENSIVE LINKEDIN PROFILE SCRAPER")
    print(f"{'='*60}")
    print(f"Target Profile: {profile_url}")
    print(f"Extracting: Person details, 5 posts, 5 comments, 5 reactions")
    print()
    
    driver = setup_driver()
    comprehensive_data = {
        "profile_url": profile_url,
        "scraped_at": datetime.now().isoformat(),
        "person_details": {},
        "recent_posts": [],
        "recent_comments": [],
        "recent_reactions": [],
        "scraping_status": {
            "person_details": "pending",
            "posts": "pending",
            "comments": "pending",
            "reactions": "pending"
        }
    }
    
    try:
        # Login to LinkedIn
        print("🔐 Logging into LinkedIn...")
        actions.login(driver, email, password)
        
        # Test if login was successful by checking current URL
        import time
        time.sleep(3)
        current_url = driver.current_url
        if 'linkedin.com/login' in current_url or 'linkedin.com/checkpoint' in current_url:
            raise Exception("Login failed - still on login page")
        
        print("✅ Successfully logged into LinkedIn\n")
        
        # Initialize Person object
        person = Person(linkedin_url=profile_url, driver=driver, scrape=False, close_on_complete=False)
        
        # 1. Scrape Person Details
        print("👤 Scraping person details...")
        try:
            person.scrape(close_on_complete=False)
            
            # Extract person details
            person_details = {
                "name": person.name,
                "job_title": person.job_title,
                "company": person.company,
                "about": person.about,
                "location": getattr(person, 'location', None),
                "experiences": [],
                "educations": [],
                "contacts": {}
            }
            
            # Add experiences
            if hasattr(person, 'experiences') and person.experiences:
                for exp in person.experiences:
                    person_details["experiences"].append({
                        "institution_name": getattr(exp, 'institution_name', ''),
                        "website": getattr(exp, 'website', ''),
                        "industry": getattr(exp, 'industry', ''),
                        "type": getattr(exp, 'type', ''),
                        "headquarters": getattr(exp, 'headquarters', ''),
                        "company_size": getattr(exp, 'company_size', ''),
                        "founded": getattr(exp, 'founded', ''),
                        "specialties": getattr(exp, 'specialties', ''),
                        "showcase_pages": getattr(exp, 'showcase_pages', []),
                        "affiliated_companies": getattr(exp, 'affiliated_companies', [])
                    })
            
            # Add educations
            if hasattr(person, 'educations') and person.educations:
                for edu in person.educations:
                    person_details["educations"].append({
                        "institution_name": getattr(edu, 'institution_name', ''),
                        "website": getattr(edu, 'website', ''),
                        "industry": getattr(edu, 'industry', ''),
                        "type": getattr(edu, 'type', ''),
                        "headquarters": getattr(edu, 'headquarters', ''),
                        "company_size": getattr(edu, 'company_size', ''),
                        "founded": getattr(edu, 'founded', ''),
                        "specialties": getattr(edu, 'specialties', ''),
                        "showcase_pages": getattr(edu, 'showcase_pages', []),
                        "affiliated_companies": getattr(edu, 'affiliated_companies', [])
                    })
            
            # Add contacts
            if hasattr(person, 'contacts') and person.contacts:
                for contact in person.contacts:
                    contact_type = getattr(contact, 'type', 'unknown')
                    contact_value = getattr(contact, 'contact', '')
                    person_details["contacts"][contact_type] = contact_value
            
            comprehensive_data["person_details"] = person_details
            comprehensive_data["scraping_status"]["person_details"] = "success"
            print(f"✅ Person details extracted: {person.name}")
            
        except Exception as e:
            print(f"❌ Error scraping person details: {e}")
            comprehensive_data["scraping_status"]["person_details"] = f"error: {str(e)}"
        
        # 2. Scrape Recent Posts
        print("\n📝 Scraping recent 5 posts...")
        try:
            posts = person.get_posts(hours_limit=24)
            recent_posts = []
            
            for i, post in enumerate(posts[:5]):
                post_data = {
                    "content": getattr(post, 'content', ''),
                    "posted_date": getattr(post, 'posted_date', ''),
                    "likes": getattr(post, 'likes', 0),
                    "comments": getattr(post, 'comments', 0),
                    "shares": getattr(post, 'shares', 0),
                    "post_url": getattr(post, 'post_url', '')
                }
                recent_posts.append(post_data)
                print(f"📄 Post {i+1}: {post_data['content'][:50]}...")
            
            comprehensive_data["recent_posts"] = recent_posts
            comprehensive_data["scraping_status"]["posts"] = "success"
            print(f"✅ Extracted {len(recent_posts)} posts")
            
        except Exception as e:
            print(f"⚠️ Posts extraction failed: {e}")
            comprehensive_data["scraping_status"]["posts"] = f"error: {str(e)}"
        
        # 3. Scrape Recent Comments
        print("\n💬 Scraping recent 5 comments...")
        try:
            comments = person.get_comments(comment_limit=5)
            recent_comments = []
            
            for i, comment in enumerate(comments[:5]):
                comment_data = {
                    "content": getattr(comment, 'content', ''),
                    "commented_date": getattr(comment, 'commented_date', ''),
                    "likes": getattr(comment, 'likes', 0),
                    "replies": getattr(comment, 'replies', 0),
                    "post_url": getattr(comment, 'post_url', ''),
                    "author": getattr(comment, 'author', '')
                }
                recent_comments.append(comment_data)
                print(f"💭 Comment {i+1}: {comment_data['content'][:50]}...")
            
            comprehensive_data["recent_comments"] = recent_comments
            comprehensive_data["scraping_status"]["comments"] = "success"
            print(f"✅ Extracted {len(recent_comments)} comments")
            
        except Exception as e:
            print(f"⚠️ Comments extraction failed: {e}")
            comprehensive_data["scraping_status"]["comments"] = f"error: {str(e)}"
        
        # 4. Scrape Recent Reactions
        print("\n👍 Scraping recent 5 reactions...")
        try:
            reactions = person.get_reactions(reaction_limit=5)
            recent_reactions = []
            
            for i, reaction in enumerate(reactions[:5]):
                reaction_data = {
                    "reaction_type": getattr(reaction, 'reaction_type', ''),
                    "reacted_date": getattr(reaction, 'reacted_date', ''),
                    "post_content": getattr(reaction, 'post_content', ''),
                    "post_author": getattr(reaction, 'post_author', ''),
                    "post_url": getattr(reaction, 'post_url', '')
                }
                recent_reactions.append(reaction_data)
                print(f"👍 Reaction {i+1}: {reaction_data['reaction_type']} on {reaction_data['post_content'][:30]}...")
            
            comprehensive_data["recent_reactions"] = recent_reactions
            comprehensive_data["scraping_status"]["reactions"] = "success"
            print(f"✅ Extracted {len(recent_reactions)} reactions")
            
        except Exception as e:
            print(f"⚠️ Reactions extraction failed: {e}")
            comprehensive_data["scraping_status"]["reactions"] = f"error: {str(e)}"
        
    except Exception as e:
        print(f"❌ Critical error during scraping: {e}")
        comprehensive_data["critical_error"] = str(e)
    
    finally:
        driver.quit()
    
    # Save results
    if not output_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        profile_name = profile_url.split('/')[-2] if profile_url.endswith('/') else profile_url.split('/')[-1]
        output_file = f"comprehensive_linkedin_data_{profile_name}_{timestamp}.json"
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(comprehensive_data, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Comprehensive data saved to: {output_file}")
    except Exception as e:
        print(f"❌ Error saving data: {e}")
    
    # Print summary
    print(f"\n{'='*60}")
    print("SCRAPING SUMMARY")
    print(f"{'='*60}")
    print(f"Person Details: {comprehensive_data['scraping_status']['person_details']}")
    print(f"Posts: {comprehensive_data['scraping_status']['posts']} ({len(comprehensive_data['recent_posts'])} extracted)")
    print(f"Comments: {comprehensive_data['scraping_status']['comments']} ({len(comprehensive_data['recent_comments'])} extracted)")
    print(f"Reactions: {comprehensive_data['scraping_status']['reactions']} ({len(comprehensive_data['recent_reactions'])} extracted)")
    print(f"\n✅ Comprehensive scraping completed!")
    
    return comprehensive_data

def main():
    """Main function to handle CLI arguments and run scraper"""
    parser = argparse.ArgumentParser(
        description='Comprehensive LinkedIn Profile Scraper',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 comprehensive_linkedin_scraper.py https://www.linkedin.com/in/shashank-n-security/
  python3 comprehensive_linkedin_scraper.py https://www.linkedin.com/in/john-doe/ --output john_doe_data.json

Environment Variables Required:
  LINKEDIN_EMAIL    - Your LinkedIn email
  LINKEDIN_PASSWORD - Your LinkedIn password

Example setup:
  export LINKEDIN_EMAIL="your-email@example.com"
  export LINKEDIN_PASSWORD="your-password"
  python3 comprehensive_linkedin_scraper.py https://www.linkedin.com/in/profile/
        """
    )
    
    parser.add_argument(
        'profile_url',
        help='LinkedIn profile URL to scrape'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Output JSON file path (optional)'
    )
    
    args = parser.parse_args()
    
    # Validate profile URL
    if not args.profile_url.startswith('https://www.linkedin.com/in/'):
        print("❌ Error: Please provide a valid LinkedIn profile URL")
        print("   Format: https://www.linkedin.com/in/username/")
        sys.exit(1)
    
    # Check environment variables
    if not os.getenv('LINKEDIN_EMAIL') or not os.getenv('LINKEDIN_PASSWORD'):
        print("❌ Error: LinkedIn credentials not found")
        print("   Please set LINKEDIN_EMAIL and LINKEDIN_PASSWORD environment variables")
        print("\n   Example:")
        print("   export LINKEDIN_EMAIL=\"your-email@example.com\"")
        print("   export LINKEDIN_PASSWORD=\"your-password\"")
        sys.exit(1)
    
    # Run comprehensive scraper
    try:
        result = scrape_comprehensive_profile(args.profile_url, args.output)
        if result:
            sys.exit(0)
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  Scraping interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()