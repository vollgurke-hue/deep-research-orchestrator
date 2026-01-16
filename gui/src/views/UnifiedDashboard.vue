<template>
  <div class="unified-dashboard">
    <!-- Header -->
    <div class="dashboard-header">
      <div class="header-left">
        <h1>🎯 Research Mission Control</h1>
        <p class="subtitle">Unified Session Management</p>
      </div>
      <div class="header-right">
        <button @click="refreshSessions" class="btn-refresh" :disabled="loading">
          <span v-if="!loading">🔄 Refresh</span>
          <span v-else>⏳ Loading...</span>
        </button>
        <button @click="openCreateModal" class="btn-create">
          ➕ New Session
        </button>
      </div>
    </div>

    <!-- Stats Bar -->
    <div class="stats-bar">
      <div class="stat-item">
        <span class="stat-icon">📦</span>
        <span class="stat-value">{{ sessionStore.stats.total }}</span>
        <span class="stat-label">Total Sessions</span>
      </div>
      <div class="stat-item">
        <span class="stat-icon">🟢</span>
        <span class="stat-value">{{ sessionStore.stats.active }}</span>
        <span class="stat-label">Active</span>
      </div>
      <div class="stat-item">
        <span class="stat-icon">✅</span>
        <span class="stat-value">{{ sessionStore.stats.completed }}</span>
        <span class="stat-label">Completed</span>
      </div>
      <div class="stat-item mode-stat">
        <span class="mode-badge unified">{{ sessionStore.stats.by_mode.unified }}</span>
        <span class="mode-badge tot">{{ sessionStore.stats.by_mode.tot }}</span>
        <span class="mode-badge thematic">{{ sessionStore.stats.by_mode.thematic }}</span>
        <span class="stat-label">By Mode</span>
      </div>
    </div>

    <!-- Main 3-Panel Layout -->
    <div class="dashboard-panels">
      <!-- Left Panel: Session List -->
      <div class="panel panel-left">
        <div class="panel-header">
          <h2>📋 Sessions</h2>
          <div class="panel-tabs">
            <button
              @click="currentTab = 'active'"
              :class="['tab', { active: currentTab === 'active' }]"
            >
              Active ({{ sessionStore.activeSessions.length }})
            </button>
            <button
              @click="currentTab = 'completed'"
              :class="['tab', { active: currentTab === 'completed' }]"
            >
              Completed ({{ sessionStore.completedSessions.length }})
            </button>
            <button
              @click="currentTab = 'all'"
              :class="['tab', { active: currentTab === 'all' }]"
            >
              All ({{ sessionStore.allSessions.length }})
            </button>
          </div>
        </div>

        <div class="panel-content">
          <SessionList
            :sessions="filteredSessions"
            :active-session-id="sessionStore.activeSessionId"
            @select="selectSession"
            @delete="deleteSession"
          />
        </div>
      </div>

      <!-- Center Panel: Session Overview -->
      <div class="panel panel-center">
        <div class="panel-header">
          <h2>📊 Session Overview</h2>
        </div>

        <div class="panel-content">
          <SessionOverview
            v-if="sessionStore.activeSession"
            :session="sessionStore.activeSession"
            @continue="continueSession"
            @export="exportSession"
            @view-graph="viewGraph"
          />

          <div v-else class="no-session-placeholder">
            <div class="placeholder-icon">🔍</div>
            <h3>No Session Selected</h3>
            <p>Select a session from the list or create a new one to get started.</p>
            <button @click="openCreateModal" class="btn-create-large">
              ➕ Create New Session
            </button>
          </div>
        </div>
      </div>

      <!-- Right Panel: Coverage Analysis -->
      <div class="panel panel-right">
        <div class="panel-header">
          <h2>🎯 Coverage Analysis</h2>
        </div>

        <div class="panel-content">
          <CoveragePanel
            v-if="sessionStore.activeSession"
            :session-id="sessionStore.activeSessionId"
            @run-mcts="runMCTS"
          />

          <div v-else class="no-session-placeholder">
            <div class="placeholder-icon">📊</div>
            <p>Coverage analysis will appear when a session is selected.</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Session Creation Wizard -->
    <SessionWizard
      :is-open="showCreateModal"
      @close="closeCreateModal"
      @created="onSessionCreated"
    />

    <!-- Error Display -->
    <div v-if="sessionStore.error" class="error-banner">
      <span>❌ {{ sessionStore.error }}</span>
      <button @click="sessionStore.clearError()" class="btn-close-error">✕</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useSessionsStore } from '@/stores/sessions'

// Components
import SessionList from '@/components/SessionList.vue'
import SessionOverview from '@/components/SessionOverview.vue'
import CoveragePanel from '@/components/CoveragePanel.vue'
import SessionWizard from '@/components/SessionWizard.vue'

const router = useRouter()
const sessionStore = useSessionsStore()

// Local state
const currentTab = ref('active')
const showCreateModal = ref(false)
const loading = ref(false)

// Computed
const filteredSessions = computed(() => {
  switch (currentTab.value) {
    case 'active':
      return sessionStore.activeSessions
    case 'completed':
      return sessionStore.completedSessions
    default:
      return sessionStore.allSessions
  }
})

// Actions
async function refreshSessions() {
  loading.value = true
  try {
    await sessionStore.fetchSessions()
  } catch (err) {
    console.error('Failed to refresh sessions:', err)
  } finally {
    loading.value = false
  }
}

function selectSession(sessionId) {
  sessionStore.selectSession(sessionId)
}

async function deleteSession(sessionId) {
  if (confirm('Are you sure you want to delete this session?')) {
    try {
      await sessionStore.deleteSession(sessionId)
    } catch (err) {
      console.error('Failed to delete session:', err)
    }
  }
}

async function continueSession(sessionId) {
  // TODO: Navigate to research execution view
  console.log('Continue session:', sessionId)
}

async function exportSession(sessionId) {
  try {
    await sessionStore.exportSession(sessionId)
  } catch (err) {
    console.error('Failed to export session:', err)
  }
}

function viewGraph(sessionId) {
  // TODO: Navigate to graph visualization
  console.log('View graph for session:', sessionId)
}

async function runMCTS(sessionId, iterations) {
  try {
    await sessionStore.runCoverageGuidedMCTS(sessionId, iterations)
  } catch (err) {
    console.error('Failed to run MCTS:', err)
  }
}

function openCreateModal() {
  showCreateModal.value = true
}

function closeCreateModal() {
  showCreateModal.value = false
}

async function onSessionCreated(session) {
  console.log('✅ Session created:', session.session_id)

  // Refresh sessions list
  await refreshSessions()

  // Select the newly created session
  sessionStore.setActiveSession(session.session_id)

  // Switch to "active" tab if not already there
  currentTab.value = 'active'
}

// Lifecycle
onMounted(async () => {
  // Load from cache first
  sessionStore.loadFromCache()

  // Then fetch fresh data from API
  await refreshSessions()
})
</script>

<style scoped>
.unified-dashboard {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #0a0a0a;
  color: #e0e0e0;
  overflow: hidden;
}

/* Header */
.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
  border-bottom: 2px solid #333;
}

.header-left h1 {
  margin: 0;
  font-size: 1.8rem;
  font-weight: 700;
  background: linear-gradient(135deg, #4CAF50, #2196F3);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.subtitle {
  margin: 0.25rem 0 0 0;
  font-size: 0.9rem;
  color: #888;
}

.header-right {
  display: flex;
  gap: 1rem;
}

.btn-refresh, .btn-create {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-refresh {
  background: #333;
  color: #e0e0e0;
}

.btn-refresh:hover:not(:disabled) {
  background: #444;
  transform: translateY(-2px);
}

.btn-refresh:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-create {
  background: linear-gradient(135deg, #4CAF50, #45a049);
  color: white;
}

.btn-create:hover {
  background: linear-gradient(135deg, #45a049, #3d8b3d);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
}

/* Stats Bar */
.stats-bar {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  padding: 1.5rem 2rem;
  background: #1a1a1a;
  border-bottom: 1px solid #333;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1rem;
  background: #222;
  border-radius: 8px;
  border: 1px solid #333;
}

.stat-icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: #4CAF50;
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.85rem;
  color: #888;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.mode-stat {
  flex-direction: row;
  gap: 0.5rem;
  flex-wrap: wrap;
  justify-content: center;
}

.mode-badge {
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 600;
  color: white;
}

.mode-badge.unified {
  background: linear-gradient(135deg, #4CAF50, #2196F3);
}

.mode-badge.tot {
  background: #2196F3;
}

.mode-badge.thematic {
  background: #4CAF50;
}

/* Panels */
.dashboard-panels {
  display: grid;
  grid-template-columns: 350px 1fr 400px;
  gap: 1rem;
  padding: 1.5rem 2rem;
  flex: 1;
  overflow: hidden;
}

.panel {
  display: flex;
  flex-direction: column;
  background: #1a1a1a;
  border-radius: 12px;
  border: 1px solid #333;
  overflow: hidden;
}

.panel-header {
  padding: 1.25rem 1.5rem;
  background: #222;
  border-bottom: 1px solid #333;
}

.panel-header h2 {
  margin: 0 0 0.75rem 0;
  font-size: 1.2rem;
  font-weight: 600;
}

.panel-tabs {
  display: flex;
  gap: 0.5rem;
}

.tab {
  padding: 0.5rem 1rem;
  background: transparent;
  border: 1px solid #444;
  border-radius: 6px;
  color: #888;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.tab:hover {
  border-color: #666;
  color: #aaa;
}

.tab.active {
  background: #333;
  border-color: #4CAF50;
  color: #4CAF50;
}

.panel-content {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
}

/* Placeholders */
.no-session-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
  color: #666;
}

.placeholder-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  opacity: 0.3;
}

.no-session-placeholder h3 {
  margin: 0 0 0.5rem 0;
  font-size: 1.3rem;
  color: #888;
}

.no-session-placeholder p {
  margin: 0 0 1.5rem 0;
  color: #666;
}

.btn-create-large {
  padding: 1rem 2rem;
  background: linear-gradient(135deg, #4CAF50, #45a049);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-create-large:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: #1a1a1a;
  border-radius: 12px;
  border: 1px solid #333;
  max-width: 600px;
  width: 90%;
  max-height: 80vh;
  overflow: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #333;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.5rem;
}

.btn-close {
  background: transparent;
  border: none;
  color: #888;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  transition: all 0.2s;
}

.btn-close:hover {
  background: #333;
  color: #fff;
}

.modal-body {
  padding: 1.5rem;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1.5rem;
  border-top: 1px solid #333;
}

.btn-secondary, .btn-primary {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary {
  background: #333;
  color: #e0e0e0;
}

.btn-secondary:hover {
  background: #444;
}

.btn-primary {
  background: linear-gradient(135deg, #4CAF50, #45a049);
  color: white;
}

.btn-primary:hover {
  background: linear-gradient(135deg, #45a049, #3d8b3d);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
}

/* Error Banner */
.error-banner {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  background: #f44336;
  color: white;
  padding: 1rem 1.5rem;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(244, 67, 54, 0.3);
  display: flex;
  align-items: center;
  gap: 1rem;
  z-index: 1001;
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
