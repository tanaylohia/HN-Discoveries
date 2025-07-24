import { defineConfig } from 'vite';

export default defineConfig({
    root: '.',
    build: {
        outDir: 'dist',
    },
    server: {
        port: 3000,
        open: true,
        // Proxy to backend server
        proxy: {
            '/reports': {
                target: 'http://localhost:8080',
                changeOrigin: true,
            },
            '/api': {
                target: 'http://localhost:8080',
                changeOrigin: true,
            }
        }
    }
});