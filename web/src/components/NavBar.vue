<template>
  <nav class="navbar">
    <router-link to="/" class="brand">DramaFlow</router-link>
    <div class="links">
      <router-link to="/">首页</router-link>
      <router-link to="/history">观看历史</router-link>
      <button class="logout" @click="handleLogout">退出</button>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

async function handleLogout() {
  await authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.navbar {
  display: flex; align-items: center; justify-content: space-between;
  padding: var(--space-3) var(--space-6); background: var(--bg-card);
  border-bottom: 1px solid var(--border);
}
.brand { font-size: 1.25rem; font-weight: 700; color: var(--color-primary); text-decoration: none; }
.links { display: flex; align-items: center; gap: var(--space-4); }
.links a { color: var(--text-secondary); text-decoration: none; }
.links a.router-link-active { color: var(--color-primary); }
.logout {
  background: none; border: 1px solid var(--border);
  color: var(--text-secondary); padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-sm); cursor: pointer;
}
</style>
