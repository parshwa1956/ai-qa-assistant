import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import type { Project } from '@/types'
import { api } from '@/services/api'

export const useProjectStore = defineStore('projects', () => {
  const projects = ref<Project[]>([])
  const selectedId = ref<string | null>(null)

  const selected = computed(() => projects.value.find((p) => p.projectId === selectedId.value) || projects.value[0])

  function setProjects(list: Project[]) {
    projects.value = list
    if (!selectedId.value && list.length) {
      const general = list.find((p) => p.name === 'General') || list[0]
      selectedId.value = general.projectId
    }
  }

  async function refresh() {
    const { projects: list } = await api.getProjects()
    setProjects(list as Project[])
  }

  async function create(name: string) {
    const { project } = await api.createProject(name) as { project: Project }
    projects.value.unshift(project)
    selectedId.value = project.projectId
  }

  async function rename(projectId: string, name: string) {
    await api.updateProject(projectId, name)
    await refresh()
  }

  async function remove(projectId: string) {
    await api.deleteProject(projectId)
    await refresh()
    if (selectedId.value === projectId) {
      selectedId.value = projects.value[0]?.projectId || null
    }
  }

  function $reset() {
    projects.value = []
    selectedId.value = null
  }

  return { projects, selectedId, selected, setProjects, refresh, create, rename, remove, $reset }
})
