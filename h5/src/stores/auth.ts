import { defineStore } from 'pinia'
import { ref } from 'vue'
import { login as apiLogin, register as apiRegister, logout as apiLogout, refreshToken } from '@/api/auth'
import type { LoginData, RegisterData } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<any>(null)
  const isLoggedIn = ref(false)

  async function login(data: LoginData) {
    const resp = await apiLogin(data)
    const { access_token, refresh_token, user: userData } = resp.data
    localStorage.setItem('access_token', access_token)
    localStorage.setItem('refresh_token', refresh_token)
    user.value = userData
    isLoggedIn.value = true
    return userData
  }

  async function register(data: RegisterData) {
    await apiRegister(data)
  }

  async function logout() {
    try {
      await apiLogout()
    } catch {
      // Ignore API errors — clean up local state regardless
    }
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    user.value = null
    isLoggedIn.value = false
  }

  /**
   * 从 Android JSBridge 同步 Token（EncryptedSharedPreferences → localStorage）。
   * 用户在 Android 原生页面登录后，Token 存在 EncryptedSharedPreferences 中，
   * H5 WebView 无法直接读取，需通过 window.DramaFlowBridge 获取。
   * 返回 true 表示成功从 Android 侧获取到 Token。
   */
  function syncTokenFromNative(): boolean {
    if (typeof window !== 'undefined' && window.DramaFlowBridge) {
      const accessToken = window.DramaFlowBridge.getAccessToken()
      if (accessToken) {
        localStorage.setItem('access_token', accessToken)

        const refreshToken = window.DramaFlowBridge.getRefreshToken() || ''
        if (refreshToken) {
          localStorage.setItem('refresh_token', refreshToken)
        }

        isLoggedIn.value = true
        return true
      }
    }
    return false
  }

  async function tryRestoreSession() {
    const token = localStorage.getItem('access_token')
    if (!token) return
    const storedRefresh = localStorage.getItem('refresh_token')
    if (!storedRefresh) {
      // Trust the existing access token; 401 interceptor will handle expiry
      isLoggedIn.value = true
      return
    }
    try {
      const resp = await refreshToken(storedRefresh)
      const { access_token, refresh_token: newRefresh, user: userData } = resp.data
      localStorage.setItem('access_token', access_token)
      localStorage.setItem('refresh_token', newRefresh)
      user.value = userData
      isLoggedIn.value = true
    } catch {
      await logout()
    }
  }

  return { user, isLoggedIn, login, register, logout, syncTokenFromNative, tryRestoreSession }
})
