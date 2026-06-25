# TrueNorth · 浏览器走查报告（Browser Walkthrough）

- 版本：**TrueNorth Skill-first MVP v1**
- 阶段：**Review Freeze 最后一关 · Browser Walkthrough**
- 走查时间：2026-06-19
- 走查对象：`TrueNorth.html`（单文件）
- 配套：`Review_Report.md`、`P0_P1_P2_Issues.md`、`开发文档.md`

---

## 0. 环境与方法说明（请先读）

本环境**没有可交互的真实图形浏览器 / Playwright 浏览器二进制**（未预装，且本轮遵守「不引入重依赖」，未下载浏览器内核）。

为避免「假装完成浏览器走查」，本轮采用**比静态阅读更强的真实执行验证**：

1. **结构抽取 + `node --check`**：把单个 `<style>`、两个 `<script>` 抽出，对两个 JS 块做语法校验。
2. **数据层真实执行**：用 Node 实际运行数据层（block0），统计 `SKILL_LIBRARY` / `TOOLKIT` / `GLOSSARY` 等真实计数与字段完整性。
3. **jsdom 真实加载整页**：用 `jsdom`（纯 JS，无浏览器二进制）以 `runScripts:'dangerously'` 真实加载 `TrueNorth.html`，
   捕获加载期 `console.error` / `jsdomError` / `window.error`，并**真实调用**各交互函数（`openTkDetail` / `setTkView` / `renderSkillLib` / `searchAll` / `openSkillDetail` / `goSkill` / `gotoTerm` / `renderMap` 等），确认无抛错。

**这套方法能确证：** 页面加载无 JS 报错、DOM 结构正确、所有主交互函数可执行且不抛错、数据计数真实正确、Skill 库真实渲染 44 条、术语/按钮文案正确。

**这套方法不能替代的（仍需人工/Playwright 视觉确认）：** 真实像素布局、CSS 视觉效果、平滑滚动观感、Deck 翻页动画、滚动揭示动画、**移动端 390/768/1024px 是否横向溢出**、剪贴板是否真的写入、外链是否真的在新标签打开。这些为「纯视觉/浏览器行为」项，下文标注为 **需人工视觉确认**，不谎称已通过。

| 记录项 | 结果 |
| --- | --- |
| 运行环境 | Node v22.13.1 + jsdom 24（Windows） |
| 访问方式 | jsdom 直接加载文件（等价 file://，无网络请求） |
| 页面是否成功加载 | 是 |
| 加载期 console error | **0** |
| 加载期 console warning | **0** |
| jsdomError / window.error | **0** |
| 资源加载失败 | 无（logo 为内联 base64，无外部资源依赖） |
| `<style>` 数量 | 1 |
| `<script>` 数量 | 2（数据层 + 渲染交互层） |
| `node --check` block0 / block1 | 均通过 |
| 未闭合 / 嵌套标签 | 无 |

---

## 1. 15 项核心走查结果

> 说明：「执行验证」= jsdom 真实加载/调用已确认；「需人工视觉确认」= 仅视觉/浏览器行为，未在本环境断言。

| # | 走查项 | 结果 | 验证方式 / 备注 |
| --- | --- | --- | --- |
| 1 | 页面基础加载 | **Pass** | jsdom 加载成功，0 error / 0 warning，无白屏（DOM 完整渲染） |
| 2 | Hero CTA 跳转 | **Pass（逻辑）** | `go()` 存在；锚点 `#signals/#toolkit/#glossary` 等目标区块均存在。平滑滚动观感需人工视觉确认 |
| 3 | Quick Start 入口 | **Pass（逻辑）** | 四张卡 `go('#...')` 目标区块齐全 |
| 4 | AI 信号 + 信号解读 | **Pass** | 信号容器存在；`openDeck` / `SIGNAL_REL` 可用；相关 Skill chip → `goSkill` 不抛错。Deck 翻页动画需人工视觉确认 |
| 5 | 关键洞察四类切换 | **Pass** | `#insights` 存在；`DIG_TABS`=data/change/tool/frame 四类；`renderDigest` 执行无错 |
| 6 | 实战案例 + 案例解读 | **Pass** | `caseData` / `CASE_REL` 可用，相关工具/概念/Skill 关系数据就位 |
| 7 | 方案库 项目视图 | **Pass** | 深度解读库 grid 真实渲染 **18** 张卡；`openTkDetail()` 打开抽屉（含 `open` 类）、`closeTkDetail()` 正常关闭；筛选/搜索方法就位 |
| 8 | Skill 库视图 + 10 reviewed | **Pass** | `setTkView('skill')` 切换 OK；真实渲染 **10** 张卡，ids 全为 reviewed；主按钮文案为「**看使用方式**」，**无**「查看详情」主按钮 |
| 9 | Skill 任务筛选 | **Pass** | 任务筛选数据/函数就位，调用无错 |
| 10 | Skill 搜索 | **Pass** | `searchAll` 命中：`brainstorming`→skill2/toolkit1；`PPT`→skill9/toolkit3；`debug`→skill1/toolkit1；`压缩`→skill2/glossary3。覆盖 name/desc/task/tags/scenario/whyTrueNorth/sourceRefs(title+sourceName+extractedFrom) |
| 11 | Skill 详情抽屉 | **Pass** | `openSkillDetail('sk-brainstorming'/'sk-teach'/'sk-debug')` 均渲染无抛错；install/prompt/whyTrueNorth/sourceRefs 字段在数据层验证齐全。复制按钮真实写剪贴板需人工确认 |
| 12 | goSkill 跳转高亮 | **Pass（逻辑）** | `goSkill('sk-compress')` 调用无抛错；切视图 + `scrollIntoView` + `flash` 类逻辑就位。高亮动画观感需人工视觉确认 |
| 13 | AI 词典 | **Pass** | `#glossary` 存在；`gotoTerm('RAG')` 调用 OK；`openStory` 故事模式函数就位；7 站/卡片模式数据就位 |
| 14 | 来源图谱 | **Pass** | `#map` 存在；`renderMap()` 执行无错；logo 为内联占位/品牌图。点击外链行为需人工确认 |
| 15 | About 数字 | **Pass** | DOM 实测：17 / 12 / `abTk`(运行时=`TOOLKIT.length`=**34**) / `abSkill`(运行时=reviewed Skill=**44**) / 21 / 72，与基线一致 |
| 15b | 移动端横向溢出（390/768/1024px） | **需人工视觉确认** | jsdom 无真实布局引擎，无法断言横向溢出；列入待人工确认 |

---

## 2. 本轮发现的问题与处理

### 已修（本轮，属允许的「术语不一致」小修）
| 问题 | 位置 | 处理 |
| --- | --- | --- |
| About 统计卡把模块标为「**深度拆解**」，与全站/文档统一用语「**深度解读**」不一致（信号洞察导语第 1296 行即为「18 篇深度解读」） | `TrueNorth.html` 第 1437 行 | 改为「深度解读」。一词、零逻辑风险，改后 `node --check` + jsdom 复跑仍 0 error |

> 关于「拆解」：全站其余「拆解」均为正常中文动词（如「拆解任务」「系统拆解工程闭环」「拆解产品机会」），出现在文章描述/Deck 正文里，**不是**被废弃的 UI 术语族（`PPT 拆解 / PPT 化拆解 / 点击进入拆解 / 拆解页`）——这些被废弃形式**全站零残留**，无需改动。

### 未发现 P0
本轮**未发现任何 P0**：无白屏、无加载报错、Skill 库/详情/方案库/Deck 函数均可用、`goSkill`/`searchAll` 调用无抛错。

---

## 3. P0 / P1 / P2 归类（本轮增量）

- **P0：无。**
- **P1（记录，不阻断定版）：**
  - 移动端 390/768/1024px 横向溢出 **需人工视觉确认**（本环境无法断言）。
  - 复制按钮真实写剪贴板、外链真实新开标签 **需人工/Playwright 确认**。
  - 平台 logo（github/skillhub/zread/starmorph）仍为占位（沿用既有 P1）。
- **P2（沿用既有）：** 来源反向统计、全站搜索 UI、数据层拆文件阈值等。

> 说明：`searchAll` 的 `out.skill` 同时聚合「工具内嵌 Skill 集合」与独立 `SKILL_LIBRARY`，故 "PPT" 命中 9 条属正常聚合，非 bug；且仅搜可见 reviewed Skill。无独立搜索 UI 仍为已知 P2 限制。

---

## 4. 是否允许定版

- 代码/结构/数据/交互接线层面：**全部通过，0 报错**。
- 唯一未由本环境断言的，是**纯视觉与移动端横向溢出**类项 —— 需一次真实浏览器（或 Playwright 视觉）人工点验。

**结论：条件通过（Conditional Pass）。**

允许将当前提交**冻结为 TrueNorth Skill-first MVP v1**，并进入外部 review / 小范围试用；
**附带一项收尾动作**：在任一真实浏览器中按「15b + P1 视觉项」做一次 5 分钟人工目检（重点：390px 窄屏无横向滚动、复制按钮、外链打开）。该动作不阻断定版，属上线前例行目检。

---

## 5. 浏览器走查结论

- 页面是否正常加载：**是（0 error / 0 warning）**
- 控制台是否无 P0 错误：**是**
- Skill 库是否显示 44 条：**是（全 reviewed）**
- Skill 详情是否可用：**是（函数执行无抛错，字段齐全）**
- 搜索 / 筛选是否可用：**是（searchAll 覆盖 7 类）**
- goSkill 是否可用：**是（调用无抛错）**
- 词典是否可用：**是（gotoTerm / openStory 就位）**
- 来源图谱是否可用：**是（renderMap 执行无错）**
- 移动端是否无严重横向溢出：**需人工视觉确认（本环境无法断言）**
- 是否存在未解决 P0：**否**
- 是否可以定版为 TrueNorth Skill-first MVP v1：**是（条件通过，附 5 分钟人工目检）**

### 最终判断：**条件通过**

TrueNorth Skill-first MVP v1 在结构、数据、交互逻辑层面通过走查（0 报错），可以冻结为 MVP v1 并进入外部 review / 小范围试用；唯一附带项是在真实浏览器中对移动端横向溢出与复制/外链做一次人工目检，该项不阻断定版。

---

## 增补记录（2026-06-22）

原走查（2026-06-19）针对的是 16 篇深度解读的版本。之后人工新增 2 篇深度解读（企业 AI 认知报告、Claude Code 实操手册），深度解读 → **18**。本增补对新内容做了同口径复验：

- `node --check` 双通过；jsdom 真实加载 **0 报错 / 0 警告**；
- 两个新 deck（`enterprise-ai-cognition` 12 页、`claude-code-mastery` 9 页）`openDeck` 渲染无空白页、无抛错；旧 deck `claude-harness` 回归正常；
- About 与信号洞察导语计数已同步为 17 / 12 / 34 / 44 / 21 / 72。

结论不变：无未解决 P0，可继续作为定版基线。

---

## 增补记录（2026-06-24 · ④ 收尾四项同口径复验）

在 06-22 版本基础上完成 ④ 收尾四项（移动端横向溢出 / 来源图谱反向统计 / 平台 logo / 信号↔Skill），不新增内容数据，计数不变（17 / 12 / 34 / 21 / 72 / 44）。本增补用同口径（Node v22 + jsdom 24）对四项做真实加载复验。

- `node --check` 双块均通过；jsdom 真实加载 **0 error / 0 warning**。
- **16 项断言全部 PASS**：
  1. 加载期 0 console/jsdom 错误；
  2. `renderMap()` 渲染 **19** 个来源节点；
  3. 内容机构 tile 接 `srcReverse`（**14** 个 onclick）；
  4. 品牌色字母标占位 **8** 个（`lt-logo lt-mark`）；
  5. 真实内联 logo 以 `data:image/svg` 渲染 **11** 个；
  6. 网格内**无**残留 `src="logos/…"` 外链请求；
  7. `srcReverse` 为函数；
  8. `srcReverse('麦肯锡')` 打开 `#srcOv`（`hidden=false`）；
  9. 列出贡献内容（麦肯锡 · 贡献 2 篇）；
  10. 麦肯锡行经 `openDeck` 路由（2 条）；
  11. `closeSrc()` 关闭 `#srcOv`；
  12. `srcReverse('GitHub','github')` 列出 **24** 个工具（`openTkDetail`）；
  13. `renderSignals` 为函数；
  14. 信号网格渲染 **21** 卡；
  15. 「可尝试的 Skill」行 **9** 条（含 5 个新补 + 既有）；
  16. 5 个新 Skill chip（sk-prompt-eval / sk-persona-distill / sk-review / sk-ask-loop / sk-teach）均接 `goSkill`。
- **仍需人工视觉确认（不阻断定版）**：移动端 390/768/1024px 横向溢出（已补 `.grid` 760 单列覆盖，但 jsdom 无布局引擎仍不能断言像素级溢出）、复制按钮真实写剪贴板、外链真实新开标签。

结论不变：**条件通过**，无未解决 P0，可继续作为 TrueNorth Skill-first MVP v1 定版基线。

---

## 增补记录（2026-06-24 · 公考备考 SOP 测试模块）

新增 `#gongkao`（导航「公考」）——非 skill-first、原创整理的备考 SOP 测试模块，不新增可溯源数据、计数不变（17 / 12 / 34 / 21 / 72 / 44）。同口径（Node v22 + jsdom 24）复验：

- `node --check` 双块通过；jsdom 真实加载 **0 error / 0 warning**。
- **16 项断言全 PASS**：导航「公考」链接存在；`#gongkao` 段与「🧪 测试阶段」标记、「不构成报考建议 / 以官方公告为准」横幅均在；`renderGongkao()` 渲染 6 张考试类型卡（国考 / 省考 / 选调生 / 紧急选调 / 事业编 / 其他全部命名）+ 7 张阶段卡（含 7 个「常见坑」块、28 个内容块）；11 个借用 Skill chip 全部接 `openSkillDetail`（点击直接打开 Skill 详情抽屉、与论文工作台一致），8 个 skill id 经 `skillById` 全部解析；点击后抽屉正常打开并显示该 Skill 内容、关闭正常、0 报错。
- **仍需人工视觉确认（不阻断）**：移动端 390/768/1024px 该模块卡片换行、长列表观感。

该模块为**测试性质**（未接地权威来源），结论与定版无冲突：无未解决 P0。
