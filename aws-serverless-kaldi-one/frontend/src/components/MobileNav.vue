<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const tabs = [
  { to: '/app/dashboard', label: 'Home', icon: '◉' },
  { to: '/app/workspace', label: 'Work', icon: '◎' },
  { to: '/app/history', label: 'History', icon: '▣' },
  { to: '/app/settings', label: 'Settings', icon: '⚙' },
]

const emailShort = computed(() => {
  const e = auth.email || ''
  if (e.length > 22) return e.slice(0, 20) + '…'
  return e
})
</script>

<template>
  <nav
    class="ios-tab-bar fixed bottom-0 left-0 right-0 z-40 lg:hidden"
    aria-label="Mobile navigation"
  >
    <p
      v-if="auth.email"
      class="border-b border-black/5 px-4 py-1.5 text-center text-[10px] font-medium text-muted-light dark:border-white/10 dark:text-muted-dark"
    >
      {{ emailShort }}
    </p>
    <div class="flex px-1 py-1.5">
      <button
        v-for="tab in tabs"
        :key="tab.to"
        type="button"
        class="flex flex-1 flex-col items-center gap-0.5 rounded-xl py-1.5 text-[10px] font-semibold transition"
        :class="route.path.startsWith(tab.to) ? 'text-accent' : 'text-muted-light dark:text-muted-dark'"
        @click="router.push(tab.to)"
      >
        <span class="text-base leading-none">{{ tab.icon }}</span>
        {{ tab.label }}
      </button>
    </div>
  </nav>
</template>
