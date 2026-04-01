# 大话西游2 自动化交接（2026-03-31）

## 当前任务
为《大话西游2》战斗自动化测试打通并固化**真实点击执行能力**，并将可用点击点位沉淀到配置与执行层。

## 当前阶段
阶段 2：真实输入与 UI 校准阶段（已完成一半）

已完成：
- 提权环境下真实点击可驱动角色移动（输入链路打通）。
- 非战斗底部工具栏已建立网格化参数。
- 部分按钮已确认命中并写入校准配置。
- 执行层支持按 `button_ref` 解析点位，不再依赖裸坐标。

未完成：
- 非战斗工具栏剩余按钮确认（`candidate` -> `confirmed`）。
- 战斗栏按钮校准（防御/道具/宝宝）。
- 真实输入网关完整接入主执行流程。

## 已确认执行原则
1. 只要涉及真实点击，默认走提权环境。
2. 遇到有规律 UI，优先网格化/参数化，不优先逐点扫描。

## 当前按钮网格（非战斗底栏）
- `start_x = 870`
- `step_x = 40`
- `y = 792`

序列：
- 千秋册：`[870, 792]`
- 宝宝：`[910, 792]`
- 道具：`[950, 792]`
- 组队：`[990, 792]`
- 攻击：`[1030, 792]`
- 元宝：`[1070, 792]`
- 商会：`[1110, 792]`
- 技能：`[1150, 792]`
- 坐骑：`[1190, 792]`
- 任务：`[1230, 792]`
- 好友：`[1270, 792]`
- 帮派：`[1310, 792]`
- 系统：`[1350, 792]`

## 已确认按钮
- `nonbattle_toolbar.pet_panel`
- `nonbattle_toolbar.bag_panel`
- `nonbattle_toolbar.team_panel`
- `nonbattle_toolbar.skill_panel`
- `nonbattle_toolbar.mount_panel`
- `nonbattle_toolbar.task_panel`
- `nonbattle_toolbar.system_panel`

说明：
- 校准文件里仍有 `candidate` 状态项，下一线程继续按截图回归确认。

## 关键文件
- 校准配置：[configs/ui/button-calibration.json](/D:/Codex/dhxy2-automation/configs/ui/button-calibration.json)
- 本地环境配置：[configs/env/local.json](/D:/Codex/dhxy2-automation/configs/env/local.json)
- 执行器按钮解析：[src/executor/button_calibration.py](/D:/Codex/dhxy2-automation/src/executor/button_calibration.py)
- 翻译器（支持 `CLICK_UI_BUTTON`）：[src/executor/translator.py](/D:/Codex/dhxy2-automation/src/executor/translator.py)
- 应用装配（加载按钮校准）：[src/app/bootstrap.py](/D:/Codex/dhxy2-automation/src/app/bootstrap.py)
- 单点探针：[scripts/click_probe.py](/D:/Codex/dhxy2-automation/scripts/click_probe.py)
- 热点扫描：[scripts/scan_probe.py](/D:/Codex/dhxy2-automation/scripts/scan_probe.py)
- 按钮扫描包装：[scripts/run_button_scan.py](/D:/Codex/dhxy2-automation/scripts/run_button_scan.py)

## 新线程建议起步命令
### 1) 运行测试（本地）
```powershell
$env:PYTHONPATH='D:\Codex\dhxy2-automation'
D:\Codex\dhxy2-automation\.venv\Scripts\python.exe -m unittest discover -s D:\Codex\dhxy2-automation\tests -p test_*.py
```

### 2) 按按钮名做热点扫描（提权）
```powershell
$env:PYTHONPATH='D:\Codex\dhxy2-automation'
D:\Codex\dhxy2-automation\.venv\Scripts\python.exe D:\Codex\dhxy2-automation\scripts\run_button_scan.py --group nonbattle_toolbar --button friend_panel --label toolbar-friend-scan --offsets '0:0,-10:0,10:0,0:-8,0:8' --delay 1.0
```

### 3) 按点位做单次点击验证（提权）
```powershell
$env:PYTHONPATH='D:\Codex\dhxy2-automation'
D:\Codex\dhxy2-automation\.venv\Scripts\python.exe D:\Codex\dhxy2-automation\scripts\click_probe.py --client-x 1270 --client-y 792 --label toolbar-friend-confirm --delay 1.0
```

## 下一线程待办（按优先级）
1. 完成非战斗底栏剩余按钮确认：`好友`、`帮派`、`千秋册`、`元宝`、`商会`、`攻击`。
2. 校准战斗栏按钮：`防御`、`道具`、`宝宝`。
3. 在策略层增加一个简单动作：`CLICK_UI_BUTTON`（按 `button_ref` 执行）。
4. 将战斗场景 `scenario` 中裸坐标逐步替换为 `button_ref`。

## 代码基线
- 分支：`codex/dhxy2-battle-framework`
- 最近提交：`cdc6fe0`（button calibration + live click probes）

## 交接必读规范（新增）
后续线程开始前，必须先阅读并遵守以下规范：

1. 全局规范：`D:\Codex\standards\global-coding-standards.md`
2. 项目补充规范：`D:\Codex\dhxy2-automation\docs\coding-standards.md`
3. 架构与分层：`D:\Codex\dhxy2-automation\docs\architecture-overview.md`
4. 运行链路：`D:\Codex\dhxy2-automation\docs\runtime-flow.md`

执行要求：
- 改动说明必须显式标注“是否符合全局规范 + 项目规范”。
- 任何新增入口脚本不得直接依赖私有属性（如 `_context`、`_window_session`）。
- 业务动作与策略输出优先 `button_ref` 配置化，不新增裸坐标散落。
- 战斗回合操作必须遵守时限：单回合可操作窗口按 30 秒预算设计，优先快速动作路径（避免扫描式验证阻塞回合）。
