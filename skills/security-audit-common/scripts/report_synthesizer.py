#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT
"""
report_synthesizer.py — 统一 P0-P3 报告合成器

输入 Report（含 findings），输出：
- SECURITY_REPORT.md（交付物，P0-P3 分级 + 最小改动修复 + 复检命令）
- findings.<scenario>.json（机器可读中间产物）

报告风格（架构锁定）：P0-P3 分级 + 最小改动修复建议 + 复检命令。
"""
from __future__ import annotations

import os
from typing import List

from common import Report, Finding, write_json, SECURITY_TOOLS_HOME

SEV_LABEL = {
    "P0": "P0 阻断（发布前必须清零）",
    "P1": "P1 高危（发布前建议清零）",
    "P2": "P2 中危（迭代修复）",
    "P3": "P3 低危/信息（记录跟踪）",
}


def _render_finding(f: Finding) -> str:
    loc = f"{f.file}" + (f":{f.line}" if f.line else "")
    block = [
        f"#### [{f.severity}] {f.title}",
        f"- 来源：{f.source} ｜ 规则：{f.rule_id}",
        f"- 位置：{loc}",
        f"- 说明：{f.description}",
    ]
    if f.recommendation:
        block.append(f"- 最小改动修复：{f.recommendation}")
    if f.recheck:
        block.append(f"- 复检命令：\n  ```\n  {f.recheck}\n  ```")
    return "\n".join(block)


def synthesize(report: Report, out_dir: str) -> str:
    """写出 SECURITY_REPORT.md 与 findings JSON，返回报告路径。"""
    os.makedirs(out_dir, exist_ok=True)
    counts = {s: len(report.by_severity(s)) for s in ("P0", "P1", "P2", "P3")}
    report.gate_blocked = counts["P0"] > 0 or counts["P1"] > 0
    report.gate_reasons = []
    if counts["P0"] > 0:
        report.gate_reasons.append(f"存在 {counts['P0']} 个 P0 阻断项，禁止发布")
    if counts["P1"] > 0:
        report.gate_reasons.append(f"存在 {counts['P1']} 个 P1 高危项，建议发布前清零")

    lines: List[str] = []
    lines.append(f"# 安全审查报告 SECURITY_REPORT")
    lines.append("")
    lines.append(f"- 审计 ID：{report.audit_id}")
    lines.append(f"- 场景：{report.scenario}")
    lines.append(f"- 项目：{report.project_path}")
    lines.append(f"- 生成时间：{report.generated_at}")
    lines.append(f"- 工具目录：{SECURITY_TOOLS_HOME}")
    lines.append("")
    lines.append("## 1. 总览")
    lines.append("")
    lines.append(f"| 级别 | 数量 |")
    lines.append(f"| --- | --- |")
    for s in ("P0", "P1", "P2", "P3"):
        lines.append(f"| {SEV_LABEL[s]} | {counts[s]} |")
    lines.append("")
    gate = "🔴 阻断（P0/P1 未清零）" if report.gate_blocked else "🟢 通过（可发布）"
    lines.append(f"**发布前 Gate：{gate}**")
    if report.gate_reasons:
        for r in report.gate_reasons:
            lines.append(f"- {r}")
    lines.append("")
    lines.append("## 2. 工具状态")
    lines.append("")
    lines.append("| 工具 | 状态 |")
    lines.append("| --- | --- |")
    for t, st in report.tool_status.items():
        lines.append(f"| {t} | {st} |")
    lines.append("")
    lines.append("## 3. 发现明细")
    lines.append("")
    for s in ("P0", "P1", "P2", "P3"):
        items = report.by_severity(s)
        if not items:
            continue
        lines.append(f"### {SEV_LABEL[s]}（{len(items)}）")
        lines.append("")
        for f in items:
            lines.append(_render_finding(f))
            lines.append("")
    lines.append("## 4. 复检总命令")
    lines.append("")
    lines.append("```")
    lines.append(f"python {os.path.join(os.path.dirname(__file__), 'audit_orchestrator.py')} "
                 f"--scenario {report.scenario} --path \"{report.project_path}\"")
    lines.append("```")
    lines.append("")
    lines.append("> 本报告由 L2 报告合成器本地生成，0 数据出境。")
    md = "\n".join(lines)
    md_path = os.path.join(out_dir, "SECURITY_REPORT.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md)

    json_path = os.path.join(out_dir, f"findings.{report.scenario}.json")
    write_json(json_path, report.to_dict())
    return md_path
