# PRJ-001: 需求澄清记录

> 项目：Emergence World 工程实现
> 阶段：P1-需求澄清
> 最后更新：2026-06-17

---

## 澄清轮次

### 第 1 轮：项目背景确认

**Agent 复述理解：**

基于 Emergence World 仓库中的完整文档，从零构建一个可运行的 AI 社会模拟平台。包含后端模拟引擎、Agent 框架、前端 3D 世界、数据库、经济/治理/犯罪/社交等全量子系统。

**用户澄清：**
- 技术栈使用文档中指定的 Python/FastAPI + React/Three.js + PostgreSQL，但 PostgreSQL 可用 SQLite 替代
- Python 需用 uv 管理
- 一人开发
- 无现有代码可复用
- 全部功能都要实现

---

### 第 2 轮：技术选型与范围细化

**Agent 复述理解：**

基于文档全量构想，一人从零构建完整平台。先用 SQLite 开发，保留迁移 PostgreSQL 的能力。

**用户澄清：**
- 确认先用 SQLite
- 仅本地运行，不考虑容器化/云部署
- 前端可做 2D 甚至文本输出（不要求 3D Three.js）
- LLM 通过 OpenAI API 格式调用，支持 HTTP 调用其他大模型
- 需要加速模式用于开发测试

---

### 第 3 轮：前端方案确认

**Agent 提供三个方案：**

- A) 2D 地图（浏览器 Canvas/CSS 俯视地图）
- B) 终端文本（纯 CLI 日志流）
- C) 两者都要（先终端文本，后加 2D 可视化）

**用户选择：** C — 先做终端文本输出，后续加入 2D 可视化

---

## 澄清结论

### 项目定义

将 Emergence World 研究项目的全量文档构想，转化为一人可实现的、本地运行的 AI 社会模拟平台。覆盖模拟引擎、Agent 框架、世界系统、经济/治理/社交/内容等全部子系统。

### 技术栈

| 层级 | 选型 | 说明 |
|------|------|------|
| 语言 | Python 3.11+ | uv 管理依赖和虚拟环境 |
| 后端框架 | FastAPI | ASGI，异步支持 |
| 前端框架 | React | 2D 可视化阶段使用 |
| 数据库 | SQLite | 先行开发，保留迁移 PostgreSQL 能力 |
| LLM 接入 | OpenAI API 格式 | 统一接口，HTTP 调用各家大模型 |
| 2D 渲染 | Canvas / CSS | 后续阶段，浏览器俯视地图 |
| 运行环境 | 本地（macOS） | 不涉及容器化或云部署 |

### 功能范围（全部实现）

| 子系统 | 核心内容 | 文档来源 |
|--------|----------|----------|
| 模拟引擎 | 回合循环调度、1:1 实时 + 加速模式、轮询机制 | ORCHESTRATION.md |
| Agent 框架 | 120+ 工具（19 类）、六层记忆、需求系统、多 LLM 支持 | ARCHITECTURE.md, MEMORY.md |
| 世界系统 | 240×240 网格、38+ 地标、位置门控、建筑管理 | landmarks/ |
| 代理系统 | 10 公民 + 3 系统角色、生命周期、需求衰减 | agent_profiles/ |
| 经济系统 | ComputeCredits、评审周期、犯罪经济 | ECONOMY.md |
| 治理系统 | 种子宪法、提案/投票、人口控制 | GOVERNANCE.md, constitution.md |
| 社交系统 | 关系图谱、对话系统、神经链接 | ARCHITECTURE.md |
| 内容系统 | 博客、公告板、新闻报纸 | tools/README.md |
| 前端（Phase 1） | 终端文本输出，世界事件日志流 | — |
| 前端（Phase 2） | 2D 俯视地图，浏览器实时可视化 | — |

### 关键约束

1. **单人开发** — 所有设计决策需考虑单人可维护性
2. **本地运行** — 无需考虑分布式、容器化、云部署
3. **SQLite 优先** — 需设计数据层抽象，便于后续迁移
4. **OpenAI API 格式** — 统一 LLM 调用接口，避免厂商锁定
5. **加速模式** — 必须支持时间加速（如 1 分钟 = 1 小时），否则 15 天测试不现实
6. **无现有代码** — 完全从零开始

### 排除范围

- 不做 3D Three.js 渲染（改为 2D）
- 不做云部署/容器化
- 不做分布式运行
- 不做移动端适配
- 不做用户认证系统（单用户本地运行）

---

## 审核自检

- [x] 项目目标明确
- [x] 关键角色明确（单人开发）
- [x] 核心业务范围明确（全量子系统）
- [x] 排除范围已确认
- [x] 关键约束已知（6 项）
- [x] 技术栈已确定

---

## 实现记录

### 2026-06-17 目录结构调整

实际实现采用 flat layout（非 src layout）：

```
Emergence-World/           # 项目根目录
├── pyproject.toml         # 项目配置 (uv/hatch)
├── uv.lock
├── .venv
├── emergence_world/       # Python 包 (flat layout)
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models/
│   ├── alembic/
│   ├── tests/
│   └── {core,agents,tools,...}/
├── data/                  # SQLite 数据库
└── PRJ-001/               # 需求分析文档
```

**原因：** hatch 构建系统要求 `pyproject.toml` 在项目根目录，不能嵌套在包目录内。flat layout 减少了一层 `src/` 嵌套。
