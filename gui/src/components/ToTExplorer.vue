<template>
  <div class="tot-explorer">
    <!-- Header -->
    <div class="explorer-header">
      <h2>🌳 Tree of Thoughts Explorer</h2>
      <div class="stats">
        <span class="stat">Total Nodes: {{ totalNodes }}</span>
        <span class="stat">Active Leaves: {{ activeLeaves.length }}</span>
        <span class="stat">Depth: {{ maxDepth }}</span>
      </div>
    </div>

    <!-- Question Input (if no session) -->
    <div v-if="!sessionId" class="question-panel">
      <h3>Start New Research</h3>
      <textarea
        v-model="question"
        placeholder="Enter your research question...&#10;&#10;Example: What e-commerce niche should I explore in 2026?"
        rows="4"
      ></textarea>

      <div class="axiom-filters">
        <h4>Select Axioms (optional):</h4>
        <div class="axiom-list">
          <label v-for="axiom in availableAxioms" :key="axiom.axiom_id">
            <input
              type="checkbox"
              :value="axiom.axiom_id"
              v-model="selectedAxioms"
            />
            {{ axiom.axiom_id }} ({{ axiom.priority }})
          </label>
        </div>
      </div>

      <button @click="startResearch" class="btn-start" :disabled="!question.trim()">
        🚀 Start Research
      </button>
    </div>

    <!-- Tree Viewer -->
    <div v-else class="tree-container">
      <div class="tree-toolbar">
        <button @click="refreshTree" class="btn-refresh">
          🔄 Refresh Tree
        </button>
        <button @click="runMCTS" class="btn-mcts">
          🎲 Run MCTS (10 iterations)
        </button>
        <button @click="showBestPath" class="btn-best-path">
          ⭐ Show Best Path
        </button>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="loading">
        <div class="spinner"></div>
        <p>Loading tree...</p>
      </div>

      <!-- Tree Nodes -->
      <div v-else-if="rootNodes.length > 0" class="tree-nodes">
        <ToTNode
          v-for="node in rootNodes"
          :key="node.node_id"
          :node="node"
          :children="getChildren(node.node_id)"
          @expand="handleExpand"
          @prune="handlePrune"
          @send-external="handleSendExternal"
        />
      </div>

      <!-- Empty State -->
      <div v-else class="empty-state">
        <p>No nodes yet. Click "Expand" to decompose the question.</p>
      </div>
    </div>

    <!-- MCTS Results Panel -->
    <div v-if="mctsResults" class="mcts-results">
      <h3>🎲 MCTS Results</h3>
      <div class="result-item">
        <strong>Iterations:</strong> {{ mctsResults.iterations }}
      </div>
      <div class="result-item">
        <strong>Best Value:</strong> {{ mctsResults.best_value.toFixed(2) }}
      </div>
      <div class="result-item">
        <strong>Best Path:</strong>
        <ol>
          <li v-for="nodeId in mctsResults.best_path" :key="nodeId">
            {{ getNodeQuestion(nodeId) }}
          </li>
        </ol>
      </div>
    </div>

    <!-- Error Display -->
    <div v-if="error" class="error-panel">
      <strong>Error:</strong> {{ error }}
      <button @click="error = null" class="btn-close">✕</button>
    </div>

    <!-- External Model Dialog -->
    <ExternalModelDialog
      :is-open="externalDialog.isOpen"
      :node-id="externalDialog.nodeId"
      :external-prompt="externalDialog.prompt"
      @close="externalDialog.isOpen = false"
      @submit="handleExternalSubmit"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import ToTNode from './ToTNode.vue'
import ExternalModelDialog from './ExternalModelDialog.vue'
import apiClient from '@/api/client'

const props = defineProps({
  initialSessionId: {
    type: String,
    default: null
  }
})

const emit = defineEmits(['session-created'])

// State
const sessionId = ref(props.initialSessionId)
const question = ref('')
const selectedAxioms = ref([])
const availableAxioms = ref([])

const nodes = ref([])
const edges = ref([])
const activeLeaves = ref([])

const loading = ref(false)
const error = ref(null)
const mctsResults = ref(null)

const externalDialog = ref({
  isOpen: false,
  nodeId: '',
  prompt: ''
})

// Computed
const rootNodes = computed(() => {
  return nodes.value.filter(n => n.depth === 0)
})

const totalNodes = computed(() => nodes.value.length)

const maxDepth = computed(() => {
  return nodes.value.length > 0
    ? Math.max(...nodes.value.map(n => n.depth))
    : 0
})

// Methods
const loadAxioms = async () => {
  try {
    const response = await apiClient.get('/api/sovereign/axioms')
    availableAxioms.value = response.axioms
  } catch (err) {
    console.error('Failed to load axioms:', err)
  }
}

const startResearch = async () => {
  try {
    loading.value = true
    error.value = null

    const response = await apiClient.post('/api/sovereign/research/start', {
      question: question.value,
      axiom_filters: selectedAxioms.value.length > 0 ? selectedAxioms.value : null
    })

    sessionId.value = response.session_id
    emit('session-created', response.session_id)

    // Load initial tree
    await refreshTree()

  } catch (err) {
    error.value = err.message || 'Failed to start research'
  } finally {
    loading.value = false
  }
}

const refreshTree = async () => {
  if (!sessionId.value) return

  try {
    loading.value = true
    error.value = null

    const response = await apiClient.get(`/api/sovereign/research/${sessionId.value}/tot-tree`)

    nodes.value = response.nodes
    edges.value = response.edges
    activeLeaves.value = response.active_leaves

  } catch (err) {
    error.value = err.message || 'Failed to refresh tree'
  } finally {
    loading.value = false
  }
}

const handleExpand = async (nodeId) => {
  try {
    loading.value = true
    error.value = null

    // Decompose with local LLM
    await apiClient.post(`/api/sovereign/research/${sessionId.value}/expand`, {
      node_id: nodeId,
      method: 'decompose'
    })

    // Refresh tree to show new children
    await refreshTree()

  } catch (err) {
    error.value = err.message || 'Failed to expand node'
  } finally {
    loading.value = false
  }
}

const handlePrune = async (nodeId) => {
  try {
    loading.value = true
    error.value = null

    await apiClient.post(`/api/sovereign/research/${sessionId.value}/prune`, {
      node_id: nodeId,
      reason: 'User decision'
    })

    // Refresh tree to show pruned branch
    await refreshTree()

  } catch (err) {
    error.value = err.message || 'Failed to prune branch'
  } finally {
    loading.value = false
  }
}

const runMCTS = async () => {
  try {
    loading.value = true
    error.value = null

    const response = await apiClient.post(`/api/sovereign/research/${sessionId.value}/mcts-step`, {
      num_steps: 10
    })

    mctsResults.value = response

    // Refresh tree to show updated visit counts & values
    await refreshTree()

  } catch (err) {
    error.value = err.message || 'Failed to run MCTS'
  } finally {
    loading.value = false
  }
}

const showBestPath = () => {
  if (!mctsResults.value) {
    alert('Run MCTS first to find best path')
    return
  }

  // Scroll to highlight best path (TODO: implement highlighting)
  alert(`Best path found with value ${mctsResults.value.best_value.toFixed(2)}`)
}

const getChildren = (nodeId) => {
  return nodes.value.filter(n => n.parent_id === nodeId)
}

const getNodeQuestion = (nodeId) => {
  const node = nodes.value.find(n => n.node_id === nodeId)
  return node ? node.question : nodeId
}

const handleSendExternal = async (nodeId) => {
  try {
    loading.value = true
    error.value = null

    // Request external prompt from server
    const response = await apiClient.post(`/api/sovereign/research/${sessionId.value}/expand`, {
      node_id: nodeId,
      method: 'external',
      external_model: 'claude-opus'
    })

    // Open dialog with generated prompt
    externalDialog.value = {
      isOpen: true,
      nodeId: nodeId,
      prompt: response.prompt
    }

  } catch (err) {
    error.value = err.message || 'Failed to generate external prompt'
  } finally {
    loading.value = false
  }
}

const handleExternalSubmit = async (data) => {
  try {
    // Add external response via API
    const response = await apiClient.post(`/api/sovereign/research/${sessionId.value}/add-response`, data)

    // Refresh tree to show updated node
    await refreshTree()

    // Return response to dialog (for success state)
    return response

  } catch (err) {
    throw new Error(err.message || 'Failed to add external response')
  }
}

// Lifecycle
onMounted(() => {
  loadAxioms()

  if (props.initialSessionId) {
    refreshTree()
  }
})
</script>

<style scoped>
.tot-explorer {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

/* Header */
.explorer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #333;
}

.explorer-header h2 {
  margin: 0;
  color: #e0e0e0;
}

.stats {
  display: flex;
  gap: 1.5rem;
}

.stat {
  padding: 0.5rem 1rem;
  background: #2a2a2a;
  border-radius: 4px;
  font-size: 0.9rem;
  color: #999;
}

/* Question Panel */
.question-panel {
  background: #1a1a1a;
  padding: 2rem;
  border-radius: 8px;
  margin-bottom: 2rem;
}

.question-panel h3 {
  margin-top: 0;
  color: #e0e0e0;
}

.question-panel textarea {
  width: 100%;
  padding: 1rem;
  background: #2a2a2a;
  border: 1px solid #444;
  border-radius: 4px;
  color: #e0e0e0;
  font-family: inherit;
  font-size: 1rem;
  resize: vertical;
}

.axiom-filters {
  margin: 1.5rem 0;
}

.axiom-filters h4 {
  margin-bottom: 0.5rem;
  color: #ccc;
}

.axiom-list {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

.axiom-list label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #ccc;
  cursor: pointer;
}

.axiom-list input[type="checkbox"] {
  cursor: pointer;
}

.btn-start {
  padding: 1rem 2rem;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-start:hover:not(:disabled) {
  background: #45a049;
}

.btn-start:disabled {
  background: #666;
  cursor: not-allowed;
}

/* Tree Container */
.tree-container {
  background: #1a1a1a;
  padding: 2rem;
  border-radius: 8px;
  min-height: 400px;
}

.tree-toolbar {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
}

.tree-toolbar button {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.btn-refresh {
  background: #2196F3;
  color: white;
}

.btn-refresh:hover {
  background: #0b7dda;
}

.btn-mcts {
  background: #FFC107;
  color: #333;
}

.btn-mcts:hover {
  background: #ffb300;
}

.btn-best-path {
  background: #9C27B0;
  color: white;
}

.btn-best-path:hover {
  background: #7b1fa2;
}

/* Loading */
.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem;
  color: #999;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #333;
  border-top-color: #4CAF50;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 4rem;
  color: #999;
}

/* MCTS Results */
.mcts-results {
  background: #1a1a1a;
  padding: 1.5rem;
  border-radius: 8px;
  margin-top: 2rem;
}

.mcts-results h3 {
  margin-top: 0;
  color: #FFC107;
}

.result-item {
  margin: 1rem 0;
  color: #ccc;
}

.result-item strong {
  color: #e0e0e0;
}

.result-item ol {
  margin: 0.5rem 0 0 1.5rem;
  padding: 0;
}

.result-item li {
  margin: 0.3rem 0;
}

/* Error Panel */
.error-panel {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  background: #f44336;
  color: white;
  padding: 1rem 1.5rem;
  border-radius: 4px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  gap: 1rem;
  max-width: 400px;
}

.btn-close {
  background: none;
  border: none;
  color: white;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0;
  line-height: 1;
}
</style>
