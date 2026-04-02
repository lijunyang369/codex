# OCR Service

`ocr-service` 是工作区级本机 OCR 服务，供 `D:\Codex` 内的其它项目通过 HTTP 调用。

## 能力

- 提供轻量 `/health` 存活检查
- 提供 `/readiness` provider 就绪检查
- 提供单文本读取和多行文本读取接口
- 支持文件路径和 base64 图片输入
- 默认只监听 `127.0.0.1`
- 默认只允许读取 `D:\Codex` 下的文件

## 安装

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -U pip
.venv\Scripts\python.exe -m pip install -e .
```

## 启动

```powershell
.venv\Scripts\python.exe -m uvicorn ocr_service.app.main:app --host 127.0.0.1 --port 18080
```

## 测试

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -t .
```

基础单元测试不依赖真实 Paddle 运行时。真实引擎验证应放到独立集成测试。

## Provider 切换

- 默认：`OCR_SERVICE_PROVIDER=null`
- Paddle：`OCR_SERVICE_PROVIDER=paddle`

示例：

```powershell
$env:OCR_SERVICE_PROVIDER='paddle'
.venv\Scripts\python.exe -m uvicorn ocr_service.app.main:app --host 127.0.0.1 --port 18080
```

## 允许读取路径边界

- 文件输入必须位于 `OCR_SERVICE_ALLOWED_ROOTS` 指定目录内
- 默认允许根目录：`D:\Codex`
- 多个根目录使用分号分隔

示例：

```powershell
$env:OCR_SERVICE_ALLOWED_ROOTS='D:\Codex;D:\Screenshots'
```

## 环境变量

- `OCR_SERVICE_HOST`
- `OCR_SERVICE_PORT`
- `OCR_SERVICE_PROVIDER`
- `OCR_SERVICE_ALLOWED_ROOTS`
- `OCR_SERVICE_REQUEST_TIMEOUT_MS`
- `OCR_SERVICE_PADDLE_LANGUAGE`
- `OCR_SERVICE_PADDLE_USE_ANGLE_CLS`
- `OCR_SERVICE_MAX_IMAGE_BYTES`
- `OCR_SERVICE_MAX_IMAGE_WIDTH`
- `OCR_SERVICE_MAX_IMAGE_HEIGHT`
- `OCR_SERVICE_MAX_IMAGE_PIXELS`

兼容说明：
- 旧前缀 `OCR_SIDECAR_*` 仍可读取
- 新增和更新配置统一使用 `OCR_SERVICE_*`
