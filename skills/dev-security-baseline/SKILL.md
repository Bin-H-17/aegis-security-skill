---
name: dev-security-baseline
version: "1.0.0"
description: >
  开发安全基线场景子 skill（MVP 核心）。对本地项目执行密钥/API 泄露扫描（gitleaks）、
  SAST（semgrep + bandit）、依赖漏洞与 SBOM（osv-scanner / pip-audit）、License REUSE 合规（reuse），
  经 L2 报告合成器产出 P0–P3 统一报告 + 最小改动修复 + 复检命令，并执行发布前 gate。
  当用户说"安全审查 dev"、"代码安全扫描"、"密钥扫描"、"依赖漏洞"时启用。
---

# dev-security-baseline（开发安全基线，MVP 核心）

## 执行步骤

1. 获取被扫描项目绝对路径（用户入参；缺省提示提供）。
2. 调用 L2 编排器（务必用绝对路径）：

```bash
python "<SECURITY_AUDIT_HOME>/scripts/audit_orchestrator.py" --scenario dev --path "<项目绝对路径>"
```

其中 `SECURITY_AUDIT_HOME` 默认为本集合 `security-audit-common/` 目录；可通过环境变量覆盖。

3. 读取生成的 `reports/SECURITY_REPORT.md` 与 `reports/findings.dev.json`。
4. 向用户汇报：P0/P1 数量、发布前 Gate（阻断/通过）、最关键修复建议。
5. 若 P0/P1 存在：明确告知**禁止发布**，给出复检命令，待用户修复后复检。

## 覆盖范围（架构 F1–F6, F12）

- F1 密钥/API 泄露（gitleaks，P0 阻断）
- F2 SAST（semgrep JS/TS + bandit Python）
- F3 依赖漏洞 + SBOM（osv-scanner / pip-audit）
- F4 License REUSE（reuse，P1）
- F5 统一 P0–P3 报告（L2 报告合成器）
- F6 最小修复引擎（本地 Ollama，缺失时回退规则建议）
- F12 发布前 gate（P0/P1 清零）

## 降级说明

任一工具缺失 → 该扫描降级跳过（BD-01），报告标注 `missing`，不整体失败。提示用户运行 `install_tools.ps1` 补全工具链。
