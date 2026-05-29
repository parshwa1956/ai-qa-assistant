<script setup lang="ts">
import { computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useGuideStore } from '@/stores/guide'

const guide = useGuideStore()
const route = useRoute()
const router = useRouter()

const progress = computed(() => ((guide.tourStepIndex + 1) / guide.totalSteps) * 100)

watch(
  () => guide.currentTourStep,
  async (step) => {
    if (!guide.tourActive || !step?.route) return
    if (!route.path.startsWith(step.route)) {
      await router.push(step.route)
    }
  },
  { immediate: true },
)
</script>

<template>
  <Teleport to="body">
    <div
      v-if="guide.tourActive"
      class="fixed inset-0 z-[100] flex items-end justify-center bg-black/40 p-4 backdrop-blur-sm sm:items-center"
      role="dialog"
      aria-modal="true"
      aria-labelledby="guide-tour-title"
    >
      <div class="guide-sheet w-full max-w-lg page-enter">
        <div class="mb-4 h-1.5 overflow-hidden rounded-full bg-gray-200/80 dark:bg-white/10">
          <div
            class="h-full rounded-full bg-gradient-to-r from-accent to-indigo-400 transition-all duration-300"
            :style="{ width: `${progress}%` }"
          />
        </div>
        <p class="text-xs font-medium uppercase tracking-wider text-accent">
          Step {{ guide.tourStepIndex + 1 }} of {{ guide.totalSteps }}
        </p>
        <h2 id="guide-tour-title" class="mt-2 text-xl font-bold">{{ guide.currentTourStep?.title }}</h2>
        <p class="mt-3 text-sm leading-relaxed text-muted-light dark:text-muted-dark">
          {{ guide.currentTourStep?.body }}
        </p>
        <div class="mt-6 flex flex-wrap gap-3">
          <button type="button" class="btn-secondary" @click="guide.skipTour">Skip tour</button>
          <button
            v-if="guide.tourStepIndex > 0"
            type="button"
            class="btn-secondary"
            @click="guide.prevTourStep"
          >
            Back
          </button>
          <button type="button" class="btn-primary ml-auto" @click="guide.nextTourStep">
            {{ guide.tourStepIndex >= guide.totalSteps - 1 ? 'Get started' : 'Next' }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>
