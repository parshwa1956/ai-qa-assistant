<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import ThemeToggle from './ThemeToggle.vue'
import UserProfileBadge from './UserProfileBadge.vue'
import { useGuideStore } from '@/stores/guide'

defineEmits<{ logout: [] }>()

const route = useRoute()
const router = useRouter()
const guide = useGuideStore()

const links = [
  { to: '/app/dashboard', label: 'Dashboard', icon: '◉' },
  { to: '/app/workspace', label: 'Workspace', icon: '◎', guideId: 'workspace-nav' },
  { to: '/app/history', label: 'History', icon: '▣' },
  { to: '/app/projects', label: 'Projects', icon: '▤' },
  { to: '/app/settings', label: 'Settings', icon: '⚙' },
]

function isActive(path: string) {
  return route.path.startsWith(path)
}
</script>

<template>
  <aside
    class="ios-sidebar hidden h-screen w-[17.5rem] shrink-0 flex-col border-r border-black/5 bg-card-light/80 p-4 backdrop-blur-glass dark:border-white/10 dark:bg-card-dark/80 lg:flex"
  >
    <div class="mb-5 flex items-center gap-3 px-1">
      <div
        class="flex h-11 w-11 items-center justify-center rounded-[14px] bg-gradient-to-br from-accent via-blue-500 to-indigo-500 text-lg font-bold text-white shadow-lift"
      >
        K
      </div>
      <div>
        <p class="text-base font-bold tracking-tight">Kaldi One</p>
        <p class="text-[11px] font-medium text-muted-light dark:text-muted-dark">AI QA · BA · Dev</p>
      </div>
    </div>

    <UserProfileBadge class="mb-5" />

    <nav class="flex-1 space-y-1" aria-label="Main">
      <button
        v-for="link in links"
        :key="link.to"
        type="button"
        :data-guide="link.guideId"
        class="nav-pill flex w-full items-center gap-3 px-3 py-2.5 text-[15px] font-medium"
        :class="isActive(link.to) ? 'nav-pill-active' : 'nav-pill-idle'"
        @click="router.push(link.to)"
      >
        <span class="flex h-7 w-7 items-center justify-center rounded-lg text-sm" :class="isActive(link.to) ? 'bg-accent/20' : 'bg-black/5 dark:bg-white/5'">{{ link.icon }}</span>
        {{ link.label }}
      </button>
    </nav>

    <div class="mt-auto space-y-3 border-t border-black/5 pt-4 dark:border-white/10">
      <button
        type="button"
        class="flex w-full items-center gap-2 rounded-xl px-3 py-2 text-sm font-medium text-accent transition hover:bg-accent/10"
        @click="guide.resetTour()"
      >
        <span aria-hidden="true">?</span>
        Replay guided tour
      </button>
      <div class="flex items-center justify-between">
        <ThemeToggle />
        <button
          type="button"
          class="rounded-xl px-3 py-2 text-sm font-medium text-muted-light transition hover:bg-red-500/10 hover:text-red-500 dark:text-muted-dark"
          @click="$emit('logout')"
        >
          Sign out
        </button>
      </div>
    </div>
  </aside>
</template>
