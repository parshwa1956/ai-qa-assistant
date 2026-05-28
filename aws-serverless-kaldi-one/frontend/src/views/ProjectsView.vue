<script setup lang="ts">
import { ref } from 'vue'
import AppShell from '@/components/AppShell.vue'
import { useProjectStore } from '@/stores/projects'
import { useToastStore } from '@/stores/toast'

const projects = useProjectStore()
const toast = useToastStore()
const renameId = ref<string | null>(null)
const renameValue = ref('')

async function saveRename(projectId: string) {
  try {
    await projects.rename(projectId, renameValue.value)
    renameId.value = null
    toast.push('Project renamed', 'success')
  } catch (e) {
    toast.push((e as Error).message, 'error')
  }
}

async function removeProject(projectId: string, name: string) {
  if (name === 'General') {
    toast.push('Cannot delete General project', 'error')
    return
  }
  if (!confirm(`Delete project "${name}" and its history?`)) return
  try {
    await projects.remove(projectId)
    toast.push('Project deleted', 'success')
  } catch (e) {
    toast.push((e as Error).message, 'error')
  }
}
</script>

<template>
  <AppShell>
    <template #title>Projects</template>
    <template #subtitle>Organize outputs by project</template>

    <div class="space-y-3">
      <div v-for="p in projects.projects" :key="p.projectId" class="glass-card flex flex-wrap items-center justify-between gap-4 p-4 transition hover:shadow-soft">
        <div>
          <p class="font-semibold">{{ p.name }} <span v-if="p.isDefault" class="text-xs text-accent">(default)</span></p>
          <p class="text-xs text-muted-light dark:text-muted-dark">Updated {{ p.updatedAt?.slice(0, 10) }}</p>
        </div>
        <div class="flex gap-2">
          <template v-if="renameId === p.projectId">
            <input v-model="renameValue" class="input-field !w-40" />
            <button type="button" class="btn-primary !px-3" @click="saveRename(p.projectId)">Save</button>
          </template>
          <button
            v-else-if="!p.isDefault && p.name !== 'General'"
            type="button"
            class="btn-secondary !text-xs"
            @click="renameId = p.projectId; renameValue = p.name"
          >Rename</button>
          <button
            v-if="!p.isDefault && p.name !== 'General'"
            type="button"
            class="text-xs text-red-500"
            @click="removeProject(p.projectId, p.name)"
          >Delete</button>
        </div>
      </div>
    </div>
  </AppShell>
</template>
