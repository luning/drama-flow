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
    console.log(`[client.ts] ${config.method?.toUpperCase()} ${config.url} → Bearer ${token.slice(0, 10)}...`)
  } else {
    console.log(`[client.ts] ${config.method?.toUpperCase()} ${config.url} → NO TOKEN`)
  }
  return config
})

client.interceptors.response.use(
  (resp) => resp,
  async (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  },
)

export default client
