import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// En desarrollo, todo lo que empiece con /api se manda a Flask (puerto 5000),
// así no hay problemas de CORS.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: { "/api": "http://127.0.0.1:5000" },
  },
});
