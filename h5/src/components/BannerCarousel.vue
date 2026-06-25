<template>
  <div class="banner-wrapper" v-if="items.length > 0">
    <div class="banner-track">
      <div
        v-for="(item, i) in items"
        :key="i"
        class="banner-slide"
        :class="{ active: i === current }"
        @click="$router.push(`/drama/${item.drama_id}`)"
      >
        <img class="banner-img" :src="item.image_url" :alt="item.title" />
        <div class="banner-overlay">
          <h2 class="banner-title">{{ item.title }}</h2>
          <span class="banner-tag">{{ tags[item.sort_order] ?? '精彩不容错过' }}</span>
        </div>
      </div>
    </div>
    <div class="banner-dots">
      <span
        v-for="(_, i) in items"
        :key="i"
        class="dot"
        :class="{ active: i === current }"
        @click="goTo(i)"
      />
    </div>
    <button class="arrow left" @click="prev">‹</button>
    <button class="arrow right" @click="next">›</button>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import type { Banner } from '@/api/dramas'

const props = defineProps<{ items: Banner[] }>()

const tags = ['🏆 本周必追', '🔥 热播榜第一', '✨ 新剧上线', '⭐ 高分推荐', '💎 编辑精选']
const current = ref(0)
let timer: ReturnType<typeof setInterval> | null = null

function goTo(i: number) { current.value = i }
function next() { current.value = (current.value + 1) % props.items.length }
function prev() { current.value = (current.value - 1 + props.items.length) % props.items.length }

onMounted(() => { timer = setInterval(next, 4000) })
onUnmounted(() => { if (timer) clearInterval(timer) })
</script>

<style scoped>
.banner-wrapper {
  position: relative; width: 100%; aspect-ratio: 16 / 5;
  overflow: hidden; background: #111;
}
.banner-track { position: relative; width: 100%; height: 100%; }
.banner-slide {
  position: absolute; inset: 0; opacity: 0;
  transition: opacity 0.6s ease; cursor: pointer;
}
.banner-slide.active { opacity: 1; }
.banner-img { width: 100%; height: 100%; object-fit: cover; display: block; }
.banner-overlay {
  position: absolute; inset: 0;
  background: linear-gradient(to right, rgba(0,0,0,0.7) 0%, transparent 60%);
  display: flex; flex-direction: column; justify-content: center; padding: 0 60px;
}
.banner-title {
  color: #fff; font-size: clamp(20px, 3vw, 36px); font-weight: 700;
  margin-bottom: 10px; text-shadow: 0 2px 8px rgba(0,0,0,0.5);
}
.banner-tag { color: #ddd; font-size: clamp(12px, 1.5vw, 16px); }
.banner-dots {
  position: absolute; bottom: 14px; left: 50%; transform: translateX(-50%);
  display: flex; gap: 6px; z-index: 2;
}
.dot {
  width: 7px; height: 7px; border-radius: 50%;
  background: rgba(255,255,255,0.4); cursor: pointer; transition: all 0.3s;
}
.dot.active { width: 22px; border-radius: 4px; background: var(--color-primary); }
.arrow {
  position: absolute; top: 50%; transform: translateY(-50%);
  background: rgba(0,0,0,0.4); color: #fff; border: none;
  width: 40px; height: 40px; border-radius: 50%; font-size: 22px;
  cursor: pointer; z-index: 2; transition: background 0.2s;
  display: flex; align-items: center; justify-content: center;
}
.arrow:hover { background: rgba(0,0,0,0.7); }
.arrow.left { left: 16px; }
.arrow.right { right: 16px; }
</style>
