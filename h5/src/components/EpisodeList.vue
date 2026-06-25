<template>
  <div class="episode-list">
    <div v-for="ep in episodes" :key="ep.id" class="episode-item" @click="handleClick(ep)">
      <span class="num" :class="{ watched: ep.watched }">{{ ep.episode_number }}</span>
      <div class="thumb-sm" :style="{ backgroundImage: ep.cover_url ? `url(${ep.cover_url})` : undefined }"></div>
      <div class="info">
        <h5>{{ ep.title }}</h5>
        <p>{{ ep.duration }}{{ ep.watched ? ' · 已观看' : '' }}</p>
      </div>
      <span class="action">{{ ep.watched ? '↻' : '▷' }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
const emit = defineEmits<{ play: [ep: any] }>()
defineProps<{ episodes: any[] }>()

function handleClick(ep: any) {
  emit('play', ep)
}
</script>

<style scoped>
.episode-list { padding: 8px 16px 20px; }
.episode-item { display: flex; align-items: center; gap: 12px; padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.04); cursor: pointer; }
.episode-item:hover { background: rgba(255,255,255,0.03); margin: 0 -8px; padding: 10px 8px; border-radius: 8px; }
.num { width: 28px; height: 28px; border-radius: 50%; background: rgba(255,255,255,0.06); display: flex; align-items: center; justify-content: center; color: var(--text-secondary); font-size: 12px; font-weight: 600; flex-shrink: 0; }
.num.watched { background: rgba(108,92,231,0.2); color: var(--color-primary); }
.thumb-sm { width: 80px; aspect-ratio: 16/9; border-radius: 6px; background: linear-gradient(135deg, #3d1b6e, #1a1a3e); background-size: cover; background-position: center; flex-shrink: 0; }
.info { flex: 1; }
.info h5 { color: var(--text-primary); font-size: 14px; font-weight: 500; }
.info p { color: var(--text-secondary); font-size: 12px; margin-top: 2px; }
.action { color: var(--text-secondary); font-size: 18px; }
</style>
