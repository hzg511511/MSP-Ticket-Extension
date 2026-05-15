# 需求文档

## 简介

本功能为一个 Chrome 浏览器插件，允许用户在浏览器中快速填写问题信息并提交至飞书多维表格（Bitable）。用户填写创建人、用户问题、问题原因及问题解决办法后，点击提交按钮，插件后端将这些信息整合后写入指定的飞书多维表格记录。飞书认证信息（app_id、app_secret）及表格配置（表格 ID、数据表 ID 等）硬编码在后端服务中，不通过插件界面暴露或输入。

## 词汇表

- **插件（Extension）**：Chrome 浏览器扩展程序，提供用户交互界面（Popup）。
- **后端服务（Backend_Service）**：插件通过 HTTP 请求调用的服务端程序，负责与飞书 API 通信。
- **飞书多维表格（Bitable）**：飞书提供的在线协作数据库产品，支持通过 API 写入记录。
- **记录（Record）**：多维表格中的一行数据。
- **创建人（Creator）**：用户在插件中填写的姓名或标识，对应多维表格中的"创建人"字段。
- **用户问题（User_Issue）**：用户在插件中填写的问题描述，对应多维表格中的独立字段。
- **问题原因（Issue_Cause）**：用户在插件中填写的问题根因，对应多维表格中的独立字段。
- **问题解决办法（Issue_Solution）**：用户在插件中填写的解决方案，对应多维表格中的独立字段。
- **任务详情描述（Task_Detail）**：多维表格中的组合字段，内容由后端将"用户问题 + 问题原因 + 问题解决办法"拼接生成。
- **提交按钮（Submit_Button）**：插件界面上触发数据提交的按钮。
- **飞书访问令牌（Access_Token）**：后端通过 app_id 和 app_secret 向飞书 API 换取的临时凭证。

---

## 需求

### 需求 1：插件界面展示与输入

**用户故事：** 作为一名用户，我希望在 Chrome 插件弹窗中看到清晰的表单，以便快速填写问题相关信息。

#### 验收标准

1. THE Extension SHALL 在用户点击插件图标时展示一个包含以下输入字段的弹窗表单：创建人、用户问题、问题原因、问题解决办法。
2. THE Extension SHALL 为每个输入字段提供可见的标签（Label），标签文字分别为"创建人"、"用户问题"、"问题原因"、"问题解决办法"。
3. THE Extension SHALL 在表单底部展示一个"提交"按钮（Submit_Button）。
4. WHILE 用户在输入字段中输入内容，THE Extension SHALL 实时保留用户输入，不自动清除。

---

### 需求 2：表单输入验证

**用户故事：** 作为一名用户，我希望在提交前得到明确的错误提示，以便确保所有必填信息已填写完整。

#### 验收标准

1. WHEN 用户点击 Submit_Button 且任意必填字段（创建人、用户问题、问题原因、问题解决办法）为空，THE Extension SHALL 阻止提交并在对应字段旁展示错误提示信息。
2. WHEN 用户点击 Submit_Button 且所有必填字段均已填写，THE Extension SHALL 允许提交流程继续执行。
3. THE Extension SHALL 将创建人、用户问题、问题原因、问题解决办法均视为必填字段。

---

### 需求 3：数据提交触发

**用户故事：** 作为一名用户，我希望只有在我主动点击提交按钮后数据才会被发送，以便我有机会在提交前检查和修改内容。

#### 验收标准

1. WHEN 用户点击 Submit_Button 且表单验证通过，THE Extension SHALL 向 Backend_Service 发送一次包含所有表单字段数据的 HTTP 请求。
2. WHILE 提交请求正在处理中，THE Extension SHALL 禁用 Submit_Button 以防止重复提交。
3. WHILE 提交请求正在处理中，THE Extension SHALL 在界面上展示加载状态提示。
4. IF 用户未点击 Submit_Button，THEN THE Extension SHALL 不向 Backend_Service 发送任何数据。

---

### 需求 4：后端数据处理与飞书 API 集成

**用户故事：** 作为系统管理员，我希望后端服务自动将表单数据整合并写入飞书多维表格，以便数据能够结构化存储。

#### 验收标准

1. WHEN Backend_Service 收到来自 Extension 的提交请求，THE Backend_Service SHALL 使用硬编码的 app_id 和 app_secret 向飞书 API 获取 Access_Token。
2. WHEN Backend_Service 成功获取 Access_Token，THE Backend_Service SHALL 向飞书多维表格 API 写入一条新 Record，包含以下字段映射：
   - 多维表格"创建人"字段 ← Creator
   - 多维表格"用户问题"字段 ← User_Issue
   - 多维表格"问题原因"字段 ← Issue_Cause
   - 多维表格"问题解决办法"字段 ← Issue_Solution
   - 多维表格"任务详情描述"字段 ← 由 User_Issue、Issue_Cause、Issue_Solution 按固定格式拼接生成的字符串
3. THE Backend_Service SHALL 使用硬编码的表格 ID 和数据表 ID 确定写入目标，不接受来自 Extension 的表格配置参数。
4. THE Backend_Service SHALL 按照以下格式拼接 Task_Detail 字段内容：
   ```
   【用户问题】{User_Issue}
   【问题原因】{Issue_Cause}
   【问题解决办法】{Issue_Solution}
   ```

---

### 需求 5：提交结果反馈

**用户故事：** 作为一名用户，我希望在提交后立即收到成功或失败的反馈，以便了解操作结果。

#### 验收标准

1. WHEN Backend_Service 成功将 Record 写入飞书多维表格，THE Extension SHALL 在界面上展示提交成功的提示信息。
2. WHEN Backend_Service 返回错误响应，THE Extension SHALL 在界面上展示提交失败的提示信息，并说明失败原因（如网络错误、服务器错误）。
3. WHEN 提交成功后，THE Extension SHALL 清空所有表单输入字段，以便用户进行下一次填写。
4. IF Backend_Service 在 10 秒内未返回响应，THEN THE Extension SHALL 中止请求并展示超时错误提示。

---

### 需求 6：后端安全与配置隔离

**用户故事：** 作为系统管理员，我希望飞书认证信息和表格配置仅存在于后端，以便防止敏感信息泄露。

#### 验收标准

1. THE Backend_Service SHALL 将 app_id、app_secret、表格 ID 及数据表 ID 以硬编码或服务端环境变量的方式存储，不通过任何 API 接口对外暴露。
2. THE Extension SHALL 不在插件代码、界面或网络请求中包含 app_id、app_secret、表格 ID 或数据表 ID。
3. THE Backend_Service SHALL 仅接受来自已授权来源的提交请求（如通过固定 API Key 或同源策略进行基础鉴权）。
