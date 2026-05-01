import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getDramaDetail, listEpisodes } from '@/api/dramas'

export const useDramaStore = defineStore('drama', () => {
  const detail = ref<any>(null)
  const episodes = ref<any[]>([])
  const loading = ref(false)

  async function fetchDetail(id: number) {
    loading.value = true
    try {
      const [detailResp, epResp] = await Promise.all([
        getDramaDetail(id),
        listEpisodes(id),
      ])
      detail.value = detailResp.data
      episodes.value = epResp.data
    } finally {
      loading.value = false
    }
  }

  return { detail, episodes, loading, fetchDetail }
})
