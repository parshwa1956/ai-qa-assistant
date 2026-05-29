import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

const STORAGE_KEY = 'kaldi-guide-v2'

interface GuidePersist {
  tourCompleted: boolean
  dismissedTips: string[]
}

function load(): GuidePersist {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) return JSON.parse(raw) as GuidePersist
  } catch {
    /* ignore */
  }
  return { tourCompleted: false, dismissedTips: [] }
}

function save(state: GuidePersist) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state))
}

export interface TourStep {
  id: string
  title: string
  body: string
  route?: string
  highlight?: string
}

export const TOUR_STEPS: TourStep[] = [
  {
    id: 'welcome',
    title: 'Welcome to Kaldi One',
    body: 'Your AI workspace for QA, Business Analysis, and Development. This short tour shows you where everything lives.',
    route: '/app/dashboard',
  },
  {
    id: 'profile',
    title: 'Your account',
    body: 'Your signed-in email appears here. All outputs and projects are private to your account.',
    highlight: 'user-profile',
  },
  {
    id: 'project',
    title: 'Projects organize work',
    body: 'Select a project before generating. Use General for quick tasks, or create projects per feature or sprint.',
    highlight: 'project-selector',
  },
  {
    id: 'workspace',
    title: 'AI Workspace',
    body: 'Pick QA, BA, Dev, or Flow to Requirement. Choose a tool, add context, attach files, then Generate.',
    route: '/app/workspace',
    highlight: 'workspace-nav',
  },
  {
    id: 'history',
    title: 'History & exports',
    body: 'Save outputs to History. Search, filter by project, and export TXT, CSV, or XLSX anytime.',
    route: '/app/history',
  },
  {
    id: 'settings',
    title: 'Settings & Jira',
    body: 'Connect Jira to create issues from generated bug reports and tasks. Theme toggle supports light and dark mode.',
    route: '/app/settings',
  },
]

export const useGuideStore = defineStore('guide', () => {
  const persist = ref<GuidePersist>(load())
  const tourActive = ref(false)
  const tourStepIndex = ref(0)

  const tourCompleted = computed(() => persist.value.tourCompleted)
  const currentTourStep = computed(() => TOUR_STEPS[tourStepIndex.value])

  function startTour(fromBeginning = true) {
    if (fromBeginning) tourStepIndex.value = 0
    tourActive.value = true
  }

  function nextTourStep() {
    if (tourStepIndex.value < TOUR_STEPS.length - 1) {
      tourStepIndex.value += 1
    } else {
      completeTour()
    }
  }

  function prevTourStep() {
    if (tourStepIndex.value > 0) tourStepIndex.value -= 1
  }

  function completeTour() {
    tourActive.value = false
    persist.value.tourCompleted = true
    save(persist.value)
  }

  function skipTour() {
    tourActive.value = false
    persist.value.tourCompleted = true
    save(persist.value)
  }

  function resetTour() {
    persist.value.tourCompleted = false
    persist.value.dismissedTips = []
    save(persist.value)
    tourStepIndex.value = 0
    tourActive.value = true
  }

  function isTipDismissed(id: string) {
    return persist.value.dismissedTips.includes(id)
  }

  function dismissTip(id: string) {
    if (!persist.value.dismissedTips.includes(id)) {
      persist.value.dismissedTips.push(id)
      save(persist.value)
    }
  }

  function maybeAutoStartTour() {
    if (!persist.value.tourCompleted) {
      tourStepIndex.value = 0
      tourActive.value = true
    }
  }

  return {
    tourActive,
    tourStepIndex,
    tourCompleted,
    currentTourStep,
    startTour,
    nextTourStep,
    prevTourStep,
    completeTour,
    skipTour,
    resetTour,
    isTipDismissed,
    dismissTip,
    maybeAutoStartTour,
    totalSteps: TOUR_STEPS.length,
  }
})
