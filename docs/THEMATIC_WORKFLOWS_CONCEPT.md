# Thematic Workflows & Generic/Specific Separation

**Datum**: 2026-01-02
**Status**: Konzept → Implementierung

---

## 🎯 Kernidee

**Phasen sind fix** - Base/Excurse/Validation/Synthesis bleiben immer gleich

**Thematische Workflows sind flexibel** - User wählt aus, welche thematischen Bereiche in Phase 0 (Base Research) relevant sind

**Generic vs Specific** - Klare visuelle Trennung zwischen wiederverwendbaren Techniques (🟠 Generic) und angepassten Prompts (🔵 Specific)

---

## 📊 Struktur

### Fixe Phasen (immer gleich)

```
Research
├─ Phase 0: Base Research          ← Thematische Workflows hier
├─ Phase 1: Excurse                ← Fix (Gap Detection Loop)
├─ Phase 2: Validation             ← Fix (Quality Assurance)
└─ Phase 3: Synthesis              ← Fix (Final Report)
```

### Thematische Workflows (flexibel auswählbar)

**In Phase 0 gibt es vordefinierte thematische Workflows:**

1. **🟠 Market Opportunity**
   - Marktbedarf, Zielgruppen, Problem-Solution-Fit
   - Techniques: `market_need_detector`, `customer_segment_analyzer`, `problem_validator`

2. **🟠 Competitor Analysis**
   - Wettbewerb, Alternativen, Feature-Vergleich
   - Techniques: `competitor_identifier`, `feature_comparison`, `pricing_analyzer`

3. **🟠 Tech Feasibility**
   - Technische Umsetzbarkeit, Stack, Integrations
   - Techniques: `tech_stack_analyzer`, `integration_checker`, `scalability_estimator`

4. **🟠 Legal & Compliance**
   - Rechtliche Rahmenbedingungen, Datenschutz, Lizenzierung
   - Techniques: `legal_requirements_checker`, `gdpr_compliance_analyzer`

5. **🟠 Monetization Strategy**
   - Geschäftsmodell, Pricing, Revenue Streams
   - Techniques: `business_model_analyzer`, `pricing_strategy_detector`

6. **🟠 Go-to-Market**
   - Launch-Strategie, Marketing-Kanäle, Distribution
   - Techniques: `channel_analyzer`, `launch_strategy_detector`

---

## 🎨 Generic vs Specific

### 🟠 Generic (Orange/Gold)

**Definition**: Wiederverwendbare Techniques, die für ALLE Researches funktionieren

**Eigenschaften:**
- Universeller Prompt
- Keine domain-spezifischen Annahmen
- Kann in verschiedenen Kontexten genutzt werden
- Standard Exit Criteria

**Beispiel: `contradiction_check`**
```json
{
  "technique_id": "contradiction_check",
  "type": "technique",
  "name": "Contradiction Detection",
  "is_generic": true,
  "prompt": "Analyze the following outputs and identify contradictions...",
  "category": "quality_assurance"
}
```

**Visuelle Darstellung:**
```
[🟠 contradiction_check]  Generic - Works everywhere
```

---

### 🔵 Specific (Blue/Turquoise)

**Definition**: Anpassungen/Customizations für eine spezifische Research

**Eigenschaften:**
- Angepasster Prompt mit domain-spezifischen Details
- Custom Exit Criteria
- Spezifische Placeholders
- Verlinkt zu Generic Base Technique

**Beispiel: Customized `market_need_detector`**
```json
{
  "technique_id": "market_need_detector_saas_custom",
  "type": "technique",
  "name": "Market Need Detector (SaaS Focus)",
  "is_generic": false,
  "base_technique": "market_need_detector",
  "prompt": "Analyze market needs specifically for SaaS products with subscription models...",
  "customizations": {
    "focus": "SaaS products",
    "pricing_model": "subscription",
    "target_audience": "B2B enterprises"
  }
}
```

**Visuelle Darstellung:**
```
[🟠 market_need_detector]  Generic
  └─ [🔵 Customized for SaaS]  Specific
```

---

## 🛠️ Research Creation Workflow

### Schritt 1: Research Name & Beschreibung

```
┌─────────────────────────────────────────────┐
│ Create New Research                         │
├─────────────────────────────────────────────┤
│ Name: Product Market Research (SaaS)        │
│ Description: Validate SaaS product ideas... │
└─────────────────────────────────────────────┘
```

---

### Schritt 2: Thematic Workflows auswählen

**User wählt aus, welche thematischen Bereiche relevant sind:**

```
┌─────────────────────────────────────────────┐
│ Phase 0: Base Research                      │
│ Select Thematic Workflows                   │
├─────────────────────────────────────────────┤
│                                             │
│ ☑ 🟠 Market Opportunity                     │
│    Marktbedarf, Zielgruppen, PSF            │
│    → 3 techniques                           │
│                                             │
│ ☑ 🟠 Competitor Analysis                    │
│    Wettbewerb, Alternativen                 │
│    → 3 techniques                           │
│                                             │
│ ☑ 🟠 Tech Feasibility                       │
│    Technische Umsetzbarkeit                 │
│    → 3 techniques                           │
│                                             │
│ ☐ 🟠 Legal & Compliance                     │
│    Rechtliche Rahmenbedingungen             │
│    → 2 techniques                           │
│                                             │
│ ☐ 🟠 Monetization Strategy                  │
│    Geschäftsmodell, Pricing                 │
│    → 2 techniques                           │
│                                             │
│ ☐ 🟠 Go-to-Market                           │
│    Launch-Strategie, Marketing              │
│    → 2 techniques                           │
│                                             │
│         [Cancel]         [Next: Customize →]│
└─────────────────────────────────────────────┘
```

**Result**: User hat 3 Workflows ausgewählt → 9 Techniques in Phase 0

---

### Schritt 3: Techniques Customizen (Optional)

**Für jede Technique kann User entscheiden:**

```
┌─────────────────────────────────────────────┐
│ Customize: market_need_detector             │
├─────────────────────────────────────────────┤
│                                             │
│ [🟠] Use Generic Version                    │
│      Standard prompt, works for all markets │
│                                             │
│ [🔵] Customize for this Research            │
│      Adapt prompt for specific domain       │
│                                             │
│ ┌─────────────────────────────────────────┐ │
│ │ Customization Options:                  │ │
│ │                                         │ │
│ │ Focus Area:                             │ │
│ │ [SaaS products with subscription model] │ │
│ │                                         │ │
│ │ Target Audience:                        │ │
│ │ [B2B enterprises, 50-500 employees]     │ │
│ │                                         │ │
│ │ Exclude:                                │ │
│ │ [Free/Freemium models]                  │ │
│ │                                         │ │
│ │ Additional Context:                     │ │
│ │ [Focus on cloud-based solutions...]     │ │
│ └─────────────────────────────────────────┘ │
│                                             │
│      [Use Generic]         [Apply Custom]   │
└─────────────────────────────────────────────┘
```

**Result nach Customization:**
- Generic: 6 techniques (🟠)
- Customized: 3 techniques (🔵)

---

### Schritt 4: Visual Review

**Zeige komplette Struktur mit Farbcodierung:**

```
┌─────────────────────────────────────────────────────┐
│ 📦 Research: Product Market Research (SaaS)         │
├─────────────────────────────────────────────────────┤
│                                                     │
│ Phase 0: Base Research                              │
│   ├─ Market Opportunity Workflow                    │
│   │  ├─ [🟠 market_need_detector]                   │
│   │  │   └─ [🔵 Customized for SaaS]                │
│   │  ├─ [🟠 customer_segment_analyzer]              │
│   │  │   └─ [🔵 B2B Enterprise Focus]               │
│   │  └─ [🟠 problem_validator] Generic              │
│   │                                                  │
│   ├─ Competitor Analysis Workflow                   │
│   │  ├─ [🟠 competitor_identifier] Generic          │
│   │  ├─ [🟠 feature_comparison] Generic             │
│   │  └─ [🟠 pricing_analyzer]                       │
│   │      └─ [🔵 Include Open Source]                │
│   │                                                  │
│   └─ Tech Feasibility Workflow                      │
│      ├─ [🟠 tech_stack_analyzer] Generic            │
│      ├─ [🟠 integration_checker] Generic            │
│      └─ [🟠 scalability_estimator] Generic          │
│                                                     │
│ Phase 1: Excurse (fix)                              │
│   └─ Gap Detection & Iterative Refinement           │
│                                                     │
│ Phase 2: Validation (fix)                           │
│   └─ Quality Assurance & Contradiction Check        │
│                                                     │
│ Phase 3: Synthesis (fix)                            │
│   └─ Final Report Generation                        │
│                                                     │
│ Total: 9 techniques (6 generic 🟠, 3 custom 🔵)     │
│                                                     │
│         [← Back to Edit]        [Save Research]     │
└─────────────────────────────────────────────────────┘
```

---

## 📂 Datei-Struktur

### Generic Techniques (Library)

```
config/
  techniques/
    generic/
      contradiction.json           🟠 Generic
      gap_detector.json            🟠 Generic
      market_need_detector.json    🟠 Generic
      competitor_identifier.json   🟠 Generic
      tech_stack_analyzer.json     🟠 Generic
      ...
```

**Eigenschaften:**
- `"is_generic": true`
- Universeller Prompt
- Kann in allen Researches verwendet werden
- Wird NICHT dupliziert, nur referenziert

---

### Customized Techniques (Per Research)

```
config/
  researches/
    product_market_research_saas/
      research.json                     ← Main Research Definition
      customizations/
        market_need_detector_custom.json  🔵 Specific
        customer_segment_custom.json      🔵 Specific
        pricing_analyzer_custom.json      🔵 Specific
```

**Eigenschaften:**
- `"is_generic": false`
- `"base_technique": "market_need_detector"` (Link zu Generic)
- Angepasster Prompt
- Research-spezifisch

---

### Thematic Workflow Definitions

```
config/
  workflows/
    thematic/
      market_opportunity.json      ← Thematic Workflow
      competitor_analysis.json     ← Thematic Workflow
      tech_feasibility.json        ← Thematic Workflow
      legal_compliance.json        ← Thematic Workflow
      monetization.json            ← Thematic Workflow
      go_to_market.json            ← Thematic Workflow
```

**Struktur:**
```json
{
  "workflow_id": "market_opportunity",
  "type": "thematic_workflow",
  "name": "Market Opportunity Analysis",
  "description": "Analyze market needs, target audiences, and problem-solution fit",
  "category": "market_opportunity",
  "icon": "🎯",
  "building_blocks": [
    {
      "block_id": "market_need_detector",
      "block_type": "technique",
      "order": 0,
      "is_generic": true
    },
    {
      "block_id": "customer_segment_analyzer",
      "block_type": "technique",
      "order": 1,
      "is_generic": true
    },
    {
      "block_id": "problem_validator",
      "block_type": "technique",
      "order": 2,
      "is_generic": true
    }
  ],
  "metadata": {
    "estimated_duration": "15-20 minutes",
    "recommended_for": ["product", "market", "startup"]
  }
}
```

---

## 🎨 UI Components

### ThematicWorkflowSelector.vue

```vue
<template>
  <div class="thematic-workflow-selector">
    <h3>Phase 0: Base Research</h3>
    <p>Select thematic areas relevant for your research:</p>

    <div class="workflow-grid">
      <div
        v-for="workflow in availableWorkflows"
        :key="workflow.workflow_id"
        :class="['workflow-card', { selected: isSelected(workflow) }]"
        @click="toggleWorkflow(workflow)"
      >
        <div class="card-header">
          <span class="workflow-icon">{{ workflow.icon }}</span>
          <div class="card-badge">🟠 Generic</div>
        </div>

        <h4>{{ workflow.name }}</h4>
        <p class="description">{{ workflow.description }}</p>

        <div class="card-meta">
          <span>{{ workflow.building_blocks.length }} techniques</span>
          <span>{{ workflow.metadata.estimated_duration }}</span>
        </div>

        <div v-if="isSelected(workflow)" class="selected-indicator">
          ✓ Selected
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const availableWorkflows = ref([
  {
    workflow_id: 'market_opportunity',
    name: 'Market Opportunity',
    description: 'Marktbedarf, Zielgruppen, Problem-Solution-Fit',
    icon: '🎯',
    building_blocks: [
      { block_id: 'market_need_detector' },
      { block_id: 'customer_segment_analyzer' },
      { block_id: 'problem_validator' }
    ],
    metadata: { estimated_duration: '15-20 min' }
  },
  {
    workflow_id: 'competitor_analysis',
    name: 'Competitor Analysis',
    description: 'Wettbewerb, Alternativen, Feature-Vergleich',
    icon: '🏆',
    building_blocks: [
      { block_id: 'competitor_identifier' },
      { block_id: 'feature_comparison' },
      { block_id: 'pricing_analyzer' }
    ],
    metadata: { estimated_duration: '15-20 min' }
  },
  // ... mehr workflows
])

const selectedWorkflows = ref([])

function toggleWorkflow(workflow) {
  const index = selectedWorkflows.value.findIndex(w => w.workflow_id === workflow.workflow_id)
  if (index >= 0) {
    selectedWorkflows.value.splice(index, 1)
  } else {
    selectedWorkflows.value.push(workflow)
  }
}

function isSelected(workflow) {
  return selectedWorkflows.value.some(w => w.workflow_id === workflow.workflow_id)
}
</script>

<style scoped>
.workflow-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
  margin-top: 1.5rem;
}

.workflow-card {
  background: var(--bg-panel);
  border: 2px solid var(--border-medium);
  border-radius: 12px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.workflow-card:hover {
  transform: translateY(-2px);
  border-color: var(--accent-gold);
}

.workflow-card.selected {
  border-color: var(--accent-gold);
  background: rgba(255, 179, 71, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.workflow-icon {
  font-size: 2rem;
}

.card-badge {
  background: var(--accent-gold);
  color: var(--bg-panel);
  padding: 0.25rem 0.6rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
}

.workflow-card h4 {
  margin: 0 0 0.5rem 0;
  color: var(--text-main);
}

.description {
  color: var(--text-muted);
  font-size: 0.9rem;
  line-height: 1.4;
  margin-bottom: 1rem;
}

.card-meta {
  display: flex;
  justify-content: space-between;
  font-size: 0.85rem;
  color: var(--text-muted);
  padding-top: 0.75rem;
  border-top: 1px solid var(--border-light);
}

.selected-indicator {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: #22c55e;
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
}
</style>
```

---

### TechniqueCustomizer.vue

```vue
<template>
  <div class="technique-customizer">
    <div class="customizer-header">
      <h4>{{ technique.name }}</h4>
      <span class="badge" :class="{ generic: !isCustomized, custom: isCustomized }">
        {{ isCustomized ? '🔵 Customized' : '🟠 Generic' }}
      </span>
    </div>

    <div class="customization-mode">
      <label class="mode-option">
        <input type="radio" v-model="mode" value="generic" />
        <div class="option-content">
          <span class="option-icon">🟠</span>
          <div>
            <strong>Use Generic Version</strong>
            <p>Standard prompt, works for all researches</p>
          </div>
        </div>
      </label>

      <label class="mode-option">
        <input type="radio" v-model="mode" value="custom" />
        <div class="option-content">
          <span class="option-icon">🔵</span>
          <div>
            <strong>Customize for this Research</strong>
            <p>Adapt prompt for specific domain</p>
          </div>
        </div>
      </label>
    </div>

    <div v-if="mode === 'custom'" class="customization-form">
      <div class="form-group">
        <label>Focus Area</label>
        <input v-model="customizations.focus" placeholder="e.g., SaaS products" />
      </div>

      <div class="form-group">
        <label>Target Audience</label>
        <input v-model="customizations.target_audience" placeholder="e.g., B2B enterprises" />
      </div>

      <div class="form-group">
        <label>Exclude</label>
        <input v-model="customizations.exclude" placeholder="e.g., Free/Freemium models" />
      </div>

      <div class="form-group">
        <label>Additional Context</label>
        <textarea v-model="customizations.additional_context" rows="3"></textarea>
      </div>

      <button @click="applyCustomization" class="apply-btn">
        Apply Customization
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  technique: {
    type: Object,
    required: true
  }
})

const mode = ref('generic')
const customizations = ref({
  focus: '',
  target_audience: '',
  exclude: '',
  additional_context: ''
})

const isCustomized = computed(() => mode.value === 'custom')

function applyCustomization() {
  // Generate customized prompt
  emit('customize', {
    technique_id: props.technique.technique_id,
    mode: mode.value,
    customizations: { ...customizations.value }
  })
}
</script>
```

---

## 🚀 Implementation Plan

### Phase 1: Thematic Workflow Definitions (Backend)
- [ ] Create 6 thematic workflow JSONs
- [ ] Define generic techniques library
- [ ] API endpoints for thematic workflows

### Phase 2: UI Components (Frontend)
- [ ] ThematicWorkflowSelector component
- [ ] TechniqueCustomizer component
- [ ] Visual Builder mit Farbcodierung

### Phase 3: Research Creation Flow
- [ ] Multi-step wizard integration
- [ ] Customization persistence
- [ ] Preview & Save

---

**Status**: Konzept Complete → Ready for Implementation 🚀
