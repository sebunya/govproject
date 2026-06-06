import { useState, createContext, useContext, useCallback, ReactNode, useEffect } from 'react';

interface Toast {
  id: number;
  message: string;
  type: 'success' | 'error' | 'info' | 'warning';
  duration?: number;
}
interface ToastContextType {
  addToast: (message: string, type?: Toast['type'], duration?: number) => void;
}

const ToastContext = createContext<ToastContextType>({ addToast: () => {} });
export const useToast = () => useContext(ToastContext);

let toastIdCounter = 0;

const ICONS: Record<Toast['type'], string> = {
  success: '✓',
  error: '✕',
  info: 'i',
  warning: '!',
};

const COLORS: Record<Toast['type'], string> = {
  success: 'bg-status-green text-white',
  error: 'bg-status-red text-white',
  info: 'bg-navy-700 text-white',
  warning: 'bg-status-orange text-white',
};

const ICON_BG: Record<Toast['type'], string> = {
  success: 'bg-white/20',
  error: 'bg-white/20',
  info: 'bg-white/20',
  warning: 'bg-white/20',
};

function ToastItem({ toast, onDismiss }: { toast: Toast; onDismiss: (id: number) => void }) {
  const [visible, setVisible] = useState(false);
  const duration = toast.duration ?? 4000;

  useEffect(() => {
    // Small delay to trigger CSS transition
    const show = requestAnimationFrame(() => setVisible(true));
    const timer = setTimeout(() => {
      setVisible(false);
      setTimeout(() => onDismiss(toast.id), 200);
    }, duration);
    return () => { cancelAnimationFrame(show); clearTimeout(timer); };
  }, [toast.id, duration, onDismiss]);

  return (
    <div
      role={toast.type === 'error' ? 'alert' : 'status'}
      aria-live={toast.type === 'error' ? 'assertive' : 'polite'}
      aria-atomic="true"
      className={`flex items-start gap-3 px-4 py-3 rounded-xl shadow-xl text-sm font-medium pointer-events-auto
        transition-all duration-200 ${COLORS[toast.type]}
        ${visible ? 'opacity-100 translate-y-0' : 'opacity-0 -translate-y-2'}`}
    >
      <span
        className={`w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0 mt-0.5 ${ICON_BG[toast.type]}`}
        aria-hidden="true"
      >
        {ICONS[toast.type]}
      </span>
      <span className="flex-1 leading-snug">{toast.message}</span>
      <button
        onClick={() => { setVisible(false); setTimeout(() => onDismiss(toast.id), 200); }}
        className="opacity-70 hover:opacity-100 transition-opacity flex-shrink-0 ml-1"
        aria-label="Dismiss notification"
      >
        <svg width="12" height="12" viewBox="0 0 12 12" fill="currentColor" aria-hidden="true">
          <path d="M1 1l10 10M11 1L1 11" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"/>
        </svg>
      </button>
    </div>
  );
}

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const addToast = useCallback((message: string, type: Toast['type'] = 'success', duration?: number) => {
    const id = ++toastIdCounter;
    setToasts(prev => [...prev.slice(-4), { id, message, type, duration }]);
  }, []);

  const dismiss = useCallback((id: number) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  }, []);

  return (
    <ToastContext.Provider value={{ addToast }}>
      {children}
      {/* Desktop: top-center / Mobile: bottom (above install prompt) */}
      <div
        className="fixed left-1/2 -translate-x-1/2 z-[65] space-y-2 pointer-events-none w-full max-w-sm px-4 print:hidden
                   top-20 sm:top-16"
        aria-label="Notifications"
      >
        {toasts.map(t => (
          <ToastItem key={t.id} toast={t} onDismiss={dismiss} />
        ))}
      </div>
    </ToastContext.Provider>
  );
}
