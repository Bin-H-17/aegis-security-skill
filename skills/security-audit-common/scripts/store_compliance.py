#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT
"""
store_compliance.py — 应用商店上架合规清单生成（F9，完整版）

说明（架构）：上架合规自动化在 MVP 为「提示 + 人工」，完整版做结构化核对。
本模块读取 references/play_policy.yaml，生成逐项 StoreChecklist；
对需要平台/法律判定的项标记为 MANUAL（转人工），不默认通过。
"""
from __future__ import annotations

import os
from typing import Dict, Any, List

from common import load_yaml, REFERENCES_DIR

PLAY_POLICY = os.path.join(REFERENCES_DIR, "play_policy.yaml")


def _load() -> Dict[str, Any]:
    if not os.path.exists(PLAY_POLICY):
        return {}
    return load_yaml(PLAY_POLICY) or {}


def checklist(project_path: str, market: str = "googleplay") -> Dict[str, Any]:
    data = _load()
    markets = data.get("markets", {})
    policy = markets.get(market, {})
    items: List[Dict[str, Any]] = []
    for key, spec in policy.items():
        if isinstance(spec, dict):
            items.append({
                "item": key,
                "requirement": spec.get("requirement", ""),
                "auto_checkable": spec.get("auto_checkable", False),
                "status": "MANUAL" if not spec.get("auto_checkable", False) else "AUTO_PENDING",
                "note": spec.get("note", ""),
            })
        else:
            items.append({"item": key, "requirement": str(spec), "auto_checkable": False,
                          "status": "MANUAL", "note": ""})
    return {
        "market": market,
        "project_path": project_path,
        "items": items,
        "auto_count": sum(1 for i in items if i["status"] == "AUTO_PENDING"),
        "manual_count": sum(1 for i in items if i["status"] == "MANUAL"),
        "note": "自动化核对仅为辅助，国内三证/ICP/软著等法律要件必须人工确认。",
    }


if __name__ == "__main__":
    import sys, json
    proj = sys.argv[1] if len(sys.argv) > 1 else "."
    mkt = sys.argv[2] if len(sys.argv) > 2 else "googleplay"
    print(json.dumps(checklist(proj, mkt), ensure_ascii=False, indent=2))
