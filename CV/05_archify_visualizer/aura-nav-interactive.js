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
    }

    getContext() {
      if (this.isMuted) return null;
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

    toggleMute() {
      this.isMuted = !this.isMuted;
      localStorage.setItem('aura_sound_muted', this.isMuted);
      return this.isMuted;
    }

    playHoverBlip() {
      const ctx = this.getContext();
      if (!ctx) return;
      try {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        const now = ctx.currentTime;

        osc.type = 'sine';
        osc.frequency.setValueAtTime(540, now);
        osc.frequency.exponentialRampToValueAtTime(840, now + 0.045);

        gain.gain.setValueAtTime(0.02, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.05);

        osc.connect(gain);
        gain.connect(ctx.destination);

        osc.start(now);
        osc.stop(now + 0.05);
      } catch (e) {
        // Audio might be waiting for user gesture
      }
    }

    playClickPop() {
      const ctx = this.getContext();
      if (!ctx) return;
      try {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        const now = ctx.currentTime;

        osc.type = 'sine';
        osc.frequency.setValueAtTime(380, now);
        osc.frequency.exponentialRampToValueAtTime(740, now + 0.07);

        gain.gain.setValueAtTime(0.04, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.08);

        osc.connect(gain);
        gain.connect(ctx.destination);

        osc.start(now);
        osc.stop(now + 0.08);
      } catch (e) {}
    }

    playChime() {
      const ctx = this.getContext();
      if (!ctx) return;
      try {
        const now = ctx.currentTime;
        [620, 930].forEach((freq, idx) => {
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          const delay = idx * 0.04;

          osc.type = 'triangle';
          osc.frequency.setValueAtTime(freq, now + delay);

          gain.gain.setValueAtTime(0.03, now + delay);
          gain.gain.exponentialRampToValueAtTime(0.001, now + delay + 0.12);

          osc.connect(gain);
          gain.connect(ctx.destination);

          osc.start(now + delay);
          osc.stop(now + delay + 0.12);
        });
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

  // --- 6. PWA SERVICE WORKER REGISTRATION ---
  if ('serviceWorker' in navigator && (window.location.protocol === 'https:' || window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('/sw.js').catch(() => {});
    });
  }

  // --- 5. INITIALIZE ALL INTERACTIVE ELEMENTS ---
  function initAuraInteractions() {
    injectAuraFloatingDock();

    // Hook up all existing navigation buttons, segmented controls, and action pills
    const interactiveSelectors = [
      '.apple-pill-btn',
      '.btn-action',
      '.nav-btn',
      '.info-btn',
      '.info-pill-btn',
      '.segmented-btn',
      '.btn-pill',
      '.aura-header-btn'
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
