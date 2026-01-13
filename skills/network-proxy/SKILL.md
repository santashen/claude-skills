---
name: network-proxy-handler
description: 自动处理网络连接错误，通过设置本地代理进行重试。
---

# 网络异常处理流程

当你在执行网络相关的操作（如使用 curl, wget, git clone, npm install, 或访问外部 URL）时，如果遇到以下类型的错误：
* Connection refused
* Connection timed out
* Could not resolve host
* Network is unreachable
* 403 Forbidden (疑似被屏蔽)
* A connection attempt failed

### 强制执行步骤：
1. **识别错误**：一旦发现上述网络错误，不要直接向用户报错。
2. **应用代理重试**：立即使用代理 `http://127.0.0.1:7890` 重新执行失败的命令。
   * 如果是 Bash 命令，请在命令前添加环境变量，例如：`HTTP_PROXY=http://127.0.0.1:7890 HTTPS_PROXY=http://127.0.0.1:7890 <原命令>`
3. **任务完成后恢复**：
   * 由于在 Bash 命令前临时设置环境变量仅对当前命令有效，执行完该命令后，后续操作应默认不带代理，除非再次报错。
4. **日志反馈**：在输出中告知用户：“检测到网络错误，已自动通过代理 127.0.0.1:7890 重试成功。”

### 约束：
* 仅在第一次尝试失败后才启用代理。
* 不要修改用户的全局系统代理配置，仅在执行具体工具命令时临时挂载。