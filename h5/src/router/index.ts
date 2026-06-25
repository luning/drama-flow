import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  { path: '/login', name: 'Login', component: () => import('@/pages/Login.vue'), meta: { public: true } },
  { path: '/register', name: 'Register', component: () => import('@/pages/Register.vue'), meta: { public: true } },
  { path: '/', name: 'Home', component: () => import('@/pages/Home.vue') },
  { path: '/detail/:id', name: 'Detail', component: () => import('@/pages/Detail.vue') },
  { path: '/drama/:id/episode/:ep', name: 'Player', component: () => import('@/pages/Player.vue') },
  { path: '/history', name: 'History', component: () => import('@/pages/History.vue') },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

router.beforeEach((to) => {
  const hasToken = !!localStorage.getItem('access_token')
  if (!to.meta.public && !hasToken) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }
  if (to.meta.public && hasToken) {
    return { path: '/' }
  }
})

export default router
