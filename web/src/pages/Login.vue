<template>
  <div class="auth-page">
    <div class="auth-card">
      <h1>DramaFlow</h1>
      <form @submit.prevent="handleLogin">
        <div class="field">
          <label>邮箱</label>
          <input v-model="email" type="email" placeholder="请输入邮箱" required />
        </div>
        <div class="field">
          <label>密码</label>
          <input v-model="password" type="password" placeholder="请输入密码" required />
        </div>
        <div class="field-row">
          <label><input v-model="rememberMe" type="checkbox" /> 记住我</label>
        </div>
        <p v-if="error" class="error">{{ error }}</p>
        <button type="submit" :disabled="loading" class="btn-primary">
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </form>
      <p class="link">没有账号？<router-link to="/register">注册</router-link></p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const rememberMe = ref(false)
const loading = ref(false)
const error = ref('')

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    await authStore.login(email.value, password.value, rememberMe.value)
    const redirect = route.query.redirect as string | undefined
    router.push(redirect || '/')
  } catch (e: any) {
    const msg = e.response?.data?.detail
    error.value = typeof msg === 'string' ? msg : '登录失败，请重试'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-primary);
}
.auth-card {
  background: var(--bg-card);
  border-radius: var(--radius-card);
  padding: var(--space-8);
  width: 360px;
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}
h1 { color: var(--color-primary); text-align: center; font-size: 1.5rem; }
.field { display: flex; flex-direction: column; gap: var(--space-1); }
.field label { font-size: 0.875rem; color: var(--text-secondary); }
.field input[type="email"],
.field input[type="password"] {
  padding: var(--space-2) var(--space-3);
  background: var(--surface-mid);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  font-size: 1rem;
}
.field-row { display: flex; align-items: center; gap: var(--space-2); font-size: 0.875rem; color: var(--text-secondary); }
.error { color: var(--color-danger); font-size: 0.875rem; }
.btn-primary {
  width: 100%;
  padding: var(--space-3);
  background: var(--color-primary);
  color: #fff;
  border: none;
  border-radius: var(--radius-sm);
  font-size: 1rem;
  cursor: pointer;
}
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
.link { text-align: center; font-size: 0.875rem; color: var(--text-secondary); }
.link a { color: var(--color-primary); }
</style>
