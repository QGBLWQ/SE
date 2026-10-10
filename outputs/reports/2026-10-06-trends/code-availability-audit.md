---
title: INTERSPEECH 2026 语音增强方向代码开源情况核查
type: audit
created: 2026-10-07
updated: 2026-10-07
tags:
  - 调研
  - reproducibility
  - open-source
  - interspeech
related:
  - [[INTERSPEECH 2026 低延迟语音增强：问题与方法拆解]]
  - [[低延迟语音增强：近年演进、论文自陈不足与可做方向]]
  - [[wiki_low_latency/方法全景：动机·前后端·网络设计]]
---

# INTERSPEECH 2026 语音增强方向代码开源情况核查

> **核查日期**：2026-10-07
> **核查方式**：① 抓取 171 个增强相关论文的 ISCA Archive 摘要页，正则提取 `github.com / gitlab.com / huggingface.co` 链接；② 对已下载全文的 14 篇低延迟论文，从 PDF 正文（含脚注与 Code Availability 小节）提取链接；③ 对每个链接**实际访问**，解析仓库首页的文件清单，判断"有代码"还是"只有 demo/权重"。

---

## 一、结论先行

| 口径 | 数量 | 占增强池比例 |
|---|---|---|
| 抓取的增强相关论文页 | 171 | —（其中 168 篇进入分类样本） |
| **摘要层可检出仓库链接** | **11** | **6.4%** |
| 加全文层新增（仅正文给链接） | +5 | 合计 **16 篇，9.4%** |
| **其中仓库里真有可运行代码** | **12** | **7.0%** |
| 只有 demo 页 / 试听页 / 仅模型权重 | 4 | 2.3% |

**一句话**：**INTERSPEECH 2026 语音增强方向的代码开源率约 7–9%，而低延迟子集的开源率明显更高（见下节）。**

> ⚠️ **口径偏差声明**：这 16 篇是**下限而非上限**。摘要层扫描会漏掉"只在正文给链接"的论文，而我只下载了 14 篇低延迟论文的全文——正是这 14 篇贡献了 5 篇"摘要层扫不到"的。**如果给全部 168 篇都读全文，检出率一定会上升。** 因此"7–9%"这个数字的准确表述是：**能在摘要层确认的比例是 6.4%；低延迟子集（读了全文的）是 43%。**

---

## 二、低延迟子集：14 篇逐一核查

这是本项目最关心的一组，且是唯一做了全文级核查的一组。

| 论文 | 链接 | 仓库实际内容 | 判定 |
|---|---|---|---|
| **RT-SEMamba** | `github.com/RoyChao19477/RT-SEMamba` | `models/` `recipes/` `dataloaders/` `infer` `ckpts/` | ✅ **完整代码** |
| **LaCo-SENet** | `github.com/yskim3271/LaCo-SENet` | `src/` `conf/` `tests/` `requirements.txt` | ✅ **完整代码** |
| **LAU-NetV2** | `github.com/yhsong06/LAU-NetV2` | `model.py` `dataset.py` `compute_metric.py` `harmonic_vad_mask.py` | ✅ **完整代码** |
| **HALO** | `github.com/dddaniel-z/HALO` | `code/` `samples/` | ✅ **完整代码**（论文只写了 "audio samples are available"，实际连 code 一起放了） |
| **WaveNorm** | `github.com/wavenorm123/WaveNorm_AGC` | `README.md` `index.html` + 三个数据集目录，**无任何 .py** | ⚠️ **仅 demo / 基准测试页** |
| **RSE-KSANC** | `github.com/RaoLi666/RSE_KSANC` | `fig/` `wav/` `index.html` `index.css`，**无任何代码** | ⚠️ **仅试听页**（与论文"listening examples are available"表述一致） |
| RT-Tango | 无 | — | ❌ 未提供 |
| ANC-FRC | 无 | — | ❌ 未提供 |
| LMPAN | 无（只引用了 `huggingface.co/microsoft/wavlm-large`） | — | ❌ 未提供 |
| HWB-plus | 无 | — | ❌ 未提供 |
| LCA | 无 | — | ❌ 未提供 |
| EffVOC | 无 | — | ❌ 未提供 |
| OVC | 无（只引用了 `github.com/JorisCos/LibriMix` 数据集） | — | ❌ 未提供 |
| DDSN | 无 | — | ❌ 未提供 |

**低延迟子集统计：6/14 给了链接（43%），其中真有代码 4/14（29%）。**

**值得注意的三点：**

1. **`RT-SEMamba` 论文原文写的是 "The code will be publicly released at github: ..."（将来时），但仓库实际已经可访问且有完整代码。** 说明"will be released"这类表述在会议论文里经常是保守写法，**不能据此判定为"未开源"，必须实际去访问。**
2. **"给了链接"≠"有代码"。** `WaveNorm` 和 `RSE-KSANC` 两篇都把仓库链接当成开源证据写在论文里，但仓库里只有试听音频和网页。**这是当前生态里一类被低估的可复现性缺口——链接存在，但复现不了。**
3. **`HALO` 反过来**：论文只声称"audio samples"，实际连代码一起放了。所以**论文措辞与仓库内容两个方向都可能不一致**。

---

## 三、全增强池：16 篇已确认开源清单

按仓库内容分类（仅列 2026 年论文；历史锚点见第四节）。

### ✅ 有可运行代码（12 篇）

| 论文 | 方向 | 仓库 | 仓库关键内容 |
|---|---|---|---|
| RT-SEMamba | 低延迟 SE | `RoyChao19477/RT-SEMamba` | models / recipes / ckpts |
| LaCo-SENet | 延迟可配置 SE | `yskim3271/LaCo-SENet` | src / conf |
| LAU-NetV2 | 可穿戴边缘 SE | `yhsong06/LAU-NetV2` | model.py / dataset.py |
| HALO | 半帧率算子 | `dddaniel-z/HALO` | code / samples |
| HFMSE | 流匹配 SE | `xxnhq/HFSE` | model / train.py |
| AV-CA-DiffUSE | 视听扩散 SE | `cexauce/AV-CA-DiffUSE` | src / sgmse / eval |
| UniSE | LM 自回归 SE | `alibaba/unified-audio`（QuarkAudio-UniSE 子目录） | 完整子项目 |
| MSR-Codec | 神经编解码 | `herbertLJY/MSRCodec` | src / inference.py / ckpt |
| PASQA | 语音质量评估 | `lycorp-jp/PASQA` | src/pasqa / pyproject |
| URGENT-MOS | 语音质量评估 | `vvwangvv/URGENT-MOS` | urgent_mos / configs |
| ASE-TM | 主动干扰（新任务） | `ofiryaish/ASE-TM` | models / recipes / train 脚本 |
| End-Fire Robust DOA | 阵列定位 | `WwHhYy666/ULA_End_Fire_Robust_ASL` | matlab / python 工具 / 结果 |

### ⚠️ 有链接但内容不足以复现（4 篇）

| 论文 | 仓库 | 实际内容 |
|---|---|---|
| ABSE-NET | `Bream101/ABSE-NET` | README 内容仅一行标题 "ABSE-NET"，**空壳仓库** |
| RSE-KSANC | `RaoLi666/RSE_KSANC` | 试听页（fig/wav/index.html） |
| WaveNorm | `wavenorm123/WaveNorm_AGC` | demo 页 + 数据集，无代码 |
| Seed-Enh | `shangqwe123/Seed-Enh` | demo 音频 + 网页；预训练权重放在 HuggingFace（`clatter-1/Seed-Enh`），推理需借用第三方 `Plachtaa/seed-vc` |

> `Seed-Enh` 单独说明：它**释放了权重**但没放训练代码，推理要绕道另一个项目。对"能跑起来"是够的，对"能复现训练"不够。

---

## 四、库内 30 篇历史锚点：9 篇有仓库

`wiki_low_latency/sources/` 共 32 篇笔记，其中 **9 篇记录了自有仓库（28%）**。这些是比 2026 年论文更实用的**可运行基线**：

| 年份 | 论文 | 仓库 | 用途 |
|---|---|---|---|
| 2019 | DeepComplexCRN | `huyanxin/DeepComplexCRN` | 复数域 CRN 起点 |
| 2020 | PercepNet 系 | — | 无 |
| 2021 | Hybrid Continuity Loss | `zexupan/avse_hybrid_loss` | 连续性损失实现（方向 4 可用） |
| 2022 | Skip-DPCRN | `Le-Xiaohuai-speech/SKIP-DPCRN` | **平均/峰值算力差异的经典案例** |
| 2023 | Uncertainty-Aware | `sp-uhh/uncertainty-SE` | 不确定性感知（方向 4 可用） |
| 2024 | **GTCRN** | `Xiaobin-Rong/gtcrn` | **超轻量锚点**（含 `stream/` 流式实现 + LADSPA 插件） |
| 2024 | LiSenNet | `hyyan2k/LiSenNet` | 轻量基线 |
| 2025 | **FastEnhancer** | `aask1357/fastenhancer` | **多档复杂度 + ONNX 导出 + 文档站**，工程最完整 |
| 2025 | PrimeK-Net | `huaidanquede/PrimeK-Net` | 含 ckpt |
| 2025 | DISPATCH | `rlaehghks5/DISPATCH` | KD 方向唯一有代码的 |
| — | （非论文）RNNoise | `xiph/rnnoise` | 传统 DSP 工业基线 |

**其中 `GTCRN` 与 `FastEnhancer` 是本项目做"延迟账本"（方向 3）最合适的两块料**：`GTCRN` 被 4 篇论文当作锚点引用却自己零速度数字；`FastEnhancer` 自带多档复杂度和 ONNX 导出，便于做同构对比。

---

## 五、核查方法上的一个坑（值得记住）

**单次 HTTP 状态码探测不可靠。** 对 `github.com/rlaehghks5/DISPATCH` 的首次探测返回 **404**，我一度判定为"仓库已失效"，但**重复三次全部返回 200**，且仓库内有 `dispatch_DFKD.py`、`dispatch_L2.py`、LICENSE 与完整文件树。

⇒ **结论：判定一个仓库是否存在，必须 (a) 重复探测，(b) 检查页面内容（是否有文件树 payload、是否含 "Page not found"），而不能只看一次状态码。** 同理，`github.com/RoyChao19477/RT-SEMamba` 论文用将来时表述但仓库已就绪，也说明**论文措辞不能替代实际访问**。

---

## 六、对本项目的直接含义

1. **做"延迟账本"（方向 3）的料是齐的**：`GTCRN`、`FastEnhancer`、`RT-SEMamba`、`LaCo-SENet`、`HALO`、`LAU-NetV2` 六个仓库全部可访问且有完整代码，覆盖 2024–2026 三代、覆盖 Subband/全频带、覆盖固定延迟/可配置延迟。**可以立刻开工，无需向作者要代码。**
2. **方向 1（延迟旋钮 × 非对称双窗）的两个零件都有代码**：旋钮侧用 `LaCo-SENet`（`src/` + `conf/`），前端侧的非对称双窗需要自己按 `STFT-Very-Low-Latency 2022` 的描述实现（**该论文无代码**，这是方向 1 的主要工程量）。
3. **方向 2（多通道 FiLM 化）缺多通道低延迟基线代码**：`RT-Tango`（双耳 8 ms）**未开源**，这是这条路上最强基线却拿不到实现。**需要自己复现，或退回到用 `LAU-NetV2` 的单通道骨干 + 自己搭多通道前端。**
4. **方向 4（低 SNR 人声保留）的三个工具两个有代码**：`uncertainty-SE`（`network.py`）与 `avse_hybrid_loss`（`src/`）都可用；`PercepNet` 无官方代码，但 `rnnoise` 是它的开源后继，可作参考。
5. **不要依赖 `RSE-KSANC` / `WaveNorm` / `ABSE-NET` 的仓库做复现**——三者都只有 demo 或空壳。

---

## 七、局限

- 检出率 6.4%（摘要层）是**下限**，因为只对 14 篇做了全文级核查；未对剩余 154 篇读正文。
- 未检查仓库的 **License 兼容性**（`RSE_KSANC` 相关引用中出现的 CARNIVAL AGC 为 GPLv3，若借用需注意），也未检查代码是否与论文方法一致（即"代码可用"≠"代码可复现论文数字"）。
- 未核查 **HuggingFace 模型权重**的覆盖情况（`Seed-Enh`、`wavlm-large` 之外未系统扫描）。
- 仓库内容判定基于**首页文件树**，未逐个子目录展开，可能漏掉藏在子目录里的代码（反之，首页有 `.py` 也不保证能跑）。
- 状态码探测存在网络抖动，已对可疑项做重复探测，但未对全部 25 个仓库都做三次重试。
