<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useHomeStore } from '@/stores/home'
import BannerCarousel from '@/components/BannerCarousel.vue'
import CategoryTabs from '@/components/CategoryTabs.vue'
import DramaCard from '@/components/DramaCard.vue'
import ContinueWatching from '@/components/ContinueWatching.vue'

const store = useHomeStore()

const tabs = computed(() => [
  { key: 'all', label: '全部' },
  ...store.categories.map((c: any) => ({ key: c.slug, label: c.name })),
])

onMounted(async () => {
  await Promise.all([
    store.fetchBanners(),
    store.fetchCategories(),
    store.fetchDramas(),
    store.fetchContinueWatching(),
  ])
})
</script>

<template>
  <div class="home-page">
    <header class="app-bar">
      <span class="logo">DramaFlow</span>
    </header>

    <BannerCarousel :items="store.banners" />

    <ContinueWatching :items="store.continueWatchingList" />

    <CategoryTabs
      :tabs="tabs"
      :active="store.currentCategory"
      @change="store.setCategory"
    />

    <div v-if="store.loading" class="skeleton-grid">
      <div v-for="i in 6" :key="i" class="skeleton-card" />
    </div>
    <div v-else-if="store.dramas.length === 0" class="empty">暂无剧集</div>
    <div v-else class="drama-grid">
      <DramaCard v-for="drama in store.dramas" :key="drama.id" :drama="drama" />
    </div>
  </div>
</template>

<style scoped>
.home-page {
  min-height: 100vh;
  background: var(--bg-primary);
  padding-bottom: 24px;
}

.app-bar {
  display: flex;
  align-items: center;
  padding: 16px 16px 8px;
}

.logo {
  color: var(--color-primary);
  font-size: 20px;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.drama-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  padding: 8px 16px 0;
}

.skeleton-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  padding: 8px 16px 0;
}

.skeleton-card {
  aspect-ratio: 3/4;
  border-radius: 14px;
  background: linear-gradient(90deg, #1a1a2e 25%, #252540 50%, #1a1a2e 75%);
  background-size: 200% 100%;
  animation: shimmer 1.4s infinite;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.empty {
  text-align: center;
  color: #555;
  padding: 48px 0;
  font-size: 14px;
}
</style>
