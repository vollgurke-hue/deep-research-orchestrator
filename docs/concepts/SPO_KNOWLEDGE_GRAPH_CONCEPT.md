# SPO-Tripletts & Tiered RAG Konzept

**Datum:** 2026-01-22
**Quelle:** Gemini Strategic Planning
**Status:** Konzept-Definition

---

## 🎯 Kernidee

Transformation von unstrukturiertem KI-Output in **atomare, maschinenlesbare Fakten** durch SPO-Tripletts (Subject-Predicate-Object) und gestuftes Wissensmanagement (Tiered RAG).

---

## 1. Das SPO-Muster (Knowledge Graph Triplets)

### Konzept
**Subject-Predicate-Object (SPO)** ist die fundamentale Struktur von Knowledge Graphs.

### Problem mit Fließtext
LLMs neigen in natürlicher Sprache zu "Vibes" - vage, schwammige Aussagen ohne klare Struktur.

**Beispiel problematischer Output:**
```
"Solaranlagen sind generell eine gute Investition, wenn man bedenkt,
dass die Strompreise wahrscheinlich steigen werden und man langfristig
spart, wobei es natürlich Ausnahmen gibt..."
```

### Lösung: SPO-Extraktion
Zwinge die KI, Informationen als **Triplett** zu extrahieren:

```turtle
# RDF/Turtle Notation
[Solaranlage] --[ROI-Periode]--> [15-20 Jahre]
[Solaranlage] --[Abhängig von]--> [Strompreisentwicklung]
[Strompreis Deutschland] --[Trend]--> [Steigend]
[Strompreis 2024] --[Wert]--> [0.42 EUR/kWh]
```

### Vorteile
1. **Keine Unschärfe**: Jedes Triplett ist entweder wahr oder falsch
2. **Maschinenlesbar**: MCTS kann mathematisch prüfen ob Tripletts logisch kompatibel sind
3. **Verknüpfbar**: Tripletts können zu komplexen Reasoning-Ketten kombiniert werden
4. **Nachvollziehbar**: Jede Schlussfolgerung ist auf Triplett-Ebene zurückverfolgbar

---

## 2. Tiered RAG & Staging Logic

### Das Problem mit Standard-RAG
Normales RAG (Retrieval Augmented Generation) mischt:
- Verifizierte Fakten
- Ungeprüfte Web-Scrapes
- Spekulative KI-Outputs

in einen Topf → **Keine Vertrauenshierarchie**

### Lösung: Medallion Architecture für Wissen

Inspiriert von Data Engineering (Bronze/Silver/Gold), aber für Knowledge:

```
┌─────────────────────────────────────┐
│   SOVEREIGN TRUTH (Deep Graph)      │ ← Gold
│   ✓ Axiom-verifiziert               │
│   ✓ Multi-Source bestätigt          │
│   ✓ Mathematisch geprüft            │
└─────────────────────────────────────┘
              ↑
              │ Promotion nach Validierung
              │
┌─────────────────────────────────────┐
│   STRUCTURED KNOWLEDGE (Draft)      │ ← Silver
│   • SPO-Tripletts extrahiert        │
│   • Noch nicht verifiziert          │
│   • Wartet auf Axiom-Check          │
└─────────────────────────────────────┘
              ↑
              │ Strukturierung
              │
┌─────────────────────────────────────┐
│   RAW DATA (Scraping Layer)         │ ← Bronze
│   • Reddit-Posts                    │
│   • Web-Scrapes                     │
│   • API-Responses                   │
│   • Dokumente                       │
└─────────────────────────────────────┘
```

---

## 3. Der Promotion-Prozess

### Schritt-für-Schritt

```python
# 1. RAW DATA → STRUCTURED
raw_reddit_post = scraper.fetch("r/solar", query="ROI Erfahrung")

spo_extractor = SPOExtractor(llm=local_model)
triples = spo_extractor.extract(raw_reddit_post)

# Output:
# [
#   ("Solaranlage_User123", "ROI_erreicht_nach", "12_Jahre"),
#   ("Solaranlage_User123", "Standort", "Bayern"),
#   ("Solaranlage_User123", "Einspeisevergütung", "8.2_Cent/kWh")
# ]

# 2. STRUCTURED → VERIFICATION
for triple in triples:
    # Axiom-Check
    axiom_score = axiom_judge.evaluate(triple)

    # Cross-Reference mit existierendem Graph
    consistency_score = graph.check_consistency(triple)

    # Multi-Source Validation
    confirmation_count = graph.count_supporting_sources(triple)

# 3. VERIFICATION → SOVEREIGN TRUTH
if (axiom_score > 0.8 and
    consistency_score > 0.9 and
    confirmation_count >= 2):

    deep_graph.add_verified_triple(triple, metadata={
        "verified_at": timestamp,
        "sources": [source1, source2],
        "confidence": final_score
    })
```

---

## 4. Verified Knowledge Graph (VKG)

### Eigenschaften des "Deep Graph"

**Immutability (Unveränderlichkeit)**
- Einmal aufgenommene Tripletts werden nicht überschrieben
- Widersprüche führen zu neuen "Conflict-Nodes"
- Versionshistorie für jedes Triplett

**Provenance (Herkunft)**
```python
@dataclass
class VerifiedTriple:
    subject: str
    predicate: str
    object: str

    # Provenance
    sources: List[str]           # URLs, Dokumente, APIs
    verification_method: str     # axiom_check, multi_source, calculation
    confidence_score: float      # 0.0 - 1.0
    verified_at: datetime
    verified_by: str            # model_name oder "human"

    # Context
    related_triples: List[str]  # IDs von verbundenen Tripletts
    invalidates: List[str]      # IDs von widersprüchlichen alten Tripletts
```

**Query-Effizienz**
```python
# Normale Suche: "Was ist der ROI einer Solaranlage?"
results = deep_graph.query(
    pattern=("Solaranlage", "ROI", "?value"),
    confidence_threshold=0.85
)

# Multi-Hop Reasoning: "Welche Investitionen haben ROI < 10 Jahre UND passen zu Axiom 'Nachhaltigkeit'?"
results = deep_graph.reasoning_query(
    constraints=[
        ("?investment", "ROI", "?roi"),
        ("?roi", "less_than", "10_Jahre"),
        ("?investment", "axiom_compliance", "Nachhaltigkeit")
    ]
)
```

---

## 5. SPO-Extraktion: Best Practices

### Prompt Engineering für SPO

```python
SPO_EXTRACTION_PROMPT = """
Extrahiere aus dem folgenden Text ALLE Fakten als RDF-Tripletts.

Format: [Subject] --[Predicate]--> [Object]

Regeln:
1. Subjects und Objects müssen KONKRET sein (keine Pronomen)
2. Predicates müssen VERBEN oder RELATIONEN sein
3. Objects müssen MESSBAR oder VERIFIZIERBAR sein
4. Bei Zahlen: Immer Einheit angeben
5. Bei Vergleichen: Explizite Referenz

FALSCH:
[Es] --[ist]--> [teuer]

RICHTIG:
[Wärmepumpe_Modell_X] --[Anschaffungskosten]--> [25000_EUR]
[Wärmepumpe_Modell_X] --[teurer_als]--> [Gasheizung_Standard]
[Gasheizung_Standard] --[Anschaffungskosten]--> [8000_EUR]

Text:
{input_text}

Tripletts (JSON):
"""
```

### Qualitätskontrolle

**Automatische Validierung:**
```python
def validate_triple(triple: Tuple[str, str, str]) -> bool:
    subject, predicate, obj = triple

    # 1. Keine leeren Werte
    if not all([subject, predicate, obj]):
        return False

    # 2. Subject darf kein Pronomen sein
    pronouns = ["es", "sie", "er", "das", "dies", "jenes"]
    if subject.lower() in pronouns:
        return False

    # 3. Object muss verifizierbar sein
    if obj.lower() in ["gut", "schlecht", "viel", "wenig"]:
        return False  # Zu vage

    # 4. Zahlen brauchen Einheiten
    if obj.replace(".", "").isdigit() and not any(unit in obj for unit in ["EUR", "kWh", "kg", "%"]):
        return False

    return True
```

---

## 6. Integration mit MCTS

### Triplett-basierte Exploration

```python
class MCTSNode:
    def __init__(self, research_question: str):
        self.question = research_question
        self.triples: List[VerifiedTriple] = []
        self.draft_triples: List[Tuple] = []

    def expand(self):
        """Generate child nodes based on missing triples"""

        # Finde Lücken im Wissen
        missing_predicates = self.identify_missing_relations()

        for predicate in missing_predicates:
            child_question = f"Was ist {predicate} von {self.subject}?"
            child = MCTSNode(child_question)
            self.children.append(child)

    def simulate(self):
        """Simulate research path quality"""

        # Simuliere: Wie viele Tripletts könnten hier gefunden werden?
        potential_triples = llm.estimate_triplet_count(self.question)

        # Simuliere: Wie wahrscheinlich ist Axiom-Konformität?
        axiom_compatibility = axiom_judge.estimate_compliance(self.question)

        return potential_triples * axiom_compatibility
```

---

## 7. Vorteile gegenüber Vektor-RAG

### Standard RAG (Embedding-basiert)
```
Frage: "Ist Solaranlage wirtschaftlich?"
→ Findet semantisch ähnliche Textblöcke
→ KI interpretiert diese Blöcke
→ Antwort: "Ja, meistens schon"
```

**Problem:** Keine logische Kette, keine Verifikation

### SPO-basiertes RAG
```
Frage: "Ist Solaranlage wirtschaftlich?"
→ Findet relevante Tripletts:
   [Solaranlage] --[Stromproduktion]--> [4500_kWh/Jahr]
   [Strompreis] --[Wert]--> [0.42_EUR/kWh]
   [Solaranlage] --[Kosten]--> [15000_EUR]

→ Berechnung:
   Jahresersparnis = 4500 * 0.42 = 1890 EUR
   ROI = 15000 / 1890 = 7.9 Jahre

→ Antwort: "Ja, ROI nach 7.9 Jahren (berechnet aus verifizierten Daten)"
```

**Vorteil:** Mathematisch nachvollziehbar, jeder Schritt verifizierbar

---

## 8. Next Steps: GraphRAG Integration

### Microsoft GraphRAG (2024/25)
Kombination aus:
- Semantischer Suche (Vektoren)
- Struktureller Suche (Graph-Relationen)

### Unser Vorteil
Wir gehen einen Schritt weiter:
- GraphRAG für die **Suche**
- SPO-Tripletts für die **Verifikation**
- MCTS für die **strategische Exploration**

---

## Referenzen
- RDF (Resource Description Framework) - W3C Standard
- GraphRAG - Microsoft Research 2024
- Knowledge Graph Embeddings - Survey 2023
- Gemini Strategic Planning Session (Jan 2026)
