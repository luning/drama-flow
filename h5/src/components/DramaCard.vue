<template>
  <div class="card" @click="$router.push(`/detail/${drama.id}`)">
    <div class="thumb" :style="{ backgroundImage: drama.cover_url ? `url(${drama.cover_url})` : undefined }">
      <span class="badge">{{ badgeText }}</span>
      <span class="duration">{{ drama.episode_count }}集</span>
    </div>
    <div class="info">
      <h4>{{ drama.title }}</h4>
      <div class="meta">
        <span>{{ drama.episode_count }}集</span>
        <span>·</span>
        <span>{{ categoryName }}</span>
      </div>
      <div class="rating">★ {{ drama.rating }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { DramaListItem } from '@/api/dramas'

type DramaCardItem = DramaListItem & { category_slug?: string }

const props = defineProps<{ drama: DramaCardItem }>()

const categoryNames: Record<string, string> = {
  romance: '甜宠', suspense: '悬疑', comedy: '搞笑', fantasy: '奇幻', president: '霸总',
}

const categoryName = computed(() => {
  const slug = props.drama.category_slug
  return (slug ? categoryNames[slug] : undefined) ?? slug ?? '热门'
})

const badgeText = computed(() => {
  return props.drama.status === 'completed' ? '完结' : '热门'
})
</script>

<style scoped>
.card { border-radius: 14px; overflow: hidden; background: var(--bg-card); cursor: pointer; transition: transform 0.2s; }
.card:hover { transform: translateY(-3px); }
.thumb { aspect-ratio: 3/4; display: flex; align-items: flex-end; padding: 10px; position: relative; background-size: cover; background-position: center; background-color: #2d1b4e; }
.badge { position: absolute; top: 8px; left: 8px; background: rgba(108,92,231,0.9); color: #fff; font-size: 10px; padding: 2px 8px; border-radius: 4px; }
.duration { position: absolute; bottom: 6px; right: 6px; background: rgba(0,0,0,0.7); color: #fff; font-size: 10px; padding: 2px 6px; border-radius: 4px; }
.info { padding: 10px 12px 12px; }
.info h4 { color: #fff; font-size: 14px; font-weight: 600; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.meta { display: flex; gap: 4px; margin-top: 4px; color: #777; font-size: 11px; }
.rating { color: var(--rating); font-size: 11px; margin-top: 2px; }
</style>
