# M-terminology-clarity — Detail (L2)

> L0: L2 detail for `M_TERMINOLOGY_CLARITY.md`.  Per
> P11 摘要+引用, the summary file is the L0/L1 layer
> (≤ 7KB); this file is the L2 layer (worked examples
> + term selection criteria table).  Per R6, this
> companion is referenced from the summary.

---

## Worked examples

### Example 1: "撞到一起" → "replan" (current case)

- **Detect**: 5+ occurrences, metaphor without
  source domain, multiple plausible meanings (a)
  plan conflict, (b) task conflict, (c) context
  confusion)
- **Acknowledge**: "I used '撞到一起' 5+ times; it's
  unclear.  Let me clarify: it means 'multiple
  context / task / rule need to be replanned'."
- **Refine**: "撞到一起" → "**replan**" (P7 奥卡姆
  + P11 摘要+引用)
- **Verify**: re-read SUA + skill + skill-incubator
  docs; ensure no "撞到一起" remains (or only
  references to its refinement)

### Example 2: Hypothetical "vision" (potential future case)

- **Detect**: "vision" used 5+ times in SUA
  PROJECT_STATE.md, but "vision" has multiple
  meanings: (a) future goal, (b) current state
  intent, (c) project's north star.
- **Acknowledge**: "I used 'vision' 5+ times; it's
  overloaded."
- **Refine**: pick 1 — "goal" (clearer for future
  intent).  Or split into "**goal**" (future intent)
  + "**state intent**" (current direction).
- **Verify**: re-read SUA; replace "vision" with
  "goal" or split.

### Example 3: Hypothetical "agent behavior rules" (potential future case)

- **Detect**: "agent behavior rules" used 10+ times
  in SUA + skill, but "rules" can mean (a) P-n, (b)
  M-n, (c) R-n, (d) implicit conventions.
- **Acknowledge**: "I used 'agent behavior rules'
  loosely; clarify."
- **Refine**: split into "**principles (P-n)**",
  "**workflows (M-n)**", "**invariants (R-n)**",
  "**conventions**" (or "implicit rules").
- **Verify**: re-read; use precise terms.


## Term selection criteria (P11 摘要+引用 + P7 奥卡姆)

When choosing a refined term, apply:

| Criterion | Why |
|---|---|
| Shorter | P7 奥卡姆 |
| No jargon | P11 摘要+引用 |
| Self-describing | reduces new-agent cognitive load (P26) |
| Consistent with existing terminology | P14 + P22 |
| Native (English or 中文, not mixed unless necessary) | user message "中文回答，不要中英文混杂" |
| No metaphor (or metaphor with clear source domain) | M-n 12 application |
| Verifiable (can be checked in code/docs) | P17 honest |
