<template>
  <div class="coverage-panel">
    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading coverage analysis...</p>
    </div>

    <!-- Coverage Data -->
    <div v-else-if="coverageData" class="coverage-content">
      <!-- Overall Coverage Score -->
      <div class="coverage-header">
        <div class="overall-score">
          <div class="score-circle" :style="getScoreStyle(coverageData.overall_coverage)">
            <span class="score-value">{{ Math.round(coverageData.overall_coverage * 100) }}%</span>
          </div>
          <div class="score-label">Overall Coverage</div>
        </div>
      </div>

      <!-- Coverage Heatmap -->
      <div class="section">
        <h3 class="section-title">🎯 Coverage Dimensions</h3>
        <div class="heatmap">
          <div class="heatmap-item">
            <div class="heatmap-label">
              <span class="label-icon">🏷️</span>
              <span class="label-text">Entity Density</span>
            </div>
            <div class="heatmap-bar">
              <div
                class="bar-fill"
                :style="getBarStyle(coverageData.avg_entity_density)"
              ></div>
            </div>
            <div class="heatmap-value">
              {{ Math.round(coverageData.avg_entity_density * 100) }}%
            </div>
            <div :class="['heatmap-status', getCoverageLevel(coverageData.avg_entity_density)]">
              {{ getCoverageLabel(coverageData.avg_entity_density) }}
            </div>
          </div>

          <div class="heatmap-item">
            <div class="heatmap-label">
              <span class="label-icon">🕳️</span>
              <span class="label-text">Exploration Depth</span>
            </div>
            <div class="heatmap-bar">
              <div
                class="bar-fill"
                :style="getBarStyle(coverageData.avg_exploration_depth)"
              ></div>
            </div>
            <div class="heatmap-value">
              {{ Math.round(coverageData.avg_exploration_depth * 100) }}%
            </div>
            <div :class="['heatmap-status', getCoverageLevel(coverageData.avg_exploration_depth)]">
              {{ getCoverageLabel(coverageData.avg_exploration_depth) }}
            </div>
          </div>

          <div class="heatmap-item">
            <div class="heatmap-label">
              <span class="label-icon">⚡</span>
              <span class="label-text">Axiom Coverage</span>
            </div>
            <div class="heatmap-bar">
              <div
                class="bar-fill"
                :style="getBarStyle(coverageData.avg_axiom_coverage)"
              ></div>
            </div>
            <div class="heatmap-value">
              {{ Math.round(coverageData.avg_axiom_coverage * 100) }}%
            </div>
            <div :class="['heatmap-status', getCoverageLevel(coverageData.avg_axiom_coverage)]">
              {{ getCoverageLabel(coverageData.avg_axiom_coverage) }}
            </div>
          </div>
        </div>
      </div>

      <!-- Coverage Gaps -->
      <div v-if="coverageData.gaps_count > 0" class="section">
        <h3 class="section-title">⚠️ Coverage Gaps</h3>
        <div class="gaps-card">
          <div class="gap-count">{{ coverageData.gaps_count }}</div>
          <div class="gap-label">areas need exploration</div>
        </div>
      </div>

      <!-- AI Recommendations -->
      <div v-if="coverageData.recommendations?.length" class="section">
        <h3 class="section-title">💡 AI Recommendations</h3>
        <div class="recommendations-list">
          <div
            v-for="(rec, idx) in coverageData.recommendations"
            :key="idx"
            class="recommendation-item"
          >
            <div class="rec-icon">{{ getRecIcon(rec) }}</div>
            <div class="rec-text">{{ rec }}</div>
          </div>
        </div>
      </div>

      <!-- Top Gaps (if available) -->
      <div v-if="coverageData.top_gaps?.length" class="section">
        <h3 class="section-title">🎯 Priority Gaps</h3>
        <div class="gaps-list">
          <div
            v-for="(gap, idx) in coverageData.top_gaps.slice(0, 3)"
            :key="idx"
            class="gap-item"
          >
            <div class="gap-priority">
              <span class="priority-badge">P{{ idx + 1 }}</span>
              <span class="priority-score">{{ Math.round(gap.priority * 100) }}%</span>
            </div>
            <div class="gap-question">{{ truncate(gap.question, 80) }}</div>
            <div class="gap-coverage">
              Coverage: {{ Math.round(gap.coverage * 100) }}%
            </div>
          </div>
        </div>
      </div>

      <!-- MCTS Control -->
      <div class="section">
        <h3 class="section-title">🎮 Coverage-Guided MCTS</h3>
        <div class="mcts-control">
          <div class="mcts-info">
            <p class="mcts-description">
              Run MCTS to intelligently explore under-covered areas.
              <strong>Adaptive weight: {{ getAdaptiveWeight() }}</strong>
            </p>
          </div>

          <div class="mcts-input">
            <label>Iterations:</label>
            <input
              v-model.number="mctsIterations"
              type="number"
              min="1"
              max="100"
              class="input-iterations"
            />
          </div>

          <button
            @click="runMCTS"
            :disabled="mctsRunning"
            class="btn-run-mcts"
          >
            <span v-if="!mctsRunning">▶️ Run MCTS</span>
            <span v-else>⏳ Running...</span>
          </button>

          <div v-if="mctsResult" class="mcts-result">
            <div class="result-icon">✅</div>
            <div class="result-text">
              MCTS completed {{ mctsResult.iterations_completed }} iterations
            </div>
          </div>
        </div>
      </div>

      <!-- Refresh Button -->
      <button @click="refreshCoverage" class="btn-refresh-coverage" :disabled="loading">
        🔄 Refresh Coverage
      </button>
    </div>

    <!-- Empty State -->
    <div v-else class="empty-state">
      <div class="empty-icon">📊</div>
      <p>No coverage data available</p>
      <button @click="refreshCoverage" class="btn-load-coverage">
        Load Coverage Analysis
      </button>
    </div>

    <!-- Error State -->
    <div v-if="error" class="error-message">
      <span>❌ {{ error }}</span>
      <button @click="clearError" class="btn-close-error">✕</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as api from '@/api/client'

const props = defineProps({
  sessionId: {
    type: String,
    required: true
  }
})

defineEmits(['run-mcts'])

// State
const coverageData = ref(null)
const loading = ref(false)
const error = ref(null)
const mctsIterations = ref(10)
const mctsRunning = ref(false)
const mctsResult = ref(null)

// Load coverage on mount
onMounted(() => {
  loadCoverage()
})

// Actions
async function loadCoverage() {
  loading.value = true
  error.value = null

  try {
    const response = await api.get(`/api/v2/sessions/${props.sessionId}/coverage`)
    coverageData.value = response.data
    console.log('✓ Loaded coverage data:', coverageData.value)
  } catch (err) {
    error.value = err.message || 'Failed to load coverage'
    console.error('Error loading coverage:', err)
  } finally {
    loading.value = false
  }
}

async function refreshCoverage() {
  await loadCoverage()
}

async function runMCTS() {
  mctsRunning.value = true
  mctsResult.value = null
  error.value = null

  try {
    const response = await api.post(`/api/v2/sessions/${props.sessionId}/mcts/coverage-guided`, {
      num_iterations: mctsIterations.value
    })

    mctsResult.value = response.data
    console.log('✓ MCTS completed:', mctsResult.value)

    // Refresh coverage after MCTS
    await loadCoverage()

  } catch (err) {
    error.value = err.message || 'Failed to run MCTS'
    console.error('Error running MCTS:', err)
  } finally {
    mctsRunning.value = false
  }
}

function clearError() {
  error.value = null
}

// Helpers
function getScoreStyle(score) {
  const percentage = score * 100
  const color = getColorForScore(score)
  return {
    background: `conic-gradient(${color} ${percentage}%, #222 ${percentage}%)`
  }
}

function getBarStyle(value) {
  const color = getColorForScore(value)
  return {
    width: `${value * 100}%`,
    background: color
  }
}

function getColorForScore(score) {
  if (score >= 0.7) return '#4CAF50' // Green (High)
  if (score >= 0.4) return '#FFB347' // Gold (Medium)
  return '#FF8C42' // Orange (Low)
}

function getCoverageLevel(score) {
  if (score >= 0.7) return 'high'
  if (score >= 0.4) return 'medium'
  return 'low'
}

function getCoverageLabel(score) {
  if (score >= 0.7) return 'High'
  if (score >= 0.4) return 'Medium'
  return 'Low - Expand!'
}

function getRecIcon(recommendation) {
  if (recommendation.includes('depth')) return '🕳️'
  if (recommendation.includes('gap')) return '⚠️'
  if (recommendation.includes('axiom')) return '⚡'
  if (recommendation.includes('graph')) return '🕸️'
  return '💡'
}

function getAdaptiveWeight() {
  const coverage = coverageData.value?.overall_coverage || 0
  if (coverage < 0.4) return '0.7 (Early - Breadth)'
  if (coverage < 0.7) return '0.5 (Mid - Balanced)'
  return '0.3 (Late - Depth)'
}

function truncate(text, length) {
  if (!text) return ''
  return text.length > length ? text.substring(0, length) + '...' : text
}
</script>

<style scoped>
.coverage-panel {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  height: 100%;
}

/* Loading */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  color: #888;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #333;
  border-top-color: #4CAF50;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Coverage Header */
.coverage-header {
  display: flex;
  justify-content: center;
  padding: 1.5rem 0;
}

.overall-score {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
}

.score-circle {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.score-circle::before {
  content: '';
  position: absolute;
  inset: 8px;
  background: #1a1a1a;
  border-radius: 50%;
}

.score-value {
  position: relative;
  z-index: 1;
  font-size: 2rem;
  font-weight: 700;
  color: #e0e0e0;
}

.score-label {
  font-size: 0.9rem;
  color: #888;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Sections */
.section {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.section-title {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 600;
  color: #aaa;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Heatmap */
.heatmap {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.heatmap-item {
  display: grid;
  grid-template-columns: 1fr 2fr auto auto;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: #222;
  border-radius: 8px;
}

.heatmap-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.label-icon {
  font-size: 1.2rem;
}

.label-text {
  font-size: 0.85rem;
  font-weight: 500;
  color: #e0e0e0;
}

.heatmap-bar {
  height: 12px;
  background: #333;
  border-radius: 6px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  transition: width 0.3s ease;
  border-radius: 6px;
}

.heatmap-value {
  font-size: 0.9rem;
  font-weight: 600;
  color: #e0e0e0;
  min-width: 45px;
  text-align: right;
}

.heatmap-status {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  min-width: 80px;
  text-align: center;
}

.heatmap-status.high {
  background: #4CAF50;
  color: white;
}

.heatmap-status.medium {
  background: #FFB347;
  color: #1a1a1a;
}

.heatmap-status.low {
  background: #FF8C42;
  color: white;
}

/* Gaps */
.gaps-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1.5rem;
  background: #FF8C42;
  border-radius: 8px;
}

.gap-count {
  font-size: 3rem;
  font-weight: 700;
  color: white;
}

.gap-label {
  font-size: 0.9rem;
  color: white;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Recommendations */
.recommendations-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.recommendation-item {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.75rem;
  background: #222;
  border-left: 3px solid #FFB347;
  border-radius: 6px;
}

.rec-icon {
  font-size: 1.2rem;
  flex-shrink: 0;
}

.rec-text {
  flex: 1;
  font-size: 0.9rem;
  color: #e0e0e0;
  line-height: 1.5;
}

/* Priority Gaps */
.gaps-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.gap-item {
  padding: 1rem;
  background: #222;
  border-radius: 8px;
  border: 1px solid #333;
}

.gap-priority {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.priority-badge {
  padding: 0.25rem 0.5rem;
  background: #FF8C42;
  color: white;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 700;
}

.priority-score {
  font-size: 0.85rem;
  color: #888;
}

.gap-question {
  font-size: 0.9rem;
  color: #e0e0e0;
  margin-bottom: 0.5rem;
  line-height: 1.4;
}

.gap-coverage {
  font-size: 0.8rem;
  color: #888;
}

/* MCTS Control */
.mcts-control {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1rem;
  background: #222;
  border-radius: 8px;
  border: 2px solid #4CAF50;
}

.mcts-info {
  font-size: 0.9rem;
  color: #aaa;
  line-height: 1.5;
}

.mcts-info strong {
  color: #4CAF50;
}

.mcts-input {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.mcts-input label {
  font-size: 0.9rem;
  color: #888;
  font-weight: 500;
}

.input-iterations {
  flex: 1;
  padding: 0.5rem;
  background: #1a1a1a;
  border: 1px solid #333;
  border-radius: 6px;
  color: #e0e0e0;
  font-size: 0.9rem;
}

.input-iterations:focus {
  outline: none;
  border-color: #4CAF50;
}

.btn-run-mcts {
  width: 100%;
  padding: 1rem;
  background: linear-gradient(135deg, #4CAF50, #45a049);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-run-mcts:hover:not(:disabled) {
  background: linear-gradient(135deg, #45a049, #3d8b3d);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
}

.btn-run-mcts:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.mcts-result {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: #2a2a2a;
  border-radius: 6px;
}

.result-icon {
  font-size: 1.5rem;
}

.result-text {
  flex: 1;
  font-size: 0.9rem;
  color: #4CAF50;
}

/* Refresh Button */
.btn-refresh-coverage, .btn-load-coverage {
  width: 100%;
  padding: 0.75rem;
  background: #333;
  color: #e0e0e0;
  border: none;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-refresh-coverage:hover:not(:disabled),
.btn-load-coverage:hover {
  background: #444;
  transform: translateY(-2px);
}

.btn-refresh-coverage:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 1rem;
  color: #666;
  text-align: center;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  opacity: 0.3;
}

.empty-state p {
  margin: 0 0 1.5rem 0;
  font-size: 0.95rem;
}

/* Error */
.error-message {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  background: #f44336;
  color: white;
  border-radius: 8px;
  font-size: 0.9rem;
}

.btn-close-error {
  background: transparent;
  border: none;
  color: white;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: background 0.2s;
}

.btn-close-error:hover {
  background: rgba(255, 255, 255, 0.2);
}
</style>
