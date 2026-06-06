import { useState, createContext, useContext, useCallback, ReactNode } from 'react';

interface Toast { id: number; message: string; type: 'success' | 'error' | 'info' | 'warning'; }
interface ToastContextType { addToast: (message: string, type?: Toast['type']) => void; }

const ToastContext = createContext<ToastContextType>({ addToast: () => {} });
export const useToast = () => useContext(ToastContext);

let toastIdCounter = 0;

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const addToast = useCallback((message: string, type: Toast['type'] = 'success') => {
    const id = ++toastIdCounter;
    setToasts(prev => [...prev, { id, message, type }]);
    setTimeout(() => setToasts(prev => prev.filter(t => t.id !== id)), 4000);
  }, []);

  const icons = { success: '✅', error: '❌', info: 'ℹ', warning: '⚠' };
  const colors = {
    success: 'bg-status-green text-white',
    error: 'bg-status-red text-white',
    info: 'bg-navy-700 text-white',
    warning: 'bg-status-orange text-white',
  };

  return (
    <ToastContext.Provider value={{ addToast }}>
      {children}
      <div className="fixed top-16 left-1/2 -translate-x-1/2 z-50 space-y-2 pointer-events-none w-full max-w-sm px-4 print:hidden">
        {toasts.map(t => (
          <div key={t.id} className={`flex items-center gap-2 px-4 py-3 rounded-xl shadow-xl text-sm font-semibold pointer-events-auto ${colors[t.type]}`}>
            <span>{icons[t.type]}</span>
            <span className="flex-1">{t.message}</span>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}
