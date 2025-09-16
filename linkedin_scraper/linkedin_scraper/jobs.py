from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import urllib.parse

from .objects import Scraper
from . import constants as c
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Job(Scraper):

    def __init__(
        self,
        linkedin_url=None,
        job_title=None,
        company=None,
        company_linkedin_url=None,
        location=None,
        posted_date=None,
        applicant_count=None,
        job_description=None,
        benefits=None,
        driver=None,
        close_on_complete=True,
        scrape=True,
    ):
        super().__init__()
        self.linkedin_url = linkedin_url
        self.job_title = job_title
        self.driver = driver
        self.company = company
        self.company_linkedin_url = company_linkedin_url
        self.location = location
        self.posted_date = posted_date
        self.applicant_count = applicant_count
        self.job_description = job_description
        self.benefits = benefits

        if scrape:
            self.scrape(close_on_complete)

    def __repr__(self):
        return f"<Job {self.job_title} {self.company}>"

    def scrape(self, close_on_complete=True):
        if self.is_signed_in():
            self.scrape_logged_in(close_on_complete=close_on_complete)
        else:
            raise NotImplemented("This part is not implemented yet")

    def to_dict(self):
        return {
            "linkedin_url": self.linkedin_url,
            "job_title": self.job_title,
            "company": self.company,
            "company_linkedin_url": self.company_linkedin_url,
            "location": self.location,
            "posted_date": self.posted_date,
            "applicant_count": self.applicant_count,
            "job_description": self.job_description,
            "benefits": self.benefits
        }


    def scrape_logged_in(self, close_on_complete=True):
        driver = self.driver
        
        driver.get(self.linkedin_url)
        self.focus()
        self.job_title = self.wait_for_element_to_load(name="job-details-jobs-unified-top-card__job-title").text.strip()
        self.company = self.wait_for_element_to_load(name="job-details-jobs-unified-top-card__company-name").text.strip()
        self.company_linkedin_url = self.wait_for_element_to_load(name="job-details-jobs-unified-top-card__company-name").find_element(By.TAG_NAME,"a").get_attribute("href")
        primary_descriptions = self.wait_for_element_to_load(name="job-details-jobs-unified-top-card__primary-description-container").find_elements(By.TAG_NAME, "span")
        texts = [span.text for span in primary_descriptions if span.text.strip() != ""]
        self.location = texts[0]
        self.posted_date = texts[3]
        
        try:
            self.applicant_count = self.wait_for_element_to_load(name="jobs-unified-top-card__applicant-count").text.strip()
        except TimeoutException:
            self.applicant_count = 0
        job_description_elem = self.wait_for_element_to_load(name="jobs-description")
        self.mouse_click(job_description_elem.find_element(By.TAG_NAME, "button"))
        job_description_elem = self.wait_for_element_to_load(name="jobs-description")
        job_description_elem.find_element(By.TAG_NAME, "button").click()
        self.job_description = job_description_elem.text.strip()
        try:
            self.benefits = self.wait_for_element_to_load(name="jobs-unified-description__salary-main-rail-card").text.strip()
        except TimeoutException:
            self.benefits = None

        if close_on_complete:
            driver.close()
    
    @staticmethod
    def get_company_jobs(driver, job_title="security engineer", company_name=None, max_jobs=25):
        """
        Search for jobs with specific title and optionally filter by company on LinkedIn
        
        Args:
            driver: Selenium WebDriver instance (must be logged in)
            job_title: Job title to search for (default: "security engineer")
            company_name: Name of the company to filter by (optional)
            max_jobs: Maximum number of jobs to retrieve (default: 25)
            
        Returns:
            List of Job objects
        """
        jobs = []
        
        try:
            print(f"Searching for '{job_title}' jobs" + (f" at {company_name}" if company_name else "") + "...")
            
            # Navigate to LinkedIn jobs page first
            driver.get("https://www.linkedin.com/jobs/")
            time.sleep(3)
            
            # Find and fill the search box with job title
            try:
                search_box = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[aria-label*='Search by title, skill, or company']"))
                )
                search_box.clear()
                search_box.send_keys(job_title)
                
                # Click search button or press enter
                search_button = driver.find_element(By.CSS_SELECTOR, "button[aria-label*='Search']") 
                search_button.click()
                
            except (TimeoutException, NoSuchElementException):
                # Fallback: construct search URL directly
                encoded_title = urllib.parse.quote(job_title)
                search_url = f"https://www.linkedin.com/jobs/search/?keywords={encoded_title}&location=Worldwide"
                driver.get(search_url)
            
            time.sleep(5)
            
            # If company name is provided, apply company filter
            if company_name:
                try:
                    print(f"Applying company filter for {company_name}...")
                    
                    # Click on "All filters" button
                    all_filters_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'All filters') or contains(text(), 'Show all filters')]"))
                    )
                    all_filters_button.click()
                    time.sleep(2)
                    
                    # Find and click on Company input field
                    company_input = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Add a company' or @aria-label='Add a company']"))
                    )
                    company_input.clear()
                    company_input.send_keys(company_name)
                    time.sleep(2)
                    
                    # Select the company from dropdown
                    try:
                        company_option = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, f"//div[contains(@class, 'basic-typeahead__triggered-content')]//span[contains(text(), '{company_name}')]"))
                        )
                        company_option.click()
                        time.sleep(1)
                    except Exception:
                        # Try alternative selector
                        try:
                            company_option = WebDriverWait(driver, 5).until(
                                EC.element_to_be_clickable((By.XPATH, f"//li[contains(@class, 'typeahead-result')]//span[contains(text(), '{company_name}')]"))
                            )
                            company_option.click()
                            time.sleep(1)
                        except Exception:
                            print(f"Could not select company {company_name} from dropdown")
                    
                    # Click "Show results" or "Apply" button
                    try:
                        apply_button = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Show results') or contains(text(), 'Apply')]"))
                        )
                        apply_button.click()
                        time.sleep(3)
                    except Exception:
                        print("Could not find apply button, continuing...")
                        
                except Exception as e:
                    print(f"Error applying company filter: {e}")
                    print("Continuing with general search...")
            
            # Wait for job results to load
            try:
                WebDriverWait(driver, 15).until(
                    EC.any_of(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".jobs-search__results-list")),
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".jobs-search-results__list")),
                        EC.presence_of_element_located((By.CSS_SELECTOR, "[data-job-id]")),
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".job-card-container"))
                    )
                )
            except TimeoutException:
                print(f"No jobs found for company: {company_name}")
                return jobs
            
            # Scroll to load more jobs
            last_height = driver.execute_script("return document.body.scrollHeight")
            jobs_collected = 0
            
            while jobs_collected < max_jobs:
                # Scroll down
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                # Check if new content loaded
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
                
                # Get current job count
                job_cards = driver.find_elements(By.CSS_SELECTOR, ".jobs-search-results__list-item")
                jobs_collected = len(job_cards)
            
            # Extract job information using the correct LinkedIn selector
            job_cards = driver.find_elements(By.CSS_SELECTOR, ".jobs-search__results-list li")
            
            if not job_cards:
                print("No job cards found")
                return jobs
            
            print(f"Found {len(job_cards)} job cards")
            
            for i, card in enumerate(job_cards[:max_jobs]):
                try:
                    # Try to click on job card to load details
                    try:
                        driver.execute_script("arguments[0].scrollIntoView(true);", card)
                        time.sleep(0.5)
                        card.click()
                        time.sleep(1)
                    except Exception:
                        pass  # Continue even if click fails
                    
                    # Extract job URL from the base card link
                    job_url = None
                    try:
                        job_link = card.find_element(By.CSS_SELECTOR, "a.base-card__full-link")
                        job_url = job_link.get_attribute("href")
                    except NoSuchElementException:
                        # Try alternative selectors
                        url_selectors = [
                            "a[href*='/jobs/view/']",
                            ".base-search-card a",
                            "a[data-tracking-id]"
                        ]
                        
                        for url_selector in url_selectors:
                            try:
                                job_link = card.find_element(By.CSS_SELECTOR, url_selector)
                                job_url = job_link.get_attribute("href")
                                if job_url and '/jobs/view/' in job_url:
                                    break
                            except NoSuchElementException:
                                continue
                    
                    if not job_url:
                        print(f"Could not find job URL for job {i+1}")
                        continue
                    
                    # Create Job object with minimal info first
                    job = Job(
                        linkedin_url=job_url,
                        driver=driver,
                        scrape=False,
                        close_on_complete=False
                    )
                    
                    # Extract basic info from search results using LinkedIn's structure
                    # Job Title - LinkedIn uses h3 with specific classes
                    job.job_title = "Unknown Title"
                    try:
                        title_elem = card.find_element(By.CSS_SELECTOR, "h3.base-search-card__title a span[title]")
                        job.job_title = title_elem.get_attribute("title").strip()
                    except NoSuchElementException:
                        try:
                            title_elem = card.find_element(By.CSS_SELECTOR, "h3.base-search-card__title a")
                            job.job_title = title_elem.text.strip()
                        except NoSuchElementException:
                            try:
                                title_elem = card.find_element(By.CSS_SELECTOR, "h3 a span")
                                job.job_title = title_elem.text.strip()
                            except NoSuchElementException:
                                pass
                    
                    # Company Name - LinkedIn uses h4 with specific classes
                    job.company = company_name if company_name else "Unknown Company"
                    try:
                        company_elem = card.find_element(By.CSS_SELECTOR, "h4.base-search-card__subtitle a")
                        company_text = company_elem.text.strip()
                        if company_text:
                            job.company = company_text
                    except NoSuchElementException:
                        try:
                            company_elem = card.find_element(By.CSS_SELECTOR, "h4 a")
                            company_text = company_elem.text.strip()
                            if company_text:
                                job.company = company_text
                        except NoSuchElementException:
                            pass
                    
                    # Location - LinkedIn uses specific metadata classes
                    job.location = "Unknown Location"
                    try:
                        location_elem = card.find_element(By.CSS_SELECTOR, ".job-search-card__location")
                        location_text = location_elem.text.strip()
                        if location_text:
                            job.location = location_text
                    except NoSuchElementException:
                        try:
                            # Try alternative location selector
                            location_elem = card.find_element(By.CSS_SELECTOR, ".base-search-card__metadata span")
                            location_text = location_elem.text.strip()
                            if location_text:
                                job.location = location_text
                        except NoSuchElementException:
                            pass
                    
                    jobs.append(job)
                    print(f"Found job {i+1}: {job.job_title} at {job.company} ({job.location})")
                    
                except Exception as e:
                    print(f"Error extracting job {i+1}: {e}")
                    continue
            
            print(f"Successfully found {len(jobs)} jobs for '{job_title}'" + (f" at {company_name}" if company_name else ""))
            
        except Exception as e:
            print(f"Error searching for company jobs: {e}")
        
        return jobs
    
    @staticmethod
    def scrape_company_jobs_detailed(driver, job_title="security engineer", company_name=None, max_jobs=25):
        """
        Get detailed information for jobs with specific title and optionally filter by company
        
        Args:
            driver: Selenium WebDriver instance (must be logged in)
            job_title: Job title to search for (default: "security engineer")
            company_name: Name of the company to filter by (optional)
            max_jobs: Maximum number of jobs to retrieve and scrape in detail
            
        Returns:
            List of fully scraped Job objects with detailed information
        """
        # First get basic job list
        jobs = Job.get_company_jobs(driver, job_title, company_name, max_jobs)
        
        # Then scrape each job in detail
        detailed_jobs = []
        for i, job in enumerate(jobs):
            try:
                print(f"Scraping detailed info for job {i+1}/{len(jobs)}: {job.job_title}")
                job.scrape_logged_in(close_on_complete=False)
                detailed_jobs.append(job)
                time.sleep(2)  # Be respectful to LinkedIn's servers
            except Exception as e:
                print(f"Error scraping detailed info for job {i+1}: {e}")
                # Still add the job with basic info
                detailed_jobs.append(job)
                continue
        
        return detailed_jobs
