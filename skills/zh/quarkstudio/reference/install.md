# 安装与 smoke-check QuarkStudio

## Install

Captured official lesson 中 QuarkStudio 要求 Python `>=3.12`，安装命令为：

```bash
python -m pip install quarkstudio
```

lesson 使用的 import 是：

```python
from quark import Task
```

确认方式：`platform-info.md` 汇总的 Quafu-SQC 官方文档快照；置信度：doc snapshot。

## Checks

使用 bundled helper 做确定性、redacted 的检查：

```bash
python .claude/skills/quarkstudio/helpers/sdk_smoke.py --check-import
```

这只会 import `quark.Task`，不会使用 token，也不会发起网络请求。

只读认证检查前，先问用户，然后运行：

```bash
python .claude/skills/quarkstudio/helpers/sdk_smoke.py --status
```

helper 会从 `QUAFU_API_TOKEN`、`~/.config/quarkstudio/credentials.env` 或传入 `--project-root` 时的项目 `secrets.yaml` 读取 token。它只打印 status 输出；永远不打印 token。
