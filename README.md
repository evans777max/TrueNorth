# 指北 TrueNorth

> 用 AI 工作的方向 —— 一个**单文件、离线、自包含**的 AI 工作导航站 + Skill-first 能力层。

## 这是什么

指北 TrueNorth 把分散的 AI 信息整理成一条主线：**看懂 → 找到方法 → 看到案例 → 找到工具 / Skill → 尝试跑通**。
核心是一个**单 HTML 文件**（内联 CSS / JS，无构建、无后端、无依赖），双击即可打开，可整文件分享。

## 怎么打开

直接双击 `TrueNorth.html`（任意现代浏览器）。无需服务器、无需联网——logo 已 base64 内联。

## 模块

- AI 信号 · 关键洞察 · 实战案例 · 方案库 · Skill 库 · AI 词典 · 来源图谱
- 论文工作台（`#paper`）
- 公考备考 SOP（`#gongkao`，**测试模块**：原创整理、非 skill-first、不构成报考建议，一切以官方公告为准）
- 全站搜索（`Ctrl / ⌘ K`）

当前内容基线：深度解读 17 · 实战案例 12 · 方案 36 · 信号 21 · 词条 72 · 已复核 Skill 45。

## 目录结构

| 路径 | 说明 |
|---|---|
| `TrueNorth.html` | 网站本体（核心资产，单文件） |
| `说明.md` | 一页式索引：什么是什么、从哪看起 |
| `评审文档/` | 开发文档 / Review_Report / P0_P1_P2_Issues / Browser_Walkthrough_Report / External_Review_Feedback |
| `内容流水线/` | 离线 Skill 提取 / 复核脚本与数据（非前端运行） |
| `论文终稿Review-SOP/` | 独立交付物：论文终稿 review 可执行 SOP（HTML + MD） |
| `logos/` | 品牌 SVG（同时已 base64 内联进 HTML） |

## 维护约定

- **单文件是核心资产**：不拆分 `TrueNorth.html` 的数据层；保持一个 `<style>` + 两个 `<script>`（数据层 / 渲染层）。
- **不原创、必接地**：每个 Skill 接地真实 GitHub / 权威来源（公考 SOP 为显式破例，已标注「测试」）。
- **改完必验证**：抽出 `<script>` 跑 `node --check`；再用 jsdom 真实加载复验，0 error 才算过。
- 详见 `评审文档/开发文档.md`。

## 状态

TrueNorth Skill-first MVP v1（已冻结，无未解决 P0）。详见 `评审文档/`。

---

个人独立项目 · 一个人从 0 到上线。
