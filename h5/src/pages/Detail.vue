<template>
  <div class="page">
    <NavBar />
    <div v-if="dramaStore.loading" class="loading">加载中...</div>
    <main v-else-if="dramaStore.detail" class="container">
      <div class="hero">
        <img :src="dramaStore.detail.cover_url" :alt="dramaStore.detail.title" class="cover" />
        <div class="meta">
          <h1>{{ dramaStore.detail.title }}</h1>
          <p class="sub">{{ dramaStore.detail.category_name }} · {{ dramaStore.detail.year }} · {{ dramaStore.detail.episode_count }}集</p>
          <p class="rating">评分：{{ dramaStore.detail.rating?.toFixed(1) }}</p>
          <p class="desc">{{ dramaStore.detail.description }}</p>
          <button v-if="continueEp" class="btn-primary" @click="goEpisode(continueEp)">
            继续观看第 {{ continueEp.episode_number }} 集
          </button>
        </div>
      </div>
      <h2>剧集列表</h2>
      <EpisodeList :episodes="enrichedEpisodes" @play="goEpisode" />
    </main>
    <div v-else class="loading">剧集不存在</div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useDramaStore } from '@/stores/drama'
import { useWatchRecordStore } from '@/stores/watchRecord'
import NavBar from '@/components/NavBar.vue'
import EpisodeList from '@/components/EpisodeList.vue'

const route = useRoute()
const router = useRouter()
const dramaStore = useDramaStore()
const wrStore = useWatchRecordStore()

const dramaId = Number(route.params.id)

const enrichedEpisodes = computed(() =>
  dramaStore.episodes.map((ep: any) => {
    const rec = wrStore.cachedRecord(ep.id)
    return { ...ep, watched: rec ? rec.completed || rec.progress > 0 : false }
  })
)

const continueEp = computed(() =>
  dramaStore.episodes.find((ep: any) => {
    const rec = wrStore.cachedRecord(ep.id)
    return rec && rec.progress > 0 && !rec.completed
  }) ?? null
)

function goEpisode(ep: any) {
  router.push(`/drama/${dramaId}/episode/${ep.id}`)
}

onMounted(async () => {
  await dramaStore.fetchDetail(dramaId)
  await wrStore.fetchForEpisodes(dramaStore.episodes.map((ep: any) => ep.id))
})
</script>

<style scoped>
.page { min-height: 100vh; background: var(--bg-primary); }
.container { max-width: 900px; margin: 0 auto; padding: var(--space-6); }
.loading { text-align: center; padding: var(--space-8); color: var(--text-secondary); }
.hero { display: flex; gap: var(--space-6); margin-bottom: var(--space-6); flex-wrap: wrap; }
.cover { width: 180px; border-radius: var(--radius-md); object-fit: cover; flex-shrink: 0; align-self: flex-start; }
.meta { flex: 1; min-width: 200px; display: flex; flex-direction: column; gap: var(--space-2); }
h1 { font-size: 1.5rem; color: var(--text-primary); }
.sub, .rating { font-size: 0.875rem; color: var(--text-secondary); }
.desc { color: var(--text-primary); line-height: 1.6; }
h2 { font-size: 1.125rem; margin-bottom: var(--space-3); color: var(--text-primary); }
.btn-primary {
  padding: var(--space-2) var(--space-4); background: var(--color-primary);
  color: #fff; border: none; border-radius: var(--radius-sm); cursor: pointer;
  font-size: 0.875rem; align-self: flex-start;
}
</style>
