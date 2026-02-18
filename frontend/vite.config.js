import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    // Proxy /api calls to the FastAPI backend so CORS is never an issue
    proxy: {
      '/api': 'http://localhost:8000'
    }
  }
})
