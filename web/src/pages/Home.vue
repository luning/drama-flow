<template>
  <div class="page">
    <NavBar />
    <main class="container">
      <div class="grid">
        <DramaCard
          v-for="drama in dramaStore.dramas"
          :key="drama.id"
          :drama="drama"
          @click="router.push(`/drama/${drama.id}`)"
        />
      </div>
      <div v-if="dramaStore.loading" class="loading">加载中...</div>
      <div v-if="!dramaStore.hasMore && dramaStore.dramas.length" class="end">已加载全部</div>
      <button
        v-if="dramaStore.hasMore && !dramaStore.loading"
        class="load-more"
        @click="dramaStore.loadDramas()"
      >加载更多</button>
    </main>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useDramaStore } from '@/stores/drama'
import DramaCard from '@/components/DramaCard.vue'
import NavBar from '@/components/NavBar.vue'

const router = useRouter()
const dramaStore = useDramaStore()
onMounted(() => dramaStore.loadDramas(true))
</script>

<style scoped>
.page { min-height: 100vh; background: var(--bg-primary); }
.container { max-width: 1200px; margin: 0 auto; padding: var(--space-4); }
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: var(--space-4);
}
.loading, .end { text-align: center; color: var(--text-secondary); padding: var(--space-4); }
.load-more {
  display: block; margin: var(--space-4) auto; padding: var(--space-2) var(--space-6);
  background: var(--color-primary); color: #fff; border: none;
  border-radius: var(--radius-sm); cursor: pointer;
}
</style>
