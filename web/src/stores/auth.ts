import { defineStore } from 'pinia'
import { ref } from 'vue'
import { authApi, type UserResponse } from '@/api/auth'

function getStorage(key: string): string | null {
  return localStorage.getItem(key) ?? sessionStorage.getItem(key)
}

function setStorage(key: string, value: string, persistent: boolean) {
  if (persistent) localStorage.setItem(key, value)
  else sessionStorage.setItem(key, value)
}

function clearStorage() {
  ;['access_token', 'refresh_token', 'remember_me'].forEach((k) => {
    localStorage.removeItem(k)
    sessionStorage.removeItem(k)
  })
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<UserResponse | null>(null)
  const isLoggedIn = ref(false)

  async function login(email: string, password: string, rememberMe: boolean) {
    const { data } = await authApi.login({ email, password })
    const persistent = rememberMe
    setStorage('access_token', data.access_token, persistent)
    setStorage('refresh_token', data.refresh_token, persistent)
    if (persistent) localStorage.setItem('remember_me', '1')
    user.value = data.user
    isLoggedIn.value = true
  }

  async function logout() {
    try { await authApi.logout() } catch { /* ignore */ }
    clearStorage()
    user.value = null
    isLoggedIn.value = false
  }

  async function refreshAccessToken(): Promise<string | null> {
    const refreshToken = getStorage('refresh_token')
    if (!refreshToken) return null
    try {
      const persistent = !!localStorage.getItem('remember_me')
      const { data } = await authApi.refresh({ refresh_token: refreshToken })
      setStorage('access_token', data.access_token, persistent)
      setStorage('refresh_token', data.refresh_token, persistent)
      user.value = data.user
      isLoggedIn.value = true
      return data.access_token
    } catch {
      clearStorage()
      user.value = null
      isLoggedIn.value = false
      return null
    }
  }

  async function initFromStorage() {
    const accessToken = getStorage('access_token')
    if (!accessToken) return
    // 先标记为已登录，让页面正常渲染；
    // 刷新失败时不清除 token（access token 可能仍有效），
    // 真正过期时由 401 拦截器统一处理。
    isLoggedIn.value = true
    const refreshToken = getStorage('refresh_token')
    if (!refreshToken) return
    try {
      const persistent = !!localStorage.getItem('remember_me')
      const { data } = await authApi.refresh({ refresh_token: refreshToken })
      setStorage('access_token', data.access_token, persistent)
      setStorage('refresh_token', data.refresh_token, persistent)
      user.value = data.user
    } catch {
      // 静默忽略；access token 可能仍有效，401 拦截器会在需要时再次尝试
    }
  }

  return { user, isLoggedIn, login, logout, refreshAccessToken, initFromStorage }
})
