# Emergence World

AI 社会模拟平台 — 基于 Emergence World 研究项目的工程实现。

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Python 3.11+ / uv / FastAPI / SQLAlchemy 2.0 / SQLite |
| 前端 | React 19 + TypeScript + Vite + Canvas 2D |
| LLM | Anthropic SDK（本地代理） |
| 迁移 | Alembic |

## 快速开始

```bash
# 安装依赖
uv sync
cd emergence_world/frontend && npm install

# 配置环境变量
cp emergence_world/.env.example emergence_world/.env

# 启动后端
uv run uvicorn emergence_world.backend.main:app --host 127.0.0.1 --port 8000

# 启动前端（新终端）
cd emergence_world/frontend && npm run dev
# 打开 http://localhost:5173
```

## 项目结构

```
Emergence-World/
├── pyproject.toml
├── emergence_world/
│   ├── README.md
│   │
│   ├── backend/                    # 后端（Python）
│   │   ├── main.py                 # FastAPI 入口 + API
│   │   ├── config.py               # 配置
│   │   ├── database.py             # 数据库引擎
│   │   ├── models/                 # 16 个 ORM 模型
│   │   ├── seed/                   # 种子数据
│   │   ├── core/                   # 模拟引擎
│   │   │   ├── engine.py           # 主循环 + 工具执行
│   │   │   ├── scheduler.py        # 调度器
│   │   │   ├── llm.py              # Anthropic 客户端
│   │   │   └── awi.py              # AWI 指标
│   │   ├── agents/prompt.py        # 提示词构建器
│   │   ├── tools/                  # 28 个工具
│   │   ├── ui/console.py           # 终端控制台
│   │   ├── alembic/                # 数据库迁移
│   │   ├── data/                   # SQLite（gitignored）
│   │   └── tests/
│   │
│   └── frontend/                   # 前端（React）
│       ├── package.json
│       └── src/
│           ├── WorldCanvas.tsx     # Canvas 地图
│           ├── Sidebar.tsx         # 代理列表 + 对话
│           └── ControlPanel.tsx    # 模拟控制
│
├── docs/                           # 系统设计文档
├── agent_profiles/                 # 代理档案
├── landmarks/                      # 地标描述
└── PRJ-001/                        # 需求分析
```

## API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/health` | 健康检查 |
| GET | `/api/v1/agents` | 代理列表 |
| GET | `/api/v1/landmarks` | 地标列表 |
| GET | `/api/v1/constitution` | 宪法 |
| GET | `/api/v1/metrics/awi` | AWI 指标 |
| POST | `/api/v1/simulation/start` | 启动模拟 |
| POST | `/api/v1/simulation/pause` | 暂停 |
| POST | `/api/v1/simulation/resume` | 恢复 |
| POST | `/api/v1/simulation/stop` | 停止 |
| GET | `/api/v1/console/*` | 终端控制台视图 |

## 工具（28 个）

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
| 内容 | add_to_billboard, read_billboard, write_blog, publish_news, do_deep_research, browse_scientific_papers |
| 犯罪 | steal_compute_credits, arson_building, intimidate_agent |

## Alembic

```bash
uv run alembic -c emergence_world/alembic.ini current
uv run alembic -c emergence_world/alembic.ini upgrade head
```
