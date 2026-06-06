import { useState, useEffect } from 'react';

export default function OfflineBanner() {
  const [offline, setOffline] = useState(!navigator.onLine);
  const [wasOffline, setWasOffline] = useState(false);
  const [showBackOnline, setShowBackOnline] = useState(false);

  useEffect(() => {
    const goOffline = () => { setOffline(true); setWasOffline(true); };
    const goOnline  = () => {
      setOffline(false);
      if (wasOffline) {
        setShowBackOnline(true);
        setTimeout(() => setShowBackOnline(false), 3000);
      }
    };
    window.addEventListener('offline', goOffline);
    window.addEventListener('online', goOnline);
    return () => {
      window.removeEventListener('offline', goOffline);
      window.removeEventListener('online', goOnline);
    };
  }, [wasOffline]);

  if (offline) {
    return (
      <div
        role="alert"
        aria-live="assertive"
        className="fixed top-0 left-0 right-0 z-[70] bg-status-orange text-white text-sm font-semibold
                   px-4 py-2.5 flex items-center justify-center gap-2 text-center"
      >
        <span aria-hidden="true">📡</span>
        You are offline. Some features may be unavailable until connection is restored.
      </div>
    );
  }

  if (showBackOnline) {
    return (
      <div
        role="status"
        aria-live="polite"
        className="fixed top-0 left-0 right-0 z-[70] bg-status-green text-white text-sm font-semibold
                   px-4 py-2.5 flex items-center justify-center gap-2 animate-fade-in"
      >
        <span aria-hidden="true">✓</span>
        Back online
      </div>
    );
  }

  return null;
}
