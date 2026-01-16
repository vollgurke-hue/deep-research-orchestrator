import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as api from '@/api/client'

export const useOrchestratorStore = defineStore('orchestrator', () => {
  // State
  const frameworks = ref([])
  const phases = ref([])
  const workflows = ref([])
  const techniques = ref([])

  const currentFramework = ref(null)
  const currentPhase = ref(null)
  const currentWorkflow = ref(null)
  const currentTechnique = ref(null)

  const loading = ref(false)
  const error = ref(null)

  // Computed
  const currentFrameworkHierarchy = computed(() => {
    if (!currentFramework.value) return null

    // Build full hierarchy with phases, workflows, and techniques
    return {
      ...currentFramework.value,
      phases: currentFramework.value.building_blocks
        ?.filter(b => b.block_type === 'phase')
        .map(phaseBlock => {
          // Try both block_id and phase_id for compatibility
          const phase = phases.value.find(p =>
            p.phase_id === phaseBlock.block_id || p.block_id === phaseBlock.block_id
          )
          if (!phase) return null

          return {
            ...phase,
            workflows: phase.building_blocks
              ?.filter(b => b.block_type === 'workflow')
              .map(workflowBlock => {
                // Try both block_id and workflow_id for compatibility
                const workflow = workflows.value.find(w =>
                  w.workflow_id === workflowBlock.block_id || w.block_id === workflowBlock.block_id
                )
                if (!workflow) return null

                return {
                  ...workflow,
                  techniques: workflow.building_blocks
                    ?.filter(b => b.block_type === 'technique')
                    .map(techBlock => {
                      // Try both block_id and technique_id for compatibility
                      return techniques.value.find(t =>
                        t.technique_id === techBlock.block_id || t.block_id === techBlock.block_id
                      )
                    })
                    .filter(Boolean) || []
                }
              })
              .filter(Boolean) || []
          }
        })
        .filter(Boolean) || []
    }
  })

  // Actions
  async function fetchFrameworks() {
    loading.value = true
    error.value = null
    try {
      frameworks.value = await api.getFrameworks()
    } catch (e) {
      error.value = e.message
      console.error('Failed to fetch frameworks:', e)
    } finally {
      loading.value = false
    }
  }

  async function fetchFramework(id) {
    loading.value = true
    error.value = null
    try {
      currentFramework.value = await api.getFramework(id)

      // Load all related phases, workflows, techniques
      await Promise.all([
        fetchPhases(),
        fetchWorkflows(),
        fetchTechniques()
      ])
    } catch (e) {
      error.value = e.message
      console.error('Failed to fetch framework:', e)
    } finally {
      loading.value = false
    }
  }

  async function fetchPhases() {
    try {
      const phasesList = await api.getPhases()
      // Load full data for each phase
      phases.value = await Promise.all(
        phasesList.map(p => api.getPhase(p.phase_id))
      )
    } catch (e) {
      console.error('Failed to fetch phases:', e)
    }
  }

  async function fetchWorkflows() {
    try {
      const workflowsList = await api.getWorkflows()
      // Load full data for each workflow
      workflows.value = await Promise.all(
        workflowsList.map(w => api.getWorkflow(w.workflow_id))
      )
    } catch (e) {
      console.error('Failed to fetch workflows:', e)
    }
  }

  async function fetchTechniques() {
    try {
      const techniquesList = await api.getTechniques()
      // Load full data for each technique
      techniques.value = await Promise.all(
        techniquesList.map(t => api.getTechnique(t.technique_id))
      )
    } catch (e) {
      console.error('Failed to fetch techniques:', e)
    }
  }

  async function fetchTechnique(id) {
    loading.value = true
    error.value = null
    try {
      currentTechnique.value = await api.getTechnique(id)
    } catch (e) {
      error.value = e.message
      console.error('Failed to fetch technique:', e)
    } finally {
      loading.value = false
    }
  }

  async function updateTechnique(id, data) {
    loading.value = true
    error.value = null
    try {
      const updated = await api.updateTechnique(id, data)

      // Update local state
      const index = techniques.value.findIndex(t => t.technique_id === id)
      if (index !== -1) {
        techniques.value[index] = updated
      }

      if (currentTechnique.value?.technique_id === id) {
        currentTechnique.value = updated
      }

      return updated
    } catch (e) {
      error.value = e.message
      console.error('Failed to update technique:', e)
      throw e
    } finally {
      loading.value = false
    }
  }

  async function updateWorkflow(id, data) {
    loading.value = true
    error.value = null
    try {
      const updated = await api.updateWorkflow(id, data)

      const index = workflows.value.findIndex(w => w.workflow_id === id)
      if (index !== -1) {
        workflows.value[index] = updated
      }

      if (currentWorkflow.value?.workflow_id === id) {
        currentWorkflow.value = updated
      }

      return updated
    } catch (e) {
      error.value = e.message
      console.error('Failed to update workflow:', e)
      throw e
    } finally {
      loading.value = false
    }
  }

  async function updatePhase(id, data) {
    loading.value = true
    error.value = null
    try {
      const updated = await api.updatePhase(id, data)

      const index = phases.value.findIndex(p => p.phase_id === id)
      if (index !== -1) {
        phases.value[index] = updated
      }

      if (currentPhase.value?.phase_id === id) {
        currentPhase.value = updated
      }

      return updated
    } catch (e) {
      error.value = e.message
      console.error('Failed to update phase:', e)
      throw e
    } finally {
      loading.value = false
    }
  }

  async function reloadOrchestrator() {
    loading.value = true
    error.value = null
    try {
      await api.reloadOrchestrator()

      // Refresh all data
      await Promise.all([
        fetchFrameworks(),
        fetchPhases(),
        fetchWorkflows(),
        fetchTechniques()
      ])

      // Refresh current framework if one is selected
      if (currentFramework.value) {
        await fetchFramework(currentFramework.value.framework_id)
      }
    } catch (e) {
      error.value = e.message
      console.error('Failed to reload orchestrator:', e)
    } finally {
      loading.value = false
    }
  }

  function selectFramework(framework) {
    currentFramework.value = framework
    currentPhase.value = null
    currentWorkflow.value = null
    currentTechnique.value = null
  }

  function selectPhase(phase) {
    currentPhase.value = phase
    currentWorkflow.value = null
    currentTechnique.value = null
  }

  function selectWorkflow(workflow) {
    currentWorkflow.value = workflow
    currentTechnique.value = null
  }

  function selectTechnique(technique) {
    currentTechnique.value = technique
  }

  return {
    // State
    frameworks,
    phases,
    workflows,
    techniques,
    currentFramework,
    currentPhase,
    currentWorkflow,
    currentTechnique,
    loading,
    error,

    // Computed
    currentFrameworkHierarchy,

    // Actions
    fetchFrameworks,
    fetchFramework,
    fetchPhases,
    fetchWorkflows,
    fetchTechniques,
    fetchTechnique,
    updateTechnique,
    updateWorkflow,
    updatePhase,
    reloadOrchestrator,
    selectFramework,
    selectPhase,
    selectWorkflow,
    selectTechnique
  }
})
