<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import SidebarNav from './SidebarNav.vue'
import MobileNav from './MobileNav.vue'
import ProjectSelector from './ProjectSelector.vue'

const auth = useAuthStore()
const router = useRouter()

async function logout() {
  await auth.logout()
  router.push('/auth/login')
}
</script>

<template>
  <div class="flex min-h-screen bg-gradient-to-br from-surface-light via-white to-blue-50/40 dark:from-surface-dark dark:via-surface-dark dark:to-slate-900/40">
    <SidebarNav @logout="logout" />
    <div class="flex min-h-screen flex-1 flex-col pb-20 lg:pb-0">
      <header class="sticky top-0 z-30 border-b border-gray-200/60 bg-card-light/70 px-4 py-4 backdrop-blur-glass dark:border-white/10 dark:bg-card-dark/70 lg:px-8">
        <div class="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h1 class="text-xl font-bold lg:text-2xl"><slot name="title">Kaldi One</slot></h1>
            <p v-if="$slots.subtitle" class="text-sm text-muted-light dark:text-muted-dark"><slot name="subtitle" /></p>
          </div>
          <div class="w-full max-w-xs"><ProjectSelector /></div>
        </div>
      </header>
      <main class="flex-1 px-4 py-6 page-enter lg:px-8">
        <slot />
      </main>
    </div>
    <MobileNav />
  </div>
</template>
