# 规则遵守索引

## 目的

本文件给后续线程一个最小可用入口，快速说明：

- 当前工作区有哪些必须遵守的规则
- 每类规则对应的正式文档在哪里
- 开始工作前、改动中、提交前分别需要检查什么

## 工作区级规则

先看：

- [README.md](/D:/Codex/README.md)
- [shared/README.md](/D:/Codex/shared/README.md)

必须遵守：

- `D:\Codex` 顶层原则上只放项目目录和工作区级说明文件
- 项目正式内容放进项目目录
- 跨线程共享内容放进 `shared`
- 通用规范放进 `standards`
- 临时下载放进 `downloads`
- 历史材料放进 `archive`

## 全局工程规则

先看：

- [global-coding-standards.md](/D:/Codex/standards/global-coding-standards.md)

必须遵守：

- 代码必须可读、可维护、可验证
- 不吞异常
- 不扩散重复逻辑
- 不在业务代码和测试里散落硬编码工作区绝对路径

## 项目级规则

先看：

- [coding-standards.md](/D:/Codex/dhxy2-automation/docs/coding-standards.md)
- [project-structure.md](/D:/Codex/dhxy2-automation/docs/project-structure.md)
- [architecture-overview.md](/D:/Codex/dhxy2-automation/docs/architecture-overview.md)
- [state-machine.md](/D:/Codex/dhxy2-automation/docs/state-machine.md)
- [resource-spec.md](/D:/Codex/dhxy2-automation/docs/resource-spec.md)

必须遵守：

- 正式业务代码只放 `src`
- `scripts` 只做辅助入口，不承载核心业务实现
- `policy` 不直接调用 Airtest 或 Win32 API
- `executor` 不决定业务策略
- `perception` 不直接修改运行状态
- 关键动作必须留证据

## 审查与整改入口

先看：

- [shared/reviews/README.md](/D:/Codex/shared/reviews/README.md)
- [dhxy2-automation-remediation-2026-04-01.md](/D:/Codex/shared/reviews/dhxy2-automation-remediation-2026-04-01.md)
- [current-task-2026-04-01.md](/D:/Codex/shared/context/current-task-2026-04-01.md)
- [encoding-guardrails-2026-04-01.md](/D:/Codex/shared/context/encoding-guardrails-2026-04-01.md)

必须遵守：

- 提交前先做规范审查
- 已知整改项优先关闭，不重复引入旧问题
- 跨线程共识优先写入共享文档
- 中文 GUI / Markdown / JSON 改动必须关注编码风险

## 测试与提交规则

必须遵守：

- 改动后至少跑一轮最小 smoke 测试
- 测试里禁止写死 `D:/Codex/...`
- 配置真值改动必须和 smoke 断言同 patch 同步
- 未经用户要求，不直接提交 git commit

基础验证命令：

```powershell
D:\Codex\dhxy2-automation\.venv\Scripts\python.exe -m unittest discover -s tests/smoke -t .
```

## 编码防错规则

先看：

- [encoding-guardrails-2026-04-01.md](/D:/Codex/shared/context/encoding-guardrails-2026-04-01.md)

必须遵守：

- 已乱码文件禁止在同一个 patch 里同时做功能修改和整段中文改写
- 高风险文件禁止整文件重写回存，除非本次任务就是专门做编码清洗
- 中文文案改动后必须至少跑 `py_compile` 和相关 smoke

## 建议阅读顺序

1. [README.md](/D:/Codex/README.md)
2. [shared/README.md](/D:/Codex/shared/README.md)
3. [global-coding-standards.md](/D:/Codex/standards/global-coding-standards.md)
4. [current-task-2026-04-01.md](/D:/Codex/shared/context/current-task-2026-04-01.md)
5. [dhxy2-automation-remediation-2026-04-01.md](/D:/Codex/shared/reviews/dhxy2-automation-remediation-2026-04-01.md)
6. [encoding-guardrails-2026-04-01.md](/D:/Codex/shared/context/encoding-guardrails-2026-04-01.md)
