import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      strategies: 'injectManifest',
      srcDir: 'src',
      filename: 'sw.ts',
      includeAssets: ['favicon.svg', 'icons.svg'],
      manifest: {
        name: 'LocalDVR Viewer',
        short_name: 'LocalDVR',
        theme_color: '#1a1a1a',
        background_color: '#1a1a1a',
        display: 'standalone',
        icons: [
          {
            src: 'favicon.svg',
            sizes: 'any',
            type: 'image/svg+xml'
          }
        ]
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,svg,png}']
      }
    })
  ],
  server: {
    host: '0.0.0.0',
    port: 5173,
    allowedHosts: true, // Permite acessos via IP do Tailscale / Domínio externo
    proxy: {
      '/api': {
        target: 'http://recorder:8000',
        changeOrigin: true,
      }
    }
  },
  build: {
    outDir: 'dist',
  },
})
