# SECURITY_REPORT.md 报告模板（规范）

> 本报告由 L2 报告合成器本地生成，遵循 P0–P3 分级 + 最小改动修复 + 复检命令规范。
> 0 数据出境；所有产物落本地项目目录。

## 头部元信息

| 字段 | 说明 |
| --- | --- |
| 审计 ID | AUD-YYYYMMDD-HHMMSS |
| 场景 | dev / oss / store / ai |
| 项目 | 被扫描项目绝对路径 |
| 生成时间 | ISO8601 |
| 工具目录 | `$SECURITY_TOOLS_HOME`（默认 `~/security-tools`） |

## 1. 总览

| 级别 | 数量 |
| --- | --- |
| P0 阻断（发布前必须清零） | N |
| P1 高危（发布前建议清零） | N |
| P2 中危（迭代修复） | N |
| P3 低危/信息（记录跟踪） | N |

**发布前 Gate：🔴 阻断 / 🟢 通过**

## 2. 工具状态

| 工具 | 状态（ok / missing / degraded） |
| --- | --- |

## 3. 发现明细

每个发现含：来源、规则、位置、说明、最小改动修复、复检命令。

### [P0] 示例：硬编码 AWS 密钥

- 来源：gitleaks ｜ 规则：aws-access-token
- 位置：config/settings.py:42
- 说明：命中规则 aws-access-token：AKIA****************
- 最小改动修复：在 Vault/环境变量存真实密钥，代码中改读 `os.environ["AWS_KEY"]`；立即轮换并清理 git 历史。
- 复检命令：
  ```bash
  gitleaks detect --source <项目> -f json --exit-code 0
  ```

## 4. 复检总命令

```bash
python audit_orchestrator.py --scenario <场景> --path "<项目>"
```
