# Emergence World

AI 社会模拟平台 — 基于 Emergence World 研究项目的工程实现。

## 技术栈

| 层级 | 技术 |
|------|------|
| 语言 | Python 3.11+ |
| 包管理 | uv |
| Web 框架 | FastAPI + Uvicorn |
| 数据库 | SQLite (开发期) / PostgreSQL (生产) |
| ORM | SQLAlchemy 2.0 (async) |
| 迁移 | Alembic |
| LLM 接入 | OpenAI API 格式 (多模型统一调用) |
| 配置 | pydantic-settings |

## 快速开始

以下命令均在项目根目录 `Emergence-World/` 下执行。

### 1. 安装依赖

```bash
uv sync
```

### 2. 配置环境变量

```bash
cp emergence_world/.env.example emergence_world/.env
# 编辑 .env，填入 LLM API Key 等配置
```

### 3. 初始化数据库

```bash
uv run alembic -c emergence_world/alembic.ini upgrade head
```

### 4. 启动服务

```bash
uv run uvicorn emergence_world.main:app --host 127.0.0.1 --port 8000
```

### 5. 验证

```bash
curl http://127.0.0.1:8000/health
# → {"status":"ok"}

# Swagger UI
open http://127.0.0.1:8000/docs
```

## API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/health` | 健康检查 |
| GET | `/api/v1/world/state` | 世界状态 |
| GET | `/api/v1/agents` | 代理列表 |
| GET | `/api/v1/agents/{id}` | 代理详情 |
| GET | `/api/v1/landmarks` | 地标列表 |
| WS | `/ws/events` | 实时事件流 (WebSocket) |

## Alembic 数据库迁移

所有 alembic 命令需指定配置文件路径 `-c emergence_world/alembic.ini`。

```bash
# 查看当前迁移版本
uv run alembic -c emergence_world/alembic.ini current

# 自动生成迁移脚本（模型变更后）
uv run alembic -c emergence_world/alembic.ini revision --autogenerate -m "描述信息"

# 执行迁移
uv run alembic -c emergence_world/alembic.ini upgrade head

# 回滚一个版本
uv run alembic -c emergence_world/alembic.ini downgrade -1

# 查看迁移历史
uv run alembic -c emergence_world/alembic.ini history
```

## 项目结构

```
Emergence-World/
├── pyproject.toml                  # 项目配置和依赖
├── uv.lock                         # 依赖锁定文件
├── emergence_world/                # Python 包
│   ├── alembic.ini                 # Alembic 迁移配置
│   ├── .env.example                # 环境变量模板
│   ├── __init__.py
│   ├── main.py                     # FastAPI 应用入口
│   ├── config.py                   # 配置管理 (pydantic-settings)
│   ├── database.py                 # 数据库引擎和会话
│   ├── models/                     # ORM 数据模型
│   │   ├── base.py                 # 基础模型 (UUID + 时间戳)
│   │   ├── agent.py                # 代理模型
│   │   ├── landmark.py             # 地标模型
│   │   ├── memory.py               # 六层记忆模型
│   │   ├── economy.py              # 经济系统模型
│   │   ├── governance.py           # 治理系统模型
│   │   └── world.py                # 世界状态模型
│   ├── core/                       # 模拟引擎 (待实现)
│   ├── agents/                     # 代理管理 (待实现)
│   ├── tools/                      # 工具框架 (待实现)
│   ├── memory/                     # 记忆系统 (待实现)
│   ├── world/                      # 世界系统 (待实现)
│   ├── economy/                    # 经济系统 (待实现)
│   ├── governance/                 # 治理系统 (待实现)
│   ├── social/                     # 社交系统 (待实现)
│   ├── ui/                         # 终端输出 (待实现)
│   ├── alembic/                    # 数据库迁移脚本
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions/
│   └── tests/                      # 测试 (待实现)
├── docs/                           # 系统设计文档
├── agent_profiles/                 # 代理档案
├── landmarks/                      # 地标描述
├── data/                           # 宪法、宣言等数据
└── PRJ-001/                        # 需求分析文档
```
