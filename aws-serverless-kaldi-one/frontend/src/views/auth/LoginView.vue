<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import ThemeToggle from '@/components/ThemeToggle.vue'

const email = ref('')
const password = ref('')
const auth = useAuthStore()
const toast = useToastStore()
const router = useRouter()

async function submit() {
  try {
    await auth.login(email.value, password.value)
    router.push('/app/workspace')
  } catch (e) {
    toast.push((e as Error).message || 'Login failed', 'error')
  }
}
</script>

<template>
  <div class="flex min-h-screen items-center justify-center bg-gradient-to-br from-blue-50/50 to-white px-4 dark:from-surface-dark dark:to-slate-900">
    <div class="absolute right-4 top-4"><ThemeToggle /></div>
    <div class="glass-card w-full max-w-md p-8 page-enter">
      <h1 class="text-2xl font-bold">Sign in</h1>
      <p class="mt-1 text-sm text-muted-light dark:text-muted-dark">Welcome back to Kaldi One</p>
      <form class="mt-6 space-y-4" @submit.prevent="submit">
        <input v-model="email" type="email" required class="input-field" placeholder="Email" />
        <input v-model="password" type="password" required class="input-field" placeholder="Password" />
        <button type="submit" class="btn-primary w-full" :disabled="auth.loading">{{ auth.loading ? 'Signing in…' : 'Sign in' }}</button>
      </form>
      <p class="mt-4 text-center text-sm">
        <router-link to="/auth/forgot" class="text-accent hover:underline">Forgot password?</router-link>
      </p>
      <p class="mt-2 text-center text-sm text-muted-light dark:text-muted-dark">
        No account? <router-link to="/auth/register" class="text-accent hover:underline">Sign up</router-link>
      </p>
    </div>
  </div>
</template>
