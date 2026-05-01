import { defineStore } from 'pinia'
import { ref } from 'vue'
import { listDramas, getBanners, getCategories } from '@/api/dramas'

export const useHomeStore = defineStore('home', () => {
  const banners = ref<any[]>([])
  const categories = ref<any[]>([])
  const dramas = ref<any[]>([])
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

  function setCategory(cat: string) {
    currentCategory.value = cat
    fetchDramas(cat)
  }

  return { banners, categories, dramas, currentCategory, loading, fetchBanners, fetchCategories, fetchDramas, setCategory }
})
