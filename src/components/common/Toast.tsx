import React from 'react';

interface ToastProps {
  message: string | null;
  type?: 'success' | 'info' | 'error';
  onClose: () => void;
}

export const Toast: React.FC<ToastProps> = ({ message, type = 'success', onClose }) => {
  if (!message) return null;

  const bgColors = {
    success: 'bg-[#10b981] text-white',
    info: 'bg-[#00687a] text-white',
    error: 'bg-[#ba1a1a] text-white',
  };

  const icons = {
    success: 'check_circle',
    info: 'info',
    error: 'error',
  };

  return (
    <div className="fixed bottom-20 md:bottom-6 right-6 z-50 animate-bounceIn">
      <div className={`${bgColors[type]} px-4 py-3 rounded-xl shadow-xl flex items-center gap-3 border border-white/20 text-sm font-medium`}>
        <span className="material-symbols-outlined text-[20px]">{icons[type]}</span>
        <span>{message}</span>
        <button 
          onClick={onClose}
          className="ml-2 hover:opacity-75 text-white/80"
        >
          <span className="material-symbols-outlined text-[16px]">close</span>
        </button>
      </div>
    </div>
  );
};
