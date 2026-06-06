import { useState, useEffect } from 'react';

interface BeforeInstallPromptEvent extends Event {
  prompt(): Promise<void>;
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>;
}

function NileLogo() {
  return (
    <svg width="40" height="40" viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" className="flex-shrink-0">
      <rect width="36" height="36" rx="7" fill="#1A1A1A"/>
      <rect x="0" y="29" width="36" height="7" rx="0" fill="#C8102E"/>
      <text x="18" y="25" fontFamily="system-ui,sans-serif" fontWeight="800" fontSize="22"
            fill="#F5C000" textAnchor="middle" dominantBaseline="auto">N</text>
    </svg>
  );
}

export default function InstallPrompt() {
  const [prompt, setPrompt] = useState<BeforeInstallPromptEvent | null>(null);
  const [dismissed, setDismissed] = useState(false);
  const [installed, setInstalled] = useState(false);

  useEffect(() => {
    if (window.matchMedia('(display-mode: standalone)').matches) { setInstalled(true); return; }
    if (sessionStorage.getItem('pwa-prompt-dismissed')) { setDismissed(true); return; }

    const handler = (e: Event) => { e.preventDefault(); setPrompt(e as BeforeInstallPromptEvent); };
    window.addEventListener('beforeinstallprompt', handler);
    window.addEventListener('appinstalled', () => setInstalled(true));
    return () => window.removeEventListener('beforeinstallprompt', handler);
  }, []);

  const handleInstall = async () => {
    if (!prompt) return;
    await prompt.prompt();
    const { outcome } = await prompt.userChoice;
    if (outcome === 'accepted') setInstalled(true);
    setPrompt(null);
  };

  const handleDismiss = () => {
    sessionStorage.setItem('pwa-prompt-dismissed', '1');
    setDismissed(true);
    setPrompt(null);
  };

  if (!prompt || dismissed || installed) return null;

  return (
    <div role="banner" aria-label="Install NileGov app" className="fixed bottom-0 left-0 right-0 z-50 pb-safe animate-slide-up">
      <div className="bg-navy-700 border-t-4 border-gold-500 shadow-nav">
        {/* Uganda flag stripe */}
        <div className="flex" style={{ height: '3px' }} aria-hidden="true">
          <div className="flex-1 bg-navy-900" />
          <div className="flex-1 bg-gold-500" />
          <div className="flex-1 bg-ug-red" />
        </div>
        <div className="max-w-2xl mx-auto px-4 py-3 flex items-center gap-3">
          <NileLogo />
          <div className="flex-1 min-w-0">
            <div className="text-white text-sm font-bold leading-tight">Install NileGov Stack</div>
            <div className="text-gray-300 text-xs mt-0.5">Add to home screen for offline access &amp; faster loading</div>
          </div>
          <div className="flex items-center gap-2 flex-shrink-0">
            <button onClick={handleDismiss} className="text-gray-300 hover:text-white text-xs px-2 py-1.5 rounded transition-colors">
              Not now
            </button>
            {/* Uganda yellow button — must use dark text */}
            <button onClick={handleInstall} className="bg-gold-500 hover:bg-gold-600 text-gray-900 text-xs font-bold px-3 py-1.5 rounded-lg transition-colors">
              Install
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
