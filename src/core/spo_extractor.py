"""
SPO Extractor - LLM-based Subject-Predicate-Object triplet extraction.

Part of Cluster 1: Foundations (SRO Implementation)
Extracts structured knowledge from unstructured text responses.

Design Philosophy:
- LLM-based (not regex/NER) for semantic understanding
- Multiple triplets per text
- Confidence scoring per triplet
- Provenance tracking
"""

import json
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime

from src.models.unified_session import SPOTriplet, SPOProvenance
from src.core.model_orchestrator import ModelOrchestrator, ModelCapability, QualityLevel


class SPOExtractor:
    """
    Extract SPO tripletts from natural language text using LLM.

    Process:
    1. Send text + extraction prompt to LLM
    2. Parse structured JSON response
    3. Create SPOTriplet instances with provenance
    4. Return list of tripletts (Bronze tier by default)

    Usage:
        extractor = SPOExtractor(model_orchestrator)

        text = "Die Solaranlage hat eine ROI-Periode von 15-20 Jahren."
        triplets = extractor.extract_from_text(text, context={
            "source_id": "response_123",
            "node_id": "tot_node_456"
        })

        # Result:
        # [
        #   SPOTriplet(subject="Solaranlage", predicate="ROI-Periode", object="15-20 Jahre", ...)
        # ]
    """

    # Extraction prompt template (optimized for DeepSeek-R1)
    EXTRACTION_PROMPT = """Task: Extract facts from text as JSON triplets.

Text to analyze:
{text}

Instructions:
1. Extract key facts as Subject-Predicate-Object triplets
2. Subject = main entity, Predicate = relationship, Object = value
3. Assign confidence 0.0-1.0 for each fact
4. Return ONLY valid JSON array, no other text

Format (strict JSON array):
[{{"subject": "entity", "predicate": "relation", "object": "value", "confidence": 0.8}}]

Example:
Input: "Solar panels reduce CO2 emissions by up to 95%."
Output: [{{"subject": "solar panels", "predicate": "reduce", "object": "CO2 emissions", "confidence": 0.9}}, {{"subject": "CO2 reduction", "predicate": "percentage", "object": "95%", "confidence": 0.85}}]

Now extract from the text above. Return ONLY the JSON array:"""

    def __init__(
        self,
        model_orchestrator: ModelOrchestrator,
        min_confidence: float = 0.5,
        max_triplets: int = 20
    ):
        """
        Initialize SPO Extractor.

        Args:
            model_orchestrator: LLM orchestrator for extraction
            min_confidence: Minimum confidence threshold (discard below this)
            max_triplets: Maximum tripletts to extract per text
        """
        self.llm = model_orchestrator
        self.min_confidence = min_confidence
        self.max_triplets = max_triplets

    def extract_from_text(
        self,
        text: str,
        context: Optional[Dict[str, Any]] = None,
        quality: QualityLevel = QualityLevel.BALANCED
    ) -> List[SPOTriplet]:
        """
        Extract SPO tripletts from text.

        Args:
            text: Natural language text to extract from
            context: Optional context dict with source_id, node_id, etc.
            quality: LLM quality level (FAST/BALANCED/QUALITY)

        Returns:
            List of SPOTriplet instances (Bronze tier)

        Example:
            context = {
                "source_id": "response_123",
                "node_id": "tot_node_456",
                "model_used": "deepseek-r1-14b"
            }
        """
        if not text or len(text.strip()) < 10:
            return []  # Text too short

        context = context or {}

        try:
            # Generate extraction prompt
            prompt = self.EXTRACTION_PROMPT.format(text=text[:2000])  # Limit to 2k chars

            # Debug: Show input
            print(f"[SPO Debug] Input text length: {len(text)}, first 200 chars: {text[:200]}")

            # Call LLM
            response = self.llm.generate(
                prompt=prompt,
                capability=ModelCapability.EXTRACTION,
                quality=quality
            )

            # Debug: Show what LLM returned
            print(f"[SPO Debug] LLM response length: {len(response.content)}, first 300 chars: {response.content[:300]}")

            # Parse JSON response
            triplets = self._parse_json_response(response.content)

            # Convert to SPOTriplet instances
            spo_triplets = []
            for i, triplet_data in enumerate(triplets[:self.max_triplets]):
                # Validate confidence
                confidence = triplet_data.get("confidence", 0.5)
                if confidence < self.min_confidence:
                    continue  # Skip low-confidence tripletts

                # Create SPOTriplet
                spo_triplet = SPOTriplet(
                    id=f"spo_{uuid.uuid4().hex[:12]}",
                    subject=triplet_data["subject"],
                    predicate=triplet_data["predicate"],
                    object=triplet_data["object"],
                    confidence=confidence,
                    tier="bronze",  # All extracted tripletts start as Bronze
                    provenance=SPOProvenance(
                        source_id=context.get("source_id", "unknown"),
                        extraction_method="llm_structured",
                        model_used=context.get("model_used") or response.model_used,
                        extracted_at=datetime.utcnow().isoformat(),
                        verified=False,
                        verification_count=0,
                        verification_sources=[]
                    ),
                    created_at=datetime.utcnow().isoformat(),
                    metadata={
                        "extraction_context": context,
                        "original_text_length": len(text),
                        "extraction_index": i
                    }
                )

                spo_triplets.append(spo_triplet)

            return spo_triplets

        except Exception as e:
            print(f"SPO extraction failed: {e}")
            return []

    def _parse_json_response(self, response_text: str) -> List[Dict[str, Any]]:
        """
        Parse LLM JSON response to list of triplett dicts.

        Handles:
        - Clean JSON arrays
        - JSON with extra text around it
        - Malformed JSON (attempts cleanup)
        - Code blocks (```json ... ```)

        Returns:
            List of triplett dicts
        """
        import re

        # Remove code block markers if present
        response_text = re.sub(r'```[\w]*\n?', '', response_text)
        response_text = response_text.strip()

        # Try direct JSON parse
        try:
            data = json.loads(response_text.strip())
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and "triplets" in data:
                return data["triplets"]
            else:
                return []
        except json.JSONDecodeError:
            pass

        # Try to extract JSON from text
        try:
            # Find JSON array in response
            start = response_text.find("[")
            end = response_text.rfind("]") + 1

            if start != -1 and end > start:
                json_str = response_text[start:end]
                data = json.loads(json_str)
                if isinstance(data, list):
                    return data
        except json.JSONDecodeError as e:
            # Debug output
            print(f"SPO extraction failed: {str(e)[:50]}")
            pass

        # Last resort: line-by-line parsing (if LLM didn't use JSON)
        return self._parse_text_fallback(response_text)

    def _parse_text_fallback(self, response_text: str) -> List[Dict[str, Any]]:
        """
        Fallback parser for non-JSON responses.

        Attempts to extract tripletts from plain text format like:
        - Subject: X, Predicate: Y, Object: Z, Confidence: 0.8
        """
        triplets = []
        lines = response_text.strip().split('\n')

        current_triplet = {}
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Look for key-value pairs
            for key in ["subject", "predicate", "object", "confidence"]:
                if key.lower() in line.lower():
                    parts = line.split(":", 1)
                    if len(parts) == 2:
                        value = parts[1].strip().strip(',').strip('"')
                        current_triplet[key] = value

            # If we have all required fields, save triplet
            if len(current_triplet) >= 3:  # At least subject, predicate, object
                # Convert confidence to float
                if "confidence" in current_triplet:
                    try:
                        current_triplet["confidence"] = float(current_triplet["confidence"])
                    except:
                        current_triplet["confidence"] = 0.5
                else:
                    current_triplet["confidence"] = 0.5

                triplets.append(current_triplet)
                current_triplet = {}

        return triplets

    def extract_batch(
        self,
        texts: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> List[SPOTriplet]:
        """
        Extract tripletts from multiple texts.

        Args:
            texts: List of text strings
            context: Shared context for all texts

        Returns:
            Combined list of SPOTriplet instances
        """
        all_triplets = []

        for i, text in enumerate(texts):
            # Add text index to context
            text_context = context.copy() if context else {}
            text_context["batch_index"] = i

            triplets = self.extract_from_text(text, context=text_context)
            all_triplets.extend(triplets)

        return all_triplets

    def validate_triplet(self, triplet: SPOTriplet) -> bool:
        """
        Validate if triplet is well-formed.

        Checks:
        - Subject, predicate, object not empty
        - Confidence in range [0, 1]
        - No duplicate values (subject != object)

        Returns:
            True if valid
        """
        # Check non-empty
        if not triplet.subject or not triplet.predicate or not triplet.object:
            return False

        # Check confidence range
        if not 0.0 <= triplet.confidence <= 1.0:
            return False

        # Check not duplicate (optional)
        if triplet.subject.lower() == triplet.object.lower():
            # Allow same value if different case or whitespace
            if triplet.subject == triplet.object:
                return False

        # Check minimum length
        if len(triplet.subject) < 2 or len(triplet.object) < 2:
            return False

        return True

    def get_stats(self) -> Dict[str, Any]:
        """
        Get extraction statistics.

        Returns:
            Stats dict (can be extended for production use)
        """
        return {
            "min_confidence": self.min_confidence,
            "max_triplets": self.max_triplets,
            "extraction_method": "llm_structured"
        }
