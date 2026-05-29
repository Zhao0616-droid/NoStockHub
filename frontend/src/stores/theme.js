import { ref, computed, watch } from 'vue'
import { defineStore } from 'pinia'

const STORAGE_KEY = 'theme_settings'

function getStoredTheme() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) {
      const parsed = JSON.parse(raw)
      if (['light', 'dark', 'auto'].includes(parsed.theme)) {
        return parsed.theme
      }
    }
  } catch { /* ignore */ }
  return 'auto'
}

function resolveMode(mode) {
  if (mode === 'auto') {
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
  }
  return mode
}

const AUTH_PATHS = ['/login', '/register', '/two-factor']

function isAuthPage() {
  return AUTH_PATHS.some(p => window.location.pathname.startsWith(p))
}

function applyDark(isDark) {
  // 登录/注册等页面始终亮色
  document.documentElement.classList.toggle('dark', isDark && !isAuthPage())
}

export const useThemeStore = defineStore('theme', () => {
  const mode = ref(getStoredTheme())

  let systemMedia = null

  function apply() {
    const resolved = resolveMode(mode.value)
    applyDark(resolved === 'dark')

    // 自动模式时监听系统主题变化
    if (mode.value === 'auto' && !systemMedia) {
      systemMedia = window.matchMedia('(prefers-color-scheme: dark)')
      systemMedia.addEventListener('change', onSystemChange)
    } else if (mode.value !== 'auto' && systemMedia) {
      systemMedia.removeEventListener('change', onSystemChange)
      systemMedia = null
    }
  }

  function onSystemChange(e) {
    if (mode.value === 'auto') {
      applyDark(e.matches)
    }
  }

  function setTheme(newMode) {
    mode.value = newMode
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ theme: newMode }))
    apply()
  }

  const isDark = computed(() => resolveMode(mode.value) === 'dark')

  // 应用初始化
  apply()
  // 自动模式下持续监听
  watch(mode, () => apply())

  return { mode, setTheme, isDark, apply }
})
