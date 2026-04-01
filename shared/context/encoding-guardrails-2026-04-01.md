# 编码防错记忆（2026-04-01）

## 背景

本项目已经多次出现中文乱码问题。根因不是单一文件，而是：

- 在已经存在编码污染的文件上继续直接编辑
- 使用会整文件重写的方式保存，导致原有乱码进一步扩散
- 在功能修改时顺手改中文文案，没有把“编码清洗”和“功能改动”拆开

这条记忆从现在开始按硬规则执行。

## 硬规则

1. 任何包含中文的 Python / Markdown / JSON 文件，修改前必须先判断是否已经存在乱码。
2. 如果文件已经乱码，禁止在同一个 patch 里同时做“功能修改 + 文案修改 + 整体重写”。
3. 如果文件已经乱码，优先策略是：
   - 先做最小功能改动，避免整文件重写
   - 或先单独做一轮编码清洗，再做功能修改
4. 禁止用会整文件重编码的方式回写高风险文件，尤其是：
   - `src/app/manual_probe_tool.py`
   - `shared/context/*.md`
   - `docs/thread-handoff-*.md`
5. 任何中文 GUI 文案改动后，必须至少执行：
   - `py_compile`
   - 相关 smoke 测试
6. 共享上下文文件必须保持 UTF-8 可读；乱码文件不能继续当有效交接材料使用。

## 高风险文件

- `D:\Codex\dhxy2-automation\src\app\manual_probe_tool.py`
- `D:\Codex\shared\context\current-task-2026-04-01.md`
- `D:\Codex\shared\context\rules-index.md`
- `D:\Codex\dhxy2-automation\docs\thread-handoff-2026-03-31.md`
- `D:\Codex\shared\reviews\dhxy2-automation-remediation-2026-04-01.md`

## 默认处理策略

后续只要任务涉及中文文案、GUI、共享文档，默认先执行下面顺序：

1. 先确认文件是否已乱码
2. 已乱码则避免整文件回写
3. 功能改动和编码清洗分开做
4. 改完立即做 `py_compile` / smoke

## 本次问题的直接结论

这次重复犯错的直接原因是：在 `manual_probe_tool.py` 已存在乱码污染的前提下，又做了界面结构调整，期间触发了整段中文字符串的连锁损坏。

后续不再把这种文件当普通 UTF-8 干净文件处理。
