import React, { useState } from 'react';
import { ICONS_LIST } from '../data/iconsList';
import { StudioSettings } from '../types/icon';
import { InteractiveIcon } from './InteractiveIcon';
import { soundEffects } from '../utils/audio';

interface WebContextsShowcaseProps {
  settings: StudioSettings;
  onSelectIcon: (id: string) => void;
  onOpenExport: () => void;
}

export const WebContextsShowcase: React.FC<WebContextsShowcaseProps> = ({
  settings,
  onSelectIcon,
  onOpenExport,
}) => {
  const [likes, setLikes] = useState(142);
  const [hasLiked, setHasLiked] = useState(false);
  const [bookmarked, setBookmarked] = useState(false);
  const [cartCount, setCartCount] = useState(2);
  const [rating, setRating] = useState(4);
  const [isCopied, setIsCopied] = useState(false);

  const getIcon = (id: string) => ICONS_LIST.find((i) => i.id === id) || ICONS_LIST[0];

  const handleLikeClick = () => {
    if (hasLiked) {
      setLikes((l) => l - 1);
      setHasLiked(false);
    } else {
      setLikes((l) => l + 1);
      setHasLiked(true);
    }
  };

  const handleShareClick = () => {
    soundEffects.playChime();
    setIsCopied(true);
    setTimeout(() => setIsCopied(false), 2000);
  };

  return (
    <div className="flex flex-col gap-10">
      <div>
        <div className="flex items-center gap-2 text-xs text-indigo-400 font-mono mb-1">
          <span>CASOS DE USO REALES</span>
          <span aria-hidden="true">·</span>
          <span>INTEGRACIÓN WEB</span>
        </div>
        <h3 className="text-2xl font-bold text-slate-100 font-display">
          Mira cómo lucen los iconos interactivos en tu sitio web
        </h3>
        <p className="text-sm text-slate-400 mt-1 max-w-2xl">
          Diseñados para elevar la tasa de interacción y deleitar al usuario con micro-animaciones fluidas a 60fps.
        </p>
      </div>

      {/* 1. Header / Navbar Simulation */}
      <div className="flex flex-col gap-3">
        <div className="flex items-center justify-between text-xs text-slate-400">
          <span className="font-semibold text-slate-200">1. Barra de Navegación (Header de tu Web)</span>
          <span className="font-mono text-slate-500">Prueba los botones de la derecha</span>
        </div>

        <div className="p-4 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white font-bold text-sm">
              ▲
            </div>
            <span className="font-display font-semibold text-slate-100 text-sm hidden sm:inline">
              NovaStudio
            </span>
          </div>

          <div className="hidden md:flex items-center gap-6 text-xs font-medium text-slate-400">
            <span className="text-slate-100 cursor-pointer">Productos</span>
            <span className="hover:text-slate-200 cursor-pointer transition-colors">Servicios</span>
            <span className="hover:text-slate-200 cursor-pointer transition-colors">Portafolio</span>
            <span className="hover:text-slate-200 cursor-pointer transition-colors">Nosotros</span>
          </div>

          {/* Interactive Icon Group in Navbar */}
          <div className="flex items-center gap-1.5 sm:gap-2">
            {/* Search */}
            <div onClick={() => onSelectIcon('search-lens')} title="Buscar">
              <InteractiveIcon
                icon={getIcon('search-lens')}
                size={18}
                strokeWidth={settings.strokeWidth}
                theme={settings.selectedTheme}
                containerShape="squircle"
                enableSound={settings.enableSound}
              />
            </div>

            {/* Notification Bell */}
            <div onClick={() => onSelectIcon('bell-notify')} title="Notificaciones">
              <InteractiveIcon
                icon={getIcon('bell-notify')}
                size={18}
                strokeWidth={settings.strokeWidth}
                theme={settings.selectedTheme}
                badge={3}
                containerShape="squircle"
                enableSound={settings.enableSound}
              />
            </div>

            {/* Shopping Cart */}
            <div
              onClick={() => {
                setCartCount((c) => c + 1);
                onSelectIcon('shopping-cart');
              }}
              title="Carrito de compra"
            >
              <InteractiveIcon
                icon={getIcon('shopping-cart')}
                size={18}
                strokeWidth={settings.strokeWidth}
                theme={settings.selectedTheme}
                badge={cartCount}
                containerShape="squircle"
                enableSound={settings.enableSound}
              />
            </div>

            {/* Theme Toggle Sun / Moon */}
            <div onClick={() => onSelectIcon('sun-moon')} title="Cambiar tema día/noche">
              <InteractiveIcon
                icon={getIcon('sun-moon')}
                size={18}
                strokeWidth={settings.strokeWidth}
                theme={settings.selectedTheme}
                triggerMode="click"
                containerShape="squircle"
                enableSound={settings.enableSound}
              />
            </div>

            {/* Mobile Hamburger / Morph */}
            <div onClick={() => onSelectIcon('menu-morph')} title="Menú hamburguesa que hace morph a cerrar">
              <InteractiveIcon
                icon={getIcon('menu-morph')}
                size={18}
                strokeWidth={settings.strokeWidth}
                theme={settings.selectedTheme}
                triggerMode="click"
                containerShape="squircle"
                enableSound={settings.enableSound}
              />
            </div>
          </div>
        </div>
      </div>

      {/* 2. Interactive Feature Bento Cards */}
      <div className="flex flex-col gap-3">
        <div className="flex items-center justify-between text-xs text-slate-400">
          <span className="font-semibold text-slate-200">2. Tarjetas de Características (Bento Grid)</span>
          <span className="font-mono text-slate-500">Pasa el ratón sobre cada tarjeta</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Card 1 */}
          <div
            onClick={() => onSelectIcon('rocket-thrust')}
            className="group relative p-6 rounded-3xl bg-slate-900/60 hover:bg-slate-900/90 border border-slate-800 hover:border-indigo-500/40 transition-all duration-300 cursor-pointer flex flex-col justify-between min-h-[220px]"
          >
            <div>
              <div className="mb-4">
                <InteractiveIcon
                  icon={getIcon('rocket-thrust')}
                  size={28}
                  strokeWidth={settings.strokeWidth}
                  theme="sunset"
                  containerShape="squircle"
                  enableSound={settings.enableSound}
                />
              </div>
              <h4 className="text-base font-semibold text-slate-100 font-display group-hover:text-indigo-300 transition-colors">
                Velocidad Ultrasónica
              </h4>
              <p className="text-xs text-slate-400 mt-1.5 leading-relaxed">
                Tiempos de respuesta inferiores a 100ms gracias a arquitectura distribuida edge.
              </p>
            </div>
            <div className="flex items-center gap-1 text-xs text-indigo-400 font-medium pt-3 border-t border-slate-800/80">
              <span>Explorar telemetría</span>
              <span className="transform group-hover:translate-x-1 transition-transform">→</span>
            </div>
          </div>

          {/* Card 2 */}
          <div
            onClick={() => onSelectIcon('brain-neural')}
            className="group relative p-6 rounded-3xl bg-slate-900/60 hover:bg-slate-900/90 border border-slate-800 hover:border-indigo-500/40 transition-all duration-300 cursor-pointer flex flex-col justify-between min-h-[220px]"
          >
            <div>
              <div className="mb-4">
                <InteractiveIcon
                  icon={getIcon('brain-neural')}
                  size={28}
                  strokeWidth={settings.strokeWidth}
                  theme="glass"
                  containerShape="squircle"
                  enableSound={settings.enableSound}
                />
              </div>
              <h4 className="text-base font-semibold text-slate-100 font-display group-hover:text-indigo-300 transition-colors">
                Sinapsis Predictiva
              </h4>
              <p className="text-xs text-slate-400 mt-1.5 leading-relaxed">
                Modelos de machine learning que anticipan la siguiente acción del visitante.
              </p>
            </div>
            <div className="flex items-center gap-1 text-xs text-indigo-400 font-medium pt-3 border-t border-slate-800/80">
              <span>Ver algoritmos</span>
              <span className="transform group-hover:translate-x-1 transition-transform">→</span>
            </div>
          </div>

          {/* Card 3 */}
          <div
            onClick={() => onSelectIcon('shield-verified')}
            className="group relative p-6 rounded-3xl bg-slate-900/60 hover:bg-slate-900/90 border border-slate-800 hover:border-indigo-500/40 transition-all duration-300 cursor-pointer flex flex-col justify-between min-h-[220px]"
          >
            <div>
              <div className="mb-4">
                <InteractiveIcon
                  icon={getIcon('shield-verified')}
                  size={28}
                  strokeWidth={settings.strokeWidth}
                  theme="emerald"
                  containerShape="squircle"
                  enableSound={settings.enableSound}
                />
              </div>
              <h4 className="text-base font-semibold text-slate-100 font-display group-hover:text-emerald-300 transition-colors">
                Cifrado Militar
              </h4>
              <p className="text-xs text-slate-400 mt-1.5 leading-relaxed">
                Protección punto a punto y verificación criptográfica en cada transacción.
              </p>
            </div>
            <div className="flex items-center gap-1 text-xs text-emerald-400 font-medium pt-3 border-t border-slate-800/80">
              <span>Auditoría de seguridad</span>
              <span className="transform group-hover:translate-x-1 transition-transform">→</span>
            </div>
          </div>
        </div>
      </div>

      {/* 3. Action Buttons & Social Reactions Bar */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-center">
        {/* Social Reactions Strip */}
        <div className="p-6 rounded-3xl bg-slate-900/60 border border-slate-800 flex flex-col gap-4">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-semibold text-slate-200 font-display">Barra de Reacciones para Artículos</h4>
            <span className="text-xs text-slate-500 font-mono">Haz clic para interactuar</span>
          </div>

          <div className="flex items-center gap-4 p-3 bg-slate-950/60 rounded-2xl border border-slate-800/80">
            {/* Heart with particle burst */}
            <div className="flex items-center gap-1.5">
              <div onClick={handleLikeClick}>
                <InteractiveIcon
                  icon={getIcon('heart-like')}
                  size={22}
                  strokeWidth={settings.strokeWidth}
                  theme={hasLiked ? 'sunset' : 'minimal'}
                  triggerMode="click"
                  enableParticles={true}
                  enableSound={settings.enableSound}
                  containerShape="circle"
                />
              </div>
              <span className="text-xs font-mono text-slate-300 tabular-nums">{likes}</span>
            </div>

            {/* Bookmark */}
            <div onClick={() => setBookmarked(!bookmarked)}>
              <InteractiveIcon
                icon={getIcon('tag-discount')}
                size={20}
                strokeWidth={settings.strokeWidth}
                theme={bookmarked ? 'neon' : 'minimal'}
                triggerMode="click"
                containerShape="circle"
                enableSound={settings.enableSound}
              />
            </div>

            {/* Star Rating */}
            <div className="flex items-center gap-0.5">
              {[1, 2, 3, 4, 5].map((s) => (
                <button
                  key={s}
                  onClick={() => {
                    setRating(s);
                    soundEffects.playPop();
                  }}
                  className={`p-1 transition-transform hover:scale-125 ${
                    s <= rating ? 'text-amber-400' : 'text-slate-600'
                  }`}
                  aria-label={`Calificar con ${s} estrellas`}
                >
                  ★
                </button>
              ))}
            </div>

            {/* Share */}
            <div className="ml-auto" onClick={handleShareClick}>
              <InteractiveIcon
                icon={getIcon('share-nodes')}
                size={18}
                strokeWidth={settings.strokeWidth}
                theme={isCopied ? 'emerald' : 'minimal'}
                containerShape="circle"
                enableSound={settings.enableSound}
              />
            </div>
          </div>
          {isCopied && (
            <p className="text-xs text-emerald-400 font-medium animate-fadeIn text-center">
              ✓ ¡Enlace copiado al portapapeles!
            </p>
          )}
        </div>

        {/* High-Converting CTA Buttons */}
        <div className="p-6 rounded-3xl bg-slate-900/60 border border-slate-800 flex flex-col gap-4">
          <h4 className="text-sm font-semibold text-slate-200 font-display">Botones CTA con Iconos Vivos</h4>
          <div className="flex flex-col sm:flex-row items-center gap-3">
            <button
              onClick={onOpenExport}
              className="group flex-1 w-full flex items-center justify-center gap-3 px-5 py-3 rounded-2xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-lg shadow-indigo-600/25 transition-all active:scale-95"
            >
              <span>Comenzar Ahora</span>
              <span className="transform group-hover:translate-x-1 transition-transform">
                <InteractiveIcon
                  icon={getIcon('arrow-slide')}
                  size={16}
                  strokeWidth={2.5}
                  theme="minimal"
                  containerShape="none"
                  enableSound={false}
                />
              </span>
            </button>

            <button
              onClick={onOpenExport}
              className="group flex-1 w-full flex items-center justify-center gap-2.5 px-5 py-3 rounded-2xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium border border-slate-700 transition-all active:scale-95"
            >
              <InteractiveIcon
                icon={getIcon('sparkle-ai')}
                size={16}
                strokeWidth={2}
                theme="duotone"
                containerShape="none"
                enableSound={false}
              />
              <span>Generar con IA</span>
            </button>
          </div>
          <p className="text-xs text-slate-400">
            El 73% de los usuarios reconoce antes una acción cuando está acompañada por un icono con micro-animación al hover.
          </p>
        </div>
      </div>
    </div>
  );
};
