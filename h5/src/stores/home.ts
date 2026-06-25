import { defineStore } from 'pinia'
import { ref } from 'vue'
import { listDramas, getBanners, getCategories } from '@/api/dramas'
import { continueWatching } from '@/api/watchRecord'

export const useHomeStore = defineStore('home', () => {
  const banners = ref<any[]>([])
  const categories = ref<any[]>([])
  const dramas = ref<any[]>([])
  const continueWatchingList = ref<any[]>([])
  const currentCategory = ref('all')
  const loading = ref(false)

  async function fetchBanners() {
    const resp = await getBanners()
    banners.value = resp.data
  }

  async function fetchCategories() {
    const resp = await getCategories()
    categories.value = resp.data
  }

  async function fetchDramas(category = 'all', page = 1) {
    loading.value = true
    try {
      const resp = await listDramas(category, page)
      dramas.value = resp.data.items
    } finally {
      loading.value = false
    }
  }

  async function fetchContinueWatching() {
    try {
      const resp = await continueWatching()
      continueWatchingList.value = resp.data
    } catch {
      continueWatchingList.value = []
    }
  }

  function setCategory(cat: string) {
    currentCategory.value = cat
    fetchDramas(cat)
  }

  return {
    banners, categories, dramas, continueWatchingList, currentCategory, loading,
    fetchBanners, fetchCategories, fetchDramas, fetchContinueWatching, setCategory,
  }
})
