import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const loading = ref(false)

  const isLoggedIn = computed(() => user.value !== null)
  const isCreator = computed(() => user.value?.role === 1 || user.value?.role === 2)
  const isSuperAdmin = computed(() => user.value?.role === 1 || user.value?.is_superuser)

  async function fetchMe() {
    try {
      const { data } = await api.get('/api/auth/me/')
      user.value = data
    } catch {
      user.value = null
    }
  }

  async function login(username, password) {
    const { data } = await api.post('/api/auth/login/', { username, password })
    user.value = data
    return data
  }

  async function register(username, email, password, role = 3) {
    const { data } = await api.post('/api/auth/register/', { username, email, password, role })
    user.value = data
    return data
  }

  async function logout() {
    await api.post('/api/auth/logout/')
    user.value = null
  }

  return { user, loading, isLoggedIn, isCreator, isSuperAdmin, fetchMe, login, register, logout }
})
