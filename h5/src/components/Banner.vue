<template>
  <div class="banner-wrapper">
    <div class="banner-track" :style="{ transform: `translateX(-${current * 100}%)` }">
      <div v-for="(item, i) in items" :key="i" class="banner-slide" :style="{ background: item.color }">
        <div class="overlay">
          <h3>{{ item.title }}</h3>
          <p>{{ item.subtitle }}</p>
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

defineProps<{ items: { title: string; subtitle: string; color: string }[] }>()

const current = ref(0)
let timer: ReturnType<typeof setInterval> | null = null

function goTo(i: number) { current.value = i }

onMounted(() => { timer = setInterval(() => current.value = (current.value + 1) % 3, 4000) })
onUnmounted(() => { if (timer) clearInterval(timer) })
</script>

<style scoped>
.banner-wrapper { padding: 0 16px; margin-top: 8px; }
.banner-track { display: flex; border-radius: 16px; overflow: hidden; aspect-ratio: 16/7; transition: transform 0.5s ease; }
.banner-slide { min-width: 100%; display: flex; align-items: flex-end; padding: 20px; }
.overlay { background: linear-gradient(transparent, rgba(0,0,0,0.7)); padding: 16px; border-radius: 8px; width: 100%; }
.overlay h3 { color: #fff; font-size: 18px; font-weight: 700; }
.overlay p { color: #ddd; font-size: 12px; margin-top: 2px; }
.dots { display: flex; justify-content: center; gap: 6px; margin-top: 10px; }
.dots span { width: 6px; height: 6px; border-radius: 50%; background: #444; cursor: pointer; transition: all 0.3s; }
.dots span.active { width: 20px; border-radius: 3px; background: var(--primary); }
</style>
