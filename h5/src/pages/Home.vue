<!--
  DramaFlow 首页.vue — Auto-generated from specs/screens/home.yaml
  DO NOT EDIT MANUALLY. Modify the screen spec instead.
-->
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useHome } from '@/stores/home'
import { fetchfetchContinueWatching } from '@/api/home'
import { fetchfetchBanner } from '@/api/home'
import { fetchfetchCategoryTabs } from '@/api/home'
import { fetchfetchDramaGrid } from '@/api/home'

const router = useRouter()
const store = useHome()
const loading = ref(true)
const continue_watching = ref([])
const banner = ref([])
const category_tabs = ref([])
const drama_grid = ref([])

onMounted(async () => {
  loading.value = true
  try {
    await store.fetchContinueWatching()
    await store.fetchBanner()
    await store.fetchCategoryTabs()
    await store.fetchDramaGrid()
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="page home-page">
    <header class="app-bar">
      <h1>{{ title }}</h1>
    </header>
    <ContinueWatchingCard :items="store.continueWatching" />
    <BannerCarousel :items="store.banners" />
    <CategoryTabs v-model="activeCategory" :items="store.categories" />
    <div class="drama-grid">
      <div class="drama-card" v-for="item in store.dramas" :key="item.id"
           @click="router.push('/detail/' + item.id)">
        <div class="thumb"><span class="badge">{{ item.tag }}</span></div>
        <div class="info">
          <h4>{{ item.title }}</h4>
          <div class="rating">★ {{ item.rating }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg-primary);
}
</style>
