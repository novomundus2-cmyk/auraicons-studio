import { InteractiveIconDef, StudioSettings } from '../types/icon';

export function generateReactCode(icon: InteractiveIconDef, settings: StudioSettings): string {
  const componentName = `${icon.name.replace(/[^a-zA-Z0-9]/g, '')}Icon`;
  const primary = settings.primaryColor || '#60a5fa';

  if (icon.id === 'menu-morph') {
    return `import React, { useState } from 'react';
import { motion } from 'motion/react';

export const ${componentName}: React.FC<{ size?: number; className?: string }> = ({ size = ${settings.iconSize}, className = '' }) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <button
      onClick={() => setIsOpen(!isOpen)}
      className={\`inline-flex items-center justify-center p-2 rounded-xl transition-colors hover:bg-slate-800/60 \${className}\`}
      aria-label="Alternar menú"
    >
      <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="${primary}" strokeWidth="${settings.strokeWidth}" strokeLinecap="round">
        <motion.line
          x1="4" x2="20"
          animate={isOpen ? { y1: 12, y2: 12, rotate: 45, originX: '12px', originY: '12px' } : { y1: 7, y2: 7, rotate: 0 }}
          transition={{ type: 'spring', stiffness: 400, damping: 25 }}
        />
        <motion.line
          x1="4" y1="12" x2="20" y2="12"
          animate={isOpen ? { opacity: 0, scaleX: 0 } : { opacity: 1, scaleX: 1 }}
          transition={{ duration: 0.15 }}
        />
        <motion.line
          x1="4" x2="20"
          animate={isOpen ? { y1: 12, y2: 12, rotate: -45, originX: '12px', originY: '12px' } : { y1: 17, y2: 17, rotate: 0 }}
          transition={{ type: 'spring', stiffness: 400, damping: 25 }}
        />
      </svg>
    </button>
  );
};
`;
  }

  if (icon.id === 'heart-like') {
    return `import React, { useState } from 'react';
import { motion } from 'motion/react';

export const ${componentName}: React.FC<{ size?: number; className?: string }> = ({ size = ${settings.iconSize}, className = '' }) => {
  const [liked, setLiked] = useState(false);

  return (
    <motion.button
      whileTap={{ scale: 0.85 }}
      onClick={() => setLiked(!liked)}
      className={\`relative p-2.5 rounded-full transition-colors \${liked ? 'bg-rose-500/10 text-rose-500' : 'text-slate-400 hover:text-slate-200'} \${className}\`}
      aria-label="Dar me gusta"
    >
      <motion.svg
        width={size}
        height={size}
        viewBox="0 0 24 24"
        fill={liked ? 'currentColor' : 'none'}
        stroke="currentColor"
        strokeWidth="${settings.strokeWidth}"
        strokeLinejoin="round"
        animate={liked ? { scale: [1, 1.35, 0.95, 1.15, 1] } : { scale: 1 }}
        transition={{ duration: 0.45 }}
      >
        <path d="M20.84 4.61a5.5 5.5 0 00-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 00-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 000-7.78z" />
      </motion.svg>
    </motion.button>
  );
};
`;
  }

  // Generic motion component template
  const pathsJSX = icon.paths
    .map(
      (p) =>
        `        <path d="${p.d}" strokeLinecap="${p.strokeLinecap || 'round'}" strokeLinejoin="${p.strokeLinejoin || 'round'}" ${
          p.fill ? `fill="${p.fill}"` : 'fill="none"'
        } />`
    )
    .join('\n');

  return `import React from 'react';
import { motion } from 'motion/react';

export const ${componentName}: React.FC<{ size?: number; className?: string }> = ({ size = ${settings.iconSize}, className = '' }) => {
  return (
    <motion.div
      whileHover={{ y: -4, scale: 1.08 }}
      whileTap={{ scale: 0.94 }}
      transition={{ type: 'spring', stiffness: 400, damping: 20 }}
      className={\`inline-flex items-center justify-center p-2.5 rounded-2xl bg-slate-900/60 backdrop-blur-md border border-slate-800 text-[${primary}] cursor-pointer \${className}\`}
    >
      <svg
        width={size}
        height={size}
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="${settings.strokeWidth}"
      >
${pathsJSX}
      </svg>
    </motion.div>
  );
};
`;
}

export function generateHTMLCSSCode(icon: InteractiveIconDef, settings: StudioSettings): string {
  const primary = settings.primaryColor || '#38bdf8';
  const pathD = icon.paths.map((p) => `<path d="${p.d}" />`).join('\n    ');

  return `<!-- Icono Interactivo para tu web: ${icon.nameEs} -->
<style>
  .aura-icon-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 10px;
    border-radius: 14px;
    background: rgba(15, 23, 42, 0.7);
    border: 1px solid rgba(56, 189, 248, 0.25);
    color: ${primary};
    cursor: pointer;
    transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1),
                border-color 0.25s ease,
                box-shadow 0.25s ease;
  }
  .aura-icon-btn:hover {
    transform: translateY(-4px) scale(1.08);
    border-color: rgba(56, 189, 248, 0.7);
    box-shadow: 0 10px 25px -5px rgba(56, 189, 248, 0.35);
  }
  .aura-icon-btn:active {
    transform: scale(0.94);
  }
  .aura-icon-btn svg {
    stroke: currentColor;
    stroke-width: ${settings.strokeWidth};
    stroke-linecap: round;
    stroke-linejoin: round;
    fill: none;
    transition: stroke 0.2s ease;
  }
</style>

<button class="aura-icon-btn" aria-label="${icon.nameEs}">
  <svg width="${settings.iconSize}" height="${settings.iconSize}" viewBox="0 0 24 24">
    ${pathD}
  </svg>
</button>
`;
}

export function generatePureSVGCode(icon: InteractiveIconDef, settings: StudioSettings): string {
  const primary = settings.primaryColor || 'currentColor';
  const pathTags = icon.paths
    .map(
      (p) =>
        `  <path d="${p.d}" strokeLinecap="${p.strokeLinecap || 'round'}" strokeLinejoin="${p.strokeLinejoin || 'round'}" ${
          p.fill ? `fill="${p.fill}"` : 'fill="none"'
        } />`
    )
    .join('\n');

  return `<svg xmlns="http://www.w3.org/2000/svg" width="${settings.iconSize}" height="${settings.iconSize}" viewBox="0 0 24 24" fill="none" stroke="${primary}" stroke-width="${settings.strokeWidth}">
${pathTags}
</svg>`;
}

export function downloadSVGFile(icon: InteractiveIconDef, settings: StudioSettings) {
  const svgContent = generatePureSVGCode(icon, settings);
  const blob = new Blob([svgContent], { type: 'image/svg+xml' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${icon.id}-interactive-icon.svg`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
