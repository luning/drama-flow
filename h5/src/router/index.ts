import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'Home', component: () => import('@/pages/Home.vue') },
  { path: '/detail/:id', name: 'Detail', component: () => import('@/pages/Detail.vue') },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

export default router
