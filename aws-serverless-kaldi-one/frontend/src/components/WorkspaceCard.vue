<script setup lang="ts">
defineProps<{
  title: string
  description: string
  icon: string
  active?: boolean
}>()
defineEmits<{ select: [] }>()
</script>

<template>
  <button
    type="button"
    class="glass-card w-full p-5 text-left transition hover:-translate-y-1 hover:shadow-lift"
    :class="active ? 'ring-2 ring-accent/60' : ''"
    @click="$emit('select')"
  >
    <span class="text-2xl">{{ icon }}</span>
    <h3 class="mt-3 text-base font-semibold">{{ title }}</h3>
    <p class="mt-1 text-sm text-muted-light dark:text-muted-dark">{{ description }}</p>
  </button>
</template>
