<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const tabs = [
  { to: '/app/dashboard', label: 'Home', icon: '🏠' },
  { to: '/app/workspace', label: 'Work', icon: '🧪' },
  { to: '/app/history', label: 'History', icon: '📂' },
  { to: '/app/settings', label: 'Settings', icon: '⚙️' },
]
</script>

<template>
  <nav class="fixed bottom-0 left-0 right-0 z-40 flex border-t border-gray-200/80 bg-card-light/90 px-2 py-2 backdrop-blur-glass dark:border-white/10 dark:bg-card-dark/90 lg:hidden">
    <button
      v-for="tab in tabs"
      :key="tab.to"
      type="button"
      class="flex flex-1 flex-col items-center gap-0.5 rounded-lg py-1 text-[10px] font-medium"
      :class="route.path.startsWith(tab.to) ? 'text-accent' : 'text-muted-light dark:text-muted-dark'"
      @click="router.push(tab.to)"
    >
      <span class="text-lg">{{ tab.icon }}</span>
      {{ tab.label }}
    </button>
  </nav>
</template>
