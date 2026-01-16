<template>
  <div class="thematic-workflow-selector">
    <div class="selector-header">
      <h3>📦 Phase 0: Base Research</h3>
      <p>Select thematic areas relevant for your research:</p>
    </div>

    <div class="workflow-grid">
      <div
        v-for="workflow in availableWorkflows"
        :key="workflow.workflow_id"
        :class="['workflow-card', { selected: isSelected(workflow) }]"
        @click="toggleWorkflow(workflow)"
      >
        <!-- Card Header -->
        <div class="card-header">
          <span class="workflow-icon">{{ workflow.icon }}</span>
          <div class="card-badge generic">🟠 Generic</div>
        </div>

        <!-- Card Content -->
        <h4>{{ workflow.name }}</h4>
        <p class="description">{{ workflow.description }}</p>

        <!-- Card Meta -->
        <div class="card-meta">
          <span class="meta-item">
            <span class="meta-icon">🔧</span>
            {{ workflow.building_blocks.length }} techniques
          </span>
          <span class="meta-item">
            <span class="meta-icon">⏱️</span>
            {{ workflow.metadata.estimated_duration }}
          </span>
        </div>

        <!-- Selected Indicator -->
        <div v-if="isSelected(workflow)" class="selected-indicator">
          <span class="check-icon">✓</span>
          Selected
        </div>
      </div>
    </div>

    <!-- Selection Summary -->
    <div v-if="selectedWorkflows.length > 0" class="selection-summary">
      <div class="summary-header">
        <h4>Selected Workflows ({{ selectedWorkflows.length }})</h4>
        <button @click="clearSelection" class="clear-btn">Clear All</button>
      </div>
      <div class="summary-content">
        <div class="summary-stat">
          <span class="stat-label">Total Techniques:</span>
          <span class="stat-value">{{ totalTechniques }}</span>
        </div>
        <div class="summary-stat">
          <span class="stat-label">Estimated Duration:</span>
          <span class="stat-value">{{ estimatedDuration }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const emit = defineEmits(['update:selectedWorkflows'])

const availableWorkflows = ref([])
const selectedWorkflows = ref([])

onMounted(async () => {
  // Load thematic workflows from backend
  // TODO: Replace with actual API call
  availableWorkflows.value = [
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
    {
      workflow_id: 'tech_feasibility',
      name: 'Technical Feasibility',
      description: 'Technische Umsetzbarkeit, Stack, Integrations',
      icon: '⚙️',
      building_blocks: [
        { block_id: 'tech_stack_analyzer' },
        { block_id: 'integration_checker' },
        { block_id: 'scalability_estimator' }
      ],
      metadata: { estimated_duration: '20-25 min' }
    },
    {
      workflow_id: 'legal_compliance',
      name: 'Legal & Compliance',
      description: 'Rechtliche Rahmenbedingungen, Datenschutz',
      icon: '⚖️',
      building_blocks: [
        { block_id: 'legal_requirements_checker' },
        { block_id: 'gdpr_compliance_analyzer' }
      ],
      metadata: { estimated_duration: '10-15 min' }
    },
    {
      workflow_id: 'monetization',
      name: 'Monetization Strategy',
      description: 'Geschäftsmodell, Pricing, Revenue Streams',
      icon: '💰',
      building_blocks: [
        { block_id: 'business_model_analyzer' },
        { block_id: 'pricing_strategy_detector' }
      ],
      metadata: { estimated_duration: '12-18 min' }
    },
    {
      workflow_id: 'go_to_market',
      name: 'Go-to-Market Strategy',
      description: 'Launch-Strategie, Marketing-Kanäle',
      icon: '🚀',
      building_blocks: [
        { block_id: 'channel_analyzer' },
        { block_id: 'launch_strategy_detector' }
      ],
      metadata: { estimated_duration: '12-18 min' }
    }
  ]
})

const totalTechniques = computed(() => {
  return selectedWorkflows.value.reduce((sum, workflow) => {
    return sum + workflow.building_blocks.length
  }, 0)
})

const estimatedDuration = computed(() => {
  if (selectedWorkflows.value.length === 0) return '0 min'

  // Extract min and max from duration strings
  let totalMin = 0
  let totalMax = 0

  selectedWorkflows.value.forEach(workflow => {
    const duration = workflow.metadata.estimated_duration
    const match = duration.match(/(\d+)-(\d+)/)
    if (match) {
      totalMin += parseInt(match[1])
      totalMax += parseInt(match[2])
    }
  })

  return `${totalMin}-${totalMax} min`
})

function toggleWorkflow(workflow) {
  const index = selectedWorkflows.value.findIndex(w => w.workflow_id === workflow.workflow_id)
  if (index >= 0) {
    selectedWorkflows.value.splice(index, 1)
  } else {
    selectedWorkflows.value.push(workflow)
  }

  emit('update:selectedWorkflows', selectedWorkflows.value)
}

function isSelected(workflow) {
  return selectedWorkflows.value.some(w => w.workflow_id === workflow.workflow_id)
}

function clearSelection() {
  selectedWorkflows.value = []
  emit('update:selectedWorkflows', [])
}
</script>

<style scoped>
.thematic-workflow-selector {
  padding: 1.5rem;
}

.selector-header {
  margin-bottom: 2rem;
}

.selector-header h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-main, #FFF5E6);
  font-size: 1.5rem;
}

.selector-header p {
  margin: 0;
  color: var(--text-muted, #C9B299);
  font-size: 1rem;
}

.workflow-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.workflow-card {
  background: var(--bg-panel, #0A0A0A);
  border: 2px solid var(--border-medium, rgba(255, 255, 255, 0.3));
  border-radius: 12px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.workflow-card:hover {
  transform: translateY(-4px);
  border-color: var(--accent-gold, #FFB347);
  box-shadow: 0 8px 20px rgba(255, 179, 71, 0.3);
}

.workflow-card.selected {
  border-color: var(--accent-gold, #FFB347);
  background: rgba(255, 179, 71, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.workflow-icon {
  font-size: 2.5rem;
}

.card-badge {
  padding: 0.25rem 0.6rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
}

.card-badge.generic {
  background: var(--accent-gold, #FFB347);
  color: var(--bg-panel, #0A0A0A);
}

.workflow-card h4 {
  margin: 0 0 0.5rem 0;
  color: var(--text-main, #FFF5E6);
  font-size: 1.2rem;
}

.description {
  color: var(--text-muted, #C9B299);
  font-size: 0.9rem;
  line-height: 1.5;
  margin-bottom: 1rem;
}

.card-meta {
  display: flex;
  justify-content: space-between;
  padding-top: 1rem;
  border-top: 1px solid var(--border-light, rgba(255, 255, 255, 0.2));
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.85rem;
  color: var(--text-muted, #C9B299);
}

.meta-icon {
  font-size: 0.95rem;
}

.selected-indicator {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: #22c55e;
  color: white;
  padding: 0.4rem 0.9rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.35rem;
}

.check-icon {
  font-size: 1rem;
}

.selection-summary {
  background: var(--bg-panel, #0A0A0A);
  border: 2px solid var(--accent-gold, #FFB347);
  border-radius: 12px;
  padding: 1.5rem;
}

.summary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.summary-header h4 {
  margin: 0;
  color: var(--accent-gold, #FFB347);
  font-size: 1.1rem;
}

.clear-btn {
  background: none;
  border: 1px solid var(--border-medium, rgba(255, 255, 255, 0.3));
  color: var(--text-muted, #C9B299);
  padding: 0.4rem 0.9rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.2s;
}

.clear-btn:hover {
  border-color: var(--accent-orange, #FF8C42);
  color: var(--accent-orange, #FF8C42);
}

.summary-content {
  display: flex;
  gap: 2rem;
}

.summary-stat {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.stat-label {
  color: var(--text-muted, #C9B299);
  font-size: 0.85rem;
}

.stat-value {
  color: var(--text-main, #FFF5E6);
  font-size: 1.3rem;
  font-weight: 700;
}
</style>
