<template>
  <div class="page">
    <NavBar />
    <div v-if="loading" class="loading">加载中...</div>
    <main v-else-if="drama" class="container">
      <div class="hero">
        <img :src="drama.cover_url" :alt="drama.title" class="cover" />
        <div class="meta">
          <h1>{{ drama.title }}</h1>
          <p class="sub">{{ drama.category_name }} · {{ drama.year }} · {{ drama.episode_count }}集</p>
          <p class="rating">评分：{{ drama.rating.toFixed(1) }}</p>
          <p class="desc">{{ drama.description }}</p>
          <button v-if="continueEp" class="btn-primary" @click="goEpisode(continueEp)">
            继续观看第 {{ continueEp.episode_number }} 集
          </button>
        </div>
      </div>
      <h2>剧集列表</h2>
      <EpisodeList
        :episodes="episodes"
        :records="wrStore.records"
        @select="goEpisode"
      />
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useDramaStore } from '@/stores/drama'
import { useWatchRecordStore } from '@/stores/watchRecord'
import { episodeApi, type Episode } from '@/api/episodes'
import NavBar from '@/components/NavBar.vue'
import EpisodeList from '@/components/EpisodeList.vue'

const route = useRoute()
const router = useRouter()
const dramaStore = useDramaStore()
const wrStore = useWatchRecordStore()

const loading = ref(true)
const episodes = ref<Episode[]>([])
const dramaId = Number(route.params.id)

const drama = computed(() => dramaStore.currentDrama)

const continueEp = computed(() => {
  return episodes.value.find((ep) => {
    const rec = wrStore.cachedRecord(ep.id)
    return rec && rec.progress > 0 && !rec.completed
  }) ?? null
})

function goEpisode(ep: Episode) {
  router.push(`/drama/${dramaId}/episode/${ep.id}`)
}

onMounted(async () => {
  try {
    await dramaStore.loadDrama(dramaId)
    const { data } = await episodeApi.list(dramaId)
    episodes.value = data
    await wrStore.fetchForEpisodes(data.map((ep) => ep.id))
  } catch (e) {
    console.error('Detail load failed', e)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.page { min-height: 100vh; background: var(--bg-primary); }
.container { max-width: 900px; margin: 0 auto; padding: var(--space-6); }
.loading { text-align: center; padding: var(--space-8); color: var(--text-secondary); }
.hero { display: flex; gap: var(--space-6); margin-bottom: var(--space-6); }
.cover { width: 200px; border-radius: var(--radius-md); object-fit: cover; flex-shrink: 0; align-self: flex-start; }
.meta { flex: 1; display: flex; flex-direction: column; gap: var(--space-2); }
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
