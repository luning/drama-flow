<template>
  <div class="player-page">
    <NavBar />
    <div v-if="loading" class="loading">加载中...</div>
    <main v-else class="player-container">
      <VideoPlayer
        :key="currentEpisodeId"
        :src="videoUrl"
        :startPosition="startPosition"
        :autoplay="autoplay"
        @progress="onProgress"
        @ended="onEnded"
      />
      <div class="info">
        <h2>{{ episode?.title }}</h2>
        <div class="ep-nav">
          <button v-if="prevEpisode" class="ep-btn" @click="goEpisode(prevEpisode)">‹ 上一集</button>
          <span class="ep-num">第 {{ episode?.episode_number }} 集 / 共 {{ allEpisodes.length }} 集</span>
          <button v-if="nextEpisode" class="ep-btn" @click="goEpisode(nextEpisode)">下一集 ›</button>
        </div>
      </div>
      <div class="episodes-section">
        <h3>全部剧集</h3>
        <EpisodeList :episodes="enrichedEpisodes" @play="goEpisode" />
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { episodeApi, type Episode } from '@/api/episodes'
import { useWatchRecordStore } from '@/stores/watchRecord'
import VideoPlayer from '@/components/VideoPlayer.vue'
import EpisodeList from '@/components/EpisodeList.vue'
import NavBar from '@/components/NavBar.vue'

const route = useRoute()
const router = useRouter()
const wrStore = useWatchRecordStore()

const dramaId = Number(route.params.id)

const loading = ref(true)
const autoplay = ref(false)
const videoUrl = ref('')
const startPosition = ref(0)
const episode = ref<Episode | null>(null)
const allEpisodes = ref<Episode[]>([])

const currentEpisodeId = computed(() => Number(route.params.ep))

const currentIdx = computed(() =>
  allEpisodes.value.findIndex((ep) => ep.id === currentEpisodeId.value)
)
const prevEpisode = computed(() =>
  currentIdx.value > 0 ? allEpisodes.value[currentIdx.value - 1] : null
)
const nextEpisode = computed(() =>
  currentIdx.value >= 0 && currentIdx.value < allEpisodes.value.length - 1
    ? allEpisodes.value[currentIdx.value + 1]
    : null
)

const enrichedEpisodes = computed(() =>
  allEpisodes.value.map((ep) => {
    const rec = wrStore.cachedRecord(ep.id)
    return {
      ...ep,
      watched: rec ? rec.completed || rec.progress > 0 : false,
      active: ep.id === currentEpisodeId.value,
    }
  })
)

function goEpisode(ep: Episode) {
  router.push(`/drama/${dramaId}/episode/${ep.id}`)
}

async function onProgress(currentTime: number, duration: number) {
  await wrStore.saveProgress(currentEpisodeId.value, currentTime, duration, false)
}

async function onEnded(currentTime: number, duration: number) {
  await wrStore.saveProgress(currentEpisodeId.value, currentTime, duration, true)
  if (nextEpisode.value) {
    autoplay.value = true
    goEpisode(nextEpisode.value)
  }
}

async function loadEpisode(episodeId: number) {
  loading.value = true
  videoUrl.value = ''
  startPosition.value = 0
  try {
    const [urlResp, record] = await Promise.all([
      episodeApi.videoUrl(episodeId),
      wrStore.fetchRecord(episodeId).catch(() => null),
    ])
    videoUrl.value = urlResp.data.url
    startPosition.value = record?.last_position ?? 0

    if (allEpisodes.value.length === 0) {
      const epResp = await episodeApi.list(dramaId)
      allEpisodes.value = epResp.data
      await wrStore.fetchForEpisodes(allEpisodes.value.map((ep) => ep.id))
    }
    episode.value = allEpisodes.value.find((ep) => ep.id === episodeId) ?? null
  } catch (e) {
    console.error('Player load failed', e)
    autoplay.value = false
  } finally {
    loading.value = false
  }
}

// Reload when navigating between episodes in the same component instance
watch(currentEpisodeId, (id) => {
  if (window.DramaFlowBridge) return
  loadEpisode(id)
})

onMounted(async () => {
  if (window.DramaFlowBridge) {
    try {
      const { data: ep } = await episodeApi.detail(currentEpisodeId.value)
      window.DramaFlowBridge.openPlayer(currentEpisodeId.value, dramaId, ep.episode_number)
    } catch (e) {
      console.error('openPlayer failed', e)
    } finally {
      loading.value = false
    }
    router.back()
    return
  }
  await loadEpisode(currentEpisodeId.value)
})
</script>

<style scoped>
.player-page { min-height: 100vh; background: var(--bg-primary); }
.loading { text-align: center; padding: var(--space-8); color: var(--text-secondary); }
.player-container { max-width: 1000px; margin: 0 auto; padding: var(--space-4); }

.info { padding: var(--space-3) 0 var(--space-2); }
.info h2 { color: var(--text-primary); font-size: 1.125rem; margin-bottom: var(--space-2); }

.ep-nav {
  display: flex; align-items: center; gap: var(--space-3);
  padding: var(--space-2) 0;
}
.ep-num { color: var(--text-secondary); font-size: 0.875rem; flex: 1; text-align: center; }
.ep-btn {
  padding: var(--space-1) var(--space-3); background: var(--surface-mid);
  color: var(--text-primary); border: 1px solid var(--border);
  border-radius: var(--radius-sm); cursor: pointer; font-size: 0.875rem;
  white-space: nowrap;
}
.ep-btn:hover { background: var(--color-primary); border-color: var(--color-primary); }

.episodes-section { margin-top: var(--space-4); }
.episodes-section h3 {
  color: var(--text-primary); font-size: 1rem;
  padding: 0 0 var(--space-3); border-bottom: 1px solid var(--border);
  margin-bottom: var(--space-2);
}
</style>
