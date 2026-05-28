<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import ThemeToggle from './ThemeToggle.vue'

defineEmits<{ logout: [] }>()

const route = useRoute()
const router = useRouter()

const links = [
  { to: '/app/dashboard', label: 'Dashboard', icon: '📊' },
  { to: '/app/workspace', label: 'Workspace', icon: '🧪' },
  { to: '/app/history', label: 'History', icon: '📂' },
  { to: '/app/projects', label: 'Projects', icon: '📁' },
  { to: '/app/settings', label: 'Settings', icon: '⚙️' },
]

function isActive(path: string) {
  return route.path.startsWith(path)
}
</script>

<template>
  <aside class="hidden h-full w-64 flex-col border-r border-gray-200/80 bg-card-light/60 p-5 backdrop-blur-glass dark:border-white/10 dark:bg-card-dark/60 lg:flex">
    <div class="mb-8 flex items-center gap-3">
      <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-accent to-accent-soft text-lg font-bold text-white shadow-lift">K</div>
      <div>
        <p class="font-bold">Kaldi One</p>
        <p class="text-xs text-muted-light dark:text-muted-dark">AI QA Assistant</p>
      </div>
    </div>
    <nav class="flex-1 space-y-1">
      <button
        v-for="link in links"
        :key="link.to"
        type="button"
        class="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition"
        :class="isActive(link.to) ? 'bg-accent/15 text-accent' : 'text-muted-light hover:bg-gray-100 dark:text-muted-dark dark:hover:bg-white/5'"
        @click="router.push(link.to)"
      >
        <span>{{ link.icon }}</span>
        {{ link.label }}
      </button>
    </nav>
    <div class="mt-auto flex items-center justify-between pt-4">
      <ThemeToggle />
      <button type="button" class="text-sm text-muted-light hover:text-red-500 dark:text-muted-dark" @click="$emit('logout')">Sign out</button>
    </div>
  </aside>
</template>
