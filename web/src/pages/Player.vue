<template>
  <div class="player-page">
    <NavBar />
    <div v-if="loading" class="loading">加载中...</div>
    <main v-else class="player-container">
      <VideoPlayer
        :src="videoUrl"
        :startPosition="startPosition"
        @progress="onProgress"
        @ended="onEnded"
      />
      <div class="info">
        <h2>{{ episode?.title }}</h2>
        <p v-if="nextEpisode" class="next-hint">下一集：{{ nextEpisode.title }}</p>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { episodeApi, type Episode } from '@/api/episodes'
import { useWatchRecordStore } from '@/stores/watchRecord'
import VideoPlayer from '@/components/VideoPlayer.vue'
import NavBar from '@/components/NavBar.vue'

const route = useRoute()
const router = useRouter()
const wrStore = useWatchRecordStore()

const dramaId = Number(route.params.id)
const episodeId = Number(route.params.ep)

const loading = ref(true)
const videoUrl = ref('')
const startPosition = ref(0)
const episode = ref<Episode | null>(null)
const nextEpisode = ref<Episode | null>(null)

async function onProgress(currentTime: number, duration: number) {
  await wrStore.saveProgress(episodeId, currentTime, duration, false)
}

async function onEnded() {
  await wrStore.saveProgress(episodeId, 0, 1, true)
  if (nextEpisode.value) {
    router.push(`/drama/${dramaId}/episode/${nextEpisode.value.id}`)
  }
}

onMounted(async () => {
  try {
    const [urlResp, recordResp, episodesResp] = await Promise.all([
      episodeApi.videoUrl(episodeId),
      wrStore.fetchRecord(episodeId),
      episodeApi.list(dramaId),
    ])

    videoUrl.value = urlResp.data.url
    startPosition.value = recordResp.last_position ?? 0

    const episodes = episodesResp.data
    episode.value = episodes.find((ep: any) => ep.id === episodeId) ?? null
    const idx = episodes.findIndex((ep: any) => ep.id === episodeId)
    nextEpisode.value = idx >= 0 && idx < episodes.length - 1 ? episodes[idx + 1] : null
  } catch (e) {
    console.error('Player load failed', e)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.player-page { min-height: 100vh; background: var(--bg-primary); }
.loading { text-align: center; padding: var(--space-8); color: var(--text-secondary); }
.player-container { max-width: 1000px; margin: 0 auto; padding: var(--space-4); }
.info { padding: var(--space-4) 0; }
.info h2 { color: var(--text-primary); }
.next-hint { margin-top: var(--space-2); color: var(--text-secondary); font-size: 0.875rem; }
</style>
