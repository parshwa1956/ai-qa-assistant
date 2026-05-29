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
    class="glass-card w-full p-5 text-left transition duration-300 hover:-translate-y-1 hover:shadow-lift active:scale-[0.99]"
    :class="active ? 'ring-2 ring-accent/50 ring-offset-2 ring-offset-transparent dark:ring-offset-surface-dark' : ''"
    @click="$emit('select')"
  >
    <span class="flex h-10 w-10 items-center justify-center rounded-[12px] bg-accent/10 text-xl">{{ icon }}</span>
    <h3 class="mt-3 text-base font-semibold tracking-tight">{{ title }}</h3>
    <p class="mt-1.5 text-sm leading-snug text-muted-light dark:text-muted-dark">{{ description }}</p>
  </button>
</template>
