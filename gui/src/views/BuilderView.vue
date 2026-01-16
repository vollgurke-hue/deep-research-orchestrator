<template>
  <div class="editor-view">
    <div class="editor-sidebar">
      <FrameworkTree
        :framework="currentFramework"
        @edit-technique="onEditTechnique"
      />
    </div>

    <div class="editor-main">
      <div class="editor-mode-toggle">
        <button
          :class="['mode-btn', { active: useTemplateEditor }]"
          @click="useTemplateEditor = true"
        >
          📝 Template Editor
        </button>
        <button
          :class="['mode-btn', { active: !useTemplateEditor }]"
          @click="useTemplateEditor = false"
        >
          📄 Simple Editor
        </button>
      </div>

      <TemplatePromptEditor
        v-if="currentTechnique && useTemplateEditor"
        :technique="currentTechnique"
      />
      <PromptEditor
        v-else-if="currentTechnique && !useTemplateEditor"
      />
      <div v-else class="no-selection">
        <span class="no-selection-icon">🎯</span>
        <h3>No Technique Selected</h3>
        <p>Select a technique from the tree to edit</p>
      </div>
    </div>

    <div class="editor-toolbar">
      <button @click="goBack" class="btn-back">
        ← Back to Dashboard
      </button>
      <button @click="reload" class="btn-reload" :disabled="loading">
        🔄 Reload
      </button>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useOrchestratorStore } from '@/stores/orchestrator'
import { storeToRefs } from 'pinia'
import FrameworkTree from '@/components/FrameworkTree.vue'
import PromptEditor from '@/components/PromptEditor.vue'
import TemplatePromptEditor from '@/components/TemplatePromptEditor.vue'

const router = useRouter()
const store = useOrchestratorStore()

const { currentFramework, currentTechnique, loading } = storeToRefs(store)
const useTemplateEditor = ref(true)

onMounted(async () => {
  // If no framework selected, go back to dashboard
  if (!currentFramework.value) {
    router.push('/')
    return
  }

  // Load full framework with hierarchy
  await store.fetchFramework(currentFramework.value.framework_id)
})

function onEditTechnique(technique) {
  // Technique is already selected in store via FrameworkTree
  // Could add additional actions here (e.g., scroll to editor)
  console.log('Editing technique:', technique.technique_id)
}

function goBack() {
  router.push('/')
}

async function reload() {
  if (currentFramework.value) {
    await store.fetchFramework(currentFramework.value.framework_id)
  }
}
</script>

<style scoped>
.editor-view {
  display: grid;
  grid-template-columns: 400px 1fr;
  grid-template-rows: 1fr auto;
  height: 100vh;
  background: var(--bg-page, #4E342E);
  gap: 1rem;
  padding: 1rem;
}

.editor-sidebar {
  grid-row: 1 / 2;
  grid-column: 1 / 2;
  overflow: hidden;
}

.editor-main {
  grid-row: 1 / 2;
  grid-column: 2 / 3;
  overflow: hidden;
}

.editor-toolbar {
  grid-row: 2 / 3;
  grid-column: 1 / 3;
  display: flex;
  gap: 1rem;
  align-items: center;
  padding: 1rem;
  background: var(--bg-panel, #0A0A0A);
  border-radius: 10px;
  border: 2px solid var(--accent-gold, #FFB347);
}

.btn-back, .btn-reload {
  padding: 0.6rem 1.2rem;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-back {
  background: var(--bg-dark, #A1887F);
  color: white;
}

.btn-back:hover {
  transform: translateY(-2px);
}

.btn-reload {
  background: var(--accent-orange, #FF8C42);
  color: white;
}

.btn-reload:hover:not(:disabled) {
  transform: translateY(-2px);
}

.btn-reload:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.editor-mode-toggle {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  background: var(--bg-sidebar);
  padding: 0.5rem;
  border-radius: var(--radius-sm);
}

.mode-btn {
  flex: 1;
  padding: 0.5rem 1rem;
  background: transparent;
  color: var(--text-muted);
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 500;
}

.mode-btn:hover {
  color: var(--text-main);
  background: rgba(255, 179, 71, 0.1);
}

.mode-btn.active {
  background: var(--accent-gold);
  color: var(--bg-panel);
}

.no-selection {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--text-muted);
}

.no-selection-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.no-selection h3 {
  color: var(--text-main);
  margin-bottom: 0.5rem;
}
</style>
