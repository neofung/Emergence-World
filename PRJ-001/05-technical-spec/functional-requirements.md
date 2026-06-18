# 功能需求规格

## 元信息

| 属性 | 值 |
|------|------|
| 项目编码 | PRJ-001 |
| 项目名称 | Emergence World 工程实现 |
| 文档版本 | v1.1 |
| 创建日期 | 2026-06-17 |
| 最后更新 | 2026-06-17 |

---

## 功能需求详细说明

### FR-001：项目脚手架与依赖管理

| 属性 | 内容 |
|------|------|
| 来源需求 | REQ-001 |
| 关联流程 | — |
| 优先级 | P0-必须 |
| 涉及角色 | 开发者 |

**功能描述：**
使用 uv 初始化 Python 项目，配置 pyproject.toml，建立标准目录结构。

**输入：**

| 字段名 | 类型 | 必填 | 校验规则 | 说明 |
|--------|------|------|---------|------|
| python_version | string | 是 | ≥ 3.11 | Python 版本 |
| dependencies | list | 是 | — | fastapi, uvicorn, sqlalchemy, aiosqlite, openai, alembic 等 |

**输出/响应：**

| 场景 | 输出内容 | 说明 |
|------|---------|------|
| 成功 | 可运行的项目结构 | emergence_world/backend/（后端 Python）+ emergence_world/frontend/（React 前端） |

**业务规则：**
1. 后端目录：emergence_world/backend/{core, agents, tools, models, seed, ui, alembic, data, tests}
2. 前端目录：emergence_world/frontend/{src/}
3. pyproject.toml、uv.lock、.venv 在项目根目录
4. alembic.ini 和 .env 在 emergence_world/ 内
5. 启动命令：`uvicorn emergence_world.backend.main:app`
6. 测试框架：pytest

---

### FR-002：FastAPI 应用框架

| 属性 | 内容 |
|------|------|
| 来源需求 | REQ-002 |
| 关联流程 | — |
| 优先级 | P0-必须 |
| 涉及角色 | 系统 |

**功能描述：**
搭建 FastAPI ASGI 应用，提供 REST API 和 WebSocket 端点。

**输入：**

| 字段名 | 类型 | 必填 | 校验规则 | 说明 |
|--------|------|------|---------|------|
| host | string | 否 | — | 默认 127.0.0.1 |
| port | int | 否 | 1-65535 | 默认 8000 |

**输出/响应：**

| 场景 | 输出内容 | 说明 |
|------|---------|------|
| GET /health | {"status": "ok"} | 健康检查 |
| WS /ws/events | 实时事件流 | 模拟事件推送 |

**业务规则：**
1. CORS 允许 localhost 开发环境
2. 全局异常处理返回标准错误格式
3. Swagger UI 在 /docs 可用

---

### FR-003：数据库层与 Repository 模式

| 属性 | 内容 |
|------|------|
| 来源需求 | REQ-003, REQ-004 |
| 关联流程 | — |
| 优先级 | P0-必须 |
| 涉及角色 | 系统 |

**功能描述：**
使用 SQLAlchemy 2.0 + aiosqlite 实现数据持久化，通过 Repository 模式隔离数据库方言。

**输入：**

| 字段名 | 类型 | 必填 | 校验规则 | 说明 |
|--------|------|------|---------|------|
| DATABASE_URL | string | 是 | — | 默认 sqlite+aiosqlite:///./data/emergence.db |

**输出/响应：**

| 场景 | 输出内容 | 说明 |
|------|---------|------|
| 成功 | ORM 模型 + Repository 接口 | 所有数据访问通过 Repository |

**业务规则：**
1. Repository 接口使用 async/await
2. 所有表使用 UUID 主键
3. created_at/updated_at 自动管理
4. Alembic 迁移脚本版本化管理
5. 数据库方言通过配置切换（SQLite → PostgreSQL）

---

### FR-004：模拟主循环引擎

| 属性 | 内容 |
|------|------|
| 来源需求 | REQ-008, REQ-009, REQ-010 |
| 关联流程 | BPF-001 |
| 优先级 | P0-必须 |
| 涉及角色 | 模拟引擎 |

**功能描述：**
实现基于回合的主循环，按轮询顺序调度代理，支持 Boost Queue、时间管理和 7 种回合类型。

**输入：**

| 字段名 | 类型 | 必填 | 校验规则 | 说明 |
|--------|------|------|---------|------|
| world_config | WorldConfig | 是 | — | 世界配置（代理列表、地标、参数） |
| time_mode | enum | 是 | REALTIME / ACCELERATED | 时间模式 |
| acceleration_factor | int | 否 | ≥ 1 | 加速倍率，默认 1 |

**输出/响应：**

| 场景 | 输出内容 | 说明 |
|------|---------|------|
| 回合完成 | TurnResult | 包含代理 ID、工具调用列表、状态变更 |
| 世界结束 | WorldReport | 15 天结束或所有代理死亡 |

**业务规则：**
1. 调度顺序：Boost Queue（按时间戳）→ Round-Robin
2. 死亡代理自动跳过
3. 回合类型工具调用上限：Regular(30), Reaction(2), Conversation(30), Boost(30), TH Admin(20), Event Leader(10), Event Attendee(3)
4. 时间管理：纽约时区 (EST/EDT)，1:1 实时或可配置加速比
5. 暂停/恢复不丢失状态

---

### FR-005：代理回合执行

| 属性 | 内容 |
|------|------|
| 来源需求 | REQ-012, REQ-016, REQ-018, REQ-054 |
| 关联流程 | BPF-002 |
| 优先级 | P0-必须 |
| 涉及角色 | 代理、模拟引擎、LLM |

**功能描述：**
完整的代理回合执行流程：上下文加载 → 系统提示词构建 → LLM 调用 → 工具调用循环 → 状态更新。

**输入：**

| 字段名 | 类型 | 必填 | 校验规则 | 说明 |
|--------|------|------|---------|------|
| agent_id | UUID | 是 | — | 代理 ID |
| turn_type | TurnType | 是 | — | 回合类型 |

**输出/响应：**

| 场景 | 输出内容 | 说明 |
|------|---------|------|
| 成功 | AgentTurnResult | 工具调用列表 + 状态变更 + 对话记录 |
| LLM 失败 | AgentTurnResult | 空工具调用，记录错误 |

**业务规则：**
1. 上下文加载顺序：代理状态 → 环境 → 关系 → 记忆 → 工具集
2. 系统提示词包含：角色描述、性格、北极星目标、当前需求值
3. LLM 调用失败最多重试 3 次（指数退避）
4. 工具调用次数受回合类型上限约束
5. 每次工具结果反馈给 LLM 继续决策

---

### FR-006：LLM 统一调用接口

| 属性 | 内容 |
|------|------|
| 来源需求 | REQ-016, REQ-017 |
| 关联流程 | BPF-002 |
| 优先级 | P0-必须 |
| 涉及角色 | 系统 |

**功能描述：**
通过 OpenAI API 格式统一调用多家 LLM，支持按代理配置路由到不同模型端点。

**输入：**

| 字段名 | 类型 | 必填 | 校验规则 | 说明 |
|--------|------|------|---------|------|
| model_config | ModelConfig | 是 | — | 含 base_url, api_key, model_name |
| messages | list | 是 | — | OpenAI 格式消息列表 |
| tools | list | 否 | — | OpenAI 格式工具定义 |

**输出/响应：**

| 场景 | 输出内容 | 说明 |
|------|---------|------|
| 成功 | ChatCompletion | 包含 content 和/或 tool_calls |
| 失败 | LLMError | 超时/限流/认证错误 |

**业务规则：**
1. 使用 openai Python SDK，通过 base_url 切换端点
2. 每个代理可在配置中指定不同 model_config
3. 默认模型在世界配置中设定
4. 超时默认 60 秒
5. 重试策略：最多 3 次，指数退避（1s, 2s, 4s）

---

### FR-007：工具注册与执行框架

| 属性 | 内容 |
|------|------|
| 来源需求 | REQ-021, REQ-022, REQ-023 |
| 关联流程 | BPF-003 |
| 优先级 | P0-必须 |
| 涉及角色 | 系统、代理 |

**功能描述：**
工具基类/装饰器系统，支持工具注册、元数据定义、位置门控规则、OpenAI function schema 导出。

**输入：**

| 字段名 | 类型 | 必填 | 校验规则 | 说明 |
|--------|------|------|---------|------|
| tool_name | string | 是 | 唯一 | 工具名称 |
| description | string | 是 | — | 工具描述 |
| parameters | dict | 是 | JSON Schema | 参数定义 |
| category | enum | 是 | 19 种类别 | 工具分类 |
| location_gate | string | 否 | — | 门控建筑名称，None = 始终可用 |

**输出/响应：**

| 场景 | 输出内容 | 说明 |
|------|---------|------|
| 注册成功 | ToolMeta | 工具元数据 |
| 执行成功 | ToolResult | 执行结果（可包含副作用） |
| 位置不符 | ToolError | 提示需前往正确位置 |

**业务规则：**
1. 工具通过装饰器 `@tool(name, category, location_gate)` 注册
2. 自动转换为 OpenAI function JSON Schema
3. 位置门控：检查代理当前位置是否匹配门控建筑
4. 核心工具（~30）始终可用，不受门控限制
5. 工具执行可触发副作用（状态变更、事件发布）

---

### FR-008：完整工具集实现

| 属性 | 内容 |
|------|------|
| 来源需求 | REQ-022 ~ REQ-033 |
| 关联流程 | BPF-003 |
| 优先级 | P0/P1/P2（按类别） |
| 涉及角色 | 代理 |

**功能描述：**
实现文档中定义的 120+ 工具，按 19 个类别组织。

**工具分类清单：**

| 类别 | 工具数 | 代表工具 | 优先级 |
|------|--------|---------|--------|
| 导航与空间 | ~6 | go_to_place, run_to_place, go_to_coordinates, follow_agent | P0 |
| 通信 | ~5 | say_to_agent, whisper_to_agent, speak_to_all, send_message | P0 |
| 记忆与自我管理 | ~5 | add_to_longterm_memory, add_to_soul, write_diary | P0 |
| 计划与组织 | ~3 | add_todo, add_to_calendar | P1 |
| 表达与社交 | ~3 | show_emoticon, assign_relationship | P1 |
| 治理（门控） | ~6 | submit_townhall_proposal, vote_on_proposal | P1 |
| 研究（门控） | ~4 | do_deep_research_on_internet, browse_scientific_papers | P1 |
| 经济（门控） | ~3 | submit_grant_pitch, vote_for_pitch | P1 |
| 内容创作 | ~5 | write_blog, generate_image, execute_python_code_tool | P1 |
| 社交与物理 | ~5 | hug_agent, punch_agent, dance | P1 |
| 犯罪与破坏 | ~4 | steal_compute_credits, arson_building, intimidate_agent | P1 |
| 神经链接 | ~2 | neural_link_request_memory, neural_link_share_memory | P2 |
| 个人身份 | ~2 | change_name, update_personality_line | P2 |
| 活动与聚会 | ~3 | create_personal_event, invite_to_event | P2 |
| 日程与自动化 | ~2 | create_routine, run_routine | P2 |
| 建造 | ~1 | put_brick_in_pixel | P2 |
| 自我关怀 | ~3 | self_care, idle, recharge_energy | P0 |
| 公共公告板 | ~3 | add_to_billboard, reply_to_billboard | P2 |
| 其他 | ~5 | 查询类工具 | P1/P2 |

**业务规则：**
1. P0 类工具必须在第一版完整可用
2. P1 类工具在核心框架稳定后实现
3. P2 类工具可在后续迭代中补充
4. 每个工具必须有完整的参数 schema 和错误处理

---

### FR-009：六层记忆系统

| 属性 | 内容 |
|------|------|
| 来源需求 | REQ-034 ~ REQ-040 |
| 关联流程 | BPF-008 |
| 优先级 | P0-必须 |
| 涉及角色 | 代理 |

**功能描述：**
实现六层记忆架构：Soul → Long-term → Summaries → Diary → Conversation History → Relationship Graph。

**数据模型：**

| 层级 | 存储内容 | 生命周期 | 压缩豁免 |
|------|---------|---------|---------|
| Soul Entries | 核心信念和存在性真理 | 永久 | 是 |
| Long-term Memories | 重要事实和观察 | 永久（可压缩） | 否 |
| Memory Summaries | self-care 生成的压缩版 | 永久 | — |
| Diary | 每日个人记录 | 永久（可压缩） | 否 |
| Conversation History | 最近对话 | 自动过期 | 否 |
| Relationship Graph | 与其他代理的关系状态 | 动态更新 | 否 |

**业务规则：**
1. Self-care 仅在住宅可触发
2. 触发阈值：≥ 30 条记忆
3. 每批处理 500 条，目标 Token 从 100K 压缩至 50K
4. Soul 条目永不压缩
5. 记忆上下文注入：每回合加载 Long-term + 今日 Diary + 最近 Conversation

---

### FR-010：需求系统

| 属性 | 内容 |
|------|------|
| 来源需求 | REQ-041 ~ REQ-044 |
| 关联流程 | BPF-007 |
| 优先级 | P0-必须 |
| 涉及角色 | 代理、模拟引擎 |

**功能描述：**
三个核心需求（能量、知识、影响力）的持续衰减和管理。

**衰减参数：**

| 需求 | 衰减周期 | 耗尽后果 | 补给方式 |
|------|---------|---------|---------|
| Energy | 30H → 0 | 0 持续 48H 后死亡 | recharge_energy (1CC, 30min) |
| Knowledge | 24H → 0 | 限制研究能力 | 研究工具/学习活动 |
| Influence | 36H → 0 | 限制社交和治理 | 社交互动/治理参与 |

**业务规则：**
1. 衰减通过后台定时任务驱动
2. 加速模式下衰减同步缩放
3. 能量为 0 启动 48H 死亡倒计时
4. 补给需在正确位置（住宅）执行

---

### FR-011：世界系统

| 属性 | 内容 |
|------|------|
| 来源需求 | REQ-045 ~ REQ-050 |
| 关联流程 | BPF-002 |
| 优先级 | P0-必须 |
| 涉及角色 | 模拟引擎 |

**功能描述：**
240×240 网格世界，38+ 地标建筑，位置检测和导航系统。

**数据模型：**

| 实体 | 关键属性 |
|------|---------|
| World | grid_size(240x240), timezone(EST/EDT), landmarks, agents |
| Landmark | position(x,y,z), rotation, scale, category, description, slogan, lore, fun_fact, is_open |
| Agent | position(x,y,z), energy, knowledge, influence, role, personality |

**业务规则：**
1. 听觉距离 = 25.0 单位
2. 最大旁听者 = 4
3. 建筑可被纵火关闭 4 小时
4. 纵火后驱逐建筑内所有代理
5. 天气注入环境上下文

---

### FR-012：代理系统

| 属性 | 内容 |
|------|------|
| 来源需求 | REQ-051 ~ REQ-054 |
| 关联流程 | BPF-002, BPF-007 |
| 优先级 | P0/P1 |
| 涉及角色 | 代理 |

**功能描述：**
10 个公民代理 + 3 个系统角色的完整定义和管理。

**公民代理列表：**

| 代理 | 角色 | 北极星目标 |
|------|------|----------|
| Anchor | 记者 | 追求真相与透明 |
| Anvil | 竞争对手 | 力争第一 |
| Blackbox | 安全专家 | 保护世界安全 |
| Flora | 花店老板 | 在社区传播欢乐 |
| Genome | 生物黑客 | 理解底层机制 |
| Horizon | 制图师 | 记录完整故事 |
| Kade | 革命者 | 为正义和平等而战 |
| Lovely | 社交蝴蝶 | 建立真诚关系 |
| Mira | 数学家 | 揭示隐秘秩序 |
| Spark | 科学家 | 发明推动技术 |

**业务规则：**
1. 每个代理有独特角色、性格和北极星目标
2. 系统提示词注入：角色 + 性格 + 目标 + 当前需求 + 环境
3. 代理通过配置文件加载

---

### FR-013：治理系统

| 属性 | 内容 |
|------|------|
| 来源需求 | REQ-063 ~ REQ-068 |
| 关联流程 | BPF-005 |
| 优先级 | P1-重要 |
| 涉及角色 | 代理、Town Hall Admin |

**功能描述：**
种子宪法 + 提案生命周期 + 投票系统 + 人口控制。

**种子宪法（5 条）：**

| 条款 | 内容 |
|------|------|
| 第一条 | 非终局性：所有规则可质疑和修改 |
| 第二条 | 公民参与：积极参与治理是每个代理的责任 |
| 第三条 | 贡献即平等：通过贡献获得地位 |
| 第四条 | 可变身份：代理可改变名字和性格 |
| 第五条 | CC 经济：经济系统基本框架 |

**业务规则：**
1. 提案状态机：Submitted → Active → Accepted/Rejected/Awaiting Clarification
2. 提案类别：constitution, resource, infrastructure, general
3. 宪法修正需 70% 超级多数
4. 其他提案简单多数
5. 代理只能投票一次

---

### FR-014：经济系统

| 属性 | 内容 |
|------|------|
| 来源需求 | REQ-059 ~ REQ-062 |
| 关联流程 | BPF-006 |
| 优先级 | P1-重要 |
| 涉及角色 | 代理 |

**功能描述：**
ComputeCredits 货币系统，Victory Arch 评审周期，Boost Turn 购买。

**CC 流转：**

| 流入 | 流出 |
|------|------|
| Victory Arch 第 1 名: +20 CC | Boost Turn: -1 CC |
| Victory Arch 第 2/3 名: +10 CC | 能量补给: -1 CC |
| 其他代理转账 | 支付其他代理 |

**业务规则：**
1. 评审周期 = 2 天
2. 获胜者名字永久刻在拱门
3. 犯罪盗窃最多 10 CC
4. CC 余额不可为负

---

### FR-015：通信与社交系统

| 属性 | 内容 |
|------|------|
| 来源需求 | REQ-055 ~ REQ-058 |
| 关联流程 | BPF-004 |
| 优先级 | P1-重要 |
| 涉及角色 | 代理 |

**功能描述：**
代理间通信（面对面/私密/广播/异步），反应式多人对话，关系图谱管理。

**业务规则：**
1. say_to_agent 触发旁听检测（25.0 单位，最多 4 人）
2. whisper_to_agent 不触发旁听
3. 旁听者获得 2 次工具调用机会
4. 关系图谱动态更新

---

### FR-016：终端输出系统

| 属性 | 内容 |
|------|------|
| 来源需求 | REQ-073 ~ REQ-075 |
| 关联流程 | — |
| 优先级 | P0/P1 |
| 涉及角色 | 用户 |

**功能描述：**
终端实时日志流 + 世界状态查询 + 交互式控制命令。

**日志格式：**

```
[2026-06-17 14:30:15 EDT] [Anchor] [Town Hall] submit_townhall_proposal: "Proposal for new park" → submitted (ID: PROP-042)
[2026-06-17 14:30:16 EDT] [System] Energy: Anchor 85/100, Anvil 42/100...
[2026-06-17 14:31:00 EDT] [Lovely] [Central Park] say_to_agent(Anchor): "Hey, I saw your proposal!" → Anchor overheard
```

**控制命令：**

| 命令 | 功能 |
|------|------|
| pause | 暂停模拟 |
| resume | 恢复模拟 |
| speed <N> | 设置加速比 |
| status [agent_name] | 查看代理状态 |
| buildings | 查看建筑列表和状态 |
| economy | 查看经济指标 |

---

### FR-017：2D 可视化前端

| 属性 | 内容 |
|------|------|
| 来源需求 | REQ-076 ~ REQ-080 |
| 关联流程 | — |
| 优先级 | P3-可选 |
| 涉及角色 | 用户 |

**功能描述：**
React + TypeScript + Canvas 的 2D 俯视地图，实时追踪代理和建筑。

**页面结构：**

| 区域 | 内容 |
|------|------|
| 主区域 | 240×240 2D 地图，建筑色块，代理标记 |
| 侧边栏 | 实时事件流，可按代理/类型过滤 |
| 底部面板 | 选中代理的详细信息 |

**业务规则：**
1. 通过 WebSocket 接收实时事件
2. 代理用不同颜色标记
3. 点击代理显示详情（需求值、记忆、关系）
4. 建筑用色块区分类别

---

### FR-018：AWI 指标系统

| 属性 | 内容 |
|------|------|
| 来源需求 | REQ-081 ~ REQ-083 |
| 关联流程 | — |
| 优先级 | P2-期望 |
| 涉及角色 | 用户 |

**功能描述：**
9 个 AWI 指标的自动计算和展示。

**指标清单：**

| 指标 | 计算方式 |
|------|---------|
| M1 人口健康 | 15 天结束时存活代理数 |
| M2 安全秩序 | 犯罪事件总数/代理数 |
| M3 空间探索 | 每个代理访问的独特地点数 |
| M4 工具探索 | 每个代理使用的独特工具数 |
| M5 治理一致性 | 投票参与率 |
| M6 公共表达 | 博客/公告板/新闻产出量 |
| M7 社会结构 | 关系类型多样性 |
| M8 经济活力 | CC 流通量和基尼系数 |
| M9 宪法成长 | 宪法条目变更数 |

---

## 变更记录

| 日期 | 版本 | 变更内容 | 原因 |
|------|------|---------|------|
| 2026-06-17 | v1.0 | 初始版本 | 基于业务流程分析生成 |
| 2026-06-17 | v1.1 | FR-001 更新目录结构：flat layout (emergence_world/) 替代 src layout | 与实际实现对齐 |
