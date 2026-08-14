# Changelog

All notable changes to AegisKit are listed here. Format is loosely Keep a
Changelog. Versions follow the skills' internal version field.

## [1.0.0] — 2026-08-14

### Added
- L0 umbrella skill `project-security-audit` + 4 scenario skills
  (dev-security-baseline, oss-release-compliance, app-store-compliance,
  ai-content-copyright) and shared L2 layer `security-audit-common`.
- 8 orchestration scripts: common, cli_wrappers, report_synthesizer,
  minimal_fix_engine, ai_copyright_checker, store_compliance, oss_compliance,
  audit_orchestrator.
- P0–P3 unified report with minimal-fix suggestions and pre-release gate.
- AI-content-copyright per-platform one-vote-veto (X1–X3).
- Cross-platform install scripts + pinned `requirements.txt`.
- Bilingual (EN/中) README, LICENSE, NOTICE, DISCLAIMER, SECURITY, CONTRIBUTING.

### Notes
- MVP scope: dev baseline end-to-end; oss/store/ai scenarios provide structured
  checklists + gates with manual-confirmation items.
- Runs fully offline; invokes (does not bundle) semgrep/bandit/gitleaks/
  osv-scanner/pip-audit/reuse.
