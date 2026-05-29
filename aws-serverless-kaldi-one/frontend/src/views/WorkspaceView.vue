<script setup lang="ts">
import { ref } from 'vue'
import AppShell from '@/components/AppShell.vue'
import WorkspaceCard from '@/components/WorkspaceCard.vue'
import PromptInputPanel from '@/components/PromptInputPanel.vue'
import OutputPreview from '@/components/OutputPreview.vue'
import { WORKSPACES } from '@/data/workspaces'
import type { GenerationResult, WorkspaceId } from '@/types'
import { api } from '@/services/api'
import { useProjectStore } from '@/stores/projects'
import { useToastStore } from '@/stores/toast'

const activeWorkspace = ref<WorkspaceId>('qa')
const activeTool = ref<string | null>(null)
const result = ref<GenerationResult | null>(null)
const loading = ref(false)
const lastInput = ref({ title: '', context: '' })
const projects = useProjectStore()
const toast = useToastStore()

function selectWorkspace(id: WorkspaceId) {
  activeWorkspace.value = id
  activeTool.value = null
  result.value = null
}

async function generate(payload: { title: string; context: string; objectKey?: string; sourceFilename?: string; contentType?: string }) {
  if (!activeTool.value || !projects.selectedId) {
    toast.push('Select a tool and project first', 'error')
    return
  }
  loading.value = true
  lastInput.value = { title: payload.title, context: payload.context }
  try {
    result.value = (await api.generate({
      workspace: activeWorkspace.value === 'flow' ? 'flow' : activeWorkspace.value,
      outputType: activeTool.value,
      title: payload.title,
      context: payload.context,
      projectId: projects.selectedId,
      objectKey: payload.objectKey,
      sourceFilename: payload.sourceFilename,
      contentType: payload.contentType,
      codeInput: activeTool.value === 'Smart Code Review' ? payload.context : undefined,
    })) as GenerationResult
  } catch (e) {
    toast.push((e as Error).message, 'error')
  } finally {
    loading.value = false
  }
}

async function saveOutput() {
  if (!result.value || !projects.selectedId) return
  await api.saveHistory({
    projectId: projects.selectedId,
    itemType: result.value.outputType,
    title: lastInput.value.title || result.value.outputType,
    inputContext: lastInput.value.context,
    outputText: result.value.outputText,
    outputJson: result.value.outputJson,
    mermaidCode: result.value.mermaidCode,
    workspace: WORKSPACES[activeWorkspace.value].label,
  })
  toast.push('Saved to history', 'success')
}

function downloadLocal(format: string) {
  if (!result.value) return
  const text = result.value.outputText
  const blob = new Blob([text], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${result.value.outputType}.${format === 'xlsx' ? 'txt' : format}`
  a.click()
  URL.revokeObjectURL(url)
}

async function createJira() {
  if (!result.value) return
  try {
    const res = await api.createJiraIssue({
      summary: lastInput.value.title || result.value.outputType,
      description: result.value.outputText,
      outputType: result.value.outputType,
    })
    toast.push((res as { message: string }).message, (res as { success: boolean }).success ? 'success' : 'error')
  } catch (e) {
    toast.push((e as Error).message, 'error')
  }
}
</script>

<template>
  <AppShell>
    <template #title>Workspace</template>
    <template #subtitle>Choose a workspace and AI tool</template>

    <div class="mb-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-4" data-guide="workspace-nav">
      <WorkspaceCard
        v-for="(ws, id) in WORKSPACES"
        :key="id"
        :title="ws.label"
        :description="`${ws.tools.length} AI tools`"
        :icon="ws.icon"
        :active="activeWorkspace === id"
        @select="selectWorkspace(id as WorkspaceId)"
      />
    </div>

    <div v-if="activeWorkspace" class="mb-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
      <WorkspaceCard
        v-for="tool in WORKSPACES[activeWorkspace].tools"
        :key="tool.id"
        :title="tool.label"
        :description="tool.description"
        :icon="tool.icon"
        :active="activeTool === tool.id"
        @select="activeTool = tool.id"
      />
    </div>

    <div v-if="activeTool" class="grid gap-6 lg:grid-cols-2">
      <PromptInputPanel
        :accept="activeWorkspace === 'dev' ? '.py,.js,.ts,.txt,.png,.jpg,.pdf' : '.txt,.pdf,.png,.jpg,.csv,.md,.doc,.docx'"
        @submit="generate"
      >
        <template #button>{{ loading ? 'Generating…' : 'Generate' }}</template>
      </PromptInputPanel>
      <OutputPreview
        :result="result"
        :loading="loading"
        @save="saveOutput"
        @export="downloadLocal"
        @jira="createJira"
      />
    </div>
  </AppShell>
</template>
