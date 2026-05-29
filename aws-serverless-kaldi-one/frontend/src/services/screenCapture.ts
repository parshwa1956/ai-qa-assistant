/** Screen capture via Display Media API (Chrome, Edge, Firefox, Safari 15+ on macOS/Windows). */

export type DisplayCaptureSupport = {
  supported: boolean
  reason?: string
}

export function getDisplayCaptureSupport(): DisplayCaptureSupport {
  if (typeof window === 'undefined') {
    return { supported: false, reason: 'Not in browser' }
  }
  if (!window.isSecureContext) {
    return { supported: false, reason: 'Screen capture requires HTTPS (or localhost).' }
  }
  if (!navigator.mediaDevices?.getDisplayMedia) {
    return {
      supported: false,
      reason: 'Your browser does not support screen capture. Try Chrome, Edge, Firefox, or Safari 15+.',
    }
  }
  return { supported: true }
}

export type CaptureResult = {
  blob: Blob
  filename: string
  contentType: string
  previewUrl: string
  width: number
  height: number
}

function stopStream(stream: MediaStream | null) {
  stream?.getTracks().forEach((t) => t.stop())
}

/**
 * Opens the OS/browser picker to share a tab, window, or entire screen.
 * Returns a live MediaStream — caller must stop tracks when done.
 */
export async function requestDisplayStream(): Promise<MediaStream> {
  const check = getDisplayCaptureSupport()
  if (!check.supported) {
    throw new Error(check.reason || 'Screen capture not supported')
  }

  return navigator.mediaDevices.getDisplayMedia({
    video: true,
    audio: false,
  })
}

/**
 * Grab a single PNG frame from an active display stream.
 */
export async function captureFrameFromStream(stream: MediaStream): Promise<CaptureResult> {
  const video = document.createElement('video')
  video.muted = true
  video.playsInline = true
  video.srcObject = stream

  await new Promise<void>((resolve, reject) => {
    video.onloadedmetadata = () => resolve()
    video.onerror = () => reject(new Error('Could not load screen preview'))
    video.play().catch(reject)
  })

  const width = video.videoWidth
  const height = video.videoHeight
  if (!width || !height) {
    throw new Error('Invalid capture dimensions')
  }

  const canvas = document.createElement('canvas')
  canvas.width = width
  canvas.height = height
  const ctx = canvas.getContext('2d')
  if (!ctx) throw new Error('Canvas not available')
  ctx.drawImage(video, 0, 0, width, height)

  const blob = await new Promise<Blob>((resolve, reject) => {
    canvas.toBlob(
      (b) => (b ? resolve(b) : reject(new Error('Failed to encode screenshot'))),
      'image/png',
      0.92,
    )
  })

  const ts = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19)
  const filename = `screenshot-${ts}.png`
  const previewUrl = URL.createObjectURL(blob)

  return {
    blob,
    filename,
    contentType: 'image/png',
    previewUrl,
    width,
    height,
  }
}

export function revokePreviewUrl(url: string | undefined) {
  if (url?.startsWith('blob:')) {
    URL.revokeObjectURL(url)
  }
}

export function userFriendlyCaptureError(err: unknown): string {
  const name = (err as { name?: string })?.name
  const msg = (err as Error)?.message || ''
  if (name === 'NotAllowedError' || /permission/i.test(msg)) {
    return 'Screen capture was cancelled or permission denied.'
  }
  if (name === 'NotFoundError') {
    return 'No screen or window was selected.'
  }
  if (name === 'NotSupportedError' || name === 'NotReadableError') {
    return 'Screen capture is not available in this browser or context.'
  }
  if (name === 'AbortError') {
    return 'Screen capture was cancelled.'
  }
  return msg || 'Screen capture failed'
}
