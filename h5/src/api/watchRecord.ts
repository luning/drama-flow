import client from './client'

export interface WatchRecordPayload {
  progress: number      // 0-100
  last_position: number // seconds
  completed?: boolean
}
export interface WatchRecord {
  id: number; user_id: number; episode_id: number
  progress: number; last_position: number; completed: boolean; updated_at: string
}
export interface ContinueWatchingItem {
  drama_id: number; drama_title: string; drama_cover: string
  episode_id: number; episode_number: number; episode_title: string
  progress: number; last_position: number; updated_at: string
}

// 函数式 API（现有，保留）
export function upsertRecord(episodeId: number, data: WatchRecordPayload) {
  return client.put<WatchRecord>(`/watch-records/${episodeId}`, data)
}
export function getRecord(episodeId: number) {
  return client.get<WatchRecord>(`/watch-records/${episodeId}`)
}
export function listRecords(page = 1, size = 20) {
  return client.get('/watch-records', { params: { page, size } })
}
export function continueWatching() {
  return client.get<ContinueWatchingItem[]>('/watch-records/continue-watching')
}

// 对象式 API（stores 使用）
export const watchRecordApi = {
  upsert: (episodeId: number, data: WatchRecordPayload) =>
    client.put<WatchRecord>(`/watch-records/${episodeId}`, data),
  get: (episodeId: number) =>
    client.get<WatchRecord>(`/watch-records/${episodeId}`),
  continueWatching: () =>
    client.get<ContinueWatchingItem[]>('/watch-records/continue-watching'),
}
