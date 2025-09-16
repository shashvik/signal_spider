#!/usr/bin/env python3
"""
LinkedIn Company Job Scraper

This script searches for jobs from a specific company with a specific job title on LinkedIn.
It uses the existing JobSearch functionality and adds company-specific filtering.

Usage:
    python3 company_job_scraper.py "Google" "Software Engineer"
    python3 company_job_scraper.py "Microsoft" "Data Scientist" --output jobs.json

Requirements:
    - LinkedIn credentials set as environment variables:
      LINKEDIN_EMAIL and LINKEDIN_PASSWORD
    - Chrome browser installed
    - selenium package installed
"""

import sys
import os
import json
import argparse
from datetime import datetime
from typing import List, Dict, Any
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# Import LinkedIn scraper modules
sys.path.append('linkedin_scraper')
from linkedin_scraper import actions
from linkedin_scraper.job_search import JobSearch
from linkedin_scraper.jobs import Job


def setup_driver():
    """Setup Chrome driver with stealth options"""
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--disable-web-security')
    chrome_options.add_argument('--allow-running-insecure-content')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--remote-debugging-port=9222')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    try:
        # Use webdriver-manager to automatically manage ChromeDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_page_load_timeout(30)
        driver.implicitly_wait(10)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver
    except Exception as e:
        print(f"❌ Error setting up Chrome driver: {e}")
        print("💡 Try installing Chrome browser or updating ChromeDriver")
        raise


def normalize_company_name(company_name: str) -> str:
    """Normalize company name for comparison"""
    return company_name.lower().strip().replace(',', '').replace('.', '').replace('inc', '').replace('llc', '').replace('corp', '').strip()


def is_company_match(job_company: str, target_company: str) -> bool:
    """Check if job company matches target company"""
    if not job_company or not target_company:
        return False
    
    job_company_norm = normalize_company_name(job_company)
    target_company_norm = normalize_company_name(target_company)
    
    # Exact match
    if target_company_norm in job_company_norm:
        return True
    
    # Check if target company is a substring of job company
    if target_company_norm in job_company_norm.split():
        return True
    
    return False


def is_title_match(job_title: str, target_title: str) -> bool:
    """Check if job title matches target title"""
    if not job_title or not target_title:
        return False
    
    job_title_lower = job_title.lower()
    target_title_lower = target_title.lower()
    
    # Check if all words in target title are in job title
    target_words = target_title_lower.split()
    return all(word in job_title_lower for word in target_words)


def extract_detailed_job_info(driver, job: Job) -> Dict[str, Any]:
    """Extract detailed information from a job posting"""
    job_data = {
        'job_title': job.job_title,
        'company': job.company,
        'location': job.location,
        'linkedin_url': job.linkedin_url,
        'posted_date': '',
        'applicant_count': '',
        'job_description': '',
        'employment_type': '',
        'experience_level': '',
        'industries': '',
        'scraped_at': datetime.now().isoformat()
    }
    
    try:
        # Navigate to job details page
        if job.linkedin_url:
            driver.get(job.linkedin_url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Extract additional details
            try:
                # Posted date
                posted_element = driver.find_element(By.CSS_SELECTOR, ".posted-time-ago__text, .job-posted-date")
                job_data['posted_date'] = posted_element.text.strip()
            except NoSuchElementException:
                pass
            
            try:
                # Applicant count
                applicant_element = driver.find_element(By.CSS_SELECTOR, ".num-applicants__caption")
                job_data['applicant_count'] = applicant_element.text.strip()
            except NoSuchElementException:
                pass
            
            try:
                # Job description
                description_element = driver.find_element(By.CSS_SELECTOR, ".show-more-less-html__markup, .jobs-description__content")
                job_data['job_description'] = description_element.text.strip()[:1000]  # Limit to 1000 chars
            except NoSuchElementException:
                pass
            
            try:
                # Employment type and experience level
                criteria_elements = driver.find_elements(By.CSS_SELECTOR, ".description__job-criteria-text")
                for element in criteria_elements:
                    text = element.text.strip().lower()
                    if 'full-time' in text or 'part-time' in text or 'contract' in text:
                        job_data['employment_type'] = element.text.strip()
                    elif 'entry level' in text or 'mid-senior' in text or 'director' in text:
                        job_data['experience_level'] = element.text.strip()
            except NoSuchElementException:
                pass
                
    except Exception as e:
        print(f"⚠️ Error extracting detailed info for {job.job_title}: {e}")
    
    return job_data


def search_company_jobs(company_name: str, job_title: str, max_results: int = 50, detailed_scraping: bool = True) -> List[Dict[str, Any]]:
    """Search for jobs from a specific company with a specific title"""
    print(f"\n🔍 Searching for '{job_title}' positions at '{company_name}'...")
    
    # Get LinkedIn credentials
    email = os.getenv('LINKEDIN_EMAIL', 'thecuriositycabinet98@gmail.com')
    password = os.getenv('LINKEDIN_PASSWORD', 'class7arox')
    
    if not email or not password:
        raise ValueError("Please set LINKEDIN_EMAIL and LINKEDIN_PASSWORD environment variables")
    
    driver = None
    matching_jobs = []
    
    try:
        # Setup driver
        driver = setup_driver()
        
        # Login to LinkedIn
        print("🔐 Logging into LinkedIn...")
        actions.login(driver, email, password)
        print("✅ Successfully logged into LinkedIn")
        
        # Initialize JobSearch
        job_search = JobSearch(driver=driver, scrape=False)
        
        # Search with combined query
        search_queries = [
            f"{job_title} {company_name}",
            f"{job_title}",
            f"{company_name} {job_title}"
        ]
        
        all_jobs = []
        seen_urls = set()
        
        for query in search_queries:
            print(f"🔍 Searching with query: '{query}'")
            try:
                jobs = job_search.search(query)
                for job in jobs:
                    if job.linkedin_url and job.linkedin_url not in seen_urls:
                        all_jobs.append(job)
                        seen_urls.add(job.linkedin_url)
                print(f"📋 Found {len(jobs)} jobs for query '{query}'")
            except Exception as e:
                print(f"⚠️ Error searching with query '{query}': {e}")
                continue
        
        print(f"📊 Total unique jobs found: {len(all_jobs)}")
        
        # Filter jobs by company and title
        print(f"🔍 Filtering jobs for company '{company_name}' and title '{job_title}'...")
        
        for i, job in enumerate(all_jobs[:max_results]):
            if not job.company or not job.job_title:
                continue
                
            # Check if company matches
            if is_company_match(job.company, company_name):
                # Check if title matches
                if is_title_match(job.job_title, job_title):
                    print(f"✅ Match found: {job.job_title} at {job.company}")
                    
                    if detailed_scraping:
                        job_data = extract_detailed_job_info(driver, job)
                    else:
                        job_data = {
                            'job_title': job.job_title,
                            'company': job.company,
                            'location': job.location,
                            'linkedin_url': job.linkedin_url,
                            'scraped_at': datetime.now().isoformat()
                        }
                    
                    matching_jobs.append(job_data)
                    
                    if len(matching_jobs) >= max_results:
                        break
        
        print(f"🎯 Found {len(matching_jobs)} matching jobs")
        
    except Exception as e:
        print(f"❌ Error during job search: {e}")
        
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass
    
    return matching_jobs


def save_results(jobs: List[Dict[str, Any]], output_file: str, company_name: str, job_title: str):
    """Save job results to JSON file"""
    results = {
        'search_criteria': {
            'company': company_name,
            'job_title': job_title,
            'searched_at': datetime.now().isoformat()
        },
        'total_jobs_found': len(jobs),
        'jobs': jobs
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Results saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(description='Search LinkedIn jobs from a specific company with a specific title')
    parser.add_argument('company', help='Company name to search for')
    parser.add_argument('job_title', help='Job title to search for')
    parser.add_argument('--max-results', type=int, default=50, help='Maximum number of results to return (default: 50)')
    parser.add_argument('--output', default=None, help='Output JSON file (default: auto-generated filename)')
    parser.add_argument('--quick', action='store_true', help='Quick mode - skip detailed job scraping')
    
    args = parser.parse_args()
    
    # Generate output filename if not provided
    if not args.output:
        safe_company = args.company.replace(' ', '_').replace('/', '_')
        safe_title = args.job_title.replace(' ', '_').replace('/', '_')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        args.output = f"jobs_{safe_company}_{safe_title}_{timestamp}.json"
    
    print("="*60)
    print("LINKEDIN COMPANY JOB SCRAPER")
    print("="*60)
    print(f"Company: {args.company}")
    print(f"Job Title: {args.job_title}")
    print(f"Max Results: {args.max_results}")
    print(f"Output File: {args.output}")
    print(f"Detailed Scraping: {'No' if args.quick else 'Yes'}")
    
    try:
        # Search for jobs
        jobs = search_company_jobs(
            company_name=args.company,
            job_title=args.job_title,
            max_results=args.max_results,
            detailed_scraping=not args.quick
        )
        
        if jobs:
            # Save results
            save_results(jobs, args.output, args.company, args.job_title)
            
            # Print summary
            print("\n" + "="*60)
            print("SEARCH SUMMARY")
            print("="*60)
            for i, job in enumerate(jobs[:5], 1):  # Show first 5 jobs
                print(f"{i}. {job['job_title']} at {job['company']}")
                print(f"   Location: {job['location']}")
                print(f"   URL: {job['linkedin_url']}")
                print()
            
            if len(jobs) > 5:
                print(f"... and {len(jobs) - 5} more jobs")
            
            print(f"✅ Successfully found {len(jobs)} matching jobs!")
        else:
            print("❌ No matching jobs found. Try adjusting your search criteria.")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()