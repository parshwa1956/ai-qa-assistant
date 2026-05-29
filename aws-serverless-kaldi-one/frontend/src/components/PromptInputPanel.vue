<script setup lang="ts">
import { computed, ref } from 'vue'
import { useAttachmentUpload } from '@/composables/useAttachmentUpload'
import { getDisplayCaptureSupport } from '@/services/screenCapture'
import ScreenCaptureModal from './ScreenCaptureModal.vue'
import ScreenCaptureInfo from './ScreenCaptureInfo.vue'

defineProps<{
  titleLabel?: string
  accept?: string
}>()

const emit = defineEmits<{
  submit: [payload: { title: string; context: string; objectKey?: string; sourceFilename?: string; contentType?: string }]
}>()

const title = ref('')
const context = ref('')
const showCaptureModal = ref(false)

const attachmentApi = useAttachmentUpload()
const { uploading, fileName, previewUrl, contentType, uploadBlob, uploadFile, resetAttachment, getPayloadExtras } =
  attachmentApi
const captureSupport = getDisplayCaptureSupport()
const canCaptureScreen = computed(() => captureSupport.supported)

async function onFileChange(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  if (file.type.startsWith('text/') || file.name.endsWith('.md') || file.name.endsWith('.csv')) {
    try {
      context.value = await file.text()
    } catch {
      /* ignore */
    }
  }
  await uploadFile(file)
  input.value = ''
}

async function onScreenCaptured(payload: {
  blob: Blob
  filename: string
  contentType: string
  previewUrl: string
}) {
  await uploadBlob(
    payload.blob,
    payload.filename,
    payload.contentType,
    payload.previewUrl,
  )
  if (!context.value.trim()) {
    context.value = 'Screenshot captured from screen/tab/window for analysis.'
  }
}

function openCapture() {
  if (!canCaptureScreen.value) return
  showCaptureModal.value = true
}

function removeAttachment() {
  resetAttachment()
}

function submit() {
  emit('submit', {
    title: title.value,
    context: context.value,
    ...getPayloadExtras(),
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
      <textarea
        v-model="context"
        rows="8"
        class="input-field resize-y"
        placeholder="Describe the requirement, issue, or paste notes..."
      />
    </div>

    <div class="rounded-[16px] border border-black/5 bg-black/[0.02] p-4 dark:border-white/10 dark:bg-white/[0.03]">
      <p class="mb-3 text-xs font-semibold uppercase tracking-wide text-muted-light dark:text-muted-dark">
        Attachments
      </p>
      <div class="flex flex-wrap items-center gap-2">
        <label class="btn-secondary cursor-pointer">
          <input type="file" class="hidden" :accept="accept" :disabled="uploading" @change="onFileChange" />
          {{ uploading ? 'Uploading…' : 'Attach file' }}
        </label>
        <button
          type="button"
          class="btn-secondary"
          :disabled="uploading || !canCaptureScreen"
          :title="canCaptureScreen ? 'Capture tab, window, or screen' : captureSupport.reason"
          @click="openCapture"
        >
          {{ uploading ? 'Uploading…' : '📷 Capture screen' }}
        </button>
        <button
          v-if="fileName"
          type="button"
          class="text-xs font-medium text-red-500 hover:underline"
          @click="removeAttachment"
        >
          Remove
        </button>
      </div>
      <p v-if="!canCaptureScreen" class="mt-2 text-xs text-amber-600 dark:text-amber-400">
        {{ captureSupport.reason }}
      </p>
      <ScreenCaptureInfo v-else class="mt-3" variant="compact" />
      <div v-if="previewUrl || fileName" class="mt-3 flex items-start gap-3">
        <img
          v-if="previewUrl && contentType?.startsWith('image/')"
          :src="previewUrl"
          alt="Attachment preview"
          class="h-20 w-auto max-w-[140px] rounded-lg border border-black/10 object-cover shadow-sm dark:border-white/10"
        />
        <span class="text-xs text-muted-light dark:text-muted-dark">{{ fileName }}</span>
      </div>
    </div>

    <slot name="extra" />
    <div class="flex justify-end">
      <button type="button" class="btn-primary min-w-[140px]" :disabled="uploading" @click="submit">
        <slot name="button">Generate</slot>
      </button>
    </div>

    <ScreenCaptureModal
      :open="showCaptureModal"
      @close="showCaptureModal = false"
      @captured="onScreenCaptured"
    />
  </div>
</template>
