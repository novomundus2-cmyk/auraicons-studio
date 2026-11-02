/**
 * AuraIcons · Interactive Icon Studio & Navigation Engine
 * Author: Mikel Irastorza (AuraIcons Architecture)
 * Complete client-side audio synthesis, magnetic physics, and tactile ripples
 */

(function () {
  'use strict';

  // --- 1. WEB AUDIO API SYNTHESIZER ---
  class AuraAudioSynthesizer {
    constructor() {
      this.ctx = null;
      this.isMuted = localStorage.getItem('aura_sound_muted') === 'true';
      const storedVol = parseFloat(localStorage.getItem('aura_sound_volume'));
      this.volume = isNaN(storedVol) ? 0.8 : Math.max(0, Math.min(1, storedVol));
      if (this.volume === 0) {
        this.isMuted = true;
      }
      this.soundPlayCount = parseInt(sessionStorage.getItem('aura_sound_play_count') || '0', 10);
    }

    getContext() {
      if (this.isMuted || this.volume <= 0) return null;
      if (typeof window === 'undefined') return null;

      if (!this.ctx) {
        const AudioCtx = window.AudioContext || window.webkitAudioContext;
        if (AudioCtx) {
          this.ctx = new AudioCtx();
        }
      }
      if (this.ctx && this.ctx.state === 'suspended') {
        this.ctx.resume();
      }
      return this.ctx;
    }

    recordSoundPlay() {
      this.soundPlayCount++;
      try {
        sessionStorage.setItem('aura_sound_play_count', this.soundPlayCount.toString());
        if (this.soundPlayCount === 5 && sessionStorage.getItem('aura_sound_prompt_dismissed') !== 'true') {
          setTimeout(() => {
            showAuraSoundPromptToast();
          }, 320);
        }
      } catch (e) {}
    }

    setVolume(vol) {
      vol = Math.max(0, Math.min(1, Number(vol)));
      this.volume = vol;
      if (vol === 0) {
        this.isMuted = true;
      } else {
        this.isMuted = false;
      }
      try {
        localStorage.setItem('aura_sound_volume', this.volume.toString());
        localStorage.setItem('aura_sound_muted', this.isMuted.toString());
      } catch (e) {}
      updateAllSoundUI();
    }

    setMuted(muted) {
      this.isMuted = !!muted;
      if (!this.isMuted && this.volume <= 0) {
        this.volume = 0.8;
      }
      try {
        localStorage.setItem('aura_sound_muted', this.isMuted.toString());
        localStorage.setItem('aura_sound_volume', this.volume.toString());
      } catch (e) {}
      updateAllSoundUI();
      return this.isMuted;
    }

    toggleMute() {
      return this.setMuted(!this.isMuted);
    }

    playHoverBlip() {
      const ctx = this.getContext();
      if (!ctx || this.isMuted || this.volume <= 0) return;
      try {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        const now = ctx.currentTime;
        const volFactor = this.volume;

        osc.type = 'sine';
        osc.frequency.setValueAtTime(540, now);
        osc.frequency.exponentialRampToValueAtTime(840, now + 0.045);

        gain.gain.setValueAtTime(0.02 * volFactor, now);
        gain.gain.exponentialRampToValueAtTime(0.001 * volFactor, now + 0.05);

        osc.connect(gain);
        gain.connect(ctx.destination);

        osc.start(now);
        osc.stop(now + 0.05);
        this.recordSoundPlay();
      } catch (e) {
        // Audio might be waiting for user gesture
      }
    }

    playClickPop() {
      const ctx = this.getContext();
      if (!ctx || this.isMuted || this.volume <= 0) return;
      try {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        const now = ctx.currentTime;
        const volFactor = this.volume;

        osc.type = 'sine';
        osc.frequency.setValueAtTime(380, now);
        osc.frequency.exponentialRampToValueAtTime(740, now + 0.07);

        gain.gain.setValueAtTime(0.04 * volFactor, now);
        gain.gain.exponentialRampToValueAtTime(0.001 * volFactor, now + 0.08);

        osc.connect(gain);
        gain.connect(ctx.destination);

        osc.start(now);
        osc.stop(now + 0.08);
        this.recordSoundPlay();
      } catch (e) {}
    }

    playChime() {
      const ctx = this.getContext();
      if (!ctx || this.isMuted || this.volume <= 0) return;
      try {
        const now = ctx.currentTime;
        const volFactor = this.volume;
        [620, 930].forEach((freq, idx) => {
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          const delay = idx * 0.04;

          osc.type = 'triangle';
          osc.frequency.setValueAtTime(freq, now + delay);

          gain.gain.setValueAtTime(0.03 * volFactor, now + delay);
          gain.gain.exponentialRampToValueAtTime(0.001 * volFactor, now + delay + 0.12);

          osc.connect(gain);
          gain.connect(ctx.destination);

          osc.start(now + delay);
          osc.stop(now + delay + 0.12);
        });
        this.recordSoundPlay();
      } catch (e) {}
    }
  }

  const audioSynth = new AuraAudioSynthesizer();
  window.AuraAudio = audioSynth;

  // Unlock audio context on any first user interaction
  const unlockAudio = () => {
    audioSynth.getContext();
    window.removeEventListener('pointerdown', unlockAudio);
    window.removeEventListener('keydown', unlockAudio);
  };
  window.addEventListener('pointerdown', unlockAudio, { passive: true });
  window.addEventListener('keydown', unlockAudio, { passive: true });

  // --- 2. TACTILE RIPPLE EFFECT ---
  function createAuraRipple(event, targetElement) {
    const rect = targetElement.getBoundingClientRect();
    const ripple = document.createElement('span');
    ripple.className = 'aura-ripple';

    const size = Math.max(rect.width, rect.height) * 1.5;
    ripple.style.width = ripple.style.height = `${size}px`;

    const clientX = event.clientX || (event.touches && event.touches[0] ? event.touches[0].clientX : rect.left + rect.width / 2);
    const clientY = event.clientY || (event.touches && event.touches[0] ? event.touches[0].clientY : rect.top + rect.height / 2);

    ripple.style.left = `${clientX - rect.left - size / 2}px`;
    ripple.style.top = `${clientY - rect.top - size / 2}px`;

    targetElement.appendChild(ripple);
    setTimeout(() => {
      if (ripple.parentNode) ripple.parentNode.removeChild(ripple);
    }, 550);
  }

  // --- 3. MAGNETIC HOVER PHYSICS ---
  function applyMagneticPhysics(el) {
    let rafId = null;

    el.addEventListener('mousemove', (e) => {
      if (rafId) return;
      const clientX = e.clientX;
      const clientY = e.clientY;

      rafId = requestAnimationFrame(() => {
        rafId = null;
        const rect = el.getBoundingClientRect();
        const centerX = rect.left + rect.width / 2;
        const centerY = rect.top + rect.height / 2;
        const deltaX = (clientX - centerX) * 0.18;
        const deltaY = (clientY - centerY) * 0.18;

        el.style.transform = `translate3d(${deltaX}px, ${deltaY}px, 0) scale(1.03)`;
      });
    });

    el.addEventListener('mouseenter', () => {
      audioSynth.playHoverBlip();
    });

    el.addEventListener('mouseleave', () => {
      if (rafId) {
        cancelAnimationFrame(rafId);
        rafId = null;
      }
      el.style.transform = '';
    });

    el.addEventListener('click', (e) => {
      audioSynth.playClickPop();
      createAuraRipple(e, el);
    });
  }

  // --- 4. PERSISTENT FLOATING RETURN DOCK ---
  function injectAuraFloatingDock() {
    if (document.getElementById('aura-floating-dock')) return;

    const path = window.location.pathname.toLowerCase();
    const isCV = path.includes('cv_printable') || path.includes('/cv.html');
    
    // On CV printable page, the top toolbar already has Cockpit Big Data; keep CV page clean
    if (isCV) return;

    const dock = document.createElement('div');
    dock.id = 'aura-floating-dock';
    dock.className = 'aura-floating-dock no-print';

    const primaryLink = '/cv_printable.html';
    const primaryTitle = 'Volver al CV';
    const primarySub = 'Mikel Irastorza · PDF Oficial';
    const primaryBadge = 'Oficial';

    const isCompact = localStorage.getItem('aura_dock_compact') === 'true';
    if (isCompact) {
      dock.classList.add('compact');
    }

    dock.innerHTML = `
      <button class="aura-sound-pill" id="aura-sound-toggle-btn" title="Activar/Silenciar efectos táctiles de audio AuraIcons">
        ${audioSynth.isMuted ? '🔇' : '🔔'}
      </button>
      <a href="${primaryLink}" class="aura-dock-btn" id="aura-dock-primary-btn" title="Volver al CV Oficial Imprimible de Mikel Irastorza">
        <div class="aura-icon-container">
          <svg class="aura-svg-arrow" width="18" height="18" viewBox="0 0 24 24" fill="none">
            <path d="M19 12H5" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M12 19l-7-7 7-7" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="aura-dock-content">
          <span class="aura-dock-title">${primaryTitle}</span>
          <span class="aura-dock-sub">${primarySub}</span>
        </div>
        <span class="aura-pulse-pill">${primaryBadge}</span>
      </a>
      <button class="aura-share-pill" id="aura-dock-share-btn" title="Escanear QR o Abrir en Móvil / Varios Dispositivos">
        📲
      </button>
      <button class="aura-compact-toggle" id="aura-compact-btn" title="Minimizar / Expandir muelle de navegación">
        ${isCompact ? '＋' : '—'}
      </button>
    `;

    document.body.appendChild(dock);

    const dockBtn = document.getElementById('aura-dock-primary-btn');
    if (dockBtn) applyMagneticPhysics(dockBtn);

    const soundToggle = document.getElementById('aura-sound-toggle-btn');
    if (soundToggle) {
      soundToggle.addEventListener('click', (e) => {
        const muted = audioSynth.toggleMute();
        soundToggle.textContent = muted ? '🔇' : '🔔';
        soundToggle.classList.toggle('muted', muted);
        if (!muted) audioSynth.playChime();
        createAuraRipple(e, soundToggle);
      });
    }

    const shareBtn = document.getElementById('aura-dock-share-btn');
    if (shareBtn) {
      shareBtn.addEventListener('click', (e) => {
        audioSynth.playClickPop();
        createAuraRipple(e, shareBtn);
        openAuraShareModal();
      });
    }

    const compactBtn = document.getElementById('aura-compact-btn');
    if (compactBtn) {
      compactBtn.addEventListener('click', (e) => {
        const nowCompact = dock.classList.toggle('compact');
        compactBtn.textContent = nowCompact ? '＋' : '—';
        localStorage.setItem('aura_dock_compact', nowCompact);
        audioSynth.playClickPop();
        createAuraRipple(e, compactBtn);
      });
    }
  }

  // --- 5. MODAL & MULTI-DEVICE SHARE HELPER ---
  function openAuraShareModal() {
    let modal = document.getElementById('aura-share-modal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'aura-share-modal';
      modal.onclick = (e) => {
        if (e.target === modal) closeAuraShareModal();
      };

      const currentUrl = window.location.href;
      const isCockpit = currentUrl.includes('cockpit') || currentUrl.includes('index.html');
      const isPortfolio = currentUrl.includes('portfolio');
      const origin = (window.location.origin && window.location.origin !== 'null' && !window.location.origin.startsWith('file')) ? window.location.origin : 'https://auraicons-studio.vercel.app';

      let qrSrc = `${origin}/qr-cv.png`;
      let modalTitle = 'Abrir CV en Móvil / Tablet';
      if (isCockpit) {
        qrSrc = `${origin}/qr-cockpit.png`;
        modalTitle = 'Abrir Cockpit Big Data';
      } else if (isPortfolio) {
        qrSrc = `${origin}/qr-portfolio.png`;
        modalTitle = 'Abrir Portfolio Interactivo';
      }

      modal.innerHTML = `
        <div class="aura-modal-content">
          <div class="aura-modal-header">
            <div class="aura-modal-title">
              <span>📲</span> <span>${modalTitle}</span>
            </div>
            <button class="aura-modal-close" onclick="window.auraCloseShareModal()" title="Cerrar">✕</button>
          </div>
          
          <div class="aura-qr-box">
            <img src="${qrSrc}" alt="Código QR de acceso móvil" class="aura-qr-img" />
          </div>
          
          <div class="aura-modal-sub">
            Escanea con la cámara de tu iPhone, iPad o Android para sincronizar al instante o instalar como App (PWA).
          </div>
          
          <button class="aura-copy-btn" id="aura-modal-copy-btn">
            <span>📋</span> <span id="aura-copy-text">Copiar Enlace de Producción</span>
          </button>

          ${navigator.share ? `
          <button class="aura-copy-btn" id="aura-modal-native-share-btn" style="background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.2); margin-bottom: 0;">
            <span>↗️</span> <span>Compartir mediante el Sistema</span>
          </button>
          ` : ''}
          
          <div class="aura-device-badges">
            <span class="aura-device-badge"> iPhone & iPad</span>
            <span class="aura-device-badge">⚡ PWA Offline</span>
            <span class="aura-device-badge">☁️ Vercel Edge</span>
          </div>
        </div>
      `;
      document.body.appendChild(modal);

      const copyBtn = document.getElementById('aura-modal-copy-btn');
      if (copyBtn) {
        copyBtn.addEventListener('click', () => {
          navigator.clipboard.writeText(window.location.href).then(() => {
            const copyText = document.getElementById('aura-copy-text');
            if (copyText) {
              const prev = copyText.textContent;
              copyText.textContent = '¡Enlace Copiado al Portapapeles!';
              setTimeout(() => { copyText.textContent = prev; }, 2200);
            }
            if (window.AuraAudio) window.AuraAudio.playChime();
          }).catch(() => {
            prompt('Copia este enlace para abrir en otro dispositivo:', window.location.href);
          });
        });
      }

      const nativeShareBtn = document.getElementById('aura-modal-native-share-btn');
      if (nativeShareBtn) {
        nativeShareBtn.addEventListener('click', () => {
          if (navigator.share) {
            navigator.share({
              title: document.title || 'Mikel Irastorza · Portfolio & CV',
              text: 'CV interactivo y Cockpit Big Data de Mikel Irastorza',
              url: window.location.href
            }).catch(() => {});
          }
        });
      }
    }
    modal.style.display = 'flex';
  }

  function closeAuraShareModal() {
    const modal = document.getElementById('aura-share-modal');
    if (modal) modal.style.display = 'none';
  }

  window.auraOpenShareModal = openAuraShareModal;
  window.auraCloseShareModal = closeAuraShareModal;

  // --- 6. UNIFIED AUDIO STATE SYNCHRONIZATION ---
  function updateAllSoundUI() {
    const isMuted = audioSynth.isMuted || audioSynth.volume <= 0;
    const vol = audioSynth.volume;
    const volPercent = isMuted ? 0 : Math.round(vol * 100);

    let icon = '🔊';
    if (isMuted) {
      icon = '🔇';
    } else if (vol <= 0.45) {
      icon = '🔉';
    }

    // 1. CV Toolbar Sound Pill
    const cvSoundBtn = document.getElementById('cv-sound-toggle-btn');
    if (cvSoundBtn) {
      cvSoundBtn.textContent = isMuted ? '🔇' : '🔔';
      cvSoundBtn.classList.toggle('muted', isMuted);
    }

    // 2. Floating Dock Sound Pill
    const dockSoundBtn = document.getElementById('aura-sound-toggle-btn');
    if (dockSoundBtn) {
      dockSoundBtn.textContent = icon;
      dockSoundBtn.classList.toggle('muted', isMuted);
    }

    // 3. Bottom-Right Sound FAB Widget
    const fabIcon = document.getElementById('aura-sound-fab-icon');
    if (fabIcon) {
      fabIcon.textContent = icon;
    }
    const fabBtn = document.getElementById('aura-sound-fab-btn');
    if (fabBtn) {
      fabBtn.classList.toggle('muted', isMuted);
      fabBtn.setAttribute('title', isMuted ? 'Audio silenciado (Clic para abrir control)' : `Audio activo: ${volPercent}% (Clic para control)`);
    }

    // 4. Volume Popover Controls
    const volSlider = document.getElementById('aura-vol-slider');
    if (volSlider) {
      volSlider.value = volPercent;
      volSlider.style.background = `linear-gradient(to right, #38bdf8 0%, #38bdf8 ${volPercent}%, rgba(255,255,255,0.15) ${volPercent}%, rgba(255,255,255,0.15) 100%)`;
    }
    const volText = document.getElementById('aura-vol-val-text');
    if (volText) {
      volText.textContent = isMuted ? '0% (Silencio)' : `${volPercent}%`;
    }
  }

  // --- 7. 5-SOUND PLAYS PROMPT TOAST ---
  function showAuraSoundPromptToast() {
    if (document.getElementById('aura-sound-toast')) return;
    try {
      if (sessionStorage.getItem('aura_sound_prompt_dismissed') === 'true') return;
    } catch (e) {}

    const toast = document.createElement('div');
    toast.id = 'aura-sound-toast';
    toast.className = 'aura-sound-toast no-print';
    toast.innerHTML = `
      <div class="aura-sound-toast-header">
        <div class="aura-sound-toast-title">
          <span class="aura-toast-pulse-icon">🔔</span>
          <span>¿Te gusta el sonido háptico?</span>
        </div>
        <button class="aura-sound-toast-close" id="aura-toast-close-btn" title="Cerrar">✕</button>
      </div>
      <div class="aura-sound-toast-body">
        Ha sonado <strong>5 veces</strong> durante tu navegación. Puedes dejar el sonido activo o silenciarlo por completo.
      </div>
      <div class="aura-sound-toast-actions">
        <button class="aura-toast-action-btn aura-toast-keep" id="aura-toast-keep-btn" title="Mantener los efectos de audio interactivos">
          <span>🔊</span> <span>Dejar Sonido</span>
        </button>
        <button class="aura-toast-action-btn aura-toast-mute" id="aura-toast-mute-btn" title="Silenciar efectos de audio">
          <span>🔇</span> <span>Quitar / Silenciar</span>
        </button>
      </div>
    `;

    document.body.appendChild(toast);
    requestAnimationFrame(() => {
      toast.classList.add('visible');
    });

    const closeToast = () => {
      try {
        sessionStorage.setItem('aura_sound_prompt_dismissed', 'true');
      } catch (e) {}
      toast.classList.remove('visible');
      setTimeout(() => {
        if (toast.parentNode) toast.parentNode.removeChild(toast);
      }, 350);
    };

    const keepBtn = document.getElementById('aura-toast-keep-btn');
    if (keepBtn) {
      keepBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        try { sessionStorage.setItem('aura_sound_prompt_dismissed', 'true'); } catch (err) {}
        if (audioSynth.isMuted) {
          audioSynth.setMuted(false);
        }
        audioSynth.playChime();
        closeToast();
      });
    }

    const muteBtn = document.getElementById('aura-toast-mute-btn');
    if (muteBtn) {
      muteBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        try { sessionStorage.setItem('aura_sound_prompt_dismissed', 'true'); } catch (err) {}
        audioSynth.setMuted(true);
        closeToast();
      });
    }

    const closeBtn = document.getElementById('aura-toast-close-btn');
    if (closeBtn) {
      closeBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        closeToast();
      });
    }
  }

  // --- 8. PAGE CONTEXT DETECTION ---
  function getPageContext() {
    const path = (window.location.pathname || '').toLowerCase();
    const title = (document.title || '').toLowerCase();

    if (path.includes('bot')) {
      return {
        icon: '🤖',
        name: 'Bot',
        fullName: 'Trading Bot Cuantitativo SMC',
        color: '#f59e0b',
        glow: 'rgba(245, 158, 11, 0.45)'
      };
    }
    if (path.includes('portfolio')) {
      return {
        icon: '🌐',
        name: 'Portfolio',
        fullName: 'Portfolio Interactivo & Dinámica Molecular',
        color: '#10b981',
        glow: 'rgba(16, 185, 129, 0.45)'
      };
    }
    if (path.includes('cv') || title.includes('cv') || title.includes('irastorza')) {
      return {
        icon: '📄',
        name: 'CV',
        fullName: 'CV Oficial · Mikel Irastorza',
        color: '#38bdf8',
        glow: 'rgba(56, 189, 248, 0.45)'
      };
    }
    if (path.includes('cockpit') || path.includes('visualizer') || path === '/' || path.endsWith('index.html')) {
      return {
        icon: '⚡',
        name: 'Cockpit',
        fullName: 'Cockpit Big Data & Telemetría',
        color: '#38bdf8',
        glow: 'rgba(56, 189, 248, 0.45)'
      };
    }
    return {
      icon: '✨',
      name: 'Aura',
      fullName: document.title || 'AuraIcons Studio',
      color: '#38bdf8',
      glow: 'rgba(56, 189, 248, 0.45)'
    };
  }

  // --- 9. BOTTOM-RIGHT CLUSTER (PAGE CONTEXT ARROW + INTERACTIVE SOUND FAB) ---
  function injectAuraBottomRightCluster() {
    if (document.getElementById('aura-bottom-right-cluster')) return;

    const ctx = getPageContext();
    const cluster = document.createElement('div');
    cluster.id = 'aura-bottom-right-cluster';
    cluster.className = 'aura-bottom-right-cluster no-print';

    cluster.innerHTML = `
      <!-- Contextual Page Arrow Button -->
      <button class="aura-page-arrow-btn" id="aura-page-arrow-btn" title="Subir al inicio · ${ctx.fullName}">
        <span class="aura-page-arrow-icon" id="aura-page-arrow-icon">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round">
            <line x1="12" y1="19" x2="12" y2="5"></line>
            <polyline points="5 12 12 5 19 12"></polyline>
          </svg>
        </span>
        <span class="aura-page-icon-badge">${ctx.icon}</span>
        <span class="aura-page-name-badge">${ctx.name}</span>
      </button>

      <!-- Interactive Sound Widget (FAB + Popover) -->
      <div class="aura-sound-fab-widget" id="aura-sound-fab-widget">
        <!-- Popover Menu -->
        <div class="aura-volume-popover" id="aura-volume-popover">
          <div class="aura-popover-header">
            <div class="aura-popover-title">
              <span>🎛️ Aura Audio</span>
            </div>
            <span class="aura-vol-badge" id="aura-vol-val-text">80%</span>
          </div>

          <div class="aura-slider-container">
            <input type="range" min="0" max="100" value="80" class="aura-vol-slider" id="aura-vol-slider" aria-label="Control de volumen AuraIcons">
          </div>

          <div class="aura-popover-actions">
            <button class="aura-popover-btn aura-popover-mute" id="aura-popover-mute-btn" title="Apagar el sonido por completo">
              <span>🔇 Apagar</span>
            </button>
            <button class="aura-popover-btn aura-popover-boost" id="aura-popover-boost-btn" title="Subir el volumen al 100%">
              <span>🔊 Subir</span>
            </button>
            <button class="aura-popover-btn aura-popover-leave" id="aura-popover-leave-btn" title="Cerrar manteniendo la configuración actual">
              <span>✓ Dejarlo</span>
            </button>
          </div>
        </div>

        <!-- Floating Action Button -->
        <button class="aura-sound-fab-btn" id="aura-sound-fab-btn" title="Efectos hápticos de sonido AuraIcons (Hover para agrandar, Clic para menú)">
          <span class="aura-sound-fab-icon" id="aura-sound-fab-icon">🔊</span>
        </button>
      </div>
    `;

    document.body.appendChild(cluster);

    // --- Arrow Button Interactions ---
    const arrowBtn = document.getElementById('aura-page-arrow-btn');
    if (arrowBtn) {
      arrowBtn.addEventListener('mouseenter', () => {
        audioSynth.playHoverBlip();
      });

      arrowBtn.addEventListener('click', (e) => {
        e.stopPropagation();

        // Bounce spring effect
        arrowBtn.classList.remove('aura-bounce-active');
        void arrowBtn.offsetWidth;
        arrowBtn.classList.add('aura-bounce-active');

        audioSynth.playClickPop();

        // Smooth scroll to top
        if (window.scrollY > 40) {
          window.scrollTo({ top: 0, behavior: 'smooth' });
        } else {
          // If already at top, scroll slightly down to content or trigger pulse
          const scrollTarget = Math.min(window.innerHeight * 0.7, 450);
          window.scrollTo({ top: scrollTarget, behavior: 'smooth' });
        }
      });

      arrowBtn.addEventListener('animationend', () => {
        arrowBtn.classList.remove('aura-bounce-active');
      });

      // Dynamic scroll state update
      window.addEventListener('scroll', () => {
        const atTop = window.scrollY <= 40;
        arrowBtn.setAttribute('title', atTop ? `Inicio de página · ${ctx.fullName}` : `Subir al inicio · ${ctx.fullName}`);
        const arrowSvg = arrowBtn.querySelector('.aura-page-arrow-icon svg');
        if (arrowSvg) {
          arrowSvg.style.transform = atTop ? 'rotate(180deg)' : 'rotate(0deg)';
          arrowSvg.style.transition = 'transform 0.3s ease';
        }
      }, { passive: true });
    }

    // --- Sound Controller Interactions ---
    const fabBtn = document.getElementById('aura-sound-fab-btn');
    const popover = document.getElementById('aura-volume-popover');
    const volSlider = document.getElementById('aura-vol-slider');
    const muteBtn = document.getElementById('aura-popover-mute-btn');
    const boostBtn = document.getElementById('aura-popover-boost-btn');
    const leaveBtn = document.getElementById('aura-popover-leave-btn');

    // Hover effect: enlarges and plays blip
    fabBtn.addEventListener('mouseenter', () => {
      audioSynth.playHoverBlip();
    });

    // Click effect: bounce animation + toggle popover
    fabBtn.addEventListener('click', (e) => {
      e.stopPropagation();

      fabBtn.classList.remove('aura-bounce-active');
      void fabBtn.offsetWidth;
      fabBtn.classList.add('aura-bounce-active');

      audioSynth.playClickPop();
      popover.classList.toggle('open');
    });

    fabBtn.addEventListener('animationend', () => {
      fabBtn.classList.remove('aura-bounce-active');
    });

    if (volSlider) {
      volSlider.addEventListener('input', (e) => {
        const val = parseInt(e.target.value, 10);
        audioSynth.setVolume(val / 100);
      });
    }

    if (muteBtn) {
      muteBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        audioSynth.setVolume(0);
      });
    }

    if (boostBtn) {
      boostBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        audioSynth.setVolume(1.0);
        audioSynth.playChime();
      });
    }

    if (leaveBtn) {
      leaveBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        audioSynth.playHoverBlip();
        popover.classList.remove('open');
      });
    }

    document.addEventListener('click', (e) => {
      if (popover && popover.classList.contains('open') && !cluster.contains(e.target)) {
        popover.classList.remove('open');
      }
    });

    updateAllSoundUI();
  }

  // --- 10. PWA SERVICE WORKER REGISTRATION ---
  if ('serviceWorker' in navigator && (window.location.protocol === 'https:' || window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('/sw.js').catch(() => {});
    });
  }

  // --- 11. INITIALIZE ALL INTERACTIVE ELEMENTS ---
  function initAuraInteractions() {
    injectAuraFloatingDock();
    injectAuraBottomRightCluster();
    updateAllSoundUI();

    // Hook up all existing navigation buttons, segmented controls, and action pills
    const interactiveSelectors = [
      '.apple-pill-btn',
      '.btn-action',
      '.nav-btn',
      '.info-btn',
      '.info-pill-btn',
      '.segmented-btn',
      '.btn-pill',
      '.aura-header-btn',
      '.proj-action-btn'
    ];

    document.querySelectorAll(interactiveSelectors.join(',')).forEach((btn) => {
      applyMagneticPhysics(btn);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAuraInteractions);
  } else {
    initAuraInteractions();
  }
})();
