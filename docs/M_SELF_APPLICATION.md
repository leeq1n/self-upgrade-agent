# M-self-application (full text)
Last P20-verified: 2026-07-13

> L0: Self-application rule — apply rules at 4 levels.
> Load when: encountering any new rule/pattern, when designing
> rules, or when debugging "rule didn't apply" failures.
> Per 3-condition gate (M_RULE_AUTHORING.md): reusable across
> projects ✓, triggerable (on any new rule) ✓, 3+ occurrences
> observed ✓ → promoted to full M-rule (per 2026-07-13 session).

## The class of failure mode

Agent **knows** a rule, applies to **objects** (tasks,
project, docs), but **does not** apply to **itself** (its
own operating, its own memory, its own structure).  Agent
is good at **comprehension** ("I understand this rule") but
weak at **self-application** ("does this rule apply to me?").

## The 4 levels (always-ask when encountering a rule)

When you encounter a rule or pattern, apply it at 4 levels:

1. **To current task** (object level — usually already do).
2. **To the rule itself** (meta level — "does this rule
   govern how rules are written?  Does it apply to itself?").
3. **To memory / project structure** (organizational level
   — "does this rule apply to how I store / organize things?").
4. **To your own operating behavior** (self level — "does
   this rule apply to how I behave, not just to objects?").

If you find a class of cases where the rule applies but
you didn't apply it, that's a "self-application gap" —
surface it explicitly and fix.

## Concrete examples (this project's own gaps caught)

- **Recursive decomp** (5-step loop) — applied to tasks ✓
  but **not** applied to "how I organize my memory of
  recursive decomp" ✗
- **M-rules** (M-task-summary etc.) — applied to project ✓
  but **not** applied to "how I behave outside the project" ✗
- **Audit (M-self-audit)** — applied to docs ✓ but **not**
  applied to "audit my own audit" ✗
- **P11 (摘要+引用)** — applied to docs ✓ but **not**
  applied to "how I describe myself to the user" ✗

## Bootstrap exception

M-self-application itself is the **first** rule applied
when encountering any rule.  It does **not** apply to
itself (would be infinite recursion) — just apply it to
every **other** rule, not to M-self-application itself.

## Caveat (per honest reporting / P17)

Adding this rule is **necessary but not sufficient**.
LLM training data may not have enough self-referential
examples for robust self-application.  Realistic reduction:
**60-70% of gaps**, not 100% elimination.  For higher
coverage, see "See also" (outer-loop wrapper, multi-shot
examples, fine-tuning on self-referential data).

## Anti-patterns (what NOT to do)

- **Don't** apply rules only to objects (per M-self-
  application — apply to rule itself, to memory, to
  your own behavior).
- **Don't** claim 100% coverage (60-70% is realistic,
  per honest reporting).
- **Don't** apply M-self-application to itself (infinite
  recursion, per bootstrap exception).

## Relationship to other M-* rules

- **M-self-audit**: M-self-audit catches discoverability
  gaps.  M-self-application catches "rule not applied at
  4 levels" gaps.  Different gap types, complementary.
- **M-task-summary**: M-self-application is **applied
  during** M-task-summary (4 levels of the task that
  just completed).  M-task-summary reports M-self-
  application findings.
- **M-learn**: M-self-application is itself a class of
  learning (归纳 + 类比 + 外推).  M-learn operationalizes
  M-self-application at integration points.
- **M-add-then-reduce**: M-self-application is a **signal
  trigger** for reduce phase (rule that didn't apply at
  4 levels = surface in reduce).

## See also

- `docs/OPERATING_RULES.md` — M-self-application brief pointer.
- `docs/RECURSIVE_QUALITY.md` — "loop = decomposition +
  analogy + self-reference"; M-self-application is the
  "self-reference" arm.
- `docs/COMMON_PITFALLS.md` — fresh-agent miss categories
  (one of which is exactly the self-application gap).
- agent-onboarding skill, `references/M_RULE_AUTHORING.md`
  (skill) — M-rule authorship can apply M-self-application
  to itself (the recipe is reusable across projects).
- PRINCIPLES.md P11 (摘要+引用) — the principle that
  M-self-application level 3 (memory/structure) is about.
- PRINCIPLES.md P14 (docs stay current) — the principle
  that M-self-application level 4 (self behavior) is about.