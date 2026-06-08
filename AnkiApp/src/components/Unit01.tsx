import { motion, AnimatePresence } from 'motion/react';
import { useEffect, useState } from 'react';

interface Unit01Props {
  state: 'idle' | 'reading' | 'creating' | 'deduplicating' | 'transporting';
}

export const Unit01 = ({ state }: Unit01Props) => {
  // Local state to track deduplication cycle (fusion vs no fusion)
  const [mergeScenario, setMergeScenario] = useState<'A' | 'B'>('A');

  // Randomize merge scenario during deduplicating
  useEffect(() => {
    if (state === 'deduplicating') {
      const interval = setInterval(() => {
        setMergeScenario(Math.random() > 0.5 ? 'A' : 'B');
      }, 2500); // Change scenario every 2.5s (duration of one cycle)
      return () => clearInterval(interval);
    }
  }, [state]);

  // Main wrapper translation for transporting
  const containerVariants = {
    idle: { y: [0, -4, 0], x: 0 },
    reading: { y: [0, -4, 0], x: 0 },
    creating: { y: [0, -4, 0], x: 0 },
    deduplicating: { y: [0, -4, 0], x: 0 },
    transporting: { 
      y: [0, -10, 0], 
      x: 150, // Move to the right physically
      scaleX: -1, // Flip to face the library
    }
  };

  const armLVariants = {
    idle: { rotate: 0 },
    reading: { rotate: -20 },
    creating: { rotate: -10 },
    deduplicating: {
      rotate: mergeScenario === 'A' ? [0, 45, 0] : [0, 60, 0],
      transition: { duration: 2.5, repeat: Infinity }
    },
    transporting: { rotate: -40 }
  };

  const elbowLVariants = {
    idle: { rotate: 0 },
    reading: { rotate: 30 },
    creating: { rotate: 10 },
    deduplicating: {
      rotate: mergeScenario === 'A' ? [0, -45, 0] : [0, -20, 0],
      transition: { duration: 2.5, repeat: Infinity }
    },
    transporting: { rotate: 80 }
  };

  const armRVariants = {
    idle: { rotate: 0 },
    reading: { rotate: 20 },
    creating: { 
      rotate: [20, 25, 20, 25, 20], 
      transition: { duration: 1, repeat: Infinity } 
    },
    deduplicating: {
      rotate: mergeScenario === 'A' ? [0, -45, -90, 0] : [0, -10, -90, 0],
      transition: { duration: 2.5, repeat: Infinity }
    },
    transporting: { rotate: 40 }
  };

  const elbowRVariants = {
    idle: { rotate: 0 },
    reading: { rotate: -30 },
    creating: { 
      rotate: [-10, -20, -10, -20, -10],
      transition: { duration: 1, repeat: Infinity } 
    },
    deduplicating: {
      rotate: mergeScenario === 'A' ? [0, 45, 30, 0] : [0, 10, 30, 0],
      transition: { duration: 2.5, repeat: Infinity }
    },
    transporting: { rotate: -80 }
  };

  return (
    <div className="w-full h-full relative flex items-center justify-center">
      <motion.div 
        variants={containerVariants}
        animate={state}
        transition={{ 
          y: { duration: 2, repeat: Infinity, ease: "easeInOut" },
          x: { duration: 1.5, ease: "easeInOut" },
          scaleX: { delay: 0.5, duration: 0.2 } // Flip after starting moving
        }}
        className="w-56 h-56 relative"
      >
        <svg 
          viewBox="0 0 200 200" 
          xmlns="http://www.w3.org/2000/svg"
          className="w-full h-full object-contain overflow-visible"
        >
          {/* Environment (Desk, Paper, Piles) - fade out when transporting */}
          <motion.g animate={{ opacity: state === 'transporting' ? 0 : 1 }}>
            {/* The Desk */}
            <path d="M 10 160 L 190 160 L 210 190 L -10 190 Z" fill="#E2E8F0" />
            <rect x="-10" y="190" width="220" height="10" fill="#CBD5E1" />

            {/* The Paper on the Desk (Visible in creating) */}
            <AnimatePresence>
              {(state === 'creating' || state === 'deduplicating') && (
                <motion.polygon 
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  points="80,165 120,165 130,185 70,185" 
                  fill="#FFF" 
                  stroke="#94A3B8" 
                  strokeWidth="1" 
                />
              )}
            </AnimatePresence>

            {/* Left Card Pile (Grows in creating, shrinks in deduplicating) */}
            <AnimatePresence>
              {(state === 'creating' || state === 'deduplicating') && (
                <motion.g initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                  <rect x="20" y="170" width="30" height="4" fill="#FACC15" rx="1" />
                  <rect x="20" y="166" width="30" height="4" fill="#FACC15" rx="1" />
                  <rect x="20" y="162" width="30" height="4" fill="#FACC15" rx="1" />
                  {state === 'creating' && (
                    <motion.rect x="20" y="158" width="30" height="4" fill="#FACC15" rx="1"
                      animate={{ opacity: [0, 1] }} transition={{ duration: 1, repeat: Infinity }}
                    />
                  )}
                </motion.g>
              )}
            </AnimatePresence>

            {/* Right Card Pile (Grows in deduplicating) */}
            <AnimatePresence>
              {state === 'deduplicating' && (
                <motion.g initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                  <rect x="150" y="170" width="30" height="4" fill="#22C55E" rx="1" />
                  <rect x="150" y="166" width="30" height="4" fill="#22C55E" rx="1" />
                  <motion.rect x="150" y="162" width="30" height="4" fill="#22C55E" rx="1"
                    animate={{ opacity: [0, 1] }} transition={{ duration: 2.5, repeat: Infinity }}
                  />
                </motion.g>
              )}
            </AnimatePresence>
          </motion.g>

          <g id="robot-unit-01">
            {/* Legs */}
            <rect fill="#1E40AF" height="30" id="leg-l" rx="7.5" width="15" x="85" y="145" />
            <rect fill="#1E40AF" height="30" id="leg-r" rx="7.5" width="15" x="110" y="145" />
            
            {/* Torso */}
            <rect fill="#3B82F6" height="75" id="torso" rx="18" width="65" x="72.5" y="80" />
            
            {/* Screen */}
            <rect fill="#DBEAFE" height="35" id="screen" rx="8" width="45" x="82.5" y="90" />
            
            {/* Core indicator */}
            <motion.circle 
              cx="105" cy="139" fill="#FACC15" r="3.5"
              animate={{ opacity: [0.3, 1, 0.3], scale: [0.8, 1.2, 0.8] }}
              transition={{ duration: 1.5, repeat: Infinity }}
            />

            {/* Arms with new anatomical structure (hybrid trapezoid + joint) */}
            <g id="arms">
              {/* Left Arm Assembly */}
              <motion.g
                variants={armLVariants}
                animate={state}
                style={{ originX: '70px', originY: '100px' }}
              >
                {/* Shoulder joint */}
                <circle cx="70" cy="100" r="5" fill="#1D4ED8" />
                {/* Upper arm (trapezoid-like path) */}
                <path d="M 66 100 Q 64 115 67 125 L 73 125 Q 76 115 74 100 Z" fill="#1E40AF" />
                
                {/* Left Forearm Assembly */}
                <motion.g
                  variants={elbowLVariants}
                  animate={state}
                  style={{ originX: '70px', originY: '125px' }}
                >
                  {/* Elbow joint */}
                  <circle cx="70" cy="125" r="5" fill="#2563EB" />
                  {/* Forearm */}
                  <path d="M 67 125 Q 66 140 68 150 L 72 150 Q 74 140 73 125 Z" fill="#1E40AF" />
                  {/* Hand */}
                  <rect x="67" y="150" width="6" height="8" rx="3" fill="#1D4ED8" />
                  
                  {/* Card held in left hand during deduplicating */}
                  <AnimatePresence>
                    {state === 'deduplicating' && (
                      <motion.rect 
                        x="60" y="152" width="20" height="15" fill="#FFF" stroke="#94A3B8" strokeWidth="1"
                        animate={{ opacity: mergeScenario === 'A' ? [1, 0] : [1, 1, 0] }} // Disappears on merge or drop
                        transition={{ duration: 2.5, repeat: Infinity }}
                      />
                    )}
                  </AnimatePresence>
                </motion.g>
              </motion.g>
              
              {/* Right Arm Assembly */}
              <motion.g
                variants={armRVariants}
                animate={state}
                style={{ originX: '140px', originY: '100px' }}
              >
                {/* Shoulder joint */}
                <circle cx="140" cy="100" r="5" fill="#1D4ED8" />
                {/* Upper arm */}
                <path d="M 136 100 Q 134 115 137 125 L 143 125 Q 146 115 144 100 Z" fill="#1E40AF" />
                
                {/* Right Forearm Assembly */}
                <motion.g
                  variants={elbowRVariants}
                  animate={state}
                  style={{ originX: '140px', originY: '125px' }}
                >
                  {/* Elbow joint */}
                  <circle cx="140" cy="125" r="5" fill="#2563EB" />
                  {/* Forearm */}
                  <path d="M 137 125 Q 136 140 138 150 L 142 150 Q 144 140 143 125 Z" fill="#1E40AF" />
                  {/* Hand */}
                  <rect x="137" y="150" width="6" height="8" rx="3" fill="#1D4ED8" />

                  {/* Pen in right hand during creating */}
                  <AnimatePresence>
                    {state === 'creating' && (
                      <motion.path 
                        initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                        d="M 139 155 L 135 165 L 137 165 Z" fill="#000" 
                      />
                    )}
                  </AnimatePresence>

                  {/* Card held in right hand during deduplicating */}
                  <AnimatePresence>
                    {state === 'deduplicating' && (
                      <motion.rect 
                        x="130" y="152" width="20" height="15" fill="#FFF" stroke="#94A3B8" strokeWidth="1"
                        animate={{ opacity: [1, 1, 0, 0] }} // Drops at the end
                        transition={{ duration: 2.5, repeat: Infinity }}
                      />
                    )}
                  </AnimatePresence>
                </motion.g>
              </motion.g>
            </g>

            {/* Flash Effect on Fusion (Scenario A) */}
            <AnimatePresence>
              {state === 'deduplicating' && mergeScenario === 'A' && (
                <motion.circle 
                  cx="105" cy="130" r="30" fill="#FFF"
                  animate={{ opacity: [0, 0, 1, 0], scale: [0, 0, 1.5, 0] }}
                  transition={{ duration: 2.5, repeat: Infinity, times: [0, 0.4, 0.5, 0.6] }} // Flash at center touch
                  className="mix-blend-overlay"
                />
              )}
            </AnimatePresence>

            {/* Head Unit */}
            <g id="head">
              <rect fill="#3B82F6" height="50" rx="14" width="55" x="77.5" y="40" />
              <circle cx="77.5" cy="65" fill="#1E3A8A" r="3.5" />
              <circle cx="132.5" cy="65" fill="#1E3A8A" r="3.5" />
              <motion.circle 
                cx="92" cy="65" fill="#FACC15" r="5" 
                animate={(state === 'reading' || state === 'creating') ? { scaleY: [1, 0.2, 1] } : {}}
                transition={{ duration: 0.2, repeat: Infinity, repeatDelay: 1 }}
              />
              <motion.circle 
                cx="118" cy="65" fill="#FACC15" r="5" 
                animate={(state === 'reading' || state === 'creating') ? { scaleY: [1, 0.2, 1] } : {}}
                transition={{ duration: 0.2, repeat: Infinity, repeatDelay: 1 }}
              />
              <line stroke="#B80035" strokeWidth="4" x1="105" x2="105" y1="40" y2="30" />
              <motion.circle cx="105" cy="27" fill="#B80035" r="5" animate={{ opacity: [1, 0.5, 1] }} transition={{ duration: 0.8, repeat: Infinity }} />
            </g>

            {/* The Book (Visible only when reading/transporting) */}
            {(state === 'reading' || state === 'transporting') && (
              <motion.g
                initial={{ opacity: 0, scale: 0.5, y: 50 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                className="pointer-events-none"
              >
                 {/* Book Body (V-Shape Open) */}
                 <path d="M100 120 L60 100 L60 70 L100 90 Z" fill="#FFF" stroke="#B80035" strokeWidth="2" />
                 <path d="M100 120 L140 100 L140 70 L100 90 Z" fill="#FFF" stroke="#B80035" strokeWidth="2" />
                 
                 {/* Turning Pages */}
                 {state === 'reading' && (
                   <motion.path 
                     d="M100 120 L100 90 Q120 80 140 100" 
                     fill="none" 
                     stroke="#B80035" 
                     strokeWidth="1"
                     animate={{ d: ["M100 120 L100 90 Q120 80 140 100", "M100 120 L100 90 Q100 70 60 100", "M100 120 L100 90 Q120 80 140 100"] }}
                     transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut" }}
                   />
                 )}
                 
                 {/* Text lines caricature */}
                 <path d="M65 80 L85 90 M65 85 L85 95 M115 90 L135 80 M115 95 L135 85" stroke="#B80035" strokeWidth="1" opacity="0.4" />
              </motion.g>
            )}
          </g>
        </svg>
      </motion.div>
    </div>
  );
};
