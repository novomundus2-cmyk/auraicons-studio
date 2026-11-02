import React from 'react';

export type StudioTab = 'archify' | 'cv' | 'library' | 'playground' | 'showcase';

interface HeaderProps {
  activeTab: StudioTab;
  setActiveTab: (tab: StudioTab) => void;
  onOpenExport: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  activeTab,
  setActiveTab,
  onOpenExport,
}) => {
  return (
    <header className="sticky top-0 z-40 flex flex-wrap items-center justify-between gap-4 px-6 py-3.5 bg-slate-950/85 backdrop-blur-xl border-b border-slate-800/80">
      {/* Zone 1: Single text element wordmark */}
      <div className="flex items-center gap-2.5 shrink-0">
        <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-gradient-to-tr from-indigo-600 via-sky-500 to-emerald-400 p-[1.5px] shadow-sm">
          <div className="flex h-full w-full items-center justify-center rounded-[10px] bg-slate-950">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" className="text-sky-400">
              <path
                d="M12 2l2.4 7.6 7.6 2.4-7.6 2.4L12 22l-2.4-7.6L2 12l7.6-2.4L12 2z"
                fill="currentColor"
              />
            </svg>
          </div>
        </div>
        <span className="text-base font-bold tracking-tight text-slate-100 font-display whitespace-nowrap shrink-0">
          NovusMundus · Archify &amp; AuraIcons <span className="text-xs font-normal text-sky-400 font-mono ml-1">Proyectos en Vivo</span>
        </span>
      </div>

      {/* Zone 2: Navigation links */}
      <nav className="flex flex-wrap items-center gap-4 text-xs sm:text-sm font-medium text-slate-400">
        <button
          onClick={() => setActiveTab('archify')}
          className={`transition-colors whitespace-nowrap shrink-0 hover:text-slate-100 ${
            activeTab === 'archify' ? 'text-emerald-400 font-extrabold' : ''
          }`}
        >
          🏛️ Pipeline &amp; Agentes en Directo
        </button>
        <button
          onClick={() => setActiveTab('cv')}
          className={`transition-colors whitespace-nowrap shrink-0 hover:text-slate-100 ${
            activeTab === 'cv' ? 'text-sky-400 font-extrabold' : ''
          }`}
        >
          🚀 Mi Conocimiento en Proyectos (NOVUSMUNDUS)
        </button>
        <button
          onClick={() => setActiveTab('library')}
          className={`transition-colors whitespace-nowrap shrink-0 hover:text-slate-100 ${
            activeTab === 'library' ? 'text-indigo-400 font-semibold' : ''
          }`}
        >
          ✨ Colección Iconos (48)
        </button>
        <button
          onClick={() => setActiveTab('playground')}
          className={`transition-colors whitespace-nowrap shrink-0 hover:text-slate-100 ${
            activeTab === 'playground' ? 'text-indigo-400 font-semibold' : ''
          }`}
        >
          🎛️ Taller &amp; Morph
        </button>
        <button
          onClick={() => setActiveTab('showcase')}
          className={`transition-colors whitespace-nowrap shrink-0 hover:text-slate-100 ${
            activeTab === 'showcase' ? 'text-indigo-400 font-semibold' : ''
          }`}
        >
          🌐 En Tu Web
        </button>
      </nav>

      {/* Zone 3: Primary action */}
      <div className="flex items-center gap-2.5 shrink-0">
        <button
          onClick={() => setActiveTab('cv')}
          className="px-3.5 py-2 text-xs font-extrabold text-slate-950 bg-emerald-400 hover:bg-emerald-300 rounded-xl transition-all shadow-md shadow-emerald-500/20 active:scale-95 whitespace-nowrap shrink-0"
        >
          🚀 Conocimiento en Proyectos
        </button>
        <button
          onClick={onOpenExport}
          className="px-4 py-2 text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-500 rounded-xl transition-all shadow-md shadow-indigo-600/20 active:scale-95 whitespace-nowrap shrink-0 flex items-center gap-1.5"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
            <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          Exportar Icono
        </button>
      </div>
    </header>
  );
};

