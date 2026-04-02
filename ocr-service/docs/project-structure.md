# 项目结构

项目根目录：`D:\Codex\ocr-service`

## 顶层目录

- `docs`：项目文档、结构说明、项目规范
- `src`：正式源码
- `tests`：单元测试和集成测试

## 源码目录

源码根目录：`D:\Codex\ocr-service\src\ocr_service`

- `app`：HTTP 路由、依赖装配、应用入口
- `config`：配置解析和默认值定义
- `models`：请求模型、响应模型、内部契约模型
- `providers`：OCR 引擎适配层，只允许这里直接依赖 PaddleOCR 等 SDK
- `services`：与具体 provider 无关的业务编排、输入加载、预处理

## 目录职责约束

- `app` 只做接口暴露和依赖装配，不写 OCR 业务细节
- `providers` 只做引擎调用和结果转换，不处理 HTTP 和文件路径策略
- `services` 只做 provider 无关的编排，不直接 import OCR SDK
- `models` 不承载流程逻辑
- `tests` 以模块边界组织，不把测试夹杂进正式源码

## 运行期产物

以下内容不应进入正式源码树：
- `__pycache__`
- `*.egg-info`
- `build`
- `dist`
- 运行日志和临时识别产物

这些内容必须被 `.gitignore` 覆盖，必要时应及时清理。
