# 实现计划：飞书多维表格 Chrome 插件

## 概述

按照"Chrome 插件前端 → 后端服务 → 飞书 API 集成"的顺序逐步实现。每个阶段均包含核心功能实现与对应的测试任务，确保增量验证。使用 Python（Python 3.10+ + Flask）作为后端语言，Chrome 插件采用原生 HTML/CSS/JavaScript（Manifest V3）。

## 任务

- [x] 1. 初始化项目结构
  - 创建 `extension/` 目录，添加 `manifest.json`（Manifest V3）、`popup.html`、`popup.js`、`popup.css` 空文件
  - 创建 `backend/` 目录，初始化 `requirements.txt`，列出依赖：`flask`、`python-dotenv`、`requests`
  - 安装测试依赖：`pytest`、`hypothesis`
  - 创建 `backend/` 子目录结构：`routes/`、`services/`、`utils/`
  - 创建 `backend/.env.example`，列出所有必需环境变量：`FEISHU_APP_ID`、`FEISHU_APP_SECRET`、`FEISHU_APP_TOKEN`、`FEISHU_TABLE_ID`、`API_KEY`、`PORT`
  - 创建 `backend/.gitignore`，排除 `.env` 和 `__pycache__/`、`*.pyc`
  - _需求：4.1、4.3、6.1_

- [x] 2. 实现后端工具函数与配置模块
  - [x] 2.1 实现 `backend/config.py`
    - 使用 `python-dotenv` 读取环境变量，导出 `feishu`（app_id、app_secret、app_token、table_id）和 `server`（port、api_key）配置对象（可使用 dataclass 或字典）
    - 若必需环境变量缺失，启动时抛出明确错误
    - _需求：4.3、6.1_

  - [x] 2.2 实现 `backend/utils/format_record.py`
    - 实现 `format_task_detail(user_issue, issue_cause, issue_solution)` 函数
    - 输出格式严格为：`f"【用户问题】{user_issue}\n【问题原因】{issue_cause}\n【问题解决办法】{issue_solution}"`
    - _需求：4.4_

  - [ ]* 2.3 为 `format_task_detail` 编写属性测试
    - **属性 2：Task_Detail 拼接格式不变性**
    - 使用 `hypothesis` 生成任意 `user_issue`、`issue_cause`、`issue_solution` 字符串（含特殊字符、多行文本、Unicode）
    - 断言输出严格等于指定格式模板
    - 标签：`Feature: feishu-bitable-chrome-extension, Property 2: Task_Detail 拼接格式不变性`
    - _需求：4.4_

- [x] 3. 实现飞书认证服务
  - [x] 3.1 实现 `backend/services/feishu_auth.py`
    - 实现 `get_access_token()` 函数，使用模块级字典缓存 `token` 和 `expires_at`（Unix 秒时间戳）
    - 若当前时间 < `expires_at - 300`（提前 5 分钟），直接返回缓存 token
    - 否则使用 `requests` 库调用飞书 `POST /open-apis/auth/v3/tenant_access_token/internal`，传入 `app_id` 和 `app_secret`，设置 timeout 参数
    - 成功后更新缓存（`token`、`expires_at = time.time() + expire - 300`）
    - 失败时抛出带 `AUTH_ERROR` 标识的异常
    - _需求：4.1_

  - [ ]* 3.2 为 `feishu_auth.py` 编写单元测试
    - 使用 `pytest` + `unittest.mock` mock `requests.post`，测试缓存命中、缓存过期触发刷新、飞书 API 失败时错误传播
    - _需求：4.1_

- [x] 4. 实现飞书 Bitable 写入服务
  - [x] 4.1 实现 `backend/services/bitable.py`
    - 实现 `create_record(fields)` 函数
    - 调用 `get_access_token()` 获取 token
    - 使用 `requests` 库向 `POST /open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records` 发送请求，设置 timeout=8 秒
    - 请求头携带 `Authorization: Bearer {token}`，请求体为 `{ "fields": fields }`
    - 飞书返回 `code != 0` 时抛出带 `FEISHU_API_ERROR` 标识的异常（附带飞书错误信息）
    - _需求：4.2_

  - [ ]* 4.2 为 `bitable.py` 编写属性测试
    - **属性 3：飞书记录字段映射正确性**
    - 使用 `hypothesis` 生成合法的 `SubmitRequest`（四个非空字段）
    - 使用 `unittest.mock` mock `feishu_auth.get_access_token` 和 `requests.post`，捕获传入飞书 API 的 `fields` 对象
    - 断言五个字段均正确映射（含 `format_task_detail` 计算的 `任务详情描述`）
    - 标签：`Feature: feishu-bitable-chrome-extension, Property 3: 飞书记录字段映射正确性`
    - _需求：3.1、4.2、4.4_

- [x] 5. 实现后端 API 路由与鉴权中间件
  - [x] 5.1 实现 API Key 鉴权装饰器
  - [x] 5.3 实现 `backend/routes/submit.py` Flask Blueprint
  - [x] 5.4 实现 `backend/app.py` Flask 应用入口
    - 在 `backend/app.py` 或独立文件中实现：使用 Flask 装饰器或 `before_request` 钩子检查请求头 `x-api-key` 是否与 `config.server.api_key` 匹配
    - 不匹配（缺失、为空、值不符）时返回 HTTP 401 JSON 响应 `{ "success": false, "error": "UNAUTHORIZED" }`
    - _需求：6.3_

  - [ ]* 5.2 为鉴权装饰器编写属性测试
    - **属性 4：未授权请求被拒绝**
    - 使用 `hypothesis` 生成不匹配配置 API Key 的随机字符串、空值、缺失请求头
    - 使用 Flask test client 断言后端返回 401，且 mock 的飞书 API 未被调用
    - 标签：`Feature: feishu-bitable-chrome-extension, Property 4: 未授权请求被拒绝`
    - _需求：6.3_

  - [ ] 5.3 实现 `backend/routes/submit.py` Flask Blueprint
    - 实现 `POST /api/submit` 路由处理器
    - 验证请求体包含 `creator`、`userIssue`、`issueCause`、`issueSolution` 四个非空字段，缺失时返回 400 `VALIDATION_ERROR`
    - 调用 `format_task_detail` 拼接 `task_detail`
    - 构造 `fields` 对象（五个字段映射）并调用 `create_record(fields)`
    - 成功时返回 200 `{ "success": true, "recordId": "..." }`
    - 捕获 `AUTH_ERROR` 返回 502，捕获 `FEISHU_API_ERROR` 返回 502，其他异常返回 500
    - _需求：3.1、4.1、4.2、4.3、4.4_

  - [ ] 5.4 实现 `backend/app.py` Flask 应用入口
    - 创建 Flask 应用实例，注册 JSON 请求解析
    - 注册鉴权钩子（应用于 `/api/*` 路由）
    - 注册 `routes/submit.py` Blueprint
    - 监听 `config.server.port`（默认 5000）
    - _需求：4.1、6.3_

- [ ] 6. 检查点 — 后端功能验证
  - 确保所有后端测试通过，运行 `pytest`（在 `backend/` 目录下）
  - 确认 `format_task_detail`、`feishu_auth`、`bitable`、路由及鉴权装饰器的测试均绿色通过
  - 如有问题，请向用户说明。

- [ ] 7. 实现 Chrome 插件前端
  - [ ] 7.1 实现 `extension/popup.html`
    - 创建包含四个必填字段的表单：`creator`（`<input type="text">`）、`userIssue`、`issueCause`、`issueSolution`（均为 `<textarea>`）
    - 每个字段配有可见标签（"创建人"、"用户问题"、"问题原因"、"问题解决办法"）
    - 添加 `id="submitBtn"` 的提交按钮，文字为"提交"
    - 添加用于展示加载状态的元素（`id="loadingIndicator"`，默认隐藏）
    - 添加用于展示成功/失败消息的元素（`id="statusMessage"`，默认隐藏）
    - 每个字段下方添加错误提示元素（`class="error-msg"`，默认隐藏）
    - 引入 `popup.css` 和 `popup.js`
    - _需求：1.1、1.2、1.3_

  - [ ] 7.2 实现 `extension/popup.css`
    - 设置弹窗宽度（建议 360px）、内边距、字体
    - 为标签、输入框、文本域、提交按钮设置基础样式
    - 为错误提示文字设置红色样式（`.error-msg`）
    - 为加载状态和状态消息设置可见性样式
    - _需求：1.1、1.2_

  - [ ] 7.3 实现 `extension/popup.js` — 表单验证函数
    - 实现 `validateForm(formData)` 函数：接收包含四个字段的对象，对每个字段执行 `.trim()` 后判断是否为空
    - 返回 `{ valid: boolean, errors: { [fieldId]: string } }`
    - 所有字段非空时返回 `{ valid: true, errors: {} }`；任意字段为空时返回 `{ valid: false, errors: { fieldId: "此字段为必填项" } }`
    - _需求：2.1、2.2、2.3_

  - [ ]* 7.4 为 `validateForm` 编写属性测试
    - **属性 1：表单验证的完备性**
    - 使用 `fast-check` 生成四字段数据（拒绝路径：至少一个字段为空字符串或纯空白；通过路径：四个非空白字符串）
    - 断言：空白字段时返回 `valid: false` 且 `errors` 包含对应字段；全填写时返回 `valid: true`
    - 标签：`Feature: feishu-bitable-chrome-extension, Property 1: 表单验证的完备性`
    - _需求：2.1、2.2、2.3_

  - [ ] 7.5 实现 `extension/popup.js` — UI 状态管理与提交流程
    - 实现辅助函数：`showLoading()`、`hideLoading()`、`showSuccess(message)`、`showError(message)`、`clearForm()`、`showFieldErrors(errors)`、`clearFieldErrors()`
    - 实现 `submitForm(formData)` 异步函数：使用 `fetch` 向后端 `POST /api/submit` 发送 JSON 请求，携带 `x-api-key` 请求头，设置 10 秒 `AbortController` 超时
    - 监听提交按钮点击事件：调用 `validateForm` → 若失败展示字段错误并终止；若通过则禁用按钮、展示加载状态、调用 `submitForm`
    - 成功响应（HTTP 200）：调用 `showSuccess`、`clearForm`
    - 失败响应（HTTP 4xx/5xx）：解析响应体 `message` 字段，调用 `showError`
    - 网络异常（fetch 抛出）：调用 `showError("网络错误，请检查网络连接")`
    - 超时（AbortError）：调用 `showError("请求超时，请稍后重试")`
    - 请求完成后（无论成功失败）：恢复提交按钮
    - _需求：1.4、3.1、3.2、3.3、3.4、5.1、5.2、5.3、5.4_

  - [ ] 7.6 完善 `extension/manifest.json`
    - 填写完整配置：`manifest_version: 3`、`name`、`version`、`action.default_popup`
    - 配置 `host_permissions`，包含后端服务地址（开发环境：`http://localhost:3000/*`）
    - _需求：3.1_

- [ ] 8. 最终检查点 — 全量测试通过
  - 在 `backend/` 目录下运行 `pytest`，确保所有单元测试和属性测试通过
  - 检查 `extension/` 目录下的前端属性测试（若配置了独立测试运行器）
  - 确保所有测试通过，如有问题，请向用户说明。

## 备注

- 标有 `*` 的子任务为可选项，可在快速 MVP 阶段跳过
- 每个任务均引用具体需求条款，确保可追溯性
- 属性测试使用 `hypothesis` 库，每个属性最少运行 100 次迭代
- 后端 API Key 通过请求头 `x-api-key` 传递，前端需在 `popup.js` 中配置（可通过 `manifest.json` 中的 `host_permissions` 或独立配置文件管理）
- 飞书多维表格字段名称需与实际表格中的字段名完全一致（区分大小写）
- 生产部署时需将 `manifest.json` 中的 `host_permissions` 替换为实际后端服务地址
