"""
Reddit Scraper - Mock Implementation for Sprint 3

Provides fake Reddit data for testing friction detection logic.
Can be extended with real scraping/API later.

Part of Sprint 3: Verification Layer (Gemini's Original Plan)
"""

from typing import List, Optional, Dict
from dataclasses import dataclass
from datetime import datetime, timedelta
import random


@dataclass
class RedditPost:
    """A Reddit post or comment."""
    post_id: str
    author: str
    subreddit: str
    title: str
    content: str
    upvotes: int
    created_at: datetime
    url: str
    is_comment: bool = False


class RedditScraperMock:
    """
    Mock Reddit scraper for testing Sprint 3 logic.

    Generates realistic fake Reddit data for testing:
    - Friction detection
    - Consensus scoring
    - Experience extraction

    Usage:
        scraper = RedditScraperMock()

        # Search for posts
        posts = scraper.search(
            query="solar inverter problems",
            subreddit="solar",
            limit=10
        )

        # Returns realistic mock data for testing
    """

    # Mock data templates
    MOCK_TEMPLATES = {
        "solar_inverter_positive": [
            {
                "title": "My {brand} inverter has been running flawlessly for {years} years",
                "content": "Just wanted to share my experience. Installed {brand} inverter in {year}. "
                          "Zero issues, efficiency still at {efficiency}%. Highly recommend! "
                          "Model: {model}",
                "upvotes": lambda: random.randint(20, 100),
                "sentiment": "positive"
            },
            {
                "title": "{brand} inverter - Excellent choice",
                "content": "Research shows {brand} has {percentage}% lower failure rate. "
                          "I've been using it for {years} years without problems. "
                          "Great build quality and reliable performance.",
                "upvotes": lambda: random.randint(10, 50),
                "sentiment": "positive"
            }
        ],
        "solar_inverter_negative": [
            {
                "title": "{brand} inverter died after {years} years",
                "content": "Warning: My {brand} {model} failed after only {years} years. "
                          "Support was unhelpful. Firmware update bricked it. "
                          "Cost me €{cost} to replace. Look elsewhere!",
                "upvotes": lambda: random.randint(30, 150),
                "sentiment": "negative"
            },
            {
                "title": "Issues with {brand} inverter",
                "content": "I think maybe the {brand} isn't as reliable as advertised. "
                          "Mine had problems after {years} years. "
                          "Support response was slow. Not sure I'd recommend it.",
                "upvotes": lambda: random.randint(5, 25),
                "sentiment": "negative"
            }
        ],
        "solar_inverter_technical": [
            {
                "title": "Detailed analysis of {brand} MPPT efficiency",
                "content": "After testing {brand} for {years} years, here are the numbers:\n"
                          "- MPPT efficiency: {efficiency}%\n"
                          "- String voltage range: 200-800V\n"
                          "- Max input current: 32A\n"
                          "Data suggests it performs {percentage}% better than competitors in shading conditions.",
                "upvotes": lambda: random.randint(50, 200),
                "sentiment": "neutral"
            }
        ]
    }

    def __init__(self):
        """Initialize mock scraper."""
        self.mock_subreddits = ["solar", "homeimprovement", "renewable", "diy"]
        self.mock_brands = ["SolarEdge", "Huawei", "SMA", "Fronius", "Enphase"]

    def search(
        self,
        query: str,
        subreddit: Optional[str] = None,
        limit: int = 10,
        time_filter: str = "year"
    ) -> List[RedditPost]:
        """
        Mock search returning fake Reddit posts.

        Args:
            query: Search query (determines which templates to use)
            subreddit: Subreddit to search (or None for all)
            limit: Number of posts to return
            time_filter: Time range (ignored for mock)

        Returns:
            List of mock RedditPost objects
        """
        posts = []

        # Determine sentiment mix based on query
        if "problem" in query.lower() or "issue" in query.lower() or "failure" in query.lower():
            # Negative query → more negative posts
            template_weights = {
                "negative": 0.6,
                "positive": 0.2,
                "technical": 0.2
            }
        elif "recommend" in query.lower() or "best" in query.lower():
            # Positive query → more positive posts
            template_weights = {
                "positive": 0.6,
                "negative": 0.2,
                "technical": 0.2
            }
        else:
            # Neutral query → balanced
            template_weights = {
                "positive": 0.3,
                "negative": 0.3,
                "technical": 0.4
            }

        # Generate mock posts
        for i in range(limit):
            # Pick sentiment based on weights
            sentiment = random.choices(
                list(template_weights.keys()),
                weights=list(template_weights.values())
            )[0]

            # Select template
            if sentiment == "positive":
                templates = self.MOCK_TEMPLATES["solar_inverter_positive"]
            elif sentiment == "negative":
                templates = self.MOCK_TEMPLATES["solar_inverter_negative"]
            else:
                templates = self.MOCK_TEMPLATES["solar_inverter_technical"]

            template = random.choice(templates)

            # Fill template with random data
            brand = random.choice(self.mock_brands)
            post_data = {
                "brand": brand,
                "model": f"{brand}-{random.randint(1000, 9999)}",
                "years": random.randint(1, 10),
                "year": random.randint(2015, 2023),
                "efficiency": random.randint(92, 98),
                "percentage": random.randint(10, 40),
                "cost": random.randint(500, 2000)
            }

            title = template["title"].format(**post_data)
            content = template["content"].format(**post_data)
            upvotes = template["upvotes"]()

            # Create post
            post = RedditPost(
                post_id=f"mock_{i}_{random.randint(1000, 9999)}",
                author=f"user_{random.randint(100, 999)}",
                subreddit=subreddit or random.choice(self.mock_subreddits),
                title=title,
                content=content,
                upvotes=upvotes,
                created_at=datetime.now() - timedelta(days=random.randint(1, 365)),
                url=f"https://reddit.com/r/{subreddit or 'solar'}/mock_{i}",
                is_comment=False
            )

            posts.append(post)

        # Sort by upvotes (most popular first)
        posts.sort(key=lambda p: p.upvotes, reverse=True)

        return posts

    def get_comments(self, post_id: str, limit: int = 10) -> List[RedditPost]:
        """
        Mock comments for a post.

        Args:
            post_id: Post ID
            limit: Number of comments to return

        Returns:
            List of mock comment posts
        """
        comments = []

        comment_templates = [
            "I had the same experience with {brand}!",
            "Can confirm, {brand} is {adjective}.",
            "Interesting, my {brand} works fine after {years} years.",
            "The {brand} support team was {adjective} when I contacted them.",
            "Data shows {brand} has {percentage}% better reliability."
        ]

        for i in range(limit):
            template = random.choice(comment_templates)

            content = template.format(
                brand=random.choice(self.mock_brands),
                adjective=random.choice(["great", "terrible", "okay", "unreliable", "excellent"]),
                years=random.randint(1, 8),
                percentage=random.randint(10, 50)
            )

            comment = RedditPost(
                post_id=f"comment_{post_id}_{i}",
                author=f"commenter_{random.randint(100, 999)}",
                subreddit="solar",
                title="",
                content=content,
                upvotes=random.randint(1, 50),
                created_at=datetime.now() - timedelta(days=random.randint(1, 180)),
                url=f"https://reddit.com/comment_{i}",
                is_comment=True
            )

            comments.append(comment)

        return comments


class RedditScraperWeb:
    """
    Optional: Web scraper using BeautifulSoup.

    WARNING: Web scraping Reddit violates their Terms of Service!
    This is provided for educational purposes only.

    For production, use:
    - Official Reddit API (requires credentials)
    - Or mock data for testing

    Usage:
        scraper = RedditScraperWeb()
        posts = scraper.search("solar inverter", subreddit="solar")
    """

    def __init__(self):
        """Initialize web scraper."""
        import warnings
        warnings.warn(
            "RedditScraperWeb: Web scraping Reddit may violate ToS. "
            "Use official API for production or mock data for testing.",
            UserWarning
        )

        try:
            import requests
            from bs4 import BeautifulSoup
            self.requests = requests
            self.BeautifulSoup = BeautifulSoup
        except ImportError:
            raise ImportError(
                "requests and beautifulsoup4 required for web scraping. "
                "Install: pip install requests beautifulsoup4"
            )

        self.headers = {
            "User-Agent": "Mozilla/5.0 (Educational Research Bot)"
        }

    def search(
        self,
        query: str,
        subreddit: Optional[str] = None,
        limit: int = 10
    ) -> List[RedditPost]:
        """
        Scrape Reddit search results.

        WARNING: This may violate Reddit's ToS!
        Use only for educational purposes.

        Args:
            query: Search query
            subreddit: Subreddit to search
            limit: Max results

        Returns:
            List of scraped posts
        """
        posts = []

        try:
            # Build search URL
            if subreddit:
                url = f"https://old.reddit.com/r/{subreddit}/search?q={query}&restrict_sr=on"
            else:
                url = f"https://old.reddit.com/search?q={query}"

            # Fetch page
            response = self.requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()

            # Parse HTML
            soup = self.BeautifulSoup(response.text, "html.parser")

            # Extract posts (simplified - Reddit HTML structure changes frequently)
            post_divs = soup.find_all("div", class_="thing", limit=limit)

            for div in post_divs:
                try:
                    # Extract data (this is fragile and may break!)
                    title_elem = div.find("a", class_="title")
                    if not title_elem:
                        continue

                    post = RedditPost(
                        post_id=div.get("data-fullname", "unknown"),
                        author=div.get("data-author", "unknown"),
                        subreddit=div.get("data-subreddit", subreddit or "unknown"),
                        title=title_elem.text.strip(),
                        content="",  # Would need to fetch post page
                        upvotes=int(div.get("data-score", 0)),
                        created_at=datetime.now(),  # Would need to parse timestamp
                        url=title_elem.get("href", ""),
                        is_comment=False
                    )

                    posts.append(post)

                except Exception as e:
                    print(f"Warning: Failed to parse post: {e}")
                    continue

        except Exception as e:
            print(f"Warning: Web scraping failed: {e}")
            print("Falling back to mock data...")
            # Fallback to mock
            return RedditScraperMock().search(query, subreddit, limit)

        return posts if posts else RedditScraperMock().search(query, subreddit, limit)


# Factory function
def create_reddit_scraper(mode: str = "mock") -> 'RedditScraperMock | RedditScraperWeb':
    """
    Factory to create Reddit scraper.

    Args:
        mode: "mock" (fake data) or "web" (BeautifulSoup scraper)

    Returns:
        RedditScraper instance

    Example:
        # For testing (recommended)
        scraper = create_reddit_scraper("mock")

        # For real data (educational only, may violate ToS)
        scraper = create_reddit_scraper("web")
    """
    if mode == "mock":
        return RedditScraperMock()
    elif mode == "web":
        return RedditScraperWeb()
    else:
        raise ValueError(f"Unknown mode: {mode}. Use 'mock' or 'web'")
