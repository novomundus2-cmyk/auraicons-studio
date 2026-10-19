import React, { useState } from 'react';
import { InteractiveIconDef, StudioSettings } from '../types/icon';
import { generateReactCode, generateHTMLCSSCode, generatePureSVGCode, downloadSVGFile } from '../utils/codeGenerators';

interface CodeExportModalProps {
  icon: InteractiveIconDef | null;
  settings: StudioSettings;
  isOpen: boolean;
  onClose: () => void;
}

export const CodeExportModal: React.FC<CodeExportModalProps> = ({
  icon,
  settings,
  isOpen,
  onClose,
}) => {
  const [activeTab, setActiveTab] = useState<'react' | 'html' | 'svg'>('react');
  const [copied, setCopied] = useState(false);

  if (!isOpen || !icon) return null;

  let code = '';
  let language = 'tsx';
  if (activeTab === 'react') {
    code = generateReactCode(icon, settings);
    language = 'typescript';
  } else if (activeTab === 'html') {
    code = generateHTMLCSSCode(icon, settings);
    language = 'html';
  } else {
    code = generatePureSVGCode(icon, settings);
    language = 'xml';
  }

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // fallback
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-md animate-fadeIn">
      <div className="relative w-full max-w-3xl rounded-2xl bg-slate-900 border border-slate-800 shadow-2xl flex flex-col max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-900/90">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
              <span className="font-mono text-sm font-bold">&lt;/&gt;</span>
            </div>
            <div>
              <h3 className="text-base font-semibold text-slate-100 font-display">
                Exportar: {icon.nameEs}
              </h3>
              <p className="text-xs text-slate-400">
                Código optimizado y listo para copiar en tu proyecto web
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="flex h-8 w-8 items-center justify-center rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
            aria-label="Cerrar modal"
          >
            ✕
          </button>
        </div>

        {/* Tab selection */}
        <div className="flex items-center justify-between px-6 py-3 border-b border-slate-800 bg-slate-950/40">
          <div className="flex items-center gap-1.5 p-1 bg-slate-800/80 rounded-xl">
            <button
              onClick={() => setActiveTab('react')}
              className={`px-3 py-1.5 text-xs font-medium rounded-lg transition-colors ${
                activeTab === 'react'
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              React + Motion
            </button>
            <button
              onClick={() => setActiveTab('html')}
              className={`px-3 py-1.5 text-xs font-medium rounded-lg transition-colors ${
                activeTab === 'html'
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              HTML &amp; CSS Puro
            </button>
            <button
              onClick={() => setActiveTab('svg')}
              className={`px-3 py-1.5 text-xs font-medium rounded-lg transition-colors ${
                activeTab === 'svg'
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              SVG Estándar
            </button>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => downloadSVGFile(icon, settings)}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-300 bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
              Descargar .SVG
            </button>

            <button
              onClick={handleCopy}
              className={`flex items-center gap-1.5 px-4 py-1.5 text-xs font-medium rounded-lg transition-all ${
                copied
                  ? 'bg-emerald-600 text-white'
                  : 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-sm'
              }`}
            >
              {copied ? (
                <>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                    <path d="M20 6L9 17l-5-5" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                  ¡Copiado!
                </>
              ) : (
                <>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
                    <path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1" />
                  </svg>
                  Copiar Código
                </>
              )}
            </button>
          </div>
        </div>

        {/* Code View Area */}
        <div className="relative flex-1 overflow-auto p-6 bg-slate-950 font-mono text-xs text-slate-300 leading-relaxed">
          <pre className="select-all whitespace-pre-wrap font-mono">
            <code>{code}</code>
          </pre>
        </div>

        {/* Footer info note */}
        <div className="flex items-center justify-between px-6 py-3 border-t border-slate-800 bg-slate-900 text-xs text-slate-400">
          <span>Formato: {language.toUpperCase()} · Sin dependencias pesadas</span>
          <span>Tamaño configurado: {settings.iconSize}px · Trazo: {settings.strokeWidth}px</span>
        </div>
      </div>
    </div>
  );
};
