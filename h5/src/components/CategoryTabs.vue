<template>
  <div class="tabs">
    <button
      v-for="tab in tabs" :key="tab.key"
      :class="{ active: active === tab.key }"
      @click="$emit('change', tab.key)"
    >
      {{ tab.label }}
    </button>
  </div>
</template>

<script setup lang="ts">
defineProps<{ tabs: { key: string; label: string }[]; active: string }>()
defineEmits<{ change: [key: string] }>()
</script>

<style scoped>
.tabs { display: flex; gap: 8px; padding: 16px 16px 8px; overflow-x: auto; }
.tabs::-webkit-scrollbar { display: none; }
.tabs button { padding: 8px 18px; border-radius: 20px; background: rgba(255,255,255,0.06); color: #888; font-size: 13px; font-weight: 500; white-space: nowrap; cursor: pointer; transition: all 0.25s; flex-shrink: 0; }
.tabs button.active { background: var(--primary); color: #fff; }
.tabs button:not(.active):hover { background: rgba(255,255,255,0.1); color: #ccc; }
</style>
