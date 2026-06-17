<template>
  <div class="auth-page">
    <div class="auth-card card">
      <div class="auth-brand">
        <img src="/logo.png" alt="QMaster" class="logo-icon-img" />
        <h2>注册 QMaster</h2>
        <p class="text-secondary">创建账号，开始使用</p>
      </div>
      <form @submit.prevent="handleRegister" class="auth-form">
        <div class="form-group">
          <label>用户名</label>
          <input v-model="form.username" class="input" placeholder="3-20 位字母数字" autocomplete="username" />
        </div>
        <div class="form-group">
          <label>邮箱（选填）</label>
          <input v-model="form.email" class="input" type="email" placeholder="your@email.com" autocomplete="email" />
        </div>
        <div class="form-group">
          <label>密码</label>
          <input v-model="form.password" class="input" type="password" placeholder="至少 6 位" autocomplete="new-password" />
        </div>
        <div class="form-group">
          <label>角色</label>
          <select v-model="form.role" class="input">
            <option :value="3">用户</option>
            <option :value="2">管理员</option>
          </select>
        </div>
        <p v-if="error" class="form-error">{{ error }}</p>
        <button type="submit" class="btn btn-primary btn-lg btn-block" :disabled="loading">
          {{ loading ? '注册中...' : '注册' }}
        </button>
      </form>
      <p class="auth-footer text-center">
        已有账号？<router-link to="/login">立即登录</router-link>
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

const form = reactive({ username: '', email: '', password: '', role: 3 })
const loading = ref(false)
const error = ref('')

async function handleRegister() {
  error.value = ''
  if (form.password.length < 6) {
    error.value = '密码至少 6 位'
    return
  }
  loading.value = true
  try {
    await auth.register(form.username, form.email, form.password, form.role)
    if (form.role === 2) {
      router.push('/home')
    } else {
      router.push('/')
    }
  } catch (e) {
    error.value = e.response?.data?.username?.[0] || e.response?.data?.password?.[0] || '注册失败'
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
