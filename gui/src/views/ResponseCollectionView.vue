<template>
  <div class="response-collection">
    <h2>📋 Collect External Model Responses</h2>
    <p class="subtitle">
      Copy each prompt to external AI models (Claude, GPT-4, Gemini), then paste their responses back here for quality evaluation.
    </p>

    <!-- Prompt Navigation Tabs -->
    <div class="prompt-tabs">
      <div
        v-for="(promptData, promptId) in prompts"
        :key="promptId"
        :class="['prompt-tab', { active: currentPromptId === promptId }]"
        @click="selectPrompt(promptId)"
      >
        <span class="tab-title">{{ promptData.prompt_title }}</span>
        <span :class="['response-badge', getPromptStatusClass(promptId)]">
          {{ getResponseCount(promptId) }}/3
        </span>
      </div>
    </div>

    <!-- Current Prompt Display -->
    <div v-if="currentPrompt" class="prompt-display">
      <h3>{{ currentPrompt.prompt_title }}</h3>

      <div class="prompt-meta">
        <span class="meta-tag">~{{ currentPrompt.estimated_tokens }} tokens</span>
        <span class="meta-tag">Priority: {{ currentPrompt.priority }}</span>
      </div>

      <div class="prompt-preview">
        <pre v-if="!showFullPrompt">{{ currentPrompt.comprehensive_prompt.substring(0, 300) }}...</pre>
        <pre v-else>{{ currentPrompt.comprehensive_prompt }}</pre>
      </div>

      <div class="prompt-actions">
        <button @click="toggleFullPrompt" class="btn-secondary">
          {{ showFullPrompt ? '▲ Show Less' : '▼ Show Full Prompt' }}
        </button>
        <button @click="copyPromptToClipboard" class="btn-primary">
          📋 Copy Full Prompt
        </button>
      </div>
    </div>

    <!-- Existing Responses & Evaluations -->
    <div v-if="currentEvaluations && currentEvaluations.length > 0" class="responses-section">
      <h4>Responses Collected: {{ currentEvaluations.length }} / max 3</h4>

      <div
        v-for="(eval, idx) in currentEvaluations"
        :key="idx"
        class="response-card"
      >
        <div class="response-header">
          <span class="model-badge">{{ eval.model_name }}</span>
          <div class="scores">
            <span class="score-badge relevance">
              Relevance: {{ eval.relevance_score }}%
            </span>
            <span class="score-badge accuracy">
              Accuracy: {{ eval.accuracy_score }}%
            </span>
          </div>
        </div>

        <div class="response-details">
          <div class="strengths">
            <strong>Strengths:</strong>
            <ul>
              <li v-for="strength in eval.strengths" :key="strength">{{ strength }}</li>
            </ul>
          </div>
          <div class="weaknesses">
            <strong>Weaknesses:</strong>
            <ul>
              <li v-for="weakness in eval.weaknesses" :key="weakness">{{ weakness }}</li>
            </ul>
          </div>
        </div>
      </div>

      <!-- Aggregate Status -->
      <div v-if="currentAggregate" class="aggregate-status">
        <div :class="['status-indicator', getStatusClass()]">
          <span class="status-icon">{{ getStatusIcon() }}</span>
          <span class="status-text">{{ getStatusText() }}</span>
        </div>

        <div class="aggregate-scores">
          <div class="score-item">
            <span class="label">Average Relevance:</span>
            <span class="value">{{ currentAggregate.avg_relevance }}%</span>
          </div>
          <div class="score-item">
            <span class="label">Average Accuracy:</span>
            <span class="value">{{ currentAggregate.avg_accuracy }}%</span>
          </div>
          <div class="score-item">
            <span class="label">Best Model:</span>
            <span class="value">{{ currentAggregate.best_model }}</span>
          </div>
        </div>

        <div class="recommendation-box">
          💡 {{ currentAggregate.recommendation }}
        </div>
      </div>
    </div>

    <!-- Add Response Form -->
    <div v-if="canAddMoreResponses()" class="add-response-form">
      <h4>+ Add Response from External Model</h4>

      <div class="form-group">
        <label>Model:</label>
        <select v-model="newResponse.model_name" class="input-select">
          <option value="claude-opus">Claude Opus</option>
          <option value="claude-sonnet">Claude Sonnet</option>
          <option value="gpt-4">GPT-4</option>
          <option value="gpt-4-turbo">GPT-4 Turbo</option>
          <option value="gemini-pro">Gemini Pro</option>
          <option value="gemini-ultra">Gemini Ultra</option>
        </select>
      </div>

      <div class="form-group">
        <label>Paste Response:</label>
        <textarea
          v-model="newResponse.response_text"
          rows="10"
          class="input-textarea"
          placeholder="Paste the complete response from the external AI model here..."
        ></textarea>
      </div>

      <div class="form-actions">
        <button
          @click="addResponse"
          :disabled="!newResponse.response_text || adding"
          class="btn-primary"
        >
          {{ adding ? 'Evaluating...' : 'Add & Evaluate Response →' }}
        </button>
      </div>
    </div>

    <!-- Prompt Navigation -->
    <div class="prompt-navigation">
      <button
        @click="previousPrompt"
        :disabled="!hasPreviousPrompt()"
        class="btn-secondary"
      >
        ← Previous Prompt
      </button>

      <div class="progress-info">
        Prompt {{ currentPromptIndex + 1 }} of {{ totalPrompts }}
      </div>

      <button
        @click="nextPrompt"
        :disabled="!hasNextPrompt()"
        class="btn-secondary"
      >
        Next Prompt →
      </button>
    </div>

    <!-- Overall Progress -->
    <div class="overall-progress">
      <div class="progress-bar">
        <div
          class="progress-fill"
          :style="{ width: overallProgressPercent + '%' }"
        ></div>
      </div>
      <div class="progress-text">
        {{ completedPromptsCount }} of {{ totalPrompts }} prompts have at least one response
      </div>
    </div>

    <!-- Step Actions -->
    <div class="step-actions">
      <button @click="goBack" class="btn-secondary">← Back to Prompts</button>
      <button
        @click="proceedToSynthesis"
        :disabled="!canProceedToSynthesis()"
        class="btn-primary"
      >
        Continue to Synthesis →
      </button>
    </div>

    <!-- Success Toast -->
    <div v-if="showSuccessToast" class="success-toast">
      ✅ Response evaluated successfully!
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import * as api from '@/api/client'

const props = defineProps({
  sessionId: {
    type: String,
    required: true
  },
  prompts: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['back', 'next'])

const sessionData = ref(null)
const currentPromptId = ref(null)
const showFullPrompt = ref(false)
const newResponse = ref({ model_name: 'claude-opus', response_text: '' })
const adding = ref(false)
const showSuccessToast = ref(false)
const loading = ref(false)

const promptIds = computed(() => Object.keys(props.prompts))
const totalPrompts = computed(() => promptIds.value.length)

const currentPromptIndex = computed(() => {
  return promptIds.value.indexOf(currentPromptId.value)
})

const currentPrompt = computed(() => {
  return props.prompts[currentPromptId.value]
})

const currentEvaluations = computed(() => {
  if (!sessionData.value || !currentPromptId.value) return []
  return sessionData.value.evaluations?.[currentPromptId.value] || []
})

const currentAggregate = computed(() => {
  if (!sessionData.value || !currentPromptId.value) return null
  return sessionData.value.progress?.[currentPromptId.value]
})

const completedPromptsCount = computed(() => {
  if (!sessionData.value) return 0
  return Object.values(sessionData.value.progress || {}).filter(
    p => p.total_responses > 0
  ).length
})

const overallProgressPercent = computed(() => {
  if (totalPrompts.value === 0) return 0
  return Math.round((completedPromptsCount.value / totalPrompts.value) * 100)
})

onMounted(async () => {
  await loadSessionData()
  // Select first prompt
  if (promptIds.value.length > 0) {
    currentPromptId.value = promptIds.value[0]
  }
})

// Auto-reload session data every 2 seconds when adding
watch(() => adding.value, (isAdding) => {
  if (!isAdding) {
    loadSessionData()
  }
})

async function loadSessionData() {
  loading.value = true
  try {
    sessionData.value = await api.getResearchSession(props.sessionId)
  } catch (error) {
    console.error('Failed to load session:', error)
  } finally {
    loading.value = false
  }
}

function selectPrompt(promptId) {
  currentPromptId.value = promptId
  showFullPrompt.value = false
}

function toggleFullPrompt() {
  showFullPrompt.value = !showFullPrompt.value
}

async function copyPromptToClipboard() {
  try {
    await navigator.clipboard.writeText(currentPrompt.value.comprehensive_prompt)
    showSuccessToast.value = true
    setTimeout(() => {
      showSuccessToast.value = false
    }, 2000)
  } catch (error) {
    console.error('Failed to copy:', error)
    alert('Failed to copy to clipboard')
  }
}

function getResponseCount(promptId) {
  if (!sessionData.value) return 0
  return sessionData.value.progress?.[promptId]?.total_responses || 0
}

function getPromptStatusClass(promptId) {
  const count = getResponseCount(promptId)
  const progress = sessionData.value?.progress?.[promptId]

  if (count === 0) return 'none'
  if (count >= 3) return 'max'
  if (progress && !progress.need_more_models) return 'good'
  return 'partial'
}

function canAddMoreResponses() {
  return currentEvaluations.value.length < 3
}

async function addResponse() {
  if (!newResponse.value.response_text) return

  adding.value = true
  try {
    const result = await api.addResponseToSession(props.sessionId, {
      prompt_id: currentPromptId.value,
      model_name: newResponse.value.model_name,
      response_text: newResponse.value.response_text
    })

    // Update session data immediately with the result
    if (!sessionData.value.evaluations) {
      sessionData.value.evaluations = {}
    }
    if (!sessionData.value.evaluations[currentPromptId.value]) {
      sessionData.value.evaluations[currentPromptId.value] = []
    }

    sessionData.value.evaluations[currentPromptId.value].push(result.evaluation)

    if (!sessionData.value.progress) {
      sessionData.value.progress = {}
    }
    sessionData.value.progress[currentPromptId.value] = result.aggregate

    // Clear form
    newResponse.value.response_text = ''

    // Show success
    showSuccessToast.value = true
    setTimeout(() => {
      showSuccessToast.value = false
    }, 2000)

    // Reload full session data
    await loadSessionData()

  } catch (error) {
    console.error('Failed to add response:', error)
    alert('Failed to add response: ' + error.message)
  } finally {
    adding.value = false
  }
}

function getStatusClass() {
  const agg = currentAggregate.value
  if (!agg || agg.total_responses === 0) return 'none'
  if (agg.total_responses >= 3) return 'max'
  if (!agg.need_more_models) return 'good'
  return 'warning'
}

function getStatusIcon() {
  const statusClass = getStatusClass()
  if (statusClass === 'good') return '✅'
  if (statusClass === 'max') return '🛑'
  if (statusClass === 'warning') return '⚠️'
  return '⏳'
}

function getStatusText() {
  const agg = currentAggregate.value
  if (!agg || agg.total_responses === 0) return 'No responses yet'
  if (agg.total_responses >= 3) return 'Maximum Responses Reached'
  if (!agg.need_more_models) return 'Quality Threshold Met'
  return 'Quality Below Threshold - Add More Models'
}

function hasPreviousPrompt() {
  return currentPromptIndex.value > 0
}

function hasNextPrompt() {
  return currentPromptIndex.value < totalPrompts.value - 1
}

function previousPrompt() {
  if (hasPreviousPrompt()) {
    currentPromptId.value = promptIds.value[currentPromptIndex.value - 1]
    showFullPrompt.value = false
  }
}

function nextPrompt() {
  if (hasNextPrompt()) {
    currentPromptId.value = promptIds.value[currentPromptIndex.value + 1]
    showFullPrompt.value = false
  }
}

function canProceedToSynthesis() {
  // All prompts must have at least one response
  return completedPromptsCount.value === totalPrompts.value
}

function goBack() {
  emit('back')
}

function proceedToSynthesis() {
  emit('next', sessionData.value)
}
</script>

<style scoped>
.response-collection {
  max-width: 1400px;
  margin: 2rem auto;
  padding: 0 2rem;
}

h2 {
  margin: 0 0 0.5rem 0;
  color: var(--text-main);
}

.subtitle {
  color: var(--text-muted);
  margin-bottom: 2rem;
}

/* Prompt Tabs */
.prompt-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 2rem;
  overflow-x: auto;
  padding-bottom: 0.5rem;
}

.prompt-tab {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid var(--border-medium);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.prompt-tab:hover {
  border-color: var(--accent-gold);
}

.prompt-tab.active {
  background: rgba(255, 179, 71, 0.15);
  border-color: var(--accent-gold);
}

.tab-title {
  color: var(--text-main);
  font-weight: 500;
}

.response-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 700;
}

.response-badge.none {
  background: rgba(150, 150, 150, 0.2);
  color: #999;
}

.response-badge.partial {
  background: rgba(234, 179, 8, 0.2);
  color: #eab308;
}

.response-badge.good {
  background: rgba(34, 197, 94, 0.2);
  color: #22c55e;
}

.response-badge.max {
  background: rgba(59, 130, 246, 0.2);
  color: #3b82f6;
}

/* Prompt Display */
.prompt-display {
  background: var(--bg-panel);
  border: 2px solid var(--border-medium);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.prompt-display h3 {
  margin: 0 0 1rem 0;
  color: var(--accent-gold);
}

.prompt-meta {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.meta-tag {
  background: rgba(255, 255, 255, 0.1);
  padding: 0.25rem 0.6rem;
  border-radius: 4px;
  font-size: 0.85rem;
  color: var(--text-muted);
}

.prompt-preview {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
  max-height: 400px;
  overflow: auto;
}

.prompt-preview pre {
  margin: 0;
  color: var(--text-light);
  font-size: 0.9rem;
  line-height: 1.6;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.prompt-actions {
  display: flex;
  gap: 0.75rem;
}

/* Responses Section */
.responses-section {
  margin-bottom: 2rem;
}

.responses-section h4 {
  margin: 0 0 1rem 0;
  color: var(--text-main);
}

.response-card {
  background: rgba(255, 255, 255, 0.03);
  border: 2px solid var(--border-medium);
  border-radius: 10px;
  padding: 1.5rem;
  margin-bottom: 1rem;
}

.response-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.model-badge {
  background: var(--accent-gold);
  color: var(--bg-panel);
  padding: 0.4rem 0.8rem;
  border-radius: 6px;
  font-weight: 700;
  font-size: 0.9rem;
}

.scores {
  display: flex;
  gap: 0.75rem;
}

.score-badge {
  padding: 0.3rem 0.6rem;
  border-radius: 4px;
  font-size: 0.85rem;
  font-weight: 600;
}

.score-badge.relevance {
  background: rgba(59, 130, 246, 0.2);
  color: #3b82f6;
}

.score-badge.accuracy {
  background: rgba(34, 197, 94, 0.2);
  color: #22c55e;
}

.response-details {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

.strengths, .weaknesses {
  color: var(--text-light);
  font-size: 0.9rem;
}

.strengths strong, .weaknesses strong {
  color: var(--text-main);
  display: block;
  margin-bottom: 0.5rem;
}

.strengths ul, .weaknesses ul {
  margin: 0;
  padding-left: 1.5rem;
}

.strengths li, .weaknesses li {
  margin-bottom: 0.25rem;
}

/* Aggregate Status */
.aggregate-status {
  background: rgba(255, 179, 71, 0.1);
  border: 2px solid var(--accent-gold);
  border-radius: 10px;
  padding: 1.5rem;
  margin-top: 1.5rem;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
  padding: 0.75rem;
  border-radius: 6px;
  font-weight: 600;
  font-size: 1.05rem;
}

.status-indicator.good {
  background: rgba(34, 197, 94, 0.15);
  color: #22c55e;
}

.status-indicator.warning {
  background: rgba(234, 179, 8, 0.15);
  color: #eab308;
}

.status-indicator.max {
  background: rgba(59, 130, 246, 0.15);
  color: #3b82f6;
}

.status-icon {
  font-size: 1.3rem;
}

.aggregate-scores {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-bottom: 1rem;
}

.score-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.score-item .label {
  color: var(--text-muted);
  font-size: 0.85rem;
}

.score-item .value {
  color: var(--accent-gold);
  font-weight: 700;
  font-size: 1.1rem;
}

.recommendation-box {
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid #3b82f6;
  border-radius: 6px;
  padding: 1rem;
  color: var(--text-light);
  line-height: 1.5;
}

/* Add Response Form */
.add-response-form {
  background: var(--bg-panel);
  border: 2px solid var(--border-medium);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.add-response-form h4 {
  margin: 0 0 1.5rem 0;
  color: var(--text-main);
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  color: var(--text-muted);
  margin-bottom: 0.5rem;
  font-weight: 600;
}

.input-select {
  width: 100%;
  max-width: 300px;
  padding: 0.75rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-medium);
  border-radius: 8px;
  color: var(--text-main);
  font-size: 1rem;
}

.input-textarea {
  width: 100%;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-medium);
  border-radius: 8px;
  color: var(--text-main);
  font-size: 1rem;
  font-family: inherit;
  resize: vertical;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
}

/* Prompt Navigation */
.prompt-navigation {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
}

.progress-info {
  color: var(--text-muted);
  font-weight: 600;
}

/* Overall Progress */
.overall-progress {
  margin-bottom: 2rem;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.progress-fill {
  height: 100%;
  background: var(--accent-gold);
  transition: width 0.3s;
}

.progress-text {
  color: var(--text-muted);
  font-size: 0.9rem;
  text-align: center;
}

/* Step Actions */
.step-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 2rem;
}

.btn-primary,
.btn-secondary {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: var(--accent-gold);
  color: var(--bg-panel);
}

.btn-primary:hover:not(:disabled) {
  background: var(--accent-orange);
  transform: translateY(-2px);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-light);
  border: 1px solid var(--border-medium);
}

.btn-secondary:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.15);
}

.btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Success Toast */
.success-toast {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  background: rgba(34, 197, 94, 0.95);
  color: white;
  padding: 1rem 1.5rem;
  border-radius: 8px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
  z-index: 1000;
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    transform: translateX(400px);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}
</style>
