import React from 'react';
import { InteractiveIconDef, StudioSettings, IconStyleTheme, TriggerMode, AnimationType } from '../types/icon';
import { InteractiveIcon } from './InteractiveIcon';

interface IconStudioCanvasProps {
  icon: InteractiveIconDef;
  settings: StudioSettings;
  onUpdateSettings: (partial: Partial<StudioSettings>) => void;
  onOpenExport: () => void;
}

export const IconStudioCanvas: React.FC<IconStudioCanvasProps> = ({
  icon,
  settings,
  onUpdateSettings,
  onOpenExport,
}) => {
  const themes: { id: IconStyleTheme; name: string; color: string }[] = [
    { id: 'glass', name: 'Glass Aura', color: '#60a5fa' },
    { id: 'neon', name: 'Cyber Neon', color: '#38bdf8' },
    { id: 'sunset', name: 'Sunset Rose', color: '#f43f5e' },
    { id: 'minimal', name: 'Minimal Monocromo', color: '#f8fafc' },
    { id: 'emerald', name: 'Emerald Tech', color: '#10b981' },
    { id: 'duotone', name: 'Duotone Pop', color: '#8b5cf6' },
  ];

  const animations: { id: AnimationType; label: string }[] = [
    { id: 'bounce', label: 'Rebote Elástico' },
    { id: 'morph', label: 'Morph / Transformación' },
    { id: 'pulse', label: 'Pulso Rítmico' },
    { id: 'glow', label: 'Resplandor Aura' },
    { id: 'spin', label: 'Rotación Giro' },
    { id: 'shake', label: 'Vibración / Dindán' },
    { id: 'tilt', label: 'Inclinación 3D' },
    { id: 'strokeDraw', label: 'Dibujo de Trazo' },
  ];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
      {/* Big Hero Interactive Stage */}
      <div className="lg:col-span-7 flex flex-col gap-4">
        <div className="relative flex flex-col items-center justify-center min-h-[440px] rounded-3xl bg-slate-900/60 border border-slate-800/80 p-8 overflow-hidden backdrop-blur-sm group">
          {/* Subtle grid pattern background */}
          <div
            className="absolute inset-0 opacity-[0.07] pointer-events-none"
            style={{
              backgroundImage: `radial-gradient(#94a3b8 1px, transparent 1px)`,
              backgroundSize: '24px 24px',
            }}
          />

          {/* Radial ambient lighting */}
          <div className="absolute w-72 h-72 rounded-full bg-indigo-500/10 blur-3xl pointer-events-none -top-10 -right-10" />
          <div className="absolute w-72 h-72 rounded-full bg-sky-500/10 blur-3xl pointer-events-none -bottom-10 -left-10" />

          {/* Badge indicator info */}
          <div className="absolute top-4 left-6 flex items-center gap-2 text-xs text-slate-400">
            <span className="font-semibold text-slate-200">{icon.nameEs}</span>
            <span aria-hidden="true">·</span>
            <span className="font-mono text-slate-500">#{icon.category}</span>
          </div>

          <div className="absolute top-4 right-6 flex items-center gap-1.5 bg-slate-800/70 border border-slate-700/60 rounded-xl px-2.5 py-1 text-xs text-slate-300">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            <span>Listo para interactuar</span>
          </div>

          {/* The Hero Interactive Icon */}
          <div className="my-auto transform transition-transform duration-300 flex flex-col items-center gap-6">
            <InteractiveIcon
              icon={icon}
              size={settings.iconSize * 1.5}
              strokeWidth={settings.strokeWidth}
              theme={settings.selectedTheme}
              triggerMode={settings.triggerMode}
              enableMagnetic={settings.enableMagnetic}
              enableSound={settings.enableSound}
              enableParticles={settings.enableParticles}
              containerShape={settings.containerShape}
              className="shadow-2xl"
            />
            <p className="text-xs text-slate-400 max-w-sm text-center">
              Pasa el ratón por encima, muévelo cerca o haz clic para probar la física y el sonido sintetizado.
            </p>
          </div>

          {/* Stage Bottom Controls Bar */}
          <div className="w-full flex flex-wrap items-center justify-between gap-3 pt-4 border-t border-slate-800/60 text-xs text-slate-400">
            <div className="flex items-center gap-2">
              <span>Disparador:</span>
              <div className="flex items-center gap-1 p-0.5 bg-slate-800/80 rounded-lg">
                {(['hover', 'click', 'loop'] as TriggerMode[]).map((mode) => (
                  <button
                    key={mode}
                    onClick={() => onUpdateSettings({ triggerMode: mode })}
                    className={`px-2.5 py-1 rounded-md transition-colors ${
                      settings.triggerMode === mode
                        ? 'bg-indigo-600 text-white font-medium'
                        : 'text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    {mode === 'hover' ? 'Hover' : mode === 'click' ? 'Click' : 'Loop Infinito'}
                  </button>
                ))}
              </div>
            </div>

            <button
              onClick={onOpenExport}
              className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 border border-indigo-500/30 font-medium transition-colors"
            >
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <path d="M16 4h2a2 2 0 012 2v14a2 2 0 01-2 2H6a2 2 0 01-2-2V6a2 2 0 012-2h2" strokeLinecap="round" strokeLinejoin="round" />
                <rect x="8" y="2" width="8" height="4" rx="1" ry="1" />
              </svg>
              Copiar Código de este Icono
            </button>
          </div>
        </div>

        {/* Behavior and Feedback Features Card */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div
            onClick={() => onUpdateSettings({ enableMagnetic: !settings.enableMagnetic })}
            className={`p-4 rounded-2xl border transition-all cursor-pointer ${
              settings.enableMagnetic
                ? 'bg-indigo-950/20 border-indigo-500/40 text-slate-200'
                : 'bg-slate-900/40 border-slate-800 text-slate-400 hover:border-slate-700'
            }`}
          >
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-xs font-semibold uppercase tracking-wider">Atracción Magnética</span>
              <span className={`text-[10px] px-2 py-0.5 rounded-md font-mono ${settings.enableMagnetic ? 'bg-indigo-500/20 text-indigo-300' : 'bg-slate-800 text-slate-500'}`}>
                {settings.enableMagnetic ? 'ACTIVO' : 'OFF'}
              </span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              El icono se inclina y persigue suavemente el puntero con física elástica.
            </p>
          </div>

          <div
            onClick={() => onUpdateSettings({ enableSound: !settings.enableSound })}
            className={`p-4 rounded-2xl border transition-all cursor-pointer ${
              settings.enableSound
                ? 'bg-sky-950/20 border-sky-500/40 text-slate-200'
                : 'bg-slate-900/40 border-slate-800 text-slate-400 hover:border-slate-700'
            }`}
          >
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-xs font-semibold uppercase tracking-wider">Audio Sintetizado</span>
              <span className={`text-[10px] px-2 py-0.5 rounded-md font-mono ${settings.enableSound ? 'bg-sky-500/20 text-sky-300' : 'bg-slate-800 text-slate-500'}`}>
                {settings.enableSound ? 'SONIDO' : 'MUDO'}
              </span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              Pops y chimes auditivos sutiles con Web Audio API en cada click y hover.
            </p>
          </div>

          <div
            onClick={() => onUpdateSettings({ enableParticles: !settings.enableParticles })}
            className={`p-4 rounded-2xl border transition-all cursor-pointer ${
              settings.enableParticles
                ? 'bg-fuchsia-950/20 border-fuchsia-500/40 text-slate-200'
                : 'bg-slate-900/40 border-slate-800 text-slate-400 hover:border-slate-700'
            }`}
          >
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-xs font-semibold uppercase tracking-wider">Chispas &amp; Confeti</span>
              <span className={`text-[10px] px-2 py-0.5 rounded-md font-mono ${settings.enableParticles ? 'bg-fuchsia-500/20 text-fuchsia-300' : 'bg-slate-800 text-slate-500'}`}>
                {settings.enableParticles ? 'ACTIVO' : 'OFF'}
              </span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              Explosión estelar de partículas físicas al hacer clic en acciones clave.
            </p>
          </div>
        </div>
      </div>

      {/* Customizer Sidebar */}
      <div className="lg:col-span-5 flex flex-col gap-6 p-6 rounded-3xl bg-slate-900/70 border border-slate-800/80">
        <div>
          <h4 className="text-base font-semibold text-slate-100 font-display">Personalizar Estilo &amp; Trazo</h4>
          <p className="text-xs text-slate-400 mt-0.5">Ajusta cada parámetro para adaptarlo a tu marca o web.</p>
        </div>

        {/* Preset Theme Selector */}
        <div className="flex flex-col gap-2">
          <label className="text-xs font-medium text-slate-300">Aura &amp; Paleta Visual</label>
          <div className="grid grid-cols-2 gap-2">
            {themes.map((th) => (
              <button
                key={th.id}
                onClick={() => onUpdateSettings({ selectedTheme: th.id })}
                className={`flex items-center gap-2.5 p-2.5 rounded-xl border text-left transition-all ${
                  settings.selectedTheme === th.id
                    ? 'bg-slate-800 border-indigo-500/80 text-white shadow-sm'
                    : 'bg-slate-950/40 border-slate-800/80 text-slate-400 hover:text-slate-200 hover:border-slate-700'
                }`}
              >
                <span
                  className="w-3.5 h-3.5 rounded-full shadow-sm shrink-0"
                  style={{ backgroundColor: th.color }}
                />
                <span className="text-xs font-medium truncate">{th.name}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Sliders: Size and Stroke */}
        <div className="flex flex-col gap-4 pt-2 border-t border-slate-800">
          <div>
            <div className="flex justify-between items-center text-xs mb-1.5">
              <span className="text-slate-300 font-medium">Tamaño del Icono</span>
              <span className="font-mono text-indigo-400 tabular-nums">{settings.iconSize}px</span>
            </div>
            <input
              type="range"
              min="20"
              max="64"
              step="2"
              value={settings.iconSize}
              onChange={(e) => onUpdateSettings({ iconSize: Number(e.target.value) })}
              className="w-full accent-indigo-500 bg-slate-800 h-1.5 rounded-lg cursor-pointer"
            />
          </div>

          <div>
            <div className="flex justify-between items-center text-xs mb-1.5">
              <span className="text-slate-300 font-medium">Grosor de Trazo (Stroke)</span>
              <span className="font-mono text-indigo-400 tabular-nums">{settings.strokeWidth}px</span>
            </div>
            <input
              type="range"
              min="1"
              max="3"
              step="0.25"
              value={settings.strokeWidth}
              onChange={(e) => onUpdateSettings({ strokeWidth: Number(e.target.value) })}
              className="w-full accent-indigo-500 bg-slate-800 h-1.5 rounded-lg cursor-pointer"
            />
          </div>
        </div>

        {/* Container Shape */}
        <div className="flex flex-col gap-2 pt-2 border-t border-slate-800">
          <label className="text-xs font-medium text-slate-300">Marco del Contenedor</label>
          <div className="flex items-center gap-1.5 p-1 bg-slate-950/60 rounded-xl border border-slate-800">
            {(
              [
                { id: 'squircle', label: 'Squircle' },
                { id: 'circle', label: 'Círculo' },
                { id: 'square', label: 'Cuadrado' },
                { id: 'none', label: 'Sin Marco' },
              ] as const
            ).map((shape) => (
              <button
                key={shape.id}
                onClick={() => onUpdateSettings({ containerShape: shape.id })}
                className={`flex-1 py-1.5 text-xs font-medium rounded-lg transition-colors ${
                  settings.containerShape === shape.id
                    ? 'bg-slate-800 text-white shadow-sm'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {shape.label}
              </button>
            ))}
          </div>
        </div>

        {/* Animation mode overwrite */}
        <div className="flex flex-col gap-2 pt-2 border-t border-slate-800">
          <label className="text-xs font-medium text-slate-300">Tipo de Micro-Animación</label>
          <div className="grid grid-cols-2 gap-1.5">
            {animations.map((anim) => (
              <button
                key={anim.id}
                onClick={() => {
                  icon.defaultAnimation = anim.id;
                  onUpdateSettings({});
                }}
                className={`py-1.5 px-2.5 text-xs text-left font-medium rounded-lg transition-colors truncate ${
                  icon.defaultAnimation === anim.id
                    ? 'bg-indigo-600/30 border border-indigo-500/50 text-indigo-200'
                    : 'bg-slate-950/40 border border-slate-800/80 text-slate-400 hover:text-slate-300'
                }`}
              >
                {anim.label}
              </button>
            ))}
          </div>
        </div>

        {/* CTA export */}
        <button
          onClick={onOpenExport}
          className="w-full py-3 px-4 rounded-xl font-semibold text-xs text-white bg-indigo-600 hover:bg-indigo-500 transition-all shadow-lg shadow-indigo-600/20 active:scale-[0.98] flex items-center justify-center gap-2 mt-2"
        >
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
            <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          Exportar y Copiar Código para mi Web
        </button>
      </div>
    </div>
  );
};
