---
title: INTERSPEECH 2026 语音增强方向深挖：架构 / 问题 / 目标定位
type: topic
created: 2026-10-06
updated: 2026-10-06
tags:
  - 调研
  - trends
  - enhancement
  - interspeech
related:
  - [[2026 语音领域研究方向调研]]
  - [[wiki/topics/2026 语音增强前沿五篇比较]]
  - [[wiki_array/topics/2026 前沿声源定位五篇比较]]
---

# INTERSPEECH 2026 语音增强方向深挖

> 配套数据：`enhancement_papers_2026.csv`（168 篇逐篇分类表，含主导架构与三项目标标记）
> 上游报告：`README.md`（2026 语音领域方向总览）

## 0. 方法与口径（先看这里，数字都依赖它）

**样本构造**：从 INTERSPEECH 2026 全部 184 个 session / 1379 篇论文中，按 session 主题筛出增强相关 178 篇，逐篇抓取官方摘要页并解析全文摘要，剔除 7 篇抓取失败与 3 篇误入的非增强论文（说话人验证、ASR 系统各 1 篇），最终 **168 篇**。

| 层级 | 范围 | 篇数 |
|---|---|---|
| **A 核心增强** | 8 个增强专属 session + 1 个混合 session（Generative & SSL SE / Neural SE / LM & Codec-Token SE / Real-Time Low-Latency & Edge SE / Dereverberation, BWE & Restoration / ANC, Echo Control, Sound Zone & PLC / Speech Enhancement & Restoration / SE Architectures & Audio Front-Ends / Speech Recognition-Enhancement & Real-Time） | **62** |
| **B 多通道 / 空间 / 阵列** | Multi-Channel Beamforming & Spatial SE / Multi-Channel Processing (UAV, Radar, Hearables) / Spatial Audio 1–4 | 46 |
| **C 分离 / 目标说话人提取** | Target Speaker Extraction / AV & Generative TSE / Source Separation 1–2 | 27 |
| **D 神经编解码器** | Neural Speech Codecs / Neural Audio Codec Architectures / Speech Features & Codec | 20 |
| **E 质量 / 可懂度评估** | Quality, Intelligibility & Evaluation / Speech and Audio Quality Assessment | 13 |

**三项判定标准**（多标签，可同时成立）：

- **低延迟**：摘要明确把 latency / streaming / causal / look-ahead / low-delay 作为设计目标或约束。
- **部署 / 端侧 / 效率**：摘要明确涉及 on-device、edge、MCU、hearing aid 等硬件，或把 MACs / FLOPs / 参数量 / 内存 / RTF / 推理步数 / 量化 / 剪枝 / 蒸馏作为核心卖点。
- **声称 SOTA**：摘要出现 state-of-the-art / outperform / surpass / superior 等基准性能主张。

> 口径限制：**A 层 62 篇为逐篇人工判定**（含关键词证据核验）；B/C/D/E 层为规则判定 + 抽检。判定基于摘要而非全文，可能与论文实际侧重有偏差；"刷指标"指"以基准性能提升为主要卖点、且不涉及延迟或部署约束"，**不等于**该工作没有方法创新。

---

## 1. 架构：生成式已占半壁，且正在"少步化"

核心增强 62 篇的**主导架构**（单一归属）：

| 架构 | 篇数 | 占比 |
|---|---|---|
| **生成式模型** | **30** | **48.4%** |
| 判别式（掩蔽 / 复数谱回归 / 流式网络） | 23 | 37.1% |
| 传统 DSP / ANC / 波束成形 | 9 | 14.5% |

**生成式内部细分**（31 篇生成式，多标签）：

| 范式 | 篇数 | 代表 |
|---|---|---|
| 扩散 Diffusion / SDE | 11 | ADDSE（吸收态离散扩散 + RQDiT）、DelayGSE、SLICE、DiffVQE |
| GAN 对抗 | 7 | UFL-GAN、QC-GAN（四元数 Conformer GAN）、SCNet |
| 流匹配 / 整流流 / MeanFlow | 6 | HFMSE、PhASE-Flow、VeRe-Flow、Autonomous Rectified Flow |
| LM / 自回归 / codec token 域 | 6 | UniSE、GenSE、Post-Training SE LM、cNAC-SE、DF-Conformer+Hydra |
| 薛定谔桥 Schrödinger Bridge | 2 | Schrödinger Bridge Mamba（SBM）、EffDiffSE+ |
| 漂移模型 Drifting | 1 | DriftSE |

**三个值得注意的架构信号**：

1. **扩散正在被"一步化"改造**。经典多步扩散在这一年几乎不再作为独立贡献出现，取而代之的是把它压成 1–4 步：`Absorbing Discrete Diffusion`（非自回归）、`Schrödinger Bridge Mamba`（单步）、`EffDiffSE+`（单次迭代）、`DriftSE`（一步推前分布匹配）、`A Fast Solver for Interpolating SDE`（少 NFEs 求解器）。**这是扩散路线为了活下来必须付的代价**。
2. **流匹配成为最活跃的新范式**。标题级命中 10 篇，且**跨任务扩散**：增强（HFMSE / PhASE-Flow）、分离（AV-FlowSep / MeanFlow-TSE）、TTS（Transcript-Free Flow-Matching TTS）、codec（One-Step Token-to-Waveform with MeanFlow）。流匹配之所以流行，是因为它天然支持"少步 + 确定性 ODE"，比扩散更容易满足实时约束。
3. **骨干网络层面，Mamba/SSM 正在成为流式增强的首选**。`RT-SEMamba`（8 层因果 Mamba，25 ms 延迟 3.32 PESQ，再蒸馏到 1 层）、`SEMamba++`、`Schrödinger Bridge Mamba`、`BridgeCodec`。摘要级 Mamba 提及 8 次、标题级 4 次——绝对数量不大，但**集中在"实时/流式/低码率"这批论文里**，方向性很明确。相比之下 Transformer/Conformer 仍是通用主力（标题级 11 篇），但在低延迟场景里被 Mamba 挤压。

---

## 2. 在解决什么问题

核心增强 62 篇的问题分布（多标签）：

| 问题 | 篇数 | 占比 | 说明 |
|---|---|---|---|
| 通用去噪 | 22 | 35.5% | 仍是最大公约数，但已很少单独成篇 |
| **生成幻觉 / 保真度** | 17 | 27.4% | **2026 的新问题**：生成式方法引入的新缺陷 |
| **计算 / 内存开销** | 14 | 22.6% | 与生成式扩散的"贵"直接相关 |
| 去混响 | 10 | 16.1% | 常与去噪联合（joint denoising & dereverberation） |
| ANC / 个人声区 | 8 | 12.9% | 传统 DSP 的自留地，仍有独立 session |
| 可懂度 / 助听 | 7 | 11.3% | hearing aid / hearable / open-fit 场景 |
| 带宽扩展 / 超分 | 6 | 9.7% | 常与 codec 结合 |
| 泛化 / 域适应 | 6 | 9.7% | unseen noise、zero-shot |
| 真实场景 / 远场 | 6 | 9.7% | real-world far-field 分布失配 |
| AEC 回声消除 | 3 | 4.8% | |
| PLC 丢包隐藏 | 1 | 1.6% | |

**最关键的转变**：问题清单里出现了两个过去不存在（或极边缘）的条目——**"生成幻觉"和"计算开销"**。这两个问题都是生成式方法自己带来的副作用：

- `StuPASE: Towards Low-Hallucination Studio-Quality Generative SE`
- `DelayGSE`（消融专门验证幻觉抑制）
- `Improving DF-Conformer using Hydra for high-fidelity generative SE`
- `Post-Training Speech Enhancement Language Models with Perceptual Rewards`
- `Balancing Speech Reconstruction and Noise Suppression Using Dual-Asymmetric Loss`（防止过抑制）

也就是说：**这个领域正在为上一轮"生成式转向"还债**。第一波生成式增强把 PESQ/DNSMOS 刷上去了，代价是引入幻觉（生成不存在的内容）、过抑制（吃掉人声）、以及推理成本暴涨；2026 年的很大一部分工作就是在补这三个坑。

另一个值得注意的点：**"低 SNR / 强干扰"在核心增强里几乎不出现**（<2 篇）。这说明核心增强赛道的评测场景已经默认是"中等 SNR + 已知噪声类型"，真正难的低 SNR / 竞争说话人场景被推到了**分离 / 目标说话人提取（C 层）**和**多通道（B 层）**去解决。对本项目而言，这意味着核心增强的 SOTA 数字不能直接外推到 −5 dB babble 场景。

---

## 3. 三类目标各占多少

### 3.1 核心增强 62 篇

| 目标 | 篇数 | 占比 |
|---|---|---|
| **低延迟 / 流式 / 因果** | **13** | **21.0%** |
| **部署 / 端侧 / 效率** | **18** | **29.0%** |
| **声称 SOTA / 超越** | **47** | **75.8%** |
| — 其中**纯指标导向**（既不涉延迟也不涉部署） | **39** | **62.9%** |
| 低延迟 + 部署双目标 | 8 | 12.9% |

> 补充：另有 4 篇"一步 / 单次迭代生成"（ADDSE、SBM、DriftSE、EffDiffSE+）我计入**效率/部署**而非低延迟，因为它们压缩的是推理步数（算力），未主张算法延迟或因果性。若把这 4 篇也算作延迟导向，低延迟口径会升到 **17/62 ≈ 27%**。

### 3.2 各层级对比

| 层级 | n | 低延迟 | 部署/效率 | 声称 SOTA | 纯指标导向 |
|---|---|---|---|---|---|
| A 核心增强 | 62 | 21.0% | 29.0% | 75.8% | 62.9% |
| B+C 多通道/空间 + 分离提取 | 73 | 12.3% | 34.2% | 47.9% | 30.1% |
| D 神经编解码器 | 20 | 15.0% | **70.0%** | 35.0% | 15.0% |
| E 质量评估 | 13 | 15.4% | 7.7% | 23.1% | 15.4% |
| **A+B+C 增强生态合计** | **135** | **16.3%** | **31.9%** | **60.7%** | **45.2%** |

**读法**：

- **刷指标仍是绝对主流**：核心增强里 76% 声称 SOTA，且 **63% 完全不碰延迟和部署**。这是领域现状——大部分论文的贡献是"在 VoiceBank-DEMAND / DNS2020 上再高 0.0x PESQ"。
- **低延迟是少数派但已成建制**：核心增强 21%、整体 16%。数量不大，但 INTERSPEECH 2026 **为它单独开了一个 session**（`Real-Time, Low-Latency and Edge Speech Enhancement`），说明学术共同体已把它当作独立赛道而非附属属性。
- **部署/效率比低延迟更普遍（29% vs 21%）**，且**在编解码器方向达到 70%**——编解码器的存在意义就是低码率低算力，所以它天然是效率导向的。
- **B+C 层"三项皆无"占 26/73**，说明多通道/分离方向有相当一部分工作（HRTF 个性化、RIR 建模、声场重建、DOA）既不是刷指标也不是做部署，而是**建模/表征类研究**，不适用这三个框。
- **A 层 62 篇无一"三项皆无"**——核心增强的每一篇都至少落在三个框之一里，因为它的评测体系（PESQ/STOI/DNSMOS）天然逼着论文给出可比数字。

### 3.3 21 篇低延迟 / 部署的代表作（核心增强）

**低延迟 / 流式 / 因果（13 篇）**

| 论文 | 关键数字 / 主张 |
|---|---|
| `Latency-Configurable Streaming SE via Asymmetric Temporal Padding` | 12.5 ms 全因果下 PESQ 3.35，超过 46.5 ms 的因果 SOTA (3.27) |
| `Latency Controllable Speech Enhancement` (LCA) | 单模型支持 7 档延迟，超越各档位独立模型 |
| `RT-SEMamba` | 8 层因果 Mamba，25 ms 约束下 PESQ 3.32；蒸馏到 1 层学生 |
| `RT-Tango` | 双耳分布式实时增强，面向低功耗助听器流式部署 |
| `HALO` | 半帧率因果插件，不增加算法延迟，腾出算力加宽通道 |
| `WaveNorm` | 因果时域 AGC，49M MACs / 55 KB 内存，面向端侧 |
| `Real-Time SE on Edge Devices`（加速度计引导） | LAU-NetV2 在可穿戴 MCU 上 48.66 ms |
| `LMPAN` | 全双工 AEC+NS，480K 参数 / 126 MACs，on-device |
| `EffVOC` | 低延迟波形重建，16 ms 级路线，主观 MOS 4.17/4.15 |
| `HWB-plus` | 轻量带宽扩展，面向边缘设备实时通信 |
| `DDSN` | 物理感知双流 PLC，面向实时通信 |
| `A Causal Reference-Enhanced Keep-Speech ANC` | 因果低延迟 ANC，强调"保住人声" |
| `ANC With a Gain Constraint for Micro-Loudspeakers` | 用频响增益约束替代高通滤波，避免附加电子延迟 |

**部署 / 端侧 / 效率（18 篇，含上表 8 篇重叠）**
新增：`Schrödinger Bridge Mamba`（单步 + 竞争性 RTF，流式可行）、`EffDiffSE+`（单次迭代）、`STSR`（明确以"扩散算力限制实用"为动机）、`LavaSR`（RTF 0.0001@A100 / 0.0053@8 核 CPU）、`QC-GAN`（0.89M 参数达 PESQ 3.48）、`ABSE-NET`（开放耳式助听器 BMVDR+轻量网络）、`GSU-DBNet`（脉冲网络，394K 参数 PESQ 3.04）、`Bridging the Distribution Gap`（轻量两级 + 真实远场）、`NCPSZ`（手机漏音抑制）、`Fast Solver for Interpolating SDE`。

**共同特征**：这 21 篇里**绝大多数同时给出了参数量 / MACs / 内存 / RTF 中的至少一项**，并且**几乎不宣称"全面 SOTA"**，而是宣称"在 X 约束下达到可比/更优性能"。这与纯指标派的修辞方式有清晰区别。

---

## 4. 对本项目的结论

对照 [[wiki_low_latency/index]]（严格因果、约 2 ms 算法延迟）与 [[wiki/index]]（增强与分离）：

1. **赛道已被确认，但 2 ms 级别仍是空白**。INTERSPEECH 2026 的低延迟增强论文，算法延迟普遍落在 **12–50 ms**（12.5 / 25 / 48.66 ms 等），主流做法是"因果 + 有限 look-ahead"。**没有任何一篇在摘要里主张 2 ms 量级**。这对本项目是明确的机会位——但也提示：**学界目前认为 10 ms 级就是"低延迟"了**，2 ms 是需要自己论证的更强约束。
2. **架构选型参考**：若要压到 2 ms，Mamba/SSM（`RT-SEMamba` 路线）+ 半帧率算子（`HALO`）+ 增益约束替代滤波（`A Causal ... ANC`）是三条已被验证的思路；而扩散/流匹配即便做到单步，其单步网络通常仍是 25–40 ms 前端规模，**不构成 2 ms 候选**。
3. **评测口径要对齐**：核心增强的问题分布里"低 SNR / 强干扰"几乎缺席，说明这批 SOTA 数字的适用场景偏温和。本项目若做 −10/−5 dB babble，需要在文献里另外找 C 层（分离/提取）与 B 层（多通道）的对照，而不能直接引用核心增强的 PESQ。
4. **可直接精读的 5 篇**（按与项目相关度排序）：`RT-SEMamba`、`Latency-Configurable Streaming SE`、`HALO`、`RT-Tango`、`WaveNorm`。

---

## 5. 局限

- 判定基于**摘要**，未读全文；论文实际贡献可能与其摘要修辞不一致。
- 低延迟 / 部署 / SOTA 三项为**多标签**，一篇可同时计入多项，故各列之和大于 100%。
- "声称 SOTA"统计的是**修辞层面**的主张，不代表真的达到 SOTA；"纯指标导向"是排除法结果，其中包含方法创新显著但恰好不涉延迟/部署的工作。
- 骨干网络统计（Mamba 8 篇、Transformer 30 篇等）基于**摘要显式提及**，大量论文未在摘要中说明骨干，故为**下界**而非真实占比。
- B/C/D/E 层为规则判定 + 抽检，未逐篇人工复核，误差率估计高于 A 层。
