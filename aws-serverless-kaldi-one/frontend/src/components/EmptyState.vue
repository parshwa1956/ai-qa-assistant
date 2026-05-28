<script setup lang="ts">
defineProps<{ title: string; description?: string; icon?: string }>()
</script>

<template>
  <div class="flex flex-col items-center justify-center rounded-2xl border border-dashed border-gray-200 px-8 py-16 text-center dark:border-white/10">
    <span class="mb-4 text-4xl opacity-80">{{ icon || '✨' }}</span>
    <h3 class="text-lg font-semibold text-ink-light dark:text-ink-dark">{{ title }}</h3>
    <p v-if="description" class="mt-2 max-w-md text-sm text-muted-light dark:text-muted-dark">{{ description }}</p>
    <slot />
  </div>
</template>
