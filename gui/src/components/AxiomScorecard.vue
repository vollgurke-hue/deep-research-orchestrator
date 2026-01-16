<template>
  <div class="axiom-scorecard">
    <div class="scorecard-header">
      <h3>⚖️ Axiom Alignment</h3>
      <button v-if="node" @click="evaluateAll" class="btn-evaluate" :disabled="loading">
        {{ loading ? '⏳ Evaluating...' : '🔄 Re-evaluate All' }}
      </button>
    </div>

    <!-- No Node Selected -->
    <div v-if="!node" class="empty-state">
      <p>Select a ToT node to view axiom alignment</p>
    </div>

    <!-- Node Info -->
    <div v-else class="node-info">
      <div class="info-item">
        <strong>Node:</strong> {{ node.question }}
      </div>
      <div class="info-item">
        <strong>Status:</strong> <span :class="`status-${node.status}`">{{ node.status }}</span>
      </div>
    </div>

    <!-- Axiom Scores -->
    <div v-if="node && scores.length > 0" class="scores-container">
      <div
        v-for="score in scores"
        :key="score.axiom_id"
        class="score-card"
        :class="getScoreClass(score.score)"
      >
        <div class="score-header">
          <div class="axiom-info">
            <h4>{{ score.axiom_id }}</h4>
            <span class="category">{{ score.category }}</span>
            <span class="priority" :class="`priority-${score.priority}`">
              {{ score.priority }}
            </span>
          </div>
          <div class="score-value">
            <span class="score-number">{{ Math.round(score.score * 100) }}%</span>
            <span class="verdict" :class="`verdict-${score.verdict}`">
              {{ score.verdict }}
            </span>
          </div>
        </div>

        <div class="axiom-statement">
          {{ score.statement }}
        </div>

        <div v-if="score.reasoning" class="reasoning">
          <strong>Reasoning:</strong>
          <p>{{ score.reasoning }}</p>
        </div>
      </div>
    </div>

    <!-- No Scores Yet -->
    <div v-else-if="node" class="empty-state">
      <p>No axiom evaluations yet. Click "Re-evaluate All" to assess this node.</p>
    </div>

    <!-- Overall Alignment -->
    <div v-if="node && scores.length > 0" class="overall-alignment">
      <h4>Overall Alignment</h4>
      <div class="alignment-bar">
        <div class="alignment-fill" :style="{ width: `${overallScore}%` }"></div>
      </div>
      <div class="alignment-text">
        {{ overallScore }}% aligned with your values
      </div>

      <div class="verdict-breakdown">
        <div class="verdict-item supports">
          <span class="icon">✅</span>
          <span class="count">{{ verdictCounts.supports }}</span>
          <span class="label">Supports</span>
        </div>
        <div class="verdict-item neutral">
          <span class="icon">➖</span>
          <span class="count">{{ verdictCounts.neutral }}</span>
          <span class="label">Neutral</span>
        </div>
        <div class="verdict-item contradicts">
          <span class="icon">❌</span>
          <span class="count">{{ verdictCounts.contradicts }}</span>
          <span class="label">Contradicts</span>
        </div>
      </div>
    </div>

    <!-- Error Display -->
    <div v-if="error" class="error-message">
      {{ error }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import apiClient from '@/api/client'

const props = defineProps({
  node: {
    type: Object,
    default: null
  },
  sessionId: {
    type: String,
    required: true
  },
  axioms: {
    type: Array,
    default: () => []
  }
})

// State
const scores = ref([])
const loading = ref(false)
const error = ref(null)

// Computed
const overallScore = computed(() => {
  if (scores.value.length === 0) return 0

  const total = scores.value.reduce((sum, s) => sum + s.score, 0)
  return Math.round((total / scores.value.length) * 100)
})

const verdictCounts = computed(() => {
  return {
    supports: scores.value.filter(s => s.verdict === 'supports').length,
    neutral: scores.value.filter(s => s.verdict === 'neutral').length,
    contradicts: scores.value.filter(s => s.verdict === 'contradicts').length
  }
})

// Methods
const getScoreClass = (score) => {
  if (score >= 0.7) return 'score-high'
  if (score >= 0.4) return 'score-medium'
  return 'score-low'
}

const evaluateAll = async () => {
  if (!props.node || !props.sessionId) return

  try {
    loading.value = true
    error.value = null
    scores.value = []

    // Evaluate against each axiom
    const evaluations = []

    for (const axiom of props.axioms) {
      try {
        const result = await apiClient.post(`/api/sovereign/axioms/${axiom.axiom_id}/evaluate`, {
          session_id: props.sessionId,
          node_id: props.node.node_id,
          node_type: 'tot'
        })

        evaluations.push({
          axiom_id: axiom.axiom_id,
          category: axiom.category,
          statement: axiom.statement,
          priority: axiom.priority,
          score: result.score,
          reasoning: result.reasoning,
          verdict: result.verdict
        })
      } catch (err) {
        console.error(`Failed to evaluate ${axiom.axiom_id}:`, err)
      }
    }

    scores.value = evaluations

  } catch (err) {
    error.value = err.message || 'Failed to evaluate axioms'
  } finally {
    loading.value = false
  }
}

const loadScoresFromNode = () => {
  if (!props.node || !props.node.axiom_scores) {
    scores.value = []
    return
  }

  // Load pre-computed scores from node
  scores.value = props.axioms
    .filter(axiom => props.node.axiom_scores[axiom.axiom_id] !== undefined)
    .map(axiom => {
      const score = props.node.axiom_scores[axiom.axiom_id]
      let verdict = 'neutral'
      if (score >= 0.6) verdict = 'supports'
      else if (score < 0.4) verdict = 'contradicts'

      return {
        axiom_id: axiom.axiom_id,
        category: axiom.category,
        statement: axiom.statement,
        priority: axiom.priority,
        score: score,
        reasoning: null,
        verdict: verdict
      }
    })
}

// Watch for node changes
watch(() => props.node, () => {
  loadScoresFromNode()
}, { immediate: true })
</script>

<style scoped>
.axiom-scorecard {
  background: #1a1a1a;
  padding: 1.5rem;
  border-radius: 8px;
  height: 100%;
  overflow-y: auto;
}

/* Header */
.scorecard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #333;
}

.scorecard-header h3 {
  margin: 0;
  color: #e0e0e0;
}

.btn-evaluate {
  padding: 0.6rem 1.2rem;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background 0.2s;
}

.btn-evaluate:hover:not(:disabled) {
  background: #45a049;
}

.btn-evaluate:disabled {
  background: #666;
  cursor: not-allowed;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 2rem;
  color: #999;
}

/* Node Info */
.node-info {
  background: #2a2a2a;
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 1.5rem;
}

.info-item {
  margin: 0.5rem 0;
  color: #ccc;
}

.info-item strong {
  color: #e0e0e0;
}

.status-pending { color: #FFC107; }
.status-exploring { color: #2196F3; }
.status-evaluated { color: #4CAF50; }
.status-pruned { color: #f44336; }

/* Score Cards */
.scores-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 2rem;
}

.score-card {
  background: #2a2a2a;
  padding: 1.5rem;
  border-radius: 8px;
  border-left: 4px solid #666;
  transition: all 0.2s;
}

.score-card:hover {
  background: #333;
}

.score-card.score-high {
  border-left-color: #4CAF50;
}

.score-card.score-medium {
  border-left-color: #FFC107;
}

.score-card.score-low {
  border-left-color: #f44336;
}

.score-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.axiom-info h4 {
  margin: 0 0 0.5rem 0;
  color: #e0e0e0;
}

.category {
  display: inline-block;
  padding: 0.2rem 0.6rem;
  background: #444;
  border-radius: 3px;
  font-size: 0.75rem;
  color: #aaa;
  margin-right: 0.5rem;
}

.priority {
  display: inline-block;
  padding: 0.2rem 0.6rem;
  border-radius: 3px;
  font-size: 0.75rem;
  font-weight: 600;
}

.priority-critical {
  background: #f44336;
  color: white;
}

.priority-high {
  background: #FFC107;
  color: #333;
}

.priority-medium {
  background: #2196F3;
  color: white;
}

.priority-low {
  background: #666;
  color: #ccc;
}

.score-value {
  text-align: right;
}

.score-number {
  display: block;
  font-size: 1.8rem;
  font-weight: 700;
  color: #e0e0e0;
  margin-bottom: 0.3rem;
}

.verdict {
  display: inline-block;
  padding: 0.3rem 0.8rem;
  border-radius: 4px;
  font-size: 0.85rem;
  font-weight: 600;
}

.verdict-supports {
  background: #1b5e20;
  color: #a5d6a7;
}

.verdict-neutral {
  background: #444;
  color: #ccc;
}

.verdict-contradicts {
  background: #b71c1c;
  color: #ffcdd2;
}

.axiom-statement {
  font-size: 0.9rem;
  color: #ccc;
  line-height: 1.5;
  margin-bottom: 1rem;
  font-style: italic;
}

.reasoning {
  background: #1a1a1a;
  padding: 1rem;
  border-radius: 4px;
  font-size: 0.85rem;
}

.reasoning strong {
  display: block;
  margin-bottom: 0.5rem;
  color: #e0e0e0;
}

.reasoning p {
  margin: 0;
  color: #aaa;
  line-height: 1.5;
}

/* Overall Alignment */
.overall-alignment {
  background: #2a2a2a;
  padding: 1.5rem;
  border-radius: 8px;
}

.overall-alignment h4 {
  margin: 0 0 1rem 0;
  color: #e0e0e0;
}

.alignment-bar {
  height: 30px;
  background: #1a1a1a;
  border-radius: 15px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.alignment-fill {
  height: 100%;
  background: linear-gradient(90deg, #f44336, #FFC107, #4CAF50);
  transition: width 0.5s ease;
}

.alignment-text {
  text-align: center;
  font-size: 1.1rem;
  font-weight: 600;
  color: #e0e0e0;
  margin-bottom: 1.5rem;
}

.verdict-breakdown {
  display: flex;
  justify-content: space-around;
  gap: 1rem;
}

.verdict-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.3rem;
}

.verdict-item .icon {
  font-size: 1.5rem;
}

.verdict-item .count {
  font-size: 1.5rem;
  font-weight: 700;
  color: #e0e0e0;
}

.verdict-item .label {
  font-size: 0.85rem;
  color: #999;
}

.verdict-item.supports .count {
  color: #4CAF50;
}

.verdict-item.neutral .count {
  color: #FFC107;
}

.verdict-item.contradicts .count {
  color: #f44336;
}

/* Error Message */
.error-message {
  background: #f44336;
  color: white;
  padding: 1rem;
  border-radius: 4px;
  margin-top: 1rem;
}
</style>
