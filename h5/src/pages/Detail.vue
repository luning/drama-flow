<!--
  剧集详情.vue — Auto-generated from specs/screens/detail.yaml
  DO NOT EDIT MANUALLY. Modify the screen spec instead.
-->
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useDetail } from '@/stores/detail'
import { fetchfetchDetailHeader } from '@/api/detail'
import { fetchfetchDetailBody } from '@/api/detail'
import { fetchfetchEpisodeList } from '@/api/detail'

const router = useRouter()
const store = useDetail()
const loading = ref(true)
const detail_header = ref([])
const detail_body = ref([])
const episode_list = ref([])

onMounted(async () => {
  loading.value = true
  try {
    await store.fetchDetailHeader()
    await store.fetchDetailBody()
    await store.fetchEpisodeList()
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="page detail-page">
    <!-- @component: detail-header (template not yet defined) -->
    <!-- @component: detail-body (template not yet defined) -->
    <!-- @component: tabs (template not yet defined) -->
    <div class="episode-list">
      <div class="episode-item" v-for="ep in store.episodes" :key="ep.num"
           @click="router.push('/player/' + ep.num)">
        <span class="number">{{ ep.num }}</span>
        <div class="info">
          <div class="title">{{ ep.title }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.detail-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg-primary);
}
</style>
