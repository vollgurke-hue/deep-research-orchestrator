# Sprint 3: Verification Layer - Implementation Plan

**Status:** Planning
**Date:** 2026-01-16
**Goal:** Reddit Validation + Friction Detection
**Estimated Time:** 6-8 days

---

## 📋 Gemini's Original Sprint 3 Definition

**From:** `docs/concepts/SRO_ARCHITECTURE_OVERVIEW.md`

```markdown
### Sprint 3: Verification (Woche 5-6)
□ Tiered RAG (Bronze/Silver/Gold)  ← Already done! (Cluster 2)
□ Reddit Scraper
□ Friction Detector
□ Consensus Scorer
```

**Current Status:**
- ✅ Tiered RAG (implemented in Cluster 2)
- ❌ Reddit Scraper (MISSING!)
- ❌ Friction Detector (MISSING!)
- ❌ Consensus Scorer (MISSING!)

---

## 🎯 Sprint 3 Core Concept

### The Problem We're Solving

**KI has access to:**
- Official documentation
- Marketing materials
- Whitepapers
- News headlines

**What's MISSING:** **REALITY** - What actually works in practice!

### Example: Solar Inverter

**AI (from datasheet):**
```python
SPOTriplet(
    subject="Inverter_X",
    predicate="has_MTBF",
    object="100,000_hours",
    tier="bronze"  # From manufacturer
)
```

**Reddit (r/solar):**
```
User1: "Inverter X died after 3 years, support ghosted me"
User2: "Same issue, 2nd replacement in 5 years"
User3: "Running fine for 7 years" [12 upvotes]
User4: "Firmware update bricked mine" [89 upvotes]
```

**Friction Detected:**
- Theory says: 10 years reliable
- Practice shows: Firmware issues, bad support

**Result:**
- Downgrade confidence in AI triplet
- Create friction alert
- Flag for manual review

---

## 📚 Architecture

### Component Overview

```
ToT Node Expansion
    ↓
SPO Extraction (Sprint 1)
    ↓
Tiered RAG (Cluster 2)
    ↓
[NEW] Reddit Validation (Sprint 3)
    ↓
Reddit Scraper
    ├─ Search r/solar for "Inverter X problems"
    ├─ Fetch posts + comments
    └─ Parse into Experience Nodes
    ↓
Friction Detector
    ├─ Compare AI triplet vs Human experiences
    ├─ Detect conflicts
    └─ Calculate friction score
    ↓
Consensus Scorer
    ├─ Weight by upvotes, expertise, recency
    ├─ Aggregate sentiment
    └─ Return consensus verdict
    ↓
Update SPO Confidence
    ├─ If confirmed → increase confidence
    ├─ If friction → decrease confidence
    └─ If conflict → flag for review
```

---

## 📦 Components to Implement

### 1. Reddit Scraper ⏳

**File:** `src/core/reddit_scraper.py`

**Purpose:** Scrape Reddit for human experiences related to SPO triplets.

**Key Features:**
- Reddit API integration (PRAW library)
- Search by keyword/subreddit
- Fetch posts + comments
- Rate limiting (Reddit: 60 requests/minute)
- Caching (avoid re-scraping same queries)

**Class Definition:**
```python
from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime
import praw  # Python Reddit API Wrapper


@dataclass
class RedditPost:
    """A Reddit post or comment."""
    post_id: str
    author: str
    subreddit: str
    title: str
    content: str
    upvotes: int
    downvotes: int
    created_at: datetime
    url: str
    comment_count: int
    is_comment: bool


class RedditScraper:
    """
    Scrape Reddit for human experiences.

    Usage:
        scraper = RedditScraper(
            client_id="...",
            client_secret="...",
            user_agent="SRO/1.0"
        )

        # Search for posts
        posts = scraper.search(
            query="solar inverter problems",
            subreddit="solar",
            limit=100,
            time_filter="year"
        )

        # Get top posts
        top_posts = scraper.get_top_posts(
            subreddit="solar",
            limit=50,
            time_filter="month"
        )
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        user_agent: str,
        enable_caching: bool = True,
        cache_ttl: int = 86400  # 24 hours
    ):
        """
        Initialize Reddit scraper.

        Args:
            client_id: Reddit API client ID
            client_secret: Reddit API secret
            user_agent: User agent string
            enable_caching: Cache search results
            cache_ttl: Cache time-to-live in seconds
        """
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        self.enable_caching = enable_caching
        self.cache_ttl = cache_ttl
        self._cache = {}  # query -> (results, timestamp)

    def search(
        self,
        query: str,
        subreddit: Optional[str] = None,
        limit: int = 100,
        time_filter: str = "year",  # hour, day, week, month, year, all
        sort: str = "relevance"     # relevance, hot, top, new
    ) -> List[RedditPost]:
        """
        Search Reddit for posts matching query.

        Args:
            query: Search query (e.g., "solar inverter problems")
            subreddit: Specific subreddit (e.g., "solar") or None for all
            limit: Maximum posts to return
            time_filter: Time range to search
            sort: Sort order

        Returns:
            List of RedditPost objects
        """
        # Check cache
        cache_key = f"{query}:{subreddit}:{time_filter}"
        if self.enable_caching and cache_key in self._cache:
            results, timestamp = self._cache[cache_key]
            if (datetime.now().timestamp() - timestamp) < self.cache_ttl:
                return results[:limit]

        # Perform search
        posts = []

        if subreddit:
            subreddit_obj = self.reddit.subreddit(subreddit)
            submissions = subreddit_obj.search(
                query=query,
                limit=limit,
                time_filter=time_filter,
                sort=sort
            )
        else:
            submissions = self.reddit.subreddit("all").search(
                query=query,
                limit=limit,
                time_filter=time_filter,
                sort=sort
            )

        for submission in submissions:
            post = RedditPost(
                post_id=submission.id,
                author=str(submission.author) if submission.author else "[deleted]",
                subreddit=str(submission.subreddit),
                title=submission.title,
                content=submission.selftext,
                upvotes=submission.score,
                downvotes=0,  # Reddit doesn't expose downvotes anymore
                created_at=datetime.fromtimestamp(submission.created_utc),
                url=f"https://reddit.com{submission.permalink}",
                comment_count=submission.num_comments,
                is_comment=False
            )
            posts.append(post)

        # Cache results
        if self.enable_caching:
            self._cache[cache_key] = (posts, datetime.now().timestamp())

        return posts

    def get_comments(self, post_id: str, limit: int = 50) -> List[RedditPost]:
        """Get comments for a post."""
        submission = self.reddit.submission(id=post_id)
        submission.comments.replace_more(limit=0)  # Flatten comment tree

        comments = []
        for comment in submission.comments.list()[:limit]:
            if hasattr(comment, 'body'):
                comment_obj = RedditPost(
                    post_id=comment.id,
                    author=str(comment.author) if comment.author else "[deleted]",
                    subreddit=str(submission.subreddit),
                    title="",  # Comments don't have titles
                    content=comment.body,
                    upvotes=comment.score,
                    downvotes=0,
                    created_at=datetime.fromtimestamp(comment.created_utc),
                    url=f"https://reddit.com{submission.permalink}{comment.id}/",
                    comment_count=0,
                    is_comment=True
                )
                comments.append(comment_obj)

        return comments
```

---

### 2. Experience Node Extractor ⏳

**File:** `src/core/experience_extractor.py`

**Purpose:** Convert Reddit posts into structured ExperienceNodes.

**Class Definition:**
```python
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import re

from src.core.model_orchestrator import ModelOrchestrator


@dataclass
class ExperienceNode:
    """A structured human experience extracted from social media."""

    # Source
    source: str  # "reddit", "hackernews", "forum"
    post_id: str
    author: str
    timestamp: datetime
    subreddit: Optional[str]

    # Content
    claim: str  # Core claim/statement
    sentiment: str  # "positive", "negative", "neutral"
    confidence: str  # "certain", "uncertain", "speculative"

    # Evidence
    evidence_type: str  # "personal_experience", "hearsay", "calculation"
    timeframe: Optional[str]  # "after 3 years", "since 2020"
    context: Dict[str, Any]  # Additional details

    # Credibility
    upvotes: int
    expertise_indicators: List[str]  # Technical terms, details
    account_age_days: Optional[int]
    quality_score: float  # 0.0-1.0


class ExperienceExtractor:
    """
    Extract structured experiences from Reddit posts.

    Uses LLM to parse unstructured text into ExperienceNode.
    """

    EXTRACTION_PROMPT_TEMPLATE = """Analyze the following social media post and extract structured experience:

Post:
{post_content}

Extract:
1. Core claim/statement (what is the main point?)
2. Sentiment (positive/negative/neutral)
3. Confidence level (certain/uncertain/speculative)
4. Evidence type (personal_experience/hearsay/calculation)
5. Timeframe (if mentioned, e.g., "after 3 years")
6. Relevant context details (product model, location, configuration, etc.)

Output as JSON:
{{
  "claim": "...",
  "sentiment": "positive|negative|neutral",
  "confidence": "certain|uncertain|speculative",
  "evidence_type": "personal_experience|hearsay|calculation",
  "timeframe": "..." or null,
  "context": {{...}}
}}

JSON Output:"""

    def __init__(self, model_orchestrator: ModelOrchestrator):
        self.llm = model_orchestrator

    def extract(self, post: 'RedditPost') -> Optional[ExperienceNode]:
        """
        Extract ExperienceNode from Reddit post.

        Args:
            post: RedditPost object

        Returns:
            ExperienceNode or None if extraction fails
        """
        # Use LLM to extract structured data
        prompt = self.EXTRACTION_PROMPT_TEMPLATE.format(
            post_content=post.title + "\n\n" + post.content
        )

        try:
            response = self.llm.generate(
                prompt=prompt,
                max_tokens=512,
                temperature=0.2  # Low temperature for consistent extraction
            )

            # Parse JSON from response
            import json
            data = json.loads(response.content)

            # Calculate expertise indicators
            expertise = self._detect_expertise(post.content)

            # Calculate quality score
            quality = self._calculate_quality(post, data)

            return ExperienceNode(
                source="reddit",
                post_id=post.post_id,
                author=post.author,
                timestamp=post.created_at,
                subreddit=post.subreddit,
                claim=data.get("claim", ""),
                sentiment=data.get("sentiment", "neutral"),
                confidence=data.get("confidence", "uncertain"),
                evidence_type=data.get("evidence_type", "hearsay"),
                timeframe=data.get("timeframe"),
                context=data.get("context", {}),
                upvotes=post.upvotes,
                expertise_indicators=expertise,
                account_age_days=None,  # Would need additional API call
                quality_score=quality
            )

        except Exception as e:
            print(f"Warning: Failed to extract experience from post {post.post_id}: {e}")
            return None

    def _detect_expertise(self, text: str) -> List[str]:
        """Detect technical terms indicating expertise."""
        technical_terms = {
            # Solar
            "MPPT", "inverter", "kWp", "kWh", "efficiency", "string",
            "shading", "DC", "AC", "grid", "feed-in tariff",
            # General tech
            "API", "firmware", "latency", "throughput", "bandwidth",
            "protocol", "encryption", "authentication"
        }

        found = []
        text_lower = text.lower()
        for term in technical_terms:
            if term.lower() in text_lower:
                found.append(term)

        return found

    def _calculate_quality(self, post: 'RedditPost', data: Dict) -> float:
        """Calculate quality score for experience."""
        score = 0.5  # Base score

        # Upvotes indicate community agreement
        if post.upvotes > 50:
            score += 0.2
        elif post.upvotes > 10:
            score += 0.1

        # Personal experience is more valuable
        if data.get("evidence_type") == "personal_experience":
            score += 0.2

        # Certainty adds credibility
        if data.get("confidence") == "certain":
            score += 0.1

        # Length (too short = vague, too long = rambling)
        word_count = len(post.content.split())
        if 50 < word_count < 300:
            score += 0.1

        # Has numbers/data
        if re.search(r'\d+(?:\.\d+)?\s*(?:kWh|EUR|%|years|months)', post.content):
            score += 0.1

        return min(1.0, max(0.0, score))
```

---

## 🧪 Testing Strategy

### Unit Tests
```
test_reddit_scraper.py
  ✓ Can connect to Reddit API
  ✓ Search returns results
  ✓ Caching works
  ✓ Rate limiting respected

test_experience_extractor.py
  ✓ Extracts claim from post
  ✓ Detects sentiment correctly
  ✓ Identifies expertise indicators
  ✓ Calculates quality score
```

### Integration Tests
```
test_sprint3_integration.py
  ✓ Full workflow: Search → Extract → Store
  ✓ Friction detection works
  ✓ Consensus calculation correct
```

---

## 📊 Success Criteria

Sprint 3 is COMPLETE when:

- [⏳] RedditScraper can search and fetch posts
- [⏳] ExperienceExtractor parses posts into ExperienceNodes
- [⏳] FrictionDetector compares AI vs Human
- [⏳] ConsensusScorer calculates weighted consensus
- [⏳] Integration with SPO database
- [⏳] All tests passing

---

## 🚀 Next Steps

1. Install dependencies (praw)
2. Setup Reddit API credentials
3. Implement RedditScraper
4. Implement ExperienceExtractor
5. Implement FrictionDetector
6. Implement ConsensusScorer
7. Integration tests

---

*Sprint 3 Implementation Plan*
*Created: 2026-01-16*
*Next: Begin implementation*
