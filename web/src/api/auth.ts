import client from './client'

export interface LoginPayload { email: string; password: string }
export interface RegisterPayload { nickname: string; email: string; password: string }
export interface RefreshPayload { refresh_token: string }

export interface UserResponse { id: number; nickname: string; email: string }
export interface TokenResponse {
  access_token: string
  refresh_token: string
  user: UserResponse
}

export const authApi = {
  login: (data: LoginPayload) =>
    client.post<TokenResponse>('/auth/login', data),
  register: (data: RegisterPayload) =>
    client.post<UserResponse>('/auth/register', data),
  logout: () => client.post('/auth/logout'),
  refresh: (data: RefreshPayload) =>
    client.post<TokenResponse>('/auth/refresh', data),
}
