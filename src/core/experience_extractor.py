"""
Experience Extractor - Convert Reddit posts to structured ExperienceNodes

Part of Sprint 3: Verification Layer (Gemini's Original Plan)

Extracts structured human experiences from unstructured social media text.
Uses simple rule-based extraction (can be enhanced with LLM later).
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import re


@dataclass
class ExperienceNode:
    """
    A structured human experience extracted from social media.

    This represents one person's real-world experience that can be
    compared against AI-generated hypotheses.
    """

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
    expertise_indicators: List[str]  # Technical terms found
    quality_score: float  # 0.0-1.0


class ExperienceExtractor:
    """
    Extract structured experiences from Reddit posts.

    Uses rule-based extraction for speed.
    Can be enhanced with LLM for better accuracy later.

    Usage:
        extractor = ExperienceExtractor()

        post = RedditPost(...)
        experience = extractor.extract(post)

        if experience:
            print(f"Claim: {experience.claim}")
            print(f"Sentiment: {experience.sentiment}")
            print(f"Quality: {experience.quality_score:.2f}")
    """

    # Technical terms that indicate expertise
    TECHNICAL_TERMS = {
        # Solar/Energy
        "MPPT", "inverter", "kWp", "kWh", "efficiency", "string",
        "shading", "DC", "AC", "grid", "feed-in tariff", "firmware",
        "voltage", "current", "wattage", "panel", "array",
        # General tech
        "API", "latency", "throughput", "bandwidth",
        "protocol", "encryption", "authentication",
        # Quality indicators
        "study", "research", "data", "analysis", "test", "measurement"
    }

    # Sentiment keywords
    POSITIVE_KEYWORDS = {
        "excellent", "great", "amazing", "flawless", "recommend",
        "reliable", "perfect", "best", "love", "happy", "satisfied",
        "works well", "no issues", "no problems"
    }

    NEGATIVE_KEYWORDS = {
        "terrible", "awful", "failed", "died", "broken", "issue",
        "problem", "unreliable", "worst", "hate", "disappointed",
        "unhappy", "don't recommend", "avoid", "warning"
    }

    # Confidence indicators
    CERTAIN_KEYWORDS = {
        "definitely", "certainly", "absolutely", "confirmed",
        "proven", "verified", "measured", "tested"
    }

    UNCERTAIN_KEYWORDS = {
        "maybe", "probably", "perhaps", "I think", "I believe",
        "seems", "appears", "might", "could"
    }

    # Evidence type indicators
    PERSONAL_EXPERIENCE_KEYWORDS = {
        "my", "mine", "I have", "I had", "I own", "I bought",
        "I installed", "I tested", "personal experience"
    }

    HEARSAY_KEYWORDS = {
        "I heard", "someone said", "friend told", "read somewhere",
        "apparently", "supposedly"
    }

    def extract(self, post: 'RedditPost') -> Optional[ExperienceNode]:
        """
        Extract ExperienceNode from Reddit post.

        Args:
            post: RedditPost object

        Returns:
            ExperienceNode or None if extraction fails
        """
        try:
            # Combine title and content
            full_text = f"{post.title}\n\n{post.content}".strip()

            if not full_text or len(full_text) < 10:
                return None

            # Extract components
            claim = self._extract_claim(full_text, post.title)
            sentiment = self._detect_sentiment(full_text)
            confidence = self._detect_confidence(full_text)
            evidence_type = self._detect_evidence_type(full_text)
            timeframe = self._extract_timeframe(full_text)
            context = self._extract_context(full_text, post)
            expertise = self._detect_expertise(full_text)
            quality = self._calculate_quality(post, sentiment, confidence, evidence_type, expertise, full_text)

            return ExperienceNode(
                source="reddit",
                post_id=post.post_id,
                author=post.author,
                timestamp=post.created_at,
                subreddit=post.subreddit,
                claim=claim,
                sentiment=sentiment,
                confidence=confidence,
                evidence_type=evidence_type,
                timeframe=timeframe,
                context=context,
                upvotes=post.upvotes,
                expertise_indicators=expertise,
                quality_score=quality
            )

        except Exception as e:
            print(f"Warning: Failed to extract experience from post {post.post_id}: {e}")
            return None

    def _extract_claim(self, text: str, title: str) -> str:
        """Extract main claim from text."""
        # Use title if it's substantial, otherwise first sentence
        if title and len(title) > 20:
            return title.strip()

        # Otherwise, first substantial sentence
        sentences = text.split('.')
        for sent in sentences:
            sent = sent.strip()
            if len(sent) > 20:
                return sent + "."

        return text[:200].strip()  # Fallback: first 200 chars

    def _detect_sentiment(self, text: str) -> str:
        """Detect sentiment: positive, negative, or neutral."""
        text_lower = text.lower()

        # Count positive and negative keywords
        positive_count = sum(1 for keyword in self.POSITIVE_KEYWORDS if keyword in text_lower)
        negative_count = sum(1 for keyword in self.NEGATIVE_KEYWORDS if keyword in text_lower)

        # Determine sentiment
        if negative_count > positive_count + 1:
            return "negative"
        elif positive_count > negative_count + 1:
            return "positive"
        else:
            return "neutral"

    def _detect_confidence(self, text: str) -> str:
        """Detect confidence level: certain, uncertain, or speculative."""
        text_lower = text.lower()

        # Check for uncertainty first (it's usually more explicit)
        if any(keyword in text_lower for keyword in self.UNCERTAIN_KEYWORDS):
            return "speculative"

        # Check for certainty
        if any(keyword in text_lower for keyword in self.CERTAIN_KEYWORDS):
            return "certain"

        # Default: uncertain (neutral confidence)
        return "uncertain"

    def _detect_evidence_type(self, text: str) -> str:
        """Detect type of evidence: personal_experience, hearsay, or calculation."""
        text_lower = text.lower()

        # Personal experience is most valuable
        if any(keyword in text_lower for keyword in self.PERSONAL_EXPERIENCE_KEYWORDS):
            return "personal_experience"

        # Hearsay is less valuable
        if any(keyword in text_lower for keyword in self.HEARSAY_KEYWORDS):
            return "hearsay"

        # Check for data/calculations
        if any(word in text_lower for word in ["data", "research", "study", "statistics", "analysis"]):
            return "calculation"

        # Default: assume personal experience if they're making specific claims
        if any(word in text_lower for word in ["failed", "died", "broke", "works", "installed"]):
            return "personal_experience"

        return "hearsay"  # Conservative default

    def _extract_timeframe(self, text: str) -> Optional[str]:
        """Extract timeframe mentions like 'after 3 years'."""
        # Pattern: "after X years", "in X months", "since YYYY"
        patterns = [
            r'after (\d+) (?:years?|months?|days?)',
            r'in (\d+) (?:years?|months?|days?)',
            r'since (\d{4})',
            r'for (\d+) (?:years?|months?)'
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)

        return None

    def _extract_context(self, text: str, post: 'RedditPost') -> Dict[str, Any]:
        """Extract contextual details (product models, locations, etc.)."""
        context = {}

        # Extract model numbers (e.g., "SolarEdge-5000")
        model_match = re.search(r'([A-Z][a-z]+(?:Edge|Max|Pro)?[-\s]\d+)', text)
        if model_match:
            context['model'] = model_match.group(1)

        # Extract costs (€1234 or $1234)
        cost_match = re.search(r'[€$](\d+(?:,\d{3})*(?:\.\d{2})?)', text)
        if cost_match:
            context['cost'] = cost_match.group(0)

        # Extract percentages (95%)
        percentage_matches = re.findall(r'(\d+(?:\.\d+)?%)', text)
        if percentage_matches:
            context['percentages'] = percentage_matches

        # Subreddit is context
        if post.subreddit:
            context['subreddit'] = post.subreddit

        return context

    def _detect_expertise(self, text: str) -> List[str]:
        """Detect technical terms indicating expertise."""
        found_terms = []
        text_lower = text.lower()

        for term in self.TECHNICAL_TERMS:
            if term.lower() in text_lower:
                found_terms.append(term)

        return found_terms

    def _calculate_quality(
        self,
        post: 'RedditPost',
        sentiment: str,
        confidence: str,
        evidence_type: str,
        expertise: List[str],
        text: str
    ) -> float:
        """
        Calculate quality score (0.0-1.0).

        Higher quality = more trustworthy experience.
        """
        score = 0.5  # Base score

        # Factor 1: Upvotes (community agreement)
        if post.upvotes > 100:
            score += 0.2
        elif post.upvotes > 50:
            score += 0.15
        elif post.upvotes > 10:
            score += 0.1

        # Factor 2: Evidence type
        if evidence_type == "personal_experience":
            score += 0.15
        elif evidence_type == "calculation":
            score += 0.1
        elif evidence_type == "hearsay":
            score -= 0.1

        # Factor 3: Confidence
        if confidence == "certain":
            score += 0.1
        elif confidence == "speculative":
            score -= 0.1

        # Factor 4: Expertise indicators
        score += min(len(expertise) * 0.05, 0.2)  # Max +0.2 for expertise

        # Factor 5: Text length (too short = vague, too long = rambling)
        word_count = len(text.split())
        if 50 < word_count < 300:
            score += 0.1
        elif word_count < 20:
            score -= 0.1

        # Factor 6: Has concrete numbers/data
        if re.search(r'\d+(?:\.\d+)?\s*(?:kWh|EUR|%|years|months)', text):
            score += 0.1

        # Factor 7: Specific subreddit (r/solar is more relevant than r/funny)
        if post.subreddit in ["solar", "homeimprovement", "diy", "renewable"]:
            score += 0.1

        # Clamp to 0.0-1.0
        return min(1.0, max(0.0, score))
