# MSP Ticket Extension

一个 Chrome 浏览器插件 + Python 后端，用于快速将 MSP 工单信息提交至飞书多维表格，并通过 AWS Bedrock（Claude）自动生成任务名称、根因分析、解决步骤等结构化字段。

## 功能

- 在浏览器侧边栏填写工单信息（客户名称、问题描述、原因及措施）
- 后端调用 AWS Bedrock 自动生成结构化字段（任务名称、根因分析、解决步骤、Q&A）
- 自动匹配多维表格中的多选字段选项（服务类别、问题分类等）
- 通过邮箱自动查找飞书用户并关联创建人字段
- 写入飞书多维表格，一键完成工单记录

## 项目结构

```
├── backend/                # Python Flask 后端
│   ├── app.py              # 应用入口
│   ├── config.py           # 环境变量配置
│   ├── routes/
│   │   └── submit.py       # POST /api/submit 接口
│   ├── services/
│   │   ├── feishu_auth.py  # 飞书 access_token 获取与缓存
│   │   ├── feishu_user.py  # 通过邮箱查询飞书用户 open_id
│   │   ├── bitable.py      # 多维表格记录写入
│   │   ├── bitable_meta.py # 多选字段元数据加载
│   │   └── bedrock.py      # AWS Bedrock 字段生成
│   ├── utils/
│   │   └── format_record.py
│   ├── tests/              # 单元测试
│   ├── .env.example        # 环境变量示例
│   └── requirements.txt
└── extension/              # Chrome 插件
    ├── manifest.json
    ├── sidepanel.html/js/css  # 侧边栏界面
    ├── popup.html/js/css      # 弹窗界面（含配置）
    └── background.js
```

## 快速开始

### 1. 后端

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

复制并填写环境变量：

```bash
cp .env.example .env
```

`.env` 需填写以下字段：

| 变量 | 说明 |
|------|------|
| `FEISHU_APP_ID` | 飞书应用 App ID |
| `FEISHU_APP_SECRET` | 飞书应用 App Secret |
| `FEISHU_BITABLE_URL` | 多维表格完整 URL |
| `API_KEY` | 插件请求鉴权 Key（自定义） |
| `AWS_REGION` | AWS 区域，如 `us-east-1` |
| `BEDROCK_API_KEY` | AWS Bedrock API Key |
| `BEDROCK_MODEL_ID` | 模型 ID，如 `us.anthropic.claude-sonnet-4-6` |

启动服务：

```bash
python -m backend.app
```

### 2. Chrome 插件

1. 打开 Chrome，进入 `chrome://extensions/`
2. 开启右上角「开发者模式」
3. 点击「加载已解压的扩展程序」，选择 `extension/` 目录
4. 点击插件图标，在弹窗中填写后端地址和 API Key 后即可使用

## 飞书应用配置

需在[飞书开放平台](https://open.feishu.cn/)创建企业自建应用，并开通以下权限：

- `bitable:app` — 多维表格读写
- `contact:user.id:readonly` — 通过邮箱查询用户

## 运行测试

```bash
cd /path/to/project
pytest backend/tests/
```

## 环境要求

- Python 3.12+
- Chrome 浏览器
- 飞书企业自建应用
- AWS Bedrock 访问权限
