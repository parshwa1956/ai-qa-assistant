<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'

const email = ref('')
const password = ref('')
const auth = useAuthStore()
const toast = useToastStore()
const router = useRouter()

function signUpErrorMessage(err: unknown): string {
  const code = (err as { code?: string })?.code
  const msg = (err as Error)?.message || ''
  if (code === 'UsernameExistsException' || /already exists/i.test(msg)) {
    return 'An account with this email already exists. Sign in or use Forgot password.'
  }
  if (code === 'InvalidPasswordException') {
    return 'Password does not meet requirements (min 8 chars, upper, lower, number).'
  }
  return msg || 'Sign up failed'
}

async function submit() {
  try {
    const result = await auth.register(email.value, password.value)
    if (result?.needsConfirmation) {
      toast.push('Check your email for a verification code (also check spam).', 'info')
      router.push({ path: '/auth/confirm', query: { email: email.value } })
    } else {
      toast.push('Account created. Please sign in.', 'success')
      router.push('/auth/login')
    }
  } catch (e) {
    const code = (e as { code?: string })?.code
    if (code === 'UsernameExistsException') {
      toast.push(signUpErrorMessage(e), 'error')
      router.push({ path: '/auth/confirm', query: { email: email.value } })
      return
    }
    toast.push(signUpErrorMessage(e), 'error')
  }
}
</script>

<template>
  <div class="flex min-h-screen items-center justify-center px-4">
    <div class="glass-card w-full max-w-md p-8 page-enter">
      <h1 class="text-2xl font-bold">Create account</h1>
      <form class="mt-6 space-y-4" @submit.prevent="submit">
        <input v-model="email" type="email" required class="input-field" placeholder="Email" />
        <input v-model="password" type="password" required minlength="8" class="input-field" placeholder="Password (min 8 chars)" />
        <button type="submit" class="btn-primary w-full" :disabled="auth.loading">Sign up</button>
      </form>
      <p class="mt-4 text-center text-sm">
        Already have an account?
        <router-link to="/auth/login" class="text-accent hover:underline">Sign in</router-link>
        ·
        <router-link to="/auth/forgot" class="text-accent hover:underline">Forgot password</router-link>
      </p>
    </div>
  </div>
</template>
