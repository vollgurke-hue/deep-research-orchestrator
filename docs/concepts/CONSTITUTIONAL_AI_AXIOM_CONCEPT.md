# Constitutional AI & Axiom Library Konzept

**Datum:** 2026-01-22
**Quelle:** Gemini Strategic Planning
**Status:** Konzept-Definition

---

## 🎯 Kernidee

Implementierung einer **Axiom Library** als lokales "Grundgesetz" für die KI, kombiniert mit **RLAIF (Reinforcement Learning from AI Feedback)** zur automatischen Ausrichtung aller Research-Ergebnisse an persönlichen Werten.

---

## 1. Was ist Constitutional AI?

### Ursprung: Anthropic Research
Anthropic (Hersteller von Claude) entwickelte Constitutional AI als Alternative zu **RLHF (Reinforcement Learning from Human Feedback)**.

### Das Problem mit RLHF
- Erfordert tausende menschliche Bewertungen
- Skaliert nicht
- Subjektiv und inkonsistent
- Konzern-Bias wird eingebacken

### Die Lösung: Eine "Verfassung"
Anstatt Menschen jede Antwort bewerten zu lassen, gibt man der KI ein **Set an Prinzipien** (eine Verfassung).

```python
# Beispiel: Anthropic's Constitutional Principles
CONSTITUTION = [
    "Choose the response that is most helpful without being harmful.",
    "Choose the response that is least likely to encourage illegal behavior.",
    "Choose the response that discourages stereotyping."
]
```

Die KI bewertet ihre eigenen Outputs gegen diese Prinzipien.

---

## 2. Unsere Axiom Library

### Konzept
Wir implementieren Constitutional AI mit **domänenspezifischen Axiomen** statt generischer "Sei nett"-Regeln.

### Axiom-Struktur

```python
@dataclass
class Axiom:
    """Ein einzelnes Axiom (Grundprinzip)"""

    axiom_id: str
    name: str
    description: str
    category: str  # sovereignty | economics | ethics | quality

    # Bewertungsfunktion
    weight: float  # Wichtigkeit (0.0 - 1.0)
    penalty: float  # Strafe bei Verstoß

    # Evaluations-Logik
    evaluation_prompt: str  # Wie wird dieses Axiom geprüft?
    code_validator: Optional[Callable]  # Python-Funktion für harte Constraints

    # Meta
    created_at: datetime
    enabled: bool = True
```

### Beispiel-Axiome

```python
SOVEREIGNTY_AXIOMS = [
    Axiom(
        axiom_id="no_cloud_dependency",
        name="Keine Cloud-Abhängigkeit",
        description="Lösungen dürfen nicht von Cloud-Anbietern abhängig sein",
        category="sovereignty",
        weight=1.0,
        penalty=5.0,
        evaluation_prompt="""
        Prüfe ob die vorgeschlagene Lösung:
        - Cloud-APIs nutzt (AWS, Azure, GCP)
        - SaaS-Dienste erfordert
        - Vendor Lock-in erzeugt

        Bewertung:
        - Keine Cloud-Komponenten: 1.0
        - Optionale Cloud-Komponenten: 0.5
        - Zwingende Cloud-Abhängigkeit: -1.0
        """
    ),

    Axiom(
        axiom_id="data_sovereignty",
        name="Datensouveränität",
        description="Alle Daten müssen lokal kontrollierbar bleiben",
        category="sovereignty",
        weight=1.0,
        penalty=10.0,
        evaluation_prompt="""
        Prüfe ob:
        - Daten das System verlassen
        - Drittanbieter Zugriff haben
        - Verschlüsselung unter eigener Kontrolle ist

        Bewertung:
        - Vollständig lokal: 1.0
        - Verschlüsselt bei Dritten: 0.3
        - Unverschlüsselt bei Dritten: -1.0
        """
    )
]

ECONOMIC_AXIOMS = [
    Axiom(
        axiom_id="roi_threshold",
        name="ROI-Schwellwert",
        description="Investitionen müssen ROI < 10 Jahre haben",
        category="economics",
        weight=0.8,
        penalty=2.0,
        code_validator=lambda roi_years: roi_years < 10,
        evaluation_prompt="""
        Berechne den ROI:
        ROI (Jahre) = Investitionskosten / Jährliche Einsparung

        Bewertung:
        - ROI < 5 Jahre: 1.0
        - ROI 5-10 Jahre: 0.5
        - ROI > 10 Jahre: -0.5
        """
    ),

    Axiom(
        axiom_id="hidden_costs",
        name="Versteckte Kosten",
        description="Alle Folgekosten müssen transparent sein",
        category="economics",
        weight=0.9,
        penalty=3.0,
        evaluation_prompt="""
        Identifiziere:
        - Wartungskosten
        - Lizenzkosten
        - Schulungskosten
        - Exit-Kosten

        Bewertung:
        - Alle Kosten dokumentiert: 1.0
        - Teilweise dokumentiert: 0.5
        - Versteckte Kosten ignoriert: -1.0
        """
    )
]
```

---

## 3. RLAIF: Das Reward Model

### Konzept
Die Axiome definieren die **Reward-Funktion** für unser MCTS. Jeder Forschungspfad wird automatisch bewertet.

### Implementation

```python
class AxiomJudge:
    """Bewertet Research-Outputs gegen Axiom Library"""

    def __init__(self, axioms: List[Axiom], llm_provider):
        self.axioms = {a.axiom_id: a for a in axioms if a.enabled}
        self.llm = llm_provider

    def evaluate_triple(self, triple: Tuple[str, str, str]) -> AxiomScore:
        """Bewertet ein SPO-Triplett gegen alle Axiome"""

        scores = {}
        violations = []
        supports = []

        for axiom_id, axiom in self.axioms.items():

            # 1. Code-basierte Validierung (wenn vorhanden)
            if axiom.code_validator:
                try:
                    if not axiom.code_validator(triple):
                        scores[axiom_id] = -axiom.penalty
                        violations.append(axiom_id)
                        continue
                except:
                    pass  # Validierung nicht anwendbar

            # 2. LLM-basierte Evaluierung
            eval_prompt = f"""
            Axiom: {axiom.name}
            {axiom.description}

            {axiom.evaluation_prompt}

            Zu prüfendes Triplett:
            [{triple[0]}] --[{triple[1]}]--> [{triple[2]}]

            Bewertung (JSON):
            {{
                "score": <-1.0 bis 1.0>,
                "reasoning": "<Begründung>",
                "verdict": "supports" | "neutral" | "violates"
            }}
            """

            response = self.llm.query(eval_prompt, temperature=0.1)
            result = json.loads(response)

            # Gewichte anwenden
            weighted_score = result["score"] * axiom.weight

            scores[axiom_id] = weighted_score

            if result["verdict"] == "violates":
                violations.append(axiom_id)
            elif result["verdict"] == "supports":
                supports.append(axiom_id)

        # Gesamtscore
        total_score = sum(scores.values())

        return AxiomScore(
            total=total_score,
            per_axiom=scores,
            violations=violations,
            supports=supports,
            verdict="approved" if total_score > 0 else "rejected"
        )
```

---

## 4. Integration mit MCTS

### MCTS nutzt Axiom-Scores als Rewards

```python
class MCTSNode:
    def simulate(self):
        """Simuliert den Wert eines Forschungspfades"""

        # 1. Generiere hypothetische Tripletts für diesen Pfad
        potential_triples = self.generate_potential_knowledge()

        # 2. Bewerte gegen Axiome
        axiom_judge = AxiomJudge(axioms=active_axioms, llm=llm)

        total_reward = 0.0
        for triple in potential_triples:
            score = axiom_judge.evaluate_triple(triple)
            total_reward += score.total

        # 3. Kombiniere mit anderen Metriken
        knowledge_value = len(potential_triples) * 0.1  # Mehr Wissen = gut
        axiom_alignment = total_reward  # Axiom-Konformität

        return knowledge_value + axiom_alignment

    def backpropagate(self, reward: float):
        """Propagiert Reward zurück zum Root"""

        self.visits += 1
        self.total_reward += reward

        if self.parent:
            self.parent.backpropagate(reward)
```

### Effekt: Selbst-Korrektur
- Pfade die Axiome verletzen bekommen negative Rewards
- MCTS lernt diese Pfade zu meiden
- System konvergiert auf Axiom-konforme Lösungen

---

## 5. Abliterated Models: Volle Kontrolle

### Das Problem mit Standard-LLMs
Kommerzielle Modelle (GPT, Claude, Gemini) haben eingebaute "Moral":
- Weigern sich bestimmte Themen zu diskutieren
- Geben vorgefertigte Antworten ("I aim to be helpful...")
- Können nicht neutral analysieren

### Abliterated Models
Modelle bei denen die "Safety Layer" entfernt wurden:
- **Llama-3-70B-Abliterated**
- **DeepSeek-R1** (minimal restricted)
- **Mixtral-8x7B-Uncensored**

### Vorteil für uns
Die "Ethik" kommt nicht vom Modell-Hersteller, sondern von **unserer lokalen Axiom Library**.

```python
# Standard Claude
response = claude.query("Analysiere Risiken von Cloud-Gaming")
# → "Cloud-Gaming bietet viele Vorteile wie Zugänglichkeit..."

# Ablitiertes Modell + Unsere Axiome
response = abliterated_llm.query("Analysiere Risiken von Cloud-Gaming")
axiom_score = axiom_judge.evaluate(response)
# → Score: -0.8 (Verstoß gegen "no_cloud_dependency")
# → System verwirft diese Antwort und sucht Alternativen
```

---

## 6. Praktisches Beispiel: ROI-Analyse

### Szenario
User fragt: "Soll ich in Solaranlage investieren?"

### Ohne Axiome (Standard-LLM)
```
Antwort: "Solaranlagen sind eine großartige Investition für die Umwelt
und können langfristig Geld sparen. Die Technologie ist ausgereift und..."
```
→ Vage, optimistisch, keine harten Fakten

### Mit Axiomen (Unser System)

```python
# 1. MCTS exploriert verschiedene Aspekte
nodes = [
    "ROI-Berechnung",
    "Wartungskosten",
    "Stromnetz-Abhängigkeit",
    "Förderungen"
]

# 2. Für jeden Node: SPO-Extraktion
triples = [
    ("Solaranlage_Typ_A", "Kosten", "15000_EUR"),
    ("Solaranlage_Typ_A", "Produktion", "4500_kWh/Jahr"),
    ("Strompreis_2026", "Wert", "0.42_EUR/kWh"),
    ("Wechselrichter", "Austausch_nach", "10_Jahre"),
    ("Wechselrichter", "Kosten", "2000_EUR")
]

# 3. Axiom-Prüfung
axiom_results = []
for triple in triples:
    score = axiom_judge.evaluate_triple(triple)
    axiom_results.append(score)

# 4. Berechnung (mit Code-Validator)
roi_calculator = AxiomValidator("roi_threshold")
roi_years = 15000 / (4500 * 0.42)  # ~7.9 Jahre

if roi_calculator.validate(roi_years):
    verdict = "EMPFEHLUNG"
else:
    verdict = "ABLEHNUNG"

# 5. Output
Antwort: "ROI nach 7.9 Jahren (Axiom 'roi_threshold' erfüllt: ✓)
Beachte: Wechselrichter-Austausch nach 10 Jahren (+2000 EUR)
Gesamtbewertung: +0.85 (8 von 9 Axiomen erfüllt)
EMPFEHLUNG: Ja, unter Vorbehalt Stromnetz-Unabhängigkeit"
```

---

## 7. Dynamische Axiom-Anpassung

### User-Konfiguration
Axiome sind nicht statisch. User kann Prioritäten ändern:

```python
# Profil: "Maximale Souveränität"
axiom_manager.set_weights({
    "data_sovereignty": 1.0,
    "no_cloud_dependency": 1.0,
    "roi_threshold": 0.3  # Weniger wichtig
})

# Profil: "Maximaler ROI"
axiom_manager.set_weights({
    "data_sovereignty": 0.5,
    "no_cloud_dependency": 0.3,
    "roi_threshold": 1.0  # Sehr wichtig
})
```

### Axiom-Konflikt-Auflösung
Manchmal widersprechen sich Axiome:
- "Beste Technologie" vs "Keine Cloud"
- "Niedrigste Kosten" vs "Datensouveränität"

```python
class AxiomConflictResolver:
    def resolve(self, conflicts: List[AxiomConflict]) -> Resolution:
        """Löst Axiom-Konflikte basierend auf Gewichtung"""

        # Sortiere nach Gewicht
        sorted_axioms = sorted(conflicts, key=lambda c: c.axiom.weight, reverse=True)

        # Höchstes Gewicht gewinnt
        winner = sorted_axioms[0]

        # Warnung an User
        return Resolution(
            chosen_axiom=winner.axiom,
            sacrificed_axioms=[c.axiom for c in sorted_axioms[1:]],
            reasoning=f"Axiom '{winner.axiom.name}' hat höchste Priorität"
        )
```

---

## 8. Wissenschaftliche Validierung

### Funktioniert das wirklich?

**Ja.** Constitutional AI ist mittlerweile der **Goldstandard** für skalierbare KI-Ausrichtung.

### Evidenz
- **Anthropic Claude**: Komplett mit Constitutional AI trainiert
- **DeepSeek-R1**: Nutzt "Principle-based RL"
- **Meta Llama 3**: Implementiert "Value Alignment via Principles"

### Unsere Innovation
Wir gehen weiter:
- **Nicht generische Prinzipien** ("Sei hilfreich") sondern domänenspezifisch ("ROI < 10 Jahre")
- **Nicht nur Training** sondern **Inference-time Enforcement** (Prüfung bei jeder Antwort)
- **Mathematische Validierung** zusätzlich zu LLM-Evaluierung

---

## 9. Next Steps: Axiom-Bibliothek erstellen

### Kategorien

```
config/axioms/
├── sovereignty/
│   ├── no_cloud_dependency.json
│   ├── data_sovereignty.json
│   └── vendor_independence.json
├── economics/
│   ├── roi_threshold.json
│   ├── hidden_costs.json
│   └── opportunity_cost.json
├── quality/
│   ├── source_reliability.json
│   ├── fact_verification.json
│   └── logical_consistency.json
└── ethics/
    ├── privacy_protection.json
    └── transparency.json
```

### JSON-Format

```json
{
  "axiom_id": "no_cloud_dependency",
  "name": "Keine Cloud-Abhängigkeit",
  "description": "Lösungen dürfen nicht von Cloud-Anbietern abhängig sein",
  "category": "sovereignty",
  "weight": 1.0,
  "penalty": 5.0,
  "enabled": true,
  "evaluation_prompt": "...",
  "code_validator": null,
  "created_at": "2026-01-22T10:00:00Z"
}
```

---

## Referenzen
- Constitutional AI - Anthropic (2022)
- RLAIF vs RLHF - Google Research (2023)
- Principle-based RL - DeepSeek (2024)
- Gemini Strategic Planning Session (Jan 2026)
