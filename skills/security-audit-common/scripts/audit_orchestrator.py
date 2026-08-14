#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT
"""
audit_orchestrator.py — L0 统一审查主链路编排器

用法：
  python audit_orchestrator.py --scenario dev  --path <项目路径>
  python audit_orchestrator.py --scenario oss  --path <项目路径>
  python audit_orchestrator.py --scenario store --path <项目路径> [--market googleplay]
  python audit_orchestrator.py --scenario ai   --platforms OpenAI,Udio [--intent commercial]

场景：
  dev   → 密钥/SAST/SBOM/license 扫描 + 最小修复 + 统一报告（MVP 核心，F1-F6/F12）
  oss   → 开源发布 gate（reuse + gitleaks + 发布前 gate）（完整版 F7/F8）
  store → 上架合规清单（play_policy 快照，人工辅助）（完整版 F9）
  ai    → 平台条款逐平台一票否决（X1-X3）（完整版 F10）

铁律：本地离线、0 数据出境；命令行调用不改上游（规避 AGPL/LGPL）。
"""
from __future__ import annotations

import os
import sys
import argparse
from typing import List

# 允许直接运行（scripts 目录内）
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import Report, ToolRunner, new_audit_id, now_iso  # noqa
from cli_wrappers import (run_gitleaks, run_semgrep, run_bandit,  # noqa
                          run_osv_scanner, run_pip_audit, run_reuse)
from report_synthesizer import synthesize  # noqa
from minimal_fix_engine import enrich  # noqa
from ai_copyright_checker import check as ai_check  # noqa
from store_compliance import checklist as store_checklist  # noqa
from oss_compliance import release_gate as oss_gate  # noqa


def run_dev(project_path: str, out_dir: str, trace_id: str) -> Report:
    runner = ToolRunner(trace_id=trace_id, timeout=300)
    report = Report(audit_id=new_audit_id(), trace_id=trace_id,
                    scenario="dev", project_path=project_path, generated_at=now_iso())
    findings: List = []
    # 并行可优化，这里串行保稳定；每条工具独立降级
    for fn, name in [(run_gitleaks, "gitleaks"), (run_semgrep, "semgrep"),
                     (run_bandit, "bandit"), (run_osv_scanner, "osv-scanner"),
                     (run_pip_audit, "pip-audit"), (run_reuse, "reuse")]:
        try:
            fs = fn(runner, project_path, "dev")
            findings.extend(fs)
        except Exception as e:  # noqa
            report.tool_status[name] = f"error:{e}"
    findings = enrich(findings)
    report.findings = findings
    # 工具存在性探测（error 优先保留，不被覆盖）
    _errors = {k: v for k, v in report.tool_status.items() if str(v).startswith("error")}
    report.tool_status = _tool_status(runner)
    report.tool_status.update(_errors)
    synthesize(report, out_dir)
    return report


def _tool_status(runner: ToolRunner) -> dict:
    status = {}
    for t in ("gitleaks", "semgrep", "bandit", "osv-scanner", "pip-audit", "reuse"):
        status[t] = "ok" if not runner.run(t, ["--version"]).get("degraded") else "missing"
    return status


def run_oss(project_path: str, out_dir: str, trace_id: str) -> Report:
    runner = ToolRunner(trace_id=trace_id, timeout=300)
    report = Report(audit_id=new_audit_id(), trace_id=trace_id,
                    scenario="oss", project_path=project_path, generated_at=now_iso())
    fs = run_gitleaks(runner, project_path, "oss") + run_reuse(runner, project_path, "oss")
    fs = enrich(fs)
    report.findings = fs
    gate = oss_gate(runner, project_path, fs)
    report.gate_blocked = gate["blocked"]
    report.gate_reasons = gate["blocked_reasons"]
    report.tool_status = _tool_status(runner)
    synthesize(report, out_dir)
    return report


def run_store(project_path: str, out_dir: str, trace_id: str, market: str) -> dict:
    c = store_checklist(project_path, market)
    os.makedirs(out_dir, exist_ok=True)
    import json as _json
    with open(os.path.join(out_dir, f"store_checklist.{market}.json"), "w", encoding="utf-8") as f:
        _json.dump(c, f, ensure_ascii=False, indent=2)
    return c


def run_ai(platforms: List[str], intent: str) -> dict:
    return ai_check(platforms, intent)


def main():
    ap = argparse.ArgumentParser(description="安全审查 Skill 集合 L0 编排器")
    ap.add_argument("--scenario", required=True, choices=["dev", "oss", "store", "ai"])
    ap.add_argument("--path", default=".")
    ap.add_argument("--platforms", default="OpenAI,Udio")
    ap.add_argument("--intent", default="commercial", choices=["commercial", "download", "both"])
    ap.add_argument("--market", default="googleplay")
    ap.add_argument("--out", default=None, help="报告输出目录，默认 <path>/reports")
    args = ap.parse_args()

    trace_id = new_audit_id()
    out_dir = args.out or os.path.join(args.path, "reports")

    if args.scenario == "dev":
        r = run_dev(args.path, out_dir, trace_id)
        _print_gate(r.scenario, r.gate_blocked, r.gate_reasons, r.tool_status)
        print(f"报告：{os.path.join(out_dir, 'SECURITY_REPORT.md')}")
    elif args.scenario == "oss":
        r = run_oss(args.path, out_dir, trace_id)
        _print_gate(r.scenario, r.gate_blocked, r.gate_reasons, r.tool_status)
        print(f"报告：{os.path.join(out_dir, 'SECURITY_REPORT.md')}")
    elif args.scenario == "store":
        c = run_store(args.path, out_dir, trace_id, args.market)
        print(f"[store/{args.market}] 自动可核 {c['auto_count']} 项，需人工 {c['manual_count']} 项")
        print(f"清单：{os.path.join(out_dir, f'store_checklist.{args.market}.json')}")
    elif args.scenario == "ai":
        res = run_ai([p.strip() for p in args.platforms.split(",")], args.intent)
        gate = "🔴 阻断（存在一票否决）" if res["gate_blocked"] else "🟢 通过"
        print(f"[ai 版权裁决 / intent={res['intent']}] {gate}")
        for p in res["platforms"]:
            print(f"  - {p['name']}: {p['verdict']} | 商用={p['commercial_use']} 下载={p['download_right']} | {p['reason']}")


def _print_gate(scenario: str, blocked: bool, reasons: List[str], tool_status: dict):
    gate = "🔴 阻断（P0/P1 未清零）" if blocked else "🟢 通过（可发布）"
    print(f"=== 发布前 Gate（{scenario}）: {gate} ===")
    for r in reasons:
        print(f"  - {r}")
    print("工具状态：", tool_status)


if __name__ == "__main__":
    main()
