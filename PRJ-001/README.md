# PRJ-001: Emergence World 工程实现

> 将 Emergence World 研究项目的文档构想转化为可运行的工程系统。

## 项目信息

| 字段 | 值 |
|------|-----|
| 项目编号 | PRJ-001 |
| 状态 | Phase 4 进行中 |
| 当前阶段 | 终端控制台已完成，内容/犯罪工具待实现 |
| 创建日期 | 2026-06-17 |
| 最后更新 | 2026-06-17 |

## 项目简介

基于 Emergence World 仓库全量文档，一人从零构建完整的 AI 社会模拟平台。技术栈：Python 3.11+ / uv / FastAPI + SQLite + Anthropic API 格式多 LLM 支持。本地运行，83 条需求覆盖 15 个模块。

## 实现进度

| Phase | 内容 | 状态 |
|-------|------|------|
| Phase 1 | 项目脚手架 + 数据库 + FastAPI | ✅ 完成 |
| Phase 2 | 种子数据 + 模拟引擎 + LLM 集成 | ✅ 完成 |
| Phase 3 | 工具框架 + 19 个核心工具 | ✅ 完成 |
| Phase 4 | 终端控制台 + 内容/犯罪工具 | 进行中（控制台已完成） |
| Phase 5 | AWI 指标 + 2D 可视化前端 | 待开始 |

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

## 阶段进度

| 阶段 | 状态 | 产出 |
|------|------|------|
| P1-需求澄清 | ✅ 完成 | `01-clarification/clarification.md` |
| P2-需求清单 | ✅ 完成 | `02-requirements/requirements-list.md`（83 条需求） |
| P3-成功标准 | ✅ 完成 | `03-success-criteria/success-criteria.md` |
| P4-业务流程 | ✅ 完成 | `04-business-processes/processes.md`（10 个核心流程） |
| P5-技术规格 | ✅ 完成 | `05-technical-spec/*.md`（3 份文档） |

## 文档索引

- [需求澄清记录](01-clarification/clarification.md)
- [需求清单](02-requirements/requirements-list.md)
- [成功标准](03-success-criteria/success-criteria.md)
- [业务流程](04-business-processes/processes.md)
- [功能需求](05-technical-spec/functional-requirements.md)
- [非功能需求](05-technical-spec/non-functional-requirements.md)
- [技术约束](05-technical-spec/technical-constraints.md)
