<template>
  <div class="working-state-viewer">
    <div v-if="executionState" class="state-container">
      <!-- Overall Progress Bar -->
      <div class="progress-section">
        <div class="progress-header">
          <span class="progress-label">Overall Progress</span>
          <span class="progress-percentage">{{ executionState.working_state.progress }}%</span>
        </div>
        <div class="progress-bar">
          <div
            class="progress-fill"
            :style="{ width: executionState.working_state.progress + '%' }"
            :class="executionState.working_state.status"
          ></div>
        </div>
      </div>

      <!-- Status Badge -->
      <div class="status-section">
        <div class="status-badge" :class="executionState.working_state.status">
          <span class="status-icon">{{ getStatusIcon(executionState.working_state.status) }}</span>
          <span class="status-text">{{ executionState.working_state.status }}</span>
        </div>
      </div>

      <!-- Current Step -->
      <div class="step-section">
        <h4>Current Step</h4>
        <p class="step-description">{{ executionState.working_state.current_step }}</p>
      </div>

      <!-- Timeline -->
      <div class="timeline-section">
        <h4>Timeline</h4>
        <div class="timeline-info">
          <div class="timeline-item">
            <span class="timeline-label">Started:</span>
            <span class="timeline-value">{{ formatTime(executionState.working_state.started_at) }}</span>
          </div>
          <div class="timeline-item">
            <span class="timeline-label">Last Update:</span>
            <span class="timeline-value">{{ formatTime(executionState.working_state.updated_at) }}</span>
          </div>
          <div class="timeline-item">
            <span class="timeline-label">Duration:</span>
            <span class="timeline-value">{{ calculateDuration(executionState.working_state.started_at, executionState.working_state.updated_at) }}</span>
          </div>
        </div>
      </div>

      <!-- Metadata (if available) -->
      <div v-if="executionState.output?.metadata" class="metadata-section">
        <h4>Execution Metadata</h4>
        <div class="metadata-grid">
          <div class="metadata-item">
            <span class="metadata-label">Model:</span>
            <span class="metadata-value">{{ executionState.output.metadata.model_used || 'N/A' }}</span>
          </div>
          <div class="metadata-item">
            <span class="metadata-label">Tokens:</span>
            <span class="metadata-value">{{ executionState.output.metadata.token_count || 0 }}</span>
          </div>
          <div class="metadata-item">
            <span class="metadata-label">Confidence:</span>
            <span class="metadata-value">
              {{ executionState.output.metadata.confidence_score
                ? (executionState.output.metadata.confidence_score * 100).toFixed(1) + '%'
                : 'N/A' }}
            </span>
          </div>
          <div class="metadata-item">
            <span class="metadata-label">Execution Time:</span>
            <span class="metadata-value">
              {{ executionState.output.metadata.execution_time_ms
                ? executionState.output.metadata.execution_time_ms + 'ms'
                : 'N/A' }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="no-state">
      <p>No execution state available</p>
    </div>
  </div>
</template>

<script setup>
defineProps({
  executionState: {
    type: Object,
    default: null
  }
})

function getStatusIcon(status) {
  const icons = {
    'pending': '⏳',
    'in_progress': '▶️',
    'completed': '✅',
    'failed': '❌'
  }
  return icons[status] || '❓'
}

function formatTime(isoString) {
  if (!isoString) return 'N/A'
  const date = new Date(isoString)
  return date.toLocaleString()
}

function calculateDuration(startTime, endTime) {
  if (!startTime || !endTime) return 'N/A'

  const start = new Date(startTime)
  const end = new Date(endTime)
  const diffMs = end - start

  const seconds = Math.floor(diffMs / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)

  if (hours > 0) {
    return `${hours}h ${minutes % 60}m ${seconds % 60}s`
  } else if (minutes > 0) {
    return `${minutes}m ${seconds % 60}s`
  } else {
    return `${seconds}s`
  }
}
</script>

<style scoped>
.working-state-viewer {
  width: 100%;
}

.state-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.progress-section {
  width: 100%;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  color: var(--text-main);
  font-size: 0.9rem;
}

.progress-label {
  font-weight: 500;
}

.progress-percentage {
  font-weight: 600;
  color: var(--accent-gold);
}

.progress-bar {
  height: 8px;
  background: var(--bg-panel);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--accent-gold);
  transition: width 0.3s ease, background-color 0.3s ease;
  border-radius: 4px;
}

.progress-fill.in_progress {
  background: linear-gradient(90deg, var(--accent-gold), var(--accent-orange));
  animation: shimmer 2s infinite;
}

.progress-fill.completed {
  background: #4CAF50;
}

.progress-fill.failed {
  background: #f44336;
}

@keyframes shimmer {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.status-section {
  display: flex;
  justify-content: center;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: var(--radius-sm);
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.85rem;
}

.status-badge.pending {
  background: rgba(255, 179, 71, 0.2);
  color: var(--accent-gold);
}

.status-badge.in_progress {
  background: rgba(255, 179, 71, 0.3);
  color: var(--accent-orange);
  animation: pulse 2s infinite;
}

.status-badge.completed {
  background: rgba(76, 175, 80, 0.2);
  color: #4CAF50;
}

.status-badge.failed {
  background: rgba(244, 67, 54, 0.2);
  color: #f44336;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

.step-section,
.timeline-section,
.metadata-section {
  background: rgba(255, 255, 255, 0.05);
  padding: 1rem;
  border-radius: var(--radius-sm);
}

.step-section h4,
.timeline-section h4,
.metadata-section h4 {
  margin: 0 0 0.75rem 0;
  color: var(--accent-gold);
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.step-description {
  color: var(--text-main);
  margin: 0;
  font-size: 1rem;
}

.timeline-info {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.timeline-item {
  display: flex;
  justify-content: space-between;
  font-size: 0.9rem;
}

.timeline-label {
  color: var(--text-muted);
}

.timeline-value {
  color: var(--text-main);
  font-weight: 500;
}

.metadata-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

.metadata-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.metadata-label {
  color: var(--text-muted);
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.metadata-value {
  color: var(--text-main);
  font-weight: 600;
  font-size: 1rem;
}

.no-state {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  color: var(--text-muted);
  font-style: italic;
}
</style>
