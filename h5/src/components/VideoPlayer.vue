<template>
  <div class="video-wrapper">
    <video
      ref="videoEl"
      controls
      class="video"
      @play="onPlay"
      @pause="onPause"
      @ended="onEnded"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'

const props = defineProps<{
  src: string
  startPosition: number
  autoplay?: boolean
}>()

const emit = defineEmits<{
  progress: [currentTime: number, duration: number]
  ended: [currentTime: number, duration: number]
}>()

const videoEl = ref<HTMLVideoElement | null>(null)
let progressTimer: ReturnType<typeof setInterval> | null = null
let lastSavedTime = 0

watch(() => props.src, (newSrc) => {
  if (!videoEl.value || !newSrc) return
  videoEl.value.src = newSrc
  videoEl.value.load()
  videoEl.value.addEventListener('loadedmetadata', applyStartPosition, { once: true })
})

onMounted(() => {
  if (!videoEl.value || !props.src) return
  videoEl.value.src = props.src
  videoEl.value.load()
  videoEl.value.addEventListener('loadedmetadata', applyStartPosition, { once: true })
})

onBeforeUnmount(() => {
  stopProgressTimer()
  emitProgress()
})

function applyStartPosition() {
  if (!videoEl.value) return
  if (props.startPosition > 0) {
    videoEl.value.currentTime = props.startPosition
  }
  if (props.autoplay) {
    videoEl.value.play().catch(() => {/* autoplay blocked by browser policy */})
  }
}

function emitProgress() {
  if (!videoEl.value) return
  const { currentTime, duration } = videoEl.value
  if (currentTime === lastSavedTime || !duration) return
  lastSavedTime = currentTime
  emit('progress', currentTime, duration)
}

function startProgressTimer() {
  if (!progressTimer) {
    progressTimer = setInterval(emitProgress, 10000)
  }
}

function stopProgressTimer() {
  if (progressTimer) {
    clearInterval(progressTimer)
    progressTimer = null
  }
}

function onPlay() { startProgressTimer() }
function onPause() {
  stopProgressTimer()
  emitProgress()
}
function onEnded() {
  stopProgressTimer()
  const duration = videoEl.value?.duration ?? 0
  emit('ended', duration, duration)
}
</script>

<style scoped>
.video-wrapper { width: 100%; background: #000; }
.video { width: 100%; max-height: 70vh; display: block; }
</style>
