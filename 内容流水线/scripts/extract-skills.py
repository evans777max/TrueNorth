#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
指北 TrueNorth · Skill 候选提取（Skill-first 版）
================================================

核心原则：
  Skill 是最小入库单位；sourceUrl 只是来源，不一定是项目容器。
  一篇文章 / README / 网页里作者可能随手提到多个 Skill，我们只负责：
    从来源提取候选 → 结构化 → 默认 pending → 人工复核 → reviewed 才进 SKILL_LIBRARY。

底线（务必遵守）：
  1. 默认 DRY-RUN：不联网，只校验 jobs、打印计划、写 dry_run_report.json。
  2. 只有 --fetch 才联网，且只抓【公开】内容。
  3. 不绕过登录 / 权限；遇 401/403/登录页 跳过并记录。
  4. 每请求间隔 >= 3 秒；不递归、不抓全站；单 source 只抓当前页 / README。
  5. 候选一律 reviewStatus="pending"，绝不自动 reviewed。
  6. 不直接改 TrueNorth.html，只写 data/skill_candidates.json。
  7. 医疗 / 金融 / 法律自动 riskLevel="high" + 免责声明。
  8. parentProjectId 可选，仅当来源明确是某个项目 / Skill 集合时才带。

用法：
  python scripts/extract-skills.py --input jobs.example.json          # DRY-RUN
  python scripts/extract-skills.py --input jobs.example.json --fetch   # 联网抓公开内容
"""

import argparse
import datetime
import json
import os
import re
import sys
import time

REQUEST_INTERVAL_SEC = 3
USER_AGENT = "TrueNorth-SkillExtractor/0.3 (+offline; respects robots; contact: maintainer)"
VALID_SOURCE_TYPES = ["github_readme", "skillhub", "article", "docs", "other"]
PARSER_BY_TYPE = {
    "github_readme": "parse_github_readme",
    "skillhub": "parse_skillhub",
    "article": "parse_article",
    "docs": "parse_article",
    "other": "parse_article",
}

RISK_KEYWORDS = {
    "medical": ["医疗", "诊断", "用药", "病人", "疾病", "化验", "影像", "肿瘤", "基因",
                "临床", "处方", "治疗", "medical", "clinical", "diagnos", "drug"],
    "finance": ["投资", "股票", "交易", "买入", "卖出", "收益", "基金", "证券", "财报",
                "研报", "估值", "finance", "trading", "invest"],
    "legal":   ["合同", "诉讼", "律师", "法律意见", "法规", "合规", "仲裁", "劳动纠纷",
                "legal", "lawyer", "compliance"],
}
RISK_NOTE = "仅作信息参考，不能替代专业意见。"

TASK_KEYWORDS = {
    "ppt": ["ppt", "幻灯", "演示", "海报", "网页", "卡片"],
    "report": ["报告", "研报", "财报", "报表"],
    "research": ["整理", "总结", "综述", "调研", "检索资料", "压缩", "提炼"],
    "kb": ["知识库", "文档库", "wiki"],
    "automate": ["自动化", "工作流", "流程", "定时", "批量"],
    "code": ["代码", "编程", "调试", "debug", "重构", "脚本", "开发"],
    "data": ["数据分析", "数据", "图表", "统计", "可视化"],
    "learn": ["学习", "教学", "讲解", "教程", "入门"],
    "agent": ["agent", "智能体", "多智能体"],
    "rag": ["rag", "检索增强", "向量", "知识检索"],
}
TOPIC_HINT = ["ai", "agent", "自动化", "内容", "研究", "数据", "代码", "知识库", "skill",
              "prompt", "提示词", "rag", "workflow", "工作流", "写作", "ppt", "报告"]

DIFFICULTY_RULES = [
    ("工程向", ["docker", "kubernetes", "self-host", "本地部署", "源码编译", "微服务"]),
    ("进阶",   ["api key", "环境变量", "python", "命令行", "cli", "部署"]),
    ("中等",   ["安装", "配置", "插件", "marketplace"]),
]


# ---------- 主流程 ----------
def main():
    ap = argparse.ArgumentParser(description="指北 · Skill 候选提取（默认 DRY-RUN）")
    ap.add_argument("--input", default="jobs.example.json")
    ap.add_argument("--out", default="data/skill_candidates.json")
    ap.add_argument("--report", default="dry_run_report.json")
    ap.add_argument("--fetch", action="store_true", help="显式允许联网抓取公开内容")
    args = ap.parse_args()

    jobs, load_err = load_jobs(args.input)
    if load_err:
        print("[ERROR] " + load_err)
        sys.exit(1)

    valid_jobs, errors = validate_jobs(jobs)
    if not args.fetch:
        run_dry_run(jobs, errors, args.report)
    else:
        run_fetch(valid_jobs, errors, args.out)


def load_jobs(input_path):
    if not os.path.exists(input_path):
        return None, "找不到任务清单 %s（参考 jobs.example.json）" % input_path
    try:
        data = json.load(open(input_path, encoding="utf-8"))
    except Exception as e:  # noqa
        return None, "任务清单不是合法 JSON：%s" % e
    if not isinstance(data, list):
        return None, "任务清单必须是数组"
    return data, None


def validate_jobs(jobs):
    """Skill-first：只强制 sourceUrl + 合法 sourceType；parentProjectId 可选。"""
    valid, errors = [], []
    for i, job in enumerate(jobs):
        if not isinstance(job, dict):
            errors.append({"index": i, "reason": "job 不是对象"})
            continue
        problems = []
        if not job.get("sourceUrl"):
            problems.append("缺少 sourceUrl")
        if job.get("sourceType") not in VALID_SOURCE_TYPES:
            problems.append("sourceType 非法（应为 %s）" % "/".join(VALID_SOURCE_TYPES))
        if problems:
            errors.append({"index": i, "sourceUrl": job.get("sourceUrl", ""),
                           "reason": "; ".join(problems)})
        else:
            valid.append(job)
    return valid, errors


def run_dry_run(jobs, errors, report_path):
    """jobs 为全部任务（含校验失败的）；errors 含 index。"""
    err_idx = {e.get("index"): e for e in errors if "index" in e}
    print("=" * 56)
    print("DRY-RUN（不联网）。加 --fetch 才会抓取公开内容。")
    print("=" * 56)
    print("总任务：%d ｜ 校验错误：%d" % (len(jobs), len(errors)))
    rows = []
    for i, job in enumerate(jobs):
        st = job.get("sourceType")
        parser = PARSER_BY_TYPE.get(st, "parse_article")
        has_parent = bool(job.get("parentProjectId"))
        if i in err_idx:
            status, note = "invalid", err_idx[i].get("reason", "字段校验失败")
        elif st == "skillhub":
            status, note = "unsupported", "SkillHub 多需 JS 渲染 / 登录，--fetch 时大概率 unsupported"
        elif st == "article":
            status, note = "ready", "文章解析为轻量版；若页面无法稳定抓取，--fetch 时记 unsupported"
        else:
            status, note = "ready", "可解析"
        print("  - %-38s | type=%-13s | parser=%-20s | parent=%s | %s" % (
            (job.get("sourceUrl", "") or "")[:38], st, parser, has_parent, status))
        rows.append({"sourceUrl": job.get("sourceUrl", ""), "sourceType": st,
                     "parser": parser, "hasParentProjectId": has_parent,
                     "mode": "dry-run", "status": status, "note": note})
    report = {"totalJobs": len(jobs), "generatedAt": _now(), "jobs": rows, "errors": errors,
              "note": "未联网、未写 data/skill_candidates.json。确认后加 --fetch。"}
    write_dry_run_report(report, report_path)
    print("已写出计划：%s" % report_path)


def run_fetch(jobs, errors, out_path):
    print("=" * 56)
    print("FETCH 模式：仅抓公开内容，每请求间隔 >= %ds。" % REQUEST_INTERVAL_SEC)
    print("=" * 56)
    candidates = []
    for idx, job in enumerate(jobs):
        url = job.get("sourceUrl")
        st = job.get("sourceType")
        print("[%d/%d] 抓取 %s (type=%s)" % (idx + 1, len(jobs), url, st))
        raw, status = fetch_source(job)
        if raw is None:
            print("   跳过：%s" % status)
            errors.append({"sourceUrl": url, "reason": status})
            time.sleep(REQUEST_INTERVAL_SEC)
            continue
        print("   HTTP %s，正文 %d 字" % (status, len(raw)))
        try:
            cands = parse_skills(raw, st, job)
        except Exception as e:  # noqa 单 job 失败不中断
            errors.append({"sourceUrl": url, "reason": "解析异常：%s" % e})
            time.sleep(REQUEST_INTERVAL_SEC)
            continue
        before = len(cands)
        cands = dedupe_skills(cands)
        screened = sum(1 for c in cands if isTrueNorthSkill(c)["ok"])
        high = sum(1 for c in cands if c["riskLevel"] == "high")
        print("   候选 %d → 去重 %d ｜ 疑似达标 %d ｜ high-risk %d ｜ 全部 pending" % (
            before, len(cands), screened, high))
        candidates.extend(cands)
        time.sleep(REQUEST_INTERVAL_SEC)

    candidates = dedupe_skills(candidates)
    write_output(candidates, out_path)
    print("-" * 56)
    print("写出 %d 个候选（reviewStatus=pending）→ %s" % (len(candidates), out_path))
    if errors:
        print("失败 / 跳过 %d 个（见各 job 日志）。" % len(errors))
    print("下一步：人工复核 → 通过改 reviewed → 用 merge-reviewed-skills.py 生成 SKILL_LIBRARY 片段。")


# ---------- 抓取 ----------
def fetch_source(job):
    url = job.get("sourceUrl", "")
    fetch_url = _github_readme_url(url) if job.get("sourceType") == "github_readme" else url
    fetch_url = fetch_url or url
    try:
        import urllib.request
        req = urllib.request.Request(fetch_url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=20) as resp:
            if _looks_like_login(resp.geturl()):
                return None, "疑似跳转登录页，跳过"
            ctype = resp.headers.get("Content-Type", "")
            if not any(x in ctype for x in ("text/html", "text/plain", "markdown", "json")):
                return None, "非文本内容（%s），跳过" % ctype
            raw = resp.read(2_000_000).decode("utf-8", "ignore")
            if _looks_like_login(raw):
                return None, "页面疑似需要登录，跳过"
            return raw, resp.getcode()
    except Exception as e:  # noqa
        code = getattr(e, "code", None)
        if code in (401, 403):
            return None, "HTTP %s 需要权限，跳过" % code
        return None, "请求失败：%s" % e


def _github_readme_url(url):
    m = re.match(r"https?://github\.com/([^/]+)/([^/#?]+)", url or "")
    if not m:
        return None
    return "https://raw.githubusercontent.com/%s/%s/HEAD/README.md" % (m.group(1), m.group(2))


def _looks_like_login(text):
    t = (text or "").lower()
    return any(k in t for k in ["sign in", "log in", "请登录", "登录后", "captcha", "需要登录"])


# ---------- 解析分发 ----------
def parse_skills(raw_text, source_type, job):
    if source_type == "github_readme":
        items = parse_github_readme(raw_text, job)
    elif source_type == "skillhub":
        items = parse_skillhub(raw_text, job)
    else:
        items = parse_article(raw_text, job)
    return [normalize_skill(s, job) for s in items if s.get("name")]


def parse_github_readme(raw_text, job):
    items, install = [], _first_code_block(raw_text)
    for line in raw_text.splitlines():
        m = re.match(r"\s*(?:[-*]|#{2,4})\s+(.+)", line)
        if not m:
            continue
        text = re.sub(r"`", "", m.group(1)).strip()
        if not (4 <= len(text) <= 160):
            continue
        link = _first_url(text)
        name = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
        name = re.sub(r"\(?https?://[^\s)\]]+\)?", "", name).strip(" -·:|，。")
        if name:
            items.append({"name": name, "desc": text, "url": link, "install": install,
                          "rawText": text})
    return items


def parse_skillhub(raw_text, job):
    items = []
    for t in re.findall(r"<h[1-3][^>]*>(.*?)</h[1-3]>", raw_text, re.S):
        name = re.sub(r"<[^>]+>", "", t).strip()
        if 2 <= len(name) <= 80:
            items.append({"name": name, "desc": "", "rawText": name})
    if not items:
        sys.stderr.write("[skillhub] 可能需要 JS 渲染 / 登录，未解析到 Skill：%s\n"
                         % job.get("sourceUrl"))
    return items


def parse_article(raw_text, job):
    text = re.sub(r"<[^>]+>", "", raw_text)
    items, cur = [], None
    label = re.compile(r"(Skill\s*名称|技能|能力|适用场景|安装方式|安装|Prompt|提示词|命令|工具)[：:]\s*(.+)")
    for b in re.split(r"\n{2,}", text):
        for line in b.splitlines():
            m = label.search(line.strip())
            if not m:
                continue
            key, val = m.group(1), m.group(2).strip()
            if key in ("Skill 名称", "技能", "能力"):
                if cur:
                    items.append(cur)
                cur = {"name": val, "desc": "", "rawText": b[:400]}
            elif cur and key == "适用场景":
                cur["scenario"] = val
            elif cur and key in ("安装方式", "安装", "命令", "工具"):
                cur["install"] = val
            elif cur and key in ("Prompt", "提示词"):
                cur["prompt"] = val
    if cur:
        items.append(cur)
    return items


# ---------- 规整为候选（Skill-first 模型）----------
def normalize_skill(skill, job):
    name = (skill.get("name") or "").strip()
    desc = (skill.get("desc") or "").strip()
    text = name + " " + desc + " " + (skill.get("rawText") or "")
    st = job.get("sourceType", "other")
    risk = infer_risk(text, st)
    ref = {
        "title": job.get("sourceTitle") or job.get("sourceName") or name,
        "url": skill.get("url") or job.get("sourceUrl", ""),
        "sourceType": st,
        "sourceName": job.get("sourceName", ""),
        "sourceAuthor": job.get("sourceAuthor", ""),
        "sourceDate": job.get("sourceDate", ""),
        "extractedFrom": (skill.get("rawText") or text)[:300],
    }
    cand = {
        "id": "cand-%s" % _slug(name),
        "name": name,
        "desc": desc,
        "task": infer_task(text),
        "scenario": skill.get("scenario", ""),
        "difficulty": infer_difficulty(text),
        "input": skill.get("input", ""),
        "output": skill.get("output", ""),
        "install": skill.get("install", ""),
        "prompt": skill.get("prompt", ""),
        "tags": [],
        "whyTrueNorth": "",            # 由人工复核时填写收录理由
        "sourceRefs": [ref],
        "reviewStatus": "pending",
        "riskLevel": risk["riskLevel"],
        "note": risk.get("note", ""),
    }
    # parentProjectId 仅当 job 明确指定（来源就是项目 / Skill 集合）才带
    if job.get("parentProjectId"):
        cand["parentProjectId"] = job["parentProjectId"]
    # 收录标准筛查：始终给出建议写入 note（仍保持 pending，由人工决定）
    judge = isTrueNorthSkill(cand)
    if judge["ok"]:
        sug = "建议收录：任务、用途与来源齐全，可直接复用。"
    elif len(judge["reasons"]) <= 1:
        sug = "需人工判断：" + "；".join(judge["reasons"])
    else:
        sug = "不建议收录：" + "；".join(judge["reasons"])
    cand["note"] = (cand["note"] + " " + sug).strip()
    return cand


# ---------- 指北收录标准 ----------
def isTrueNorthSkill(candidate):
    """返回 {ok, reasons}。仅作筛查建议，不改 reviewStatus。"""
    reasons = []
    name = (candidate.get("name") or "").strip()
    desc = (candidate.get("desc") or "").strip()
    text = (name + " " + desc + " " + (candidate.get("scenario") or "")).lower()
    has_usage = any([candidate.get("install"), candidate.get("prompt"),
                     candidate.get("scenario"), candidate.get("output")])
    has_source = bool(candidate.get("sourceRefs") and candidate["sourceRefs"][0].get("url"))
    # 不收录条件
    if len(name) < 2:
        reasons.append("名称过短，疑似随口提到")
    if not desc and not has_usage:
        reasons.append("没有明确用途 / 用法")
    if not has_source:
        reasons.append("没有可追溯来源")
    if not has_usage:
        reasons.append("无安装 / 使用路径 / Prompt / 示例")
    if not any(h in text for h in TOPIC_HINT) and not candidate.get("task"):
        reasons.append("与指北定位（AI / Agent / 自动化 / 内容 / 研究 / 数据 / 代码 / 知识库）关联弱")
    if any(w in text for w in ["广告", "推广", "扫码", "限时优惠"]):
        reasons.append("疑似广告")
    if candidate.get("riskLevel") == "high" and "边界" not in text and "仅作" not in (candidate.get("note") or ""):
        # 高风险但本体没说明边界（note 里已自动加免责，这里只提示从严复核）
        reasons.append("高风险领域，需人工确认使用边界")
    return {"ok": len(reasons) == 0, "reasons": reasons}


# ---------- 推断 ----------
def infer_task(text):
    t = (text or "").lower()
    return [k for k, kws in TASK_KEYWORDS.items() if any(w.lower() in t for w in kws)]


def infer_difficulty(text):
    t = (text or "").lower()
    for level, kws in DIFFICULTY_RULES:
        if any(w in t for w in kws):
            return level
    return "新手友好"


def infer_risk(text, source_type):
    t = (text or "").lower()
    for domain, kws in RISK_KEYWORDS.items():
        if any(k.lower() in t for k in kws):
            return {"riskLevel": "high", "note": RISK_NOTE, "domain": domain}
    return {"riskLevel": "low"}


# ---------- 去重（按 normalized name；合并 sourceRefs / task）----------
def dedupe_skills(cands):
    by_key = {}
    for c in cands:
        key = _norm(c.get("name", ""))
        if not key:
            continue
        if key not in by_key:
            by_key[key] = c
        else:
            by_key[key] = _merge(by_key[key], c)
    return list(by_key.values())


def _merge(a, b):
    keep = a if len(a.get("desc", "")) >= len(b.get("desc", "")) else b
    other = b if keep is a else a
    keep["task"] = sorted(set((keep.get("task") or []) + (other.get("task") or [])))
    keep["tags"] = sorted(set((keep.get("tags") or []) + (other.get("tags") or [])))
    # 合并 sourceRefs（按 url 去重）
    refs = list(keep.get("sourceRefs") or [])
    seen = {r.get("url") for r in refs}
    for r in (other.get("sourceRefs") or []):
        if r.get("url") not in seen:
            refs.append(r)
            seen.add(r.get("url"))
    keep["sourceRefs"] = refs
    for f in ("install", "prompt", "scenario", "input", "output"):
        if not keep.get(f) and other.get(f):
            keep[f] = other[f]
    return keep


# ---------- 输出 / 工具 ----------
def write_output(items, output_path):
    _ensure_dir(output_path)
    json.dump(items, open(output_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)


def write_dry_run_report(report, report_path):
    _ensure_dir(report_path)
    json.dump(report, open(report_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)


def _ensure_dir(path):
    d = os.path.dirname(os.path.abspath(path))
    if d and not os.path.exists(d):
        os.makedirs(d)


def _slug(text):
    s = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "-", (text or "").lower()).strip("-")
    return s[:48] or "skill"


def _norm(text):
    return re.sub(r"\s+", "", (text or "").lower())


def _first_url(text):
    m = re.search(r"https?://[^\s)\]]+", text or "")
    return m.group(0) if m else ""


def _first_code_block(text):
    m = re.search(r"```[a-zA-Z]*\n(.+?)```", text or "", re.S)
    return m.group(1).strip()[:200] if m else ""


def _now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


if __name__ == "__main__":
    main()
