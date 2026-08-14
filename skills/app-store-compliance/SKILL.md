---
name: app-store-compliance
version: "1.0.0"
description: >
  应用商店上架合规场景子 skill（完整版 F9）。读取 references/play_policy.yaml 政策快照，
  生成逐项 StoreChecklist；对权限 / target API 等可自动核对项给状态，对国内三证 / ICP / 软著 /
  版号等法律要件标记 MANUAL 转人工。当用户说"上架体检"、"应用商店合规"、"Play 政策"、"国内三证"时启用。
---

# app-store-compliance（应用商店上架合规，完整版 F9）

## 执行步骤

1. 获取项目绝对路径与目标市场（默认 googleplay；可选 appstore_cn）。
2. 调用 L2 编排器：

```bash
python "<SECURITY_AUDIT_HOME>/scripts/audit_orchestrator.py" --scenario store --path "<项目绝对路径>" --market googleplay
```

3. 读取 `reports/store_checklist.<market>.json`。
4. 向用户汇报：自动可核项、需人工项（国内三证 / ICP / 软著 / 版号等），并强调法律要件必须人工确认。

## 覆盖范围

- Google Play：数据安全表单 / 权限最小化 / target API 级别（X6 待精读）/ 隐私政策
- 国内应用商店：国内三证 / 版号年龄分级 / 数据出境评估

## 铁律

自动化核对仅为辅助，**绝不默认通过**。国内三证等合规要件必须人工确认后方可上架。
