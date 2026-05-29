<script setup lang="ts">
defineProps<{ label: string; value: string | number; icon?: string }>()
</script>

<template>
  <div class="glass-card group p-5 transition duration-300 hover:-translate-y-1 hover:shadow-lift">
    <div class="flex items-start justify-between">
      <div>
        <p class="text-xs font-semibold uppercase tracking-wide text-muted-light dark:text-muted-dark">{{ label }}</p>
        <p class="mt-2 text-3xl font-bold tabular-nums tracking-tight">{{ value }}</p>
      </div>
      <span
        class="flex h-10 w-10 items-center justify-center rounded-[12px] bg-black/[0.04] text-lg transition group-hover:scale-105 dark:bg-white/[0.06]"
      >{{ icon || '📊' }}</span>
    </div>
  </div>
</template>
