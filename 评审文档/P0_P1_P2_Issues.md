# TrueNorth · 问题清单（P0 / P1 / P2）

- 版本：TrueNorth Skill-first MVP v1（Review Freeze）
- 更新：2026-06-24
- 配套：`Review_Report.md`、`开发文档.md`

分级定义：
- **P0**：必须马上修，否则影响使用。
- **P1**：建议近期修，影响体验或维护。
- **P2**：后续优化，不影响当前 MVP review。

---

## P0 · 阻断级

| 状态 | 问题 | 说明 |
| --- | --- | --- |
| ✅ 已修 | Skill 卡主按钮用了过泛的「查看详情」 | 已改为「看使用方式」；全站无「查看详情」主按钮 |
| ✅ 已修 | About 统计卡「深度拆解」与全站「深度解读」用语不一致 | 第 1437 行改为「深度解读」（浏览器走查发现，属术语一致性小修） |

> 当前**无未解决的 P0**。`node --check` 通过、jsdom 真实加载 0 error / 0 warning、Skill-first 落地、术语统一。详见 `Browser_Walkthrough_Report.md`。

---

## P1 · 体验 / 维护

| 状态 | 问题 | 建议 |
| --- | --- | --- |
| 🟡 部分完成 | 平台 logo 占位 | 用户已提供 **11** 个真实品牌 SVG 并内联为 base64（`LOGOS`：a16z/accenture/anthropic/arxiv/bain/mckinsey/microsoft/openai/wechat/wef/x）；来源图谱占位升级为「**品牌色底 + 白色字母标**」(`lt-mark`)。仍缺 `github`/`skillhub`/`zread`/`simonwillison`/`starmorph` 真实 SVG——按既定规则**不伪造商标**，待用户提供后内联进 `LOGOS` |
| ✅ 已做 | 浏览器走查 | 已用 Node + jsdom 真实加载走查：0 error / 0 warning，15 项核心交互函数均执行无抛错（见 `Browser_Walkthrough_Report.md`）。**唯余移动端横向溢出 / 复制 / 外链等纯视觉项需一次真实浏览器人工目检** |
| 🟡 已补静态修复 | 移动端横向溢出 | 已补 `.grid`(内容库) 的 `@media(max-width:760px)` 单列覆盖（`body` 早 `overflow-x:hidden`、其余 grid 均有 760 断点）；390/768/1024px 真实浏览器目检无横向滚动仍列为定版前 5 分钟例行目检（jsdom 无布局引擎无法断言，不阻断定版） |
| ✅ 已补 | 信号 ↔ Skill 关系 | 给 5 个有真实对应的信号补 `relatedSkills`（缺失即隐藏）；连同既有，现 **9 / 21** 信号有「可尝试的 Skill」行，均真实匹配、不硬造 |
| 可选 | AI 信号精确数量已核 | 数据层实测 `SIGNALS`=12，与 About「12」一致，口径已统一 |

---

## P2 · 后续优化

| 状态 | 问题 | 建议 |
| --- | --- | --- |
| ✅ 已做 | 来源图谱「反向统计」 | 点内容机构 → 抽屉 `#srcOv` 反查其贡献的深度解读 / 案例（`openDeck` 打开）；点 GitHub / SkillHub → 反查其贡献的工具 / 项目（`openTkDetail`）。`srcReverse(name,kind)` / `closeSrc()`，Esc / 点遮罩可关 |
| 🧪 测试中 | 公考备考 SOP 为原创、未接地 | `#gongkao` 是经用户同意的**非 skill-first 破例**（开放生态无够格、可溯源的考公 skill）；当前已显著标注「🧪 测试阶段」、不构成报考建议。后续可接地权威备考资料或正式化；外部 review 时与「可溯源」内容分开看待 |
| ✅ 已做 | 全站搜索 UI | 已上线（导航「⌕ 搜索」+ Ctrl/⌘ K 浮层，复用 `searchAll`，跨 信号/案例/方案/Skill/词典 分组结果可点击直达） |
| 待办 | 数据层达阈值后拆文件 | 阈值：SKILL_LIBRARY>30 / TOOLKIT>60 / CURATED>20 / SIGNALS>50 / GLOSSARY>100，超过即评估把数据层拆成独立 JSON/JS |
| 可选 | 跑通路径 AI prompt 开头加 Zread | 在 Codex/Kiro/Claude 的 prompt 开头加「先用 Zread 摸清结构再改」 |

---

## 下一步三阶段

- **阶段 A · Review Freeze（当前）**：文档已校准 ✅、小 bug 已修 ✅、浏览器走查已做 ✅（0 报错）→ 仅剩一次真实浏览器 5 分钟人工目检（移动端横向溢出 / 复制 / 外链）。
- **阶段 B · 小范围精修**：不加量，只打磨 10 条 Skill 的 whyTrueNorth/sourceRefs 与主路径文案；补 3 个平台真实 logo。
- **阶段 C · 扩容前准备**：Skill>30 再拆数据文件；内容明显增多再做搜索 UI；来源数据稳定再做反向统计。

---

## 内容更新记录（2026-06-22）

- 新增 2 篇深度解读：《为何企业 80% 的 AI 投入看不到效果》（腾讯研究院深度报告）、《Claude Code 全套命令实操手册》。深度解读 16 → **18**，其余计数不变。
- 不影响问题分级：**仍无未解决 P0**；新内容已用 jsdom 复验渲染无报错。两条原文链接已核对方向无误（企业报告→KIyP9put… / Claude Code→td5iPyNd…）。

- **2026-06-22（续）**：关键洞察补 6 张洞察卡、来源图谱加「腾讯研究院」节点、AI 信号更新一批（从 X / 博客 / 报告等外部新发内容选取、以库内维度与标准为筛选基准、不含微信公众号，12 → 21）。**仍无未解决 P0**；jsdom 复验 0 报错。计数基线现为 深度解读 17 / 案例 12 / 方案 33 / 信号 21 / 词条 72 / Skill 10。

- **2026-06-22（实战案例扩充）**：案例 7 → 12（Stripe 由深度解读移入 + 4 个外部真实案例：Anthropic / Grab / Shopify River / Moderna），深度解读 18 → 17。**仍无未解决 P0**；jsdom 复验 0 报错。计数基线现为 深度解读 17 / 案例 12 / 方案 33 / 信号 21 / 词条 72 / Skill 10。

- **2026-06-22（Skill 扩容 第一波）**：SKILL_LIBRARY 10 → 24(从现有内容人工精选 14 条 A 档入库 + 入口前置 + 打磨原 4 条空 prompt)。**仍无未解决 P0**;jsdom 复验 0 报错。计数基线现为 深度解读 17 / 案例 12 / 方案 33 / 信号 21 / 词条 72 / Skill 24。第二波 B 档 6 条待补,达 30 时按阈值评估拆数据文件。这也部分关闭了原 P1「Skill 库入口埋在视图切换里」与「4/10 Skill 无可复制 prompt」两项。

- **2026-06-22（Skill 扩容 第二波）**：SKILL_LIBRARY 24 → **30**(补 B 档 6 条)。**仍无未解决 P0**;jsdom 复验 0 报错。计数基线现为 深度解读 17 / 案例 12 / 方案 33 / 信号 21 / 词条 72 / Skill 30。已达拆数据文件评估阈值(SKILL>30 临界)——按当前排序先做全站搜索 UI,拆分待内容继续增长再评估。

- **2026-06-22（全站搜索 UI）**：上线导航「⌕ 搜索」+ Ctrl/⌘ K 浮层,复用 `searchAll`,跨 信号/案例/方案/Skill/词典 分组结果可点击直达。**原 P2「全站搜索无 UI」已关闭。** jsdom 复验 0 报错。仍无未解决 P0。

- **2026-06-22（论文写作工作台）**：新增 `#paper` 页签(导航「论文」)，聚合库内对论文有用的 2 工具 + 8 Skill，按 5 阶段排列，点击直达详情。纯聚合视图、不新增内容数据。**仍无未解决 P0**;jsdom 复验 0 报错。备注:学术专用 Skill(文献综述/润色/降重/引用)目前库内没有，是后续可扩展方向。

- **2026-06-22（学术 Skill + 论文工作台扩充）**：新增 12 条论文写作 Skill(均接地真实 GitHub 仓库、非原创) + PaperQA 工具；论文工作台扩为 5 阶段 23 卡。**仍无未解决 P0**;jsdom 复验 0 报错。当前基线 深度解读 17 / 案例 12 / 方案 34 / 信号 21 / 词条 72 / Skill 42。原"论文页缺学术专用 Skill"的待补项已关闭。

- **2026-06-22（两条 Skill 接地 + SOP 严谨化）**：sk-deai（去 AI 感，依据 Wikipedia「Signs of AI writing」+ humanize-text）、sk-format（格式合规，依据 Purdue OWL APA 7 + GB/T 7714）正式入库并接地真实来源；sk-academic-polish 增挂曼彻斯特 Academic Phrasebank。SKILL 42 → **44**。配套 `论文终稿Review-SOP.html` 步步可控、附来源依据。**仍无未解决 P0**；两文件 jsdom 复验 0 报错。当前基线 深度解读 17 / 案例 12 / 方案 34 / 信号 21 / 词条 72 / Skill 44。

- **2026-06-22（首页收敛）**：合并 QuickStart 与 TrueNorth Route 为单一「开始」区块（保留 6 节路线、删除重复 Route 区块），消除 Hero 之后的三层导航重叠（原 P1「首页三层导航重叠」已收敛）。**数据层拆分：经评估暂不做**，保持单文件 / 离线 / 可整文件分发的核心特性；阈值为启发式，待真有维护或协作痛点再以可逆方式拆。仍无未解决 P0。

- **2026-06-24（④ 收尾四项 + 验证）**：四项一并完成，计数不变（深度解读 17 / 案例 12 / 方案 34 / 信号 21 / 词条 72 / Skill 44），**仍无未解决 P0**。
  - **④-1 移动端横向溢出**：静态排查后补 `.grid`(内容库) 的 `@media(max-width:760px){grid-template-columns:1fr}`（`body` 早 `overflow-x:hidden`、feedgrid/tkgrid/siggrid/glossgrid 等均有 760 断点）。390/768/1024px 仍建议定版前真实浏览器 5 分钟目检（不阻断）。
  - **④-2 来源图谱反向统计**（原 P2 关闭）：新增 `srcReverse(name,kind)` + `closeSrc()` + `#srcOv` 抽屉。点内容机构 → 反查 `LIBRARY`+`CURATED`（经 `inferOrg`）并 `openDeck`；点 GitHub/SkillHub → 反查 `TOOLKIT` 并 `openTkDetail`；「其他源」按 `!inferOrg().site` 聚合。来源图谱内容机构 tile 由外链改为可点击反查。
  - **④-3 平台 logo**（原 P1 部分关闭）：11 个真实品牌 SVG 已内联 base64；`renderMap` 占位升级为品牌色底 + 白字母标(`lt-mark`)，且仅在有内联 logo 时渲染 `<img>`（移除会 404 的外链 `logos/*.svg` 请求，单文件分发更干净）。仍缺 github/skillhub/zread/simonwillison/starmorph 真实 SVG，按规则不伪造、待用户提供。
  - **④-4 信号 ↔ Skill**（原 P1 关闭）：补 5 个真实匹配的 `relatedSkills`（SkillsBench→sk-prompt-eval、claude-skills「资深工程师人格」→sk-persona-distill、AI 写代码循环两次→sk-review、Anthropic 专家用 Claude→sk-ask-loop+sk-brainstorming、5 家大厂免费学 AI→sk-teach）。连同既有，现 9/21 信号有「可尝试的 Skill」行。
  - **验证**：`node --check` 双通过；jsdom 16 项检查全 PASS、0 error/warning（renderMap 19 节点 / 14 内容机构接 `srcReverse` / 麦肯锡→2 deck / GitHub→24 工具 / 开关正常 / 8 品牌色字母标 + 11 个 data-URI logo / 无残留外链 logo；renderSignals 21 卡 / 9 行 relskill / 5 个新 chip 接 `goSkill`）。

- **2026-06-24（新增 · 公考备考 SOP 测试模块）**：新增 `#gongkao`（导航「公考」）——经用户同意的**非 skill-first、原创整理**备考 SOP，覆盖国考 / 省考 / 选调（含紧急选调）/ 事业编等。显著标注「🧪 测试阶段」+「不构成报考建议、以官方公告为准」；真实契合处借用现有 Skill，chip 点击直接打开该 Skill 详情抽屉（`openSkillDetail`，与论文工作台一致；sk-compress↔申论概括、sk-roleplay/sk-ask-loop↔面试等）。**不新增可溯源数据，计数不变**（17/12/34/21/72/44），**无新增 P0**。`node --check` 双通过、jsdom 16 项复验 0 报错。已知限制：该模块未接地权威来源（测试性质），已列为 P2（接地或正式化）。

- **2026-06-24（修复 · 导航滚动联动错位）**：顶部导航点「公考」时高亮 / 联动错位到「词典」。根因：scroll-spy 的 `IntersectionObserver` 观察列表漏了 `gongkao`，#gongkao 在视口时由相邻的 #glossary 触发高亮，造成「点公考像是去了词典」。修复：把 `gongkao` 补进观察列表（`paper` 与 `library` 之间）。jsdom 复验 7 项全 PASS：公考 nav→`go('#gongkao')`、#gongkao 独立于 #glossary 且含 6 类型卡 + 7 阶段卡、scroll-spy 已观察 #gongkao、0 报错。无新增 P0。

- **2026-06-24（修复 · 续 · 找到真正根因）**：上一条只修了 scroll-spy 高亮，点「公考」仍会停到「词典」。**真正根因**：`setupFold` 默认把所有非核心区块（含 #gongkao / #glossary / #paper 等）折叠（`folded` + `max-height:0`），而顶部导航的 `go()` 只滚动、不展开——点公考只滚到折叠的公考标题条，相邻折叠的词典就顶上来了。**修复**：`go()` 现在会先把目标区块展开（若 `folded` 则触发其标题 `.h2.foldable` 的展开），再平滑滚动。jsdom 复验 12 项全 PASS：公考/词典/论文默认折叠 → 点导航各自展开、点公考不再连带词典、重复点不误折叠、非折叠区块导航安全、0 报错。连同 spy 修复，导航点击现已正确「展开 + 滚动 + 高亮」。
