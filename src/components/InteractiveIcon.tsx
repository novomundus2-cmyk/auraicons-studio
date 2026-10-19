import React, { useRef, useState } from 'react';
import { motion } from 'motion/react';
import confetti from 'canvas-confetti';
import { InteractiveIconDef, IconStyleTheme, AnimationType, TriggerMode } from '../types/icon';
import { soundEffects } from '../utils/audio';

interface InteractiveIconProps {
  icon: InteractiveIconDef;
  size?: number;
  strokeWidth?: number;
  theme?: IconStyleTheme;
  animation?: AnimationType;
  triggerMode?: TriggerMode;
  enableMagnetic?: boolean;
  enableSound?: boolean;
  enableParticles?: boolean;
  containerShape?: 'none' | 'squircle' | 'circle' | 'square' | 'glass';
  primaryColor?: string;
  secondaryColor?: string;
  accentColor?: string;
  badge?: string | number;
  isInspected?: boolean;
  onClick?: () => void;
  className?: string;
}

export const InteractiveIcon: React.FC<InteractiveIconProps> = ({
  icon,
  size = 28,
  strokeWidth = 2,
  theme = 'glass',
  animation = icon.defaultAnimation,
  triggerMode = 'hover',
  enableMagnetic = true,
  enableSound = true,
  enableParticles = false,
  containerShape = 'squircle',
  primaryColor,
  secondaryColor,
  accentColor,
  badge = icon.badge,
  isInspected = false,
  onClick,
  className = '',
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [isHovered, setIsHovered] = useState(false);
  const [isToggled, setIsToggled] = useState(false);
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });

  // Handle magnetic cursor pull
  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!enableMagnetic || triggerMode === 'loop') return;
    if (!containerRef.current) return;

    const rect = containerRef.current.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;

    const pullStrength = 0.28;
    const deltaX = (e.clientX - centerX) * pullStrength;
    const deltaY = (e.clientY - centerY) * pullStrength;

    setMousePos({ x: deltaX, y: deltaY });
  };

  const handleMouseEnter = () => {
    setIsHovered(true);
    if (enableSound && triggerMode !== 'click') {
      soundEffects.playHoverBlip();
    }
  };

  const handleMouseLeave = () => {
    setIsHovered(false);
    setMousePos({ x: 0, y: 0 });
  };

  const handleClick = (e: React.MouseEvent<HTMLDivElement>) => {
    const nextToggle = !isToggled;
    setIsToggled(nextToggle);

    if (enableSound) {
      if (icon.id === 'heart-like') {
        soundEffects.playPop();
      } else if (icon.id === 'copy-check') {
        soundEffects.playChime();
      } else if (icon.id === 'menu-morph' || icon.id === 'sun-moon' || icon.id === 'lock-secure') {
        soundEffects.playSwitch();
      } else {
        soundEffects.playPop();
      }
    }

    if (enableParticles && containerRef.current) {
      const rect = containerRef.current.getBoundingClientRect();
      const x = (rect.left + rect.width / 2) / window.innerWidth;
      const y = (rect.top + rect.height / 2) / window.innerHeight;

      confetti({
        particleCount: 16,
        spread: 45,
        startVelocity: 18,
        ticks: 50,
        origin: { x, y },
        colors: ['#38bdf8', '#818cf8', '#ec4899', '#34d399', '#f59e0b'],
        disableForReducedMotion: true,
      });
    }

    if (onClick) {
      onClick();
    }
  };

  // Determine active visual trigger
  const isTriggered =
    triggerMode === 'loop'
      ? true
      : triggerMode === 'click'
      ? isToggled
      : isHovered;

  // Resolve color palette based on theme
  const getThemeColors = () => {
    if (primaryColor) {
      return {
        stroke: primaryColor,
        secondary: secondaryColor || primaryColor,
        glow: accentColor || primaryColor,
        bgGlow: `rgba(99, 102, 241, 0.12)`,
      };
    }

    switch (theme) {
      case 'neon':
        return {
          stroke: '#38bdf8',
          secondary: '#c084fc',
          glow: 'rgba(56, 189, 248, 0.45)',
          bgGlow: 'rgba(56, 189, 248, 0.12)',
        };
      case 'sunset':
        return {
          stroke: '#f43f5e',
          secondary: '#fb923c',
          glow: 'rgba(244, 63, 94, 0.45)',
          bgGlow: 'rgba(244, 63, 94, 0.15)',
        };
      case 'minimal':
        return {
          stroke: '#f8fafc',
          secondary: '#94a3b8',
          glow: 'rgba(255, 255, 255, 0.2)',
          bgGlow: 'rgba(255, 255, 255, 0.05)',
        };
      case 'emerald':
        return {
          stroke: '#10b981',
          secondary: '#34d399',
          glow: 'rgba(16, 185, 129, 0.45)',
          bgGlow: 'rgba(16, 185, 129, 0.12)',
        };
      case 'cyber':
        return {
          stroke: '#06b6d4',
          secondary: '#ec4899',
          glow: 'rgba(6, 182, 212, 0.5)',
          bgGlow: 'rgba(6, 182, 212, 0.15)',
        };
      case 'duotone':
        return {
          stroke: '#8b5cf6',
          secondary: '#f59e0b',
          glow: 'rgba(139, 92, 246, 0.45)',
          bgGlow: 'rgba(139, 92, 246, 0.12)',
        };
      case 'glass':
      default:
        return {
          stroke: '#60a5fa',
          secondary: '#a78bfa',
          glow: 'rgba(96, 165, 250, 0.4)',
          bgGlow: 'rgba(96, 165, 250, 0.12)',
        };
    }
  };

  const colors = getThemeColors();

  // Container styling classes
  const getContainerClasses = () => {
    const base = 'relative inline-flex items-center justify-center transition-all duration-300 select-none';
    if (containerShape === 'none') return `${base} p-1`;

    let shapeClasses = 'rounded-2xl';
    if (containerShape === 'circle') shapeClasses = 'rounded-full';
    if (containerShape === 'square') shapeClasses = 'rounded-xl';
    if (containerShape === 'squircle') shapeClasses = 'rounded-[22%]';

    const glassStyle =
      'bg-slate-900/60 backdrop-blur-md border border-slate-700/50 shadow-sm hover:border-slate-500/60';
    return `${base} ${shapeClasses} ${glassStyle} p-3 cursor-pointer`;
  };

  // Specific Morph Renderers
  const renderIconPaths = () => {
    // 1. Morph: Hamburger to X
    if (icon.id === 'menu-morph') {
      return (
        <g stroke={colors.stroke} strokeWidth={strokeWidth} strokeLinecap="round">
          <motion.line
            x1="4"
            x2="20"
            animate={
              isTriggered
                ? { y1: 12, y2: 12, rotate: 45, originX: '12px', originY: '12px' }
                : { y1: 7, y2: 7, rotate: 0 }
            }
            transition={{ type: 'spring', stiffness: 400, damping: 25 }}
          />
          <motion.line
            x1="4"
            y1="12"
            x2="20"
            y2="12"
            animate={isTriggered ? { opacity: 0, scaleX: 0 } : { opacity: 1, scaleX: 1 }}
            transition={{ duration: 0.15 }}
          />
          <motion.line
            x1="4"
            x2="20"
            animate={
              isTriggered
                ? { y1: 12, y2: 12, rotate: -45, originX: '12px', originY: '12px' }
                : { y1: 17, y2: 17, rotate: 0 }
            }
            transition={{ type: 'spring', stiffness: 400, damping: 25 }}
          />
        </g>
      );
    }

    // 2. Morph: Sun to Moon (Theme toggle)
    if (icon.id === 'sun-moon') {
      return (
        <g stroke={colors.stroke} strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round" fill="none">
          {/* Sun Rays */}
          <motion.g
            animate={
              isTriggered
                ? { rotate: 90, scale: 0, opacity: 0, originX: '12px', originY: '12px' }
                : { rotate: 0, scale: 1, opacity: 1, originX: '12px', originY: '12px' }
            }
            transition={{ duration: 0.25 }}
          >
            <line x1="12" y1="2" x2="12" y2="4" />
            <line x1="12" y1="20" x2="12" y2="22" />
            <line x1="2" y1="12" x2="4" y2="12" />
            <line x1="20" y1="12" x2="22" y2="12" />
            <line x1="4.93" y1="4.93" x2="6.34" y2="6.34" />
            <line x1="17.66" y1="17.66" x2="19.07" y2="19.07" />
            <line x1="4.93" y1="19.07" x2="6.34" y2="17.66" />
            <line x1="17.66" y1="6.34" x2="19.07" y2="4.93" />
          </motion.g>

          {/* Center Body (Circle morphs to Moon crescent) */}
          <motion.path
            animate={
              isTriggered
                ? {
                    d: 'M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z',
                    fill: colors.secondary,
                    fillOpacity: 0.25,
                    rotate: -15,
                  }
                : {
                    d: 'M12 7a5 5 0 1 0 0 10 5 5 0 0 0 0-10z',
                    fill: 'none',
                    fillOpacity: 0,
                    rotate: 0,
                  }
            }
            transition={{ type: 'spring', stiffness: 350, damping: 22 }}
          />
        </g>
      );
    }

    // 3. Morph: Play to Pause
    if (icon.id === 'play-pause') {
      return (
        <g stroke={colors.stroke} strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round" fill="none">
          <motion.path
            animate={
              isTriggered
                ? {
                    d: 'M6 4h4v16H6z M14 4h4v16h-4z',
                    fill: colors.secondary,
                    fillOpacity: 0.2,
                  }
                : {
                    d: 'M5 3l14 9-14 9V3z',
                    fill: colors.stroke,
                    fillOpacity: 0.15,
                  }
            }
            transition={{ type: 'spring', stiffness: 450, damping: 24 }}
          />
        </g>
      );
    }

    // 4. Morph: Copy to Checkmark
    if (icon.id === 'copy-check') {
      return (
        <g stroke={isTriggered ? '#10b981' : colors.stroke} strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round" fill="none">
          <motion.path
            animate={
              isTriggered
                ? {
                    d: 'M4 12l5 5L20 6',
                    strokeDashoffset: [20, 0],
                  }
                : {
                    d: 'M8 4v12a2 2 0 002 2h8a2 2 0 002-2V7.24a2 2 0 00-.59-1.41l-2.24-2.24A2 2 0 0015.76 3H10a2 2 0 00-2 2z',
                  }
            }
            transition={{ duration: 0.25 }}
          />
          {!isTriggered && (
            <path d="M16 4h-2a2 2 0 00-2 2v10" />
          )}
        </g>
      );
    }

    // 5. Morph: Lock to Unlock
    if (icon.id === 'lock-secure') {
      return (
        <g stroke={colors.stroke} strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round" fill="none">
          <rect x="5" y="11" width="14" height="11" rx="2" ry="2" />
          <motion.path
            d="M7 11V7a5 5 0 0110 0v4"
            animate={
              isTriggered
                ? { y: -4, rotate: -20, originX: '7px', originY: '7px' }
                : { y: 0, rotate: 0 }
            }
            transition={{ type: 'spring', stiffness: 400, damping: 20 }}
          />
          <circle cx="12" cy="16" r="1.5" fill={colors.stroke} />
        </g>
      );
    }

    // 6. Morph: Eye Open to Wink / Blink
    if (icon.id === 'eye-look') {
      return (
        <g stroke={colors.stroke} strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round" fill="none">
          <motion.path
            d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"
            animate={isTriggered ? { scaleY: 0.15, originY: '12px' } : { scaleY: 1 }}
            transition={{ duration: 0.18 }}
          />
          <motion.circle
            cx="12"
            cy="12"
            r="3"
            fill={colors.secondary}
            animate={isTriggered ? { opacity: 0 } : { opacity: 1 }}
          />
        </g>
      );
    }

    // Default icon path renderer with enhanced animation styles
    return (
      <g stroke={colors.stroke} strokeWidth={strokeWidth} fill="none">
        {icon.paths.map((p, idx) => (
          <motion.path
            key={idx}
            d={p.d}
            stroke={p.stroke || colors.stroke}
            fill={p.fill === 'currentColor' ? colors.stroke : p.fill || 'none'}
            strokeWidth={p.strokeWidth || strokeWidth}
            strokeLinecap={p.strokeLinecap || 'round'}
            strokeLinejoin={p.strokeLinejoin || 'round'}
            animate={
              animation === 'strokeDraw' && isTriggered
                ? { pathLength: [0.1, 1], opacity: [0.3, 1] }
                : undefined
            }
            transition={{ duration: 0.5, ease: 'easeInOut' }}
          />
        ))}
      </g>
    );
  };

  // Motion dynamics for the entire icon SVG
  const getMotionProps = () => {
    switch (animation) {
      case 'bounce':
        return {
          animate: isTriggered
            ? { y: -5, scale: 1.1 }
            : { y: 0, scale: 1 },
          transition: { type: 'spring' as const, stiffness: 450, damping: 15 },
        };
      case 'heartbeat':
        return {
          animate: isTriggered
            ? { scale: [1, 1.25, 0.95, 1.15, 1] }
            : { scale: 1 },
          transition: { duration: 0.55, ease: 'easeInOut' as const },
        };
      case 'spin':
        return {
          animate: isTriggered
            ? triggerMode === 'loop'
              ? { rotate: 360 }
              : { rotate: 180 }
            : { rotate: 0 },
          transition:
            triggerMode === 'loop'
              ? { repeat: Infinity, duration: 4, ease: 'linear' as const }
              : { type: 'spring' as const, stiffness: 300, damping: 20 },
        };
      case 'pulse':
        return {
          animate: isTriggered
            ? { scale: [1, 1.15, 1], opacity: [0.9, 1, 0.9] }
            : { scale: 1, opacity: 1 },
          transition: { repeat: triggerMode === 'loop' ? Infinity : 1, duration: 0.6 },
        };
      case 'glow':
        return {
          animate: isTriggered
            ? {
                scale: 1.08,
                filter: `drop-shadow(0 0 10px ${colors.glow}) drop-shadow(0 0 20px ${colors.glow})`,
              }
            : { scale: 1, filter: 'drop-shadow(0 0 0px transparent)' },
          transition: { duration: 0.25 },
        };
      case 'shake':
        return {
          animate: isTriggered
            ? { rotate: [0, -14, 14, -10, 10, -5, 5, 0] }
            : { rotate: 0 },
          transition: { duration: 0.55 },
        };
      case 'tilt':
        return {
          animate: isTriggered
            ? { rotateX: 18, rotateY: -18, scale: 1.06 }
            : { rotateX: 0, rotateY: 0, scale: 1 },
          transition: { type: 'spring' as const, stiffness: 350, damping: 20 },
        };
      case 'burst':
        return {
          animate: isTriggered
            ? { scale: [1, 0.85, 1.25, 1] }
            : { scale: 1 },
          transition: { duration: 0.4, ease: 'easeOut' as const },
        };
      case 'strokeDraw':
      default:
        return {
          animate: isTriggered ? { scale: 1.06 } : { scale: 1 },
          transition: { duration: 0.2 },
        };
    }
  };

  const motionProps = getMotionProps();

  return (
    <div
      ref={containerRef}
      onMouseMove={handleMouseMove}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      onClick={handleClick}
      className={`${getContainerClasses()} ${className}`}
      style={{
        boxShadow: isTriggered && theme === 'neon' ? `0 0 25px ${colors.glow}` : undefined,
      }}
      title={`${icon.nameEs} (${icon.name})`}
    >
      {/* Ambient background glow orb */}
      {isTriggered && (
        <motion.div
          layoutId={`aura-${icon.id}`}
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 0.35, scale: 1.3 }}
          exit={{ opacity: 0, scale: 0.8 }}
          transition={{ duration: 0.25 }}
          className="absolute inset-0 pointer-events-none rounded-full blur-xl"
          style={{ background: colors.glow }}
        />
      )}

      {/* Main Animated SVG Container with Magnetic Offset */}
      <motion.div
        animate={{
          x: mousePos.x,
          y: mousePos.y,
        }}
        transition={{ type: 'spring', stiffness: 350, damping: 25, mass: 0.4 }}
        className="relative z-10 flex items-center justify-center"
      >
        <motion.svg
          width={size}
          height={size}
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          {...motionProps}
          style={{
            transformOrigin: 'center center',
            overflow: 'visible',
          }}
        >
          {renderIconPaths()}
        </motion.svg>
      </motion.div>

      {/* Dynamic Badge pip (e.g., notification count) */}
      {badge !== undefined && (
        <motion.span
          initial={{ scale: 0 }}
          animate={{ scale: isTriggered ? [1, 1.25, 1] : 1 }}
          transition={{ duration: 0.3 }}
          className="absolute -top-1 -right-1 z-20 flex h-4 min-w-4 items-center justify-center rounded-full bg-rose-500 px-1 text-[9px] font-bold text-white shadow-sm ring-2 ring-slate-900 tabular-nums"
        >
          {badge}
        </motion.span>
      )}

      {/* Inspecting ring highlight */}
      {isInspected && (
        <span className="absolute inset-0 rounded-2xl ring-2 ring-indigo-400 ring-offset-2 ring-offset-slate-950 pointer-events-none" />
      )}
    </div>
  );
};
