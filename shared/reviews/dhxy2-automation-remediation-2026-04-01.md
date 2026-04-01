# dhxy2-automation 整改记录（2026-04-01）

## 背景

本轮整改针对 2026-04-01 审查中确认的 4 个问题，并附带补了一项工具层收口：

1. smoke 测试硬编码工作区绝对路径
2. `button-calibration.json` 更新后未同步测试基线
3. 配置引用路径缺少边界校验
4. `Win32SendInputGateway.click()` 一次点击记了两条审计记录
5. 工具入口与 GUI 耦合、共享文档可读性不足

## 已完成整改

### 1. 测试路径去硬编码

新增统一测试路径入口：

- [tests/smoke/_paths.py](/D:/Codex/dhxy2-automation/tests/smoke/_paths.py)

处理方式：

- 统一通过 `PROJECT_ROOT / CONFIGS_ROOT / RESOURCES_ROOT / RUNS_ROOT` 取路径
- 不再在 smoke 测试里写死 `D:/Codex/dhxy2-automation`

后续要求：

- 新增 smoke 必须复用 `tests/smoke/_paths.py`
- 禁止重新引入工作区绝对路径硬编码

### 2. 按钮校准基线与测试同步

整改文件：

- [button-calibration.json](/D:/Codex/dhxy2-automation/configs/ui/button-calibration.json)
- [test_executor.py](/D:/Codex/dhxy2-automation/tests/smoke/test_executor.py)

处理方式：

- 配置真值与 smoke 断言保持同步
- 对布局字段与按钮点位增加一致性检查

后续要求：

- 配置真值改动必须与 smoke 断言同 patch 更新

### 3. 配置引用路径边界校验

新增公共解析工具：

- [config_refs.py](/D:/Codex/dhxy2-automation/src/app/config_refs.py)

整改文件：

- [profile_loader.py](/D:/Codex/dhxy2-automation/src/app/profile_loader.py)
- [bootstrap.py](/D:/Codex/dhxy2-automation/src/app/bootstrap.py)
- [test_profile_loader.py](/D:/Codex/dhxy2-automation/tests/smoke/test_profile_loader.py)
- [test_bootstrap.py](/D:/Codex/dhxy2-automation/tests/smoke/test_bootstrap.py)

处理方式：

- 角色知识引用只允许落在 `configs/knowledge`
- 角色配置引用只允许落在 `configs/characters`
- 越界路径直接抛 `ValueError`

后续要求：

- 所有配置驱动的文件引用都必须经过边界校验
- 不允许直接对相对路径 `resolve()` 后立刻读取

### 4. 点击审计重复记录

整改文件：

- [win32_input_gateway.py](/D:/Codex/dhxy2-automation/src/executor/win32_input_gateway.py)
- [test_win32_input_gateway.py](/D:/Codex/dhxy2-automation/tests/smoke/test_win32_input_gateway.py)

处理方式：

- 真实发送输入逻辑下沉到私有方法
- `click()` 和 `click_screen()` 各自只保留一条逻辑审计记录

后续要求：

- 一次逻辑动作只允许一条审计记录

### 5. 工具入口与文档收口

整改文件：

- [__init__.py](/D:/Codex/dhxy2-automation/src/app/__init__.py)
- [launch_manual_coordinate_probe.py](/D:/Codex/dhxy2-automation/scripts/launch_manual_coordinate_probe.py)
- [manual_probe_tool.py](/D:/Codex/dhxy2-automation/src/app/manual_probe_tool.py)
- [current-task-2026-04-01.md](/D:/Codex/shared/context/current-task-2026-04-01.md)
- [rules-index.md](/D:/Codex/shared/context/rules-index.md)

处理方式：

- GUI 工具不再挂到 `src.app` 顶层默认导出
- 启动脚本改为直接从 `src.app.manual_probe_tool` 导入
- 共享文档改写为可读 UTF-8 中文
- 新增编码防错记忆：
  - [encoding-guardrails-2026-04-01.md](/D:/Codex/shared/context/encoding-guardrails-2026-04-01.md)

后续要求：

- GUI 工具不应继续耦合核心包默认导出
- 乱码文件不能继续当有效交接材料

### 6. 启动容错与配置可移植性收口

整改文件：

- [bootstrap.py](/D:/Codex/dhxy2-automation/src/app/bootstrap.py)
- [battle-command-detection-candidates.json](/D:/Codex/dhxy2-automation/configs/ui/battle-command-detection-candidates.json)
- [test_bootstrap.py](/D:/Codex/dhxy2-automation/tests/smoke/test_bootstrap.py)
- [test_battle_command_candidates.py](/D:/Codex/dhxy2-automation/tests/smoke/test_battle_command_candidates.py)

处理方式：

- `_build_feedback_verifier()` 在缺少 `battle_button_semantics` 和 `button_calibration` 时不再误把当前目录当成语义文件加载
- 候选配置中的 `evidence_frame` 改为项目内相对路径，避免把本机工作区绝对路径带进正式配置
- 新增 smoke 覆盖启动容错和配置可移植性

后续要求：

- 所有可选配置都必须显式处理“未提供”分支，不能依赖 `Path()` 这类隐式默认值
- 正式配置文件禁止写入工作区绝对路径；证据、模板、资源路径统一使用项目根相对路径

## 统一执行要求

后续继续开发前，默认检查：

1. smoke 是否全绿
2. 是否重新引入绝对路径硬编码
3. 是否存在越界配置读取
4. 是否出现重复审计记录
5. 是否对高风险中文文件做了不安全回写
6. 正式配置里是否重新引入本机绝对路径

## 验证命令

```powershell
D:\Codex\dhxy2-automation\.venv\Scripts\python.exe -m unittest discover -s tests/smoke -t .
```
