import { defineStore } from 'pinia'
import { ref } from 'vue'
import { watchRecordApi, type WatchRecord, type ContinueWatchingItem } from '@/api/watchRecords'

export const useWatchRecordStore = defineStore('watchRecord', () => {
  const records = ref<Record<number, WatchRecord>>({})
  const history = ref<ContinueWatchingItem[]>([])

  async function fetchRecord(episodeId: number): Promise<WatchRecord> {
    const { data } = await watchRecordApi.get(episodeId)
    records.value[episodeId] = data
    return data
  }

  async function fetchForEpisodes(episodeIds: number[]) {
    await Promise.all(episodeIds.map(fetchRecord))
  }

  function cachedRecord(episodeId: number): WatchRecord | undefined {
    return records.value[episodeId]
  }

  async function saveProgress(episodeId: number, lastPosition: number, duration: number, completed = false) {
    const progress = duration > 0 ? Math.min(100, (lastPosition / duration) * 100) : 0
    const { data } = await watchRecordApi.upsert(episodeId, { progress, last_position: lastPosition, completed })
    records.value[episodeId] = data
  }

  async function fetchHistory() {
    const { data } = await watchRecordApi.continueWatching()
    history.value = data
  }

  return { records, history, fetchRecord, fetchForEpisodes, cachedRecord, saveProgress, fetchHistory }
})
