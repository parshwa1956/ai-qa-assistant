<script setup lang="ts">
import { onMounted, ref } from 'vue'
import AppShell from '@/components/AppShell.vue'
import StatCard from '@/components/StatCard.vue'
import LoadingSkeleton from '@/components/LoadingSkeleton.vue'
import { api } from '@/services/api'
import type { DashboardStats } from '@/types'

const stats = ref<DashboardStats | null>(null)
const loading = ref(true)

onMounted(async () => {
  try {
    stats.value = await api.getDashboard()
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <AppShell>
    <template #title>Dashboard</template>
    <template #subtitle>Overview of your projects and AI outputs</template>

    <div v-if="loading" class="grid gap-4 md:grid-cols-3"><LoadingSkeleton v-for="n in 3" :key="n" :lines="2" /></div>
    <div v-else-if="stats" class="space-y-8">
      <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Projects" :value="stats.totalProjects" icon="📁" />
        <StatCard label="Test Cases" :value="stats.totalTestCases" icon="✅" />
        <StatCard label="Bug Reports" :value="stats.totalBugReports" icon="🐛" />
        <StatCard label="Total Saved" :value="stats.totalItems" icon="💾" />
      </div>
      <div class="grid gap-6 lg:grid-cols-2">
        <div class="glass-card p-5">
          <h3 class="font-semibold">Recent projects</h3>
          <ul class="mt-4 space-y-2 text-sm">
            <li v-for="p in stats.recentProjects" :key="p.projectId" class="flex justify-between border-b border-gray-100 py-2 dark:border-white/5">
              <span>{{ p.name }}</span>
              <span class="text-muted-light dark:text-muted-dark">{{ p.updatedAt?.slice(0, 10) }}</span>
            </li>
          </ul>
        </div>
        <div class="glass-card p-5">
          <h3 class="font-semibold">Recent outputs</h3>
          <ul class="mt-4 space-y-2 text-sm">
            <li v-for="i in stats.recentItems" :key="i.itemId" class="flex justify-between border-b border-gray-100 py-2 dark:border-white/5">
              <span>{{ i.title }} <span class="text-muted-light">({{ i.itemType }})</span></span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </AppShell>
</template>
