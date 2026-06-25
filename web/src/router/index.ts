import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  { path: '/login', component: () => import('@/pages/Login.vue'), meta: { public: true } },
  { path: '/register', component: () => import('@/pages/Register.vue'), meta: { public: true } },
  { path: '/', component: () => import('@/pages/Home.vue') },
  { path: '/drama/:id', component: () => import('@/pages/Detail.vue') },
  { path: '/drama/:id/episode/:ep', component: () => import('@/pages/Player.vue') },
  { path: '/history', component: () => import('@/pages/History.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (!to.meta.public && !auth.isLoggedIn) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }
  if (to.meta.public && auth.isLoggedIn) {
    return { path: '/' }
  }
})

export default router
