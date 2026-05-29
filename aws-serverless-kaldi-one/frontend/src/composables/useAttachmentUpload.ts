import { ref } from 'vue'
import { api } from '@/services/api'
import { useProjectStore } from '@/stores/projects'
import { useToastStore } from '@/stores/toast'

export function useAttachmentUpload() {
  const uploading = ref(false)
  const fileName = ref('')
  const objectKey = ref<string>()
  const contentType = ref<string>()
  const previewUrl = ref<string>()

  const projects = useProjectStore()
  const toast = useToastStore()

  function clearPreview() {
    if (previewUrl.value?.startsWith('blob:')) {
      URL.revokeObjectURL(previewUrl.value)
    }
    previewUrl.value = ''
  }

  function resetAttachment() {
    clearPreview()
    fileName.value = ''
    objectKey.value = undefined
    contentType.value = undefined
  }

  async function uploadBlob(blob: Blob, filename: string, mime: string, localPreview?: string) {
    if (!projects.selectedId) {
      throw new Error('Select a project first')
    }
    uploading.value = true
    try {
      const presign = await api.presignUpload({
        filename,
        contentType: mime,
        projectId: projects.selectedId,
      })
      await fetch(presign.uploadUrl, {
        method: 'PUT',
        body: blob,
        headers: { 'Content-Type': mime },
      })
      clearPreview()
      objectKey.value = presign.objectKey
      contentType.value = mime
      fileName.value = filename
      if (localPreview) previewUrl.value = localPreview
      toast.push('Screenshot attached', 'success')
      return presign.objectKey
    } finally {
      uploading.value = false
    }
  }

  async function uploadFile(file: File): Promise<string | undefined> {
    if (!projects.selectedId) {
      toast.push('Select a project first', 'error')
      return undefined
    }
    uploading.value = true
    try {
      const presign = await api.presignUpload({
        filename: file.name,
        contentType: file.type || 'application/octet-stream',
        projectId: projects.selectedId,
      })
      await fetch(presign.uploadUrl, {
        method: 'PUT',
        body: file,
        headers: { 'Content-Type': file.type || 'application/octet-stream' },
      })
      objectKey.value = presign.objectKey
      contentType.value = file.type
      fileName.value = file.name
      if (file.type.startsWith('image/')) {
        clearPreview()
        previewUrl.value = URL.createObjectURL(file)
      }
      toast.push('File uploaded', 'success')
      return presign.objectKey
    } catch (err) {
      toast.push((err as Error).message, 'error')
      return undefined
    } finally {
      uploading.value = false
    }
  }

  function getPayloadExtras() {
    return {
      objectKey: objectKey.value,
      sourceFilename: fileName.value,
      contentType: contentType.value,
    }
  }

  return {
    uploading,
    fileName,
    objectKey,
    contentType,
    previewUrl,
    uploadBlob,
    uploadFile,
    resetAttachment,
    clearPreview,
    getPayloadExtras,
  }
}
