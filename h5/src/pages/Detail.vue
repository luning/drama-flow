<template>
  <div class="page">
    <div class="detail-header">
      <div class="gradient"></div>
      <button class="back-btn" @click="$router.push('/')">‹</button>
    </div>
    <div class="body" v-if="store.detail">
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
    <EpisodeList :episodes="store.episodes" />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useDramaStore } from '@/stores/drama'
import EpisodeList from '@/components/EpisodeList.vue'

const route = useRoute()
const router = useRouter()
const store = useDramaStore()

function playFirst() { /* emit event to Android native player */ }

onMounted(() => {
  const id = Number(route.params.id)
  if (id) store.fetchDetail(id)
})
</script>

<style scoped>
.detail-header { width: 100%; aspect-ratio: 16/9; background: linear-gradient(135deg, #6c5ce7, #2d1b4e); position: relative; }
.gradient { position: absolute; inset: 0; background: linear-gradient(transparent 40%, #0f0f23); }
.back-btn { position: absolute; top: 12px; left: 12px; width: 36px; height: 36px; border-radius: 50%; border: none; background: rgba(0,0,0,0.4); color: #fff; font-size: 20px; cursor: pointer; z-index: 2; }
.body { padding: 16px; }
.body h1 { color: #fff; font-size: 20px; font-weight: 700; }
.sub-info { display: flex; gap: 12px; margin-top: 6px; color: #888; font-size: 13px; }
.rating-row { display: flex; align-items: center; gap: 8px; margin-top: 10px; }
.stars { color: var(--rating); font-size: 16px; }
.score { color: var(--rating); font-size: 18px; font-weight: 700; }
.desc { color: #bbb; font-size: 14px; line-height: 1.7; margin-top: 14px; }
.actions { margin-top: 16px; }
.btn { display: inline-flex; align-items: center; justify-content: center; padding: 12px 24px; border-radius: 12px; border: none; font-size: 15px; font-weight: 600; cursor: pointer; }
.btn-primary { background: linear-gradient(135deg, #6c5ce7, #a29bfe); color: #fff; }
.episode-header { display: flex; border-bottom: 1px solid rgba(255,255,255,0.06); padding: 0 16px; }
.episode-header span { padding: 10px 0; color: var(--primary); font-size: 14px; font-weight: 500; border-bottom: 2px solid var(--primary); }
</style>
