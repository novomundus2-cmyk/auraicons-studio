/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useMemo } from 'react';
import { ICONS_LIST } from './data/iconsList';
import { IconCategory, InteractiveIconDef, StudioSettings } from './types/icon';
import { Header } from './components/Header';
import { InteractiveIcon } from './components/InteractiveIcon';
import { IconStudioCanvas } from './components/IconStudioCanvas';
import { WebContextsShowcase } from './components/WebContextsShowcase';
import { CodeExportModal } from './components/CodeExportModal';
import { soundEffects } from './utils/audio';

export default function App() {
  const [activeTab, setActiveTab] = useState<'library' | 'playground' | 'showcase'>('library');
  const [selectedIconId, setSelectedIconId] = useState<string>('sparkle-ai');
  const [isExportModalOpen, setIsExportModalOpen] = useState<boolean>(false);
  const [quickCopiedId, setQuickCopiedId] = useState<string | null>(null);

  const [settings, setSettings] = useState<StudioSettings>({
    searchQuery: '',
    selectedCategory: 'all',
    selectedTheme: 'glass',
    strokeWidth: 2,
    iconSize: 32,
    primaryColor: '',
    secondaryColor: '',
    accentColor: '',
    animationSpeed: 1,
    triggerMode: 'hover',
    enableMagnetic: true,
    enableSound: true,
    enableParticles: true,
    containerShape: 'squircle',
  });

  const handleUpdateSettings = (partial: Partial<StudioSettings>) => {
    setSettings((prev) => {
      const next = { ...prev, ...partial };
      if (partial.enableSound !== undefined) {
        soundEffects.setMuted(!partial.enableSound);
      }
      return next;
    });
  };

  const categories: { id: IconCategory; label: string }[] = [
    { id: 'all', label: 'Todos' },
    { id: 'navigation', label: 'Navegación' },
    { id: 'actions', label: 'Acciones' },
    { id: 'commerce', label: 'Comercio' },
    { id: 'media', label: 'Multimedia' },
    { id: 'interface', label: 'Interfaz' },
    { id: 'social', label: 'Social & Rating' },
    { id: 'tech', label: 'Tecnología & IA' },
  ];

  // Filtered icons
  const filteredIcons = useMemo(() => {
    return ICONS_LIST.filter((icon) => {
      const matchCat =
        settings.selectedCategory === 'all' || icon.category === settings.selectedCategory;
      const query = settings.searchQuery.toLowerCase().trim();
      const matchQuery =
        !query ||
        icon.name.toLowerCase().includes(query) ||
        icon.nameEs.toLowerCase().includes(query) ||
        icon.tags.some((t) => t.toLowerCase().includes(query));
      return matchCat && matchQuery;
    });
  }, [settings.selectedCategory, settings.searchQuery]);

  const selectedIcon: InteractiveIconDef =
    ICONS_LIST.find((i) => i.id === selectedIconId) || ICONS_LIST[0];

  const handleQuickCopy = (icon: InteractiveIconDef, e: React.MouseEvent) => {
    e.stopPropagation();
    soundEffects.playChime();
    setQuickCopiedId(icon.id);
    setSelectedIconId(icon.id);
    setIsExportModalOpen(true);
    setTimeout(() => setQuickCopiedId(null), 1800);
  };

  return (
    <div className="min-h-screen bg-[#090d16] text-slate-100 flex flex-col selection:bg-indigo-500/30 selection:text-indigo-200">
      {/* 3-Zone Top Bar Contract */}
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onOpenExport={() => setIsExportModalOpen(true)}
      />

      {/* Main Container */}
      <main className="flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex flex-col gap-8">
        {/* Editorial Hero Header */}
        <div className="flex flex-col gap-2 pt-2">
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <span className="text-indigo-400 font-semibold font-mono">AURAICONS STUDIO</span>
            <span aria-hidden="true">·</span>
            <span>Iconos Web Vivos con Micro-Física</span>
            <span aria-hidden="true">·</span>
            <span className="font-mono text-slate-500">60 FPS</span>
          </div>

          <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
            <div>
              <h1 className="text-3xl sm:text-4xl font-bold tracking-tight text-white font-display text-balance">
                Iconos interactivos y animados para tus páginas web
              </h1>
              <p className="text-sm text-slate-400 mt-1.5 max-w-2xl leading-relaxed">
                Reacción al cursor, morphing vectorial, feedback sonoro opcional y código listo para React y HTML/CSS.
              </p>
            </div>

            {/* Quick Status Pill-less metadata & Sound Toggle */}
            <div className="flex items-center gap-3 shrink-0">
              <button
                onClick={() => handleUpdateSettings({ enableSound: !settings.enableSound })}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-xl border text-xs font-medium transition-colors ${
                  settings.enableSound
                    ? 'bg-slate-900 border-indigo-500/50 text-indigo-300'
                    : 'bg-slate-950 border-slate-800 text-slate-500 hover:text-slate-400'
                }`}
                title="Activar/desactivar sonido sintetizado"
              >
                <span>{settings.enableSound ? '🔊 Audio Activo' : '🔇 Audio Silenciado'}</span>
              </button>

              <button
                onClick={() => handleUpdateSettings({ enableMagnetic: !settings.enableMagnetic })}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-xl border text-xs font-medium transition-colors ${
                  settings.enableMagnetic
                    ? 'bg-slate-900 border-sky-500/50 text-sky-300'
                    : 'bg-slate-950 border-slate-800 text-slate-500 hover:text-slate-400'
                }`}
                title="Atracción magnética del cursor"
              >
                <span>{settings.enableMagnetic ? '🧲 Magnético' : '🧲 Estático'}</span>
              </button>
            </div>
          </div>
        </div>

        {/* View Switcher Bar */}
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div className="flex items-center gap-1 p-1 bg-slate-900/90 rounded-2xl border border-slate-800/80">
            <button
              onClick={() => setActiveTab('library')}
              className={`px-4 py-1.5 text-xs font-semibold rounded-xl transition-all ${
                activeTab === 'library'
                  ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Colección Completa ({ICONS_LIST.length})
            </button>
            <button
              onClick={() => setActiveTab('playground')}
              className={`px-4 py-1.5 text-xs font-semibold rounded-xl transition-all ${
                activeTab === 'playground'
                  ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Taller de Ajustes ({selectedIcon.nameEs})
            </button>
            <button
              onClick={() => setActiveTab('showcase')}
              className={`px-4 py-1.5 text-xs font-semibold rounded-xl transition-all ${
                activeTab === 'showcase'
                  ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Simulador en Tu Web
            </button>
          </div>

          <div className="hidden sm:flex items-center gap-2 text-xs text-slate-500">
            <span>Tema activo:</span>
            <span className="font-semibold text-slate-300 capitalize">{settings.selectedTheme}</span>
          </div>
        </div>

        {/* TAB 1: LIBRARY VIEW */}
        {activeTab === 'library' && (
          <div className="flex flex-col gap-6">
            {/* Filter and Search Controls */}
            <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-4">
              {/* Category Segmented Buttons */}
              <div className="flex items-center gap-1.5 overflow-x-auto pb-1 scrollbar-none">
                {categories.map((cat) => (
                  <button
                    key={cat.id}
                    onClick={() => handleUpdateSettings({ selectedCategory: cat.id })}
                    className={`px-3 py-1.5 text-xs font-medium rounded-xl whitespace-nowrap transition-colors shrink-0 ${
                      settings.selectedCategory === cat.id
                        ? 'bg-slate-800 text-indigo-300 border border-indigo-500/40 shadow-sm'
                        : 'bg-slate-950/60 text-slate-400 hover:text-slate-200 border border-slate-800/80'
                    }`}
                  >
                    {cat.label}
                  </button>
                ))}
              </div>

              {/* Search input */}
              <div className="relative min-w-[240px]">
                <div className="absolute inset-y-0 left-3 flex items-center pointer-events-none text-slate-500">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="11" cy="11" r="8" />
                    <line x1="21" y1="21" x2="16.65" y2="16.65" />
                  </svg>
                </div>
                <input
                  type="text"
                  placeholder="Buscar icono o efecto (ej. corazón, cart, sol...)"
                  value={settings.searchQuery}
                  onChange={(e) => handleUpdateSettings({ searchQuery: e.target.value })}
                  className="w-full bg-slate-900/90 border border-slate-800 rounded-xl pl-9 pr-8 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-colors"
                />
                {settings.searchQuery && (
                  <button
                    onClick={() => handleUpdateSettings({ searchQuery: '' })}
                    className="absolute inset-y-0 right-2.5 flex items-center text-slate-500 hover:text-slate-300 text-xs"
                  >
                    ✕
                  </button>
                )}
              </div>
            </div>

            {/* Quick Theme Selector Bar */}
            <div className="flex items-center gap-2 overflow-x-auto py-1 text-xs text-slate-400">
              <span className="shrink-0 font-medium text-slate-500">Estilos Visuales:</span>
              {(
                [
                  { id: 'glass', label: 'Glass Aura' },
                  { id: 'neon', label: 'Cyber Neon' },
                  { id: 'sunset', label: 'Sunset Glow' },
                  { id: 'minimal', label: 'Minimal Clean' },
                  { id: 'emerald', label: 'Emerald Mint' },
                  { id: 'duotone', label: 'Duotone Pop' },
                ] as const
              ).map((th) => (
                <button
                  key={th.id}
                  onClick={() => handleUpdateSettings({ selectedTheme: th.id })}
                  className={`px-3 py-1 rounded-lg border text-xs whitespace-nowrap transition-colors ${
                    settings.selectedTheme === th.id
                      ? 'bg-slate-800 border-indigo-400 text-white font-medium'
                      : 'bg-slate-950/40 border-slate-800/80 text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {th.label}
                </button>
              ))}
            </div>

            {/* Icons Grid */}
            {filteredIcons.length === 0 ? (
              <div className="flex flex-col items-center justify-center p-12 text-center rounded-3xl bg-slate-900/40 border border-slate-800">
                <span className="text-3xl mb-2">🔍</span>
                <p className="text-sm font-semibold text-slate-300 font-display">No se encontraron iconos</p>
                <p className="text-xs text-slate-500 mt-1">
                  Intenta buscar con otra palabra clave como &quot;menú&quot;, &quot;fuego&quot;, &quot;carrito&quot;, o &quot;nube&quot;.
                </p>
                <button
                  onClick={() => handleUpdateSettings({ searchQuery: '', selectedCategory: 'all' })}
                  className="mt-4 px-3 py-1.5 text-xs text-indigo-400 hover:underline"
                >
                  Limpiar búsqueda
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3.5">
                {filteredIcons.map((icon) => {
                  const isSelected = selectedIconId === icon.id;
                  return (
                    <div
                      key={icon.id}
                      onClick={() => {
                        setSelectedIconId(icon.id);
                        if (activeTab === 'library') {
                          // Allow quick inspection
                        }
                      }}
                      className={`group relative p-4 rounded-2xl border transition-all duration-200 flex flex-col items-center justify-between gap-3 text-center cursor-pointer ${
                        isSelected
                          ? 'bg-slate-800/90 border-indigo-500/70 shadow-lg shadow-indigo-500/10'
                          : 'bg-slate-900/50 hover:bg-slate-900 border-slate-800/90 hover:border-slate-700'
                      }`}
                    >
                      {/* Icon Container */}
                      <div className="my-2">
                        <InteractiveIcon
                          icon={icon}
                          size={settings.iconSize}
                          strokeWidth={settings.strokeWidth}
                          theme={settings.selectedTheme}
                          triggerMode={settings.triggerMode}
                          enableMagnetic={settings.enableMagnetic}
                          enableSound={settings.enableSound}
                          enableParticles={settings.enableParticles}
                          containerShape={settings.containerShape}
                          isInspected={isSelected}
                        />
                      </div>

                      {/* Icon Details */}
                      <div className="w-full flex flex-col items-center">
                        <span className="text-xs font-semibold text-slate-200 group-hover:text-white transition-colors truncate max-w-full">
                          {icon.nameEs}
                        </span>
                        <span className="text-[10px] text-slate-500 font-mono capitalize">
                          {icon.category}
                        </span>
                      </div>

                      {/* Hover action bar */}
                      <div className="w-full flex items-center justify-center gap-1.5 pt-2 border-t border-slate-800/80 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setSelectedIconId(icon.id);
                            setActiveTab('playground');
                          }}
                          className="px-2 py-1 text-[10px] font-medium text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-700 rounded-md transition-colors"
                          title="Ajustar en Taller"
                        >
                          Ajustar
                        </button>
                        <button
                          onClick={(e) => handleQuickCopy(icon, e)}
                          className="px-2 py-1 text-[10px] font-medium text-indigo-300 hover:text-white bg-indigo-600/30 hover:bg-indigo-600 rounded-md transition-colors"
                          title="Copiar código listo"
                        >
                          {quickCopiedId === icon.id ? '✓ Listo' : 'Código'}
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}

        {/* TAB 2: PLAYGROUND / INSPECTOR VIEW */}
        {activeTab === 'playground' && (
          <div className="flex flex-col gap-6">
            <IconStudioCanvas
              icon={selectedIcon}
              settings={settings}
              onUpdateSettings={handleUpdateSettings}
              onOpenExport={() => setIsExportModalOpen(true)}
            />
          </div>
        )}

        {/* TAB 3: SHOWCASE / IN YOUR WEB */}
        {activeTab === 'showcase' && (
          <WebContextsShowcase
            settings={settings}
            onSelectIcon={(id) => {
              setSelectedIconId(id);
              setActiveTab('playground');
            }}
            onOpenExport={() => setIsExportModalOpen(true)}
          />
        )}
      </main>

      {/* Code Export Modal */}
      <CodeExportModal
        icon={selectedIcon}
        settings={settings}
        isOpen={isExportModalOpen}
        onClose={() => setIsExportModalOpen(false)}
      />

      {/* Quiet Footer */}
      <footer className="border-t border-slate-800/80 py-6 px-6 text-center text-xs text-slate-500">
        <p>AuraIcons Studio · Iconos vectoriales interactivos para la web moderna · Exportable en React, SVG y CSS.</p>
      </footer>
    </div>
  );
}
