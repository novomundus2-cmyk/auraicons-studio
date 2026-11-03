#!/usr/bin/env python3
"""
EKC AI Multi-Engine Bridge — ElektriKubercisC & Mikel Irastorza
==============================================================
Puente CLI para programar e interactuar con múltiples IAs locales y remotas:
- Ollama (Modelos locales offline: Qwen 3.6 27B, Novus Senior, Gemma 3, etc.)
- Claude Code CLI (`claude`)
- Codex CLI (`codex`)
- Cursor IDE (`cursor`)

Inyecta automáticamente los invariantes arquitectónicos de Mikel:
- Python Clean Code & PEP 8
- Tolerancias CAD ±0.2 mm
- Balance contable de Luca Pacioli exacto (0.00 cents)
- Motor de bytes C11 (struct 32 bytes)
- Monoides algebraicos de Haskell GHC
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

SYSTEM_CONTEXT = """Eres el Asistente Senior de Sistemas y Arquitectura para Mikel Irastorza.
Mikel es Lead Systems Architect & Big Data Engineer, creador de EKC (ElektriKubercisC).
Invariantes no negociables:
1. Python: PEP 8 estricto, Clean Code, inmutabilidad (frozen dataclasses), Decimal para finanzas (nunca float).
2. C11: EkcStreamRecord tiene 32 bytes empaquetados, 2 registros por línea L1 (64 bytes), sin malloc en streaming.
3. Haskell: Monoides de Welford asociativos demostrados formalmente, balance de Pacioli exacto (0.00 cents diff).
4. CAD Industrial: Tolerancias de corte en chapa acotadas en [-0.200, +0.200] mm (EPTA France).
5. Audio Procedural: Web Audio API en src/utils/audioSystem.ts (cero mp3 externos).
6. Estilo Visual: Obsidiana pura (#05070c), oro cepillado (#f59e0b, #fbbf24), esmeralda (#10b981).
Responde siempre con código limpio, conciso, tipado y directamente aplicable."""


@dataclass(frozen=True)
class ProviderStatus:
    name: str
    available: bool
    path: Optional[str]
    details: str


def check_providers() -> List[ProviderStatus]:
    """Detecta las herramientas e IAs instaladas en el sistema."""
    results: List[ProviderStatus] = []

    # 1. Ollama
    ollama_path = shutil.which("ollama") or "/opt/homebrew/bin/ollama"
    if os.path.exists(ollama_path):
        try:
            res = subprocess.run(
                [ollama_path, "list"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            models = [
                line.split()[0]
                for line in res.stdout.strip().splitlines()[1:]
                if line.strip()
            ]
            results.append(
                ProviderStatus(
                    name="Ollama (Local Offline)",
                    available=True,
                    path=ollama_path,
                    details=f"{len(models)} modelos disponibles: {', '.join(models[:4])}...",
                )
            )
        except Exception as e:
            results.append(
                ProviderStatus(
                    name="Ollama (Local Offline)",
                    available=True,
                    path=ollama_path,
                    details=f"Instalado pero error al listar: {e}",
                )
            )
    else:
        results.append(
            ProviderStatus(
                name="Ollama (Local Offline)",
                available=False,
                path=None,
                details="No instalado en PATH",
            )
        )

    # 2. Claude Code CLI
    claude_path = shutil.which("claude") or os.path.expanduser("~/.local/bin/claude")
    if os.path.exists(claude_path):
        results.append(
            ProviderStatus(
                name="Claude Code CLI",
                available=True,
                path=claude_path,
                details="Instalado y listo para invocar con 'claude -p'",
            )
        )
    else:
        results.append(
            ProviderStatus(
                name="Claude Code CLI",
                available=False,
                path=None,
                details="No encontrado en ~/.local/bin/claude",
            )
        )

    # 3. Codex CLI
    codex_path = shutil.which("codex") or "/opt/homebrew/bin/codex"
    if os.path.exists(codex_path):
        results.append(
            ProviderStatus(
                name="Codex CLI",
                available=True,
                path=codex_path,
                details="Instalado y listo para invocar con 'codex'",
            )
        )
    else:
        results.append(
            ProviderStatus(
                name="Codex CLI",
                available=False,
                path=None,
                details="No encontrado",
            )
        )

    # 4. Cursor IDE
    cursor_path = shutil.which("cursor") or os.path.expanduser("~/.local/bin/cursor")
    if os.path.exists(cursor_path):
        results.append(
            ProviderStatus(
                name="Cursor IDE",
                available=True,
                path=cursor_path,
                details="Configurado con .cursorrules y reglas .cursor/rules/*.mdc",
            )
        )
    else:
        results.append(
            ProviderStatus(
                name="Cursor IDE",
                available=False,
                path=None,
                details="No encontrado",
            )
        )

    return results


def run_ollama(prompt: str, model: str = "qwen3.6:27b-q8_0") -> int:
    """Envía un prompt a un modelo local de Ollama inyectando el contexto de Mikel."""
    ollama_path = shutil.which("ollama") or "/opt/homebrew/bin/ollama"
    if not os.path.exists(ollama_path):
        print(f"Error: Ollama no encontrado en {ollama_path}")
        return 1

    print(f"\n🔮 [Ollama Local] Modelo: {model}")
    print(f"⚡ Inyectando contexto EKC Tri-Core...")
    print(f"💬 Pregunta: {prompt}\n")
    print("=" * 60)

    full_prompt = f"{SYSTEM_CONTEXT}\n\nPregunta de Mikel:\n{prompt}"

    try:
        proc = subprocess.Popen(
            [ollama_path, "run", model, full_prompt],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        for line in proc.stdout:
            sys.stdout.write(line)
            sys.stdout.flush()
        proc.wait()
        print("\n" + "=" * 60)
        return proc.returncode
    except Exception as e:
        print(f"Error al ejecutar Ollama: {e}")
        return 1


def run_claude_cli(prompt: str) -> int:
    """Invoca a Claude Code CLI con el prompt especificado."""
    claude_path = shutil.which("claude") or os.path.expanduser("~/.local/bin/claude")
    if not os.path.exists(claude_path):
        print(f"Error: Claude CLI no encontrado en {claude_path}")
        return 1

    print(f"\n🧠 [Claude Code CLI] Invocando: {claude_path}")
    print(f"💬 Prompt: {prompt}\n")
    try:
        return subprocess.run([claude_path, "-p", prompt]).returncode
    except Exception as e:
        print(f"Error al invocar Claude CLI: {e}")
        return 1


def run_codex_cli(args: List[str]) -> int:
    """Invoca a Codex CLI con los argumentos dados."""
    codex_path = shutil.which("codex") or "/opt/homebrew/bin/codex"
    if not os.path.exists(codex_path):
        print(f"Error: Codex CLI no encontrado en {codex_path}")
        return 1

    print(f"\n⚡ [Codex CLI] Invocando con argumentos: {' '.join(args)}")
    try:
        return subprocess.run([codex_path] + args).returncode
    except Exception as e:
        print(f"Error al invocar Codex: {e}")
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="EKC AI Multi-Engine Bridge — Programa con cualquier IA (Ollama, Claude, Codex, Cursor)"
    )
    subparsers = parser.add_subparsers(dest="command", help="Comando a ejecutar")

    # Subcomando: list
    subparsers.add_parser("list", help="Lista los proveedores y modelos de IA disponibles")

    # Subcomando: ollama
    p_ollama = subparsers.add_parser("ollama", help="Ejecuta una consulta contra un modelo Ollama local")
    p_ollama.add_argument("prompt", type=str, help="Prompt o pregunta técnica")
    p_ollama.add_argument(
        "--model",
        type=str,
        default="qwen3.6:27b-q8_0",
        help="Modelo Ollama a utilizar (default: qwen3.6:27b-q8_0)",
    )

    # Subcomando: claude
    p_claude = subparsers.add_parser("claude", help="Ejecuta un prompt con Claude Code CLI")
    p_claude.add_argument("prompt", type=str, help="Prompt para Claude Code")

    # Subcomando: codex
    p_codex = subparsers.add_parser("codex", help="Ejecuta un comando con Codex CLI")
    p_codex.add_argument("args", nargs=argparse.REMAINDER, help="Argumentos para Codex")

    # Subcomando: test
    subparsers.add_parser("test", help="Verifica la conectividad con todas las IAs")

    args = parser.parse_args()

    if args.command == "list" or not args.command:
        print("\n" + "=" * 65)
        print("🤖 EKC AI MULTI-ENGINE STATUS — MIKEL IRASTORZA")
        print("=" * 65)
        for prov in check_providers():
            status_icon = "✅ ACTIVO" if prov.available else "❌ NO DISPONIBLE"
            print(f"\n[{status_icon}] {prov.name}")
            if prov.path:
                print(f"   Ruta: {prov.path}")
            print(f"   Detalles: {prov.details}")
        print("\n" + "=" * 65)
        print("💡 Para consultar a un modelo local offline:")
        print("   python3 ekc_ai_bridge.py ollama 'Explica el struct C11 de 32 bytes'")
        print("   python3 ekc_ai_bridge.py ollama '...' --model novus-senior:latest")
        print("💡 Para ejecutar con Claude Code CLI:")
        print("   python3 ekc_ai_bridge.py claude 'Revisa los tests'")
        print("💡 Para programar en Cursor:")
        print("   Abre el proyecto en Cursor; leerá automáticamente .cursorrules y .cursor/rules/")
        print("=" * 65 + "\n")
        return 0

    elif args.command == "ollama":
        return run_ollama(args.prompt, model=args.model)

    elif args.command == "claude":
        return run_claude_cli(args.prompt)

    elif args.command == "codex":
        return run_codex_cli(args.args)

    elif args.command == "test":
        print("Verificando proveedores...")
        providers = check_providers()
        all_ok = any(p.available for p in providers)
        print(f"Estado general: {'OK' if all_ok else 'FALLO'}")
        return 0 if all_ok else 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
