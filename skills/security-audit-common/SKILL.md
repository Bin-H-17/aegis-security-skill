---
name: security-audit-common
version: "1.0.0"
description: >
  本地离线安全审查 Skill 集合 L2 公共层（共享依赖，不直接由用户触发）。承载：编排脚本
  （audit_orchestrator / cli_wrappers / report_synthesizer / minimal_fix_engine /
  ai_copyright_checker / store_compliance / oss_compliance）、报告模板、条款库 references/、
  基线 baselines/。被 L0 与各场景子 skill 调用。命令行调用不改上游、本地离线、0 数据出境。
---

# security-audit-common（L2 公共层）

本 skill 为共享能力层，不单独对用户暴露；被 `project-security-audit` 与四个场景子 skill 依赖。

## 目录结构

```
security-audit-common/
├── SKILL.md
├── scripts/
│   ├── common.py            # 路径/配置/日志/数据模型/CLI 封装
│   ├── cli_wrappers.py      # gitleaks/semgrep/bandit/osv-scanner/pip-audit/reuse 封装与解析
│   ├── report_synthesizer.py# P0–P3 统一报告合成（SECURITY_REPORT.md + findings json）
│   ├── minimal_fix_engine.py# 最小改动修复（本地 Ollama，缺失回退规则）
│   ├── ai_copyright_checker.py # X1–X3 逐平台一票否决
│   ├── store_compliance.py  # 上架清单（play_policy.yaml）
│   ├── oss_compliance.py    # 开源发布 gate
│   └── audit_orchestrator.py# L0 主链路编排入口
├── templates/
│   └── SECURITY_REPORT.md   # 报告规范模板
├── references/
│   ├── platform_terms.yaml  # D6 平台条款快照（X1–X3 等）
│   └── play_policy.yaml     # D5 上架政策快照
└── baselines/
    ├── gitleaks.toml        # gitleaks 基线（extend default + 允许列表）
    └── semgrep_rules/owasp.yml # semgrep OWASP 规则包
```

## 环境与路径（可覆盖）

| 环境变量 | 默认 | 说明 |
| --- | --- | --- |
| `SECURITY_AUDIT_HOME` | 本目录（security-audit-common） | 脚本/references/baselines/templates 根 |
| `SECURITY_TOOLS_HOME` | `~/security-tools` | 6 个 CLI 安装目录（可用环境变量覆盖） |
| `SECURITY_AUDIT_CWD` | 无 | 子进程工作目录（可选） |
| `OLLAMA_HOST` | `http://localhost:11434` | 本地 Ollama 推理地址 |
| `OLLAMA_MODEL` | `qwen2.5-coder:7b` | 最小修复引擎模型 |

## 许可合规底线（铁律）

- 仅**命令行调用**开源工具，**不改上游**；借鉴 DeepAudit 工作流但**严禁复制其 AGPL-3.0 代码**。
- 所有产物本地落盘，0 数据出境。
- 工具缺失 → 单工具降级（BD-01），不整体失败。

## 安装

见 `install/install_tools.ps1`（Windows）与 `install/install_tools.sh`（跨平台），将 6 个 CLI 装入 `SECURITY_TOOLS_HOME`。
