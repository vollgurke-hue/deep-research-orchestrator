<template>
  <div v-if="isOpen" class="dialog-overlay" @click.self="close">
    <div class="dialog-container">
      <!-- Step 1: Copy Prompt -->
      <div v-if="step === 1" class="dialog-content">
        <div class="dialog-header">
          <h3>📤 Send to External Model</h3>
          <button @click="close" class="btn-close">✕</button>
        </div>

        <div class="dialog-body">
          <p class="instruction">
            Copy this prompt and paste it into your preferred AI model:
          </p>

          <div class="model-selector">
            <label>
              <input type="radio" value="claude-opus" v-model="selectedModel" />
              <span>Claude Opus (Anthropic)</span>
            </label>
            <label>
              <input type="radio" value="gpt-4" v-model="selectedModel" />
              <span>GPT-4 (OpenAI)</span>
            </label>
            <label>
              <input type="radio" value="gemini-pro" v-model="selectedModel" />
              <span>Gemini Pro (Google)</span>
            </label>
          </div>

          <div class="prompt-container">
            <div class="prompt-header">
              <strong>Prompt:</strong>
              <button @click="copyPrompt" class="btn-copy">
                {{ copied ? '✅ Copied!' : '📋 Copy to Clipboard' }}
              </button>
            </div>
            <pre class="prompt-text" ref="promptRef">{{ externalPrompt }}</pre>
          </div>
        </div>

        <div class="dialog-footer">
          <button @click="close" class="btn-secondary">Cancel</button>
          <button @click="step = 2" class="btn-primary">
            I've sent the prompt → Next
          </button>
        </div>
      </div>

      <!-- Step 2: Paste Response -->
      <div v-if="step === 2" class="dialog-content">
        <div class="dialog-header">
          <h3>📥 Paste Response</h3>
          <button @click="close" class="btn-close">✕</button>
        </div>

        <div class="dialog-body">
          <p class="instruction">
            Paste the response you received from {{ selectedModel }}:
          </p>

          <textarea
            v-model="responseText"
            placeholder="Paste the AI's response here..."
            rows="15"
            class="response-textarea"
          ></textarea>
        </div>

        <div class="dialog-footer">
          <button @click="step = 1" class="btn-secondary">← Back</button>
          <button
            @click="submitResponse"
            class="btn-primary"
            :disabled="!responseText.trim() || submitting"
          >
            {{ submitting ? '⏳ Processing...' : '✅ Add Response' }}
          </button>
        </div>
      </div>

      <!-- Step 3: Success -->
      <div v-if="step === 3" class="dialog-content">
        <div class="dialog-header">
          <h3>✅ Success</h3>
          <button @click="close" class="btn-close">✕</button>
        </div>

        <div class="dialog-body">
          <div class="success-message">
            <div class="success-icon">🎉</div>
            <p>Response added successfully!</p>

            <div v-if="result" class="result-stats">
              <div class="stat-item">
                <strong>Confidence:</strong> {{ Math.round(result.confidence * 100) }}%
              </div>
              <div class="stat-item">
                <strong>Entities Extracted:</strong> {{ result.entities_extracted }}
              </div>
              <div v-if="result.axiom_compatible !== undefined" class="stat-item">
                <strong>Axiom Compatible:</strong>
                {{ result.axiom_compatible ? '✅ Yes' : '❌ No' }}
              </div>
            </div>
          </div>
        </div>

        <div class="dialog-footer">
          <button @click="close" class="btn-primary">Close</button>
        </div>
      </div>

      <!-- Error State -->
      <div v-if="error" class="error-banner">
        {{ error }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  nodeId: {
    type: String,
    required: true
  },
  externalPrompt: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['close', 'submit'])

// State
const step = ref(1)
const selectedModel = ref('claude-opus')
const responseText = ref('')
const copied = ref(false)
const submitting = ref(false)
const error = ref(null)
const result = ref(null)
const promptRef = ref(null)

// Methods
const close = () => {
  // Reset state
  step.value = 1
  responseText.value = ''
  copied.value = false
  submitting.value = false
  error.value = null
  result.value = null

  emit('close')
}

const copyPrompt = async () => {
  try {
    await navigator.clipboard.writeText(props.externalPrompt)
    copied.value = true
    setTimeout(() => {
      copied.value = false
    }, 2000)
  } catch (err) {
    // Fallback: select text
    if (promptRef.value) {
      const range = document.createRange()
      range.selectNodeContents(promptRef.value)
      const selection = window.getSelection()
      selection.removeAllRanges()
      selection.addRange(range)
    }
  }
}

const submitResponse = async () => {
  submitting.value = true
  error.value = null

  try {
    const response = await emit('submit', {
      node_id: props.nodeId,
      response_text: responseText.value,
      model_name: selectedModel.value
    })

    result.value = response
    step.value = 3

  } catch (err) {
    error.value = err.message || 'Failed to submit response'
  } finally {
    submitting.value = false
  }
}

// Reset when dialog opens
watch(() => props.isOpen, (isOpen) => {
  if (isOpen) {
    step.value = 1
    responseText.value = ''
    copied.value = false
    error.value = null
    result.value = null
  }
})
</script>

<style scoped>
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.dialog-container {
  background: #1a1a1a;
  border-radius: 12px;
  max-width: 700px;
  width: 90%;
  max-height: 90vh;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
}

.dialog-content {
  display: flex;
  flex-direction: column;
  max-height: 90vh;
}

/* Header */
.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 2px solid #333;
}

.dialog-header h3 {
  margin: 0;
  color: #e0e0e0;
}

.btn-close {
  background: none;
  border: none;
  color: #999;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0;
  line-height: 1;
}

.btn-close:hover {
  color: #e0e0e0;
}

/* Body */
.dialog-body {
  padding: 1.5rem;
  overflow-y: auto;
  flex: 1;
}

.instruction {
  margin: 0 0 1rem 0;
  color: #ccc;
}

/* Model Selector */
.model-selector {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin: 1rem 0 1.5rem 0;
  padding: 1rem;
  background: #2a2a2a;
  border-radius: 8px;
}

.model-selector label {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: #e0e0e0;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 4px;
  transition: background 0.2s;
}

.model-selector label:hover {
  background: #333;
}

.model-selector input[type="radio"] {
  cursor: pointer;
}

/* Prompt Container */
.prompt-container {
  background: #0f0f0f;
  border-radius: 8px;
  overflow: hidden;
}

.prompt-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  background: #2a2a2a;
  border-bottom: 1px solid #444;
}

.prompt-header strong {
  color: #e0e0e0;
}

.btn-copy {
  padding: 0.4rem 0.8rem;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: background 0.2s;
}

.btn-copy:hover {
  background: #45a049;
}

.prompt-text {
  margin: 0;
  padding: 1rem;
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
  color: #e0e0e0;
  white-space: pre-wrap;
  word-wrap: break-word;
  max-height: 400px;
  overflow-y: auto;
}

/* Response Textarea */
.response-textarea {
  width: 100%;
  padding: 1rem;
  background: #0f0f0f;
  border: 1px solid #444;
  border-radius: 8px;
  color: #e0e0e0;
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
  resize: vertical;
  min-height: 300px;
}

.response-textarea:focus {
  outline: none;
  border-color: #2196F3;
}

/* Success Message */
.success-message {
  text-align: center;
  padding: 2rem;
}

.success-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.success-message p {
  font-size: 1.2rem;
  color: #4CAF50;
  margin-bottom: 1.5rem;
}

.result-stats {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  text-align: left;
  background: #2a2a2a;
  padding: 1rem;
  border-radius: 8px;
}

.stat-item {
  color: #ccc;
}

.stat-item strong {
  color: #e0e0e0;
}

/* Footer */
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1.5rem;
  border-top: 2px solid #333;
}

.btn-primary,
.btn-secondary {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.95rem;
  transition: all 0.2s;
}

.btn-primary {
  background: #4CAF50;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #45a049;
}

.btn-primary:disabled {
  background: #666;
  cursor: not-allowed;
  opacity: 0.6;
}

.btn-secondary {
  background: #666;
  color: white;
}

.btn-secondary:hover {
  background: #777;
}

/* Error Banner */
.error-banner {
  background: #f44336;
  color: white;
  padding: 1rem;
  text-align: center;
  font-weight: 600;
}

/* Scrollbar */
.dialog-body::-webkit-scrollbar,
.prompt-text::-webkit-scrollbar {
  width: 8px;
}

.dialog-body::-webkit-scrollbar-track,
.prompt-text::-webkit-scrollbar-track {
  background: #1a1a1a;
}

.dialog-body::-webkit-scrollbar-thumb,
.prompt-text::-webkit-scrollbar-thumb {
  background: #444;
  border-radius: 4px;
}

.dialog-body::-webkit-scrollbar-thumb:hover,
.prompt-text::-webkit-scrollbar-thumb:hover {
  background: #555;
}
</style>
