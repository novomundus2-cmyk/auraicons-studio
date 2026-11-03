# CLAUDE.md — EKC (ElektriKubercisC) & Mikel Irastorza Ecosystem

Este archivo es leído automáticamente por **Claude Code CLI** y **Claude Desktop** al inicializarse en este repositorio. Define las reglas de arquitectura, estilo de código, comandos operativos e invariantes matemáticos no negociables.

---

## 1. Identidad y Misión del Proyecto

- **Autor**: Mikel Irastorza · Lead Systems Architect & Big Data Engineer.
- **Ecosistema**: EKC (ElektriKubercisC) — Sistema Multi-Agente Distribuido ("The Brothers").
- **Estilo de Diseño**: Lujo industrial honesto, obsidiana profunda (`#05070c`), oro cepillado (`#f59e0b`, `#fbbf24`), tipografía monoespaciada para métricas, cero plantillas genéricas de IA.
- **Filosofía**: Código limpio en Python (PEP 8, tipado estricto, inmutabilidad), motores de bytes en C11 para latencia sub-microsegundo, y pruebas algebraicas formales en Haskell GHC.

---

## 2. Arquitectura Tri-Core

El núcleo computacional opera en tres niveles matemáticos integrados:

```
┌────────────────────────────────────────────────────────┐
│  Python 3.14 Clean Code (ekc_clean_math.py)            │
│  - PEP 8, frozen dataclasses, Decimal arithmetic       │
│  - Orquestador de alto nivel & ctypes FFI zero-copy    │
└──────────────────────────┬─────────────────────────────┘
                           │
             ┌─────────────┴─────────────┐
             ▼                           ▼
┌───────────────────────────┐ ┌──────────────────────────┐
│ C11 Byte Engine           │ │ Haskell GHC Invariants   │
│ (ekc_byte_engine.c)       │ │ (ekc_math_proofs.hs)     │
│ - Packed 32-byte structs  │ │ - Monoides de Welford    │
│ - 2 structs / L1 64B line │ │ - Balance Pacioli exacto │
│ - SIMD Welford variance   │ │ - Verificación de tipos  │
│ - Tolerancias CAD ±0.2 mm │ │ - Pruebas categoriales   │
└───────────────────────────┘ └──────────────────────────┘
```

---

## 3. Comandos Esenciales de Ejecución y Test

Ejecuta siempre estos comandos para validar cambios antes de dar por buena cualquier tarea:

```bash
# 1. Verificación completa de 10 pasadas (cero fallos)
python3 verify_10_passes.py

# 2. Comprobar el Tri-Core matemático (C + Haskell + Python)
python3 CV/03_math_haskell_python/ekc_clean_math.py

# 3. Sincronizar métricas con las bases SQLite de los agentes
python3 sync_ekc_math_to_dbs.py

# 4. Estado de privacidad y publicación (lock / unlock)
python3 publish_live_control.py status

# 5. Compilación y chequeo de tipos TypeScript (si aplica en frontend)
npm run check || npm run build
```

---

## 4. Agentes EKC ("The Brothers") y Bases de Datos SQLite

Cada agente tiene su base de datos SQLite WAL persistente en la carpeta `EKC_AGENTS/`:

1. `EKC - David` (`EKC_AGENTS/david.db`): Orquestador maestro, cronología y registro histórico.
2. `EKC - Salomón` (`EKC_AGENTS/salomon.db`): Gobernanza, auditoría, Luca Pacioli 1494 balance ($0.00$ cents).
3. `EKC - Bezalel` (`EKC_AGENTS/bezalel.db`): Arquitectura de datos, CAD/CAM industrial, tolerancias $\pm 0.2\text{ mm}$.
4. `EKC - San Miguel Arcángel` (`EKC_AGENTS/san_miguel_arcangel.db`): Ciberseguridad, cortafuegos de red, firmas SHA-256.
5. `EKC - Gabriel` (`EKC_AGENTS/gabriel.db`): Mensajería inter-agente y colas asíncronas.
6. `EKC - Rafael` (`EKC_AGENTS/rafael.db`): Monitor de salud, watchdog de latencia, autorreparación.
7. `EKC - Uriel` (`EKC_AGENTS/uriel.db`): Inteligencia analítica y predicción estadística (Z-Score Robusto).
8. `EKC - Daniel` (`EKC_AGENTS/daniel.db`): Interpretación de señales de mercado y series temporales.
9. `EKC - Nehemías` (`EKC_AGENTS/nehemias.db`): Reconstrucción, backups y resiliencia ante desastres.

> **Regla Crítica**: Nunca borres, sobreescribas con esquemas vacíos ni corrompas las bases de datos de `EKC_AGENTS/`. Todas operan en modo WAL con claves foráneas activas.

---

## 5. Invariantes Matemáticos y de Negocio No Negociables

1. **Balance de Pacioli (Contabilidad Exacta)**:
   - Todo movimiento contable debe cuadrar en `0.00` céntimos exactos.
   - Usar `Decimal` en Python y tipos racionales en Haskell. Cero aritmética de coma flotante para dinero.
2. **Tolerancias Físicas CAD (EPTA France)**:
   - Toda pieza o dimensión física está acotada estrictamente en el intervalo $[d_{nom} - 0.200, d_{nom} + 0.200]\text{ mm}$.
   - Cualquier valor fuera de rango debe lanzar una excepción de control de calidad.
3. **Monoides de Welford-Chan**:
   - Agregación incremental $O(1)$ de media y varianza con asociatividad matemática:
     $$(A \oplus B) \oplus C \equiv A \oplus (B \oplus C)$$
   - Tolerancia relativa a epsilon de máquina ($2.22 \times 10^{-16}$).
4. **C11 Byte Engine**:
   - `EkcStreamRecord` debe tener exactamente 32 bytes (`__attribute__((packed))`).
   - Cero asignaciones dinámicas en el bucle caliente (`malloc`/`free` prohibidos en el streaming L1).

---

## 6. Guía de Estilo por Lenguaje

### Python
- Estricto **Clean Code**: PEP 8, nombres de variables autodocumentados, máximo 88-100 caracteres por línea.
- `from dataclasses import dataclass` con `frozen=True` para estructuras inmutables.
- Tipado estricto PEP 484 (`typing.Optional`, `typing.List`, `typing.Dict`).
- Manejo explícito de excepciones con contexto (`raise EkcDomainError(...) from err`).

### C / C++
- Estándar C11.
- Estructuras alineadas a 64 bytes (líneas de caché L1).
- Uso de `stdint.h` (`uint32_t`, `int64_t`, `double`).
- Funciones puras sin efectos secundarios en el núcleo de cálculo.

### Haskell
- GHC 9.14+.
- Tipos de datos algebraicos puros (`data`, `newtype`).
- Instancias de `Semigroup` y `Monoid` formales.

---

## 7. Política de Privacidad y Publicación

- El proyecto está protegido localmente en `127.0.0.1` (loopback privado).
- Los repositorios de GitHub están en modo **PRIVATE**.
- Los despliegues de Vercel tienen **SSO Protection** activada.
- Para inspeccionar o cambiar el estado, utiliza exclusivamente:
  ```bash
  python3 publish_live_control.py status
  python3 publish_live_control.py unlock  # Solo cuando Mikel decida publicar
  ```
