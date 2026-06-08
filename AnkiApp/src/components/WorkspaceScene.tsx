import { motion, AnimatePresence } from 'framer-motion';
import { useEffect, useState, useRef } from 'react';
import { BookOpen } from 'lucide-react';

export type RobotState = 'idle' | 'reading' | 'generation' | 'bridge_generation' | 'deduplication' | 'transporting' | 'fusion' | 'sort';

interface WorkspaceSceneProps {
  state: RobotState;
  stageProgress: number;
  stageStatusText: string;
  books: any[];
  isSyncing: boolean;
  onBookClick: (id: string) => void;
}

export function WorkspaceScene({ state, stageProgress, stageStatusText, books, isSyncing, onBookClick }: WorkspaceSceneProps) {
  const [dedupMode, setDedupMode] = useState<'fusion' | 'sort' | 'none'>('none');
  const [targetSlot, setTargetSlot] = useState(0);

  // Random slot for library placement
  useEffect(() => {
    if (state === 'transporting') {
      setTargetSlot(Math.floor(Math.random() * 15));
    }
  }, [state]);

  // Deduplication Loop
  useEffect(() => {
    let active = true;
    if (state === 'deduplication') {
      const loop = async () => {
        while (active) {
          setDedupMode(Math.random() > 0.5 ? 'fusion' : 'sort');
          await new Promise(r => setTimeout(r, 2000));
        }
      };
      loop();
    } else if (state === 'fusion') {
      setDedupMode('fusion');
    } else if (state === 'sort') {
      setDedupMode('sort');
    } else {
      setDedupMode('none');
    }
    return () => { active = false; };
  }, [state]);

  const animKey = (state === 'deduplication' || state === 'fusion' || state === 'sort') && dedupMode !== 'none' ? dedupMode : state;

  // Stacks height based on progress
  // Left stack decreases (1 to 0), Right stack increases (0 to 1)
  const leftStackCount = Math.max(0, Math.floor((1 - stageProgress) * 5));
  const rightStackCount = Math.min(5, Math.ceil(stageProgress * 5));

  // --- ANIMATIONS ---
  const robotVariants = {
    idle: { y: [0, -3, 0], scale: 1, x: 0, transition: { repeat: Infinity, duration: 4, ease: "easeInOut" } },
    reading: { y: [0, 2, 0], scale: 1, x: 0, transition: { repeat: Infinity, duration: 2, ease: "easeInOut" } },
    generation: { y: [0, 1, 0], scale: 1, x: 0, transition: { repeat: Infinity, duration: 0.5, ease: "linear" } },
    bridge_generation: { y: [0, 1, 0], scale: 1, x: 0, transition: { repeat: Infinity, duration: 0.5, ease: "linear" } },
    sort: { y: [-1, 1, -1], scale: 1, x: 0, transition: { duration: 2, ease: "easeInOut" } },
    fusion: { y: [-2, 2, -2], scale: 1, x: 0, transition: { duration: 2, ease: "easeInOut" } },
    // Turn back and move towards library
    transporting: { 
      y: 0, 
      x: 150, 
      scale: 0.6, 
      opacity: [1, 1, 0], 
      transition: { duration: 3, ease: "easeInOut", times: [0, 0.8, 1] } 
    }
  };

  const eyesVariants = {
    idle: { x: 0 },
    reading: { x: [-10, 10, -10], transition: { repeat: Infinity, duration: 1.5, ease: "linear" } },
    generation: { x: [0, 2, -2, 0], transition: { repeat: Infinity, duration: 0.8 } },
    bridge_generation: { x: [0, 2, -2, 0], transition: { repeat: Infinity, duration: 0.8 } },
    sort: { x: [-5, 5, -5], transition: { duration: 3 } },
    fusion: { x: 0, scale: [1, 1.2, 1], transition: { duration: 3, times: [0, 0.5, 1] } },
    transporting: { x: 5 }
  };

  const pageTurnVariants = {
    idle: { opacity: 0 },
    reading: {
      opacity: [0, 0, 1, 1, 0, 0],
      x: [0, 0, 0, -35, -35, 0],
      scaleX: [1, 1, 1, 0.1, 0.1, 1],
      transition: { repeat: Infinity, duration: 4, times: [0, 0.6, 0.65, 0.8, 0.81, 1], ease: "easeInOut" }
    },
    default: { opacity: 0 }
  };

  const fusionFlashVariants = {
    fusion: { opacity: [0, 0, 1, 1, 0], scale: [0.5, 0.5, 1.5, 1.5, 0.5], transition: { duration: 3, times: [0, 0.4, 0.5, 0.6, 1] } },
    default: { opacity: 0 }
  };

  const upperArmLeftVariants = {
    idle: { rotate: 0 },
    reading: { rotate: 10 },
    generation: { rotate: 15 },
    bridge_generation: { rotate: 15 },
    sort: { rotate: [0, 30, 0], transition: { duration: 2, times: [0, 0.5, 1] } },
    fusion: { rotate: [0, -24, -24, 0], transition: { duration: 2, times: [0, 0.3, 0.7, 1] } },
    transporting: { rotate: 0, opacity: 0 }
  };

  const forearmLeftVariants = {
    idle: { rotate: 0 },
    reading: { rotate: 15 },
    generation: { rotate: 10 },
    bridge_generation: { rotate: 10 },
    sort: { rotate: [0, 20, 0], transition: { duration: 2, times: [0, 0.5, 1] } },
    fusion: { rotate: [0, -7, -7, 0], transition: { duration: 2, times: [0, 0.3, 0.7, 1] } },
    transporting: { rotate: 0 }
  };
  
  const upperArmRightVariants = {
    idle: { rotate: 0 },
    reading: { 
      rotate: [0, -15, 20, 0],
      transition: { repeat: Infinity, duration: 4, times: [0, 0.6, 0.8, 1], ease: "easeInOut" } 
    },
    generation: { 
      rotate: [0, -5, 0, -5, 0, -5, 0],
      transition: { repeat: Infinity, duration: 1.5, ease: "linear" } 
    },
    bridge_generation: { 
      rotate: [0, -5, 0, -5, 0, -5, 0],
      transition: { repeat: Infinity, duration: 1.5, ease: "linear" } 
    },
    sort: { rotate: [0, -30, 0], transition: { duration: 2, times: [0, 0.5, 1] } },
    fusion: { rotate: [0, 24, 24, 0], transition: { duration: 2, times: [0, 0.3, 0.7, 1] } },
    transporting: { rotate: 0, opacity: 0 }
  };

  const forearmRightVariants = {
    idle: { rotate: 0 },
    reading: { 
      rotate: [0, -10, 15, 0],
      transition: { repeat: Infinity, duration: 4, times: [0, 0.6, 0.8, 1], ease: "easeInOut" } 
    },
    generation: { 
      rotate: [0, 5, 0, 5, 0, 5, 0],
      transition: { repeat: Infinity, duration: 1.5, ease: "linear" } 
    },
    bridge_generation: { 
      rotate: [0, 5, 0, 5, 0, 5, 0],
      transition: { repeat: Infinity, duration: 1.5, ease: "linear" } 
    },
    sort: { rotate: [0, -20, 0], transition: { duration: 2, times: [0, 0.5, 1] } },
    fusion: { rotate: [0, 7, 7, 0], transition: { duration: 2, times: [0, 0.3, 0.7, 1] } },
    transporting: { rotate: 0 }
  };

  const inkVariants = {
    generation: { strokeDashoffset: [60, 0, 60], transition: { repeat: Infinity, duration: 1.5, ease: "linear" } },
    bridge_generation: { strokeDashoffset: [60, 0, 60], transition: { repeat: Infinity, duration: 1.5, ease: "linear" } },
    default: { strokeDashoffset: 60 }
  };

  // Library Shelves Logic
  const shelves = [0, 1, 2]; // 3 shelves

  return (
    <div className="w-full h-full flex flex-col items-center bg-surface-container-lowest relative overflow-hidden rounded-[2rem] border border-outline-variant shadow-sm">
      
      {/* HUD */}
      <div className="absolute top-6 left-1/2 -translate-x-1/2 w-full max-w-lg z-50 flex flex-col items-center pointer-events-none">
        <motion.div 
          key={stageStatusText}
          initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}
          className="bg-white/80 backdrop-blur-xl border border-white px-8 py-3 rounded-2xl shadow-xl mb-4 flex items-center justify-center gap-3"
        >
          <div className="w-2 h-2 rounded-full bg-primary animate-pulse" />
          <p className="text-sm font-extrabold tracking-widest text-on-surface uppercase">
            {stageStatusText || "Système en attente"}
          </p>
        </motion.div>
        
        <div className="w-full h-1.5 bg-surface-container-highest/50 rounded-full overflow-hidden shadow-inner">
          <motion.div className="h-full bg-gradient-to-r from-primary to-secondary"
            initial={{ width: 0 }} animate={{ width: `${stageProgress * 100}%` }}
            transition={{ type: "spring", stiffness: 40, damping: 15 }}
          />
        </div>
      </div>

      {/* 3D SCENE SVG */}
      <svg viewBox="0 0 800 600" className="w-full h-full" preserveAspectRatio="xMidYMax slice">
        
        {/* --- LAYER 1: BACKGROUND LIBRARY --- */}
        <g id="library" transform="translate(450, 100)">
          {/* Library Frame */}
          <rect x="0" y="0" width="300" height="400" rx="10" fill="#F3F4F6" stroke="#E5E7EB" strokeWidth="4" />
          
          {/* Shelves */}
          {shelves.map((shelf, sIdx) => (
            <g key={`shelf-${sIdx}`}>
              {/* Shelf Base */}
              <rect x="10" y={100 + sIdx * 120} width="280" height="10" fill="#D1D5DB" />
              {/* Shelf Shadow */}
              <rect x="10" y={110 + sIdx * 120} width="280" height="5" fill="#9CA3AF" opacity="0.2" />
              
              {/* Books on shelf */}
              {books.map((book, idx) => {
                const bShelf = Math.floor(idx / 5);
                const bPos = idx % 5;
                if (bShelf !== sIdx) return null;
                return (
                  <g key={book.id} transform={`translate(${30 + bPos * 50}, ${30 + sIdx * 120})`} className="cursor-pointer" onClick={() => onBookClick(book.id)}>
                    {/* Book spine */}
                    <rect x="0" y="0" width="30" height="70" rx="3" fill={book.color} />
                    {/* Title mock */}
                    <rect x="5" y="10" width="20" height="5" fill="#ffffff" opacity="0.5" />
                    <rect x="5" y="20" width="15" height="5" fill="#ffffff" opacity="0.3" />
                  </g>
                );
              })}
            </g>
          ))}
          
          {/* Flying Book (Transporting) */}
          <AnimatePresence>
            {state === 'transporting' && (
              <motion.g
                initial={{ x: -200, y: 200, scale: 2, opacity: 1, rotate: -20 }}
                animate={{ 
                  x: 30 + (targetSlot % 5) * 50, 
                  y: 30 + Math.floor(targetSlot / 5) * 120, 
                  scale: 1, rotate: 0 
                }}
                transition={{ duration: 2, ease: "easeInOut", delay: 0.5 }}
              >
                <rect x="0" y="0" width="30" height="70" rx="3" fill="#3B82F6" />
                <rect x="5" y="10" width="20" height="5" fill="#ffffff" opacity="0.5" />
                <rect x="5" y="20" width="15" height="5" fill="#ffffff" opacity="0.3" />
              </motion.g>
            )}
          </AnimatePresence>
        </g>

        {/* --- LAYER 2: ISOMETRIC DESK --- */}
        {/* We use a transform matrix to create an isometric/trapezoid projection for the desk surface */}
        <g id="desk-surface" transform="translate(100, 350) scale(1, 0.4) skewX(-30)">
          {/* Desk Top */}
          <rect x="0" y="0" width="500" height="350" rx="20" fill="#FFFFFF" stroke="#E5E7EB" strokeWidth="2" />
          <rect x="-10" y="10" width="500" height="350" rx="20" fill="rgba(0,0,0,0.02)" />

          {/* Isometric Items on Desk */}
          <AnimatePresence>
            {/* BOOK (Reading Phase) */}
            {state === 'reading' && (
              <motion.g initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                {/* Left Page */}
                <path d="M 100 100 L 250 100 L 250 250 L 100 250 Z" fill="#F9FAFB" stroke="#D1D5DB" strokeWidth="2" />
                {/* Right Page */}
                <path d="M 250 100 L 400 100 L 400 250 L 250 250 Z" fill="#FFFFFF" stroke="#D1D5DB" strokeWidth="2" />
                {/* Binding */}
                <line x1="250" y1="100" x2="250" y2="250" stroke="#9CA3AF" strokeWidth="4" />
                
                {/* Animated Page Turn */}
                <motion.path 
                  d="M 250 100 L 400 100 L 400 250 L 250 250 Z" fill="#FFFFFF" stroke="#E5E7EB" strokeWidth="1"
                  initial={{ opacity: 0 }}
                  animate={{ 
                    opacity: [0, 0, 1, 1, 0, 0],
                    scaleX: [1, 1, 1, -1, -1, 1], // Flips over the binding!
                  }}
                  transition={{ repeat: Infinity, duration: 4, times: [0, 0.6, 0.65, 0.8, 0.81, 1], ease: "easeInOut" }}
                  style={{ transformOrigin: "250px 175px" }}
                />
              </motion.g>
            )}

            {/* CARDS & INK (Generation Phase) */}
            {(state === 'generation' || state === 'bridge_generation') && (
              <motion.g initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                <rect x="150" y="100" width="200" height="150" rx="5" fill={state === 'bridge_generation' ? '#FEF3C7' : '#FFFFFF'} stroke="#D1D5DB" strokeWidth="2" />
                
                {/* Ink Path (Strictly tracked by right hand) */}
                <motion.path 
                  d="M 170 130 L 330 130 M 170 170 L 300 170 M 170 210 L 330 210" 
                  stroke={state === 'bridge_generation' ? '#D97706' : '#3B82F6'} 
                  strokeWidth="6" strokeLinecap="round" strokeDasharray="60"
                  variants={inkVariants}
                  animate={state}
                />
              </motion.g>
            )}

            {/* DEDUPLICATION STACKS */}
            {state === 'deduplication' && (
              <motion.g initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                {/* Incoming Pile (Left) */}
                {[...Array(leftStackCount)].map((_, i) => (
                  <rect key={`left-${i}`} x="100" y={100 - i * 5} width="120" height="80" rx="3" fill="#FFFFFF" stroke="#D1D5DB" strokeWidth="2" />
                ))}
                
                {/* Validated Pile (Right) */}
                {[...Array(rightStackCount)].map((_, i) => (
                  <rect key={`right-${i}`} x="280" y={150 - i * 5} width="120" height="80" rx="3" fill="#FFFFFF" stroke="#D1D5DB" strokeWidth="2" />
                ))}
              </motion.g>
            )}
          </AnimatePresence>
        </g>

        {/* --- LAYER 3: ROBOT AVATAR --- */}
        {/* Placed in front of desk */}
        <motion.g variants={robotVariants} animate={animKey} transform="translate(180, 200)">
          
          {/* Back View (When transporting) */}
          <AnimatePresence>
            {state === 'transporting' && (
              <motion.g initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.5 }}>
                {/* Back of body */}
                <rect x="75" y="80" width="100" height="120" rx="30" fill="#F9FAFB" stroke="#D1D5DB" strokeWidth="3" />
                {/* Back details */}
                <circle cx="125" cy="140" r="20" fill="#E5E7EB" />
                <path d="M 115 130 L 135 150 M 135 130 L 115 150" stroke="#9CA3AF" strokeWidth="4" />
                {/* Back of head */}
                <rect x="65" y="10" width="120" height="80" rx="20" fill="#FFFFFF" stroke="#D1D5DB" strokeWidth="3" />
                {/* Back antennas */}
                <rect x="50" y="30" width="15" height="30" rx="5" fill="#9CA3AF" />
                <rect x="185" y="30" width="15" height="30" rx="5" fill="#9CA3AF" />
              </motion.g>
            )}
          </AnimatePresence>

          {/* Front View */}
          <AnimatePresence>
            {state !== 'transporting' && (
              <motion.g initial={{ opacity: 1 }} exit={{ opacity: 0 }}>
                {/* LEFT ARM */}
                <g>
                  <motion.g variants={upperArmLeftVariants} animate={animKey} style={{ transformOrigin: "60px 100px" }}>
                    {/* Upper Arm */}
                    <line x1="60" y1="100" x2="20" y2="145" stroke="#FFFFFF" strokeWidth="20" strokeLinecap="round" style={{ filter: 'drop-shadow(2px 2px 2px rgba(0,0,0,0.1))' }} />
                    
                    <motion.g variants={forearmLeftVariants} animate={animKey} style={{ transformOrigin: "20px 145px" }}>
                      {/* Forearm */}
                      <line x1="20" y1="145" x2="90" y2="190" stroke="#FFFFFF" strokeWidth="20" strokeLinecap="round" style={{ filter: 'drop-shadow(2px 2px 2px rgba(0,0,0,0.1))' }} />
                      
                      {/* Left Apple-style Hand */}
                      <g transform="translate(90, 190)">
                        {/* Palm */}
                        <rect x="-12" y="-10" width="24" height="20" rx="8" fill="#FFFFFF" stroke="#E5E7EB" strokeWidth="2" />
                        {/* Dark Joints */}
                        <circle cx="-10" cy="12" r="3" fill="#374151" />
                        <circle cx="0" cy="14" r="3" fill="#374151" />
                        <circle cx="10" cy="12" r="3" fill="#374151" />
                        {/* Fingers (White smooth) */}
                        <rect x="-14" y="12" width="8" height="15" rx="4" fill="#FFFFFF" stroke="#E5E7EB" strokeWidth="1" />
                        <rect x="-4" y="14" width="8" height="18" rx="4" fill="#FFFFFF" stroke="#E5E7EB" strokeWidth="1" />
                        <rect x="6" y="12" width="8" height="15" rx="4" fill="#FFFFFF" stroke="#E5E7EB" strokeWidth="1" />
                        {/* Thumb */}
                        <rect x="12" y="-5" width="12" height="8" rx="4" fill="#FFFFFF" stroke="#E5E7EB" strokeWidth="1" transform="rotate(30)" />
                        
                        {/* Left Hand Item (Card) */}
                        <AnimatePresence>
                          {state === 'deduplication' && (
                            <motion.rect initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                              x="-10" y="10" width="40" height="30" fill="#FFFFFF" stroke="#9CA3AF" strokeWidth="1" transform="rotate(-15)" 
                            />
                          )}
                        </AnimatePresence>
                      </g>
                    </motion.g>
                  </motion.g>
                  {/* Shoulder Joint (Fixed Anchor) */}
                  <circle cx="60" cy="100" r="15" fill="#F3F4F6" stroke="#D1D5DB" strokeWidth="2" />
                </g>

                {/* RIGHT ARM */}
                <g>
                  <motion.g variants={upperArmRightVariants} animate={animKey} style={{ transformOrigin: "190px 100px" }}>
                    {/* Upper Arm */}
                    <line x1="190" y1="100" x2="230" y2="145" stroke="#FFFFFF" strokeWidth="20" strokeLinecap="round" style={{ filter: 'drop-shadow(2px 2px 2px rgba(0,0,0,0.1))' }} />
                    
                    <motion.g variants={forearmRightVariants} animate={animKey} style={{ transformOrigin: "230px 145px" }}>
                      {/* Forearm */}
                      <line x1="230" y1="145" x2="160" y2="190" stroke="#FFFFFF" strokeWidth="20" strokeLinecap="round" style={{ filter: 'drop-shadow(2px 2px 2px rgba(0,0,0,0.1))' }} />
                      
                      {/* Right Apple-style Hand */}
                      <g transform="translate(160, 190)">
                        {/* Palm */}
                        <rect x="-12" y="-10" width="24" height="20" rx="8" fill="#FFFFFF" stroke="#E5E7EB" strokeWidth="2" />
                        {/* Dark Joints */}
                        <circle cx="-10" cy="12" r="3" fill="#374151" />
                        <circle cx="0" cy="14" r="3" fill="#374151" />
                        <circle cx="10" cy="12" r="3" fill="#374151" />
                        {/* Fingers */}
                        <rect x="-14" y="12" width="8" height="15" rx="4" fill="#FFFFFF" stroke="#E5E7EB" strokeWidth="1" />
                        <rect x="-4" y="14" width="8" height="18" rx="4" fill="#FFFFFF" stroke="#E5E7EB" strokeWidth="1" />
                        <rect x="6" y="12" width="8" height="15" rx="4" fill="#FFFFFF" stroke="#E5E7EB" strokeWidth="1" />
                        {/* Thumb */}
                        <rect x="-22" y="2" width="12" height="8" rx="4" fill="#FFFFFF" stroke="#E5E7EB" strokeWidth="1" transform="rotate(-30)" />
                        
                        {/* Right Hand Items (Pen or Card) */}
                        <AnimatePresence>
                          {(state === 'generation' || state === 'bridge_generation') && (
                            <motion.g initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                              {/* Pencil (HB) perfectly centered in palm */}
                              <g transform="rotate(-30)">
                                {/* Eraser */}
                                <rect x="-5" y="-35" width="10" height="12" rx="3" fill="#F472B6" />
                                {/* Ferrule */}
                                <rect x="-5" y="-23" width="10" height="8" fill="#9CA3AF" />
                                {/* Body */}
                                <rect x="-5" y="-15" width="10" height="40" fill="#FCD34D" />
                                {/* Hexagonal line */}
                                <line x1="0" y1="-15" x2="0" y2="25" stroke="#D97706" strokeWidth="1" />
                                {/* Wood Cone */}
                                <path d="M -5 25 L 5 25 L 0 37 Z" fill="#FDE68A" />
                                {/* Tip (Graphite) touches the paper */}
                                <path d="M -1.5 33.5 L 1.5 33.5 L 0 37 Z" fill="#1F2937" />
                              </g>
                            </motion.g>
                          )}
                          {state === 'deduplication' && (
                            <motion.rect initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                              x="-15" y="10" width="40" height="30" fill="#FFFFFF" stroke="#9CA3AF" strokeWidth="1" transform="rotate(15)" 
                            />
                          )}
                        </AnimatePresence>
                      </g>
                    </motion.g>
                  </motion.g>
                  {/* Shoulder Joint (Fixed Anchor) */}
                  <circle cx="190" cy="100" r="15" fill="#F3F4F6" stroke="#D1D5DB" strokeWidth="2" />
                </g>

                {/* Body Base */}
                <rect x="75" y="80" width="100" height="120" rx="30" fill="#F9FAFB" stroke="#D1D5DB" strokeWidth="3" />
                {/* Chest Glow */}
                <rect x="95" y="110" width="60" height="30" rx="10" fill="#E5E7EB" />
                <motion.circle cx="125" cy="125" r="5" fill="#3B82F6" animate={{ opacity: [0.3, 1, 0.3] }} transition={{ repeat: Infinity, duration: 2 }} />

                {/* Head */}
                <rect x="65" y="10" width="120" height="80" rx="20" fill="#FFFFFF" stroke="#D1D5DB" strokeWidth="3" />
                
                {/* Face Screen */}
                <rect x="75" y="20" width="100" height="60" rx="15" fill="#111827" />
                
                {/* Eyes Group (Scanning) */}
                <motion.g variants={eyesVariants} animate={animKey}>
                  <rect x="95" y="40" width="20" height="20" rx="10" fill="#60A5FA" />
                  <rect x="135" y="40" width="20" height="20" rx="10" fill="#60A5FA" />
                </motion.g>

                {/* Antennas */}
                <rect x="50" y="35" width="15" height="30" rx="5" fill="#9CA3AF" />
                <rect x="185" y="35" width="15" height="30" rx="5" fill="#9CA3AF" />
              </motion.g>
            )}
          </AnimatePresence>

          {/* Fusion Flash VFX (Centered on chest) */}
          <motion.g variants={fusionFlashVariants} animate={animKey === 'fusion' ? 'fusion' : 'default'} style={{ transformOrigin: "125px 160px" }}>
            <circle cx="125" cy="160" r="120" fill="url(#fusionGradient)" style={{ mixBlendMode: 'screen' }} />
            <circle cx="125" cy="160" r="40" fill="#FFFFFF" filter="blur(8px)" />
            {/* Lightning arcs */}
            <path d="M 125 40 L 135 100 L 220 160 L 135 180 L 125 280 L 115 180 L 30 160 L 115 100 Z" fill="#60A5FA" opacity="0.9" filter="blur(2px)" />
          </motion.g>
        </motion.g>

        {/* DEFINITIONS */}
        <defs>
          <radialGradient id="fusionGradient" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#93C5FD" stopOpacity="1" />
            <stop offset="50%" stopColor="#3B82F6" stopOpacity="0.8" />
            <stop offset="100%" stopColor="#1D4ED8" stopOpacity="0" />
          </radialGradient>
        </defs>

      </svg>
    </div>
  );
}
