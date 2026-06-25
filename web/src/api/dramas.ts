import client from './client'

export interface DramaListItem {
  id: number; title: string; category_id: number; rating: number
  cover_url: string; year: number | null; status: string; episode_count: number
}
export interface DramaDetail extends DramaListItem {
  description: string; category_name: string; created_at: string
}
export interface PaginatedDramas {
  items: DramaListItem[]; total: number; page: number; size: number
}

export const dramaApi = {
  list: (params?: { category?: string; page?: number; size?: number }) =>
    client.get<PaginatedDramas>('/dramas', { params }),
  detail: (id: number) => client.get<DramaDetail>(`/dramas/${id}`),
  categories: () => client.get<{ id: number; name: string; slug: string }[]>('/categories'),
}
