<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import * as cognito from '@/services/cognito'
import { useToastStore } from '@/stores/toast'

const route = useRoute()
const router = useRouter()
const toast = useToastStore()

const email = ref((route.query.email as string) || '')
const code = ref('')
const busy = ref(false)

async function confirm() {
  if (!email.value || !code.value) {
    toast.push('Enter your email and verification code', 'error')
    return
  }
  busy.value = true
  try {
    await cognito.confirmSignUp(email.value, code.value)
    toast.push('Email confirmed. You can sign in now.', 'success')
    router.push('/auth/login')
  } catch (e) {
    toast.push((e as Error).message || 'Confirmation failed', 'error')
  } finally {
    busy.value = false
  }
}

async function resend() {
  if (!email.value) {
    toast.push('Enter your email first', 'error')
    return
  }
  busy.value = true
  try {
    await cognito.resendConfirmationCode(email.value)
    toast.push('Verification code sent. Check inbox and spam.', 'info')
  } catch (e) {
    toast.push((e as Error).message || 'Could not resend code', 'error')
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <div class="flex min-h-screen items-center justify-center px-4">
    <div class="glass-card w-full max-w-md p-8 page-enter">
      <h1 class="text-2xl font-bold">Confirm your email</h1>
      <p class="mt-2 text-sm text-muted-light dark:text-muted-dark">
        Cognito sent a verification code to your email. If you did not receive it, ask an admin to confirm your
        account in the AWS Console, or resend the code below.
      </p>
      <form class="mt-6 space-y-4" @submit.prevent="confirm">
        <input v-model="email" type="email" required class="input-field" placeholder="Email" />
        <input v-model="code" type="text" required class="input-field" placeholder="Verification code" autocomplete="one-time-code" />
        <button type="submit" class="btn-primary w-full" :disabled="busy">Confirm email</button>
      </form>
      <div class="mt-4 flex flex-col gap-2 text-center text-sm">
        <button type="button" class="text-accent hover:underline" :disabled="busy" @click="resend">Resend code</button>
        <router-link to="/auth/login" class="text-accent hover:underline">Back to sign in</router-link>
      </div>
    </div>
  </div>
</template>
