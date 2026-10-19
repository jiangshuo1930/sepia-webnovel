# sepia-webnovel

中文网文写作与去AI 味技能包。面向编程 Agent（Claude Code / Codex / OpenCode等），
也可作为独立的机械校验工具使用。

目标：**写中文网文，写得不像是 AI 写的。**

## 六层结构

| 层 | 文件 | 管什么 |
|---|---|---|
| 第 0 层 | `references/state-schema.md` | 跨章台账 |
| 第 1 层 | `references/narrative-pass.md` | 架构：人物要什么、事件怎么连 |
| 第 2 层 | `references/discourse-pass.md` | 篇章：段落怎么走、读者在哪滑走 |
| 第 3 层 | `references/style-surface.md` + `zh-fiction/` | 句子表面 |
| 第 4 层 | `references/arc-pass.md` | 卷级：连着几章会不会腻 |
| 交付前 | `scripts/lint.py` | 机械校验（硬伤必须清零） |

**顺序不能颠倒。** 结构没定就抠字，等于在错的地方精雕。

## 安装

把整个目录放进你的 Agent 技能目录即可，无需依赖安装。

机械校验需要 **Python 3.8+**；完整去味检测（句式与退化）需要 **Node.js**。
缺 Node 时 `lint.py` 会自动降级，只跑 sepia 自有规则并给出提示。

## 使用

```bash
# 机械校验（默认含去味检测器）
python scripts/lint.py <章节文件>

# 只看非 OK 项 / JSON 输出 / 跳过去味检测器
python scripts/lint.py <章节文件> --quiet
python scripts/lint.py <章节文件> --json
python scripts/lint.py <章节文件> --no-deslop
```

输出带`[可直改]` / `[读上下文]` 标记：前者形态即问题可就地改，后者需读上下文再定。

## 去味检测器

`lint.py` 挂载了一套来自 [oh-story-claudecode](https://github.com/zenstory-ai/oh-story-claudecode)
（MIT）的 Node 检测器，补上退化检测与5 类 blocking 句式。

| story-deslop | lint.py | 处置 |
|---|---|---|
| `blocking` | **FAIL（必须清零）** | 就地改写，规则带护栏，不需判断 |
| `advisory` + `mechanical` | WARN `[可直改]` | 形态即问题 |
| `advisory` + `semantic` | WARN `[读上下文]` | 可能承担叙事功能，读上下文再定 |

### 7 类 blocking

| 类型 | 形态 |
|---|---|
| `not-is-comparison` | “不是 A，而是 B” |
| `voice-contrast` | “声音不大…却” |
| `negation-parade` | “没有 X，没有 Y…” / “没 X…只是 Y” |
| `reverse-not-is` | “是 A，不是 B” |
| `trailer-ending` | 章尾预告：“没人知道”“才刚刚开始” |
| `trailer-summary` | 章尾盖章过去：“这一切都结束了” |
| `em-dash` | 破折号 |

### 豁免机制

- **书级白名单**：作品根目录建 `.deslop-whitelist`，一行一条作者刻意保留的原句，
  检测时整句遮罩。只认本书，不跨书继承。
- **章内标记**：标题下写 `<!-- 去味:跳过 -->`。
  注意这是**流程标记不是豁免**——脚本照常检测；blocking 清零后删掉该行。

## 口径约定

- **引号**：正文统一用全角弯引号 `“”` 成对出现；直角 `「」` 与半角 `"` 都是硬伤。
- **台词豁免**：`“”` 内的套词不计。人物说话本来就会用“深吸一口气”“眼里闪过一丝”。
  sepia 与 deslop 同口径，避免同一段台词两套结论。
- **道具词**：钥匙 / 手机 / U盘 / 旧相册… 只做警惕提示，不当硬伤。
- **markdown 结构**：标题、表格、代码块、引用行都不是正文，两侧都不扫。

## 测试

```bash
python scripts/test_deslop.py            # 23 条：护栏行为 + 引号规范
python scripts/verify_deslop_parity.py   # 与上游原稿的一致性比对
```

## 一条纪律

**脚本只报告，永不自动改写。** 安全改法永远是上下文判断：通常删掉否定铺垫直接写肯定项，
或用动作/细节呈现。标点归一默认 `--check`，要真改必须显式 `--fix`。

## 目录

```
sepia-webnovel/
  SKILL.md                    技能主文件
  CHANGELOG.md                版本变更
  references/                 六层规则
  scripts/
    lint.py                   机械校验主入口
    deslop_bridge.py          去味检测器编排层
    test_deslop.py护栏测试
    verify_deslop_parity.py   一致性回归
    deslop/                   上游检测器（MIT，原样迁入勿改）
```

稿子不放在技能包里。技能与稿件位置无关，`lint.py` 接受任意路径。

## 许可

MIT，详见 [LICENSE](LICENSE)。`scripts/deslop/` 来自 oh-story-claudecode（MIT，原样迁入）。