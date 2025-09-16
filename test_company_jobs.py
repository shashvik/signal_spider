#!/usr/bin/env python3
"""
Test script for company job scraping functionality

This script demonstrates how to use the modified Job class to get all jobs from a specific company.

Usage:
    python3 test_company_jobs.py "Google" --max-jobs 10
    python3 test_company_jobs.py "Microsoft" --detailed
"""

import sys
import os
import json
import argparse
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Add linkedin_scraper to path
sys.path.append('linkedin_scraper')
from linkedin_scraper import actions
from linkedin_scraper.jobs import Job


def setup_driver():
    """Setup Chrome driver with appropriate options"""
    try:
        print("🚀 Setting up Chrome driver...")
        
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.notifications": 2
        })
        
        # Try system ChromeDriver first (most stable)
        driver = None
        
        try:
            print("Trying system ChromeDriver...")
            driver = webdriver.Chrome(options=chrome_options)
        except Exception as e1:
            print(f"⚠️ System ChromeDriver failed: {e1}")
            
            # Try common ChromeDriver paths
            common_paths = [
                "/usr/local/bin/chromedriver",
                "/opt/homebrew/bin/chromedriver",
                "./chromedriver"
            ]
            
            for path in common_paths:
                try:
                    print(f"Trying ChromeDriver at {path}...")
                    service = Service(path)
                    driver = webdriver.Chrome(service=service, options=chrome_options)
                    break
                except Exception:
                    continue
            
            # Last resort: Use webdriver-manager
            if not driver:
                try:
                    print("Trying webdriver-manager...")
                    from webdriver_manager.chrome import ChromeDriverManager
                    service = Service(ChromeDriverManager().install())
                    driver = webdriver.Chrome(service=service, options=chrome_options)
                except Exception as e3:
                    print(f"⚠️ webdriver-manager failed: {e3}")
        
        if driver:
            # Execute script to remove webdriver property
            try:
                driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            except Exception:
                pass  # Ignore if this fails
            
            return driver
        else:
            raise Exception("Could not initialize ChromeDriver with any method")
        
    except Exception as e:
        print(f"❌ Error setting up driver: {e}")
        print("💡 Try installing Chrome and ChromeDriver:")
        print("   brew install chromedriver")
        print("   or download from: https://chromedriver.chromium.org/")
        return None


def main():
    parser = argparse.ArgumentParser(description='Test company job scraping')
    parser.add_argument('company_name', help='Name of the company to search for jobs')
    parser.add_argument('--max-jobs', type=int, default=10, help='Maximum number of jobs to retrieve (default: 10)')
    parser.add_argument('--detailed', action='store_true', help='Scrape detailed job information')
    parser.add_argument('--output', help='Output JSON file (optional)')
    
    args = parser.parse_args()
    
    # Get LinkedIn credentials
    email = os.getenv('LINKEDIN_EMAIL', 'thecuriositycabinet98@gmail.com')
    password = os.getenv('LINKEDIN_PASSWORD', 'class7arox')
    
    if not email or not password:
        print("❌ Please set LINKEDIN_EMAIL and LINKEDIN_PASSWORD environment variables")
        sys.exit(1)
    
    driver = None
    
    try:
        print(f"🔍 Searching for jobs at {args.company_name}...")
        print(f"📊 Max jobs: {args.max_jobs}")
        print(f"🔬 Detailed scraping: {'Yes' if args.detailed else 'No'}")
        print()
        
        # Setup driver
        print("🚀 Setting up Chrome driver...")
        driver = setup_driver()
        
        # Login to LinkedIn
        print("🔐 Logging into LinkedIn...")
        actions.login(driver, email, password)
        print("✅ Successfully logged into LinkedIn")
        print()
        
        # Search for company jobs
        if args.detailed:
            print("🔍 Searching and scraping detailed job information...")
            jobs = Job.scrape_company_jobs_detailed(driver, "security engineer", args.company_name, args.max_jobs)
        else:
            print("🔍 Searching for basic job information...")
            jobs = Job.get_company_jobs(driver, "security engineer", args.company_name, args.max_jobs)
        
        print(f"\n📋 Found {len(jobs)} jobs at {args.company_name}:")
        print("=" * 60)
        
        # Display results
        job_data = []
        for i, job in enumerate(jobs, 1):
            print(f"{i}. {job.job_title}")
            print(f"   Company: {job.company}")
            print(f"   Location: {job.location}")
            print(f"   URL: {job.linkedin_url}")
            
            if args.detailed and hasattr(job, 'job_description') and job.job_description:
                print(f"   Description: {job.job_description[:100]}...")
                print(f"   Posted: {job.posted_date}")
                print(f"   Applicants: {job.applicant_count}")
            
            print()
            
            # Convert to dict for JSON output
            job_data.append(job.to_dict())
        
        # Save to JSON if requested
        if args.output:
            output_data = {
                'company': args.company_name,
                'search_date': datetime.now().isoformat(),
                'total_jobs': len(jobs),
                'detailed_scraping': args.detailed,
                'jobs': job_data
            }
            
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Results saved to: {args.output}")
        
        print(f"\n✅ Successfully found {len(jobs)} jobs at {args.company_name}!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
        
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass


if __name__ == "__main__":
    main()