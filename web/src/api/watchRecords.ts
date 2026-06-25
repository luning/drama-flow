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

export const watchRecordApi = {
  upsert: (episodeId: number, data: WatchRecordPayload) =>
    client.put<WatchRecord>(`/watch-records/${episodeId}`, data),
  get: (episodeId: number) =>
    client.get<WatchRecord>(`/watch-records/${episodeId}`),
  list: (params?: { page?: number; size?: number }) =>
    client.get<{ items: WatchRecord[]; total: number; page: number; size: number }>(
      '/watch-records', { params }
    ),
  continueWatching: () =>
    client.get<ContinueWatchingItem[]>('/watch-records/continue-watching'),
}
