# EKC (ElektriKubercisC) — Arquitectura de Sistemas y Enjambre Multi-Agente
### Mikel Irastorza · Lead Systems Architect & Big Data Engineer (EFA)

[![Verification](https://img.shields.io/badge/Verification-10%2F10%20Passes%20(Grade%20A%2B)-f59e0b?style=for-the-badge&logo=shield)](verify_10_passes.py)
[![Architecture](https://img.shields.io/badge/Core-C11%20%7C%20Haskell%20GHC%20%7C%20Python%203.14-10b981?style=for-the-badge)](CV/03_math_haskell_python/)
[![Persistence](https://img.shields.io/badge/SQLite%20WAL-9%20Agents-3b82f6?style=for-the-badge)](EKC_AGENTS/)
[![Privacy](https://img.shields.io/badge/Security-Air--Gapped%20%7C%20Zero--Trust-8b5cf6?style=for-the-badge)](publish_live_control.py)

---

## 1. Visión y Propósito del Ecosistema

**EKC (ElektriKubercisC)** es el núcleo de ingeniería distribuida diseñado y desarrollado por **Mikel Irastorza**. Integra tres pilares fundamentales:
1. **Tri-Core Matemático de Precisión**: Pruebas formales categoriales en **Haskell GHC**, motor de bytes a nivel de línea de caché L1 en **C11**, y orquestación de alto nivel con **Python Clean Code** (PEP 8, inmutabilidad y aritmética `Decimal` exacta).
2. **Enjambre Multi-Agente ("The Brothers")**: 9 agentes autónomos especializados con bases de datos persistentes SQLite en modo WAL, búsqueda de texto completo FTS5 y cadenas de auditoría SHA-256.
3. **Interoperabilidad Universal Multi-IA**: Compatibilidad completa y sin alucinaciones para ser programado, auditado o extendido con **Claude Code CLI**, **Cursor IDE**, **Codex CLI**, **GitHub Copilot**, **Windsurf**, **Aider**, **IAs Web** (ChatGPT, DeepSeek) y modelos locales offline en **Ollama**.

---

## 2. Mapa Completo de Archivos y Organización del Repositorio

El proyecto está rigurosamente ordenado para que cualquier ingeniero, revisor o agente de IA pueda utilizar cada componente sin fricción:

```text
├── README.md                            # Guía maestra de arquitectura y manual operativo
├── CLAUDE.md                            # Instrucciones nativas para Claude Code CLI y Claude Desktop
├── .cursorrules                         # Reglas maestras para Cursor IDE
├── .cursor/rules/                       # Reglas avanzadas contextuales de Cursor
│   ├── ekc-tri-core.mdc                 # Invariantes de Python, C11 y Haskell
│   └── the-brothers-agents.mdc          # Persistencia y contratos de los 9 agentes
├── .github/copilot-instructions.md      # Instrucciones para GitHub Copilot
├── AGENTS.md                            # Estándar universal para Codex, Windsurf y Aider
├── PROMPT_SYSTEM.md                     # Prompt de sistema para ChatGPT, DeepSeek, Claude Web y Gemini
├── ekc_ai_bridge.py                     # Puente CLI para modelos locales Ollama y CLIs de IA
├── verify_10_passes.py                  # Suite de verificación integral de 10 pasadas (Grado A+)
├── publish_live_control.py              # Conmutador de privacidad y publicación (lock/unlock)
├── sync_ekc_math_to_dbs.py              # Sincronizador de registros matemáticos a SQLite WAL
├── abrir_en_windows.bat                 # Script de arranque en un clic para sistemas Windows
│
├── EKC_AGENTS/                          # Bases de datos SQLite WAL de los 9 agentes autónomos
│   ├── david.db                         # EKC - David (Orquestador maestro y cronología)
│   ├── salomon.db                       # EKC - Salomón (Gobernanza y balance Pacioli 1494)
│   ├── bezalel.db                       # EKC - Bezalel (Arquitectura de datos y CAD ±0.2 mm)
│   ├── san_miguel_arcangel.db           # EKC - San Miguel Arcángel (Ciberseguridad y firmas SHA-256)
│   ├── gabriel.db                       # EKC - Gabriel (Mensajería inter-agente)
│   ├── rafael.db                        # EKC - Rafael (Salud y watchdog de latencia)
│   ├── uriel.db                         # EKC - Uriel (Inteligencia analítica y Z-Score)
│   ├── daniel.db                        # EKC - Daniel (Microestructura y señales de mercado)
│   └── nehemias.db                      # EKC - Nehemías (Resiliencia y recuperación ante desastres)
│
├── CV/                                  # Módulos técnicos y laboratorios de producción
│   ├── 03_math_haskell_python/          # Núcleo Tri-Core Matemático
│   │   ├── ekc_byte_engine.c            # Motor C11 bare-metal (structs 32 bytes empaquetados)
│   │   ├── ekc_byte_engine.h            # Cabecera de tipos y prototipos C
│   │   ├── libekc_byte_engine.dylib     # Binario dinámico compilado para macOS ARM64
│   │   ├── ekc_math_proofs.hs           # Pruebas formales inductivas en Haskell GHC 9.14
│   │   └── ekc_clean_math.py            # Orquestador Python Clean Code con Decimal y ctypes FFI
│   ├── 05_archify_visualizer/           # Visualizador de grafos y servidor NetGUI (puerto 8765)
│   └── 07_trading_bot/                  # Motor cuantitativo y libro de órdenes L2/L3
│
├── public/                              # Recursos públicos estáticos
│   └── llms.txt                         # Especificación machine-readable para LLMs y crawlers
└── dist/                                # Compilados listos para distribución
```

---

## 3. Invariantes de Ingeniería No Negociables

| Dominio | Invariante Matemático / Técnico | Mecanismo de Validación |
|---|---|---|
| **Contabilidad** | Balance Contable = `0.00` céntimos exactos | Libro mayor de Luca Pacioli (1494) implementado con `Decimal` en Python y `Rational` en Haskell. Cero aritmética de coma flotante para divisas. |
| **CAD Industrial** | Tolerancia dimensional $[-0.200, +0.200]\text{ mm}$ | Cotas heredadas de células robóticas de plegado y corte de chapa en EPTA France. |
| **Estadística Streaming** | Monoide de Welford-Chan $(A \oplus B) \oplus C \equiv A \oplus (B \oplus C)$ | Asociatividad demostrada en Haskell dentro del epsilon de máquina ($2.22 \times 10^{-16}$) y ejecutada en $3.45\ \mu\text{s}$ con C11 SIMD. |
| **Memoria y Caché** | Struct `EkcStreamRecord` empaquetado a exactamente 32 bytes | Dos registros encajan en una línea de caché L1 de 64 bytes (`__attribute__((packed))`). Cero `malloc` en streaming. |
| **Ciberseguridad** | Red privada en `127.0.0.1` y despliegues con SSO | Cortafuegos local, firma criptográfica SHA-256 y control air-gap vía `publish_live_control.py`. |

---

## 4. Guía de Ejecución Rápida (Multi-Plataforma)

La aplicación web usa Node 24 y npm como instalación principal: `npm ci`,
`npm run lint` y `npm run build`. `package-lock.json` fija ese entorno.
También se conserva `bun.lock` para Bun 1.4.4: `bun install --frozen-lockfile`.
La CI instala, audita y comprueba ambos árboles de dependencias por separado;
un audit de npm no cubre las versiones de Bun. Al actualizar dependencias,
revisa ambos locks y ejecuta `npm audit --include=dev --audit-level=low`
y `bun audit --audit-level=low`.

Los laboratorios Python mantienen entornos separados: PySpark usa Python 3.10
y Java 17; la plataforma de `CV/` se comprueba con Python 3.12. La CI audita
los requirements y los dos locks de uv, e incluye una prueba del cliente Kafka
con datos sintéticos, sin broker ni acceso a la base de datos local.

### En macOS y Linux

```bash
# 1. Ejecutar la suite de verificación de 10 pasadas
python3 verify_10_passes.py

# 2. Ejecutar el Tri-Core matemático (Python + C + Haskell)
python3 CV/03_math_haskell_python/ekc_clean_math.py

# 3. Sincronizar datos con las bases de datos de los agentes
python3 sync_ekc_math_to_dbs.py

# 4. Consultar a las IAs locales offline (Ollama)
python3 ekc_ai_bridge.py list
python3 ekc_ai_bridge.py ollama "Explica los invariantes de EKC"
```

### En Windows

Haz doble clic en `abrir_en_windows.bat` o ejecuta en PowerShell:
```cmd
abrir_en_windows.bat
```

### En Móvil y Web (iOS / Android)

La interfaz web del Portfolio (`http://127.0.0.1:3222`) y del Visualizador NetGUI (`http://127.0.0.1:8765`) están diseñadas con **diseño responsivo adaptativo**, probadas para resoluciones desde smartphones (390 px) hasta pantallas panorámicas de 4K.

---

## 5. Control de Privacidad y Publicación en Directo

El repositorio y sus despliegues están actualmente en **modo Privado** para proteger la propiedad intelectual:

```bash
# Consultar estado:
python3 publish_live_control.py status

# Publicar en abierto cuando Mikel lo decida:
python3 publish_live_control.py unlock

# Volver a bloquear en privado:
python3 publish_live_control.py lock
```

---

## 6. Contacto y Autoría

- **Autor**: Mikel Irastorza
- **Especialidad**: Lead Systems Architect & Big Data Engineer (EFA)
- **GitHub**: [@novomundus2-cmyk](https://github.com/novomundus2-cmyk)
- **Email**: [mikelirastorza24@gmail.com](mailto:mikelirastorza24@gmail.com)