<template>
  <div class="template-prompt-editor">
    <div class="editor-header">
      <h3>{{ technique?.name }}</h3>
      <div class="header-actions">
        <button @click="toggleMode" class="mode-toggle">
          {{ editMode === 'template' ? '📝 Template Mode' : '📄 Raw Mode' }}
        </button>
        <button @click="save" :disabled="saving || !isDirty" class="save-btn">
          {{ saving ? 'Saving...' : 'Save Changes' }}
        </button>
        <button @click="reset" :disabled="!isDirty" class="reset-btn">
          Reset
        </button>
      </div>
    </div>

    <!-- Technique Info -->
    <div class="info-grid">
      <div class="info-item">
        <label>ID:</label>
        <span>{{ technique.technique_id }}</span>
      </div>
      <div class="info-item">
        <label>Type:</label>
        <span>{{ technique.type }}</span>
      </div>
      <div class="info-item">
        <label>Category:</label>
        <select v-model="editedCategory" @change="markDirty">
          <option value="market_opportunity">Market Opportunity</option>
          <option value="technical_feasibility">Technical Feasibility</option>
          <option value="competition">Competition</option>
          <option value="quality_assurance">Quality Assurance</option>
          <option value="strategic_planning">Strategic Planning</option>
          <option value="iterative_refinement">Iterative Refinement</option>
        </select>
      </div>
      <div class="info-item">
        <label>Agent Role:</label>
        <input v-model="editedAgentRole" @input="markDirty" />
      </div>
    </div>

    <!-- Template Mode: Structured Sections -->
    <div v-if="editMode === 'template'" class="template-sections">
      <div class="section-card">
        <div class="section-header">
          <h4>📋 Context</h4>
          <span class="section-hint">Background information for the AI</span>
        </div>
        <textarea
          v-model="promptSections.context"
          @input="markDirty"
          placeholder="Provide context about what the AI should know..."
          rows="3"
        ></textarea>
      </div>

      <div class="section-card">
        <div class="section-header">
          <h4>📥 Input</h4>
          <span class="section-hint">What data will be provided</span>
        </div>
        <textarea
          v-model="promptSections.input"
          @input="markDirty"
          placeholder="Describe the input data: {placeholder_name}"
          rows="2"
        ></textarea>
        <div class="placeholders-list">
          <span class="placeholder-label">Placeholders:</span>
          <div class="placeholder-tags">
            <span
              v-for="(ph, idx) in editedPlaceholders"
              :key="idx"
              class="placeholder-tag"
            >
              {{ '{' + ph + '}' }}
              <button @click="removePlaceholder(idx)" class="remove-ph">×</button>
            </span>
            <button @click="addPlaceholder" class="add-ph">+ Add</button>
          </div>
        </div>
      </div>

      <div class="section-card">
        <div class="section-header">
          <h4>🎯 Task</h4>
          <span class="section-hint">Clear instruction what to do</span>
        </div>
        <textarea
          v-model="promptSections.task"
          @input="markDirty"
          placeholder="Explain the specific task the AI should perform..."
          rows="4"
        ></textarea>
      </div>

      <div class="section-card">
        <div class="section-header">
          <h4>📤 Output Format</h4>
          <span class="section-hint">Exact structure expected</span>
        </div>
        <textarea
          v-model="promptSections.outputFormat"
          @input="markDirty"
          placeholder="Define the expected output format..."
          rows="4"
        ></textarea>
      </div>

      <div class="section-card">
        <div class="section-header">
          <h4>✅ Quality Criteria</h4>
          <span class="section-hint">What makes a good response</span>
        </div>
        <textarea
          v-model="promptSections.qualityCriteria"
          @input="markDirty"
          placeholder="List quality criteria (one per line)..."
          rows="3"
        ></textarea>
      </div>

      <div class="section-card optional">
        <div class="section-header">
          <h4>💡 Examples</h4>
          <span class="section-hint">Optional: Example input/output pairs</span>
        </div>
        <textarea
          v-model="promptSections.examples"
          @input="markDirty"
          placeholder="Provide example input and expected output..."
          rows="3"
        ></textarea>
      </div>
    </div>

    <!-- Raw Mode: Full Prompt -->
    <div v-else class="raw-mode">
      <div class="raw-header">
        <h4>Raw Prompt</h4>
        <span class="raw-hint">Edit the complete prompt directly</span>
      </div>
      <textarea
        v-model="editedPrompt"
        @input="markDirty"
        class="raw-prompt-textarea"
        rows="20"
      ></textarea>
    </div>

    <!-- Settings -->
    <div class="settings-section">
      <h4>⚙️ Model Settings</h4>
      <div class="settings-grid">
        <div class="setting-item">
          <label>Recommended Model:</label>
          <select v-model="editedModel" @change="markDirty">
            <option value="tier1_fast">Tier 1 Fast (Mixtral)</option>
            <option value="tier2_quality">Tier 2 Quality (Larger Model)</option>
          </select>
        </div>
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
          <span class="setting-hint">0 = deterministic, 2 = creative</span>
        </div>
        <div class="setting-item">
          <label>Max Tokens:</label>
          <input
            type="number"
            v-model.number="editedMaxTokens"
            min="100"
            max="8000"
            step="100"
            @input="markDirty"
          />
        </div>
      </div>
    </div>

    <!-- Exit Criteria -->
    <div class="exit-criteria-section">
      <h4>🚪 Exit Criteria</h4>
      <div class="criteria-grid">
        <div class="criteria-item">
          <label>Type:</label>
          <select v-model="editedExitCriteria.type" @change="markDirty">
            <option value="completion">Completion (default)</option>
            <option value="confidence_threshold">Confidence Threshold</option>
            <option value="custom">Custom</option>
          </select>
        </div>
        <div v-if="editedExitCriteria.type === 'confidence_threshold'" class="criteria-item">
          <label>Threshold:</label>
          <input
            type="number"
            v-model.number="editedExitCriteria.threshold"
            min="0"
            max="1"
            step="0.1"
            @change="markDirty"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useOrchestratorStore } from '@/stores/orchestrator'

const props = defineProps({
  technique: {
    type: Object,
    required: true
  }
})

const store = useOrchestratorStore()

const editMode = ref('template') // 'template' or 'raw'
const isDirty = ref(false)
const saving = ref(false)

// Editable fields
const editedCategory = ref(props.technique.category || 'general')
const editedAgentRole = ref(props.technique.agent_role || 'general_analyst')
const editedPrompt = ref(props.technique.prompt || '')
const editedModel = ref(props.technique.recommended_model || 'tier1_fast')
const editedTemperature = ref(props.technique.temperature || 0.3)
const editedMaxTokens = ref(props.technique.max_tokens || 2000)
const editedPlaceholders = ref([...(props.technique.placeholders || [])])
const editedExitCriteria = ref({
  type: props.technique.exit_criteria?.type || 'completion',
  threshold: props.technique.exit_criteria?.threshold || null,
  required_outputs: props.technique.exit_criteria?.required_outputs || ['content']
})

// Prompt sections (for template mode)
const promptSections = ref(parsePromptIntoSections(props.technique.prompt))

function parsePromptIntoSections(prompt) {
  // Simple parser - extract sections from existing prompt
  // In production, use more sophisticated parsing
  return {
    context: extractSection(prompt, 'CONTEXT', 'INPUT') || '',
    input: extractSection(prompt, 'INPUT', 'TASK') || extractSection(prompt, 'DOCUMENT TO ANALYZE', 'INSTRUCTIONS') || '',
    task: extractSection(prompt, 'TASK', 'OUTPUT') || extractSection(prompt, 'INSTRUCTIONS', 'OUTPUT') || '',
    outputFormat: extractSection(prompt, 'OUTPUT FORMAT', 'QUALITY') || extractSection(prompt, 'OUTPUT FORMAT', '---') || '',
    qualityCriteria: extractSection(prompt, 'QUALITY CRITERIA', 'EXAMPLES') || '',
    examples: extractSection(prompt, 'EXAMPLES', null) || ''
  }
}

function extractSection(text, startMarker, endMarker) {
  if (!text) return ''

  const startIdx = text.indexOf(startMarker)
  if (startIdx === -1) return ''

  const contentStart = startIdx + startMarker.length
  const endIdx = endMarker ? text.indexOf(endMarker, contentStart) : text.length

  return text.substring(contentStart, endIdx === -1 ? text.length : endIdx).trim()
}

function buildPromptFromSections() {
  const sections = []

  if (promptSections.value.context) {
    sections.push(`## Context\n${promptSections.value.context}`)
  }

  if (promptSections.value.input) {
    sections.push(`## Input\n${promptSections.value.input}`)
  }

  if (promptSections.value.task) {
    sections.push(`## Task\n${promptSections.value.task}`)
  }

  if (promptSections.value.outputFormat) {
    sections.push(`## Output Format\n${promptSections.value.outputFormat}`)
  }

  if (promptSections.value.qualityCriteria) {
    sections.push(`## Quality Criteria\n${promptSections.value.qualityCriteria}`)
  }

  if (promptSections.value.examples) {
    sections.push(`## Examples\n${promptSections.value.examples}`)
  }

  return `<s>[INST] ${sections.join('\n\n---\n\n')} [/INST]</s>`
}

function toggleMode() {
  if (editMode.value === 'template') {
    // Switching to raw mode - build prompt from sections
    editedPrompt.value = buildPromptFromSections()
    editMode.value = 'raw'
  } else {
    // Switching to template mode - parse prompt into sections
    promptSections.value = parsePromptIntoSections(editedPrompt.value)
    editMode.value = 'template'
  }
}

function markDirty() {
  isDirty.value = true
}

function addPlaceholder() {
  const name = prompt('Enter placeholder name:')
  if (name) {
    editedPlaceholders.value.push(name)
    markDirty()
  }
}

function removePlaceholder(index) {
  editedPlaceholders.value.splice(index, 1)
  markDirty()
}

async function save() {
  saving.value = true

  try {
    // Build final prompt based on current mode
    const finalPrompt = editMode.value === 'template'
      ? buildPromptFromSections()
      : editedPrompt.value

    const updates = {
      category: editedCategory.value,
      agent_role: editedAgentRole.value,
      prompt: finalPrompt,
      recommended_model: editedModel.value,
      temperature: editedTemperature.value,
      max_tokens: editedMaxTokens.value,
      placeholders: editedPlaceholders.value,
      exit_criteria: editedExitCriteria.value
    }

    await store.updateTechnique(props.technique.technique_id, updates)
    isDirty.value = false

    alert('✅ Technique saved successfully!')
  } catch (error) {
    alert(`❌ Error saving: ${error.message}`)
  } finally {
    saving.value = false
  }
}

function reset() {
  editedCategory.value = props.technique.category || 'general'
  editedAgentRole.value = props.technique.agent_role || 'general_analyst'
  editedPrompt.value = props.technique.prompt || ''
  editedModel.value = props.technique.recommended_model || 'tier1_fast'
  editedTemperature.value = props.technique.temperature || 0.3
  editedMaxTokens.value = props.technique.max_tokens || 2000
  editedPlaceholders.value = [...(props.technique.placeholders || [])]
  editedExitCriteria.value = {
    type: props.technique.exit_criteria?.type || 'completion',
    threshold: props.technique.exit_criteria?.threshold || null
  }
  promptSections.value = parsePromptIntoSections(props.technique.prompt)
  isDirty.value = false
}
</script>

<style scoped>
.template-prompt-editor {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  padding: 1.5rem;
  background: var(--bg-panel);
  border-radius: var(--radius-md);
  max-height: calc(100vh - 200px);
  overflow-y: auto;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border-light);
}

.editor-header h3 {
  margin: 0;
  color: var(--accent-gold);
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

.mode-toggle,
.save-btn,
.reset-btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: var(--radius-sm);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.mode-toggle {
  background: var(--bg-sidebar);
  color: var(--text-main);
}

.save-btn {
  background: var(--accent-gold);
  color: var(--bg-panel);
}

.save-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.reset-btn {
  background: var(--bg-dark);
  color: var(--text-main);
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.info-item label {
  font-size: 0.8rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-item span {
  color: var(--text-main);
  font-weight: 500;
}

.info-item select,
.info-item input {
  padding: 0.5rem;
  background: var(--bg-sidebar);
  color: var(--text-main);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-sm);
}

.template-sections {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.section-card {
  background: var(--bg-sidebar);
  padding: 1rem;
  border-radius: var(--radius-sm);
  border-left: 3px solid var(--accent-gold);
}

.section-card.optional {
  border-left-color: var(--text-muted);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.section-header h4 {
  margin: 0;
  color: var(--accent-gold);
  font-size: 1rem;
}

.section-hint {
  font-size: 0.8rem;
  color: var(--text-muted);
}

.section-card textarea {
  width: 100%;
  padding: 0.75rem;
  background: var(--bg-code);
  color: var(--text-main);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-sm);
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
  resize: vertical;
}

.placeholders-list {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.5rem;
  flex-wrap: wrap;
}

.placeholder-label {
  font-size: 0.85rem;
  color: var(--text-muted);
}

.placeholder-tags {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.placeholder-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.5rem;
  background: var(--accent-gradient);
  color: var(--accent-gold);
  border-radius: 4px;
  font-size: 0.85rem;
  font-family: 'Courier New', monospace;
}

.remove-ph {
  background: none;
  border: none;
  color: var(--accent-orange);
  cursor: pointer;
  font-size: 1.2rem;
  padding: 0;
  line-height: 1;
}

.add-ph {
  padding: 0.25rem 0.5rem;
  background: var(--bg-dark);
  color: var(--text-main);
  border: 1px dashed var(--border-light);
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
}

.raw-mode {
  background: var(--bg-sidebar);
  padding: 1rem;
  border-radius: var(--radius-sm);
}

.raw-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.75rem;
}

.raw-header h4 {
  margin: 0;
  color: var(--accent-gold);
}

.raw-hint {
  font-size: 0.8rem;
  color: var(--text-muted);
}

.raw-prompt-textarea {
  width: 100%;
  padding: 1rem;
  background: var(--bg-code);
  color: var(--text-main);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-sm);
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
  resize: vertical;
}

.settings-section,
.exit-criteria-section {
  background: var(--bg-sidebar);
  padding: 1rem;
  border-radius: var(--radius-sm);
}

.settings-section h4,
.exit-criteria-section h4 {
  margin: 0 0 1rem 0;
  color: var(--accent-gold);
}

.settings-grid,
.criteria-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.setting-item,
.criteria-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.setting-item label,
.criteria-item label {
  font-size: 0.85rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.setting-item select,
.setting-item input,
.criteria-item select,
.criteria-item input {
  padding: 0.5rem;
  background: var(--bg-code);
  color: var(--text-main);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-sm);
}

.setting-hint {
  font-size: 0.75rem;
  color: var(--text-muted);
  font-style: italic;
}
</style>
