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
  const [likes, setLikes] = useState(248);
  const [hasLiked, setHasLiked] = useState(false);
  const [bookmarked, setBookmarked] = useState(false);
  const [cartCount, setCartCount] = useState(3);
  const [rating, setRating] = useState(5);
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
    if (navigator.clipboard) {
      navigator.clipboard.writeText(window.location.origin);
    }
    setTimeout(() => setIsCopied(false), 2400);
  };

  return (
    <div className="flex flex-col gap-10">
      {/* Cupertino Apple Header & Identity */}
      <div>
        <div className="flex flex-wrap items-center gap-2 text-xs text-sky-400 font-mono mb-1.5">
          <span className="font-bold tracking-wider">MIKEL IRASTORZA</span>
          <span aria-hidden="true" className="text-slate-600">·</span>
          <span>PORTAFOLIO DE INGENIERÍA DE DATOS &amp; DESPLIEGUE</span>
          <span aria-hidden="true" className="text-slate-600">·</span>
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[10px] font-semibold">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            DISPONIBLE PARA NUEVOS RETOS
          </span>
        </div>
        <h3 className="text-2xl sm:text-3xl font-bold text-slate-100 font-display tracking-tight text-balance">
          Cómo se integran los iconos interactivos en tu sitio web profesional
        </h3>
        <p className="text-sm text-slate-400 mt-1.5 max-w-3xl leading-relaxed text-pretty">
          Diseñado bajo los principios de Steve Jobs y Apple Cupertino: esquinas redondeadas en squircle, micro-interacciones a 60fps con feedback auditivo y visualización viva de pipelines de datos distribuidos (Kafka, Spark, Haskell, Lakehouse y BigQuery AI/ML).
        </p>
      </div>

      {/* 1. Navbar Simulation: Mikel Irastorza · Data Platform */}
      <div className="flex flex-col gap-3">
        <div className="flex items-center justify-between text-xs text-slate-400">
          <span className="font-semibold text-slate-200">1. Barra de Navegación (Header de tu Web Personal)</span>
          <span className="font-mono text-slate-500">Prueba los botones interactivos a la derecha</span>
        </div>

        <div className="p-4 rounded-3xl bg-slate-900/80 backdrop-blur-xl border border-slate-800 shadow-2xl flex items-center justify-between gap-4">
          {/* Logo & Brand Monogram */}
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-2xl bg-gradient-to-br from-slate-700 via-slate-800 to-slate-900 border border-slate-600/40 text-sky-400 flex items-center justify-center font-bold font-mono text-sm shadow-md">
              MI
            </div>
            <div className="flex flex-col">
              <span className="font-display font-semibold text-slate-100 text-sm tracking-tight hidden sm:inline">
                Mikel Irastorza
              </span>
              <span className="text-[10px] text-slate-400 font-mono hidden md:inline">
                Data Platform &amp; Deployment Engineer
              </span>
            </div>
          </div>

          {/* Navigation Links */}
          <div className="hidden lg:flex items-center gap-6 text-xs font-medium text-slate-400">
            <a
              href="http://localhost:8765/cv.pdf"
              target="_blank"
              rel="noopener noreferrer"
              className="text-sky-400 hover:text-sky-300 transition-colors font-semibold flex items-center gap-1"
            >
              <span>CV Ejecutivo</span>
              <span className="text-[10px] px-1.5 py-0.2 bg-sky-500/15 rounded text-sky-400 border border-sky-500/30">PDF</span>
            </a>
            <span
              onClick={() => onSelectIcon('kafka-spark-stream')}
              className="hover:text-slate-200 cursor-pointer transition-colors"
            >
              Streaming Lakehouse
            </span>
            <span
              onClick={() => onSelectIcon('welford-shield-mad')}
              className="hover:text-slate-200 cursor-pointer transition-colors"
            >
              Matemáticas &amp; Haskell
            </span>
            <span
              onClick={() => onSelectIcon('bigquery-graph-nodes')}
              className="hover:text-slate-200 cursor-pointer transition-colors"
            >
              BigQuery AI/ML
            </span>
            <a
              href="http://localhost:8765/index.html"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-emerald-400 cursor-pointer transition-colors flex items-center gap-1 text-slate-300"
            >
              <span>Ahorro Luz (137 €)</span>
            </a>
          </div>

          {/* Interactive Icon Group in Navbar */}
          <div className="flex items-center gap-1.5 sm:gap-2">
            {/* Search */}
            <div onClick={() => onSelectIcon('search-lens')} title="Buscar tecnología o proyecto">
              <InteractiveIcon
                icon={getIcon('search-lens')}
                size={18}
                strokeWidth={settings.strokeWidth}
                theme={settings.selectedTheme}
                containerShape="squircle"
                enableSound={settings.enableSound}
              />
            </div>

            {/* Kafka & Spark Streaming Status Icon */}
            <div
              onClick={() => {
                setCartCount((c) => c + 1);
                onSelectIcon('kafka-spark-stream');
              }}
              title="Pipeline de Streaming Kafka & Spark en directo"
            >
              <InteractiveIcon
                icon={getIcon('kafka-spark-stream')}
                size={18}
                strokeWidth={settings.strokeWidth}
                theme="sunset"
                badge="LIVE"
                containerShape="squircle"
                enableSound={settings.enableSound}
              />
            </div>

            {/* Lakehouse ACID Cube */}
            <div onClick={() => onSelectIcon('iceberg-lakehouse-cube')} title="Lakehouse ACID con Apache Iceberg & SQLite">
              <InteractiveIcon
                icon={getIcon('iceberg-lakehouse-cube')}
                size={18}
                strokeWidth={settings.strokeWidth}
                theme="emerald"
                containerShape="squircle"
                enableSound={settings.enableSound}
              />
            </div>

            {/* Theme Toggle Sun / Moon */}
            <div onClick={() => onSelectIcon('sun-moon')} title="Alternar tema día / noche">
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
            <div onClick={() => onSelectIcon('menu-morph')} title="Menú interactivo con morph animado">
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

      {/* 2. Interactive Feature Bento Cards (Key Pillars from data_engineer_deployment_plan.md) */}
      <div className="flex flex-col gap-3">
        <div className="flex items-center justify-between text-xs text-slate-400">
          <span className="font-semibold text-slate-200">2. Bento Grid de Pilares de Ingeniería (Apple Keynote Style)</span>
          <span className="font-mono text-slate-500">Pasa el ratón sobre cada tarjeta para activar micro-animaciones</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Bento Card 1: Streaming Distribuido */}
          <div
            onClick={() => onSelectIcon('kafka-spark-stream')}
            className="group relative p-6 rounded-3xl bg-slate-900/60 hover:bg-slate-900/90 border border-slate-800 hover:border-amber-500/40 transition-all duration-300 cursor-pointer flex flex-col justify-between min-h-[250px] shadow-lg"
          >
            <div>
              <div className="flex items-center justify-between mb-4">
                <InteractiveIcon
                  icon={getIcon('kafka-spark-stream')}
                  size={28}
                  strokeWidth={settings.strokeWidth}
                  theme="sunset"
                  containerShape="squircle"
                  enableSound={settings.enableSound}
                />
                <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-300 border border-amber-500/20">
                  Kafka acks=all
                </span>
              </div>
              <h4 className="text-base font-semibold text-slate-100 font-display group-hover:text-amber-300 transition-colors">
                Streaming Distribuido &amp; KRaft
              </h4>
              <p className="text-xs text-slate-400 mt-2 leading-relaxed text-pretty">
                Ingesta resiliente con Apache NiFi (Backpressure), clúster Kafka en modo KRaft y micro-batches PySpark con watermarking de 5s y latencia inferior a 80ms.
              </p>
            </div>
            <div className="flex items-center justify-between text-xs text-amber-400 font-medium pt-4 border-t border-slate-800/80 mt-4">
              <span>Explorar telemetría de streaming</span>
              <span className="transform group-hover:translate-x-1.5 transition-transform font-bold">→</span>
            </div>
          </div>

          {/* Bento Card 2: Matemáticas en Haskell & Welford Monoids */}
          <div
            onClick={() => onSelectIcon('welford-shield-mad')}
            className="group relative p-6 rounded-3xl bg-slate-900/60 hover:bg-slate-900/90 border border-slate-800 hover:border-sky-500/40 transition-all duration-300 cursor-pointer flex flex-col justify-between min-h-[250px] shadow-lg"
          >
            <div>
              <div className="flex items-center justify-between mb-4">
                <InteractiveIcon
                  icon={getIcon('welford-shield-mad')}
                  size={28}
                  strokeWidth={settings.strokeWidth}
                  theme="glass"
                  containerShape="squircle"
                  enableSound={settings.enableSound}
                />
                <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded-full bg-sky-500/10 text-sky-300 border border-sky-500/20">
                  (A ⊕ B) ⊕ C
                </span>
              </div>
              <h4 className="text-base font-semibold text-slate-100 font-display group-hover:text-sky-300 transition-colors">
                Matemáticas en Haskell &amp; Welford
              </h4>
              <p className="text-xs text-slate-400 mt-2 leading-relaxed text-pretty">
                Monoides paralelos asociativos formalizados en Haskell y SymPy. Algoritmo de Welford en una sola pasada con Z-Score robusto (MAD = 295.76) para detección de fraude.
              </p>
            </div>
            <div className="flex items-center justify-between text-xs text-sky-400 font-medium pt-4 border-t border-slate-800/80 mt-4">
              <span>Ver demostración matemática</span>
              <span className="transform group-hover:translate-x-1.5 transition-transform font-bold">→</span>
            </div>
          </div>

          {/* Bento Card 3: Lakehouse ACID & BigQuery AI/ML */}
          <div
            onClick={() => onSelectIcon('bigquery-graph-nodes')}
            className="group relative p-6 rounded-3xl bg-slate-900/60 hover:bg-slate-900/90 border border-slate-800 hover:border-emerald-500/40 transition-all duration-300 cursor-pointer flex flex-col justify-between min-h-[250px] shadow-lg"
          >
            <div>
              <div className="flex items-center justify-between mb-4">
                <InteractiveIcon
                  icon={getIcon('bigquery-graph-nodes')}
                  size={28}
                  strokeWidth={settings.strokeWidth}
                  theme="emerald"
                  containerShape="squircle"
                  enableSound={settings.enableSound}
                />
                <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-300 border border-emerald-500/20">
                  TimesFM 2.0
                </span>
              </div>
              <h4 className="text-base font-semibold text-slate-100 font-display group-hover:text-emerald-300 transition-colors">
                Lakehouse ACID &amp; BigQuery AI
              </h4>
              <p className="text-xs text-slate-400 mt-2 leading-relaxed text-pretty">
                Almacenamiento ACID particionado en formato Parquet ZSTD, replicación automática a NAS compartido y consultas BigQuery SQL con AI.DETECT_ANOMALIES y ML.DESCRIBE_DATA.
              </p>
            </div>
            <div className="flex items-center justify-between text-xs text-emerald-400 font-medium pt-4 border-t border-slate-800/80 mt-4">
              <span>Consultar esquema analítico</span>
              <span className="transform group-hover:translate-x-1.5 transition-transform font-bold">→</span>
            </div>
          </div>
        </div>

        {/* Bento Banner Spotlight: 137 € Calculadora de Energía & Clima */}
        <div className="p-5 rounded-3xl bg-gradient-to-r from-slate-900/80 via-slate-900/60 to-emerald-950/20 border border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div onClick={() => onSelectIcon('flame-fire')} className="cursor-pointer">
              <InteractiveIcon
                icon={getIcon('flame-fire')}
                size={24}
                strokeWidth={settings.strokeWidth}
                theme="sunset"
                containerShape="squircle"
                enableSound={settings.enableSound}
              />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h5 className="text-sm font-semibold text-slate-200">
                  Auditoría Energética Real: 137,21 € de Ahorro Eléctrico Anual
                </h5>
                <span className="text-[10px] font-mono px-2 py-0.5 bg-emerald-500/15 text-emerald-400 rounded-full border border-emerald-500/30">
                  Auditado PVPC
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                Cálculo matemático en Python de optimización horaria de termo de agua caliente con temporizador digital y tarifa discriminada.
              </p>
            </div>
          </div>
          <a
            href="http://localhost:8765/index.html"
            target="_blank"
            rel="noopener noreferrer"
            className="shrink-0 px-4 py-2 rounded-2xl bg-emerald-600/20 hover:bg-emerald-600/30 border border-emerald-500/40 text-emerald-300 text-xs font-semibold transition-all hover:scale-105"
          >
            Ver Estudio en Archify →
          </a>
        </div>
      </div>

      {/* 3. Action Buttons & Social Reactions Bar */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-stretch">
        {/* Social Reactions Strip */}
        <div className="p-6 rounded-3xl bg-slate-900/60 border border-slate-800 flex flex-col justify-between gap-4">
          <div>
            <div className="flex items-center justify-between mb-1">
              <h4 className="text-sm font-semibold text-slate-200 font-display">Barra de Reacciones para Artículos Técnicos</h4>
              <span className="text-xs text-slate-500 font-mono">Haz clic para interactuar</span>
            </div>
            <p className="text-xs text-slate-400">
              Micro-interacciones con físicas de resorte y partículas para publicaciones y artículos de ingeniería.
            </p>
          </div>

          <div className="flex items-center gap-4 p-3 bg-slate-950/60 rounded-2xl border border-slate-800/80">
            {/* Heart with particle burst */}
            <div className="flex items-center gap-1.5 cursor-pointer" onClick={handleLikeClick}>
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
              <span className="text-xs font-mono text-slate-300 tabular-nums font-semibold">{likes}</span>
            </div>

            {/* Bookmark */}
            <div className="cursor-pointer" onClick={() => setBookmarked(!bookmarked)} title="Guardar artículo">
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
            <div className="ml-auto cursor-pointer" onClick={handleShareClick} title="Compartir enlace">
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

          {isCopied ? (
            <p className="text-xs text-emerald-400 font-medium animate-fadeIn text-center">
              ✓ ¡Enlace copiado al portapapeles con éxito!
            </p>
          ) : (
            <p className="text-[11px] text-slate-500 text-center font-mono">
              Calificación media de la comunidad: {rating}.0 / 5.0
            </p>
          )}
        </div>

        {/* High-Converting Cupertino CTAs & Official Downloads */}
        <div className="p-6 rounded-3xl bg-slate-900/60 border border-slate-800 flex flex-col justify-between gap-4">
          <div>
            <h4 className="text-sm font-semibold text-slate-200 font-display">Descargas Oficiales &amp; Acceso en Vivo</h4>
            <p className="text-xs text-slate-400 mt-1">
              Accede a los documentos ejecutivos generados por el servidor LAN y el visualizador Archify.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {/* Live Studio Link */}
            <a
              href="http://localhost:8765/index.html"
              target="_blank"
              rel="noopener noreferrer"
              className="group flex items-center justify-center gap-2 px-4 py-3 rounded-2xl bg-gradient-to-r from-sky-600 to-indigo-600 hover:from-sky-500 hover:to-indigo-500 text-white text-xs font-semibold shadow-lg shadow-sky-600/25 transition-all active:scale-95"
            >
              <InteractiveIcon
                icon={getIcon('sparkle-ai')}
                size={16}
                strokeWidth={2}
                theme="minimal"
                containerShape="none"
                enableSound={false}
              />
              <span>Archify Studio en Vivo</span>
            </a>

            {/* Download Official CV PDF */}
            <a
              href="http://localhost:8765/cv.pdf"
              download="CV_Mikel_Irastorza.pdf"
              className="group flex items-center justify-center gap-2 px-4 py-3 rounded-2xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow-lg shadow-emerald-600/25 transition-all active:scale-95"
            >
              <InteractiveIcon
                icon={getIcon('download-cloud')}
                size={16}
                strokeWidth={2}
                theme="minimal"
                containerShape="none"
                enableSound={false}
              />
              <span>Descargar CV (PDF)</span>
            </a>

            {/* Download Technical Dossier PDF */}
            <a
              href="http://localhost:8765/dossier.pdf"
              download="DOSSIER_NOTEBOOKLM_MIKEL.pdf"
              className="group flex items-center justify-center gap-2 px-4 py-3 rounded-2xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium border border-slate-700 transition-all active:scale-95"
            >
              <InteractiveIcon
                icon={getIcon('code-brackets')}
                size={16}
                strokeWidth={2}
                theme="duotone"
                containerShape="none"
                enableSound={false}
              />
              <span>Dossier Técnico (PDF)</span>
            </a>

            {/* Export Code Modal */}
            <button
              onClick={onOpenExport}
              className="group flex items-center justify-center gap-2 px-4 py-3 rounded-2xl bg-slate-800 hover:bg-slate-700 text-sky-400 hover:text-sky-300 text-xs font-semibold border border-sky-500/30 transition-all active:scale-95"
            >
              <span>Exportar Icono React</span>
              <span className="transform group-hover:translate-x-1 transition-transform">
                <InteractiveIcon
                  icon={getIcon('arrow-slide')}
                  size={14}
                  strokeWidth={2.5}
                  theme="minimal"
                  containerShape="none"
                  enableSound={false}
                />
              </span>
            </button>
          </div>

          <p className="text-xs text-slate-400 text-pretty">
            El 73% de los reclutadores y líderes técnicos prefieren un portafolio interactivo con código ejecutable e infraestructura verificable frente a un PDF estático.
          </p>
        </div>
      </div>
    </div>
  );
};
