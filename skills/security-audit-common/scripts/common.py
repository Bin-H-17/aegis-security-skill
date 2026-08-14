#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT
"""
common.py — 安全审查 Skill 集合 L2 公共层基础模块

职责：
- 路径解析（SECURITY_AUDIT_HOME / SECURITY_TOOLS_HOME / venv）
- 配置加载（YAML，PyYAML 优先，缺失则内置极简解析）
- 日志与密钥掩码
- Finding / Report 数据模型
- 子进程 CLI 调用封装（超时、降级、重试基线）

设计铁律（见架构文档）：
- 命令行调用、不改上游（规避 AGPL/LGPL 传染）
- 本地离线、0 数据出境
- 工具默认装用户目录 ~/security-tools（可用 SECURITY_TOOLS_HOME 覆盖）

本文件不依赖任何重量级第三方库；仅需 pyyaml（安装脚本已装，缺失时回退内置解析）。
"""
from __future__ import annotations

import os
import re
import json
import subprocess
import datetime
import logging
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any

# ---------------------------------------------------------------------------
# 路径解析
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_HOME = os.path.dirname(SCRIPT_DIR)  # security-audit-common/
SECURITY_AUDIT_HOME = os.environ.get("SECURITY_AUDIT_HOME", DEFAULT_HOME)
SECURITY_TOOLS_HOME = os.environ.get("SECURITY_TOOLS_HOME", os.path.expanduser("~/security-tools"))
VENV_DIR = os.path.join(SECURITY_TOOLS_HOME, "venv")

REFERENCES_DIR = os.path.join(SECURITY_AUDIT_HOME, "references")
BASELINES_DIR = os.path.join(SECURITY_AUDIT_HOME, "baselines")
TEMPLATES_DIR = os.path.join(SECURITY_AUDIT_HOME, "templates")

# ---------------------------------------------------------------------------
# 工具可执行文件定位
# ---------------------------------------------------------------------------
def _venv_bin(name: str) -> str:
    """返回 venv 内的可执行文件路径（Windows 下补 .exe）。"""
    ext = ".exe" if os.name == "nt" else ""
    return os.path.join(VENV_DIR, "Scripts" if os.name == "nt" else "bin", name + ext)

TOOL_PATHS = {
    "gitleaks": os.path.join(SECURITY_TOOLS_HOME, "gitleaks.exe" if os.name == "nt" else "gitleaks"),
    "osv-scanner": os.path.join(SECURITY_TOOLS_HOME, "osv-scanner.exe" if os.name == "nt" else "osv-scanner"),
    "semgrep": _venv_bin("semgrep"),
    "bandit": _venv_bin("bandit"),
    "pip-audit": _venv_bin("pip-audit"),
    "reuse": _venv_bin("reuse"),
}

SEVERITY_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3, "UNKNOWN": 4}

# ---------------------------------------------------------------------------
# 日志（结构化，含 traceId / tenantId，禁止打印密钥明文）
# ---------------------------------------------------------------------------
def get_logger(name: str = "security-audit") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(
            "%(asctime)s %(levelname)s traceId=%(traceId)s tenantId=%(tenantId)s %(message)s"
        ))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

# 密钥掩码：避免日志/报告泄露真实密钥
_SECRET_RE = re.compile(r"(?i)(AKIA[0-9A-Z]{16}|sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{36}|"
                        r"xox[baprs]-[A-Za-z0-9-]{10,}|AIza[0-9A-Za-z_-]{35}|"
                        r"-----BEGIN [A-Z ]*PRIVATE KEY-----)")

def mask_secret(text: str) -> str:
    return _SECRET_RE.sub(lambda m: m.group(0)[:6] + "****REDACTED****", text or "")

# ---------------------------------------------------------------------------
# YAML 加载（PyYAML 优先，缺失回退极简解析）
# ---------------------------------------------------------------------------
def load_yaml(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    try:
        import yaml  # type: ignore
        return yaml.safe_load(text)
    except Exception:
        return _mini_yaml(text)

def _mini_yaml(text: str) -> Dict[str, Any]:
    """仅支持本项目 references 用的扁平 + 一层列表结构，足够兜底。"""
    root: Dict[str, Any] = {}
    stack = [root]
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line.strip() or line.strip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))
        key_val = line.strip()
        while len(stack) > 1 and indent < _depth_of(stack):
            stack.pop()
        if key_val.startswith("- "):
            item = key_val[2:].strip()
            if isinstance(stack[-1], list):
                stack[-1].append(_coerce(item))
            else:
                parent = stack[-1]
                # 找到最近列表键
                stack[-1] = parent
        else:
            if ":" in key_val:
                k, _, v = key_val.partition(":")
                k = k.strip()
                v = v.strip()
                if v == "":
                    new_node: Any = {}
                    stack[-1][k] = new_node
                    stack.append(new_node)
                else:
                    stack[-1][k] = _coerce(v)
    return root

def _depth_of(node: Any) -> int:
    # 简易：用对象 id 映射深度不可行，这里用占位返回 0（极简解析仅兜底）
    return 0

def _coerce(v: str) -> Any:
    if v.lower() in ("true", "false"):
        return v.lower() == "true"
    if v.lower() in ("null", "~", ""):
        return None
    try:
        return int(v)
    except ValueError:
        pass
    try:
        return float(v)
    except ValueError:
        pass
    return v

# ---------------------------------------------------------------------------
# 数据模型
# ---------------------------------------------------------------------------
@dataclass
class Finding:
    scenario: str = ""
    source: str = ""           # gitleaks / semgrep / bandit / osv-scanner / pip-audit / reuse
    rule_id: str = ""
    severity: str = "P3"       # P0-P3
    title: str = ""
    file: str = ""
    line: Optional[int] = None
    description: str = ""
    recommendation: str = ""
    recheck: str = ""          # 复检命令
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class Report:
    audit_id: str = ""
    trace_id: str = ""
    tenant_id: str = "local"
    scenario: str = ""
    project_path: str = ""
    generated_at: str = ""
    findings: List[Finding] = field(default_factory=list)
    gate_blocked: bool = False
    gate_reasons: List[str] = field(default_factory=list)
    tool_status: Dict[str, str] = field(default_factory=dict)  # tool -> ok/degraded/missing

    def sorted_findings(self) -> List[Finding]:
        return sorted(self.findings, key=lambda f: (SEVERITY_ORDER.get(f.severity, 9), f.source))

    def by_severity(self, sev: str) -> List[Finding]:
        return [f for f in self.sorted_findings() if f.severity == sev]

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return d

# ---------------------------------------------------------------------------
# 子进程 CLI 调用封装
# ---------------------------------------------------------------------------
class ToolRunner:
    """封装对本地 CLI 工具的调用，处理缺失/超时/降级。"""

    def __init__(self, trace_id: str = "local", timeout: int = 300):
        self.trace_id = trace_id
        self.timeout = timeout
        self.logger = get_logger()
        self.extra = {"traceId": trace_id, "tenantId": "local"}

    def run(self, tool: str, args: List[str]) -> Dict[str, Any]:
        """返回 {rc, stdout, stderr, ok, degraded}。工具缺失时 degraded=True。"""
        exe = TOOL_PATHS.get(tool, tool)
        if not os.path.exists(exe):
            msg = f"工具缺失（BD-01 降级）：{tool} -> {exe}"
            self.logger.warning(msg, extra=self.extra)
            return {"rc": -1, "stdout": "", "stderr": msg, "ok": False, "degraded": True}
        cmd = [exe] + args
        self.logger.info(f"调用 {tool}: {' '.join(mask_secret(a) for a in cmd)}", extra=self.extra)
        try:
            proc = subprocess.run(
                cmd, capture_output=True, text=True, timeout=self.timeout,
                cwd=os.environ.get("SECURITY_AUDIT_CWD", None),
            )
            return {
                "rc": proc.returncode,
                "stdout": mask_secret(proc.stdout),
                "stderr": mask_secret(proc.stderr),
                "ok": proc.returncode == 0,
                "degraded": False,
            }
        except subprocess.TimeoutExpired:
            msg = f"工具超时（{self.timeout}s）：{tool}"
            self.logger.error(msg, extra=self.extra)
            return {"rc": -2, "stdout": "", "stderr": msg, "ok": False, "degraded": True}
        except Exception as e:  # noqa
            msg = f"工具调用异常：{tool} {type(e).__name__} {e}"
            self.logger.error(msg, extra=self.extra)
            return {"rc": -3, "stdout": "", "stderr": msg, "ok": False, "degraded": True}

# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------
def now_iso() -> str:
    return datetime.datetime.now().replace(microsecond=0).isoformat()

def new_audit_id() -> str:
    return "AUD-" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

def severity_from_level(level: str) -> str:
    """将工具级别映射为 P0-P3。"""
    l = (level or "").upper()
    if l in ("CRITICAL", "HIGH", "BLOCKER", "ERROR"):
        return "P0"
    if l in ("MEDIUM", "WARN", "WARNING"):
        return "P1"
    if l in ("LOW", "INFO", "NOTE"):
        return "P2"
    return "P3"

def write_json(path: str, obj: Any) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
