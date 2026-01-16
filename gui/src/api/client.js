import axios from 'axios'

const apiClient = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Error handler
apiClient.interceptors.response.use(
  response => response,
  error => {
    console.error('API Error:', error)
    throw error
  }
)

// Frameworks
export async function getFrameworks() {
  const response = await apiClient.get('/frameworks')
  return response.data.frameworks || []
}

export async function getFramework(id) {
  const response = await apiClient.get(`/framework/${id}`)
  return response.data
}

// Phases
export async function getPhases() {
  const response = await apiClient.get('/phases')
  return response.data.phases || []
}

export async function getPhase(id) {
  const response = await apiClient.get(`/phase/${id}`)
  return response.data
}

export async function updatePhase(id, data) {
  const response = await apiClient.patch(`/phase/${id}`, data)
  return response.data
}

// Workflows
export async function getWorkflows() {
  const response = await apiClient.get('/workflows')
  return response.data.workflows || []
}

export async function getWorkflow(id) {
  const response = await apiClient.get(`/workflow/${id}`)
  return response.data
}

export async function updateWorkflow(id, data) {
  const response = await apiClient.patch(`/workflow/${id}`, data)
  return response.data
}

// Techniques
export async function getTechniques() {
  const response = await apiClient.get('/techniques')
  return response.data.techniques || []
}

export async function getTechnique(id) {
  const response = await apiClient.get(`/technique/${id}`)
  return response.data
}

export async function updateTechnique(id, data) {
  const response = await apiClient.patch(`/technique/${id}`, data)
  return response.data
}

// Orchestrator
export async function reloadOrchestrator() {
  const response = await apiClient.post('/orchestrator/reload')
  return response.data
}

export async function getStatus() {
  const response = await apiClient.get('/status')
  return response.data
}

// Research Generation
export async function generateResearchStructure(data) {
  const response = await apiClient.post('/research/generate/structure', data)
  return response.data
}

export async function generateCustomPrompts(data) {
  const response = await apiClient.post('/research/generate/prompts', data)
  return response.data
}

export async function saveResearch(data) {
  const response = await apiClient.post('/research/save', data)
  return response.data
}

// Blindspot Detection
export async function detectBlindspots(data) {
  const response = await apiClient.post('/research/detect-blindspots', data)
  return response.data
}

// Deep Prompt Generation
export async function generateDeepPrompts(data) {
  const response = await apiClient.post('/research/generate-deep-prompts', data)
  return response.data
}

// Theme Expansion (optional)
export async function expandTheme(data) {
  const response = await apiClient.post('/research/expand-theme', data)
  return response.data
}

// Research Session Management (Response Collection)
export async function createResearchSession(data) {
  const response = await apiClient.post('/research/session/create', data)
  return response.data
}

export async function addResponseToSession(sessionId, data) {
  const response = await apiClient.post(`/research/session/${sessionId}/add-response`, data)
  return response.data
}

export async function getResearchSession(sessionId) {
  const response = await apiClient.get(`/research/session/${sessionId}`)
  return response.data
}

// Response Evaluation (direct, no session needed)
export async function evaluateResponse(data) {
  const response = await apiClient.post('/research/evaluate-response', data)
  return response.data
}

// Coverage Analysis (Local analysis of external text response)
export async function analyzeCoverageResponse(data) {
  const response = await apiClient.post('/research/analyze-coverage', data)
  return response.data
}

// Research Input Quality Evaluation
export async function evaluateResearchInputQuality(data) {
  const response = await apiClient.post('/research/evaluate-input-quality', data)
  return response.data
}

// ============================================================================
// SOVEREIGN RESEARCH API (Sprint 3)
// ============================================================================

// Sovereign Research Session
export async function startSovereignResearch(data) {
  const response = await apiClient.post('/sovereign/research/start', data)
  return response.data
}

export async function getSovereignToTTree(sessionId) {
  const response = await apiClient.get(`/sovereign/research/${sessionId}/tot-tree`)
  return response.data
}

export async function getSovereignGraph(sessionId, params = {}) {
  const queryString = new URLSearchParams(params).toString()
  const url = `/sovereign/research/${sessionId}/graph${queryString ? `?${queryString}` : ''}`
  const response = await apiClient.get(url)
  return response.data
}

export async function expandSovereignNode(sessionId, data) {
  const response = await apiClient.post(`/sovereign/research/${sessionId}/expand`, data)
  return response.data
}

export async function pruneSovereignBranch(sessionId, data) {
  const response = await apiClient.post(`/sovereign/research/${sessionId}/prune`, data)
  return response.data
}

export async function runSovereignMCTS(sessionId, data) {
  const response = await apiClient.post(`/sovereign/research/${sessionId}/mcts-step`, data)
  return response.data
}

// Axioms
export async function getSovereignAxioms() {
  const response = await apiClient.get('/sovereign/axioms')
  return response.data
}

export async function evaluateSovereignAxiom(axiomId, data) {
  const response = await apiClient.post(`/sovereign/axioms/${axiomId}/evaluate`, data)
  return response.data
}

export async function addSovereignExternalResponse(sessionId, data) {
  const response = await apiClient.post(`/sovereign/research/${sessionId}/add-response`, data)
  return response.data
}

export default apiClient
