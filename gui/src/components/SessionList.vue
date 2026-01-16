<template>
  <div class="session-list">
    <!-- Search & Filter -->
    <div class="list-controls">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="🔍 Search sessions..."
        class="search-input"
      />
      <select v-model="modeFilter" class="mode-filter">
        <option value="">All Modes</option>
        <option value="unified">Unified</option>
        <option value="tot">Tree of Thoughts</option>
        <option value="thematic">Thematic</option>
      </select>
    </div>

    <!-- Session Items -->
    <div class="session-items">
      <div
        v-for="session in filteredSessions"
        :key="session.session_id"
        :class="['session-item', { active: session.session_id === activeSessionId }]"
        @click="$emit('select', session.session_id)"
      >
        <!-- Mode Badge -->
        <div :class="['mode-badge', session.mode]">
          {{ getModeLabel(session.mode) }}
        </div>

        <!-- Session Header -->
        <div class="session-header">
          <h3 class="session-title">{{ session.title || 'Untitled Session' }}</h3>
          <span :class="['status-badge', session.status]">
            {{ getStatusIcon(session.status) }}
          </span>
        </div>

        <!-- Session Meta -->
        <div class="session-meta">
          <div class="meta-row">
            <span class="meta-label">Goal:</span>
            <span class="meta-value">{{ truncate(session.goal, 60) }}</span>
          </div>
          <div class="meta-row">
            <span class="meta-label">Created:</span>
            <span class="meta-value">{{ formatDate(session.created_at) }}</span>
          </div>
        </div>

        <!-- Session Stats (if available) -->
        <div v-if="session.tot" class="session-stats">
          <div class="stat-mini">
            <span class="stat-icon">🌳</span>
            <span>{{ session.tot.total_nodes || 0 }} nodes</span>
          </div>
          <div class="stat-mini">
            <span class="stat-icon">📊</span>
            <span>{{ session.responses?.length || 0 }} responses</span>
          </div>
        </div>

        <!-- Actions -->
        <div class="session-actions" @click.stop>
          <button
            @click="$emit('select', session.session_id)"
            class="btn-action"
            title="View Details"
          >
            👁️
          </button>
          <button
            @click="$emit('delete', session.session_id)"
            class="btn-action btn-danger"
            title="Delete"
          >
            🗑️
          </button>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="filteredSessions.length === 0" class="empty-state">
        <div class="empty-icon">📭</div>
        <p v-if="searchQuery || modeFilter">No sessions match your filters</p>
        <p v-else>No sessions yet. Create your first one!</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  sessions: {
    type: Array,
    required: true
  },
  activeSessionId: {
    type: String,
    default: null
  }
})

defineEmits(['select', 'delete'])

// Local state
const searchQuery = ref('')
const modeFilter = ref('')

// Computed
const filteredSessions = computed(() => {
  let result = props.sessions

  // Filter by search query
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(s =>
      s.title?.toLowerCase().includes(query) ||
      s.goal?.toLowerCase().includes(query) ||
      s.description?.toLowerCase().includes(query)
    )
  }

  // Filter by mode
  if (modeFilter.value) {
    result = result.filter(s => s.mode === modeFilter.value)
  }

  return result
})

// Helpers
function getModeLabel(mode) {
  const labels = {
    unified: 'Unified',
    tot: 'ToT',
    thematic: 'Thematic'
  }
  return labels[mode] || mode
}

function getStatusIcon(status) {
  const icons = {
    exploring: '🔍',
    validating: '✓',
    complete: '✅',
    failed: '❌',
    archived: '📦'
  }
  return icons[status] || '⏸️'
}

function formatDate(dateString) {
  if (!dateString) return 'Unknown'

  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  if (diffDays < 7) return `${diffDays}d ago`

  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

function truncate(text, length) {
  if (!text) return ''
  return text.length > length ? text.substring(0, length) + '...' : text
}
</script>

<style scoped>
.session-list {
  display: flex;
  flex-direction: column;
  height: 100%;
  gap: 1rem;
}

/* Controls */
.list-controls {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.search-input, .mode-filter {
  width: 100%;
  padding: 0.75rem;
  background: #222;
  border: 1px solid #333;
  border-radius: 8px;
  color: #e0e0e0;
  font-size: 0.9rem;
  transition: border-color 0.2s;
}

.search-input:focus, .mode-filter:focus {
  outline: none;
  border-color: #4CAF50;
}

.search-input::placeholder {
  color: #666;
}

/* Session Items */
.session-items {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.session-item {
  position: relative;
  padding: 1rem;
  background: #222;
  border: 2px solid #333;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
}

.session-item:hover {
  background: #282828;
  border-color: #4CAF50;
  transform: translateX(4px);
}

.session-item.active {
  background: #2a2a2a;
  border-color: #4CAF50;
  box-shadow: 0 0 12px rgba(76, 175, 80, 0.2);
}

/* Mode Badge */
.mode-badge {
  position: absolute;
  top: 0.75rem;
  right: 0.75rem;
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  color: white;
}

.mode-badge.unified {
  background: linear-gradient(135deg, #4CAF50, #2196F3);
}

.mode-badge.tot {
  background: #2196F3;
}

.mode-badge.thematic {
  background: #4CAF50;
}

/* Session Header */
.session-header {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
  padding-right: 4rem; /* Space for mode badge */
}

.session-title {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: #e0e0e0;
  flex: 1;
  line-height: 1.3;
}

.status-badge {
  font-size: 1.2rem;
  flex-shrink: 0;
}

/* Session Meta */
.session-meta {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.meta-row {
  display: flex;
  gap: 0.5rem;
  font-size: 0.85rem;
}

.meta-label {
  color: #888;
  font-weight: 500;
  min-width: 60px;
}

.meta-value {
  color: #aaa;
  flex: 1;
}

/* Session Stats */
.session-stats {
  display: flex;
  gap: 1rem;
  margin-bottom: 0.75rem;
}

.stat-mini {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.8rem;
  color: #888;
}

.stat-icon {
  font-size: 1rem;
}

/* Actions */
.session-actions {
  display: flex;
  gap: 0.5rem;
  padding-top: 0.75rem;
  border-top: 1px solid #333;
}

.btn-action {
  flex: 1;
  padding: 0.5rem;
  background: #333;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-action:hover {
  background: #444;
  transform: scale(1.05);
}

.btn-action.btn-danger:hover {
  background: #f44336;
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 1rem;
  color: #666;
  text-align: center;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.3;
}

.empty-state p {
  margin: 0;
  font-size: 0.95rem;
}

/* Scrollbar */
.session-items::-webkit-scrollbar {
  width: 6px;
}

.session-items::-webkit-scrollbar-track {
  background: #1a1a1a;
  border-radius: 3px;
}

.session-items::-webkit-scrollbar-thumb {
  background: #333;
  border-radius: 3px;
}

.session-items::-webkit-scrollbar-thumb:hover {
  background: #444;
}
</style>
