#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
指北 TrueNorth · 合并已复核 Skill → SKILL_LIBRARY 片段
================================================

读取 data/skill_candidates.json，只取 reviewStatus == "reviewed"，
去重、合并 sourceRefs，输出可手动复制进前端 SKILL_LIBRARY 的 JS 片段。

不修改 TrueNorth.html。请人工把片段贴进前端并自查。

用法：
  python scripts/merge-reviewed-skills.py --input data/skill_candidates.json
  python scripts/merge-reviewed-skills.py --input data/skill_candidates.json --out skill_library_snippet.js
"""

import argparse
import json
import os
import re
import sys

# 前端 SKILL_LIBRARY 会用到的字段
FIELDS = ["id", "name", "desc", "task", "scenario", "difficulty", "input", "output",
          "install", "prompt", "tags", "whyTrueNorth", "sourceRefs",
          "reviewStatus", "riskLevel", "note", "parentProjectId"]


def norm(s):
    return re.sub(r"\s+", "", (s or "").lower())


def merge(a, b):
    keep = a if len(a.get("desc", "")) >= len(b.get("desc", "")) else b
    other = b if keep is a else a
    keep["task"] = sorted(set((keep.get("task") or []) + (other.get("task") or [])))
    keep["tags"] = sorted(set((keep.get("tags") or []) + (other.get("tags") or [])))
    refs = list(keep.get("sourceRefs") or [])
    seen = {r.get("url") for r in refs}
    for r in (other.get("sourceRefs") or []):
        if r.get("url") not in seen:
            refs.append(r)
            seen.add(r.get("url"))
    keep["sourceRefs"] = refs
    for f in ("install", "prompt", "scenario", "input", "output", "whyTrueNorth"):
        if not keep.get(f) and other.get(f):
            keep[f] = other[f]
    return keep


def main():
    ap = argparse.ArgumentParser(description="合并已复核 Skill → SKILL_LIBRARY 片段")
    ap.add_argument("--input", default="data/skill_candidates.json")
    ap.add_argument("--output", "--out", dest="output", default="data/skill_library_reviewed.js")
    args = ap.parse_args()

    if not os.path.exists(args.input):
        print("[ERROR] 找不到 %s。请先 extract-skills.py --fetch 并人工复核。" % args.input)
        sys.exit(1)

    data = json.load(open(args.input, encoding="utf-8"))
    reviewed = [s for s in data if s.get("reviewStatus") == "reviewed"]
    pending = [s for s in data if s.get("reviewStatus") not in ("reviewed", "rejected")]
    rejected = [s for s in data if s.get("reviewStatus") == "rejected"]
    print("总计 %d ｜ reviewed %d ｜ pending %d ｜ rejected %d"
          % (len(data), len(reviewed), len(pending), len(rejected)))
    if not reviewed:
        print("没有 reviewed 的 Skill。请先把通过的改成 reviewStatus=\"reviewed\"。")
        return

    # 去重 + 合并 sourceRefs（按 normalized name）
    by_key = {}
    for s in reviewed:
        k = norm(s.get("name", ""))
        if not k:
            continue
        by_key[k] = s if k not in by_key else merge(by_key[k], s)
    merged = list(by_key.values())

    slim = []
    for s in merged:
        slim.append({k: s[k] for k in FIELDS if k in s and s[k] not in ("", [], None)})

    snippet = ("/* 由 merge-reviewed-skills.py 生成；人工核对后并入前端 SKILL_LIBRARY */\n"
               "const SKILL_LIBRARY_REVIEWED = "
               + json.dumps(slim, ensure_ascii=False, indent=2) + ";")
    d = os.path.dirname(os.path.abspath(args.output))
    if d and not os.path.exists(d):
        os.makedirs(d)
    open(args.output, "w", encoding="utf-8").write(snippet)
    print("已写出片段 → %s（%d 个 Skill）" % (args.output, len(slim)))
    print("-" * 56)
    print("下一步：把这些条目并入前端 SKILL_LIBRARY（已存在的同名 Skill 只合并 sourceRefs、补字段，不重复新增）。")


if __name__ == "__main__":
    main()
