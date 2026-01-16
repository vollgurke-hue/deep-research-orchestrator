<template>
  <div class="research-creator">
    <!-- Step Indicator -->
    <div class="wizard-steps">
      <div v-for="(step, idx) in steps" :key="idx" :class="['step', { active: currentStep === idx, completed: currentStep > idx }]">
        <div class="step-number">{{ idx + 1 }}</div>
        <div class="step-label">{{ step.label }}</div>
      </div>
    </div>

    <!-- Step Content -->
    <div class="step-content">
      <!-- Step 0: Describe Research -->
      <div v-if="currentStep === 0" class="step-panel">
        <h2>🎯 Describe Your Research</h2>
        <p class="step-description">Describe what you want to research and your specific goal/objective.</p>

        <div class="form-group">
          <label class="form-label">Research Description:</label>
          <textarea
            v-model="userInput"
            placeholder="Ich möchte ein SaaS-Produkt für AI-gestütztes Tutoring im Bildungsbereich validieren. Das Produkt soll Schülern und Studenten personalisierte Lernhilfe bieten..."
            rows="6"
            class="input-textarea"
          ></textarea>
        </div>

        <div class="form-group">
          <label class="form-label">Explicit Goal/Objective:</label>
          <textarea
            v-model="researchGoal"
            placeholder="Ziel: Ich brauche eine umfassende Marktanalyse, Wettbewerbsanalyse, technische Machbarkeit und Geschäftsmodell-Validierung um fundierte Go/No-Go Entscheidung zu treffen."
            rows="3"
            class="input-textarea"
          ></textarea>
          <p class="field-hint">💡 Be specific about what you want to achieve with this research.</p>
        </div>

        <div class="form-group">
          <label class="form-label">Research Type:</label>
          <select v-model="researchType" class="input-select">
            <option value="product">Product Validation</option>
            <option value="market">Market Research</option>
            <option value="scientific">Scientific Literature</option>
            <option value="business">Business Analysis</option>
            <option value="technical">Technical Research</option>
          </select>
        </div>

        <!-- Quality Helper Section -->
        <div v-if="userInput && researchGoal" class="quality-helper-section">
          <h3>🎯 Input Quality Check (Local AI)</h3>
          <p class="section-hint">Get AI feedback to improve your research input before starting</p>

          <button @click="evaluateInputQuality" :disabled="evaluating" class="btn-evaluate-quality">
            {{ evaluating ? 'Evaluating...' : '✓ Evaluate Quality (Local Model)' }}
          </button>

          <!-- Quality Results -->
          <div v-if="qualityResult" class="quality-results">
            <!-- Overall Score -->
            <div :class="['quality-score-badge', getQualityScoreClass(qualityResult.quality_score)]">
              <span class="score-number">{{ qualityResult.quality_score }}%</span>
              <span class="score-label">Overall Quality</span>
            </div>

            <!-- Sub-Scores -->
            <div class="sub-scores">
              <div class="sub-score-item">
                <span class="label">Description:</span>
                <span :class="['score', getQualityScoreClass(qualityResult.description_score)]">
                  {{ qualityResult.description_score }}%
                </span>
              </div>
              <div class="sub-score-item">
                <span class="label">Goal:</span>
                <span :class="['score', getQualityScoreClass(qualityResult.goal_score)]">
                  {{ qualityResult.goal_score }}%
                </span>
              </div>
            </div>

            <!-- Strengths -->
            <div v-if="qualityResult.strengths.length > 0" class="quality-list strengths-list">
              <h4>✅ Strengths:</h4>
              <ul>
                <li v-for="(strength, idx) in qualityResult.strengths" :key="idx">{{ strength }}</li>
              </ul>
            </div>

            <!-- Weaknesses -->
            <div v-if="qualityResult.weaknesses.length > 0" class="quality-list weaknesses-list">
              <h4>⚠️ Areas to Improve:</h4>
              <ul>
                <li v-for="(weakness, idx) in qualityResult.weaknesses" :key="idx">{{ weakness }}</li>
              </ul>
            </div>

            <!-- Suggestions -->
            <div v-if="qualityResult.suggestions.length > 0" class="quality-list suggestions-list">
              <h4>💡 Suggestions:</h4>
              <ul>
                <li v-for="(suggestion, idx) in qualityResult.suggestions" :key="idx">{{ suggestion }}</li>
              </ul>
            </div>

            <!-- Improved Versions (if provided) -->
            <div v-if="qualityResult.improved_description || qualityResult.improved_goal" class="improved-versions">
              <h4>📝 AI-Improved Versions:</h4>

              <div v-if="qualityResult.improved_description" class="improved-field">
                <label>Improved Description:</label>
                <div class="improved-text">{{ qualityResult.improved_description }}</div>
                <button @click="applyImprovedDescription" class="btn-apply">Use This</button>
              </div>

              <div v-if="qualityResult.improved_goal" class="improved-field">
                <label>Improved Goal:</label>
                <div class="improved-text">{{ qualityResult.improved_goal }}</div>
                <button @click="applyImprovedGoal" class="btn-apply">Use This</button>
              </div>
            </div>
          </div>
        </div>

        <div class="step-actions">
          <button @click="router.push('/')" class="btn-secondary">Cancel</button>
          <button @click="generateStructure" :disabled="!userInput || !researchGoal || generating" class="btn-primary">
            {{ generating ? 'Generating...' : 'Generate Structure →' }}
          </button>
        </div>
      </div>

      <!-- Step 1: Hierarchical Theme Structure -->
      <div v-else-if="currentStep === 1" class="step-panel">
        <h2>📊 Hierarchical Theme Structure</h2>
        <p class="step-description">
          Review the thematic structure. Select the themes you want to research.
        </p>

        <!-- Metadata Bar -->
        <div class="metadata-bar">
          <div class="meta-item">
            <span class="meta-icon">📦</span>
            <span>{{ metadata.total_themes || 0 }} Total Themes</span>
          </div>
          <div class="meta-item">
            <span class="meta-icon">✓</span>
            <span>{{ selectedThemes.size }} Selected</span>
          </div>
          <div class="meta-item">
            <span class="meta-icon">📝</span>
            <span>{{ selectedThemes.size }} Prompts (1 per theme)</span>
          </div>
          <div class="meta-item" :class="['coverage-item', getCoverageClass()]">
            <span class="meta-icon">📊</span>
            <span>Coverage: {{ calculateCoverage() }}%</span>
          </div>
        </div>

        <!-- External Model Coverage Check -->
        <div class="external-coverage-section">
          <h3>📊 Coverage Analysis (External Model)</h3>
          <p class="section-hint">Get expert coverage analysis from Claude, GPT-4, or other flagship models</p>

          <button @click="copyCoveragePrompt" class="btn-copy-prompt-large">
            📋 Copy Coverage Analysis Prompt
          </button>

          <div class="paste-response-area">
            <label>Paste Coverage Analysis Response (Text):</label>
            <textarea
              v-model="coverageResponse"
              placeholder="Paste the TEXT response from Claude, GPT-4, or another model here...&#10;&#10;The local model will analyze it and extract:&#10;- Coverage percentage&#10;- Covered aspects&#10;- Missing aspects&#10;- Recommended new themes"
              rows="10"
              class="response-textarea-large"
            ></textarea>
            <button
              @click="processCoverageAnalysis"
              :disabled="!coverageResponse || generating"
              class="btn-process"
            >
              {{ generating ? 'Analyzing...' : '✓ Analyze Coverage (Local Model)' }}
            </button>
            <p class="field-hint">💡 Local model will extract structured data from the text - no need for JSON format!</p>
          </div>

          <!-- Coverage Results -->
          <div v-if="coverageAnalysis" class="coverage-results">
            <div :class="['coverage-score-display', getCoverageResultClass()]">
              <span class="score-label">Coverage:</span>
              <span class="score-value">{{ coverageAnalysis.coverage_percentage }}%</span>
            </div>

            <div v-if="coverageAnalysis.covered_aspects?.length" class="covered-list">
              <h4>✅ Well Covered:</h4>
              <ul>
                <li v-for="aspect in coverageAnalysis.covered_aspects" :key="aspect">{{ aspect }}</li>
              </ul>
            </div>

            <div v-if="coverageAnalysis.missing_critical_aspects?.length" class="missing-list">
              <h4>❌ Missing Critical Aspects:</h4>
              <ul>
                <li v-for="aspect in coverageAnalysis.missing_critical_aspects" :key="aspect">{{ aspect }}</li>
              </ul>
            </div>

            <div class="rationale-box">
              <strong>Rationale:</strong> {{ coverageAnalysis.rationale }}
            </div>

            <div v-if="coverageAnalysis.recommendation" class="recommendation-box-new">
              <strong>💡 Recommendation:</strong> {{ coverageAnalysis.recommendation }}
            </div>

            <!-- Coverage Status Message -->
            <div v-if="coverageAnalysis.coverage_percentage < 80" class="coverage-warning-box">
              <h4>⚠️ Coverage Below 80%</h4>
              <p>
                The coverage analysis suggested {{ coverageAnalysis.suggested_themes?.length || 0 }} new themes to improve coverage.
                {{ coverageAnalysis.suggested_themes?.length > 0 ? 'They have been automatically added.' : '' }}
              </p>
              <p class="action-hint">
                📋 <strong>Next step:</strong> Run coverage analysis again to check if coverage improved, or proceed if satisfied.
              </p>
            </div>

            <div v-else-if="coverageAnalysis" class="coverage-good-large">
              <span class="check-icon-large">✅</span>
              <span>Coverage goal reached (≥80%)! You can proceed to generate prompts.</span>
            </div>
          </div>
        </div>

        <!-- Theme Tree -->
        <div class="theme-tree">
          <ThemeNode
            v-for="theme in thematicHierarchy"
            :key="theme.theme_id"
            :theme="theme"
            :level="0"
            :selectedThemes="selectedThemes"
            @select="toggleThemeSelection"
          />
        </div>

        <!-- Selection Summary -->
        <div class="selection-summary">
          <div class="summary-stat">
            <span class="stat-label">Selected Themes:</span>
            <span class="stat-value">{{ selectedThemes.size }}</span>
          </div>
        </div>

        <div class="step-actions">
          <button @click="currentStep = 0" class="btn-secondary">← Back</button>
          <button
            @click="generatePrompts"
            :disabled="selectedThemes.size === 0 || generating"
            class="btn-primary"
          >
            {{ generating ? 'Generating...' : `Generate Prompts (${selectedThemes.size}) →` }}
          </button>
        </div>
      </div>

      <!-- Step 2: Deep Research Prompts Generation -->
      <div v-else-if="currentStep === 2" class="step-panel">
        <h2>📝 Deep Research Prompts</h2>
        <p class="step-description">
          Review and copy the {{ Object.keys(deepPrompts.prompts || {}).length }} generated prompts.
          These will be used to collect deep research from external AI models in the next step.
        </p>

        <!-- Prompts List (Read-Only) -->
        <div class="prompts-list">
          <div
            v-for="(prompt, themeId) in deepPrompts.prompts || {}"
            :key="themeId"
            class="prompt-card"
          >
            <div class="prompt-card-header">
              <h3>{{ prompt.prompt_title }}</h3>
              <button @click="copyPrompt(prompt.comprehensive_prompt)" class="btn-copy-prompt">
                📋 Copy Prompt
              </button>
            </div>

            <div class="prompt-preview-box">
              <pre>{{ prompt.comprehensive_prompt }}</pre>
            </div>

            <hr class="prompt-separator" />
          </div>
        </div>

        <!-- Summary -->
        <div class="prompts-summary">
          <p>
            <strong>{{ Object.keys(deepPrompts.prompts || {}).length }} prompts generated</strong>
            - Ready to collect deep research from external AI models.
          </p>
        </div>

        <div class="step-actions">
          <button @click="currentStep = 1" class="btn-secondary">← Back to Themes</button>
          <button
            @click="currentStep = 3"
            class="btn-primary"
          >
            Start Base Research Collection →
          </button>
        </div>
      </div>

      <!-- Step 3: Base Research Collection -->
      <div v-else-if="currentStep === 3" class="step-panel">
        <h2>📚 Base Research Collection</h2>
        <p class="step-description">
          Copy each prompt to external AI models (Claude, GPT-4, etc.), then paste responses back for local evaluation.
          MAX 3 responses per prompt, can stop early if quality ≥75%.
        </p>

        <div class="prompts-with-responses">
          <div
            v-for="(prompt, themeId) in deepPrompts.prompts || {}"
            :key="themeId"
            class="prompt-response-section"
          >
            <!-- Prompt Display -->
            <div class="prompt-card-header">
              <h3>{{ prompt.prompt_title }}</h3>
              <button @click="copyPrompt(prompt.comprehensive_prompt)" class="btn-copy-prompt">
                📋 Copy Prompt
              </button>
            </div>

            <!-- Response Collection Area -->
            <div class="response-collection-area">
              <h4>📥 Responses ({{ getResponsesForPrompt(themeId).length }} / max 3)</h4>

              <!-- Existing Responses with Live Evaluation -->
              <div v-if="getResponsesForPrompt(themeId).length > 0" class="existing-responses">
                <div
                  v-for="(resp, idx) in getResponsesForPrompt(themeId)"
                  :key="idx"
                  class="response-item"
                >
                  <div class="response-header">
                    <span class="response-model">{{ resp.model_name }}</span>
                    <div class="response-scores">
                      <span class="score-badge relevance">
                        Relevance: {{ resp.evaluation.relevance_score }}%
                      </span>
                      <span class="score-badge accuracy">
                        Accuracy: {{ resp.evaluation.accuracy_score }}%
                      </span>
                    </div>
                  </div>
                  <div class="response-preview">{{ resp.response_text.substring(0, 150) }}...</div>
                </div>

                <!-- Quality Assessment -->
                <div :class="['quality-status', getQualityStatus(themeId)]">
                  <span class="status-icon">{{ getQualityIcon(themeId) }}</span>
                  <span>{{ getQualityMessage(themeId) }}</span>
                </div>
              </div>

              <!-- Add New Response Form -->
              <div v-if="canAddMoreResponses(themeId)" class="add-response-form">
                <div class="form-row">
                  <label>AI Model:</label>
                  <select v-model="newResponse[themeId].model" class="input-select-small">
                    <option value="claude-opus">Claude Opus</option>
                    <option value="gpt4">GPT-4</option>
                    <option value="gemini-pro">Gemini Pro</option>
                    <option value="perplexity">Perplexity</option>
                    <option value="other">Other</option>
                  </select>
                </div>

                <div class="form-row">
                  <label>Paste Response (Text):</label>
                  <textarea
                    v-model="newResponse[themeId].text"
                    placeholder="Paste the AI model's deep research response here...&#10;&#10;Local model will evaluate for:&#10;- Relevance (how relevant for your goal)&#10;- Accuracy (factual correctness)"
                    rows="8"
                    class="response-textarea"
                  ></textarea>
                </div>

                <button
                  @click="addAndEvaluateResponse(themeId)"
                  :disabled="!newResponse[themeId].text || evaluating"
                  class="btn-add-response"
                >
                  {{ evaluating ? 'Evaluating...' : '✓ Add & Evaluate (Local)' }}
                </button>
              </div>

              <div v-else class="max-responses-reached">
                ⚠️ Maximum 3 responses reached for this prompt
              </div>
            </div>

            <hr class="prompt-separator" />
          </div>
        </div>

        <!-- Overall Progress -->
        <div class="overall-progress">
          <h3>Base Research Progress</h3>
          <div class="progress-stats">
            <div class="stat-item">
              <span class="stat-label">Total Prompts:</span>
              <span class="stat-value">{{ Object.keys(deepPrompts.prompts || {}).length }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Prompts with Responses:</span>
              <span class="stat-value">{{ getPromptsWithResponses() }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Total Responses:</span>
              <span class="stat-value">{{ getTotalResponses() }}</span>
            </div>
          </div>
        </div>

        <div class="step-actions">
          <button @click="currentStep = 2" class="btn-secondary">← Back to Prompts</button>
          <button
            @click="currentStep = 4"
            :disabled="getPromptsWithResponses() < Object.keys(deepPrompts.prompts || {}).length"
            class="btn-primary"
          >
            Continue to Excursive Research →
          </button>
        </div>
      </div>

      <!-- Step 4: Excursive Research -->
      <div v-else-if="currentStep === 4" class="step-panel">
        <h2>🔬 Excursive Research</h2>
        <p class="step-description">
          Analyze collected base researches to identify NEW themes that emerged from the content.
        </p>

        <div class="excursive-placeholder">
          <p>🚧 Excursive Research phase - Coming soon</p>
          <p>This step will analyze all collected researches and suggest new themes found within them.</p>
        </div>

        <div class="step-actions">
          <button @click="currentStep = 3" class="btn-secondary">← Back to Base Research</button>
          <button
            @click="currentStep = 5"
            class="btn-primary"
          >
            Complete Research →
          </button>
        </div>
      </div>

      <!-- Step 5: Complete -->
      <div v-else-if="currentStep === 5" class="step-panel success-panel">
        <div class="success-icon">✅</div>
        <h2>Research Complete!</h2>
        <p class="success-message">All base and excursive research has been collected and evaluated.</p>

        <div class="success-details">
          <div class="detail-item">
            <span class="detail-label">Themes Researched:</span>
            <span class="detail-value">{{ selectedThemes.size }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Prompts Generated:</span>
            <span class="detail-value">{{ Object.keys(deepPrompts.prompts || {}).length }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Total Responses Collected:</span>
            <span class="detail-value">{{ getTotalResponsesCount() }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Average Quality:</span>
            <span class="detail-value">{{ getAverageQuality() }}%</span>
          </div>
        </div>

        <div class="next-steps">
          <h3>Next Steps:</h3>
          <ol>
            <li>Use the Multi-AI Analyzer to synthesize all collected responses</li>
            <li>Generate a comprehensive research report</li>
            <li>Identify consensus and contradictions across models</li>
            <li>Export findings for further analysis</li>
          </ol>
        </div>

        <div class="step-actions">
          <button @click="router.push('/')" class="btn-secondary">Go to Dashboard</button>
          <button @click="resetWizard" class="btn-primary">Create New Research</button>
        </div>
      </div>
    </div>

    <!-- Error Display -->
    <div v-if="error" class="error-banner">
      <span class="error-icon">⚠️</span>
      <span class="error-message">{{ error }}</span>
      <button @click="error = null" class="error-close">×</button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import * as api from '@/api/client'
import ThemeNode from '@/components/ThemeNode.vue'

const router = useRouter()

const steps = [
  { label: 'Describe' },
  { label: 'Themes & Coverage' },
  { label: 'Prompts' },
  { label: 'Base Research' },
  { label: 'Excursive' },
  { label: 'Complete' }
]

const currentStep = ref(0)
const userInput = ref('')
const researchGoal = ref('')
const researchType = ref('product')
const generating = ref(false)
const saving = ref(false)
const error = ref(null)

// New data structures for hierarchical approach
const thematicHierarchy = ref([])
const metadata = ref({})
const selectedThemes = ref(new Set())
const blindspots = ref({ blindspots_detected: [] })
const deepPrompts = ref({ prompts: {} })
const savedResearch = ref({})
const sessionId = ref(null) // For response collection

// Response collection data (integrated into Step 3)
const promptResponses = ref({}) // themeId -> [{ model_name, response_text, evaluation }]
const newResponse = ref({}) // themeId -> { model: '', text: '' }
const evaluating = ref(false)

// External model coverage & blindspot detection
const coverageResponse = ref('')
const coverageAnalysis = ref(null)
// blindspotResponse and showBlindspotSection removed - now integrated into coverage analysis

// Step 0: Quality Helper
const qualityResult = ref(null)

async function evaluateInputQuality() {
  if (!userInput.value || !researchGoal.value) return

  evaluating.value = true
  error.value = null

  try {
    const result = await api.evaluateResearchInputQuality({
      description: userInput.value,
      goal: researchGoal.value,
      research_type: researchType.value
    })

    qualityResult.value = result
    error.value = null
  } catch (err) {
    error.value = `Quality evaluation failed: ${err.message}`
    console.error('Quality evaluation error:', err)
  } finally {
    evaluating.value = false
  }
}

function getQualityScoreClass(score) {
  if (score >= 80) return 'score-excellent'
  if (score >= 60) return 'score-good'
  if (score >= 40) return 'score-medium'
  return 'score-poor'
}

function applyImprovedDescription() {
  if (qualityResult.value?.improved_description) {
    userInput.value = qualityResult.value.improved_description
    qualityResult.value = null // Clear to re-evaluate
    alert('✅ Applied improved description! Click "Evaluate Quality" again to check.')
  }
}

function applyImprovedGoal() {
  if (qualityResult.value?.improved_goal) {
    researchGoal.value = qualityResult.value.improved_goal
    qualityResult.value = null // Clear to re-evaluate
    alert('✅ Applied improved goal! Click "Evaluate Quality" again to check.')
  }
}

async function generateStructure() {
  if (!userInput.value || !researchGoal.value) return

  generating.value = true
  error.value = null

  try {
    const response = await api.generateResearchStructure({
      user_input: userInput.value,
      research_goal: researchGoal.value,
      research_type: researchType.value
    })

    // NEW data structure!
    thematicHierarchy.value = response.thematic_hierarchy || []
    metadata.value = response.metadata || {}

    currentStep.value = 1
  } catch (err) {
    error.value = `Failed to generate structure: ${err.message}`
    console.error('Generation error:', err)
  } finally {
    generating.value = false
  }
}

function toggleThemeSelection({ themeId, selected }) {
  if (selected) {
    selectedThemes.value.add(themeId)
  } else {
    selectedThemes.value.delete(themeId)
  }
  // Force reactivity
  selectedThemes.value = new Set(selectedThemes.value)
}

// Local Blindspot Detection (for automated workflow)
async function runLocalBlindspotDetection() {
  generating.value = true
  error.value = null

  try {
    const response = await api.detectBlindspots({
      thematic_hierarchy: thematicHierarchy.value,
      user_context: userInput.value,
      research_goal: researchGoal.value
    })

    // Auto-add detected blindspots to hierarchy
    if (response.blindspots_detected && response.blindspots_detected.length > 0) {
      response.blindspots_detected.forEach(blindspot => {
        addBlindspotToHierarchy(blindspot)
      })

      // Update metadata
      metadata.value.total_themes = (metadata.value.total_themes || 0) + response.blindspots_detected.length
    }
  } catch (err) {
    error.value = `Failed to detect blindspots: ${err.message}`
    console.error('Blindspot detection error:', err)
  } finally {
    generating.value = false
  }
}

function addBlindspotToHierarchy(blindspot) {
  // Convert blindspot to theme format and add to hierarchy
  const newTheme = {
    theme_id: blindspot.blindspot_id,
    theme_name: blindspot.theme_name,
    description: blindspot.description || 'Identified as a potential gap in research coverage',
    relevance_score: blindspot.relevance_score,
    sub_themes: (blindspot.suggested_sub_themes || []).map((subName, idx) => ({
      theme_id: `${blindspot.blindspot_id}_sub_${idx}`,
      theme_name: subName,
      description: '',
      relevance_score: blindspot.relevance_score - 5,
      sub_themes: []
    }))
  }

  thematicHierarchy.value.push(newTheme)
  // Auto-select high relevance blindspots
  if (blindspot.relevance_score >= 70) {
    selectedThemes.value.add(newTheme.theme_id)
    selectedThemes.value = new Set(selectedThemes.value)
  }
}

async function generatePrompts() {
  if (selectedThemes.value.size === 0) return

  generating.value = true
  error.value = null

  try {
    // Recursively collect all selected themes
    const selected = getAllSelectedThemes(thematicHierarchy.value)

    const response = await api.generateDeepPrompts({
      selected_themes: selected,
      research_context: userInput.value
    })

    deepPrompts.value = response

    // Initialize newResponse for each prompt
    Object.keys(response.prompts || {}).forEach(themeId => {
      newResponse.value[themeId] = { model: 'claude-opus', text: '' }
      promptResponses.value[themeId] = []
    })

    currentStep.value = 2  // Go to Prompts step (was 3, now 2)
  } catch (err) {
    error.value = `Failed to generate prompts: ${err.message}`
    console.error('Prompt generation error:', err)
  } finally {
    generating.value = false
  }
}

async function proceedToResponseCollection() {
  generating.value = true
  error.value = null

  try {
    // Create research session for response collection
    const session = await api.createResearchSession({
      research_id: `research_${researchType.value}_${Date.now()}`,
      deep_prompts: deepPrompts.value.prompts
    })

    sessionId.value = session.session_id
    currentStep.value = 4
  } catch (err) {
    error.value = `Failed to create session: ${err.message}`
    console.error('Session creation error:', err)
  } finally {
    generating.value = false
  }
}

function handleResponseCollectionComplete(sessionData) {
  // Save the collected responses and proceed to final step
  savedResearch.value = {
    ...savedResearch.value,
    sessionData
  }
  currentStep.value = 5
}

// Helper: Recursively collect all selected themes
function getAllSelectedThemes(themes) {
  const result = []

  for (const theme of themes) {
    if (selectedThemes.value.has(theme.theme_id)) {
      result.push(theme)
    }

    if (theme.sub_themes && theme.sub_themes.length) {
      result.push(...getAllSelectedThemes(theme.sub_themes))
    }
  }

  return result
}

async function saveResearch() {
  saving.value = true
  error.value = null

  try {
    const response = await api.saveResearch({
      research_name: `Research_${researchType.value}_${Date.now()}`,
      user_input: userInput.value,
      thematic_hierarchy: thematicHierarchy.value,
      deep_prompts: deepPrompts.value
    })

    savedResearch.value = response
    currentStep.value = 4
  } catch (err) {
    error.value = `Failed to save research: ${err.message}`
    console.error('Save error:', err)
  } finally {
    saving.value = false
  }
}

async function copyPrompt(text) {
  try {
    await navigator.clipboard.writeText(text)
    // Show temporary success feedback
    const tempError = error.value
    error.value = null
    setTimeout(() => {
      if (!tempError) {
        // You could use a toast notification here instead
        alert('Prompt copied to clipboard!')
      }
    }, 100)
  } catch (err) {
    error.value = 'Failed to copy to clipboard'
  }
}

function exportPrompt(themeId, prompt) {
  const blob = new Blob([prompt.comprehensive_prompt], { type: 'text/markdown' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${themeId}_research_prompt.md`
  a.click()
  URL.revokeObjectURL(url)
}

function getTotalResponsesCount() {
  if (!savedResearch.value.sessionData?.progress) return 0
  return Object.values(savedResearch.value.sessionData.progress).reduce(
    (sum, p) => sum + (p.total_responses || 0),
    0
  )
}

function getAverageQuality() {
  if (!savedResearch.value.sessionData?.progress) return 0
  const progress = Object.values(savedResearch.value.sessionData.progress)
  if (progress.length === 0) return 0

  const avgRelevance = progress.reduce((sum, p) => sum + (p.avg_relevance || 0), 0) / progress.length
  const avgAccuracy = progress.reduce((sum, p) => sum + (p.avg_accuracy || 0), 0) / progress.length

  return Math.round((avgRelevance + avgAccuracy) / 2)
}

// Response Collection Functions (integrated in Step 3)
function getResponsesForPrompt(themeId) {
  return promptResponses.value[themeId] || []
}

function canAddMoreResponses(themeId) {
  const responses = getResponsesForPrompt(themeId)
  return responses.length < 3
}

async function addAndEvaluateResponse(themeId) {
  const responseData = newResponse.value[themeId]
  if (!responseData.text) return

  evaluating.value = true
  error.value = null

  try {
    // Call backend to evaluate response
    const result = await api.evaluateResponse({
      prompt: deepPrompts.value.prompts[themeId].comprehensive_prompt,
      response_text: responseData.text,
      model_name: responseData.model,
      user_context: userInput.value
    })

    // Add to promptResponses
    if (!promptResponses.value[themeId]) {
      promptResponses.value[themeId] = []
    }

    promptResponses.value[themeId].push({
      model_name: responseData.model,
      response_text: responseData.text,
      evaluation: result.evaluation
    })

    // Clear form
    newResponse.value[themeId] = { model: 'claude-opus', text: '' }
  } catch (err) {
    error.value = `Failed to evaluate response: ${err.message}`
    console.error('Evaluation error:', err)
  } finally {
    evaluating.value = false
  }
}

function getQualityStatus(themeId) {
  const responses = getResponsesForPrompt(themeId)
  if (responses.length === 0) return 'no-responses'

  const avgRelevance = responses.reduce((sum, r) => sum + r.evaluation.relevance_score, 0) / responses.length
  const avgAccuracy = responses.reduce((sum, r) => sum + r.evaluation.accuracy_score, 0) / responses.length

  if (avgRelevance >= 75 && avgAccuracy >= 75) return 'good'
  if (responses.length >= 3) return 'max-reached'
  return 'needs-more'
}

function getQualityIcon(themeId) {
  const status = getQualityStatus(themeId)
  if (status === 'good') return '🟢'
  if (status === 'max-reached') return '⚠️'
  return '🟡'
}

function getQualityMessage(themeId) {
  const status = getQualityStatus(themeId)
  const responses = getResponsesForPrompt(themeId)

  if (status === 'good') {
    return 'Quality threshold met! You can proceed or add more models.'
  }
  if (status === 'max-reached') {
    return 'Maximum responses reached. Quality may be below threshold.'
  }
  return `Consider adding ${3 - responses.length} more response(s) to improve quality.`
}

function getPromptsWithResponses() {
  return Object.keys(promptResponses.value).filter(
    themeId => (promptResponses.value[themeId] || []).length > 0
  ).length
}

function getTotalResponses() {
  return Object.values(promptResponses.value).reduce(
    (sum, responses) => sum + responses.length,
    0
  )
}

function completeResearch() {
  // Save all collected responses
  savedResearch.value = {
    thematic_hierarchy: thematicHierarchy.value,
    deep_prompts: deepPrompts.value,
    responses: promptResponses.value
  }

  currentStep.value = 3  // Go to Done step (was 4, now 3)
}

// Coverage Calculation (fallback - real coverage comes from external model)
function calculateCoverage() {
  if (coverageAnalysis.value) {
    return coverageAnalysis.value.coverage_percentage
  }

  // Fallback before external analysis
  const totalThemes = metadata.value.total_themes || 0
  if (totalThemes === 0) return 0
  const estimatedIdeal = Math.max(totalThemes * 1.2, 10)
  return Math.min(Math.round((totalThemes / estimatedIdeal) * 100), 100)
}

function getCoverageClass() {
  const coverage = calculateCoverage()
  if (coverage >= 80) return 'coverage-good'
  if (coverage >= 60) return 'coverage-medium'
  return 'coverage-low'
}

function getCoverageResultClass() {
  const coverage = coverageAnalysis.value?.coverage_percentage || 0
  if (coverage >= 80) return 'score-good'
  if (coverage >= 60) return 'score-medium'
  return 'score-low'
}

// External Model Coverage Check (Text-based, NOT JSON)
async function copyCoveragePrompt() {
  const themesJson = JSON.stringify(thematicHierarchy.value, null, 2)

  const prompt = `# DEEP COVERAGE ANALYSIS

## USER'S RESEARCH GOAL
${researchGoal.value}

## CURRENT THEMATIC STRUCTURE
${themesJson}

## YOUR TASK
You are an expert analyst in ${researchType.value} research. Perform a DEEP analysis of how well the current thematic structure enables achieving the user's stated goal.

Write a detailed analysis covering:

1. **Coverage Assessment** (estimate percentage 0-100%):
   - How comprehensively does this structure address the goal?
   - What's your confidence in this coverage estimate?

2. **Well-Covered Aspects**:
   - Which critical aspects ARE adequately addressed by current themes?
   - List specific examples

3. **Missing Critical Aspects**:
   - What ESSENTIAL aspects are missing that prevent achieving the goal?
   - Be specific and prioritize by importance
   - Consider: Are there regulatory, technical, market, or operational aspects missing?

4. **Recommendations**:
   - What specific themes should be added?
   - Why are they critical for the goal?
   - Suggest concrete theme names and descriptions

Be CRITICAL and goal-oriented. Write in natural language - I will analyze your response locally.`

  try {
    await navigator.clipboard.writeText(prompt)
    error.value = null
    alert('✅ Coverage analysis prompt copied! Paste it to Claude, GPT-4, or another flagship model, then paste the response back.')
  } catch (err) {
    error.value = 'Failed to copy to clipboard'
  }
}

// Process External Coverage Response with LOCAL Analysis
async function processCoverageAnalysis() {
  if (!coverageResponse.value.trim()) {
    error.value = 'Please paste the coverage analysis response from your external model.'
    return
  }

  generating.value = true
  error.value = null

  try {
    // Send external text to LOCAL model for analysis
    const response = await api.analyzeCoverageResponse({
      external_response: coverageResponse.value,
      current_themes: thematicHierarchy.value,
      research_goal: researchGoal.value,
      research_type: researchType.value
    })

    // Local model extracts structured data from external text
    coverageAnalysis.value = {
      coverage_percentage: response.coverage_percentage,
      covered_aspects: response.covered_aspects || [],
      missing_critical_aspects: response.missing_critical_aspects || [],
      rationale: response.rationale || '',
      recommendation: response.recommendation || '',
      suggested_themes: response.suggested_themes || [],
      verified: false  // Mark as unverified for later validation
    }

    // Update metadata
    metadata.value.external_coverage = response.coverage_percentage

    // Auto-add suggested themes if provided and coverage < 80%
    if (response.suggested_themes && response.suggested_themes.length > 0 && response.coverage_percentage < 80) {
      response.suggested_themes.forEach(theme => {
        thematicHierarchy.value.push({
          ...theme,
          verified: false  // Mark new themes as unverified
        })
        if (theme.relevance_score >= 70) {
          selectedThemes.value.add(theme.theme_id)
        }
      })
      selectedThemes.value = new Set(selectedThemes.value)
      metadata.value.total_themes = (metadata.value.total_themes || 0) + response.suggested_themes.length

      alert(`✅ Added ${response.suggested_themes.length} new themes! Coverage now: ${response.coverage_percentage}%\n\n${response.coverage_percentage < 80 ? 'Run coverage analysis again to continue improving.' : 'Coverage goal reached!'}`)
    }

    // Clear response field for next iteration
    if (response.coverage_percentage < 80) {
      coverageResponse.value = ''
    }

    error.value = null
  } catch (err) {
    error.value = `Failed to analyze coverage response: ${err.message}`
    console.error('Coverage analysis error:', err)
  } finally {
    generating.value = false
  }
}

// OLD: Separate blindspot detection removed - now integrated into coverage analysis
// The coverage analyzer automatically suggests new themes based on missing aspects

function resetWizard() {
  currentStep.value = 0
  userInput.value = ''
  researchType.value = 'product'
  thematicHierarchy.value = []
  metadata.value = {}
  selectedThemes.value = new Set()
  blindspots.value = { blindspots_detected: [] }
  deepPrompts.value = { prompts: {} }
  savedResearch.value = {}
  sessionId.value = null
  promptResponses.value = {}
  newResponse.value = {}
  error.value = null
}
</script>

<style scoped>
.research-creator {
  max-width: 1400px;
  margin: 2rem auto;
  padding: 0 2rem;
  min-height: calc(100vh - 140px);
}

/* Step Indicator */
.wizard-steps {
  display: flex;
  justify-content: center;
  gap: 1.5rem;
  margin-bottom: 3rem;
  position: relative;
}

.wizard-steps::before {
  content: '';
  position: absolute;
  top: 20px;
  left: 15%;
  right: 15%;
  height: 2px;
  background: var(--border-medium);
  z-index: -1;
}

.step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.step-number {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--bg-panel);
  border: 2px solid var(--border-medium);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  color: var(--text-muted);
  transition: all 0.3s;
}

.step.active .step-number {
  background: var(--accent-gold);
  border-color: var(--accent-gold);
  color: var(--bg-panel);
}

.step.completed .step-number {
  background: #22c55e;
  border-color: #22c55e;
  color: white;
}

.step-label {
  font-size: 0.9rem;
  color: var(--text-muted);
  font-weight: 500;
}

.step.active .step-label {
  color: var(--accent-gold);
  font-weight: 600;
}

/* Step Content */
.step-content {
  background: var(--bg-panel);
  border: 2px solid var(--border-medium);
  border-radius: 12px;
  padding: 2rem;
  min-height: 500px;
}

.step-panel h2 {
  margin: 0 0 0.5rem 0;
  color: var(--text-main);
  font-size: 1.8rem;
}

.step-description {
  color: var(--text-muted);
  margin-bottom: 2rem;
  font-size: 1rem;
}

/* Form Elements */
.input-textarea {
  width: 100%;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-medium);
  border-radius: 8px;
  color: var(--text-main);
  font-size: 1rem;
  font-family: inherit;
  resize: vertical;
  margin-bottom: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-label {
  display: block;
  margin-bottom: 0.5rem;
  color: var(--text-main);
  font-weight: 600;
  font-size: 0.95rem;
}

/* Step 0: Quality Helper */
.quality-helper-section {
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(79, 70, 229, 0.05) 100%);
  border: 2px solid var(--accent-purple);
  border-radius: 12px;
  padding: 2rem;
  margin: 2rem 0;
}

.quality-helper-section h3 {
  color: var(--accent-purple);
  margin-bottom: 0.5rem;
}

.btn-evaluate-quality {
  background: linear-gradient(135deg, var(--accent-purple) 0%, #6366f1 100%);
  color: white;
  padding: 1rem 2rem;
  border: none;
  border-radius: 8px;
  font-weight: 700;
  cursor: pointer;
  margin: 1rem 0;
  width: 100%;
  transition: all 0.3s;
}

.btn-evaluate-quality:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(139, 92, 246, 0.4);
}

.btn-evaluate-quality:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.quality-results {
  margin-top: 1.5rem;
}

.quality-score-badge {
  text-align: center;
  padding: 2rem;
  border-radius: 12px;
  margin-bottom: 1.5rem;
}

.quality-score-badge.score-excellent {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(16, 185, 129, 0.1) 100%);
  border: 3px solid #10b981;
}

.quality-score-badge.score-good {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.2) 0%, rgba(59, 130, 246, 0.1) 100%);
  border: 3px solid #3b82f6;
}

.quality-score-badge.score-medium {
  background: linear-gradient(135deg, rgba(251, 191, 36, 0.2) 0%, rgba(251, 191, 36, 0.1) 100%);
  border: 3px solid #fbbf24;
}

.quality-score-badge.score-poor {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(239, 68, 68, 0.1) 100%);
  border: 3px solid #ef4444;
}

.score-number {
  display: block;
  font-size: 3rem;
  font-weight: 900;
  margin-bottom: 0.5rem;
}

.score-label {
  display: block;
  font-size: 1rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
  opacity: 0.8;
}

.sub-scores {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.sub-score-item {
  flex: 1;
  background: rgba(0, 0, 0, 0.2);
  padding: 1rem;
  border-radius: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sub-score-item .label {
  font-weight: 600;
  color: var(--text-light);
}

.sub-score-item .score {
  font-weight: 900;
  font-size: 1.2rem;
}

.sub-score-item .score.score-excellent { color: #10b981; }
.sub-score-item .score.score-good { color: #3b82f6; }
.sub-score-item .score.score-medium { color: #fbbf24; }
.sub-score-item .score.score-poor { color: #ef4444; }

.quality-list {
  background: rgba(0, 0, 0, 0.2);
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 1rem;
}

.quality-list h4 {
  margin-bottom: 1rem;
  font-size: 1.1rem;
}

.quality-list ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.quality-list li {
  padding: 0.75rem;
  margin: 0.5rem 0;
  border-radius: 6px;
  line-height: 1.6;
}

.strengths-list li {
  background: rgba(16, 185, 129, 0.1);
  border-left: 3px solid #10b981;
}

.weaknesses-list li {
  background: rgba(239, 68, 68, 0.1);
  border-left: 3px solid #ef4444;
}

.suggestions-list li {
  background: rgba(59, 130, 246, 0.1);
  border-left: 3px solid #3b82f6;
}

.improved-versions {
  background: rgba(139, 92, 246, 0.1);
  border: 2px solid var(--accent-purple);
  border-radius: 8px;
  padding: 1.5rem;
  margin-top: 1.5rem;
}

.improved-versions h4 {
  color: var(--accent-purple);
  margin-bottom: 1rem;
}

.improved-field {
  margin-bottom: 1.5rem;
}

.improved-field label {
  display: block;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: var(--text-light);
}

.improved-text {
  background: rgba(0, 0, 0, 0.3);
  padding: 1rem;
  border-radius: 6px;
  border-left: 3px solid var(--accent-purple);
  margin-bottom: 0.75rem;
  line-height: 1.6;
  white-space: pre-wrap;
}

.btn-apply {
  background: var(--accent-purple);
  color: white;
  padding: 0.5rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-apply:hover {
  background: #7c3aed;
  transform: translateY(-1px);
}

.field-hint {
  margin-top: 0.5rem;
  margin-bottom: 0;
  font-size: 0.85rem;
  color: var(--text-muted);
  font-style: italic;
}

.form-group label {
  display: block;
  color: var(--text-muted);
  margin-bottom: 0.5rem;
  font-weight: 600;
}

.input-select {
  width: 100%;
  max-width: 300px;
  padding: 0.75rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-medium);
  border-radius: 8px;
  color: var(--text-main);
  font-size: 1rem;
}

/* Metadata Bar */
.metadata-bar {
  display: flex;
  gap: 2rem;
  padding: 1rem 1.5rem;
  background: rgba(255, 179, 71, 0.1);
  border: 1px solid var(--accent-gold);
  border-radius: 8px;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-light);
  font-size: 0.95rem;
}

.meta-icon {
  font-size: 1.1rem;
}

/* Theme Tree */
.theme-tree {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  max-height: 500px;
  overflow-y: auto;
}

/* Selection Summary */
.selection-summary {
  display: flex;
  gap: 2rem;
  padding: 1rem 1.5rem;
  background: rgba(34, 197, 94, 0.1);
  border: 1px solid #22c55e;
  border-radius: 8px;
  margin-bottom: 1.5rem;
}

.summary-stat {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.stat-label {
  color: var(--text-muted);
  font-size: 0.95rem;
}

.stat-value {
  color: #22c55e;
  font-size: 1.5rem;
  font-weight: 700;
}

/* Blindspots */
.recommendation-box {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.5rem;
  background: rgba(59, 130, 246, 0.15);
  border: 1px solid #3b82f6;
  border-radius: 8px;
  margin-bottom: 2rem;
  color: var(--text-light);
  font-size: 1rem;
}

.recommendation-icon {
  font-size: 1.5rem;
}

.blindspots-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 2rem;
  max-height: 500px;
  overflow-y: auto;
}

.blindspot-card {
  background: rgba(255, 255, 255, 0.03);
  border: 2px solid var(--border-medium);
  border-radius: 10px;
  padding: 1.5rem;
  transition: all 0.2s;
}

.blindspot-card.severity-high {
  border-color: #ef4444;
  background: rgba(239, 68, 68, 0.05);
}

.blindspot-card.severity-medium {
  border-color: #eab308;
  background: rgba(234, 179, 8, 0.05);
}

.blindspot-card.severity-low {
  border-color: #3b82f6;
  background: rgba(59, 130, 246, 0.05);
}

.blindspot-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.blindspot-header h3 {
  margin: 0;
  flex: 1;
  color: var(--text-main);
  font-size: 1.2rem;
}

.severity-badge {
  padding: 0.25rem 0.6rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.severity-badge.high {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.severity-badge.medium {
  background: rgba(234, 179, 8, 0.2);
  color: #eab308;
}

.severity-badge.low {
  background: rgba(59, 130, 246, 0.2);
  color: #3b82f6;
}

.blindspot-description {
  color: var(--text-light);
  margin-bottom: 1rem;
  line-height: 1.5;
}

.suggested-subs {
  margin-bottom: 1rem;
}

.subs-label {
  display: block;
  color: var(--text-muted);
  font-size: 0.85rem;
  margin-bottom: 0.5rem;
}

.subs-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.sub-tag {
  background: rgba(255, 179, 71, 0.2);
  color: var(--accent-gold);
  padding: 0.25rem 0.6rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 600;
}

.btn-add-blindspot {
  background: var(--accent-gold);
  color: var(--bg-panel);
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-add-blindspot:hover {
  background: var(--accent-orange);
  transform: translateY(-2px);
}

/* Prompts Grid */
.prompts-grid {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin-bottom: 2rem;
  max-height: 550px;
  overflow-y: auto;
}

.prompt-card {
  background: rgba(255, 255, 255, 0.03);
  border: 2px solid var(--border-medium);
  border-radius: 10px;
  padding: 1.5rem;
  transition: all 0.2s;
}

.prompt-card:hover {
  border-color: var(--accent-gold);
}

.prompt-header h4 {
  margin: 0 0 1rem 0;
  color: var(--accent-gold);
  font-size: 1.2rem;
}

.prompt-meta {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 1rem;
}

.meta-tag {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-muted);
  font-size: 0.9rem;
}

.prompt-models {
  margin-bottom: 1rem;
}

.models-label {
  display: block;
  color: var(--text-muted);
  font-size: 0.85rem;
  margin-bottom: 0.5rem;
}

.models-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.model-tag {
  background: rgba(59, 130, 246, 0.2);
  color: #3b82f6;
  padding: 0.25rem 0.6rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
}

.prompt-preview {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 6px;
  padding: 1rem;
  margin-bottom: 1rem;
  max-height: 200px;
  overflow: auto;
}

.prompt-preview pre {
  margin: 0;
  color: var(--text-light);
  font-size: 0.85rem;
  line-height: 1.5;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.prompt-actions {
  display: flex;
  gap: 0.75rem;
}

.btn-icon {
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-light);
  border: 1px solid var(--border-medium);
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-icon:hover {
  background: rgba(255, 179, 71, 0.2);
  border-color: var(--accent-gold);
  color: var(--accent-gold);
}

/* Success Panel */
.success-panel {
  text-align: center;
  padding: 3rem 2rem;
}

.success-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.success-message {
  color: var(--text-light);
  font-size: 1.1rem;
  margin-bottom: 2rem;
}

.success-details {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  max-width: 600px;
  margin: 0 auto 2rem;
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.detail-label {
  color: var(--text-muted);
}

.detail-value {
  color: var(--accent-gold);
  font-weight: 600;
  word-break: break-all;
}

.next-steps {
  max-width: 600px;
  margin: 0 auto 2rem;
  text-align: left;
  background: rgba(59, 130, 246, 0.1);
  padding: 1.5rem;
  border-radius: 8px;
}

.next-steps h3 {
  margin: 0 0 1rem 0;
  color: var(--text-main);
}

.next-steps ol {
  margin: 0;
  padding-left: 1.5rem;
  color: var(--text-light);
  line-height: 1.8;
}

/* Step Actions */
.step-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 2rem;
  flex-wrap: wrap;
}

.btn-primary,
.btn-secondary,
.btn-tertiary {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: var(--accent-gold);
  color: var(--bg-panel);
}

.btn-primary:hover:not(:disabled) {
  background: var(--accent-orange);
  transform: translateY(-2px);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-light);
  border: 1px solid var(--border-medium);
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.15);
}

.btn-tertiary {
  background: rgba(59, 130, 246, 0.2);
  color: #3b82f6;
  border: 1px solid #3b82f6;
}

.btn-tertiary:hover:not(:disabled) {
  background: rgba(59, 130, 246, 0.3);
}

.btn-tertiary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Response Collection Styles */
.prompts-with-responses {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.prompt-response-section {
  background: var(--bg-panel);
  padding: 1.5rem;
  border-radius: 12px;
  border: 1px solid var(--border-medium);
}

.prompt-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.prompt-card-header h3 {
  margin: 0;
  color: var(--text-main);
  font-size: 1.25rem;
}

.btn-copy-prompt {
  padding: 0.5rem 1rem;
  background: rgba(59, 130, 246, 0.2);
  color: #3b82f6;
  border: 1px solid #3b82f6;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.btn-copy-prompt:hover {
  background: rgba(59, 130, 246, 0.3);
  transform: translateY(-1px);
}

/* Step 2: Prompts List */
.prompts-list {
  margin: 2rem 0;
}

.prompt-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-medium);
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.prompts-summary {
  background: rgba(79, 70, 229, 0.1);
  border: 2px solid var(--accent-purple);
  border-radius: 8px;
  padding: 1.5rem;
  margin: 2rem 0;
  text-align: center;
}

.prompts-summary p {
  margin: 0;
  color: var(--text-light);
  font-size: 1.1rem;
}

/* Step 4: Excursive Research */
.excursive-placeholder {
  background: rgba(255, 179, 71, 0.1);
  border: 2px dashed var(--accent-gold);
  border-radius: 12px;
  padding: 3rem;
  text-align: center;
  margin: 2rem 0;
}

.excursive-placeholder p {
  color: var(--text-muted);
  font-size: 1.1rem;
  margin: 0.5rem 0;
}

.prompt-preview-box {
  background: rgba(0, 0, 0, 0.3);
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  border-left: 3px solid var(--accent-gold);
  max-height: 400px;
  overflow-y: auto;
}

.prompt-preview-box pre {
  margin: 0;
  color: var(--text-light);
  font-size: 0.85rem;
  white-space: pre-wrap;
  font-family: 'Consolas', 'Monaco', monospace;
}

.response-collection-area {
  background: rgba(0, 0, 0, 0.2);
  padding: 1.5rem;
  border-radius: 8px;
}

.response-collection-area h4 {
  margin: 0 0 1rem 0;
  color: var(--text-main);
}

.existing-responses {
  margin-bottom: 1.5rem;
}

.response-item {
  background: rgba(255, 255, 255, 0.05);
  padding: 1rem;
  border-radius: 6px;
  margin-bottom: 0.75rem;
  border-left: 3px solid var(--accent-gold);
}

.response-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.response-model {
  font-weight: 600;
  color: var(--accent-gold);
}

.response-scores {
  display: flex;
  gap: 0.75rem;
}

.score-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 4px;
  font-size: 0.85rem;
  font-weight: 600;
}

.score-badge.relevance {
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
}

.score-badge.accuracy {
  background: rgba(59, 130, 246, 0.2);
  color: #3b82f6;
}

.response-preview {
  color: var(--text-light);
  font-size: 0.9rem;
  font-style: italic;
}

.quality-status {
  padding: 1rem;
  border-radius: 6px;
  margin-top: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 500;
}

.quality-status.good {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.quality-status.max-reached {
  background: rgba(251, 191, 36, 0.1);
  color: #fbbf24;
  border: 1px solid rgba(251, 191, 36, 0.3);
}

.quality-status.needs-more {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
  border: 1px solid rgba(59, 130, 246, 0.3);
}

.add-response-form {
  margin-top: 1rem;
}

.form-row {
  margin-bottom: 1rem;
}

.form-row label {
  display: block;
  margin-bottom: 0.5rem;
  color: var(--text-main);
  font-weight: 500;
}

.input-select-small {
  width: 200px;
  padding: 0.5rem;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid var(--border-medium);
  border-radius: 6px;
  color: var(--text-main);
  font-size: 1rem;
}

.response-textarea {
  width: 100%;
  padding: 0.75rem;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid var(--border-medium);
  border-radius: 6px;
  color: var(--text-main);
  font-size: 0.95rem;
  font-family: inherit;
  resize: vertical;
}

.btn-add-response {
  padding: 0.75rem 1.5rem;
  background: var(--accent-gold);
  color: var(--bg-panel);
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-add-response:hover:not(:disabled) {
  background: var(--accent-orange);
  transform: translateY(-2px);
}

.btn-add-response:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.max-responses-reached {
  padding: 1rem;
  background: rgba(251, 191, 36, 0.1);
  border: 1px solid rgba(251, 191, 36, 0.3);
  border-radius: 6px;
  color: #fbbf24;
  text-align: center;
  font-weight: 500;
}

.prompt-separator {
  border: none;
  border-top: 1px solid var(--border-medium);
  margin: 2rem 0;
}

.overall-progress {
  background: var(--bg-panel);
  padding: 1.5rem;
  border-radius: 12px;
  border: 1px solid var(--border-medium);
  margin-bottom: 2rem;
}

.overall-progress h3 {
  margin: 0 0 1rem 0;
  color: var(--text-main);
}

.progress-stats {
  display: flex;
  gap: 2rem;
  flex-wrap: wrap;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.stat-label {
  color: var(--text-light);
  font-size: 0.85rem;
}

.stat-value {
  color: var(--accent-gold);
  font-size: 1.5rem;
  font-weight: 700;
}

/* External Model Coverage & Blindspot Styles */
.external-coverage-section {
  background: var(--bg-panel);
  border: 2px solid var(--border-medium);
  border-radius: 12px;
  padding: 2rem;
  margin: 2rem 0;
}

.external-coverage-section h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-main);
}

.section-hint {
  color: var(--text-muted);
  font-size: 0.9rem;
  margin-bottom: 1.5rem;
}

.btn-copy-prompt-large {
  width: 100%;
  padding: 1rem;
  background: rgba(59, 130, 246, 0.2);
  color: #3b82f6;
  border: 2px solid #3b82f6;
  border-radius: 8px;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 1.5rem;
}

.btn-copy-prompt-large:hover {
  background: rgba(59, 130, 246, 0.3);
  transform: translateY(-2px);
}

.paste-response-area {
  margin: 1.5rem 0;
}

.paste-response-area label {
  display: block;
  margin-bottom: 0.5rem;
  color: var(--text-main);
  font-weight: 600;
}

.response-textarea-large {
  width: 100%;
  padding: 1rem;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid var(--border-medium);
  border-radius: 8px;
  color: var(--text-main);
  font-size: 0.95rem;
  font-family: 'Consolas', 'Monaco', monospace;
  resize: vertical;
  margin-bottom: 0.75rem;
}

.btn-process {
  width: 100%;
  padding: 0.75rem;
  background: var(--accent-gold);
  color: var(--bg-panel);
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-process:hover:not(:disabled) {
  background: var(--accent-orange);
  transform: translateY(-2px);
}

.btn-process:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.coverage-results {
  margin-top: 2rem;
  padding: 1.5rem;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
}

.coverage-score-display {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  font-size: 1.5rem;
  font-weight: 700;
}

.coverage-score-display.score-good {
  background: rgba(16, 185, 129, 0.2);
  border: 2px solid #10b981;
  color: #10b981;
}

.coverage-score-display.score-medium {
  background: rgba(251, 191, 36, 0.2);
  border: 2px solid #fbbf24;
  color: #fbbf24;
}

.coverage-score-display.score-low {
  background: rgba(239, 68, 68, 0.2);
  border: 2px solid #ef4444;
  color: #ef4444;
}

.covered-list,
.missing-list {
  margin: 1rem 0;
  padding: 1rem;
  border-radius: 6px;
}

.covered-list {
  background: rgba(16, 185, 129, 0.1);
  border-left: 3px solid #10b981;
}

.covered-list h4 {
  margin: 0 0 0.75rem 0;
  color: #10b981;
}

.missing-list {
  background: rgba(239, 68, 68, 0.1);
  border-left: 3px solid #ef4444;
}

.missing-list h4 {
  margin: 0 0 0.75rem 0;
  color: #ef4444;
}

.covered-list ul,
.missing-list ul {
  margin: 0;
  padding-left: 1.5rem;
  color: var(--text-light);
}

.covered-list li,
.missing-list li {
  margin-bottom: 0.5rem;
}

.rationale-box,
.recommendation-box-new {
  padding: 1rem;
  border-radius: 6px;
  margin: 1rem 0;
}

.rationale-box {
  background: rgba(59, 130, 246, 0.1);
  border-left: 3px solid #3b82f6;
  color: var(--text-light);
}

.recommendation-box-new {
  background: rgba(251, 191, 36, 0.1);
  border-left: 3px solid #fbbf24;
  color: var(--text-light);
}

.blindspot-section {
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 2px solid var(--border-medium);
}

.blindspot-section h4 {
  margin: 0 0 0.5rem 0;
  color: var(--text-main);
}

.blindspot-section p {
  color: var(--text-muted);
  margin-bottom: 1.5rem;
}

.coverage-warning-box {
  background: rgba(251, 191, 36, 0.1);
  border: 2px solid #fbbf24;
  border-radius: 8px;
  padding: 1.5rem;
  margin-top: 2rem;
}

.coverage-warning-box h4 {
  color: #fbbf24;
  margin-bottom: 1rem;
  font-size: 1.2rem;
}

.coverage-warning-box p {
  color: var(--text-light);
  margin: 0.5rem 0;
  line-height: 1.6;
}

.coverage-warning-box .action-hint {
  margin-top: 1rem;
  padding: 1rem;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 6px;
  border-left: 3px solid #fbbf24;
}

.coverage-good-large {
  background: rgba(16, 185, 129, 0.2);
  border: 2px solid #10b981;
  border-radius: 8px;
  padding: 1.5rem;
  margin-top: 2rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  color: #10b981;
  font-weight: 600;
  font-size: 1.1rem;
}

.check-icon-large {
  font-size: 2rem;
}

/* Coverage & Blindspot Styles */
.coverage-item.coverage-good {
  color: #10b981;
  font-weight: 600;
}

.coverage-item.coverage-medium {
  color: #f59e0b;
  font-weight: 600;
}

.coverage-item.coverage-low {
  color: #ef4444;
  font-weight: 600;
}

.blindspot-alert {
  background: rgba(251, 191, 36, 0.1);
  border: 2px solid rgba(251, 191, 36, 0.3);
  border-radius: 8px;
  padding: 1rem;
  margin: 1rem 0;
}

.alert-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.alert-icon {
  font-size: 1.25rem;
}

.alert-text {
  color: var(--text-main);
  font-weight: 500;
}

.btn-detect-blindspots {
  width: 100%;
  padding: 0.75rem;
  background: var(--accent-orange);
  color: var(--bg-panel);
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-detect-blindspots:hover:not(:disabled) {
  background: var(--accent-gold);
  transform: translateY(-2px);
}

.btn-detect-blindspots:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.coverage-good {
  background: rgba(16, 185, 129, 0.1);
  border: 2px solid rgba(16, 185, 129, 0.3);
  border-radius: 8px;
  padding: 1rem;
  margin: 1rem 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #10b981;
  font-weight: 600;
}

.check-icon {
  font-size: 1.25rem;
}

/* Error Banner */
.error-banner {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  background: rgba(239, 68, 68, 0.95);
  color: white;
  padding: 1rem 1.5rem;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 1rem;
  max-width: 500px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
  z-index: 1000;
}

.error-close {
  background: none;
  border: none;
  color: white;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0;
  margin-left: auto;
}
</style>
