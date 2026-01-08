"""
Research Generator Service

This service generates research structures dynamically using local LLM prompting.
It uses generic techniques to analyze user input and create customized research workflows.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

# Make tiktoken optional (only needed for non-mock mode)
try:
    import tiktoken
    HAS_TIKTOKEN = True
except ImportError:
    HAS_TIKTOKEN = False

from src.models.llama_cpp_client import LlamaCppClient

logger = logging.getLogger(__name__)


class ResearchGenerator:
    """
    Generates research structures using meta-workflow patterns.

    This service:
    1. Uses thematic_structure_detector to identify research areas
    2. Uses prompt_customizer to generate custom prompts for each area
    3. Saves complete research structures to config/researches/
    """

    def __init__(self, use_mock: bool = True):
        self.config_dir = Path("config")
        self.techniques_dir = self.config_dir / "techniques"
        self.researches_dir = self.config_dir / "researches"
        self.model_config = "config/models/tier1_fast.json"
        self.use_mock = use_mock

        # Initialize model client ONLY if not in mock mode
        if not use_mock:
            self.model = LlamaCppClient(self.model_config)
        else:
            self.model = None
            logger.info("ResearchGenerator initialized in MOCK MODE - no model client created")

        # Load generic techniques
        self.generic_techniques = self._load_generic_techniques()

        # Token counter (only in non-mock mode)
        if not use_mock and HAS_TIKTOKEN:
            self.encoding = tiktoken.get_encoding("cl100k_base")
        else:
            self.encoding = None

    def _load_generic_techniques(self) -> Dict[str, Dict]:
        """Load all generic techniques from config/techniques/"""
        techniques = {}

        if not self.techniques_dir.exists():
            logger.warning(f"Techniques directory not found: {self.techniques_dir}")
            return techniques

        for technique_file in self.techniques_dir.rglob("*.json"):
            try:
                with open(technique_file, 'r', encoding='utf-8') as f:
                    technique = json.load(f)
                    if technique.get("is_generic", False):
                        technique_id = technique.get("technique_id")
                        techniques[technique_id] = technique
                        logger.info(f"Loaded generic technique: {technique_id}")
            except Exception as e:
                logger.error(f"Error loading technique {technique_file}: {e}")

        return techniques

    def _count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        if self.encoding is not None:
            return len(self.encoding.encode(text))
        else:
            # Rough approximation when tiktoken not available
            return len(text.split()) * 1.3  # ~1.3 tokens per word

    def _build_prompt_from_template(self, technique: Dict, variables: Dict[str, Any]) -> str:
        """Build a prompt from technique template with variable substitution"""
        template = technique.get("prompt_template", {})
        sections = template.get("sections", {})

        # Build prompt from sections
        prompt_parts = []

        if "context" in sections:
            context = sections["context"]
            # Replace variables
            for key, value in variables.items():
                context = context.replace(f"{{{{{key}}}}}", str(value))
            prompt_parts.append(context)

        if "input" in sections and "user_input" in variables:
            prompt_parts.append(f"\nInput:\n{variables['user_input']}")

        if "task" in sections:
            task = sections["task"]
            for key, value in variables.items():
                task = task.replace(f"{{{{{key}}}}}", str(value))
            prompt_parts.append(f"\nTask:\n{task}")

        if "output_format" in sections:
            prompt_parts.append(f"\nOutput Format:\n{sections['output_format']}")

        if "quality_criteria" in sections:
            prompt_parts.append(f"\nQuality Criteria:\n{sections['quality_criteria']}")

        if "examples" in sections:
            prompt_parts.append(f"\nExamples:\n{sections['examples']}")

        return "\n".join(prompt_parts)

    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Extract and parse JSON from LLM response"""
        # Try to find JSON block
        start_idx = response.find('{')
        end_idx = response.rfind('}')

        if start_idx == -1 or end_idx == -1:
            raise ValueError("No JSON found in response")

        json_str = response[start_idx:end_idx + 1]

        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            logger.error(f"Response: {json_str[:500]}...")
            raise

    def generate_thematic_structure(
        self,
        user_input: str,
        research_goal: str,
        research_type: str = "product"
    ) -> Dict[str, Any]:
        """
        Generate thematic structure for research using local LLM with critical analysis.

        Args:
            user_input: User's research description
            research_goal: User's explicit goal/objective
            research_type: Type of research (product, market, etc.)

        Returns:
            Dictionary with thematic hierarchy optimized for deep research
        """
        logger.info(f"Generating thematic structure for goal: {research_goal[:100]}...")

        # MOCK MODE: Use instance variable (set in __init__)
        if self.use_mock:
            logger.info("Using MOCK data for testing (TinyLlama too small for JSON)")
            # HIERARCHICAL THEMATIC STRUCTURE with RELEVANCE SCORES
            return {
                "thematic_hierarchy": [
                    {
                        "theme_id": "market_analysis",
                        "theme_name": "Marktanalyse",
                        "description": "Umfassende Analyse des Fitness-App-Marktes",
                        "relevance_score": 95,
                        "confidence": 0.92,
                        "sub_themes": [
                            {
                                "theme_id": "target_groups",
                                "theme_name": "Zielgruppen",
                                "description": "Identifikation und Segmentierung potentieller Nutzer",
                                "relevance_score": 90,
                                "confidence": 0.88,
                                "sub_themes": [
                                    {
                                        "theme_id": "hobby_athletes",
                                        "theme_name": "Hobbysportler",
                                        "description": "Casual Fitness-Enthusiasten",
                                        "relevance_score": 85,
                                        "confidence": 0.90,
                                        "sub_themes": []
                                    },
                                    {
                                        "theme_id": "professional_athletes",
                                        "theme_name": "Profisportler",
                                        "description": "Leistungsorientierte Athleten",
                                        "relevance_score": 60,
                                        "confidence": 0.70,
                                        "sub_themes": []
                                    },
                                    {
                                        "theme_id": "health_conscious",
                                        "theme_name": "Gesundheitsbewusste",
                                        "description": "Nutzer mit Fokus auf Gesundheit",
                                        "relevance_score": 75,
                                        "confidence": 0.85,
                                        "sub_themes": []
                                    }
                                ]
                            },
                            {
                                "theme_id": "market_size",
                                "theme_name": "Marktgröße & Wachstum",
                                "description": "Analyse der Marktgröße und Wachstumspotenzial",
                                "relevance_score": 95,
                                "confidence": 0.95,
                                "sub_themes": [
                                    {
                                        "theme_id": "global_market",
                                        "theme_name": "Globaler Markt",
                                        "description": "Weltweite Marktgröße",
                                        "relevance_score": 80,
                                        "confidence": 0.85,
                                        "sub_themes": []
                                    },
                                    {
                                        "theme_id": "regional_markets",
                                        "theme_name": "Regionale Märkte",
                                        "description": "DACH, USA, Asien",
                                        "relevance_score": 85,
                                        "confidence": 0.90,
                                        "sub_themes": []
                                    }
                                ]
                            },
                            {
                                "theme_id": "competition",
                                "theme_name": "Wettbewerbsanalyse",
                                "description": "Bestehende Fitness-Apps und ihre Features",
                                "relevance_score": 88,
                                "confidence": 0.92,
                                "sub_themes": []
                            }
                        ]
                    },
                    {
                        "theme_id": "technology",
                        "theme_name": "Technologie & Umsetzung",
                        "description": "Technische Anforderungen und Machbarkeit",
                        "relevance_score": 90,
                        "confidence": 0.90,
                        "sub_themes": [
                            {
                                "theme_id": "sensors_hardware",
                                "theme_name": "Sensoren & Hardware",
                                "description": "Integration mit Wearables und Sensoren",
                                "relevance_score": 95,
                                "confidence": 0.93,
                                "sub_themes": [
                                    {
                                        "theme_id": "heart_rate",
                                        "theme_name": "Herzfrequenz-Messung",
                                        "relevance_score": 90,
                                        "confidence": 0.95,
                                        "sub_themes": []
                                    },
                                    {
                                        "theme_id": "gps_tracking",
                                        "theme_name": "GPS-Tracking",
                                        "relevance_score": 85,
                                        "confidence": 0.90,
                                        "sub_themes": []
                                    }
                                ]
                            },
                            {
                                "theme_id": "data_privacy",
                                "theme_name": "Datenschutz & DSGVO",
                                "description": "Rechtliche Anforderungen an Gesundheitsdaten",
                                "relevance_score": 92,
                                "confidence": 0.95,
                                "sub_themes": []
                            },
                            {
                                "theme_id": "platform_apis",
                                "theme_name": "Plattform-APIs",
                                "description": "iOS HealthKit, Android Health Connect",
                                "relevance_score": 85,
                                "confidence": 0.88,
                                "sub_themes": []
                            }
                        ]
                    },
                    {
                        "theme_id": "business_model",
                        "theme_name": "Geschäftsmodell",
                        "description": "Monetarisierung und Revenue Streams",
                        "relevance_score": 78,
                        "confidence": 0.80,
                        "sub_themes": [
                            {
                                "theme_id": "subscription",
                                "theme_name": "Abo-Modell",
                                "description": "Monatliche/Jährliche Subscriptions",
                                "relevance_score": 85,
                                "confidence": 0.88,
                                "sub_themes": []
                            },
                            {
                                "theme_id": "freemium",
                                "theme_name": "Freemium-Strategie",
                                "description": "Basis gratis, Premium Features kostenpflichtig",
                                "relevance_score": 90,
                                "confidence": 0.90,
                                "sub_themes": []
                            }
                        ]
                    }
                ],
                "metadata": {
                    "total_themes": 15
                }
            }

        # REAL LLM MODE (uses critical_theme_analyzer for goal-oriented analysis)
        analyzer_path = self.techniques_dir / "research_creation" / "critical_theme_analyzer.json"
        if not analyzer_path.exists():
            raise FileNotFoundError(f"Critical theme analyzer not found: {analyzer_path}")

        with open(analyzer_path, 'r', encoding='utf-8') as f:
            analyzer = json.load(f)

        variables = {
            "user_input": user_input,
            "research_goal": research_goal,
            "research_type": research_type
        }

        prompt = self._build_prompt_from_template(analyzer, variables)
        logger.info(f"Prompt tokens: {self._count_tokens(prompt)}")

        temperature = analyzer.get("temperature", 0.4)
        max_tokens = analyzer.get("max_tokens", 3000)

        response = self.model.generate(
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )

        result = self._parse_json_response(response)
        logger.info(f"Generated {len(result.get('thematic_areas', []))} thematic areas")

        return result

    def detect_blindspots(
        self,
        thematic_hierarchy: List[Dict[str, Any]],
        user_context: str
    ) -> Dict[str, Any]:
        """
        Detect missing themes/blindspots in the thematic structure.

        Uses blindspot detection technique to find gaps.

        Args:
            thematic_hierarchy: Current thematic structure
            user_context: Original research context

        Returns:
            Dictionary with identified blindspots and suggestions
        """
        logger.info("Running blindspot detection...")

        # MOCK MODE: Use instance variable (set in __init__)
        if self.use_mock:
            logger.info("Using MOCK blindspot detection")
            return {
                "blindspots_detected": [
                    {
                        "blindspot_id": "user_retention",
                        "theme_name": "Nutzer-Retention & Engagement",
                        "description": "Strategien zur langfristigen Nutzerbindung fehlen",
                        "severity": "high",
                        "relevance_score": 88,
                        "suggested_sub_themes": [
                            "Gamification",
                            "Social Features",
                            "Push-Notifications"
                        ]
                    },
                    {
                        "blindspot_id": "accessibility",
                        "theme_name": "Barrierefreiheit",
                        "description": "Zugänglichkeit für Menschen mit Einschränkungen",
                        "severity": "medium",
                        "relevance_score": 65,
                        "suggested_sub_themes": [
                            "Screen Reader Support",
                            "Farbkontraste",
                            "Voice Control"
                        ]
                    },
                    {
                        "blindspot_id": "content_moderation",
                        "theme_name": "Community & Content Moderation",
                        "description": "Falls Social Features: Moderation nötig",
                        "severity": "medium",
                        "relevance_score": 55,
                        "suggested_sub_themes": []
                    }
                ],
                "coverage_improvement": "85%",
                "recommendation": "Füge 'Nutzer-Retention' als Hauptthema hinzu"
            }

        # REAL LLM MODE
        # TODO: Implement with blindspot_detection technique
        return {"blindspots_detected": [], "status": "not_implemented"}

    def expand_theme(
        self,
        theme: Dict[str, Any],
        expansion_depth: int = 2
    ) -> Dict[str, Any]:
        """
        Expand a single theme into sub-themes.

        Args:
            theme: Theme to expand
            expansion_depth: How deep to expand

        Returns:
            Expanded theme with new sub_themes
        """
        logger.info(f"Expanding theme: {theme.get('theme_name')}")

        # MOCK MODE: Use instance variable (set in __init__)
        if self.use_mock:
            # Mock: Just return theme as-is for now
            return theme

        # REAL LLM MODE
        # TODO: Use theme_expander technique
        return theme

    def generate_deep_research_prompts(
        self,
        selected_themes: List[Dict[str, Any]],
        research_context: str
    ) -> Dict[str, Any]:
        """
        Generate comprehensive research prompts for big models (GPT-4, Claude).

        This is the final output: prompts to be sent to external AIs.

        Args:
            selected_themes: User-selected themes from hierarchy
            research_context: Original research goal

        Returns:
            Dictionary with deep research prompts for each theme
        """
        logger.info(f"Generating deep research prompts for {len(selected_themes)} themes...")

        # MOCK MODE: Use instance variable (set in __init__)
        if self.use_mock:
            logger.info("Using MOCK deep research prompts")
            prompts = {}

            for theme in selected_themes:
                theme_id = theme.get("theme_id", "")
                theme_name = theme.get("theme_name", "")

                prompts[theme_id] = {
                    "prompt_title": f"Deep Research: {theme_name}",
                    "comprehensive_prompt": f"""# FORSCHUNGSAUFTRAG: {theme_name}

## KONTEXT
Sie führen eine umfassende Recherche für: {research_context}

Speziell zu untersuchen: {theme.get('description', '')}

## AUFGABE
Erstellen Sie eine detaillierte Analyse zu folgendem Thema:
**{theme_name}**

## ZU BEANTWORTENDE FRAGEN

1. **Aktueller Stand**: Was ist der aktuelle Stand in diesem Bereich?
2. **Trends & Entwicklungen**: Welche Trends zeichnen sich ab?
3. **Best Practices**: Was sind bewährte Vorgehensweisen?
4. **Herausforderungen**: Welche Schwierigkeiten sind zu erwarten?
5. **Chancen**: Welche Möglichkeiten bieten sich?

## ERWARTETE AUSGABE

Strukturierter Bericht mit:
- Executive Summary (2-3 Absätze)
- Detaillierte Analyse (min. 500 Wörter)
- Konkrete Handlungsempfehlungen
- Quellenangaben

## QUALITÄTSKRITERIEN

- ✅ Aktualität (bevorzugt Quellen aus 2024-2025)
- ✅ Tiefe (nicht nur Oberflächliches)
- ✅ Praxisrelevanz (konkret umsetzbar)
- ✅ Kritische Perspektive (auch Risiken benennen)

---

**Hinweis**: Nutzen Sie abliterated Models für unzensierte Einschätzungen, insbesondere bei:
- Risikobewertungen
- Marktchancen
- Konkurrenzsituation
- Regulatorische Grauzonen
""",
                    "target_models": ["claude-opus", "gpt-4", "gemini-pro"],
                    "estimated_tokens": 3000,
                    "priority": theme.get("relevance_score", 50)
                }

            return {
                "prompts": prompts,
                "total_prompts": len(prompts),
                "status": "success"
            }

        # REAL LLM MODE
        # TODO: Use deep_research_prompt_generator technique
        return {"prompts": {}, "status": "not_implemented"}

    def generate_custom_prompts(
        self,
        thematic_areas: List[Dict[str, Any]],
        research_context: str
    ) -> Dict[str, Any]:
        """
        Generate custom prompts for each thematic area.

        Args:
            thematic_areas: List of thematic areas from structure detection
            research_context: Original research context

        Returns:
            Dictionary mapping area IDs to customized prompts
        """
        logger.info(f"Generating custom prompts for {len(thematic_areas)} areas...")

        # MOCK MODE: Use instance variable (set in __init__)
        if self.use_mock:
            logger.info("Using MOCK custom prompts for testing")
            mock_prompts = {}

            for area in thematic_areas:
                area_id = area.get("area_id", "")
                area_name = area.get("area_name", "")
                techniques = area.get("techniques", [])

                for technique_spec in techniques:
                    technique_id = technique_spec.get("technique_id")
                    prompt_key = f"{area_id}_{technique_id}"

                    mock_prompts[prompt_key] = {
                        "sections": {
                            "context": f"Sie analysieren: {area_name} im Kontext von {research_context}",
                            "task": f"Führen Sie {technique_id} durch für {area_name}",
                            "output_format": "Strukturierte Markdown-Ausgabe mit klaren Abschnitten",
                            "quality_criteria": "Vollständigkeit, Relevanz, Aktualität"
                        },
                        "customization_notes": f"Angepasst für {area_name}"
                    }

            return {
                "custom_prompts": mock_prompts,
                "status": "success"
            }

        # Load prompt_customizer technique
        customizer_path = self.techniques_dir / "research_creation" / "prompt_customizer.json"

        if not customizer_path.exists():
            raise FileNotFoundError(f"Technique not found: {customizer_path}")

        with open(customizer_path, 'r', encoding='utf-8') as f:
            customizer = json.load(f)

        custom_prompts = {}

        for area in thematic_areas:
            area_id = area.get("area_id", "")
            area_name = area.get("area_name", "")
            techniques = area.get("techniques", [])

            logger.info(f"Customizing prompts for area: {area_name}")

            # For each technique in the area
            for technique_spec in techniques:
                technique_id = technique_spec.get("technique_id")

                # Get generic technique
                generic_technique = self.generic_techniques.get(technique_id)

                if not generic_technique:
                    logger.warning(f"Generic technique not found: {technique_id}")
                    continue

                # Build customization prompt
                variables = {
                    "research_context": research_context,
                    "area_name": area_name,
                    "technique_name": generic_technique.get("name", ""),
                    "generic_prompt": json.dumps(generic_technique.get("prompt_template", {}), indent=2)
                }

                prompt = self._build_prompt_from_template(customizer, variables)

                # Generate customized prompt (synchronous)
                temperature = customizer.get("temperature", 0.3)
                max_tokens = customizer.get("max_tokens", 1500)

                response = self.model.generate(
                    prompt=prompt,
                    temperature=temperature,
                    max_tokens=max_tokens
                )

                # Parse and store
                try:
                    customized = self._parse_json_response(response)
                    custom_prompts[f"{area_id}_{technique_id}"] = customized
                except Exception as e:
                    logger.error(f"Failed to parse customized prompt for {technique_id}: {e}")
                    # Use generic prompt as fallback
                    custom_prompts[f"{area_id}_{technique_id}"] = generic_technique.get("prompt_template", {})

        return {
            "custom_prompts": custom_prompts,
            "status": "success"
        }

    def save_research(
        self,
        research_id: str,
        research_name: str,
        thematic_structure: Dict[str, Any],
        custom_prompts: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Save complete research structure to config/researches/

        Args:
            research_id: Unique identifier for research
            research_name: Human-readable name
            thematic_structure: Output from generate_thematic_structure
            custom_prompts: Output from generate_custom_prompts
            metadata: Optional additional metadata

        Returns:
            Save status and file path
        """
        logger.info(f"Saving research: {research_id}")

        # Create researches directory if needed
        self.researches_dir.mkdir(parents=True, exist_ok=True)

        # Create research directory
        research_dir = self.researches_dir / research_id
        research_dir.mkdir(exist_ok=True)

        # Build complete research structure
        research_data = {
            "research_id": research_id,
            "name": research_name,
            "type": "research",
            "metadata": metadata or {},
            "thematic_structure": thematic_structure,
            "custom_prompts": custom_prompts,
            "created_at": str(Path.ctime(research_dir))
        }

        # Save main research file
        research_file = research_dir / "research.json"
        with open(research_file, 'w', encoding='utf-8') as f:
            json.dump(research_data, f, indent=2, ensure_ascii=False)

        # Save customizations separately
        customizations_dir = research_dir / "customizations"
        customizations_dir.mkdir(exist_ok=True)

        for prompt_key, prompt_data in custom_prompts.get("custom_prompts", {}).items():
            prompt_file = customizations_dir / f"{prompt_key}.json"
            with open(prompt_file, 'w', encoding='utf-8') as f:
                json.dump(prompt_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Research saved to: {research_dir}")

        return {
            "status": "success",
            "research_id": research_id,
            "path": str(research_dir),
            "files": {
                "main": str(research_file),
                "customizations": str(customizations_dir)
            }
        }
