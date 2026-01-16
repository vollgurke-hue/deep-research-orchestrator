<template>
  <div :class="['theme-node', `level-${level}`]">
    <div class="theme-header" @click="toggleExpanded">
      <span class="expand-icon">{{ expanded ? '▼' : '▶' }}</span>
      <input
        type="checkbox"
        v-model="isSelected"
        @click.stop
        @change="handleSelectionChange"
      />
      <span class="theme-name">{{ theme.theme_name }}</span>
      <span class="relevance-badge">{{ theme.relevance_score }}%</span>
    </div>

    <p class="description" v-if="expanded">{{ theme.description }}</p>

    <!-- Recursive Sub-Themes -->
    <div v-if="expanded && theme.sub_themes && theme.sub_themes.length" class="sub-themes">
      <ThemeNode
        v-for="sub in theme.sub_themes"
        :key="sub.theme_id"
        :theme="sub"
        :level="level + 1"
        :selectedThemes="selectedThemes"
        @select="handleSubSelect"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  theme: {
    type: Object,
    required: true
  },
  level: {
    type: Number,
    default: 0
  },
  selectedThemes: {
    type: Set,
    default: () => new Set()
  }
})

const emit = defineEmits(['select'])

const expanded = ref(props.level < 2) // Auto-expand first 2 levels

const isSelected = computed({
  get() {
    return props.selectedThemes.has(props.theme.theme_id)
  },
  set(value) {
    emit('select', { themeId: props.theme.theme_id, selected: value })
  }
})

function toggleExpanded() {
  expanded.value = !expanded.value
}

function handleSelectionChange() {
  // Emit is already handled by v-model
}

function handleSubSelect(payload) {
  // Propagate selection events up
  emit('select', payload)
}
</script>

<style scoped>
.theme-node {
  margin: 0.5rem 0;
  border-left: 3px solid var(--accent-gold);
  padding-left: 1rem;
  transition: all 0.2s;
}

.theme-node.level-1 {
  margin-left: 1.5rem;
  border-color: var(--accent-orange);
}

.theme-node.level-2 {
  margin-left: 3rem;
  border-color: var(--border-medium);
}

.theme-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem;
  cursor: pointer;
  background: var(--bg-panel);
  border-radius: 6px;
  transition: all 0.2s;
}

.theme-header:hover {
  background: rgba(255, 179, 71, 0.1);
  transform: translateX(4px);
}

.expand-icon {
  color: var(--text-muted);
  font-size: 0.7rem;
  min-width: 12px;
  transition: transform 0.2s;
}

input[type="checkbox"] {
  cursor: pointer;
  width: 18px;
  height: 18px;
  accent-color: var(--accent-gold);
}

.theme-name {
  font-weight: 600;
  color: var(--accent-gold);
  flex: 1;
  font-size: 1rem;
}

.relevance-badge {
  background: var(--accent-orange);
  color: var(--bg-panel);
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-weight: 700;
  font-size: 0.85rem;
  min-width: 48px;
  text-align: center;
}

.description {
  color: var(--text-light);
  margin: 0.5rem 0 0.5rem 2rem;
  padding: 0.5rem;
  font-size: 0.9rem;
  line-height: 1.5;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 4px;
}

.sub-themes {
  margin-top: 0.5rem;
  padding-left: 0.5rem;
}
</style>
