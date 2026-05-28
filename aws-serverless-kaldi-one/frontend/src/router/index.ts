import { createRouter, createWebHistory } from 'vue-router'
import { getIdToken } from '@/services/cognito'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'landing', component: () => import('@/views/LandingView.vue') },
    { path: '/auth/login', name: 'login', component: () => import('@/views/auth/LoginView.vue'), meta: { guest: true } },
    { path: '/auth/register', name: 'register', component: () => import('@/views/auth/RegisterView.vue'), meta: { guest: true } },
    { path: '/auth/forgot', name: 'forgot', component: () => import('@/views/auth/ForgotPasswordView.vue'), meta: { guest: true } },
    {
      path: '/app',
      redirect: '/app/workspace',
      meta: { requiresAuth: true },
      children: [
        { path: 'dashboard', component: () => import('@/views/DashboardView.vue') },
        { path: 'workspace', component: () => import('@/views/WorkspaceView.vue') },
        { path: 'history', component: () => import('@/views/HistoryView.vue') },
        { path: 'projects', component: () => import('@/views/ProjectsView.vue') },
        { path: 'settings', component: () => import('@/views/SettingsView.vue') },
      ],
    },
  ],
})

router.beforeEach(async (to) => {
  const token = await getIdToken()
  if (to.meta.requiresAuth && !token) return { name: 'login' }
  if (to.meta.guest && token) return { path: '/app/workspace' }
  return true
})

export default router
