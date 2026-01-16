import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'dashboard',
      component: () => import('@/views/Dashboard.vue')
    },
    {
      path: '/unified',
      name: 'unified-dashboard',
      component: () => import('@/views/UnifiedDashboard.vue')
    },
    {
      path: '/builder',
      name: 'builder',
      component: () => import('@/views/BuilderView.vue')
    },
    {
      path: '/execution',
      name: 'execution',
      component: () => import('@/views/ExecutionView.vue')
    },
    {
      path: '/docs',
      name: 'docs',
      component: () => import('@/views/DocsView.vue')
    },
    {
      path: '/research/create',
      name: 'research-create',
      component: () => import('@/views/ResearchCreator.vue')
    },
    {
      path: '/sovereign',
      name: 'sovereign-research',
      component: () => import('@/views/SovereignResearch.vue')
    }
  ]
})

export default router
