import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { useAuthStore } from './stores/auth'
import './style.css'

const app = createApp(App)
const pinia = createPinia()
app.use(pinia)
app.use(router)

// 优先从 Android JSBridge 同步 Token（WebView 环境）。
// 必须在 app.mount() 之前执行，因为 App.vue 的 onMounted 晚于子组件 Home.vue 的 onMounted，
// 若放在 App.vue 中，fetchDramas() 会在 token 同步前发出请求，导致未认证。
const auth = useAuthStore()
const synced = auth.syncTokenFromNative()
console.log(`[main.ts] syncTokenFromNative=${synced}, token=${localStorage.getItem('access_token')?.slice(0, 10) || 'null'}...`)

app.mount('#app')
