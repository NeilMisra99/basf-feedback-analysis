import path from "path";
import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [
    react({
      // Optimize JSX runtime
      jsxRuntime: "automatic",
    }),
    tailwindcss(),
  ],
  // Define environment variables for browser
  define: {
    "process.env.REACT_APP_API_URL": JSON.stringify(
      process.env.REACT_APP_API_URL
    ),
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  // Optimize dependency pre-bundling
  optimizeDeps: {
    include: [
      "react",
      "react-dom",
      "react-hook-form",
      "@hookform/resolvers/zod",
      "zod",
      "axios",
      "lucide-react",
    ],
    exclude: ["@vitejs/plugin-react"],
  },
  server: {
    host: true,
    port: 3000,
    // Enable HTTP/2 for development and optimize HMR
    hmr: {
      overlay: true,
    },
    proxy: {
      "/api": {
        target: process.env.REACT_APP_API_URL || "http://localhost:5001",
        changeOrigin: true,
        secure: false,
      },
    },
  },
  preview: {
    host: true,
    port: 3000,
  },
  build: {
    outDir: "dist",
    sourcemap: false,
    // Use esbuild for minification (faster and compatible)
    minify: "esbuild",
    // Chunk size warning limit
    chunkSizeWarningLimit: 1000,
    rollupOptions: {
      output: {
        // Enhanced manual chunks for better caching
        manualChunks: {
          vendor: ["react", "react-dom"],
          ui: [
            "@radix-ui/react-label",
            "@radix-ui/react-select",
            "@radix-ui/react-slot",
            "@radix-ui/react-tabs",
            "lucide-react",
          ],
          forms: ["react-hook-form", "@hookform/resolvers", "zod"],
          utils: [
            "axios",
            "clsx",
            "tailwind-merge",
            "class-variance-authority",
          ],
        },
        // Optimize chunk file names for caching
        chunkFileNames: (chunkInfo) => {
          const facadeModuleId = chunkInfo.facadeModuleId
            ? chunkInfo.facadeModuleId
                .split("/")
                .pop()
                ?.replace(".tsx", "")
                .replace(".ts", "") || "chunk"
            : "chunk";
          return `js/${facadeModuleId}-[hash].js`;
        },
        assetFileNames: (assetInfo) => {
          const fileName = assetInfo.name || "asset";
          if (/\.(png|jpe?g|svg|gif|tiff|bmp|ico)$/i.test(fileName)) {
            return `img/[name]-[hash][extname]`;
          }
          if (/\.(css)$/i.test(fileName)) {
            return `css/[name]-[hash][extname]`;
          }
          return `assets/[name]-[hash][extname]`;
        },
      },
    },
  },
});
