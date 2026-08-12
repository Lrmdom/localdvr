import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    allowedHosts: true,
    proxy: {
      '/api': {
        target: 'http://recorder:8000', // Nome do serviço no docker-compose
        changeOrigin: true,
        secure: false,
        timeout: 0,
        proxyTimeout: 0,
      }
    }
  },
  build: {
    outDir: 'dist',
  },
})
