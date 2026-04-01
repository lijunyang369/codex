# dhxy2-automation 整改记录（2026-04-01）

## 背景

本轮整改针对 2026-04-01 审查中确认的 3 个问题，并附带修正了 1 个执行层审计缺陷：

1. smoke 测试硬编码工作区绝对路径
2. `button-calibration.json` 更新后未同步测试基线
3. 配置引用路径缺少边界校验
4. 附带修正：`Win32SendInputGateway.click()` 会为一次点击记录两条操作

## 已完成整改

### 1. 测试路径去硬编码

新增统一测试路径入口：

- [tests/smoke/_paths.py](D:\Codex\dhxy2-automation\tests\smoke\_paths.py)

处理方式：

- 统一通过 `PROJECT_ROOT / CONFIGS_ROOT / RESOURCES_ROOT / RUNS_ROOT` 取项目路径
- 不再在 smoke 测试里写死 `D:/Codex/dhxy2-automation`
- 同类用法已同步收口到现有和新增 smoke 测试

协作要求：

- 后续新增测试必须复用 `tests/smoke/_paths.py`
- 禁止再次引入工作区绝对路径

### 2. 按钮校准基线与 smoke 同步

整改文件：

- [button-calibration.json](D:\Codex\dhxy2-automation\configs\ui\button-calibration.json)
- [test_executor.py](D:\Codex\dhxy2-automation\tests\smoke\test_executor.py)

处理方式：

- 将 `nonbattle_toolbar.baseline_y` 和 `layout.y` 与已确认按钮点位统一为 `802`
- 将 smoke 断言同步为新的已确认坐标
- 补充对 `baseline_y` 和 `layout.y` 的一致性校验，避免后续再出现“点位改了但布局基线没改”的半更新状态

协作要求：

- 配置真值变更必须与 smoke 断言同 patch 更新
- 布局字段和按钮点位字段必须保持语义一致

### 3. 配置引用路径边界校验

新增公共解析工具：

- [config_refs.py](D:\Codex\dhxy2-automation\src\app\config_refs.py)

整改文件：

- [profile_loader.py](D:\Codex\dhxy2-automation\src\app\profile_loader.py)
- [bootstrap.py](D:\Codex\dhxy2-automation\src\app\bootstrap.py)
- [test_profile_loader.py](D:\Codex\dhxy2-automation\tests\smoke\test_profile_loader.py)
- [test_bootstrap.py](D:\Codex\dhxy2-automation\tests\smoke\test_bootstrap.py)

处理方式：

- 角色知识引用只允许落在 `configs/knowledge`
- 账号绑定的角色配置引用只允许落在 `configs/characters`
- 对越界相对路径抛出显式 `ValueError`
- 增加越界路径单测，防止回归

协作要求：

- 所有配置驱动的文件引用都必须经过边界校验
- 不允许直接对相对路径 `resolve()` 后立即读文件

### 4. 附带修正：点击审计双记录

整改文件：

- [win32_input_gateway.py](D:\Codex\dhxy2-automation\src\executor\win32_input_gateway.py)
- [test_win32_input_gateway.py](D:\Codex\dhxy2-automation\tests\smoke\test_win32_input_gateway.py)

处理方式：

- 将真实发送输入动作下沉到私有 `_click_screen()`
- `click()` 仅记录客户端坐标操作
- `click_screen()` 仅记录屏幕坐标操作

协作要求：

- `operations` 必须保持“一次逻辑动作对应一条审计记录”
- 若需要复用底层发送逻辑，应拆分公共私有方法，不要复用带审计副作用的公共接口

### 5. 补充收口：探针入口去耦合与文档可读性

整改文件：

- [src/app/__init__.py](D:\Codex\dhxy2-automation\src\app\__init__.py)
- [scripts/launch_manual_coordinate_probe.py](D:\Codex\dhxy2-automation\scripts\launch_manual_coordinate_probe.py)
- [manual_probe_tool.py](D:\Codex\dhxy2-automation\src\app\manual_probe_tool.py)
- [current-task-2026-04-01.md](D:\Codex\shared\context\current-task-2026-04-01.md)
- [rules-index.md](D:\Codex\shared\context\rules-index.md)

处理方式：

- 将手工探针 GUI 入口从 `src.app` 顶层导出中移除，避免核心包导入时强耦合 `tkinter` 和 `ImageTk`
- 启动脚本改为直接从 `src.app.manual_probe_tool` 导入探针入口
- 手工探针工具的操作界面文案全部重写为可读中文
- 共享上下文和规则索引文档重写为可读中文，供其他线程直接使用

协作要求：

- GUI 工具不应挂到核心包的默认导出路径上
- 共享文档必须保持可读，不能将乱码文件当作有效交接材料

## 本轮未纳入整改

以下问题已知，但不在本轮 3 个指定 finding 的整改范围内：

- `src.app` 顶层包导出仍耦合手工探针 GUI 入口

后续若继续做审批，建议优先复核该项是否需要从 `src.app.__init__` 移出。

## 验证要求

本轮整改完成后，至少运行：

```powershell
D:\Codex\dhxy2-automation\.venv\Scripts\python.exe -m unittest discover -s tests/smoke -t .
```

审批前必须确认：

1. smoke 全绿
2. 无新增绝对路径硬编码
3. 无新的配置越界读取入口
