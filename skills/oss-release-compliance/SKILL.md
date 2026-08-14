---
name: oss-release-compliance
version: "1.0.0"
description: >
  开源发布合规场景子 skill（完整版）。对本地仓库执行密钥三层扫描 + REUSE 许可证合规 +
  社区健康/Scorecard 检查，产出 ReleaseGate（blocked_reasons）。MVP 阶段为「提示 + 人工」，
  完整版做结构化 gate。当用户说"开源合规"、"OSS 发布检查"、"REUSE"、"发布前 gate"时启用。
---

# oss-release-compliance（开源发布合规，完整版 F7/F8）

## 执行步骤

1. 获取仓库绝对路径。
2. 调用 L2 编排器：

```bash
python "<SECURITY_AUDIT_HOME>/scripts/audit_orchestrator.py" --scenario oss --path "<仓库绝对路径>"
```

3. 读取 `reports/SECURITY_REPORT.md` 与 `reports/findings.oss.json`。
4. 向用户汇报 ReleaseGate：是否阻断、blocked_reasons（密钥泄露 / REUSE 缺口等）。
5. 若 `blocked=true`：明确**禁止开源发布**，给出修复项与复检命令。

## 覆盖范围

- 密钥三层扫描（gitleaks，含 git 历史 baseline）
- REUSE 合规（reuse lint，L1 文件存在 → L2 逐文件 SPDX）
- 发布前深度检查（F8）：依赖更新 / 抄袭检测提示（完整版自动化，MVP 仅提示）

## 注意

自动化仅为辅助；涉及许可证兼容性、贡献者协议（DCO/CLA）等法律判定，转人工确认。
