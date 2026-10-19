"""去味检测器行为测试：正样本必须拦得住，负样本必须不误伤。

这是合并的核心保证——“照搬”不能只对原稿成立，对护栏同样成立。
每条用例都标注了 story-deslop 源码里的校准依据。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import deslop_bridge

CASES = [
    # ---- 正样本：必须命中 ----
    ("不是A而是B", "他不是愤怒，而是平静。", "err", "not-is-comparison",
     "固定句式模板，blocking"),
    ("音量反差", "声音不大，却压住了全场。", "err", "voice-contrast",
     "实战漏网 A：《万疆》20 章 0 命中"),
    ("否定排比", "没有伴奏，没有和声，没有提词器。", "err", "negation-parade",
     "同句 ≥2 个“没有X，”连排"),
    ("否定排比变体", "他没炫技，没有那种架势。他只是唱。", "err", "negation-parade",
     "先否定铺垫再“只是”收肯定"),
    ("反序对比", "是真嗓子，不是修音修出来的。", "err", "reverse-not-is",
     "实战漏网 C，not-is 的反序变种"),
    ("预告式收尾", "没人知道，这才刚刚开头。", "err", "trailer-ending",
     "文末 600 字窗口"),
    ("章尾总结体", "这一切都结束了。", "err", "trailer-summary",
     "盖章过去；文末窗口"),
    ("破折号", "他开口了——声音很低。", "err", "em-dash",
     "标点硬门禁（sepia L1-1 也查，此处应被去重）"),
    ("工程词泄漏", "他想起了细纲里写的伏笔。", "err", "meta-leak",
     "tier1 流水线术语"),

    # ---- 负样本：护栏必须放过（误伤=0 是设计目标）----
    ("either-or 不算翻转", "这不是A，就是B。", None, None,
     "“就是”的“是”是连词，不是肯定项系动词"),
    ("反问尾巴", "他不是英雄吗？", None, None,
     "反问助词尾巴，不是翻转"),
    ("确认语承接", "不是第一次来。是的，他还记得。", None, None,
     "“是的”是承接确认语"),
    ("黏着语素“沉没”", "船沉没在雾里，没人回头。", None, None,
     "前字排除：沉/淹/埋/出/隐/湮/吞/覆/漫/泯"),
    ("时间惯用语“没多久”", "没多久，没等她撑伞，他就走了。", None, None,
     "后字排除：没多久/没过多久/没等"),
    ("台词内不算", "“不是不报，是时候未到。”", None, None,
     "引号内台词豁免"),
    ("正常否定对偶", "他没哭也没闹。", None, None,
     "“不哭不闹”是正常叙述，blocking 不收"),
    ("普通“不是”", "这不是我的伞。", None, None,
     "无后接肯定翻转，不构成模板"),

    # ---- 边界：跳过标记是流程标记，不是豁免 ----
    ("台词内套词豁免", "“你深吸一口气，眼里闪过一丝复杂的神色。”\n\n她忍不住深吸一口气。", None, None,
     "弯引号内的套词是人物口语，与 story-deslop 引号遮罩同口径"),
    ("跳过标记仍照常扫", "他不是愤怒，而是平静。", "err", "not-is-comparison",
     "<!-- 去味:跳过 --> 是 Agent 流程标记：blocking 清零后删该行，"
     "脚本本身照常检测（见 SKILL.md Phase 1）"),
]


def run(text, tmp):
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
    findings, status = deslop_bridge.scan(tmp)
    if status != "ok":
        print("  !! 检测器不可用")
        return None
    return findings


# 用例正文需 >100 字，否则 check() 会走"正文过短"短路分支，L1-5 不会被求值
_FILL = "她把碗端起来，又放下，转身出了门，外头的天已经黑透了。"

QUOTE_CASES = [
    ("弯引号成对", f"“他开口。”\n\n她点头，没说话。{_FILL * 4}", "ok"),
    ("弯引号不配对", f"“他开口。\n\n她点头。{_FILL * 4}", "err"),
    ("直角引号违规", f"「他开口。」\n\n她点头，没说话。{_FILL * 4}", "err"),
    ("半角引号违规", f'"他开口。"\n\n她点头，没说话。{_FILL * 4}', "err"),
]


def check_quotes():
    import lint
    ok = failed = 0
    print("\n引号规范（sepia L1-5，全角弯引号）")
    print("-" * 62)
    for name, text, want in QUOTE_CASES:
        try:
            res, _ = lint.check(text)
            got = next((r["level"] for r in res if r["item"] == "L1-5 引号"), "err")
        except Exception as exc:
            got = f"error:{exc}"
        good = got == want
        ok += good
        failed += (not good)
        print(f"{name:<16} 期望 {want:<4} 实际 {got:<6} {'✅' if good else '❌'}")
    print(f"引号小计 {ok}/{ok + failed}")
    return failed


def main():
    tmp = os.path.join(os.environ.get("TEMP", "/tmp"), "_deslop_case.md")
    passed = failed = 0
    print(f"{'用例':<20} {'期望':<10} {'实际':<10} 结果")
    print("-" * 62)
    for name, text, want_level, want_type, why in CASES:
        findings = run(text, tmp)
        if findings is None:
            failed += 1
            continue
        errs = [f for f in findings if f["level"] == "err"]
        if want_type:
            hit = any(want_type in f["detail"] for f in errs)
            ok = hit and len(errs) >= 1
            got = f"err×{len(errs)}" + ("" if ok else f"（缺 {want_type}）")
        else:
            hit = any(want_type in f["detail"] for f in errs) if want_type else False
            ok = not errs
            got = f"err×{len(errs)}" if errs else "无命中"
        mark = "✅" if ok else "❌"
        passed += ok
        failed += (not ok)
        print(f"{name:<20} {'拦' if want_type else '放':<10} {got:<10} {mark}")
        if not ok:
            print(f"    └ 依据：{why}")
            for f in findings:
                print(f"       · {f['item']} {f['detail'][:60]}")
    print("-" * 62)
    print(f"护栏用例通过 {passed} / {passed + failed}")
    quote_failed = check_quotes()
    total_failed = failed + quote_failed
    print("=" * 62)
    print(f"总通过 {passed + 4 - quote_failed} / {passed + 4 + total_failed}")
    return 0 if total_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())