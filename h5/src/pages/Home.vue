<!--
  DramaFlow 首页.vue — Scaffold generated from specs/screens/home.yaml
  Edit this file to implement the page. The screen spec defines the structure.
-->
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
// Import stores and APIs as needed:

const router = useRouter()
const loading = ref(true)
const title = ref('')
const continueWatching = ref([] as any[])
const banners = ref([] as any[])
const activeCategory = ref('')
const categories = ref([] as any[])
const items = ref([] as any[])
// Data sources defined in screen spec:
// /api/watch-records/continue-watching, /api/banners, /api/categories, /api/dramas?category={category-tabs.active}

onMounted(async () => {
  loading.value = true
  try {
    // TODO: Fetch data from: /api/watch-records/continue-watching, /api/banners, /api/categories, /api/dramas?category={category-tabs.active}
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="page home-page">
    <!-- app-bar: app-bar -->
    <header class="app-bar">
      <h1>{{ title }}</h1>
    </header>
    <!-- continue-watching: continue-watching-card -->
    <ContinueWatchingCard :items="continueWatching" />
    <!-- banner: banner-carousel -->
    <BannerCarousel :items="banners" />
    <!-- category-tabs: category-tabs -->
    <CategoryTabs v-model="activeCategory" :items="categories" />
    <!-- drama-grid: drama-grid -->
    <div class="drama-grid">
      <div class="drama-card" v-for="item in items" :key="item.id"
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
