<template>
  <div v-if="isOpen" class="wizard-overlay" @click.self="close">
    <div class="wizard-modal">
      <!-- Header -->
      <div class="wizard-header">
        <h2>Create New Research Session</h2>
        <button @click="close" class="btn-close">✕</button>
      </div>

      <!-- Progress Indicator -->
      <div class="wizard-progress">
        <div
          v-for="(step, idx) in steps"
          :key="idx"
          :class="['progress-step', { active: currentStep === idx, completed: currentStep > idx }]"
        >
          <div class="step-number">{{ idx + 1 }}</div>
          <div class="step-label">{{ step.label }}</div>
        </div>
      </div>

      <!-- Step Content -->
      <div class="wizard-content">
        <!-- Step 1: Basic Info -->
        <div v-show="currentStep === 0" class="wizard-step">
          <h3>Basic Information</h3>

          <div class="form-group">
            <label for="title">Title *</label>
            <input
              id="title"
              v-model="formData.title"
              type="text"
              placeholder="e.g., AI Ethics Research"
              class="form-input"
              required
            />
          </div>

          <div class="form-group">
            <label for="goal">Research Goal *</label>
            <textarea
              id="goal"
              v-model="formData.goal"
              placeholder="e.g., Explore ethical implications of AI decision-making in healthcare"
              class="form-textarea"
              rows="3"
              required
            ></textarea>
          </div>

          <div class="form-group">
            <label for="description">Description (optional)</label>
            <textarea
              id="description"
              v-model="formData.description"
              placeholder="Additional context or details about this research"
              class="form-textarea"
              rows="2"
            ></textarea>
          </div>
        </div>

        <!-- Step 2: Axioms -->
        <div v-show="currentStep === 1" class="wizard-step">
          <h3>Select Reasoning Axioms</h3>
          <p class="step-hint">Choose axioms that will guide the AI's reasoning process</p>

          <div class="axioms-grid">
            <div
              v-for="axiom in availableAxioms"
              :key="axiom.id"
              :class="['axiom-card', { selected: formData.axioms.includes(axiom.id) }]"
              @click="toggleAxiom(axiom.id)"
            >
              <div class="axiom-header">
                <span class="axiom-icon">{{ axiom.icon }}</span>
                <span class="axiom-name">{{ axiom.name }}</span>
                <span v-if="formData.axioms.includes(axiom.id)" class="axiom-check">✓</span>
              </div>
              <p class="axiom-description">{{ axiom.description }}</p>
            </div>
          </div>
        </div>

        <!-- Step 3: Confirm -->
        <div v-show="currentStep === 2" class="wizard-step">
          <h3>Review & Create</h3>

          <div class="review-section">
            <div class="review-item">
              <span class="review-label">Title:</span>
              <span class="review-value">{{ formData.title }}</span>
            </div>
            <div class="review-item">
              <span class="review-label">Goal:</span>
              <span class="review-value">{{ formData.goal }}</span>
            </div>
            <div v-if="formData.description" class="review-item">
              <span class="review-label">Description:</span>
              <span class="review-value">{{ formData.description }}</span>
            </div>
            <div class="review-item">
              <span class="review-label">Axioms:</span>
              <div class="review-axioms">
                <span
                  v-for="axiomId in formData.axioms"
                  :key="axiomId"
                  class="axiom-chip"
                >
                  {{ getAxiomLabel(axiomId) }}
                </span>
                <span v-if="formData.axioms.length === 0" class="no-axioms">
                  None selected
                </span>
              </div>
            </div>
          </div>

          <div v-if="error" class="error-message">
            {{ error }}
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="wizard-actions">
        <button
          v-if="currentStep > 0"
          @click="previousStep"
          class="btn-secondary"
        >
          Back
        </button>
        <div class="spacer"></div>
        <button
          v-if="currentStep < steps.length - 1"
          @click="nextStep"
          :disabled="!canProceed"
          class="btn-primary"
        >
          Next
        </button>
        <button
          v-if="currentStep === steps.length - 1"
          @click="createSession"
          :disabled="creating || !canProceed"
          class="btn-primary btn-create"
        >
          {{ creating ? 'Creating...' : 'Create Session' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useSessionsStore } from '@/stores/sessions'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close', 'created'])

const sessionsStore = useSessionsStore()

// Wizard state
const currentStep = ref(0)
const creating = ref(false)
const error = ref(null)

const steps = [
  { label: 'Basic Info' },
  { label: 'Axioms' },
  { label: 'Confirm' }
]

// Form data
const formData = ref({
  title: '',
  goal: '',
  description: '',
  mode: 'unified',  // Always unified - user decides workflow later
  axioms: []
})

// Available axioms
const availableAxioms = [
  {
    id: 'first_principles',
    name: 'First Principles',
    icon: '🧱',
    description: 'Break down complex problems into fundamental truths'
  },
  {
    id: 'socratic_method',
    name: 'Socratic Method',
    icon: '❓',
    description: 'Question assumptions and explore through dialogue'
  },
  {
    id: 'devils_advocate',
    name: "Devil's Advocate",
    icon: '😈',
    description: 'Challenge ideas by arguing the opposite position'
  },
  {
    id: 'cross_domain',
    name: 'Cross-Domain',
    icon: '🔀',
    description: 'Draw insights from different fields and domains'
  },
  {
    id: 'contrarian',
    name: 'Contrarian',
    icon: '🔄',
    description: 'Seek unconventional perspectives and counter-arguments'
  },
  {
    id: 'opportunity_cost',
    name: 'Opportunity Cost',
    icon: '⚖️',
    description: 'Evaluate trade-offs and alternative paths'
  }
]

// Computed
const canProceed = computed(() => {
  if (currentStep.value === 0) {
    return formData.value.title.trim() && formData.value.goal.trim()
  }
  // All other steps can always proceed
  return true
})

// Methods
function nextStep() {
  if (currentStep.value < steps.length - 1) {
    currentStep.value++
  }
}

function previousStep() {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

function toggleAxiom(axiomId) {
  const index = formData.value.axioms.indexOf(axiomId)
  if (index > -1) {
    formData.value.axioms.splice(index, 1)
  } else {
    formData.value.axioms.push(axiomId)
  }
}

function getAxiomLabel(axiomId) {
  const axiom = availableAxioms.find(a => a.id === axiomId)
  return axiom ? axiom.name : axiomId
}

async function createSession() {
  creating.value = true
  error.value = null

  try {
    const sessionData = {
      title: formData.value.title,
      goal: formData.value.goal,
      description: formData.value.description || undefined,
      mode: formData.value.mode,
      axioms: formData.value.axioms
    }

    const createdSession = await sessionsStore.createSession(sessionData)

    // Success!
    emit('created', createdSession)
    close()
    resetForm()
  } catch (err) {
    error.value = err.message || 'Failed to create session'
    console.error('Error creating session:', err)
  } finally {
    creating.value = false
  }
}

function close() {
  emit('close')
}

function resetForm() {
  currentStep.value = 0
  formData.value = {
    title: '',
    goal: '',
    description: '',
    mode: 'unified',
    axioms: []
  }
  error.value = null
}
</script>

<style scoped>
/* Overlay */
.wizard-overlay {
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
  padding: 2rem;
}

.wizard-modal {
  background: #1a1a1a;
  border-radius: 12px;
  max-width: 800px;
  width: 100%;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
}

/* Header */
.wizard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #333;
}

.wizard-header h2 {
  margin: 0;
  font-size: 1.5rem;
  color: #e0e0e0;
}

.btn-close {
  background: none;
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
  border-radius: 4px;
  transition: all 0.2s;
}

.btn-close:hover {
  background: #333;
  color: #e0e0e0;
}

/* Progress */
.wizard-progress {
  display: flex;
  padding: 1.5rem;
  gap: 1rem;
  border-bottom: 1px solid #333;
}

.progress-step {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  position: relative;
}

.step-number {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #333;
  color: #888;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  transition: all 0.3s;
}

.progress-step.active .step-number {
  background: #4CAF50;
  color: white;
}

.progress-step.completed .step-number {
  background: #2196F3;
  color: white;
}

.step-label {
  font-size: 0.85rem;
  color: #888;
  transition: color 0.3s;
}

.progress-step.active .step-label {
  color: #4CAF50;
  font-weight: 600;
}

.progress-step.completed .step-label {
  color: #2196F3;
}

/* Content */
.wizard-content {
  flex: 1;
  overflow-y: auto;
  padding: 2rem;
}

.wizard-step {
  animation: fadeIn 0.3s;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.wizard-step h3 {
  margin: 0 0 1.5rem 0;
  font-size: 1.25rem;
  color: #e0e0e0;
}

.step-hint {
  margin: -1rem 0 1.5rem 0;
  color: #888;
  font-size: 0.9rem;
}

/* Form */
.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #aaa;
  font-size: 0.9rem;
  font-weight: 500;
}

.form-input,
.form-textarea {
  width: 100%;
  padding: 0.75rem;
  background: #222;
  border: 1px solid #333;
  border-radius: 6px;
  color: #e0e0e0;
  font-size: 0.95rem;
  font-family: inherit;
  transition: border-color 0.2s;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: #4CAF50;
}

.form-input::placeholder,
.form-textarea::placeholder {
  color: #666;
}

/* Axioms Grid */
.axioms-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

.axiom-card {
  padding: 1rem;
  background: #222;
  border: 2px solid #333;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.axiom-card:hover {
  background: #282828;
  border-color: #4CAF50;
}

.axiom-card.selected {
  background: #2a2a2a;
  border-color: #4CAF50;
}

.axiom-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.axiom-icon {
  font-size: 1.2rem;
}

.axiom-name {
  flex: 1;
  font-weight: 600;
  color: #e0e0e0;
  font-size: 0.95rem;
}

.axiom-check {
  color: #4CAF50;
  font-size: 1.2rem;
}

.axiom-description {
  margin: 0;
  font-size: 0.85rem;
  color: #aaa;
  line-height: 1.4;
}

/* Review */
.review-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.review-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 1rem;
  background: #222;
  border-radius: 6px;
}

.review-label {
  font-size: 0.85rem;
  color: #888;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.review-value {
  color: #e0e0e0;
  font-size: 0.95rem;
}

.review-axioms {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.axiom-chip {
  padding: 0.5rem 1rem;
  background: #2196F3;
  color: white;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 500;
}

.no-axioms {
  color: #666;
  font-style: italic;
}

.error-message {
  margin-top: 1rem;
  padding: 1rem;
  background: rgba(244, 67, 54, 0.1);
  border: 1px solid #f44336;
  border-radius: 6px;
  color: #f44336;
  font-size: 0.9rem;
}

/* Actions */
.wizard-actions {
  display: flex;
  gap: 1rem;
  padding: 1.5rem;
  border-top: 1px solid #333;
}

.spacer {
  flex: 1;
}

.btn-primary,
.btn-secondary {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: linear-gradient(135deg, #4CAF50, #45a049);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: linear-gradient(135deg, #45a049, #3d8b3d);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  background: #333;
  color: #e0e0e0;
}

.btn-secondary:hover {
  background: #444;
}

.btn-create {
  min-width: 150px;
}

/* Scrollbar */
.wizard-content::-webkit-scrollbar {
  width: 8px;
}

.wizard-content::-webkit-scrollbar-track {
  background: #1a1a1a;
}

.wizard-content::-webkit-scrollbar-thumb {
  background: #333;
  border-radius: 4px;
}

.wizard-content::-webkit-scrollbar-thumb:hover {
  background: #444;
}
</style>
