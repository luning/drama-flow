import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getDramaDetail, listEpisodes } from '@/api/dramas'
import type { AxiosError } from 'axios'

export const useDramaStore = defineStore('drama', () => {
  const detail = ref<any>(null)
  const episodes = ref<any[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchDetail(id: number) {
    loading.value = true
    error.value = null
    try {
      const [detailResp, epResp] = await Promise.all([
        getDramaDetail(id),
        listEpisodes(id),
      ])
      detail.value = detailResp.data
      episodes.value = epResp.data
    } catch (e: any) {
      const axiosErr = e as AxiosError
      if (axiosErr.response?.status === 404) {
        error.value = 'NOT_FOUND'
      } else {
        error.value = 'NETWORK_ERROR'
      }
      detail.value = null
      episodes.value = []
    } finally {
      loading.value = false
    }
  }

  return { detail, episodes, loading, error, fetchDetail }
})
