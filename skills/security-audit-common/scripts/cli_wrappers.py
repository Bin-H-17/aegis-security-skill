#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT
"""
cli_wrappers.py — 对 6 个开源 CLI 的封装与输出解析

调用方式：命令行调用、不改上游（规避 AGPL/LGPL 传染）。
每个函数返回 List[Finding]，工具缺失时返回空列表并标记降级。

工具版本（架构锁定，仅命令行调用、不改上游）：
- gitleaks 8.30.1
- semgrep 1.172.0
- bandit 1.9.4
- osv-scanner 2.4.0
- pip-audit 2.10.1
- reuse 6.2.0
各工具保留自身许可证（见根目录 NOTICE），用户安装/使用时须遵守。
"""
from __future__ import annotations

import json
import os
from typing import List

from common import Finding, ToolRunner, severity_from_level, BASELINES_DIR

GITLEAKS_BASELINE = os.path.join(BASELINES_DIR, "gitleaks.toml")
SEMGREP_RULES = os.path.join(BASELINES_DIR, "semgrep_rules")


def run_gitleaks(runner: ToolRunner, project_path: str, scenario: str = "dev") -> List[Finding]:
    findings: List[Finding] = []
    args = ["detect", "--source", project_path, "-f", "json", "--exit-code", "0",
            "--no-banner", "--baseline-path", GITLEAKS_BASELINE]
    # baseline 文件不存在时去掉该参数
    if not os.path.exists(GITLEAKS_BASELINE):
        args = ["detect", "--source", project_path, "-f", "json", "--exit-code", "0", "--no-banner"]
    res = runner.run("gitleaks", args)
    if res["degraded"] or not res["stdout"].strip():
        return findings
    try:
        data = json.loads(res["stdout"])
    except Exception:
        return findings
    for item in data if isinstance(data, list) else []:
        findings.append(Finding(
            scenario=scenario, source="gitleaks",
            rule_id=item.get("RuleID", ""), severity="P0",
            title=item.get("Description", "密钥/敏感信息泄露"),
            file=item.get("File", ""), line=item.get("Line"),
            description=f"命中规则 {item.get('RuleID','')}：{item.get('Match','')[:120]}",
            recommendation="立即轮换该密钥并移出仓库；如为误报加入 .gitleaksignore；清理 git 历史。",
            recheck=f"gitleaks detect --source {project_path} -f json --exit-code 0",
        ))
    return findings


def run_semgrep(runner: ToolRunner, project_path: str, scenario: str = "dev") -> List[Finding]:
    findings: List[Finding] = []
    # 优先使用本项目基线规则，否则自动规则
    cfg = os.path.join(SEMGREP_RULES, "owasp.yml")
    if os.path.exists(cfg):
        args = ["--config", cfg, "--json", "--quiet", "--error", project_path]
    else:
        args = ["--config", "auto", "--json", "--quiet", project_path]
    res = runner.run("semgrep", args)
    if res["degraded"] or not res["stdout"].strip():
        return findings
    try:
        data = json.loads(res["stdout"])
    except Exception:
        return findings
    for r in data.get("results", []):
        sev = severity_from_level(r.get("extra", {}).get("severity", ""))
        findings.append(Finding(
            scenario=scenario, source="semgrep",
            rule_id=r.get("check_id", ""), severity=sev,
            title=r.get("extra", {}).get("message", "SAST 命中"),
            file=r.get("path", ""), line=r.get("start", {}).get("line"),
            description=r.get("extra", {}).get("message", ""),
            recommendation="按规则建议修复代码；若为框架误报加 nosem 注释并说明。",
            recheck=f"semgrep --config {cfg if os.path.exists(cfg) else 'auto'} --json {project_path}",
        ))
    return findings


def run_bandit(runner: ToolRunner, project_path: str, scenario: str = "dev") -> List[Finding]:
    findings: List[Finding] = []
    args = ["-r", project_path, "-f", "json", "-q"]
    res = runner.run("bandit", args)
    if res["degraded"] or not res["stdout"].strip():
        return findings
    try:
        data = json.loads(res["stdout"])
    except Exception:
        return findings
    for r in data.get("results", []):
        sev = severity_from_level(r.get("issue_severity", ""))
        findings.append(Finding(
            scenario=scenario, source="bandit",
            rule_id=r.get("test_id", ""), severity=sev,
            title=r.get("issue_text", "Python 安全告警"),
            file=r.get("filename", ""), line=r.get("line_number"),
            description=f"[{r.get('test_name','')}] {r.get('issue_text','')}",
            recommendation="按 bandit 文档修复；关注注入/反序列化/硬编码等高危项。",
            recheck=f"bandit -r {project_path} -f json",
        ))
    return findings


def run_osv_scanner(runner: ToolRunner, project_path: str, scenario: str = "dev") -> List[Finding]:
    findings: List[Finding] = []
    args = ["--format", "json", "--recursive", project_path]
    res = runner.run("osv-scanner", args)
    if res["degraded"] or not res["stdout"].strip():
        return findings
    try:
        data = json.loads(res["stdout"])
    except Exception:
        return findings
    for pkg_group in data.get("results", []):
        for vuln in pkg_group.get("vulnerabilities", []):
            sev = severity_from_level(vuln.get("severity", ""))
            pkgs = vuln.get("packages", [])
            pkg_name = pkgs[0].get("package", {}).get("name", "") if pkgs else ""
            fixed = vuln.get("fixed_version") or (vuln.get("affected", [{}])[0].get("ranges", [{}])[0].get("events", [{}]) if vuln.get("affected") else {})
            findings.append(Finding(
                scenario=scenario, source="osv-scanner",
                rule_id=vuln.get("id", ""), severity=sev,
                title=f"依赖漏洞 {vuln.get('id','')} ({pkg_name})",
                file=pkg_name, line=None,
                description=vuln.get("summary", ""),
                recommendation=f"升级 {pkg_name} 至修复版本（参考 OSV 建议）。",
                recheck=f"osv-scanner --format json --recursive {project_path}",
            ))
    return findings


def run_pip_audit(runner: ToolRunner, project_path: str, req_path: str = None,
                  scenario: str = "dev") -> List[Finding]:
    findings: List[Finding] = []
    if req_path and os.path.exists(req_path):
        args = ["-f", "json", "-r", req_path, "-l"]
    else:
        # 退而扫描项目内所有 requirements*.txt
        import glob
        reqs = glob.glob(os.path.join(project_path, "**", "requirements*.txt"), recursive=True)
        if not reqs:
            return findings
        args = ["-f", "json", "-r", reqs[0], "-l"]
    res = runner.run("pip-audit", args)
    if res["degraded"] or not res["stdout"].strip():
        return findings
    try:
        data = json.loads(res["stdout"])
    except Exception:
        return findings
    for dep in data.get("dependencies", []):
        name = dep.get("name", "")
        for vuln in dep.get("vulnerabilities", []):
            sev = severity_from_level(vuln.get("severity", ""))
            fixes = ",".join(vuln.get("fix_versions", [])) or "见 advisories"
            findings.append(Finding(
                scenario=scenario, source="pip-audit",
                rule_id=vuln.get("id", ""), severity=sev,
                title=f"Python 依赖漏洞 {vuln.get('id','')} ({name})",
                file=name, line=None,
                description=vuln.get("description", ""),
                recommendation=f"升级 {name} 至 {fixes}。",
                recheck=f"pip-audit -f json -r {reqs[0] if not req_path else req_path} -l",
            ))
    return findings


def run_reuse(runner: ToolRunner, project_path: str, scenario: str = "dev") -> List[Finding]:
    findings: List[Finding] = []
    args = ["lint", "--json", project_path]
    res = runner.run("reuse", args)
    if res["degraded"]:
        return findings
    # reuse lint 退出码非 0 表示有问题，但 stdout 可能含 JSON
    text = res["stdout"].strip()
    data = None
    if text:
        try:
            data = json.loads(text)
        except Exception:
            data = None
    if not data:
        return findings
    summary = data.get("summary", {})
    missing = summary.get("missing_licenses", 0) + summary.get("missing_copyrights", 0)
    if missing > 0:
        findings.append(Finding(
            scenario=scenario, source="reuse",
            rule_id="REUSE-COMPLIANCE", severity="P1",
            title=f"REUSE 合规缺口：缺失许可证/版权声明 {missing} 处",
            file=project_path, line=None,
            description=f"missing_licenses={summary.get('missing_licenses')}, missing_copyrights={summary.get('missing_copyrights')}",
            recommendation="为源文件添加 SPDX-License-Identifier 与版权头；或写入 .reuse/dep5。",
            recheck=f"reuse lint --json {project_path}",
        ))
    return findings
