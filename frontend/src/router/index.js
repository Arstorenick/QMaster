import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Index',
    component: () => import('../views/IndexView.vue'),
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/LoginView.vue'),
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/RegisterView.vue'),
  },
  {
    path: '/home',
    name: 'Home',
    component: () => import('../views/HomeView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/display/:id',
    name: 'Display',
    component: () => import('../views/DisplayView.vue'),
  },
  {
    path: '/template/:id',
    name: 'Template',
    component: () => import('../views/TemplateView.vue'),
  },
  {
    path: '/thankyou',
    name: 'ThankYou',
    component: () => import('../views/ThankYouView.vue'),
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('../views/ProfileView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/departments',
    name: 'Departments',
    component: () => import('../views/DepartmentView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/tasks',
    name: 'Tasks',
    component: () => import('../views/TasksView.vue'),
    meta: { requiresAuth: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to, from, next) => {
  const { useAuthStore } = await import('../stores/auth')
  const auth = useAuthStore()

  // Fetch user if not already loaded
  if (!auth.isLoggedIn && !auth.loading) {
    try { await auth.fetchMe() } catch {}
  }

  // Redirect creators/super admins from public pages to /home
  // Redirect respondents to /tasks
  const publicPaths = ['/', '/login', '/register']
  if (publicPaths.includes(to.path)) {
    if (auth.isCreator) return next('/home')
    if (auth.isLoggedIn) return next('/tasks')
  }

  // Require auth for protected routes
  if (to.meta.requiresAuth && !auth.isLoggedIn) {
    return next('/login')
  }

  // Only creators/super admins can access /home
  if (to.path === '/home' && !auth.isCreator) {
    return next('/')
  }

  next()
})

export default router
