# Deep Research Orchestrator - User Guide

**Version:** 1.0 (Sprint 4 Complete)
**Datum:** 2025-12-23
**Status:** Alle Sprints abgeschlossen

---

## Übersicht

Der Deep Research Orchestrator ist ein modulares System zur Orchestrierung von LLM-basierten Research-Workflows. Das System kombiniert lokale, uncensored LLMs (Llama 3.1, Qwen 2.5, Mixtral) mit manueller Multi-AI-Integration (Claude, GPT-4, Gemini) für tiefgehende Recherchen.

---

## Dokumentations-Struktur

Diese Dokumentation ist in drei Teile gegliedert:

### 1. **Konzepte & Architektur** (`01_konzepte.md`)
- **Was:** Grundlegende Konzepte und Designentscheidungen
- **Für wen:** Entwickler, die das System verstehen wollen
- **Inhalt:**
  - Master-Worker Orchestration Pattern
  - Hierarchische Building Blocks (Technique ’ Workflow ’ Phase ’ Framework)
  - Iterative Refinement Loops
  - Multi-AI Integration Workflow
  - Hardware-Optimierung (VRAM + RAM Split)

### 2. **Komponenten-Referenz** (`02_reference.md`)
- **Was:** Detaillierte technische Beschreibung aller Komponenten
- **Für wen:** Entwickler, die mit dem Code arbeiten
- **Inhalt:**
  - Klassen-Referenz (Agent, Orchestrator, FrameworkLoader, etc.)
  - Konfigurationsformate (JSON-Schemas)
  - API-Dokumentation
  - File-Struktur

### 3. **Use Cases & Workflows** (`03_use_cases.md`)
- **Was:** Praktische Anwendungsbeispiele
- **Für wen:** Benutzer und Entwickler
- **Inhalt:**
  - End-to-End Workflows
  - Beispielkonfigurationen
  - Typische Anwendungsfälle
  - Troubleshooting

---

## Quick Start

```python
from src.core.orchestrator import Orchestrator

# Orchestrator initialisieren
orchestrator = Orchestrator()

# Framework ausführen
result = orchestrator.execute_framework(
    framework_id="framework_product_research",
    inputs={"topic": "AI Tutoring Market"}
)

print(result)
```

---

## System-Anforderungen

### Minimale Konfiguration (aktuelles Test-System)
- GPU: NVIDIA GTX 980 (4GB VRAM)
- RAM: 8GB
- Modelle: TinyLlama 1.1B, Mixtral 8x7B Q2_K

### Empfohlene Konfiguration (Produktiv-System)
- GPU: NVIDIA RTX 3060 Ti (8GB VRAM) oder besser
- RAM: 16GB DDR5
- Modelle: Llama 3.1 8B, Qwen 2.5 32B

---

## Sprints-Übersicht

###  Sprint 1: Foundation (Abgeschlossen)
- Projektstruktur
- llama.cpp Integration
- Agent System
- Basic Tools (web_scraper, pdf_extractor)

###  Sprint 2: Iterative Workflows (Abgeschlossen)
- Orchestrator mit Master-Worker Pattern
- WorkflowEngine (sequential + iterative)
- Gap Detection & Input Refinement
- Confidence Scoring

###  Sprint 3: Multi-AI Integration (Abgeschlossen)
- Prompt Generator für externe AIs
- Response Analyzer (Contradiction, Blind Spots, Synthesis)
- Multi-AI Workflow

###  Sprint 4: Logic Builder Foundation (Abgeschlossen)
- Hierarchische Building Blocks
- FrameworkLoader mit Caching
- Schema-Validierung
- Composable Workflows

---

## Nächste Schritte

1. **Lesen:** `01_konzepte.md` für das Gesamtverständnis
2. **Nachschlagen:** `02_reference.md` für technische Details
3. **Anwenden:** `03_use_cases.md` für praktische Beispiele
4. **Testen:** Transfer auf starkes System vorbereiten

---

## Support & Debugging

- **GUI/LiveServer:** Noch in Entwicklung (nächster Schritt)
- **Issues:** Siehe STATUS.md für bekannte Probleme
- **Logs:** `logs/` Verzeichnis für detaillierte Ausführungsprotokolle
