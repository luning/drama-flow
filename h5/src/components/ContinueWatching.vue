<template>
  <div class="cw-section" v-if="items.length > 0">
    <div class="section-header">
      <span class="section-title">继续观看</span>
    </div>
    <div class="cw-scroll">
      <div
        v-for="item in items"
        :key="item.episode_id"
        class="cw-card"
        @click="$router.push(`/detail/${item.drama_id}`)"
      >
        <div class="cw-thumb" :style="item.drama_cover ? { backgroundImage: `url(${item.drama_cover})` } : {}">
          <div class="cw-progress-bar">
            <div class="cw-progress-fill" :style="{ width: `${Math.round(item.progress * 100)}%` }" />
          </div>
        </div>
        <div class="cw-info">
          <p class="cw-title">{{ item.drama_title }}</p>
          <p class="cw-ep">第 {{ item.episode_number }} 集</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  items: {
    drama_id: number
    drama_title: string
    drama_cover: string
    episode_id: number
    episode_number: number
    progress: number
  }[]
}>()
</script>

<style scoped>
.cw-section { padding: 12px 0 4px; }

.section-header {
  padding: 0 16px 10px;
}

.section-title {
  color: #fff;
  font-size: 15px;
  font-weight: 600;
}

.cw-scroll {
  display: flex;
  gap: 10px;
  padding: 0 16px;
  overflow-x: auto;
}

.cw-scroll::-webkit-scrollbar { display: none; }

.cw-card {
  flex-shrink: 0;
  width: 110px;
  cursor: pointer;
  border-radius: 10px;
  overflow: hidden;
  background: var(--bg-card);
  transition: transform 0.2s;
}

.cw-card:hover { transform: translateY(-2px); }

.cw-thumb {
  position: relative;
  aspect-ratio: 3/4;
  background-size: cover;
  background-position: center;
  background-color: #2d1b4e;
}

.cw-progress-bar {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: rgba(255, 255, 255, 0.2);
}

.cw-progress-fill {
  height: 100%;
  background: var(--color-primary);
  min-width: 4px;
}

.cw-info {
  padding: 6px 8px 8px;
}

.cw-title {
  color: #ddd;
  font-size: 12px;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.cw-ep {
  color: #666;
  font-size: 11px;
  margin-top: 2px;
}
</style>
