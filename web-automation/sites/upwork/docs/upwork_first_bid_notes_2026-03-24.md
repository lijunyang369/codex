# Upwork 首次试投复盘

日期: 2026-03-24

## 目标

跑通一次完整的 Upwork 首投流程，包括:

- 调整个人定位
- 补基础资料
- 选择一条小单试投
- 完成 proposal 提交

本次已完成:

- 更新标题和简介
- 补 2 条 Portfolio
- 补技能标签
- 成功提交 1 条 proposal

目标职位:

- `Automate Invoice Generation and Email Notifications Using PHP Laravel`

## 本次主要卡点

### 1. 原始定位太泛

初始问题:

- 标题偏普通开发者: `Php|Laravel|JS|React|Mysql|Full stack`
- 简介缺少业务结果导向
- Portfolio 基本空白
- 容易吸引低价泛开发单, 不利于高匹配投标

处理:

- 改成电商/系统/自动化导向定位
- 强调 `Ecommerce CTO + PHP/Laravel + Shopify + API + Inventory Automation`
- 用跨境服装、供应链、自动化经验拉开与普通 PHP freelancer 的差距

### 2. Connects 不够

问题:

- 目标小单需要 `11 Connects`
- 账号初始仅有 `9 Connects`

处理:

- 补充购买 Connects
- 优先把 Connects 用在高匹配单, 不投明显低质单和过低预算单

### 3. 客户质量信息不透明

问题:

- 客户是新号
- 公开信息有限
- 很难单看列表判断是否值得投

核查结果:

- `Payment method verified`
- `Phone number verified`
- `Tbilisi, Georgia`
- `Finance & Accounting`
- `2-9 employees`
- 新客户, `0 reviews`
- 预算低, 需求文案大概率偏模板化

判断:

- 可以试投
- 但只能按 `MVP / Phase 1` 心态去接, 不能按完整系统报价理解

### 4. Proposal 页面表单控件非常难自动化

最核心难点:

- `How long will this project take?` 是自定义下拉组件
- 普通 DOM `click()` 能展开, 但无法稳定选中
- 即使 Vuex store 中 `estimatedDuration` 已写入, 页面仍可能显示 `Select a duration`
- 前端校验会继续报:
  - `Value is required and can't be empty.`

实际原因:

- Upwork 使用 Vue + 自定义 Air3 dropdown
- 页面不只校验 store 值, 还依赖组件内部状态
- 组件显示值来自 dropdown 内部 `selected/internalSelected`
- 仅改全局状态不够, 还要同步组件自身状态

最终处理办法:

- 先找到对应 Vue 组件链
- 写入:
  - store 的 `estimatedDuration`
  - 表单段组件的 `selected`
  - dropdown 组件的 `internalSelected`
  - dropdown 组件的 `lastSelected`
- 同步后页面才从 `Select a duration` 变为 `Less than 1 month`
- 表单错误随之消失

### 5. 提交不是一步, 中间有多层确认弹窗

实际提交链路:

1. 主表单 `Submit proposal`
2. 平台政策确认:
   - `I understand Upwork’s policies.`
3. Fixed-price 风险提醒:
   - `Yes, I understand.`
   - `Continue to submit`

问题:

- 每层都可能导致脚本误判为“还没提交”
- 最后一层点击后页面跳转, CDP 连接会断开

处理:

- 一层层确认 checkbox / button 状态
- 点击最终 `Continue`
- 页面跳转后重新连接新页面核验结果

### 6. 页面跳转后不能靠“感觉成功”判断

问题:

- 最终提交后页面跳回 `Best Matches`
- 单看跳转不一定能确认 proposal 是否真的进历史

处理:

- 重新打开 `My proposals`
- 核验是否出现:
  - `Submitted proposal (1)`
  - 对应职位名称

最终核验结果:

- proposal 已成功提交

## 本次有效做法

### 1. 先改定位, 再投单

比起先乱投, 先完成这些更值:

- 标题
- 简介
- Portfolio
- 技能标签

这样 proposal 更像同一套叙事, 不会出现“proposal 很 senior, 资料却像 junior”。

### 2. 第一单只拿来跑流程, 不追求利润最大化

首单目标不是利润, 而是:

- 跑通投标
- 跑通沟通
- 跑通合同/里程碑/收款
- 累积第一条反馈

### 3. Proposal 要主动收缩范围

这类预算低但描述大的单子, 最稳的打法是:

- 明确这是 `Phase 1`
- 先做最小可运行版本
- 后续复杂功能另开阶段

## 这次使用过的辅助文件

- [cdp_eval.js](D:\Codex\cdp_eval.js)
- [cross-border-ecommerce-operations.png](D:\Codex\upwork_assets\cross-border-ecommerce-operations.png)
- [shopify-inventory-sync-automation.png](D:\Codex\upwork_assets\shopify-inventory-sync-automation.png)

## 后续继续投单时的注意事项

- 只投高匹配单, 不投明显低端/低价/错位岗位
- 优先投:
  - `Laravel`
  - `Shopify`
  - `API integration`
  - `Inventory / ops automation`
- 新客户可以投, 但要先看:
  - 是否 `payment verified`
  - 是否最近活跃
  - 预算是否和工作量严重失配
- 每次提交后, 都到 `My proposals` 页做最终核验

## 当前结论

这次首投已经验证:

- 你的账号资料方向是对的
- 你能顺利完成投标全流程
- 后面的瓶颈不再是“不会投”, 而是“如何筛到更值得投的单”
