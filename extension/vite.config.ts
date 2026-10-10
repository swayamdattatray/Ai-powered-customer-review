import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';
import { copyFileSync, mkdirSync, existsSync } from 'fs';

// Custom plugin to copy manifest.json into dist
function copyManifestPlugin() {
  return {
    name: 'copy-manifest',
    closeBundle() {
      if (!existsSync('dist')) {
        mkdirSync('dist', { recursive: true });
      }
      copyFileSync('manifest.json', 'dist/manifest.json');
      
      // Ensure icons directory exists and copy icons
      if (!existsSync('dist/icons')) {
        mkdirSync('dist/icons', { recursive: true });
      }
      for (const size of [16, 48, 128]) {
        const iconPath = `icons/icon${size}.png`;
        if (existsSync(iconPath)) {
          copyFileSync(iconPath, `dist/icons/icon${size}.png`);
        }
      }
    }
  };
}

export default defineConfig({
  plugins: [react(), copyManifestPlugin()],
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    rollupOptions: {
      input: {
        sidepanel: resolve(__dirname, 'src/sidepanel/index.html'),
        dashboard: resolve(__dirname, 'src/dashboard/index.html'),
        service_worker: resolve(__dirname, 'src/background/service_worker.ts'),
        content_script: resolve(__dirname, 'src/content/content_script.ts'),
      },
      output: {
        entryFileNames: (chunkInfo) => {
          if (chunkInfo.name === 'service_worker') return 'service_worker.js';
          if (chunkInfo.name === 'content_script') return 'content_script.js';
          return 'assets/[name]-[hash].js';
        },
        chunkFileNames: 'assets/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash].[ext]'
      }
    }
  }
});
