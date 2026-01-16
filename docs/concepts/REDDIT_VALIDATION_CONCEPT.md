# Reddit Validation & Friction Detection Konzept

**Datum:** 2026-01-22
**Quelle:** Gemini Strategic Planning
**Status:** Konzept-Definition

---

## 🎯 Kernidee

Integration von **Social Validation** (Reddit, Foren) als **empirischer Realitäts-Check** für theoretische KI-Aussagen. Identifikation von "Friction" - dem Unterschied zwischen "was theoretisch funktioniert" und "was in der Praxis scheitert".

---

## 1. Das Konzept: Grounding through Human Experience

### Problem mit reiner KI-Research
KI-Modelle haben Zugriff auf:
- Offizielle Dokumentation
- Marketing-Material
- Whitepapers
- News-Headlines

**Was fehlt:** Die REALITÄT

### Beispiel: Solar-Wechselrichter

**KI (basierend auf Datenblatt):**
```
[Wechselrichter_X] --[MTBF]--> [100.000_Stunden]
[Wechselrichter_X] --[Garantie]--> [10_Jahre]
[Wechselrichter_X] --[Zuverlässigkeit]--> [Sehr_Hoch]
```

**Reddit (r/solar):**
```
User1: "Wechselrichter X nach 3 Jahren tot, Support antwortet nicht"
User2: "Gleiches Problem, 2. Austausch in 5 Jahren"
User3: "Läuft seit 7 Jahren problemlos"  [12 Upvotes]
User4: "Das Firmware-Update hat meinen gekillt" [89 Upvotes]
```

**Friction Detected:**
- Theorie sagt: 10 Jahre Zuverlässigkeit
- Praxis zeigt: Firmware-Probleme, schlechter Support

---

## 2. Der "Friction-Check": Theorie vs. Realität

### Prozess

```python
class FrictionDetector:
    """Vergleicht theoretisches KI-Wissen mit menschlicher Erfahrung"""

    def validate_hypothesis(
        self,
        hypothesis_triple: Tuple[str, str, str],
        social_sources: List[str]
    ) -> FrictionReport:
        """
        Prüft ob eine Hypothese (SPO-Triplett) durch Social Media bestätigt wird
        """

        subject, predicate, obj = hypothesis_triple

        # 1. Generiere gezielte Suchqueries
        queries = self.generate_validation_queries(hypothesis_triple)

        # Beispiel-Queries:
        # - "Wechselrichter X Probleme"
        # - "Wechselrichter X vs Y Erfahrung"
        # - "Wechselrichter X Langzeittest"
        # - "Wechselrichter X Support"

        # 2. Scrape Social Media
        posts = []
        for query in queries:
            for source in social_sources:
                results = self.scraper.search(source, query)
                posts.extend(results)

        # 3. Extraktion von "Experience-Nodes"
        experiences = self.extract_experiences(posts)

        # 4. Sentiment-Analyse & Consensus
        consensus = self.calculate_consensus(experiences)

        # 5. Vergleich mit Hypothese
        friction_score = self.compare_with_hypothesis(
            hypothesis=hypothesis_triple,
            consensus=consensus
        )

        return FrictionReport(
            hypothesis=hypothesis_triple,
            supporting_evidence=consensus.positive,
            contradicting_evidence=consensus.negative,
            friction_score=friction_score,  # 0.0 = perfect match, 1.0 = total contradiction
            verdict="confirmed" | "friction_detected" | "contradicted"
        )
```

---

## 3. Experience-Node Extraktion

### Was ist ein Experience-Node?

```python
@dataclass
class ExperienceNode:
    """Ein menschlicher Erfahrungsbericht als strukturierte Daten"""

    # Source
    source: str  # reddit | hackernews | forum
    post_id: str
    author: str
    timestamp: datetime

    # Content
    claim: str  # Die Kernaussage
    sentiment: str  # positive | negative | neutral
    confidence: str  # certain | uncertain | speculative

    # Evidence
    evidence_type: str  # personal_experience | hearsay | calculation
    timeframe: Optional[str]  # "nach 3 Jahren", "seit 2020"
    context: Dict[str, Any]  # Zusatzinfos (Standort, Konfiguration, etc.)

    # Credibility
    upvotes: int
    expertise_indicators: List[str]  # Fachbegriffe, Details
    account_age: int  # Tage
    verification: bool  # Verifizierter Account?
```

### Extraktion mit LLM

```python
EXPERIENCE_EXTRACTION_PROMPT = """
Analysiere folgenden Social Media Post und extrahiere strukturierte Erfahrung:

Post:
{post_content}

Extrahiere:
1. Kernaussage (claim)
2. Sentiment (positive/negative/neutral)
3. Konfidenz (certain/uncertain/speculative)
4. Evidenz-Typ (personal_experience/hearsay/calculation)
5. Zeitrahmen (wenn genannt)
6. Relevante Kontext-Details

Output (JSON):
{{
  "claim": "...",
  "sentiment": "...",
  "confidence": "...",
  "evidence_type": "...",
  "timeframe": "...",
  "context": {{...}}
}}
"""

# Beispiel-Output:
{
  "claim": "Wechselrichter X fiel nach Firmware-Update aus",
  "sentiment": "negative",
  "confidence": "certain",
  "evidence_type": "personal_experience",
  "timeframe": "nach 3 Jahren Betrieb",
  "context": {
    "model": "Wechselrichter X Pro",
    "firmware_version": "2.1.4",
    "location": "Süddeutschland"
  }
}
```

---

## 4. Human Consensus Score

### Gewichtete Aggregation

Nicht alle Reddit-Posts sind gleich wertvoll:

```python
def calculate_consensus_score(experiences: List[ExperienceNode]) -> ConsensusScore:
    """Berechnet gewichteten Konsens aus menschlichen Erfahrungen"""

    total_weight = 0.0
    sentiment_sum = 0.0  # -1.0 (negativ) bis +1.0 (positiv)

    for exp in experiences:

        # Basis-Gewicht
        weight = 1.0

        # Faktor 1: Upvote-Ratio
        if exp.upvotes > 50:
            weight *= 3.0
        elif exp.upvotes > 10:
            weight *= 2.0

        # Faktor 2: Evidenz-Typ
        if exp.evidence_type == "personal_experience":
            weight *= 2.0  # Eigene Erfahrung > Hörensagen
        elif exp.evidence_type == "hearsay":
            weight *= 0.5

        # Faktor 3: Konfidenz
        if exp.confidence == "certain":
            weight *= 1.5
        elif exp.confidence == "speculative":
            weight *= 0.5

        # Faktor 4: Expertise-Indikatoren
        expertise_count = len(exp.expertise_indicators)
        weight *= (1.0 + expertise_count * 0.1)

        # Faktor 5: Subreddit-Autorität
        if exp.source == "r/Solar":  # Fach-Subreddit
            weight *= 1.5
        elif exp.source == "r/Funny":
            weight *= 0.1  # Nicht relevant

        # Faktor 6: Temporal Relevance
        age_days = (datetime.now() - exp.timestamp).days
        if age_days < 180:  # < 6 Monate
            weight *= 1.5
        elif age_days > 1095:  # > 3 Jahre
            weight *= 0.5

        # Sentiment kodieren
        sentiment_value = {
            "positive": 1.0,
            "neutral": 0.0,
            "negative": -1.0
        }[exp.sentiment]

        # Akkumuliere
        total_weight += weight
        sentiment_sum += sentiment_value * weight

    # Final Score
    consensus_sentiment = sentiment_sum / total_weight if total_weight > 0 else 0.0

    return ConsensusScore(
        sentiment=consensus_sentiment,  # -1.0 bis +1.0
        confidence=min(total_weight / 100.0, 1.0),  # Wie sicher sind wir?
        sample_size=len(experiences),
        dominant_verdict="positive" if consensus_sentiment > 0.3 else
                        "negative" if consensus_sentiment < -0.3 else
                        "mixed"
    )
```

---

## 5. Expertise-Filter: Trolle vermeiden

### Qualitäts-Indikatoren

```python
def assess_post_quality(post: RedditPost) -> QualityScore:
    """Bewertet Qualität eines Posts"""

    score = 0.0

    # 1. Technische Sprache
    technical_terms = [
        "MPPT", "Wirkungsgrad", "Einspeisevergütung", "kWp",
        "Wechselstrom", "String", "Verschattung"
    ]
    tech_term_count = sum(1 for term in technical_terms if term.lower() in post.content.lower())
    score += tech_term_count * 0.1

    # 2. Konkrete Zahlen
    numbers_mentioned = len(re.findall(r'\d+(?:\.\d+)?\s*(?:kWh|EUR|%|Jahre)', post.content))
    score += numbers_mentioned * 0.15

    # 3. Vergleiche & Kontext
    if any(word in post.content.lower() for word in ["im vergleich", "vs", "besser als", "schlechter als"]):
        score += 0.2

    # 4. Länge (zu kurz = wenig Info, zu lang = Geschwafel)
    word_count = len(post.content.split())
    if 50 < word_count < 300:
        score += 0.3
    elif word_count < 20:
        score -= 0.2

    # 5. Emotionale Sprache (negativ)
    emotional_words = ["hasse", "liebe", "schrecklich", "fantastisch"]
    if any(word in post.content.lower() for word in emotional_words):
        score -= 0.3

    # 6. Account-History
    if post.author_karma > 1000:
        score += 0.2
    if post.author_account_age_days > 365:
        score += 0.1

    return QualityScore(
        value=max(0.0, min(1.0, score)),
        reasoning={
            "technical_terms": tech_term_count,
            "has_numbers": numbers_mentioned > 0,
            "appropriate_length": 50 < word_count < 300
        }
    )
```

---

## 6. SPO-Mapping: KI vs. Mensch

### Vergleichs-Logik

```python
def compare_ai_vs_human(
    ai_triple: Tuple[str, str, str],
    human_experiences: List[ExperienceNode]
) -> Comparison:
    """Vergleicht AI-Hypothese mit menschlichen Erfahrungen"""

    subject, predicate, obj = ai_triple

    # 1. Extrahiere menschliche Tripletts aus Experiences
    human_triples = []
    for exp in human_experiences:
        extracted = spo_extractor.extract_from_text(exp.claim)
        human_triples.extend(extracted)

    # 2. Finde Überschneidungen und Widersprüche
    matches = []
    conflicts = []

    for h_triple in human_triples:
        h_subject, h_predicate, h_obj = h_triple

        # Gleicher Gegenstand?
        if semantic_similarity(subject, h_subject) > 0.8:

            # Gleiche Eigenschaft?
            if semantic_similarity(predicate, h_predicate) > 0.7:

                # Werte vergleichen
                if semantic_similarity(obj, h_obj) > 0.8:
                    matches.append(h_triple)
                else:
                    conflicts.append({
                        "ai_says": (subject, predicate, obj),
                        "human_says": h_triple,
                        "conflict_type": "value_mismatch"
                    })

    # 3. Tension-Node erstellen bei Konflikt
    if len(conflicts) > len(matches):
        tension = TensionNode(
            ai_claim=ai_triple,
            human_claim=most_common(conflicts)["human_says"],
            evidence_count=len(conflicts),
            severity="high" if len(conflicts) > 5 else "medium"
        )
        return Comparison(
            verdict="CONFLICT",
            tension_node=tension,
            recommendation="Investigate discrepancy"
        )

    return Comparison(
        verdict="CONFIRMED",
        supporting_evidence=len(matches),
        confidence=len(matches) / (len(matches) + len(conflicts))
    )
```

---

## 7. Integration mit MCTS: Friction-Guided Exploration

### MCTS priorisiert Conflict-Resolution

```python
class FrictionGuidedMCTS(MCTSEngine):
    """MCTS der Widersprüche auflösen muss"""

    def select(self) -> MCTSNode:
        """Wähle nächsten Node basierend auf Friction"""

        # Standard: UCB1 Score
        ucb_scores = [node.ucb1_score() for node in self.root.children]

        # Bonus: Friction-Resolution
        friction_bonus = []
        for node in self.root.children:
            if node.has_unresolved_tension:
                # Nodes mit Widersprüchen bekommen Priorität
                friction_bonus.append(2.0)
            else:
                friction_bonus.append(0.0)

        # Kombiniere
        total_scores = [ucb + bonus for ucb, bonus in zip(ucb_scores, friction_bonus)]

        return self.root.children[argmax(total_scores)]

    def simulate(self, node: MCTSNode) -> float:
        """Simuliere Wert unter Berücksichtigung von Friction"""

        # Normale Simulation
        base_reward = super().simulate(node)

        # Penalty wenn Friction ungelöst bleibt
        if node.tension_node and not node.tension_node.resolved:
            friction_penalty = -0.5
        else:
            friction_penalty = 0.0

        # Bonus wenn Friction aufgelöst wurde
        if node.tension_node and node.tension_node.resolved:
            resolution_bonus = +1.0
        else:
            resolution_bonus = 0.0

        return base_reward + friction_penalty + resolution_bonus
```

---

## 8. Strategischer Vorteil: Bias-Umgehung

### Problem mit Massenmedien

**Headlines:**
- "Der Markt für Wärmepumpen boomt" (Quelle: Industrie-Verband)
- "Solarenergie billiger als je zuvor" (Quelle: Hersteller-PR)

**Reality (Reddit/Foren):**
- "Wir haben keine Fachkräfte für Einbau, Wartezeit 12 Monate"
- "Solaranlage günstig, aber Anschluss kostet 5000 EUR extra"

### Unser Vorteil

```python
# Standard-RAG: Nimmt Headlines als Wahrheit
headline_triple = ("Wärmepumpen-Markt", "Status", "Boomend")

# Unser System: Prüft gegen Reddit
friction_check = friction_detector.validate(
    headline_triple,
    sources=["r/Handwerker", "r/HausUndGarten"]
)

# Ergebnis:
{
  "verdict": "FRICTION_DETECTED",
  "headline_says": "Markt boomt",
  "reality_says": "Markt boomt, aber Umsetzung scheitert an Fachkräftemangel",
  "recommendation": "Add constraint-triple: (Wärmepumpen-Installation, Bottleneck, Fachkräftemangel)"
}
```

### Resultat
System erkennt: Chance ist da (Theorie), aber Umsetzung scheitert (Praxis).

---

## 9. Validation-Template für Reddit-Analyse

### Prompt für systematische Auswertung

```python
REDDIT_VALIDATION_TEMPLATE = """
Aufgabe: Validiere folgendes SPO-Triplett gegen Reddit-Erfahrungen

SPO-Triplett (zu prüfen):
[{subject}] --[{predicate}]--> [{object}]

Reddit-Posts (Sample von {n} Posts):
{posts_summary}

Analysiere:

1. KONSENSUS
   - Wie viele Posts bestätigen das Triplett?
   - Wie viele widersprechen?
   - Wie viele sind neutral/irrelevant?

2. FEHLERRATEN
   - Berichten User von Problemen?
   - Welche Fehlerrate wird genannt? (in %)
   - Gibt es systematische Ausfallmuster?

3. VERSTECKTE KOSTEN
   - Erwähnen User zusätzliche Kosten?
   - Installation, Wartung, Reparatur?
   - Folgekosten die nicht offensichtlich sind?

4. NUTZERZUFRIEDENHEIT
   - Würden User die Investition wiederholen?
   - Empfehlungsrate (in %)
   - Häufige Beschwerden?

5. KONTEXT-FAKTOREN
   - Unter welchen Bedingungen funktioniert es?
   - Wo scheitert es?
   - Geografische/klimatische Einflüsse?

Output (JSON):
{{
  "consensus": "confirms" | "contradicts" | "mixed",
  "failure_rate": <0.0-1.0>,
  "hidden_costs": [<list of cost categories>],
  "satisfaction_score": <0.0-1.0>,
  "context_dependencies": [<list of critical factors>],
  "recommendation": "accept" | "reject" | "investigate_further"
}}
"""
```

---

## 10. Implementation Roadmap

### Phase 1: Scraping Infrastructure
```python
# Reddit-API Integration
- reddit_scraper.py: PRAW library
- Subreddit-Listen nach Domäne (r/Solar, r/Finanzen, etc.)
- Rate-Limiting & Caching
```

### Phase 2: Experience Extraction
```python
# LLM-basierte Strukturierung
- experience_extractor.py
- Batch-Verarbeitung mit RLM
- Quality-Filtering
```

### Phase 3: Friction Detection
```python
# Vergleichs-Engine
- friction_detector.py
- SPO-Mapping AI vs Human
- Tension-Node Generation
```

### Phase 4: MCTS-Integration
```python
# Friction-guided Exploration
- MCTS nutzt Friction-Score für Priorisierung
- Automatische Conflict-Resolution
```

---

## 11. Data Sources Hierarchy

### Vertrauens-Ranking

```python
SOCIAL_SOURCE_TRUST_LEVELS = {
    # Tier 1: Expert Communities (Gewicht: 1.0)
    "r/Solar": 1.0,
    "r/Finanzen": 1.0,
    "Photovoltaikforum.com": 1.0,

    # Tier 2: Generalist but Active (Gewicht: 0.7)
    "r/de": 0.7,
    "r/HausUndGarten": 0.7,

    # Tier 3: Low Trust (Gewicht: 0.3)
    "r/Funny": 0.1,
    "Allgemeine News-Kommentare": 0.3,
}
```

---

## Referenzen
- Social Validation in AI Systems - Research 2024
- Wisdom of the Crowd - Surowiecki
- Gemini Strategic Planning Session (Jan 2026)
- PRAW: Python Reddit API Wrapper
