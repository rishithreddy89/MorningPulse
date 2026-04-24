"""LinkedIn company post scraper using Selenium."""

import json
import os
import random
import re
import time
from typing import Dict, List

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager


LINKEDIN_COMPANIES = [
    {"handle": "classdojo", "name": "ClassDojo"},
    {"handle": "instructure", "name": "Canvas LMS"},
    {"handle": "schoology", "name": "Schoology"},
    {"handle": "powerschool", "name": "PowerSchool"},
    {"handle": "blackboard", "name": "Blackboard"},
    {"handle": "seesaw-learning", "name": "Seesaw"},
    {"handle": "remind101", "name": "Remind"}
]

# UI text to ignore
INVALID_CONTENT = [
    "search new feed",
    "skip to main content",
    "no posts yet",
    "notifications",
    "search",
    "feed updates",
    "what's on your mind",
    "start a post",
    "follow",
    "like",
    "comment",
    "share",
    "see more",
    "see less"
]


class LinkedInScraper:
    
    def __init__(self, headless=True):
        """Initialize Chrome WebDriver with anti-detection settings."""
        self.email = os.getenv("LINKEDIN_EMAIL")
        self.password = os.getenv("LINKEDIN_PASSWORD")
        self.headless = headless
        self.driver = None
        self.wait = None
        self.is_logged_in = False
    
    def _setup_driver(self):
        """Configure Chrome with options to reduce bot detection."""
        options = Options()
        
        if self.headless:
            options.add_argument("--headless=new")
        
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument("--window-size=1920,1080")
        options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        
        self.driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        
        self.wait = WebDriverWait(self.driver, 15)
        print("Chrome driver initialized")
    
    def login(self) -> bool:
        """Log into LinkedIn. Returns True on success, False on failure."""
        try:
            self.driver.get("https://www.linkedin.com/login")
            time.sleep(2)
            
            email_field = self.wait.until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            email_field.clear()
            for char in self.email:
                email_field.send_keys(char)
                time.sleep(0.05)
            
            time.sleep(0.5)
            
            pass_field = self.driver.find_element(By.ID, "password")
            pass_field.clear()
            for char in self.password:
                pass_field.send_keys(char)
                time.sleep(0.05)
            
            time.sleep(0.5)
            
            self.driver.find_element(
                By.XPATH, "//button[@type='submit']"
            ).click()
            
            time.sleep(4)
            
            current_url = self.driver.current_url
            
            if "feed" in current_url or "mynetwork" in current_url:
                self.is_logged_in = True
                print("LinkedIn login successful")
                return True
            
            elif "checkpoint" in current_url or "challenge" in current_url:
                print("LinkedIn security checkpoint triggered")
                print("Cannot proceed - manual verification required")
                return False
            
            elif "login" in current_url:
                print("LinkedIn login failed - check credentials")
                return False
            
            else:
                self.is_logged_in = True
                print(f"LinkedIn login - redirected to: {current_url}")
                return True
        
        except TimeoutException:
            print("LinkedIn login timeout - page took too long")
            return False
        except Exception as e:
            print(f"LinkedIn login error: {e}")
            return False
    
    def _is_valid_post_text(self, text: str) -> bool:
        """Check if text is a valid post (not UI text)."""
        if not text or len(text) < 50:
            return False
        
        text_lower = text.lower()
        
        # Skip if contains invalid content
        for invalid in INVALID_CONTENT:
            if invalid in text_lower:
                return False
        
        return True
    
    def _check_no_posts_page(self) -> bool:
        """Check if page shows 'No posts yet' message."""
        try:
            page_text = self.driver.page_source.lower()
            if "no posts yet" in page_text:
                return True
        except Exception:
            pass
        return False
    
    def _extract_posts_from_feed(self, company_name: str) -> List[Dict]:
        """Extract posts from LinkedIn feed using proper selectors."""
        posts = []
        
        try:
            # Wait for posts to load
            self.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div.feed-shared-update-v2")
                )
            )
            print(f"  Posts loaded for {company_name}")
            
            # Check for "No posts yet" message
            if self._check_no_posts_page():
                print(f"  {company_name}: No posts yet")
                return []
            
            # Find all post containers
            post_elements = self.driver.find_elements(
                By.CSS_SELECTOR, "div.feed-shared-update-v2"
            )
            print(f"  Found {len(post_elements)} post containers")
            
            valid_posts = []
            
            for idx, post_element in enumerate(post_elements):
                try:
                    # Extract post text from the correct selector
                    text_elements = post_element.find_elements(
                        By.CSS_SELECTOR, "span.break-words"
                    )
                    
                    if not text_elements:
                        continue
                    
                    # Get text from first matching element
                    post_text = text_elements[0].text.strip()
                    
                    # Validate post text
                    if not self._is_valid_post_text(post_text):
                        continue
                    
                    # Try to get post URL
                    post_url = self.driver.current_url
                    try:
                        link_element = post_element.find_element(
                            By.CSS_SELECTOR, "a[href*='/feed/update/']"
                        )
                        post_url = link_element.get_attribute("href")
                    except NoSuchElementException:
                        pass
                    
                    # Clean text
                    clean_text = re.sub(r'\s+', ' ', post_text).strip()
                    
                    # Create post object
                    post = {
                        "title": clean_text[:80],
                        "summary": clean_text[:500],
                        "url": post_url,
                        "source": f"LinkedIn - {company_name}",
                        "category": "competitor_linkedin",
                        "competitor_name": company_name
                    }
                    
                    valid_posts.append(post)
                    
                    if len(valid_posts) >= 5:
                        break
                
                except Exception as e:
                    print(f"    Error extracting post {idx}: {e}")
                    continue
            
            print(f"  {company_name}: {len(valid_posts)} real posts extracted")
            return valid_posts
        
        except TimeoutException:
            print(f"  Timeout waiting for posts on {company_name}")
            return []
        except Exception as e:
            print(f"  Error extracting posts from {company_name}: {e}")
            return []
    
    def scrape_company(self, company: Dict) -> List[Dict]:
        """Scrape recent posts from one company's LinkedIn page."""
        handle = company["handle"]
        name = company["name"]
        url = f"https://www.linkedin.com/company/{handle}/posts/"
        
        try:
            self.driver.get(url)
            time.sleep(3)
            
            # Scroll to load posts
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight / 3)"
            )
            time.sleep(2)
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight / 2)"
            )
            time.sleep(2)
            
            # Extract posts using proper selectors
            posts = self._extract_posts_from_feed(name)
            
            return posts
        
        except Exception as e:
            print(f"  Error scraping {name}: {e}")
            return []
    
    def scrape_all(self, companies=None) -> List[Dict]:
        """Main method: login then scrape all companies."""
        if companies is None:
            companies = LINKEDIN_COMPANIES
        
        all_posts = []
        
        try:
            self._setup_driver()
            
            if not self.login():
                print("LinkedIn login failed. Returning empty results.")
                return []
            
            for i, company in enumerate(companies):
                print(f"\nScraping {company['name']} "
                      f"({i+1}/{len(companies)})...")
                
                posts = self.scrape_company(company)
                all_posts.extend(posts)
                
                if i < len(companies) - 1:
                    delay = random.uniform(8, 15)
                    print(f"  Waiting {delay:.1f}s before next company...")
                    time.sleep(delay)
            
            # Deduplicate by URL
            seen = set()
            unique = []
            for post in all_posts:
                url = post.get("url", "")
                text = post.get("summary", "")
                key = url if url else hash(text)
                if key not in seen:
                    seen.add(key)
                    unique.append(post)
            
            print(f"\nLinkedIn total: {len(unique)} unique posts")
            return unique
        
        except Exception as e:
            print(f"LinkedIn scrape_all error: {e}")
            return []
        
        finally:
            self.quit()
    
    def quit(self):
        """Close the browser and clean up."""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
                print("Chrome driver closed")
        except Exception:
            pass
