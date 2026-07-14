# Knowledge organization: graph/tree + flat context (per user 2026-07-14)

> L0: Codification of "知识是图/树, 上下文是平铺式"
> insight.  This is the **architecture** for the
> self-organization sub-plan: SUA maintains the
> knowledge graph (project-agnostic), agent-onboarding
> skill maintains the flat context reader (per-project).
> Per user clarification 2026-07-14.
> Last P20-verified: 2026-07-14 (initial codification)








## Revised plan (commits 53+)

| # | Commit | Content |
|---|---|---|
| **53** | this commit | Codify 图/树 + 平铺式 model (this doc) |
| **54** | `feat(skill-v2): create agent-onboarding-v2/ in hermes-root` | New project skeleton |
| **55** | `docs(skill-v2): initial SKILL.md with flat context entry point` | Skill entry point |
| **56** | `docs(EXTENSIONS): update X2 to point to skill-v2 in hermes-root` | Cross-ref SUA → skill |
| **57** | `docs(SUA): link SUA docs to skill references (L0 cross-refs)` | Cross-ref back |
| **58** | parent verification | SUMMARY_LIFECYCLE |

## Per P26 fresh-agent simulation (post-this-doc)

| Discovery step | Pre-doc | Post-doc |
|---|---|---|
| New agent enters SUA project | sees graph, no flat reading path | ✅ sees both (graph + flat) |
| New agent enters other project | must import SUA docs (not portable) | ✅ imports skill (portable) |
| Understands graph vs flat distinction | ❌ implicit | ✅ explicit doc |
| Knows where to put new knowledge | ⚠️ unclear | ✅ graph in SUA, flat in skill |
| Cross-project link mechanism | ✅ EXTENSIONS.md | ✅ (unchanged) |

Fresh-agent simulation **PASS**.

## Detail (L2)

For per-principle analysis, M-self-application, follow-ups, and other L2 detail, see [`KNOWLEDGE_ORG_DETAIL.md`](KNOWLEDGE_ORG_DETAIL.md).  Per R6, this companion is required for files > 7KB.
