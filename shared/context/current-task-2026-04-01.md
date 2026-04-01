# 当前任务定义（2026-04-01）

## 目的

本文件用于说明 `dhxy2-automation` 当前阶段的主任务、边界、优先级和暂不处理项，供后续线程直接读取后继续协作。

## 当前主任务

当前主任务不是继续堆战斗脚本，而是先把两条基础线做稳：

1. 建立可被策略层正式消费的游戏知识基线
2. 建立可被执行层稳定复用的战斗 UI 识别与按钮语义确认基线

同时必须保持结构约束：

- 最终运行形态是“多开 + 多角色”
- 当前阶段虽然按单实例推进，但配置、上下文和策略读取方式不能写死成“单窗口单角色”

## 当前已完成

### 知识层

- 已建立 `docs/knowledge` 的资料分层结构
- 已形成两份正式知识配置：
  - `configs/knowledge/character-system.json`
  - `configs/knowledge/pet-system.json`
- 角色配置已接入知识引用：
  - `configs/characters/mage-default.json`
- 已补充角色资料加载、实例绑定和相关 smoke 测试
- 已补充配置引用边界校验，避免越界读取

### 执行层 / UI 层

- 已有 `button_ref -> point` 的执行翻译能力
- 非战斗底栏已有一批按钮完成校对
- 角色战斗指令、宠物战斗指令已完成一轮人工坐标校对
- 角色战斗指令不再包含“宝宝”
- 宠物战斗指令当前正式入口为：
  - `法术`
  - `道具`
  - `防御`
  - `保护`
- 已建立战斗按钮语义配置和反馈 verifier
- 手工坐标探针工具已可用于：
  - 读取正式配置
  - 修改坐标并回写
  - 标记状态
  - 查看截图和日志
- 识别链已拆成独立模块：
  - `battle_scene`
  - `battle_round`
  - `battle_action_prompt`
  - `battle_skill_bar`
  - `battle_target_select`
  - `battle_settlement`
- GUI 已新增“识别模块测试”页，可按模块单独检测
- `battle_scene` 已改为使用右下角“自动”按钮模板，当前实机已确认可识别
- `battle_round` 已独立为单独模块，支持在 GUI 中调截图区域和保存回合数字模板

### 规范与测试

- smoke 测试中的工作区绝对路径硬编码已清理
- 配置真值与 smoke 断言已同步
- 当前 smoke 基线可用
- 已新增编码防错记忆：
  - `shared/context/encoding-guardrails-2026-04-01.md`

## 当前进行中

### A. 战斗回合数字识别稳定化

- 当前 `1`、`3` 回合识别已正确
- `2`、`4`、`5` 回合仍需补真实数字模板
- 已提供 GUI 保存回合数字模板能力，下一步应补齐真实模板而不是继续依赖字体兜底

### B. 战斗按钮语义确认

- 指令坐标校对已完成
- 但“点击后真实 UI 反馈确认”仍未完全覆盖
- `item`、`spell`、`protect` 等动作仍需继续补稳定确认链路

### C. 知识层正式接入策略

- 目前知识配置已可加载
- 但还未完全推进到“策略层正式消费”

## 当前未完成

### P1

- 补齐 `battle_round` 的真实数字模板
- 让回合识别在实机战斗中稳定覆盖 1~5 及后续常见回合

### P2

- 完成角色 / 宠物战斗指令的点击后反馈确认
- 把已校对指令正式接回策略链和执行链

### P3

- 将知识层字段正式注入策略上下文
- 保持 `instance_id -> window_session -> character_profile -> runtime_context` 可扩展到多开

## 当前任务看板

### 已完成

- 非战斗底栏按钮校对
- 角色战斗指令坐标校对
- 宠物战斗指令坐标校对
- 战斗场景识别模块独立化
- 战斗场景模板改为“自动”按钮
- 识别模块测试 GUI 和截图区域回写能力
- 回合数字模板保存入口

### 进行中

- 战斗回合数字模板补齐
- 战斗按钮语义确认
- 知识层正式接入策略

### 待开始

- 宠物法术 / 道具面板语义确认
- 目标选择和结算识别模板补齐
- 更完整的主流程接入

## 当前明确不做

- 不继续盲目扩大量战斗脚本
- 不在按钮语义未确认前把候选按钮写成 `confirmed`
- 不绕过知识层直接写复杂职业策略
- 不让 `scripts` 目录继续承载越来越多核心业务逻辑

## 执行约束

后续线程必须同时遵守：

1. `D:\Codex\shared\context\rules-index.md`
2. `D:\Codex\standards\global-coding-standards.md`
3. `D:\Codex\dhxy2-automation\docs\coding-standards.md`
4. `D:\Codex\shared\reviews\dhxy2-automation-remediation-2026-04-01.md`
5. `D:\Codex\shared\context\encoding-guardrails-2026-04-01.md`

额外强调：

- 战斗按钮确认不能只看 `frame_changed`
- 重要共识优先写入共享文档
- 中文 GUI / Markdown 文件修改必须先评估编码风险

## 建议下一步

1. 在 GUI 里补齐 `2 / 4 / 5` 回合的真实数字模板
2. 用真实模板重新验证 `battle_round` 模块
3. 再继续推进战斗按钮点击后的真实反馈确认
