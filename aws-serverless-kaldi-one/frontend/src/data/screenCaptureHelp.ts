/** User-facing help copy for browser screen capture (Display Media API). */

export const SCREEN_CAPTURE_INFO = {
  title: 'How screen capture works',
  summary:
    'Kaldi One uses your browser’s built-in screen sharing — the same safe technology used by Google Meet, Zoom, and Teams when you share your screen.',
  points: [
    {
      heading: 'You stay in control',
      text: 'Your browser will ask what to share: a specific tab, an app window, or your full screen. Kaldi One only sees what you choose. You can cancel anytime.',
    },
    {
      heading: 'Browser-based (not a desktop recorder)',
      text: 'Capture runs inside Chrome, Edge, Firefox, or Safari. No extra app is installed. This works on Windows and macOS when you use Kaldi One over HTTPS.',
    },
    {
      heading: 'Permission is required each time',
      text: 'For your privacy, the browser never allows silent screenshots. You must approve sharing in the system dialog before each capture — Kaldi One cannot access your screen without that consent.',
    },
    {
      heading: 'Best for QA bug reports',
      text: 'Capture a UI defect from another tab or app, then generate a Bug Report with AI vision analysis on the screenshot.',
    },
  ],
  shortHint:
    'Uses browser screen share (like Meet/Zoom). You pick the tab, window, or screen — nothing is captured without your permission.',
} as const
