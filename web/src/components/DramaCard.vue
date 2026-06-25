<template>
  <div class="drama-card" @click="$emit('click')">
    <img :src="drama.cover_url" :alt="drama.title" class="cover" />
    <div class="info">
      <p class="title">{{ drama.title }}</p>
      <p class="meta">{{ drama.rating.toFixed(1) }} · {{ drama.episode_count }}集</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { DramaListItem } from '@/api/dramas'
defineProps<{ drama: DramaListItem }>()
defineEmits<{ click: [] }>()
</script>

<style scoped>
.drama-card {
  cursor: pointer; border-radius: var(--radius-md);
  overflow: hidden; background: var(--bg-card);
  transition: transform 0.15s;
}
.drama-card:hover { transform: translateY(-2px); }
.cover { width: 100%; aspect-ratio: 3/4; object-fit: cover; display: block; }
.info { padding: var(--space-2); }
.title { font-size: 0.875rem; font-weight: 600; color: var(--text-primary); line-height: 1.3; }
.meta { font-size: 0.75rem; color: var(--text-secondary); margin-top: var(--space-1); }
</style>
