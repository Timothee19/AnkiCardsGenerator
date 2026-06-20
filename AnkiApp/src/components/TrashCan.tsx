import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface Deck {
  id: string;
  title: string;
  color: string;
  position: number;
}

interface TrashCanProps {
  isDeleting: boolean;
  trashedBooks: Deck[];
  onRestore: (id: string) => void;
}

export const TrashCan: React.FC<TrashCanProps> = ({ isDeleting, trashedBooks, onRestore }) => {
  return (
    <div className="relative w-48 h-64">
      {/* Drop Shadow */}
      <div className="absolute -bottom-2 left-1/2 -translate-x-1/2 w-32 h-6 bg-black/15 blur-[6px] rounded-full"></div>

      {/* --- LAYER 1: BACK SVG (Lid + Inner Hole) --- */}
      <svg viewBox="0 0 100 130" className="w-full h-full drop-shadow-lg overflow-visible absolute inset-0 z-0 pointer-events-none">
        {/* Lid */}
        <motion.g 
          id="lid" 
          initial={{ rotate: 0, y: 0 }}
          animate={isDeleting ? { rotate: -100, x: -15, y: -25 } : { rotate: 0, x: 0, y: 0 }}
          transition={{ type: "spring", stiffness: 250, damping: 15 }}
          style={{ originX: "14px", originY: "30px" }}
        >
          <ellipse cx="50" cy="28" rx="38" ry="14" fill="#D1D5DB" stroke="#1F2937" strokeWidth="4" />
          <path d="M 35 14 L 35 5 L 65 5 L 65 14" fill="none" stroke="#1F2937" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" />
        </motion.g>

        {/* Back rim (inner hole) - darker for depth */}
        <ellipse cx="50" cy="30" rx="36" ry="12" fill="#111827" stroke="#1F2937" strokeWidth="2" />
      </svg>

      {/* --- LAYER 2: TRASHED BOOKS (Inside the hole) --- */}
      <div className="absolute top-[35px] left-1/2 -translate-x-1/2 w-[90px] h-[40px] z-10 flex flex-wrap-reverse gap-1 justify-center items-end pointer-events-auto">
        <AnimatePresence>
          {trashedBooks.map((book, idx) => (
            <motion.div
              key={book.id}
              onClick={(e) => { e.stopPropagation(); onRestore(book.id); }}
              className="cursor-pointer hover:scale-125 transition-transform shadow-lg relative rounded-sm overflow-hidden"
              style={{ 
                width: '18px', 
                height: '40px', 
                backgroundColor: book.color,
                zIndex: trashedBooks.length - idx
              }}
              animate={{ rotate: (idx % 2 === 0 ? 1 : -1) * (10 + (idx * 5) % 20) }}
            >
              <div className="absolute inset-y-0 left-0.5 w-[1px] bg-white/30"></div>
              <div className="absolute inset-y-0 right-0 w-0.5 bg-black/20"></div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      {/* --- LAYER 3: FRONT SVG (Body) --- */}
      <svg viewBox="0 0 100 130" className="w-full h-full overflow-visible absolute inset-0 z-20 pointer-events-none">
        <defs>
          <linearGradient id="cartoon-highlight" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#9CA3AF" />
            <stop offset="10%" stopColor="#9CA3AF" />
            <stop offset="15%" stopColor="#D1D5DB" />
            <stop offset="35%" stopColor="#D1D5DB" />
            <stop offset="40%" stopColor="#9CA3AF" />
            <stop offset="100%" stopColor="#9CA3AF" />
          </linearGradient>
        </defs>
        <g id="body-front">
          {/* Main Body (Conical) with mathematically perfect top and bottom ellipse curves */}
          <path 
            d="M 14 30 C 14 36.62 30.12 42 50 42 C 69.88 42 86 36.62 86 30 L 75 115 C 75 117.76 63.8 120 50 120 C 36.2 120 25 117.76 25 115 Z" 
            fill="url(#cartoon-highlight)" 
            stroke="#1F2937" 
            strokeWidth="4" 
            strokeLinejoin="round" 
          />
          
          {/* Vertical Ribs */}
          <path d="M 35 44 L 40 116 M 50 46 L 50 119 M 65 44 L 60 116" stroke="#4B5563" strokeWidth="4" strokeLinecap="round" />
        </g>
      </svg>
    </div>
  );
};
