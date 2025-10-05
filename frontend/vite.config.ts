import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/videos': 'http://localhost:8000',
      '/process': 'http://localhost:8000',
      '/manual': 'http://localhost:8000',
      '/export': 'http://localhost:8000',
    },
  },
})
