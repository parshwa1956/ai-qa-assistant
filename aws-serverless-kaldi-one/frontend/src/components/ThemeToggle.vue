<script setup lang="ts">
import { computed } from 'vue'
import { useThemeStore } from '@/stores/theme'

const theme = useThemeStore()

const label = computed(() => {
  if (theme.mode === 'dark') return 'Light mode'
  if (theme.mode === 'light') return 'Dark mode'
  return 'Toggle theme'
})
</script>

<template>
  <button
    type="button"
    class="flex items-center gap-2 rounded-xl border border-black/5 bg-white/70 px-3 py-2 text-sm font-medium shadow-sm transition hover:shadow-soft dark:border-white/10 dark:bg-white/5"
    :aria-label="label"
    @click="theme.toggle()"
  >
    <span class="flex h-6 w-6 items-center justify-center rounded-lg bg-black/5 text-xs dark:bg-white/10">
      {{ theme.mode === 'light' ? '🌙' : '☀️' }}
    </span>
    <span class="hidden text-muted-light dark:text-muted-dark xl:inline">{{ label }}</span>
  </button>
</template>
