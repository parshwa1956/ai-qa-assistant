<script setup lang="ts">
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

const initials = computed(() => {
  const e = auth.email || ''
  const part = e.split('@')[0] || 'U'
  const bits = part.split(/[._-]/).filter(Boolean)
  if (bits.length >= 2) return (bits[0][0] + bits[1][0]).toUpperCase()
  return part.slice(0, 2).toUpperCase()
})

const displayEmail = computed(() => auth.email || 'Signed in')
</script>

<template>
  <div
    data-guide="user-profile"
    class="flex items-center gap-3 rounded-2xl border border-white/50 bg-white/60 p-3 shadow-sm backdrop-blur-md dark:border-white/10 dark:bg-white/5"
  >
    <div
      class="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-accent to-indigo-500 text-sm font-bold text-white shadow-md ring-2 ring-white/30 dark:ring-white/10"
      aria-hidden="true"
    >
      {{ initials }}
    </div>
    <div class="min-w-0 flex-1">
      <p class="truncate text-sm font-semibold text-ink-light dark:text-ink-dark">Signed in</p>
      <p class="truncate text-xs text-muted-light dark:text-muted-dark" :title="displayEmail">{{ displayEmail }}</p>
    </div>
  </div>
</template>
