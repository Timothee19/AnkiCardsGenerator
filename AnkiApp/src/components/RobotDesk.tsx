import { motion, AnimatePresence, useMotionValue, animate } from 'framer-motion';
import { useEffect, useState, useRef } from 'react';

export type RobotState = 'idle' | 'reading' | 'generation' | 'bridge_generation' | 'sort' | 'fusion' | 'transporting';

interface RobotDeskProps {
  state: RobotState;
  stageProgress: number;
  stageStatusText: string;
}

export function RobotDesk({ state, stageProgress, stageStatusText }: RobotDeskProps) {
  const isDeduplication = state === 'sort' || state === 'fusion';
  const [dedupAction, setDedupAction] = useState<'fusion_action' | 'sort_action'>('fusion_action');

  useEffect(() => {
    if (isDeduplication) {
      const interval = setInterval(() => {
        setDedupAction(Math.random() > 0.5 ? 'fusion_action' : 'sort_action');
      }, 3000);
      return () => clearInterval(interval);
    }
  }, [isDeduplication]);

  const activeState = isDeduplication ? dedupAction : state;

  let leftStackCount = 0;
  let rightStackCount = 0;

  if (state === 'generation' || state === 'bridge_generation') {
    leftStackCount = Math.max(0, Math.floor(stageProgress * 15));
    rightStackCount = 0;
  } else if (isDeduplication) {
    leftStackCount = Math.max(0, 15 - Math.floor(stageProgress * 15));
    rightStackCount = Math.min(15, Math.floor(stageProgress * 15));
  }

  // ========================================================
  // ARTICULATED ARM SYSTEM — True Double-Pendulum Kinematics
  // ========================================================
  //
  // We use useMotionValue + animate() to drive joint angles,
  // then apply them as native SVG transform="rotate(angle)"
  // via refs. SVG rotate() ALWAYS rotates around (0,0) of the
  // local coordinate system — guaranteed by SVG spec.
  //
  // Structure per arm:
  //   <g transform="translate(shoulderX, shoulderY)">     ← positions shoulder
  //     <g ref={shoulderRef} transform="rotate(θ₁)">      ← upper arm rotates around shoulder (FIXED anchor)
  //       <path ... upper arm segment ... />
  //       <g transform="translate(elbowOffsetX, elbowOffsetY)">  ← positions elbow at end of upper arm
  //         <g ref={elbowRef} transform="rotate(θ₂)">     ← forearm rotates around elbow (MOBILE anchor)
  //           <path ... forearm segment ... />
  //           <g ... hand + items ... />
  //         </g>
  //       </g>
  //     </g>
  //   </g>

  // Motion values for joint angles (degrees)
  const lShoulderAngle = useMotionValue(0);
  const lElbowAngle = useMotionValue(0);
  const rShoulderAngle = useMotionValue(0);
  const rElbowAngle = useMotionValue(0);

  // Refs to SVG <g> elements for direct attribute manipulation
  const lShoulderRef = useRef<SVGGElement>(null);
  const lElbowRef = useRef<SVGGElement>(null);
  const rShoulderRef = useRef<SVGGElement>(null);
  const rElbowRef = useRef<SVGGElement>(null);

  // Sync motion values → SVG transform attributes (bypasses CSS entirely)
  useEffect(() => {
    const unsubs = [
      lShoulderAngle.on("change", (v) => lShoulderRef.current?.setAttribute('transform', `rotate(${v})`)),
      lElbowAngle.on("change", (v) => lElbowRef.current?.setAttribute('transform', `rotate(${v})`)),
      rShoulderAngle.on("change", (v) => rShoulderRef.current?.setAttribute('transform', `rotate(${v})`)),
      rElbowAngle.on("change", (v) => rElbowRef.current?.setAttribute('transform', `rotate(${v})`)),
    ];
    return () => unsubs.forEach(u => u());
  }, [lShoulderAngle, lElbowAngle, rShoulderAngle, rElbowAngle]);

  // Drive joint animations based on active state
  useEffect(() => {
    const controls: ReturnType<typeof animate>[] = [];
    const ease = "easeInOut" as const;

    switch (activeState) {
      case 'idle':
        controls.push(
          animate(lShoulderAngle, 0, { duration: 0.5, ease }),
          animate(lElbowAngle, 0, { duration: 0.5, ease }),
          animate(rShoulderAngle, 0, { duration: 0.5, ease }),
          animate(rElbowAngle, 0, { duration: 0.5, ease }),
        );
        break;

      case 'reading':
        controls.push(
          animate(lShoulderAngle, -15, { duration: 0.5, ease }),
          animate(lElbowAngle, 10, { duration: 0.5, ease }),
          animate(rShoulderAngle, 15, { duration: 0.5, ease }),
          animate(rElbowAngle, -10, { duration: 0.5, ease }),
        );
        break;

      case 'generation':
      case 'bridge_generation':
        controls.push(
          animate(lShoulderAngle, [0, -5, 2, -3, 0], { duration: 1, repeat: Infinity, ease }),
          animate(lElbowAngle, [0, 15, -5, 10, 0], { duration: 1, repeat: Infinity, ease }),
          animate(rShoulderAngle, 0, { duration: 0.5, ease }),
          animate(rElbowAngle, 0, { duration: 0.5, ease }),
        );
        break;

      case 'fusion_action':
        controls.push(
          animate(lShoulderAngle, [0, -30, -51, -51, 0], { duration: 3, times: [0, 0.3, 0.5, 0.7, 1], ease }),
          animate(lElbowAngle, [0, -10, -15, -15, 0], { duration: 3, times: [0, 0.3, 0.5, 0.7, 1], ease }),
          animate(rShoulderAngle, [0, 30, 51, 51, 0], { duration: 3, times: [0, 0.3, 0.5, 0.7, 1], ease }),
          animate(rElbowAngle, [0, 10, 15, 15, 0], { duration: 3, times: [0, 0.3, 0.5, 0.7, 1], ease }),
        );
        break;

      case 'sort_action':
        controls.push(
          animate(lShoulderAngle, [0, 15, 25, 0, 0, 0], { duration: 3, times: [0, 0.2, 0.4, 0.6, 0.8, 1], ease }),
          animate(lElbowAngle, [0, 10, 15, 0, 0, 0], { duration: 3, times: [0, 0.2, 0.4, 0.6, 0.8, 1], ease }),
          animate(rShoulderAngle, [0, 0, 0, -15, -25, 0], { duration: 3, times: [0, 0.2, 0.4, 0.6, 0.8, 1], ease }),
          animate(rElbowAngle, [0, 0, 0, -10, -15, 0], { duration: 3, times: [0, 0.2, 0.4, 0.6, 0.8, 1], ease }),
        );
        break;

      case 'transporting':
        controls.push(
          animate(lShoulderAngle, 30, { duration: 0.5, ease }),
          animate(lElbowAngle, 10, { duration: 0.5, ease }),
          animate(rShoulderAngle, -40, { duration: 0.5, ease }),
          animate(rElbowAngle, 20, { duration: 0.5, ease }),
        );
        break;
    }

    return () => controls.forEach(c => c.stop());
  }, [activeState, lShoulderAngle, lElbowAngle, rShoulderAngle, rElbowAngle]);

  // --- NON-ARM ANIMATION VARIANTS (cards, flash, page turn) ---

  const leftCardVariants = {
    fusion_action: { opacity: [0, 1, 1, 0, 0], transition: { duration: 3, times: [0, 0.19, 0.69, 0.7, 1] } },
    sort_action: { opacity: [0, 1, 1, 0, 0, 0], transition: { duration: 3, times: [0, 0.19, 0.39, 0.4, 0.6, 1] } },
    default: { opacity: 0 }
  };

  const rightCardVariants = {
    fusion_action: { opacity: [0, 1, 1, 1, 0], transition: { duration: 3, times: [0, 0.19, 0.7, 0.84, 1] } },
    sort_action: { opacity: [0, 0, 0, 1, 1, 0], transition: { duration: 3, times: [0, 0.4, 0.59, 0.79, 0.8, 1] } },
    default: { opacity: 0 }
  };

  const fusionFlashVariants = {
    fusion_action: { opacity: [0, 0, 1, 0, 0], scale: [0.5, 0.5, 1.5, 0.5, 0.5], transition: { duration: 3, times: [0, 0.59, 0.6, 0.7, 1] } },
    default: { opacity: 0 }
  };

  const pageTurnVariants = {
    idle: { opacity: 0 },
    reading: {
      opacity: [0, 0, 1, 1, 0, 0],
      x: [0, 0, 0, -40, -40, 0],
      scaleX: [1, 1, 1, 0.1, 0.1, 1],
      transition: { repeat: Infinity, duration: 4, times: [0, 0.6, 0.65, 0.8, 0.81, 1], ease: "easeInOut" }
    },
    default: { opacity: 0 }
  };

  // --- SVG SUB-COMPONENTS ---

  const Hand = () => (
    <g transform="translate(-15, 0)">
      <rect x="0" y="0" width="30" height="20" rx="6" fill="#FFFFFF" stroke="#9CA3AF" strokeWidth="2" />
      <rect x="2" y="20" width="6" height="12" rx="3" fill="#FFFFFF" stroke="#9CA3AF" strokeWidth="1.5" />
      <rect x="12" y="20" width="6" height="14" rx="3" fill="#FFFFFF" stroke="#9CA3AF" strokeWidth="1.5" />
      <rect x="22" y="20" width="6" height="12" rx="3" fill="#FFFFFF" stroke="#9CA3AF" strokeWidth="1.5" />
      <rect x="-8" y="8" width="10" height="6" rx="3" fill="#FFFFFF" stroke="#9CA3AF" strokeWidth="1.5" transform="rotate(-30)" />
    </g>
  );

  const DetailedPencil = () => (
    <g transform="translate(0, 10) rotate(-30)">
       <rect x="-4" y="-35" width="8" height="15" rx="2" fill="#F472B6" />
       <rect x="-4" y="-20" width="8" height="5" fill="#9CA3AF" />
       <rect x="-4" y="-15" width="8" height="25" fill="#FCD34D" />
       <path d="M -4 10 L 4 10 L 0 20 Z" fill="#FDE68A" />
       <path d="M -1.5 16.5 L 1.5 16.5 L 0 20 Z" fill="#1F2937" />
    </g>
  );

  return (
    <div className="absolute inset-0 flex flex-col items-center pt-8">
      {/* HUD */}
      <div className="w-full max-w-md mx-auto mb-4 flex flex-col items-center z-10 relative">
        <motion.div 
          key={stageStatusText}
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white/90 backdrop-blur-md border border-neutral-200 px-6 py-2 rounded-full shadow-sm mb-3"
        >
          <p className="text-[13px] font-bold tracking-wide text-neutral-800 uppercase">
            {stageStatusText || "Système prêt"}
          </p>
        </motion.div>
        
        <div className="w-full h-2 bg-neutral-200 rounded-full overflow-hidden shadow-inner max-w-xs">
          <motion.div 
            className="h-full bg-blue-500"
            initial={{ width: 0 }}
            animate={{ width: `${stageProgress * 100}%` }}
            transition={{ type: "spring", stiffness: 50, damping: 15 }}
          />
        </div>
      </div>

      {/* Z-Indexed SVG Environment */}
      <div className="relative w-full h-full flex justify-center items-center">
        <svg viewBox="0 0 400 300" className="w-full max-w-3xl h-full overflow-visible transform -translate-x-12 -translate-y-6 scale-[0.75] origin-center">
          
          {/* LAYER 0: DESK */}
          <g id="desk">
            <path d="M 10 220 L 390 220 L 410 250 L -10 250 Z" fill="#F9FAFB" stroke="#E5E7EB" strokeWidth="2" strokeLinejoin="round" />
            <path d="M -10 250 L 410 250 L 410 270 L -10 270 Z" fill="#E5E7EB" />
            <ellipse cx="200" cy="275" rx="180" ry="15" fill="rgba(0,0,0,0.04)" />
          </g>

          {/* LAYER 1: STATIC PROPS */}
          <g id="static-props">
            <path d="M 120 225 L 280 225 L 300 245 L 100 245 Z" fill="#FFFFFF" stroke="#D1D5DB" strokeWidth="1" />
            
            <AnimatePresence>
              {(state === 'generation' || state === 'bridge_generation') && (
                <motion.path 
                  d="M 125 232 L 200 232 M 115 238 L 240 238" 
                  stroke="#3B82F6" strokeWidth="2" strokeDasharray="30"
                  initial={{ strokeDashoffset: 30, opacity: 0 }}
                  animate={{ strokeDashoffset: [30, 0, 30], opacity: 1 }}
                  exit={{ opacity: 0 }}
                  transition={{ repeat: Infinity, duration: 1, ease: "linear" }}
                />
              )}
            </AnimatePresence>

            <AnimatePresence>
              {state === 'reading' && (
                <motion.g initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                   <path d="M 140 225 L 200 235 L 260 225 L 250 245 L 200 255 L 150 245 Z" fill="#3B82F6" />
                   <path d="M 142 227 L 200 233 L 200 253 L 152 243 Z" fill="#FFFFFF" />
                   <path d="M 200 233 L 258 227 L 248 243 L 200 253 Z" fill="#F3F4F6" />
                   <motion.path 
                     d="M 200 233 L 258 227 L 248 243 L 200 253 Z" fill="#FFFFFF" 
                     variants={pageTurnVariants} animate={state === 'reading' ? 'reading' : 'idle'}
                     style={{ transformOrigin: "200px 233px" }}
                   />
                </motion.g>
              )}
            </AnimatePresence>

            <g transform="translate(320, 200)">
              <line x1="10" y1="5" x2="5" y2="-15" stroke="#FCD34D" strokeWidth="4" strokeLinecap="round" />
              <line x1="15" y1="5" x2="22" y2="-10" stroke="#EF4444" strokeWidth="3" strokeLinecap="round" />
              <rect x="0" y="5" width="25" height="30" rx="4" fill="#D1D5DB" />
              <ellipse cx="12.5" cy="5" rx="12.5" ry="4" fill="#9CA3AF" />
            </g>
          </g>

          {/* LAYER 2: DYNAMIC STACKS */}
          <g id="dynamic-stacks">
            <AnimatePresence>
              {[...Array(leftStackCount)].map((_, i) => (
                <path key={`left-${i}`} d={`M 50 ${235 - i*2} L 100 ${235 - i*2} L 90 ${245 - i*2} L 40 ${245 - i*2} Z`} fill="#FFFFFF" stroke="#D1D5DB" strokeWidth="1" />
              ))}
              {[...Array(rightStackCount)].map((_, i) => (
                <path key={`right-${i}`} d={`M 300 ${235 - i*2} L 350 ${235 - i*2} L 340 ${245 - i*2} L 290 ${245 - i*2} Z`} fill="#FFFFFF" stroke="#D1D5DB" strokeWidth="1" />
              ))}
            </AnimatePresence>
          </g>

          {/* LAYER 3: ROBOT BODY & ARTICULATED ARMS */}
          <motion.g 
            animate={state === 'transporting' ? { x: 150, opacity: 0 } : { x: 0, opacity: 1 }} 
            transition={{ duration: 2, ease: "easeInOut" }}
          >
            {/* BREATHING ANIMATION — Torso + Arms + Head move together so shoulders never detach */}
            <motion.g animate={{ y: [0, -3, 0] }} transition={{ repeat: Infinity, duration: 4, ease: "easeInOut" }}>
              {/* Neck */}
              <path d="M 180 115 Q 200 130 220 115 Z" fill="#9CA3AF" />
              
              {/* Torso */}
              <rect x="140" y="120" width="120" height="100" rx="30" fill="#FFFFFF" stroke="#E5E7EB" strokeWidth="2" />
              
              {/* Head */}
              <rect x="130" y="30" width="140" height="90" rx="25" fill="#FFFFFF" stroke="#E5E7EB" strokeWidth="2" />
              <rect x="145" y="45" width="110" height="60" rx="12" fill="#111827" />
              <motion.g animate={
                state === 'reading' ? { x: [-10, 10, -10], transition: { repeat: Infinity, duration: 2 } } : 
                state === 'generation' ? { scaleY: [1, 0.2, 1], transition: { repeat: Infinity, duration: 3, times: [0, 0.1, 0.2] } } :
                { x: 0 }
              }>
                <rect x="160" y="65" width="25" height="25" rx="6" fill="#3B82F6" />
                <rect x="215" y="65" width="25" height="25" rx="6" fill="#3B82F6" />
              </motion.g>

              {/* Fusion Flash VFX on Torso */}
              <motion.g variants={fusionFlashVariants} animate={activeState} initial="default" style={{ transformOrigin: "200px 170px" }}>
                <circle cx="200" cy="170" r="40" fill="url(#blueFlash)" style={{ mixBlendMode: 'screen' }} />
                <circle cx="200" cy="170" r="15" fill="#FFFFFF" filter="blur(2px)" />
              </motion.g>



              {/* Chest Glow */}
              <rect x="165" y="150" width="70" height="30" rx="10" fill="#E5E7EB" />
              <motion.circle cx="200" cy="165" r="5" fill="#3B82F6" animate={{ opacity: [0.3, 1, 0.3] }} transition={{ repeat: Infinity, duration: 2 }} />

              {/* Antennas */}
              <rect x="115" y="55" width="15" height="30" rx="5" fill="#9CA3AF" />
              <rect x="270" y="55" width="15" height="30" rx="5" fill="#9CA3AF" />

              {/* ============================================ */}
              {/* ARTICULATED RIGID ARMS (Pendulum Kinematics) */}
              {/* ============================================ */}
              {/*                                              */}
              {/* Each arm uses native SVG transform="rotate()"*/}
              {/* applied via refs, NOT CSS transforms.        */}
              {/* SVG rotate() always pivots around (0,0) of   */}
              {/* the local coordinate system = the joint.     */}
              {/*                                              */}
              {/* Shoulder = FIXED anchor (never translates)   */}
              {/* Elbow = MOBILE anchor (moves with upper arm) */}
              {/* ============================================ */}
              <g id="robot-arms">
                
                {/* LEFT ARM (Robot's Right, Viewer's Left) */}
                {/* Shoulder is at absolute position (130, 140) in the breathing group */}
                <g transform="translate(130, 140)">
                  {/* Upper arm group — rotates around (0,0) = shoulder joint */}
                  <g ref={lShoulderRef} transform="rotate(0)">
                    {/* Upper Arm Segment */}
                    <path d="M 0 0 L -30 35" stroke="#FFFFFF" strokeWidth="16" strokeLinecap="round" />
                    <path d="M 0 0 L -30 35" stroke="#D1D5DB" strokeWidth="2" fill="none" />
                    
                    {/* Shoulder Joint Circle (at rotation center, visually static) */}
                    <circle cx="0" cy="0" r="16" fill="#D1D5DB" />
                    <circle cx="0" cy="0" r="8" fill="#FFFFFF" />

                    {/* Elbow Joint & Forearm — positioned at end of upper arm */}
                    <g transform="translate(-30, 35)">
                      {/* Forearm group — rotates around (0,0) = elbow joint */}
                      <g ref={lElbowRef} transform="rotate(0)">
                        {/* Elbow Joint Circle */}
                        <circle cx="0" cy="0" r="14" fill="#D1D5DB" />
                        <circle cx="0" cy="0" r="6" fill="#FFFFFF" />
                        
                        {/* Forearm Segment */}
                        <path d="M 0 0 L 40 40" stroke="#FFFFFF" strokeWidth="14" strokeLinecap="round" />
                        <path d="M 0 0 L 40 40" stroke="#D1D5DB" strokeWidth="2" fill="none" />
                        
                        {/* Hand & Items */}
                        <g transform="translate(40, 40)">
                          <Hand />
                          
                          {/* Left Hand Card (for deduplication) */}
                          <motion.g variants={leftCardVariants} animate={activeState} initial="default">
                            <path d="M -15 0 L 15 -10 L 25 10 L -5 20 Z" fill="#FFFFFF" stroke="#9CA3AF" />
                          </motion.g>

                          {/* Pencil (for Generation) */}
                          <AnimatePresence>
                            {(state === 'generation' || state === 'bridge_generation') && (
                              <motion.g initial={{ opacity: 0, scale: 0 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0 }}>
                                <DetailedPencil />
                              </motion.g>
                            )}
                          </AnimatePresence>
                        </g>
                      </g>
                    </g>
                  </g>
                </g>

                {/* RIGHT ARM (Robot's Left, Viewer's Right) */}
                {/* Shoulder is at absolute position (270, 140) in the breathing group */}
                <g transform="translate(270, 140)">
                  {/* Upper arm group — rotates around (0,0) = shoulder joint */}
                  <g ref={rShoulderRef} transform="rotate(0)">
                    {/* Upper Arm Segment */}
                    <path d="M 0 0 L 30 35" stroke="#FFFFFF" strokeWidth="16" strokeLinecap="round" />
                    <path d="M 0 0 L 30 35" stroke="#D1D5DB" strokeWidth="2" fill="none" />
                    
                    {/* Shoulder Joint Circle (at rotation center, visually static) */}
                    <circle cx="0" cy="0" r="16" fill="#D1D5DB" />
                    <circle cx="0" cy="0" r="8" fill="#FFFFFF" />

                    {/* Elbow Joint & Forearm — positioned at end of upper arm */}
                    <g transform="translate(30, 35)">
                      {/* Forearm group — rotates around (0,0) = elbow joint */}
                      <g ref={rElbowRef} transform="rotate(0)">
                        {/* Elbow Joint Circle */}
                        <circle cx="0" cy="0" r="14" fill="#D1D5DB" />
                        <circle cx="0" cy="0" r="6" fill="#FFFFFF" />
                        
                        {/* Forearm Segment */}
                        <path d="M 0 0 L -40 40" stroke="#FFFFFF" strokeWidth="14" strokeLinecap="round" />
                        <path d="M 0 0 L -40 40" stroke="#D1D5DB" strokeWidth="2" fill="none" />
                        
                        {/* Hand & Items */}
                        <g transform="translate(-40, 40)">
                          <Hand />
                          
                          {/* Right Hand Card (for deduplication) */}
                          <motion.g variants={rightCardVariants} animate={activeState} initial="default">
                            <path d="M -25 10 L 5 20 L 15 0 L -15 -10 Z" fill="#FFFFFF" stroke="#9CA3AF" />
                          </motion.g>
                        </g>
                      </g>
                    </g>
                  </g>
                </g>
              </g>
            </motion.g>
          </motion.g>

          <defs>
            <radialGradient id="blueFlash" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="#93C5FD" stopOpacity="1" />
              <stop offset="50%" stopColor="#3B82F6" stopOpacity="0.6" />
              <stop offset="100%" stopColor="#1D4ED8" stopOpacity="0" />
            </radialGradient>
          </defs>
        </svg>
      </div>
    </div>
  );
}
