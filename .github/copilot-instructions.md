# GitHub Copilot Instructions — Mikel Irastorza · EKC Ecosystem

When generating or refactoring code in this repository:

1. **Python Standards (Clean Code)**:
   - Always follow strict PEP 8 conventions.
   - Use `dataclasses` with `frozen=True` for domain entities.
   - Use `Decimal` from the `decimal` module for all financial values and accounting ledgers. Never use binary floats (`float`) for currency.
   - Enforce explicit type annotations (`typing`) on all function signatures.

2. **C11 Byte Engine**:
   - `EkcStreamRecord` must strictly be 32 bytes packed (`__attribute__((packed))`).
   - Align memory for 64-byte L1 CPU cache lines (2 records per cache line).
   - Zero dynamic allocations (`malloc`/`free`) in the streaming hot loop.
   - Respect CAD tolerances of $\pm 0.2\text{ mm}$.

3. **Haskell Formal Proofs**:
   - Use GHC 9.14+ idiomatic pure functional code.
   - Ensure algebraic monoid laws hold for streaming statistics.
   - Maintain exact double-entry ledger balance with rational arithmetic ($0.00$ cents difference).

4. **Multi-Agent SQLite Architecture**:
   - The 9 EKC agents store their states in `EKC_AGENTS/*.db` with WAL mode enabled.
   - Never generate code that drops tables, overwrites databases, or corrupts audit trails.

5. **Design System & Aesthetics**:
   - Brand colors: Obsidian `#05070c`, brushed gold `#f59e0b` and `#fbbf24`, emerald `#10b981`.
   - Professional, engineering-focused tone. No generic AI filler.
