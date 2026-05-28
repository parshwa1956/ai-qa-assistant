<script setup lang="ts">
import { useThemeStore } from '@/stores/theme'

const theme = useThemeStore()
</script>

<template>
  <button
    type="button"
    class="btn-secondary !rounded-full !p-2.5"
    aria-label="Toggle theme"
    @click="theme.toggle()"
  >
    <span v-if="theme.mode !== 'light'" class="text-lg">☀️</span>
    <span v-else class="text-lg">🌙</span>
  </button>
</template>
