<script setup lang="ts">
import { ref } from 'vue'
import { SCREEN_CAPTURE_INFO } from '@/data/screenCaptureHelp'

const props = withDefaults(
  defineProps<{
    variant?: 'compact' | 'full'
    defaultExpanded?: boolean
  }>(),
  {
    variant: 'compact',
    defaultExpanded: false,
  },
)

const expanded = ref(props.defaultExpanded)
</script>

<template>
  <div
    class="rounded-[14px] border border-blue-500/20 bg-blue-500/5 dark:border-blue-400/20 dark:bg-blue-500/10"
    role="note"
    aria-label="Screen capture information"
  >
    <button
      v-if="variant === 'compact'"
      type="button"
      class="flex w-full items-start gap-2 px-3 py-2.5 text-left text-sm"
      :aria-expanded="expanded"
      @click="expanded = !expanded"
    >
      <span class="mt-0.5 shrink-0 text-base" aria-hidden="true">ℹ️</span>
      <span class="flex-1">
        <span class="font-medium text-ink-light dark:text-ink-dark">{{ SCREEN_CAPTURE_INFO.title }}</span>
        <span class="mt-0.5 block text-xs leading-relaxed text-muted-light dark:text-muted-dark">
          {{ SCREEN_CAPTURE_INFO.shortHint }}
        </span>
      </span>
      <span class="shrink-0 text-xs text-accent">{{ expanded ? 'Less' : 'More' }}</span>
    </button>

    <div v-if="variant === 'full' || expanded" class="border-t border-blue-500/15 px-3 py-3 dark:border-blue-400/15">
      <p v-if="variant === 'full'" class="mb-3 text-sm leading-relaxed text-muted-light dark:text-muted-dark">
        {{ SCREEN_CAPTURE_INFO.summary }}
      </p>
      <ul class="space-y-3">
        <li v-for="(point, i) in SCREEN_CAPTURE_INFO.points" :key="i">
          <p class="text-sm font-medium text-ink-light dark:text-ink-dark">{{ point.heading }}</p>
          <p class="mt-0.5 text-xs leading-relaxed text-muted-light dark:text-muted-dark">{{ point.text }}</p>
        </li>
      </ul>
    </div>
  </div>
</template>
