# Bias-Mapping Strategy - Perspektiven-Graph

**Datum:** 2026-01-22
**Quelle:** Gemini Strategic Planning - Hardening Phase
**Status:** Konzept-Definition

---

## 🎯 Kernidee

**Bias ist keine Fehlerquelle, sondern Information.**

Anstatt Bias zu "löschen" oder "neutralisieren", ordnen wir ihn in einem **Vektorraum** ein. Wir bauen keinen "neutralen" Graphen, sondern einen **Perspektiven-Graphen**.

---

## 1. Das Problem mit "Neutralität"

### Standard-Ansatz
- Quellen als "verzerrt" markieren und verwerfen
- Versuchen "objektive" Wahrheit zu extrahieren
- Bias als Rauschen behandeln

### Warum das scheitert
```
Beispiel: "Ist Cloud-Computing wirtschaftlich?"

AWS-Whitepaper:  "Ja, TCO 40% niedriger"  → Cloud-Bias
Reddit r/Selfhosted: "Nein, Lock-in zu teuer" → Souveränitäts-Bias

Standard-System: "Widerspruch! Kann keine Antwort geben."
```

**Problem:** Beide haben recht - aus ihrer Perspektive.

---

## 2. Der Perspektiven-Graph

### Konzept: Bias als Koordinatensystem

```python
# Jede Quelle hat eine Position im Bias-Raum
@dataclass
class BiasVector:
    """Mathematische Repräsentation der Quelle-Perspektive"""

    # Primäre Dimensionen
    risk_affinity: float        # -1.0 (konservativ) bis +1.0 (spekulativ)
    time_horizon: float         # -1.0 (kurzfristig) bis +1.0 (langfristig)
    centralization: float       # -1.0 (dezentral) bis +1.0 (zentralisiert)
    empirical_depth: float      # 0.0 (anekdotisch) bis 1.0 (datengetrieben)

    # Sekundäre Dimensionen
    profit_motive: float        # 0.0 (neutral) bis 1.0 (kommerzielle Agenda)
    ideological_stance: float   # -1.0 (links) bis +1.0 (rechts) - optional
    expertise_level: float      # 0.0 (Laie) bis 1.0 (Experte)

    # Meta
    confidence: float           # Wie sicher sind wir über diesen Bias?
    sample_size: int            # Aus wie vielen Texten extrahiert?
```

### Referenz-Position: Deine Axiome

```python
# Der Nullpunkt = Deine Werte
MY_AXIOM_POSITION = BiasVector(
    risk_affinity=-0.3,      # Leicht konservativ
    time_horizon=0.8,        # Langfristig denken
    centralization=-0.9,     # Stark dezentral
    empirical_depth=0.9,     # Datengetrieben
    profit_motive=0.0,       # Kein kommerzieller Bias
    expertise_level=0.7      # Fortgeschritten
)
```

---

## 3. Source Profiling: Bias-Extraktion

### Automatische Profilerstellung

```python
class SourceProfiler:
    """Extrahiert Bias-Profil aus Texten einer Quelle"""

    def profile_source(self, source_name: str, sample_texts: List[str]) -> BiasVector:
        """Analysiert Texte und erstellt Bias-Vektor"""

        # 1. LLM-basierte Analyse
        analysis_prompt = f"""
        Analysiere folgende Texte von Quelle '{source_name}':

        {sample_texts[:5]}  # Top 5 repräsentative Texte

        Bewerte auf folgenden Dimensionen (-1.0 bis +1.0):

        1. RISIKO-AFFINITÄT:
           -1.0 = "Immer vorsichtig, warnt vor Risiken"
           0.0 = "Ausgewogen, zeigt Pros & Cons"
           +1.0 = "Fokus auf Chancen, downplays Risiken"

        2. ZEITHORIZONT:
           -1.0 = "Kurzfristige Gains, Pump & Dump Mentalität"
           0.0 = "Normale Investitions-Horizonte (1-3 Jahre)"
           +1.0 = "Generationen-übergreifend, Nachhaltigkeit"

        3. ZENTRALISIERUNG:
           -1.0 = "Pro Dezentralisierung, Souveränität, Self-Hosting"
           0.0 = "Neutral"
           +1.0 = "Pro Cloud, Konzerne, zentrale Lösungen"

        4. EMPIRISCHE TIEFE:
           0.0 = "Anekdoten, Feelings, Vibes"
           0.5 = "Mix aus Meinungen und Fakten"
           1.0 = "Nur Daten, Quellen, Messungen"

        5. PROFIT-MOTIV:
           0.0 = "Keine erkennbare Agenda"
           0.5 = "Soft-Marketing (native ads)"
           1.0 = "Offensichtlich kommerzielle Agenda"

        Output (JSON):
        {{
          "risk_affinity": <float>,
          "time_horizon": <float>,
          "centralization": <float>,
          "empirical_depth": <float>,
          "profit_motive": <float>,
          "reasoning": "<Begründung>",
          "key_phrases": [<typische Phrasen>]
        }}
        """

        response = self.llm.query(analysis_prompt, temperature=0.1)
        bias_data = json.loads(response)

        # 2. Code-basierte Validierung
        # Checke ob empirical_depth mit Zahlen im Text korreliert
        number_density = self._count_numbers_per_word(sample_texts)
        if number_density > 0.05:  # Viele Zahlen
            bias_data["empirical_depth"] = max(bias_data["empirical_depth"], 0.7)

        # Checke Marketing-Sprache
        marketing_keywords = ["beste", "führend", "revolutionär", "game-changer"]
        if self._contains_many(sample_texts, marketing_keywords):
            bias_data["profit_motive"] = max(bias_data["profit_motive"], 0.6)

        # 3. Erstelle Vektor
        return BiasVector(
            risk_affinity=bias_data["risk_affinity"],
            time_horizon=bias_data["time_horizon"],
            centralization=bias_data["centralization"],
            empirical_depth=bias_data["empirical_depth"],
            profit_motive=bias_data["profit_motive"],
            confidence=0.8,  # Initial
            sample_size=len(sample_texts)
        )
```

---

## 4. Bias-Vergleich: Quelle vs. Axiome

### Distanz-Berechnung

```python
def calculate_bias_distance(
    source_bias: BiasVector,
    reference_bias: BiasVector
) -> BiasDistance:
    """Berechnet wie weit eine Quelle von deinen Axiomen entfernt ist"""

    # Gewichtete Euklidische Distanz
    weights = {
        "risk_affinity": 0.8,
        "time_horizon": 1.0,      # Sehr wichtig
        "centralization": 1.2,    # Extrem wichtig
        "empirical_depth": 0.9,
        "profit_motive": 0.7
    }

    squared_diffs = []

    for dimension, weight in weights.items():
        source_val = getattr(source_bias, dimension)
        ref_val = getattr(reference_bias, dimension)
        squared_diff = weight * (source_val - ref_val) ** 2
        squared_diffs.append(squared_diff)

    distance = math.sqrt(sum(squared_diffs))

    # Interpretation
    if distance < 0.5:
        alignment = "aligned"
    elif distance < 1.0:
        alignment = "moderate_difference"
    else:
        alignment = "strong_difference"

    return BiasDistance(
        total_distance=distance,
        alignment=alignment,
        dimension_diffs={
            dim: getattr(source_bias, dim) - getattr(reference_bias, dim)
            for dim in ["risk_affinity", "time_horizon", "centralization"]
        }
    )
```

### Interpretation für User

```python
def explain_bias_difference(distance: BiasDistance, source_name: str) -> str:
    """Erklärt die Bias-Differenz in natürlicher Sprache"""

    explanations = []

    # Zentral-Dimension (meist wichtigster Konflikt)
    if abs(distance.dimension_diffs["centralization"]) > 0.5:
        if distance.dimension_diffs["centralization"] > 0:
            explanations.append(
                f"⚠️ {source_name} favorisiert zentralisierte Lösungen "
                f"(+{distance.dimension_diffs['centralization']:.1f}), "
                f"während deine Axiome Souveränität priorisieren."
            )

    # Zeithorizont
    if abs(distance.dimension_diffs["time_horizon"]) > 0.5:
        if distance.dimension_diffs["time_horizon"] < 0:
            explanations.append(
                f"⚠️ {source_name} fokussiert kurzfristige Perspektive "
                f"({distance.dimension_diffs['time_horizon']:.1f}), "
                f"deine Axiome priorisieren Langfristigkeit."
            )

    # Risiko
    if abs(distance.dimension_diffs["risk_affinity"]) > 0.5:
        if distance.dimension_diffs["risk_affinity"] > 0:
            explanations.append(
                f"ℹ️ {source_name} ist risikofreudiger als deine Axiome."
            )

    if not explanations:
        return f"✓ {source_name} ist gut mit deinen Axiomen aligned."

    return "\n".join(explanations)
```

---

## 5. SPO mit Bias-Metadaten

### Erweitertes Triplett-Format

```python
@dataclass
class BiasedTriple:
    """SPO-Triplett mit Bias-Awareness"""

    # Kern-Triplett
    subject: str
    predicate: str
    object: str

    # Provenance (woher?)
    source: str
    source_bias: BiasVector

    # Sentiment/Wertung
    sentiment: str  # positive | negative | neutral
    confidence: float

    # Bias-Kontext
    bias_influence: BiasInfluence  # Wie stark beeinflusst Bias diese Aussage?
```

### Beispiel

```python
# Quelle: AWS Whitepaper
triple_aws = BiasedTriple(
    subject="Cloud_Hosting",
    predicate="TCO_vs_OnPremise",
    object="-40%",  # 40% günstiger
    source="AWS_Whitepaper_2024",
    source_bias=BiasVector(
        centralization=0.9,  # Pro-Cloud
        profit_motive=0.8,   # Verkaufs-Agenda
        empirical_depth=0.7  # Zahlen, aber selektiv
    ),
    sentiment="positive",
    confidence=0.6,  # Reduziert wegen Profit-Motiv
    bias_influence=BiasInfluence(
        severity="high",
        reasoning="Quelle hat kommerzielles Interesse, TCO könnte geschönt sein"
    )
)

# Quelle: r/Selfhosted
triple_reddit = BiasedTriple(
    subject="Cloud_Hosting",
    predicate="Lock-in_Risk",
    object="High",
    source="r/Selfhosted",
    source_bias=BiasVector(
        centralization=-0.8,  # Anti-Cloud
        profit_motive=0.0,    # Keine Agenda
        empirical_depth=0.6   # Mix aus Erfahrung & Meinung
    ),
    sentiment="negative",
    confidence=0.8,  # Höher wegen unabhängiger Quelle
    bias_influence=BiasInfluence(
        severity="medium",
        reasoning="Community hat ideologischen Bias gegen Cloud, aber authentisch"
    )
)
```

---

## 6. MCTS Integration: Bias-Aware Selection

### Bias-Korrektur im MCTS

```python
class BiasAwareMCTS(MCTSEngine):
    """MCTS der Bias bei Exploration berücksichtigt"""

    def select(self) -> MCTSNode:
        """Wähle Node unter Berücksichtigung von Source-Bias"""

        candidates = self.root.children

        scores = []
        for node in candidates:

            # Standard UCB1
            ucb_score = node.ucb1_score()

            # Bias-Bonus/Penalty
            bias_adjustment = self._calculate_bias_adjustment(node)

            # Coverage-Bonus (aus früherem Konzept)
            coverage_bonus = (1.0 - node.coverage) * 0.3

            total_score = ucb_score + bias_adjustment + coverage_bonus
            scores.append(total_score)

        return candidates[argmax(scores)]

    def _calculate_bias_adjustment(self, node: MCTSNode) -> float:
        """Berechnet Bias-Korrektur für Node"""

        if not node.triples:
            return 0.0

        # Durchschnitts-Distanz aller Tripletts zu Axiomen
        total_distance = 0.0
        for triple in node.triples:
            if hasattr(triple, 'source_bias'):
                distance = calculate_bias_distance(
                    triple.source_bias,
                    self.reference_axioms
                )
                total_distance += distance.total_distance

        avg_distance = total_distance / len(node.triples)

        # Penalty für zu große Distanz
        if avg_distance > 1.0:
            return -0.5  # Vermeide Nodes mit stark abweichendem Bias
        elif avg_distance < 0.3:
            return +0.3  # Belohne gut aligned Nodes

        return 0.0
```

---

## 7. Praktisches Beispiel: Solar-Investment

### Szenario
User fragt: "Soll ich in Solaranlage investieren?"

### Source Profiling

```python
sources_analyzed = {
    "Solaranlagen_Hersteller_Website": BiasVector(
        centralization=0.5,
        profit_motive=0.9,  # Verkaufs-Agenda
        empirical_depth=0.6,
        confidence=0.9
    ),

    "r/Solar": BiasVector(
        centralization=-0.2,  # Leicht DIY-fokussiert
        profit_motive=0.1,    # Community-driven
        empirical_depth=0.7,  # Viele Erfahrungsberichte
        confidence=0.85
    ),

    "Stiftung_Warentest": BiasVector(
        centralization=0.0,
        profit_motive=0.0,
        empirical_depth=0.95,  # Sehr datengetrieben
        confidence=0.95
    ),

    "r/Finanzen": BiasVector(
        risk_affinity=-0.6,   # Sehr konservativ
        time_horizon=0.4,
        empirical_depth=0.8,
        confidence=0.8
    )
}

# User's Axiome
user_axioms = BiasVector(
    centralization=-0.9,  # Pro-Souveränität
    profit_motive=0.0,
    empirical_depth=0.9,
    risk_affinity=-0.2,   # Leicht konservativ
    time_horizon=0.8      # Langfristig
)
```

### Bias-Distance Analysis

```python
for source, bias in sources_analyzed.items():
    distance = calculate_bias_distance(bias, user_axioms)
    print(explain_bias_difference(distance, source))

# Output:
"""
Solaranlagen_Hersteller_Website:
⚠️ Hohe kommerzielle Agenda (0.9). Informationen mit Vorsicht.
⚠️ Zentralisierungsgrad weicht ab (+1.4). Quelle bevorzugt Konzern-Lösungen.

r/Solar:
✓ Gut aligned (Distanz: 0.4)
ℹ️ Leicht höhere Risikobereitschaft als deine Axiome.

Stiftung_Warentest:
✓ Exzellent aligned (Distanz: 0.2)
✓ Höchste empirische Tiefe.

r/Finanzen:
⚠️ Deutlich konservativer (-0.4 risk_affinity).
ℹ️ Kürzerer Zeithorizont als deine Präferenz.
"""
```

### MCTS Decision

```python
# MCTS priorisiert:
1. Stiftung_Warentest (Distanz 0.2, Empirisch 0.95) → Highest Weight
2. r/Solar (Distanz 0.4, Community-basiert) → High Weight
3. r/Finanzen (Distanz 0.6, konservativ) → Medium Weight (als Gegencheck)
4. Hersteller-Website (Distanz 1.2, Profit-Motiv) → Lowest Weight

# System extrahiert SPO, gewichtet nach Bias-Alignment
verified_triple = weighted_consensus([
    (triple_warentest, weight=1.0),
    (triple_reddit, weight=0.8),
    (triple_finanzen, weight=0.5),
    (triple_hersteller, weight=0.2)
])
```

---

## 8. Visualisierung: Bias-Landkarte

### 2D-Projektion (t-SNE oder PCA)

```python
# Hauptdimensionen: Centralization (X) vs. Risk-Affinity (Y)
import matplotlib.pyplot as plt

sources_plot = {
    "AWS": (0.9, 0.3),
    "r/Selfhosted": (-0.8, -0.2),
    "Stiftung_Warentest": (0.0, -0.1),
    "r/Finanzen": (0.2, -0.6),
    "Deine Axiome": (-0.9, -0.2)
}

plt.figure(figsize=(10, 8))
for source, (x, y) in sources_plot.items():
    if source == "Deine Axiome":
        plt.scatter(x, y, s=300, c='gold', marker='*', label=source)
    else:
        plt.scatter(x, y, s=100, alpha=0.7, label=source)

plt.xlabel("Centralization (-1=Dezentral, +1=Cloud)")
plt.ylabel("Risk Affinity (-1=Konservativ, +1=Spekulativ)")
plt.title("Bias-Landkarte: Sources im Axiom-Raum")
plt.legend()
plt.grid(True, alpha=0.3)
plt.axhline(y=0, color='k', linestyle='--', alpha=0.3)
plt.axvline(x=0, color='k', linestyle='--', alpha=0.3)
plt.show()
```

---

## 9. Contrastive Reasoning: Synthetische Debatte

### Konzept
Wenn zwei stark abweichende Bias-Positionen existieren, lasse sie debattieren.

```python
class ContrastiveDebate:
    """Führt synthetische Debatte zwischen widersprüchlichen Quellen"""

    def run_debate(
        self,
        position_a: BiasedTriple,
        position_b: BiasedTriple,
        rounds: int = 3
    ) -> DebateResult:
        """Lässt zwei Positionen gegeneinander antreten"""

        # LLM-A: Verteidigt Position A
        llm_a_prompt = f"""
        Du vertrittst die Position von {position_a.source}.
        Bias-Profil: {position_a.source_bias}

        Behauptung: {position_a.subject} {position_a.predicate} {position_a.object}

        Dein Gegner behauptet das Gegenteil. Verteidige deine Position mit:
        - Fakten
        - Logischen Argumenten
        - Schwächen der Gegenposition
        """

        # LLM-B: Verteidigt Position B
        llm_b_prompt = f"""
        Du vertrittst die Position von {position_b.source}.
        Bias-Profil: {position_b.source_bias}

        Behauptung: {position_b.subject} {position_b.predicate} {position_b.object}

        Dein Gegner behauptet das Gegenteil. Verteidige deine Position.
        """

        debate_history = []

        for round_num in range(rounds):
            # A's Argument
            arg_a = self.llm.query(llm_a_prompt + f"\n\nDebatte-Historie:\n{debate_history}")
            debate_history.append(f"Position A (Runde {round_num+1}): {arg_a}")

            # B's Gegenargument
            arg_b = self.llm.query(llm_b_prompt + f"\n\nDebatte-Historie:\n{debate_history}")
            debate_history.append(f"Position B (Runde {round_num+1}): {arg_b}")

        # Judge: Axiom-basiert
        winner = self._judge_debate(debate_history, self.reference_axioms)

        return DebateResult(
            winner=winner,  # position_a | position_b | draw
            debate_log=debate_history,
            reasoning="Position B überlebte Axiom-Prüfung besser"
        )
```

---

## 10. Implementation Checklist

### Phase 1: Source Profiling
```
□ BiasVector Dataclass
□ SourceProfiler Class
□ LLM-based Bias Extraction Prompt
□ Code-based Validation (number density, marketing keywords)
□ Bias-Vektor Persistierung (JSON)
```

### Phase 2: Bias Distance
```
□ calculate_bias_distance() Funktion
□ Gewichtungs-Schema für Dimensionen
□ explain_bias_difference() für User-Feedback
□ Visualisierung (Matplotlib oder D3.js)
```

### Phase 3: Integration
```
□ BiasedTriple erweitert SPO-Struktur
□ MCTS Bias-Adjustment
□ ContrastiveDebate für Widersprüche
□ Deep Graph speichert Bias-Metadaten
```

---

## Referenzen
- Epistemische Pluralität - Stanford Encyclopedia of Philosophy
- Source Credibility in Information Retrieval - ACL 2023
- Bias Detection in Text - NeurIPS 2024
- Gemini Strategic Planning Session (Jan 2026)
