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
    const code = (e as { code?: string })?.code
    if (code === 'UserNotConfirmedException') {
      toast.push('Confirm your email first, or ask an admin to confirm your account.', 'error')
      router.push({ path: '/auth/confirm', query: { email: email.value } })
      return
    }
    toast.push((e as Error).message || 'Login failed', 'error')
  }
}
</script>

<template>
  <div class="ios-app-shell flex min-h-screen items-center justify-center px-4">
    <div class="absolute right-4 top-4"><ThemeToggle /></div>
    <div class="guide-sheet w-full max-w-md page-enter">
      <div class="mb-6 flex items-center gap-3">
        <div class="flex h-12 w-12 items-center justify-center rounded-[14px] bg-gradient-to-br from-accent to-indigo-500 text-xl font-bold text-white">K</div>
        <div>
          <h1 class="text-2xl font-bold tracking-tight">Sign in</h1>
          <p class="text-sm text-muted-light dark:text-muted-dark">Welcome back to Kaldi One</p>
        </div>
      </div>
      <form class="space-y-4" @submit.prevent="submit">
        <input v-model="email" type="email" required class="input-field" placeholder="Email" autocomplete="email" />
        <input v-model="password" type="password" required class="input-field" placeholder="Password" autocomplete="current-password" />
        <button type="submit" class="btn-primary w-full" :disabled="auth.loading">{{ auth.loading ? 'Signing in…' : 'Sign in' }}</button>
      </form>
      <p class="mt-4 text-center text-sm">
        <router-link to="/auth/forgot" class="font-medium text-accent hover:underline">Forgot password?</router-link>
        ·
        <router-link to="/auth/confirm" class="font-medium text-accent hover:underline">Confirm email</router-link>
      </p>
      <p class="mt-2 text-center text-sm text-muted-light dark:text-muted-dark">
        No account? <router-link to="/auth/register" class="font-medium text-accent hover:underline">Sign up</router-link>
      </p>
    </div>
  </div>
</template>
