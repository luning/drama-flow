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
const loading = ref(false)
const error = ref('')

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    await authStore.login({ email: email.value, password: password.value })
    const redirect = route.query.redirect as string | undefined
    // Only allow same-origin relative paths to prevent open redirect attacks
    const safePath = redirect && redirect.startsWith('/') && !redirect.startsWith('//') ? redirect : '/'
    router.push(safePath)
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
  padding: var(--space-6);
}
.auth-card {
  background: var(--bg-card);
  border-radius: var(--radius-card);
  padding: var(--space-10);
  width: 360px;
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
}
h1 {
  color: var(--color-primary-light);
  text-align: center;
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
  margin: 0;
}
form {
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
}
.field {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}
.field label {
  font-size: var(--font-size-base);
  color: var(--text-label);
}
.field input {
  padding: var(--space-4) var(--space-4);
  background: var(--surface-mid);
  border: 1px solid var(--border);
  border-radius: var(--radius-btn);
  color: var(--text-primary);
  font-size: var(--font-size-md);
  transition: border-color var(--transition-default);
}
.field input:focus {
  outline: none;
  border-color: var(--color-primary);
}
.error {
  color: var(--color-danger);
  font-size: var(--font-size-sm);
  margin: 0;
}
.btn-primary {
  width: 100%;
  padding: var(--space-4);
  margin-top: var(--space-2);
  background: var(--color-primary);
  color: var(--text-primary);
  border: none;
  border-radius: var(--radius-btn);
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-semibold);
  cursor: pointer;
  transition: background var(--transition-default), box-shadow var(--transition-default);
}
.btn-primary:hover:not(:disabled) {
  background: var(--color-primary-light);
  box-shadow: var(--shadow-md);
}
.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.link {
  text-align: center;
  font-size: var(--font-size-base);
  color: var(--text-secondary);
  margin: 0;
}
.link a {
  color: var(--text-link);
}
</style>
