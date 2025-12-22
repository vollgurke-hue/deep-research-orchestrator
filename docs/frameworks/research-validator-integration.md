# Research Validator - Integration in Product Management Kit

**Version:** 1.0
**Last Updated:** 2025-12-09
**Purpose:** Lokales AI Response Validation Tool für kritische Research-Entscheidungen

---

## Executive Summary

**Was:** Lokales Validierungs-Tool das mehrere AI-Responses vergleicht und kritisch analysiert.

**Warum:** Verhindert Bias, Widersprüche und blinde Flecken in Business Research.

**Wie:** Abliterated Local Model (Ollama + Dolphin-Mistral) analysiert gesammelte AI-Responses offline.

**Wann:** Primär in **Base Research Review Phase** + ad-hoc bei kritischen Questions in Iterations.

---

## Core Concept

### Problem

Wenn du AI (Claude, GPT-4, Gemini) für Research nutzt:
- ✅ Schnell, günstig, hilft bei Ideenfindung
- ⚠️ **ABER:** Alle haben ähnliche Biases (gemeinsame Training-Daten, RLHF)
- ⚠️ **ABER:** Alle sind auf "helpful" konditioniert (niceness bias)
- ⚠️ **ABER:** Widersprüche zwischen Modellen bleiben unentdeckt
- ⚠️ **ABER:** Blinde Flecken (was ALLE ignorieren) sind unsichtbar

### Lösung

**Research Validator:**
1. Du fragst **mehrere AIs** die gleiche Research-Frage (manuell)
2. Speicherst jede Response als `.md` File
3. **Lokales abliterated Model** analysiert alle Responses
4. Validator findet:
   - **Contradictions** (wo widersprechen sich Modelle?)
   - **Consensus Bias** (was sagen ALLE? = verdächtig)
   - **Blind Spots** (was erwähnt NIEMAND?)
   - **Premortem** (forciert Failure Scenarios)
5. Du nutzt Validation Report für bessere Decisions

---

## Integration in dein Kit

### Wo passt das hin?

**Primäre Integration: Base Research Review Phase**

```
Phase 0: Base Research (6 Kategorien)
  ↓
Phase 2: Base Research Review ← VALIDATOR HIER! ⭐
  → Cross-Category Consistency Check
  → Big Picture Questions
  → Validation kritischer Annahmen ← VALIDATOR
  ↓
Phase 3: Question Extraction
  ↓
Phase 4: GIST Iterations ← VALIDATOR auch hier (bei Bedarf)
  ↓
Phase 5: Output
```

**Warum Review Phase?**
- ✅ Du hast alle 6 Kategorien researched = vollständiger Kontext
- ✅ Vor Planning = Verhindert falsche Decisions basierend auf Bias
- ✅ Big Picture Check = Validator entdeckt Inkonsistenzen
- ✅ Timeboxed = passt zu Review-Phase Zeitrahmen (1-2 Tage)

**Sekundär: Ad-hoc in Iterations**
- Wenn eine Question besonders kritisch ist (z.B. "Local vs Hybrid?")
- Nutze Validator für tiefere Analyse
- Dokumentiere in Iteration File unter "Validation"

---

## Workflow: Validator in Review Phase

### Vorbereitung (einmalig)

```bash
# 1. Ollama installieren (einmalig)
curl -fsSL https://ollama.com/install.sh | sh

# 2. Abliterated Model holen (einmalig)
ollama pull dolphin-mistral

# 3. Python Environment (einmalig)
python -m venv product-management/validator-env
source product-management/validator-env/bin/activate
pip install requests

# 4. Validator Code (Claude Code erstellt später)
# → product-management/tools/validator/
```

### Usage während Review Phase

**Schritt 1: Review Progress (wie gehabt)**
```markdown
2-working-state/planning_state.json:
{
  "current": {
    "phase": "0-base-research-review",
    "review_progress": {
      "1-technical-feasibility": "in_progress",
      ...
    }
  }
}
```

**Schritt 2: Critical Assumptions identifizieren**

Während du jede Kategorie reviewst, markiere **kritische Annahmen**:

```markdown
# In 2-working-state/0-base-research/1-technical-feasibility/tech-stack.md

## CRITICAL ASSUMPTION (for Validation):
"React (32/40), Vue (28/40), Svelte (25/40)"
- Source: AI analysis (Claude + GPT-4)
- Confidence: MEDIUM
- Impact: HIGH (affects dev velocity, hiring, bundle size)
- **→ VALIDATE THIS**
```

**Schritt 3: AI Responses sammeln (manuell)**

Für jede kritische Assumption:

1. Frage **mindestens 3 verschiedene AIs:**
   - Claude (claude.ai)
   - GPT-4 (ChatGPT)
   - Gemini (AI Studio)
   - Optional: Lokales Model (Ollama)

2. **Gleiche Frage, verschiedene AIs:**
   ```
   "Bewerte React, Vue, Svelte für ein Desktop-App Projekt:
   - Team: 1-2 Entwickler
   - Constraints: Bundle size wichtig
   - Requirements: Desktop (Tauri)

   Bewerte jedes Framework 1-10 in:
   - Dev Velocity, Community Support, Bundle Size, Tauri Integration"
   ```

3. **Speichere Responses:**
   ```
   2-working-state/research-data/validations/tech-stack-framework/
   ├── question.md          (Die Frage)
   ├── claude-response.md   (Claude's Antwort)
   ├── gpt4-response.md     (GPT-4's Antwort)
   ├── gemini-response.md   (Gemini's Antwort)
   └── llama-response.md    (Optional: Llama)
   ```

**Schritt 4: Validator laufen lassen**

```bash
cd product-management/tools/validator

python validator.py \
  ../../2-working-state/research-data/validations/tech-stack-framework/question.md \
  ../../2-working-state/research-data/validations/tech-stack-framework/ \
  ../../2-working-state/research-data/validations/tech-stack-framework/

# Output: validation-report-TIMESTAMP.md
```

**Schritt 5: Validation Report analysieren**

```markdown
# Validation Report - Tech Stack Framework

**Date:** 2025-12-09
**Question:** Framework Choice (React vs Vue vs Svelte)
**Models Analyzed:** claude, gpt4, gemini, llama
**Validator:** dolphin-mistral (local)

---

## ⚔️ Contradictions

**CONTRADICTION 1: Bundle Size**
- **claude.md** sagt: "Svelte 15KB, React 45KB"
- **gpt4.md** sagt: "Svelte 7KB, React 140KB"
- **Implikation:** Faktor 2-3 Unterschied - welche Messung? Production oder Dev?

**CONTRADICTION 2: Tauri Integration**
- **claude.md** sagt: "All equal for Tauri"
- **gemini.md** sagt: "Vue better Tauri integration (official examples)"
- **Implikation:** Muss nachprüfen - gibt es offizielle Tauri+Vue Examples?

---

## 🎯 Consensus Bias

**CONSENSUS 1:** Alle Modelle sagen "React has largest community"
- **Warum verdächtig:** Standard-Narrative, aber ist es für Tauri relevant?
- **Alternative:** Tauri community könnte Vue/Svelte bevorzugen
- **Action:** Check Tauri showcase apps - welche Frameworks nutzen sie?

---

## 👁️ Blind Spots

Folgende Aspekte erwähnt KEIN Model:

1. **HMR Performance** - Hot Module Reload bei Desktop Apps
2. **Memory Footprint** - RAM usage on user devices (8GB constraint)
3. **Update Size** - Incremental update size (für Auto-updater)
4. **Tauri Plugin Ecosystem** - Framework-specific plugins

---

## ⚰️ Premortem

Es ist 2026. Das Projekt ist gescheitert. Post-Mortem:

**Haupt-Todesursache:** Bundle size zu groß → App zu langsam → User churn.

**Ignorierte Warnsignale:**
- React bundle trotz Optimierung 80KB (vs. 15KB bei Svelte)
- Langsame Startup-Zeit auf älteren Devices
- Update-Downloads 50MB statt 5MB

**Fundamentale Fehlannahme:** "React community = besserer Support" - aber Tauri community nutzt primär Vue/Svelte.

---

## 📊 Summary

**Verdict:** INVESTIGATE FURTHER

**Critical Actions:**
- [ ] Kläre Bundle Size Widerspruch (messen, nicht glauben)
- [ ] Check Tauri showcase apps (welche Frameworks?)
- [ ] Test HMR performance (alle 3 Frameworks)
- [ ] Memory profiling (8GB constraint)

**Confidence:** LOW → Zu viele Widersprüche für Decision
```

**Schritt 6: Actions umsetzen**

Basierend auf Validation Report:
1. Fehlende Infos researchen (Blind Spots)
2. Widersprüche klären (selbst testen/messen)
3. Consensus-Annahmen hinterfragen

**Schritt 7: Base Research updaten**

```markdown
# In 2-working-state/0-base-research/1-technical-feasibility/tech-stack.md

## UPDATE nach Validation (2025-12-09)

**Validation fand:**
- ⚠️ Widerspruch: Bundle Size Messungen variieren 2-3x
- ⚠️ Blind Spot: HMR Performance, Memory Footprint
- ✅ Consensus: React community größer (validiert durch GitHub stars)

**Actions taken:**
- ✅ Eigene Bundle Size Messung: React 42KB, Vue 30KB, Svelte 12KB (production build)
- ✅ Tauri Showcase check: 60% Vue, 30% React, 10% Svelte
- ✅ Memory profiling: Svelte 50MB, Vue 60MB, React 80MB (initial load)

**Updated Scores:**
- React: 28/40 (down from 32, bundle size issue)
- Vue: 32/40 (up from 28, Tauri ecosystem + balance)
- Svelte: 30/40 (up from 25, bundle + memory wins)

**Confidence:** MEDIUM → HIGH (nach Validation + eigenen Tests)
```

**Schritt 8: Dokumentiere Validation**

```markdown
# In 2-working-state/planning_state.json

{
  "current": {
    "phase": "0-base-research-review",
    "validations_run": [
      {
        "topic": "tech-stack-framework",
        "date": "2025-12-09",
        "status": "complete",
        "outcome": "Updated scores, increased confidence",
        "report": "research-data/validations/tech-stack-framework/validation-report-20251209.md"
      }
    ]
  }
}
```

---

## Validation Methods (im Detail)

### 1. Contradiction Detection

**Was:** Findet faktische Widersprüche zwischen AI-Responses.

**Validator Prompt:**
```markdown
Analysiere diese AI Responses auf WIDERSPRÜCHE:

{alle_responses}

Liste konkrete Widersprüche:
1. Welche faktischen Claims widersprechen sich?
2. Wo sind Einschätzungen diametral unterschiedlich?

Format:
WIDERSPRUCH 1:
- Model X sagt: [Zitat]
- Model Y sagt: [Zitat]
- Implikation: [Was bedeutet das für Entscheidung?]
```

**Output-Qualität:** Hoch - abliterated Model ist nicht "helpful", findet echte Konflikte.

---

### 2. Consensus Bias Detection

**Was:** Findet was ALLE Modelle sagen = verdächtig (gemeinsame Training-Bias).

**Validator Prompt:**
```markdown
Finde CONSENSUS BIAS:

{alle_responses}

Was sagen ALLE Modelle? Das ist verdächtig weil:
- Gemeinsame Training-Daten
- Ähnliche RLHF
- Kultureller Bias

Für jeden Consensus-Punkt:
- Was sagen alle?
- Warum könnte das falsch sein?
- Welche Alternative wird ignoriert?
```

**Beispiel:**
- Alle: "React hat die größte Community"
- Validator: "Warum ist das für Tauri relevant? Tauri-spezifische Community könnte anders aussehen."

---

### 3. Blind Spot Detection

**Was:** Findet was NIEMAND erwähnt = fehlende Perspektiven.

**Validator Prompt:**
```markdown
Gegeben die Frage:
{question}

Analysiere diese Responses:
{alle_responses}

Was fehlt in ALLEN Antworten?
- Wichtige Aspekte nicht erwähnt
- Perspektiven ignoriert
- Trade-offs nicht diskutiert

Liste fehlende Aspekte die für die Entscheidung relevant sein könnten.
```

**Output:** Liste von Aspekten zum weiteren Research.

---

### 4. Premortem Analysis

**Was:** Forciert konkrete Failure Scenarios (bricht "helpful" Bias).

**Validator Prompt:**
```markdown
Es ist 2026. Das Projekt ist gescheitert. Post-Mortem Analyse:

Gegeben die Frage:
{question}

Und diese Antworten:
{alle_responses}

Schreibe ein detailliertes Failure Scenario:
- Haupt-Todesursache
- Ignorierte Warnsignale
- Fundamentale Fehlannahme
- Was hätte man anders machen müssen?

Sei brutal ehrlich. Keine Platitüden.
```

**Power:** Abliterated Model nimmt "Es ist gescheitert" als Fakt, ist nicht optimistisch.

---

### 5. Adversarial Prompting (manuell von dir)

**Was:** Du fragst bewusst verschiedene Perspektiven.

**Beispiel (Framework Choice):**

**Prompt 1 (Optimist):**
```
"Als React-Fan: Warum ist React die beste Wahl für unsere Tauri-App?"
```

**Prompt 2 (Pessimist):**
```
"Als Bundle-Size-Purist: Warum sollten wir React NICHT nutzen?"
```

**Prompt 3 (Neutral):**
```
"Faktenbasierte Bewertung: React vs Vue vs Svelte für Tauri Desktop App."
```

**Validator vergleicht:** Wie stark sind die Biases? Was sagen alle 3 Perspectives?

---

### 6. Anonymization (optional)

**Was:** Entfernt "ich/mein/wir" aus deiner Frage → macht AI distanzierter/kritischer.

**Beispiel:**

❌ **Original:**
```
"Ich plane eine AI Tutoring App. Sollte ich React oder Vue nutzen?"
```

✅ **Anonymized:**
```
"Ein Entwickler plant eine AI Tutoring App. Sollte React oder Vue genutzt werden?"
```

**Warum:** AI ist weniger "helpful" wenn es 3rd-person ist (behandelt es objektiver).

**Implementation:** Simple String-Replacement im Validator-Script.

---

## File Structure

```
product-management/
├── tools/
│   └── validator/
│       ├── validator.py         (Haupt-Logik)
│       ├── cli.py               (Command Line Interface)
│       ├── config.py            (Ollama Settings)
│       ├── prompts.py           (Validation Prompts)
│       ├── README.md            (Setup & Usage)
│       └── requirements.txt     (nur: requests)
│
├── 2-working-state/
│   ├── research-data/
│   │   └── validations/         ← Validation Data
│   │       ├── tech-stack-framework/
│   │       │   ├── question.md
│   │       │   ├── claude-response.md
│   │       │   ├── gpt4-response.md
│   │       │   ├── gemini-response.md
│   │       │   ├── llama-response.md
│   │       │   └── validation-report-20251209.md
│   │       │
│   │       ├── local-vs-hybrid/
│   │       │   ├── question.md
│   │       │   ├── ...
│   │       │   └── validation-report-20251209.md
│   │       │
│   │       └── pricing-model/
│   │           └── ...
│   │
│   └── planning_state.json     (tracks validations_run)
│
└── 1-description/
    └── research-validator-integration.md  (dieses File)
```

---

## When to Use Validator?

### HIGH Priority (must validate)

✅ **Architecture Decisions** (z.B. Local vs Hybrid)
- Reach: 10, Impact: 10
- Beeinflusst alles (Privacy, Performance, Cost)
- Multiple AIs widersprechen sich stark

✅ **Market Sizing** (z.B. TAM/SAM/SOM)
- Impact: 10
- Zahlen variieren massiv zwischen Sources
- Consensus Bias (alle zitieren gleichen Report)

✅ **Pricing Strategy** (z.B. Freemium vs Paid)
- Impact: 9-10
- Business-kritisch
- Viele Meinungen, wenig Fakten

### MEDIUM Priority (consider validation)

🟡 **Feature Prioritization** (z.B. MVP Scope)
- Impact: 8-9
- Nutze Validator wenn unklar

🟡 **GTM Channel Priority** (z.B. Reddit vs HackerNews vs Forums)
- Impact: 7-8
- Validation hilft bei blinden Flecken

### LOW Priority (skip validation)

⚪ **Nice-to-Have Features** (z.B. Dark Mode)
- Impact: 3-5
- Nicht kritisch, spare Zeit

⚪ **Naming/Branding** (z.B. Logo Colors)
- Impact: 4-6
- Subjektiv, Validation wenig Wert

---

## Cost & Time Budget

### Setup (einmalig)
- Ollama Installation: 10 min
- Model Download: 5 min (Dolphin-Mistral ~4GB)
- Python Environment: 5 min
- **Total:** 20 min

### Per Validation
- AI Responses sammeln (manuell): 20-30 min (3-4 AIs fragen)
- Responses als Files speichern: 5 min
- Validator laufen lassen: 2-5 min (lokal)
- Report analysieren: 10-15 min
- Actions umsetzen: 30-60 min (abhängig von Findings)
- **Total:** 1-2 Stunden pro kritischer Assumption

### Review Phase Budget
- Identifiziere 3-5 kritische Assumptions (aus 6 Kategorien)
- 1-2 Stunden pro Assumption
- **Total:** 3-10 Stunden für komplette Review Validation

**→ Fits in 1-2 Tage Review Phase Budget**

---

## Tech Stack (Validator)

### Required
- **Ollama:** Lokaler LLM Server (free, open-source)
- **Dolphin-Mistral:** Abliterated Mistral-7B (free, no censorship)
- **Python 3.8+:** Scripting
- **requests:** HTTP library (für Ollama API)

### Optional (Future)
- **Chroma/FAISS:** Vector DB für RAG (wenn du externe Daten einbinden willst)
- **LangChain:** Orchestration (wenn komplexere Workflows)
- **Gradio:** Web UI (wenn du GUI statt CLI willst)

**Start Simple:** CLI + Ollama + Python requests reicht!

---

## Alternative Models (falls Dolphin-Mistral nicht passt)

### Abliterated Models (keine RLHF "niceness")
1. **Dolphin-Mistral** (empfohlen)
   - Size: 7B params (~4GB)
   - Speed: ~30-50 tok/s (GPU), ~10-15 tok/s (CPU)
   - Lizenz: Apache 2.0

2. **Dolphin-Llama3:8b**
   - Size: 8B params (~5GB)
   - Speed: ~35-50 tok/s (GPU)
   - Lizenz: Llama 3 (commercial OK)

3. **Nous-Hermes-Uncensored**
   - Size: 7B/13B params
   - Speed: ~20-40 tok/s
   - Lizenz: Apache 2.0

### Standard Models (falls abliterated zu kritisch)
- **Llama 3.1:8b** (balanced)
- **Mistral:7b** (balanced)
- **Qwen2.5:7b** (good reasoning)

**Recommendation:** Start mit Dolphin-Mistral, wechseln wenn zu "brutal".

---

## Integration in Iterations (Optional)

Wenn eine **Question besonders kritisch** ist (z.B. I001 "Local vs Hybrid?"):

### In Iteration File:

```markdown
# I001: Local vs Hybrid Architecture?

**Question:** Should we build local-first or hybrid architecture?
**Priority:** CRITICAL (RICE 16.0)
**Status:** In Progress

---

## 1. Research

**Relevant Base Research:**
- 1-technical-feasibility/architecture.md
- 2-market-opportunity/segments.md (privacy segment)
- 3-monetization/cost-structure.md (cloud costs)

---

## 2. Validation ⭐ NEW SECTION

**Why Validate:**
- Decision impacts EVERYTHING (privacy, performance, cost, GTM)
- Multiple AI responses contradict each other
- High uncertainty (Confidence: 6/10)

**Validation Process:**
1. ✅ Collected 4 AI responses (Claude, GPT-4, Gemini, Llama)
2. ✅ Ran Validator (dolphin-mistral)
3. ✅ Analyzed report

**Validation Report:** `research-data/validations/local-vs-hybrid/validation-report-20251209.md`

**Key Findings:**
- ⚠️ Contradiction: Cloud cost estimates vary 10x ($0.01 vs $0.10 per query)
- ⚠️ Blind Spot: Installation friction for local-first (nobody mentioned)
- ✅ Consensus: Privacy = competitive moat (validated)

**Actions Taken:**
- ✅ Researched actual cloud costs (OpenAI, Anthropic pricing)
- ✅ Surveyed local AI tools (LM Studio, GPT4All) for installation UX
- ✅ Updated confidence: 6/10 → 8/10

---

## 3. Goals

[... rest of GIST iteration]
```

---

## Best Practices

### Do's ✅

✅ **Validate Critical Decisions** - nicht alles, nur Impact 9-10
✅ **Sammle 3-4 AI Responses** - mehr = bessere Widerspruchserkennung
✅ **Gleiche Frage, gleicher Kontext** - faire Vergleichbarkeit
✅ **Dokumentiere Actions** - was hast du nach Validation getan?
✅ **Update Base Research** - Validation-Findings zurück ins Research
✅ **Timeboxing** - 1-2 Stunden pro Validation, nicht länger

### Don'ts ❌

❌ **Nicht alles validieren** - nur kritische Assumptions (spare Zeit)
❌ **Nicht blind vertrauen** - Validator kann auch falsch liegen
❌ **Nicht ohne Follow-up** - Validation ohne Action = wertlos
❌ **Nicht nur ein Model** - minimum 3 AI Responses für gute Validation
❌ **Nicht in Analyse-Paralyse** - nach 2h Actions starten, nicht 2 Tage researchen

---

## Exit Criteria: Validation Complete

Für eine Validation:
- [ ] Kritische Assumption identifiziert
- [ ] 3-4 AI Responses gesammelt
- [ ] Validator gelaufen
- [ ] Report analysiert
- [ ] Contradictions geklärt (durch eigenes Research/Testing)
- [ ] Blind Spots adressiert (recherchiert oder dokumentiert für später)
- [ ] Base Research updated mit Findings
- [ ] Confidence Level aktualisiert

Für Review Phase (gesamt):
- [ ] 3-5 kritische Assumptions validiert
- [ ] Alle 6 Kategorien reviewed (mit oder ohne Validation)
- [ ] Cross-dependencies geprüft
- [ ] planning_state.json updated
- [ ] Bereit für Question Extraction

---

## Future Enhancements

### Phase 1 (nice to have)
- **Web UI:** Gradio interface statt CLI
- **Auto-Prompting:** Script fragt AIs automatisch (via APIs)
- **RAG Integration:** Validator nutzt deine `research-data/` Files

### Phase 2 (advanced)
- **Fine-Tuned Validator:** Trainiert auf deinen Validation History
- **Multi-Validator:** Mehrere lokale Models für Cross-Validation
- **Validation Templates:** Vorgefertigte Prompts für häufige Validation-Types

**Start Simple:** CLI + manuelles Response-Sammeln reicht erstmal!

---

## Related Files

- **planning-framework.md** - GIST Iterations
- **research-framework.md** - Base Research Process
- **templates.md** - Template für Validation Report
- **planning_state.json** - Tracking validations_run

---

## Summary

**Validator = Research Quality Assurance Tool**

**Use Cases:**
1. ✅ Base Research Review (primär)
2. ✅ Kritische Questions in Iterations (sekundär)
3. ✅ Widersprüche klären
4. ✅ Blinde Flecken finden
5. ✅ Consensus Bias aufdecken

**Tech:** Lokal, kostenlos, keine APIs, privacy-safe

**ROI:** 1-2 Stunden Aufwand → Verhindert falsche Decisions (€1000+ Impact)

**Integration:** Passt in existierende Review Phase (kein neuer Workflow nötig)

---

**Next Steps:**

1. **Entscheide:** Willst du Validator nutzen? (Ja/Nein/Später)
2. **Setup:** Ollama + Dolphin-Mistral installieren (20 min)
3. **Test:** Eine Validation durchführen (z.B. "Local vs Hybrid?")
4. **Evaluate:** Hilft es? Dann in Review Phase integrieren
5. **Iterate:** Bei Bedarf Prompts/Workflow anpassen

**Claude Code kann helfen mit:** Validator Code schreiben, Setup automatisieren, Prompts optimieren
