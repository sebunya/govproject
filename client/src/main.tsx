import React, { Suspense } from 'react';
import ReactDOM from 'react-dom/client';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import App from './App';
import './index.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 10_000,
      refetchOnWindowFocus: true,
      refetchOnReconnect: true,
    },
  },
});

// Register PWA service worker
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    // vite-plugin-pwa injects this at build time
    // In dev mode this is a no-op
    import('virtual:pwa-register').then(({ registerSW }) => {
      registerSW({
        onRegistered(r) {
          // Check for updates every hour
          r && setInterval(() => r.update(), 60 * 60 * 1_000);
        },
        onOfflineReady() {
          console.info('[NileGov] App ready for offline use');
        },
      });
    }).catch(() => {
      // Dev mode — PWA module not available, ignore
    });
  });
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Suspense fallback={null}>
          <App />
        </Suspense>
      </BrowserRouter>
    </QueryClientProvider>
  </React.StrictMode>
);
