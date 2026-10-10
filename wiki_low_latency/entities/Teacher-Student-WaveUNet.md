---
title: Teacher-Student Wave-U-Net (Nakaoka 2021)
type: entity
created: 2026-09-18
updated: 2026-09-18
tags:
  - entity
  - speech-enhancement
  - knowledge-distillation
  - wave-u-net
  - time-domain
  - block-online
  - low-look-ahead
  - non-causal-teacher
  - low-latency
sources:
  - [[wiki_low_latency/sources/2021/Teacher-Student Wave-U-Net 2021]]
related:
  - [[wiki_low_latency/sources/2021/Teacher-Student Wave-U-Net 2021]]
  - [[wiki_low_latency/concepts/nakaoka21-wave-unet-distillation]]
  - [[wiki_low_latency/entities/On-TasNet]]
  - [[wiki_low_latency/sources/2021/On TasNet Low-Latency SE 2021]]
  - [[wiki_low_latency/concepts/低时延前端与延迟账本]]
  - [[wiki_low_latency/concepts/严格因果与算法延迟]]
---

# Teacher-Student Wave-U-Net (Nakaoka 2021)

## 定义

**Teacher-Student Wave-U-Net** 是 Nakaoka et al. (ICASSP 2021) 提出的单通道时域语音增强系统：一个离线（offline）Wave-U-Net 作为 **non-causal teacher**，通过输出级蒸馏监督一个块处理（block-wise）的在线 Wave-U-Net **student**。论文面向助听器与车内通信，硬约束是 **system latency < 10 ms**，最终报告的最低 system latency 为 **6.71 ms**（K=64）。它是本库中最早把"离线 teacher → 在线低时延 student"显式用于语音增强的工作，也是 2309.08144 与 2408.04267 的共同思想前身。

## 证据

| 属性 | 本地 PDF 证据 |
|---|---|
| 任务 | 单通道时域波形增强；CMU Arctic + JEIDA-NOISE，16 kHz，p.3 |
| 输入/输出 | 带噪片段 $m_i(\tau)=m(iK+\tau)$，$\tau=[1,\ldots,K]$；输出 $\tilde s_i(\tau)$；噪声由 mixture consistency 反推 $\tilde n_i(\tau)=m_i(\tau)-\tilde s_i(\tau)$，Eq. (1)(2)，p.1-2 |
| 架构 | teacher/student 均为 Wave-U-Net：DSBlock（下采样）+ USBlock（上采样），上采样用插值而非转置卷积；DS/US 各 $L$ 层、卷积核 15/5/15/1、第 $l$ 层通道 $20l$，Fig. 1、4.2 节，p.2-3 |
| student 规模 | $L'=6$ → 1,079,302；$L'=7$ → 1,625,602；$L'=8$ → 2,329,942；$K=64$→$L'=6$、$K=128$→$L'=7$、其余 $L'=8$，4.2 节，p.3 |
| KD | student 损失 $\mathcal L_{stu}=\mathcal L+\beta\mathcal L_{diff}$，$\beta=0.01$；$\mathcal L_{diff}$ 对齐 student 输出与离线 teacher 对同一时刻的输出，Eq. (4)(5)，p.2 |
| 关键消融 | 同 $K$ 下 β=0 vs β=0.01 全部 $K$ 提升约 4 dB SDR（K=1024：7.82→12.19），Table 3，p.4 |
| 预实验 | $K=1024$：regular CNN SDR 7.82 > causal CNN SDR 7.51；作者称 "opposite to what we expected"，后续全部改用 regular CNN，Table 2/4.4 节，p.4 |
| 最优结果 | $K=1024$ + TS：SDR 12.19 / SIR 28.07 / SAR 12.38 / PESQ 2.90 / STOI 0.93；offline teacher：13.84 / 29.81 / 13.98 / 2.56 / 0.92，Table 3，p.4 |

## 架构与流程

~~~text
noisy waveform
  → 分块 m_i(τ) = m(iK+τ)，K ∈ {64,128,256,512,1024,2048}
  → online Wave-U-Net student（L' 层 DSBlock/USBlock，插值上采样）
  → 估计语音 s̃_i(τ)
  → mixture consistency: ñ_i(τ) = m_i(τ) − s̃_i(τ)

offline teacher（同架构，L=8，处理完整 64000-sample 序列）
  → 对同一时刻的输出 ŝ(iK+τ), n̂(iK+τ)
  → 构成 L_diff = E[|s̃_i(τ)−ŝ(iK+τ)|² + |ñ_i(τ)−n̂(iK+τ)|²]，Eq. (5)
~~~

student 的训练目标为：

$$
\mathcal{L}_{\text{stu}}=\mathcal{L}+\beta\mathcal{L}_{\text{diff}},\qquad \beta\ge 0,
$$

其中 $\mathcal L$ 是对 clean 真值的 MSE（语音项 + 噪声项），$\beta=0.01$。$\mathcal L_{diff}$ 与 $\mathcal L$ 形状相同，但目标换成 teacher 的输出——teacher 看的是完整长序列，其判断已吸收片段之外的上下文，因此相当于把 student 因 $K$ 太小而看不到的信息以软目标形式注入监督。

## 本 Wiki 相关字段

| 字段 | 本系统证据/边界 |
|---|---|
| 采样率 | 16 kHz（4.1 节） |
| 分析窗 | 无 STFT 窗（时域方法），等效"窗"由卷积感受野决定；PDF 未给逐层感受野 |
| hop / 片段长度 | 块处理片段 $K \in \{64,128,256,512,1024,2048\}$ samples；16 kHz 下 K=64 → 4 ms，K=128 → 8 ms |
| 算法延迟 | **6.71 ms**（K=64）= processing time 2.71 ms + 缓冲 4 ms，Table 4；K=128 → 11.40 ms |
| 因果判定 | **teacher = `non_causal`**（offline Wave-U-Net，读完整 64000-sample 序列）；**student = `low_look_ahead`**（论文自称 causal CNN 单侧 padding，但实测 causal CNN 更差后，最终系统改用 **regular CNN**；段内同时使用左右邻域，段边界 padding 方向未报告） |
| 参数量 | student：1,079,302（L'=6）/ 1,625,602（L'=7）/ 2,329,942（L'=8）；teacher 参数量未单独给出 |
| 计算量 | MACs/FLOPs 未报告；Table 4 仅给单次平均 processing time（2.71–14.89 ms） |
| 实时性证据 | 只有平均 processing time，**无 RTF、无 p50/p95/p99**；测试硬件为 Intel Core i7-7800X @3.50 GHz 桌面 CPU |
| 未验证项 | 段边界 padding 方向与段间 click 伪影；任何跨段 state/缓存；warm-up、state reset、长流稳定性；ADC/DMA/DAC 与端到端 capture-to-playback；量化、峰值内存、功耗；−10/−5 dB 分层、false-suppression、ASR WER、F0/formant 连续性；β 敏感性扫描 |

实体判定：**non-causal teacher → block-online student（实际为非因果 regular CNN）/ 6.71 ms system latency / 无尾部延迟与端侧证据**。

> [!contradiction] 因果性声明与实际实现不符
> 论文在 3.1 节论证在线算法"通常使用 causal CNN"，但 4.4 节的 $K=1024$ 预实验显示 causal CNN 的 SDR（7.51）**低于** regular CNN（7.82），SIR 低 1.16 dB，作者未解释原因即放弃 causal CNN。因此最终系统**不满足逐样本 strict causal**。任何把本文作为"因果基线"的引用都需要打折。

## 结果与证据边界

- 支持：同 $K$、同参数量、同时延下，加入 $\mathcal L_{diff}$ 使 SDR 在全 $K$ 上提升约 4 dB（K=64：4.79→8.80），因此短片段损失可被离线 teacher 监督补偿；蒸馏不改变推理结构，故时延与开销与 β=0 版本完全相同。
- 不支持：strict causal 已达成、约 2 ms 已接近、端侧 deadline 已通过、低 SNR 人声保留已证明。
- 未报告：teacher 参数量、MACs/FLOPs、逐层感受野、RTF、p50/p95/p99、warm-up/state reset、量化、目标嵌入式硬件、β 敏感性。
- 异常：offline teacher 的 PESQ 2.56 **低于** online K=1024 的 2.90，论文未解释，说明该系统的 PESQ 与 SDR 不同向。

## 交叉链接

- 源论文：[[wiki_low_latency/sources/2021/Teacher-Student Wave-U-Net 2021]]
- 蒸馏概念：[[wiki_low_latency/concepts/nakaoka21-wave-unet-distillation]]
- 同分支实体：[[wiki_low_latency/entities/On-TasNet]]、[[wiki_low_latency/sources/2021/On TasNet Low-Latency SE 2021]]
- 延迟审计：[[wiki_low_latency/concepts/低时延前端与延迟账本]]、[[wiki_low_latency/concepts/严格因果与算法延迟]]

> [!warning] 本页能支持什么 / 不能支持什么
> **能支持**：作为"离线 teacher → 在线 student 输出级蒸馏"这一路线的历史原点；作为"论文声称 causal 但最终使用 regular CNN"的典型案例；作为延迟账本"system latency = processing time + K/f_s"的最早期实例。
> **不能支持**：任何关于本系统满足约 2 ms 的说法。**6.71 ms 距约 2 ms 仍差 ~3.4 倍**，且它不含 ADC/DAC/DMA 与 I/O buffer，也未做逐样本因果证明。三篇蒸馏论文（2021/2023/2024）**都远不满足约 2 ms**，本页不构成 2 ms 方向的正向证据。
