#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT
"""
ai_copyright_checker.py — AI 内容版权逐平台裁决（X1-X3 一票否决）

铁律（X1-X7冲突裁决附录.md）：
- X1-X3：OpenAI（用户拥有 Output / 可商用 / 可下载） vs Udio（平台保留 / 禁商用 / 禁下载）条款冲突。
- 裁决逻辑：逐平台核对，不默认合规；任一平台禁止商用/下载即整体阻断（一票否决）。
- 条款库快照来自 references/platform_terms.yaml（季度重抓，U-05/U-06）。
"""
from __future__ import annotations

import os
from typing import Dict, Any, List

from common import load_yaml, REFERENCES_DIR

PLATFORM_TERMS = os.path.join(REFERENCES_DIR, "platform_terms.yaml")


def _load() -> Dict[str, Any]:
    if not os.path.exists(PLATFORM_TERMS):
        return {}
    return load_yaml(PLATFORM_TERMS) or {}


def check(platforms: List[str], intent: str = "commercial") -> Dict[str, Any]:
    """
    intent: 'commercial' | 'download' | 'both'
    返回 {platforms:[{name, commercial_use, download_right, verdict, reason}], gate_blocked, gate_reasons}
    """
    data = _load()
    known = data.get("platforms", {})
    results: List[Dict[str, Any]] = []
    blocked = False
    reasons: List[str] = []
    unknown_platforms: List[str] = []

    for p in platforms:
        entry = known.get(p)
        if not entry:
            unknown_platforms.append(p)
            results.append({
                "name": p, "commercial_use": "unknown", "download_right": "unknown",
                "verdict": "MANUAL", "reason": "条款库未收录，转人工核对（X7 国产平台缺失）。",
            })
            blocked = True
            reasons.append(f"{p} 条款未知，需人工裁决")
            continue
        cu = entry.get("commercial_use", "unknown")
        dr = entry.get("download_right", "unknown")
        verdict = "PASS"
        reason = []
        if intent in ("commercial", "both") and cu != "allowed":
            verdict = "VETO"
            reason.append(f"商用权={cu}（禁止/受限）")
        if intent in ("download", "both") and dr != "allowed":
            verdict = "VETO"
            reason.append(f"下载权={dr}（禁止/受限）")
        if verdict == "VETO":
            blocked = True
            reasons.append(f"{p}：{'；'.join(reason)}")
        results.append({
            "name": p, "commercial_use": cu, "download_right": dr,
            "verdict": verdict, "reason": "；".join(reason) or "条款允许，可商用/下载。",
        })

    return {
        "intent": intent,
        "platforms": results,
        "unknown_platforms": unknown_platforms,
        "gate_blocked": blocked,
        "gate_reasons": reasons,
    }


if __name__ == "__main__":
    import sys, json
    plats = sys.argv[1].split(",") if len(sys.argv) > 1 else ["OpenAI", "Udio"]
    it = sys.argv[2] if len(sys.argv) > 2 else "commercial"
    print(json.dumps(check(plats, it), ensure_ascii=False, indent=2))
