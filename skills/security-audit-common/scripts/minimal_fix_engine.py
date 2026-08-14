#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT
"""
minimal_fix_engine.py — 最小改动修复引擎

设计（架构锁定）：
- 思路借鉴 DeepAudit（多 agent 工作流 + 本地推理），**严禁复制其代码**（AGPL-3.0 强 copyleft）。
- 坚持命令行调用、不改上游；本地推理走本地 Ollama（不联网、0 数据出境）。
- 无 Ollama 时回退规则建议（仍可交付，不阻塞）。

职责：对每条 Finding 产出「最小改动修复」建议，写回 Finding.recommendation。
"""
from __future__ import annotations

import json
import logging
import os
import urllib.request
from typing import List

from common import Finding

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5-coder:7b")

# 规则回退库：按 source/rule 关键词给最小改动建议
RULE_FALLBACK = {
    "gitleaks": "在 1Password/Vault 存真实密钥，代码中改用环境变量读取；立即在对应平台吊销并轮换该密钥；清理 git 历史（git filter-repo）。",
    "semgrep": "按规则给出的修复模式改写；如为测试/脚手架误报，加 `// nosemgrep` 并附理由。",
    "bandit": "使用参数化查询/安全反序列化/避免 eval；硬编码凭证改为配置注入。",
    "osv-scanner": "升级到 OSV 建议的修复版本；检查 lockfile 是否锁定安全版本。",
    "pip-audit": "执行 `pip install --upgrade <pkg>` 到修复版本；更新 requirements 与 lockfile。",
    "reuse": "在源文件头添加 `SPDX-License-Identifier` 与 `SPDX-FileCopyrightText`，或在 `.reuse/dep5` 声明。",
}


def _ollama_available() -> bool:
    try:
        req = urllib.request.Request(OLLAMA_HOST + "/api/tags", method="GET")
        with urllib.request.urlopen(req, timeout=3) as r:
            return r.status == 200
    except Exception:
        return False


def _ollama_fix(f: Finding, max_tokens: int = 400) -> str:
    prompt = (
        "你是本地安全修复助手。请针对下面这条安全发现，给出最小改动修复建议"
        "（只改必要处，附关键代码片段，中文，≤200字）。\n"
        f"来源：{f.source}\n规则：{f.rule_id}\n位置：{f.file}:{f.line}\n说明：{f.description}\n"
    )
    payload = json.dumps({"model": OLLAMA_MODEL, "prompt": prompt, "stream": False,
                          "options": {"num_predict": max_tokens}}).encode("utf-8")
    req = urllib.request.Request(OLLAMA_HOST + "/api/generate", data=payload,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.loads(r.read())
    return data.get("response", "").strip()


def enrich(findings: List[Finding]) -> List[Finding]:
    """为每条 Finding 补充最小改动修复建议（就地更新 recommendation）。"""
    has_ollama = _ollama_available()
    for f in findings:
        # 若已有推荐则保留，否则补充
        base = RULE_FALLBACK.get(f.source, "按该来源最佳实践修复，并复检确认。")
        if has_ollama and not f.recommendation:
            try:
                ai = _ollama_fix(f)
                if ai:
                    f.recommendation = f"{base}\n[AiFix] {ai}"
                    continue
            except Exception as e:
                logging.getLogger("security-audit").debug("ollama fix unavailable: %s", e)
        if not f.recommendation:
            f.recommendation = base
    return findings
