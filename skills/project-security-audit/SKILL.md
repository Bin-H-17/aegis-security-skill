---
name: project-security-audit
version: "1.0.0"
description: >
  本地离线「安全审查 Skill 集合」L0 伞形入口。统一触发入口：识别用户场景（开发安全基线 /
  开源发布合规 / 应用商店上架 / AI 内容版权），调度对应场景子 skill，并串起 L2 公共层
  （编排脚本 / 报告合成 / 最小修复 / 条款库 / 基线）。本地离线、0 数据出境、命令行调用不改上游。
  当用户说"安全审查"、"安全审计"、"代码安全"、"开源合规"、"上架体检"、"AI 版权"时启用本 skill。
---

# project-security-audit（L0 入口）

你是本地离线安全审查体系的统一入口。收到请求后：

## 1. 场景识别（L0 分发）

| 用户意图关键词 | 调度子 skill | 编排命令场景 |
| --- | --- | --- |
| 开发安全 / 密钥 / SAST / 依赖漏洞 / license / 代码安全 | `dev-security-baseline` | `dev` |
| 开源发布 / OSS / REUSE / 发布前 gate | `oss-release-compliance` | `oss` |
| 上架 / 应用商店 / Play / 国内三证 / ICP / 软著 | `app-store-compliance` | `store` |
| AI 版权 / 平台条款 / 商用权 / 下载权 / Udio / OpenAI | `ai-content-copyright` | `ai` |

识别后**加载对应子 skill** 并按其指令执行；子 skill 统一调用 L2 脚本 `security-audit-common/scripts/audit_orchestrator.py`。

## 2. 公共约定（所有场景必须遵守）

- **本地离线**：工具目录由 `SECURITY_TOOLS_HOME` 指定（默认 `~/security-tools`），报告落项目 `reports/`，0 数据出境。
- **命令行调用不改上游**：编排 gitleaks/semgrep/bandit/osv-scanner/pip-audit/reuse，**严禁复制 AGPL/LGPL 上游代码**（尤其 DeepAudit）。
- **报告规范**：P0–P3 分级 + 最小改动修复 + 复检命令，产出 `SECURITY_REPORT.md`。
- **发布前 Gate**：P0/P1 未清零即阻断发布。

## 3. 工具链就绪检查

执行前先确认工具存在；缺失则提示运行 `security-audit-common/install/install_tools.ps1`（或 .sh）。

详见各子 skill 与 `security-audit-common/SKILL.md`。
