import path from "path"
import react from "@vitejs/plugin-react"
import { defineConfig } from "vite"

export default defineConfig({
  plugins: [react()],
  resolve: { alias: { "@": path.resolve(__dirname, "./src"), } },
  server: {
    host: true, // Listen on all network interfaces
    port: 5173,
  }
})
