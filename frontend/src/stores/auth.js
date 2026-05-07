import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authAPI } from '@/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const accessToken = ref(localStorage.getItem('access_token') || '')
  const refreshToken = ref(localStorage.getItem('refresh_token') || '')

  const isLoggedIn = computed(() => !!accessToken.value)

  async function login(username, password) {
    const res = await authAPI.login({ username, password })
    accessToken.value = res.access
    refreshToken.value = res.refresh
    user.value = res.user
    localStorage.setItem('access_token', res.access)
    localStorage.setItem('refresh_token', res.refresh)
  }

  async function fetchProfile() {
    const res = await authAPI.profile()
    user.value = res
  }

  function logout() {
    user.value = null
    accessToken.value = ''
    refreshToken.value = ''
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  return { user, accessToken, refreshToken, isLoggedIn, login, fetchProfile, logout }
})
