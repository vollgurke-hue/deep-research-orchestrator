/**
 * Pinia Store for Unified Session Management (API v2)
 *
 * Replaces the old orchestrator.js store with a session-based architecture.
 * Connects to Backend API v2 endpoints.
 */
import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import apiClient from '@/api/client'

export const useSessionsStore = defineStore('sessions', () => {
  // ============================================================================
  // STATE
  // ============================================================================

  // Sessions stored as Map for O(1) lookup
  const sessions = ref(new Map())

  // Currently selected session
  const activeSessionId = ref(null)

  // Loading & error states
  const loading = ref(false)
  const error = ref(null)

  // ============================================================================
  // COMPUTED
  // ============================================================================

  /**
   * Get all sessions as array (sorted by updated_at DESC)
   */
  const allSessions = computed(() => {
    return Array.from(sessions.value.values())
      .sort((a, b) => {
        const dateA = new Date(a.updated_at || a.created_at || 0)
        const dateB = new Date(b.updated_at || b.created_at || 0)
        return dateB - dateA
      })
  })

  /**
   * Get active/in-progress sessions
   */
  const activeSessions = computed(() => {
    return allSessions.value.filter(s =>
      s.status !== 'complete' &&
      s.status !== 'archived'
    )
  })

  /**
   * Get completed sessions
   */
  const completedSessions = computed(() => {
    return allSessions.value.filter(s =>
      s.status === 'complete'
    )
  })

  /**
   * Get currently active session
   */
  const activeSession = computed(() => {
    return activeSessionId.value
      ? sessions.value.get(activeSessionId.value)
      : null
  })

  /**
   * Filter sessions by mode
   */
  const sessionsByMode = computed(() => (mode) => {
    return allSessions.value.filter(s => s.mode === mode)
  })

  /**
   * Get session statistics
   */
  const stats = computed(() => ({
    total: sessions.value.size,
    active: activeSessions.value.length,
    completed: completedSessions.value.length,
    by_mode: {
      thematic: sessionsByMode.value('thematic').length,
      tot: sessionsByMode.value('tot').length,
      unified: sessionsByMode.value('unified').length
    }
  }))

  // ============================================================================
  // ACTIONS - CRUD Operations
  // ============================================================================

  /**
   * Fetch all sessions from API
   */
  async function fetchSessions(filters = {}) {
    loading.value = true
    error.value = null

    try {
      const response = await apiClient.get('/v2/sessions', { params: filters })

      // Clear and repopulate sessions Map
      sessions.value.clear()

      // API returns { sessions: [...] }, not [...] directly
      const sessionList = response.data.sessions || response.data || []

      if (Array.isArray(sessionList)) {
        sessionList.forEach(session => {
          // API v2 returns flat session objects, not nested with metadata
          const sessionId = session.session_id
          sessions.value.set(sessionId, session)
        })
      }

      console.log(`✓ Loaded ${sessions.value.size} sessions`)

      return sessions.value.size

    } catch (err) {
      error.value = err.message || 'Failed to fetch sessions'
      console.error('Error fetching sessions:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Fetch a single session by ID
   */
  async function fetchSession(sessionId) {
    loading.value = true
    error.value = null

    try {
      const response = await apiClient.get(`/v2/sessions/${sessionId}`)

      if (response.data) {
        sessions.value.set(sessionId, response.data)
        console.log(`✓ Loaded session ${sessionId}`)
        return response.data
      }

    } catch (err) {
      error.value = err.message || 'Failed to fetch session'
      console.error(`Error fetching session ${sessionId}:`, err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Create a new session
   */
  async function createSession(data) {
    loading.value = true
    error.value = null

    try {
      const response = await apiClient.post('/v2/sessions', {
        mode: data.mode || 'unified',
        title: data.title,
        goal: data.goal,
        description: data.description,
        axioms: data.axioms || []
      })

      if (response.data && response.data.session_id) {
        // Fetch full session data
        await fetchSession(response.data.session_id)

        // Set as active
        activeSessionId.value = response.data.session_id

        console.log(`✓ Created session ${response.data.session_id}`)

        return response.data
      }

    } catch (err) {
      error.value = err.message || 'Failed to create session'
      console.error('Error creating session:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Update session data (rarely used, sessions update themselves)
   */
  async function updateSession(sessionId, updates) {
    loading.value = true
    error.value = null

    try {
      // No direct update endpoint in API v2
      // Sessions are updated through their specific actions
      // This is a client-side update only

      const session = sessions.value.get(sessionId)
      if (session) {
        Object.assign(session, updates)
        sessions.value.set(sessionId, session)
      }

      console.log(`✓ Updated session ${sessionId} (client-side)`)

    } catch (err) {
      error.value = err.message || 'Failed to update session'
      console.error(`Error updating session ${sessionId}:`, err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Delete a session
   */
  async function deleteSession(sessionId) {
    loading.value = true
    error.value = null

    try {
      await apiClient.delete(`/v2/sessions/${sessionId}`)

      sessions.value.delete(sessionId)

      // Clear active if deleted
      if (activeSessionId.value === sessionId) {
        activeSessionId.value = null
      }

      console.log(`✓ Deleted session ${sessionId}`)

    } catch (err) {
      error.value = err.message || 'Failed to delete session'
      console.error(`Error deleting session ${sessionId}:`, err)
      throw err
    } finally {
      loading.value = false
    }
  }

  // ============================================================================
  // ACTIONS - Session Operations
  // ============================================================================

  /**
   * Initialize session components (ToT, MCTS, etc.)
   */
  async function initializeSession(sessionId, config = {}) {
    loading.value = true
    error.value = null

    try {
      const response = await apiClient.post(`/v2/sessions/${sessionId}/initialize`, {
        branching_factor: config.branching_factor || 3,
        max_depth: config.max_depth || 3
      })

      // Refresh session data
      await fetchSession(sessionId)

      console.log(`✓ Initialized session ${sessionId}`)

      return response.data

    } catch (err) {
      error.value = err.message || 'Failed to initialize session'
      console.error(`Error initializing session ${sessionId}:`, err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Get coverage analysis for session
   */
  async function getCoverage(sessionId) {
    loading.value = true
    error.value = null

    try {
      const response = await apiClient.get(`/v2/sessions/${sessionId}/coverage`)

      console.log(`✓ Got coverage for session ${sessionId}`)

      return response.data

    } catch (err) {
      error.value = err.message || 'Failed to get coverage'
      console.error(`Error getting coverage for ${sessionId}:`, err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Run Coverage-Guided MCTS
   */
  async function runCoverageGuidedMCTS(sessionId, numIterations = 10) {
    loading.value = true
    error.value = null

    try {
      const response = await apiClient.post(`/v2/sessions/${sessionId}/mcts/coverage-guided`, {
        num_iterations: numIterations
      })

      // Refresh session after MCTS run
      await fetchSession(sessionId)

      console.log(`✓ Ran MCTS for session ${sessionId}`)

      return response.data

    } catch (err) {
      error.value = err.message || 'Failed to run MCTS'
      console.error(`Error running MCTS for ${sessionId}:`, err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Export session as JSON
   */
  async function exportSession(sessionId) {
    loading.value = true
    error.value = null

    try {
      const response = await apiClient.get(`/v2/sessions/${sessionId}/export`)

      // Trigger download
      const blob = new Blob([JSON.stringify(response.data, null, 2)], {
        type: 'application/json'
      })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `session_${sessionId}_${Date.now()}.json`
      a.click()
      URL.revokeObjectURL(url)

      console.log(`✓ Exported session ${sessionId}`)

    } catch (err) {
      error.value = err.message || 'Failed to export session'
      console.error(`Error exporting session ${sessionId}:`, err)
      throw err
    } finally {
      loading.value = false
    }
  }

  // ============================================================================
  // ACTIONS - Utility
  // ============================================================================

  /**
   * Select a session as active
   */
  function selectSession(sessionId) {
    if (sessions.value.has(sessionId)) {
      activeSessionId.value = sessionId
      console.log(`✓ Selected session ${sessionId}`)
    } else {
      console.warn(`Session ${sessionId} not found`)
    }
  }

  /**
   * Clear all sessions (client-side only)
   */
  function clearSessions() {
    sessions.value.clear()
    activeSessionId.value = null
    error.value = null
    console.log('✓ Cleared all sessions (client-side)')
  }

  /**
   * Reset error state
   */
  function clearError() {
    error.value = null
  }

  // ============================================================================
  // PERSISTENCE - localStorage
  // ============================================================================

  /**
   * Save sessions to localStorage (cache)
   */
  watch(
    sessions,
    (newSessions) => {
      try {
        const serialized = JSON.stringify(Array.from(newSessions.entries()))
        localStorage.setItem('research_sessions_cache', serialized)
        console.log(`✓ Cached ${newSessions.size} sessions to localStorage`)
      } catch (err) {
        console.error('Failed to save sessions to localStorage:', err)
      }
    },
    { deep: true }
  )

  /**
   * Watch active session ID
   */
  watch(activeSessionId, (newId) => {
    if (newId) {
      localStorage.setItem('active_session_id', newId)
    } else {
      localStorage.removeItem('active_session_id')
    }
  })

  /**
   * Load sessions from localStorage on init
   */
  function loadFromCache() {
    try {
      const cached = localStorage.getItem('research_sessions_cache')
      if (cached) {
        const entries = JSON.parse(cached)
        sessions.value = new Map(entries)
        console.log(`✓ Loaded ${sessions.value.size} sessions from cache`)
      }

      const cachedActiveId = localStorage.getItem('active_session_id')
      if (cachedActiveId && sessions.value.has(cachedActiveId)) {
        activeSessionId.value = cachedActiveId
      }
    } catch (err) {
      console.error('Failed to load sessions from cache:', err)
    }
  }

  // ============================================================================
  // RETURN PUBLIC API
  // ============================================================================

  return {
    // State
    sessions,
    activeSessionId,
    loading,
    error,

    // Computed
    allSessions,
    activeSessions,
    completedSessions,
    activeSession,
    sessionsByMode,
    stats,

    // Actions - CRUD
    fetchSessions,
    fetchSession,
    createSession,
    updateSession,
    deleteSession,

    // Actions - Operations
    initializeSession,
    getCoverage,
    runCoverageGuidedMCTS,
    exportSession,

    // Actions - Utility
    selectSession,
    clearSessions,
    clearError,
    loadFromCache
  }
})
