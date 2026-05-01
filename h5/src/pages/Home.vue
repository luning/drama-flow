<template>
  <div class="page">
    <header class="app-bar">
      <h1 class="brand">DramaFlow</h1>
    </header>

    <div class="continue-watching" v-if="continueList.length > 0">
      <div class="cw-header">
        <span>继续观看</span>
        <a>查看全部 →</a>
      </div>
      <div class="cw-card" v-for="item in continueList" :key="item.episode_id" @click="$router.push(`/detail/${item.drama_id}`)">
        <div class="cw-thumb"></div>
        <div class="cw-info">
          <h4>{{ item.drama_title }}</h4>
          <div class="ep">第 {{ item.episode_number }} 集 · {{ Math.round(item.progress) }}%</div>
          <div class="progress-bar"><div class="fill" :style="{ width: item.progress + '%' }"></div></div>
        </div>
      </div>
    </div>

    <section class="section"><h3>🔥 热门推荐</h3></section>
    <Banner :items="bannerItems" />

    <CategoryTabs :tabs="categoryTabs" :active="store.currentCategory" @change="store.setCategory" />

    <section class="section" style="padding:0 16px;"><h3>为你推荐</h3></section>
    <div class="drama-grid" v-if="!store.loading">
      <DramaCard v-for="d in store.dramas" :key="d.id" :drama="d" />
    </div>
    <div v-else class="loading">加载中...</div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, computed } from 'vue'
import { useHomeStore } from '@/stores/home'
import Banner from '@/components/Banner.vue'
import CategoryTabs from '@/components/CategoryTabs.vue'
import DramaCard from '@/components/DramaCard.vue'

const store = useHomeStore()

const bannerItems = computed(() => [
  { title: '🏆 本周必追', subtitle: '霸道总裁爱上我 · 新更 2 集', color: 'linear-gradient(135deg, #6c5ce7, #2d1b4e)' },
  { title: '🔥 热播榜第一', subtitle: '重生之女王归来 · 12万人在看', color: 'linear-gradient(135deg, #e17055, #2d1b4e)' },
  { title: '✨ 新剧上线', subtitle: '我的房东是财阀 · 首集免费', color: 'linear-gradient(135deg, #00b894, #2d1b4e)' },
])

const categoryTabs = [
  { key: 'all', label: '全部' },
  { key: 'romance', label: '甜宠' },
  { key: 'suspense', label: '悬疑' },
  { key: 'comedy', label: '搞笑' },
  { key: 'fantasy', label: '奇幻' },
  { key: 'president', label: '霸总' },
]

const continueList = computed(() => [])

onMounted(() => {
  store.fetchBanners()
  store.fetchCategories()
  store.fetchDramas()
})
</script>

<style scoped>
.app-bar { display: flex; align-items: center; padding: 12px 16px; }
.brand { font-size: 22px; font-weight: 800; background: linear-gradient(135deg, #6c5ce7, #a29bfe); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.section { margin-top: 12px; }
.section h3 { color: #fff; font-size: 17px; font-weight: 700; }
.continue-watching { padding: 0 16px; margin-top: 8px; }
.cw-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.cw-header span { color: #fff; font-size: 14px; font-weight: 600; }
.cw-header a { color: var(--primary-light); font-size: 12px; }
.cw-card { display: flex; gap: 12px; background: var(--bg-card); border-radius: 14px; padding: 12px; cursor: pointer; border: 1px solid rgba(108,92,231,0.15); margin-bottom: 8px; }
.cw-thumb { width: 80px; aspect-ratio: 3/4; border-radius: 8px; background: linear-gradient(135deg, #2d1b4e, #1a1a3e); flex-shrink: 0; }
.cw-info { flex: 1; }
.cw-info h4 { color: #fff; font-size: 14px; font-weight: 600; }
.cw-info .ep { color: #888; font-size: 12px; margin-top: 2px; }
.progress-bar { height: 4px; background: rgba(255,255,255,0.08); border-radius: 2px; margin-top: 8px; overflow: hidden; }
.progress-bar .fill { height: 100%; background: linear-gradient(90deg, #6c5ce7, #a29bfe); border-radius: 2px; }
.drama-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; padding: 8px 16px 20px; }
.loading { text-align: center; color: #888; padding: 40px; }
</style>
