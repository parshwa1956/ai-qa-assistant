import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export type ThemeMode = 'light' | 'dark' | 'system'

const STORAGE_KEY = 'kaldi-theme'

function systemPrefersDark() {
  return window.matchMedia('(prefers-color-scheme: dark)').matches
}

function applyTheme(mode: ThemeMode) {
  const dark = mode === 'dark' || (mode === 'system' && systemPrefersDark())
  document.documentElement.classList.toggle('dark', dark)
}

export const useThemeStore = defineStore('theme', () => {
  const mode = ref<ThemeMode>((localStorage.getItem(STORAGE_KEY) as ThemeMode) || 'system')

  applyTheme(mode.value)

  watch(mode, (v) => {
    localStorage.setItem(STORAGE_KEY, v)
    applyTheme(v)
  })

  const media = window.matchMedia('(prefers-color-scheme: dark)')
  media.addEventListener('change', () => {
    if (mode.value === 'system') applyTheme('system')
  })

  function setMode(m: ThemeMode) {
    mode.value = m
  }

  function toggle() {
    const isDark = document.documentElement.classList.contains('dark')
    setMode(isDark ? 'light' : 'dark')
  }

  return { mode, setMode, toggle }
})
