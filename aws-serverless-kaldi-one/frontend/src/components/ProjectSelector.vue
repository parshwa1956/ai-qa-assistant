<script setup lang="ts">
import { ref } from 'vue'
import { useProjectStore } from '@/stores/projects'
import { useToastStore } from '@/stores/toast'

const projects = useProjectStore()
const toast = useToastStore()
const newName = ref('')
const showCreate = ref(false)

async function createProject() {
  if (!newName.value.trim()) return
  try {
    await projects.create(newName.value.trim())
    newName.value = ''
    showCreate.value = false
    toast.push('Project created', 'success')
  } catch (e) {
    toast.push((e as Error).message, 'error')
  }
}
</script>

<template>
  <div class="space-y-2">
    <label class="text-xs font-medium uppercase tracking-wide text-muted-light dark:text-muted-dark">Project</label>
    <select v-model="projects.selectedId" class="input-field">
      <option v-for="p in projects.projects" :key="p.projectId" :value="p.projectId">{{ p.name }}</option>
    </select>
    <button type="button" class="text-xs font-medium text-accent hover:underline" @click="showCreate = !showCreate">
      + New project
    </button>
    <div v-if="showCreate" class="flex gap-2">
      <input v-model="newName" class="input-field flex-1" placeholder="Project name" />
      <button type="button" class="btn-primary !px-3" @click="createProject">Add</button>
    </div>
  </div>
</template>
