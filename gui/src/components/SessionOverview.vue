<template>
  <div class="session-overview">
    <!-- Session Header -->
    <div class="overview-header">
      <div class="header-left">
        <h2 class="session-title">{{ session.title || 'Untitled Session' }}</h2>
        <div class="header-badges">
          <span :class="['mode-badge', session.mode]">
            {{ getModeLabel(session.mode) }}
          </span>
          <span :class="['status-badge', session.status]">
            {{ session.status }}
          </span>
        </div>
      </div>
      <div class="header-actions">
        <button @click="$emit('view-graph', session.session_id)" class="btn-icon" title="View Graph">
          🔍
        </button>
        <button @click="$emit('export', session.session_id)" class="btn-icon" title="Export">
          💾
        </button>
      </div>
    </div>

    <!-- Session Goal -->
    <div class="section">
      <h3 class="section-title">🎯 Research Goal</h3>
      <p class="goal-text">{{ session.goal }}</p>
    </div>

    <!-- Description (if exists) -->
    <div v-if="session.description" class="section">
      <h3 class="section-title">📝 Description</h3>
      <p class="description-text">{{ session.description }}</p>
    </div>

    <!-- Phase Indicator (for unified/tot modes) -->
    <div v-if="session.mode !== 'thematic'" class="section">
      <h3 class="section-title">📍 Current Phase</h3>
      <div class="phase-indicator">
        <div
          v-for="(phase, idx) in phases"
          :key="phase.id"
          :class="['phase-step', { active: isPhaseActive(phase.id), completed: isPhaseCompleted(phase.id) }]"
        >
          <div class="phase-number">{{ idx + 1 }}</div>
          <div class="phase-label">{{ phase.label }}</div>
        </div>
      </div>
    </div>

    <!-- Progress Metrics -->
    <div class="section">
      <h3 class="section-title">📊 Progress Metrics</h3>
      <div class="metrics-grid">
        <!-- ToT Metrics (if available) -->
        <div v-if="session.tot" class="metric-card">
          <div class="metric-icon">🌳</div>
          <div class="metric-content">
            <div class="metric-value">{{ session.tot.total_nodes || 0 }}</div>
            <div class="metric-label">Tree Nodes</div>
          </div>
        </div>

        <!-- Responses -->
        <div class="metric-card">
          <div class="metric-icon">💬</div>
          <div class="metric-content">
            <div class="metric-value">{{ session.responses?.length || 0 }}</div>
            <div class="metric-label">Responses</div>
          </div>
        </div>

        <!-- Knowledge Graph -->
        <div v-if="session.knowledge_graph" class="metric-card">
          <div class="metric-icon">🕸️</div>
          <div class="metric-content">
            <div class="metric-value">{{ session.knowledge_graph.total_nodes || 0 }}</div>
            <div class="metric-label">Graph Nodes</div>
          </div>
        </div>

        <!-- Axioms -->
        <div v-if="session.axioms?.length" class="metric-card">
          <div class="metric-icon">⚡</div>
          <div class="metric-content">
            <div class="metric-value">{{ session.axioms.length }}</div>
            <div class="metric-label">Active Axioms</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Active Axioms (if any) -->
    <div v-if="session.axioms?.length" class="section">
      <h3 class="section-title">⚡ Active Axioms</h3>
      <div class="axioms-list">
        <div v-for="axiom in session.axioms" :key="axiom" class="axiom-chip">
          {{ formatAxiom(axiom) }}
        </div>
      </div>
    </div>

    <!-- Timestamps -->
    <div class="section">
      <h3 class="section-title">🕐 Timeline</h3>
      <div class="timeline">
        <div class="timeline-item">
          <span class="timeline-label">Created:</span>
          <span class="timeline-value">{{ formatDateTime(session.created_at) }}</span>
        </div>
        <div class="timeline-item">
          <span class="timeline-label">Updated:</span>
          <span class="timeline-value">{{ formatDateTime(session.updated_at) }}</span>
        </div>
        <div v-if="session.completed_at" class="timeline-item">
          <span class="timeline-label">Completed:</span>
          <span class="timeline-value">{{ formatDateTime(session.completed_at) }}</span>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="section">
      <h3 class="section-title">⚡ Quick Actions</h3>
      <div class="quick-actions">
        <button
          @click="$emit('continue', session.session_id)"
          class="btn-action btn-primary"
          :disabled="session.status === 'complete'"
        >
          <span v-if="session.status === 'complete'">✅ Completed</span>
          <span v-else>▶️ Continue Research</span>
        </button>
        <button
          @click="$emit('view-graph', session.session_id)"
          class="btn-action btn-secondary"
        >
          🔍 View Knowledge Graph
        </button>
        <button
          @click="$emit('export', session.session_id)"
          class="btn-action btn-secondary"
        >
          💾 Export Session
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  session: {
    type: Object,
    required: true
  }
})

defineEmits(['continue', 'view-graph', 'export'])

// Phase definitions
const phases = [
  { id: 'wizard', label: 'Setup' },
  { id: 'exploring', label: 'Explore' },
  { id: 'validating', label: 'Validate' },
  { id: 'synthesis', label: 'Synthesize' }
]

// Helpers
function getModeLabel(mode) {
  const labels = {
    unified: 'Unified',
    tot: 'Tree of Thoughts',
    thematic: 'Thematic'
  }
  return labels[mode] || mode
}

function isPhaseActive(phaseId) {
  return props.session.status === phaseId
}

function isPhaseCompleted(phaseId) {
  const phaseOrder = ['wizard', 'exploring', 'validating', 'synthesis', 'complete']
  const currentIndex = phaseOrder.indexOf(props.session.status)
  const phaseIndex = phaseOrder.indexOf(phaseId)
  return phaseIndex < currentIndex
}

function formatAxiom(axiom) {
  // Convert snake_case to Title Case
  return axiom
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

function formatDateTime(dateString) {
  if (!dateString) return 'Unknown'

  const date = new Date(dateString)
  return date.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped>
.session-overview {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* Header */
.overview-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding-bottom: 1rem;
  border-bottom: 2px solid #333;
}

.header-left {
  flex: 1;
}

.session-title {
  margin: 0 0 0.75rem 0;
  font-size: 1.5rem;
  font-weight: 700;
  color: #e0e0e0;
}

.header-badges {
  display: flex;
  gap: 0.5rem;
}

.mode-badge, .status-badge {
  padding: 0.35rem 0.75rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.mode-badge {
  color: white;
}

.mode-badge.unified {
  background: linear-gradient(135deg, #4CAF50, #2196F3);
}

.mode-badge.tot {
  background: #2196F3;
}

.mode-badge.thematic {
  background: #4CAF50;
}

.status-badge {
  background: #333;
  color: #FFB347;
}

.status-badge.complete {
  color: #4CAF50;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-icon {
  width: 40px;
  height: 40px;
  background: #333;
  border: none;
  border-radius: 8px;
  font-size: 1.2rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-icon:hover {
  background: #444;
  transform: scale(1.1);
}

/* Sections */
.section {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.section-title {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: #aaa;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.goal-text, .description-text {
  margin: 0;
  font-size: 0.95rem;
  line-height: 1.6;
  color: #e0e0e0;
  background: #222;
  padding: 1rem;
  border-radius: 8px;
  border-left: 3px solid #4CAF50;
}

/* Phase Indicator */
.phase-indicator {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.5rem;
}

.phase-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background: #222;
  border: 2px solid #333;
  border-radius: 8px;
  transition: all 0.2s;
}

.phase-step.active {
  background: #2a2a2a;
  border-color: #FFB347;
}

.phase-step.completed {
  background: #2a2a2a;
  border-color: #4CAF50;
}

.phase-number {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #333;
  border-radius: 50%;
  font-weight: 700;
  color: #888;
}

.phase-step.active .phase-number {
  background: #FFB347;
  color: #1a1a1a;
}

.phase-step.completed .phase-number {
  background: #4CAF50;
  color: white;
}

.phase-label {
  font-size: 0.85rem;
  font-weight: 500;
  color: #888;
  text-align: center;
}

.phase-step.active .phase-label {
  color: #FFB347;
}

.phase-step.completed .phase-label {
  color: #4CAF50;
}

/* Metrics Grid */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 1rem;
}

.metric-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: #222;
  border: 1px solid #333;
  border-radius: 8px;
}

.metric-icon {
  font-size: 2rem;
}

.metric-content {
  flex: 1;
}

.metric-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #4CAF50;
  line-height: 1;
  margin-bottom: 0.25rem;
}

.metric-label {
  font-size: 0.8rem;
  color: #888;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Axioms */
.axioms-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.axiom-chip {
  padding: 0.5rem 1rem;
  background: #2196F3;
  color: white;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 500;
}

/* Timeline */
.timeline {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.timeline-item {
  display: flex;
  justify-content: space-between;
  padding: 0.75rem;
  background: #222;
  border-radius: 6px;
  font-size: 0.9rem;
}

.timeline-label {
  color: #888;
  font-weight: 500;
}

.timeline-value {
  color: #e0e0e0;
}

/* Quick Actions */
.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.btn-action {
  padding: 1rem;
  border: none;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-action:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: linear-gradient(135deg, #4CAF50, #45a049);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: linear-gradient(135deg, #45a049, #3d8b3d);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
}

.btn-secondary {
  background: #333;
  color: #e0e0e0;
}

.btn-secondary:hover {
  background: #444;
  transform: translateY(-2px);
}
</style>
