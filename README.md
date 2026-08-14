# Aegis Security Skill

[中文](#中文) | [English](#english)

> **Offline Security Audit Skill Pack for AI Coding / 面向 AI 编码的本地离线安全审查 Skill 集合** · v1.0.0 (MIT)
> SAST + SBOM/License + AI-Content-Copyright gate, fully local, zero data egress / 全程本地运行，数据零外传。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform: Cross-platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows-blue.svg)](#)
[![Offline](https://img.shields.io/badge/Data%20Egress-None-success.svg)](#)

---

## 中文

### 简介

Aegis Security Skill 是一套**本地离线、数据不出本机**的安全审查 **Skill 集合**（面向 AI 时代 Vibe coding 场景的 AI 编码 Agent 的智能体技能体系设计，也可独立通过 CLI 脚本使用）。它通过命令行编排成熟的开源扫描器（semgrep、bandit、pip-audit、gitleaks、osv-scanner、reuse），合成统一的 **P0–P3** 报告，附带最小改动修复与发布前 gate，并提供 **AI 内容版权**检查器，按平台执行"一票否决"规则（如禁商用、禁下载）。

全部在本机运行，不上传任何数据。

### 核心能力

- **一份报告，多种扫描器**：SAST（semgrep、bandit）、依赖/SBOM 审计（pip-audit、osv-scanner）、密钥扫描（gitleaks）、许可证合规（reuse）。
- **风险分级输出**：发现统一归一到 **P0（阻断）… P3（信息）**，每条含 *最小改动修复* 与 *复检命令*。
- **发布前 Gate**：P0/P1 未清零即阻断发布。
- **AI 内容版权**：按平台编码的"通过 / 否决"标志（X1–X3），在发布前回答"我能在平台 X 上商用吗？"。
- **纯本地**：分析过程无网络调用，报告落在项目的 `reports/`。

### 四大场景

| 场景 | 主要检查 | Gate 语义 |
| --- | --- | --- |
| `dev` 开发安全基线 | SAST、硬编码密钥、依赖 CVE、许可证 | P0/P1 阻断发布 |
| `oss` 开源发布合规 | REUSE 合规、许可证头、发布就绪 | 缺头则 gate 阻断 |
| `store` 应用市场上架 | 应用商店政策清单（Play / 国内三证） | 产出上架清单 |
| `ai` AI 内容版权 | 平台级商用/衍生/下载权 | 一票否决阻断商用 |

### 架构

```text
L0  project-security-audit        （伞形入口，按意图分发）
    ├── dev-security-baseline     （场景：dev / SAST+密钥+许可证）
    ├── oss-release-compliance    （场景：oss / REUSE + 发布 gate）
    ├── app-store-compliance      （场景：store / Play + 国内三证清单）
    └── ai-content-copyright      （场景：ai / 平台级否决）
L2  security-audit-common         （公共层：scripts/ templates/ references/ baselines/）
```

L2 公共层承载全部编排逻辑：`audit_orchestrator.py` 为主链路入口；`cli_wrappers.py` 封装各工具；`report_synthesizer.py` 合成报告；`ai_copyright_checker.py` / `store_compliance.py` / `oss_compliance.py` 实现各场景；`minimal_fix_engine.py` 给出修复建议（可选本地 Ollama，缺失回退规则）；`common.py` 提供路径/配置/日志/数据模型。

### 安装

**1. 安装扫描器工具链**（semgrep、bandit、pip-audit、gitleaks、osv-scanner、reuse）到 `SECURITY_TOOLS_HOME`（默认 `~/security-tools`）：

```bash
# Linux / macOS
bash skills/security-audit-common/install/install_tools.sh

# Windows (PowerShell)
pwsh skills/security-audit-common/install/install_tools.ps1
```

自定义路径：先 `export SECURITY_TOOLS_HOME=/your/path`。

**2. 把 skills 放进你的智能体技能目录**（不同平台目录不同，如 `~/.workbuddy/skills/` 或你所用平台的对应目录）：

```bash
cp -r skills/* ~/.workbuddy/skills/   # 示例：WorkBuddy 平台
```

### 快速开始（CLI）

```bash
# 对某个项目做开发安全基线
python skills/security-audit-common/scripts/audit_orchestrator.py \
    --scenario dev --path /path/to/your/project

# AI 内容版权检查
python skills/security-audit-common/scripts/audit_orchestrator.py \
    --scenario ai --platforms OpenAI,Udio --intent commercial

# 应用商店合规清单（Google Play）
python skills/security-audit-common/scripts/audit_orchestrator.py \
    --scenario store --path /path/to/app --market googleplay

# 开源发布 gate
python skills/security-audit-common/scripts/audit_orchestrator.py \
    --scenario oss --path /path/to/project
```

报告写入 `<项目>/reports/SECURITY_REPORT.md` 及 `findings.<场景>.json`。缺失的扫描器会降级跳过（BD-01），不会整体失败。

### 目录结构

```text
aegis-security-skill/
├── LICENSE              MIT（英文，权威文本）
├── LICENSE.zh-CN        MIT 中文译本
├── README.md            本文件（中英双语）
├── NOTICE               第三方与条款声明
├── DISCLAIMER.md        保证与法律免责
├── SECURITY.md          漏洞报告
├── CONTRIBUTING.md      贡献指南
├── CHANGELOG.md         版本历史
├── .gitignore
└── skills/
    ├── project-security-audit/
    ├── dev-security-baseline/
    ├── oss-release-compliance/
    ├── app-store-compliance/
    ├── ai-content-copyright/
    └── security-audit-common/
        ├── scripts/      （8 个编排脚本，MIT）
        ├── templates/    （SECURITY_REPORT.md）
        ├── references/   （platform_terms.yaml、play_policy.yaml —— 自行提取的规则）
        ├── baselines/    （gitleaks.toml、semgrep_rules/owasp.yml）
        ├── install/      （install_tools.sh / .ps1 + requirements.txt）
        └── smoke_test/   （sample_repo 测试夹具，含 .env.example）
```

### 许可证

基于 **MIT 许可证** 发布，详见 [LICENSE](LICENSE)。中文译本见 [LICENSE.zh-CN](LICENSE.zh-CN)，如有歧义以英文为准。

### 第三方与免责

- Aegis Security Skill **仅命令行调用**开源扫描器，不复制、修改或再分发其代码（规避许可证传染的硬性规则）。
- 本仓库**不**逐字再分发任何第三方平台服务条款或官方文档，仅附带我们**自行提取**的合规启发式规则（位于 `references/*.yaml`）。详见 [NOTICE](NOTICE)。
- 本项目为安全辅助工具，**不构成**安全保证；AI 版权检查器为**决策辅助，非法律意见**。详见 [DISCLAIMER.md](DISCLAIMER.md)。
- 发现漏洞？请按 [SECURITY.md](SECURITY.md) 负责任地披露。

---

## English

### Overview

Aegis Security Skill is a collection of offline, local-first security-audit **skills** for AI-assisted coding workflows (designed for the Vibe coding era, for agent skill systems, but usable standalone via its CLI scripts). It orchestrates well-known open-source scanners (semgrep, bandit, pip-audit, gitleaks, osv-scanner, reuse) via command line, synthesizes a unified **P0–P3** report with minimal-fix suggestions and a pre-release gate, and adds an **AI-content-copyright** checker that applies per-platform one-vote-veto rules (e.g. commercial-use bans).

Everything runs on your machine. Nothing is uploaded.

### Key features

- **One report, many scanners** — SAST (semgrep, bandit), dependency/SBOM audit (pip-audit, osv-scanner), secret scanning (gitleaks), license compliance (reuse).
- **Risk-ranked output** — findings are normalized to **P0 (blocker) … P3 (info)**, each with a *minimal-change fix* and a *recheck command*.
- **Pre-release gate** — P0/P1 must be cleared before publishing.
- **AI content copyright** — per-platform rules encoded as pass / veto flags (X1–X3), so you learn "can I monetize this on platform X?" before you ship.
- **Local-only** — no network calls for analysis; scanners are invoked locally; reports stay in your project's `reports/`.

### Scenarios

| Scenario | Key checks | Gate semantics |
| --- | --- | --- |
| `dev` (dev security baseline) | SAST, hardcoded secrets, dependency CVEs, license | P0/P1 block release |
| `oss` (OSS release compliance) | REUSE compliance, license headers, publish readiness | gate blocked if headers missing |
| `store` (app-store listing) | app-store policy checklist (Play / CN 三证) | produces submission checklist |
| `ai` (AI content copyright) | per-platform commercial/derivative/download rights | one-veto blocks monetization |

### Architecture

```text
L0  project-security-audit        (umbrella entry — routes by intent)
    ├── dev-security-baseline     (scenario: dev / SAST+secrets+license)
    ├── oss-release-compliance    (scenario: oss / REUSE + publish gate)
    ├── app-store-compliance      (scenario: store / Play + CN 三证 checklist)
    └── ai-content-copyright      (scenario: ai / per-platform veto)
L2  security-audit-common         (shared: scripts/, templates/, references/, baselines/)
```

The L2 layer (`security-audit-common`) holds all orchestration logic: `audit_orchestrator.py` is the main entry; `cli_wrappers.py` wraps each tool; `report_synthesizer.py` builds the report; `ai_copyright_checker.py`, `store_compliance.py`, `oss_compliance.py` implement scenario logic; `minimal_fix_engine.py` suggests fixes (optional local Ollama, falls back to rules); `common.py` provides paths/config/logging/data models.

### Install

**1. Install the scanner toolchain** (semgrep, bandit, pip-audit, gitleaks, osv-scanner, reuse) into `SECURITY_TOOLS_HOME` (default `~/security-tools`):

```bash
# Linux / macOS
bash skills/security-audit-common/install/install_tools.sh

# Windows (PowerShell)
pwsh skills/security-audit-common/install/install_tools.ps1
```

To use a custom location: `export SECURITY_TOOLS_HOME=/your/path` first.

**2. Place the skills** into your agent's skills directory (the path differs per platform, e.g. `~/.workbuddy/skills/` or your platform's equivalent):

```bash
cp -r skills/* ~/.workbuddy/skills/   # example: WorkBuddy
```

### Quick start (CLI)

```bash
# Dev security baseline on a project
python skills/security-audit-common/scripts/audit_orchestrator.py \
    --scenario dev --path /path/to/your/project

# AI content copyright check
python skills/security-audit-common/scripts/audit_orchestrator.py \
    --scenario ai --platforms OpenAI,Udio --intent commercial

# App-store compliance checklist (Google Play)
python skills/security-audit-common/scripts/audit_orchestrator.py \
    --scenario store --path /path/to/app --market googleplay

# OSS release gate
python skills/security-audit-common/scripts/audit_orchestrator.py \
    --scenario oss --path /path/to/project
```

Reports are written to `<project>/reports/SECURITY_REPORT.md` plus a `findings.<scenario>.json`. Missing scanners degrade gracefully (BD-01) instead of failing the whole run.

### Project layout

```text
aegis-security-skill/
├── LICENSE              MIT (English, authoritative)
├── LICENSE.zh-CN        MIT 中文译本
├── README.md            this file (bilingual)
├── NOTICE               third-party & terms acknowledgments
├── DISCLAIMER.md        warranty & legal disclaimer
├── SECURITY.md          vulnerability reporting
├── CONTRIBUTING.md      contribution guide
├── CHANGELOG.md         version history
├── .gitignore
└── skills/
    ├── project-security-audit/
    ├── dev-security-baseline/
    ├── oss-release-compliance/
    ├── app-store-compliance/
    ├── ai-content-copyright/
    └── security-audit-common/
        ├── scripts/      (8 orchestration scripts, MIT)
        ├── templates/    (SECURITY_REPORT.md)
        ├── references/   (platform_terms.yaml, play_policy.yaml — OUR extracted rules)
        ├── baselines/    (gitleaks.toml, semgrep_rules/owasp.yml)
        ├── install/      (install_tools.sh / .ps1 + requirements.txt)
        └── smoke_test/   (sample_repo fixture, incl. .env.example)
```

### License

Released under the **MIT License** — see [LICENSE](LICENSE). A Chinese translation is provided in [LICENSE.zh-CN](LICENSE.zh-CN) for convenience; the English text governs.

### Third-party & disclaimer

- Aegis Security Skill **invokes** open-source scanners via CLI; it does **not** copy, modify, or redistribute their code (hard rule against license contamination).
- This repo does **not** redistribute third-party platform Terms of Service or official docs verbatim. It ships only **our own extracted** compliance heuristics in `references/*.yaml`. See [NOTICE](NOTICE).
- This is a security-assistance toolkit, **not** a guarantee of security, and the AI-copyright checker is a **decision aid, not legal advice**. See [DISCLAIMER.md](DISCLAIMER.md).
- Found a vulnerability? See [SECURITY.md](SECURITY.md) for responsible disclosure.
