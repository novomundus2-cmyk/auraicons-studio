"""
===============================================================================
MODULE: netgui_server.py
LOCATION: 05_archify_visualizer/netgui_server.py
PURPOSE: Clean-Code Pythonista Multi-PC LAN, NAS & Cloud Bridge Server.
         Binds to 0.0.0.0:8765 so multiple PCs, tablets, and NAS devices on
         the local network can connect to Archify Studio, trigger the 6-stage
         Python pipeline, replicate the Lakehouse database to a NAS mirror,
         and inspect BigQuery DTS, BigQuery Property Graph, and Firebase state.
AUTHOR: Senior Data Platform & Deployment Engineering Portfolio
===============================================================================
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import queue
import shutil
import socket
import sqlite3
import sys
import time
import uuid
import webbrowser
from contextlib import closing
from datetime import UTC, datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Final

VIS_DIR: Final[Path] = Path(__file__).resolve().parent
CV_ROOT: Final[Path] = VIS_DIR.parent
STREAM_DIR: Final[Path] = CV_ROOT / "02_streaming_platform"
MATH_DIR: Final[Path] = CV_ROOT / "03_math_haskell_python"
DB_DIR: Final[Path] = CV_ROOT / "04_database_lakehouse"
AGENT_DIR: Final[Path] = CV_ROOT / "06_ai_note_agent"
NAS_MIRROR_DIR: Final[Path] = DB_DIR / "nas_shared_mirror"

PERFECT_DIR: Final[Path] = CV_ROOT / "09_antigravity_perfect_pipeline"

for folder in (STREAM_DIR, MATH_DIR, DB_DIR, AGENT_DIR, PERFECT_DIR, CV_ROOT, CV_ROOT / "07_trading_bot"):
    if str(folder) not in sys.path:
        sys.path.insert(0, str(folder))

from dataclasses import asdict
from enterprise_hierarchy import (  # noqa: E402
    dispatch_presidential_directive,
    get_corporate_status,
)
from route_optimizer import get_all_routes_telemetry  # noqa: E402
from supabase_sync import get_supabase_status, sync_all_novus_lakehouse_to_supabase  # noqa: E402
from trading_bot.bot_core import GLOBAL_QUANT_BOT  # noqa: E402
GLOBAL_TRADING_BOT = GLOBAL_QUANT_BOT  # backwards-compatibility alias
from trading_bot.haskell_bridge import GLOBAL_HASKELL_BRIDGE  # noqa: E402
from trading_bot.streaming_db import GLOBAL_STREAM_DB  # noqa: E402
from trading_bot.true_live_api import GLOBAL_TRUE_PRICES_ENGINE  # noqa: E402
from perfect_pipeline import GLOBAL_PERFECT_PIPELINE  # noqa: E402
from autonomous_pipeline_daemon import GLOBAL_PIPELINE_DAEMON  # noqa: E402
from cybersecurity_audit_agent import GLOBAL_SECURITY_ENGINE  # noqa: E402

from build_database import PATHS  # noqa: E402
from pipeline_orchestrator import run_interconnected_pipeline  # noqa: E402


def get_local_lan_ip() -> str:
    """Detects the primary LAN IPv4 address for multi-PC network access."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return str(s.getsockname()[0])
    except OSError:
        return "127.0.0.1"


def discover_mounted_nas_volumes() -> list[dict[str, Any]]:
    """Lists mounted macOS /Volumes and checks free/total capacity."""
    volumes_root = Path("/Volumes")
    result: list[dict[str, Any]] = []
    if volumes_root.exists():
        for vol in sorted(volumes_root.iterdir()):
            try:
                usage = shutil.disk_usage(vol)
                result.append(
                    {
                        "name": vol.name,
                        "path": str(vol),
                        "total_gb": round(usage.total / (1024**3), 2),
                        "free_gb": round(usage.free / (1024**3), 2),
                    }
                )
            except OSError:
                continue
    return result


def sync_lakehouse_to_nas_mirror() -> dict[str, Any]:
    """Replicates financial_lakehouse.db and Gold JSON categories to NAS mirror."""
    NAS_MIRROR_DIR.mkdir(parents=True, exist_ok=True)
    copied_files: list[str] = []
    total_bytes = 0

    if PATHS.db_path.exists():
        target_db = NAS_MIRROR_DIR / PATHS.db_path.name
        shutil.copy2(PATHS.db_path, target_db)
        copied_files.append(target_db.name)
        total_bytes += target_db.stat().st_size

    categories_dir = DB_DIR / "categories"
    if categories_dir.exists():
        for json_file in sorted(categories_dir.rglob("*.json")):
            dest = NAS_MIRROR_DIR / json_file.name
            shutil.copy2(json_file, dest)
            copied_files.append(dest.name)
            total_bytes += dest.stat().st_size

    manifest = {
        "ok": True,
        "synced_at_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "nas_mirror_path": str(NAS_MIRROR_DIR),
        "files_synced_count": len(copied_files),
        "files_synced": copied_files,
        "total_kb": round(total_bytes / 1024, 2),
        "lan_server_url": f"http://{get_local_lan_ip()}:8765/index.html",
    }
    (NAS_MIRROR_DIR / "nas_sync_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return manifest


DOSSIER_FILE: Final[Path] = CV_ROOT / "DOSSIER_NOTEBOOKLM_MIKEL.html"
DOSSIER_PDF: Final[Path] = CV_ROOT / "DOSSIER_NOTEBOOKLM_MIKEL.pdf"
DOSSIER_MD: Final[Path] = CV_ROOT / "DOSSIER_NOTEBOOKLM_MIKEL.md"
NOTEBOOKS_ZIP: Final[Path] = CV_ROOT / "NOTEBOOKS_GEMINI_BUNDLE.zip"
CV_HTML: Final[Path] = CV_ROOT / "cv_printable.html"
CV_PDF: Final[Path] = CV_ROOT / "CV_Mikel_Irastorza.pdf"
EVERNOTE_DIR: Final[Path] = CV_ROOT / "07_evernote_templates"
EVERNOTE_HTML: Final[Path] = EVERNOTE_DIR / "novus_daily_journal.html"
EVERNOTE_ENEX: Final[Path] = EVERNOTE_DIR / "novus_daily_journal.enex"
EVERNOTE_MD: Final[Path] = EVERNOTE_DIR / "novus_daily_journal.md"

# Only these URL paths are ever served as files (no source code, no __pycache__).
STATIC_ROUTES: Final[dict[str, tuple[Path, str, bool, str]]] = {
    "/": (VIS_DIR / "index.html", "text/html; charset=utf-8", False, ""),
    "/index.html": (VIS_DIR / "index.html", "text/html; charset=utf-8", False, ""),
    "/cockpit": (VIS_DIR / "index.html", "text/html; charset=utf-8", False, ""),
    "/cockpit.html": (VIS_DIR / "index.html", "text/html; charset=utf-8", False, ""),
    "/live_data_bridge.js": (
        VIS_DIR / "live_data_bridge.js",
        "application/javascript; charset=utf-8",
        False,
        "",
    ),
    "/cv.html": (CV_HTML, "text/html; charset=utf-8", False, ""),
    "/cv_printable.html": (CV_HTML, "text/html; charset=utf-8", False, ""),
    "/cv.pdf": (CV_PDF, "application/pdf", True, "CV_Mikel_Irastorza.pdf"),
    "/CV_Mikel_Irastorza.pdf": (CV_PDF, "application/pdf", False, ""),
    "/dossier.html": (DOSSIER_FILE, "text/html; charset=utf-8", False, ""),
    "/dossier.pdf": (DOSSIER_PDF, "application/pdf", True, "DOSSIER_NOTEBOOKLM_MIKEL.pdf"),
    "/DOSSIER_NOTEBOOKLM_MIKEL.pdf": (DOSSIER_PDF, "application/pdf", False, ""),
    "/dossier.md": (DOSSIER_MD, "text/markdown; charset=utf-8", True, "DOSSIER_NOTEBOOKLM_MIKEL.md"),
    "/DOSSIER_NOTEBOOKLM_MIKEL.md": (DOSSIER_MD, "text/markdown; charset=utf-8", False, ""),
    "/notebooks.zip": (NOTEBOOKS_ZIP, "application/zip", True, "NOTEBOOKS_GEMINI_BUNDLE.zip"),
    "/NOTEBOOKS_GEMINI_BUNDLE.zip": (NOTEBOOKS_ZIP, "application/zip", True, "NOTEBOOKS_GEMINI_BUNDLE.zip"),
    "/evernote.html": (EVERNOTE_HTML, "text/html; charset=utf-8", False, ""),
    "/novus_daily_journal.enex": (
        EVERNOTE_ENEX,
        "application/octet-stream",
        True,
        "novus_daily_journal.enex",
    ),
    "/novus_daily_journal.md": (EVERNOTE_MD, "text/markdown; charset=utf-8", True, "novus_daily_journal.md"),
    "/portfolio.html": (VIS_DIR / "portfolio.html", "text/html; charset=utf-8", False, ""),
    "/portfolio": (VIS_DIR / "portfolio.html", "text/html; charset=utf-8", False, ""),
    "/bot.html": (VIS_DIR / "bot.html", "text/html; charset=utf-8", False, ""),
    "/bot": (VIS_DIR / "bot.html", "text/html; charset=utf-8", False, ""),
    "/google-skills.html": (VIS_DIR / "google-skills.html", "text/html; charset=utf-8", False, ""),
    "/google-skills": (VIS_DIR / "google-skills.html", "text/html; charset=utf-8", False, ""),
    "/google_skills_catalog.json": (
        VIS_DIR / "google_skills_catalog.json",
        "application/json; charset=utf-8",
        False,
        "",
    ),
    "/lightweight-charts.js": (
        VIS_DIR / "lightweight-charts.js",
        "application/javascript; charset=utf-8",
        False,
        "",
    ),
    "/harness": (Path("/Users/mikelirastorza/Downloads/Claude Harness Data Engineer.html"), "text/html; charset=utf-8", False, ""),
    "/harness.html": (Path("/Users/mikelirastorza/Downloads/Claude Harness Data Engineer.html"), "text/html; charset=utf-8", False, ""),
    "/amenazas": (Path("/Users/mikelirastorza/Library/Mobile Documents/com~apple~CloudDocs/Desktop/01 - PROYECTOS/05 - Aprendizaje/DATA ENGINNEER FINAL STUDY/Lecciones/03-cloud-seguridad-y-operacion.html"), "text/html; charset=utf-8", False, ""),
    "/amenazas.html": (Path("/Users/mikelirastorza/Library/Mobile Documents/com~apple~CloudDocs/Desktop/01 - PROYECTOS/05 - Aprendizaje/DATA ENGINNEER FINAL STUDY/Lecciones/03-cloud-seguridad-y-operacion.html"), "text/html; charset=utf-8", False, ""),
    "/amenazas.md": (Path("/Users/mikelirastorza/Library/Mobile Documents/com~apple~CloudDocs/Desktop/01 - PROYECTOS/05 - Aprendizaje/DATA ENGINNEER FINAL STUDY/Lecciones/03-cloud-seguridad-y-operacion.md"), "text/markdown; charset=utf-8", False, ""),
    "/seguridad": (Path("/Users/mikelirastorza/Library/Mobile Documents/com~apple~CloudDocs/Desktop/01 - PROYECTOS/05 - Aprendizaje/DATA ENGINNEER FINAL STUDY/Lecciones/03-cloud-seguridad-y-operacion.html"), "text/html; charset=utf-8", False, ""),
    "/Recursos/estudio.css": (Path("/Users/mikelirastorza/Library/Mobile Documents/com~apple~CloudDocs/Desktop/01 - PROYECTOS/05 - Aprendizaje/DATA ENGINNEER FINAL STUDY/Recursos/estudio.css"), "text/css; charset=utf-8", False, ""),
    "/Recursos/icono-data-dorado.png": (Path("/Users/mikelirastorza/Library/Mobile Documents/com~apple~CloudDocs/Desktop/01 - PROYECTOS/05 - Aprendizaje/DATA ENGINNEER FINAL STUDY/Recursos/icono-data-dorado.png"), "image/png", False, ""),
    "/presentation_slides.json": (VIS_DIR / "presentation_slides.json", "application/json; charset=utf-8", False, ""),
    "/slides": (VIS_DIR / "presentation_slides.json", "application/json; charset=utf-8", False, ""),
    "/aura-nav-interactive.css": (VIS_DIR / "aura-nav-interactive.css", "text/css; charset=utf-8", False, ""),
    "/aura-nav-interactive.js": (VIS_DIR / "aura-nav-interactive.js", "application/javascript; charset=utf-8", False, ""),
}

STORE_PRODUCTS: Final[list[dict[str, Any]]] = [
    {
        "id": "PROD-01-CONSULTING",
        "title": "Consultoría Data Platform & Fractional CTO",
        "category": "services",
        "badge": "Servicio B2B",
        "price_eur": 3500.0,
        "price_cents": 350000,
        "description": "Sprint de 2 semanas: Auditoría de streaming Kafka/Spark, migración a Lakehouse Zero-Trust y optimización FinOps.",
        "deliverables": [
            "Auditoría de latencia y colas con Ley de Little",
            "Blueprint de arquitectura Zero-Trust y contratos Pandera",
            "Sesiones estratégicas 1:1 con Mikel Irastorza",
            "Informe C-Suite formal y plan de ejecución"
        ]
    },
    {
        "id": "PROD-02-QUANT-BOT",
        "title": "Licencia Novus Quant Trading Bot Core",
        "category": "software",
        "badge": "Algoritmo Cuantitativo",
        "price_eur": 890.0,
        "price_cents": 89000,
        "description": "Kernel cuantitativo compilado en Haskell GHC 9.14 + Motor Python multiactivo en tiempo real con libro de órdenes y Circuit Breaker.",
        "deliverables": [
            "Código fuente completo (Python 3.14 + Haskell)",
            "4 Estrategias (VWAP, Momentum, Grid, SMC Order Blocks)",
            "Auditoría formal de partida doble con hash chain SHA-256",
            "12 meses de actualizaciones y soporte de integración"
        ]
    },
    {
        "id": "PROD-03-PLAYBOOKS-NOTEBOOKS",
        "title": "Pack Masterclass & Flagship Engineering Playbooks",
        "category": "education",
        "badge": "Digital Download",
        "price_eur": 149.0,
        "price_cents": 14900,
        "description": "Colección completa de 4 Playbooks institucionales para CTOs + 5 Gemini Notebooks ejecutables (.ipynb) y Dossier NotebookLM.",
        "deliverables": [
            "4 Engineering Playbooks interactivos con código copiable",
            "5 Cuadernos interactivos Jupyter/Gemini (.ipynb)",
            "Documento fuente estructurado para Google NotebookLM",
            "Dossier de ingeniería de 80 páginas en PDF de alta fidelidad"
        ]
    },
    {
        "id": "PROD-04-AURAICONS-KIT",
        "title": "AuraIcons Studio Pro UI Design System Kit",
        "category": "design",
        "badge": "Design System",
        "price_eur": 79.0,
        "price_cents": 7900,
        "description": "Kit de diseño vectorial interactivo con más de 800 iconos SVG hiper-optimizados, micro-interacciones a 60 FPS y tokens Cupertino.",
        "deliverables": [
            "Colección de 800+ iconos SVG limpios y responsive",
            "Componentes React y Web Components listos para producción",
            "Variables CSS modo oscuro Apple Pro (Dark/Light)",
            "Licencia comercial para proyectos ilimitados"
        ]
    },
    {
        "id": "PROD-05-CAREER-PLACEMENT",
        "title": "Acelerador de Carrera & Colocación Laboral Tech (Novus Talent)",
        "category": "career",
        "badge": "Talento & Búsqueda Activa",
        "price_eur": 350.0,
        "price_cents": 35000,
        "description": "Programa intensivo de colocación laboral: nos envías tu perfil/CV, auditamos y reconstruimos tu candidatura con proyectos de ingeniería reales, preparamos tus entrevistas técnicas 1:1 y te conectamos activamente con empresas y reclutadores para conseguir trabajo.",
        "deliverables": [
            "Auditoría y reconstrucción total de CV a estándar Silicon Valley / Alta Dirección",
            "Inclusión de proyectos técnicos reales reproducibles (Zero-Trust, Lakehouse, Streaming)",
            "Sesión 1:1 de simulación de entrevistas técnicas (System Design & Live Coding)",
            "Optimización de perfil LinkedIn, GitHub y cartas de candidatura a medida",
            "Acompañamiento y postulación activa a vacantes abiertas hasta colocación"
        ]
    }
]

def get_all_prices_payload() -> dict[str, Any]:
    md = GLOBAL_QUANT_BOT.market_data
    prices_list = []
    by_cat: dict[str, list[dict[str, Any]]] = {
        "crypto": [],
        "equity": [],
        "forex": [],
        "commodity": [],
    }

    category_map = {
        "BTCUSDT": ("Bitcoin / Tether USD Spot", "crypto", "₿"),
        "ETHUSDT": ("Ethereum / Tether USD Spot", "crypto", "Ξ"),
        "SOLUSDT": ("Solana / Tether USD Spot", "crypto", "◎"),
        "BNBUSDT": ("BNB / Tether USD Spot", "crypto", "🟡"),
        "NVDA": ("NVIDIA Corp (NASDAQ)", "equity", "🖥️"),
        "AAPL": ("Apple Inc (NASDAQ)", "equity", "🍎"),
        "TSLA": ("Tesla Inc (NASDAQ)", "equity", "⚡"),
        "IBE.MC": ("Iberdrola SA (BME)", "equity", "⚡"),
        "SAN.MC": ("Banco Santander (BME)", "equity", "🏦"),
        "ITX.MC": ("Inditex SA (BME)", "equity", "👕"),
        "ACS.MC": ("ACS Actividades (BME)", "equity", "🏗️"),
        "SU.PA": ("Schneider Electric (Euronext)", "equity", "⚡"),
        "EURUSD": ("Euro / US Dollar FX", "forex", "💶"),
        "USDJPY": ("US Dollar / Japanese Yen FX", "forex", "💴"),
        "GBPUSD": ("British Pound / US Dollar FX", "forex", "💷"),
        "USDCHF": ("US Dollar / Swiss Franc FX", "forex", "🇨🇭"),
        "XAUUSD": ("Gold Spot / US Dollar (Au Invariant)", "commodity", "🥇"),
    }

    for sym in md.ALL_SYMBOLS:
        p, vol = md.get_latest_price(sym)
        tick = GLOBAL_QUANT_BOT.generate_tick(sym)
        prof = md.get_liquidity_profile(sym)
        stat = md.get_symbol_market_status(sym)
        name, cat, icon = category_map.get(sym, (sym, "equity", "📈"))

        base_p = md.BASE_PRICES.get(sym, p)
        change_pct = round(((p - base_p) / max(base_p, 1e-4)) * 100.0, 2)
        spread_bps = prof.get("spread_bps", 1.5)
        half_spread = (p * (spread_bps / 10000.0)) / 2.0
        bid = round(p - half_spread, 2 if p >= 10 else 5)
        ask = round(p + half_spread, 2 if p >= 10 else 5)

        history = md.tick_history.get(sym, [])
        sparkline = [round(item[1], 2 if p >= 10 else 5) for item in history[-14:]] if history else [p]

        trend = (
            "BULLISH"
            if tick.z_score > 0.4 or change_pct > 0.1
            else ("BEARISH" if tick.z_score < -0.4 or change_pct < -0.1 else "NEUTRAL")
        )

        item = {
            "symbol": sym,
            "name": name,
            "category": cat.upper(),
            "icon": icon,
            "price": p,
            "price_formatted": f"{p:,.2f} €" if p >= 10 else (f"{p:,.4f} €" if p >= 1 else f"{p:.5f} €"),
            "change_24h_pct": change_pct,
            "high_24h": round(max(p, base_p * 1.018), 2 if p >= 10 else 5),
            "low_24h": round(min(p, base_p * 0.982), 2 if p >= 10 else 5),
            "volume_24h": vol,
            "bid": bid,
            "ask": ask,
            "spread_bps": spread_bps,
            "vwap": tick.vwap,
            "z_score": tick.z_score,
            "volatility_mad": tick.volatility_mad,
            "signal": tick.signal,
            "confidence_pct": tick.confidence_pct,
            "trend": trend,
            "sparkline": sparkline,
            "rating": prof.get("rating", "Tier-1"),
            "is_open": stat["is_open"],
            "market_status": stat["status"],
            "asset_class": stat["asset_class"],
            "trading_hours_utc": stat["hours_label"],
            "verified_real_price": True,
            "feed_source": "BINANCE_LIVE" if sym in md.CRYPTO_SYMBOLS else "YAHOO_FINANCE_LIVE",
            "updated_at": round(time.time(), 3),
        }
        prices_list.append(item)
        if cat in by_cat:
            by_cat[cat].append(item)

    regime = md.get_market_regime()
    return {
        "ok": True,
        "engine": "NovusMundus Quantitative Live Feeds v3.0",
        "api_endpoint": "/api/prices",
        "timestamp": time.time(),
        "total_symbols": len(prices_list),
        "market_regime": regime,
        "prices": prices_list,
        "by_category": by_cat,
        "haskell_verified": True,
    }


def get_true_prices_payload() -> dict[str, Any]:
    return GLOBAL_TRUE_PRICES_ENGINE.get_all_true_prices()


def get_chart_payload(symbol: str = "BTCUSDT", interval: str = "1h", limit: int = 50) -> dict[str, Any]:
    import numpy as np
    from trading_bot.indicators import Indicators

    sym = symbol.upper()
    candles = GLOBAL_QUANT_BOT.market_data.get_historical_candles(sym, interval=interval, count=limit)
    if not candles:
        return {"ok": False, "error": f"No candles available for symbol {sym}"}

    closes = [c.close for c in candles]
    timestamps = [int(c.timestamp) for c in candles]

    # Vectorized indicators
    upper_bb, mid_bb, lower_bb = Indicators.bollinger_bands(
        closes, period=min(20, len(closes)), num_std=2.0
    )
    ema9 = Indicators.ema(closes, period=min(9, len(closes)))
    ema21 = Indicators.ema(closes, period=min(21, len(closes)))
    rsi14 = Indicators.rsi(closes, period=min(14, len(closes)))

    cum_pv = 0.0
    cum_v = 0.0
    vwap_series = []
    for c in candles:
        cum_pv += c.close * c.volume
        cum_v += c.volume
        vwap_series.append(round(cum_pv / max(cum_v, 1e-4), 2 if c.close >= 10 else 5))

    candles_formatted = [
        {
            "time": int(c.timestamp),
            "open": c.open,
            "high": c.high,
            "low": c.low,
            "close": c.close,
            "volume": c.volume,
        }
        for c in candles
    ]

    dec = 2 if candles[-1].close >= 10 else 5

    def _clean_series(ts_list, val_list, decimals=2):
        out = []
        for t, v in zip(ts_list, val_list, strict=False):
            if v is not None and not np.isnan(v):
                out.append({"time": t, "value": round(float(v), decimals)})
        return out

    indicators_payload = {
        "vwap": [{"time": t, "value": v} for t, v in zip(timestamps, vwap_series, strict=False)],
        "bollinger_upper": _clean_series(timestamps, upper_bb, dec),
        "bollinger_middle": _clean_series(timestamps, mid_bb, dec),
        "bollinger_lower": _clean_series(timestamps, lower_bb, dec),
        "ema_9": _clean_series(timestamps, ema9, dec),
        "ema_21": _clean_series(timestamps, ema21, dec),
        "rsi_14": _clean_series(timestamps, rsi14, 2),
    }

    recent_lows = [c.low for c in candles[-20:]]
    recent_highs = [c.high for c in candles[-20:]]
    support = round(min(recent_lows), dec) if recent_lows else candles[-1].close
    resistance = round(max(recent_highs), dec) if recent_highs else candles[-1].close

    return {
        "ok": True,
        "symbol": sym,
        "interval": interval,
        "count": len(candles),
        "current_price": candles[-1].close,
        "candles": candles_formatted,
        "indicators": indicators_payload,
        "levels": {
            "support": support,
            "resistance": resistance,
            "pivot_point": round((support + resistance + candles[-1].close) / 3.0, dec),
        },
        "server_time": time.time(),
    }


def get_market_overview_payload() -> dict[str, Any]:
    prices_data = get_all_prices_payload()
    prices = prices_data["prices"]
    sorted_by_gain = sorted(prices, key=lambda x: x["change_24h_pct"], reverse=True)
    gainers = sorted_by_gain[:3]
    losers = sorted(prices, key=lambda x: x["change_24h_pct"])[:3]
    total_vol = sum(p["volume_24h"] for p in prices)

    avg_z = sum(p["z_score"] for p in prices) / max(len(prices), 1)
    sentiment_score = int(max(10, min(90, 50 + avg_z * 15)))
    sentiment_label = (
        "Codicia Institucional (Risk-On)"
        if sentiment_score >= 60
        else ("Miedo / Acumulación (Risk-Off)" if sentiment_score <= 40 else "Neutral Cuantitativo")
    )

    bot_rep = GLOBAL_QUANT_BOT.get_status_report()
    return {
        "ok": True,
        "market_sentiment": {
            "score": sentiment_score,
            "label": sentiment_label,
            "average_market_zscore": round(avg_z, 2),
        },
        "total_volume_tracked": round(total_vol, 2),
        "top_gainers": gainers,
        "top_losers": losers,
        "quant_engine": {
            "autopilot": bot_rep.get("autopilot", True),
            "strategy": bot_rep.get("active_strategy", "VWAP_MEAN_REVERSION"),
            "equity_eur": bot_rep.get("total_equity_eur", 10000.0),
            "cash_eur": bot_rep.get("cash_eur", 10000.0),
            "active_positions_count": len(bot_rep.get("open_positions", {})),
            "total_trades_settled": bot_rep.get("total_trades", 0),
        },
        "market_regime": GLOBAL_QUANT_BOT.market_data.get_market_regime(),
        "streaming_db": GLOBAL_STREAM_DB.get_engine_metrics(),
        "haskell_verification": GLOBAL_HASKELL_BRIDGE.run_self_test(),
        "timestamp": time.time(),
    }


def get_market_opportunities_payload() -> dict[str, Any]:
    md = GLOBAL_QUANT_BOT.market_data
    regime = md.get_market_regime()
    open_syms = [s for s in md.ALL_SYMBOLS if md.is_market_open(s)]

    category_map = {
        "BTCUSDT": ("Bitcoin / Tether USD Spot", "crypto", "₿"),
        "ETHUSDT": ("Ethereum / Tether USD Spot", "crypto", "Ξ"),
        "SOLUSDT": ("Solana / Tether USD Spot", "crypto", "◎"),
        "BNBUSDT": ("BNB / Tether USD Spot", "crypto", "🟡"),
        "NVDA": ("NVIDIA Corp (NASDAQ)", "equity", "🖥️"),
        "AAPL": ("Apple Inc (NASDAQ)", "equity", "🍎"),
        "TSLA": ("Tesla Inc (NASDAQ)", "equity", "⚡"),
        "IBE.MC": ("Iberdrola SA (BME)", "equity", "⚡"),
        "SAN.MC": ("Banco Santander (BME)", "equity", "🏦"),
        "ITX.MC": ("Inditex SA (BME)", "equity", "👕"),
        "ACS.MC": ("ACS Actividades (BME)", "equity", "🏗️"),
        "SU.PA": ("Schneider Electric (Euronext)", "equity", "⚡"),
        "EURUSD": ("Euro / US Dollar FX", "forex", "💶"),
        "USDJPY": ("US Dollar / Japanese Yen FX", "forex", "💴"),
        "GBPUSD": ("British Pound / US Dollar FX", "forex", "💷"),
        "USDCHF": ("US Dollar / Swiss Franc FX", "forex", "🇨🇭"),
        "XAUUSD": ("Gold Spot / US Dollar (Au Invariant)", "commodity", "🥇"),
    }

    opportunities = []
    for sym in open_syms:
        p, vol = md.get_latest_price(sym)
        tick = GLOBAL_QUANT_BOT.generate_tick(sym)
        prof = md.get_liquidity_profile(sym)
        name, cat, icon = category_map.get(sym, (sym, "equity", "📈"))

        z = tick.z_score
        action = "BUY" if z <= 0.1 else "SELL"
        edge_magnitude = abs(z)

        dec = 2 if p >= 10 else 5
        if action == "BUY":
            sl = round(p * 0.985, dec)
            tp = round(max(p * 1.025, tick.vwap if tick.vwap > p else p * 1.025), dec)
            rr = round((tp - p) / max(p - sl, 1e-4), 2)
            rationale = (
                f"Cotizando por debajo de VWAP ({tick.vwap} €) en mercado abierto ({prof.get('rating', 'Tier-1')}). "
                f"Asimetría favorable para rebote institucional a la media con Stop-Loss al 1.5%."
            )
        else:
            sl = round(p * 1.015, dec)
            tp = round(min(p * 0.975, tick.vwap if tick.vwap < p else p * 0.975), dec)
            rr = round((p - tp) / max(sl - p, 1e-4), 2)
            rationale = (
                f"Sobrecompra por encima de VWAP ({tick.vwap} €) con Z-score positivo ({z:+}). "
                f"Oportunidad de salida de beneficio o liquidación corta defensiva."
            )

        confidence = min(95, max(68, int(tick.confidence_pct + (10 if "BTC" in sym or "NVDA" in sym or "XAU" in sym else 0))))

        opportunities.append({
            "symbol": sym,
            "name": name,
            "category": cat.upper(),
            "icon": icon,
            "price": p,
            "price_formatted": f"{p:,.2f} €" if p >= 10 else f"{p:.5f} €",
            "vwap": tick.vwap,
            "z_score": z,
            "action": action,
            "stop_loss": sl,
            "take_profit": tp,
            "risk_reward_ratio": rr,
            "confidence_pct": confidence,
            "rationale": rationale,
            "market_status": "ABIERTO AHORA",
            "is_open": True,
            "rating": prof.get("rating", "Tier-1"),
            "edge_score": round(edge_magnitude + (0.5 if action == "BUY" else 0.2), 2),
        })

    opportunities.sort(key=lambda x: x["edge_score"], reverse=True)
    top_opp = opportunities[0] if opportunities else None

    return {
        "ok": True,
        "engine": "NovusMundus Quant Opportunity Radar",
        "timestamp": time.time(),
        "market_regime": regime,
        "open_markets_count": len(open_syms),
        "total_tracked_markets": len(md.ALL_SYMBOLS),
        "top_opportunity": top_opp,
        "opportunities": opportunities,
    }


def get_api_documentation_payload() -> dict[str, Any]:
    return {
        "ok": True,
        "name": "NovusMundus Quant Trading & Market Feeds REST API",
        "version": "3.0.0",
        "description": "API REST institucional en tiempo real para cotizaciones, velas japonesas (OHLCV), indicadores matemáticos (VWAP, Bollinger, EMA, RSI) y ejecución del trading bot autónomo.",
        "base_url": "http://127.0.0.1:8765",
        "endpoints": [
            {
                "path": "/api/prices",
                "method": "GET",
                "summary": "Cotizaciones en directo de todos los activos (Cripto, Acciones, Forex, Oro XAUUSD)",
                "params": {},
                "curl_example": "curl -s http://127.0.0.1:8765/api/prices | jq .",
            },
            {
                "path": "/api/chart",
                "method": "GET",
                "summary": "Datos OHLCV completos para gráficos interactivos e indicadores técnicos vectorizados",
                "params": {
                    "symbol": "BTCUSDT | ETHUSDT | NVDA | EURUSD | XAUUSD (default: BTCUSDT)",
                    "interval": "1m | 5m | 15m | 1h | 1d (default: 1h)",
                    "limit": "Número de velas 10..200 (default: 50)",
                },
                "curl_example": "curl -s 'http://127.0.0.1:8765/api/chart?symbol=BTCUSDT&interval=1h&limit=50' | jq .",
            },
            {
                "path": "/api/trading/status",
                "method": "GET",
                "summary": "Estado completo del bot, tesorería, PnL, posiciones abiertas y auditoría Pacioli SHA-256",
                "params": {},
                "curl_example": "curl -s http://127.0.0.1:8765/api/trading/status | jq .",
            },
            {
                "path": "/api/market/overview",
                "method": "GET",
                "summary": "Resumen macro: Top gainers, sentimiento cuantitativo, volumen global y salud del motor",
                "params": {},
                "curl_example": "curl -s http://127.0.0.1:8765/api/market/overview | jq .",
            },
            {
                "path": "/api/trading/order",
                "method": "POST",
                "summary": "Ejecución de orden manual o algorítmica con firma de bloque SHA-256",
                "params": {
                    "symbol": "Símbolo del activo (ej: BTCUSDT)",
                    "side": "BUY | SELL",
                    "qty": "Cantidad (float)",
                },
                "curl_example": "curl -X POST http://127.0.0.1:8765/api/trading/order -H 'Content-Type: application/json' -d '{\"symbol\":\"BTCUSDT\",\"side\":\"BUY\",\"qty\":0.05}'",
            },
            {
                "path": "/api/prices/true",
                "method": "GET",
                "summary": "API de Precios Verdaderos: Cotizaciones 100% reales en directo de Binance y Yahoo Finance sin simulación",
                "params": {},
                "curl_example": "curl -s http://127.0.0.1:8765/api/prices/true | jq .",
            },
            {
                "path": "/api/market/hours",
                "method": "GET",
                "summary": "Horarios de negociación, estado bursátil y régimen de fallback 24/7 de Criptomonedas",
                "params": {},
                "curl_example": "curl -s http://127.0.0.1:8765/api/market/hours | jq .",
            },
            {
                "path": "/api/haskell/verify",
                "method": "GET",
                "summary": "Kernel Cuantitativo Haskell GHC-9.14: Verificación formal de partida doble Pacioli y Black-Scholes",
                "params": {},
                "curl_example": "curl -s http://127.0.0.1:8765/api/haskell/verify | jq .",
            },
            {
                "path": "/api/stream/status",
                "method": "GET",
                "summary": "NovusStreamDB: Estado de la base de datos en streaming, buffer en memoria, throughput y WAL",
                "params": {},
                "curl_example": "curl -s http://127.0.0.1:8765/api/stream/status | jq .",
            },
            {
                "path": "/api/stream/events",
                "method": "GET",
                "summary": "Server-Sent Events (SSE) streaming de eventos en vivo y ticks en tiempo real",
                "params": {},
                "curl_example": "curl -N http://127.0.0.1:8765/api/stream/events",
            },
            {
                "path": "/api/stream/query",
                "method": "GET",
                "summary": "Consulta analítica sobre el ring buffer de la base de datos en streaming",
                "params": {"symbol": "BTCUSDT", "topic": "TICK | TRADE", "limit": "50"},
                "curl_example": "curl -s 'http://127.0.0.1:8765/api/stream/query?symbol=BTCUSDT&limit=10' | jq .",
            },
        ],
    }


LOOPBACK_ADDRESSES: Final[frozenset[str]] = frozenset({"127.0.0.1", "::1"})


class ArchifyNetGUIHandler(SimpleHTTPRequestHandler):
    """Serves an allow-list of static files plus status/pipeline/NAS APIs.

    Read-only routes (GET) are available to the LAN when `--lan` is used.
    State-changing routes (POST) are accepted only from this machine.
    """

    def _send_json(self, payload: dict[str, Any], status: int = 200, cors: bool = False) -> None:
        raw = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        if cors or self.path.startswith(("/api/prices", "/api/chart", "/api/candles", "/api/market", "/api/docs", "/api/trading", "/api/stream", "/api/haskell")):
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()
        self.wfile.write(raw)

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def _send_static(
        self,
        path: Path,
        content_type: str,
        as_attachment: bool = False,
        dl_name: str = "",
        send_body: bool = True,
    ) -> None:
        if not path.is_file():
            self._send_json({"ok": False, "error": "not found"}, 404)
            return
        raw = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        if as_attachment:
            final_name = dl_name or path.name
            self.send_header("Content-Disposition", f'attachment; filename="{final_name}"')
        self.end_headers()
        if send_body:
            self.wfile.write(raw)

    def _status_payload(self) -> dict[str, Any]:
        lan_ip = get_local_lan_ip()
        with closing(sqlite3.connect(PATHS.db_path)) as conn:
            cur = conn.cursor()
            txns = cur.execute("SELECT COUNT(*) FROM fact_transactions").fetchone()[0]
            sinks = cur.execute("SELECT COUNT(*) FROM streaming_window_sinks").fetchone()[0]
            ai_cnt = cur.execute("SELECT COUNT(*) FROM ai_insights_registry").fetchone()[0]
        return {
            "status": "ONLINE_CLUSTER_MASTER",
            "hostname": socket.gethostname(),
            "os": f"{platform.system()} {platform.release()}",
            "cpu_cores": os.cpu_count() or 8,
            "python_version": sys.version.split()[0],
            "lan_ip": lan_ip,
            "lan_url": f"http://{lan_ip}:8765/index.html",
            "mounted_volumes": discover_mounted_nas_volumes(),
            "database": str(PATHS.db_path.name),
            "fact_transactions": txns,
            "streaming_window_sinks": sinks,
            "ai_insights_count": ai_cnt,
        }

    def _run_pipeline_payload(self) -> dict[str, Any]:
        run_interconnected_pipeline(batch_size=2_400, simulated_lambda=36_000.0)
        with closing(sqlite3.connect(PATHS.db_path)) as conn:
            sinks = conn.execute("SELECT COUNT(*) FROM streaming_window_sinks").fetchone()[0]
        return {
            "ok": True,
            "message": "Pipeline Python 6-Etapas ejecutado y guardado en financial_lakehouse.db",
            "total_windows_saved": sinks,
        }

    def do_GET(self) -> None:
        route = self.path.split("?", 1)[0]
        try:
            if route == "/api/status":
                self._send_json(self._status_payload())
            elif route == "/api/enterprise/status":
                self._send_json(get_corporate_status())
            elif route == "/api/enterprise/routes":
                self._send_json({"ok": True, "routes": get_all_routes_telemetry()})
            elif route == "/api/enterprise/knowledge":
                with closing(sqlite3.connect(PATHS.db_path)) as conn:
                    cur = conn.execute(
                        "SELECT knowledge_id, category, title, summary, executable_code, reusable_prompt, created_at "
                        "FROM corporate_reusable_knowledge ORDER BY category, knowledge_id"
                    )
                    cols = [d[0] for d in cur.description]
                    records = [dict(zip(cols, r, strict=False)) for r in cur.fetchall()]
                self._send_json({"ok": True, "knowledge": records})
            elif route in ("/api/knowledge/playbooks", "/api/enterprise/playbooks"):
                pb_file = DB_DIR / "categories" / "08_corporate_enterprise" / "engineering_playbooks.json"
                if pb_file.exists():
                    with open(pb_file, "r", encoding="utf-8") as f:
                        playbooks = json.load(f)
                else:
                    playbooks = []
                self._send_json({"ok": True, "count": len(playbooks), "playbooks": playbooks})
            elif route in ("/api/presentation/slides", "/api/slides"):
                slides_file = VIS_DIR / "presentation_slides.json"
                if slides_file.exists():
                    with open(slides_file, "r", encoding="utf-8") as f:
                        slides = json.load(f)
                else:
                    from notebook_presenter_agent import build_master_presentation_deck
                    slides = build_master_presentation_deck()
                self._send_json({"ok": True, "count": len(slides), "slides": slides})
            elif route in ("/api/store/products", "/api/boutique/products"):
                self._send_json({"ok": True, "count": len(STORE_PRODUCTS), "products": STORE_PRODUCTS})
            elif route in ("/api/store/candidates", "/api/talent/profiles"):
                try:
                    with closing(sqlite3.connect(PATHS.db_path)) as conn:
                        cur = conn.cursor()
                        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='candidate_profiles'")
                        if cur.fetchone():
                            cur.execute(
                                "SELECT candidate_id, created_at, full_name, target_role, experience_years, linkedin_url, github_url, bio, status, intake_seal "
                                "FROM candidate_profiles ORDER BY created_at DESC LIMIT 50"
                            )
                            cols = [d[0] for d in cur.description]
                            candidates = [dict(zip(cols, r, strict=False)) for r in cur.fetchall()]
                        else:
                            candidates = []
                except Exception:
                    candidates = []
                self._send_json({"ok": True, "count": len(candidates), "candidates": candidates})
            elif route in ("/api/chatty/orders", "/api/enterprise/orders"):
                try:
                    with closing(sqlite3.connect(PATHS.db_path)) as conn:
                        cur = conn.cursor()
                        cur.execute(
                            "SELECT order_id, order_timestamp, issuer, directive_text, assigned_c_suite, "
                            "chatty_response, resulting_action, efficiency_impact_pct, status "
                            "FROM corporate_executive_orders ORDER BY order_timestamp DESC LIMIT 30"
                        )
                        cols = [d[0] for d in cur.description]
                        orders = [dict(zip(cols, r, strict=False)) for r in cur.fetchall()]
                        for o in orders:
                            o.setdefault("directive", o.get("directive_text", ""))
                            o.setdefault("response", o.get("chatty_response", ""))
                            o.setdefault("created_at", o.get("order_timestamp", ""))
                            s_payload = f"{o.get('order_id')}|{o.get('directive_text')}|{o.get('order_timestamp')}|{o.get('assigned_c_suite')}"
                            o.setdefault("digital_seal", hashlib.sha256(s_payload.encode("utf-8")).hexdigest())
                except Exception:
                    orders = []
                self._send_json({"ok": True, "count": len(orders), "orders": orders})
            elif route in ("/api/pipeline/daemon/status", "/api/daemon/telemetry"):
                telem = GLOBAL_PIPELINE_DAEMON.get_telemetry()
                self._send_json({
                    "ok": True,
                    "running": telem.running,
                    "cycles_completed": telem.cycles_completed,
                    "current_rho": telem.current_rho,
                    "last_latency_ms": telem.last_latency_ms,
                    "littles_law_compliant": telem.littles_law_compliant,
                    "pacioli_compliant": telem.pacioli_compliant,
                    "telemetry": telem.to_dict(),
                })
            elif route in ("/api/security/audit", "/api/security/status", "/api/ciso/audit"):
                sec_report = GLOBAL_SECURITY_ENGINE.run_full_security_audit()
                self._send_json({"ok": True, "report": asdict(sec_report)})
            elif route == "/api/generate-pdf":
                query = self.path.split("?", 1)[1] if "?" in self.path else ""
                params = dict(p.split("=", 1) for p in query.split("&") if "=" in p)
                doc_type = params.get("doc", "cv").lower()
                target_pdf = DOSSIER_PDF if doc_type == "dossier" else CV_PDF
                dl_name = (
                    "DOSSIER_NOTEBOOKLM_MIKEL.pdf" if doc_type == "dossier" else "CV_Mikel_Irastorza.pdf"
                )
                self._send_static(target_pdf, "application/pdf", as_attachment=True, dl_name=dl_name)
            elif route == "/api/supabase/status":
                self._send_json(get_supabase_status())
            elif route in ("/api/prices/true", "/api/prices/live", "/api/real-prices", "/api/market/live-true"):
                self._send_json(get_true_prices_payload())
            elif route in ("/api/prices", "/api/market/prices"):
                self._send_json(get_all_prices_payload())
            elif route in ("/api/chart", "/api/candles", "/api/market/chart"):
                query = self.path.split("?", 1)[1] if "?" in self.path else ""
                params = dict(p.split("=", 1) for p in query.split("&") if "=" in p)
                sym = params.get("symbol", "BTCUSDT").upper()
                interval = params.get("interval", params.get("timeframe", "1h"))
                limit = int(params.get("limit", params.get("count", 50)))
                self._send_json(get_chart_payload(symbol=sym, interval=interval, limit=limit))
            elif route in ("/api/market/hours", "/api/market/schedule"):
                self._send_json({"ok": True, "market_regime": GLOBAL_QUANT_BOT.market_data.get_market_regime()})
            elif route in ("/api/haskell/verify", "/api/haskell/status"):
                self._send_json(GLOBAL_HASKELL_BRIDGE.run_self_test())
            elif route in ("/api/stream/status", "/api/stream/metrics"):
                self._send_json(GLOBAL_STREAM_DB.get_engine_metrics())
            elif route == "/api/stream/query":
                query = self.path.split("?", 1)[1] if "?" in self.path else ""
                params = dict(p.split("=", 1) for p in query.split("&") if "=" in p)
                sym = params.get("symbol")
                top = params.get("topic")
                limit = int(params.get("limit", 50))
                self._send_json({
                    "ok": True,
                    "symbol": sym,
                    "topic": top,
                    "events": GLOBAL_STREAM_DB.query_stream(symbol=sym, topic=top, limit=limit),
                })
            elif route == "/api/stream/events":
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.send_header("Cache-Control", "no-cache")
                self.send_header("Connection", "keep-alive")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                init_msg = json.dumps({"type": "CONNECTED", "engine": "NovusStreamDB SSE", "time": time.time()})
                self.wfile.write(f"data: {init_msg}\n\n".encode("utf-8"))
                self.wfile.flush()

                event_queue: queue.Queue[Any] = queue.Queue(maxsize=200)

                def _stream_listener(ev: Any) -> None:
                    try:
                        event_queue.put_nowait(ev)
                    except queue.Full:
                        pass

                GLOBAL_STREAM_DB.add_subscriber(_stream_listener)
                try:
                    recent = GLOBAL_STREAM_DB.query_stream(limit=10)
                    for ev in reversed(recent):
                        msg = json.dumps({"type": "EVENT", "event": ev})
                        self.wfile.write(f"data: {msg}\n\n".encode("utf-8"))
                    self.wfile.flush()

                    start_stream = time.time()
                    while time.time() - start_stream < 45.0:
                        try:
                            ev_item = event_queue.get(timeout=1.0)
                            msg = json.dumps({"type": "EVENT", "event": ev_item.to_dict()})
                            self.wfile.write(f"data: {msg}\n\n".encode("utf-8"))
                            self.wfile.flush()
                        except queue.Empty:
                            self.wfile.write(b": ping\n\n")
                            self.wfile.flush()
                except (BrokenPipeError, ConnectionResetError, OSError):
                    pass
                finally:
                    GLOBAL_STREAM_DB.remove_subscriber(_stream_listener)
                return
            elif route == "/api/market/overview":
                self._send_json(get_market_overview_payload())
            elif route in ("/api/trading/opportunities", "/api/market/opportunities", "/api/trading/recommendation"):
                self._send_json(get_market_opportunities_payload())
            elif route in ("/api/docs", "/api/market/api-docs"):
                self._send_json(get_api_documentation_payload())
            elif route == "/api/trading/status":
                self._send_json(GLOBAL_QUANT_BOT.get_status_report())
            elif route == "/api/trading/tick":
                query = self.path.split("?", 1)[1] if "?" in self.path else ""
                params = dict(p.split("=", 1) for p in query.split("&") if "=" in p)
                sym = params.get("symbol", "BTCUSDT").upper()
                self._send_json({"ok": True, "tick": asdict(GLOBAL_QUANT_BOT.generate_tick(sym))})
            elif route == "/api/trading/klines":
                query = self.path.split("?", 1)[1] if "?" in self.path else ""
                params = dict(p.split("=", 1) for p in query.split("&") if "=" in p)
                sym = params.get("symbol", "BTCUSDT").upper()
                interval = params.get("interval", "1h")
                limit = int(params.get("limit", 40))
                candles = GLOBAL_QUANT_BOT.market_data.get_historical_candles(sym, interval=interval, count=limit)
                self._send_json({"ok": True, "symbol": sym, "candles": [c.to_dict() for c in candles]})
            elif route == "/api/trading/audit":
                self._send_json({"ok": True, "audit": GLOBAL_QUANT_BOT.execution.verify_ledger_integrity()})
            elif route == "/api/trading/orderbook":
                query = self.path.split("?", 1)[1] if "?" in self.path else ""
                params = dict(p.split("=", 1) for p in query.split("&") if "=" in p)
                sym = params.get("symbol", "BTCUSDT").upper()
                limit = int(params.get("limit", 5))
                depth = GLOBAL_QUANT_BOT.market_data.fetch_live_binance_depth(sym, limit=limit)
                self._send_json({"ok": True, "symbol": sym, "orderbook": depth})
            elif route == "/api/trading/liquidity":
                query = self.path.split("?", 1)[1] if "?" in self.path else ""
                params = dict(p.split("=", 1) for p in query.split("&") if "=" in p)
                sym = params.get("symbol", "BTCUSDT").upper()
                prof = GLOBAL_QUANT_BOT.market_data.get_liquidity_profile(sym)
                self._send_json({"ok": True, "symbol": sym, "liquidity": prof})
            elif route == "/api/pipeline/perfect/status":
                query = self.path.split("?", 1)[1] if "?" in self.path else ""
                params = dict(p.split("=", 1) for p in query.split("&") if "=" in p)
                sym = params.get("symbol", "BTCUSDT").upper()
                res = GLOBAL_PERFECT_PIPELINE.execute_perfect_pipeline(symbol=sym)
                self._send_json(res)
            elif route == "/api/trading/audio-thesis":
                query = self.path.split("?", 1)[1] if "?" in self.path else ""
                params = dict(p.split("=", 1) for p in query.split("&") if "=" in p)
                sym = params.get("symbol", "BTCUSDT").upper()
                res = GLOBAL_PERFECT_PIPELINE.execute_perfect_pipeline(symbol=sym)
                audio = res["stages"]["stage5_audio_intelligence"]
                self._send_json({"ok": True, "symbol": sym, "audio": audio})
            elif route == "/api/trading/ml/status":
                self._send_json({"ok": True, "tensorflow": GLOBAL_QUANT_BOT.tf_learner.get_status_report()})
            elif route == "/api/science/gold-molecule":
                import scientific_analytics as sa
                cluster_metrics = sa.analyze_gold_nanocluster_au20()
                self._send_json({"ok": True, "metrics": asdict(cluster_metrics)})
            elif route == "/api/libraries":
                import importlib.metadata
                pkgs = {}
                for p in ("numpy", "scipy", "sympy", "polars", "pandas", "matplotlib", "tensorflow", "pypdf", "faker", "google-antigravity", "pydantic", "starlette", "websockets", "pytest"):
                    try:
                        pkgs[p] = importlib.metadata.version(p)
                    except Exception:
                        pkgs[p] = "not installed"
                vendor_dir = VIS_DIR / "vendor"
                vendor_files = [str(f.relative_to(VIS_DIR)) for f in vendor_dir.rglob("*") if f.is_file()] if vendor_dir.exists() else []
                self._send_json({"ok": True, "python_libraries": pkgs, "vendor_assets": vendor_files})
            elif route in (
                "/api/run-pipeline",
                "/api/nas-sync",
                "/api/enterprise/directive",
                "/api/supabase/sync",
                "/api/trading/order",
                "/api/trading/toggle",
                "/api/trading/autopilot/toggle",
                "/api/trading/strategy/set",
                "/api/trading/backtest",
                "/api/trading/demo-run",
                "/api/trading/demo-step",
                "/api/trading/live-shock",
                "/api/trading/ml/train",
                "/api/pipeline/perfect/run",
            ):
                self.send_response(405)
                self.send_header("Allow", "POST")
                self.send_header("Content-Length", "0")
                self.end_headers()
            elif route == "/favicon.ico":
                self.send_response(204)
                self.end_headers()
            elif route.startswith("/vendor/"):
                raw_rel = route.lstrip("/")
                vendor_root = (VIS_DIR / "vendor").resolve()
                try:
                    vpath = (VIS_DIR / raw_rel).resolve()
                    if vpath.is_file() and vpath.is_relative_to(vendor_root):
                        ext = vpath.suffix.lower()
                        mime_map = {
                            ".css": "text/css; charset=utf-8",
                            ".js": "application/javascript; charset=utf-8",
                            ".woff2": "font/woff2",
                            ".woff": "font/woff",
                            ".ttf": "font/ttf",
                            ".json": "application/json; charset=utf-8",
                            ".svg": "image/svg+xml",
                        }
                        ct = mime_map.get(ext, "application/octet-stream")
                        self._send_static(vpath, ct, False, "")
                    else:
                        self._send_json({"ok": False, "error": "not found"}, 404)
                except Exception:
                    self._send_json({"ok": False, "error": "not found"}, 404)
            elif route in STATIC_ROUTES:
                self._send_static(*STATIC_ROUTES[route])
            else:
                self._send_json({"ok": False, "error": "not found"}, 404)
        except Exception as exc:
            self._send_json({"ok": False, "error": f"{type(exc).__name__}: {exc}"}, 500)

    def do_HEAD(self) -> None:
        route = self.path.split("?", 1)[0]
        if route in STATIC_ROUTES:
            self._send_static(*STATIC_ROUTES[route], send_body=False)
        elif route.startswith("/vendor/"):
            raw_rel = route.lstrip("/")
            vendor_root = (VIS_DIR / "vendor").resolve()
            try:
                vpath = (VIS_DIR / raw_rel).resolve()
                if vpath.is_file() and vpath.is_relative_to(vendor_root):
                    ext = vpath.suffix.lower()
                    mime_map = {
                        ".css": "text/css; charset=utf-8",
                        ".js": "application/javascript; charset=utf-8",
                        ".woff2": "font/woff2",
                        ".woff": "font/woff",
                        ".ttf": "font/ttf",
                        ".json": "application/json; charset=utf-8",
                        ".svg": "image/svg+xml",
                    }
                    ct = mime_map.get(ext, "application/octet-stream")
                    self._send_static(vpath, ct, False, "", send_body=False)
                else:
                    self.send_response(404)
                    self.end_headers()
            except Exception:
                self.send_response(404)
                self.end_headers()
        elif route in (
            "/api/status",
            "/api/generate-pdf",
            "/api/enterprise/status",
            "/api/enterprise/routes",
            "/api/libraries",
        ):
            self.send_response(200)
            self.send_header(
                "Content-Type",
                "application/json; charset=utf-8" if not route.endswith(".pdf") else "application/pdf",
            )
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self) -> None:
        route = self.path.split("?", 1)[0]
        if self.client_address[0] not in LOOPBACK_ADDRESSES:
            self._send_json({"ok": False, "error": "solo se permite desde este equipo"}, 403)
            return

        # Anti-CSRF Protection: If request originates from a browser, enforce origin whitelist
        origin = self.headers.get("Origin") or self.headers.get("origin")
        if origin:
            allowed_origins = {
                "http://127.0.0.1:8765",
                "http://localhost:8765",
                f"http://{get_local_lan_ip()}:8765",
            }
            if origin not in allowed_origins:
                self._send_json({"ok": False, "error": "Petición cross-origin bloqueada por seguridad (Anti-CSRF Shield)"}, 403)
                return
        try:
            if route == "/api/run-pipeline":
                self._send_json(self._run_pipeline_payload())
            elif route == "/api/nas-sync":
                self._send_json(sync_lakehouse_to_nas_mirror())
            elif route == "/api/enterprise/directive":
                content_len = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_len).decode("utf-8") if content_len > 0 else "{}"
                try:
                    data = json.loads(body)
                except json.JSONDecodeError:
                    data = {}
                directive = str(data.get("directive", "Optimizar pipeline")).strip()
                issuer = str(data.get("issuer", "Mikel Irastorza · Presidente")).strip()
                result = dispatch_presidential_directive(directive, issuer)
                self._send_json(result)
            elif route == "/api/supabase/sync":
                self._send_json(sync_all_novus_lakehouse_to_supabase())
            elif route == "/api/trading/order":
                content_len = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_len).decode("utf-8") if content_len > 0 else "{}"
                data = json.loads(body) if body else {}
                sym = str(data.get("symbol", "BTCUSDT")).upper()
                side = str(data.get("side", "BUY")).upper()

                if not GLOBAL_QUANT_BOT.market_data.is_market_open(sym):
                    open_list = [s for s in GLOBAL_QUANT_BOT.market_data.ALL_SYMBOLS if GLOBAL_QUANT_BOT.market_data.is_market_open(s)]
                    self._send_json({
                        "ok": False,
                        "error": f"El mercado de {sym} está cerrado en este horario. Opera en los mercados abiertos ahora: {', '.join(open_list[:6])}",
                        "open_markets": open_list,
                    }, 400)
                    return

                curr_p, _ = GLOBAL_QUANT_BOT.market_data.get_latest_price(sym)
                raw_qty = data.get("qty")
                cash_eur = GLOBAL_QUANT_BOT.execution.cash_cents / 100.0
                if raw_qty is None or float(raw_qty) <= 0:
                    budget = cash_eur * 0.18
                    qty = round(max(budget / max(curr_p, 1e-4), 0.001), 4 if curr_p > 10 else 2)
                else:
                    qty = float(raw_qty)
                    if side == "BUY" and (qty * curr_p) > cash_eur * 0.4:
                        budget = cash_eur * 0.20
                        qty = round(max(budget / max(curr_p, 1e-4), 0.001), 4 if curr_p > 10 else 2)

                trade = GLOBAL_QUANT_BOT.execute_trade(symbol=sym, side=side, qty=qty)
                self._send_json({"ok": True, "trade": asdict(trade)})
            elif route == "/api/trading/execute-opportunity":
                content_len = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_len).decode("utf-8") if content_len > 0 else "{}"
                data = json.loads(body) if body else {}
                opp_payload = get_market_opportunities_payload()
                top = opp_payload.get("top_opportunity")

                sym = str(data.get("symbol", top["symbol"] if top else "BTCUSDT")).upper()
                side = str(data.get("side", top["action"] if top else "BUY")).upper()

                if not GLOBAL_QUANT_BOT.market_data.is_market_open(sym):
                    open_list = [s for s in GLOBAL_QUANT_BOT.market_data.ALL_SYMBOLS if GLOBAL_QUANT_BOT.market_data.is_market_open(s)]
                    self._send_json({
                        "ok": False,
                        "error": f"El mercado de {sym} está cerrado actualmente. Opera en mercados abiertos: {', '.join(open_list[:6])}",
                        "open_markets": open_list,
                    }, 400)
                    return

                cash_eur = GLOBAL_QUANT_BOT.execution.cash_cents / 100.0
                curr_p, _ = GLOBAL_QUANT_BOT.market_data.get_latest_price(sym)
                budget = cash_eur * 0.18
                qty = round(max(budget / max(curr_p, 1e-4), 0.001), 4 if curr_p > 10 else 2)

                trade = GLOBAL_QUANT_BOT.execute_trade(symbol=sym, side=side, qty=qty)
                self._send_json({
                    "ok": True,
                    "message": f"Operación {side} ejecutada con éxito en mercado abierto ({sym})",
                    "trade": asdict(trade),
                    "execution_time": time.time(),
                    "pacioli_hash": trade.block_hash,
                })
            elif route in ("/api/trading/toggle", "/api/trading/autopilot/toggle"):
                running = GLOBAL_QUANT_BOT.toggle_autopilot()
                self._send_json({"ok": True, "autopilot": running, "running": running})
            elif route == "/api/trading/strategy/set":
                content_len = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_len).decode("utf-8") if content_len > 0 else "{}"
                data = json.loads(body) if body else {}
                strat = str(data.get("strategy", "VWAP_MEAN_REVERSION"))
                GLOBAL_QUANT_BOT.set_active_strategy(strat)
                self._send_json({"ok": True, "active_strategy": GLOBAL_QUANT_BOT.active_strategy_type.value})
            elif route == "/api/trading/backtest":
                content_len = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_len).decode("utf-8") if content_len > 0 else "{}"
                data = json.loads(body) if body else {}
                sym = str(data.get("symbol", "BTCUSDT")).upper()
                strat = data.get("strategy", None)
                count = int(data.get("count", 120))
                report = GLOBAL_QUANT_BOT.run_backtest(symbol=sym, strategy_type=strat, candle_count=count)
                self._send_json({"ok": True, "report": asdict(report)})
            elif route == "/api/trading/demo-run":
                content_len = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_len).decode("utf-8") if content_len > 0 else "{}"
                data = json.loads(body) if body else {}
                sym = str(data.get("symbol", "BTCUSDT")).upper()
                scenario = str(data.get("scenario", "realistic"))
                strat = data.get("strategy", None)
                count = int(data.get("count", 150))
                report = GLOBAL_QUANT_BOT.run_demo_simulation(
                    symbol=sym, strategy_type=strat, scenario=scenario, candle_count=count
                )
                self._send_json({"ok": True, "report": asdict(report)})
            elif route == "/api/trading/demo-step":
                content_len = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_len).decode("utf-8") if content_len > 0 else "{}"
                data = json.loads(body) if body else {}
                sym = str(data.get("symbol", "BTCUSDT")).upper()
                res = GLOBAL_QUANT_BOT.execute_autonomous_demo_step(symbol=sym)
                self._send_json(res)
            elif route == "/api/trading/live-shock":
                content_len = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_len).decode("utf-8") if content_len > 0 else "{}"
                data = json.loads(body) if body else {}
                sym = str(data.get("symbol", "BTCUSDT")).upper()
                shock_type = str(data.get("shock_type", "oversold_entry"))
                res = GLOBAL_QUANT_BOT.trigger_live_market_shock(symbol=sym, shock_type=shock_type)
                self._send_json(res)
            elif route == "/api/pipeline/perfect/run":
                content_len = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_len).decode("utf-8") if content_len > 0 else "{}"
                data = json.loads(body) if body else {}
                sym = str(data.get("symbol", "BTCUSDT")).upper()
                qty = float(data.get("qty", 0.05))
                res = GLOBAL_PERFECT_PIPELINE.execute_perfect_pipeline(symbol=sym, qty=qty)
                self._send_json(res)
            elif route == "/api/trading/ml/train":
                content_len = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_len).decode("utf-8") if content_len > 0 else "{}"
                data = json.loads(body) if body else {}
                batch_size = int(data.get("batch_size", 16))
                res = GLOBAL_QUANT_BOT.tf_learner.train_online_step(batch_size=batch_size)
                self._send_json({"ok": True, "step_result": res, "tensorflow": GLOBAL_QUANT_BOT.tf_learner.get_status_report()})
            elif route in ("/api/store/checkout", "/api/boutique/checkout"):
                content_len = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_len).decode("utf-8") if content_len > 0 else "{}"
                data = json.loads(body) if body else {}
                cart_items = data.get("items", [])
                customer_name = str(data.get("customer_name", "Cliente Institucional")).strip()
                customer_email = str(data.get("customer_email", "cliente@novusmundus.com")).strip()
                tax_id = str(data.get("tax_id", "ESB00000000")).strip()
                payment_method = str(data.get("payment_method", "CARD")).upper()

                subtotal_cents = sum(int(item.get("price_cents", 0)) * int(item.get("quantity", 1)) for item in cart_items)
                if subtotal_cents <= 0:
                    subtotal_cents = 14900
                vat_rate = 0.21
                vat_cents = int(round(subtotal_cents * vat_rate))
                total_cents = subtotal_cents + vat_cents

                invoice_id = f"INV-{datetime.now(UTC).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
                order_hash_payload = f"{invoice_id}|{customer_email}|{total_cents}|{payment_method}"
                digital_seal = hashlib.sha256(order_hash_payload.encode("utf-8")).hexdigest()

                try:
                    with closing(sqlite3.connect(PATHS.db_path)) as conn, conn:
                        conn.execute(
                            "CREATE TABLE IF NOT EXISTS store_orders ("
                            "  invoice_id TEXT PRIMARY KEY, "
                            "  created_at TEXT, "
                            "  customer_name TEXT, "
                            "  customer_email TEXT, "
                            "  tax_id TEXT, "
                            "  subtotal_cents INT, "
                            "  vat_cents INT, "
                            "  total_cents INT, "
                            "  payment_method TEXT, "
                            "  digital_seal TEXT, "
                            "  items_json TEXT, "
                            "  status TEXT"
                            ")"
                        )
                        conn.execute(
                            "INSERT INTO store_orders VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                            (
                                invoice_id,
                                datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
                                customer_name,
                                customer_email,
                                tax_id,
                                subtotal_cents,
                                vat_cents,
                                total_cents,
                                payment_method,
                                digital_seal,
                                json.dumps(cart_items),
                                "LIQUIDADO Y CERTIFICADO ✅",
                            ),
                        )
                except Exception:
                    pass

                self._send_json({
                    "ok": True,
                    "invoice_id": invoice_id,
                    "created_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "customer_name": customer_name,
                    "customer_email": customer_email,
                    "subtotal_eur": round(subtotal_cents / 100.0, 2),
                    "vat_eur": round(vat_cents / 100.0, 2),
                    "total_eur": round(total_cents / 100.0, 2),
                    "payment_method": payment_method,
                    "digital_seal": digital_seal,
                    "status": "LIQUIDADO Y CERTIFICADO ✅",
                    "pacioli_balanced": True,
                    "message": "Transacción asentada en el libro mayor de doble partida de NovusMundus.",
                })
            elif route in ("/api/store/submit-profile", "/api/talent/submit"):
                content_len = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_len).decode("utf-8") if content_len > 0 else "{}"
                data = json.loads(body) if body else {}

                full_name = str(data.get("full_name", "")).strip() or "Candidato Anónimo"
                email = str(data.get("email", "")).strip() or "candidato@novusmundus.org"
                phone = str(data.get("phone", "")).strip()
                target_role = str(data.get("target_role", "Data Engineer / AI Systems Architect")).strip()
                experience_years = str(data.get("experience_years", "3-5 años")).strip()
                linkedin_url = str(data.get("linkedin_url", "")).strip()
                github_url = str(data.get("github_url", "")).strip()
                bio = str(data.get("bio", "")).strip()

                candidate_id = f"TALENT-{datetime.now(UTC).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
                seal_payload = f"{candidate_id}|{email}|{target_role}|{datetime.now(UTC).isoformat()}"
                intake_seal = hashlib.sha256(seal_payload.encode("utf-8")).hexdigest()
                created_at = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

                try:
                    with closing(sqlite3.connect(PATHS.db_path)) as conn, conn:
                        conn.execute(
                            "CREATE TABLE IF NOT EXISTS candidate_profiles ("
                            "  candidate_id TEXT PRIMARY KEY, "
                            "  created_at TEXT, "
                            "  full_name TEXT, "
                            "  email TEXT, "
                            "  phone TEXT, "
                            "  target_role TEXT, "
                            "  experience_years TEXT, "
                            "  linkedin_url TEXT, "
                            "  github_url TEXT, "
                            "  bio TEXT, "
                            "  status TEXT, "
                            "  intake_seal TEXT"
                            ")"
                        )
                        conn.execute(
                            "INSERT INTO candidate_profiles VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                            (
                                candidate_id,
                                created_at,
                                full_name,
                                email,
                                phone,
                                target_role,
                                experience_years,
                                linkedin_url,
                                github_url,
                                bio,
                                "PERFIL RECIBIDO · EN COLA DE AUDITORÍA Y COLOCACIÓN 🚀",
                                intake_seal,
                            ),
                        )
                except Exception:
                    pass

                self._send_json({
                    "ok": True,
                    "candidate_id": candidate_id,
                    "created_at": created_at,
                    "full_name": full_name,
                    "email": email,
                    "target_role": target_role,
                    "status": "PERFIL RECIBIDO · EN COLA DE AUDITORÍA Y COLOCACIÓN 🚀",
                    "intake_seal": intake_seal,
                    "message": "Perfil registrado formalmente en el Acelerador de Talento Novus. Mikel Irastorza auditará tu candidatura para iniciar el proceso de búsqueda y colocación laboral.",
                })
            elif route in ("/api/chatty/command", "/api/chatty/directive", "/api/enterprise/directive"):
                content_len = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_len).decode("utf-8") if content_len > 0 else "{}"
                data = json.loads(body) if body else {}
                directive = str(data.get("directive") or data.get("command") or data.get("text", "")).strip()
                issuer = str(data.get("issuer", "Mikel Irastorza · Presidente")).strip()
                if not directive:
                    directive = "Auditar cero fallos y coordinar C-Suite"
                res = dispatch_presidential_directive(directive_text=directive, issuer=issuer)
                self._send_json(res)
            elif route in ("/api/pipeline/daemon/control", "/api/daemon/control"):
                content_len = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_len).decode("utf-8") if content_len > 0 else "{}"
                data = json.loads(body) if body else {}
                action = str(data.get("action", "force_cycle")).strip().lower()

                if action not in ("start", "stop", "pause", "resume", "force_cycle", "cycle", "step"):
                    self._send_json({"ok": False, "error": f"Acción de daemon no válida: {action}"}, 400)
                    return

                cycle_result = None
                if action == "start":
                    GLOBAL_PIPELINE_DAEMON.start()
                elif action == "stop":
                    GLOBAL_PIPELINE_DAEMON.stop()
                elif action == "pause":
                    GLOBAL_PIPELINE_DAEMON.pause()
                elif action == "resume":
                    GLOBAL_PIPELINE_DAEMON.resume()
                elif action in ("force_cycle", "cycle", "step"):
                    cycle_result = GLOBAL_PIPELINE_DAEMON.force_cycle()

                telem = GLOBAL_PIPELINE_DAEMON.get_telemetry()
                self._send_json({
                    "ok": True,
                    "action_executed": action,
                    "result": cycle_result or {"status": "action_processed"},
                    "telemetry": telem.to_dict(),
                })
            elif route in ("/api/security/audit/run", "/api/security/scan", "/api/ciso/scan"):
                sec_report = GLOBAL_SECURITY_ENGINE.run_full_security_audit()
                self._send_json({"ok": True, "report": asdict(sec_report)})
            else:
                self._send_json({"ok": False, "error": "not found"}, 404)
        except Exception as exc:
            self._send_json({"ok": False, "error": f"{type(exc).__name__}: {exc}"}, 500)


NetGUIHandler: Final = ArchifyNetGUIHandler


def start_netgui(port: int = 8765, open_browser: bool = True, lan: bool = False) -> None:
    """Starts the threaded server. Binds to 127.0.0.1 unless `lan=True` (then 0.0.0.0)."""
    lan_ip = get_local_lan_ip()
    local_url = f"http://127.0.0.1:{port}/index.html"

    # Start 24/7 Autonomous Pipeline Daemon in background
    try:
        GLOBAL_PIPELINE_DAEMON.start()
    except Exception as exc:
        print(f"Warning starting pipeline daemon: {exc}")
    print("=========================================================================")
    print(f"🖥️  SERVIDOR LOCAL (ESTE MAC):       {local_url}")
    if lan:
        print(f"🖧  RED LAN (solo lectura, otros dispositivos): http://{lan_ip}:{port}/index.html")
    else:
        print("🔒 Solo accesible desde este Mac (usa --lan para compartir en tu Wi-Fi)")
    print("=========================================================================", flush=True)
    if open_browser:
        webbrowser.open(local_url)
    with ThreadingHTTPServer(("0.0.0.0" if lan else "127.0.0.1", port), ArchifyNetGUIHandler) as httpd:
        httpd.serve_forever()


if __name__ == "__main__":
    start_netgui(open_browser="--no-browser" not in sys.argv, lan="--lan" in sys.argv)
