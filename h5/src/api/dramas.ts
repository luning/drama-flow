import client from './client'

export function listDramas(category?: string, page = 1, size = 20) {
  return client.get('/dramas', { params: { category, page, size } })
}

export function getDramaDetail(id: number) {
  return client.get(`/dramas/${id}`)
}

export function getBanners() {
  return client.get('/banners')
}

export function getCategories() {
  return client.get('/categories')
}

export function listEpisodes(dramaId: number) {
  return client.get(`/dramas/${dramaId}/episodes`)
}
