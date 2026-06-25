import client from './client'

export interface Episode {
  id: number; drama_id: number; episode_number: number
  title: string; duration: string; video_url: string; cover_url: string
}
export interface VideoUrlResponse { url: string; expires_at: number }

export const episodeApi = {
  list: (dramaId: number) =>
    client.get<Episode[]>(`/dramas/${dramaId}/episodes`),
  detail: (episodeId: number) =>
    client.get<Episode>(`/episodes/${episodeId}`),
  videoUrl: (episodeId: number) =>
    client.get<VideoUrlResponse>(`/episodes/${episodeId}/video-url`),
}
