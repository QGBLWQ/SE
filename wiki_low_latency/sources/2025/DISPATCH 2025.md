---
title: DISPATCH - 蒸馏选择性 patch 的语音增强知识蒸馏框架
type: source
created: 2026-09-18
updated: 2026-09-18
tags:
  - speech-enhancement
  - knowledge-distillation
  - selective-distillation
  - frequency-dependent
  - knowledge-gap-score
  - multi-scale-patches
  - patch-selection
  - model-compression
  - non-causal
  - non-causal-teacher
  - non-real-time-orientation
  - method-analogy-only
  - dccrn
  - conv-tasnet
source_type: paper
year: 2025
authors: Dohwan Kim; Jung-Woo Choi
venue: arXiv preprint (cs.SD) — arXiv:2509.15922v2, 26 Jan 2026（v1 为 2025-09）
arxiv: https://arxiv.org/abs/2509.15922
local_pdf: raw/papers/low_latency_causal_se/2509.15922.pdf
evidence_policy: local_pdf_only
related:
  - [[wiki_low_latency/sources/2025/Dynamic Frequency-Adaptive KD 2025]]
  - [[wiki_low_latency/sources/2024/Distil-DCCRN 2024]]
  - [[wiki_low_latency/concepts/2008.00264-complex-phase-enhancement]]
  - [[wiki_low_latency/sources/2020/DCCRN Low-Latency Direction 2020]]
  - [[wiki_low_latency/concepts/低 SNR 人声保留评估]]
---

~~~yaml
- 论文: [DISPATCH: Distilling Selective Patches for Speech Enhancement](2025)
  ├── 要解决什么问题: 常规 KD 让 student 模仿 teacher 的**全部**输出——但这既浪费力气在 student 已经学好的区域，又强迫 student 去模仿 teacher 本身做错的区域（"transfer harmful artifacts"）
  ├── 核心方法: 引入 Knowledge Gap Score（KGS）= student 的 patch 误差 − teacher 的 patch 误差，只对 KGS 排名前 k% 的 patch 施加 KD 损失；再用 MSSP 在低频用小 patch（10）、高频用大 patch（40）
  ├── 属于哪个分支: 单通道 SE 的模型压缩 / 输出级（spectrogram patch）选择性知识蒸馏 / 频率相关蒸馏
  ├── 输入/输出: noisy speech → STFT → (target, student 输出, teacher 输出) → patch 化 → KGS 排序 → top-k% 施加 L_KD；MSSP 按动态分界点用不同 patch 尺寸
  ├── 关键trick: KGS 用**差值** E_p^S − E_p^T 而不是单一分量——论文 Table 3 证明只看 teacher 误差或只看 student 误差都劣于差值
  ├── 数据集: DNS2020（>500h clean speech + 100h noise，4 秒片段，16kHz，SNR 0–20dB 均匀）；评测 DNS2020-test + VoiceBank+DEMAND
  ├── 对比了谁: Scratch、L1、L2、DFKD；每个都做 DISPatch 开/关对照；另有 MSSP 的 patch 尺寸消融（20/20、10/20、20/40、10/40）与 KGS 分量消融
  ├── 性能上限: ConvTasNet student（1.75M）配 DFKD+MSSP(10/40) 得 DNS2020-test WB-PESQ 2.677（scratch 2.563）、VoiceBank+DEMAND WB-PESQ 2.618（scratch 2.585）；DCCRN-CL student（2.24M）得 2.758 / 2.719
  ├── 参数量: ConvTasNet teacher 9.71M → student 1.75M；DCCRN-CL teacher 9.22M → student 2.24M；MAC/s 分别为 8.05G → 0.57G 与 15.33G → 3.84G
  ├── 消融关键发现: ①DFKD 上叠 DISPatch 在**全部 12 组指标上一致改善**；②MSSP 的 10/40（低/高）配置在全部模型与数据集上最优，优于 uniform 20/20；③Table 3 证明 KGS 差值优于任何单分量
  ├── 遗留问题(你的机会): 论文承认 teacher 在 46.8% 的 patch 上比 student 更差——**这一发现对低时延 KD 有直接冲击但论文未展开**；完全不面向低时延（无 causal/latency/RTF/实时表述）；STFT 用 32ms 窗 + 8ms hop；MATLAB 风格
  └── 跟哪篇像: [[wiki_low_latency/sources/2025/Dynamic Frequency-Adaptive KD 2025]]（直接前身与整合对象）、[[wiki_low_latency/sources/2024/Distil-DCCRN 2024]]
~~~

# DISPATCH: Distilling Selective Patches for Speech Enhancement

> Dohwan Kim, Jung-Woo Choi（**School of Electrical Engineering, KAIST, Daejeon, Republic of Korea**），arXiv:2509.15922v2 [cs.SD]，26 Jan 2026（v1 2025-09）。代码：`https://github.com/rlaehghks5/DISPATCH`

> [!warning] 本文与本 Wiki 方向的关系：**方法学类比（method analogy），不是直接竞品**
> 与 [[wiki_low_latency/sources/2025/Dynamic Frequency-Adaptive KD 2025]] 一样，本节必须先说清定位：
> - 本文**不以低时延为目标**。全文**没有出现 causal / latency / real-time / RTF / streaming / algorithmic delay 中的任何一个概念**；
> - 论文的约束是 **"high computational demands … in resource-constrained settings like on-device AI, where hardware limitations, power consumption, and monetary costs are critical concerns"**——即 **算力、功耗、成本**，**不是时间**；
> - 实验用的两个 student（ConvTasNet 1.75M、DCCRN-CL 2.24M）都**不是流式低时延系统**；
> - 论文**从未声明 student 的因果性**；两个 teacher（ConvTasNet、DCCRN-CL）都**不以因果为前提**；
> - **唯一与低时延相关的时序信息是 STFT 配置**：Hann 窗 **32 ms**、hop **8 ms**（75% overlap）。
>
> **因此本页的定位是**：DISPATCH 的价值在于 **①「选择性蒸馏」的机制设计（KGS）**、**②它对 teacher 可靠性的实证质疑**（46.8% patch 上 teacher 更差）、**③它是 DFKD 的直接后续与整合者**。
>
> ⭐ **其中第 ② 点对低时延 KD 有直接的方法学冲击**——因为低时延场景下 teacher 往往是"非因果大模型 / 因果浅层模型"，其可靠性本就存疑，"盲目全盘蒸馏"的风险更大。**这一点论文自己没有意识到，是本页读出的最重要迁移价值。**

> [!warning] PDF 转换质量与阅读说明
> 原 PDF 共 ****（txt 抽取中无页眉页码痕迹；从内容结构看为 5 页左右的会议短文，含 2 张图 + 3 张表 + 参考文献 + 致谢）。
>
> **本文抽取的实际问题（已核对 txt 后据实记录）**：
> 1. ⭐ **Fig.1（DISPatch 框架总览）在 txt 中被彻底压成乱码**——第 77-101 行只留下 `…`、`H`、`L`、`Target`、`Student`、`Teacher`、`Noisy Speech`、`STFT`、`DISPatch` 等孤立符号，**无法还原任何拓扑**。**本页不推断该图结构**；
> 2. ⭐ **Fig.2（patch 级 teacher-student 失配分析）同样不可还原**——论文正文描述的 (a) "Confusion matrix of patch classification" 与 (b) "Scatter plot comparing patch-wise errors" 在 txt 中**完全不存在图像内容**。**这两张图承载了论文最重要的实证发现（46.8%），必须回查原 PDF**；
> 3. **公式编号与正文混排**——Eq. (1) 到 Eq. (8) 在 txt 中分散（例如第 137 行的 `ep = ∥|sp | − |ŝp |∥22 (1)` 与第 155 行的 `(2)` 分离，第 179 行的 `(5)` 与第 190 行的 `(6)` 分离）；
> 4. ⚠️ **公式 (1) 的下标在 txt 中丢失**——`∥|sp | − |ŝp |∥22` 中，**求和/范数阶数 2 被压成 "22"**（应为 $\lVert\cdot\rVert_2^2$），且 $s_p$、$\hat s_p$ 的下标 $p$ 与范数符号粘连。**该式形式可按上下文确认，但排版需回查原 PDF**；
> 5. ⚠️ **Eq. (6) 的求和下标有严重矛盾**——txt 中写作 `L_DISPatch = (1/(P·k%)) Σ_{i=0}^{P−1} I_{k%}(KGS_p) · L_KD(ŝ_p^S, ŝ_p^T)`，**求和变量是 $i$，但被求和的表达式下标全是 $p$**。这**在原文中就是如此**（应与 $P$ 个 patch 一一对应），是论文的记号笔误，不是抽取错误。本页据实标注；
> 6. **Table 1/2/3 的数值部分抽取质量较好**——Table 1（第 225-248 行）、Table 2（第 250-262 行）、Table 3（第 250-262 行）的数值可逐行核对；⚠️ **但 Table 2 与 Table 3 在 txt 中被并列排布**（两张表的表头与数据行交错出现在第 250-262 行），**阅读时需按论文正文的引用关系区分**；
> 7. **Table 1 的行合并结构有歧义**——`ConvTasNet (Teacher)` / `ConvTasNet (Student)` 与 `DCCRN-CL (Teacher)` / `DCCRN-CL (Student)` 是**跨行标签**，在 txt 中它们与数据行的对应关系靠位置推断。本页按论文正文的表述与数值合理性整理，**建议回查原 PDF 确认**；
> 8. **论文的一处表述不一致**——正文说 "we **set** the patch size N to 20"（第 2.1 节末）与 "For the analysis in Section 2.1, we set the patch size N to 20. We used **the same setting for DISPatch with a single patch size**…"（第 3.2 节），但 Table 2 中"DISPatch with a single patch size"对应的是 `20/20` 一行 ✔ 自洽，**这一处没有问题**。⚠️ 但论文**未说明 patch 数量 $P$ 的取值**；
> 9. ⭐ **论文存在一处自我矛盾的报告口径差异**——正文说 "46.8% of patches"（第 2.1 节末，指 J-th 点时 teacher 误差超过 student 的 patch 比例），但**没说明这是在多少样本、多少 patch 上统计的**（论文只说 "a single speech sample" 的 Fig.2，但 46.8% 这个数字的来源未明确）。**本页据实标注这一证据边界**。
>
> **本页做的处理**：
> - **已按 txt 原文完整核对**：Eq. (1)–(8) 的形式（含上述问题标注）、Table 1/2/3 的全部数值、第 III.A 节数据集描述、第 III.B 节的全部实现细节（模型配置、patch 尺寸、$k$、优化器、学习率、训练轮数）。
> - **未做视觉核对的部分**：Fig.1、Fig.2 的结构与内容（txt 不可还原，**必须回查原 PDF**）。本页对这两张图**只描述论文正文提到的结论，不还原图结构**。
> - **PDF 未给出的信息一律不补写**：patch 数量 $P$、采样率与 STFT 采样率的关系、$\alpha$ 的敏感性、精确的 KGS 统计口径、任何延迟/RTF/硬件数值。**论文确实没有写，不是抽取丢失**。

## 1. 他们为什么这么做？（motivation）

### 1.1 任务与对象

本文研究**语音增强模型的压缩**，手段同样限定在 **KD**。论文对压缩手段的定位与 DFKD 一致（pruning [4]、quantization [5]、KD [6]–[8]），但**明确把本文限定在 KD**：

> "This paper focuses on KD, a teacher-student paradigm in which a compact student model is trained to mimic a larger teacher model, thereby inheriting the teacher's knowledge."

论文对 KD 在语音领域的应用做了分类：

| 类别 | 代表工作 | 本文的定位 |
|---|---|---|
| Response-based KD | 说话人验证 [9][10]、语音分离 [11][12]、语音增强 [13]–[17] | ⭐ **本文的战场**——"a prominent line of work" |
| 蒸馏对象为时频输出 | Subband-KD [13]、DFKD [17] | ⭐ 本文最相关的两条前置工作 |
| Feature-based / 混合 | ABC-KD [15] | 作为对比方法 |

### 1.2 论文动机：KD 的两条隐含假设都站不住

**这是本文最重要的部分，也是它区别于 DFKD 的地方。** 论文原文（Introduction）：

> "However, conventional KD methods train the student to **mimic the teacher's output entirely**, which forces the student to imitate the regions where the **teacher performs poorly** and to apply distillation to the regions where the **student already performs well**, which yields only **marginal gains**."

论文进一步把这两个问题拆解清楚：

> "**The first limitation concerns the student's existing proficiency.** Distilling knowledge in regions where the student has already converged yields **minimal benefit**."
>
> "**The second challenge stems from the inherent imperfections of the teacher model**, which may result from **overfitting to the training dataset**. Therefore, forcing the student to learn from **flawed regions** in the teacher's output is detrimental, as it leads the student to **replicate the teacher's weakness instead of its strengths**."
>
> "As a result, **indiscriminate distillation** not only **diverts the student's focus from the regions where the teacher's guidance is most needed** but also, more importantly, can cause the student to **imitate the teacher's erroneous output**, leading to a **degradation in performance**."

论文把 KD 的隐含假设明确点出来并质疑：

> "KD generally assumes that the **teacher provides reliable supervision**. However, this premise **overlooks two critical issues** in practice."

论文还专门批评了既有的"自适应蒸馏"策略（这一段很重要，因为它划清了本文与已有工作的界限）：

> "Although several adaptive strategies have been proposed, such as **importance-weighted KD [18, 19]** and **uncertainty-aware KD [20, 21]**, they still **presuppose that the teacher is uniformly superior to the student for a given input**. Consequently, they inevitably **transfer local artifacts even under reduced weights**, neglecting that **the student may locally outperform the teacher**."

即论文指出三档方法的不同假设：

| 方法 | 假设 | 问题 |
|---|---|---|
| 常规 KD | teacher 全程可靠、student 全程不足 | 浪费(student 已学好的地方) + 有害(teacher 做错的地方) |
| Importance-weighted KD [18][19] | teacher 全局优于 student，只是某些区域**更重要** | 仍会传递局部伪影，只是权重降低 |
| Uncertainty-aware KD [20][21] | teacher 全局优于 student，只是某些区域**更不确定** | 同上 |
| ⭐ **DISPATCH（本文）** | **teacher 并非全局优于 student，student 可能在局部更好** | 用 **KGS 差值**显式排除这些区域 |

### 1.3 论文的实证基础：46.8%

论文做了 patch 级的 teacher-student 误差分析（第 2.1 节），**这是全文的实证支柱**：

**分析设置**（论文明确）：
- 数据集：DNS2020 Challenge；
- 模型：**ConvTasNet** [23]；
- 记录频率：每 **1000** 训练步记录一次每个 patch 的误差，共 **$J+1$** 个观测点；
- patch 尺寸 $N = 20$；
- 判据阈值 $\Delta e_p < -0.01$ / $\Delta e_p > 0.01$（论文注明："Note that decision thresholds other than 0.01 (e.g., 0.02 or 0.03) **result in similar patch distributions**"）。

**分析得到的核心数字**：

> "Furthermore, Fig.2 (b) confirms that at the J-th point, **the teacher's error exceeds the student's in 46.8% of patches**."

> [!warning] 46.8% 这个数字的证据边界
> 论文正文说 Fig.2 展示的是 "**a single speech sample** reveals misalignment between the teacher and student"，紧接着给出 46.8%。
> ⚠️ **但论文没有明确 46.8% 是在"单个样本"上统计还是在整个数据集上统计**——从上下文看，"a single speech sample" 描述的是 Fig.2 的可视化，而 46.8% 可能来自更广的统计，**但论文未澄清**。
> **本页据实记录这一歧义，不做推断。**

**论文对这一发现的两条结论**：

> "This empirical evidence exposes **two critical risks of indiscriminate distillation**: the **transfer of harmful artifacts** by forcing the student to mimic the teacher's flawed regions, and the **diversion of the student's focus** to regions where the student already excels, rather than where distillation is truly needed."

**patch 的四分类**（论文定义的判据，Eq. 3 后）：

| 类别 | 判据 |
|---|---|
| **Converging** | $\Delta e_p < -0.01$ |
| **Exploding** | $\Delta e_p > 0.01$ |
| **Converged** | $-0.01 \le \Delta e_p \le 0.01$ 且 $e_p^{(J)} \le e_{mean}$ |
| **Challenging** | $-0.01 \le \Delta e_p \le 0.01$ 且 $e_p^{(J)} > e_{mean}$ |

论文对 Fig.2(a) 结论的描述（**图本身不可还原，仅有文字**）：

> "Although the student has stabilized in many regions (Converged or Converging), **a significant subset exists where the teacher remains unstable (Exploding or Challenging) despite the student's proficiency** (highlighted in the red box)."

### 1.4 与本 Wiki 方向的关系

> [!warning] ⭐ **46.8% 这个发现对低时延 KD 有直接冲击——而论文自己没有意识到**
> 论文的发现是：**在一个普通的非因果 teacher 上，就有 46.8% 的 patch 上 teacher 比 student 更差。**
>
> **把这个发现搬到低时延场景，问题会变得更尖锐**：
>
> | 场景 | Teacher 类型 | Teacher 可靠性的额外风险 |
> |---|---|---|
> | [[wiki_low_latency/sources/2026/RT-SEMamba 2026]] | 因果 8-layer cTF-Mamba（**同窗长同采样率**） | 较低——teacher 与 student 共享前端 |
> | [[wiki_low_latency/sources/2024/RaD-Net 2 2024]] | 非因果（**同容量，只差 padding**） | 较低——但非因果 teacher 在**因果可观测的区域内**未必更可靠 |
> | [[wiki_low_latency/sources/2024/Distil-DCCRN 2024]] | 非因果 Uformer（Conformer），**teacher hop = 10 ms，student hop = 6.25 ms** | ⚠️ **高**——teacher 与 student 的时频网格不同，patch 级对齐本身就有歧义 |
> | **假想的 2 ms 场景** | 可能是"非因果大模型"或"因果浅层模型" | ⚠️⚠️ **最高**——极短窗下高频相位与瞬态细节本就不可靠，teacher 在这些区域的输出可能比 student 更差 |
>
> **结论**：在 2 ms 场景中做 KD，**不能假设 teacher 全局可靠**；DISPATCH 的 KGS 机制（用差值而不是单一分量选择蒸馏区域）**几乎是必需的**，而不是可选的优化。
>
> ⚠️ 但必须诚实说明：**DISPATCH 的 patch 机制本身依赖于一个稳定的时频网格**（固定 patch 尺寸 + 逐帧切分），在严格的流式因果实现中，**"对整段的 patch 排序取 top-k%"是一个跨时间的全局操作，无法直接在线执行**。**这是迁移时必须解决的架构问题**——可能的做法是用滑动窗口的历史统计近似（但会引入延迟）或改用逐帧/逐 patch 的在线判据。**本库中尚无论文处理过这个问题。**

## 2. 之前的人怎么做不了？（limitation → gap）

### 2.1 既有路线的局限与本文 gap

| 既有路线 | 论文指出的局限 | 本文要补的缺口 |
|---|---|---|
| Pruning [4] / Quantization [5] | 论文仅列举，**未批评** | —（本文不用这两种手段） |
| 常规 response-based KD [9][11]–[13][17] | "forces the student to **mimic the teacher's output entirely**" | 只蒸馏有用的 patch |
| 常规 KD 对 student 已收敛区域 | "yields **minimal benefit**" | 显式排除 student 已学好的区域 |
| 常规 KD 对 teacher 做错的区域 | "leads the student to **replicate the teacher's weakness instead of its strengths**" | 用 KGS 显式排除 |
| ⭐ **Importance-weighted KD** [18][19] | "**presuppose that the teacher is uniformly superior to the student for a given input**"，"inevitably **transfer local artifacts even under reduced weights**" | 不用权重、**直接丢弃**这些 patch |
| ⭐ **Uncertainty-aware KD** [20][21] | 同上——都基于 "teacher 全局优于 student" 的假设 | 同上 |
| **Subband-KD** [13] | "limitation … arising from **static band partitioning**" | （由 DFKD 解决，本文沿用 DFKD 的分界） |
| ⭐ **DFKD** [17] | "**remains limited by relying on the entire teacher output, which may contain low-quality time–frequency regions**" | ⭐ **本文的主要攻击点**——DFKD 的动态分带解决了"怎么切"，但没解决"切完之后哪些该蒸" |
| 单一 patch 尺寸 | "**A single, uniform patch size is suboptimal for DISPatch** because it fails to account for the **heterogeneous characteristics of speech signals across frequency bands**" | 用 MSSP 分频带用不同 patch 尺寸 |

本文的 gap 可以一句话概括：

> **即使解决了"频带怎么切"（DFKD），KD 仍然在"哪些 patch 该蒸"上没有选择性；而实证表明 teacher 在 46.8% 的 patch 上并不比 student 更好。**

### 2.2 延迟与因果审计表

> [!warning] **本节对本文的结论是"论文不涉及"，而非"论文做得不好"**

| 审计项 | PDF 证据 | 所属对象 | 本 Wiki 判定 |
|---|---|---|---|
| **STFT window** | **32 ms**（Hann，"we apply DISPatch using the STFT with a **Hann window of 32 ms**"） | 全部 | ⭐ **这是本文唯一与低时延相关的硬数值**。32 ms 窗远超约 2 ms |
| **hop** | **8 ms**（"and **a hop size of 8 ms**, corresponding to **75% overlap**"） | 全部 | 8 ms hop，75% overlap |
| **采样率** | **16 kHz**（"all audio clips are 4-second segments sampled at **16 kHz**"；测试集同样 16 kHz） | 全部 | ✔ 明确（数据层面）；⚠️ **但论文未说明 STFT 的 32 ms/8 ms 是否在 16 kHz 下计算**（16 kHz 下 32 ms = 512 samples、8 ms = 128 samples，为整数，**自洽**，但论文未写明） |
| **算法延迟（显式值）** | **未报告** | 全部 | ❌ **未报告**。论文**从未讨论延迟概念** |
| **time path padding** | **未提及** | student | ❌ **未报告**。论文全文无 "causal" 一词 |
| **causal 声明** | **无任何 causal 相关表述** | teacher / student | **`non-causal`（未声明）** |
| **teacher 结构（因果性推断）** | **ConvTasNet (Deep w/ PReLU)** [23] + **DCCRN-CL** [2] | teacher | **`non-causal-teacher`**——ConvTasNet 的 TCN 与 DCCRN 的 LSTM 都不以因果为设计前提。⚠️ **论文未讨论 teacher 的因果性** |
| **student 结构** | ConvTasNet 1.75M（{N,L,B,H,Sc,P,X,R} = {128, 40, 128, 256, 128, 3, 7, 2}）；DCCRN-CL 2.24M（encoder 通道 {32,64,128,128,256,256}，1 层 complex LSTM，128 hidden） | student | 架构非流式 → **不是低时延候选** |
| **state 缓存 / 流式设计** | **未提及** | student | ❌ **未报告** |
| **warm-up / reset** | **未报告** | student | ❌ **未报告** |
| **compute** | 只给 **MAC/s**（ConvTasNet 8.05G → 0.57G；DCCRN-CL 15.33G → 3.84G） | 全部 | ⭐ **MAC/s 口径明确**（每秒音频的乘加数），比 DFKD 的 FLOPs 口径更清楚。但 MAC/s 不是延迟 |
| **RTF / p99 / 硬件** | **全部未报告** | 全部 | ❌ **缺失** |
| ⭐ **patch 选择的在线可行性** | DISPatch 对整段谱图做 patch 排序取 **top-k%** | **KD 训练阶段** | ⭐ **这是训练时的操作，不影响推理延迟**；但它**依赖整段的全局排序**，因此**该机制本身不可流式化**（若要在在线场景使用需重新设计） |
| **end-to-end** | **未报告** | 全部 | ❌ **未验证** |

**因果性判定汇总**：

| 对象 | 判定 | 依据 |
|---|---|---|
| Teacher（ConvTasNet、DCCRN-CL） | **`non-causal-teacher`** | 架构不以因果为前提；论文无因果性表述 |
| Student（ConvTasNet、DCCRN-CL 压缩版） | ⚠️ **`non-causal`（未声明）** | 论文**从未讨论因果性**；student 由 teacher 减通道而来 |
| KD 机制本身 | ⭐ **训练期全局操作**（top-k% 排序） | **不可流式化**——即使 student 是因果的，该选择机制也需要整段信息。⚠️ **这是迁移到低时延时的关键架构障碍** |
| 本 Wiki 定位 | **不适合作为低时延候选** | 无任何延迟或因果证据；32 ms 窗 |

### 2.3 Latency ledger（延迟账本）

| 项目 | 论文证据 | 证据边界 |
|---|---|---|
| 采样率 | **16 kHz** | ✔ 明确（数据层面） |
| 分析窗 / hop | **32 ms Hann / 8 ms**（75% overlap） | ⭐ **本库中时序信息最明确的一篇 KD 论文**（对比：DFKD 完全未报告） |
| 帧内可读样本 | 16 kHz 下 32 ms = 512 samples、8 ms = 128 samples | ⚠️ **本页按 16 kHz 换算，但论文未明写 STFT 采样率** |
| 算法延迟 | **未报告** | ❌ 论文未讨论延迟概念 |
| look-ahead | **未报告** | ❌ 缺失 |
| MAC/s | ConvTasNet 8.05G → 0.57G；DCCRN-CL 15.33G → 3.84G | ✔ 明确，**口径清楚** |
| 参数量 | ConvTasNet 9.71M → 1.75M；DCCRN-CL 9.22M → 2.24M | ✔ 明确 |
| ⭐ **DISPatch 的训练开销** | "approximately **1.2% per epoch** when used with DFKD on ConvTasNet" | ✔ 明确（**训练期开销，不影响推理**） |
| RTF / p99 / 目标硬件 | **全部未报告** | ❌ 缺失 |
| warm-up / 长流稳定性 | **未报告** | ❌ 缺失 |
| 端到端 capture-to-playback | **未报告** | ❌ 缺失 |

> [!note] 与 DFKD 的对比
> 在**时序信息的完整度**上，DISPATCH **明显优于** [[wiki_low_latency/sources/2025/Dynamic Frequency-Adaptive KD 2025]]：
> - DISPATCH 报告了 **32 ms 窗 / 8 ms hop**，DFKD **完全没有**；
> - DISPATCH 报告了 **MAC/s**（口径清楚），DFKD 只给 FLOPs（口径不明）；
> - DISPATCH 报告了**训练开销 +1.2%/epoch**，DFKD 无。
>
> 但**两者都不面向低时延**，32 ms 窗同样远超约 2 ms。

## 3. 这个做法核心 trick 是什么？

### 3.1 整体流程（仅还原 txt 中明确的内容）

论文第 2 节的流程可逐句核对：

~~~text
noisy speech ──STFT──┬──> Teacher ──> ŝ^T（复谱）
                     ├──> Student ──> ŝ^S（复谱）
                     └──> Target  ──> s  （干净复谱）
                                │
                ┌───────────────┴────────────────┐
          patch 化（尺寸 N，单帧宽）         patch 化
                │                                │
          E_p^T = ε(s_p, ŝ_p^T)          E_p^S = ε(s_p, ŝ_p^S)
                └────────────┬───────────────────┘
                             │
                  KGS_p = E_p^S − E_p^T   （Eq. 5）
                             │
                  取 KGS 排名前 k% 的 patch
                             │
          L_DISPatch = 加权 L_KD 只施加于选中的 patch（Eq. 6）
                             │
          L_total = α·L_SE + (1−α)·L_DISPatch（Eq. 8，α = 0.5）
~~~

论文明确说明 teacher 冻结（"Throughout the DFKD training, the teacher model's parameters are kept constant"——⚠️ 这是**论文对 DFKD 的描述**，DISPATCH 沿用了同一训练范式）。

> [!question] Fig.1 的还原边界
> 上图是**按第 2.1–2.4 节的正文文字与公式重构的**，**不是从 Fig.1 还原的**——Fig.1 在 txt 中被压成碎片（见前文 warning）。
> 论文 Fig.1 的图注（txt 中**可辨**，第 99-100 行）给出了 patch 尺寸：**"Patch size: $2C \times N \times 1$"**——即 patch 覆盖 **全部 $2C$ 个通道、$N$ 个频率 bin、1 个时间帧**。
> ⭐ **注意 "$2C$" 中的 2**：由于是复数谱，实部与虚部各 $C$ 个通道，合计 $2C$。

### 3.2 Trick A：Knowledge Gap Score（KGS）

**这是本文的核心机制。**

**Step 1**：定义 patch 化的误差（Eq. 1）：

$$
e_p = \big\lVert\, |s_p| - |\hat s_p| \,\big\rVert_2^2.
\tag{1}
$$

符号含义：

- $s_p$、$\hat s_p \in \mathbb{R}^{2C \times N \times 1}$：第 $p$ 个 patch 在 **target** 与 **估计**复谱中的对应切片；
- $|\cdot|$：取**幅度**（丢弃相位）；
- $p \in \{0, \ldots, P-1\}$：patch 索引；
- $N = FT/P$：每个 patch 的频率 bin 数（**每个 patch 只含单帧**）；
- ⚠️ **该式的范数阶数在 txt 中被压成 "22"**（见前文 warning 第 4 条），本页按 $\lVert\cdot\rVert_2^2$ 书写。

> [!note] 零填充的细节（论文明确给出，值得记录）
> 论文原文："In practice, we use **zero padding along the frequency axis so that $F$ becomes a multiple of $N$**. Specifically, padding is used **only at the high-frequency end** of the spectrogram, and **padded bins are ignored in all computations**."
> ⭐ **"padding 只用在高频端且被完全忽略"** 这一点很重要——它保证了 patch 切分**不会引入虚假的低频信息**。这与 DFKD 的"分界点可能落在任意位置"形成对比。

**Step 2**：误差序列与线性回归（Eq. 2–3）：

对每个 patch，在训练过程中每 **1000** 步记录一次误差，得到序列 $(e_p^{(0)}, e_p^{(1)}, \ldots, e_p^{(J)})$。对序列做一阶多项式拟合：

$$
f(a_p, b_p) = \min_{a_p, b_p} \sum_{j=0}^{J} \left( e_p^{(j)} - (a_p j + b_p)\right)^2.
\tag{2}
$$

- $a_p$：拟合直线的**斜率**，代表误差的收敛/发散趋势；
- $b_p$：截距。

**Step 3**：计算"误差变化量"与"平均误差"（Eq. 3）：

$$
\Delta e_p = a_p \cdot J,
\tag{3a}
$$

$$
e_{mean} = \frac{1}{P}\sum_{p=0}^{P-1} e_p^{(J)}.
\tag{3b}
$$

- $\Delta e_p$：从拟合直线**首点到末点的变化量**——**负值表示误差在下降（收敛），正值表示在上升（发散）**；
- $e_{mean}$：**最终迭代点上所有 patch 的平均误差**——作为"收敛得好不好"的相对基准。

**Step 4**：计算 teacher 与 student 的 patch 误差（Eq. 4）：

$$
E_p^S = \varepsilon(s_p, \hat s_p^S),\qquad
E_p^T = \varepsilon(s_p, \hat s_p^T).
\tag{4}
$$

- 上标 $S$ / $T$：student / teacher；
- $\varepsilon(\cdot,\cdot)$：**patch 级误差度量，论文明确说它"designed to be flexible"**——"It can be defined as a simple magnitude spectrogram distance (e.g., L1 or L2) or as a more advanced objective, such as the one proposed in **DFKD [17]**"。
- ⚠️ **论文在实验中使用的是 L2**（第 3.3 节："For an ablation study on the components of KGS, we adopt **objective L2** to align with the analysis setup in Section 2.1"）。

**Step 5**：⭐ **定义 Knowledge Gap Score（Eq. 5）**：

$$
KGS_p = E_p^S - E_p^T.
\tag{5}
$$

论文对该式的解释：

> "A **higher $KGS_p$ indicates a greater knowledge disparity**, suggesting that the teacher's knowledge in that patch is **particularly valuable for distillation**."

> [!note] ⭐ KGS 的直觉：为什么"差值"比"单一分量"好
> $KGS_p = E_p^S - E_p^T$ 同时编码了两个条件：
> - **$E_p^T$ 小**（teacher 在这个 patch 做得好）→ KGS 大；
> - **$E_p^S$ 大**（student 在这个 patch 做得差）→ KGS 大。
>
> **两者必须同时满足** KGS 才大。论文在 Table 3 中用实验证明了这一点（见 4.4 节）：
> - 只用 $E_p^T$（teacher 误差）→ 会**选出 teacher 做得差的 patch**，没有蒸馏价值；
> - 只用 $E_p^S$（student 误差）→ 会**选出 student 已经做得好的 patch**（因为误差高不一定是学不好，也可能是这个 patch 本身难），且**无法排除 teacher 也做得差的 patch**。
> - ⭐ **论文的表述**："$KGS_p$ selects patches based on the **difference** $(E_p^S - E_p^T)$, **inherently considering both counterparts** to identify regions with the most significant potential for student improvement."

**Step 6**：选择性蒸馏损失（Eq. 6–7）：

$$
L_{\mathrm{DISPatch}} = \frac{1}{P \cdot k\%}\sum_{i=0}^{P-1} I_{k\%}(KGS_p)\cdot L_{KD}(\hat s_p^S, \hat s_p^T),
\tag{6}
$$

$$
I_{k\%}(KGS_p) =
\begin{cases}
1 & \text{if } KGS_p \text{ ranks in the top } k\%,\\
0 & \text{otherwise.}
\end{cases}
\tag{7}
$$

- $L_{KD}(\cdot,\cdot)$：**patch 级的 KD 损失**——⚠️ **论文没有指定它是什么**，只说 "$L_{KD}$ is a KD loss for $p$-th patch"。在实验中，DISPATCH 被应用于 "response-based KD methods, including **L1, L2, and DFKD**"，即 $L_{KD}$ 随基线方法变化；
- $I_{k\%}(\cdot)$：**指示函数**，只对 KGS 排名前 $k\%$ 的 patch 置 1；
- $k$：**patch 选择比例**，实验设为 **80**（即选 80% 的 patch）。⚠️ **论文没有报告 $k$ 的敏感性分析**——这在论文的 future work 中被承认（"investigate the suitable top-k setting"）。

> [!question] Eq. (6) 的求和下标矛盾（txt 已核对，矛盾属实）
> txt 中该式的求和变量写作 $i$（$i=0$ 到 $P-1$），但**被求和的表达式下标全部是 $p$**。
> **这应是论文的记号笔误**（$i$ 与 $p$ 在本式中应指同一索引），不是抽取错误。本页按原文保留并在此标注。
> ⚠️ 另注：分母是 $P \cdot k\%$，而不是"被选中的 patch 数"——由于 $I_{k\%}(\cdot)$ 的 1 的个数按定义就是 $P \cdot k\%$，**两者等价**，这一写法是正确的。

### 3.3 Trick B：MSSP——分频带用不同 patch 尺寸

论文的声学动机（第 2.3 节，**这段是本页认为论文写得最扎实的部分之一**）：

> "**Acoustic phonetics** shows that **low-frequency regions are typically dominated by fine-grained structured information such as formants**, which are crucial for **vowel identity** [24]. In contrast, **high-frequency regions often contain broader, less-structured energy patterns, such as those found in fricatives** [25]."

> "Therefore, we propose Multi-Scale Selective Patches (MSSP), which uses a **smaller patch size for low frequencies** and a **larger one for high frequencies** to account for these heterogeneous characteristics."

⭐ **一个关键的声学事实**：DISPATCH 是**本库中唯一明确引用声学语音学文献（[24] Diehl 2008 关于共振峰与元音识别、[25] Jongman 2000 关于英语擦音声学特性）来为蒸馏设计提供依据的论文**。这使它的"分频带"主张比 DFKD 的"<4 kHz 语音主导、>4 kHz 噪声主导"更精细——**DFKD 按噪声/语音能量比分区，DISPATCH 按语音的内部结构粒度分区。**

**MSSP 的实现方式**（论文明确）：

> "To implement MSSP, we identify the **dynamic crossover point by adopting the frequency adapter from DFKD [17]**, which determines the boundary for each time frame."

即 **MSSP 直接复用 DFKD 的 Frequency Adapter**（即 [[wiki_low_latency/sources/2025/Dynamic Frequency-Adaptive KD 2025]] 的累积最大值导数法）来定位分界点，然后在两侧用不同 patch 尺寸。

论文说明了 MSSP 与 DFKD 的**概念一致性**：

> "The **combination of MSSP and DFKD is conceptually aligned**, as both adopt **frequency-dependent objectives**. Accordingly, we integrate MSSP into DFKD to evaluate the effect of employing distinct patch sizes across low and high frequencies."

以及**损失配置的对应关系**：

> "In practice, a **phase-only cosine loss** is used in the **low-frequency band**, while the **high-frequency band uses a combination of amplitude L2 and phase losses**."

⭐ **注意这与 DFKD 的损失配置完全一致**（低频纯相位、高频幅度+相位）——MSSP 继承的正是 DFKD 的频带损失哲学。

**patch 尺寸消融**（Table 2，见 4.3 节）：测试了 **20/20（uniform）、10/20、20/40、10/40** 四种配置，**10/40（低频小、高频大）在全部模型与数据集上最优**。

### 3.4 总损失与训练

$$
L_{total} = \alpha \cdot L_{SE} + (1 - \alpha)\cdot L_{DISPatch}.
\tag{8}
$$

- $L_{SE}$：**标准 SE 损失，沿用各模型原论文的定义**；
- $\alpha$：**论文明确取 0.5**（"In our experiments, we set $\alpha$ to **0.5**, giving **equal weight** to direct supervision and selective knowledge distillation"）；
- ⭐ 论文专门说明了 $\alpha$ **不是逐方法调优的**："To avoid overfitting the weighting to any particular method, we **fix $\alpha$ across all models and different KD objectives**, rather than tuning it per method."

> [!note] 与 DFKD 的一个关键区别
> DFKD 的 $\alpha$ **未报告**（见 [[wiki_low_latency/sources/2025/Dynamic Frequency-Adaptive KD 2025]] 第 5.2 节），而 DISPATCH **明确取 0.5 并说明了理由**。
> **DISPATCH 在可复现性上明显优于 DFKD。**

### 3.5 核心 trick 判断

**本文的核心是 Trick A（KGS），MSSP 是次要的增益放大器。** 判断依据：

| Trick | 证据 | 判断 |
|---|---|---|
| **A. KGS 选择性** | 在 DFKD 上叠 DISPatch 带来**全部指标的改善**（Table 1，12/12 组）；且 Table 3 证明 KGS 差值优于任何单分量 | ⭐ **核心** |
| **B. MSSP** | Table 2 显示 10/40 优于 20/20，但**增益幅度小于 KGS 本身**（见 4.3 节） | 次要 |

**KGS 是本文与 DFKD 的真正分界线**：DFKD 解决"**怎么切频带**"，DISPATCH 解决"**切完之后蒸哪些 patch**"。论文自己也把 DISPatch 定位为**可以叠加在 DFKD 之上的插件**（"We incorporate DISPatch into conventional KD methods and observe consistent gains"）。

## 4. 实验里哪个消融最关键？

### 4.1 数据与训练设置

| 项目 | 论文设置 |
|---|---|
| 训练数据 | **DNS2020 挑战赛** [26]：**>500 小时** clean speech + **>100 小时** noise |
| 混合方式 | 各种 SNR，**0 到 20 dB 均匀采样** |
| 片段长度 | **4 秒** |
| 采样率 | **16 kHz** |
| 评测集 1 | **DNS2020 challenge test set** |
| 评测集 2 | **VoiceBank+DEMAND** [27]（16 kHz） |
| 评价指标 | **WB-PESQ、NB-PESQ、STOI(%)** |
| Student 模型 1 | **ConvTasNet (Deep w/ PReLU)** [23]，**1.75M**，{N,L,B,H,Sc,P,X,R} = **{128, 40, 128, 256, 128, 3, 7, 2}** |
| Teacher 模型 1 | 同架构，**9.71M**，{N,L,B,H,Sc,P,X,R} = **{512, 16, 128, 512, 128, 3, 8, 3}** |
| Student 模型 2 | **DCCRN-CL** [2]，**2.24M**，encoder 通道 **{32,64,128,128,256,256}**，**1 层** complex LSTM、**128** hidden |
| Teacher 模型 2 | 同架构，**9.22M**，encoder 通道 **{64,128,256,256,512,512}**，**2 层** complex LSTM、**256** hidden |
| STFT（DISPatch 用） | **Hann 窗 32 ms，hop 8 ms**（75% overlap） |
| Patch 尺寸 $N$ | 分析用 **20**；DISPatch 单尺寸也用 **20**；MSSP 测试 **10/20、20/40、10/40** |
| Patch 选择比例 $k$ | **80**（%） |
| 优化器 | **Adam** |
| 学习率 | 初始 **$1\times10^{-3}$**，连续 **3** 个 epoch 验证损失不改善则减半 |
| 早停 | 连续 **10** 个 epoch 不改善则停止 |
| 训练轮数 | **100 epochs** |
| Batch size | **16** |
| 梯度裁剪 | L2 norm 上限 **5** |
| $\alpha$ | **0.5** |
| DISPatch 额外开销 | 配 DFKD + ConvTasNet 时约 **+1.2% / epoch**（训练期） |
| Patch 数量 $P$ | ❌ **未报告** |
| 硬件 / 训练时长 | ❌ **未报告** |

> [!note] 可复现性观察
> DISPATCH 的可复现性在本库 KD 论文中属于**较好的一档**：
> - ✔ 两个 teacher 与两个 student 的**完整超参配置**都给出了；
> - ✔ STFT 窗/hop、patch 尺寸、$k$、$\alpha$、优化器、学习率、epoch、batch size、梯度裁剪**全部给出**；
> - ✔ 提供了**代码链接**（`https://github.com/rlaehghks5/DISPATCH`）——这是本库 KD 论文中**唯一一篇给出代码仓库的**（对比：[[wiki_low_latency/sources/2024/Distil-DCCRN 2024]] 无代码链接、[[wiki_low_latency/sources/2025/Dynamic Frequency-Adaptive KD 2025]] 无代码链接）；
> - ❌ **patch 数量 $P$ 未报告**——这是 KGS 机制的一个基本参数（P 决定了 top-k% 的粒度）；
> - ❌ **$k$ 的敏感性未做**（论文在 future work 中承认）。

### 4.2 Table 1：主结果（已逐行核对）

> [!question] Table 1 的行合并结构
> txt 中 `ConvTasNet (Teacher)` / `ConvTasNet (Student)` / `DCCRN-CL (Teacher)` / `DCCRN-CL (Student)` 是**跨行标签**（第 228、233、238、243 行），它们与上/下数据行的归属需按论文表格布局判断。
> 本页按下表整理（Teacher 行只有 Scratch；Student 行有 Scratch/L1/L2/DFKD/DISPatch 系列），**建议回查原 PDF 确认**。

| Model | Param. | MAC/s | Method | DISPatch | DNS2020 WB-PESQ | DNS2020 NB-PESQ | DNS2020 STOI | VBD WB-PESQ | VBD NB-PESQ | VBD STOI |
|---|---:|---:|---|:---:|---:|---:|---:|---:|---:|---:|
| ConvTasNet (**Teacher**) | 9.71M | 8.05G | Scratch | ✗ | **2.792** | **3.337** | **96.71** | **2.770** | **3.582** | **94.12** |
| ConvTasNet (**Student**) | 1.75M | 0.57G | Scratch | ✗ | 2.563 | 3.122 | 96.05 | 2.585 | 3.424 | 93.44 |
| | | | L1 | ✗ | 2.584 | 3.135 | 96.11 | 2.584 | 3.429 | 93.57 |
| | | | L1 | **✓** | 2.602 | 3.165 | 96.16 | 2.614 | 3.450 | 93.79 |
| | | | L2 | ✗ | 2.563 | 3.127 | 95.98 | 2.556 | 3.400 | 93.37 |
| | | | L2 | **✓** | 2.602 | 3.157 | 96.10 | 2.603 | 3.431 | 93.39 |
| | | | DFKD | ✗ | 2.623 | 3.170 | 96.08 | 2.583 | 3.458 | 93.70 |
| | | | DFKD | **✓** | 2.650 | 3.208 | 96.12 | 2.589 | 3.490 | 93.81 |
| | | | **DFKD + MSSP(10/40)** | **✓** | **2.677** | **3.226** | **96.17** | **2.618** | **3.505** | **94.02** |
| DCCRN-CL (**Teacher**) | 9.22M | 15.33G | Scratch | ✗ | **2.764** | **3.318** | **96.38** | **2.655** | **3.591** | **92.94** |
| DCCRN-CL (**Student**) | 2.24M | 3.84G | Scratch | ✗ | 2.691 | 3.247 | 96.08 | 2.582 | 3.482 | 92.96 |
| | | | L1 | ✗ | 2.660 | 3.236 | 96.07 | 2.631 | 3.454 | 92.98 |
| | | | L1 | **✓** | 2.709 | 3.270 | 96.13 | 2.678 | 3.497 | 93.20 |
| | | | L2 | ✗ | 2.690 | 3.241 | 95.96 | 2.587 | 3.446 | 92.96 |
| | | | L2 | **✓** | 2.726 | 3.283 | 96.08 | 2.675 | 3.486 | 93.04 |
| | | | DFKD | ✗ | 2.719 | 3.279 | 96.06 | 2.635 | 3.476 | 93.04 |
| | | | DFKD | **✓** | 2.757 | 3.291 | 96.10 | 2.618 | 3.490 | 93.13 |
| | | | **DFKD + MSSP(10/40)** | **✓** | **2.758** | **3.301** | **96.10** | **2.719** | **3.535** | **93.29** |

### 4.3 Table 2：MSSP 的 patch 尺寸消融（已逐行核对）

| Model | low/high | DNS2020 WB-PESQ | DNS2020 NB-PESQ | DNS2020 STOI | VBD WB-PESQ | VBD NB-PESQ | VBD STOI |
|---|---|---:|---:|---:|---:|---:|---:|
| ConvTasNet | **20/20**（uniform） | 2.650 | 3.208 | 96.12 | 2.589 | 3.490 | 93.81 |
| | 10/20 | 2.630 | 3.191 | 96.01 | 2.555 | 3.470 | 93.66 |
| | 20/40 | 2.662 | 3.211 | 96.12 | 2.626 | 3.483 | 93.76 |
| | **10/40** ⭐ | **2.677** | **3.226** | **96.17** | **2.618** | **3.505** | **94.02** |
| DCCRN-CL | **20/20**（uniform） | 2.757 | 3.291 | 96.10 | 2.618 | 3.490 | 93.13 |
| | 10/20 | 2.746 | 3.295 | 96.09 | 2.690 | 3.506 | 93.28 |
| | 20/40 | 2.745 | 3.298 | 96.11 | 2.668 | 3.506 | 93.16 |
| | **10/40** ⭐ | **2.758** | **3.301** | **96.10** | **2.719** | **3.535** | **93.29** |

论文对 Table 2 的解读：

> "For both models and across two datasets, the configuration applying a **smaller patch size in low frequencies and a larger patch size in high frequencies (10/40) achieves the highest scores**, outperforming using only a small low-frequency patch (10/20) or only a large high-frequency patch (20/40) when compared to the uniform patch size (20/20)."

⭐ **注意这里有一个重要的对照逻辑**：论文用 `10/20` 和 `20/40` 作为**两个单边对照**，证明"低频变小"和"高频变大"**各自单独都不够**，必须**同时做**。

用 Table 2 的数据验证这个论证：

**ConvTasNet（DNS2020 WB-PESQ）**：
- `20/20` = 2.650（基准）
- `10/20` = 2.630 → **低频变小单独作用：−0.020** ❌ **变差**
- `20/40` = 2.662 → **高频变大单独作用：+0.012**
- `10/40` = **2.677** → **两者同时：+0.027** ⭐

> [!note] 这个论证在 ConvTasNet 上是成立的，在 DCCRN-CL 上不完全成立
> **DCCRN-CL（DNS2020 WB-PESQ）**：
> - `20/20` = 2.757（基准）
> - `10/20` = 2.746（**−0.011**）
> - `20/40` = 2.745（**−0.012**）
> - `10/40` = **2.758**（**+0.001**）⭐
>
> ⚠️ **在 DCCRN-CL 的 DNS2020 上，10/40 相对 uniform 的增益只有 +0.001**——这在 3 位小数的精度下**几乎为零**。
> 增益主要集中在 DCCRN-CL 的 **VoiceBank+DEMAND** 上（2.719 vs 2.618，**+0.101**）和 ConvTasNet 的 DNS2020 上（+0.027）。
> **论文的表述 "achieves the highest scores" 在字面上正确（10/40 确实是每列最高），但 "outperforming" 的强度在 DCCRN-CL / DNS2020 这一格上非常微弱。论文未报告方差或显著性检验。**

### 4.4 Table 3：KGS 分量的消融 ⭐ **本文最关键的表**

| Selection Criterion | DNS2020 WB-PESQ | DNS2020 NB-PESQ | DNS2020 STOI | VBD WB-PESQ | VBD NB-PESQ | VBD STOI |
|---|---:|---:|---:|---:|---:|---:|
| ⭐ **Top-k by KGS**（本文） | **2.602** | **3.157** | **96.10** | **2.603** | **3.431** | **93.39** |
| Top-k by $E_p^T$（teacher 误差高） | 2.551 | 3.110 | 95.94 | 2.559 | 3.401 | 93.46 |
| Bottom-k by $E_p^T$（teacher 误差低） | 2.570 | 3.134 | 96.07 | 2.556 | 3.430 | 93.30 |
| Top-k by $E_p^S$（student 误差高） | 2.587 | 3.146 | 96.10 | 2.577 | 3.418 | 93.38 |
| Bottom-k by $E_p^S$（student 误差低） | 2.566 | 3.136 | 95.97 | 2.585 | 3.430 | 93.23 |

> [!note] Top-k 与 Bottom-k 的含义
> 论文明确："where **Top-k and Bottom-k** denote selecting the **highest and lowest $k$% patches**, respectively."
> 对照组统一使用 **L2 作为 KD 目标**（论文："we adopt **objective L2** to align with the analysis setup in Section 2.1"）。
> ⚠️ 因此这张表的**基准应为 Table 1 中 ConvTasNet student + L2 + DISPatch 的 2.602**——**与 KGS 行完全一致**（2.602 / 3.157 / 96.10 / 2.603 / 3.431 / 93.39）✔ 说明该表确实是基于 ConvTasNet + L2 的配置。

论文对这五个判据的分析（**这段是本文方法论的核心论证**）：

> "Table 3 shows that the proposed $KGS_p$ is the **most effective selection criterion**, whereas **relying on a single component degrades performance**."
>
> "First, the patches selected by **Top-k by $E_p^T$** or **Bottom-k by $E_p^S$** are **not priorities for distillation**, as they select **patches with high teacher error** and **patches where the student's error is already low**."
>
> "Second, although selecting patches with **Bottom-k by $E_p^T$** and **Top-k by $E_p^S$** are individually informative, **$KGS_p$ still outperforms them**. This gap occurs because **each single component criterion fails to exclude its uninformative or harmful complement**, respectively. For example, **Bottom-k by $E_p^T$ fails to filter out patches where the student is already proficient (low $E_p^S$)**, and **Top-k by $E_p^S$ fails to avoid patches where the teacher also performs poorly (high $E_p^T$)**."

> [!note] 这五个判据的逻辑结构（本页整理）
>
> | 判据 | 想选什么 | 实际选到 | 问题 |
> |---|---|---|---|
> | Top-k by $E_p^T$ | teacher 做得**差**的 | ❌ **完全错**——选到了没有蒸馏价值的地方 | 方向反了 |
> | Bottom-k by $E_p^T$ | teacher 做得**好**的 | ✔ 一半对——但**没排除 student 已经学好的** | 遗漏 student 侧 |
> | Top-k by $E_p^S$ | student 做得**差**的 | ✔ 一半对——但**没排除 teacher 也做得差的** | 遗漏 teacher 侧 |
> | Bottom-k by $E_p^S$ | student 做得**好**的 | ❌ **完全错** | 方向反了 |
> | ⭐ **Top-k by KGS** | **teacher 好 AND student 差** | ✔ **两者兼得** | — |
>
> ⭐ **这是本文最有说服力的实验**：它不只是说"我们的方法更好"，而是**用四个对照完整地论证了"为什么必须用差值"**。这在本库的 KD 论文中是最严谨的一类消融设计。

### 4.5 哪个消融最能隔离方法贡献？

#### A. ⭐ 最干净：`DFKD + DISPatch off` vs `DFKD + DISPatch on`（同一 student、同一 base KD）

| Model | 方法 | DISPatch | DNS2020 WB-PESQ | Δ | VBD WB-PESQ | Δ |
|---|---|:---:|---:|---:|---:|---:|
| ConvTasNet | DFKD | ✗ | 2.623 | — | 2.583 | — |
| | DFKD | ✓ | **2.650** | **+0.027** | **2.589** | **+0.006** |
| DCCRN-CL | DFKD | ✗ | 2.719 | — | 2.635 | — |
| | DFKD | ✓ | **2.757** | **+0.038** | 2.618 | **−0.017** |

同样的对照在 L1 与 L2 上也做了：

| Model | 方法 | DISPatch ✗ | DISPatch ✓ | Δ DNS2020 WB-PESQ |
|---|---|---:|---:|---:|
| ConvTasNet | L1 | 2.584 | **2.602** | +0.018 |
| ConvTasNet | L2 | 2.563 | **2.602** | **+0.039** |
| DCCRN-CL | L1 | 2.660 | **2.709** | **+0.049** |
| DCCRN-CL | L2 | 2.690 | **2.726** | +0.036 |

⭐ **这是最干净的对照**：同一 student、同一 base KD 目标、同一数据、同一评测，**唯一变量是是否施加 DISPatch 的 patch 选择**（$\alpha$ 固定 0.5、$k$ 固定 80、patch 尺寸固定 20）。

**结论**：**8 个 DNS2020 对照全部为正**（+0.018 到 +0.049），说明选择机制本身有稳定的增益。

⚠️ **但 VoiceBank+DEMAND 上并非全部为正**：DCCRN-CL + DFKD 的 DISPatch 开/关在 VBD 上是 **2.618 vs 2.635（−0.017）**——⚠️ **这是唯一一个 DISPatch 使结果变差的格子，论文没有讨论**。（不过在 DCCRN-CL + DFKD + MSSP 的组合下 VBD 回升到 **2.719**，说明 MSSP 掩盖了这个问题。）

#### B. ⭐ 次干净且论证最完整：Table 3 的五个判据对照

见 4.4 节。**这是本文最有价值的表**，因为它隔离的是"**用什么判据选 patch**"这一核心设计决策，而且给出了完整的四组对照来解释**为什么**。

#### C. 中等干净：`DFKD` vs `DFKD + MSSP(10/40)`

见 4.3 节。这个对照的变量是"**patch 尺寸配置**"，但注意它**同时改变了两件事**（低频变小 + 高频变大），因此**不能分离两个变化的各自贡献**——不过论文用 `10/20` 与 `20/40` 两个单边对照补上了这一点 ✔。

#### D. ⭐ 一个论文未强调但很有价值的观察：L1/L2 的基线增益非常有限

| Model | Scratch | L1 | L2 | Δ L1 | Δ L2 |
|---|---:|---:|---:|---:|---:|
| ConvTasNet | 2.563 | 2.584 | 2.563 | +0.021 | **0.000** |
| DCCRN-CL | 2.691 | 2.660 | 2.690 | **−0.031** | **−0.001** |

论文对此的表述（**这是本文对 SE KD 领域的一个重要诊断**）：

> "Table 1 indicates that **magnitude distance-based KD methods (L1, L2) offer marginal gains over the scratch baseline and often result in performance degradation**."

⭐ **即：单纯的 magnitude 距离 KD 在 SE 上几乎无效（甚至有害）；加上 DISPatch 后才变得有效**（ConvTasNet + L2：2.563 → 2.602，**+0.039**；DCCRN-CL + L1：2.660 → 2.709，**+0.049**）。

**这是本文一个隐含的、比"我们更好"更重要的结论：SE 的输出级 KD 之所以效果差，很可能是因为"全盘蒸"稀释了有用的监督信号。**

#### E. ❌ 不干净的对照

- **Teacher vs Student**（ConvTasNet 2.792 vs 2.677）—— 混淆了参数量（9.71M vs 1.75M）、MAC/s（8.05G vs 0.57G）与蒸馏，**不能用来评估 KD 效果**。⚠️ **注意在一切配置下，student 都没有达到 teacher**（DNS2020 WB-PESQ 最好的 student 是 2.677，teacher 是 2.792）——**与 DFKD 不同，本文没有"student 超过 teacher"的声称** ✔ 这是本文表述上更诚实的地方。

### 4.6 人声保留 / 低 SNR 证据边界

> [!warning] 本文的人声保留证据同样**极其薄弱**
>
> **PDF 中完全不存在**以下证据：
> - ❌ **无任何 SNR 分层**——训练与测试的 SNR 统一为 **0–20 dB**（论文明确："mixed at various Signal-to-Noise Ratios (SNRs) **uniformly sampled from 0 to 20 dB**"）。**没有任何负 SNR 结果**；
> - ❌ **无 babble / 竞争说话人 / 瞬态噪声分层**；
> - ❌ **无 false-suppression 指标**；
> - ❌ **无 SPP / VAD 校准**；
> - ❌ **无 ASR WER**；
> - ❌ **无 F0 / formant / prosody continuity**——⚠️ **这是本文一个特别值得点出的反差**：论文在**方法动机**中明确引用了**声学语音学文献**，指出"低频区域的**共振峰（formants）**对**元音识别**至关重要"（引 [24]），但**整篇论文没有任何一个实验测量共振峰或元音的保留情况**！**声学动机与评测完全脱节**；
> - ❌ **无 voiced energy 保留率**；
> - ❌ **无 DNSMOS 或任何 MOS 类指标**——全文只有 **PESQ 和 STOI**；
> - ❌ **无 SIG / BAK 分解**；
> - ❌ **无主观听测**。
>
> **本文对"人声保留"最接近的表述是方法层面的**——低频用更小的 patch（10 vs 40）以捕捉"fine-grained structured information such as formants"。**这只是设计意图，没有任何实验验证它确实保护了共振峰。**
>
> ⚠️ **与 FDKD 相比的一个区别**：DFKD 至少用低频"纯相位损失"间接指向了语音保真；DISPATCH 的 patch 尺寸差异**完全不改变损失的形式**（MSSP 与 DFKD 的损失配置一致），只是改变了**统计粒度**。因此 DISPATCH 的"保护共振峰"主张**比 DFKD 的"保护音色"更难被验证**。

### 4.7 计算量与部署证据

| 项目 | 本文状态 |
|---|---|
| MAC/s | ✔ 给出（两个 teacher × 两个 student） |
| 参数量 | ✔ 给出 |
| MAC/s 口径 | ✔ **明确**（每秒音频的乘加数） |
| ⭐ DISPatch 训练开销 | ✔ 明确（**+1.2%/epoch**，配 DFKD + ConvTasNet） |
| RTF | ❌ **未报告** |
| p50/p95/p99 | ❌ **未报告** |
| 峰值 RAM / SRAM | ❌ **未报告** |
| 量化精度 | ❌ **未报告** |
| 目标硬件 | ❌ **未报告**（论文只说 "on-device AI"，未指定设备） |
| deadline / underrun | ❌ **未报告** |
| 端到端延迟 | ❌ **未报告** |

> [!note] ⭐ 与 DFKD 的重要区别：DISPATCH 的额外开销**不在推理侧**
> DISPatch 的机制（patch 化 + KGS 计算 + top-k% 排序）**完全发生在训练阶段**。推理时 student 就是原样的 student，**没有任何额外计算**。
> 论文明确量化了这一点：**"+1.2% per epoch"**（训练期）。
> ⭐ **这对低时延迁移是有利的一面**：DISPATCH 的机制**不会增加推理延迟**——它只改变训练信号的分配。**这与"加模块"类方法（如 RaD-Net 2 的 ASA）有本质区别。**
> ⚠️ **但不利的一面是**：该选择机制**依赖整段的全局排序**（见 2.2 节），因此在**训练**时无法在线应用于流式数据——**不过训练本来就不需要流式，所以这个问题实际上不影响迁移**。真正的问题是：**如果要在 2 ms 场景用这个机制，需要有一个能看全段的 teacher 来生成可靠的选择信号**。

## 5. 这个方向还剩什么问题没解决？（future work / limitation）

### 5.1 论文自己承认的局限

论文第 4 节 Conclusions 的结尾明确列出了 future work：

> "**Future work will extend the principle of selective transfer to other speech tasks, such as speech separation and speech restoration, and investigate the suitable top-k setting and a wider range of patch sizes.**"

即论文承认两处**自身设计参数未充分探索**：

| 承认的局限 | 论文原话 |
|---|---|
| **$k$ 的取值未调优** | "investigate the **suitable top-k setting**" |
| **patch 尺寸范围未充分探索** | "a **wider range of patch sizes**" |

⚠️ **除此之外，论文没有承认任何其他局限**——特别是**没有承认任何与低时延、SNR 分层或人声保留相关的缺口**（因为它不在这个问题域内）。

> [!note] 论文在正文中还有一处"隐含承认"
> 在引用 DFKD 时，论文写道"DISPatch is **simple to plug into** existing response-based KD objectives that **utilize a spectrogram**"。
> ⚠️ 这句话隐含了一个限制：**DISPatch 需要频域（spectrogram）的 student 输出**。对于**纯时域模型**（如 ConvTasNet 的时域版本、或任何 waveform-domain 模型），该机制**无法直接应用**——必须先转成时频表示。
> **这是一个论文没有明说但影响迁移范围的限制。**

### 5.2 本 Wiki 审计出的缺口

> [!warning] 本文的低时延相关缺口与 DFKD 一样是**结构性的**

| 缺口 | 本文状态 | 说明 |
|---|---|---|
| ⭐ **完全不面向低时延** | 论文全文**无 causal / latency / real-time / streaming / RTF** | **问题设定不同**，非缺陷 |
| ⭐ **32 ms 窗 / 8 ms hop** | 明确报告 ✔ | **距约 2 ms 差 16 倍**。这是本文唯一可用的时序信息 |
| ⭐ **任何延迟数值缺失** | 0 个延迟数字 | 无法评估时序可行性 |
| ⭐ **Teacher 非因果** | ConvTasNet（TCN）+ DCCRN-CL（LSTM） | 若迁移到低时延，teacher 需重新设计；**但 DISPATCH 的机制本身不要求 teacher 因果** |
| ⭐ **Student 非流式** | ConvTasNet 1.75M / DCCRN-CL 2.24M | 都不是 2 ms 候选 |
| ⭐ **KD 机制依赖全局排序** | top-k% over all patches | 机制本身不可流式化（但只在训练期使用，影响有限） |
| **Patch 数量 $P$ 未报告** | ❌ 缺失 | $P$ 决定 KGS 的粒度，是机制的基本参数 |
| **$k$ 的敏感性未做** | ❌ 论文自己承认 | 最优 $k$ 未知 |
| **patch 尺寸范围有限** | 只有 10/20/40 三个值 | 论文自己承认需要"wider range" |
| **46.8% 的统计口径不清** | ⚠️ 论文只说 "a single speech sample" 与 "at the J-th point"，**未说明样本数** | 这个数字是全文最重要的事实依据，口径不清是明显缺口 |
| **$\varepsilon(\cdot,\cdot)$ 的灵活性未被利用** | 实验只用 L2 | 论文说 $\varepsilon$ 可以是 L1/L2 或 DFKD 的度量，但**只测了 L2** |
| **无 teacher 可靠性的分层分析** | **缺失** | 论文证明了 teacher 在 46.8% patch 上更差，**但没有分析这些 patch 有什么特征**（是高频？是瞬态？是低位语音？）——⭐ **这是本页认为最有价值的未解问题** |
| **SNR 分层** | **完全没有负 SNR** | 训练测试均为 0–20 dB |
| **噪声类型分层** | **缺失** | babble、竞争说话人、瞬态、未见噪声 |
| ⭐ **人声保留指标与声学动机脱节** | 论文引 [24][25] 论共振峰与擦音，**但零相关测量** | false-suppression、SPP/VAD、ASR WER、F0/formant/prosody、voiced energy、SIG/BAK **全部缺失** |
| **只报 PESQ / STOI** | 无 DNSMOS、无 SIG/BAK、无 SI-SDR | 评测维度偏窄 |
| **统计显著性** | 无方差、无置信区间、无多次运行 | ⭐ **Table 2 中 DCCRN-CL / DNS2020 的 10/40 vs 20/20 只差 0.001**，这类差值需要显著性检验；论文未做 |
| **DCCRN-CL + DFKD 在 VBD 上 DISPatch 变差** | **−0.017，论文未讨论** | 见 4.5 节 A |
| **代码开源** | ✔ **提供**（`https://github.com/rlaehghks5/DISPATCH`） | ⭐ 本库 KD 论文中唯一一篇 |
| **硬件 / 训练时长** | ❌ **未报告** | — |

### 5.3 ⭐ 本页读出的最重要的未解问题

> [!question] **teacher 做得比 student 差的那 46.8% 的 patch，究竟长什么样？**
> 论文证明了这种现象**存在**，证明了**用它做筛选有效**，但**完全没有分析它的成因或特征**。
>
> **如果能回答这个问题，会带来三重价值**：
> 1. **方法层面**：可以设计更廉价、更可解释的判据（不必每次都算 $E_p^S$ 与 $E_p^T$）；
> 2. **KD 理论层面**：可以解释为什么 SE 的输出级 KD 效果差（论文自己的观察：L1/L2 几乎无增益甚至有害）；
> 3. ⭐ **低时延层面**：如果能确定"teacher 不可靠区域"的模式（例如集中在**高频**、**瞬态**、**低能量帧**），就能预判在 2 ms 极短窗场景下这些区域会如何扩张——**这对设计低时延 KD 的 teacher 选择策略是直接可用的知识**。
>
> **本库中没有任何论文回答过这个问题。**

> [!note] 另一个本页读出的机会：把 DISPatch 与"频带差异化监督"组合
> [[wiki_low_latency/sources/2025/Dynamic Frequency-Adaptive KD 2025]] 在**损失形式**上做频带差异（低频纯相位、高频幅度+相位）；
> DISPATCH 在**统计粒度**上做频带差异（低频小 patch、高频大 patch）。
>
> **两者是正交的维度**——理论上可以叠加：**用 KGS 判据在一个按频带差异化损失的空间里选择 patch**。实际上 DISPATCH 已经部分做了这件事（它把 MSSP 集成进 DFKD，而 DFKD 的损失本身就是频带差异化的），但**没有把 KGS 的判据本身做成频带相关的**（例如低频用相位敏感的误差度量、高频用幅度敏感的度量）。
> ⭐ **"band-dependent KGS metric" 是一个自然的、本库中尚无人尝试的扩展。**

### 5.4 与库内其它 KD 论文的关系

> [!note] DISPATCH 在本库 KD 谱系中的位置
>
> | 论文 | 蒸馏层级 | 频带处理 | 选择机制 | 低时延 | 代码 |
> |---|---|---|---|---|---|
> | [[wiki_low_latency/sources/2023/Two-Step Knowledge Distillation for Tiny SE 2023]] | 输出 + 中间 | 无 | 无 | ⚠️ 因果，32ms | ❌ |
> | [[wiki_low_latency/sources/2024/Distil-DCCRN 2024]] | 输出 + 中间（AT+KL） | 无 | 无 | ❌ 25ms 窗 | ❌ |
> | [[wiki_low_latency/sources/2024/RaD-Net 2 2024]] | **仅输出**（多项加权） | 无 | 无 | ❌ 20ms 窗 | ❌ |
> | [[wiki_low_latency/sources/2025/Dynamic Frequency-Adaptive KD 2025]] | **仅输出** | ⭐ **动态二分频带** | 无 | ❌ 未报告 STFT | ❌ |
> | [[wiki_low_latency/sources/2026/RT-SEMamba 2026]] | 输出 + 中间 + ramp-up | 无 | 无 | ❌ 25ms 窗 | ❌ |
> | ⭐ **DISPATCH (2025)** | **仅输出** | ⭐ **动态二分频带 + MSSP** | ⭐ **KGS top-k%** | ❌ **32ms 窗** | ✔ |
>
> ⭐ **DISPATCH 是本库中唯一引入"选择性蒸馏"机制的论文**，也是唯一有代码的 SE KD 论文。
>
> **它与 RaD-Net 2 的对照特别有意思**：
> - **RaD-Net 2**：teacher 与 student **同容量**，唯一差别是 padding 因果性 → **论文自己控制住了 teacher 可靠性问题**（因为 teacher 就是 student 的非因果版）；
> - **DISPATCH**：teacher 与 student **容量差 5.5 倍**（9.71M vs 1.75M）→ **teacher 在 46.8% patch 上反而更差**。
>
> **两者从不同角度触碰了同一个问题**："KD 的监督信号有多少是可信的？"**但两篇论文都没有意识到对方的存在。**

## 6. 本论文在库中的位置关联（cross-reference matrix）

| 关系 | 库中页面/论文 | 关联与边界 |
|---|---|---|
| ⭐ **前身/基石（本库中最强关联，有 PDF 级证据）** | [[wiki_low_latency/sources/2025/Dynamic Frequency-Adaptive KD 2025]] | ⭐ **DISPATCH 是 DFKD 的直接后续、批评者与整合者**，且**有 PDF 级证据**：DISPATCH 的参考文献 **[17]** 明确列出 "Xihao Yuan, Siqi Liu, Hanting Chen, Lu Zhou, Jian Li, and Jie Hu, **Dynamic frequency-adaptive knowledge distillation for speech enhancement**, in ICASSP, 2025"——即 DFKD。本文在**至少 6 处**引用 [17]。<br>**具体关系**：<br>① **DISPATCH 明确批评 DFKD**："Although DFKD has shown strong performance, it **remains limited by relying on the entire teacher output, which may contain low-quality time–frequency regions**."；<br>② **DISPATCH 把 DFKD 作为自己的实验基线**（Table 1 中有 DFKD 行）；<br>③ **DISPATCH 把 MSSP 集成进 DFKD**（"we integrate MSSP into DFKD"），即 **DFKD 是 DISPATCH 的载体方法**；<br>④ **MSSP 直接复用 DFKD 的 Frequency Adapter** 作为动态分界点；<br>⑤ **MSSP 的损失配置与 DFKD 完全一致**（低频纯相位 cosine、高频幅度 L2 + 相位）；<br>⑥ ⚠️ **DFKD 未引用 DISPATCH**（DFKD 于 2025-02 发表，DISPATCH v1 于 2025-09）——**单向引用**。<br>**两者的分工**：DFKD 解决"**频带怎么切**"；DISPATCH 解决"**切完之后蒸哪些 patch**" |
| **同分支竞品（SE 输出级 KD）** | [[wiki_low_latency/sources/2024/Distil-DCCRN 2024]] | 同为 SE 的 KD 论文，但路线不同：<br>① **蒸馏层级**：Distil-DCCRN 做**中间特征**（AT + KL）；DISPATCH 只做**输出**（spectrogram patch）；<br>② **核心机制**：Distil-DCCRN 解决**维度不匹配**（teacher hop 10ms vs student hop 6.25ms）；DISPATCH 解决**区域选择**；<br>③ ⭐ **一个值得注意的对照**：Distil-DCCRN 的消融显示 **AT（中间特征）是最大增益来源（+0.11 PESQ）**；DISPATCH 显示 **纯输出 KD 加上选择机制后也能稳定取得增益**（+0.018～+0.049）。**两者不矛盾但方向不同**——"频带差异化的中间特征蒸馏 + patch 选择"是一个未被任何人尝试的天然组合；<br>④ ⚠️ **两篇互未引用** |
| **同分支竞品（RaD-Net 2 的因果 KD）** | [[wiki_low_latency/sources/2024/RaD-Net 2 2024]] | ⭐ **两篇从不同角度触碰了"teacher 可靠性"问题**：<br>① **RaD-Net 2**：teacher 与 student **同参数量（2.21M/2.21M）、只差 padding 因果性**——**论文自己把 teacher 可靠性差异控制到了最小**；<br>② **DISPATCH**：teacher 与 student **差 5.5 倍容量**，**实证发现 teacher 在 46.8% patch 上更差**；<br>③ ⭐ **两者的交叉启示**：RaD-Net 2 的干净对照**恰恰是 DISPATCH 缺失的那类实验**（同容量 teacher，可靠性可保证）；而 DISPATCH 的 KGS 机制**恰恰是 RaD-Net 2 缺失的那类保护**（RaD-Net 2 用全盘蒸馏，未检查 teacher 是否在局部更差）。**把 KGS 用到 RaD-Net 2 的因果 KD 上是本库最明显的组合机会之一**；<br>④ ⚠️ **两篇互未引用**（RaD-Net 2 于 2024-06，DISPATCH 于 2025-09） |
| **前身/基石（被压缩对象）** | [[wiki_low_latency/sources/2020/DCCRN Low-Latency Direction 2020]] | DISPATCH 的两个实验模型之一，参考文献 [2] 即 DCCRN。⚠️ 论文**从未讨论 DCCRN 的因果性或 look-ahead**（同 DFKD 的情形） |
| **概念页（复数谱与相位）** | [[wiki_low_latency/concepts/2008.00264-complex-phase-enhancement]] | 源自 DCCRN 的复数相位增强概念页。DISPATCH 的低频"phase-only cosine loss"与高频"amplitude L2 + phase"的组合**直接继承自 DFKD**，间接与复数相位增强相关。⚠️ 该概念页未包含 DISPATCH 内容 |
| **概念页（人声保留评估）** | [[wiki_low_latency/concepts/低 SNR 人声保留评估]] | ⭐ **本文是该 scorecard 最值得点名的负面样本之一**：<br>① 论文**引用了声学语音学文献 [24]（Diehl 2008，共振峰与元音识别）与 [25]（Jongman 2000，英语擦音声学特性）**，明确以"低频共振峰对元音识别至关重要"作为 MSSP 的动机；<br>② **但整篇论文没有任何一个实验测量共振峰、元音或擦音的保留**；<br>③ 无 SNR 分层（0–20 dB）、无 DNSMOS/SIG/BAK、无 false-suppression、无 ASR WER、无 F0/prosody。<br>**这是"声学动机与评测设计完全脱节"的典型案例** |
| ⚠️ **疑似关联，需用户确认** | [[wiki_low_latency/sources/2023/Two-Step Knowledge Distillation for Tiny SE 2023]] | 同为 SE 的特征/输出 KD，但 Two-Step 解决的是**训练范式**（两步 vs 混合），DISPATCH 解决的是**区域选择**。⚠️ **互未引用，关联较弱** |
| ⚠️ **疑似关联，需用户确认** | [[wiki_low_latency/sources/2026/RT-SEMamba 2026]] | 两者都是 SE 的 KD 论文且**互未引用**。RT-SEMamba 的 progressive KD 是**输出 + 中间 + ramp-up**；DISPATCH 是**输出 + patch 选择**。⚠️ **关联较弱，仅在"SE KD"分类下成立** |
| ⚠️ **疑似关联，需用户确认** | [[wiki_low_latency/concepts/2608.12099-mamba-distillation]] | 该概念页展开 RT-SEMamba 的 KD 公式。⚠️ **疑似关联** |
| ⚠️ **疑似关联，需用户确认** | [[wiki_low_latency/sources/2023/FSB-LSTM 2023]] | FSB-LSTM 用 full-band/sub-band 集成建模，DISPATCH 的 MSSP 也做分频带处理。**一个在架构层面分带、一个在蒸馏统计粒度上分带**。⚠️ **无引用关系，需用户确认** |
| ⚠️ **疑似关联，需用户确认** | [[wiki_low_latency/sources/2024/Ultra-Low Latency Speech Enhancement Comprehensive Study 2024]] | 该研究提出低时延审计需"同时报告窗口、模型容量和 MACs"。⚠️ DISPATCH 在窗口（32ms ✔ 报告）与 MAC/s ✔ 报告上**比 DFKD 好**，但仍**无 RTF、无硬件**。链接的意义仅在于展示审计框架。**本文不在低时延问题域内** |
| ⚠️ **疑似关联，需用户确认** | [[wiki_low_latency/sources/2023/Uncertainty-Aware Speech Enhancement 2023]] | ⭐ **一个有意思的概念对照**：DISPATCH 在 Introduction 中明确批评 **uncertainty-aware KD [20][21]**（"presuppose that the teacher is uniformly superior to the student"）。而库内该 source 页讨论的是**不确定性感知的抑制**（在 SE 模型内部用不确定性调节 gain），**不是 KD 中的不确定性**。⚠️ **两者是"不确定性"这个词在不同层面的使用（KD 的教师可靠性 vs 增强模型的抑制风险），关联为概念对照而非谱系，需用户确认是否值得链接** |
| ⚠️ **疑似关联，需用户确认** | [[wiki_low_latency/sources/2022/DeepFilterNet2 2022]] | DeepFilterNet2 真正面向部署（RTF + 目标硬件）；DISPATCH 以 "on-device AI" 为动机但**零部署测量**。⚠️ **关联为"证据对比"，需用户确认** |

> [!question] 关联不确定性
> - 与 [[wiki_low_latency/sources/2025/Dynamic Frequency-Adaptive KD 2025]] 的关联**有 PDF 级证据**（本文参考文献 [17]，且在方法、实验、结论中反复引用），**强关联，是本页最重要的谱系链接**。
> - 与 [[wiki_low_latency/sources/2024/RaD-Net 2 2024]] 的关联为**本页读出的方法学交叉**（都触碰"teacher 可靠性"问题），⚠️ **两篇互未引用**，是**潜在实验机会**而非文献谱系。
> - 与 [[wiki_low_latency/sources/2024/Distil-DCCRN 2024]]、[[wiki_low_latency/sources/2023/Two-Step Knowledge Distillation for Tiny SE 2023]]、[[wiki_low_latency/sources/2026/RT-SEMamba 2026]] 的关联为**同期/近似同任务的并行工作**。⚠️ **均互未引用，需用户确认**。
> - 与 [[wiki_low_latency/sources/2023/Uncertainty-Aware Speech Enhancement 2023]] 的关联是**概念对照**（论文批评的是 KD 语境下的 uncertainty-aware 方法 [20][21]，而库内该页是 SE 模型内部的不确定性）——**⚠️ 疑似关联，需用户确认**。
> - ⚠️ **本页未使用** [[wiki_low_latency/sources/2021/Noise Suppression Losses 2021]]、[[wiki_low_latency/sources/2022/Hybrid Continuity Loss 2022]]、[[wiki_low_latency/sources/2021/DPCRN Low-Latency Direction 2021]]、[[wiki_low_latency/sources/2023/GCFSnet 2023]]、[[wiki_low_latency/sources/2022/STFT-Domain Very Low Algorithmic Latency 2022]]、[[wiki_low_latency/sources/2024/SlowFast-SSM 2024]]、[[wiki_low_latency/sources/2021/On TasNet Low-Latency SE 2021]] 作为关联项——**本文完全不涉及低 SNR 损失设计、连续性/过抑制、双路径复数循环、双耳链路、短窗 STFT、状态空间模型或因果 TasNet**，强行链接会误导。
> - ⭐ **本页的核心判断**：DISPATCH 在本 wiki 中的定位是 **「方法学类比 + teacher 可靠性的实证警示」，不是「直接竞品」**。它与本方向的连接点是"**蒸馏监督信号的选择性**"这一思想，**而不是任何延迟、因果性或部署指标**。

## 7. 一句话总结"江湖地位"

~~~text
2025 | SE 模型压缩 / 选择性 patch 知识蒸馏 | 用实证推翻"teacher 全局可靠"这一 KD 隐含假设——测得 teacher 在 46.8% 的谱图 patch 上误差反而高于 student；据此提出 Knowledge Gap Score（KGS = E_p^S − E_p^T），只对 KGS 排名前 k% 的 patch 施加 KD 损失，并用 MSSP 在低频用小 patch（10）、高频用大 patch（40）匹配语音的声学结构粒度；在 ConvTasNet 与 DCCRN-CL 上，DISPatch 使 L1/L2/DFKD 三种基线在全部 DNS2020 对照上一致改善（+0.018～+0.049 WB-PESQ），并在 Table 3 中用四组对照完整论证了"为何必须用差值而非任何单一分量" → 成为 DFKD (2025) 的直接后续、批评者与整合者（DISPATCH 批评 DFKD"依赖整个 teacher 输出，其中含低质量时频区域"，同时复用其 Frequency Adapter 作为 MSSP 的动态分界点）；但其 32ms 窗、零因果性声明、零延迟/RTF 数值、零 SNR 分层与"引用声学语音学论证共振峰却从不测量共振峰"的动机-评测脱节，使它在约 2ms 严格因果方向上只能作为"选择性监督"的方法学参照；不过它对 teacher 可靠性的实证质疑，以及"DISPatch 开销只在训练期（+1.2%/epoch）、推理零成本"这一性质，对低时延 KD 有直接可用的警示价值。
~~~

## 参考资料

- [arXiv:2509.15922](https://arxiv.org/abs/2509.15922)
- 本地原件：raw/papers/low_latency_causal_se/2509.15922.pdf
- arXiv:2509.15922v2 [cs.SD]，26 Jan 2026（v1 为 2025-09）
- 作者单位：**School of Electrical Engineering, KAIST, Daejeon, Republic of Korea**（通讯作者：Jung-Woo Choi）
- ⭐ 代码：`https://github.com/rlaehghks5/DISPATCH`（**本库 SE KD 论文中唯一提供代码仓库的一篇**）
- 致谢：National Research Foundation of Korea (NRF) grant No. RS-2024-00337945；STEAM research grant No. RS-2024-00464269（MSIT）；BK21 FOUR program（MOE）
- 论文参考文献 [2]：Hu, Liu, Lv, Xing, Zhang, Fu, Wu, Zhang, Xie, "DCCRN: Deep complex convolution recurrent network for phase-aware speech enhancement," Interspeech, 2020（→ 库内 [[wiki_low_latency/sources/2020/DCCRN Low-Latency Direction 2020]]；**实验模型之一**）
- 论文参考文献 [13]：Hao, Wen, Su, Liu, Gao, Li, "**Sub-band knowledge distillation framework for speech enhancement**," Interspeech, 2020（**Subband-KD，静态分带**）
- 论文参考文献 [14]：Park, Shin, Kim, Han, "Leveraging non-causal knowledge via cross-network knowledge distillation for real-time speech enhancement," IEEE SPL, vol. 31, pp. 1129–1133, 2024（⚠️ **标题含 "non-causal knowledge" 与 "real-time"，是本文参考文献中唯一直接涉及因果性与实时性的工作——值得单独追踪**）
- 论文参考文献 [15]：Wan, Zhou, Peng, Chang, Lu, "**ABC-KD: Attention-based-compression knowledge distillation for deep learning-based noise suppression**," Interspeech, 2023（**对比方法**）
- ⭐ 论文参考文献 [17]：Yuan, Liu, Chen, Zhou, Li, Hu, "**Dynamic frequency-adaptive knowledge distillation for speech enhancement**," ICASSP, 2025（→ 库内 [[wiki_low_latency/sources/2025/Dynamic Frequency-Adaptive KD 2025]]；**本文的直接前身与整合对象**）
- 论文参考文献 [18]：Kim, Ham, Lee, Jang, Kim, "Maximizing discrimination capability of knowledge distillation with energy function," Knowledge-Based Systems, 2024（⚠️ **被本文批评的 importance-weighted KD 之一**）
- 论文参考文献 [20]：Jin, Lan, Zeng, Chen, "Uncertainty-aware multi-shot knowledge distillation for image-based object re-identification," AAAI, 2020（⚠️ **被本文批评的 uncertainty-aware KD 之一**）
- 论文参考文献 [22]：Lin, Gou, Gong, Liu, Shen, Xu, Lin, Yang, Jiao, Duan et al., "**Rho-1: Not all tokens are what you need**," NeurIPS, 2024（⭐ **本文的核心灵感来源**——"训练模型时只用有用的 token，由在高质量数据集上训练的参考模型识别"；DISPATCH 把这个 LLM 的想法迁移到 SE 的谱图 patch）
- 论文参考文献 [23]：Kadıoğlu, Horgan, Liu, Pons, Darcy, Kumar, "An empirical study of Conv-TasNet," ICASSP, 2020（**实验模型之一**）
- ⭐ 论文参考文献 [24]：Diehl, "**Acoustic and auditory phonetics: the adaptive design of speech sound systems**," Philosophical Transactions of the Royal Society B, vol. 363, no. 1493, pp. 965–978, 2008（**MSSP 的声学依据之一：低频共振峰与元音识别**）
- ⭐ 论文参考文献 [25]：Jongman, Wayland, Wong, "**Acoustic characteristics of English fricatives**," JASA, vol. 108, no. 3, pp. 1252–1263, 2000（**MSSP 的声学依据之二：高频擦音的能量模式**）
- 论文参考文献 [26]：Reddy, Gopal, Cutler, Beyrami, Cheng, Dubey, Matusevych, Aichner, Aazami, Braun, Rana, Srinivasan, Gehrke, "The INTERSPEECH 2020 deep noise suppression challenge," Interspeech, 2020（**训练数据集**）
- 论文参考文献 [27]：Valentini-Botinhao, Wang, Takaki, Yamagishi, "Investigating RNN-based speech enhancement methods for noise-robust text-to-speech," 9th ISCA SSW, 2016（**VoiceBank+DEMAND**）
- ⚠️ **本页未生成图片资产**：原论文 **Fig.1（DISPatch 框架总览，patch size $2C\times N\times 1$）** 与 **Fig.2（patch 级 teacher-student 失配分析：(a) 混淆矩阵、(b) 误差散点图）** 在 txt 抽取中**完全不可还原**，需主 agent 统一处理渲染与嵌入；本页不做图结构推断。
