<script setup lang="ts">
defineProps<{ label: string; value: string | number; icon?: string }>()
</script>

<template>
  <div class="glass-card p-5 transition hover:-translate-y-0.5 hover:shadow-lift">
    <div class="flex items-start justify-between">
      <div>
        <p class="text-sm text-muted-light dark:text-muted-dark">{{ label }}</p>
        <p class="mt-2 text-3xl font-bold tracking-tight">{{ value }}</p>
      </div>
      <span class="text-2xl">{{ icon || '📊' }}</span>
    </div>
  </div>
</template>
