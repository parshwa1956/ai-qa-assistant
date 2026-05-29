import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as cognito from '@/services/cognito'
import { api } from '@/services/api'
import { useProjectStore } from './projects'

export const useAuthStore = defineStore('auth', () => {
  const email = ref<string | null>(null)
  const userId = ref<string | null>(null)
  const loading = ref(false)
  const bootstrapped = ref(false)

  async function login(e: string, password: string) {
    loading.value = true
    try {
      await cognito.signIn(e, password)
      email.value = e
      await bootstrap()
    } finally {
      loading.value = false
    }
  }

  async function register(e: string, password: string) {
    loading.value = true
    try {
      return await cognito.signUp(e, password)
    } finally {
      loading.value = false
    }
  }

  async function logout() {
    cognito.signOut()
    email.value = null
    userId.value = null
    bootstrapped.value = false
    useProjectStore().$reset()
  }

  async function bootstrap() {
    const data = await api.bootstrap()
    userId.value = data.userId
    email.value = data.email
    useProjectStore().setProjects(data.projects as import('@/types').Project[])
    bootstrapped.value = true
  }

  async function restoreSession() {
    const token = await cognito.getIdToken()
    if (!token) return false
    try {
      await bootstrap()
      return true
    } catch {
      await logout()
      return false
    }
  }

  return { email, userId, loading, bootstrapped, login, register, logout, bootstrap, restoreSession }
})
