<script setup lang="ts">
import { ref } from 'vue'
import * as cognito from '@/services/cognito'
import { useToastStore } from '@/stores/toast'

const email = ref('')
const code = ref('')
const newPassword = ref('')
const step = ref<'request' | 'confirm'>('request')
const toast = useToastStore()

async function requestCode() {
  try {
    await cognito.forgotPassword(email.value)
    step.value = 'confirm'
    toast.push('Check your email for a reset code', 'info')
  } catch (e) {
    toast.push((e as Error).message, 'error')
  }
}

async function confirm() {
  try {
    await cognito.confirmPassword(email.value, code.value, newPassword.value)
    toast.push('Password updated. You can sign in.', 'success')
  } catch (e) {
    toast.push((e as Error).message, 'error')
  }
}
</script>

<template>
  <div class="flex min-h-screen items-center justify-center px-4">
    <div class="glass-card w-full max-w-md p-8 page-enter">
      <h1 class="text-2xl font-bold">Reset password</h1>
      <form v-if="step === 'request'" class="mt-6 space-y-4" @submit.prevent="requestCode">
        <input v-model="email" type="email" required class="input-field" placeholder="Email" />
        <button type="submit" class="btn-primary w-full">Send reset code</button>
      </form>
      <form v-else class="mt-6 space-y-4" @submit.prevent="confirm">
        <input v-model="code" class="input-field" placeholder="Verification code" required />
        <input v-model="newPassword" type="password" class="input-field" placeholder="New password" required minlength="8" />
        <button type="submit" class="btn-primary w-full">Update password</button>
      </form>
      <p class="mt-4 text-center text-sm"><router-link to="/auth/login" class="text-accent">Back to sign in</router-link></p>
    </div>
  </div>
</template>
