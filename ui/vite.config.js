import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// The API runs on localhost:8000; the dev server proxies to it so the browser sees one origin.
export default defineConfig({
  plugins: [react()],
  server: { host: "127.0.0.1", port: 5173, proxy: { "/api": "http://127.0.0.1:8000", "/charts": "http://127.0.0.1:8000" } },
});
