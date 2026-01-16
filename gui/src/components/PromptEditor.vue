<template>
  <div class="prompt-editor">
    <div class="editor-header">
      <div class="header-title">
        <span class="icon">🎯</span>
        <h3>{{ technique?.name || 'Select a Technique' }}</h3>
      </div>
      <div class="header-actions" v-if="technique">
        <button @click="reset" class="btn-secondary" :disabled="!isDirty">
          Reset
        </button>
        <button @click="save" class="btn-primary" :disabled="saving || !isDirty">
          {{ saving ? 'Saving...' : 'Save Changes' }}
        </button>
      </div>
    </div>

    <div v-if="!technique" class="editor-empty">
      <p>Select a technique from the tree to edit its prompt</p>
    </div>

    <div v-else class="editor-content">
      <!-- Technique Info -->
      <div class="info-section">
        <div class="info-row">
          <span class="info-label">ID:</span>
          <span class="info-value">{{ technique.technique_id }}</span>
        </div>
        <div class="info-row">
          <span class="info-label">Description:</span>
          <span class="info-value">{{ technique.description }}</span>
        </div>
      </div>

      <!-- Prompt Editor -->
      <div class="prompt-section">
        <label class="section-label">Prompt Template:</label>
        <textarea
          v-model="editedPrompt"
          class="prompt-textarea"
          placeholder="Enter prompt template..."
          @input="markDirty"
        ></textarea>
      </div>

      <!-- Settings -->
      <div class="settings-section">
        <h4>Settings</h4>
        <div class="settings-grid">
          <div class="setting-item">
            <label>Temperature:</label>
            <input
              type="number"
              v-model.number="editedTemperature"
              min="0"
              max="2"
              step="0.1"
              @input="markDirty"
            />
            <span class="help-text">Controls randomness (0.0 - 2.0)</span>
          </div>

          <div class="setting-item">
            <label>Max Tokens:</label>
            <input
              type="number"
              v-model.number="editedMaxTokens"
              min="1"
              max="8000"
              step="100"
              @input="markDirty"
            />
            <span class="help-text">Maximum response length</span>
          </div>

          <div class="setting-item">
            <label>Agent Role:</label>
            <input
              type="text"
              v-model="editedAgentRole"
              @input="markDirty"
            />
            <span class="help-text">Role for this technique</span>
          </div>
        </div>
      </div>

      <!-- Metadata -->
      <div class="metadata-section" v-if="technique.metadata">
        <h4>Metadata</h4>
        <pre class="metadata-content">{{ JSON.stringify(technique.metadata, null, 2) }}</pre>
      </div>

      <!-- Save Status -->
      <div v-if="saveSuccess" class="save-status success">
        ✓ Changes saved successfully!
      </div>
      <div v-if="saveError" class="save-status error">
        ⚠️ Error saving: {{ saveError }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { useOrchestratorStore } from '@/stores/orchestrator'
import { storeToRefs } from 'pinia'

const store = useOrchestratorStore()
const { currentTechnique } = storeToRefs(store)

const technique = computed(() => currentTechnique.value)

const editedPrompt = ref('')
const editedTemperature = ref(0.7)
const editedMaxTokens = ref(2000)
const editedAgentRole = ref('')

const isDirty = ref(false)
const saving = ref(false)
const saveSuccess = ref(false)
const saveError = ref(null)

// Watch for technique changes
watch(technique, (newTechnique) => {
  if (newTechnique) {
    loadTechnique(newTechnique)
  }
}, { immediate: true })

function loadTechnique(tech) {
  editedPrompt.value = tech.prompt || ''
  editedTemperature.value = tech.temperature ?? 0.7
  editedMaxTokens.value = tech.max_tokens ?? 2000
  editedAgentRole.value = tech.agent_role || ''
  isDirty.value = false
  saveSuccess.value = false
  saveError.value = null
}

function markDirty() {
  isDirty.value = true
  saveSuccess.value = false
}

function reset() {
  if (technique.value) {
    loadTechnique(technique.value)
  }
}

async function save() {
  if (!technique.value || !isDirty.value) return

  saving.value = true
  saveError.value = null
  saveSuccess.value = false

  try {
    const updates = {
      prompt: editedPrompt.value,
      temperature: editedTemperature.value,
      max_tokens: editedMaxTokens.value,
      agent_role: editedAgentRole.value
    }

    await store.updateTechnique(technique.value.technique_id, updates)

    isDirty.value = false
    saveSuccess.value = true

    // Hide success message after 3 seconds
    setTimeout(() => {
      saveSuccess.value = false
    }, 3000)
  } catch (error) {
    saveError.value = error.message
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.prompt-editor {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--bg-panel, #0A0A0A);
  border-radius: 10px;
  overflow: hidden;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  background: rgba(255, 179, 71, 0.1);
  border-bottom: 2px solid var(--accent-gold, #FFB347);
}

.header-title {
  display: flex;
  align-items: center;
  gap: 0.8rem;
}

.header-title .icon {
  font-size: 1.8rem;
}

.header-title h3 {
  margin: 0;
  color: var(--accent-gold, #FFB347);
  font-size: 1.4rem;
}

.header-actions {
  display: flex;
  gap: 1rem;
}

.btn-primary, .btn-secondary {
  padding: 0.6rem 1.2rem;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: var(--accent-orange, #FF8C42);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 140, 66, 0.4);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  background: transparent;
  color: var(--text-light, #F5E6D3);
  border: 1px solid var(--border-medium, rgba(255, 255, 255, 0.3));
}

.btn-secondary:hover:not(:disabled) {
  border-color: var(--accent-gold, #FFB347);
}

.editor-empty {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted, #C9B299);
  font-size: 1.1rem;
}

.editor-content {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
}

.info-section {
  background: rgba(255, 179, 71, 0.05);
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
}

.info-row {
  display: flex;
  gap: 1rem;
  margin-bottom: 0.5rem;
}

.info-row:last-child {
  margin-bottom: 0;
}

.info-label {
  font-weight: 600;
  color: var(--text-muted, #C9B299);
  min-width: 100px;
}

.info-value {
  color: var(--text-light, #F5E6D3);
}

.prompt-section {
  margin-bottom: 1.5rem;
}

.section-label {
  display: block;
  font-weight: 600;
  color: var(--accent-gold, #FFB347);
  margin-bottom: 0.5rem;
  font-size: 1.1rem;
}

.prompt-textarea {
  width: 100%;
  min-height: 300px;
  padding: 1rem;
  background: var(--bg-code, #1A1410);
  color: var(--text-code, #F5E6D3);
  border: 1px solid var(--border-light, rgba(255, 255, 255, 0.2));
  border-radius: 8px;
  font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
  font-size: 0.95rem;
  line-height: 1.6;
  resize: vertical;
}

.prompt-textarea:focus {
  outline: none;
  border-color: var(--accent-gold, #FFB347);
  box-shadow: 0 0 0 3px rgba(255, 179, 71, 0.2);
}

.settings-section {
  margin-bottom: 1.5rem;
}

.settings-section h4 {
  color: var(--accent-gold, #FFB347);
  margin-bottom: 1rem;
}

.settings-grid {
  display: grid;
  gap: 1.5rem;
}

.setting-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.setting-item label {
  font-weight: 600;
  color: var(--text-light, #F5E6D3);
}

.setting-item input {
  padding: 0.6rem;
  background: var(--bg-code, #1A1410);
  color: var(--text-code, #F5E6D3);
  border: 1px solid var(--border-light, rgba(255, 255, 255, 0.2));
  border-radius: 6px;
  font-size: 0.95rem;
}

.setting-item input:focus {
  outline: none;
  border-color: var(--accent-gold, #FFB347);
}

.help-text {
  font-size: 0.85rem;
  color: var(--text-muted, #C9B299);
}

.metadata-section {
  margin-bottom: 1.5rem;
}

.metadata-section h4 {
  color: var(--accent-gold, #FFB347);
  margin-bottom: 0.5rem;
}

.metadata-content {
  background: var(--bg-code, #1A1410);
  padding: 1rem;
  border-radius: 8px;
  color: var(--text-code, #F5E6D3);
  font-size: 0.9rem;
  overflow-x: auto;
}

.save-status {
  padding: 1rem;
  border-radius: 8px;
  font-weight: 600;
  text-align: center;
}

.save-status.success {
  background: rgba(76, 175, 80, 0.2);
  color: #81C784;
  border: 2px solid #4CAF50;
}

.save-status.error {
  background: rgba(244, 67, 54, 0.2);
  color: #E57373;
  border: 2px solid #F44336;
}
</style>
