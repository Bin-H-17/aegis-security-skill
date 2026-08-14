#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT
"""
oss_compliance.py — 开源发布合规 gate（F7/F8，完整版）

聚合：reuse lint + gitleaks + 可选 scorecard-lite，产出 ReleaseGate。
MVP 阶段本场景为「提示 + 人工」，完整版做结构化 gate。
"""
from __future__ import annotations

import os
from typing import List, Dict, Any

from common import Finding, ToolRunner


def release_gate(runner: ToolRunner, project_path: str,
                 findings: List[Finding]) -> Dict[str, Any]:
    """基于已扫描 findings 与 reuse 状态产出发布 gate。"""
    blocked_reasons: List[str] = []
    p0 = [f for f in findings if f.severity == "P0"]
    p1 = [f for f in findings if f.severity == "P1"]
    if p0:
        blocked_reasons.append(f"存在 {len(p0)} 个 P0（含密钥泄露），禁止开源发布")
    reuse_issues = [f for f in findings if f.source == "reuse"]
    if reuse_issues:
        blocked_reasons.append(f"REUSE 合规缺口 {len(reuse_issues)} 处，需补齐许可证/版权声明")
    # 发布前深度检查（F8）提示项（完整版自动化，此处仅标记）
    return {
        "project_path": project_path,
        "blocked": len(blocked_reasons) > 0,
        "blocked_reasons": blocked_reasons,
        "hint": "完整版将自动执行密钥三层扫描、依赖更新检查、抄袭检测（F8）。",
    }


if __name__ == "__main__":
    import sys, json
    from cli_wrappers import run_gitleaks, run_reuse
    proj = sys.argv[1] if len(sys.argv) > 1 else "."
    runner = ToolRunner()
    fs = run_gitleaks(runner, proj, "oss") + run_reuse(runner, proj, "oss")
    print(json.dumps(release_gate(runner, proj, fs), ensure_ascii=False, indent=2))
