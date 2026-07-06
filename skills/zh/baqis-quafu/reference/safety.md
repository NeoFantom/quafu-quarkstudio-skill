# Safety gates

## 真实硬件 / quota gate

除非用户明确授权当前这一次具体提交，否则不要运行 `tmgr.run(task)`。安全的授权说明应包含：

- backend/chip name；
- task name；
- circuit summary 或 file path；
- shots；
- compiler/correction/DD options 是否启用；
- 已知的 quota 影响；
- 返回的 task id 将保存在哪里。

## 只读和本地操作

完成相关 setup gate 后，以下操作通常安全，但仍不要突然发起网络调用：

- import `quark.Task`（无 token、无网络）；
- 从已批准位置加载 token；
- 用户同意只读认证检查后运行 `tmgr.status()`；
- 针对用户提供或已保存的 task id 运行 `tmgr.result(tid)`；
- 用户 opt-in 安装 QSteed 包后，运行 QSteed 本地 import/transpile smoke check。

## QSteed 边界

- QSteed transpiler demo 是本地代码执行；它不等于授权 Quafu 硬件提交。
- QSteed setup 会安装包，并可能创建 `~/QSteed/config.ini`；只能在 opt-in 后运行。
- QSteed `Compiler`/`compiler_api` 路径可能需要 MySQL/resource database deployment，也可能属于真实设备控制管线；除非用户明确要求该 deployment/configuration，否则不要运行这些路径。
- compiled OpenQASM circuit 在 `tmgr.run(task)` 前仍必须经过 QuarkStudio 提交安全门。

## Secret leak prevention

- 优先用 `helpers/retrieve_token_opencli.py --store ...`，不要手工复制 token 值。
- 如果用户直接提供 token，优先用 `helpers/store_token.py --token-stdin`。
- 不要通过 `--token VALUE` 参数把 token 放入 shell history。
- 对环境 dump 做 redaction；在可能存在 `QUAFU_API_TOKEN` 的上下文里，不要运行 `env` 或 `set`。
