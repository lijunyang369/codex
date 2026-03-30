# Chrome Relay 重启恢复 SOP

日期: 2026-03-25

适用场景:

- 电脑重启后原来的 Chrome 调试会话失效
- `chrome-relay` 断开
- `http://172.31.208.1:9223` 无法访问
- 需要重新接管浏览器中的 Upwork 会话

## 一、问题现象

这次出现的实际现象:

- 之前的 `chrome-relay` 端口 `9223` 持续报 `ECONNRESET`
- 本地 `http://127.0.0.1:9222/json/version` 也无法访问
- 说明不是单纯 relay 挂了，而是 Chrome 的远程调试端口没有恢复

## 二、根因

这次根因有两层:

1. 电脑重启后，之前带 `--remote-debugging-port=9222` 的 Chrome 会话已经不存在
2. 新启动 Chrome 时，`--user-data-dir=%TEMP%\\codex-chrome-profile` 这种写法没有正确展开成真实路径，导致 Chrome 虽然启动了，但 `9222` 没有正常开放

## 三、正确恢复顺序

正确顺序不是先查 Upwork，而是:

1. 先确认 Chrome 远程调试端口 `9222` 是否存在
2. 如果不存在，重新启动带调试端口的 Chrome
3. 再恢复 `9223 -> 9222` 的 relay
4. 最后确认浏览器页签和 Upwork 登录态

## 四、本次验证过的有效启动方式

### 1. 启动带调试端口的 Chrome

关键点:

- 必须显式指定:
  - `--remote-debugging-port=9222`
  - `--remote-debugging-address=127.0.0.1`
- 必须给 `--user-data-dir` 一个真实展开后的绝对路径
- 推荐单独开新窗口，避免污染原用户浏览器

本次有效命令逻辑:

```powershell
$chrome='C:\Program Files\Google\Chrome\Application\chrome.exe'
$profile=Join-Path $env:TEMP 'codex-chrome-profile'
Start-Process -FilePath $chrome -ArgumentList '--remote-debugging-port=9222','--remote-debugging-address=127.0.0.1',"--user-data-dir=$profile",'--new-window','https://www.upwork.com/nx/proposals/'
```

### 2. 验证 `9222` 是否已恢复

验证方式:

```text
http://127.0.0.1:9222/json/version
```

本次恢复成功后的返回包含:

- `Browser: Chrome/146...`
- `webSocketDebuggerUrl`

这说明 Chrome 的 CDP 调试端口恢复成功。

### 3. 恢复 `chrome-relay`

本次本地 relay 逻辑:

- `9223 -> 127.0.0.1:9222`

代理脚本文件:

- [chrome_cdp_proxy.js](D:\Codex\chrome_cdp_proxy.js)

本次实际验证:

- 即使日志文件没有立即刷新
- 只要 `http://172.31.208.1:9223/json/version` 能正常返回
- 就说明 relay 已经可用

## 五、本次踩到的坑

### 1. `%TEMP%` 不能直接当作可靠路径拼到参数里

问题:

- 直接写 `--user-data-dir=%TEMP%\\codex-chrome-profile`
- 在当前调用链里没有正确展开
- 导致 Chrome 启动但调试端口没正常起来

解决:

- 先在 PowerShell 中用 `Join-Path $env:TEMP ...` 生成真实路径
- 再传给 `--user-data-dir`

### 2. 不能只看 Chrome 进程存在

问题:

- Chrome 进程能启动，不代表 `9222` 已开启

解决:

- 必须用 `/json/version` 实测

### 3. 不能只恢复 relay，不恢复 Chrome

问题:

- 如果 `9222` 本身没起来，`9223` 只会继续报错

解决:

- 先恢复 Chrome 调试端口，再管 relay

### 4. 新开的 Chrome 是全新 profile

结果:

- 新会话会停在 `chrome://intro/`
- 不带原来的 Upwork 登录态

解决:

- 需要用户在这个新开的调试 Chrome 中重新登录 Upwork

## 六、恢复后的检查清单

以后每次恢复都按这 4 步确认:

1. `http://127.0.0.1:9222/json/version` 能打开
2. `http://172.31.208.1:9223/json/version` 能打开
3. `json/list` 里能看到目标页签
4. 浏览器里已经登录 Upwork

## 七、结论

以后遇到“重启后连不上 chrome-relay”，默认按下面思路处理:

1. 不先怀疑 Upwork
2. 先检查 `9222`
3. 再恢复 `9223`
4. 再确认页签
5. 最后让用户补登录

这套流程本次已经验证可用。
