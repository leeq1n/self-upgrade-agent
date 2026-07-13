# EXTENSIONS
L0: Cross-project extensions this project references, as a 1-table pointer.
Last P20-verified: 2026-07-13

| ID | Name | Status | Location |
|----|------|--------|----------|
| X1 | Knowledge Graph | idea | `../knowledge-graph-seed/` |
| X2 | (reserved) | — | — |

- Knowledge graph integration is in a separate project at
  `../knowledge-graph-seed/`.  Per P21 (cross-project independence):
  this project LINKS to it, does not duplicate.  Trigger fires
  when v3.0.2 stage gate closes (met 2026-07-11).  Spec lives
  in `../knowledge-graph-seed/SEED.md`.  First commit (minimal
  `src/kg.py` stub) made 2026-07-11 (commit `4c79bbb`).