---
name: ai-content-copyright
version: "1.0.0"
description: >
  AI 内容版权场景子 skill（完整版 F10，近期主攻）。读取 references/platform_terms.yaml 平台条款快照，
  按用户意图（商用 / 下载 / 两者）对指定平台做逐平台一票否决裁决，任一平台禁止即整体阻断。
  落实 X1–X3（OpenAI 可商用 vs Udio 禁商用 / 禁下载）。当用户说"AI 版权"、"平台条款"、"商用权"、
  "Udio / OpenAI / Midjourney / Suno 版权"时启用。
---

# ai-content-copyright（AI 内容版权，完整版 F10，X1–X3 一票否决）

## 执行步骤

1. 获取平台列表（逗号分隔，如 `OpenAI,Udio`）与意图（默认 commercial；可选 download / both）。
2. 调用 L2 编排器：

```bash
python "<SECURITY_AUDIT_HOME>/scripts/audit_orchestrator.py" --scenario ai --platforms "OpenAI,Udio" --intent commercial
```

3. 读取裁决结果（stdout + `reports/` 可选留存）。
4. 向用户汇报：逐平台 verdict（PASS / VETO / MANUAL）、整体 Gate（阻断/通过）。

## 裁决逻辑（X1–X3）

- 逐平台核对 `commercial_use` 与 `download_right`，**不默认合规**。
- 任一平台禁止商用或下载 → 整体 **VETO 阻断**。
- 条款库未收录（如 X7 通义 / 混元）→ `MANUAL` 转人工，同样阻断直至人工确认。

## 范围

- 已确认：OpenAI / Udio / Midjourney / Suno
- 待核（pending）：Kling / Jimeng / Flux-dev（X5 非商用许可）
- 缺失（missing，转人工）：Tongyi / Hunyuan（X7）
- 条款库按 U-05 / U-06 季度重抓更新。
