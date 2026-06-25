import axios from 'axios'

const client = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

client.interceptors.request.use((config) => {
  const token =
    localStorage.getItem('access_token') ||
    sessionStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

let isRefreshing = false
let waitQueue: Array<(token: string) => void> = []

client.interceptors.response.use(
  (res) => res,
  async (err) => {
    const original = err.config
    // /auth/ 端点的 401（如登录失败）不触发 token 刷新，直接透传
    if (err.response?.status !== 401 || original._retry || original.url?.startsWith('/auth/')) {
      return Promise.reject(err)
    }
    original._retry = true

    if (isRefreshing) {
      return new Promise((resolve) => {
        waitQueue.push((token) => {
          original.headers.Authorization = `Bearer ${token}`
          resolve(client(original))
        })
      })
    }

    isRefreshing = true
    const { useAuthStore } = await import('@/stores/auth')
    const authStore = useAuthStore()
    const newToken = await authStore.refreshAccessToken()
    isRefreshing = false

    if (newToken) {
      waitQueue.forEach((cb) => cb(newToken))
      waitQueue = []
      original.headers.Authorization = `Bearer ${newToken}`
      return client(original)
    } else {
      waitQueue = []
      const { useRouter } = await import('vue-router')
      useRouter().push('/login')
      return Promise.reject(err)
    }
  }
)

export default client
