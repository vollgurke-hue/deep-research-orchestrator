<template>
  <div class="dashboard">
    <header class="dashboard-header">
      <h1>🎯 Deep Research Orchestrator</h1>
      <p class="subtitle">Visual Workflow Editor</p>
    </header>

    <div class="status-bar" v-if="!loading">
      <div class="status-item">
        <span class="label">Frameworks:</span>
        <span class="value">{{ frameworks.length }}</span>
      </div>
      <div class="status-item">
        <span class="label">Workflows:</span>
        <span class="value">{{ workflows.length }}</span>
      </div>
      <div class="status-item">
        <span class="label">Techniques:</span>
        <span class="value">{{ techniques.length }}</span>
      </div>
      <button @click="reload" class="reload-btn" :disabled="loading">
        🔄 Reload
      </button>
    </div>

    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>Loading orchestrator data...</p>
    </div>

    <div v-else-if="error" class="error">
      <h3>⚠️ Error</h3>
      <p>{{ error }}</p>
      <button @click="reload">Retry</button>
    </div>

    <div v-else class="frameworks-grid">
      <div
        v-for="framework in frameworks"
        :key="framework.framework_id"
        class="framework-card"
        @click="openEditor(framework)"
      >
        <div class="card-header">
          <h3>{{ framework.name }}</h3>
          <span class="card-icon">📦</span>
        </div>
        <p class="card-description">{{ framework.description }}</p>
        <div class="card-meta">
          <span class="meta-item">
            {{ framework.building_blocks?.length || 0 }} phases
          </span>
          <span class="meta-item">
            {{ framework.metadata?.estimated_total_duration || 'N/A' }}
          </span>
        </div>
      </div>

      <div class="framework-card add-new" @click="createResearch">
        <div class="add-icon">➕</div>
        <p>Create New Research</p>
      </div>

      <div class="framework-card sovereign" @click="openSovereignResearch">
        <div class="card-header">
          <h3>🧠 Sovereign Research</h3>
          <span class="card-icon">⚡</span>
        </div>
        <p class="card-description">Tree of Thoughts • Knowledge Graph • Axiom-Guided Reasoning</p>
        <div class="card-meta">
          <span class="meta-item">NEW</span>
          <span class="meta-item">Sprint 3</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useOrchestratorStore } from '@/stores/orchestrator'
import { storeToRefs } from 'pinia'

const router = useRouter()
const store = useOrchestratorStore()

const { frameworks, workflows, techniques, loading, error } = storeToRefs(store)

onMounted(async () => {
  await store.fetchFrameworks()
  await store.fetchWorkflows()
  await store.fetchTechniques()
})

function openEditor(framework) {
  store.selectFramework(framework)
  router.push('/builder')
}

function createResearch() {
  router.push('/research/create')
}

function openSovereignResearch() {
  router.push('/sovereign')
}

async function reload() {
  await store.reloadOrchestrator()
}
</script>

<style scoped>
.dashboard {
  padding: 2rem;
  min-height: 100vh;
  background: var(--bg-page, #4E342E);
  color: var(--text-main, #FFF5E6);
}

.dashboard-header {
  text-align: center;
  margin-bottom: 3rem;
}

.dashboard-header h1 {
  font-size: 2.5rem;
  margin: 0;
  color: var(--accent-gold, #FFB347);
  text-shadow: 0 0 10px rgba(255, 179, 71, 0.4);
}

.subtitle {
  font-size: 1.1rem;
  color: var(--text-muted, #C9B299);
  margin-top: 0.5rem;
}

.status-bar {
  display: flex;
  gap: 2rem;
  align-items: center;
  justify-content: center;
  margin-bottom: 2rem;
  padding: 1rem;
  background: var(--bg-panel, #0A0A0A);
  border-radius: 10px;
  border: 2px solid var(--accent-gold, #FFB347);
}

.status-item {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.status-item .label {
  color: var(--text-muted, #C9B299);
  font-weight: 600;
}

.status-item .value {
  color: var(--accent-gold, #FFB347);
  font-weight: 700;
  font-size: 1.2rem;
}

.reload-btn {
  padding: 0.5rem 1rem;
  background: var(--accent-orange, #FF8C42);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: transform 0.2s;
}

.reload-btn:hover:not(:disabled) {
  transform: translateY(-2px);
}

.reload-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.loading, .error {
  text-align: center;
  padding: 3rem;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(255, 179, 71, 0.2);
  border-top-color: var(--accent-gold, #FFB347);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.frameworks-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-top: 2rem;
}

.framework-card {
  background: var(--bg-panel, #0A0A0A);
  border: 2px solid var(--border-medium, rgba(255, 255, 255, 0.3));
  border-radius: 12px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.framework-card:hover {
  transform: translateY(-4px);
  border-color: var(--accent-gold, #FFB347);
  box-shadow: 0 8px 20px rgba(255, 179, 71, 0.3);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.card-header h3 {
  margin: 0;
  color: var(--accent-gold, #FFB347);
  font-size: 1.3rem;
}

.card-icon {
  font-size: 2rem;
}

.card-description {
  color: var(--text-light, #F5E6D3);
  margin: 0.5rem 0 1rem;
  line-height: 1.5;
}

.card-meta {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-light, rgba(255, 255, 255, 0.2));
}

.meta-item {
  font-size: 0.9rem;
  color: var(--text-muted, #C9B299);
}

.framework-card.add-new {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 200px;
  border-style: dashed;
  background: rgba(255, 179, 71, 0.05);
}

.add-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  color: var(--accent-gold, #FFB347);
}

.framework-card.add-new p {
  color: var(--text-muted, #C9B299);
  font-weight: 600;
}
</style>
