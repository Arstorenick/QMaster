<template>
  <div class="auth-page">
    <div class="auth-card card">
      <div class="auth-brand">
        <img src="/logo.png" alt="QMaster" class="logo-icon-img" />
        <h2>注册QMaster</h2>
        <p class="text-secondary">创建账号，开始使用</p>
      </div>
      <form @submit.prevent="handleRegister" class="auth-form">
        <div class="form-group">
          <label>账号</label>
          <input v-model="form.username" class="input" placeholder="请输入6-20位字母或数字" autocomplete="username" />
        </div>
        <div class="form-group">
          <label>用户名</label>
          <input v-model="form.display_name" class="input" placeholder="请输入真实姓名" />
        </div>
        <div class="form-group">
          <label>密码</label>
          <input v-model="form.password" class="input" type="password" placeholder="8-20位，支持大小写字母、数字及特殊符号" autocomplete="new-password" />
        </div>
        <div class="form-group">
          <label>确认密码</label>
          <input v-model="form.confirmPassword" class="input" type="password" placeholder="再次输入密码" autocomplete="new-password" />
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

const form = reactive({ username: '', display_name: '', password: '', confirmPassword: '' })
const loading = ref(false)
const error = ref('')

async function handleRegister() {
  error.value = ''
  if (!form.username.trim()) { error.value = '请输入账号'; return }
  if (form.username.length < 6 || form.username.length > 20) { error.value = '请输入正确长度的账号'; return }
  if (!/^[a-zA-Z0-9]+$/.test(form.username)) { error.value = '账号仅允许使用字母和数字，不可包含其他符号'; return }
  if (form.password.length < 8 || form.password.length > 20) { error.value = '请输入正确的密码'; return }
  if (form.password !== form.confirmPassword) { error.value = '两次输入的密码不一致'; return }
  loading.value = true
  try {
    await auth.register(form.username.trim(), '', form.password, 3)
    router.push('/tasks')
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
