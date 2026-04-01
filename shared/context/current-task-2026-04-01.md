# 当前任务定义（2026-04-01）

## 目的

本文件用于说明 `dhxy2-automation` 当前阶段的主任务、边界、优先级和暂不处理项，供其他线程直接读取后继续协作。

## 当前主任务

当前主任务不是继续堆战斗脚本，而是先把两条基础线做稳：

1. 建立可被策略层正式消费的游戏知识基线
2. 建立可被执行层稳定复用的战斗 UI 识别与按钮语义确认基线

同时必须保持终态约束：

- 最终运行形态是“多开 + 多角色”
- 当前阶段的配置、上下文和策略读取方式，不能把“单窗口单角色”写死成未来难以拆开的结构

## 当前已完成

### 知识层

- 已建立 `docs/knowledge` 的资料分层结构
- 已形成第一批正式知识配置：
  - `configs/knowledge/character-system.json`
  - `configs/knowledge/pet-system.json`
- 已建立角色配置对知识配置的引用：
  - `configs/characters/mage-default.json`
- 已补充角色资料加载和实例绑定的 smoke 测试
- 已形成 `instance -> character_profile` 的正式绑定入口
- 已补充账号实例绑定 loader，窗口匹配与角色绑定开始围绕实例配置收口
- 已补充配置引用路径边界校验，避免越界读取

### 执行层 / UI 层

- 已有 `button_ref -> point` 的翻译能力
- 非战斗底栏已有一批已确认按钮
- 已能识别：
  - `battle_action_prompt`
  - `battle_skill_bar`
- `defend` 已做过真实点击确认
- 已新增战斗按钮语义配置与 verifier，点击确认开始基于前后模板变化，不再只看 `frame_changed`
- 已新增手工坐标探针工具：
  - `src/app/manual_probe_tool.py`
  - `scripts/launch_manual_coordinate_probe.py`

### 规范与测试

- smoke 测试中的工作区绝对路径硬编码已清理
- 按钮校准基线与 smoke 断言已同步
- 当前 smoke 结果为全绿

## 当前未完成

### A. 知识层正式接入

- 仍需把知识配置从“可加载”推进到“策略可消费”
- 仍需把人物、召唤兽等字段正式注入策略上下文
- 仍需继续验证实例级角色绑定在多开场景下不会退化为全局默认角色

### B. 战斗按钮语义确认

- `item`、`pet` 等按钮虽然进入了语义配置，但还没有形成稳定的正向确认链路
- 仍需建立“点击后出现明确 UI 反馈”的确认规则
- 仍需把按钮从“坐标候选”推进到“可验证语义按钮”

### C. 主流程接入

- 真正的复杂执行链还没有完整接入主流程
- 当前战斗脚本仍是最小闭环入口，不是完整策略执行器
- 复杂动作不应继续堆在 `scripts` 目录
- 仍需保持 `instance_id -> window_session -> character_profile -> runtime_context` 这条链可扩展到多开

## 当前优先级

### P1

已完成并默认不再重复处理：

- 临时文件治理
- 配置引用边界校验
- 测试绝对路径治理

### P2

当前最高优先级：

- 把知识层从“样例可加载”推进到“策略可消费”
- 明确角色/召唤兽的正式 schema
- 继续保持实例级角色绑定，不回退为全局默认角色读取

### P3

- 完成战斗按钮语义确认流程
- 明确每个按钮点击后的反馈信号
- 再把这些按钮逐步接回动作执行测试

## 当前明确不做

- 不直接扩展大量战斗动作脚本
- 不在按钮语义未确认前把候选按钮写成 `confirmed`
- 不绕过知识层直接写复杂职业策略
- 不让 `scripts` 目录继续承载越来越多核心业务逻辑

## 执行约束

后续线程必须同时遵守：

1. `D:\Codex\shared\context\rules-index.md`
2. `D:\Codex\standards\global-coding-standards.md`
3. `D:\Codex\dhxy2-automation\docs\coding-standards.md`
4. `D:\Codex\shared\reviews\dhxy2-automation-remediation-2026-04-01.md`

额外强调：

- 战斗按钮确认不能只看 `frame_changed`
- 重要共识优先落盘，不依赖聊天上下文传递
- 当前实现虽然按单实例推进，但结构必须保留多开扩展空间

## 建议下一步

1. 先验证手工坐标探针工具能否正常启动和回填
2. 用手工回填方式重建非战斗底栏与战斗栏的真实坐标
3. 将回填结果同步回正式配置
4. 再回到“战斗输入为何未被 UI 接受”的专项排查
