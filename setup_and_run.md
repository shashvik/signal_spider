# LinkedIn Profile Scraper Setup and Usage

## Quick Setup

### 1. Install Dependencies
```bash
pip install selenium requests lxml
```

### 2. Install ChromeDriver

**Option A: Using Homebrew (macOS)**
```bash
brew install chromedriver
```

**Option B: Manual Installation**
1. Download ChromeDriver from: https://chromedriver.chromium.org/
2. Extract and place it in your PATH or project directory
3. Make it executable: `chmod +x chromedriver`

### 3. Set LinkedIn Credentials (Optional but Recommended)
```bash
export LINKEDIN_EMAIL="your-email@example.com"
export LINKEDIN_PASSWORD="your-password"
```

## Running the Scraper

### Method 1: Run the Custom Script
```bash
python scrape_shashank_profile.py
```

### Method 2: Interactive Python Session
```python
import sys
sys.path.append('./linkedin_scraper')

from linkedin_scraper import Person, actions
from selenium import webdriver

# Setup driver
driver = webdriver.Chrome()

# Login (will prompt for credentials if not set in environment)
actions.login(driver, None, None)

# Scrape the profile
person = Person("https://www.linkedin.com/in/shashank-n-security/", driver=driver)

# Access the data
print(f"Name: {person.name}")
print(f"Job Title: {person.job_title}")
print(f"Company: {person.company}")
print(f"About: {person.about}")

# Close browser
driver.quit()
```

## What the Script Does

1. **Sets up Chrome WebDriver** with appropriate options
2. **Logs into LinkedIn** using provided credentials
3. **Scrapes the target profile** (https://www.linkedin.com/in/shashank-n-security/)
4. **Extracts information** including:
   - Name
   - Job title
   - Company
   - About section
   - Work experiences
   - Education
   - Interests
5. **Displays results** in the terminal
6. **Saves data** to a text file

## Important Notes

- **LinkedIn Login Required**: Most profiles require authentication
- **Rate Limiting**: Don't scrape too frequently to avoid being blocked
- **Terms of Service**: Use responsibly and comply with LinkedIn's ToS
- **Profile Visibility**: The target profile must be publicly accessible or you must be connected
- **Language Setting**: Set your LinkedIn account language to English for best results

## Troubleshooting

### ChromeDriver Issues
```bash
# Check if chromedriver is in PATH
which chromedriver

# If not found, install via Homebrew
brew install chromedriver
```

### Permission Issues
```bash
# Make chromedriver executable
chmod +x /path/to/chromedriver
```

### LinkedIn Login Issues
- Ensure your credentials are correct
- Check if your account has 2FA enabled (may require manual intervention)
- Try logging in manually first in the browser

## Output Example

The script will output something like:
```
LinkedIn Profile Scraper
Target Profile: https://www.linkedin.com/in/shashank-n-security/
--------------------------------------------------
Logging into LinkedIn...
Login successful!
Scraping profile: https://www.linkedin.com/in/shashank-n-security/

==================================================
LINKEDIN PROFILE INFORMATION
==================================================
Name: Shashank N
Job Title: Security Professional
Company: [Company Name]
LinkedIn URL: https://www.linkedin.com/in/shashank-n-security/

About:
[About section content]

Experiences:
  1. [Job Title] at [Company]
     Duration: [Duration]

Education:
  1. [Degree] at [University]

==================================================

Profile data saved to: Shashank_N_linkedin_profile.txt
```