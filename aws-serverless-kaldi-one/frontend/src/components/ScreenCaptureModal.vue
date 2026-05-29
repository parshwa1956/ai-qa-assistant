<script setup lang="ts">
import { onUnmounted, ref, watch } from 'vue'
import {
  captureFrameFromStream,
  requestDisplayStream,
  revokePreviewUrl,
  userFriendlyCaptureError,
} from '@/services/screenCapture'
import { useToastStore } from '@/stores/toast'
import ScreenCaptureInfo from './ScreenCaptureInfo.vue'

const props = defineProps<{
  open: boolean
}>()

const emit = defineEmits<{
  close: []
  captured: [result: { blob: Blob; filename: string; contentType: string; previewUrl: string }]
}>()

const toast = useToastStore()
const stream = ref<MediaStream | null>(null)
const videoRef = ref<HTMLVideoElement | null>(null)
const starting = ref(false)
const capturing = ref(false)
const statusText = ref('Choose a browser tab, window, or your full screen to share.')

async function startCapture() {
  starting.value = true
  statusText.value = 'Waiting for you to pick a tab, window, or screen…'
  try {
    stopStream()
    const media = await requestDisplayStream()
    stream.value = media
    statusText.value = 'Preview active — navigate to what you want, then click Capture screenshot.'

    media.getVideoTracks()[0]?.addEventListener('ended', () => {
      statusText.value = 'Sharing stopped. Start again to capture another screenshot.'
      stopStream()
    })
  } catch (err) {
    toast.push(userFriendlyCaptureError(err), 'error')
    emit('close')
  } finally {
    starting.value = false
  }
}

watch(
  () => props.open,
  async (isOpen) => {
    if (isOpen) {
      await startCapture()
    } else {
      stopStream()
    }
  },
)

watch(stream, async (s) => {
  const el = videoRef.value
  if (!el) return
  if (s) {
    el.srcObject = s
    await el.play().catch(() => undefined)
  } else {
    el.srcObject = null
  }
})

function stopStream() {
  stream.value?.getTracks().forEach((t) => t.stop())
  stream.value = null
  if (videoRef.value) videoRef.value.srcObject = null
}

async function captureNow() {
  if (!stream.value) {
    toast.push('Start screen share first', 'error')
    return
  }
  capturing.value = true
  try {
    const result = await captureFrameFromStream(stream.value)
    stopStream()
    emit('captured', {
      blob: result.blob,
      filename: result.filename,
      contentType: result.contentType,
      previewUrl: result.previewUrl,
    })
    emit('close')
  } catch (err) {
    toast.push(userFriendlyCaptureError(err), 'error')
  } finally {
    capturing.value = false
  }
}

function cancel() {
  stopStream()
  emit('close')
}

onUnmounted(() => {
  stopStream()
})
</script>

<template>
  <Teleport to="body">
    <div
      v-if="open"
      class="fixed inset-0 z-[110] flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm"
      role="dialog"
      aria-modal="true"
      aria-labelledby="screen-capture-title"
    >
      <div class="guide-sheet flex max-h-[90vh] w-full max-w-2xl flex-col overflow-hidden">
        <div class="flex items-start justify-between gap-4">
          <div>
            <h2 id="screen-capture-title" class="text-xl font-bold">Capture screenshot</h2>
            <p class="mt-1 text-sm text-muted-light dark:text-muted-dark">
              {{ statusText }}
            </p>
          </div>
          <button type="button" class="btn-secondary !px-3 !py-1.5 text-xs" aria-label="Close" @click="cancel">✕</button>
        </div>

        <div
          class="relative mt-4 flex min-h-[200px] flex-1 items-center justify-center overflow-hidden rounded-[16px] border border-black/10 bg-black/90 dark:border-white/10"
        >
          <video
            v-show="stream"
            ref="videoRef"
            class="max-h-[50vh] w-full object-contain"
            muted
            playsinline
            autoplay
          />
          <div v-if="!stream && !starting" class="p-8 text-center text-sm text-white/70">
            <p>Works on <strong>Windows</strong> and <strong>macOS</strong> in Chrome, Edge, Firefox, and Safari.</p>
            <p class="mt-2">You can capture another browser tab, an app window, or the entire screen.</p>
          </div>
          <div v-if="starting" class="absolute inset-0 flex items-center justify-center bg-black/40">
            <span class="text-sm text-white">Opening picker…</span>
          </div>
        </div>

        <ol class="mt-4 list-decimal space-y-1 pl-4 text-xs text-muted-light dark:text-muted-dark">
          <li>Pick <strong>Chrome Tab</strong>, <strong>Window</strong>, or <strong>Entire Screen</strong> in the system dialog.</li>
          <li>Show the UI you want in the preview (switch tabs or apps if needed).</li>
          <li>Click <strong>Capture screenshot</strong> — the image is uploaded securely for AI analysis.</li>
        </ol>

        <ScreenCaptureInfo class="mt-4" variant="full" />

        <div class="mt-5 flex flex-wrap gap-3">
          <button type="button" class="btn-secondary" :disabled="capturing" @click="cancel">Cancel</button>
          <button
            v-if="!stream"
            type="button"
            class="btn-secondary"
            :disabled="starting"
            @click="startCapture"
          >
            {{ starting ? 'Starting…' : 'Choose screen again' }}
          </button>
          <button
            type="button"
            class="btn-primary ml-auto"
            :disabled="!stream || capturing"
            @click="captureNow"
          >
            {{ capturing ? 'Capturing…' : 'Capture screenshot' }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>
