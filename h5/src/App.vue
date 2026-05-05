<template>
  <router-view />
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

onMounted(() => {
  // Token 已在 main.ts 中通过 syncTokenFromNative() 同步。
  // 若未在 WebView 中运行（如浏览器开发环境），尝试从 localStorage 恢复会话。
  const auth = useAuthStore()
  if (!auth.isLoggedIn) {
    auth.tryRestoreSession()
  }
})
</script>
