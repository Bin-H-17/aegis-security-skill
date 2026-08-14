# Contributing / 贡献指南

Thanks for your interest in improving AegisKit! / 感谢你想为 AegisKit 出力！

## How to contribute / 如何贡献

- **Issues**: report bugs or suggest features via GitHub Issues.
- **Pull requests**: fork → branch → commit → PR. Keep changes focused.
- **Code style**: follow existing style; run `py_compile` on any Python change
  (`python -m py_compile skills/security-audit-common/scripts/*.py`) before
  submitting.
- **License headers**: every new `.py` file must start with
  `# SPDX-License-Identifier: MIT`.
- **No secrets**: never commit real credentials. Test fixtures must use obvious
  placeholders (`*_EXAMPLE` / `CHANGE_ME`).
- **Third-party terms**: do NOT paste verbatim platform Terms of Service into
  the repo. Encode only our own extracted heuristics in `references/*.yaml` and
  cite the official source.

By contributing, you agree your contributions are licensed under the project's
MIT License. / 贡献内容按项目 MIT 许可证授权。

## Scope of automation / 自动化范围

AegisKit intentionally stays local-only and CLI-invoking. Please do not add
network telemetry, cloud calls, or copies of upstream scanner code (license
contamination). / AegisKit 坚持本地离线、命令行调用；请勿添加遥测/云调用或
上游扫描器代码副本（许可证传染）。
