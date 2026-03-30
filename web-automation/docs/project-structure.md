# Project Structure

采用轻量结构：

- 通用能力放到 `common/`
- 站点特殊能力放到 `sites/<site>/`

## Current Structure

- `common/docs/`
  - Chrome relay / CDP 相关说明
- `common/scripts/`
  - 通用 CDP / relay 脚本
- `common/runs/`
  - 通用运行日志
- `sites/upwork/docs/`
  - 投标、SOP、复盘、草稿
- `sites/upwork/scripts/`
  - Upwork 专用自动化脚本
- `sites/upwork/resources/`
  - Upwork 用到的资源文件
- `sites/boss/docs/`
  - Boss 简历优化文档
- `sites/boss/scripts/`
  - Boss 专用自动化脚本

## Rule

新增站点时：

1. 在 `sites/` 下新建站点目录
2. 该站点的文档、脚本、资源只放到自己的目录
3. 只有跨站点复用的能力，才放到 `common/`

## Common Constraints

- Shared rules are documented in common/docs/common-constraints.md`r

