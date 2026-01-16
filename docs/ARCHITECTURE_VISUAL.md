# SRO - Architektur-Übersicht (Visual)

**Stand:** 2026-01-16 | **Status:** Sprint 1-3 COMPLETE

---

## 🏗️ Gesamt-Architektur

```
┌────────────────────────────────────────────────────────────────────────┐
│                           USER INTERFACE                                │
│                         (Sprint 5 - Pending)                            │
├────────────────────────────────────────────────────────────────────────┤
│  [ GUI ]              [ CLI ]              [ API ]                      │
│  React/Vite           Python CLI           FastAPI                      │
└─────────────────────────────┬──────────────────────────────────────────┘
                              │
┌─────────────────────────────┴──────────────────────────────────────────┐
│                      ORCHESTRATION LAYER                                │
├────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌────────────────────┐         ┌──────────────────────┐              │
│  │  ToT Manager       │◄───────►│  Model Orchestrator  │              │
│  │  (900 LOC)         │         │  (Profile Management)│              │
│  └────────┬───────────┘         └──────────┬───────────┘              │
│           │                                 │                           │
│           │                    ┌────────────┴────────────┐             │
│           │                    │  LLM Provider Layer     │             │
│           │                    ├─────────────────────────┤             │
│           │                    │  • LocalLlamaCpp        │             │
│           │                    │  • Ollama               │             │
│           │                    │  • API Providers        │             │
│           │                    └─────────────────────────┘             │
│           │                                                             │
└───────────┼─────────────────────────────────────────────────────────────┘
            │
┌───────────┴─────────────────────────────────────────────────────────────┐
│                         SPRINT 2: INTELLIGENCE LAYER                     │
│                              ✅ COMPLETE                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│   ┌──────────────────────────────────────────────────────────────┐     │
│   │  CoT Generator (400 LOC)                                     │     │
│   │  ┌────────────┐  ┌────────────┐  ┌────────────┐             │     │
│   │  │ Variant A  │  │ Variant B  │  │ Variant C  │             │     │
│   │  │ Analytical │  │ Empirical  │  │Theoretical │             │     │
│   │  │  T=0.7     │  │  T=0.8     │  │  T=0.9     │             │     │
│   │  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘             │     │
│   └────────┼───────────────┼───────────────┼────────────────────┘     │
│            │               │               │                            │
│   ┌────────┴───────────────┴───────────────┴────────────────────┐     │
│   │  Process Reward Model (470 LOC)                             │     │
│   │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │     │
│   │  │Axiom (40%)   │  │Logic (40%)   │  │Evidence(20%) │      │     │
│   │  │Compliance    │  │Consistency   │  │Strength      │      │     │
│   │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │     │
│   │         └──────────────────┴──────────────────┘              │     │
│   │                    Overall Score (0.0-1.0)                   │     │
│   └──────────────────────────────┬───────────────────────────────┘     │
│                                  │                                      │
│                    Select Best Variant (highest score)                  │
│                                  │                                      │
└──────────────────────────────────┼──────────────────────────────────────┘
                                   │
┌──────────────────────────────────┴──────────────────────────────────────┐
│                    SPRINT 3: VERIFICATION LAYER                          │
│                              ✅ COMPLETE                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│   ┌───────────────────────────────────────────────────────────────┐    │
│   │  Reddit Scraper (450 LOC)                                     │    │
│   │  ┌──────────┐              ┌──────────┐                       │    │
│   │  │Mock Mode │◄──default───►│Web Mode  │                       │    │
│   │  │(Testing) │              │(BeautifulS│                       │    │
│   │  └────┬─────┘              └────┬─────┘                       │    │
│   └───────┼──────────────────────────┼────────────────────────────┘    │
│           │                          │                                  │
│           └──────────┬───────────────┘                                  │
│                      │                                                  │
│   ┌──────────────────┴────────────────────────────────────────────┐   │
│   │  Experience Extractor (360 LOC)                               │   │
│   │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │   │
│   │  │Sentiment │  │Confidence│  │Evidence  │  │Quality   │     │   │
│   │  │Detection │  │Detection │  │Type      │  │Score     │     │   │
│   │  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘     │   │
│   └───────┼─────────────┼─────────────┼─────────────┼────────────┘   │
│           └─────────────┴─────────────┴─────────────┘                  │
│                              │                                          │
│   ┌──────────────────────────┴──────────────────────────────────┐     │
│   │  Friction Detector (340 LOC)                                │     │
│   │                                                              │     │
│   │  AI Hypothesis (SPO Triplet)                                │     │
│   │           │                                                  │     │
│   │           ▼                                                  │     │
│   │  ┌─────────────────────────────────────────────┐            │     │
│   │  │ Compare with Human Experiences              │            │     │
│   │  ├─────────────────────────────────────────────┤            │     │
│   │  │  Supporting (5)  │  Neutral (8)  │ Contra (7) │         │     │
│   │  └─────────┬────────┴───────┬───────┴────┬──────┘           │     │
│   │            │                │            │                   │     │
│   │            └────────────────┴────────────┘                   │     │
│   │                     │                                        │     │
│   │                     ▼                                        │     │
│   │            Friction Score: 0.693                             │     │
│   │            Verdict: FRICTION_DETECTED                        │     │
│   └──────────────────────────────────────────────────────────────┘     │
│                                                                         │
│   ┌─────────────────────────────────────────────────────────────┐     │
│   │  Consensus Scorer (220 LOC)                                 │     │
│   │                                                              │     │
│   │  Weighted Factors:                                          │     │
│   │  • Upvotes (community agreement)                            │     │
│   │  • Evidence Type (personal > hearsay)                       │     │
│   │  • Confidence (certain > speculative)                       │     │
│   │  • Expertise (technical terms)                              │     │
│   │  • Recency (recent > old)                                   │     │
│   │  • Quality Score                                            │     │
│   │                                                              │     │
│   │  Output: Consensus Score (-1.0 to +1.0)                     │     │
│   └─────────────────────────────────────────────────────────────┘     │
│                                                                         │
└─────────────────────────────────┬───────────────────────────────────────┘
                                  │
┌─────────────────────────────────┴───────────────────────────────────────┐
│                    CLUSTER 2: TIERED RAG LAYER                           │
│                              ✅ COMPLETE                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│   ┌─────────────────────────────────────────────────────────────┐      │
│   │  Multi-Source Verifier (500 LOC)                            │      │
│   │  ┌────────┐  ┌────────┐  ┌────────┐                         │      │
│   │  │Source 1│  │Source 2│  │Source 3│                         │      │
│   │  └───┬────┘  └───┬────┘  └───┬────┘                         │      │
│   │      └───────────┴───────────┘                               │      │
│   │              │                                                │      │
│   │              ▼                                                │      │
│   │      Cross-Verification                                      │      │
│   │      (3+ sources = upgrade confidence)                       │      │
│   └──────────────────────┬──────────────────────────────────────┘      │
│                          │                                              │
│   ┌──────────────────────┴──────────────────────────────────────┐      │
│   │  Tier Promoter (400 LOC)                                    │      │
│   │                                                              │      │
│   │  Bronze (low confidence) ──────┐                            │      │
│   │                                │                             │      │
│   │  Silver (verified 3+ sources) ─┼─► Automatic Promotion      │      │
│   │                                │   based on:                 │      │
│   │  Gold (high confidence)  ──────┘   • Verification count     │      │
│   │                                     • Confidence score       │      │
│   │                                     • Source quality         │      │
│   └──────────────────────┬──────────────────────────────────────┘      │
│                          │                                              │
│   ┌──────────────────────┴──────────────────────────────────────┐      │
│   │  Conflict Resolver (450 LOC)                                │      │
│   │                                                              │      │
│   │  Detect: SPO1 contradicts SPO2                              │      │
│   │  Strategies:                                                 │      │
│   │  • Keep both (uncertainty)                                   │      │
│   │  • Keep higher confidence                                    │      │
│   │  • Flag for manual review                                    │      │
│   └──────────────────────────────────────────────────────────────┘      │
│                                                                          │
│   ┌─────────────────────────────────────────────────────────────┐      │
│   │  Axiom Judge (350 LOC)                                      │      │
│   │                                                              │      │
│   │  Check SPO Triplets against User Axioms:                    │      │
│   │  • Does this violate a principle?                           │      │
│   │  • Flag violations                                           │      │
│   │  • Downgrade confidence if violation                         │      │
│   └─────────────────────────────────────────────────────────────┘      │
│                                                                          │
└──────────────────────────────────┬───────────────────────────────────────┘
                                   │
┌──────────────────────────────────┴──────────────────────────────────────┐
│                      SPRINT 1: FOUNDATION LAYER                          │
│                              ✅ COMPLETE                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│   ┌─────────────────────────────────────────────────────────────┐      │
│   │  MCTS Engine (800 LOC)                                      │      │
│   │                                                              │      │
│   │  UCB1 = exploit + explore + coverage + xot_prior            │      │
│   │                                                              │      │
│   │  ┌──────────┐     ┌──────────┐     ┌──────────┐            │      │
│   │  │Selection │────►│Expansion │────►│Simulation│            │      │
│   │  └────┬─────┘     └────┬─────┘     └────┬─────┘            │      │
│   │       │                │                 │                   │      │
│   │       └────────────────┴─────────────────┘                   │      │
│   │                        │                                      │      │
│   │                        ▼                                      │      │
│   │                  Backpropagation                              │      │
│   └───────────────────────────────────────────────────────────────┘      │
│                                                                          │
│   ┌─────────────────────────────────────────────────────────────┐      │
│   │  XoT Simulator (500 LOC)                                    │      │
│   │                                                              │      │
│   │  "Vor-Denker" für MCTS:                                     │      │
│   │  • Predict node value before full expansion                 │      │
│   │  • Fast simulation (< 1s)                                    │      │
│   │  • Used as UCB1 prior                                        │      │
│   └─────────────────────────────────────────────────────────────┘      │
│                                                                          │
│   ┌─────────────────────────────────────────────────────────────┐      │
│   │  Graph Manager (600 LOC)                                    │      │
│   │                                                              │      │
│   │  Knowledge Graph:                                            │      │
│   │  • Nodes (SPO Triplets)                                      │      │
│   │  • Edges (Relations)                                         │      │
│   │  • Traversal                                                 │      │
│   │  • Query                                                     │      │
│   └─────────────────────────────────────────────────────────────┘      │
│                                                                          │
│   ┌─────────────────────────────────────────────────────────────┐      │
│   │  SPO Extractor (450 LOC)                                    │      │
│   │                                                              │      │
│   │  Text Input → LLM → SPO Triplets                            │      │
│   │                                                              │      │
│   │  "Solar panels reduce emissions by 40%"                     │      │
│   │  ↓                                                           │      │
│   │  SPOTriplet(                                                 │      │
│   │    subject="solar_panels",                                   │      │
│   │    predicate="reduce_emissions_by",                          │      │
│   │    object="40_percent",                                      │      │
│   │    confidence=0.85                                           │      │
│   │  )                                                           │      │
│   └─────────────────────────────────────────────────────────────┘      │
│                                                                          │
│   ┌─────────────────────────────────────────────────────────────┐      │
│   │  SPO Database (400 LOC)                                     │      │
│   │                                                              │      │
│   │  SQLite Storage:                                             │      │
│   │  • CRUD Operations                                           │      │
│   │  • Tier Storage (Bronze/Silver/Gold)                         │      │
│   │  • Query by subject/predicate/object                         │      │
│   │  • Session Management                                        │      │
│   └─────────────────────────────────────────────────────────────┘      │
│                                                                          │
│   ┌─────────────────────────────────────────────────────────────┐      │
│   │  Token Budget Manager (350 LOC)                             │      │
│   │                                                              │      │
│   │  Track token usage per session:                             │      │
│   │  • Quality-level based budgets                              │      │
│   │  • Enforcement (stop if exceeded)                            │      │
│   │  • Cost estimation                                           │      │
│   └─────────────────────────────────────────────────────────────┘      │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Datenfluss: End-to-End Reasoning

```
┌────────────────────────────────────────────────────────────────────────┐
│ USER QUERY: "What are the benefits of renewable energy?"              │
└────────────────────────────┬───────────────────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────────────────┐
│ SPRINT 1: ToT Manager                                                  │
│ • Create root node                                                     │
│ • Decompose into sub-questions                                         │
└────────────────────────────┬───────────────────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────────────────┐
│ SPRINT 1: MCTS Engine                                                  │
│ • Select best node to expand (UCB1)                                    │
│ • XoT Simulator provides prior                                         │
└────────────────────────────┬───────────────────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────────────────┐
│ SPRINT 2: CoT Generator                                                │
│ • Generate Variant A (Analytical): "Deductive analysis..."             │
│ • Generate Variant B (Empirical): "Studies show..."                    │
│ • Generate Variant C (Theoretical): "First principles..."              │
└────────────────────────────┬───────────────────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────────────────┐
│ SPRINT 2: Process Reward Model                                         │
│ • Score each variant's reasoning steps                                 │
│ • Variant A: 0.72                                                      │
│ • Variant B: 0.85 ← BEST                                               │
│ • Variant C: 0.68                                                      │
│ • Select Variant B                                                     │
└────────────────────────────┬───────────────────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────────────────┐
│ SPRINT 1: SPO Extractor                                                │
│ • Extract facts from Variant B's conclusion                            │
│ • SPO1: (solar, reduces, emissions)                                    │
│ • SPO2: (solar, costs, decreasing)                                     │
│ • SPO3: (solar, creates, jobs)                                         │
└────────────────────────────┬───────────────────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────────────────┐
│ CLUSTER 2: Multi-Source Verifier                                       │
│ • Compare SPO1 with other sources                                      │
│ • Found in 3+ sources → Tier upgrade to Silver                         │
└────────────────────────────┬───────────────────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────────────────┐
│ SPRINT 3: Reddit Validation                                            │
│ • Scrape r/solar for "solar panel emissions"                           │
│ • Extract 20 human experiences                                         │
│ • Friction Detector: Compare AI vs Humans                              │
│ • Consensus: +0.6 (positive) → CONFIRMED!                              │
│ • Upgrade SPO1 confidence: 0.8 → 0.9                                   │
└────────────────────────────┬───────────────────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────────────────┐
│ SPRINT 1: SPO Database                                                 │
│ • Store verified SPO triplets                                          │
│ • SPO1: Silver tier, confidence 0.9, Reddit-validated                  │
└────────────────────────────┬───────────────────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────────────────┐
│ SPRINT 1: Graph Manager                                                │
│ • Add to knowledge graph                                               │
│ • Connect with related facts                                           │
└────────────────────────────┬───────────────────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────────────────┐
│ SPRINT 1: MCTS Backpropagation                                         │
│ • Update parent node values                                            │
│ • Continue search with updated knowledge                               │
└────────────────────────────┬───────────────────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────────────────┐
│ USER: Receives high-quality, verified answer                           │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Komponenten-Status Matrix

| Layer | Komponente | Status | LOC | LLM-frei | Getestet |
|-------|------------|--------|-----|----------|----------|
| **Foundation** | SPO Database | ✅ | 400 | ✅ | ✅ |
| **Foundation** | SPO Extractor | ✅ | 450 | ❌ | ⏳ |
| **Foundation** | MCTS Engine | ✅ | 800 | ✅ | ✅ |
| **Foundation** | ToT Manager | ✅ | 900 | ❌ | ⏳ |
| **Foundation** | Graph Manager | ✅ | 600 | ✅ | ✅ |
| **Foundation** | XoT Simulator | ✅ | 500 | ❌ | ⏳ |
| **Foundation** | Token Budget | ✅ | 350 | ✅ | ✅ |
| **Intelligence** | CoT Generator | ✅ | 400 | ❌ | ⏳ |
| **Intelligence** | Process Reward | ✅ | 470 | 🟡 | ✅ |
| **Verification** | Reddit Scraper | ✅ | 450 | ✅ | ✅ |
| **Verification** | Experience Ext | ✅ | 360 | 🟡 | ✅ |
| **Verification** | Friction Det | ✅ | 340 | ✅ | ✅ |
| **Verification** | Consensus Sc | ✅ | 220 | ✅ | ✅ |
| **Tiered RAG** | Multi-Source | ✅ | 500 | ❌ | ⏳ |
| **Tiered RAG** | Tier Promoter | ✅ | 400 | ✅ | ✅ |
| **Tiered RAG** | Conflict Res | ✅ | 450 | ✅ | ✅ |
| **Tiered RAG** | Axiom Manager | ✅ | 600 | ✅ | ✅ |
| **Tiered RAG** | Axiom Judge | ✅ | 350 | ❌ | ⏳ |

**Legende:**
- ✅ = Vollständig
- 🟡 = Teilweise (Regel-basiert JA, LLM-Modus NEIN)
- ❌ = Nein
- ⏳ = Wartet auf Hardware

---

## 📈 Test-Coverage Visual

```
┌────────────────────────────────────────────────────────────────────┐
│                        TEST COVERAGE                                │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  LLM-freie Komponenten:          ████████████████████  100% ✅     │
│  (Database, MCTS, Graph, etc.)                                     │
│                                                                     │
│  Regel-basierte Komponenten:     ████████████████████  100% ✅     │
│  (PRM Rule-based, Friction, etc.)                                  │
│                                                                     │
│  LLM-abhängige Komponenten:      ████████░░░░░░░░░░░   40% ⏳      │
│  (CoT, SPO Extract, XoT, etc.)                                     │
│                                                                     │
│  Integration-Tests (Mock):       ████████████████████  100% ✅     │
│  (Sprint 2 & 3 unit tests)                                         │
│                                                                     │
│  Integration-Tests (LLM):        ░░░░░░░░░░░░░░░░░░░░   0% ⏳      │
│  (Full pipeline tests)                                             │
│                                                                     │
│  E2E-Tests:                      ░░░░░░░░░░░░░░░░░░░░   0% ⏳      │
│  (Complete workflow)                                               │
│                                                                     │
├────────────────────────────────────────────────────────────────────┤
│  OVERALL TEST COVERAGE:          ████████████░░░░░░░░   60% 🟡     │
└────────────────────────────────────────────────────────────────────┘
```

---

## 🔥 Kritischer Pfad (ohne LLM-Hardware)

### Was wir JETZT entwickeln können:

```
1. MCTS Engine Optimizations
   ├─ Coverage-aware Selection ✅ Mathematik
   ├─ UCB1 Tuning ✅ Mathematik
   ├─ Tree Pruning ✅ Algorithmen
   └─ Adaptive Exploration ✅ Heuristiken

2. Graph Visualization
   ├─ NetworkX Integration ✅ Keine LLM
   ├─ HTML Export ✅ Keine LLM
   ├─ Interactive Viz ✅ Keine LLM
   └─ ToT Tree Display ✅ Keine LLM

3. CLI Tools
   ├─ Session Management ✅ Keine LLM
   ├─ SPO Query Tool ✅ Keine LLM
   ├─ Stats Dashboard ✅ Keine LLM
   └─ Export Tools ✅ Keine LLM

4. GUI Development
   ├─ React Frontend ✅ Keine LLM
   ├─ API Backend ✅ Keine LLM
   ├─ WebSocket ✅ Keine LLM
   └─ Visualization ✅ Keine LLM
```

---

## 🚀 Roadmap Visual

```
Timeline:
│
├─ Sprint 1: Foundation          ✅ COMPLETE (Week 1-2)
│  └─ 5.000 LOC, All tests passed
│
├─ Sprint 2: Intelligence        ✅ COMPLETE (Today!)
│  └─ 1.320 LOC, Unit tests passed
│
├─ Sprint 3: Verification        ✅ COMPLETE (Today!)
│  └─ 1.620 LOC, Mock tests passed
│
├─ [NOW] Hardware Limitation     ⚠️ BLOCKING
│  └─ LLM-Tests waiting
│
├─ [OPTION] MCTS Optimization    ⏳ NEXT (2-3 days)
│  └─ Pure math, no LLM needed
│
├─ [OPTION] Graph Visualization  ⏳ NEXT (2-3 days)
│  └─ No LLM needed
│
├─ Sprint 4: Scaling             ⏳ FUTURE (1-2 weeks)
│  └─ Requires LLM hardware
│
└─ Sprint 5: Polish              ⏳ FUTURE (1 week)
   └─ GUI, Viz, Export
```

---

**Fazit:** Starke, modulare Architektur mit klarer Layer-Trennung! 🏗️

---

*Architecture Visual - 2026-01-16*
