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
export interface Banner {
  drama_id: number; title: string; image_url: string; sort_order: number
}

// 函数式 API（现有，保留）
export function listDramas(category?: string, page = 1, size = 20) {
  return client.get<PaginatedDramas>('/dramas', { params: { category, page, size } })
}
export function getDramaDetail(id: number) {
  return client.get<DramaDetail>(`/dramas/${id}`)
}
export function getBanners() {
  return client.get<Banner[]>('/banners')
}
export function getCategories() {
  return client.get<{ id: number; name: string; slug: string }[]>('/categories')
}
export function listEpisodes(dramaId: number) {
  return client.get(`/dramas/${dramaId}/episodes`)
}

// 对象式 API（BannerCarousel 等新组件使用）
export const dramaApi = {
  banners: () => client.get<Banner[]>('/banners'),
}
