<template>
  <div class="iteration-viewer">
    <div class="iteration-header">
      <h4>🔄 {{ phaseName }}</h4>
      <span class="iteration-badge">
        Iteration {{ currentIteration }} / {{ maxIterations }}
      </span>
    </div>

    <!-- Iteration History -->
    <div class="iteration-history">
      <div
        v-for="iter in iterationHistory"
        :key="iter.iteration"
        :class="['iteration-item', { active: iter.iteration === currentIteration }]"
      >
        <div class="iteration-header-row">
          <div class="iteration-number">
            <span class="iteration-label">Iteration {{ iter.iteration }}</span>
            <span :class="['status-icon', iter.result]">
              {{ getStatusIcon(iter.result) }}
            </span>
          </div>
          <div class="iteration-meta">
            <span v-if="iter.duration" class="duration">
              {{ formatDuration(iter.duration) }}
            </span>
          </div>
        </div>

        <div class="iteration-details" v-if="iter.iteration === currentIteration || showDetails[iter.iteration]">
          <!-- Techniques Executed -->
          <div class="detail-section">
            <span class="detail-label">Techniques:</span>
            <div class="technique-list">
              <span
                v-for="tech in iter.techniques_executed"
                :key="tech"
                class="technique-tag"
              >
                {{ tech }}
              </span>
            </div>
          </div>

          <!-- Context Info -->
          <div class="detail-section" v-if="iter.context_loaded">
            <span class="detail-label">Context:</span>
            <div class="context-summary">
              <span class="context-item">
                📊 {{ iter.context_loaded.tokens || 0 }} tokens
              </span>
              <span class="context-item" v-if="iter.context_loaded.previous_outputs">
                📤 {{ iter.context_loaded.previous_outputs.length }} previous outputs
              </span>
            </div>
          </div>

          <!-- Gaps Detected -->
          <div class="detail-section" v-if="iter.gaps_detected && iter.gaps_detected.length > 0">
            <span class="detail-label">Gaps Detected:</span>
            <ul class="gaps-list">
              <li v-for="(gap, idx) in iter.gaps_detected" :key="idx">
                {{ gap }}
              </li>
            </ul>
          </div>
        </div>

        <button
          v-if="iter.iteration !== currentIteration"
          @click="toggleDetails(iter.iteration)"
          class="toggle-details-btn"
        >
          {{ showDetails[iter.iteration] ? '▲ Hide' : '▼ Show' }} Details
        </button>
      </div>
    </div>

    <!-- Estimated Remaining -->
    <div class="iteration-estimate" v-if="estimatedRemaining !== null">
      <span class="estimate-label">Estimated Remaining:</span>
      <span class="estimate-value">
        {{ estimatedRemaining === 0 ? 'Completing...' : `${estimatedRemaining} iteration${estimatedRemaining !== 1 ? 's' : ''}` }}
      </span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  iterationState: {
    type: Object,
    required: true
  },
  phaseName: {
    type: String,
    default: 'Phase 1: Excurse'
  }
})

const showDetails = ref({})

const currentIteration = computed(() => props.iterationState?.current_iteration || 1)
const maxIterations = computed(() => props.iterationState?.max_iterations || 5)
const iterationHistory = computed(() => props.iterationState?.iteration_history || [])

const estimatedRemaining = computed(() => {
  const current = currentIteration.value
  const max = maxIterations.value
  const history = iterationHistory.value

  // If last iteration had no gaps, we're done
  if (history.length > 0) {
    const lastIter = history[history.length - 1]
    if (lastIter.result === 'complete' || (lastIter.gaps_detected && lastIter.gaps_detected.length === 0)) {
      return 0
    }
  }

  // Otherwise, estimate based on remaining iterations
  return Math.max(0, max - current)
})

function toggleDetails(iteration) {
  showDetails.value[iteration] = !showDetails.value[iteration]
}

function getStatusIcon(result) {
  const icons = {
    complete: '✅',
    gaps_found: '🔍',
    in_progress: '⏳',
    failed: '❌'
  }
  return icons[result] || '⏳'
}

function formatDuration(durationMs) {
  if (!durationMs) return ''

  const seconds = Math.floor(durationMs / 1000)
  if (seconds < 60) {
    return `${seconds}s`
  }

  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = seconds % 60
  return `${minutes}m ${remainingSeconds}s`
}
</script>

<style scoped>
.iteration-viewer {
  background: var(--bg-panel, #0A0A0A);
  border: 2px solid var(--border-medium, rgba(255, 255, 255, 0.3));
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1rem;
}

.iteration-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.iteration-header h4 {
  margin: 0;
  color: var(--text-main, #FFF5E6);
  font-size: 1.1rem;
}

.iteration-badge {
  background: var(--accent-orange, #FF8C42);
  color: white;
  padding: 0.35rem 0.85rem;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 600;
}

.iteration-history {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.iteration-item {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-light, rgba(255, 255, 255, 0.2));
  border-radius: 8px;
  padding: 0.75rem;
  transition: all 0.3s ease;
}

.iteration-item.active {
  border-color: var(--accent-gold, #FFB347);
  background: rgba(255, 179, 71, 0.1);
}

.iteration-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.iteration-number {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.iteration-label {
  font-weight: 600;
  color: var(--text-light, #F5E6D3);
}

.status-icon {
  font-size: 1.1rem;
}

.status-icon.complete {
  color: #22c55e;
}

.status-icon.gaps_found {
  color: #f59e0b;
}

.status-icon.in_progress {
  color: #3b82f6;
  animation: spin 2s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.iteration-meta {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.duration {
  color: var(--text-muted, #C9B299);
  font-size: 0.85rem;
  font-family: 'Courier New', monospace;
}

.iteration-details {
  border-top: 1px solid var(--border-light, rgba(255, 255, 255, 0.2));
  padding-top: 0.75rem;
  margin-top: 0.75rem;
}

.detail-section {
  margin-bottom: 0.75rem;
}

.detail-section:last-child {
  margin-bottom: 0;
}

.detail-label {
  color: var(--text-muted, #C9B299);
  font-size: 0.85rem;
  font-weight: 600;
  display: block;
  margin-bottom: 0.35rem;
}

.technique-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.technique-tag {
  background: var(--accent-gold, #FFB347);
  color: var(--bg-panel, #0A0A0A);
  padding: 0.25rem 0.6rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 600;
}

.context-summary {
  display: flex;
  gap: 1rem;
}

.context-item {
  color: var(--text-light, #F5E6D3);
  font-size: 0.85rem;
}

.gaps-list {
  margin: 0;
  padding-left: 1.5rem;
  color: var(--text-light, #F5E6D3);
  font-size: 0.9rem;
}

.gaps-list li {
  margin-bottom: 0.25rem;
}

.toggle-details-btn {
  background: none;
  border: none;
  color: var(--accent-gold, #FFB347);
  cursor: pointer;
  font-size: 0.85rem;
  padding: 0.35rem 0;
  margin-top: 0.5rem;
  font-weight: 600;
  transition: color 0.2s;
}

.toggle-details-btn:hover {
  color: var(--accent-orange, #FF8C42);
}

.iteration-estimate {
  padding: 0.75rem 1rem;
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid #3b82f6;
  border-radius: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.estimate-label {
  color: #3b82f6;
  font-weight: 600;
  font-size: 0.9rem;
}

.estimate-value {
  color: var(--text-light, #F5E6D3);
  font-weight: 600;
  font-size: 0.95rem;
}
</style>
