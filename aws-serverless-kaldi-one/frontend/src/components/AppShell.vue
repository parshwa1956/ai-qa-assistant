<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import SidebarNav from './SidebarNav.vue'
import MobileNav from './MobileNav.vue'
import ProjectSelector from './ProjectSelector.vue'
import GuideTour from './GuideTour.vue'
import ContextualGuide from './ContextualGuide.vue'
import UserProfileBadge from './UserProfileBadge.vue'

const auth = useAuthStore()
const router = useRouter()

async function logout() {
  await auth.logout()
  router.push('/auth/login')
}
</script>

<template>
  <div class="ios-app-shell flex min-h-screen">
    <SidebarNav @logout="logout" />
    <div class="flex min-h-screen flex-1 flex-col pb-[4.5rem] lg:pb-0">
      <header class="ios-header sticky top-0 z-30 px-4 py-3 lg:px-8 lg:py-4">
        <div class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div class="min-w-0">
            <h1 class="truncate text-xl font-bold tracking-tight lg:text-2xl">
              <slot name="title">Kaldi One</slot>
            </h1>
            <p v-if="$slots.subtitle" class="mt-0.5 text-sm text-muted-light dark:text-muted-dark">
              <slot name="subtitle" />
            </p>
          </div>
          <div class="flex flex-col gap-3 sm:flex-row sm:items-start lg:max-w-md lg:flex-1 lg:justify-end">
            <UserProfileBadge class="lg:hidden" />
            <div data-guide="project-selector" class="w-full sm:min-w-[200px] lg:max-w-xs">
              <ProjectSelector />
            </div>
          </div>
        </div>
      </header>
      <main class="flex-1 px-4 py-5 page-enter lg:px-8 lg:py-6">
        <ContextualGuide />
        <slot />
      </main>
    </div>
    <MobileNav />
    <GuideTour />
  </div>
</template>
