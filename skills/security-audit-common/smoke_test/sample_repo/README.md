# Sample Repo for Smoke Test

Minimal fixture project used by the smoke test. Contains intentionally bad
patterns so AegisKit's scanners have something to find:

- `app.py` — hardcoded credential + `eval()` (bandit/semgrep will flag)
- `.env.example` — env-var fixture; copy to `.env` to demo gitleaks
- `requirements.txt` — pins an old `flask==2.0.0` so pip-audit / osv-scanner
  report known CVEs

Run from this directory:

```bash
python .../audit_orchestrator.py --scenario dev --path .
```
