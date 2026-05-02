<template>
  <div class="banner-wrapper" v-if="items.length > 0">
    <div class="banner-track">
      <div v-for="(item, i) in items" :key="i" class="banner-slide" :class="{ active: i === current }" @click="goDetail(item.drama_id)">
        <img class="banner-img" :src="item.image_url" alt="" />
        <div class="overlay">
          <h3>{{ item.title }}</h3>
          <p>{{ getSubtitle(item) }}</p>
        </div>
      </div>
    </div>
    <div class="dots">
      <span v-for="(_, i) in items" :key="i" :class="{ active: i === current }" @click="goTo(i)" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps<{ items: { drama_id: number; title: string; image_url: string; sort_order: number }[] }>()
const router = useRouter()

const current = ref(0)
let timer: ReturnType<typeof setInterval> | null = null

function goTo(i: number) { current.value = i }

function goDetail(id: number) {
  router.push(`/detail/${id}`)
}

function getSubtitle(item: { title: string; sort_order: number }) {
  const tags = ['🏆 本周必追', '🔥 热播榜第一', '✨ 新剧上线', '⭐ 高分推荐', '💎 编辑精选']
  return `${tags[item.sort_order] || '📺 精彩不容错过'}`
}

onMounted(() => {
  timer = setInterval(() => {
    if (props.items.length > 0) {
      current.value = (current.value + 1) % props.items.length
    }
  }, 4000)
})

onUnmounted(() => { if (timer) clearInterval(timer) })
</script>

<style scoped>
.banner-wrapper { padding: 0 16px; margin-top: 8px; }
.banner-track { position: relative; border-radius: 16px; overflow: hidden; aspect-ratio: 16/7; }
.banner-slide { position: absolute; inset: 0; display: flex; flex-direction: column; cursor: pointer; opacity: 0; transition: opacity 0.6s ease; }
.banner-slide.active { opacity: 1; }
.banner-img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
.overlay { position: relative; z-index: 1; margin-top: auto; background: linear-gradient(transparent, rgba(0,0,0,0.8)); padding: 16px; width: 100%; }
.overlay h3 { color: #fff; font-size: 18px; font-weight: 700; }
.overlay p { color: #ddd; font-size: 12px; margin-top: 2px; }
.dots { display: flex; justify-content: center; gap: 6px; margin-top: 10px; }
.dots span { width: 6px; height: 6px; border-radius: 50%; background: #444; cursor: pointer; transition: all 0.3s; }
.dots span.active { width: 20px; border-radius: 3px; background: var(--primary); }
</style>
