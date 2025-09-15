# LinkedIn Posts Scraping Module

This module extends the LinkedIn scraper to include posts scraping functionality, allowing you to extract posts from the last 24 hours (or any specified time period) from a LinkedIn profile.

## Features

- **Time-based Filtering**: Scrape posts from the last 24 hours (configurable)
- **Comprehensive Data Extraction**: Extract post content, engagement metrics, media types, and metadata
- **Multiple Output Formats**: Display results in console and save to file
- **Robust Error Handling**: Gracefully handle missing elements and parsing errors
- **Flexible Usage**: Can be used as part of full profile scraping or standalone

## What Gets Extracted

For each post, the scraper extracts:

- **Content**: Full text content of the post
- **Posted Date**: When the post was published
- **Engagement Metrics**:
  - Likes/reactions count
  - Comments count
  - Shares/reposts count
- **Media Type**: text, image, video, or document
- **Post URL**: Direct link to the post
- **Author Information**: Name and profile URL

## Usage

### Method 1: Standalone Posts Scraper

```bash
python3 scrape_posts.py
```

This will:
1. Prompt for LinkedIn credentials (or use environment variables)
2. Scrape posts from the last 24 hours
3. Display results in the console
4. Save results to a timestamped file

### Method 2: Integrated with Profile Scraper

```bash
python3 scrape_shashank_profile.py
```

This will scrape the full profile AND posts from the last 24 hours.

### Method 3: Programmatic Usage

```python
import sys
sys.path.append('./linkedin_scraper')

from linkedin_scraper import Person, actions
from selenium import webdriver

# Setup driver and login
driver = webdriver.Chrome()
actions.login(driver, "your-email@example.com", "your-password")

# Create person object
person = Person("https://www.linkedin.com/in/shashank-n-security/", driver=driver, scrape=False)

# Scrape posts from last 24 hours
person.get_posts(hours_limit=24)

# Access the posts
for post in person.posts:
    print(f"Posted: {post.posted_date}")
    print(f"Content: {post.content}")
    print(f"Likes: {post.likes_count}")
    print(f"Comments: {post.comments_count}")
    print(f"Shares: {post.shares_count}")
    print(f"Media Type: {post.media_type}")
    print(f"URL: {post.post_url}")
    print("-" * 50)

driver.quit()
```

## Configuration Options

### Time Limit

You can customize the time range for posts:

```python
# Last 12 hours
person.get_posts(hours_limit=12)

# Last 48 hours
person.get_posts(hours_limit=48)

# Last week
person.get_posts(hours_limit=168)  # 24 * 7
```

### Environment Variables

Set these environment variables to avoid manual login:

```bash
export LINKEDIN_EMAIL="your-email@example.com"
export LINKEDIN_PASSWORD="your-password"
```

## Output Files

### Standalone Posts File

When using `scrape_posts.py`, a separate file is created:
- Format: `linkedin_posts_YYYYMMDD_HHMMSS.txt`
- Contains: Detailed post information with full content and metadata

### Integrated Profile File

When using `scrape_shashank_profile.py`, posts are included in the main profile file:
- Format: `Shashank_N_linkedin_profile.txt`
- Contains: Full profile data + posts section

## Sample Output

```
LinkedIn Posts Scraping Results
============================================================

Found 3 posts from the last 24 hours:
--------------------------------------------------

Post #1:
  Posted: 2h ago
  Author: Shashank N
  Media Type: text
  Content: Excited to share my latest insights on AI security and LLM vulnerabilities...
  Engagement:
    - Likes: 45
    - Comments: 12
    - Shares: 8
  URL: https://www.linkedin.com/posts/shashank-n-security_...

Post #2:
  Posted: 8h ago
  Author: Shashank N
  Media Type: image
  Content: Just completed an amazing security assessment using the latest tools...
  Engagement:
    - Likes: 23
    - Comments: 5
    - Shares: 3
  URL: https://www.linkedin.com/posts/shashank-n-security_...
```

## Technical Details

### How It Works

1. **Navigation**: The scraper navigates to the user's activity page (`/recent-activity/all/`)
2. **Content Loading**: Scrolls and waits for posts to load
3. **Element Detection**: Uses multiple CSS selectors to find post elements
4. **Data Extraction**: Extracts content, metadata, and engagement metrics
5. **Time Filtering**: Parses dates and filters based on the specified time limit
6. **Data Storage**: Creates Post objects and stores them in the Person object

### Supported Date Formats

The scraper can parse various date formats:
- Relative dates: "2h ago", "1d ago", "3w ago"
- ISO format: "2024-01-15T10:30:00Z"
- LinkedIn's custom formats

### Error Handling

- **Missing Elements**: Gracefully handles missing post elements
- **Date Parsing Errors**: Includes posts with unparseable dates
- **Network Issues**: Retries and continues with available data
- **Authentication**: Clear error messages for login issues

## Limitations

1. **LinkedIn Login Required**: Posts scraping requires authentication
2. **Rate Limiting**: LinkedIn may limit scraping frequency
3. **Privacy Settings**: Can only access publicly visible posts or posts visible to your account
4. **Dynamic Content**: LinkedIn's structure may change, affecting selectors
5. **Time Zone**: Date parsing assumes local time zone

## Troubleshooting

### No Posts Found

- Check if the user has posted recently
- Verify the profile is public or you're connected
- Ensure you're logged in properly
- Try increasing the time limit

### Login Issues

- Verify credentials are correct
- Check for 2FA requirements
- Try logging in manually first
- Use environment variables for credentials

### Scraping Errors

- Update ChromeDriver to the latest version
- Check internet connection
- Verify LinkedIn hasn't changed their structure
- Try running with fewer concurrent requests

## Best Practices

1. **Respect Rate Limits**: Don't scrape too frequently
2. **Use Proper Credentials**: Set up environment variables
3. **Handle Errors**: Always wrap scraping in try-catch blocks
4. **Save Data**: Regularly save scraped data to avoid loss
5. **Stay Updated**: Monitor for LinkedIn structure changes

## Legal and Ethical Considerations

- **Terms of Service**: Ensure compliance with LinkedIn's ToS
- **Privacy**: Respect user privacy and data protection laws
- **Rate Limiting**: Don't overload LinkedIn's servers
- **Data Usage**: Use scraped data responsibly
- **Attribution**: Give proper credit when using scraped content

## Future Enhancements

- Support for scraping comments on posts
- Image and video content extraction
- Advanced filtering options (by content type, engagement level)
- Export to different formats (JSON, CSV)
- Batch processing for multiple profiles