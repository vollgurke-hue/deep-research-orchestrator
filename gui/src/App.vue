<template>
  <div id="app">
    <nav class="main-nav">
      <div class="nav-header">
        <h1 class="nav-title">Deep Research Orchestrator</h1>
      </div>
      <div class="nav-tabs">
        <RouterLink to="/" class="nav-tab" active-class="active">
          <span class="tab-icon">📊</span>
          <span class="tab-label">Dashboard</span>
        </RouterLink>
        <RouterLink to="/builder" class="nav-tab" active-class="active">
          <span class="tab-icon">🎛️</span>
          <span class="tab-label">Builder</span>
        </RouterLink>
        <RouterLink to="/execution" class="nav-tab" active-class="active">
          <span class="tab-icon">📈</span>
          <span class="tab-label">Execution</span>
        </RouterLink>
        <RouterLink to="/docs" class="nav-tab" active-class="active">
          <span class="tab-icon">📂</span>
          <span class="tab-label">Docs</span>
        </RouterLink>
      </div>
    </nav>
    <div class="app-content">
      <RouterView />
    </div>
  </div>
</template>

<script setup>
import { RouterView, RouterLink } from 'vue-router'
</script>

<style>
/* Global CSS Variables - Kakao Theme */
:root {
  --bg-page: #4E342E;
  --bg-panel: #0A0A0A;
  --bg-panel-light: #8D6E63;
  --bg-sidebar: #6D4C41;
  --bg-sidebar-el: #8D6E63;
  --bg-code: #1A1410;
  --bg-dark: #A1887F;

  --text-main: #FFF5E6;
  --text-light: #F5E6D3;
  --text-muted: #C9B299;
  --text-code: #F5E6D3;

  --accent: #FFB347;
  --accent-strong: #FF8C42;
  --accent-gold: #FFB347;
  --accent-orange: #FF8C42;
  --accent-gradient: linear-gradient(90deg, rgba(255, 179, 71, 0.18), rgba(255, 140, 66, 0.06));

  --border-light: rgba(255, 255, 255, 0.2);
  --border-medium: rgba(255, 255, 255, 0.3);

  --radius-sm: 8px;
  --radius-md: 10px;
  --radius-lg: 14px;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: Inter, system-ui, -apple-system, "Segoe UI", Roboto, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background: var(--bg-page);
  color: var(--text-main);
}

#app {
  width: 100%;
  min-height: 100vh;
}

/* Scrollbar Styling */
::-webkit-scrollbar {
  width: 10px;
  height: 10px;
}

::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 5px;
}

::-webkit-scrollbar-thumb {
  background: var(--accent-gold);
  border-radius: 5px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--accent-orange);
}

/* Main Navigation */
.main-nav {
  background: var(--bg-sidebar);
  border-bottom: 2px solid var(--border-medium);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.nav-header {
  padding: 1rem 2rem;
  border-bottom: 1px solid var(--border-light);
}

.nav-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--accent-gold);
  margin: 0;
}

.nav-tabs {
  display: flex;
  gap: 0;
  padding: 0 2rem;
}

.nav-tab {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem 1.5rem;
  text-decoration: none;
  color: var(--text-muted);
  font-weight: 500;
  border-bottom: 3px solid transparent;
  transition: all 0.2s ease;
  position: relative;
}

.nav-tab:hover {
  color: var(--text-main);
  background: rgba(255, 179, 71, 0.1);
}

.nav-tab.active {
  color: var(--accent-gold);
  border-bottom-color: var(--accent-gold);
  background: rgba(255, 179, 71, 0.15);
}

.tab-icon {
  font-size: 1.2rem;
}

.tab-label {
  font-size: 0.95rem;
}

.app-content {
  width: 100%;
  min-height: calc(100vh - 140px);
}
</style>
