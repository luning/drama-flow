import { defineStore } from 'pinia'
import { ref } from 'vue'
import { dramaApi, type DramaListItem, type DramaDetail } from '@/api/dramas'

export const useDramaStore = defineStore('drama', () => {
  const dramas = ref<DramaListItem[]>([])
  const currentDrama = ref<DramaDetail | null>(null)
  const loading = ref(false)
  const page = ref(1)
  const hasMore = ref(true)

  async function loadDramas(reset = false) {
    if (loading.value || (!hasMore.value && !reset)) return
    if (reset) { dramas.value = []; page.value = 1; hasMore.value = true }
    loading.value = true
    try {
      const { data } = await dramaApi.list({ page: page.value, size: 20 })
      dramas.value.push(...data.items)
      hasMore.value = dramas.value.length < data.total
      page.value++
    } finally {
      loading.value = false
    }
  }

  async function loadDrama(id: number) {
    const { data } = await dramaApi.detail(id)
    currentDrama.value = data
    return data
  }

  return { dramas, currentDrama, loading, hasMore, loadDramas, loadDrama }
})
