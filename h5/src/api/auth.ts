import client from './client'

export interface LoginData {
  email: string
  password: string
}

export interface RegisterData {
  nickname: string
  email: string
  password: string
}

export function login(data: LoginData) {
  return client.post('/auth/login', data)
}

export function register(data: RegisterData) {
  return client.post('/auth/register', data)
}

export function logout() {
  return client.post('/auth/logout')
}

export function refreshToken(refreshToken: string) {
  return client.post('/auth/refresh', { refresh_token: refreshToken })
}
