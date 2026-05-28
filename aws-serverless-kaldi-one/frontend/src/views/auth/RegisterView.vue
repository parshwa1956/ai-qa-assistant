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

async function submit() {
  try {
    await auth.register(email.value, password.value)
    toast.push('Account created. Please sign in.', 'success')
    router.push('/auth/login')
  } catch (e) {
    toast.push((e as Error).message || 'Sign up failed', 'error')
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
      <p class="mt-4 text-center text-sm"><router-link to="/auth/login" class="text-accent">Back to sign in</router-link></p>
    </div>
  </div>
</template>
