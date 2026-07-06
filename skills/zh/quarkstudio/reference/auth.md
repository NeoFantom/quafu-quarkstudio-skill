# QuarkStudio / Quafu 认证与凭证 bootstrap

## Source-backed facts

- `[DURABLE]` Quafu-SQC 账号必须先存在，才能进行 token 设置。如果用户尚未注册，引导他们查看公开注册截图：<https://neofantom.github.io/quafu-lesson1/assets/screenshots/00-register.png>。置信度：public walkthrough asset。
- `[DURABLE]` QuarkStudio 初始化方式是 `from quark import Task` 与 `Task("token")`。确认方式：`platform-info.md` 汇总的 Quafu-SQC 公开文档；置信度：public docs。
- `[DURABLE]` 官方 lesson 说明 token 30 天过期，过期后需要重新申请。确认方式：`platform-info.md` 汇总的 Quafu-SQC 公开文档；置信度：public docs。
- `[DURABLE]` Quafu-SQC UI 有认证端点：`GET /api/api-token` 返回字段 `api_token`，`POST /api/api-token` 刷新 token，`GET /api/api-token-expiration` 获取过期时间；请求使用浏览器 credentials。确认方式：console behavior snapshot；置信度：UI behavior snapshot。
- `[DURABLE]` 登录使用 `/api/token` 表单流程，可能包含反机器人检查。确认方式：console login behavior snapshot；置信度：UI behavior snapshot。因此 agent 不得自动填写密码；应让用户手动登录。

## First-run decision tree

1. 询问用户是否已经注册 Quafu-SQC 账号。
2. 如果用户尚未注册，引导他们查看注册截图，并等待他们完成注册：

```text
https://neofantom.github.io/quafu-lesson1/assets/screenshots/00-register.png
```

用户说注册完成前，不要请求、获取或保存 API token。

3. 如果用户已经注册或刚完成注册，询问他们是否已有 Quafu API token。
4. 如果用户通过安全输入通道提供 token，不要复述它。立即用 `helpers/store_token.py` 保存。
5. 如果用户没有 token，询问是否允许打开浏览器并辅助获取。
6. 用户同意后运行：

```bash
opencli browser quafu-token open https://quafu-sqc.baqis.ac.cn/login
```

然后让用户手动登录。不要填写用户名或密码。

7. 用户说已经登录后，取回并保存 token，过程不打印 token：

```bash
python helpers/retrieve_token_opencli.py --session quafu-token --store user-env
```

只有用户明确选择 per-project dotenv 存储时，才使用 `--store project-env --project-root PATH`。

## Storage destinations

### 默认：XDG 用户配置文件

`$XDG_CONFIG_HOME/quarkstudio/credentials.env`，未设置 `XDG_CONFIG_HOME` 时回退到 `~/.config/quarkstudio/credentials.env`。

helper 写入：

```bash
QUAFU_API_TOKEN=<redacted-secret-value>
```

目录权限为 `0700`，文件权限为 `0600`。后续 agent 可以用 shell 或 Python dotenv 风格解析。

### 显式项目选项：`.env.local`

只有用户选择 per-project 存储时才使用。helper 会在选定项目根目录的 `.env.local` 中写入或更新：

```bash
QUAFU_API_TOKEN=<redacted-secret-value>
```

文件权限为 `0600`。如果选定根目录是 git 仓库，helper 会拒绝写入未被 git ignore 的 `.env.local`，因为项目本地 secret 不应被提交。应先把 `.env.local` 加入 `.gitignore`、改用 `user-env`，或在明确解释风险后传 `--allow-unignored-project-env`。

## Token hygiene checklist

- 永远不要把 token 粘到源码、task JSON、日志、截图或回复里。
- 不要把 token 作为可见命令行参数运行；优先用 stdin 或浏览器登录态获取。
- 不要把整个 secrets dict 传给可能在异常里打印参数的 SDK constructor 或 wrapper。
- 报告成功时，只说明 token 存在哪里、是否拿到过期时间；永远不要包含 token 值。
