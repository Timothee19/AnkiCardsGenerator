import { useState, useRef, useEffect } from 'react';
import { Terminal, ChevronUp, ChevronDown } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface TerminalDrawerProps {
  logs: string[];
}

export function TerminalDrawer({ logs }: TerminalDrawerProps) {
  const [isOpen, setIsOpen] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isOpen && endRef.current) {
      endRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs, isOpen]);

  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 flex flex-col items-center pointer-events-none">
      
      {/* Toggle Button */}
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className="pointer-events-auto bg-surface-container-highest border border-surface-container-low text-on-surface-variant hover:text-primary hover:bg-surface-container-low transition-colors px-4 py-2 rounded-t-xl shadow-[0_-4px_10px_rgba(0,0,0,0.05)] flex items-center gap-2"
      >
        <Terminal size={16} />
        <span className="text-xs font-bold uppercase tracking-wider">Terminal Logs</span>
        {isOpen ? <ChevronDown size={16} /> : <ChevronUp size={16} />}
      </button>

      {/* Drawer Content */}
      <AnimatePresence>
        {isOpen && (
          <motion.div 
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 250, opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="w-full bg-black/90 backdrop-blur-xl border-t border-white/10 pointer-events-auto overflow-hidden flex flex-col"
          >
            <div className="flex-1 overflow-y-auto p-4 font-mono text-[11px] leading-relaxed text-neutral-300 space-y-1.5 scrollbar-thin scrollbar-thumb-neutral-700 scrollbar-track-transparent">
              {logs.map((log, index) => (
                <div key={index} className="flex gap-2">
                  <span className="text-primary select-none opacity-50">&gt;</span>
                  <span>{log}</span>
                </div>
              ))}
              {logs.length === 0 && (
                <div className="text-neutral-500 italic">En attente des événements système...</div>
              )}
              <div ref={endRef} />
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
