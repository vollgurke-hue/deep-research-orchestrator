<template>
  <div class="visualizer-view">
    <h1>🎨 Workflow Visualizer</h1>
    <p class="subtitle">Vue Flow integration coming soon...</p>

    <div class="placeholder">
      <div class="placeholder-icon">🚧</div>
      <h2>Under Construction</h2>
      <p>The visual workflow builder with Vue Flow will be implemented here.</p>
      <button @click="goBack" class="btn-back">← Back to Dashboard</button>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

function goBack() {
  router.push('/')
}
</script>

<style scoped>
.visualizer-view {
  min-height: 100vh;
  background: var(--bg-page, #4E342E);
  padding: 2rem;
  color: var(--text-main, #FFF5E6);
}

.visualizer-view h1 {
  text-align: center;
  color: var(--accent-gold, #FFB347);
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
}

.subtitle {
  text-align: center;
  color: var(--text-muted, #C9B299);
  font-size: 1.1rem;
  margin-bottom: 3rem;
}

.placeholder {
  max-width: 600px;
  margin: 0 auto;
  text-align: center;
  background: var(--bg-panel, #0A0A0A);
  padding: 3rem;
  border-radius: 12px;
  border: 2px solid var(--accent-gold, #FFB347);
}

.placeholder-icon {
  font-size: 5rem;
  margin-bottom: 1rem;
}

.placeholder h2 {
  color: var(--accent-gold, #FFB347);
  margin-bottom: 1rem;
}

.placeholder p {
  color: var(--text-light, #F5E6D3);
  margin-bottom: 2rem;
  line-height: 1.6;
}

.btn-back {
  padding: 0.8rem 1.5rem;
  background: var(--accent-orange, #FF8C42);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-back:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 140, 66, 0.4);
}
</style>
