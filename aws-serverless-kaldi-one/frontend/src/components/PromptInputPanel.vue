<script setup lang="ts">
import { ref } from 'vue'
import { api } from '@/services/api'
import { useProjectStore } from '@/stores/projects'
import { useToastStore } from '@/stores/toast'

const props = defineProps<{
  titleLabel?: string
  accept?: string
}>()

const emit = defineEmits<{
  submit: [payload: { title: string; context: string; objectKey?: string; sourceFilename?: string; contentType?: string }]
}>()

const title = ref('')
const context = ref('')
const uploading = ref(false)
const fileName = ref('')
const objectKey = ref<string>()
const contentType = ref<string>()

const projects = useProjectStore()
const toast = useToastStore()

async function onFileChange(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file || !projects.selectedId) return
  uploading.value = true
  try {
    const presign = await api.presignUpload({
      filename: file.name,
      contentType: file.type || 'application/octet-stream',
      projectId: projects.selectedId,
    })
    await fetch(presign.uploadUrl, { method: 'PUT', body: file, headers: { 'Content-Type': file.type } })
    objectKey.value = presign.objectKey
    contentType.value = file.type
    fileName.value = file.name
    if (file.type.startsWith('text/') || file.name.endsWith('.md') || file.name.endsWith('.csv')) {
      context.value = await file.text()
    }
    toast.push('File uploaded', 'success')
  } catch (err) {
    toast.push((err as Error).message, 'error')
  } finally {
    uploading.value = false
  }
}

function submit() {
  emit('submit', {
    title: title.value,
    context: context.value,
    objectKey: objectKey.value,
    sourceFilename: fileName.value,
    contentType: contentType.value,
  })
}
</script>

<template>
  <div class="glass-card space-y-4 p-6">
    <div>
      <label class="mb-1 block text-sm font-medium">{{ titleLabel || 'Title / Requirement' }}</label>
      <input v-model="title" class="input-field" placeholder="Enter title or feature name" />
    </div>
    <div>
      <label class="mb-1 block text-sm font-medium">Context / Details</label>
      <textarea v-model="context" rows="8" class="input-field resize-y" placeholder="Describe the requirement, issue, or paste notes..." />
    </div>
    <div class="flex flex-wrap items-center gap-3">
      <label class="btn-secondary cursor-pointer">
        <input type="file" class="hidden" :accept="accept" @change="onFileChange" />
        {{ uploading ? 'Uploading…' : 'Attach file' }}
      </label>
      <span v-if="fileName" class="text-xs text-muted-light dark:text-muted-dark">{{ fileName }}</span>
    </div>
    <slot name="extra" />
    <div class="flex justify-end">
      <button type="button" class="btn-primary min-w-[140px]" :disabled="uploading" @click="submit">
        <slot name="button">Generate</slot>
      </button>
    </div>
  </div>
</template>
