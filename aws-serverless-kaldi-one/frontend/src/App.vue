<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import ToastNotification from '@/components/ToastNotification.vue'

const auth = useAuthStore()
const theme = useThemeStore()
const router = useRouter()

onMounted(async () => {
  theme.setMode(theme.mode)
  const ok = await auth.restoreSession()
  if (ok && router.currentRoute.value.meta.guest) {
    router.push('/app/workspace')
  }
})
</script>

<template>
  <router-view />
  <ToastNotification />
</template>
