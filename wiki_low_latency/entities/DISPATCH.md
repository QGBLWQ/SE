---
title: DISPATCH
type: entity
created: 2026-09-18
updated: 2026-09-18
tags:
  - entity
  - speech-enhancement
  - model
  - knowledge-distillation
  - selective-distillation
  - knowledge-gap-score
  - multi-scale-patches
  - patch-selection
  - non-causal
  - non-causal-teacher
  - non-real-time-orientation
  - method-analogy-only
sources:
  - [[wiki_low_latency/sources/2025/DISPATCH 2025]]
related:
  - [[wiki_low_latency/sources/2025/DISPATCH 2025]]
  - [[wiki_low_latency/concepts/2509.15922-selective-patch-distillation]]
  - [[wiki_low_latency/entities/Dynamic-Frequency-Adaptive-KD]]
  - [[wiki_low_latency/entities/RaD-Net-2]]
  - [[wiki_low_latency/entities/DCCRN]]
---

# DISPATCH

> Dohwan Kim, Jung-Woo Choi（**School of Electrical Engineering, KAIST**，Daejeon, Republic of Korea），arXiv:2509.15922v2 [cs.SD]，26 Jan 2026（v1 2025-09）。代码：`https://github.com/rlaehghks5/DISPATCH`。

## 定义

DISPATCH 是一个**选择性 patch 知识蒸馏**框架，用于语音增强模型的压缩。它的出发点是**质疑 KD 的一个隐含假设**：

> KD 通常假设 **teacher 提供可靠的监督**。DISPATCH 用实验推翻了这一前提——在一个普通的非因果 teacher 上，**46.8% 的时频谱图 patch 上 teacher 的误差反而高于 student**。

据此论文提出 **Knowledge Gap Score（KGS）**：

$$
KGS_p = E_p^S - E_p^T,
$$

只对 KGS 排名**前 $k$%** 的 patch 施加 KD 损失，并用 **MSSP（Multi-Scale Selective Patches）** 在低频用小 patch（10）、高频用大 patch（40）匹配语音的声学结构粒度。

> [!warning] 本文与本 Wiki 方向的关系：**方法学类比 + teacher 可靠性的实证警示，不是直接竞品**
> - **本文不以低时延为目标**。全文**没有出现 causal / latency / real-time / RTF / streaming / algorithmic delay 中的任何一个概念**；
> - 论文的约束是 **"high computational demands … on-device AI, where hardware limitations, power consumption, and monetary costs are critical concerns"**——即**算力、功耗、成本，不是时间**；
> - 两个 student（ConvTasNet 1.75M、DCCRN-CL 2.24M）都**不是流式低时延系统**；论文**从未声明 student 的因果性**；两个 teacher 都不以因果为前提；
> - ⭐ **唯一与低时延相关的时序信息是 STFT 配置**：Hann 窗 **32 ms**、hop **8 ms**（75% overlap）。**32 ms 距约 2 ms 差 16 倍**。

## 证据

| 项目 | 论文报告 | 出处 |
|---|---|---|
| 采样率 | **16 kHz**（数据层；⚠️ STFT 采样率未明写） | 明确 |
| STFT 窗 / hop | **Hann 32 ms / 8 ms**（75% overlap） | ⭐ 明确 |
| 核心机制 | KGS = $E_p^S-E_p^T$，top-$k$% 选择 | Eq.(5)–(7) |
| $k$（选择比例） | **80**（%） | 明确 |
| $\alpha$（KD 权重） | **0.5**（论文明确说明不逐方法调优） | Eq.(8) |
| Patch 尺寸 | 分析用 20；MSSP 测试 10/20、20/40、10/40 | Table 2 |
| Patch 数量 $P$ | **未报告** | ❌ |
| 数据集 | DNS2020（>500h clean + >100h noise，4 秒，16 kHz，SNR 0–20 dB 均匀） | 明确 |
| 评测集 | DNS2020-test + VoiceBank+DEMAND | 明确 |
| 评价指标 | **WB-PESQ / NB-PESQ / STOI(%)**（无 DNSMOS） | 明确 |
| Teacher 1 | ConvTasNet，**9.71M**，MAC/s **8.05G** | Table 1 |
| Student 1 | ConvTasNet，**1.75M**，MAC/s **0.57G** | Table 1 |
| Teacher 2 | DCCRN-CL，**9.22M**，MAC/s **15.33G** | Table 1 |
| Student 2 | DCCRN-CL，**2.24M**，MAC/s **3.84G** | Table 1 |
| 最佳结果 | ConvTasNet + DFKD + MSSP(10/40)：DNS2020 WB-PESQ **2.677**（scratch 2.563）；VBD **2.618** | Table 1 |
| DCCRN-CL 最佳 | **2.758** / VBD **2.719** | Table 1 |
| ⭐ 实证发现 | teacher 在 **46.8%** 的 patch 上误差高于 student | 正文 Fig.2(b) |
| ⭐ 训练开销 | **+1.2% / epoch**（配 DFKD + ConvTasNet，**训练期**） | 正文 |
| 算法延迟 / RTF / p99 / 硬件 | **全部未报告** | ❌ |

## 架构与状态

~~~text
noisy speech ──STFT──┬──> Teacher (非因果) ──> ŝ^T（复谱）
                     ├──> Student (非因果) ──> ŝ^S（复谱）
                     └──> Target  ──> s  （干净复谱）
                                │
                ┌───────────────┴────────────────┐
          patch 化（尺寸 N）              patch 化（尺寸 N）
                │                                │
          E_p^T = ε(s_p, ŝ_p^T)          E_p^S = ε(s_p, ŝ_p^S)
                └────────────┬───────────────────┘
                             │
                  KGS_p = E_p^S − E_p^T   （Eq. 5）
                             │
                  取 KGS 排名前 k% 的 patch（k = 80）
                             │
          L_DISPatch 只施加于选中的 patch（Eq. 6–7）
                             │
          L_total = α·L_SE + (1−α)·L_DISPatch（Eq. 8，α = 0.5）
~~~

**关键设计要素**：

**① KGS（Eq.5）**：$KGS_p=E_p^S-E_p^T$。直觉是**两个条件必须同时满足**才得分高——$E_p^T$ 小（teacher 做得好）**且** $E_p^S$ 大（student 做得差）。Paper 用 Table 3 的四组对照证明：只看 teacher 误差或只看 student 误差都劣于差值。

**② patch 的四分类**（论文定义的判据）：

| 类别 | 判据 |
|---|---|
| **Converging** | $\Delta e_p < -0.01$ |
| **Exploding** | $\Delta e_p > 0.01$ |
| **Converged** | $-0.01\le\Delta e_p\le 0.01$ 且 $e_p^{(J)}\le e_{mean}$ |
| **Challenging** | $-0.01\le\Delta e_p\le 0.01$ 且 $e_p^{(J)} > e_{mean}$ |

其中 $\Delta e_p=a_p\cdot J$ 是对该 patch 误差序列做一阶多项式拟合后的首末变化量，$a_p$ 为斜率。

**③ MSSP**：复用 [[wiki_low_latency/entities/Dynamic-Frequency-Adaptive-KD]] 的 **Frequency Adapter** 定位动态分界点，低频用 patch size **10**、高频用 **40**。声学依据来自 **Diehl 2008**（低频共振峰对元音识别至关重要）与 **Jongman 2000**（高频擦音为宽结构能量模式）。损失配置与 DFKD 一致（低频纯相位 cosine、高频幅度 L2 + 相位）。

**④ 零填充细节**：论文明确"zero padding 只用在高频端，且 padded bins 在所有计算中被忽略"——保证 patch 切分不引入虚假低频信息。

## 低时延账本

| 项目 | 证据 | 判定 |
|---|---|---|
| 采样率 | **16 kHz**（数据层） | ✔ 明确；⚠️ STFT 采样率未明写 |
| **分析窗 / hop** | **32 ms Hann / 8 ms**（75% overlap） | ⭐ **本库 KD 论文中时序信息最明确的一篇** |
| 帧内可读样本 | 16 kHz 下 32 ms = 512 samples、8 ms = 128 samples | ⚠️ 本页按 16 kHz 换算，论文未明写 STFT 采样率 |
| **算法延迟** | **未报告** | ❌ **未报告**（论文从未讨论延迟概念） |
| look-ahead | **未报告** | ❌ 未报告 |
| **时间因果 — Teacher** | ConvTasNet（时域 TCN）+ DCCRN-CL（complex LSTM），均不以因果为前提 | ❌ **`non-causal-teacher`** |
| **时间因果 — Student** | 由 teacher 减通道而来；**论文全文无 "causal" 一词** | ❌ **`non-causal`（未声明）** |
| **KD 机制本身** | ⭐ top-$k$% 是**对整段谱图的全局排序** | ⚠️ **训练期操作**——不影响推理延迟，但**机制本身不可流式化** |
| 起始与状态 | warm-up / state reset **未报告** | ❌ 未报告 |
| 计算量 | **MAC/s**（口径明确：每秒音频的乘加数）：8.05G→0.57G、15.33G→3.84G | ✔ 明确，口径清楚 |
| 运行时 | RTF / p50/p95/p99 **全部未报告** | ❌ 未报告 |
| 端到端与 deadline | **未报告** | ❌ 未报告 |
| 部署资源 | 参数量 ✔；峰值 RAM / SRAM / 量化精度 / **目标硬件全部未报告** | ⚠️ 部分 |

> [!warning] 因果性必须区分 teacher 与 student
> | 对象 | 判定 | 依据 |
> |---|---|---|
> | **Teacher**（ConvTasNet、DCCRN-CL） | **`non-causal-teacher`** | 架构不以因果为前提；论文无因果性表述 |
> | **Student**（压缩版） | ⚠️ **`non-causal`（未声明）** | 论文**从未讨论因果性** |
> | **KD 机制** | ⭐ **训练期全局操作**（top-$k$% 排序） | **不可流式化**，但只在训练期使用 |
> | **整体** | **不适合作为低时延候选** | 无任何延迟或因果证据；32 ms 窗 |
>
> ⚠️ **注意一个容易误判的点**：DISPATCH 的机制**完全不增加推理延迟**——patch 化、KGS 计算、top-$k$% 排序**全部发生在训练阶段**，推理时 student 就是原样的 student。论文量化了这一点（**+1.2%/epoch，训练期**）。
> ⭐ **这与"加模块"类方法（如 RaD-Net 2 的 Complex ASA）有本质区别。**
> ⚠️ 但**该选择机制依赖整段的全局排序**，因此若要用于在线场景需重新设计（滑动窗口近似会引入延迟，或改用逐 patch 的在线判据）。**本库中尚无论文处理过这个问题。**

## 结果与证据边界

**可支持**：
- ⭐ **选择性蒸馏有效**：在 DFKD 上叠加 DISPatch 使**全部 12 组指标一致改善**；在 8 个 DNS2020 对照中全部为正（+0.018 ~ +0.049 WB-PESQ）；
- ⭐ **"差值判据"优于任何单分量**（Table 3，五组对照）——这是本文最有说服力的实验，它论证的是**为什么**必须用差值，而不只是"我们更好"；
- ⭐ **MSSP 的 10/40 配置优于 uniform 20/20**（Table 2，全部模型与数据集）；
- ⭐ **SE 的输出级 KD 效果差这一诊断**：Table 1 显示纯 magnitude 距离 KD（L1/L2）相对 scratch **几乎无增益甚至有害**（ConvTasNet + L2：**±0.000**；DCCRN-CL + L1：**−0.031**），加上 DISPatch 后才变得有效；
- ⭐ **teacher 可靠性的实证质疑**：46.8% 的 patch 上 teacher 比 student 更差。

**不能支持**：
- ❌ **不能支持任何延迟声称**——算法延迟、RTF、p99、硬件、端到端**全部缺失**；只有 STFT 窗/hop 与 MAC/s；
- ❌ **不能支持流式/因果**——两个 teacher 均非因果，student 因果性零提及；
- ❌ **不能支持低 SNR 人声保留**——训练测试均 **0–20 dB**（**无任何负 SNR 结果**）、无 false-suppression、无 SPP/VAD、无 ASR WER、无 F0/formant/prosody、无 voiced energy、无 DNSMOS、无 SIG/BAK 分解、无主观听测；
- ⚠️ ⭐ **声学动机与评测完全脱节**：论文引用 Diehl 2008 与 Jongman 2000 论证"低频共振峰对元音识别至关重要"作为 MSSP 的动机，**但整篇论文没有任何一个实验测量共振峰、元音或擦音的保留情况**；
- ❌ **不能支持显著性**——无方差、无置信区间、无多次运行。⚠️ **Table 2 中 DCCRN-CL / DNS2020 的 10/40 vs 20/20 只差 0.001**，这类差值需要显著性检验；
- ❌ **不能支持"student 超过 teacher"**——一切配置下 student 都没达到 teacher（最好 2.677 vs teacher 2.792）。✔ 这是本文表述上比 DFKD 更诚实的地方；
- ⚠️ **一处未被讨论的反例**：DCCRN-CL + DFKD 在 VoiceBank+DEMAND 上，DISPatch 开/关为 **2.618 vs 2.635（−0.017）**——**唯一一个 DISPatch 使结果变差的格子，论文没有讨论**。

## 交叉链接

- source 页：[[wiki_low_latency/sources/2025/DISPATCH 2025]]
- concept 页：[[wiki_low_latency/concepts/2509.15922-selective-patch-distillation]]
- ⭐ **直接前身与整合对象**：[[wiki_low_latency/entities/Dynamic-Frequency-Adaptive-KD]]
- ⭐ **方法学交叉（teacher 可靠性问题的另一个角度）**：[[wiki_low_latency/entities/RaD-Net-2]]
- 被压缩对象：[[wiki_low_latency/entities/DCCRN]]
- 因果性定义依据：[[wiki_low_latency/concepts/严格因果与算法延迟]]
- 人声保留评估框架：[[wiki_low_latency/concepts/低 SNR 人声保留评估]]

> [!note] 本页能支持什么 / 不能支持什么
> **支持**：
> 1. 把 DISPATCH 作为「**选择性蒸馏**」机制的出处引用（KGS 差值判据 + top-$k$% 选择）；
> 2. ⭐ **引用其 teacher 可靠性的实证警示**——"teacher 并非全局优于 student，46.8% 的 patch 上更差"，并指出**低时延场景下 teacher（非因果大模型 / 因果浅层模型）的可靠性风险更高，因此选择性蒸馏几乎是必需的而非可选的**；
> 3. 引用其"**推理零额外成本**"的性质（机制只在训练期，+1.2%/epoch）。
>
> **不支持**：任何**延迟**、**因果性**、**部署**推断。⚠️ 32 ms 窗距约 2 ms 差 16 倍；**KD 机制的全局排序性质使其不可直接流式化**——这是迁移到约 2 ms 方向时必须解决的架构障碍。
