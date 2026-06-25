<template>
  <div class="page">
    <NavBar />
    <main class="container">
      <h1>观看历史</h1>
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="!wrStore.history.length" class="empty">暂无观看记录</div>
      <div v-else class="history-list">
        <div
          v-for="item in wrStore.history"
          :key="item.episode_id"
          class="history-item"
          @click="goPlay(item)"
        >
          <img :src="item.drama_cover" :alt="item.drama_title" class="cover" />
          <div class="info">
            <p class="title">{{ item.drama_title }}</p>
            <p class="sub">第 {{ item.episode_number }} 集</p>
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: item.progress + '%' }" />
            </div>
            <p class="time">{{ formatTime(item.updated_at) }}</p>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useWatchRecordStore } from '@/stores/watchRecord'
import { type ContinueWatchingItem } from '@/api/watchRecords'
import NavBar from '@/components/NavBar.vue'

const router = useRouter()
const wrStore = useWatchRecordStore()
const loading = ref(true)

function goPlay(item: ContinueWatchingItem) {
  router.push(`/drama/${item.drama_id}/episode/${item.episode_id}`)
}

function formatTime(iso: string): string {
  return new Date(iso).toLocaleString('zh-CN', {
    month: 'numeric', day: 'numeric', hour: '2-digit', minute: '2-digit'
  })
}

onMounted(async () => {
  try {
    await wrStore.fetchHistory()
  } catch (e) {
    console.error('fetchHistory failed', e)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.page { min-height: 100vh; background: var(--bg-primary); }
.container { max-width: 900px; margin: 0 auto; padding: var(--space-6); }
h1 { font-size: 1.5rem; color: var(--text-primary); margin-bottom: var(--space-4); }
.loading, .empty { color: var(--text-secondary); text-align: center; padding: var(--space-8); }
.history-list { display: flex; flex-direction: column; gap: var(--space-3); }
.history-item {
  display: flex; gap: var(--space-4); padding: var(--space-3);
  background: var(--bg-card); border-radius: var(--radius-md);
  cursor: pointer; border: 1px solid var(--border);
}
.history-item:hover { border-color: var(--color-primary); }
.cover { width: 80px; height: 110px; object-fit: cover; border-radius: var(--radius-sm); flex-shrink: 0; }
.info { flex: 1; display: flex; flex-direction: column; gap: var(--space-1); }
.title { font-weight: 600; color: var(--text-primary); }
.sub { font-size: 0.875rem; color: var(--text-secondary); }
.progress-bar { height: 3px; background: var(--border); border-radius: 2px; margin: var(--space-1) 0; }
.progress-fill { height: 100%; background: var(--color-primary); border-radius: 2px; }
.time { font-size: 0.75rem; color: var(--text-secondary); }
</style>
