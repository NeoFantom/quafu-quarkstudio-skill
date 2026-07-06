# 安全门

## 真实硬件 / quota gate

除非用户明确授权当前这一次具体提交，否则不要运行 `tmgr.run(task)`。一个安全的授权说明应包含：

- backend/chip 名称；
- task name；
- circuit 摘要或文件路径；
- shots；
- compiler/correction/DD options 是否开启；
- 已知的 quota 影响；
- 返回 task id 将保存在哪里。

## Read-only operations

完成凭证设置后，以下操作通常可作为只读检查，但仍应避免意外网络调用：

- import `quark.Task`（无 token、无网络）；
- 从用户批准的位置加载 token；
- 用户同意只读认证检查后运行 `tmgr.status()`；
- 对用户提供或已经持久化的 task id 运行 `tmgr.result(tid)`。

## Secret leak prevention

- 优先用 `helpers/retrieve_token_opencli.py --store ...`，而不是手动复制 token 值。
- 如果用户直接提供 token，优先用 `helpers/store_token.py --token-stdin`。
- 永远不要通过 `--token VALUE` 这类命令行参数把 token 写入 shell history。
- 对所有环境变量 dump 做 redaction；在可能存在 `QUAFU_API_TOKEN` 的上下文中不要运行 `env` 或 `set`。
