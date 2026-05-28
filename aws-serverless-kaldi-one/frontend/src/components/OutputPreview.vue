<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import type { GenerationResult } from '@/types'
import mermaid from 'mermaid'
import EmptyState from './EmptyState.vue'
import LoadingSkeleton from './LoadingSkeleton.vue'

const props = defineProps<{
  result: GenerationResult | null
  loading?: boolean
}>()

defineEmits<{
  save: []
  export: [format: string]
  jira: []
}>()

const diagramRef = ref<HTMLElement>()

const tableRows = computed(() => props.result?.tableData || [])

watch(
  () => props.result?.mermaidCode,
  async (code) => {
    if (!code || !diagramRef.value) return
    try {
      mermaid.initialize({ startOnLoad: false, theme: document.documentElement.classList.contains('dark') ? 'dark' : 'default' })
      const { svg } = await mermaid.render(`mmd-${Date.now()}`, code)
      diagramRef.value.innerHTML = svg
    } catch {
      diagramRef.value.textContent = code
    }
  },
  { immediate: true },
)

onMounted(() => mermaid.initialize({ startOnLoad: false }))
</script>

<template>
  <div class="glass-card p-6">
    <div class="mb-4 flex flex-wrap items-center justify-between gap-3">
      <h3 class="text-lg font-semibold">Generated Output</h3>
      <div v-if="result && !loading" class="flex flex-wrap gap-2">
        <button type="button" class="btn-secondary text-xs" @click="$emit('save')">Save</button>
        <button type="button" class="btn-secondary text-xs" @click="$emit('export', 'txt')">TXT</button>
        <button type="button" class="btn-secondary text-xs" @click="$emit('export', 'csv')">CSV</button>
        <button type="button" class="btn-secondary text-xs" @click="$emit('export', 'xlsx')">XLSX</button>
        <button type="button" class="btn-secondary text-xs" @click="$emit('jira')">Create Jira</button>
      </div>
    </div>

    <div v-if="loading" class="py-8">
      <LoadingSkeleton :lines="6" />
      <p class="mt-4 text-center text-sm text-muted-light animate-pulse dark:text-muted-dark">Generating with AI…</p>
    </div>

    <EmptyState v-else-if="!result" title="No output yet" description="Select a tool, add your input, and click Generate." />

    <template v-else>
      <div v-if="result.mermaidCode" ref="diagramRef" class="mb-6 overflow-x-auto rounded-xl bg-white/50 p-4 dark:bg-black/20" />
      <pre class="max-h-[420px] overflow-auto whitespace-pre-wrap rounded-xl bg-gray-50/80 p-4 text-sm leading-relaxed dark:bg-black/30">{{ result.outputText }}</pre>
      <div v-if="tableRows.length" class="mt-4 overflow-x-auto">
        <table class="w-full text-left text-sm">
          <thead>
            <tr class="border-b border-gray-200 dark:border-white/10">
              <th v-for="key in Object.keys(tableRows[0])" :key="key" class="px-3 py-2 font-semibold">{{ key }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, idx) in tableRows" :key="idx" class="border-b border-gray-100 dark:border-white/5">
              <td v-for="key in Object.keys(tableRows[0])" :key="key" class="px-3 py-2 align-top">{{ row[key] }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>
  </div>
</template>
