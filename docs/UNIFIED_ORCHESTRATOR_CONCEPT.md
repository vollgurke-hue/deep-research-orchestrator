# Unified Orchestrator Concept

**Ziel**: Eine vereinte Vue.js Frontend-Applikation für den gesamten Deep Research Orchestrator mit klaren, wiederverwendbaren Patterns.

---

## 🎯 1. Vereinheitlichung der UIs

### Aktueller Zustand (3 getrennte UIs):
```
❌ MD Viewer         (Port 8002/docs)       - Dokumentation
❌ Vue Orchestrator  (Port 5173)            - Workflow-Editor
❌ Flask UI          (Port 8002/gui)        - Dashboard
```

### Neuer Zustand (1 vereinte UI):
```
✅ Vue Orchestrator App (Port 5173)
   ├── 📂 Documentation Tab    (MD Viewer integriert)
   ├── 🎛️  Orchestrator Tab    (Workflow-Editor)
   ├── 📊 Dashboard Tab        (Übersicht)
   └── 📈 Execution Tab        (Live Working State)
```

---

## 🏗️ 2. Grundlegende Orchestrator-Patterns

### Pattern 1: **Research Lifecycle** (Universal für jedes Framework)

```
Phase 0: Base Research
   ↓
Phase 1: Excurse (Vertiefung)
   ↓
Phase 2: Validation
   ↓
Phase 3: Synthesis
```

**Beschreibung:**
- **Base Research**: Initiales breites Research (parallele Datensammlung)
- **Excurse**: Vertiefende Recherche zu identifizierten Gaps
- **Validation**: Qualitätskontrolle & Widerspruchsprüfung
- **Synthesis**: Zusammenfassung & Actionable Insights

**Status**: ✅ Teilweise implementiert (Base, Validation, Synthesis)
**Fehlend**: ❌ Phase 1 "Excurse" muss noch erstellt werden

---

### Pattern 2: **Output Structure** (für JEDEN Building Block)

Jeder Building Block (Technique, Workflow, Phase, Framework) muss diese Struktur haben:

```json
{
  "block_id": "unique_identifier",
  "name": "Human-readable Name",
  "description": "Was macht dieser Block?",
  "type": "technique|workflow|phase|framework",

  "working_state": {
    "status": "pending|in_progress|completed|failed",
    "progress": 0-100,
    "current_step": "description of current step",
    "started_at": "ISO timestamp",
    "updated_at": "ISO timestamp"
  },

  "output": {
    "format": "markdown|json|structured",
    "content": "actual output content",
    "metadata": {
      "confidence_score": 0.0-1.0,
      "model_used": "model_id",
      "token_count": 1234,
      "execution_time_ms": 5678
    }
  },

  "building_blocks": [
    // Nested building blocks (für Workflow/Phase/Framework)
  ],

  "exit_criteria": {
    "type": "all_complete|confidence_threshold|custom",
    "threshold": 0.8,
    "required_outputs": ["output1", "output2"]
  }
}
```

**Status**: ⚠️ Teilweise implementiert
**Fehlend**:
- ❌ `working_state` fehlt in aktuellen JSONs
- ❌ `output` Struktur nicht standardisiert

---

### Pattern 3: **Technique-Prompt Template** (Basis für alle Prompts)

```markdown
# [Technique Name]

## Context
{context_from_previous_steps}

## Input
{input_data}

## Task
[Clear instruction what to do]

## Output Format
[Exact structure expected]

## Quality Criteria
- Criterion 1
- Criterion 2
- ...

## Examples (optional)
[Example input/output pairs]
```

**Status**: ⚠️ Nicht standardisiert
**Aktuell**: Jede Technique hat freien Prompt-Text
**Ziel**: Template-basierte Prompts mit klaren Sections

---

### Pattern 4: **Category System** (für Organisation)

Jedes Framework nutzt diese Standard-Kategorien:

```
1. market_opportunity      - Markt & Bedarf
2. technical_feasibility   - Technische Umsetzbarkeit
3. competition             - Wettbewerb & Alternativen
4. quality_assurance       - Validierung & QA
5. strategic_planning      - Synthese & Planung
6. iterative_refinement    - Gap-Detection & Nachforschung
```

**Status**: ✅ Implementiert in Phases
**Verwendung**: Building Blocks haben `category` Field

---

## 🧱 3. Building Block Hierarchie (Bottom-Up)

### Ebene 1: **Technique** (kleinste Einheit)

```json
{
  "technique_id": "contradiction_check",
  "name": "Contradiction Check",
  "description": "Analyze research for internal contradictions",
  "type": "technique",

  "prompt": "[Template-based prompt]",
  "temperature": 0.3,
  "max_tokens": 2000,
  "agent_role": "quality_validator",

  "working_state": { ... },
  "output": { ... }
}
```

**GUI-Funktionen:**
- ✅ Prompt editieren (Textarea)
- ✅ Settings anpassen (Temperature, Max Tokens)
- ❌ Template-based Prompt Editor (Sections)
- ❌ Test-Execution (Prompt testen mit Sample Input)

---

### Ebene 2: **Workflow** (Gruppe von Techniques)

```json
{
  "workflow_id": "research_validation",
  "name": "Research Validation Workflow",
  "description": "Multi-technique validation of research findings",
  "type": "workflow",
  "mode": "sequential",

  "building_blocks": [
    { "block_type": "technique", "block_id": "contradiction_check" },
    { "block_type": "technique", "block_id": "blind_spots" },
    { "block_type": "technique", "block_id": "sanity_check" }
  ],

  "working_state": { ... },
  "output": { ... },
  "exit_criteria": { ... }
}
```

**GUI-Funktionen:**
- ✅ Workflows anzeigen (Tree View)
- ❌ Drag & Drop Techniques zu Workflow hinzufügen
- ❌ Reihenfolge ändern (Drag & Drop)
- ❌ Mode wählen (sequential vs parallel)
- ❌ Exit Criteria definieren

---

### Ebene 3: **Phase** (Gruppe von Workflows)

```json
{
  "phase_id": "phase_0_base_research",
  "name": "Base Research Phase",
  "description": "Initial research collection",
  "type": "phase",

  "building_blocks": [
    { "block_type": "workflow", "block_id": "market_research_collection" },
    { "block_type": "workflow", "block_id": "tech_feasibility_collection" }
  ],

  "working_state": { ... },
  "output": { ... },
  "exit_criteria": { ... },
  "metadata": {
    "parallelizable": true,
    "estimated_duration": "1-2 hours"
  }
}
```

**GUI-Funktionen:**
- ✅ Phases anzeigen (Tree View)
- ❌ Workflows zu Phase hinzufügen
- ❌ Parallelisierung konfigurieren
- ❌ Exit Criteria definieren

---

### Ebene 4: **Framework** (kompletter Research-Durchgang)

```json
{
  "framework_id": "framework_product_research",
  "name": "Product Research Framework",
  "description": "Complete product research workflow",
  "type": "framework",

  "building_blocks": [
    { "block_type": "phase", "block_id": "phase_0_base_research", "order": 1 },
    { "block_type": "phase", "block_id": "phase_1_excurse", "order": 2 },
    { "block_type": "phase", "block_id": "phase_2_validation", "order": 3 },
    { "block_type": "phase", "block_id": "phase_3_synthesis", "order": 4 }
  ],

  "working_state": { ... },
  "output": { ... },
  "global_exit_criteria": { ... },
  "metadata": {
    "use_case": "Product planning and validation",
    "estimated_total_duration": "4-6 hours"
  }
}
```

**GUI-Funktionen:**
- ✅ Frameworks anzeigen (Dashboard)
- ❌ Framework-Builder (Phases zusammenstellen)
- ❌ Execution starten
- ❌ Live Working State visualisieren

---

## 📊 4. Working State Visualisierung (Vue Component)

### Component: `<WorkingStateViewer>`

**Zweck**: Live-Anzeige des aktuellen Execution-Status

```vue
<template>
  <div class="working-state">
    <!-- Overall Progress -->
    <div class="progress-bar">
      <div class="progress" :style="{ width: overallProgress + '%' }"></div>
    </div>

    <!-- Current Phase -->
    <div class="current-phase">
      <h3>{{ currentPhase.name }}</h3>
      <span class="status">{{ currentPhase.working_state.status }}</span>
    </div>

    <!-- Execution Timeline -->
    <div class="timeline">
      <div v-for="phase in phases" :key="phase.phase_id"
           class="timeline-item"
           :class="phase.working_state.status">
        <div class="phase-name">{{ phase.name }}</div>
        <div class="phase-progress">{{ phase.working_state.progress }}%</div>
      </div>
    </div>

    <!-- Current Step Details -->
    <div class="step-details">
      <h4>Current Step:</h4>
      <p>{{ currentStep.description }}</p>
      <code>Model: {{ currentStep.model_used }}</code>
      <code>Tokens: {{ currentStep.token_count }}</code>
    </div>
  </div>
</template>
```

**Features:**
- ✅ Live Progress Bar
- ✅ Timeline mit allen Phases
- ✅ Status-Badges (pending/in_progress/completed/failed)
- ✅ Token-Count & Model-Info
- ✅ Execution Time

---

## 🎨 5. Vereinte UI-Architektur

### Main Navigation (Top-Level Tabs)

```
┌────────────────────────────────────────────────────────────┐
│  Deep Research Orchestrator                                │
├────────────────────────────────────────────────────────────┤
│  [📊 Dashboard] [🎛️ Builder] [📈 Execution] [📂 Docs]      │
└────────────────────────────────────────────────────────────┘
```

### Tab 1: **Dashboard** (Übersicht)
```
- Framework-Karten (wie jetzt)
- Quick Stats (Anzahl Frameworks, Workflows, Techniques)
- Recent Executions (History)
- Quick Actions (New Framework, Import, Export)
```

### Tab 2: **Builder** (Workflow-Editor)
```
Linke Sidebar:
  - Building Blocks Library
    - Techniques (searchbar + cards)
    - Workflows (list)
    - Phases (list)

Hauptbereich:
  - Canvas (Vue Flow Drag & Drop)
  - Technique/Workflow/Phase Editor (rechts)

Rechte Sidebar:
  - Property Panel (aktives Element)
  - Prompt Editor (für Techniques)
```

### Tab 3: **Execution** (Live Working State)
```
- Framework-Auswahl
- Execute-Button
- Live Working State Viewer
- Output-Anzeige (Markdown/JSON)
- Logs & Debug-Info
```

### Tab 4: **Docs** (MD Viewer integriert)
```
- Sidebar mit Docs-Tree (wie jetzt)
- Markdown-Viewer (wie jetzt)
- Search-Funktion
```

---

## 🚀 6. Implementierungs-Roadmap

### Phase 1: **Konzept & Schema** ✅ (JETZT)
- [x] Patterns definieren
- [x] Output-Struktur standardisieren
- [x] Working State Schema
- [ ] JSON-Schemas updaten

### Phase 2: **UI Vereinheitlichung** 🚧
- [ ] Main Tab Navigation
- [ ] MD Viewer in Vue integrieren
- [ ] Dashboard erweitern
- [ ] Builder-Tab Grundgerüst

### Phase 3: **Working State System** 📋
- [ ] Working State zu allen JSONs hinzufügen
- [ ] WorkingStateViewer Component
- [ ] Execution Engine erweitern (Status-Updates)
- [ ] WebSocket für Live-Updates

### Phase 4: **Builder-Funktionalität** 📋
- [ ] Drag & Drop Canvas (Vue Flow)
- [ ] Building Blocks Library
- [ ] Create/Delete Funktionen
- [ ] Template-System

### Phase 5: **Execution & Monitoring** 📋
- [ ] Execute-Button Integration
- [ ] Live Progress Tracking
- [ ] Output-Viewer
- [ ] Error Handling & Retry

---

## 📋 7. Offene Fragen (für Klärung)

### Frage 1: **Excurse-Phase**
Du hast "Excurse" erwähnt - soll das eine eigene Phase werden?
- **Option A**: Phase 1 "Excurse" zwischen Base Research und Validation
- **Option B**: Excurse als Teil von Validation (Gap-Detection Loop)
- **Deine Präferenz?**

### Frage 2: **Description vs Working State**
> "das pattern des description workingstat und des outputes genau zu deffinieren"

Meinst du:
- **description**: Statische Beschreibung was der Block macht
- **working_state**: Live-Status während Execution (progress, current_step)
- **output**: Resultat nach Completion

Korrekt verstanden?

### Frage 3: **Product Management Pattern**
Du erwähnst:
> "so wir wir es zuvor in pruduct managment gemacht haben"

Soll ich das alte Product Management Projekt analysieren und die Patterns extrahieren? Oder reichen die 3 Strukturen (description, working_state, output)?

### Frage 4: **Visualisierung**
> "wobei der workingstate einfach eine visuallisierung sein kann in vue"

Soll Working State NUR in der UI visualisiert werden, oder auch in den JSON-Files persistiert (für History/Replay)?

---

## ✅ Nächste Schritte

Sobald diese Fragen geklärt sind, können wir:

1. **JSON-Schemas aktualisieren** mit working_state + output
2. **Vue UI vereinheitlichen** (Tabs + MD Viewer Integration)
3. **Builder-Tab implementieren** (Drag & Drop Canvas)
4. **Working State System** (Live Execution Tracking)

---

**Status**: Konzept fertig, warte auf dein Feedback zu den offenen Fragen! 🎯
