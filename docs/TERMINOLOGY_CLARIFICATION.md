# Terminologie-Klarstellung: Sprints vs. Cluster

**Date:** 2026-01-16
**Problem:** Verwirrung zwischen "Sprints" und "Cluster"
**Lösung:** Zurück zu Gemini's ORIGINAL Plan!

---

## 🔍 Was ist passiert?

### Gemini's ORIGINALE Terminologie (KORREKT!)

**In:** `docs/concepts/SRO_ARCHITECTURE_OVERVIEW.md`

```markdown
## 8. Implementation Roadmap

### Sprint 1: Foundation (Woche 1-2)
✓ Axiom Library Setup
✓ SPO Extractor
✓ Basic MCTS (ohne CoT)
✓ Flat Knowledge Graph

### Sprint 2: Intelligence Layer (Woche 3-4)
□ Generative CoT Integration
□ Process Reward Model (PRM)
□ XoT Simulator
□ Multi-variant Selection

### Sprint 3: Verification (Woche 5-6)
□ Tiered RAG (Bronze/Silver/Gold)
□ Reddit Scraper
□ Friction Detector
□ Consensus Scorer

### Sprint 4: Scaling (Woche 7-8)
□ Recursive LLM
□ CEO-Worker Architecture
□ Multi-GPU Support
□ Performance Optimization

### Sprint 5: Polish (Woche 9-10)
□ GUI Integration
□ Graph Visualization
□ Working State Timeline
□ Export/Import
```

---

## ❌ Mein Fehler (Claude's Erfindung!)

### Was ich gemacht habe:

Ich habe **"Cluster"** als Gruppierungs-Begriff eingeführt:

**Datei:** `docs/CLUSTER_1_COMPLETE.md`
```markdown
# Cluster 1: Foundations - COMPLETE ✅
**Sprint:** 2 Complete (SPO + XoT + Token Budget)
```

**Datei:** `docs/CLUSTER_2_COMPLETE.md`
```markdown
# Cluster 2: Intelligence Layer - COMPLETE ✅
```

### Warum habe ich das gemacht?

Ich habe mehrere Sprints ZUSAMMENGEFASST:

- **Cluster 1** = Sprint 1 + Teile von Sprint 2 (SPO + XoT + Token Budget)
- **Cluster 2** = Teile von Sprint 3 (Tiered RAG, Multi-Source Verification)
- **Cluster 3** = MEINE ERFINDUNG (Fact Quality Enhancement)

**ABER:** Das war NICHT der Original-Plan!

---

## ✅ Die WAHRHEIT

### Was Gemini WIRKLICH geplant hat:

| Sprint | Inhalt | Status (Real) |
|--------|--------|---------------|
| **Sprint 1** | Axiom Library, SPO Extractor, Basic MCTS, Flat Graph | ✅ COMPLETE |
| **Sprint 2** | **Generative CoT**, Process Reward Model, XoT, Multi-variant | ⏳ PARTIAL (nur XoT!) |
| **Sprint 3** | Tiered RAG, **Reddit Scraper**, Friction Detector, Consensus | ⏳ PARTIAL (nur RAG!) |
| **Sprint 4** | Recursive LLM, CEO-Worker, Multi-GPU | ❌ NOT STARTED |
| **Sprint 5** | GUI, Graph Viz, Timeline, Export | ❌ NOT STARTED |

### Was wir TATSÄCHLICH implementiert haben:

**Sprint 1:** ✅ COMPLETE
- ✅ Axiom Library
- ✅ SPO Extractor
- ✅ Basic MCTS
- ✅ Flat Knowledge Graph

**Sprint 2:** ⏳ NUR 25% FERTIG!
- ✅ XoT Simulator
- ✅ Token Budget Manager (Bonus!)
- ❌ **Generative CoT** ← FEHLT! (DAS IST DER KERN!)
- ❌ **Process Reward Model** ← FEHLT!
- ❌ Multi-variant Selection ← FEHLT!

**Sprint 3:** ⏳ NUR 33% FERTIG!
- ✅ Tiered RAG (Bronze/Silver/Gold)
- ✅ Multi-Source Verifier (unser Bonus!)
- ✅ Tier Promoter (unser Bonus!)
- ❌ **Reddit Scraper** ← FEHLT! (DAS IST DER KERN!)
- ❌ **Friction Detector** ← FEHLT!
- ❌ Consensus Scorer ← FEHLT!

---

## 🎯 Was FEHLT vom Original-Plan?

### 1. Generative CoT (Sprint 2) ← KRITISCH!

**Gemini's Vision:**
> Generate **3 alternative reasoning chains** per MCTS node
> Use Process Reward Model to score each step

**Was wir haben:**
- ToT expansion → 1 Answer pro Node
- Keine Varianten-Generation
- Kein Process Reward Model

**Was fehlt:**
```python
class CoTGenerator:
    def generate_variants(self, node, count=3) -> List[CoT]:
        """
        Generate 3 reasoning chain variants:
        - Variant A: Analytical approach
        - Variant B: Empirical approach
        - Variant C: Theoretical approach
        """
```

---

### 2. Reddit Validation (Sprint 3) ← KRITISCH!

**Gemini's Vision:**
> Validate hypotheses against real human experiences
> Scrape Reddit/Forums for friction detection
> Calculate consensus scores

**Was wir haben:**
- NICHTS!

**Was fehlt:**
```python
class RedditValidator:
    def scrape_experiences(self, query: str) -> List[Experience]:
        """Scrape Reddit for real human experiences."""

    def detect_friction(self, hypothesis: SPOTriplet) -> FrictionReport:
        """Check if hypothesis matches reality."""

    def calculate_consensus(self, experiences: List) -> float:
        """Score based on human consensus."""
```

---

## 🔄 Zurück zum ORIGINAL Plan

### Option A: Gemini's Plan STRIKT folgen

**Nächster Schritt:** Sprint 2 KORREKT vervollständigen

1. **Generative CoT implementieren** (3-4 Tage)
   - Generate 3 CoT variants per node
   - Process Reward Model
   - Multi-variant selection

2. **Sprint 3 vervollständigen** (4-5 Tage)
   - Reddit Scraper
   - Friction Detector
   - Consensus Scorer

3. **DANN:** Sprint 4 (Recursive LLM)

---

### Option B: Meine Enhancements (FactQuality) AUCH verwenden

**Hybrid-Ansatz:**

1. **ERST:** Gemini's Sprint 2 implementieren (CoT!)
2. **DANN:** Mein FactQuality-Enhancement integrieren
3. **DANN:** Gemini's Sprint 3 implementieren (Reddit!)

**Vorteil:** Beides nutzen!
**Nachteil:** Dauert länger

---

## 📝 Korrigierte Benennung

### ❌ ALT (meine Erfindung):
```
Cluster 1: Foundations
Cluster 2: Intelligence Layer
Cluster 3: MCTS + Tiered RAG (geplant)
```

### ✅ NEU (Gemini's Original):
```
Sprint 1: Foundation ✅ COMPLETE
Sprint 2: Intelligence Layer ⏳ PARTIAL (25% - fehlt CoT!)
Sprint 3: Verification ⏳ PARTIAL (33% - fehlt Reddit!)
Sprint 4: Scaling ❌ NOT STARTED
Sprint 5: Polish ❌ NOT STARTED
```

---

## 🎯 Empfehlung

**Folge Gemini's Original Plan!**

**Nächster Schritt:**
1. Sprint 2 vervollständigen → Generative CoT implementieren
2. Sprint 3 vervollständigen → Reddit Validation implementieren
3. Sprint 4 starten → Recursive LLM

**Meine Enhancements (FactQuality):**
- Dokumentiert in `docs/enhancements/FACT_QUALITY_GUIDED_MCTS.md`
- Kann SPÄTER integriert werden (nach Sprint 3)

---

## ✅ Zusammenfassung

**Problem:**
- Ich habe "Cluster" erfunden und damit Verwirrung gestiftet
- Gemini's Original Plan nutzt "Sprints"
- Wir haben Teile implementiert, aber NICHT den Kern!

**Lösung:**
- Zurück zu Gemini's Sprints
- Sprint 2 vervollständigen (Generative CoT!)
- Sprint 3 vervollständigen (Reddit Validation!)

**Nächste Aktion:**
- User entscheidet: Sprint 2 implementieren? (empfohlen!)

---

*Dokumentiert: 2026-01-16*
*Zweck: Terminologie-Klarstellung & Realitätscheck*
