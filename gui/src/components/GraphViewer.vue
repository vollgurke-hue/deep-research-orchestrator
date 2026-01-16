<template>
  <div class="graph-viewer">
    <div class="viewer-header">
      <h3>🌐 Knowledge Graph</h3>
      <div class="controls">
        <button @click="zoomIn" class="btn-control">➕</button>
        <button @click="zoomOut" class="btn-control">➖</button>
        <button @click="resetView" class="btn-control">🔄</button>
        <select v-model="colorBy" @change="updateColors" class="select-control">
          <option value="type">Color by Type</option>
          <option value="axiom">Color by Axiom</option>
          <option value="confidence">Color by Confidence</option>
        </select>
      </div>
    </div>

    <!-- Stats -->
    <div class="stats">
      <span class="stat">Nodes: {{ graphData?.nodes?.length || 0 }}</span>
      <span class="stat">Edges: {{ graphData?.edges?.length || 0 }}</span>
      <span v-if="selectedNode" class="stat selected">
        Selected: {{ selectedNode.label }}
      </span>
    </div>

    <!-- SVG Canvas -->
    <div class="canvas-container">
      <svg ref="svgRef" class="graph-canvas"></svg>
    </div>

    <!-- Node Details Panel -->
    <div v-if="selectedNode" class="node-details">
      <div class="details-header">
        <h4>{{ selectedNode.label }}</h4>
        <button @click="selectedNode = null" class="btn-close">✕</button>
      </div>

      <div class="detail-item">
        <strong>Type:</strong> {{ selectedNode.type }}
      </div>

      <div v-if="selectedNode.metadata" class="metadata">
        <strong>Metadata:</strong>
        <pre>{{ JSON.stringify(selectedNode.metadata, null, 2) }}</pre>
      </div>

      <div class="actions">
        <button @click="focusNode(selectedNode.id)" class="btn-action">
          🎯 Focus on this node
        </button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="loading-overlay">
      <div class="spinner"></div>
      <p>Loading graph...</p>
    </div>

    <!-- Empty State -->
    <div v-if="!loading && (!graphData || graphData.nodes.length === 0)" class="empty-state">
      <p>No graph data yet. Start exploring to build the knowledge graph.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'
import * as d3 from 'd3'

const props = defineProps({
  graphData: {
    type: Object,
    default: () => ({ nodes: [], edges: [], stats: {} })
  },
  focusEntity: {
    type: String,
    default: null
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['node-selected', 'request-focus'])

// Refs
const svgRef = ref(null)
const selectedNode = ref(null)
const colorBy = ref('type')

// D3 State
let simulation = null
let svg = null
let g = null
let zoom = null

// Methods
const initGraph = () => {
  if (!svgRef.value) return

  const container = svgRef.value.parentElement
  const width = container.clientWidth
  const height = container.clientHeight

  // Clear existing
  d3.select(svgRef.value).selectAll('*').remove()

  // Setup SVG
  svg = d3.select(svgRef.value)
    .attr('width', width)
    .attr('height', height)

  // Zoom behavior
  zoom = d3.zoom()
    .scaleExtent([0.1, 4])
    .on('zoom', (event) => {
      g.attr('transform', event.transform)
    })

  svg.call(zoom)

  // Container for graph elements
  g = svg.append('g')

  // Force simulation
  simulation = d3.forceSimulation()
    .force('link', d3.forceLink().id(d => d.id).distance(100))
    .force('charge', d3.forceManyBody().strength(-300))
    .force('center', d3.forceCenter(width / 2, height / 2))
    .force('collision', d3.forceCollide().radius(30))
}

const updateGraph = () => {
  if (!g || !simulation) return
  if (!props.graphData || props.graphData.nodes.length === 0) return

  // Clear previous graph
  g.selectAll('*').remove()

  // Prepare data
  const nodes = props.graphData.nodes.map(n => ({ ...n }))
  const links = props.graphData.edges.map(e => ({
    source: e.source,
    target: e.target,
    relation: e.relation,
    confidence: e.confidence || 1.0
  }))

  // Draw edges
  const link = g.append('g')
    .attr('class', 'links')
    .selectAll('line')
    .data(links)
    .enter()
    .append('line')
    .attr('stroke', '#666')
    .attr('stroke-width', d => Math.max(1, d.confidence * 3))
    .attr('stroke-opacity', 0.6)

  // Draw edge labels
  const linkLabel = g.append('g')
    .attr('class', 'link-labels')
    .selectAll('text')
    .data(links)
    .enter()
    .append('text')
    .attr('font-size', 10)
    .attr('fill', '#999')
    .text(d => d.relation)

  // Draw nodes
  const node = g.append('g')
    .attr('class', 'nodes')
    .selectAll('g')
    .data(nodes)
    .enter()
    .append('g')
    .attr('class', 'node')
    .call(d3.drag()
      .on('start', dragstarted)
      .on('drag', dragged)
      .on('end', dragended))
    .on('click', (event, d) => {
      selectedNode.value = d
      emit('node-selected', d)
    })

  // Node circles
  node.append('circle')
    .attr('r', 10)
    .attr('fill', d => getNodeColor(d))
    .attr('stroke', '#fff')
    .attr('stroke-width', 2)

  // Node labels
  node.append('text')
    .attr('dx', 15)
    .attr('dy', 5)
    .attr('font-size', 12)
    .attr('fill', '#e0e0e0')
    .text(d => d.label)

  // Update simulation
  simulation.nodes(nodes)
  simulation.force('link').links(links)

  simulation.on('tick', () => {
    link
      .attr('x1', d => d.source.x)
      .attr('y1', d => d.source.y)
      .attr('x2', d => d.target.x)
      .attr('y2', d => d.target.y)

    linkLabel
      .attr('x', d => (d.source.x + d.target.x) / 2)
      .attr('y', d => (d.source.y + d.target.y) / 2)

    node.attr('transform', d => `translate(${d.x},${d.y})`)
  })

  simulation.alpha(1).restart()
}

const getNodeColor = (node) => {
  if (colorBy.value === 'type') {
    const colors = {
      'entity': '#4CAF50',
      'concept': '#2196F3',
      'fact': '#FFC107',
      'question': '#9C27B0'
    }
    return colors[node.type] || '#666'
  } else if (colorBy.value === 'confidence') {
    const confidence = node.metadata?.confidence || 0.5
    return d3.interpolateRdYlGn(confidence)
  } else if (colorBy.value === 'axiom') {
    // Color by axiom alignment (if available)
    const score = node.metadata?.axiom_score || 0.5
    return d3.interpolateRdYlGn(score)
  }
  return '#666'
}

const updateColors = () => {
  if (!g) return

  g.selectAll('.node circle')
    .transition()
    .duration(500)
    .attr('fill', d => getNodeColor(d))
}

const zoomIn = () => {
  if (!svg || !zoom) return
  svg.transition().call(zoom.scaleBy, 1.3)
}

const zoomOut = () => {
  if (!svg || !zoom) return
  svg.transition().call(zoom.scaleBy, 0.7)
}

const resetView = () => {
  if (!svg || !zoom) return
  const container = svgRef.value.parentElement
  const width = container.clientWidth
  const height = container.clientHeight

  svg.transition()
    .duration(750)
    .call(zoom.transform, d3.zoomIdentity.translate(width / 2, height / 2).scale(1))
}

const focusNode = (nodeId) => {
  emit('request-focus', nodeId)
}

// Drag handlers
function dragstarted(event, d) {
  if (!event.active) simulation.alphaTarget(0.3).restart()
  d.fx = d.x
  d.fy = d.y
}

function dragged(event, d) {
  d.fx = event.x
  d.fy = event.y
}

function dragended(event, d) {
  if (!event.active) simulation.alphaTarget(0)
  d.fx = null
  d.fy = null
}

// Lifecycle
onMounted(() => {
  nextTick(() => {
    initGraph()
    if (props.graphData && props.graphData.nodes.length > 0) {
      updateGraph()
    }
  })
})

watch(() => props.graphData, () => {
  nextTick(() => {
    updateGraph()
  })
}, { deep: true })

watch(() => props.focusEntity, (entityId) => {
  if (entityId && props.graphData) {
    const node = props.graphData.nodes.find(n => n.id === entityId)
    if (node) {
      selectedNode.value = node
    }
  }
})
</script>

<style scoped>
.graph-viewer {
  background: #1a1a1a;
  border-radius: 8px;
  height: 100%;
  display: flex;
  flex-direction: column;
  position: relative;
}

/* Header */
.viewer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 2px solid #333;
}

.viewer-header h3 {
  margin: 0;
  color: #e0e0e0;
}

.controls {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.btn-control {
  padding: 0.5rem 1rem;
  background: #2a2a2a;
  color: #e0e0e0;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: background 0.2s;
}

.btn-control:hover {
  background: #3a3a3a;
}

.select-control {
  padding: 0.5rem;
  background: #2a2a2a;
  color: #e0e0e0;
  border: 1px solid #444;
  border-radius: 4px;
  cursor: pointer;
}

/* Stats */
.stats {
  display: flex;
  gap: 1rem;
  padding: 0.75rem 1rem;
  background: #2a2a2a;
  border-bottom: 1px solid #333;
}

.stat {
  font-size: 0.9rem;
  color: #999;
}

.stat.selected {
  color: #4CAF50;
  font-weight: 600;
}

/* Canvas */
.canvas-container {
  flex: 1;
  position: relative;
  overflow: hidden;
}

.graph-canvas {
  width: 100%;
  height: 100%;
  background: #0f0f0f;
}

/* Node Details */
.node-details {
  position: absolute;
  top: 4rem;
  right: 1rem;
  width: 300px;
  background: #2a2a2a;
  border: 1px solid #444;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 4px 12px rgba(0,0,0,0.5);
  z-index: 10;
}

.details-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #444;
}

.details-header h4 {
  margin: 0;
  color: #e0e0e0;
}

.btn-close {
  background: none;
  border: none;
  color: #999;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0;
  line-height: 1;
}

.btn-close:hover {
  color: #e0e0e0;
}

.detail-item {
  margin: 0.75rem 0;
  color: #ccc;
}

.detail-item strong {
  color: #e0e0e0;
}

.metadata {
  margin: 0.75rem 0;
}

.metadata strong {
  display: block;
  margin-bottom: 0.5rem;
  color: #e0e0e0;
}

.metadata pre {
  background: #1a1a1a;
  padding: 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  color: #999;
  overflow-x: auto;
}

.actions {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #444;
}

.btn-action {
  width: 100%;
  padding: 0.75rem;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background 0.2s;
}

.btn-action:hover {
  background: #45a049;
}

/* Loading */
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(26, 26, 26, 0.9);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 5;
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

.loading-overlay p {
  margin-top: 1rem;
  color: #999;
}

/* Empty State */
.empty-state {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  color: #999;
  padding: 2rem;
}
</style>
