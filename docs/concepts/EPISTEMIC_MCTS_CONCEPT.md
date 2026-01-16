# Epistemisches MCTS - Information Gathering als Spielzug

**Datum:** 2026-01-22
**Quelle:** Gemini Strategic Planning - Hardening Phase
**Status:** Konzept-Definition

---

## 🎯 Kernidee

MCTS nutzen **nicht nur für Reasoning**, sondern auch für **Informations-Beschaffung**. Das System entscheidet autonom: "Welche Quelle sollte ich als nächstes anzapfen, um die Unsicherheit optimal zu reduzieren?"

---

## 1. Das Problem: Informations-Überflutung

### Naiver Ansatz
```python
# Schlechte Strategie
for source in ALL_SOURCES:
    scrape(source)
    extract_spo(source)

# Problem: Verschwendet Zeit auf irrelevante Quellen
```

### Intelligenter Ansatz
```python
# MCTS entscheidet
while uncertainty > threshold:
    best_source = mcts.select_information_source()
    data = scrape(best_source)
    uncertainty = recalculate_uncertainty()
```

---

## 2. Meta-MCTS: Suche nach Erkenntnis

### Konzept
Ein **zweiter MCTS** der nicht die Antwort sucht, sondern die **beste Such-Strategie**.

```
Haupt-MCTS (Reasoning):
  "Was ist die Antwort auf die Frage?"

Meta-MCTS (Epistemisch):
  "Wo finde ich die Information um diese Frage zu beantworten?"
```

### Architektur

```python
class EpistemicMCTS:
    """MCTS für Information Gathering"""

    def __init__(self, knowledge_graph, uncertainty_model):
        self.graph = knowledge_graph
        self.uncertainty = uncertainty_model
        self.available_actions = self._get_info_sources()

    def _get_info_sources(self) -> List[InformationAction]:
        """Definiere mögliche Informations-Quellen"""
        return [
            InformationAction(
                type="scrape_reddit",
                params={"subreddit": "r/Solar"},
                cost_estimate={"time": 30, "tokens": 5000},
                expected_gain="medium"
            ),
            InformationAction(
                type="query_api",
                params={"api": "financial_data_api"},
                cost_estimate={"time": 5, "tokens": 1000},
                expected_gain="high"
            ),
            InformationAction(
                type="transcribe_youtube",
                params={"channel": "Expert_Reviews"},
                cost_estimate={"time": 120, "tokens": 15000},
                expected_gain="low"  # Meist wenig neue Info
            ),
            InformationAction(
                type="deep_web_search",
                params={"query": "specific_technical_detail"},
                cost_estimate={"time": 60, "tokens": 8000},
                expected_gain="medium"
            )
        ]

    def select_best_action(self) -> InformationAction:
        """Wähle Aktion die Uncertainty am meisten senkt"""

        # Standard MCTS Loop
        for iteration in range(self.max_iterations):
            node = self.tree_policy()  # Selection + Expansion
            reward = self.simulate(node)  # Simulation
            self.backpropagate(node, reward)  # Update

        # Beste Aktion = Kind mit höchstem UCB
        return max(self.root.children, key=lambda c: c.ucb_score())
```

---

## 3. Uncertainty Model

### Konzept: Entropie im Knowledge Graph

```python
class UncertaintyModel:
    """Berechnet Unsicherheit im Wissens-Graphen"""

    def calculate_node_uncertainty(self, node: GraphNode) -> float:
        """Wie unsicher sind wir über diesen Node?"""

        uncertainty = 0.0

        # Faktor 1: Anzahl widersprüchlicher Tripletts
        conflicts = node.get_conflicting_triples()
        uncertainty += len(conflicts) * 0.3

        # Faktor 2: Bias-Varianz der Quellen
        source_biases = [t.source_bias for t in node.triples]
        bias_variance = np.var([b.to_vector() for b in source_biases])
        uncertainty += bias_variance * 0.4

        # Faktor 3: Coverage
        if node.coverage < 0.5:
            uncertainty += (1.0 - node.coverage) * 0.5

        # Faktor 4: Confidence-Scores
        avg_confidence = np.mean([t.confidence for t in node.triples])
        uncertainty += (1.0 - avg_confidence) * 0.3

        return min(uncertainty, 1.0)  # Cap bei 1.0

    def calculate_global_uncertainty(self) -> float:
        """Gesamtunsicherheit im Graph"""

        node_uncertainties = [
            self.calculate_node_uncertainty(node)
            for node in self.graph.nodes
        ]

        # Gewichtete Summe (wichtige Nodes zählen mehr)
        weighted_sum = sum(
            u * node.importance
            for u, node in zip(node_uncertainties, self.graph.nodes)
        )

        total_importance = sum(n.importance for n in self.graph.nodes)

        return weighted_sum / total_importance
```

---

## 4. Information Gain Estimation

### Konzept: Value of Information (VoI)

```python
def estimate_information_gain(
    action: InformationAction,
    current_uncertainty: float
) -> float:
    """Schätze wie viel Unsicherheit diese Aktion reduziert"""

    # Basis-Schätzung aus Historie
    if action.type in self.action_history:
        historical_gains = [
            h.uncertainty_before - h.uncertainty_after
            for h in self.action_history[action.type]
        ]
        expected_gain = np.mean(historical_gains)
    else:
        # Default-Schätzungen
        expected_gain = {
            "scrape_reddit": 0.3,
            "query_api": 0.5,  # APIs meist präzise
            "transcribe_youtube": 0.2,
            "deep_web_search": 0.35
        }.get(action.type, 0.25)

    # Anpassung basierend auf aktuellem Stand
    # Je höher die Unsicherheit, desto mehr Potential
    adjusted_gain = expected_gain * current_uncertainty

    return adjusted_gain
```

### Value of Information (VoI) Berechnung

```python
def calculate_voi(
    action: InformationAction,
    current_uncertainty: float
) -> float:
    """
    VoI = (Expected Uncertainty Reduction) / (Cost)

    Höherer VoI = Bessere Aktion
    """

    # Erwartete Unsicherheits-Reduktion
    expected_gain = estimate_information_gain(action, current_uncertainty)

    # Kosten (normalisiert)
    time_cost = action.cost_estimate["time"] / 120.0  # Normalisiert auf 2h
    token_cost = action.cost_estimate["tokens"] / 10000.0

    total_cost = time_cost + token_cost

    # VoI = Gain / Cost
    voi = expected_gain / (total_cost + 0.01)  # +0.01 um Division durch 0 zu vermeiden

    return voi
```

---

## 5. MCTS Simulation für Info-Gathering

### Simulation-Funktion

```python
def simulate_information_action(
    self,
    action: InformationAction
) -> float:
    """Simuliere den Effekt dieser Aktion"""

    # 1. Schätze welche Tripletts wir finden würden
    estimated_triples = self._estimate_triple_yield(action)

    # 2. Simuliere Integration in Graph
    simulated_graph = self.graph.copy()
    for triple in estimated_triples:
        simulated_graph.add_triple(triple, temp=True)

    # 3. Berechne neue Unsicherheit
    new_uncertainty = self.uncertainty.calculate_global_uncertainty()

    # 4. Reward = Unsicherheits-Reduktion
    uncertainty_reduction = self.current_uncertainty - new_uncertainty

    # 5. Penalty für Kosten
    cost_penalty = action.cost_estimate["time"] / 1000.0

    return uncertainty_reduction - cost_penalty

def _estimate_triple_yield(self, action: InformationAction) -> List[SPOTriple]:
    """Schätze wie viele Tripletts wir aus dieser Quelle bekommen"""

    # Nutze historische Daten oder Heuristiken
    if action.type == "scrape_reddit":
        # Reddit: Viele Posts, aber viel Noise
        return [
            self._generate_plausible_triple(quality=0.6)
            for _ in range(np.random.poisson(8))  # Durchschnittlich 8 Tripletts
        ]

    elif action.type == "query_api":
        # API: Wenig Daten, aber hochwertig
        return [
            self._generate_plausible_triple(quality=0.9)
            for _ in range(np.random.poisson(3))  # Durchschnittlich 3 Tripletts
        ]

    # etc.
```

---

## 6. Dynamic Scraping Queue

### Konzept: Automatische Priorisierung

```python
class DynamicScrapingQueue:
    """Verwaltet Scraping-Tasks basierend auf MCTS-Entscheidungen"""

    def __init__(self, epistemic_mcts: EpistemicMCTS):
        self.mcts = epistemic_mcts
        self.queue: List[InformationAction] = []
        self.completed: List[InformationAction] = []

    def update_queue(self):
        """Aktualisiere Queue basierend auf aktueller Unsicherheit"""

        # MCTS entscheidet: Was sind die Top-3 Aktionen?
        top_actions = []

        for _ in range(3):  # Top-3
            best_action = self.mcts.select_best_action()
            top_actions.append(best_action)

            # Temporary: Entferne aus verfügbaren Aktionen
            self.mcts.available_actions.remove(best_action)

        # Restore verfügbare Aktionen
        self.mcts.available_actions.extend(top_actions)

        # Update Queue
        self.queue = top_actions

    def execute_next(self) -> Optional[ScrapingResult]:
        """Führe nächste Aktion aus"""

        if not self.queue:
            self.update_queue()

        if not self.queue:
            return None  # Keine sinnvollen Aktionen mehr

        action = self.queue.pop(0)

        # Execute
        result = self._execute_action(action)

        # Log für Lernen
        self.completed.append(action)

        # Update Unsicherheit
        new_uncertainty = self.mcts.uncertainty.calculate_global_uncertainty()

        # Feedback an MCTS
        actual_gain = self.mcts.current_uncertainty - new_uncertainty
        self.mcts.update_action_history(action, actual_gain)

        return result
```

---

## 7. Praktisches Beispiel: Solar-ROI-Recherche

### Szenario
User fragt: "Ist Solaranlage wirtschaftlich?"

MCTS hat bereits einige Daten, aber **Widersprüche bei Wartungskosten**.

### Unsicherheits-Analyse

```python
# Current State
node_wartungskosten = graph.get_node("Wartungskosten")

triples = [
    ("Solaranlage", "Wartung_pro_Jahr", "1%"),    # Quelle: Hersteller
    ("Solaranlage", "Wartung_pro_Jahr", "3%"),    # Quelle: Reddit
    ("Solaranlage", "Wartung_pro_Jahr", "0.5%"),  # Quelle: Optimistischer Blog
]

uncertainty = uncertainty_model.calculate_node_uncertainty(node_wartungskosten)
# → 0.75 (hoch, wegen Widersprüchen)
```

### Epistemisches MCTS entscheidet

```python
available_actions = [
    InformationAction(
        type="scrape_reddit",
        params={"subreddit": "r/Solar", "query": "Wartungskosten Erfahrung"},
        cost={"time": 30, "tokens": 5000},
        expected_gain=0.4  # Viele Erfahrungsberichte
    ),
    InformationAction(
        type="query_stiftung_warentest",
        params={"topic": "Solar Langzeittest"},
        cost={"time": 10, "tokens": 2000},
        expected_gain=0.7  # Hochwertige Daten
    ),
    InformationAction(
        type="scrape_maintenance_forums",
        params={"forum": "Photovoltaikforum"},
        cost={"time": 45, "tokens": 8000},
        expected_gain=0.6  # Spezialisiert
    )
]

# VoI Berechnung
voi_scores = {
    "reddit": 0.4 / 35 = 0.011,
    "stiftung_warentest": 0.7 / 12 = 0.058,  # BEST
    "forums": 0.6 / 53 = 0.011
}

# Entscheidung: Stiftung Warentest hat höchsten VoI
selected_action = "query_stiftung_warentest"
```

### Ausführung & Update

```python
# Execute
result = execute_action("query_stiftung_warentest")

# Neue Tripletts
new_triple = ("Solaranlage", "Wartung_pro_Jahr", "1.5%")  # Quelle: ST
new_triple.confidence = 0.95  # Sehr vertrauenswürdig

# Graph Update
graph.add_verified_triple(new_triple)

# Neue Unsicherheit
new_uncertainty = 0.25  # Deutlich reduziert!

# MCTS lernt: "Stiftung Warentest war sehr wertvoll"
mcts.update_action_history(
    action="query_stiftung_warentest",
    actual_gain=0.75 - 0.25 = 0.50  # Sogar besser als erwartet (0.7)
)
```

---

## 8. Abbruch-Bedingungen

### Wann aufhören zu suchen?

```python
class StoppingCriteria:
    """Entscheidet wann genug Information gesammelt wurde"""

    def should_stop_gathering(
        self,
        current_uncertainty: float,
        time_spent: float,
        actions_completed: int
    ) -> bool:
        """Mehrere Kriterien für Abbruch"""

        # Kriterium 1: Uncertainty niedrig genug
        if current_uncertainty < self.uncertainty_threshold:
            return True

        # Kriterium 2: Diminishing Returns
        if actions_completed >= 3:
            last_3_gains = self.action_history[-3:]
            avg_gain = np.mean([a.actual_gain for a in last_3_gains])

            if avg_gain < 0.05:  # Kaum noch Fortschritt
                return True

        # Kriterium 3: Zeit-Budget erschöpft
        if time_spent > self.max_time_budget:
            return True

        # Kriterium 4: Beste verfügbare Aktion hat VoI < Threshold
        best_voi = max(calculate_voi(a) for a in self.available_actions)
        if best_voi < 0.01:  # Keine gute Option mehr
            return True

        return False
```

---

## 9. Integration mit Haupt-MCTS

### Zwei-Ebenen-Architektur

```python
class TwoLevelMCTS:
    """Kombiniert Reasoning-MCTS und Epistemisches MCTS"""

    def __init__(self):
        self.reasoning_mcts = MCTSEngine()  # Haupt-Reasoning
        self.epistemic_mcts = EpistemicMCTS()  # Info-Gathering

    def research_loop(self, question: str) -> Answer:
        """Haupt-Forschungsschleife"""

        while not self.is_complete():

            # 1. Reasoning-Phase: Versuche Frage zu beantworten
            current_answer = self.reasoning_mcts.search(question)

            # 2. Uncertainty-Check: Wie sicher sind wir?
            uncertainty = self.epistemic_mcts.uncertainty.calculate_global_uncertainty()

            # 3. Wenn zu unsicher: Info-Gathering
            if uncertainty > self.threshold:
                print(f"Unsicherheit zu hoch ({uncertainty:.2f}), starte Info-Gathering...")

                # Epistemisches MCTS entscheidet
                action = self.epistemic_mcts.select_best_action()

                # Execute
                result = self.execute_information_action(action)

                # Update Graph
                self.reasoning_mcts.graph.integrate(result)

                # Reasoning MCTS muss neu evaluieren
                self.reasoning_mcts.invalidate_cache()

            else:
                # Unsicherheit akzeptabel, Antwort ist gut genug
                return current_answer

        return current_answer
```

---

## 10. Lernende Heuristiken

### System lernt aus Erfahrung

```python
class AdaptiveInfoGatheringPolicy:
    """Lernt welche Quellen für welche Fragen am besten sind"""

    def __init__(self):
        self.source_performance = defaultdict(list)

    def record_outcome(
        self,
        source: str,
        query_type: str,
        uncertainty_before: float,
        uncertainty_after: float,
        cost: float
    ):
        """Logge Performance einer Quelle"""

        gain = uncertainty_before - uncertainty_after
        efficiency = gain / cost

        self.source_performance[(source, query_type)].append({
            "gain": gain,
            "efficiency": efficiency,
            "timestamp": datetime.now()
        })

    def get_expected_efficiency(self, source: str, query_type: str) -> float:
        """Schätze Effizienz basierend auf Historie"""

        history = self.source_performance[(source, query_type)]

        if not history:
            return 0.5  # Default

        # Exponential weighted average (neuere Daten zählen mehr)
        weights = np.exp(-np.arange(len(history)) * 0.1)
        weights /= weights.sum()

        efficiencies = [h["efficiency"] for h in history]

        return np.average(efficiencies, weights=weights)
```

---

## 11. Implementation Checklist

### Phase 1: Basic Epistemisches MCTS
```
□ UncertaintyModel Class
□ InformationAction Dataclass
□ EpistemicMCTS mit VoI-Berechnung
□ Stopping Criteria
```

### Phase 2: Dynamic Scraping
```
□ DynamicScrapingQueue
□ Action Executor (Reddit, API, YouTube)
□ Feedback-Loop für Lernen
```

### Phase 3: Integration
```
□ TwoLevelMCTS Architecture
□ AdaptiveInfoGatheringPolicy
□ Visualization (Uncertainty over Time)
```

---

## Referenzen
- Active Learning - Machine Learning Survey 2023
- Value of Information - Decision Theory
- Epistemic Uncertainty - AI Safety Research
- Gemini Strategic Planning Session (Jan 2026)
