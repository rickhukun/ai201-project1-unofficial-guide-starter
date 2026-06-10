"""
Web scrapers for UCLA dining data from 12 sources.
Use these to replace load_sample_documents() in production.

This module requires additional dependencies:
- pip install praw  # Reddit API
- pip install requests beautifulsoup4  # Web scraping
- pip install youtube-transcript-api  # YouTube transcripts
"""

import requests
from typing import List, Dict
import json
from urllib.parse import urljoin


# ============================================================================
# REDDIT SCRAPER
# ============================================================================

def scrape_reddit_posts(subreddit: str, search_query: str, limit: int = 50) -> List[Dict]:
    """
    Scrape Reddit posts using PRAW (Python Reddit API Wrapper).
    Requires: pip install praw
    Setup: Create reddit app at https://www.reddit.com/prefs/apps
    
    Args:
        subreddit: e.g., "ucla" or "college"
        search_query: e.g., "dining" or "meal plan"
        limit: Number of posts to fetch
    
    Returns:
        List of dicts with 'text' and 'source'
    """
    try:
        import praw
    except ImportError:
        print("⚠️  PRAW not installed. Run: pip install praw")
        return []
    
    # TODO: Requires Reddit app credentials (client_id, client_secret, user_agent)
    # For now, return empty list. In production:
    # reddit = praw.Reddit(client_id='...', client_secret='...', user_agent='...')
    # subreddit_obj = reddit.subreddit(subreddit)
    # posts = subreddit_obj.search(search_query, limit=limit)
    # return [{"text": post.selftext, "source": f"https://reddit.com{post.permalink}"} for post in posts]
    
    print(f"Note: Implement Reddit scraper with PRAW credentials")
    return []


def scrape_reddit_threads() -> List[Dict]:
    """Scrape UCLA dining threads from specific Reddit URLs."""
    documents = []
    
    reddit_sources = [
        ("UCLA - Dining", "https://www.reddit.com/r/ucla/search/?q=dining"),
        ("UCLA - Meal Plan", "https://www.reddit.com/r/ucla/search/?q=meal+plan"),
        ("UCLA - Housing", "https://www.reddit.com/r/uclahousing"),
        ("r/college - UCLA", "https://www.reddit.com/r/college/search/?q=UCLA+dining"),
    ]
    
    for source_name, url in reddit_sources:
        # Fetch JSON from Reddit
        try:
            headers = {
                "User-Agent": "UCLA-Dining-RAG/1.0 (research project)"
            }
            response = requests.get(url + ".json", headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if "data" in data and "children" in data["data"]:
                for child in data["data"]["children"]:
                    post = child.get("data", {})
                    text = post.get("selftext") or post.get("title", "")
                    if text:
                        documents.append({
                            "text": text,
                            "source": url,
                            "title": post.get("title"),
                        })
        except Exception as e:
            print(f"Error scraping Reddit {source_name}: {e}")
    
    return documents


# ============================================================================
# GOOGLE MAPS SCRAPER
# ============================================================================

def scrape_google_maps_reviews(place_name: str, place_id: str) -> List[Dict]:
    """
    Scrape Google Maps reviews.
    Note: Google Maps has anti-scraping measures. For production, use:
    - Google Maps API (requires API key and paid plan)
    - Alternative: google-places library (limited free tier)
    
    Args:
        place_name: e.g., "FEAST at Rieber"
        place_id: Google Place ID (from Google Maps URL)
    
    Returns:
        List of dicts with review text
    """
    # In production, would use Google Maps API or browser automation (Selenium)
    # For now, return placeholder
    print(f"Note: Implement Google Maps scraper (requires API key): {place_name}")
    return []


def get_google_maps_sources() -> List[tuple]:
    """Return list of UCLA dining halls for Google Maps scraping."""
    return [
        ("FEAST at Rieber", "https://www.google.com/maps/place/FEAST+at+Rieber"),
        ("De Neve Dining Hall", "https://www.google.com/maps/place/De+Neve+Dining+Hall"),
        ("Bruin Plate", "https://www.google.com/maps/place/Bruin+Plate+Residential+Restaurant"),
        ("Epicuria at Ackerman", "https://www.google.com/maps/place/Epicuria+at+Ackerman"),
        ("Café 1919", "https://www.google.com/maps/place/Café+1919"),
    ]


# ============================================================================
# YOUTUBE TRANSCRIPT SCRAPER
# ============================================================================

def scrape_youtube_transcripts(search_query: str = "UCLA dining hall review") -> List[Dict]:
    """
    Scrape YouTube video transcripts.
    Requires: pip install youtube-transcript-api
    
    Args:
        search_query: YouTube search query
    
    Returns:
        List of dicts with transcript text
    """
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except ImportError:
        print("⚠️  youtube-transcript-api not installed. Run: pip install youtube-transcript-api")
        return []
    
    # In production:
    # 1. Search YouTube for "UCLA dining hall review"
    # 2. Extract video IDs
    # 3. Fetch transcripts using YouTubeTranscriptApi.get_transcript(video_id)
    # 4. Return as documents
    
    print("Note: Implement YouTube transcript scraper")
    return []


# ============================================================================
# BRUINWALK SCRAPER
# ============================================================================

def scrape_bruinwalk_housing_guides() -> List[Dict]:
    """
    Scrape BruinWalk housing guide pages.
    BruinWalk is a UCLA student-run resource with housing reviews.
    
    Returns:
        List of dicts with guide text mentioning dining
    """
    # In production:
    # 1. Request https://bruinwalk.com with headers
    # 2. Parse HTML to find housing guides
    # 3. Extract sections mentioning dining halls
    # 4. Return as documents
    
    print("Note: Implement BruinWalk scraper")
    return []


# ============================================================================
# UCLA OFFICIAL DINING WEBSITE
# ============================================================================

def scrape_ucla_dining_website() -> List[Dict]:
    """
    Scrape UCLA's official dining website.
    This is less useful for opinions (it's official), but includes useful context.
    
    Source: https://www.dining.ucla.edu
    """
    # In production:
    # 1. Fetch dining.ucla.edu
    # 2. Parse menu pages, dining hall descriptions
    # 3. Extract relevant info
    # 4. Return as documents
    
    print("Note: Implement UCLA dining website scraper")
    return []


# ============================================================================
# MASTER LOADER (PRODUCTION VERSION)
# ============================================================================

def load_all_documents_from_web() -> List[Dict[str, str]]:
    """
    Production version: Load documents from all 12 sources.
    
    Returns:
        Combined list of all documents
    """
    all_documents = []
    
    print("Fetching documents from 12 sources...\n")
    
    # Reddit
    print("1. Scraping Reddit threads...")
    reddit_docs = scrape_reddit_threads()
    all_documents.extend(reddit_docs)
    print(f"   ✓ Got {len(reddit_docs)} Reddit posts\n")
    
    # Google Maps (requires setup)
    print("2. Google Maps reviews (requires API key setup)...")
    for place_name, url in get_google_maps_sources():
        maps_docs = scrape_google_maps_reviews(place_name, url)
        all_documents.extend(maps_docs)
    print(f"   ⚠️  Skipped (API setup needed)\n")
    
    # YouTube
    print("3. YouTube transcripts...")
    yt_docs = scrape_youtube_transcripts()
    all_documents.extend(yt_docs)
    print(f"   ⚠️  Skipped (configure YouTube search)\n")
    
    # BruinWalk
    print("4. BruinWalk housing guides...")
    bw_docs = scrape_bruinwalk_housing_guides()
    all_documents.extend(bw_docs)
    print(f"   ⚠️  Skipped (configure BruinWalk scraper)\n")
    
    # UCLA Official Dining
    print("5. UCLA official dining website...")
    dining_docs = scrape_ucla_dining_website()
    all_documents.extend(dining_docs)
    print(f"   ⚠️  Skipped (configure dining.ucla.edu scraper)\n")
    
    print(f"{'='*60}")
    print(f"Total documents fetched: {len(all_documents)}")
    print(f"{'='*60}\n")
    
    return all_documents


# ============================================================================
# QUICK SETUP GUIDE
# ============================================================================

SETUP_GUIDE = """
PRODUCTION SCRAPER SETUP GUIDE
================================

To enable all web scrapers, follow these steps:

1. REDDIT (r/UCLA, r/college, r/UCLAHousing)
   - Create app: https://www.reddit.com/prefs/apps
   - Install: pip install praw
   - Get credentials: client_id, client_secret
   - Add to scrapers.py or .env file

2. GOOGLE MAPS
   - Get API key: https://cloud.google.com/maps-platform
   - Enable Places API
   - Use google-maps library or Selenium
   - Note: Reviews require special handling (often blocked)

3. YOUTUBE
   - Install: pip install youtube-transcript-api
   - Use YouTube Data API for search (requires API key)
   - Extract video IDs from search results
   - Fetch transcripts using APIyt

4. BRUINWALK
   - Use BeautifulSoup to scrape HTML
   - Install: pip install beautifulsoup4 requests
   - Parse housing guide pages
   - Extract dining-related sections

5. UCLA DINING WEBSITE
   - Parse dining.ucla.edu
   - Extract menu descriptions, dining hall info
   - Use requests + BeautifulSoup

DEVELOPMENT APPROACH:
- Start with Reddit (easiest, most student opinions)
- Add each scraper incrementally
- Test each independently before full pipeline
- Use sample_documents.py for offline testing
"""

if __name__ == "__main__":
    print(SETUP_GUIDE)
