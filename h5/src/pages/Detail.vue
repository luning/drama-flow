<template>
  <div class="page">
    <div class="detail-header" :style="coverBg">
      <div class="gradient"></div>
      <button class="back-btn" @click="goBack">‹</button>
    </div>

    <!-- Loading skeleton -->
    <div v-if="store.loading" class="skeleton">
      <div class="skeleton-title" />
      <div class="skeleton-line w-60" />
      <div class="skeleton-line w-40" />
      <div class="skeleton-desc" />
      <div class="skeleton-desc-short" />
      <div class="skeleton-episodes">
        <div v-for="n in 5" :key="n" class="skeleton-episode" />
      </div>
    </div>

    <!-- Error: not found -->
    <div v-else-if="store.error === 'NOT_FOUND'" class="error-view">
      <p class="error-icon">📭</p>
      <p class="error-text">剧集不存在</p>
      <button class="btn btn-primary" @click="goBack">返回首页</button>
    </div>

    <!-- Error: network -->
    <div v-else-if="store.error === 'NETWORK_ERROR'" class="error-view">
      <p class="error-icon">⚠️</p>
      <p class="error-text">网络加载失败</p>
      <button class="btn btn-primary" @click="retry">重试</button>
    </div>

    <!-- Content -->
    <template v-else-if="store.detail">
      <div class="body">
        <h1>{{ store.detail.title }}</h1>
        <div class="sub-info">
          <span>{{ store.detail.year }} · 共{{ store.detail.episode_count }}集</span>
        </div>
        <div class="rating-row">
          <span class="stars">★★★★★</span>
          <span class="score">{{ store.detail.rating }}</span>
        </div>
        <div class="desc">{{ store.detail.description }}</div>
        <div class="actions">
          <button class="btn btn-primary" @click="playFirst">▶ 立即观看</button>
        </div>
      </div>
      <div class="episode-header">
        <span class="active">剧集列表</span>
      </div>
      <EpisodeList :episodes="store.episodes" @play="playEpisode" />
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useDramaStore } from '@/stores/drama'
import EpisodeList from '@/components/EpisodeList.vue'

const route = useRoute()
const router = useRouter()
const store = useDramaStore()

const coverBg = computed(() => {
  const url = store.detail?.cover_url
  return url ? { backgroundImage: `url(${url})`, backgroundSize: 'cover', backgroundPosition: 'center' } : {}
})

function playFirst() {
  if (store.episodes.length > 0) {
    playEpisode(store.episodes[0])
  }
}

function playEpisode(ep: { id: number; episode_number: number; video_url: string; title: string }) {
  window.DramaFlowBridge?.playVideo(ep.id, ep.video_url, ep.title, store.detail?.id ?? 0, ep.episode_number)
}

function goBack() {
  router.push('/')
}

function retry() {
  const id = Number(route.params.id)
  if (id) store.fetchDetail(id)
}

onMounted(() => {
  const id = Number(route.params.id)
  if (id) store.fetchDetail(id)
})
</script>

<style scoped>
.detail-header { width: 100%; aspect-ratio: 16/9; background: linear-gradient(135deg, var(--primary), #2d1b4e); position: relative; }
.gradient { position: absolute; inset: 0; background: linear-gradient(transparent 40%, var(--bg)); }
.back-btn { position: absolute; top: 12px; left: 12px; width: 36px; height: 36px; border-radius: 50%; border: none; background: rgba(0,0,0,0.4); color: var(--text); font-size: 20px; cursor: pointer; z-index: 2; }
.body { padding: 16px; }
.body h1 { color: var(--text); font-size: 20px; font-weight: 700; }
.sub-info { display: flex; gap: 12px; margin-top: 6px; color: var(--text-secondary); font-size: 13px; }
.rating-row { display: flex; align-items: center; gap: 8px; margin-top: 10px; }
.stars { color: var(--rating); font-size: 16px; }
.score { color: var(--rating); font-size: 18px; font-weight: 700; }
.desc { color: var(--text-secondary); font-size: 14px; line-height: 1.7; margin-top: 14px; }
.actions { margin-top: 16px; }
.btn { display: inline-flex; align-items: center; justify-content: center; padding: 12px 24px; border-radius: 12px; border: none; font-size: 15px; font-weight: 600; cursor: pointer; }
.btn-primary { background: linear-gradient(135deg, var(--primary), var(--primary-light)); color: var(--text); }
.episode-header { display: flex; border-bottom: 1px solid var(--border); padding: 0 16px; }
.episode-header span { padding: 10px 0; color: var(--primary); font-size: 14px; font-weight: 500; border-bottom: 2px solid var(--primary); }

/* Skeleton */
.skeleton { padding: 16px; }
.skeleton-title { height: 22px; width: 70%; background: rgba(255,255,255,0.06); border-radius: 6px; margin-bottom: 10px; }
.skeleton-line { height: 14px; background: rgba(255,255,255,0.04); border-radius: 4px; margin-bottom: 8px; }
.skeleton-line.w-60 { width: 60%; }
.skeleton-line.w-40 { width: 40%; }
.skeleton-desc { height: 14px; background: rgba(255,255,255,0.04); border-radius: 4px; margin-top: 18px; margin-bottom: 6px; }
.skeleton-desc-short { height: 14px; width: 55%; background: rgba(255,255,255,0.04); border-radius: 4px; margin-bottom: 18px; }
.skeleton-episodes { margin-top: 20px; }
.skeleton-episode { height: 48px; background: rgba(255,255,255,0.03); border-radius: 8px; margin-bottom: 8px; }

/* Error */
.error-view { display: flex; flex-direction: column; align-items: center; padding: 80px 16px; }
.error-icon { font-size: 48px; margin-bottom: 12px; }
.error-text { color: var(--text-secondary); font-size: 16px; margin-bottom: 20px; }
</style>
