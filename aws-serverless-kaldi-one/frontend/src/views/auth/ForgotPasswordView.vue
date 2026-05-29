<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import * as cognito from '@/services/cognito'
import { useToastStore } from '@/stores/toast'

const email = ref('')
const code = ref('')
const newPassword = ref('')
const step = ref<'request' | 'confirm' | 'success'>('request')
const busy = ref(false)
const toast = useToastStore()
const router = useRouter()

function resetCodeErrorMessage(err: unknown): string {
  const c = (err as { code?: string })?.code
  const msg = (err as Error)?.message || ''
  if (c === 'ExpiredCodeException' || /expired|request a code again/i.test(msg)) {
    return 'This reset code expired or was already used. Send a new code and use the latest email only.'
  }
  if (c === 'CodeMismatchException' || /invalid code/i.test(msg)) {
    return 'Incorrect code. Use the code from the password reset email (not sign-up confirmation).'
  }
  if (c === 'InvalidPasswordException') {
    return 'Password must be at least 8 characters with upper, lower, and number.'
  }
  if (c === 'LimitExceededException') {
    return 'Too many attempts. Wait a few minutes and try again.'
  }
  return msg || 'Password reset failed'
}

async function requestCode() {
  busy.value = true
  try {
    await cognito.forgotPassword(email.value.trim())
    code.value = ''
    step.value = 'confirm'
    toast.push('Reset code sent. Check inbox and spam — codes expire in about an hour.', 'info')
  } catch (e) {
    toast.push((e as Error).message, 'error')
  } finally {
    busy.value = false
  }
}

async function confirm() {
  busy.value = true
  try {
    await cognito.confirmPassword(email.value.trim(), code.value, newPassword.value)
    step.value = 'success'
    toast.push('Password updated successfully.', 'success')
  } catch (e) {
    toast.push(resetCodeErrorMessage(e), 'error')
    const c = (e as { code?: string })?.code
    if (c === 'ExpiredCodeException' || c === 'CodeMismatchException') {
      code.value = ''
    }
  } finally {
    busy.value = false
  }
}

function goToLogin() {
  router.push('/auth/login')
}
</script>

<template>
  <div class="flex min-h-screen items-center justify-center px-4">
    <div class="glass-card w-full max-w-md p-8 page-enter">
      <!-- Success state -->
      <div v-if="step === 'success'" class="text-center">
        <div class="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-green-500/15 text-3xl">✓</div>
        <h1 class="text-2xl font-bold">Password updated</h1>
        <p class="mt-2 text-sm text-muted-light dark:text-muted-dark">
          Your password was reset successfully. Sign in with your new password.
        </p>
        <button type="button" class="btn-primary mt-6 w-full" @click="goToLogin">Go to sign in</button>
      </div>

      <template v-else>
        <h1 class="text-2xl font-bold">Reset password</h1>
        <p v-if="step === 'confirm'" class="mt-2 text-sm text-muted-light dark:text-muted-dark">
          Code sent to <strong>{{ email }}</strong>. Enter the <em>password reset</em> code from email — not the sign-up confirmation code.
        </p>
        <form v-if="step === 'request'" class="mt-6 space-y-4" @submit.prevent="requestCode">
          <input v-model="email" type="email" required class="input-field" placeholder="Email" />
          <button type="submit" class="btn-primary w-full" :disabled="busy">
            {{ busy ? 'Sending…' : 'Send reset code' }}
          </button>
        </form>
        <form v-else class="mt-6 space-y-4" @submit.prevent="confirm">
          <input v-model="code" class="input-field" placeholder="Reset code from email" required autocomplete="one-time-code" />
          <input v-model="newPassword" type="password" class="input-field" placeholder="New password (min 8 chars)" required minlength="8" />
          <button type="submit" class="btn-primary w-full" :disabled="busy">
            {{ busy ? 'Updating…' : 'Update password' }}
          </button>
          <button type="button" class="btn-secondary w-full" :disabled="busy" @click="requestCode">Send new code</button>
        </form>
        <p class="mt-4 text-center text-sm">
          <router-link to="/auth/login" class="text-accent hover:underline">Back to sign in</router-link>
          <span v-if="step === 'confirm'">
            ·
            <router-link to="/auth/confirm" class="text-accent hover:underline">Confirm sign-up email</router-link>
          </span>
        </p>
      </template>
    </div>
  </div>
</template>
