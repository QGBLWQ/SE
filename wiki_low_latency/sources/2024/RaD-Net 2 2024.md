---
title: RaD-Net 2 - 因果两阶段修复与去噪网络（知识蒸馏 + 复数轴向自注意力）
type: source
created: 2026-09-18
updated: 2026-09-18
tags:
  - speech-enhancement
  - single-channel
  - two-stage
  - repair-and-denoise
  - knowledge-distillation
  - non-causal-teacher
  - axial-attention
  - complex-valued
  - causal
  - paper-claimed-causal
  - 20ms-window-10ms-hop
  - non-2ms-frontend
source_type: paper
year: 2024
authors: Mingshuai Liu; Zhuangqi Chen; Xiaopeng Yan; Yuanjun Lv; Xianjun Xia; Chuanzeng Huang; Yijian Xiao; Lei Xie
venue: arXiv preprint (cs.SD) — arXiv:2406.07498v1，ICASSP 2024 SSI Challenge 相关
arxiv: https://arxiv.org/abs/2406.07498
local_pdf: raw/papers/low_latency_causal_se/2406.07498.pdf
evidence_policy: local_pdf_only
related:
  - [[wiki_low_latency/concepts/严格因果与算法延迟]]
  - [[wiki_low_latency/concepts/低时延前端与延迟账本]]
  - [[wiki_low_latency/concepts/低 SNR 人声保留评估]]
  - [[wiki_low_latency/concepts/2608.12099-mamba-distillation]]
  - [[wiki_low_latency/sources/2026/RT-SEMamba 2026]]
  - [[wiki_low_latency/sources/2024/Ultra-Low Latency Speech Enhancement Comprehensive Study 2024]]
  - [[wiki_low_latency/sources/2020/DCCRN Low-Latency Direction 2020]]
  - [[wiki_low_latency/sources/2022/DeepFilterNet2 2022]]
---

~~~yaml
- 论文: [RaD-Net 2: A causal two-stage repairing and denoising speech enhancement network with knowledge distillation and complex axial self-attention](2024)
  ├── 要解决什么问题: RaD-Net 的 causal 修复网络因拿不到未来信息、且卷积感受野受限，性能被卡住
  ├── 核心方法: 因果知识蒸馏（非因果修复网络当 teacher 指导因果 student）+ 去噪网络 encoder/decoder 内插入 frequency-axis complex ASA
  ├── 属于哪个分支: 单通道语音信号修复（SSI）/ 两阶段 repair+denoise / 复数谱 / 因果 KD
  ├── 输入/输出: degraded complex spectrum → Stage1 修复复谱 → Stage2 去残留噪声 → iSTFT 得 restored speech
  ├── 关键trick: 让 teacher 与 student **共享全部参数设置，唯一差别是 TFCM 的 padding 因果与否**——把"未来信息"变成可蒸馏的纯因果差异
  ├── 数据集: DNS5 子集（约 400h clean speech + 181h noise, 48kHz）；增强模拟器造 1200h 训练 + 30h 评测；DNS5 含 GSM/OPUS/AAC/AMR-NB/AMR-WB 五类 codec
  ├── 对比了谁: Noisy、Stage-1、Stage-1 Large、Stage-1 Non-causal、Stage-1+KDLarge、Stage-1+KDNon-causal、RaD-Net、RaD-Net+ASA、RaD-Net 2；另在 ICASSP 2023 blind set 对比 Gesper
  ├── 性能上限: RaD-Net 2 在 ICASSP 2024 SSI blind set 得 DNSMOS SIG/BAK/OVRL = 3.41/4.15/3.20，比 RaD-Net 的 3.34/4.10/3.10 高 **+0.10 OVRL**；SIGMOS SIG/OVRL = 3.69/3.27
  ├── 参数量: 修复网络 2.21M（Large 3.54M）；RaD-Net 4.00M；RaD-Net+ASA 3.97M；RaD-Net 2 3.97M
  ├── 消融关键发现: ①KD-Non-causal 优于 KD-Large（3.09 vs 3.04 OVRL）说明**未来信息的质量比 teacher 的容量更值钱**；②ASA 单独 +0.04 OVRL，KD+ASA 合计 +0.10 OVRL
  ├── 遗留问题(你的机会): 前端 20ms 窗 + 10ms hop，两阶段串行延迟**论文完全未报告**；因果性只是论文级声称；无 RTF/p99/RAM/量化；DNSMOS 的 BAK 已接近天花板（4.15）无 SIG-BAK trade-off；无 SNR 分层、无 false-suppression、无 ASR WER、无 F0/prosody
  └── 跟哪篇像: [[wiki_low_latency/sources/2020/DCCRN Low-Latency Direction 2020]]、[[wiki_low_latency/sources/2026/RT-SEMamba 2026]]、[[wiki_low_latency/sources/2022/DeepFilterNet2 2022]]
~~~

# RaD-Net 2: A causal two-stage repairing and denoising speech enhancement network with knowledge distillation and complex axial self-attention

> Mingshuai Liu, Zhuangqi Chen, Xiaopeng Yan, Yuanjun Lv, Xianjun Xia, Chuanzeng Huang, Yijian Xiao, Lei Xie（ASLP@NPU + ByteDance），arXiv:2406.07498v1 [cs.SD]，11 Jun 2024。

> [!warning] PDF 转换质量与阅读说明
> 原 PDF 共 **5 页**（arXiv 版，双栏 ICASSP 模板，含 Fig.1 架构图、Fig.2 ASA 模块图、Table 1 盲测结果表、Table 2 2023 盲测对比表、Table 3 与参考文献）。
>
> **本文抽取的实际问题（已核对 txt 后据实记录）**：
> 1. **公式严重碎片化**——Eq. (1) 的三个频域损失（$L_{sc}$、$L_{log-mag}$、$L_{asym}$）在 txt 中被拆成左右两栏交错的长串（第 183-195 行），加上下标丢失，**无法从 txt 可靠还原原始排版**；Eq. (2) 的 $L_G$ 与 $L_{FM}$ 同样被压成散行；
> 2. **公式编号与图片标题混入正文**——`Figure 1: The architecture of RaD-Net 2.` 出现在第 173 行、`Figure 2: The architecture of the Complex ASA module.` 出现在第 247 行，恰好插在正文段落中间，容易误读为正文句子；
> 3. **Fig.1 / Fig.2 的框图文本被拆散并错位**——Stage 1 / Stage 2 的模块标签（`Real Decoder`、`Imag Decoder`、`FU Module`、`FD Module`、`STCM`、`Complex Feature Encoder/Decoder`、`Complex ASA`、`Dense Block`、`Complex Sub-pixel Conv2d`）以极长空白分隔的形式散落在第 72-173 行，**无法从中确定模块的真实连接顺序**；
> 4. **Table 1 的列对齐在 txt 中保留完好**（第 306-321 行），这是本文抽取质量最好的部分，数值已逐行核对；
> 5. **论文页码/页眉标注缺失**——txt 中无 `\newpage` 痕迹，无法从 txt 判断 Table 1 究竟落在第几页；
> 6. **`QK^T` 与 `dp`/`dq` 记号在 Eq. (5) 文中自相矛盾**——文字写 "where $d_p$ denotes the dimension of the queries $Q$"，但公式里的分母写作 $\sqrt{d_q}$，且分母的 $d$ 在 txt 中断开成一个孤立的 `q`（第 290-293 行）。
>
> **本页做的处理**：
> - **已按 txt 原文完整核对**：Table 1 全部 9 行 × 11 列数值、Table 2 全部 3 行数值、第 3.2 节全部超参数（窗长/hop/STFT length/通道数/dilation/kernel/优化器）。
> - **公式只保留 txt 中可被明确识别的部分**；Eq. (1)(2)(7)(8) 中符号边界不清的分项，本页**按语义标出但明确标注识别状态**，不补写。
> - **框架图结构未被可靠还原**——本页对 Fig.1/Fig.2 的描述**仅限 txt 中明确出现的模块名与正文文字说明**，不推断连接拓扑。原论文第 2 页 Figure 1（架构）与第 2 页 Figure 2（Complex ASA）需回查原 PDF。
> - **PDF 未给出的信息一律不补写**：无算法延迟数值、无 RTF、无硬件、无训练 epoch 数、无 batch size、无采样率与样本级时序口径（⚠️ 论文只说 "sampled at 48kHz" 指数据，**未说明 STFT 的 20ms/hop 10ms 对应哪个采样率**）。

## 1. 他们为什么这么做？（motivation）

### 1.1 任务与对象

本文研究的任务不是经典意义上的"从加性噪声里恢复干净语音"，而是 **ICASSP Speech Signal Improvement (SSI) Challenge** 定义的**语音信号修复**：输入是经过真实通信链路（编解码、网络丢包、硬件限制）处理后的 **degraded speech**，失真类型是复合的——论文列举为 coloration、discontinuity、loudness、noisiness、reverberation。

论文明确写出两阶段分工的动机（Introduction）：

> "the first-stage module is adopted for noise suppression. Then, in the second stage, the speech enhanced by the first stage is restored to higher-quality speech signals."

但在 SSI 场景下，RaD-Net 系列实际采用的分工**与此相反**——先修复、再去噪。论文对 RaD-Net 原始框架的描述是：

> "a two-stage Repair-and-Denoising network (RaD-Net) … a complex mapping-based model named COM-Net is applied in the **repairing** stage, while a complex masked-based model called S-DCCSN is adapted in the **denoising** stage."

信号流为（论文第 2 节，逐句可核）：

$$
x(t)\ \xrightarrow{\ \text{STFT}\ }\ X_0(f,\tau)
\ \xrightarrow{\ \text{Stage 1: RepNet}\ }\ \hat X_1(f,\tau)
\ \xrightarrow{\ \text{Stage 2: DenNet}\ }\ \hat X_2(f,\tau)
\ \xrightarrow{\ \text{iSTFT}\ }\ \hat s(t),
$$

其中 $x(t)$ 是 degraded waveform，$X_0$ 是其复数谱，$\hat X_1$ 是修复网络输出的"相对高质量复数谱"，$\hat X_2$ 是去噪网络输出，$\hat s(t)$ 是最终 restored speech。

### 1.2 论文动机：为什么 Causal 模型打不过 Non-causal

论文的动机陈述非常直接，**这是全篇最重要的一句话**（Introduction 第 2 段）：

> "the performance of the repairing network is limited without accessing future information. In addition, due to the constrained receptive field of convolution layers, the denoising network module's complex feature encoder/decoder could not effectively capture long-range relations between features."

即论文识别出**两个彼此独立的瓶颈**：

| 瓶颈 | 出在哪一阶段 | 论文的对策 |
|---|---|---|
| **拿不到未来信息** | Stage 1 修复网络（生成任务，非因果天然更强） | 因果知识蒸馏（非因果 teacher → 因果 student） |
| **卷积感受野受限** | Stage 2 去噪网络的 CFE/CFD | 在 encoder/decoder 中插入 frequency-axis complex ASA |

论文对第一条瓶颈的证据是经验性的、也是全文的核心假设：

> "For generation tasks, the performance of the model is influenced by their ability to access future information, resulting in **non-causal models outperforming causal models**."

### 1.3 与本 Wiki 方向的关系

> [!warning] RaD-Net 2 与本 Wiki 约 2 ms 方向的关系：**远距离参照，不是合格系统**
> 必须诚实说明三点：
> 1. **前端是 20 ms 窗 + 10 ms hop**（论文第 3.2 节明文："a Hanning window with a **20ms frame length** and a **10ms frame shift**. The STFT length is **960**"）。这比本 Wiki 的约 2 ms 目标**高一个数量级**；
> 2. **两阶段是串行级联**——Stage 1 的输出必须完整交给 Stage 2 才能开始，因此**两阶段的算法延迟是累加的**，而论文**完全没有报告任何延迟数值**（既无公式，也无表格列，见第 2.2 节审计表）；
> 3. **任务口径不同**——本文面向通信链路修复 + 全频带感知质量（DNSMOS/SIGMOS），**不面向低 SNR 下的弱语音保留**。DNSMOS BAK 已经到 4.15（接近满分 5），说明评测集里噪声本身就不是主要敌人。
>
> 因此 RaD-Net 2 在本库中的定位是：**"如何用 KD 把未来信息因果地灌进 causal 模型"的最强方法学范例**，以及 **"两阶段架构 + 复数注意力"的参照系**；而不是 2 ms 讨论中的竞争者。

## 2. 之前的人怎么做不了？（limitation → gap）

### 2.1 既有路线的局限与本文 gap

| 既有路线 | 论文指出的局限 | 本文要补的缺口 |
|---|---|---|
| 经典 SE（codebook [1]、Wiener [2]、NMF [3]） | 论文仅在 Introduction 列举为历史方法，**未评论其局限** | 由 DNN 方法整体取代（论文未展开对比） |
| DNN 单阶段 SE（[4] Conv-TasNet、[5] DCCRN） | "these DNN-based methods often induce **additional distortions** to the speech while suppressing noise" | 用两阶段拆分"修复"与"去噪"两种不同性质的操作 |
| 两阶段策略 [6][7][8] | 论文指出这些是已有思路，**未指出局限** | 沿用两阶段框架 |
| RaD-Net（前作 [15]） | ⭐ "**failure to use future information** and **constraint receptive field of convolution layers** limit the system's performance" | 用因果 KD 补第一个缺口、用 complex ASA 补第二个缺口 |
| 对抗训练（RaD-Net 已用） | 论文未批评，**予以保留** | 不变 |

本文的 gap 可以一句话概括：

> **在必须因果的实时通信场景下，修复网络因为读不到未来帧而质量受限；而已有的 causal SE 文献没有给出"把非因果教师的能力因果地转移给因果学生"的具体做法与消融证据。**

### 2.2 延迟与因果审计表

> [!note] 本节的关键方法学点：**这是本库中"teacher-student 因果性差异被论文最干净地控制住"的一篇**
> 论文原文（第 2.1 节）：
> > "Note that the teacher and the student model **share the same parameter settings**. The only difference is that the **TFCM modules in the teacher model are non-causal while being causal in the student model**."
>
> 这意味着 Table 1 中 `Stage-1 Non-causal` 与 `Stage-1 + KD_Non-causal` 的差距，**几乎可以全部归因于"是否用非因果教师做蒸馏"这一个变量**（参数量同为 2.21M）。这在 KD 论文里是很少见的干净对照。

| 审计项 | PDF 证据 | 所属对象 | 本 Wiki 判定 |
|---|---|---|---|
| **采样率** | 数据 "sampled at **48kHz**"；STFT length = 960 | 全部 | ⚠️ **论文未明确说 STFT 的采样率**。若按 48 kHz 算，960 samples = 20 ms ✔ 与 20ms 窗自洽；若按 16 kHz 算则 960 samples = 60 ms ✘ 与 20ms 矛盾。**因此 960 应指 48 kHz 下的点数**，但论文**未写明**，本页不代为断定 |
| **STFT window** | **20 ms**（Hanning） | teacher + student | 远超约 2 ms；这是本文最硬的延迟上界证据 |
| **hop** | **10 ms** | teacher + student | 50% overlap |
| **STFT length** | **960**，得 **481-dim** 谱特征 | teacher + student | 与 20 ms@48kHz 自洽 |
| **time path padding（student）** | TFCM 用 **causal padding** | Stage 1 student（+ Stage 2） | **`paper-claimed-causal`**，论文级证据 |
| **time path padding（teacher）** | TFCM 用 **non-causal padding** | Stage 1 teacher | **`non-causal`**（仅训练用，不参与推理） |
| **frequency path** | Stage 2 的 complex ASA **沿频率轴**做 self-attention | Stage 2 | ⚠️ 论文只说 "along the frequency axis"；**未说明是否需要整帧全部频率 bin**。若必须等完整帧，则与 hop 对齐即可、不额外引入跨帧 look-ahead；**但论文未给出这一澄清**，标 ⚠️ |
| **Stage 2 是否 causal** | 论文**从未对 Stage 2 使用 "causal" 一词** | Stage 2 | ⚠️ **Stage 2 的因果性论文未声明也未证明**。S-DCCSN 源自 S-DCCRN [21]，其 decoder 结构与 look-ahead 未在本文展开 |
| **两阶段串行延迟** | **论文完全未报告** | 全系统 | ❌ **缺失**。这是本文对本 Wiki 最关键的缺口——20 ms 窗 + 10 ms hop 的两级串行，**理论算法延迟至少是单级的 2 倍量级**，论文却无任何数字 |
| **state 缓存 / 流式设计** | 论文**未提及任何 streaming state、warm-up 或 reset** | 全系统 | ❌ **缺失** |
| **compute** | 论文**未报告 RTF / FLOPs / MACs** | 全系统 | ❌ **缺失**。仅有参数量（M） |
| **end-to-end** | ADC/DMA、I/O buffer、DAC、capture-to-playback 均未报告 | 全系统 | ❌ **未验证** |

**因果性判定汇总**：

| 对象 | 判定 | 依据 |
|---|---|---|
| Stage 1 student（修复网络，causal） | **`paper-claimed-causal`** | "TFCM modules … being causal in the student model"；无逐层 padding certificate |
| Stage 1 teacher（修复网络，non-causal） | **`non-causal`** | "TFCM modules in the teacher model are non-causal" |
| Stage 1 Large（3.54M，另一 teacher 候选） | **`paper-claimed-causal`** | 论文称其为 "large **causal** repairing network" |
| Stage 2（去噪网络 S-DCCSN + ASA） | ⚠️ **未声明** | 论文全文未对 Stage 2 使用 causal 表述 |
| 全系统 | **不可标为 strict_causal** | 两阶段串行延迟未报告 + Stage 2 因果性未声明 |

### 2.3 Latency ledger（延迟账本）

| 项目 | 论文证据 | 证据边界 |
|---|---|---|
| 分析窗 / hop | 20 ms Hanning / 10 ms | 明确（第 3.2 节） |
| STFT length | 960 → 481 维谱 | 明确；采样率未明示（见上表 ⚠️） |
| 单级算法延迟 | **未报告** | ❌ 论文无 $L_s-P$ 或 look-ahead 表述 |
| 两阶段累加延迟 | **未报告** | ❌ **最关键缺口** |
| look-ahead | **未报告** | ❌ 缺失 |
| 参数量 | 修复网络 2.21M / Large 3.54M；RaD-Net 4.00M；+ASA 3.97M | 明确（Table 1） |
| RTF / FLOPs / MACs | **全部未报告** | ❌ 缺失 |
| p50/p95/p99、目标硬件 | **未报告** | ❌ 缺失 |
| warm-up / reset / 长流稳定性 | **未报告** | ❌ 缺失 |
| 端到端 capture-to-playback | **未报告** | ❌ 缺失 |

> [!contradiction] "causal" 一词在本文中的覆盖范围不清
> 论文标题、摘要、贡献列表都使用 "**causal** two-stage … network"，但正文中**只有 Stage 1 的 TFCM padding 被明确说明为 causal**：
> - 标题层级：`RaD-Net 2: A causal two-stage repairing and denoising speech enhancement network`；
> - 摘要层级：`a causality-based knowledge distillation is introduced in the first stage`；
> - 正文层级：Stage 1 的 TFCM 用 causal padding，Stage 2 无任何因果陈述。
>
> **读者容易从标题推断"整个两阶段系统是因果的"，但论文的证据只覆盖 Stage 1。** 这是本页读出的一个重要的表述—证据不匹配问题，建议在引用时只声称 "Stage 1 的修复网络为 causal"。

## 3. 这个做法核心 trick 是什么？

### 3.1 整体骨架（仅还原 txt 中明确出现的模块）

> [!question] 架构图的还原边界
> Fig.1 在 txt 抽出中模块标签被拆散并错位（第 72-173 行），**本页不推断连接拓扑**。下面只列出**正文文字明确提到**的模块及其归属，连接关系以正文描述为准。

| 阶段          | 模块                                                                                                     | 论文正文依据                                                                                                       |
| ----------- | ------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------ |
| Stage 1 修复  | **COM-Net**（来自 TEA-PSE [17]）                                                                           | "we employ COM-Net from TEA-PSE as the backbone of the repairing network"                                    |
| Stage 1 编码器 | 3 × **FD layer**（frequency down-sampling）                                                              | "the encoder consists of three frequency down-sampling (FD) layers"                                          |
| FD layer 内部 | **GateConv** → **cumulative layer norm** → **PReLU** → **TFCM** [18]                                   | 同上段逐句可核                                                                                                      |
| Stage 1 中间  | 4 × **S-GTCM**（stacked gated temporal conv modules）                                                    | "we apply four stacked gated temporal convolutional modules (S-GTCM)"                                        |
| Stage 1 解码器 | 3 × **FU layer**（mirror 结构，GateConv 换成 **Tr-GateConv**）                                                | "The FU layer uses a mirror structure and replaces the GateConv with a transposed gated convolutional layer" |
| Stage 2 去噪  | **S-DCCSN**（S-DCCRN [21] 的变体）                                                                          | "a variant of S-DCCRN [21] named S-DCCSN is applied as the denoising network"                                |
| Stage 2 组件  | **CFE**（complex feature encoder）+ **CFD**（complex feature decoder）+ sub-band module + full-band module | "S-DCCSN is composed of four parts"                                                                          |
| Stage 2 新引入 | **Complex ASA**（插在 CFE 与 CFD 中）                                                                        | "we apply the complex ASA module in the CFE and CFD"                                                         |

论文提到 Stage 2 为降算力做了 depthwise separable convolution 替换（"To reduce the computational cost, we replace convolution layers with depthwise separable convolution layers"）。

### 3.2 Trick A：因果知识蒸馏——把"未来信息"变成纯 padding 差异

**这是本文真正的核心 trick。** 论文把 teacher 与 student 的差异压缩到**一个可观测、可控制的变量**上：

> "Convolution layers with **non-causal padding and causal padding** are adopted in the TFCM modules of the teacher and student model, respectively. Note that the teacher and the student model **share the same parameter settings**. The **only difference** is that the TFCM modules in the teacher model are non-causal while being causal in the student model."

三段式训练流程（论文第 2.1 节结尾，逐句可核）：

~~~text
① 训练 non-causal 修复网络 → 冻结参数
        ↓
② 预训练 causal 修复网络（student），得到初始 student
        ↓
③ 用冻结的 non-causal teacher 对预训练 causal student 做知识蒸馏
~~~

> [!note] 为什么这个设计比 RT-SEMamba 的 progressive KD 更"干净"
> [[wiki_low_latency/sources/2026/RT-SEMamba 2026]] 的 teacher（8-layer）与 student（1/2-layer）**深度不同**，因此 KD 收益混杂了"层数差距"与"蒸馏监督"两个变量。
> RaD-Net 2 的 teacher 与 student **参数量完全相同（各 2.21M）、只差 padding 方向**——这使得 `Stage-1` vs `Stage-1+KD_Non-causal` 的差距**几乎完全隔离出"从未来信息中蒸馏"的净收益**。
> 这是本库中 KD 消融设计最干净的一例。

### 3.3 Trick B：复数轴向自注意力（Complex ASA）

论文指出 Stage 2 的问题与对策：

> "To overcome the limitation of the constraint receptive field, the **complex ASA along the frequency axis** is adapted in the second stage. Compared to pixel or patch-level attention in computer vision, the ASA [18] can improve the network's ability to capture **long-range relations between features** while **reducing the cost of memory and computation**."

ASA 模块结构（论文第 2.2 节）：三个复数卷积层分别生成 $Q,K,V$。论文给出的 Q/K/V 计算式（Eq. 4）：

$$
\begin{aligned}
Q &= (W_R^{Q}(Z_R) - W_I^{Q}(Z_I)) + j\,(W_R^{Q}(Z_I) + W_I^{Q}(Z_R)),\\
K &= (W_R^{K}(Z_R) - W_I^{K}(Z_I)) + j\,(W_R^{K}(Z_I) + W_I^{K}(Z_R)),\\
V &= (W_R^{V}(Z_R) - W_I^{V}(Z_I)) + j\,(W_R^{V}(Z_I) + W_I^{V}(Z_R)),
\end{aligned}
\tag{4}
$$

符号含义：

- $W_R^{\bullet}$、$W_I^{\bullet}$：复数卷积层 $W$ 的**实部层**与**虚部层**；
- $Z_R$、$Z_I$：复数输入 $Z$ 的实部与虚部；
- $j$：虚数单位；
- 这正是复数乘法 $(a+jb)(c+jd)=(ac-bd)+j(ad+bc)$ 的展开——**每个"复数卷积层"实际由两个实数卷积层组合实现**。⚠️ 该式的括号与下标在 txt 中已核对，形式可靠。

注意力计算（Eq. 5）：

$$
\operatorname{ComplexASA}(Q,K,V) = \operatorname{softmax}\!\left(\frac{|QK^T|}{\sqrt{d}}\right)V,
\tag{5}
$$

- $|QK^T|$：对复数注意力矩阵**取模（绝对值）**；
- $\operatorname{softmax}(\cdot)$：作用在取模后的**实数**矩阵上；
- $V$：复数 value，因此输出仍为复数。

> [!question] Eq. (5) 的记号矛盾（txt 已核对，矛盾属实）
> 论文正文写 **"where $d_p$ denotes the dimension of the queries $Q$"**，但公式分母在 txt 中呈现为 $\sqrt{d_q}$（且 $q$ 被换行断成孤立字符）。
> **这是论文自身的记号不一致，不是抽取错误**。本页在公式中统一写作 $d$，并在此说明符号原文歧义。

复数矩阵乘法（Eq. 6）：

$$
QK^T = (Q_R K_R^T - Q_I K_I^T) + j\,(Q_R K_I^T + Q_I K_R^T).
\tag{6}
$$

论文说明 softmax-on-absolute-value 的做法**受 D2Former [22] 启发**：

> "Inspired by the complex attention operation of D2Former [22], the **softmax function is employed on the absolute values of the complex matrix** to compute the complex ASA."

### 3.4 损失函数

> [!warning] Eq. (1)(2) 的识别状态
> txt 中 Eq. (1)(2) 的三/两个分项被拆成左右栏交错的长串（第 183-226 行），**下标（如 $L_{sc}$、$L_{log\text{-}mag}$、$L_{asym}$）与边界均无法从 txt 可靠还原**。下面的书写形式是按论文正文**逐字描述**整理的，**公式的排版细节需回查原 PDF**。

论文第 2.1 节的频域损失由三项组成，**论文原文的逐字描述**是："The frequency-domain loss consists of the **spectral convergence loss** $L_{sc}$ [19], the **L1 loss of the logarithmic magnitude** $L_{log\text{-}mag}$, and the **asymmetric loss** $L_{asym}$"：

$$
L_{sc} = \frac{\lVert X - \hat X\rVert_F}{\lVert \hat X\rVert_F},\qquad
L_{log\text{-}mag} = \lVert \log(X) - \log(\hat X)\rVert_1,
\tag{1a}
$$

$$
L_{asym} = \lVert h(X^{0.5} - \hat X^{0.5})\rVert_2^2,\qquad
h(x) = \begin{cases} 0, & x \le 0\\ x, & x > 0\end{cases}
\tag{1b}
$$

- $X$、$\hat X$：**训练 teacher 时**为 clean speech 与 restored speech 的幅度谱；**蒸馏阶段**为 **teacher 的 restored speech** 与 **student 的 restored speech** 的幅度谱（论文明确说明这一双重语义）；
- $\lVert\cdot\rVert_F$：Frobenius 范数；
- $h(\cdot)$：**单边 ReLU**，只惩罚 $X > \hat X$（即欠估计）的项，**不惩罚过估计**——这正是 "asymmetric" 的含义；
- $X^{0.5}$：幅度谱的**幂律压缩**（指数 0.5）。

> [!note] $L_{asym}$ 的双重语义是本文 KD 设计的核心机制
> 蒸馏阶段 $X$ 换成 teacher 的恢复谱、$\hat X$ 换成 student 的恢复谱后，$h(X^{0.5}-\hat X^{0.5})$ **只惩罚 student 幅度低于 teacher 的地方**。
> 也就是说：**这条损失在告诉 student "你压得比 teacher 更狠的地方要补回来"**——方向上与"防止过抑制"一致，但本文并未从这个角度分析它。

对抗损失（Eq. 2，论文第 2.1 节）：

$$
L_G = \mathbb{E}_{(\hat s, s)}\big[(D(s)-1)^2 + (D(\hat s))^2\big],
\tag{2a}
$$

$$
L_{FM} = \mathbb{E}_{(\hat s, s)}\left[\sum_{i=1}^{M}\frac{1}{N_i}\lVert D_i(s) - D_i(G(\hat s))\rVert_1\right].
\tag{2b}
$$

- $s$、$\hat s$：**训练 teacher 时**为 clean speech 与 restored speech；**蒸馏阶段**为 **teacher 的 restored speech** 与 **student 的 restored speech**；
- $D$：判别器；$M$：每个判别器的层数；$N_i$：第 $i$ 层特征数；
- ⚠️ Eq. (2) 在 txt 中散落，**求和上限 $M$ 与 $N_i$ 的位置需回查原 PDF 确认**。

Stage 1 总损失（Eq. 3）：

$$
L_1 = L_{sc} + L_{log\text{-}mag} + 0.5\,L_{asym} + L_G + 2\,L_{FM}.
\tag{3}
$$

**权重 $0.5$ 与 $2$ 为论文明文给出**。

Stage 2 的损失（Eq. 7-8）：

$$
L_{si\text{-}snr} = 20\log_{10}\frac{\lVert (\hat s^T s / s^T \hat s)\cdot s\rVert}{\lVert s - (\hat s^T s / s^T \hat s)\cdot s\rVert},
\tag{7a}
$$

$$
L_{plc} = \lVert X^{0.5}e^{j\varphi_X} - \hat X^{0.5}e^{j\varphi_{\hat X}}\rVert_2^2 + \lVert X^{0.5} - \hat X^{0.5}\rVert_2^2.
\tag{7b}
$$

- $L_{si\text{-}snr}$：尺度不变信噪比（**论文把它写成比值取对数，注意这与惯常的"能量比"写法在符号上略有出入，但形式在 txt 中可辨**）；
- $L_{plc}$：**power-law compressed loss**，第一项约束复谱（含相位 $\varphi$），第二项约束幅度。

预训练与微调两阶段的总损失（Eq. 8）：

$$
L_{2\text{-}pre} = L_{si\text{-}snr} + L_{plc} + L_{asym},
\tag{8a}
$$

$$
L_2 = L_{si\text{-}snr} + L_{plc} + L_{asym} + L_G + 2L_{FM}.
\tag{8b}
$$

### 3.5 判别器：生成质量的"外部裁判"

论文引入两类判别器（第 2.3 节）：

| 判别器 | 结构 | 论文明文 |
|---|---|---|
| **MRD** [23]（multi-resolution） | **6** 个子判别器，输入为不同 STFT 参数生成的幅度；每个子判别器 **7** 层卷积；除最后一层外均用 weight norm + LeakyReLU | 逐句可核 |
| **MBD** [24]（multi-band） | 不同 STFT 参数的复谱分成 **5** 个子带，送入 **3** 个子判别器；每个子判别器用 **5** 个并行卷积模块处理子带；每个卷积模块为 **5** 层卷积 + weight norm | 逐句可核 |

> [!note] 判别器是"全频带修复"任务的特权
> MRD 的 6 个子判别器使用**不同 STFT 参数**、MBD 跨 5 个子带——这些设计**只有在非实时、全频带、整段处理的训练流程里才划算**。
> **在约 2 ms 的严格因果流式场景中，这类多分辨率/多带判别器无法直接移植**（它们需要整段信号与多次变换）。这是本文方法学向本方向迁移时的主要障碍之一。

### 3.6 核心 trick 判断

**三个 trick 的贡献排序（依据 Table 1 的增量）**：

| Trick | 增量（DNSMOS OVRL） | 判断 |
|---|---|---|
| **KD（非因果 teacher）** | Stage-1 3.02 → +KD 3.09，**+0.07** | ⭐ **单笔最大** |
| **ASA** | RaD-Net 3.10 → +ASA 3.14，**+0.04** | 次之 |
| 两者叠加 | 3.10 → RaD-Net 2 **3.20**，**+0.10** | 与各自增量之和（0.07+0.04=0.11）基本一致 → **两个 trick 近似独立可加** |

**真正关键的是 Trick A（因果 KD）**，理由有三：

1. 单笔增量最大（+0.07 OVRL vs ASA 的 +0.04）；
2. 它**换掉的是 teacher 的选择**而不是加模块——`Stage-1 + KD_Large`（3.04）甚至**低于无 KD 的其它因果配置**，说明"随便找个大 teacher"没用，**必须是大且非因果的 teacher** 才有效；
3. 论文摘要与贡献列表把 KD 放在**第一条**（"In the repairing stage, we introduce a causality-based knowledge distillation strategy…"），ASA 放第二条。

## 4. 实验里哪个消融最关键？

### 4.1 数据与训练设置

| 项目 | 论文设置 |
|---|---|
| 数据来源 | **DNS5 数据集**的子集 |
| clean speech | 约 **400 小时** |
| noise clips | **181 小时**，sampled at **48 kHz** |
| 模拟器 | ICASSP 2024 SSI Challenge 发布的 **data synthesizer**（模拟真实通信系统处理流） |
| 数据增强 | 除 GSM codec 外，额外引入 **OPUS、AAC、AMR-NB、AMR-WB** 四种开源 codec |
| 增强后规模 | **1200 小时**训练 + **30 小时**评测 |
| 窗 / hop | Hanning，**20 ms** / **10 ms** |
| STFT length | **960** → **481** 维谱特征 |
| 修复网络通道 | 所有 GConv/TrGConv = **64**（Large 版 = **80**） |
| GConv/TrGConv stride & kernel | 频率轴 **(4,1)**，时间轴 **(5,1)** |
| TFCM（标准） | **3** 层 depthwise dilated conv，dilation **{1,2,4}**，kernel **(3,5)** |
| TFCM（Large） | **4** 层 depthwise dilated conv，dilation **{1,2,4,8}** |
| S-GTCM | **4** 层 GTCM，dilated conv kernel = 5，dilation **{1,2,5,9}** |
| 去噪网络通道 | sub-band / full-band = **{16,32,32,32,64,64}** |
| 去噪网络 conv | kernel **(5,2)**，stride **(2,1)** |
| CED/CFD | 通道 **32**，DenseBlock 深度 **5** |
| ASA | hidden channels = **16** |
| STCM hidden | **64** |
| 优化器 | **AdamW** [25]，初始 lr = **0.0002**，每 epoch 乘 **0.999** 衰减 |
| 训练 epoch / batch size | **未报告** |
| 采样率（STFT 口径） | ⚠️ **未明确**（见 2.2 节） |

### 4.2 Table 1：ICASSP 2024 SSI Challenge 盲测集（已逐行核对）

> 图表位置：**原论文第 3 页 Table 1**（DNSMOS 与 SIGMOS 分数）。⚠️ 本页**未生成图片资产**（撰写时无截图工具），下表为逐行文字转录，与上表内容一致；如需原样截图，请主 agent 统一处理渲染与嵌入。

| Model | Para. (M) | DNSMOS SIG | DNSMOS BAK | **DNSMOS OVRL** | COL | DISC | LOUD | NOISE | REVERB | SIGMOS SIG | SIGMOS OVRL |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Noisy | – | 3.00 | 3.57 | 2.62 | 3.09 | 3.89 | 3.55 | 3.44 | 3.70 | 3.05 | 2.54 |
| Stage-1 | 2.21 | 3.30 | 4.01 | 3.02 | 3.53 | 4.01 | 4.07 | 4.25 | 4.21 | 3.45 | 3.03 |
| Stage-1 Large | 3.54 | 3.34 | 4.05 | 3.08 | 3.58 | 4.04 | 4.05 | 4.31 | 4.25 | 3.49 | 3.09 |
| **Stage-1 Non-causal** | 2.21 | **3.43** | 4.05 | **3.16** | 3.73 | 4.19 | 4.14 | 4.34 | 4.27 | **3.72** | **3.32** |
| Stage-1 + KD_Large | 2.21 | 3.31 | 4.01 | 3.04 | 3.55 | 4.03 | 4.06 | 4.27 | 4.22 | 3.47 | 3.06 |
| **Stage-1 + KD_Non-causal** | 2.21 | 3.36 | 4.02 | **3.09** | 3.63 | 4.06 | 4.05 | 4.29 | 4.19 | 3.54 | 3.10 |
| RaD-Net | 4.00 | 3.34 | 4.10 | 3.10 | 3.51 | 4.04 | 4.10 | 4.41 | 4.31 | 3.52 | 3.12 |
| RaD-Net + ASA | 3.97 | 3.36 | 4.13 | 3.14 | 3.51 | 4.05 | 4.12 | 4.48 | 4.36 | 3.59 | 3.17 |
| **RaD-Net + KD + ASA (RaD-Net 2)** | **3.97** | **3.41** | **4.15** | **3.20** | 3.62 | 4.09 | 4.11 | **4.56** | **4.42** | 3.69 | 3.27 |

> [!note] 表中"causal 系统内部最高分"的判定
> 论文表注写明："**Among all the causal systems, the highest scores are highlighted below.**"
> 按此规则，被高亮的应是 **RaD-Net 2**（SIG 3.41 / BAK 4.15 / OVRL 3.20）——它是表中所有 causal 系统里三项最高的。
> 注意 `Stage-1 Non-causal` 虽然 SIG/OVRL 更高（3.43/3.16），但它**不是 causal 系统**，不参与该高亮规则；且它在 RaD-Net 2 出现后已不再是最高的。

### 4.3 Table 2：ICASSP 2023 SSI Challenge 盲测集（已逐行核对）

| Model | SIG | BAK | OVRL |
|---|---:|---:|---:|
| Noisy | 2.89 | 3.45 | 2.46 |
| Gesper（2023 挑战赛第 1 名） | 3.45 | 4.12 | 3.20 |
| **RaD-Net 2** | **3.47** | **4.13** | **3.22** |

### 4.4 哪个消融最能隔离方法贡献？

**三个层次的对照，干净程度递减**：

#### A. ⭐ 最干净：`Stage-1` vs `Stage-1 + KD_Non-causal`（同为 2.21M）

| 变量 | Stage-1 | Stage-1 + KD_Non-causal | Δ |
|---|---:|---:|---:|
| 参数量 | 2.21M | **2.21M** | 0 |
| 架构 | causal TFCM | **同上** | 0 |
| 前端 | 20ms/10ms | **同上** | 0 |
| 数据/训练 | 同 | **同上** | 0 |
| **蒸馏监督** | 无 | **有（非因果 teacher）** | ⭐ **唯一变量** |
| DNSMOS OVRL | 3.02 | **3.09** | **+0.07** |
| SIGMOS SIG | 3.45 | **3.54** | **+0.09** |
| SIGMOS OVRL | 3.03 | **3.10** | **+0.07** |

**+0.07 OVRL 可以干净地归因于"从非因果 teacher 蒸馏未来信息"**。

#### B. ⭐ 次干净且最有信息量：`KD_Large` vs `KD_Non-causal`（同为 2.21M student）

| Teacher | 参数量 | DNSMOS OVRL | SIGMOS SIG | 结论 |
|---|---:|---:|---:|---|
| 无（Stage-1 基线） | – | 3.02 | 3.45 | – |
| **KD_Large**（因果、3.54M） | 3.54M | **3.04** | 3.47 | 几乎无增益（+0.02） |
| **KD_Non-causal**（非因果、2.21M） | 2.21M | **3.09** | 3.54 | **+0.07** |

> [!note] 本文最有信息量的负结果
> **一个参数量更大（3.54M vs 2.21M）但仍然是因果的 teacher，蒸馏效果明显不如一个参数量更小但非因果的 teacher。**
>
> 这直接支持了论文的核心假设——**"未来信息"本身才是 student 缺的东西，而不是"更大的容量"**。如果 KD 的收益只是"更多参数的知识"，那么 3.54M 的因果 teacher 应该更有用；事实相反。
>
> 这条对照是本文对 KD 文献最有价值的贡献，**也是迁移到本库 2 ms 方向时最需要注意的一点**：在 2 ms 场景下设计 teacher，**优先保证 teacher 能看未来**（即便它是一个"小模型 + 大步幅回看"的设计），而不是优先堆容量。

#### C. 中等干净：`RaD-Net` vs `RaD-Net + ASA` vs `RaD-Net 2`

| 对照 | 参数量 | 变量 | Δ OVRL |
|---|---:|---|---:|
| RaD-Net → RaD-Net + ASA | 4.00M → **3.97M** | 只加 ASA（参数量还略降） | **+0.04** |
| RaD-Net + ASA → RaD-Net 2 | 3.97M → **3.97M** | 只加 KD | **+0.04** |
| RaD-Net → RaD-Net 2 | 4.00M → **3.97M** | ASA + KD | **+0.10** |

论文明确说明参数量是被**刻意对齐**的：

> "In addition, we adjust the parameter settings to ensure that the denoising network with ASA and the denoising network without ASA maintain **approximately the same computational complexity**."

⚠️ 注意论文说的是 "**computational complexity**"（计算复杂度），但表里给的是 **参数量（Para. M）**——**本文没有给出 FLOPs/MACs**，所以"计算复杂度相同"这一声明**在表内无法独立验证**，只能看到参数量接近。这是本文消融设计的一个证据缺口。

#### D. ❌ 不干净的对照

- **`Stage-1 Non-causal`（3.16 OVRL）vs `RaD-Net 2`（3.20 OVRL）**——**这不是"因果 vs 非因果"的对照**，因为两者架构、阶段数、参数量（2.21M vs 3.97M）全都不同。不能据此说"因果系统超越了非因果系统"。
- **Table 2 的 Gesper vs RaD-Net 2**——Gesper 是 2023 挑战赛系统、RaD-Net 2 在 **2024** 数据上训练，两者**训练数据与挑战赛年份不同**，不能直接横比。

### 4.5 SIGMOS 的逐维度分析（论文的重要补充证据）

论文对 SIGMOS 七个维度做了归因分析，**这是本文最有价值的细粒度证据**：

> "1) The **repairing network can improve each dimension in SIGMOS** of the degraded speech, while the **denoising network mainly improves NOISE and REVERB**."

用 Table 1 验证这条主张（Stage-1 → RaD-Net）：
- NOISE：4.25 → 4.41（**+0.16**）；
- REVERB：4.21 → 4.31（**+0.10**）；
- DISC：4.01 → 4.04（+0.03）；
- LOUD：4.07 → 4.10（+0.03）；
- COL：3.53 → **3.51**（**−0.02**，**去噪网络反而让 coloration 变差**）。

✔ **论文的主张在 NOISE/REVERB 上得到支持，但 COL 维度出现退化——论文没有讨论这一点。**

第二条主张：

> "2) The **non-causal repairing network achieves the best performance in SIGMOS**, while **not performing as well on DNSMOS**."

用 Table 1 验证：
- Stage-1 Non-causal 的 SIGMOS SIG = **3.72**（表中最高）、OVRL = **3.32**（表中最高）；
- 但它的 DNSMOS OVRL = 3.16，**低于 RaD-Net 2 的 3.20**。

论文对此的解释是**指标口径差异**：

> "The DNSMOS and SIGMOS are designed to evaluate **wide-band speech and full-band speech**. In the blind test set, some speech utterances **missed high-frequency components**. Therefore, the SIGMOS evaluates the quality of **generated high-frequency components that DNSMOS can not access**."

即：**SIGMOS 衡量的是"生成出来的高频内容"，而这些高频内容可能根本不在原始信号里**——SIGMOS 在这里奖励的是**带宽外推能力**，不完全是"保真"。

> [!warning] 这是本文一个需要注意的证据解读问题
> 如果按 SIGMOS SIG 排序，`Stage-1 Non-causal`（3.72，**非因果**）> `RaD-Net 2`（3.69，因果）。
> 论文用"评测指标口径不同"来解释，并援引论文自己的观察："The above analysis indicates that **future information is a significant factor in the generation task**."
>
> 但这样一来，**本文最强的"因果 KD"证据其实依赖 DNSMOS OVRL 的 +0.07，而 SIGMOS 反而显示非因果系统更优**。两个指标给出了方向不同的信号，**论文未做统计检验，也未讨论这一张力**。

### 4.6 人声保留 / 低 SNR 证据边界

> [!warning] 本文的人声保留证据**极不完整**，且**评测集的设计决定了它不可能充分**
>
> **PDF 中完全不存在**以下证据：
> - ❌ **无任何 SNR 分层**——没有 −10/−5/0/5 dB；评测集是 ICASSP SSI blind set，SNR 分布未知；
> - ❌ **无 babble / 竞争说话人 / 瞬态噪声分层**——SSI 挑战赛的失真主要是 **codec + 网络损伤**，**不是加性噪声**；这是任务口径的根本差异；
> - ❌ **无 false-suppression 指标**；
> - ❌ **无 SPP / VAD 校准**；
> - ❌ **无 ASR WER**；
> - ❌ **无 F0 / formant / prosody continuity**；
> - ❌ **无 voiced energy 保留率**；
> - ❌ **无主观听测**（DNSMOS/SIGMOS 都是非侵入式预测指标）。
>
> **本文对"人声保留"最接近的证据是 DNSMOS SIG 和 SIGMOS 的维度分解**：
> - DNSMOS **SIG 3.41**（RaD-Net 2 vs RaD-Net 3.34，+0.07）——有改善 ✔；
> - SIGMOS **COL 3.62**（vs RaD-Net 3.51，**+0.11**）——coloration 改善明显 ✔；
> - 但 **COL 在 Stage-1 → RaD-Net 的过渡中曾下降 0.02**，说明**去噪阶段有引入 coloration 的风险**（论文未讨论）。

### 4.7 计算量与部署证据

| 项目 | 本文状态 |
|---|---|
| 参数量 | ✔ 全部给出（2.21M / 3.54M / 4.00M / 3.97M） |
| FLOPs / MACs | ❌ **未报告** |
| RTF | ❌ **未报告** |
| p50/p95/p99 | ❌ **未报告** |
| 峰值 RAM / SRAM | ❌ **未报告** |
| 量化精度 | ❌ **未报告** |
| 目标硬件 | ❌ **未报告** |
| deadline miss / underrun | ❌ **未报告** |
| 端到端 capture-to-playback | ❌ **未报告** |

**本文是纯"质量—参数量"论文，零部署证据。** 这与 [[wiki_low_latency/sources/2024/Ultra-Low Latency Speech Enhancement Comprehensive Study 2024]] 提出的"必须同时报告窗口、模型容量和 MACs"的要求相差很远。

## 5. 这个方向还剩什么问题没解决？（future work / limitation）

### 5.1 论文自己承认的局限

> [!warning] 论文**没有 future work 章节**，也**几乎没有自陈任何局限**
> 第 5 节 Conclusions 只有一段，全部是正面总结：
> > "In this paper, we extend the two-stage neural network RaD-Net to RaD-Net 2. In the first stage, a causality-based knowledge distillation strategy is introduced… Then in the second stage, we introduce the complex axial self-attention module…"
>
> 全文唯一接近"承认不足"的表述出现在**结果分析**中（第 4 节）：
> > "The **non-causal repairing network achieves the best performance in SIGMOS**, while **not performing as well on DNSMOS**."
>
> 这是一个**结果层面的观察**，不是对方法的局限陈述。**作者对"因果 KD 仍未追平非因果模型"这一核心事实，没有在结论中做出任何说明。**

### 5.2 本 Wiki 审计出的缺口

| 缺口 | 本文状态 | 需要补的证据 |
|---|---|---|
| ⭐ **两阶段串行延迟** | **论文完全未报告** | 这是本文对本 Wiki 最关键的缺口：20ms 窗 + 10ms hop 的两级串行，算法延迟至少是单级的 2 倍量级；需明确 $L_{\text{total}} = L_{\text{stage1}} + L_{\text{stage2}} + L_{\text{interface}}$ 与阶段间的缓冲策略 |
| ⭐ **Stage 2 的因果性** | **论文从未声明** | 标题声称 "causal two-stage"，但 Stage 2 无任何因果陈述；需逐层审计 S-DCCSN 的 decoder padding 与 look-ahead |
| ⭐ **前端距约 2 ms 差一个数量级** | 20 ms 窗 + 10 ms hop | 本文是"远距离参照"，不可作为 2 ms 候选 |
| **采样率与样本级时序** | 只说数据 48 kHz，**未说 STFT 采样率** | 需给出 STFT 的采样率、帧锚点、每帧可读样本范围 |
| **strict causality certificate** | 只有 "TFCM modules … being causal" | 逐层检查右侧 padding、cumulative layer norm 的统计窗口、GTCM/STCM 的方向、ASA 的频率轴范围 |
| **RTF / p99 / 目标硬件** | **全部未报告** | 无任何部署证据 |
| **RAM / SRAM / 功耗 / 量化** | **全部未报告** | 4M 参数的两阶段模型在边缘设备上不可行，需量化与内存测量 |
| **warm-up / state reset / 长流稳定性** | **未报告** | 两阶段级联的状态管理比单阶段更复杂，尤其 Stage 1 输出的分布会漂移 |
| **训练超参** | epoch / batch size **未报告** | 影响可复现性 |
| **统计显著性** | 无方差、无置信区间、无多次运行 | **RaD-Net 2 vs RaD-Net 的 +0.10 OVRL 需要显著性检验**；DNSMOS 预测器本身的误差量级可能就在这个范围 |
| **FLOPs / 计算复杂度** | 论文说"same computational complexity"但**只给了参数量** | "计算复杂度相同"的声明在表内无法验证 |
| **SIGMOS 与 DNSMOS 的方向冲突** | 论文用口径差异解释，**未做进一步分析** | 两个指标给出方向不同的信号（SIGMOS 偏好非因果），需要更细的维度级分析 |
| **COL 维度退化** | Stage-1 → RaD-Net 时 COL 下降 **0.02**，**论文未讨论** | 去噪阶段引入 coloration 的风险 |
| **SNR 分层** | **完全缺失** | −10/−5/0/5 dB |
| **噪声类型分层** | **完全缺失**（SSI 任务的失真不是加性噪声） | babble、竞争说话人、瞬态、未见噪声 |
| **人声保留指标族** | 只有 DNSMOS SIG + SIGMOS 维度 | false-suppression、SPP/VAD、ASR WER、F0/formant/prosody、voiced energy |
| **SIG–BAK trade-off** | **BAK 从 4.01 升到 4.15 的同时 SIG 从 3.30 升到 3.41**，方向上无冲突；但 BAK **已接近 4.15/5 的天花板**，抑制噪声已不是瓶颈 | 需要一个**噪声更难的测试集**才能验证 SIG–BAK 权衡 |
| **代码/模型开源** | **PDF 中未提供代码仓库链接** | 可复现性缺口 |
| **"因果"一词的覆盖范围** | 标题/摘要暗示两阶段因果，证据只覆盖 Stage 1 | 表述—证据不匹配，引用时需谨慎 |

### 5.3 与本库 KD 论文的矛盾点

> [!contradiction] 本库现有 4 篇 KD 论文对"teacher 应该选什么"给出**部分冲突**的答案
>
> | 论文 | Teacher 因果性 | Teacher 容量 | Student 因果性 | KD 收益 |
> |---|---|---|---|---|
> | [[wiki_low_latency/sources/2024/Distil-DCCRN 2024\|Distil-DCCRN (2024)]] | ❌ 非因果（Uformer/Conformer） | 8.82M → 1.10M | ⚠️ 声称 causal，证据不足 | +0.27 NB-PESQ |
> | [[wiki_low_latency/sources/2023/Two-Step Knowledge Distillation for Tiny SE 2023\|Two-Step KD (2023)]] | ✅ **因果** | – | ✅ causal conv | 论文称两步法更优 |
> | [[wiki_low_latency/sources/2026/RT-SEMamba 2026\|RT-SEMamba (2026)]] | ✅ **因果**（8-layer causal cTF-Mamba） | 2.74M → 1.05M | ✅ 因果 | +0.12 PESQ |
> | **RaD-Net 2 (2024)** | ❌ **非因果** | 2.21M → 2.21M（**同容量**） | ✅ 论文级 causal | +0.07 OVRL |
>
> **四篇的 teacher 选择**：
> - Distil-DCCRN 与 RaD-Net 2 用**非因果 teacher**；
> - Two-Step KD 与 RT-SEMamba 用**因果 teacher**。
>
> **没有一篇论文讨论过"teacher 是否应该因果"这个问题本身。**
>
> **RaD-Net 2 的 Table 1 实际上给出了这个问题的第一个直接证据**：在同一个 student 上，**非因果 teacher（2.21M）明显优于因果 teacher（3.54M）**。但论文**没有把这一发现提炼成一个可推广的结论**，也**没有与其他 KD 论文对话**。

> [!note] 一个可以直接做的实验（本页读出的机会）
> **RT-SEMamba 的 progressive KD 中，teacher 是因果的（8-layer causal cTF-Mamba）。如果按 RaD-Net 2 的发现，把 teacher 换成同容量的非因果 cTF-Mamba，student 的收益应该会更大。**
> 这是一个**用现成组件就能验证的假设**，且能同时回答"teacher 的因果性是否是 KD 收益的独立变量"——本库中尚无任何论文回答过。

### 5.4 对本方向的可迁移启示

1. **"只差 padding 的 teacher-student 对"是设计 KD 消融的最佳范式**——直接借用，可以最干净地隔离蒸馏监督的贡献；
2. **teacher 的选择优先级：能看未来 > 容量大**——RaD-Net 2 的 KD_Large vs KD_Non-causal 是硬证据；
3. **两阶段级联在 2 ms 场景下需要重新论证**——延迟是累加的，且 Stage 1 的输出会成为 Stage 2 的输入分布漂移来源；
4. **MRD/MBD 多分辨率判别器无法移植到流式**——如果要在 2 ms 场景用对抗训练，需要重新设计单帧可用的判别器；
5. **SIGMOS 式的"生成高频"奖励会掩盖保真问题**——在低 SNR 人声保留评估中，**必须使用侵入式指标 + 分层分析**，不能只看非侵入式预测 MOS。

## 6. 本论文在库中的位置关联（cross-reference matrix）

| 关系 | 库中页面/论文 | 关联与边界 |
|---|---|---|
| ⭐ **同分支竞品（KD + 因果性，最强关联）** | [[wiki_low_latency/sources/2026/RT-SEMamba 2026]] | **两篇是本库中最直接的"因果 KD"对照**：<br>① **Teacher-student 因果性配置相反**：RaD-Net 2 是 **非因果 teacher + 因果 student**；RT-SEMamba 是 **因果 teacher + 因果 student**；<br>② **容量配置相反**：RaD-Net 2 的 teacher/student **参数量完全相同（2.21M/2.21M），只差 padding**；RT-SEMamba 是 **8-layer (2.74M) → 1/2-layer (1.05/1.29M)**，差深度；<br>③ **蒸馏层级**：RaD-Net 2 是**输出级**（用 $L_{sc}/L_{log\text{-}mag}/L_{asym}/L_G/L_{FM}$ 对齐 teacher 与 student 的 restored speech）；RT-SEMamba 是**输出级 + 中间表征 + progressive ramp-up**；<br>④ **前端**：RaD-Net 2 **20ms/10ms**；RT-SEMamba **25ms/6.25ms**——两者都远超约 2 ms；<br>⑤ ⭐ **两篇都对"teacher 因果性"这个问题给出了证据但都没意识到**：RaD-Net 2 的 Table 1 显示非因果 teacher 更优（3.09 vs 3.04 OVRL），而 RT-SEMamba 只用了因果 teacher。**这两篇的交叉正是本库最明显的实验机会** |
| ⭐ **概念页（KD 一致性）** | [[wiki_low_latency/concepts/2608.12099-mamba-distillation]] | 该页展开 RT-SEMamba 的 progressive KD 公式（$\gamma(k)$ ramp-up、feature aggregation）；与 RaD-Net 2 的输出级 KD 是**两种不同的层级设计**。⚠️ 该概念页**以 RT-SEMamba 为目标论文**，不含 RaD-Net 2 内容 |
| ⭐ **前身/基石（架构来源）** | [[wiki_low_latency/sources/2020/DCCRN Low-Latency Direction 2020]] | RaD-Net 2 的 Stage 2（S-DCCSN）源自 **S-DCCRN [21]**，而 S-DCCRN 是 DCCRN 的 super wide band 变体；DCCRN 也是本文参考文献 [5]。**关键边界**：DCCRN 原论文的 decoder 使用未来帧、look-ahead 37.5 ms；本文 Stage 2 **未声明因果性**（见 2.2 节）。**因此"RaD-Net 2 是因果系统"这一声明不能从 DCCRN 谱系自动继承** |
| **延迟基准** | [[wiki_low_latency/sources/2024/Ultra-Low Latency Speech Enhancement Comprehensive Study 2024]] | 该研究把窗长 / look-ahead / 计算 / 质量分开审计，并明确 **"25–40 ms 前端模型不得作为 2 ms 合格系统"**。**RaD-Net 2 的 20 ms 窗落在同一被批评区间内**，且它**连 MACs 都没报告**——是该研究提出的审计清单的一个典型反面案例 |
| **同分支竞品（低复杂度流式）** | [[wiki_low_latency/sources/2022/DeepFilterNet2 2022]] | DeepFilterNet2 走**嵌入式实时 + deep filtering**路线（明确报告 RTF 与目标硬件），RaD-Net 2 走**离线训练 + 大参数量 + 无部署证据**路线。**两者是低时延方向的两个极端**：前者算力优先，后者质量优先。⚠️ 关联为**路线对比**，需用户确认是否值得显式链接 |
| **同分支竞品（复数谱）** | [[wiki_low_latency/sources/2020/DCCRN Low-Latency Direction 2020]] | 见上（既是前身也是竞品） |
| **同分支竞品（多阶段）** | [[wiki_low_latency/sources/2023/Two-Step Knowledge Distillation for Tiny SE 2023]] | 该文用**因果 teacher + 两步法**（先纯 KD 再纯监督），与 RaD-Net 2 的**单步加权蒸馏**形成对照。⚠️ 两者**互未引用**，关联为**方法学类比** |
| **跨分支类比（频带分解）** | [[wiki_low_latency/sources/2023/FSB-LSTM 2023]] | FSB-LSTM 用 full-band/sub-band 集成建模；RaD-Net 2 的 Stage 2 也有 sub-band/full-band 模块级联。⚠️ **架构思路相近但任务不同**，疑似关联 |
| **跨分支类比（复数注意力）** | [[wiki_low_latency/concepts/2008.00264-complex-phase-enhancement]] | 复数相位增强概念页（源自 DCCRN）；RaD-Net 2 的 complex ASA 是该概念在**注意力维度**的延伸（用复数 Q/K/V + softmax on modulus）。⚠️ 该概念页未包含 ASA 内容 |
| **概念页（延迟审计）** | [[wiki_low_latency/concepts/严格因果与算法延迟]] | RaD-Net 2 是**"标题声称 causal、证据只覆盖一阶段"**的典型案例，可用于说明为何需要逐层 certificate |
| **概念页（延迟账本）** | [[wiki_low_latency/concepts/低时延前端与延迟账本]] | 本文提供了一条**"算法延迟与计算延迟双重未报告"**的极端案例：有窗长/hop，但**连 RTF/MACs 都没有** |
| **概念页（人声保留）** | [[wiki_low_latency/concepts/低 SNR 人声保留评估]] | 本文**无 SNR 分层、无 false-suppression、无 ASR WER**；且评测集（SSI blind set）的失真类型是 **codec/网络损伤而非加性噪声**，因此**结构上就无法回答低 SNR 保真问题** |
| **概念页（超低时延基准）** | [[wiki_low_latency/concepts/2409.10358-ultra-low-latency-benchmark]] | 该概念页定义的统一账本与审计字段；RaD-Net 2 可放入该框架作为"未闭合"的一行 |
| ⚠️ **疑似关联，需用户确认** | [[wiki_low_latency/sources/2021/Noise Suppression Losses 2021]] | 该文研究**损失函数对语音失真与 ASR 的影响**；RaD-Net 2 的 $L_{asym}$（只惩罚欠估计）在设计思路上与该主题相关，但**本文未引用该文，也未做失真/ASR 分析** |
| ⚠️ **疑似关联，需用户确认** | [[wiki_low_latency/sources/2022/Hybrid Continuity Loss 2022]] | 连续性损失/过抑制主题；RaD-Net 2 的 SIGMOS DISC（discontinuity）维度与之相关（3.89 → 4.09，见 Table 1 的 Noisy → RaD-Net 2），但**本文未把 DISC 与过抑制文献联系** |
| ⚠️ **疑似关联，需用户确认** | [[wiki_low_latency/sources/2024/SlowFast-SSM 2024]] | SlowFast-SSM 关注**低 MAC 的状态空间调制**；RaD-Net 2 关注**因果 KD**。两者都以"降低小模型质量损失"为目标，但路径完全不同（架构 vs 训练）。**无直接引用关系** |

> [!question] 关联不确定性
> - 与 [[wiki_low_latency/sources/2026/RT-SEMamba 2026]] 的关联是**本页认定的最强关联**：两篇都是"因果 KD"，且 teacher 因果性配置相反——但**两篇互未引用**。这是**方法学类比 + 潜在实验机会**，不是文献谱系。
> - 与 [[wiki_low_latency/sources/2020/DCCRN Low-Latency Direction 2020]] 的关联**有 PDF 级证据**（参考文献 [5] DCCRN、[21] S-DCCRN），强关联。
> - 与 [[wiki_low_latency/sources/2023/Two-Step Knowledge Distillation for Tiny SE 2023]] 的关联为**方法学类比**（两种 KD 训练范式），⚠️ 两者互未引用。
> - 与 [[wiki_low_latency/sources/2023/FSB-LSTM 2023]]、[[wiki_low_latency/sources/2022/DeepFilterNet2 2022]]、[[wiki_low_latency/sources/2024/SlowFast-SSM 2024]] 的关联为**同维度并列**（低复杂度/频带分解）。⚠️ **疑似关联，需用户确认**。
> - 本页**未使用** [[wiki_low_latency/sources/2023/GCFSnet 2023]] 与 [[wiki_low_latency/sources/2021/DPCRN Low-Latency Direction 2021]] 作为关联项：GCFSnet 是**双耳/多麦 + 链路**方向，DPCRN 是**双路径复数循环**方向，与本文的"SSI 修复 + 因果 KD"**没有可站得住的关联依据**，故不强行链接。

## 7. 一句话总结"江湖地位"

~~~text
2024 | SSI 语音修复 + 因果知识蒸馏 | 用"teacher 与 student 参数完全相同、唯一差别是 TFCM padding 因果与否"的极干净对照，首次直接证明"非因果 teacher 比参数量更大的因果 teacher 更值钱"（KD_Non-causal 3.09 vs KD_Large 3.04 OVRL），并在 Stage 2 用 frequency-axis complex ASA 补足卷积感受野，最终在 ICASSP 2024 SSI blind set 上以 +0.10 OVRL 超过前作 RaD-Net 并压过 2023 冠军 Gesper → 成为"因果 KD"方法学的标杆与"两阶段架构"的参照系；但其 20ms 窗 + 10ms hop 的前端、两阶段串行延迟完全未报告、Stage 2 因果性从未声明、零部署证据，使它在约 2ms 严格因果方向上只能作为"远距离方法学参照"，而非合格系统。
~~~

## 参考资料

- [arXiv:2406.07498](https://arxiv.org/abs/2406.07498)
- 本地原件：raw/papers/low_latency_causal_se/2406.07498.pdf
- 原 PDF 共 5 页，arXiv:2406.07498v1 [cs.SD]，11 Jun 2024
- 作者单位：Audio, Speech and Language Processing Group (ASLP@NPU), School of Software, Northwestern Polytechnical University, Xi'an + ByteDance, China（通讯作者：Lei Xie）
- 论文参考文献 [15]：Liu, Chen, Yan, Lv, Xia, Huang, Xiao, Xie, "RaD-Net: A repairing and denoising network for speech signal improvement," ICASSP 2024（**前作**）
- 论文参考文献 [17]：Ju, Rao, Yan, Fu, Lv, Cheng, Wang, Xie, Shang, "TEA-PSE: Tencent-ethereal-audio-lab personalized speech enhancement system for ICASSP 2022 DNS Challenge," ICASSP 2022（**COM-Net 来源**）
- 论文参考文献 [18]：Zhang, Yu, Wang, Wei, "Multi-scale temporal frequency convolutional network with axial attention for speech enhancement," ICASSP 2022（**TFCM 与 ASA 来源**）
- 论文参考文献 [21]：Lv, Fu, Xing, Sun, Xie, Huang, Wang, Yu, "S-DCCRN: Super wide band DCCRN with learnable complex feature for speech enhancement," ICASSP 2022（**S-DCCSN 来源**）
- 论文参考文献 [22]：Zhao & Ma, "D2Former: A fully complex dual-path dual-decoder conformer network using joint complex masking and complex spectral mapping for monaural speech enhancement," ICASSP 2023（**复数注意力启发**）
- 论文参考文献 [23]：Jang, Lim, Yoon, Kim, Kim, "UnivNet: A neural vocoder with multi-resolution spectrogram discriminators for high-fidelity waveform generation," arXiv:2106.07889（**MRD 来源**）
- 论文参考文献 [24]：Kumar, Seetharaman, Luebs, Kumar, Kumar, "High-fidelity audio compression with improved RVQGAN," NeurIPS 2023（**MBD 来源**）
- 论文参考文献 [9]：Cutler, Saabas, Naderi, Ristea, Braun, Branets, "ICASSP 2023 Speech Signal Improvement Challenge," arXiv:2303.06566
- 论文参考文献 [10]：Ristea, Saabas, Cutler, Naderi, Braun, Branets, "ICASSP 2024 Speech Signal Improvement Challenge," ICASSP 2024
- 论文参考文献 [11]：Liu, Shi, Chen, Rao, He, Li, Wang, Wu, "Gesper: A Restoration-Enhancement Framework for General Speech Reconstruction," INTERSPEECH 2023（**Table 2 对比对象**）
- 论文参考文献 [26]：Reddy, Gopal, Cutler, "DNSMOS P.835: A non-intrusive perceptual objective speech quality metric to evaluate noise suppressors," ICASSP 2022
- ⚠️ **本页未生成图片资产**：原论文第 2 页 Figure 1（RaD-Net 2 架构）与第 2 页 Figure 2（Complex ASA 模块）需主 agent 统一处理渲染与嵌入。
