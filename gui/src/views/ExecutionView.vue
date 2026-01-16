<template>
  <div class="execution-view">
    <div class="execution-header">
      <h2>Workflow Execution</h2>
      <div class="header-actions">
        <select v-model="selectedFrameworkId" class="framework-select">
          <option value="">Select Framework...</option>
          <option v-for="framework in frameworks" :key="framework.framework_id" :value="framework.framework_id">
            {{ framework.name }}
          </option>
        </select>
        <button
          class="execute-btn"
          :disabled="!selectedFrameworkId || isExecuting"
          @click="executeFramework"
        >
          {{ isExecuting ? 'Executing...' : '▶ Execute' }}
        </button>
      </div>
    </div>

    <div v-if="isExecuting || executionHistory.length > 0" class="execution-content">
      <!-- Working State Viewer -->
      <div class="working-state-panel">
        <h3>Execution Progress</h3>

        <!-- Context Window Monitor -->
        <ContextMonitor
          v-if="currentExecution?.working_state?.context"
          :context-info="currentExecution.working_state.context"
          :model-name="currentExecution?.model || 'mistral-7b-instruct'"
        />

        <!-- Iteration Viewer (for Phase 1 Excurse) -->
        <IterationViewer
          v-if="currentExecution?.working_state?.iteration"
          :iteration-state="currentExecution.working_state.iteration"
          :phase-name="currentExecution.working_state.current_phase || 'Phase 1: Excurse'"
        />

        <WorkingStateViewer :execution-state="currentExecution" />
      </div>

      <!-- Output Panel -->
      <div class="output-panel">
        <h3>Output</h3>
        <div class="output-tabs">
          <button
            :class="['tab', { active: activeOutputTab === 'preview' }]"
            @click="activeOutputTab = 'preview'"
          >
            Preview
          </button>
          <button
            :class="['tab', { active: activeOutputTab === 'json' }]"
            @click="activeOutputTab = 'json'"
          >
            JSON
          </button>
          <button
            :class="['tab', { active: activeOutputTab === 'logs' }]"
            @click="activeOutputTab = 'logs'"
          >
            Logs
          </button>
        </div>

        <div class="output-content">
          <div v-if="activeOutputTab === 'preview'" class="output-preview">
            <div v-if="currentExecution?.output?.content" v-html="renderMarkdown(currentExecution.output.content)"></div>
            <div v-else class="no-output">No output yet...</div>
          </div>
          <div v-else-if="activeOutputTab === 'json'" class="output-json">
            <pre>{{ JSON.stringify(currentExecution, null, 2) }}</pre>
          </div>
          <div v-else-if="activeOutputTab === 'logs'" class="output-logs">
            <div v-for="(log, idx) in executionLogs" :key="idx" :class="['log-entry', log.level]">
              <span class="log-time">{{ log.timestamp }}</span>
              <span class="log-message">{{ log.message }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="execution-placeholder">
      <div class="placeholder-content">
        <span class="placeholder-icon">📈</span>
        <h3>No Active Execution</h3>
        <p>Select a framework and click Execute to start</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useOrchestratorStore } from '@/stores/orchestrator'
import WorkingStateViewer from '@/components/WorkingStateViewer.vue'
import ContextMonitor from '@/components/ContextMonitor.vue'
import IterationViewer from '@/components/IterationViewer.vue'

const store = useOrchestratorStore()

const selectedFrameworkId = ref('')
const isExecuting = ref(false)
const activeOutputTab = ref('preview')
const currentExecution = ref(null)
const executionHistory = ref([])
const executionLogs = ref([])

const frameworks = computed(() => store.frameworks)

async function executeFramework() {
  if (!selectedFrameworkId.value) return

  isExecuting.value = true
  executionLogs.value = []

  // Initialize execution state
  currentExecution.value = {
    framework_id: selectedFrameworkId.value,
    model: 'mixtral-8x7b-instruct',
    working_state: {
      status: 'in_progress',
      progress: 0,
      current_step: 'Initializing execution...',
      current_phase: 'Phase 0: Base Research',
      started_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),

      // Context Window Info
      context: {
        loaded_data: [
          { type: 'system_prompt', tokens: 482 },
          { type: 'technique_prompt', tokens: 356 },
          { type: 'user_input', name: 'Product Idea Query', tokens: 142 }
        ],
        total_tokens: 980,
        context_limit: 32768,
        percentage: 3.0,
        safety_status: 'safe',
        output_buffer: 8192
      }
    },
    output: {
      format: 'markdown',
      content: '',
      metadata: {
        confidence_score: 0,
        model_used: '',
        token_count: 0,
        execution_time_ms: 0
      }
    }
  }

  addLog('info', 'Starting framework execution...')

  try {
    // TODO: Call actual execution API
    // For now, simulate execution
    await simulateExecution()

    currentExecution.value.working_state.status = 'completed'
    currentExecution.value.working_state.progress = 100
    addLog('success', 'Execution completed successfully')

    executionHistory.value.unshift({...currentExecution.value})
  } catch (error) {
    currentExecution.value.working_state.status = 'failed'
    addLog('error', `Execution failed: ${error.message}`)
  } finally {
    isExecuting.value = false
  }
}

async function simulateExecution() {
  // Simulate phases
  const phases = [
    { name: 'Base Research', hasIteration: false },
    { name: 'Excurse', hasIteration: true },
    { name: 'Validation', hasIteration: false },
    { name: 'Synthesis', hasIteration: false }
  ]

  for (let i = 0; i < phases.length; i++) {
    const phase = phases[i]
    currentExecution.value.working_state.current_step = `Executing ${phase.name}...`
    currentExecution.value.working_state.current_phase = `Phase ${i}: ${phase.name}`
    currentExecution.value.working_state.progress = Math.floor(((i + 1) / phases.length) * 100)
    currentExecution.value.working_state.updated_at = new Date().toISOString()

    addLog('info', `Phase ${i}/${phases.length - 1}: ${phase.name}`)

    // Update context based on phase
    const previousTokens = i === 0 ? 0 : 2104 + (i * 800)
    currentExecution.value.working_state.context = {
      loaded_data: [
        { type: 'system_prompt', tokens: 482 },
        { type: 'technique_prompt', tokens: 356 + (i * 100) },
        { type: 'user_input', name: 'Product Idea Query', tokens: 142 },
        ...(previousTokens > 0 ? [{ type: 'previous_output', name: `Phase ${i - 1} Output`, tokens: previousTokens }] : [])
      ],
      total_tokens: 980 + previousTokens + (i * 100),
      context_limit: 32768,
      percentage: ((980 + previousTokens + (i * 100)) / 32768 * 100).toFixed(1),
      safety_status: (980 + previousTokens + (i * 100)) < 19661 ? 'safe' : 'warning',
      output_buffer: 8192
    }

    // Simulate iteration for Phase 1 (Excurse)
    if (phase.hasIteration) {
      currentExecution.value.working_state.iteration = {
        current_iteration: 1,
        max_iterations: 3,
        iteration_history: []
      }

      // Iteration 1: Gaps found
      addLog('info', 'Iteration 1: Detecting gaps...')
      await new Promise(resolve => setTimeout(resolve, 1500))

      currentExecution.value.working_state.iteration.iteration_history.push({
        iteration: 1,
        gaps_detected: ['Missing competitor pricing data', 'No user retention metrics'],
        techniques_executed: ['gap_detector', 'quick_web_research'],
        context_loaded: {
          previous_outputs: ['phase_0_output'],
          tokens: 3420
        },
        result: 'gaps_found',
        duration: 12400
      })

      currentExecution.value.working_state.iteration.current_iteration = 2

      // Iteration 2: Filling gaps
      addLog('info', 'Iteration 2: Filling detected gaps...')
      await new Promise(resolve => setTimeout(resolve, 1500))

      currentExecution.value.working_state.iteration.iteration_history.push({
        iteration: 2,
        gaps_detected: [],
        techniques_executed: ['validation_check', 'completeness_check'],
        context_loaded: {
          previous_outputs: ['phase_0_output', 'iteration_1_output'],
          tokens: 5840
        },
        result: 'complete',
        duration: 10200
      })

      addLog('success', 'Phase 1 complete - No more gaps detected')
    } else {
      await new Promise(resolve => setTimeout(resolve, 2000))
    }
  }

  currentExecution.value.output.content = '# Research Results\n\nThis is a simulated output.\n\n## Key Findings\n- Finding 1\n- Finding 2\n- Finding 3'
  currentExecution.value.output.metadata.confidence_score = 0.85
  currentExecution.value.output.metadata.model_used = 'mixtral-8x7b'
  currentExecution.value.output.metadata.token_count = 1234
}

function addLog(level, message) {
  executionLogs.value.push({
    level,
    message,
    timestamp: new Date().toLocaleTimeString()
  })
}

function renderMarkdown(content) {
  // Simple markdown rendering (in production, use a proper markdown library)
  return content
    .replace(/^# (.*$)/gim, '<h1>$1</h1>')
    .replace(/^## (.*$)/gim, '<h2>$1</h2>')
    .replace(/^### (.*$)/gim, '<h3>$1</h3>')
    .replace(/^\- (.*$)/gim, '<li>$1</li>')
    .replace(/\n/g, '<br>')
}

// Load frameworks on mount
store.fetchFrameworks()
</script>

<style scoped>
.execution-view {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 140px);
  background: var(--bg-page);
}

.execution-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  background: var(--bg-sidebar);
  border-bottom: 1px solid var(--border-light);
}

.execution-header h2 {
  margin: 0;
  color: var(--text-main);
}

.header-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.framework-select {
  padding: 0.5rem 1rem;
  background: var(--bg-panel);
  color: var(--text-main);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-sm);
  font-size: 0.95rem;
  min-width: 250px;
}

.execute-btn {
  padding: 0.5rem 1.5rem;
  background: var(--accent-gold);
  color: var(--bg-panel);
  border: none;
  border-radius: var(--radius-sm);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.execute-btn:hover:not(:disabled) {
  background: var(--accent-orange);
  transform: translateY(-1px);
}

.execute-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.execution-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  padding: 1.5rem 2rem;
  height: 100%;
  overflow: hidden;
}

.working-state-panel,
.output-panel {
  background: var(--bg-sidebar);
  border-radius: var(--radius-md);
  padding: 1.5rem;
  overflow: auto;
}

.working-state-panel h3,
.output-panel h3 {
  margin: 0 0 1rem 0;
  color: var(--accent-gold);
  font-size: 1.1rem;
}

.output-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  border-bottom: 1px solid var(--border-light);
}

.output-tabs .tab {
  padding: 0.5rem 1rem;
  background: none;
  color: var(--text-muted);
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  transition: all 0.2s;
}

.output-tabs .tab:hover {
  color: var(--text-main);
}

.output-tabs .tab.active {
  color: var(--accent-gold);
  border-bottom-color: var(--accent-gold);
}

.output-content {
  max-height: calc(100% - 100px);
  overflow: auto;
}

.output-preview,
.output-json,
.output-logs {
  color: var(--text-main);
}

.output-json pre {
  background: var(--bg-code);
  padding: 1rem;
  border-radius: var(--radius-sm);
  overflow-x: auto;
}

.log-entry {
  padding: 0.5rem;
  margin-bottom: 0.25rem;
  border-left: 3px solid transparent;
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
}

.log-entry.info {
  border-left-color: var(--accent-gold);
}

.log-entry.success {
  border-left-color: #4CAF50;
}

.log-entry.error {
  border-left-color: #f44336;
}

.log-time {
  color: var(--text-muted);
  margin-right: 1rem;
}

.no-output {
  color: var(--text-muted);
  font-style: italic;
  text-align: center;
  padding: 2rem;
}

.execution-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.placeholder-content {
  text-align: center;
  color: var(--text-muted);
}

.placeholder-icon {
  font-size: 4rem;
  display: block;
  margin-bottom: 1rem;
}

.placeholder-content h3 {
  color: var(--text-main);
  margin-bottom: 0.5rem;
}
</style>
