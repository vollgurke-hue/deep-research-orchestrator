# Recursive Language Models (RLM) Konzept

**Datum:** 2026-01-22
**Quelle:** MIT Paper (arXiv:2512.24601) + Gemini Strategic Planning
**Status:** Konzept-Definition

---

## 🎯 Kernidee

Nutzung von **Recursive Language Models (RLMs)** zur Verarbeitung von Kontexten, die **100x größer** sind als das Context Window des Modells, durch programmatische Exploration und selbst-rekursive Aufrufe.

---

## 1. Das Problem: Context Rot

### Standard-LLM Ansatz
Wir laden einen langen Text (Prompt) ins Modell und hoffen, dass es "alles versteht".

```python
# Traditionell
prompt = load_entire_dataset()  # 500.000 Tokens
response = llm.complete(prompt)
```

### Das Problem ab 100k+ Tokens
- **Context Rot**: Logische Tiefe bricht ein
- **Lost in the Middle**: Modell vergisst Anfang
- **Kosten explodieren**: Jeder Token kostet
- **Halluzinationen steigen**: Bei zu viel Input steigt Fehlerrate

### Forschungs-Evidenz (MIT Paper)
Selbst GPT-4 mit 128k Context Window zeigt massiven Qualitätsverlust bei >50k Tokens.

---

## 2. Die RLM-Lösung: Prompt als Environment

### Paradigmenwechsel

**Alt:**
```
Text → In LLM laden → Hoffen dass es funktioniert
```

**Neu (RLM):**
```
Text → Als Python-Variable speichern → LLM schreibt Code um Text zu durchsuchen
```

### Konzept: Externe Umgebung

```python
# Der gesamte Datensatz wird NICHT ins LLM geladen
massive_dataset = load_all_reddit_posts()  # 10 Millionen Tokens

# Stattdessen: In Python-Umgebung (REPL) als Variable
env = PythonREPL()
env.set_variable("dataset", massive_dataset)

# LLM bekommt nur: "Es gibt eine Variable 'dataset' mit 10M Posts"
# LLM schreibt Code um diese zu durchsuchen
code = llm.generate_exploration_code(
    task="Finde alle Posts über Solaranlagen-Probleme",
    environment_description="Variable 'dataset' mit Reddit-Posts"
)

# Code wird ausgeführt, Ergebnis zurück ans LLM
result = env.execute(code)

# LLM kann sich REKURSIV selbst aufrufen für Teilmengen
if result.needs_deeper_analysis:
    sub_code = llm.generate_exploration_code(
        task="Analysiere gefundene Posts im Detail",
        input_data=result.summary  # Nur Summary, nicht alle Daten!
    )
```

---

## 3. Technische Mechanik

### A. Environment Setup

```python
class RLMEnvironment:
    """Verwaltet externe Daten für RLM"""

    def __init__(self):
        self.variables = {}
        self.code_history = []

    def load_dataset(self, name: str, data: Any):
        """Lädt Daten als Variable (nicht ins LLM!)"""
        self.variables[name] = data

    def execute_code(self, code: str) -> ExecutionResult:
        """Führt LLM-generierten Code aus"""

        # Sicherheits-Sandbox
        safe_globals = {
            "variables": self.variables,
            "search": self.search_function,
            "filter": self.filter_function,
            "slice": self.slice_function,
            # Keine gefährlichen Funktionen (os, sys, etc.)
        }

        try:
            exec(code, safe_globals)
            result = safe_globals.get("result", None)
            return ExecutionResult(success=True, data=result)
        except Exception as e:
            return ExecutionResult(success=False, error=str(e))
```

### B. RLM-Aufruf mit Recursion

```python
class RecursiveLLM:
    """LLM das sich selbst rekursiv aufrufen kann"""

    def __init__(self, llm_provider, environment: RLMEnvironment):
        self.llm = llm_provider
        self.env = environment
        self.recursion_depth = 0
        self.max_recursion = 10

    def query_with_massive_context(
        self,
        task: str,
        dataset_name: str,
        recursion_budget: int = 5
    ) -> str:
        """Verarbeitet Daten die größer sind als Context Window"""

        if self.recursion_depth >= self.max_recursion:
            return "Max recursion reached"

        # 1. LLM bekommt Meta-Information (nicht Daten selbst)
        meta_prompt = f"""
        Task: {task}

        Environment:
        - Variable '{dataset_name}' enthält große Datenmenge
        - Du kannst Python-Code schreiben um diese zu durchsuchen

        Verfügbare Operationen:
        - search(dataset, query) → Findet relevante Einträge
        - filter(dataset, condition) → Filtert nach Bedingung
        - slice(dataset, start, end) → Nimmt Ausschnitt
        - recursive_call(subtask, subset) → Ruft dich selbst für Teilmenge auf

        Schreibe Code der:
        1. Die relevanten Daten findet
        2. Bei Bedarf recursive_call() nutzt für Details
        3. Ergebnis als 'result' zurückgibt

        Code:
        """

        # 2. LLM generiert Explorations-Code
        code = self.llm.query(meta_prompt, temperature=0.3)

        # 3. Code ausführen
        execution = self.env.execute_code(code)

        # 4. Wenn Code recursive_call() genutzt hat
        if execution.has_recursive_calls:
            for call in execution.recursive_calls:
                self.recursion_depth += 1
                sub_result = self.query_with_massive_context(
                    task=call.subtask,
                    dataset_name=call.subset_name,
                    recursion_budget=recursion_budget - 1
                )
                # Sub-Result zurück in Environment
                self.env.variables[call.result_name] = sub_result
                self.recursion_depth -= 1

        # 5. Final Answer
        return execution.result
```

---

## 4. Anwendung im SRO: Reddit-Validierung

### Problem
Wir wollen 1 Million Reddit-Posts nach "Friction" (realen Problemen) durchsuchen.

### Traditioneller Ansatz (scheitert)
```python
# Unmöglich: Alle Posts ins LLM laden
all_posts = reddit_scraper.fetch_all()  # 5M Tokens
response = llm.query(f"Analysiere diese Posts: {all_posts}")
# → Context Rot, Kosten explodieren
```

### RLM-Ansatz

```python
# 1. Posts als Environment-Variable
env = RLMEnvironment()
env.load_dataset("reddit_solar", all_reddit_posts)

# 2. RLM-Exploration
rlm = RecursiveLLM(llm_provider, env)

result = rlm.query_with_massive_context(
    task="Finde alle Posts die von Solaranlagen-PROBLEMEN berichten",
    dataset_name="reddit_solar"
)

# 3. LLM generiert z.B. diesen Code:
"""
# Generated by LLM:
problem_keywords = ["defekt", "ausgefallen", "problem", "enttäuscht"]

# Erste Filter-Runde (massiv reduzieren)
candidates = search(variables["reddit_solar"], problem_keywords)

# Für jeden Kandidaten: Rekursive Detail-Analyse
for i, post in enumerate(candidates[:100]):  # Nur Top 100
    result = recursive_call(
        subtask=f"Extrahiere SPO-Tripletts über Probleme aus Post",
        subset=post
    )

result = aggregated_tripletts
"""

# 4. Rekursive Aufrufe prozessieren nur kleine Schnipsel
# Jeder Aufruf bleibt unter 10k Tokens → Kein Context Rot
```

---

## 5. Vorteile für SRO

### A. Massive Skalierung der Sovereign Truth

**Ohne RLM:**
- Maximal ~100k Tokens verarbeitbar
- ~50 Dokumente gleichzeitig

**Mit RLM:**
- 10M+ Tokens verarbeitbar
- Tausende Dokumente
- Ganze Datenbanken, Archive, Gesetztexte

### B. Automatisierte SPO-Extraktion

```python
# RLM-Script für SPO-Batch-Extraktion
rlm_task = """
Gehe durch alle Dokumente in 'legal_documents' und:
1. Identifiziere relevante Paragraphen für 'Datenschutz'
2. Für jeden Paragraph: Extrahiere SPO-Tripletts
3. Aggregiere in Master-Liste

Nutze recursive_call() für jeden Paragraph einzeln.
"""

tripletts = rlm.query_with_massive_context(
    task=rlm_task,
    dataset_name="legal_documents"
)

# Resultat: Tausende SPO-Tripletts, sauber extrahiert
```

### C. Kosteneffizienz: Sub-Model Spawning

**CEO-Worker-Architektur:**

```python
# Hauptmodell (teuer): Strategische Planung
ceo_model = "claude-opus-4"

strategy = ceo_model.query("Wie sollten wir die Solaranlagen-Recherche angehen?")
# → "Fokussiere auf: Kosten, Wartung, Haltbarkeit"

# RLM nutzt kleine Modelle (billig) für Ausführung
worker_model = "llama-3-8b"

for aspect in ["kosten", "wartung", "haltbarkeit"]:
    rlm = RecursiveLLM(worker_model, env)
    result = rlm.query_with_massive_context(
        task=f"Extrahiere alle Fakten über {aspect}",
        dataset_name="reddit_solar"
    )
```

**Kostenersparnis:**
- CEO-Call: 1x teuer (Strategie)
- Worker-Calls: 1000x billig (Ausführung)
- **Gesamt: ~80% Kostenreduktion**

### D. Kampf gegen Context Rot

**Problem bei tiefem GoT:**
Nach 50 MCTS-Schritten hat Standard-LLM den Anfang vergessen.

**RLM-Lösung:**
```python
# Alle Forschungs-Erkenntnisse als persistente Variablen
env.variables["research_step_1"] = "ROI beträgt 7.9 Jahre"
env.variables["research_step_2"] = "Wartungskosten 2% p.a."
# ... Step 50 ...

# LLM kann JEDERZEIT auf Step 1 zugreifen
code = """
# Check: Passt aktuelle Erkenntnis zu Step 1?
if current_finding.roi != variables["research_step_1"].roi:
    flag_contradiction()
"""
```

Informationen bleiben "frisch" weil sie in Python-Variablen liegen, nicht im LLM-Context.

---

## 6. Integration mit MCTS

### MCTS-Node mit RLM-Exploration

```python
class RLM_MCTSNode(MCTSNode):
    def expand(self):
        """Nutze RLM um große Datenmengen zu explorieren"""

        # Statt alle Daten zu laden: RLM-basierte Suche
        rlm_code = f"""
        # Finde relevante Daten für: {self.research_question}
        relevant = search(
            dataset=variables["knowledge_base"],
            query="{self.research_question}"
        )

        # Identifiziere Lücken
        for topic in relevant.topics:
            if topic.coverage < 0.5:
                recursive_call(
                    subtask=f"Vertiefe: {topic}",
                    subset=topic.data
                )

        result = discovered_knowledge_gaps
        """

        gaps = self.rlm.execute(rlm_code)

        # Erstelle Child-Nodes für jede Lücke
        for gap in gaps:
            child = RLM_MCTSNode(research_question=gap)
            self.children.append(child)
```

---

## 7. Praktisches Beispiel: Gesamtablauf

### Szenario
User fragt: "Ist Solaranlage wirtschaftlich unter Berücksichtigung ALLER Erfahrungsberichte?"

### Ablauf

```python
# 1. Environment Setup
env = RLMEnvironment()
env.load_dataset("reddit_solar", fetch_all_reddit_posts())  # 2M Posts
env.load_dataset("forums", fetch_solar_forums())  # 500k Posts
env.load_dataset("reviews", fetch_amazon_reviews())  # 100k Reviews

# 2. RLM Strategic Planning (mit großem Modell)
strategy = claude_opus.query("""
Environment enthält 2.6M Erfahrungsberichte.
Schreibe einen Exploration-Plan als Python-Code.
""")

# Claude generiert:
"""
# Phase 1: Problem-Identifikation
problems = search(variables["reddit_solar"], ["Problem", "defekt", "Fehler"])
problem_summary = recursive_call("Klassifiziere Probleme", problems[:1000])

# Phase 2: Kosten-Analyse
cost_posts = search(variables["reddit_solar"], ["ROI", "Kosten", "rechnet"])
cost_analysis = recursive_call("Extrahiere Kosten-Daten", cost_posts[:500])

# Phase 3: Langzeit-Erfahrung
longterm = filter(variables["reddit_solar"], lambda p: p.age_years > 5)
longterm_verdict = recursive_call("Bewerte Langzeit-Zufriedenheit", longterm)

result = {
    "problems": problem_summary,
    "costs": cost_analysis,
    "longterm": longterm_verdict
}
"""

# 3. Execution mit kleinem Modell
rlm = RecursiveLLM(llama_8b, env)
results = rlm.execute_strategy(strategy)

# 4. SPO-Extraktion aus Results
tripletts = spo_extractor.extract_all(results)

# 5. Axiom-Validierung
for triple in tripletts:
    score = axiom_judge.evaluate(triple)
    if score.total > 0.8:
        deep_graph.add_verified_triple(triple)

# 6. Final Answer (wieder großes Modell)
answer = claude_opus.query(f"""
Basierend auf {len(tripletts)} verifizierten Fakten:
{deep_graph.export_relevant_tripletts()}

Ist Solaranlage wirtschaftlich? Begründung mit Daten.
""")
```

---

## 8. Sicherheits-Überlegungen

### Sandboxing
RLM-Code muss sicher ausgeführt werden:

```python
ALLOWED_OPERATIONS = {
    "search", "filter", "slice", "map", "reduce",
    "recursive_call", "len", "sum", "avg"
}

FORBIDDEN = {
    "exec", "eval", "import", "open", "os", "sys",
    "__import__", "compile"
}

def validate_code(code: str) -> bool:
    """Prüfe ob Code sicher ist"""

    # AST-Analyse (kein eval von User-Code!)
    tree = ast.parse(code)

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            return False  # Keine Imports
        if isinstance(node, ast.Call):
            if node.func.id not in ALLOWED_OPERATIONS:
                return False  # Nur erlaubte Funktionen

    return True
```

---

## 9. Performance-Charakteristiken

### Benchmarks (MIT Paper)

| Metrik | Standard LLM | RLM |
|--------|-------------|-----|
| **Max Kontext** | 128k Tokens | 10M+ Tokens |
| **Kosten (100k Tokens)** | $10 | $2 |
| **Qualität bei 1M Tokens** | 40% Accuracy | 85% Accuracy |
| **Context Rot** | Ab 50k | Kein Rot |

### Unsere erwarteten Zahlen

```python
# Ohne RLM: Reddit-Analyse
- Verarbeitbar: 500 Posts (begrenzt durch Context)
- Kosten: $5 (viele teure API-Calls)
- Dauer: 10 Minuten
- Qualität: Mittel (Information Loss)

# Mit RLM: Reddit-Analyse
- Verarbeitbar: 50.000 Posts
- Kosten: $1 (viele billige lokale Calls)
- Dauer: 15 Minuten
- Qualität: Hoch (kein Information Loss)
```

---

## 10. Implementation Roadmap

### Phase 1: Basic RLM
```python
# Einfacher Proof-of-Concept
- Python-REPL Environment
- Simple Operationen (search, filter)
- Single recursion level
```

### Phase 2: Advanced RLM
```python
# Volle Features
- Multi-level recursion (depth 10+)
- Sub-model spawning (CEO-Worker)
- Caching von Zwischen-Ergebnissen
```

### Phase 3: MCTS-Integration
```python
# RLM als MCTS-Expansion-Strategy
- Nodes nutzen RLM für Daten-Exploration
- RLM-Scores fließen in MCTS-Rewards ein
```

---

## Referenzen
- **MIT Paper**: "Recursive Language Models" (arXiv:2512.24601, Dec 2025)
  - Alex L. Zhang, Tim Kraska, Omar Khattab
- **Gemini Strategic Planning** (Jan 2026)
- **Related Work**: ReAct, Toolformer, AutoGPT
