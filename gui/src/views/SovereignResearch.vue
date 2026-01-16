<template>
  <div class="sovereign-research">
    <!-- Header -->
    <div class="page-header">
      <div class="title-section">
        <h1>🧠 Sovereign Research Architect</h1>
        <p class="subtitle">Tree of Thoughts • Knowledge Graph • Axiom-Guided Reasoning</p>
      </div>

      <div class="header-actions">
        <button v-if="sessionId" @click="exportSession" class="btn-export">
          💾 Export Session
        </button>
        <button v-if="sessionId" @click="resetSession" class="btn-reset">
          🔄 New Research
        </button>
      </div>
    </div>

    <!-- Main Layout (3 Panels) -->
    <div class="main-layout">
      <!-- Left Panel: ToT Explorer -->
      <div class="panel panel-left">
        <ToTExplorer
          :initial-session-id="sessionId"
          @session-created="handleSessionCreated"
        />
      </div>

      <!-- Center Panel: Graph Viewer -->
      <div class="panel panel-center">
        <GraphViewer
          :graph-data="graphData"
          :focus-entity="focusEntity"
          :loading="graphLoading"
          @node-selected="handleNodeSelected"
          @request-focus="handleFocusRequest"
        />
      </div>

      <!-- Right Panel: Axiom Scorecard -->
      <div class="panel panel-right">
        <AxiomScorecard
          :node="selectedNode"
          :session-id="sessionId"
          :axioms="axioms"
        />
      </div>
    </div>

    <!-- Status Bar -->
    <div class="status-bar">
      <div class="status-item">
        <span class="status-icon">🔬</span>
        <span class="status-text">{{ statusText }}</span>
      </div>

      <div v-if="sessionId" class="status-metrics">
        <span class="metric">Session: {{ sessionId.slice(0, 8) }}</span>
        <span class="metric">Nodes: {{ totalNodes }}</span>
        <span class="metric">Entities: {{ totalEntities }}</span>
        <span class="metric">Axioms: {{ axioms.length }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import ToTExplorer from '@/components/ToTExplorer.vue'
import GraphViewer from '@/components/GraphViewer.vue'
import AxiomScorecard from '@/components/AxiomScorecard.vue'
import apiClient from '@/api/client'

const route = useRoute()

// State
const sessionId = ref(route.query.session || null)
const selectedNode = ref(null)
const focusEntity = ref(null)

const graphData = ref({ nodes: [], edges: [], stats: {} })
const graphLoading = ref(false)

const axioms = ref([])
const totalNodes = ref(0)

const statusText = ref('Ready to start research')

// Computed
const totalEntities = computed(() => graphData.value.nodes.length)

// Methods
const handleSessionCreated = (newSessionId) => {
  sessionId.value = newSessionId
  statusText.value = 'Session created - exploring...'

  // Load axioms
  loadAxioms()

  // Start polling graph
  startGraphPolling()
}

const loadAxioms = async () => {
  try {
    const response = await apiClient.get('/api/sovereign/axioms')
    axioms.value = response.axioms
  } catch (err) {
    console.error('Failed to load axioms:', err)
  }
}

const loadGraph = async () => {
  if (!sessionId.value) return

  try {
    graphLoading.value = true

    const response = await apiClient.get(`/api/sovereign/research/${sessionId.value}/graph`)

    graphData.value = {
      nodes: response.nodes || [],
      edges: response.edges || [],
      stats: response.stats || {}
    }

  } catch (err) {
    console.error('Failed to load graph:', err)
  } finally {
    graphLoading.value = false
  }
}

let graphPollInterval = null

const startGraphPolling = () => {
  // Poll graph every 5 seconds
  graphPollInterval = setInterval(() => {
    loadGraph()
  }, 5000)

  // Load immediately
  loadGraph()
}

const stopGraphPolling = () => {
  if (graphPollInterval) {
    clearInterval(graphPollInterval)
    graphPollInterval = null
  }
}

const handleNodeSelected = (node) => {
  // Convert graph node to ToT-like structure for AxiomScorecard
  selectedNode.value = {
    node_id: node.id,
    question: node.label,
    status: 'evaluated',
    axiom_scores: node.metadata?.axiom_scores || {}
  }

  statusText.value = `Selected entity: ${node.label}`
}

const handleFocusRequest = async (entityId) => {
  focusEntity.value = entityId

  // Reload graph with focus
  try {
    graphLoading.value = true

    const response = await apiClient.get(
      `/api/sovereign/research/${sessionId.value}/graph?focus=${entityId}&depth=2`
    )

    graphData.value = {
      nodes: response.nodes || [],
      edges: response.edges || [],
      stats: response.stats || {}
    }

    statusText.value = `Focused on: ${entityId}`

  } catch (err) {
    console.error('Failed to focus graph:', err)
  } finally {
    graphLoading.value = false
  }
}

const exportSession = async () => {
  try {
    // Export ToT tree + Graph
    const totResponse = await apiClient.get(`/api/sovereign/research/${sessionId.value}/tot-tree`)
    const graphResponse = await apiClient.get(`/api/sovereign/research/${sessionId.value}/graph`)

    const exportData = {
      session_id: sessionId.value,
      timestamp: new Date().toISOString(),
      tot_tree: {
        nodes: totResponse.nodes,
        edges: totResponse.edges
      },
      knowledge_graph: {
        nodes: graphResponse.nodes,
        edges: graphResponse.edges
      },
      axioms: axioms.value
    }

    // Download as JSON
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `sovereign-research-${sessionId.value.slice(0, 8)}.json`
    a.click()
    URL.revokeObjectURL(url)

    statusText.value = 'Session exported successfully'

  } catch (err) {
    console.error('Failed to export session:', err)
    statusText.value = 'Export failed'
  }
}

const resetSession = () => {
  if (confirm('Start new research? Current session will be lost (export first if needed).')) {
    stopGraphPolling()
    sessionId.value = null
    selectedNode.value = null
    focusEntity.value = null
    graphData.value = { nodes: [], edges: [], stats: {} }
    totalNodes.value = 0
    statusText.value = 'Ready to start research'
  }
}

// Lifecycle
onMounted(() => {
  if (sessionId.value) {
    loadAxioms()
    startGraphPolling()
  } else {
    loadAxioms()
  }
})

// Cleanup
import { onBeforeUnmount } from 'vue'
onBeforeUnmount(() => {
  stopGraphPolling()
})
</script>

<style scoped>
.sovereign-research {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #0f0f0f;
  overflow: hidden;
}

/* Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  background: #1a1a1a;
  border-bottom: 2px solid #333;
}

.title-section h1 {
  margin: 0 0 0.5rem 0;
  color: #e0e0e0;
  font-size: 1.8rem;
}

.subtitle {
  margin: 0;
  color: #999;
  font-size: 0.9rem;
}

.header-actions {
  display: flex;
  gap: 1rem;
}

.btn-export,
.btn-reset {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.btn-export {
  background: #4CAF50;
  color: white;
}

.btn-export:hover {
  background: #45a049;
}

.btn-reset {
  background: #f44336;
  color: white;
}

.btn-reset:hover {
  background: #da190b;
}

/* Main Layout (3 Panels) */
.main-layout {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr 1fr 400px;
  gap: 1rem;
  padding: 1rem;
  overflow: hidden;
}

.panel {
  background: #1a1a1a;
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.panel-left {
  overflow-y: auto;
}

.panel-center {
  /* Graph viewer handles its own overflow */
}

.panel-right {
  overflow-y: auto;
}

/* Status Bar */
.status-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 2rem;
  background: #1a1a1a;
  border-top: 1px solid #333;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.status-icon {
  font-size: 1.2rem;
}

.status-text {
  color: #e0e0e0;
  font-size: 0.9rem;
}

.status-metrics {
  display: flex;
  gap: 1.5rem;
}

.metric {
  padding: 0.4rem 0.8rem;
  background: #2a2a2a;
  border-radius: 4px;
  font-size: 0.85rem;
  color: #999;
  font-family: monospace;
}

/* Responsive */
@media (max-width: 1400px) {
  .main-layout {
    grid-template-columns: 1fr 1fr;
    grid-template-rows: 1fr 400px;
  }

  .panel-right {
    grid-column: 1 / -1;
  }
}

@media (max-width: 900px) {
  .main-layout {
    grid-template-columns: 1fr;
    grid-template-rows: auto auto auto;
  }

  .panel-left,
  .panel-center,
  .panel-right {
    height: 500px;
  }
}

/* Scrollbar Styling */
.panel::-webkit-scrollbar {
  width: 8px;
}

.panel::-webkit-scrollbar-track {
  background: #1a1a1a;
}

.panel::-webkit-scrollbar-thumb {
  background: #444;
  border-radius: 4px;
}

.panel::-webkit-scrollbar-thumb:hover {
  background: #555;
}
</style>
