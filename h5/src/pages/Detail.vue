<!--
  剧集详情.vue — Scaffold generated from specs/screens/detail.yaml
  Edit this file to implement the page. The screen spec defines the structure.
-->
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
// Import stores and APIs as needed:

const router = useRouter()
const loading = ref(true)
const episodes = ref([] as any[])
// Data sources defined in screen spec:
// /api/dramas/{drama_id}, /api/dramas/{drama_id}, /api/dramas/{drama_id}/episodes

onMounted(async () => {
  loading.value = true
  try {
    // TODO: Fetch data from: /api/dramas/{drama_id}, /api/dramas/{drama_id}, /api/dramas/{drama_id}/episodes
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="page detail-page">
    <!-- @component: detail-header — template not yet defined for section detail-header -->
    <!-- @component: detail-body — template not yet defined for section detail-body -->
    <!-- @component: tabs — template not yet defined for section episode-tabs -->
    <!-- episode-list: episode-list -->
    <div class="episode-list">
      <div class="episode-item" v-for="ep in episodes" :key="ep.num"
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
