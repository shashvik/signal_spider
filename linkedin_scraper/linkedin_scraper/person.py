import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from .objects import Experience, Education, Scraper, Interest, Accomplishment, Contact, Post, Comment
import os
from datetime import datetime, timedelta
import re
from linkedin_scraper import selectors


class Person(Scraper):

    __TOP_CARD = "main"
    __WAIT_FOR_ELEMENT_TIMEOUT = 5

    def __init__(
        self,
        linkedin_url=None,
        name=None,
        about=None,
        experiences=None,
        educations=None,
        interests=None,
        accomplishments=None,
        company=None,
        job_title=None,
        contacts=None,
        driver=None,
        get=True,
        scrape=True,
        close_on_complete=True,
        time_to_wait_after_login=0,
    ):
        self.linkedin_url = linkedin_url
        self.name = name
        self.about = about or []
        self.experiences = experiences or []
        self.educations = educations or []
        self.interests = interests or []
        self.accomplishments = accomplishments or []
        self.also_viewed_urls = []
        self.contacts = contacts or []
        self.posts = []
        self.comments = []

        if driver is None:
            try:
                if os.getenv("CHROMEDRIVER") == None:
                    driver_path = os.path.join(
                        os.path.dirname(__file__), "drivers/chromedriver"
                    )
                else:
                    driver_path = os.getenv("CHROMEDRIVER")

                driver = webdriver.Chrome(driver_path)
            except:
                driver = webdriver.Chrome()

        if get:
            driver.get(linkedin_url)

        self.driver = driver

        if scrape:
            self.scrape(close_on_complete)

    def add_about(self, about):
        self.about.append(about)

    def add_experience(self, experience):
        self.experiences.append(experience)

    def add_education(self, education):
        self.educations.append(education)

    def add_interest(self, interest):
        self.interests.append(interest)

    def add_accomplishment(self, accomplishment):
        self.accomplishments.append(accomplishment)

    def add_location(self, location):
        self.location = location

    def add_contact(self, contact):
        self.contacts.append(contact)

    def add_post(self, post):
        self.posts.append(post)

    def add_comment(self, comment):
        self.comments.append(comment)

    def scrape(self, close_on_complete=True):
        if self.is_signed_in():
            self.scrape_logged_in(close_on_complete=close_on_complete)
        else:
            print("you are not logged in!")

    def _click_see_more_by_class_name(self, class_name):
        try:
            _ = WebDriverWait(self.driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located((By.CLASS_NAME, class_name))
            )
            div = self.driver.find_element(By.CLASS_NAME, class_name)
            div.find_element(By.TAG_NAME, "button").click()
        except Exception as e:
            pass

    def is_open_to_work(self):
        try:
            return "#OPEN_TO_WORK" in self.driver.find_element(By.CLASS_NAME,"pv-top-card-profile-picture").find_element(By.TAG_NAME,"img").get_attribute("title")
        except:
            return False

    def get_experiences(self):
        url = os.path.join(self.linkedin_url, "details/experience")
        self.driver.get(url)
        self.focus()
        main = self.wait_for_element_to_load(by=By.TAG_NAME, name="main")
        self.scroll_to_half()
        self.scroll_to_bottom()
        
        # Try to click "Show more" buttons to expand descriptions
        try:
            show_more_buttons = self.driver.find_elements(By.XPATH, "//button[contains(@aria-label, 'Show more') or contains(text(), 'Show more') or contains(@aria-label, 'see more') or contains(text(), 'see more')]")
            for button in show_more_buttons:
                try:
                    self.driver.execute_script("arguments[0].click();", button)
                    self.wait(1)  # Wait a bit for content to load
                except:
                    continue
        except:
            pass
            
        main_list = self.wait_for_element_to_load(name="pvs-list__container", base=main)
        for position in main_list.find_elements(By.CLASS_NAME, "pvs-list__paged-list-item"):
            position = position.find_element(By.CSS_SELECTOR, "div[data-view-name='profile-component-entity']")
            
            # Fix: Handle case where more than 2 elements are returned
            elements = position.find_elements(By.XPATH, "*")
            if len(elements) < 2:
                continue  # Skip if we don't have enough elements
                
            company_logo_elem = elements[0]
            position_details = elements[1]

            # company elem
            try:
                company_linkedin_url = company_logo_elem.find_element(By.XPATH,"*").get_attribute("href")
                if not company_linkedin_url:
                    continue
            except NoSuchElementException:
                continue

            # position details
            position_details_list = position_details.find_elements(By.XPATH,"*")
            position_summary_details = position_details_list[0] if len(position_details_list) > 0 else None
            position_summary_text = position_details_list[1] if len(position_details_list) > 1 else None
            
            if not position_summary_details:
                continue
                
            outer_positions = position_summary_details.find_element(By.XPATH,"*").find_elements(By.XPATH,"*")

            if len(outer_positions) == 4:
                position_title = outer_positions[0].find_element(By.TAG_NAME,"span").text
                company = outer_positions[1].find_element(By.TAG_NAME,"span").text
                work_times = outer_positions[2].find_element(By.TAG_NAME,"span").text
                location = outer_positions[3].find_element(By.TAG_NAME,"span").text
            elif len(outer_positions) == 3:
                if "·" in outer_positions[2].text:
                    position_title = outer_positions[0].find_element(By.TAG_NAME,"span").text
                    company = outer_positions[1].find_element(By.TAG_NAME,"span").text
                    work_times = outer_positions[2].find_element(By.TAG_NAME,"span").text
                    location = ""
                else:
                    position_title = ""
                    company = outer_positions[0].find_element(By.TAG_NAME,"span").text
                    work_times = outer_positions[1].find_element(By.TAG_NAME,"span").text
                    location = outer_positions[2].find_element(By.TAG_NAME,"span").text
            else:
                position_title = ""
                company = outer_positions[0].find_element(By.TAG_NAME,"span").text if outer_positions else ""
                work_times = outer_positions[1].find_element(By.TAG_NAME,"span").text if len(outer_positions) > 1 else ""
                location = ""

            # Safely extract times and duration
            if work_times:
                parts = work_times.split("·")
                times = parts[0].strip() if parts else ""
                duration = parts[1].strip() if len(parts) > 1 else None
            else:
                times = ""
                duration = None

            from_date = " ".join(times.split(" ")[:2]) if times else ""
            to_date = " ".join(times.split(" ")[3:]) if times and len(times.split(" ")) > 3 else ""
            
            if position_summary_text and any(element.get_attribute("class") == "pvs-list__container" for element in position_summary_text.find_elements(By.XPATH, "*")):
                try:
                    inner_positions = (position_summary_text.find_element(By.CLASS_NAME,"pvs-list__container")
                                    .find_element(By.XPATH,"*").find_element(By.XPATH,"*").find_element(By.XPATH,"*")
                                    .find_elements(By.CLASS_NAME,"pvs-list__paged-list-item"))
                except NoSuchElementException:
                    inner_positions = []
            else:
                inner_positions = []
            
            if len(inner_positions) > 1:
                descriptions = inner_positions
                for desc_element in descriptions:
                    try:
                        res = desc_element.find_element(By.TAG_NAME,"a").find_elements(By.XPATH,"*")
                        position_title_elem = res[0] if len(res) > 0 else None
                        work_times_elem = res[1] if len(res) > 1 else None
                        location_elem = res[2] if len(res) > 2 else None

                        location = location_elem.find_element(By.XPATH,"*").text if location_elem else None
                        position_title = position_title_elem.find_element(By.XPATH,"*").find_element(By.TAG_NAME,"*").text if position_title_elem else ""
                        work_times = work_times_elem.find_element(By.XPATH,"*").text if work_times_elem else ""
                        
                        # Extract description text from the element
                        try:
                            description_text = desc_element.text or ""
                        except:
                            description_text = ""
                        
                        # Safely extract times and duration
                        if work_times:
                            parts = work_times.split("·")
                            times = parts[0].strip() if parts else ""
                            duration = parts[1].strip() if len(parts) > 1 else None
                        else:
                            times = ""
                            duration = None
                            
                        from_date = " ".join(times.split(" ")[:2]) if times else ""
                        to_date = " ".join(times.split(" ")[3:]) if times and len(times.split(" ")) > 3 else ""

                        experience = Experience(
                            position_title=position_title,
                            from_date=from_date,
                            to_date=to_date,
                            duration=duration,
                            location=location,
                            description=description_text,
                            institution_name=company,
                            linkedin_url=company_linkedin_url
                        )
                        self.add_experience(experience)
                    except (NoSuchElementException, IndexError) as e:
                        # Skip this description if elements are missing
                        continue
            else:
                description = position_summary_text.text if position_summary_text else ""

                experience = Experience(
                    position_title=position_title,
                    from_date=from_date,
                    to_date=to_date,
                    duration=duration,
                    location=location,
                    description=description,
                    institution_name=company,
                    linkedin_url=company_linkedin_url
                )
                self.add_experience(experience)

    def get_educations(self):
        url = os.path.join(self.linkedin_url, "details/education")
        self.driver.get(url)
        self.focus()
        main = self.wait_for_element_to_load(by=By.TAG_NAME, name="main")
        self.scroll_to_half()
        self.scroll_to_bottom()
        main_list = self.wait_for_element_to_load(name="pvs-list__container", base=main)
        for position in main_list.find_elements(By.CLASS_NAME,"pvs-list__paged-list-item"):
            try:
                position = position.find_element(By.CSS_SELECTOR, "div[data-view-name='profile-component-entity']")
                
                # Fix: Handle case where more than 2 elements are returned
                elements = position.find_elements(By.XPATH,"*")
                if len(elements) < 2:
                    continue  # Skip if we don't have enough elements
                    
                institution_logo_elem = elements[0]
                position_details = elements[1]

                # institution elem
                try:
                    institution_linkedin_url = institution_logo_elem.find_element(By.XPATH,"*").get_attribute("href")
                except NoSuchElementException:
                    institution_linkedin_url = None

                # position details
                position_details_list = position_details.find_elements(By.XPATH,"*")
                position_summary_details = position_details_list[0] if len(position_details_list) > 0 else None
                position_summary_text = position_details_list[1] if len(position_details_list) > 1 else None
                
                if not position_summary_details:
                    continue
                    
                outer_positions = position_summary_details.find_element(By.XPATH,"*").find_elements(By.XPATH,"*")

                institution_name = outer_positions[0].find_element(By.TAG_NAME,"span").text if outer_positions else ""
                degree = outer_positions[1].find_element(By.TAG_NAME,"span").text if len(outer_positions) > 1 else None

                from_date = None
                to_date = None
                
                if len(outer_positions) > 2:
                    try:
                        times = outer_positions[2].find_element(By.TAG_NAME,"span").text

                        if times and "-" in times:
                            split_times = times.split(" ")
                            dash_index = split_times.index("-") if "-" in split_times else -1
                            
                            if dash_index > 0:
                                from_date = split_times[dash_index-1]
                            if dash_index < len(split_times) - 1:
                                to_date = split_times[-1]
                    except (NoSuchElementException, ValueError):
                        from_date = None
                        to_date = None

                description = position_summary_text.text if position_summary_text else ""

                education = Education(
                    from_date=from_date,
                    to_date=to_date,
                    description=description,
                    degree=degree,
                    institution_name=institution_name,
                    linkedin_url=institution_linkedin_url
                )
                self.add_education(education)
            except (NoSuchElementException, IndexError) as e:
                # Skip this education entry if elements are missing
                continue

    def get_name_and_location(self):
        top_panel = self.driver.find_element(By.XPATH, "//*[@class='mt2 relative']")
        self.name = top_panel.find_element(By.TAG_NAME, "h1").text
        self.location = top_panel.find_element(By.XPATH, "//*[@class='text-body-small inline t-black--light break-words']").text

    def get_about(self):
        try:
            about = self.driver.find_element(By.ID,"about").find_element(By.XPATH,"..").find_element(By.CLASS_NAME,"display-flex").text
        except NoSuchElementException :
            about=None
        self.about = about

    def get_posts(self, hours_limit=24):
        """Scrape posts from the last specified hours (default 24 hours)"""
        # Navigate to the person's activity page
        activity_url = os.path.join(self.linkedin_url, "recent-activity/all/")
        self.driver.get(activity_url)
        self.focus()
        
        # Wait for the page to load
        self.wait(3)
        
        # Scroll to load more posts
        self.scroll_to_half()
        self.scroll_to_bottom()
        
        # Calculate the cutoff time
        cutoff_time = datetime.now() - timedelta(hours=hours_limit)
        
        try:
            # Find all post containers
            posts_container = self.wait_for_element_to_load(by=By.TAG_NAME, name="main")
            
            # Look for posts in the activity feed
            post_elements = posts_container.find_elements(By.CSS_SELECTOR, "[data-urn*='urn:li:activity']")
            
            if not post_elements:
                # Try alternative selector for posts
                post_elements = posts_container.find_elements(By.CSS_SELECTOR, ".feed-shared-update-v2")
            
            for post_element in post_elements:
                try:
                    # Extract post data
                    post_data = self._extract_post_data(post_element)
                    
                    if post_data and self._is_within_time_limit(post_data['posted_date'], cutoff_time):
                        post = Post(
                            content=post_data['content'],
                            posted_date=post_data['posted_date'],
                            likes_count=post_data['likes_count'],
                            comments_count=post_data['comments_count'],
                            shares_count=post_data['shares_count'],
                            post_url=post_data['post_url'],
                            media_type=post_data['media_type'],
                            author_name=post_data['author_name'],
                            author_url=post_data['author_url']
                        )
                        self.add_post(post)
                    elif post_data and not self._is_within_time_limit(post_data['posted_date'], cutoff_time):
                        # If we've reached posts older than our limit, stop processing
                        break
                        
                except Exception as e:
                    print(f"Error processing post: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error scraping posts: {e}")
            
    def _extract_post_data(self, post_element):
        """Extract data from a single post element"""
        try:
            post_data = {
                'content': '',
                'posted_date': '',
                'likes_count': 0,
                'comments_count': 0,
                'shares_count': 0,
                'post_url': '',
                'media_type': 'text',
                'author_name': '',
                'author_url': ''
            }
            
            # Extract post content
            try:
                content_element = post_element.find_element(By.CSS_SELECTOR, ".feed-shared-text, .feed-shared-update-v2__description")
                post_data['content'] = content_element.text.strip()
            except:
                pass
            
            # Extract posted date
            try:
                time_element = post_element.find_element(By.CSS_SELECTOR, "time, .feed-shared-actor__sub-description time")
                post_data['posted_date'] = time_element.get_attribute('datetime') or time_element.text
            except:
                pass
            
            # Extract engagement metrics
            try:
                # Likes count
                likes_element = post_element.find_element(By.CSS_SELECTOR, "[aria-label*='reaction'], .social-counts-reactions__count")
                likes_text = likes_element.text or likes_element.get_attribute('aria-label')
                post_data['likes_count'] = self._extract_number_from_text(likes_text)
            except:
                pass
                
            try:
                # Comments count
                comments_element = post_element.find_element(By.CSS_SELECTOR, "[aria-label*='comment'], .social-counts-comments")
                comments_text = comments_element.text or comments_element.get_attribute('aria-label')
                post_data['comments_count'] = self._extract_number_from_text(comments_text)
            except:
                pass
                
            try:
                # Shares count
                shares_element = post_element.find_element(By.CSS_SELECTOR, "[aria-label*='repost'], .social-counts-reposts")
                shares_text = shares_element.text or shares_element.get_attribute('aria-label')
                post_data['shares_count'] = self._extract_number_from_text(shares_text)
            except:
                pass
            
            # Extract post URL
            try:
                post_link = post_element.find_element(By.CSS_SELECTOR, "a[href*='/posts/'], a[href*='/activity/']")
                post_data['post_url'] = post_link.get_attribute('href')
            except:
                pass
            
            # Determine media type
            if post_element.find_elements(By.CSS_SELECTOR, "img, .feed-shared-image"):
                post_data['media_type'] = 'image'
            elif post_element.find_elements(By.CSS_SELECTOR, "video, .feed-shared-video"):
                post_data['media_type'] = 'video'
            elif post_element.find_elements(By.CSS_SELECTOR, ".feed-shared-document"):
                post_data['media_type'] = 'document'
            
            # Extract author information
            try:
                author_element = post_element.find_element(By.CSS_SELECTOR, ".feed-shared-actor__name, .feed-shared-actor__title")
                post_data['author_name'] = author_element.text.strip()
                author_link = post_element.find_element(By.CSS_SELECTOR, ".feed-shared-actor__container-link")
                post_data['author_url'] = author_link.get_attribute('href')
            except:
                post_data['author_name'] = self.name or 'Unknown'
                post_data['author_url'] = self.linkedin_url
            
            return post_data
            
        except Exception as e:
            print(f"Error extracting post data: {e}")
            return None
    
    def _extract_number_from_text(self, text):
        """Extract number from text like '5 reactions' or '12 comments'"""
        if not text:
            return 0
        
        # Look for numbers in the text
        numbers = re.findall(r'\d+', text.replace(',', ''))
        if numbers:
            return int(numbers[0])
        return 0
    
    def _is_within_time_limit(self, posted_date, cutoff_time):
        """Check if the post is within the specified time limit"""
        if not posted_date:
            return True  # If we can't determine the date, include it
        
        try:
            # Handle different date formats
            if 'ago' in posted_date.lower():
                return self._parse_relative_date(posted_date, cutoff_time)
            else:
                # Try to parse absolute date
                post_time = datetime.fromisoformat(posted_date.replace('Z', '+00:00'))
                return post_time >= cutoff_time
        except:
            return True  # If parsing fails, include the post
    
    def _parse_relative_date(self, date_text, cutoff_time):
        """Parse relative dates like '2h ago', '1d ago'"""
        try:
            date_text = date_text.lower()
            now = datetime.now()
            
            if 'minute' in date_text or 'm ago' in date_text:
                minutes = int(re.findall(r'\d+', date_text)[0])
                post_time = now - timedelta(minutes=minutes)
            elif 'hour' in date_text or 'h ago' in date_text:
                hours = int(re.findall(r'\d+', date_text)[0])
                post_time = now - timedelta(hours=hours)
            elif 'day' in date_text or 'd ago' in date_text:
                days = int(re.findall(r'\d+', date_text)[0])
                post_time = now - timedelta(days=days)
            elif 'week' in date_text or 'w ago' in date_text:
                weeks = int(re.findall(r'\d+', date_text)[0])
                post_time = now - timedelta(weeks=weeks)
            else:
                return True  # Unknown format, include it
            
            return post_time >= cutoff_time
        except:
            return True  # If parsing fails, include the post

    def get_comments(self, hours_limit=24, comment_limit=None):
        """
        Scrape comments made by this person on posts.
        
        Args:
            hours_limit (int): Number of hours to look back for comments (default: 24)
            comment_limit (int): Maximum number of latest comments to get (overrides hours_limit if set)
        """
        try:
            # Navigate to the person's activity page
            activity_url = f"{self.linkedin_url.rstrip('/')}/recent-activity/comments/"
            print(f"🌐 Navigating to: {activity_url}")
            self.driver.get(activity_url)
            self.wait(5)  # Increased wait time for page load
            
            # Wait for page to be fully loaded
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "main"))
                )
                print("✅ Page loaded successfully")
            except:
                print("⚠️  Page load timeout, continuing anyway")
            
            # Calculate cutoff time (only used if comment_limit is not set)
            cutoff_time = datetime.now() - timedelta(hours=hours_limit) if not comment_limit else None
            
            # Scroll to load more comments with improved logic
            print("📜 Starting to scroll and load comments...")
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            scroll_attempts = 0
            max_scrolls = 15  # Increased scroll attempts
            
            while scroll_attempts < max_scrolls:
                # Scroll down
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                self.wait(3)  # Increased wait time between scrolls
                
                # Check if new content loaded
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                scroll_attempts += 1
                
                # Check for comments after each scroll
                try:
                    current_comments = self.driver.find_elements(By.CSS_SELECTOR, ".comments-comment-entity")
                    print(f"📊 Scroll {scroll_attempts}: Found {len(current_comments)} comment elements")
                    
                    # Break early if we have enough comments and using comment_limit
                    if comment_limit and len(current_comments) >= comment_limit:
                        print(f"🎯 Found {len(current_comments)} comments, stopping scroll (limit: {comment_limit})")
                        break
                except Exception as e:
                    print(f"⚠️  Error checking comments during scroll: {e}")
                
                # Stop if no new content loaded
                if new_height == last_height:
                    print(f"📄 No new content loaded after scroll {scroll_attempts}")
                    break
                    
                last_height = new_height
            
            # Use the correct LinkedIn comment selectors based on DOM analysis
            comment_selectors = [
                # Actual LinkedIn comment structure (from DOM analysis)
                ".comments-comment-entity",  # Individual comment containers
                "article.comments-comment-entity",  # More specific comment articles
                ".comments-comment-item",  # Alternative comment items
                "[data-id*='comment']",  # Comments with data-id attributes
                # Fallback selectors for different LinkedIn layouts
                ".feed-shared-update-v2 .comments-comment-entity",
                ".comments-comments-list .comments-comment-entity",
                ".comments-comment-list__container .comments-comment-entity"
            ]
            
            comment_elements = []
            for selector in comment_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        print(f"✅ Found {len(elements)} elements with selector: {selector}")
                        
                        # Debug: Show sample element info
                        for i, elem in enumerate(elements[:3]):
                            try:
                                classes = elem.get_attribute('class') or 'no-class'
                                data_urn = elem.get_attribute('data-urn') or 'no-urn'
                                text_preview = (elem.text or 'no-text')[:100].replace('\n', ' ')
                                print(f"  Sample [{i+1}]: class='{classes[:50]}...' urn='{data_urn[:30]}...' text='{text_preview}...'")
                            except Exception as debug_e:
                                print(f"  Sample [{i+1}]: Error getting info - {debug_e}")
                        
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
                    
                    # Save page source for debugging
                    debug_filename = f"scraper_page_source_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
                    with open(debug_filename, 'w', encoding='utf-8') as f:
                        f.write(page_source)
                    print(f"💾 Page source saved to: {debug_filename}")
                    
                    # Analyze page content
                    page_lower = page_source.lower()
                    comment_count = page_lower.count('comment')
                    activity_count = page_lower.count('activity')
                    entity_count = page_lower.count('comments-comment-entity')
                    print(f"📊 Page analysis: {comment_count} 'comment', {activity_count} 'activity', {entity_count} 'comments-comment-entity' occurrences")
                    
                    if "No activity yet" in page_source or "hasn't shared anything" in page_source:
                        print("📝 Profile has no recent activity")
                    elif entity_count > 0:
                        print("📝 Page contains comment entities but selectors failed - timing issue?")
                    elif "comment" in page_lower:
                        print("📝 Page contains 'comment' text but elements not found")
                    else:
                        print("📝 Page loaded but structure unclear")
                except Exception as e:
                    print(f"Error checking page source: {e}")
            
            comments_found = 0
            for comment_element in comment_elements:
                # If using comment_limit, stop when we reach the limit
                if comment_limit and comments_found >= comment_limit:
                    print(f"✅ Reached comment limit of {comment_limit}, stopping processing")
                    break
                    
                try:
                    comment_data = self._extract_comment_data(comment_element)
                    if comment_data:
                        # If using comment_limit, just take the first N comments
                        if comment_limit:
                            comment = Comment(
                                content=comment_data['content'],
                                commented_date=comment_data['commented_date'],
                                likes_count=comment_data['likes_count'],
                                replies_count=comment_data['replies_count'],
                                comment_url=comment_data['comment_url'],
                                post_url=comment_data['post_url'],
                                post_author=comment_data['post_author'],
                                post_content_preview=comment_data['post_content_preview'],
                                commenter_name=comment_data['commenter_name'],
                                commenter_url=comment_data['commenter_url']
                            )
                            self.add_comment(comment)
                            comments_found += 1
                            print(f"📝 Added comment {comments_found}/{comment_limit}")
                        # If using time-based filtering
                        elif self._is_within_time_limit(comment_data['commented_date'], cutoff_time):
                            comment = Comment(
                                content=comment_data['content'],
                                commented_date=comment_data['commented_date'],
                                likes_count=comment_data['likes_count'],
                                replies_count=comment_data['replies_count'],
                                comment_url=comment_data['comment_url'],
                                post_url=comment_data['post_url'],
                                post_author=comment_data['post_author'],
                                post_content_preview=comment_data['post_content_preview'],
                                commenter_name=comment_data['commenter_name'],
                                commenter_url=comment_data['commenter_url']
                            )
                            self.add_comment(comment)
                            comments_found += 1
                        elif not self._is_within_time_limit(comment_data['commented_date'], cutoff_time):
                            # If we hit a comment older than our limit, stop processing
                            print(f"⏰ Reached time limit, stopping at {comments_found} comments")
                            break
                except Exception as e:
                    print(f"⚠️  Error extracting comment data: {e}")
                    continue
            
            if comment_limit:
                print(f"Found {comments_found} latest comments")
            else:
                print(f"Found {comments_found} comments from the last {hours_limit} hours")
            
        except Exception as e:
            print(f"Error scraping comments: {e}")
    
    def _extract_comment_data(self, comment_element):
        """
        Extract data from a comment element.
        
        Args:
            comment_element: Selenium WebElement representing a comment
            
        Returns:
            dict: Comment data or None if extraction fails
        """
        try:
            # Extract comment content using comment-specific selectors
            content = ""
            
            # Use the correct comment content selectors based on DOM analysis
            comment_content_selectors = [
                # Primary comment content selectors (from DOM analysis)
                ".comments-comment-item__main-content",  # Main comment text container
                ".comments-comment-item__main-content .update-components-text",  # Nested text content
                ".feed-shared-main-content--comment",  # Alternative main content
                ".comments-comment-entity__content .update-components-text",  # Content within entity
                ".feed-shared-inline-show-more-text .update-components-text",  # Show more text content
                # Fallback selectors
                ".comments-comment-item-content-body",
                ".comment-item__main-content",
                ".feed-shared-comment__main-content",
                ".comments-comment-item .feed-shared-inline-show-more-text",
                ".activity-item__commentary"
            ]
            
            for selector in comment_content_selectors:
                try:
                    content_element = comment_element.find_element(By.CSS_SELECTOR, selector)
                    content = content_element.text.strip()
                    if content and self._is_valid_comment_content(content):
                        print(f"🔍 Found comment content with selector '{selector}': {content[:100]}...")
                        break
                except:
                    continue
            
            # If no content found with comment selectors, try getting text from the element but filter it
            if not content:
                try:
                    full_text = comment_element.text.strip()
                    if full_text:
                        # Try to extract just the comment part from the full text
                        content = self._extract_comment_from_full_text(full_text)
                        if content and self._is_valid_comment_content(content):
                            print(f"🔍 Extracted comment from element text: {content[:100]}...")
                        else:
                            content = "[Comment content not available]"
                except:
                    content = "[Comment content not available]"
            
            # Extract comment date with multiple fallback selectors
            commented_date = ""
            date_selectors = [
                "time",
                ".feed-shared-actor__sub-description time",
                "[data-test-id='feed-shared-actor__sub-description'] time",
                ".feed-shared-actor__sub-description",
                "[aria-label*='ago']"
            ]
            
            for selector in date_selectors:
                try:
                    date_element = comment_element.find_element(By.CSS_SELECTOR, selector)
                    commented_date = date_element.get_attribute('datetime') or date_element.text.strip()
                    if commented_date:
                        break
                except:
                    continue
            
            # Extract likes count with multiple fallback selectors
            likes_count = 0
            likes_selectors = [
                ".social-counts-reactions__count",
                ".feed-shared-social-action-bar__reaction-count",
                "[aria-label*='reaction']",
                "[aria-label*='like']",
                ".social-action-bar__reaction-count",
                ".feed-shared-social-counts__num-likes"
            ]
            
            for selector in likes_selectors:
                try:
                    likes_element = comment_element.find_element(By.CSS_SELECTOR, selector)
                    likes_text = likes_element.text.strip() or likes_element.get_attribute('aria-label') or "0"
                    likes_count = self._extract_number_from_text(likes_text)
                    break
                except:
                    continue
            
            # Extract replies count with multiple fallback selectors
            replies_count = 0
            replies_selectors = [
                ".feed-shared-social-action-bar__comment-count",
                ".social-counts-comments__count",
                "[aria-label*='comment']",
                "[aria-label*='repl']",
                ".social-action-bar__comment-count",
                ".feed-shared-social-counts__num-comments"
            ]
            
            for selector in replies_selectors:
                try:
                    replies_element = comment_element.find_element(By.CSS_SELECTOR, selector)
                    replies_text = replies_element.text.strip() or replies_element.get_attribute('aria-label') or "0"
                    replies_count = self._extract_number_from_text(replies_text)
                    break
                except:
                    continue
            
            # Extract comment URL
            comment_url = ""
            try:
                permalink_element = comment_element.find_element(By.CSS_SELECTOR, "a[href*='/feed/update/']")
                comment_url = permalink_element.get_attribute('href') if permalink_element else ""
            except:
                pass
            
            # Extract post information
            post_url = ""
            post_author = ""
            post_content_preview = ""
            
            try:
                # Find the original post container
                post_container = comment_element.find_element(By.XPATH, "./ancestor::*[contains(@class, 'feed-shared-update-v2')]")
                
                # Extract post URL
                post_link = post_container.find_element(By.CSS_SELECTOR, "a[href*='/posts/'], a[href*='/feed/update/']")
                post_url = post_link.get_attribute('href') if post_link else ""
                
                # Extract post author
                author_element = post_container.find_element(By.CSS_SELECTOR, ".feed-shared-actor__name, .feed-shared-actor__title")
                post_author = author_element.text.strip() if author_element else ""
                
                # Extract post content preview (first 100 chars)
                post_content_element = post_container.find_element(By.CSS_SELECTOR, ".feed-shared-text, .attributed-text-segment-list__content")
                full_content = post_content_element.text.strip() if post_content_element else ""
                post_content_preview = full_content[:100] + "..." if len(full_content) > 100 else full_content
                
            except:
                pass
            
            # Extract commenter information (should be the person we're scraping)
            commenter_name = self.name or ""
            commenter_url = self.linkedin_url or ""
            
            return {
                'content': content,
                'commented_date': commented_date,
                'likes_count': likes_count,
                'replies_count': replies_count,
                'comment_url': comment_url,
                'post_url': post_url,
                'post_author': post_author,
                'post_content_preview': post_content_preview,
                'commenter_name': commenter_name,
                'commenter_url': commenter_url
            }
            
        except Exception as e:
            print(f"Error extracting comment data: {e}")
            return None

    def _is_valid_comment_content(self, content):
        """
        Check if the extracted content is likely a comment rather than a post.
        
        Args:
            content (str): The content to validate
            
        Returns:
            bool: True if content appears to be a comment
        """
        if not content or len(content.strip()) < 3:
            return False
            
        # Filter out common post indicators
        post_indicators = [
            "We're Hiring:",
            "🚀 Exploring",
            "Your next DFIR teammate",
            "What's stopping you from",
            "Feed post number",
            "Post by",
            "shared a post",
            "posted this",
            "• View profile",
            "Connect with",
            "Follow",
            "ago • Edited",
            "reacted to this",
            "liked this",
            "commented on this"
        ]
        
        content_lower = content.lower()
        for indicator in post_indicators:
            if indicator.lower() in content_lower:
                print(f"🚫 Filtered out post content (indicator: '{indicator}'): {content[:50]}...")
                return False
        
        # Filter out very long content (likely posts, not comments)
        if len(content) > 1000:
            print(f"🚫 Filtered out long content (likely post): {content[:50]}...")
            return False
            
        return True
    
    def _extract_comment_from_full_text(self, full_text):
        """
        Extract the actual comment content from full element text.
        
        Args:
            full_text (str): Full text from the element
            
        Returns:
            str: Extracted comment content or empty string
        """
        if not full_text:
            return ""
            
        lines = full_text.split('\n')
        
        # Look for comment-like content (shorter, conversational)
        for line in lines:
            line = line.strip()
            if line and len(line) > 10 and len(line) < 500:
                # Skip metadata lines
                if any(skip in line.lower() for skip in ['ago', 'like', 'reply', 'view profile', 'connect']):
                    continue
                # Skip lines that look like post titles or headers
                if line.startswith('🚀') or line.startswith('We\'re Hiring') or 'DFIR' in line:
                    continue
                return line
        
        # If no good line found, return first non-empty line that's not too long
        for line in lines:
            line = line.strip()
            if line and len(line) > 5 and len(line) < 200:
                return line
                
        return ""

    def get_reactions(self, reaction_limit=5):
        """
        Scrape posts that this person reacted to.
        
        Args:
            reaction_limit (int): Maximum number of latest reactions to get (default: 5)
        """
        try:
            # Navigate to the person's reactions activity page
            reactions_url = f"{self.linkedin_url.rstrip('/')}/recent-activity/reactions/"
            print(f"🔍 Navigating to reactions page: {reactions_url}")
            self.driver.get(reactions_url)
            self.wait(3)
            
            # Scroll to load more reactions
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            scroll_attempts = 0
            max_scrolls = 5
            
            while scroll_attempts < max_scrolls:
                # Scroll down
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                self.wait(2)
                
                # Check if new content loaded
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                    
                last_height = new_height
                scroll_attempts += 1
                
                # Check if we have enough reactions and break early
                current_reactions = self.driver.find_elements(By.CSS_SELECTOR, ".feed-shared-update-v2, .activity-item, [data-urn*='activity']")
                if len(current_reactions) >= reaction_limit:
                    break
            
            # Try multiple selectors for reaction items
            reaction_selectors = [
                ".feed-shared-update-v2",
                ".activity-item", 
                "[data-urn*='activity']",
                ".feed-shared-mini-update-v2",
                "article[data-urn]",
                ".feed-shared-activity"
            ]
            
            reaction_elements = []
            for selector in reaction_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        print(f"✅ Found {len(elements)} reaction elements with selector: {selector}")
                        reaction_elements = elements
                        break
                except Exception as e:
                    print(f"⚠️  Selector '{selector}' failed: {e}")
                    continue
            
            if not reaction_elements:
                print("❌ No reaction elements found with any selector")
                return []
            
            print(f"📊 Processing {min(len(reaction_elements), reaction_limit)} reactions...")
            
            reactions = []
            processed_count = 0
            
            for element in reaction_elements:
                if processed_count >= reaction_limit:
                    break
                    
                reaction_data = self._extract_reaction_data(element)
                if reaction_data:
                    reactions.append(reaction_data)
                    processed_count += 1
                    print(f"✅ Extracted reaction {processed_count}: {reaction_data.get('post_preview', 'N/A')[:50]}...")
            
            print(f"🎯 Successfully extracted {len(reactions)} reactions")
            return reactions
            
        except Exception as e:
            print(f"❌ Error scraping reactions: {e}")
            return []

    def _extract_reaction_data(self, reaction_element):
        """
        Extract data from a reaction element.
        
        Args:
            reaction_element: Selenium WebElement representing a reaction
            
        Returns:
            dict: Reaction data or None if extraction fails
        """
        try:
            # Extract post content/preview
            post_preview = ""
            content_selectors = [
                ".feed-shared-inline-show-more-text",
                ".feed-shared-text",
                ".feed-shared-update-v2__description",
                ".feed-shared-actor__description",
                ".activity-item__description"
            ]
            
            for selector in content_selectors:
                try:
                    content_element = reaction_element.find_element(By.CSS_SELECTOR, selector)
                    post_preview = content_element.text.strip()
                    if post_preview:
                        break
                except:
                    continue
            
            # If no content found with selectors, try getting text from the element
            if not post_preview:
                try:
                    post_preview = reaction_element.text.strip()
                    # Take first meaningful line
                    lines = post_preview.split('\n')
                    for line in lines:
                        line = line.strip()
                        if line and len(line) > 10 and not line.endswith('ago'):
                            post_preview = line
                            break
                except:
                    post_preview = "[Content not available]"
            
            # Extract reaction date
            reacted_date = ""
            date_selectors = [
                "time",
                ".feed-shared-actor__sub-description time",
                "[data-test-id='feed-shared-actor__sub-description'] time",
                ".feed-shared-actor__sub-description",
                "[aria-label*='ago']"
            ]
            
            for selector in date_selectors:
                try:
                    date_element = reaction_element.find_element(By.CSS_SELECTOR, selector)
                    reacted_date = date_element.get_attribute('datetime') or date_element.text.strip()
                    if reacted_date:
                        break
                except:
                    continue
            
            # Extract post author
            post_author = ""
            author_selectors = [
                ".feed-shared-actor__name",
                ".feed-shared-actor__title",
                "[data-test-id='feed-shared-actor__name']",
                ".feed-shared-update-v2__actor-name"
            ]
            
            for selector in author_selectors:
                try:
                    author_element = reaction_element.find_element(By.CSS_SELECTOR, selector)
                    post_author = author_element.text.strip()
                    if post_author:
                        break
                except:
                    continue
            
            # Extract post URL
            post_url = ""
            url_selectors = [
                "a[href*='/posts/']",
                "a[href*='/feed/update/']",
                ".feed-shared-control-menu__trigger"
            ]
            
            for selector in url_selectors:
                try:
                    url_element = reaction_element.find_element(By.CSS_SELECTOR, selector)
                    post_url = url_element.get_attribute('href')
                    if post_url and ('/posts/' in post_url or '/feed/update/' in post_url):
                        break
                except:
                    continue
            
            # Extract reaction type (like, love, etc.)
            reaction_type = "like"  # Default to like
            try:
                reaction_elements = reaction_element.find_elements(By.CSS_SELECTOR, "[aria-label*='reaction'], .reaction-icon, [data-test-id*='reaction']")
                for elem in reaction_elements:
                    aria_label = elem.get_attribute('aria-label') or ""
                    if 'love' in aria_label.lower():
                        reaction_type = "love"
                        break
                    elif 'celebrate' in aria_label.lower():
                        reaction_type = "celebrate"
                        break
                    elif 'support' in aria_label.lower():
                        reaction_type = "support"
                        break
                    elif 'insightful' in aria_label.lower():
                        reaction_type = "insightful"
                        break
                    elif 'funny' in aria_label.lower():
                        reaction_type = "funny"
                        break
            except:
                pass
            
            return {
                'post_preview': post_preview[:200] if post_preview else "[Content not available]",
                'post_author': post_author,
                'post_url': post_url,
                'reacted_date': reacted_date,
                'reaction_type': reaction_type,
                'reactor_name': self.name or "",
                'reactor_url': self.linkedin_url
            }
            
        except Exception as e:
            print(f"⚠️  Error extracting reaction data: {e}")
            return None

    def scrape_logged_in(self, close_on_complete=True):
        driver = self.driver
        duration = None

        root = WebDriverWait(driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
            EC.presence_of_element_located(
                (
                    By.TAG_NAME,
                    self.__TOP_CARD,
                )
            )
        )
        self.focus()
        self.wait(5)

        # get name and location
        self.get_name_and_location()

        self.open_to_work = self.is_open_to_work()

        # get about
        self.get_about()
        driver.execute_script(
            "window.scrollTo(0, Math.ceil(document.body.scrollHeight/2));"
        )
        driver.execute_script(
            "window.scrollTo(0, Math.ceil(document.body.scrollHeight/1.5));"
        )

        # get experience
        self.get_experiences()

        # get education
        self.get_educations()

        driver.get(self.linkedin_url)

        # get interest
        try:

            _ = WebDriverWait(driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//*[@class='pv-profile-section pv-interests-section artdeco-container-card artdeco-card ember-view']",
                    )
                )
            )
            interestContainer = driver.find_element(By.XPATH,
                "//*[@class='pv-profile-section pv-interests-section artdeco-container-card artdeco-card ember-view']"
            )
            for interestElement in interestContainer.find_elements(By.XPATH,
                "//*[@class='pv-interest-entity pv-profile-section__card-item ember-view']"
            ):
                interest = Interest(
                    interestElement.find_element(By.TAG_NAME, "h3").text.strip()
                )
                self.add_interest(interest)
        except:
            pass

        # get accomplishment
        try:
            _ = WebDriverWait(driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//*[@class='pv-profile-section pv-accomplishments-section artdeco-container-card artdeco-card ember-view']",
                    )
                )
            )
            acc = driver.find_element(By.XPATH,
                "//*[@class='pv-profile-section pv-accomplishments-section artdeco-container-card artdeco-card ember-view']"
            )
            for block in acc.find_elements(By.XPATH,
                "//div[@class='pv-accomplishments-block__content break-words']"
            ):
                category = block.find_element(By.TAG_NAME, "h3")
                for title in block.find_element(By.TAG_NAME,
                    "ul"
                ).find_elements(By.TAG_NAME, "li"):
                    accomplishment = Accomplishment(category.text, title.text)
                    self.add_accomplishment(accomplishment)
        except:
            pass

        # get connections
        try:
            driver.get("https://www.linkedin.com/mynetwork/invite-connect/connections/")
            _ = WebDriverWait(driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located((By.CLASS_NAME, "mn-connections"))
            )
            connections = driver.find_element(By.CLASS_NAME, "mn-connections")
            if connections is not None:
                for conn in connections.find_elements(By.CLASS_NAME, "mn-connection-card"):
                    anchor = conn.find_element(By.CLASS_NAME, "mn-connection-card__link")
                    url = anchor.get_attribute("href")
                    name = conn.find_element(By.CLASS_NAME, "mn-connection-card__details").find_element(By.CLASS_NAME, "mn-connection-card__name").text.strip()
                    occupation = conn.find_element(By.CLASS_NAME, "mn-connection-card__details").find_element(By.CLASS_NAME, "mn-connection-card__occupation").text.strip()

                    contact = Contact(name=name, occupation=occupation, url=url)
                    self.add_contact(contact)
        except:
            connections = None

        if close_on_complete:
            driver.quit()

    @property
    def company(self):
        if self.experiences:
            return (
                self.experiences[0].institution_name
                if self.experiences[0].institution_name
                else None
            )
        else:
            return None

    @property
    def job_title(self):
        if self.experiences:
            return (
                self.experiences[0].position_title
                if self.experiences[0].position_title
                else None
            )
        else:
            return None

    def __repr__(self):
        return "<Person {name}\n\nAbout\n{about}\n\nExperience\n{exp}\n\nEducation\n{edu}\n\nInterest\n{int}\n\nAccomplishments\n{acc}\n\nContacts\n{conn}>".format(
            name=self.name,
            about=self.about,
            exp=self.experiences,
            edu=self.educations,
            int=self.interests,
            acc=self.accomplishments,
            conn=self.contacts,
        )
