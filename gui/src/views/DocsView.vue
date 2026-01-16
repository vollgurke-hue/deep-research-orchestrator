<template>
  <div class="docs-view">
    <div class="docs-sidebar">
      <div class="sidebar-header">
        <h3>Documentation</h3>
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search docs..."
          class="search-input"
        />
      </div>

      <div class="docs-tree">
        <!-- Main Docs -->
        <div class="tree-section">
          <h4 class="section-title">Main Documentation</h4>
          <div
            v-for="doc in filteredMainDocs"
            :key="doc.path"
            :class="['doc-item', { active: currentDoc === doc.path }]"
            @click="loadDoc(doc.path)"
          >
            <span class="doc-icon">📄</span>
            <span class="doc-name">{{ doc.name }}</span>
          </div>
        </div>

        <!-- Guides -->
        <div class="tree-section">
          <div class="section-header" @click="toggleSection('guides')">
            <span class="toggle-icon">{{ expandedSections.guides ? '▾' : '▸' }}</span>
            <h4 class="section-title">Guides</h4>
          </div>
          <div v-show="expandedSections.guides" class="section-content">
            <div
              v-for="doc in filteredGuides"
              :key="doc.path"
              :class="['doc-item', { active: currentDoc === doc.path }]"
              @click="loadDoc(doc.path)"
            >
              <span class="doc-icon">📖</span>
              <span class="doc-name">{{ doc.name }}</span>
            </div>
          </div>
        </div>

        <!-- Architecture -->
        <div class="tree-section">
          <div class="section-header" @click="toggleSection('architecture')">
            <span class="toggle-icon">{{ expandedSections.architecture ? '▾' : '▸' }}</span>
            <h4 class="section-title">Architecture</h4>
          </div>
          <div v-show="expandedSections.architecture" class="section-content">
            <div
              v-for="doc in filteredArchitecture"
              :key="doc.path"
              :class="['doc-item', { active: currentDoc === doc.path }]"
              @click="loadDoc(doc.path)"
            >
              <span class="doc-icon">🏗️</span>
              <span class="doc-name">{{ doc.name }}</span>
            </div>
          </div>
        </div>

        <!-- Frameworks -->
        <div class="tree-section">
          <div class="section-header" @click="toggleSection('frameworks')">
            <span class="toggle-icon">{{ expandedSections.frameworks ? '▾' : '▸' }}</span>
            <h4 class="section-title">Frameworks</h4>
          </div>
          <div v-show="expandedSections.frameworks" class="section-content">
            <div
              v-for="doc in filteredFrameworks"
              :key="doc.path"
              :class="['doc-item', { active: currentDoc === doc.path }]"
              @click="loadDoc(doc.path)"
            >
              <span class="doc-icon">📦</span>
              <span class="doc-name">{{ doc.name }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="docs-content">
      <div v-if="loading" class="loading-state">
        <span class="loading-icon">⏳</span>
        <p>Loading documentation...</p>
      </div>

      <div v-else-if="error" class="error-state">
        <span class="error-icon">❌</span>
        <p>{{ error }}</p>
      </div>

      <div v-else-if="currentContent" class="markdown-content" v-html="renderedContent"></div>

      <div v-else class="placeholder-state">
        <span class="placeholder-icon">📂</span>
        <h3>Select a document</h3>
        <p>Choose a document from the sidebar to view</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { marked } from 'marked'

const searchQuery = ref('')
const currentDoc = ref(null)
const currentContent = ref(null)
const loading = ref(false)
const error = ref(null)

const expandedSections = ref({
  guides: true,
  architecture: true,
  frameworks: true
})

const mainDocs = ref([
  { name: 'Unified Orchestrator Concept', path: 'docs/UNIFIED_ORCHESTRATOR_CONCEPT.md' },
  { name: 'Vue GUI Implementation Guide', path: 'docs/VUE_GUI_IMPLEMENTATION_GUIDE.md' },
  { name: 'Implementation Guide', path: 'docs/IMPLEMENTATION_GUIDE.md' },
  { name: 'Integration Analysis', path: 'docs/INTEGRATION_ANALYSIS.md' },
  { name: 'Analysis Summary', path: 'docs/ANALYSIS_SUMMARY.md' },
  { name: 'Multi-GPU Testing Plan', path: 'docs/MULTI_GPU_TESTING_PLAN.md' },
  { name: 'Node-Based Pipeline Analysis', path: 'docs/NODE_BASED_PIPELINE_ANALYSIS.md' },
  { name: 'Transfer Checklist', path: 'docs/TRANSFER_CHECKLIST.md' }
])

const guides = ref([])
const architecture = ref([])
const frameworks = ref([])

const filteredMainDocs = computed(() => filterDocs(mainDocs.value))
const filteredGuides = computed(() => filterDocs(guides.value))
const filteredArchitecture = computed(() => filterDocs(architecture.value))
const filteredFrameworks = computed(() => filterDocs(frameworks.value))

const renderedContent = computed(() => {
  if (!currentContent.value) return ''
  return marked(currentContent.value)
})

function filterDocs(docs) {
  if (!searchQuery.value) return docs
  const query = searchQuery.value.toLowerCase()
  return docs.filter(doc => doc.name.toLowerCase().includes(query))
}

function toggleSection(section) {
  expandedSections.value[section] = !expandedSections.value[section]
}

async function loadDoc(path) {
  currentDoc.value = path
  loading.value = true
  error.value = null

  try {
    const response = await fetch(`/api/docs/${path}`)
    if (!response.ok) {
      throw new Error(`Failed to load document: ${response.statusText}`)
    }
    currentContent.value = await response.text()
  } catch (err) {
    error.value = err.message
    currentContent.value = null
  } finally {
    loading.value = false
  }
}

async function fetchDocsList() {
  try {
    const response = await fetch('/api/docs')
    const data = await response.json()

    guides.value = data.guides || []
    architecture.value = data.architecture || []
    frameworks.value = data.frameworks || []
  } catch (err) {
    console.error('Failed to fetch docs list:', err)
  }
}

onMounted(() => {
  fetchDocsList()
  // Load the unified concept by default
  loadDoc('docs/UNIFIED_ORCHESTRATOR_CONCEPT.md')
})
</script>

<style scoped>
.docs-view {
  display: grid;
  grid-template-columns: 300px 1fr;
  height: calc(100vh - 140px);
  background: var(--bg-page);
}

.docs-sidebar {
  background: var(--bg-sidebar);
  border-right: 1px solid var(--border-light);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.sidebar-header {
  padding: 1.5rem;
  border-bottom: 1px solid var(--border-light);
}

.sidebar-header h3 {
  margin: 0 0 1rem 0;
  color: var(--accent-gold);
}

.search-input {
  width: 100%;
  padding: 0.5rem;
  background: var(--bg-panel);
  color: var(--text-main);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-sm);
  font-size: 0.9rem;
}

.search-input::placeholder {
  color: var(--text-muted);
}

.docs-tree {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
}

.tree-section {
  margin-bottom: 1.5rem;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: var(--radius-sm);
  transition: background 0.2s;
}

.section-header:hover {
  background: rgba(255, 255, 255, 0.05);
}

.toggle-icon {
  color: var(--text-muted);
  font-size: 0.8rem;
}

.section-title {
  margin: 0 0 0.75rem 0;
  color: var(--text-light);
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.section-content {
  margin-left: 0.5rem;
}

.doc-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  margin-bottom: 0.25rem;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.2s;
  color: var(--text-main);
}

.doc-item:hover {
  background: rgba(255, 179, 71, 0.15);
  color: var(--accent-gold);
}

.doc-item.active {
  background: var(--accent-gradient);
  color: var(--accent-gold);
  border-left: 3px solid var(--accent-gold);
}

.doc-icon {
  font-size: 1rem;
}

.doc-name {
  font-size: 0.9rem;
  font-weight: 500;
}

.docs-content {
  overflow-y: auto;
  padding: 2rem;
  background: var(--bg-page);
}

.markdown-content {
  max-width: 900px;
  margin: 0 auto;
  color: var(--text-main);
  line-height: 1.7;
}

/* Markdown Styling */
.markdown-content :deep(h1) {
  color: var(--accent-gold);
  border-bottom: 2px solid var(--border-medium);
  padding-bottom: 0.5rem;
  margin-top: 2rem;
  margin-bottom: 1rem;
}

.markdown-content :deep(h2) {
  color: var(--accent-gold);
  margin-top: 1.5rem;
  margin-bottom: 0.75rem;
}

.markdown-content :deep(h3),
.markdown-content :deep(h4) {
  color: var(--text-light);
  margin-top: 1.25rem;
  margin-bottom: 0.5rem;
}

.markdown-content :deep(p) {
  margin-bottom: 1rem;
}

.markdown-content :deep(code) {
  background: var(--bg-code);
  padding: 0.2rem 0.4rem;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
  font-size: 0.9em;
  color: var(--accent-gold);
}

.markdown-content :deep(pre) {
  background: var(--bg-code);
  padding: 1rem;
  border-radius: var(--radius-sm);
  overflow-x: auto;
  margin-bottom: 1rem;
}

.markdown-content :deep(pre code) {
  background: none;
  padding: 0;
}

.markdown-content :deep(ul),
.markdown-content :deep(ol) {
  margin-bottom: 1rem;
  padding-left: 2rem;
}

.markdown-content :deep(li) {
  margin-bottom: 0.5rem;
}

.markdown-content :deep(blockquote) {
  border-left: 4px solid var(--accent-gold);
  padding-left: 1rem;
  margin: 1rem 0;
  color: var(--text-muted);
  font-style: italic;
}

.markdown-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 1rem;
}

.markdown-content :deep(th),
.markdown-content :deep(td) {
  border: 1px solid var(--border-light);
  padding: 0.5rem;
  text-align: left;
}

.markdown-content :deep(th) {
  background: var(--bg-sidebar);
  color: var(--accent-gold);
  font-weight: 600;
}

.loading-state,
.error-state,
.placeholder-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--text-muted);
}

.loading-icon,
.error-icon,
.placeholder-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.placeholder-state h3 {
  color: var(--text-main);
  margin-bottom: 0.5rem;
}
</style>
