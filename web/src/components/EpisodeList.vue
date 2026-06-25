<template>
  <div class="episode-list">
    <div
      v-for="ep in episodes"
      :key="ep.id"
      class="episode-item"
      @click="$emit('select', ep)"
    >
      <div class="ep-info">
        <span class="ep-num">第 {{ ep.episode_number }} 集</span>
        <span class="ep-title">{{ ep.title }}</span>
        <span class="ep-duration">{{ ep.duration }}</span>
      </div>
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: progressOf(ep.id) + '%' }" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Episode } from '@/api/episodes'
import type { WatchRecord } from '@/api/watchRecords'

const props = defineProps<{
  episodes: Episode[]
  records: Record<number, WatchRecord>
}>()
defineEmits<{ select: [ep: Episode] }>()

function progressOf(episodeId: number): number {
  return props.records[episodeId]?.progress ?? 0
}
</script>

<style scoped>
.episode-list { display: flex; flex-direction: column; gap: var(--space-2); }
.episode-item {
  padding: var(--space-3); background: var(--bg-card);
  border-radius: var(--radius-sm); cursor: pointer;
  border: 1px solid var(--border);
}
.episode-item:hover { border-color: var(--color-primary); }
.ep-info { display: flex; gap: var(--space-3); align-items: center; margin-bottom: var(--space-2); }
.ep-num { color: var(--color-primary); font-weight: 600; font-size: 0.875rem; min-width: 60px; }
.ep-title { flex: 1; color: var(--text-primary); font-size: 0.875rem; }
.ep-duration { color: var(--text-secondary); font-size: 0.75rem; }
.progress-bar { height: 3px; background: var(--border); border-radius: 2px; }
.progress-fill { height: 100%; background: var(--color-primary); border-radius: 2px; transition: width 0.3s; }
</style>
