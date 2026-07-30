# SUA v2.3.0 Release Notes

> **Release date**: 2026-07-30
> **Version policy**: SemVer 2.0 (PATCH from v2.2.0; v3.0.0 reserved for breaking changes)
> **Status**: Re-open-source release — first public SUA release with full open-source compliance

## What's new since v2.2.0

### Open-source compliance
- **LICENSE** (MIT) — first time added (1061 B)
- **CONTRIBUTING.md** — contribution workflow + commit-msg P-n cite convention (3419 B)
- **CODE_OF_CONDUCT.md** — Contributor Covenant v2.1 industry standard (5485 B)

### Cross-runtime support
- **docs/CROSS_RUNTIME_SKILL_BRIDGE.md** — Agent Skills open standard bridge
  (works in Hermes / Codex / Claude Code / Cursor / Antigravity / GitHub Copilot per
  the public Agent Skills standard 2025-12-18)
- **README badges** — MIT / PRs Welcome / AAIF / Agent Skills compatibility

### Documentation
- **README sections** — Changelog / Code of conduct / License pointers
- **6-step onboarding** preserved as canonical (vs old "Read ./sua/AGENTS.md...")

### Cleanup
- **chromedriver-win64.zip removed** (18.1 MB legacy artifact, no SUA relevance)
- **force-pushed** clean-sua local history (532 commits now visible, was 1 reset commit)

## Migration from v2.2.0

If you are upgrading from v2.x:
- Hook install path **unchanged** (`cp hooks/* .git/hooks/`)
- AGENTS.md / AGENTS_DETAIL.md / CHANGELOG.md / hooks/ **unchanged**
- Quick start is now 6-step onboarding (was "Read ./sua/AGENTS.md...")
- For non-canonical runtimes, see [docs/CROSS_RUNTIME_SKILL_BRIDGE.md]

## Breaking changes

**None.** v2.3.0 is fully backward-compatible with v2.x hooks and docs.

## Note on pre-existing v2.x tags

The following tags were created during dev iteration on the previous main
branch (now orphaned by the v2.3.0 force-push):

- `v2.0.0-critical-thinking-injection`
- `v2.1.0-lifecycle-scripts`
- `v2.2.0-session-final-2026-07-16`

These tags remain in git history (per P-17 老实说 / git history preservation)
but **do not point to any commit reachable from main**. They document
pre-re-open-source development history and are not part of the v2.3.0
release lineage.

## License

This project is licensed under the MIT License (c) 2026 LiQin.
See [LICENSE](LICENSE).
