---
title: RaD-Net 2
type: entity
created: 2026-09-18
updated: 2026-09-18
tags:
  - entity
  - speech-enhancement
  - model
  - knowledge-distillation
  - two-stage
  - causal-knowledge-distillation
  - repair-and-denoise
  - complex-asa
  - paper-claimed-causal
  - non-causal-teacher
  - latency-not-reported
sources:
  - [[wiki_low_latency/sources/2024/RaD-Net 2 2024]]
related:
  - [[wiki_low_latency/sources/2024/RaD-Net 2 2024]]
  - [[wiki_low_latency/concepts/2406.07498-two-stage-causal-repair]]
  - [[wiki_low_latency/entities/DCCRN]]
  - [[wiki_low_latency/concepts/严格因果与算法延迟]]
---

# RaD-Net 2

> Mingshuai Liu 等（**ASLP@NPU** + **ByteDance**），arXiv:2406.07498v1 [eess.AS]，2024-06。ICASSP 2024 Speech Signal Improvement (SSI) Challenge 相关。

## 定义

RaD-Net 2 是一个**两阶段级联**的单通道语音增强系统，面向 ICASSP 2024 SSI Challenge 的**语音质量/可懂度改善**目标：

1. **Stage 1 — Repair（修复）**：基于 COM-Net 结构，对退化（degraded）语音做初步修复。该阶段被设计为 KD 的战场——**teacher 与 student 参数完全相同（2.21M / 2.21M），唯一差别是 TFCM 模块的 padding 是否因果**；
2. **Stage 2 — Denoise（降噪）**：基于 S-DCCSN（S-DCCRN 变体）叠加 **Complex ASA（复数轴向自注意力）**，对 Stage 1 的输出进一步降噪。

本文的 KD 设计是**因果知识蒸馏**的一个罕见干净对照：teacher 与 student 同容量、同前端、同数据，只差 TFCM 的 padding 方向。

## 证据

| 项目 | 论文报告 | 出处 |
|---|---|---|
| 采样率（数据） | 48 kHz | 数据层；⚠️ STFT 采样率未明示 |
| STFT 窗 / hop / length | **20 ms Hanning / 10 ms / 960** → 481 维谱 | 明确 |
| Stage 1 参数量 | student 2.21M；teacher（Large）3.54M（KD_Large 配置） | Table / 正文 |
| RaD-Net 参数量 | 4.00M；配 ASA 3.97M；RaD-Net 2 **3.97M** | 正文 |
| 盲测 DNSMOS（RaD-Net 2） | SIG 3.41 / BAK 4.15 / OVRL 3.20 | Table 1 |
| 盲测 SIGMOS | 3.69 / 3.27 | Table 1 |
| 对照 Gesper | 3.45 / 4.12 / 3.20 | Table 2 |
| Stage-1 Non-causal | SIG 3.43 / OVRL 3.16 | Table 1 |
| KD_Non-causal vs KD_Large | OVRL 3.09 vs 3.04 | 正文 |
| 算法延迟 | **未报告** | — |
| RTF / FLOPs / MACs | **全部未报告** | — |

## 架构与状态

~~~text
degraded speech ──> Stage 1 (COM-Net, TFCM)  ──中间增强信号──> Stage 2 (S-DCCSN + Complex ASA) ──> enhanced
                          ▲
                          │  因果知识蒸馏（KD）
                          │
        teacher = 同结构、同 2.21M，仅 TFCM padding 为非因果
~~~

**因果知识蒸馏的关键设计**：论文构造了一个**纯净对照** —— teacher 与 student 参数完全相同，唯一区别是 TFCM 的 padding 方式。teacher 使用非因果 padding（可看右侧未来帧），student 使用因果 padding。这样 KD 的目标函数传递的**不是容量差异**，而是**"非因果可见性"带来的知识**：

$$
\mathcal{L}_{KD}=\mathcal{L}_{SE}+\lambda\cdot\mathcal{L}_{distill}(\hat y^{S},\hat y^{T})
$$

论文对损失用 Eq.(1)–(8) 展开（含多项加权项），但笔记记录该部分在 PDF 抽取中**碎片化**，符号完整性未完全核对。

**Complex ASA（复数轴向自注意力）**：Stage 2 引入的频轴自注意力，受 D2Former 启发，**softmax 施加在模值（modulus）上**而非直接施加在复数上。它是 RaD-Net 2 相对 RaD-Net 的主要结构增量（3.97M vs 4.00M，参数几乎持平）。

## 低时延账本

| 项目 | 证据 | 判定 |
|---|---|---|
| 采样率 | 48 kHz（数据层） | ⚠️ STFT 采样率未明示 |
| 分析窗 / hop | **20 ms Hanning / 10 ms**，STFT length 960 → 481 bins | 明确 |
| 帧内可读样本 | 480（20 ms @ 降采样后 960-point STFT） | 按论文配置换算 |
| **算法延迟** | **未报告** | ❌ **未报告** |
| **两阶段串行延迟累加** | **未报告** | ❌ **最大缺口**（见 concept 页） |
| **时间因果 — Stage 1 student** | 因果 padding（TFCM） | ✅ **`paper-claimed-causal`** |
| **时间因果 — Stage 1 teacher** | 非因果 padding（TFCM） | ❌ **`non-causal`** |
| **时间因果 — Stage 2** | **论文从未声明因果性** | ❌ **未声明** |
| **全系统因果判定** | 两阶段串行 + Stage 2 未声明 | ❌ **不满足 `strict_causal`** |
| 起始与状态 | 未报告 warm-up / state reset | ❌ 未报告 |
| 运行时 | RTF / p50/p95/p99 **全部未报告** | ❌ 未报告 |
| 端到端与 deadline | **未报告** | ❌ 未报告 |
| 部署资源 | 参数量 3.97M；峰值 RAM / SRAM / 量化 / 目标硬件 **未报告** | ⚠️ 部分 |

> [!warning] 因果性必须区分 teacher 与 student
> **本页不把 RaD-Net 2 标记为 `strict_causal`**，理由有三：
> 1. **Stage 1 teacher 明确非因果**（TFCM 非因果 padding）——这是论文**自己设计**的对照条件，不是缺陷，但 teacher 的因果性与 student 无关；
> 2. **Stage 1 student 为 `paper-claimed-causal`**：论文声称因果 padding，但**未给出逐层的可见性证明**（未说明是否有其他非因果操作），因此达不到本 Wiki 的 `strict_causal` 定义（禁止 centered STFT、右侧 padding、双向统计、完整 chunk future attention）；
> 3. ⭐ **Stage 2（S-DCCSN + Complex ASA）论文从未声明因果性**——**这是一个两阶段系统，Stage 2 的因果性缺失直接使全系统无法标为严格因果**。
>
> ⚠️ 此外，**两阶段的串行算法延迟累加从未被报告**：即使 Stage 1 与 Stage 2 都各自满足因果，级联系统的总延迟也必须是 $L_{total}=L_{stage1}+L_{stage2}+L_{interface}$。**论文完全没有讨论这一项**——这是本页读出的最大缺口。

## 结果与证据边界

**可支持**：
- 在 SSI Challenge 的盲测口径下，RaD-Net 2 的 DNSMOS 与 SIGMOS 与同期的 Gesper 相当（Table 2：3.47/4.13/3.22 vs 3.45/4.12/3.20）；
- **因果 student 可以通过与同容量非因果 teacher 的 KD 获得提升**：KD_Non-causal 在 OVRL 上（3.09）优于 KD_Large（3.04），说明**容量更大的非因果 teacher 不如同容量的非因果 teacher**——即因果关系本身（而非容量）是关键的知识来源；
- Complex ASA 在参数几乎不增的前提下（4.00M → 3.97M）替换了原结构。

**不能支持**：
- ❌ **不能支持任何延迟声称**——算法延迟、RTF、FLOPs、MACs **全部未报告**；
- ❌ **不能支持两阶段的端到端实时性**——串行延迟累加未报告；
- ❌ **不能支持"RaD-Net 2 是严格因果系统"**——Stage 2 因果性未声明，Stage 1 仅 `paper-claimed-causal`；
- ❌ **不能支持低 SNR 人声保留**——**无 SNR 分层、无 false-suppression、无 ASR WER、无 F0/formant/prosody 连续性证据**；
- ❌ 不能支持部署可行性——目标硬件、峰值内存、量化精度均未报告。

## 交叉链接

- source 页：[[wiki_low_latency/sources/2024/RaD-Net 2 2024]]
- concept 页：[[wiki_low_latency/concepts/2406.07498-two-stage-causal-repair]]
- 因果性定义依据：[[wiki_low_latency/concepts/严格因果与算法延迟]]
- 同分支竞品（同为 SE KD）：[[wiki_low_latency/entities/Dynamic-Frequency-Adaptive-KD]]、[[wiki_low_latency/entities/DISPATCH]]、[[wiki_low_latency/entities/Distil-DCCRN]]
- 被压缩对象谱系：[[wiki_low_latency/entities/DCCRN]]

> [!note] 本页能支持什么 / 不能支持什么
> **支持**：把 RaD-Net 2 作为「**同容量 teacher 的因果知识蒸馏对照**」引用——它是本库中唯一把 teacher 可靠性差异控制到"只差 padding"的 KD 实验；也可引用其 Complex ASA 的 softmax-on-modulus 设计。
>
> **不支持**：任何**延迟数值**、任何**全系统因果性**声称、任何**两阶段实时性**推断。**Stage 2 因果性未声明**是本页最需要读者警惕的一点。
