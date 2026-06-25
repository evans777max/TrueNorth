# 指北 TrueNorth · Skill 候选提取与复核流程（Skill-first）

> **本目录（`内容流水线/`）即流水线根目录。** 下文所有命令都在本目录下运行，
> 例如 `python scripts/extract-skills.py --input jobs.example.json`，路径都相对本目录。

把「完整爬取 Skill」做成一个**安全、可复核、可扩展**的离线流程。
前端**不运行任何爬虫**;所有抓取都在本地手动执行,结果默认进入「待复核」。

> **当前阶段是链路验证,不是大规模收录。**
> 先用 3 个公开来源跑通 `jobs → dry-run → --fetch → 候选 → 人工 reviewed → merge → 贴回前端` 全链路,
> 验证 Skill 库展示 / 任务筛选 / 搜索 / sourceRefs / goSkill / About 计数无误后,再扩大来源数量。

## 核心原则

> **Skill 是最小入库单位;`sourceUrl` 只是来源,不一定是项目容器。**

一篇文章 / 一个 GitHub README / 一个网页里,作者可能随手提到多个 Skill。
我们不需要还原来源里的全部结构,只需要:
从来源提取候选 → 判断哪些符合指北收录标准 → 把符合的单独放进 Skill 库 → 保留原文链接作为 `sourceRef`。

---

## 0. 总览

```
jobs.json
   │  (1) python scripts/extract-skills.py --input jobs.json          # DRY-RUN：只校验+打印计划
   │  (2) python scripts/extract-skills.py --input jobs.json --fetch  # 联网抓公开内容
   ▼
data/skill_candidates.json   （每条候选 reviewStatus=pending）
   │  (3) 人工复核：符合收录标准→reviewed，不符合→rejected，拿不准→保持 pending
   ▼
   │  (4) python scripts/merge-reviewed-skills.py --input data/skill_candidates.json
   ▼
SKILL_LIBRARY 片段  →  人工贴进 TrueNorth.html 的 SKILL_LIBRARY
```

脚本**永远不会**直接修改 `TrueNorth.html`。

---

## 1. 如何写 jobs.json

复制 `jobs.example.json`,每个来源一项。**只有 `sourceUrl` 和 `sourceType` 是必填**:

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `sourceUrl` | 是 | 原始来源链接（公开可访问） |
| `sourceType` | 是 | `github_readme` / `skillhub` / `article` / `docs` / `other` |
| `sourceTitle` | 否 | 来源标题（写入 sourceRefs.title） |
| `sourceAuthor` / `sourceName` / `sourceDate` | 否 | 来源元信息 |
| `parentProjectId` | 否 | **仅当来源本身就是某个项目 / Skill 集合时才填**（对应前端 `TOOLKIT` id） |
| `note` | 否 | 备注 |

普通文章来源**不要**填 `parentProjectId`——候选会作为独立 Skill,文章只作为 `sourceRef`。

### 何时才用 parentProjectId
1. 来源本身就是一个明确项目;
2. 来源本身就是一个 Skill 集合;
3. 这些 Skill 确实属于同一个项目;
4. 前端需要展示「该项目包含哪些 Skill」。
否则不要强行 parentProjectId。

---

## 2. dry-run（默认,不联网）

```bash
python scripts/extract-skills.py --input jobs.example.json
```

会做:读取 jobs → 校验字段 → 打印每个 job 用哪个解析器、是否独立 Skill 来源 → 写出 `dry_run_report.json`。
**不联网、不写 `data/skill_candidates.json`。**

---

## 3. --fetch（联网抓公开内容）

```bash
python scripts/extract-skills.py --input jobs.example.json --fetch
```

约束（已内置）:
- 只抓公开内容;`github_readme` 会转成 `raw.githubusercontent.com/.../README.md`。
- 每个请求间隔 **≥ 3 秒**;不递归、不抓全站;单 source 只抓当前页 / README。
- 遇到 `401 / 403 / 登录页 / 验证码` → **跳过并记录原因**,不绕过权限。
- 带合理 `User-Agent`;单 job 失败不中断其它 job（写入 errors）。
- 输出 `data/skill_candidates.json`,所有候选 `reviewStatus = "pending"`,来源写进 `sourceRefs`。

---

## 4. 候选数据结构（skill_candidates.json）

每条候选:

```json
{
  "id": "cand-xxx",
  "name": "Skill 名称",
  "desc": "描述",
  "task": ["ppt", "report"],
  "scenario": "适用场景",
  "difficulty": "新手友好 / 中等 / 进阶 / 工程向",
  "input": "需要输入什么",
  "output": "会输出什么",
  "install": "安装命令或使用方式",
  "prompt": "可复制 Prompt",
  "tags": [],
  "whyTrueNorth": "",
  "sourceRefs": [
    { "title": "来源标题", "url": "原文链接", "sourceType": "article", "extractedFrom": "原文片段" }
  ],
  "reviewStatus": "pending",
  "riskLevel": "low",
  "note": "",
  "parentProjectId": "（可选，仅明确属于某项目/集合时才有）"
}
```

样例见 `data/skill_candidates.sample.json`（仅样例,不作正式数据）。

---

## 5. 指北收录标准（isTrueNorthSkill）

脚本里的 `isTrueNorthSkill(candidate)` 只给**筛查建议**（不达标的在 `note` 里提示,仍保持 pending,由人工决定）。

**收录**（满足以下大多数）:
1. 能完成明确任务;2. 有实际使用场景;3. 用户能理解并复用;
4. 有安装 / 使用路径 / Prompt / 示例之一;5. 来源可追溯;
6. 能帮用户从「知道」走向「能用」;7. 与 AI 工作 / Agent / 自动化 / 内容 / 研究 / 数据 / 代码 / 知识库相关。

**不收录**:
1. 只是随口提到的工具名;2. 没有明确用途;3. 没有来源;4. 无法判断怎么用;
5. 明显广告;6. 纯概念 / 纯口号;7. 与指北定位无关;8. 重复度过高;9. 高风险但没说明边界。

不确定的候选:保留 `pending`,**不进入公开前端**。

---

## 6. 人工复核

打开 `data/skill_candidates.json`,逐条判断:
- 符合收录标准 → 改 `"reviewStatus": "reviewed"`,并**补写 `whyTrueNorth`**（指北收录理由,会展示在前端）。
- 不符合 → 改 `"rejected"`。
- 拿不准 → 保持 `"pending"`。

复核要点:名称/描述是否如实、`sourceRefs[].url` 是否能打开、`install`/`prompt` 是否可直接用;
`riskLevel: high`（医疗 / 金融 / 法律）必须保留 `note`:「仅作信息参考,不能替代专业意见。」并从严复核。

---

## 7. 合并进前端 SKILL_LIBRARY

### 方式 A：用脚本生成片段（推荐）

```bash
python scripts/merge-reviewed-skills.py --input data/skill_candidates.json
# 默认写出 data/skill_library_reviewed.js；也可指定路径：
python scripts/merge-reviewed-skills.py --input data/skill_candidates.json --output data/skill_library_reviewed.js
```

脚本只取 `reviewed`,按名称去重、**合并 sourceRefs**、补全字段,输出 `const SKILL_LIBRARY_REVIEWED = [...]`（写入 `data/skill_library_reviewed.js`）。
把这些条目**手动合并**进 `TrueNorth.html` 里的 `SKILL_LIBRARY`:
- 已存在的同名 Skill → 只合并 `sourceRefs`、补字段,**不重复新增**;
- 新 Skill → 直接追加。

### 方式 B：纯手动
从 `skill_candidates.json` 挑 `reviewed` 的条目,按前端 `SKILL_LIBRARY` 既有结构复制进去。

---

## 8. 前端展示规则（已实现）

`TrueNorth.html` 渲染脚本里:

```js
const SHOW_PENDING_SKILLS = false; // 公开站保持 false，本地预览可临时改 true
```

- `reviewed` → 正常展示
- `pending` → **默认不展示**;`SHOW_PENDING_SKILLS=true` 时展示并打「待复核」标签
- `rejected` → **永不展示**
- 缺失 `reviewStatus` 的旧数据 → 兼容按 `reviewed` 处理

展示位置:方案库顶部「项目 / 工具」｜「Skill 库」视图切换。Skill 库视图渲染 `SKILL_LIBRARY`,
卡片含名称 / 任务标签 / 描述 / 场景 / 难度 / 输入 / 输出 / 可复制安装与 Prompt / 来源链接（可多个）/
指北收录理由 `whyTrueNorth`;支持任务入口与搜索过滤;可反向跳到 `relatedTool` 项目或 `relatedGlossary` 概念。

> 项目集合（`TOOLKIT` + `TK_SKILLS`）里的 `TK_STATS[id].skillCount` 仍表示**来源真实总数**,
> 用于「已展示 N 个已复核代表 Skill,共约 X 个,更多见原文」。它与独立的 `SKILL_LIBRARY` 是两套互补展示。

---

## 9. 风险规则

`infer_risk()` 命中以下关键词自动 `riskLevel = "high"` 并加免责声明:
- 医疗:医疗 / 诊断 / 用药 / 病人 / 疾病 / 化验 / 影像 / 肿瘤 / 基因 / 临床 / 处方 / 治疗
- 金融:投资 / 股票 / 交易 / 买入 / 卖出 / 收益 / 基金 / 证券 / 财报 / 研报 / 估值
- 法律:合同 / 诉讼 / 律师 / 法律意见 / 法规 / 合规 / 仲裁 / 劳动纠纷

---

## 10. 不允许抓取的内容

- 需要登录 / 付费 / 鉴权才能看的内容
- 明确 `robots.txt` 或服务条款禁止抓取的内容
- 个人隐私、非公开数据
- 任何需要绕过验证码 / 风控的内容

遇到上述情况:**跳过并记录**,不要尝试绕过。

---

## 11. 解析器现状

| sourceType | 解析器 | 状态 |
| --- | --- | --- |
| `github_readme` | `parse_github_readme` | 可用:标题 / bullet / 仓库链接 / 代码块 |
| `article` / `docs` / `other` | `parse_article` | 可用:识别「Skill 名称 / 适用场景 / 安装 / Prompt / 命令 / 工具」标签结构 |
| `skillhub` | `parse_skillhub` | **仅框架**:多为 JS 渲染 / 需登录,抓不到时记录 unsupported,不绕过 |

下一步要真正批量爬取,优先补:
1. `parse_skillhub`:若有公开 API / 静态数据则改用;否则保持 unsupported。
2. `parse_github_readme`:补表格解析、每个 Skill 的 install/prompt 精确归属。
3. `parse_article`:针对微信图文实际结构细化分段与字段抽取。
4. `infer_task` / `infer_difficulty`:用更多语料校准关键词。

---

## 12. 小批量验证流程（本轮）

> 当前阶段是链路验证,不是大规模收录。

1. 当前不是大批量阶段,先用 **3 个公开来源**测试(见 `jobs.example.json`)。
2. 默认 dry-run 不联网:`python scripts/extract-skills.py --input jobs.example.json` → 写 `dry_run_report.json`。
3. `--fetch` 才联网,产出 `data/skill_candidates.json`(全部 `pending`)。
4. 人工把 3–5 个候选改 `reviewed`,并补 `whyTrueNorth`;不合适的改 `rejected`(不展示)。
5. `python scripts/merge-reviewed-skills.py --input data/skill_candidates.json --output data/skill_library_reviewed.js` → 只合并 `reviewed`,产出 `const SKILL_LIBRARY_REVIEWED = [...]`。
6. 人工把 `SKILL_LIBRARY_REVIEWED` 各项贴进前端 `TrueNorth.html` 的 `SKILL_LIBRARY`。
7. 在前端验证:Skill 库视图展示 / 任务入口筛选 / 搜索(含 sourceRefs) / 多来源 sourceRefs / `whyTrueNorth` / install·prompt 复制 / `relatedTool` 打开项目 / `relatedGlossary` 跳词典 / `goSkill()` 跳转高亮 / About「已复核 Skill」计数。
8. 确认无误后,再逐步扩大来源数量(每次仍小批 + 人工复核)。

## 13. 文件清单

- `jobs.example.json` — 来源清单示例（parentProjectId 可选）
- `scripts/extract-skills.py` — 候选提取（默认 DRY-RUN,`--fetch` 才联网）
- `scripts/merge-reviewed-skills.py` — 合并 reviewed → `SKILL_LIBRARY` 片段
- `data/skill_candidates.sample.json` — 候选样例（仅样例）
- 前端 `TrueNorth.html` 的 `SKILL_LIBRARY` — 已复核 Skill 的展示数据
