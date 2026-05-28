<script setup lang="ts">
import { onMounted, ref } from 'vue'
import AppShell from '@/components/AppShell.vue'
import HistoryTable from '@/components/HistoryTable.vue'
import { api } from '@/services/api'
import type { HistoryItem } from '@/types'
import { useToastStore } from '@/stores/toast'
import { useProjectStore } from '@/stores/projects'

const items = ref<HistoryItem[]>([])
const loading = ref(true)
const search = ref('')
const toast = useToastStore()
const projects = useProjectStore()

async function load() {
  loading.value = true
  try {
    const params: Record<string, string> = {}
    if (projects.selectedId) params.projectId = projects.selectedId
    if (search.value) params.q = search.value
    const res = await api.getHistory(params)
    items.value = res.items as HistoryItem[]
  } finally {
    loading.value = false
  }
}

onMounted(load)

async function remove(item: HistoryItem) {
  await api.deleteHistory(item.itemId)
  toast.push('Deleted', 'success')
  await load()
}

function view(item: HistoryItem) {
  alert(item.outputText?.slice(0, 2000) || 'No content')
}
</script>

<template>
  <AppShell>
    <template #title>History</template>
    <template #subtitle>Search and manage saved outputs</template>

    <div class="mb-4 flex gap-3">
      <input v-model="search" class="input-field max-w-md" placeholder="Search title, type, output…" @keyup.enter="load" />
      <button type="button" class="btn-primary" @click="load">Search</button>
    </div>
    <HistoryTable :items="items" :loading="loading" @view="view" @delete="remove" />
  </AppShell>
</template>
