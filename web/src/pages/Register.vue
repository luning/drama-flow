<template>
  <div class="auth-page">
    <div class="auth-card">
      <h1>注册账号</h1>
      <form @submit.prevent="handleRegister">
        <div class="field">
          <label>昵称</label>
          <input v-model="nickname" type="text" placeholder="请输入昵称" required />
        </div>
        <div class="field">
          <label>邮箱</label>
          <input v-model="email" type="email" placeholder="请输入邮箱" required />
        </div>
        <div class="field">
          <label>密码</label>
          <input v-model="password" type="password" placeholder="至少 8 位，含字母和数字" required />
        </div>
        <p v-if="error" class="error">{{ error }}</p>
        <button type="submit" :disabled="loading" class="btn-primary">
          {{ loading ? '注册中...' : '注册' }}
        </button>
      </form>
      <p class="link">已有账号？<router-link to="/login">登录</router-link></p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { authApi } from '@/api/auth'

const router = useRouter()
const nickname = ref('')
const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

async function handleRegister() {
  error.value = ''
  if (password.value.length < 8 || !/[A-Za-z]/.test(password.value) || !/\d/.test(password.value)) {
    error.value = '密码至少 8 位，需包含字母和数字'
    return
  }
  loading.value = true
  try {
    await authApi.register({ nickname: nickname.value, email: email.value, password: password.value })
    router.push('/login')
  } catch (e: any) {
    const detail = e.response?.data?.detail
    if (Array.isArray(detail)) {
      error.value = detail.map((d: any) => d.msg).join('；')
    } else {
      error.value = typeof detail === 'string' ? detail : '注册失败，请重试'
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh; display: flex; align-items: center;
  justify-content: center; background: var(--bg-primary);
}
.auth-card {
  background: var(--bg-card); border-radius: var(--radius-card);
  padding: var(--space-8); width: 360px; display: flex;
  flex-direction: column; gap: var(--space-4);
}
h1 { color: var(--color-primary); text-align: center; font-size: 1.5rem; }
.field { display: flex; flex-direction: column; gap: var(--space-1); }
.field label { font-size: 0.875rem; color: var(--text-secondary); }
.field input {
  padding: var(--space-2) var(--space-3); background: var(--surface-mid);
  border: 1px solid var(--border); border-radius: var(--radius-sm);
  color: var(--text-primary); font-size: 1rem;
}
.error { color: var(--color-danger); font-size: 0.875rem; }
.btn-primary {
  width: 100%; padding: var(--space-3); background: var(--color-primary);
  color: #fff; border: none; border-radius: var(--radius-sm);
  font-size: 1rem; cursor: pointer;
}
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
.link { text-align: center; font-size: 0.875rem; color: var(--text-secondary); }
.link a { color: var(--color-primary); }
</style>
