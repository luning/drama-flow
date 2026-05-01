import { defineStore } from 'pinia'
import { ref } from 'vue'
import { login as apiLogin, register as apiRegister, refreshToken } from '@/api/auth'
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

  function logout() {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    user.value = null
    isLoggedIn.value = false
  }

  async function tryRestoreSession() {
    const token = localStorage.getItem('access_token')
    if (token) {
      try {
        const resp = await refreshToken(localStorage.getItem('refresh_token') || '')
        const { access_token, refresh_token: newRefresh, user: userData } = resp.data
        localStorage.setItem('access_token', access_token)
        localStorage.setItem('refresh_token', newRefresh)
        user.value = userData
        isLoggedIn.value = true
      } catch {
        logout()
      }
    }
  }

  return { user, isLoggedIn, login, register, logout, tryRestoreSession }
})
