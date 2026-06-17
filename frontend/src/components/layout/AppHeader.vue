<template>
  <header class="app-header">
    <div class="header-inner">
      <div class="header-left">
        <router-link :to="auth.isLoggedIn ? '/home' : '/'" class="logo">
          <img src="/QMaster.png" alt="QMaster" class="logo-img" />
        </router-link>
        <nav class="nav-links" v-if="auth.isLoggedIn && auth.isCreator">
          <router-link to="/home" class="nav-link">我的问卷</router-link>
          <router-link to="/departments" class="nav-link">我的部门</router-link>
        </nav>
        <nav class="nav-links" v-if="auth.isLoggedIn && !auth.isCreator">
          <router-link to="/tasks" class="nav-link">我的任务</router-link>
        </nav>
      </div>

      <div class="header-right">
        <template v-if="auth.isLoggedIn">
          <router-link to="/profile" class="header-user-link header-name">{{ auth.user?.display_name || auth.user?.username }}</router-link>
          <a class="header-user-link header-logout" @click="handleLogout">退出</a>
        </template>
        <template v-else>
          <router-link to="/login" class="header-user-link header-name">登录</router-link>
          <router-link to="/register" class="btn btn-primary header-btn">注册</router-link>
        </template>
      </div>
    </div>
  </header>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'

const auth = useAuthStore()
const router = useRouter()

auth.fetchMe()

async function handleLogout() {
  await auth.logout()
  router.push('/')
}
</script>

<style scoped>
.app-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: var(--header-height);
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--color-border-light);
  z-index: 100;
}
.header-inner {
  padding: 0 var(--spacing-lg);
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.header-left {
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
}
.logo {
  display: flex;
  align-items: center;
  text-decoration: none;
}
.logo-img {
  height: 32px;
  width: auto;
}
.nav-links {
  display: flex;
  gap: var(--spacing-sm);
}
.nav-link {
  padding: 6px 14px;
  font-size: 15px;
  color: var(--color-text-secondary);
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
}
.nav-link:hover,
.nav-link.router-link-active {
  color: var(--color-primary);
  background: var(--color-primary-light);
}
.header-right {
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
}
.header-user-link {
  font-size: 15px;
  color: var(--color-text-secondary);
  cursor: pointer;
  text-decoration: none;
  transition: color var(--transition-fast);
}
.header-name:hover {
  color: var(--color-text-primary);
}
.header-logout:hover {
  color: var(--color-danger);
}
.header-btn {
  font-size: 15px !important;
  padding: 6px 18px !important;
  color: #fff !important;
}
.header-btn:hover {
  color: #fff !important;
}
.user-name {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}
</style>
