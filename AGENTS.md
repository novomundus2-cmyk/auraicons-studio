# AGENTS.md — Universal Agent Instructions for EKC (ElektriKubercisC)

This document provides explicit guidelines for autonomous coding agents (Codex, Windsurf, Aider, OpenCode, Claude Code, Gemini CLI, Cursor, etc.) working on this repository.

---

## 1. Project Context & Purpose

- **Owner**: Mikel Irastorza · Lead Systems Architect & Big Data Engineer.
- **Repository**: EKC (ElektriKubercisC) Distributed Agent System & Architecture Core.
- **Components**:
  - `CV/`: Architecture whitepapers, interactive dashboards, and production modules.
  - `CV/03_math_haskell_python/`: Mathematical Tri-Core (C11, Haskell GHC, Python Clean Code).
  - `EKC_AGENTS/`: 9 persistent SQLite WAL databases for each distributed agent.
  - `verify_10_passes.py`: Automated 10-pass end-to-end verification suite.
  - `publish_live_control.py`: Air-gap and privacy control switch.

---

## 2. Inviolable Engineering Contracts

| Domain | Invariant | Enforcement Mechanism |
|---|---|---|
| **Accounting** | Balance Difference = 0.00 exact cents | Luca Pacioli double-entry ledger with Python `Decimal` and Haskell `Rational`. Zero floating point drift. |
| **Mechanical CAD** | Tolerance $[-0.200, +0.200]\text{ mm}$ | Strict boundary assertions inherited from EPTA France sheet-metal robotics. |
| **Statistical Streaming** | Welford-Chan Algebraic Monoid | Pure associativity within machine epsilon ($2.22 \times 10^{-16}$) in Haskell & C SIMD. |
| **Memory Footprint** | 32-byte packed records | Two records per 64-byte L1 CPU cache line in C11 (`__attribute__((packed))`). |
| **Agent Persistence** | Zero data loss in `EKC_AGENTS/` | SQLite WAL mode with SHA-256 audit chaining. |

---

## 3. Standard Verification Commands

Any agent making changes to this repository **MUST** run and pass the following tests:

```bash
# 1. Run 10-Pass End-to-End Verification Suite
python3 verify_10_passes.py

# 2. Verify Tri-Core Math Execution (C + Haskell + Python)
python3 CV/03_math_haskell_python/ekc_clean_math.py

# 3. Synchronize records with agent databases
python3 sync_ekc_math_to_dbs.py

# 4. Verify Privacy Lock Status
python3 publish_live_control.py status
```

---

## 4. Coding Conventions

- **Python**: Strict Clean Code, PEP 8, frozen dataclasses, type hints, explicit error handling.
- **C/C++**: C11 standard, packed structs, no heap allocations in hot loops.
- **Haskell**: GHC 9.14+, pure category-theoretic formulations (Monoids, Semigroups).
- **Design**: Obsidian background `#05070c`, brushed gold `#f59e0b`/`#fbbf24`, zero generic templates.
