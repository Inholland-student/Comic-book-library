import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

// dev: proxy /api to flask; docker passes backend url via env
const backendProxyTarget =
  process.env.BACKEND_PROXY_TARGET ||
  process.env.VITE_BACKEND_PROXY_TARGET ||
  'http://127.0.0.1:5000'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    strictPort: false,
    watch: {
      usePolling: true
    },
    proxy: {
      '/api': {
        target: backendProxyTarget,
        changeOrigin: true
      }
    }
  }
})
