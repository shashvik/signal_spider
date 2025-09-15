#!/usr/bin/env python3
"""
Test Comment Content Filtering

This script tests the improved comment content filtering logic
using the existing scraped data to demonstrate the fix.
"""

import json
import sys
import os

# Add the linkedin_scraper directory to the path
sys.path.append('linkedin_scraper')

from linkedin_scraper.person import Person

def test_comment_filtering():
    """Test the comment filtering logic with sample data"""
    
    # Create a Person instance to access the filtering methods
    person = Person(linkedin_url="https://www.linkedin.com/in/test/", scrape=False)
    
    # Sample content from the problematic scraped data
    test_contents = [
        "We're Hiring: Cyber Security Intern @ Matters.ai\n\nAt Matters.ai, we're building the future of AI-powered data security...",
        "What's stopping you from coding like this?",
        "Your next DFIR teammate isn't human — it's an LLM agent.\n\nThat's exactly what I built: the Agentic Digital Forensics Toolkit.",
        "🚀 Exploring AI Agents in GoLang\n\nGoLang has always been one of my favourite languages...",
        "Great insights! Thanks for sharing.",  # This should be a valid comment
        "CFBR, if you want to build something really cool do apply.",  # This should be a valid comment
        "Interesting approach to the problem.",  # This should be a valid comment
        "Feed post number 1",  # This should be filtered out
        "Post by John Doe",  # This should be filtered out
    ]
    
    print("Testing Comment Content Filtering")
    print("=" * 50)
    
    valid_comments = []
    filtered_posts = []
    
    for i, content in enumerate(test_contents, 1):
        print(f"\nTest {i}: {content[:50]}...")
        
        if person._is_valid_comment_content(content):
            print(f"✅ VALID COMMENT")
            valid_comments.append(content)
        else:
            print(f"🚫 FILTERED OUT (Post content)")
            filtered_posts.append(content)
    
    print(f"\n{'='*50}")
    print(f"RESULTS:")
    print(f"Valid Comments: {len(valid_comments)}")
    print(f"Filtered Posts: {len(filtered_posts)}")
    
    print(f"\nVALID COMMENTS:")
    for i, comment in enumerate(valid_comments, 1):
        print(f"  {i}. {comment[:100]}...")
    
    print(f"\nFILTERED POSTS:")
    for i, post in enumerate(filtered_posts, 1):
        print(f"  {i}. {post[:100]}...")
    
    # Test the text extraction method
    print(f"\n{'='*50}")
    print("Testing Comment Extraction from Full Text")
    print("=" * 50)
    
    sample_full_text = """John Doe
• 1st
Software Engineer at Tech Corp
3d • Edited

Great insights! Thanks for sharing this approach.

👍 Like
💬 Comment
🔄 Repost
📤 Send

15 reactions
3 comments
"""
    
    extracted = person._extract_comment_from_full_text(sample_full_text)
    print(f"Full text: {sample_full_text[:100]}...")
    print(f"Extracted comment: '{extracted}'")
    
    if extracted and person._is_valid_comment_content(extracted):
        print("✅ Successfully extracted valid comment from full text")
    else:
        print("❌ Failed to extract valid comment")

def analyze_existing_data():
    """Analyze the existing scraped data to show the problem"""
    
    json_file = "linkedin_comments_20250915_205126.json"
    
    if not os.path.exists(json_file):
        print(f"❌ File {json_file} not found")
        return
    
    print(f"\n{'='*50}")
    print(f"Analyzing Existing Scraped Data: {json_file}")
    print("=" * 50)
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    person = Person(linkedin_url="https://www.linkedin.com/in/test/", scrape=False)
    
    print(f"Total items in file: {len(data['comments'])}")
    
    actual_comments = 0
    post_content = 0
    
    for i, item in enumerate(data['comments'], 1):
        content = item['content']
        print(f"\nItem {i}: {content[:80]}...")
        
        if person._is_valid_comment_content(content):
            print(f"  ✅ This appears to be a COMMENT")
            actual_comments += 1
        else:
            print(f"  🚫 This appears to be POST CONTENT (should be filtered)")
            post_content += 1
    
    print(f"\n{'='*50}")
    print(f"ANALYSIS RESULTS:")
    print(f"Actual Comments: {actual_comments}")
    print(f"Post Content (should be filtered): {post_content}")
    print(f"\nThe issue: {post_content}/{len(data['comments'])} items are post content, not comments!")
    print(f"With the fix: Only {actual_comments} valid comments would be extracted.")

if __name__ == "__main__":
    test_comment_filtering()
    analyze_existing_data()