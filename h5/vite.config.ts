import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      // Design system single source of truth — import from anywhere with @design/
      '@design': resolve(__dirname, '../design-system'),
    },
  },
  css: {
    // Ensure Vite resolves @import in CSS to the design-system directory
    preprocessorOptions: {},
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
