import axios from 'axios'

const client = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
})

client.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

let isRefreshing = false
let waitingQueue: Array<(token: string) => void> = []

function clearAuthAndRedirect() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  waitingQueue = []
  window.location.href = '/#/login'
}

client.interceptors.response.use(
  (resp) => resp,
  async (error) => {
    const original = error.config
    if (error.response?.status !== 401 || original._retry) {
      return Promise.reject(error)
    }

    const storedRefresh = localStorage.getItem('refresh_token')
    if (!storedRefresh) {
      clearAuthAndRedirect()
      return Promise.reject(error)
    }

    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        waitingQueue.push((token) => {
          original.headers.Authorization = `Bearer ${token}`
          resolve(client(original))
        })
        // Add rejection handler in case refresh fails while queued
        setTimeout(() => reject(error), 10000)
      })
    }

    original._retry = true
    isRefreshing = true
    try {
      // Use raw axios to avoid interceptor loop; baseURL not inherited
      const resp = await axios.post('/api/auth/refresh', { refresh_token: storedRefresh })
      const { access_token, refresh_token: newRefresh } = resp.data
      localStorage.setItem('access_token', access_token)
      localStorage.setItem('refresh_token', newRefresh)
      waitingQueue.forEach((cb) => cb(access_token))
      waitingQueue = []
      original.headers.Authorization = `Bearer ${access_token}`
      return client(original)
    } catch {
      clearAuthAndRedirect()
      return Promise.reject(error)
    } finally {
      isRefreshing = false
    }
  },
)

export default client
