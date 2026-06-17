<template>
  <div class="auth-page">
    <div class="auth-card card">
      <div class="auth-brand">
        <img src="/logo.png" alt="QMaster" class="logo-icon-img" />
        <h2>登录到QMaster</h2>
        <p class="text-secondary">欢迎回来</p>
      </div>
      <form @submit.prevent="handleLogin" class="auth-form">
        <div class="form-group">
          <label>用户名</label>
          <input v-model="form.username" class="input" placeholder="请输入用户名" autocomplete="username" />
        </div>
        <div class="form-group">
          <label>密码</label>
          <input v-model="form.password" class="input" type="password" placeholder="请输入密码" autocomplete="current-password" />
        </div>
        <p v-if="error" class="form-error">{{ error }}</p>
        <button type="submit" class="btn btn-primary btn-lg btn-block" :disabled="loading">
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </form>
      <p class="auth-footer text-center">
        还没有账号？<router-link to="/register">立即注册</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()

const form = reactive({ username: '', password: '' })
const loading = ref(false)
const error = ref('')

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(form.username, form.password)
    router.push(auth.isCreator ? '/home' : '/')
  } catch (e) {
    error.value = e.response?.data?.detail || e.response?.data?.non_field_errors?.[0] || '登录失败'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  min-height: calc(100vh - var(--header-height));
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-lg);
}
.auth-card {
  width: 100%;
  max-width: 400px;
  padding: var(--spacing-2xl);
}
.auth-brand {
  text-align: center;
  margin-bottom: var(--spacing-xl);
}
.logo-icon-img {
  height: 72px;
  width: auto;
  margin-bottom: var(--spacing-sm);
}
.auth-brand h2 {
  margin-top: var(--spacing-md);
}
.auth-form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}
.form-group label {
  display: block;
  font-size: var(--font-size-sm);
  font-weight: 500;
  margin-bottom: var(--spacing-xs);
  color: var(--color-text-primary);
}
.form-error {
  color: var(--color-danger);
  font-size: var(--font-size-xs);
}
.btn-block {
  width: 100%;
}
.auth-footer {
  margin-top: var(--spacing-lg);
  font-size: var(--font-size-sm);
}
</style>
