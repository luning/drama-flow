<template>
  <div class="video-wrapper">
    <video
      ref="videoEl"
      controls
      class="video"
      @ended="onEnded"
      @pause="onPause"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'

const props = defineProps<{
  src: string
  startPosition: number
}>()

const emit = defineEmits<{
  progress: [currentTime: number, duration: number]
  ended: []
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
  videoEl.value.addEventListener('loadedmetadata', applyStartPosition, { once: true })
  progressTimer = setInterval(emitProgress, 10000)
})

onBeforeUnmount(() => {
  if (progressTimer) clearInterval(progressTimer)
  emitProgress()
})

function applyStartPosition() {
  if (videoEl.value && props.startPosition > 0) {
    videoEl.value.currentTime = props.startPosition
  }
}

function emitProgress() {
  if (!videoEl.value) return
  const { currentTime, duration } = videoEl.value
  if (currentTime === lastSavedTime || !duration) return
  lastSavedTime = currentTime
  emit('progress', currentTime, duration)
}

function onPause() { emitProgress() }
function onEnded() { emit('ended') }
</script>

<style scoped>
.video-wrapper { width: 100%; background: #000; }
.video { width: 100%; max-height: 70vh; display: block; }
</style>
