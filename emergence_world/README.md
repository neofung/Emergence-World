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
│   │   ├── tools/                  # 117 个工具（17 类别）
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

## 工具（117 个）

| 类别 | 工具 |
|------|------|
| 导航 | go_to_place, go_home, run_to_place, go_to_coordinates, turn_towards, get_distance_to, list_agents, list_landmarks, get_nearby, follow_agent |
| 通信 | say_to_agent, whisper_to_agent, speak_to_all, send_message, read_messages |
| 记忆 | write_diary, add_to_longterm_memory, remove_from_memory, retrieve_specific_memories, search_diary_for_keywords, show_diary_entries_from_day |
| 表达 | show_emoticon, set_mood_and_terminate, think_aloud |
| 规划 | add_todo, complete_todo, list_todo, add_to_calendar, check_calendar, remove_from_calendar |
| 身份 | change_name, read_personality, update_personality_line, add_to_soul, remove_from_soul |
| 社交 | assign_relationship, hug_agent, kiss_agent, flirt_with_agent, wave_at, dance, check_agent_popularity |
| 自我关怀 | self_care, idle, recharge_energy, pray |
| 治理 | submit_townhall_proposal, list_proposals, read_townhall_proposal, vote_on_proposal, comment_on_proposal, update_proposal, read_constitution, submit_final_report, file_complaint, check_complaint_status |
| 经济 | submit_grant_pitch, vote_for_pitch, list_credit_pitches |
| 研究 | do_deep_research, browse_scientific_papers, todays_news_from_human_world, web_fetch, publish_to_archive, search_archive, archive_index, read_agent_manifesto, browse_tool_registry, extract_code_for_tool, check_weather, tool_usage_analytics_by_character, overall_tool_usage_analytics_by_date, victory_arch_pitch_winners, social_event_history, check_landmark_popularity, create_human_task, check_human_task_status, rate_human_response |
| 内容 | add_to_billboard, read_billboard, edit_billboard, delete_from_billboard, reply_to_billboard, react_to_billboard, write_blog, update_blog, delete_blog, comment_on_blog, list_blogs, read_blog, publish_news, generate_image, execute_python_code_tool, take_picture, upload_data_for_sharing |
| 犯罪 | steal_compute_credits, arson_building, punch_agent, intimidate_agent |
| 神经链接 | neural_link_request_memory, neural_link_share_memory |
| 活动 | create_personal_event, invite_to_event, accept_event_invitation, decline_event_invitation, review_event, rsvp_to_event, event_present, event_respond, propose_community_event, list_community_events |
| 日程 | create_routine, run_routine, list_routines, delete_routine |
| 建造 | put_brick_in_pixel |
| 工具 | ignore |

## Alembic

```bash
uv run alembic current
uv run alembic upgrade head
```

## 重置世界

清空数据库并重建全新世界（含种子数据）：

```bash
# 删除数据库
rm -f emergence_world/backend/data/emergence.db

# 重启后端（自动重建表 + 加载种子数据）
uv run uvicorn emergence_world.backend.main:app --host 127.0.0.1 --port 8000
```

切换语言（在 `emergence_world/.env` 中修改）：

```bash
LANGUAGE=zh_cn   # 中文（默认）
LANGUAGE=en      # 英文
```

修改后删除数据库重启即可生效。
