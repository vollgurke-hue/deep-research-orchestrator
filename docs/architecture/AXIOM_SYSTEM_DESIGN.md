
# Axiom System Design: Der Souveräne Filter

**Version:** 1.0
**Date:** 2026-01-08
**Purpose:** Deep dive into the axiom-based validation system

---

## Das Problem: Echo-Kammer der Big Tech KI

Große Modelle (GPT-4, Claude, Gemini) sind trainiert auf:
- Silicon Valley Bias (Tech-Optimismus, Wachstum über alles)
- US-zentrisches Weltbild
- Corporate-freundliche Narrative
- Vermeidung kontroverser Wahrheiten

**Ergebnis:** Sie erzählen dir, was du hören willst, oder was ihre Hersteller wollen, dass du hörst.

---

## Die Lösung: Axiom-Library als Souveräner Filter

### Konzept

**Axiome = Unumstößliche Wahrheiten deiner Weltanschauung**

Anstatt dem LLM lange Essays über deine Weltanschauung zu füttern (VRAM-Verschwendung), definierst du **kurze, prägnante Axiome** als JSON-Filter.

### Die drei Ebenen der Axiom-Integration

```
1. EXTRACTION (ToT Phase)
   ↓ Axiome steuern, welche Fragen gestellt werden

2. GRAPH VALIDATION (Grounding Phase)
   ↓ Axiome bewerten Graph-Knoten (weighted edges)

3. FINAL SYNTHESIS (Synthesis Phase)
   ↓ Axiome entscheiden, welcher Pfad "gewinnt"
```

---

## 1. Axiom als Vektor (Die Mathematik dahinter)

### Weighted Edges im Knowledge Graph

Jede Verbindung (Edge) im Graphen bekommt ein **Gewicht basierend auf Axiom-Alignment**:

```python
# Beispiel: Edge wird gegen Axiome bewertet
edge = {
    "subject": "Digitale Währung",
    "predicate": "ermöglicht",
    "object": "Staatliche Kontrolle",
    "source": "reuters.com",
    "confidence": 0.85
}

# Axiom: "Privatsphäre ist nicht verhandelbar"
axiom_privacy = {
    "axiom_id": "privacy_paramount",
    "category": "ethics",
    "priority": "critical",
    "weight_modifier": -1.0  # Negative Bewertung für Kontroll-Mechanismen
}

# Edge-Gewicht Berechnung
base_weight = edge["confidence"]  # 0.85
axiom_weight = evaluate_axiom_alignment(edge, axiom_privacy)  # -0.9
final_weight = base_weight * axiom_weight  # 0.85 * -0.9 = -0.765

# Ergebnis: Diese Edge wird im MCTS als NEGATIV bewertet
```

### Axiom-Vektor für Multi-Axiom Evaluation

```python
# Mehrere Axiome gleichzeitig anwenden
axiom_vector = {
    "privacy_paramount": -0.9,      # Kontroll-Mechanismus = schlecht
    "decentralization_good": -0.8,  # Zentralisierung = Risiko
    "opportunity_cost": 0.0,        # Neutral (nicht anwendbar)
    "austrian_economics": -0.7      # Staat-gesteuertes Geld = Problem
}

# Aggregierter Score
final_score = np.mean([v for v in axiom_vector.values() if v != 0])
# -0.8 → Diese Verbindung widerspricht stark deiner Weltanschauung
```

---

## 2. Die drei Validierungs-Methoden

### Methode 1: First Principles Validator

**Zweck:** Prüfe, ob Schlussfolgerungen auf fundamentalen Wahrheiten basieren

**Implementierung:**
```python
class FirstPrinciplesValidator:
    """
    Zerlegt eine Behauptung in ihre Grundannahmen
    und prüft diese gegen physikalische/ökonomische Axiome
    """

    def validate(self, claim, graph):
        """
        Beispiel:
        Claim: "SaaS-Geschäft X wird profitabel sein"

        First Principles Zerlegung:
        1. Profitabilität = Revenue > Costs
        2. Revenue = Kunden * Preis
        3. Kosten = Fixed + Variable
        4. Kunden erfordert Marketing (CAC)
        5. Preis muss > CAC / LTV sein

        Prüfung: Sind diese Grundannahmen im Graph belegt?
        """

        # 1. LLM zerlegt Claim in fundamentale Annahmen
        assumptions = self.llm.extract_assumptions(claim)

        # 2. Prüfe jede Annahme gegen Graph
        validation_results = []
        for assumption in assumptions:
            evidence = graph.find_evidence(assumption)
            axiom_check = self.axiom_judge.evaluate(assumption)

            validation_results.append({
                "assumption": assumption,
                "evidence_found": len(evidence) > 0,
                "axiom_alignment": axiom_check.score,
                "verdict": "valid" if evidence and axiom_check.score > 0.6 else "unproven"
            })

        return validation_results
```

**Axiom-Beispiel für First Principles:**
```json
{
  "axiom_id": "economic_fundamentals",
  "category": "economics",
  "statement": "Jede Geschäftsanalyse muss auf den Grundgleichungen basieren: Profit = Revenue - Costs. Revenue = Volume * Price. Costs = Fixed + Variable. Wenn eine dieser Komponenten im Graph fehlt, ist die Analyse unvollständig.",
  "application": "validator",
  "priority": "critical"
}
```

### Methode 2: Bias-Inverter

**Zweck:** Aktiv nach Mainstream-Narrativen suchen und deren Fehler aufdecken

**Implementierung:**
```python
class BiasInverter:
    """
    Sucht gezielt nach dem 'offiziellen' Narrativ
    und hinterfragt es kritisch
    """

    def invert(self, topic, axiom_id):
        """
        Beispiel:
        Topic: "Elektromobilität"
        Axiom: "Österreichische Schule - Subventionen verzerren Märkte"

        Inverter-Prompt:
        "Suche nach Quellen, die Elektromobilität positiv darstellen.
        Identifiziere, welche dieser Quellen staatliche Subventionen
        als 'notwendig' oder 'förderlich' beschreiben.
        Analysiere dann: Würde der Markt ohne Subventionen existieren?
        Was ist der wahre Preis ohne Verzerrung?"
        """

        # 1. Finde Mainstream-Narrativ
        mainstream_sources = self.scraper.search(
            query=f"{topic} opportunities benefits",
            sources=["forbes.com", "techcrunch.com", "mainstream-media"]
        )

        # 2. Extrahiere Kern-Behauptungen
        claims = self.llm.extract_claims(mainstream_sources)

        # 3. Prüfe gegen Axiom
        contradictions = []
        for claim in claims:
            axiom = self.axiom_judge.get_axiom(axiom_id)

            # LLM beauftragt: "Finde logische Fehler in dieser Behauptung"
            critique = self.llm.critique_against_axiom(claim, axiom)

            if critique.contradicts:
                contradictions.append({
                    "claim": claim,
                    "source": claim.source,
                    "contradiction": critique.reasoning,
                    "alternative_view": critique.alternative
                })

        return contradictions
```

**Axiom-Beispiel für Bias-Inversion:**
```json
{
  "axiom_id": "subsidy_skepticism",
  "category": "economics",
  "statement": "Staatliche Subventionen verzerren Marktpreise und verschleiern wahre Kosten. Analysiere jede als 'erfolgreich' dargestellte Branche auf Subventionsabhängigkeit. Wenn >30% des Umsatzes aus Subventionen stammt, ist das Geschäftsmodell fragil.",
  "application": "filter",
  "priority": "high",
  "metadata": {
    "school": "austrian_economics",
    "reference": "Hayek, The Road to Serfdom"
  }
}
```

### Methode 3: Stress-Simulation (MCTS mit Axiom-Scoring)

**Zweck:** Simuliere Worst-Case-Szenarien basierend auf deinen Erfolgskriterien

**Implementierung:**
```python
class StressSimulator:
    """
    Nutzt MCTS, um Business-Szenarien zu simulieren
    Erfolg wird nach deinen Axiomen definiert, nicht "allgemein"
    """

    def simulate_scenario(self, business_model, stress_axioms):
        """
        Beispiel:
        Business Model: "SaaS für Projektmanagement"
        Stress Axiom: "Zeit ist die knappste Ressource"

        Simulation:
        - Wie viele Stunden/Woche braucht dieses Business?
        - Wie lange bis Break-Even?
        - Opportunity Cost vs. Index Fund + Freizeit?
        """

        # 1. Definiere Stress-Parameter aus Axiomen
        stress_params = self.extract_stress_parameters(stress_axioms)

        # 2. Generiere Python-Simulation
        simulation_code = self.llm.generate_simulation(
            business_model=business_model,
            stress_params=stress_params
        )

        # 3. Führe Monte Carlo Simulation aus (1000 Runs)
        results = []
        for _ in range(1000):
            # Variiere Parameter (z.B. Churn Rate, CAC, Time Investment)
            randomized_params = self.randomize_within_bounds(stress_params)
            result = exec(simulation_code, randomized_params)
            results.append(result)

        # 4. Bewerte Ergebnisse gegen Axiome
        success_rate = self.calculate_success_rate(results, stress_axioms)

        return {
            "success_probability": success_rate,
            "worst_case": min(results, key=lambda x: x.score),
            "best_case": max(results, key=lambda x: x.score),
            "median_case": np.median([r.score for r in results]),
            "axiom_alignment": self.judge.score_results(results, stress_axioms)
        }

    def extract_stress_parameters(self, axioms):
        """
        Beispiel Axiom: "opportunity_cost"
        → Stress Parameter: time_investment_hours, alternative_passive_income
        """
        params = {}

        for axiom in axioms:
            if axiom.id == "opportunity_cost":
                params["time_investment_hours"] = {
                    "min": 10, "max": 80, "critical_threshold": 40
                }
                params["alternative_passive_income"] = {
                    "baseline": 0.07  # 7% Index Fund
                }

            elif axiom.id == "time_preference":
                params["months_to_profitability"] = {
                    "acceptable": 12, "warning": 24, "unacceptable": 36
                }

        return params
```

**Axiom-Beispiel für Stress-Simulation:**
```json
{
  "axiom_id": "time_preference",
  "category": "time",
  "statement": "Zeit ist die knappste Ressource. Ein Business, das länger als 12 Monate bis zum Break-Even braucht, muss außergewöhnliche Upside haben (10x ROI Minimum). Nach 24 Monaten ist es inakzeptabel, egal wie profitabel danach.",
  "application": "scorer",
  "priority": "critical",
  "metadata": {
    "stress_params": {
      "months_to_breakeven": {"acceptable": 12, "warning": 24, "critical": 36},
      "required_roi_multiplier": {"after_12m": 3, "after_24m": 10}
    }
  }
}
```

---

## 3. Praktisches Beispiel: Heimspeicher-Batterien Analyse

### Szenario
**Frage:** "Ist der Markt für Heimspeicher-Batterien eine lukrative Gelegenheit?"

### Phase 0: EXPLORATION (ToT mit Axiom-gesteuerter Fragenstellung)

```python
# ToT Decomposition
root_question = "Heimspeicher-Batterien Marktchance?"

# Axiom-gesteuerte Fragengenerierung
axioms_to_consider = [
    "opportunity_cost",      # Zeit vs. Profit
    "subsidy_skepticism",    # Abhängigkeit von Förderung
    "supply_chain_sovereignty"  # Geopolitisches Risiko
]

# ToT generiert Branches basierend auf Axiomen
branches = {
    "branch_1": {
        "question": "Wie abhängig ist der Markt von staatlichen Subventionen?",
        "driven_by_axiom": "subsidy_skepticism"
    },
    "branch_2": {
        "question": "Wie sicher ist die Lithium-Lieferkette außerhalb Chinas?",
        "driven_by_axiom": "supply_chain_sovereignty"
    },
    "branch_3": {
        "question": "Technologie-Effizienz vs. Endkundenpreis: Ist Marge möglich?",
        "driven_by_axiom": "opportunity_cost"
    }
}
```

### Phase 1: GROUNDING (Scraping + Axiom-Validation)

```python
# Branch 1: Subventions-Abhängigkeit
scraper.search(query="home battery subsidies germany 2026")

# Gefundene Fakten:
facts_branch_1 = [
    ("Germany", "offers", "25% subsidy on home batteries"),
    ("EU", "plans", "phase-out subsidies by 2028"),
    ("Average installation cost", "is", "€12,000"),
    ("Subsidy amount", "is", "€3,000")
]

# Axiom-Check
axiom_subsidy = get_axiom("subsidy_skepticism")

for fact in facts_branch_1:
    edge_weight = axiom_judge.evaluate_fact(fact, axiom_subsidy)
    graph.add_edge(fact, weight=edge_weight)

# Ergebnis:
# Edge: (Germany, offers, 25% subsidy) → Weight: -0.7 (negativ!)
# Reasoning: "Subsidy macht 25% des Preises aus → fragil nach 2028"
```

### Phase 2: REASONING (MCTS + Stress-Simulation)

```python
# MCTS Navigation
# UCB1 Formel wird angewandt
mcts = MCTSEngine(graph, axioms)

for iteration in range(20):
    # 1. SELECT: Wähle vielversprechendsten Pfad
    node = mcts.select_best_node()  # UCB1 Formel

    # 2. EXPAND: Generiere neue Hypothese
    if not node.fully_explored:
        child = mcts.expand(node)

    # 3. SIMULATE: Python-Simulation
    if node.branch == "branch_3":  # Profitabilität
        simulation = StressSimulator().simulate_scenario(
            business_model={
                "installation_cost": 12000,
                "markup": 0.15,
                "time_per_install": 8,  # Stunden
                "installs_per_month": 10
            },
            stress_axioms=["opportunity_cost", "time_preference"]
        )

        # Ergebnis:
        # - Profit/Stunde: €30
        # - Vs. passive income + freie Zeit: Schlechter
        # - Axiom "opportunity_cost" Score: 0.3 (niedrig!)

    # 4. BACKPROPAGATE: Update Werte
    mcts.backpropagate(node, simulation.axiom_alignment)

# Bester Pfad nach MCTS
best_path = mcts.get_best_path()
# Ergebnis: Branch 2 gewinnt (Supply Chain Risiko ist real, aber technisch lösbar)
```

### Phase 3: SYNTHESIS (Axiom Final Check)

```python
# Finale Synthese
winning_path = graph.get_path(best_path)

# Axiom Final Check
final_axiom_scores = {
    "opportunity_cost": 0.45,        # Borderline (Warnung!)
    "subsidy_skepticism": 0.20,      # Kritisch niedrig (Rot!)
    "supply_chain_sovereignty": 0.65  # Akzeptabel (Gelb)
}

# Gesamtscore (gewichtet nach Priority)
total_score = (
    0.45 * axioms["opportunity_cost"].priority_weight +
    0.20 * axioms["subsidy_skepticism"].priority_weight +
    0.65 * axioms["supply_chain_sovereignty"].priority_weight
)
# = 0.43 → UNTER Schwellenwert 0.60

# Urteil
verdict = {
    "recommendation": "NICHT VERFOLGEN",
    "confidence": 0.82,
    "primary_reason": "Subsidy-Abhängigkeit widerspricht Axiom 'subsidy_skepticism'",
    "secondary_concern": "Opportunity Cost zweifelhaft (€30/h vs. passive alternatives)",
    "alternative": "Warte bis 2028 post-Subsidy-Marktkonsolidierung"
}
```

---

## 4. Axiom-Library Struktur

### Beispiel: 5 Kern-Axiome für ökonomische Analysen

```json
[
  {
    "axiom_id": "opportunity_cost",
    "category": "economics",
    "statement": "Bewerte jede Chance nach Opportunitätskosten. Ein Gewinn ist nur sinnvoll, wenn er Zeitinvestition vs. passive Alternativen rechtfertigt (z.B. 7% Index Fund + Freizeit).",
    "application": "scorer",
    "priority": "critical",
    "weight_modifier": {
      "if_roi_per_hour < 50": -0.5,
      "if_roi_per_hour >= 50 and < 100": 0.3,
      "if_roi_per_hour >= 100": 0.8
    }
  },
  {
    "axiom_id": "subsidy_skepticism",
    "category": "economics",
    "statement": "Staatliche Subventionen verzerren Preise. Wenn >20% des Umsatzes aus Subventionen kommt, ist das Geschäftsmodell fragil und politisch verwundbar.",
    "application": "filter",
    "priority": "high",
    "weight_modifier": {
      "if_subsidy_ratio < 0.1": 0.5,
      "if_subsidy_ratio >= 0.1 and < 0.2": 0.0,
      "if_subsidy_ratio >= 0.2": -0.8
    }
  },
  {
    "axiom_id": "time_preference",
    "category": "time",
    "statement": "Zeit ist die knappste Ressource. Break-Even >12 Monate braucht 10x Upside. >24 Monate ist inakzeptabel.",
    "application": "validator",
    "priority": "critical",
    "weight_modifier": {
      "if_months_to_breakeven <= 12": 0.7,
      "if_months_to_breakeven > 12 and <= 24 and roi_multiplier >= 10": 0.3,
      "if_months_to_breakeven > 24": -0.9
    }
  },
  {
    "axiom_id": "supply_chain_sovereignty",
    "category": "geopolitics",
    "statement": "Abhängigkeit von Single-Source-Lieferketten (besonders China) ist systemisches Risiko. Prüfe immer: Gibt es Alternativen? Wie stabil ist die geopolitische Lage?",
    "application": "validator",
    "priority": "medium",
    "weight_modifier": {
      "if_single_source_china": -0.6,
      "if_diversified_supply": 0.5
    }
  },
  {
    "axiom_id": "privacy_paramount",
    "category": "ethics",
    "statement": "Privatsphäre ist nicht verhandelbar. Geschäftsmodelle, die auf Datensammlung oder Überwachung basieren, sind abzulehnen, egal wie profitabel.",
    "application": "filter",
    "priority": "critical",
    "weight_modifier": {
      "if_business_model_requires_user_tracking": -1.0,
      "if_privacy_preserving": 0.8
    }
  }
]
```

---

## 5. Integration in den Code

### GraphManager mit Weighted Edges

```python
class GraphManager:
    def add_fact_triplet(self, subject, predicate, obj, metadata, axiom_judge):
        """
        Enhanced version: Jedes Tripel wird sofort gegen Axiome bewertet
        """
        # Basis-Edge erstellen
        edge_id = f"{subject}_{predicate}_{obj}"

        # Axiom-Evaluation
        axiom_scores = {}
        for axiom in axiom_judge.get_all_axioms():
            score = axiom_judge.evaluate_triplet(
                (subject, predicate, obj),
                axiom
            )
            axiom_scores[axiom.id] = score

        # Gewichteter Durchschnitt (nach Priority)
        weighted_score = self._calculate_weighted_score(axiom_scores, axiom_judge)

        # Edge mit Gewicht hinzufügen
        self.graph.add_edge(
            subject,
            obj,
            predicate=predicate,
            weight=weighted_score,
            axiom_scores=axiom_scores,
            metadata=metadata
        )

    def _calculate_weighted_score(self, axiom_scores, axiom_judge):
        """
        Gewichteter Durchschnitt basierend auf Axiom-Priority
        """
        total_weight = 0
        weighted_sum = 0

        for axiom_id, score in axiom_scores.items():
            axiom = axiom_judge.get_axiom(axiom_id)
            priority_weight = {
                "critical": 1.0,
                "high": 0.7,
                "medium": 0.4,
                "low": 0.2
            }[axiom.priority]

            weighted_sum += score * priority_weight
            total_weight += priority_weight

        return weighted_sum / total_weight if total_weight > 0 else 0.0
```

---

## Zusammenfassung

**Die Axiom-Library ist der entscheidende Unterschied zwischen:**
- ❌ KI die dir nach dem Mund redet
- ✅ Souveränem System das nach DEINEN Werten urteilt

**Drei Validierungs-Methoden:**
1. **First Principles** → Zerlegung in Grundwahrheiten
2. **Bias-Inverter** → Aktive Suche nach Mainstream-Fehlern
3. **Stress-Simulation** → MCTS mit deinen Erfolgsmaßstäben

**Weighted Edges im Graph:**
- Jede Verbindung wird gegen Axiome bewertet
- MCTS navigiert zu Pfaden mit hohem Axiom-Alignment
- Finale Entscheidung basiert auf deinen Werten, nicht Big Tech Bias

**Nächster Schritt:** Willst du deine 3-5 Kern-Axiome jetzt definieren?
