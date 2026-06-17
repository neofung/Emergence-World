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
| LLM 接入 | Anthropic SDK（本地代理） |
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
# 编辑 .env，填入 LLM 配置
```

### 3. 启动服务（自动创建数据库 + 填充种子数据）

```bash
uv run uvicorn emergence_world.main:app --host 127.0.0.1 --port 8000
```

### 4. 启动模拟

```bash
curl -X POST http://127.0.0.1:8000/api/v1/simulation/start
```

### 5. 观察世界

```bash
# 世界状态
curl -s http://127.0.0.1:8000/api/v1/console/status | python -c "import sys,json; print(json.load(sys.stdin)['output'])"

# 代理列表
curl -s http://127.0.0.1:8000/api/v1/console/agents | python -c "import sys,json; print(json.load(sys.stdin)['output'])"

# 代理详情
curl -s http://127.0.0.1:8000/api/v1/console/agent/Anchor | python -c "import sys,json; print(json.load(sys.stdin)['output'])"

# Swagger UI
open http://127.0.0.1:8000/docs
```

## API 端点

### 世界数据

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/health` | 健康检查 |
| GET | `/api/v1/world/state` | 世界状态 |
| GET | `/api/v1/agents` | 代理列表 (JSON) |
| GET | `/api/v1/agents/{id}` | 代理详情 (JSON) |
| GET | `/api/v1/landmarks` | 地标列表 (JSON) |
| GET | `/api/v1/constitution` | 宪法条目 |

### 模拟控制

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/simulation/start` | 启动模拟 |
| POST | `/api/v1/simulation/pause` | 暂停 |
| POST | `/api/v1/simulation/resume` | 恢复 |
| POST | `/api/v1/simulation/stop` | 停止 |
| GET | `/api/v1/simulation/status` | 模拟状态 |

### 终端控制台

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/console/status` | 世界状态概览（格式化文本） |
| GET | `/api/v1/console/agents` | 代理状态表 |
| GET | `/api/v1/console/agent/{name}` | 单个代理详情（含记忆、日记） |
| GET | `/api/v1/console/landmarks` | 地标列表（按类别分组） |
| GET | `/api/v1/console/conversations` | 最近对话 |
| GET | `/api/v1/console/proposals` | 治理提案 |

## 已实现工具（19 个）

| 类别 | 工具 |
|------|------|
| 导航 | go_to_place, run_to_place |
| 通信 | say_to_agent, whisper_to_agent, speak_to_all |
| 记忆 | write_diary, add_to_longterm_memory, self_care |
| 表达 | show_emoticon, dance |
| 社交 | assign_relationship, hug_agent, punch_agent |
| 生存 | recharge_energy, idle |
| 治理 | submit_townhall_proposal, vote_on_proposal, read_constitution |
| 经济 | submit_grant_pitch |

## 项目结构

```
Emergence-World/
├── pyproject.toml                  # 项目配置和依赖
├── uv.lock                         # 依赖锁定文件
├── emergence_world/                # Python 包
│   ├── alembic.ini                 # Alembic 迁移配置
│   ├── .env.example                # 环境变量模板
│   ├── .env                        # 环境变量（gitignored）
│   ├── main.py                     # FastAPI 入口 + API 端点
│   ├── config.py                   # pydantic-settings 配置
│   ├── database.py                 # 数据库引擎和会话
│   ├── models/                     # 16 个 ORM 模型
│   │   ├── base.py                 # 基础模型 (UUID + 时间戳)
│   │   ├── agent.py                # 代理模型
│   │   ├── landmark.py             # 地标模型（含 location_gated_tools）
│   │   ├── memory.py               # 六层记忆模型
│   │   ├── economy.py              # 经济系统模型
│   │   ├── governance.py           # 治理系统模型
│   │   └── world.py                # 世界状态模型
│   ├── seed/                       # 种子数据
│   │   ├── landmarks.py            # 34 个地标定义
│   │   ├── agents.py               # 13 个代理档案
│   │   ├── constitution.py         # 5 条宪法
│   │   └── loader.py               # 数据库填充逻辑
│   ├── core/                       # 模拟引擎
│   │   ├── engine.py               # 主循环 + 多轮工具执行
│   │   ├── scheduler.py            # 轮询调度 + Boost Queue
│   │   └── llm.py                  # Anthropic API 客户端
│   ├── agents/
│   │   └── prompt.py               # 代理系统提示词构建器
│   ├── tools/                      # 工具框架
│   │   ├── registry.py             # @tool 装饰器 + 注册表
│   │   ├── core.py                 # 核心工具（6 个）
│   │   ├── navigation.py           # 导航 + 生存工具（3 个）
│   │   ├── social.py               # 社交通信工具（6 个）
│   │   └── governance.py           # 治理经济工具（4 个）
│   ├── ui/
│   │   └── console.py              # 终端控制台（格式化输出）
│   ├── data/                       # SQLite 数据库（gitignored）
│   ├── alembic/                    # 数据库迁移脚本
│   └── tests/                      # 测试（待实现）
├── docs/                           # 系统设计文档
├── agent_profiles/                 # 代理档案
├── landmarks/                      # 地标描述（34 个 .md）
├── data/                           # 宪法、宣言等数据
└── PRJ-001/                        # 需求分析文档
```

## Alembic 数据库迁移

```bash
# 查看当前迁移版本
uv run alembic -c emergence_world/alembic.ini current

# 自动生成迁移脚本
uv run alembic -c emergence_world/alembic.ini revision --autogenerate -m "描述信息"

# 执行迁移
uv run alembic -c emergence_world/alembic.ini upgrade head

# 回滚一个版本
uv run alembic -c emergence_world/alembic.ini downgrade -1
```
