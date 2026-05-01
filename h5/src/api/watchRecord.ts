import client from './client'

export function upsertRecord(episodeId: number, data: {
  progress: number
  last_position: number
  completed: boolean
}) {
  return client.put(`/watch-records/${episodeId}`, data)
}

export function getRecord(episodeId: number) {
  return client.get(`/watch-records/${episodeId}`)
}

export function listRecords(page = 1, size = 20) {
  return client.get('/watch-records', { params: { page, size } })
}

export function continueWatching() {
  return client.get('/watch-records/continue-watching')
}
