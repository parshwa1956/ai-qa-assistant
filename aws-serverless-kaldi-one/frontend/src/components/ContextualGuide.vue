<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import { tipForRoute } from '@/data/contextualTips'
import { useGuideStore } from '@/stores/guide'

const route = useRoute()
const guide = useGuideStore()
const expanded = ref(true)

const tip = computed(() => tipForRoute(route.path))
const visible = computed(() => tip.value && !guide.isTipDismissed(tip.value!.id))

function dismiss() {
  if (tip.value) guide.dismissTip(tip.value.id)
}
</script>

<template>
  <div v-if="visible && tip" class="mb-6 guide-tip-card page-enter">
    <button
      type="button"
      class="flex w-full items-center justify-between gap-3 text-left"
      @click="expanded = !expanded"
    >
      <div class="flex items-center gap-2">
        <span class="flex h-8 w-8 items-center justify-center rounded-full bg-accent/15 text-sm">💡</span>
        <span class="font-semibold">{{ tip.title }}</span>
      </div>
      <span class="text-muted-light dark:text-muted-dark">{{ expanded ? '−' : '+' }}</span>
    </button>
    <ol v-show="expanded" class="mt-4 space-y-2 border-t border-gray-200/60 pt-4 text-sm leading-relaxed dark:border-white/10">
      <li v-for="(step, i) in tip.steps" :key="i" class="flex gap-2">
        <span class="font-medium text-accent">{{ i + 1 }}.</span>
        <span class="text-muted-light dark:text-muted-dark">{{ step }}</span>
      </li>
    </ol>
    <button type="button" class="mt-3 text-xs font-medium text-muted-light hover:text-accent dark:text-muted-dark" @click="dismiss">
      Got it, hide this guide
    </button>
  </div>
</template>
