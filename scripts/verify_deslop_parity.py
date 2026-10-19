#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""去味合并回归比对：原稿 story-deslop  vs  sepia 编排层

断言：编排层 deslop 段贡献的 err 数 == 原稿 blocking 数（破折号已去重）。
"""
import json
import os
import subprocess
import sys

PY = sys.executable
NODE = "C:/Users/Jani/.workbuddy/binaries/node/versions/22.22.2-6/node.exe"
SK = os.path.dirname(os.path.abspath(__file__))
DEMO = "D:/Work/case_novel/oh-story-claudecode/demo/长篇/让你管账号，你高燃混剪炸全网/正文"

# 原稿 blocking 数（含 em-dash；sepia 自己查 em-dash，去重后按类型比对）
EXPECT = {
    "第011章_新任务：老兵的愿望.md": 1,
    "第012章_他们才是真正的偶像啊.md": 1,
    "第018章_全民热议.md": 1,
}


def node_blocking(f):
    r = subprocess.run(
        [NODE, os.path.join(SK, "deslop", "check-ai-patterns.js"), "--json", f],
        capture_output=True, text=True, encoding="utf-8")
    try:
        data = json.loads(r.stdout or "{}")
    except json.JSONDecodeError:
        return None, []
    b = [x for x in data.get("findings", []) if x.get("severity") == "blocking"]
    return len(b), [x["type"] for x in b]


def bridge_err(f):
    """编排层：从 lint.py 的 --json 里取出 deslop 段贡献的 err。"""
    r = subprocess.run([PY, os.path.join(SK, "lint.py"), "--json", f],
                       capture_output=True, text=True, encoding="utf-8")
    data = json.loads(r.stdout or "{}")
    errs = [i["item"] for i in data.get("items", [])
            if i.get("level") == "err" and i["item"].startswith("句式与密度·")]
    warns = [i["item"] for i in data.get("items", [])
             if i.get("level") == "warn" and i["item"].startswith("句式与密度·")]
    return errs, warns


def main():
    files = sorted(f for f in os.listdir(DEMO) if f.endswith(".md"))
    ok = True
    total_b = total_e = 0
    advisory_types = {}
    for name in files:
        p = os.path.join(DEMO, name)
        nb, types = node_blocking(p)
        errs, warns = bridge_err(p)
        # em-dash 由 sepia 自有 L1-1 负责，编排层刻意去重，故不参与一致性比对
        nb_cmp = sum(1 for t in types if t != "em-dash")
        total_b += nb_cmp
        total_e += len(errs)
        for w in warns:
            advisory_types[w] = advisory_types.get(w, 0) + 1
        mark = "OK " if len(errs) == nb_cmp else "!! "
        if len(errs) != nb_cmp:
            ok = False
        if nb or errs or warns:
            print(f"{mark}{name[:28]:<30} 原稿blocking={nb}(非破折号{nb_cmp}) 编排err={len(errs)} types={types}")

    print("\n" + "=" * 60)
    print(f"非破折号 blocking 合计：原稿 {total_b} / 编排层 {total_e}  → {'一致 ✅' if total_b == total_e else '不一致 ❌'}")
    print("（em-dash 已由 sepia 自有 L1-1 覆盖，编排层刻意去重，不计入）")
    print(f"\nadvisory 类型分布（{sum(advisory_types.values())} 条）：")
    for k, v in sorted(advisory_types.items(), key=lambda x: -x[1]):
        print(f"   {k:<28} × {v}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())