import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authAPI } from '@/api'
import { ElMessage } from 'element-plus'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const accessToken = ref(localStorage.getItem('access_token') || '')
  const refreshToken = ref(localStorage.getItem('refresh_token') || '')
  const twoFactorRequired = ref(false)
  const twoFactorToken = ref('')

  const isLoggedIn = computed(() => !!accessToken.value && !twoFactorRequired.value)
  const isAuthenticated = computed(() => !!accessToken.value)

  async function login(username, password) {
    try {
      const res = await authAPI.login({ username, password })
      
      // 检查是否需要双因素认证
      if (res.two_factor_required) {
        twoFactorRequired.value = true
        twoFactorToken.value = res.two_factor_token
        return { twoFactorRequired: true }
      }
      
      // 正常登录流程
      accessToken.value = res.access
      refreshToken.value = res.refresh
      user.value = res.user
      localStorage.setItem('access_token', res.access)
      localStorage.setItem('refresh_token', res.refresh)
      
      return { success: true }
    } catch (error) {
      throw error
    }
  }

  async function verifyTwoFactor(code) {
    try {
      const res = await authAPI.verifyTwoFactor({
        token: twoFactorToken.value,
        code
      })
      
      accessToken.value = res.access
      refreshToken.value = res.refresh
      user.value = res.user
      twoFactorRequired.value = false
      twoFactorToken.value = ''
      
      localStorage.setItem('access_token', res.access)
      localStorage.setItem('refresh_token', res.refresh)
      
      return { success: true }
    } catch (error) {
      throw error
    }
  }

  async function register(data) {
    try {
      const res = await authAPI.register(data)
      ElMessage.success('注册成功，请登录')
      return res
    } catch (error) {
      throw error
    }
  }

  async function fetchProfile() {
    try {
      const res = await authAPI.profile()
      user.value = res
      return res
    } catch (error) {
      throw error
    }
  }

  async function updateProfile(data) {
    try {
      const res = await authAPI.updateProfile(data)
      user.value = { ...user.value, ...res }
      ElMessage.success('个人信息已更新')
      return res
    } catch (error) {
      throw error
    }
  }

  async function changePassword(oldPassword, newPassword) {
    try {
      await authAPI.changePassword({
        old_password: oldPassword,
        new_password: newPassword
      })
      ElMessage.success('密码修改成功')
    } catch (error) {
      throw error
    }
  }

  async function enableTwoFactor() {
    try {
      const res = await authAPI.enableTwoFactor()
      ElMessage.success('双因素认证已启用')
      return res
    } catch (error) {
      throw error
    }
  }

  async function disableTwoFactor() {
    try {
      const res = await authAPI.disableTwoFactor()
      ElMessage.success('双因素认证已禁用')
      return res
    } catch (error) {
      throw error
    }
  }

  async function refreshAccessToken() {
    try {
      const res = await authAPI.refreshToken()
      accessToken.value = res.access
      localStorage.setItem('access_token', res.access)
      return res.access
    } catch (error) {
      // Token 刷新失败，需要重新登录
      logout()
      throw error
    }
  }

  function logout() {
    user.value = null
    accessToken.value = ''
    refreshToken.value = ''
    twoFactorRequired.value = false
    twoFactorToken.value = ''
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('remember_username')
  }

  return {
    user,
    accessToken,
    refreshToken,
    twoFactorRequired,
    isLoggedIn,
    isAuthenticated,
    login,
    register,
    verifyTwoFactor,
    fetchProfile,
    updateProfile,
    changePassword,
    enableTwoFactor,
    disableTwoFactor,
    refreshAccessToken,
    logout
  }
})
