<template>
  <div class="tot-node" :class="[`status-${node.status}`, `depth-${node.depth}`]">
    <!-- Node Header -->
    <div class="node-header" @click="toggleExpanded">
      <div class="node-icon">
        <span v-if="node.status === 'pending'">⏸</span>
        <span v-else-if="node.status === 'exploring'">🔍</span>
        <span v-else-if="node.status === 'evaluated'">✅</span>
        <span v-else-if="node.status === 'pruned'">✂️</span>
      </div>

      <div class="node-content">
        <div class="node-question">{{ node.question }}</div>
        <div class="node-meta">
          <span class="depth">Depth: {{ node.depth }}</span>
          <span class="confidence" v-if="node.confidence > 0">
            Confidence: {{ Math.round(node.confidence * 100) }}%
          </span>
          <span class="visits" v-if="node.visits > 0">
            Visits: {{ node.visits }}
          </span>
          <span class="value" v-if="node.value > 0">
            Value: {{ node.value.toFixed(2) }}
          </span>
        </div>
      </div>

      <div class="node-actions">
        <button
          v-if="node.status === 'pending'"
          @click.stop="$emit('expand', node.node_id)"
          class="btn-expand"
          title="Decompose question with local LLM"
        >
          🌳 Expand
        </button>
        <button
          v-if="node.status === 'pending' || node.status === 'evaluated'"
          @click.stop="$emit('send-external', node.node_id)"
          class="btn-external"
          title="Send to external model (Claude, GPT-4, Gemini)"
        >
          📤 External
        </button>
        <button
          v-if="node.status === 'evaluated'"
          @click.stop="$emit('prune', node.node_id)"
          class="btn-prune"
          title="Prune this branch"
        >
          ✂️ Prune
        </button>
      </div>
    </div>

    <!-- Node Answer (if evaluated) -->
    <div v-if="node.answer && isExpanded" class="node-answer">
      <strong>Answer:</strong>
      <p>{{ node.answer }}</p>
    </div>

    <!-- Axiom Scores -->
    <div v-if="Object.keys(node.axiom_scores || {}).length > 0 && isExpanded" class="axiom-scores">
      <strong>Axiom Alignment:</strong>
      <div class="score-list">
        <div
          v-for="(score, axiomId) in node.axiom_scores"
          :key="axiomId"
          class="score-item"
          :class="getScoreClass(score)"
        >
          <span class="axiom-name">{{ axiomId }}</span>
          <span class="score-value">{{ Math.round(score * 100) }}%</span>
        </div>
      </div>
    </div>

    <!-- Children (Recursive) -->
    <div v-if="children.length > 0" class="node-children">
      <ToTNode
        v-for="child in children"
        :key="child.node_id"
        :node="child"
        :children="getChildren(child.node_id)"
        @expand="$emit('expand', $event)"
        @prune="$emit('prune', $event)"
        @send-external="$emit('send-external', $event)"
      />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  node: {
    type: Object,
    required: true
  },
  children: {
    type: Array,
    default: () => []
  }
})

defineEmits(['expand', 'prune', 'send-external'])

const isExpanded = ref(true)

const toggleExpanded = () => {
  isExpanded.value = !isExpanded.value
}

const getChildren = (nodeId) => {
  return props.children.filter(c => c.parent_id === nodeId)
}

const getScoreClass = (score) => {
  if (score >= 0.7) return 'score-high'
  if (score >= 0.4) return 'score-medium'
  return 'score-low'
}
</script>

<style scoped>
.tot-node {
  margin: 1rem 0;
  padding: 1rem;
  border-left: 3px solid #666;
  background: #1a1a1a;
  border-radius: 4px;
  transition: all 0.2s;
}

.tot-node:hover {
  background: #222;
  border-left-color: #4CAF50;
}

/* Status Colors */
.tot-node.status-pending {
  border-left-color: #FFC107;
}

.tot-node.status-exploring {
  border-left-color: #2196F3;
}

.tot-node.status-evaluated {
  border-left-color: #4CAF50;
}

.tot-node.status-pruned {
  border-left-color: #f44336;
  opacity: 0.5;
}

/* Depth Indentation */
.tot-node.depth-1 {
  margin-left: 0rem;
}

.tot-node.depth-2 {
  margin-left: 2rem;
}

.tot-node.depth-3 {
  margin-left: 4rem;
}

.tot-node.depth-4 {
  margin-left: 6rem;
}

/* Node Header */
.node-header {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  cursor: pointer;
}

.node-icon {
  font-size: 1.5rem;
  min-width: 2rem;
  text-align: center;
}

.node-content {
  flex: 1;
}

.node-question {
  font-size: 1rem;
  font-weight: 600;
  color: #e0e0e0;
  margin-bottom: 0.5rem;
}

.node-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.85rem;
  color: #999;
}

.node-meta span {
  padding: 0.2rem 0.5rem;
  background: #333;
  border-radius: 3px;
}

.confidence {
  color: #4CAF50;
}

.visits {
  color: #2196F3;
}

.value {
  color: #FFC107;
}

/* Node Actions */
.node-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-expand,
.btn-external,
.btn-prune {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.btn-expand {
  background: #4CAF50;
  color: white;
}

.btn-expand:hover {
  background: #45a049;
}

.btn-external {
  background: #2196F3;
  color: white;
}

.btn-external:hover {
  background: #0b7dda;
}

.btn-prune {
  background: #f44336;
  color: white;
}

.btn-prune:hover {
  background: #da190b;
}

/* Node Answer */
.node-answer {
  margin-top: 1rem;
  padding: 1rem;
  background: #2a2a2a;
  border-radius: 4px;
  font-size: 0.9rem;
  color: #ccc;
}

.node-answer p {
  margin: 0.5rem 0 0 0;
}

/* Axiom Scores */
.axiom-scores {
  margin-top: 1rem;
  padding: 1rem;
  background: #2a2a2a;
  border-radius: 4px;
}

.axiom-scores strong {
  display: block;
  margin-bottom: 0.5rem;
  color: #e0e0e0;
}

.score-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.score-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.4rem 0.8rem;
  border-radius: 4px;
  font-size: 0.85rem;
}

.score-item.score-high {
  background: #1b5e20;
  color: #a5d6a7;
}

.score-item.score-medium {
  background: #f57f17;
  color: #fff9c4;
}

.score-item.score-low {
  background: #b71c1c;
  color: #ffcdd2;
}

.axiom-name {
  font-weight: 600;
}

.score-value {
  font-family: monospace;
}

/* Node Children */
.node-children {
  margin-top: 1rem;
}
</style>
