<template>
  <div class="framework-tree">
    <div class="tree-header">
      <h2>{{ framework?.name || 'Framework' }}</h2>
      <button @click="collapseAll" class="btn-secondary">Collapse All</button>
    </div>

    <div v-if="hierarchy" class="tree-root">
      <!-- Framework Level -->
      <div class="tree-node framework-node">
        <div class="node-header" @click="toggleNode('framework')">
          <span class="toggle-icon">{{ isExpanded('framework') ? '▾' : '▸' }}</span>
          <span class="node-icon">📦</span>
          <span class="node-label">{{ hierarchy.name }}</span>
        </div>

        <!-- Phases Level -->
        <div v-show="isExpanded('framework')" class="node-children">
          <div
            v-for="phase in hierarchy.phases"
            :key="phase.phase_id"
            class="tree-node phase-node"
          >
            <div
              class="node-header"
              :class="{ active: currentPhase?.phase_id === phase.phase_id }"
              @click="selectAndToggle(phase, 'phase')"
            >
              <span class="toggle-icon">{{ isExpanded(phase.phase_id) ? '▾' : '▸' }}</span>
              <span class="node-icon">📋</span>
              <span class="node-label">{{ phase.name }}</span>
              <span class="node-badge">{{ phase.workflows?.length || 0 }} workflows</span>
            </div>

            <!-- Workflows Level -->
            <div v-show="isExpanded(phase.phase_id)" class="node-children">
              <div
                v-for="workflow in phase.workflows"
                :key="workflow.workflow_id"
                class="tree-node workflow-node"
              >
                <div
                  class="node-header"
                  :class="{ active: currentWorkflow?.workflow_id === workflow.workflow_id }"
                  @click="selectAndToggle(workflow, 'workflow')"
                >
                  <span class="toggle-icon">{{ isExpanded(workflow.workflow_id) ? '▾' : '▸' }}</span>
                  <span class="node-icon">🔄</span>
                  <span class="node-label">{{ workflow.name }}</span>
                  <span class="node-badge">{{ workflow.techniques?.length || 0 }} techniques</span>
                </div>

                <!-- Techniques Level -->
                <div v-show="isExpanded(workflow.workflow_id)" class="node-children">
                  <div
                    v-for="technique in workflow.techniques"
                    :key="technique.technique_id"
                    class="tree-node technique-node"
                  >
                    <div
                      class="node-header"
                      :class="{ active: currentTechnique?.technique_id === technique.technique_id }"
                      @click="selectTechnique(technique)"
                    >
                      <span class="node-icon">🎯</span>
                      <span class="node-label">{{ technique.name }}</span>
                      <button class="edit-btn" @click.stop="editTechnique(technique)">
                        ✏️ Edit
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="tree-empty">
      <p>No framework selected</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useOrchestratorStore } from '@/stores/orchestrator'
import { storeToRefs } from 'pinia'

const emit = defineEmits(['edit-technique'])

const store = useOrchestratorStore()
const { currentFrameworkHierarchy, currentPhase, currentWorkflow, currentTechnique } = storeToRefs(store)

const props = defineProps({
  framework: {
    type: Object,
    default: null
  }
})

const hierarchy = computed(() => currentFrameworkHierarchy.value)

// Expanded state for each node
const expanded = ref({
  framework: true  // Framework is expanded by default
})

function isExpanded(nodeId) {
  return expanded.value[nodeId] === true
}

function toggleNode(nodeId) {
  expanded.value[nodeId] = !expanded.value[nodeId]
}

function selectAndToggle(item, type) {
  const id = item[`${type}_id`]

  // Select in store
  if (type === 'phase') {
    store.selectPhase(item)
  } else if (type === 'workflow') {
    store.selectWorkflow(item)
  }

  // Toggle expansion
  toggleNode(id)
}

function selectTechnique(technique) {
  store.selectTechnique(technique)
}

function editTechnique(technique) {
  store.selectTechnique(technique)
  emit('edit-technique', technique)
}

function collapseAll() {
  expanded.value = { framework: true }
}
</script>

<style scoped>
.framework-tree {
  height: 100%;
  overflow-y: auto;
  background: var(--bg-sidebar, #6D4C41);
  padding: 1rem;
  border-radius: 10px;
}

.tree-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid var(--accent-gold, #FFB347);
}

.tree-header h2 {
  margin: 0;
  color: var(--accent-gold, #FFB347);
  font-size: 1.3rem;
}

.btn-secondary {
  padding: 0.4rem 0.8rem;
  background: var(--bg-panel, #0A0A0A);
  color: var(--text-light, #F5E6D3);
  border: 1px solid var(--border-medium, rgba(255, 255, 255, 0.3));
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.2s;
}

.btn-secondary:hover {
  border-color: var(--accent-gold, #FFB347);
  transform: translateY(-1px);
}

.tree-root {
  color: var(--text-light, #F5E6D3);
}

.tree-node {
  margin-bottom: 0.3rem;
}

.node-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 0.8rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s ease;
  background: var(--bg-sidebar-el, #8D6E63);
}

.node-header:hover {
  background: rgba(255, 179, 71, 0.15);
  transform: translateX(4px);
}

.node-header.active {
  background: var(--accent-gradient, linear-gradient(90deg, rgba(255, 179, 71, 0.18), rgba(255, 140, 66, 0.06)));
  border-left: 3px solid var(--accent-orange, #FF8C42);
  font-weight: 700;
  box-shadow: 0 0 10px rgba(255, 140, 66, 0.3);
}

.toggle-icon {
  font-size: 0.9rem;
  color: var(--text-muted, #C9B299);
  min-width: 1rem;
  text-align: center;
}

.node-icon {
  font-size: 1.1rem;
}

.node-label {
  flex: 1;
  font-weight: 500;
}

.node-badge {
  font-size: 0.75rem;
  padding: 0.2rem 0.5rem;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 10px;
  color: var(--text-muted, #C9B299);
}

.node-children {
  margin-left: 1.5rem;
  padding-left: 0.5rem;
  border-left: 2px solid rgba(255, 179, 71, 0.2);
  margin-top: 0.3rem;
}

.edit-btn {
  padding: 0.2rem 0.6rem;
  background: var(--accent-orange, #FF8C42);
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.2s;
}

.edit-btn:hover {
  background: var(--accent-strong, #FF8C42);
  transform: scale(1.05);
}

.tree-empty {
  text-align: center;
  padding: 3rem 1rem;
  color: var(--text-muted, #C9B299);
}

/* Specific node styling */
.framework-node > .node-header {
  background: rgba(255, 179, 71, 0.1);
  font-weight: 600;
  border: 2px solid var(--accent-gold, #FFB347);
}

.phase-node > .node-header {
  background: rgba(141, 110, 99, 0.5);
}

.workflow-node > .node-header {
  background: rgba(161, 136, 127, 0.3);
}

.technique-node > .node-header {
  background: rgba(198, 134, 66, 0.2);
}
</style>
