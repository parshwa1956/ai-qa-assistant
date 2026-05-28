<script setup lang="ts">
defineProps<{ lines?: number }>()
</script>

<template>
  <div class="animate-pulse space-y-3">
    <div v-for="n in (lines || 4)" :key="n" class="h-4 rounded-lg bg-gray-200/80 dark:bg-white/10" :style="{ width: `${90 - n * 8}%` }" />
  </div>
</template>
