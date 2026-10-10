---
title: PrimeK-Net 2025
type: source
paper: "PrimeK-Net: Multi-scale Spectral Learning via Group Prime-Kernel Convolutional Neural Networks for Single Channel Speech Enhancement"
authors: Zizhen Lin, Junyu Wang, Ruili Li, Fei Shen, Xi Xuan
year: 2025
venue: ICASSP 2025
venue_status: published
arxiv: 2502.19906
doi: 10.48550/arXiv.2502.19906
local_pdf: raw/papers/low_latency_causal_se/2502.19906.pdf
evidence_policy: arXiv_pdf
created: 2026-09-27
updated: 2026-09-27
tags:
  - speech-enhancement
  - prime-kernel
  - multi-scale
  - channel-attention
  - dense-block
  - depthwise-separable
  - non-causal
  - two-stage
  - voicebank-demand
related:
  - [[wiki_low_latency/entities/PrimeK-Net]]
  - [[wiki_low_latency/concepts/2502.19906-prime-kernel-multiscale-dense-block]]
  - [[wiki_low_latency/sources/2026/LaCo-SENet 2026]]
  - [[wiki_low_latency/entities/LaCo-SENet]]
---

# PrimeK-Net 2025

> [!important] 本页在库中的特殊位置
> PrimeK-Net 是 [[wiki_low_latency/sources/2026/LaCo-SENet 2026]] **直接沿用的骨干**（LaCo-SENet 的 §3.3 明写「骨干沿用 PrimeK-Net [3] 的分解方式」、损失「完全沿用 PrimeK-Net」）。
> 因此补摄 PrimeK-Net 的价值**主要不在它自己**，而在于：**它是 LaCo-SENet 全部结论的上界与原型**——LaCo-SENet 的 1.37 M 骨干、TS 分解方式、五个损失分项、以及 Table 1 里的「非因果上界 3.61 PESQ」都指向这一篇。
> **但必须诚实指出：PrimeK-Net 不是低时延论文。** 它全文没有任何延迟数字、没有 causal 声明、没有流式讨论。它是**非因果的质量上界**。

## 快速索引卡片

~~~yaml
- 论文: PrimeK-Net (ICASSP 2025, arXiv:2502.19906)
  ├── 要解决什么问题: 两阶段 SE 的两个核心组件各有缺陷——Conformer 是 O(t²) 复杂度（显存随帧数平方增长，限制边缘设备）；DDB 的通道维随层数增长（C² 项），参数与算力膨胀；且固定感受野忽略了频谱的自然多尺度分布
  ├── 核心方法: 用 GPFCA（组质数核前馈通道注意力，线性复杂度）替换 Conformer 的位置，用 DSDDB（深度可分离空洞密集块）替换 DDB
  ├── 属于哪个分支: 两阶段（TS）时频域掩蔽增强 / **高效 CNN 架构设计** / 非因果质量上界；**不是**低时延、**不是**流式、**不是**因果
  ├── 输入/输出: 论文未逐一列出输入输出张量口径；STFT 为 FFT size 400 / window 400 / hop 100（@16 kHz ⇒ 25 ms 窗、6.25 ms hop）；输出为幅度谱与相位谱的并行估计（TS 结构，沿用 MP-SENet）
  ├── 关键trick: **用质数当卷积核尺寸**（{3, 11, 23, 31}）来避免周期性响应重叠，同时用四组不同尺度覆盖多粒度感受野；再把空洞卷积分解为 depthwise + pointwise 使复杂度从 O(iC²K²) 降到 O(iCK² + iC²)
  ├── 数据集: VoiceBank+DEMAND（训练/测试标准划分）；语音切成 2 秒片段
  ├── 对比了谁: MP-SENet [5]、SE-Mamba [16]（Table I，**同框架同损失重训**）；Fig. 3(a) 还比 CMGAN / MP-SENet / SE-Mamba / TridentSE
  ├── 性能上限: **PESQ 3.61 / CSIG 4.81 / CBAK 3.98 / COVL 4.35**（1.41 M 参数，44.64 G FLOPs）
  ├── 参数量: **1.41 M**（PrimeK-Net-S 0.79 M）；FLOPs 44.64 G（PrimeK-Net-S 26.45 G）
  ├── 消融关键发现: ① **GPFN→普通宽 FFN：PESQ 3.61→3.51，而参数量 1.41M 完全不变**（证明增益不是来自参数增加）；② **w/o SCA：3.61→3.42，参数量仅少 0.07M**（SCA 是性价比最高的一块）；③ DSDDB→DDB：PESQ 3.61→3.61（不变），参数 1.41M→2.37M（**+68%**）——**这就是"12.7%"论证的实证**；④ 核尺寸 (17,17,17,17)→(5,15,21,27)→**(3,11,23,31)**：3.57→3.59→**3.61**，三行 FLOPs 与参数**完全相同**
  ├── 遗留问题(你的机会): ① **非因果**——两阶段结构 + 频率轴全局操作，无任何因果性声明；② **零延迟数字**——无 RTF、无 ms、无硬件、无量化；③ 窗 400 / hop 100 是 25 ms / 6.25 ms，**远超 2 ms 目标**；④ FLOPs 是**解析值**，无实测速度；⑤ Table I 的"同框架同损失"虽好，但 MP-SENet / SE-Mamba 的**重训是否收敛、有无多种子**未报告；⑥ 无 WER/ASR、无负 SNR 分层、无噪声类型分层、无方差
  └── 跟哪篇像: [[wiki_low_latency/sources/2026/LaCo-SENet 2026]]（**直接后继**：把它的非因果骨干改造成时延可配置）；MP-SENet [5]（损失与 TS 范式的来源）；NAFNet（GPFCA 的通道注意力来源）；HIFI-GAN 的 MPD（质数核的灵感来源）
~~~

## 1. 他们为什么这么做？（motivation）

### 1.1 任务与对象

单通道语音增强，目标是从退化信号中估计干净语音（p.1 Abstract）。论文的定位非常明确：**不是"再做一个更强的增强器"，而是把两阶段（Two-Stage, TS）结构里两个核心组件的效率问题拆开修**。

论文的出发点是对 TS 范式本身的认可（p.1 §I）：

> "Recent advancements in speech enhancement have been inspired by **TSTNN [2]**, often using the two-stage (TS) architecture. ... The TS structure is widely used due to its efficiency to **separate feature extraction for time and frequency dimensions**."

它点名的代表是 **CMGAN [3]**（证明 Conformer 有效，并引入 MetricGAN）与 **MP-SENet [5]**（把 CMGAN 与 PHASEN 结合做相位谱估计）。**这两篇一起构成本文的方法论地基**——损失函数直接沿用 MP-SENet。

### 1.2 论文自己列的三个缺陷（p.1 §I 逐条）

论文把 SOTA 方法的问题写成三条 bullet，**这三条就是它的全部动机**：

| # | 缺陷 | 原文要点 | 本文的对策 |
|---|---|---|---|
| **①** | **Transformer 是 $O(t^2)$** | "Transformers' memory consumption scales with $O(t^2)$, which imposes **many limitations on memory-constrained edge devices**" | GPFCA 用 SCA + GPFN 达到**线性复杂度** |
| **②** | **忽视了频谱的多尺度特性** | "Previous methods have **neglected the multi-scale characteristics of the spectrum**. The Conformer's Transformer and convolutional modules typically consider attention maps in **fixed receptive fields**, ignoring the multi-scale nature of the spectrogram" | GPFN 用四组不同质数核覆盖**多粒度感受野** |
| **③** | **DDB 的效率问题** | "the channel dimension used in advanced methods **increases with the number of layers while the initial $C$ is large**, so we must consider the efficiency problem of $C^2$ in DDB" | DSDDB 把空洞卷积分解为 depthwise + pointwise |

> [!note] 三条缺陷里，只有 ① 是"部署"问题，② 是"建模"问题，③ 是"效率"问题
> 这一点决定了本文的性质：**它不是一篇部署导向的论文**。① 提到 "memory-constrained edge devices"，但论文**从未给出任何端侧实测、量化、RTF 或内存数字**——这句只是复杂度层面的论证（$O(t^2)$ vs 线性）。
> 换句话说：**本文的"边缘设备"动机是用渐近复杂度表达的，不是用实测表达的。** 这与 [[wiki_low_latency/sources/2025/FastEnhancer 2025]] 的"单 CPU 线程实测 RTF"形成鲜明对照。

### 1.3 质数核这一设计的灵感来源（这是本文最有特色的一条）

GPU 的第三点是多尺度，而实现多尺度的关键选择是**用质数当卷积核尺寸**。论文给出了明确的灵感来源（p.3 §II-A）：

> "The prime-kernel design **reduces feature redundancy and improves accuracy by avoiding periodic responses**, inspired by the **Multi-Period Discriminator (MPD) in HIFI-GAN [17]**."

以及（p.2 §II）：

> "GPFCA uses **prime number properties to avoid periodic overlap effects [17]**"

**这个想法的逻辑链是**：卷积核在时间/频率轴上滑动时，若核长为合数，则不同尺度的核之间存在**周期性共振/重叠**（例如核长 6 与 9 在周期 3 上重叠）；取质数则任意两个尺度**互质**，周期结构不会共享，从而减少冗余响应。

论文用 Table III 把这一定性论证做了量化（见 §4.4）——**三行 FLOPs 与参数完全相同，只有核尺寸不同**，是本文最干净的对照。

### 1.4 动机的真实坐标：**它是质量上界，不是低时延方案**

> [!warning] 必须与 LaCo-SENet 的定位严格区分
> | 维度 | PrimeK-Net 2025 | LaCo-SENet 2026 |
> |---|---|---|
> | 因果性 | **未声明**（两阶段 + 频率轴全局操作 ⇒ 实质非因果） | 逐层 padding 分配 + SSU ⇒ **库内唯一可核验因果** |
> | 延迟数字 | **零** | 12.5–200 ms（9 个点） |
> | 流式 | **未讨论** | dual-buffer + chunk-wise ≡ full-sequence |
> | 在库中的角色 | **非因果质量上界**（Table 1 的 3.61） | 时延可配置的因果实现（12.5 ms 保留上界 93%） |
>
> LaCo-SENet 的价值主张正是"**用同样的骨干与损失，把 PrimeK-Net 的未来访问参数化**"。所以读 PrimeK-Net 时应该问的问题是：**它多出来的那 7% PESQ（3.61 vs 3.35 @12.5 ms）究竟买到了什么未来上下文？** 这正是 LaCo-SENet 的 Figure 2 在回答的。

## 2. 之前的人怎么做不了？（limitation → gap）

### 2.1 前人路线的谱系与各自留下的缝

| 前人                                 | 做了什么                               | 留下的缝                               |
| ---------------------------------- | ---------------------------------- | ---------------------------------- |
| **TSTNN [2]**（ICASSP 2021）         | 提出两阶段（时域）Transformer 结构            | 奠定了 TS 范式，但用的是 Transformer         |
| **CMGAN [3]**（Interspeech 2022）    | 证明 Conformer 在 TS 里有效；引入 MetricGAN | Conformer 的 $O(t^2)$ 显存未解          |
| **MP-SENet [5]**（Interspeech 2023） | CMGAN + PHASEN，并行估计幅度与相位谱          | 同上；且感受野固定                          |
| **DDB [9]**（ICASSP 2020）           | 空洞密集块做编解码器                         | **$C^2$ 参数与算力随层数膨胀**               |
| **NAFNet [19]**（ECCV 2022）         | 用高效结构替换 attention 与 FFN，线性复杂度      | 是**图像**复原的 baseline，未适配 SE 的 TS 结构 |
| **GDFN [22]**（Restormer）           | depth-wise gate 前馈网络               | 单尺度                                |
| **HIFI-GAN 的 MPD [17]**            | 多周期判别器，用质数周期避免重叠                   | 是**判别器**设计，未用于 SE 的卷积核选择           |

### 2.2 gap 的准确形状

把上面几条缝合起来，gap 是：

> **在 TS 结构里，"效率"与"多尺度"从来没有被同时解决**——Conformer 提供了长程建模但代价是 $O(t^2)$；DDB 提供了密集连接但代价是 $C^2$；而两者的感受野都是固定的、没有利用频谱的多尺度分布。

论文的答案是把 Conformer 整个换掉（GPFCA），同时把 DDB 的卷积分解（DSDDB）。**两处都是替换，不是叠加。**

### 2.3 一个论文没有直说的 gap：**质数核这个想法在 SE 里此前没有先例**

论文只说灵感来自 HIFI-GAN 的 MPD。但值得记录的是：**MPD 用质数是为了让不同周期的判别器不共享周期**，而本文把它搬到**卷积核尺寸**上，这是**跨任务的思路迁移**。论文没有论证"质数核在频谱卷积上必然优于合数核"的理论依据——它只给了 Table III 的经验对照。

## 3. 这个做法核心 trick 是什么？

### 3.1 整体架构与两个模块的分工

论文总述（p.2 §II 开头）：

> "it features the **Group Prime-kernel Feed-Forward Channel Attention (GPFCA)** module, which **replaces Conformers** in the Two-Stage structure. ... Additionally, we introduce the **Deep Separable Dilated Dense Block (DSDDB)** as a **streamlined modification of DDB [9]** for spectrum encoding and decoding."

~~~text
带噪语音
  → STFT (FFT 400 / window 400 / hop 100)
  → Encoder：DSDDB（谱编码）
  → TS Blocks：GPFCA × N（贯穿时间/频率两阶段做深层特征提取）
        └── 内部 = 通道权重分配层（SCA） + GPFN（组质数核前馈网络）
  → Decoder：DSDDB（谱解码）
  → 并行的 mask / phase 双路输出（沿用 MP-SENet 的 TS 范式）
  → iSTFT
~~~

> [!question] Fig. 1 的还原边界
> 原 PDF 第 2 页 **Fig. 1（整体架构）在文本抽取中只剩一行图注**（`Fig. 1: The overall architecture of the PrimeK-Net.`），**模块标签完全没有进入文本流**。
> 因此上面的管线是**依据 §II 正文的模块描述重构的**，**不是从 Fig. 1 还原的**。TS Blocks 的层数、GPFCA 的堆叠数量、双 decoder 的连接方式**均需回查原 PDF 第 2 页的渲染图**（`wiki_low_latency/assets/primek-net_2025/primek-page2.png`）。
> **本页不对未确认的连接拓扑做断言。**

### 3.2 Trick A：GPFCA = 通道注意力（SCA）+ 组质数核前馈网络（GPFN）

**GPFCA 的设计哲学**（p.2 §II-A）：

> "Inspired by **NAFNet [19]**, we found that **while retaining a module framework similar to that of the Transformer [15], substituting the attention mechanism and feed-forward neural network (FFN) with more efficient structures can achieve competitive performance while maintaining linear complexity**."

#### 3.2.1 通道权重分配层：SCA（Eq. 1）

$$\operatorname{SCA}(X) = X \odot \operatorname{PWC}\big(\operatorname{AAP}(X)\big) \tag{1}$$

- $\operatorname{AAP}$（adaptive average pooling）：**把每个通道的整条序列压成一个标量**；
- $\operatorname{PWC}$（point-wise convolution）：由这个标量算出通道权重；
- $\odot$：与原 $X$ 相乘，完成通道权重分配。

论文对这一层的定性（p.3）：

> "this scalar captures **global information to some extent**, as it leverages the **entire feature map of the current channel**. Simplified Channel Attention **avoids the $O(t^2)$ complexity of Self Attention**, providing computational efficiency while maintaining **key functions: aggregating global information and facilitating channel interactions**."

> [!important] SCA 与 Self-Attention 的关键差别（对低时延方向有直接含义）
> SCA 用 **AAP 把时间轴整个压掉**，只留一个 per-channel 标量。
> ⇒ **它在时间轴上没有"查询-键"交互，因此天然不存在"必须看到未来帧才能算权重"的问题**；但它同时也**丢掉了时间轴的位置结构**（只剩全局均值）。
> 对照：Self-Attention 在时间轴上需要按位置计算相似度，**若不做 causal mask 就必然读取未来**——这是库内时间轴 attention 类方法（如 FastEnhancer 的 DPT，见 [[wiki_low_latency/overview]] 判据③）在流式下的核心负担。
> **SCA 是一个"时间轴全局池化"的操作，它在因果性上比 attention 干净，但在建模能力上更弱。** 论文没有讨论这一取舍。

#### 3.2.2 GPFN：四组质数核的深度门控（Eq. 2–4）

**Step 1 —— 把第一次 point-wise conv 的输出沿通道维切成四组**（Eq. 2）：

$$a_1,a_2,a_3,a_4 = \operatorname{chunk}(X) \tag{2}$$

**Step 2 —— 定义第 $i$ 个 Depth-wise Fusion Gate（DFG）**（Eq. 3），论文说灵感来自 **GDFN [22]**（Restormer 的 depth-wise gate）：

$$\operatorname{DFG}_i(X_i,k_i) = \operatorname{PWC}\big(\operatorname{DWC}_{k_i}(X_i)\big)\odot\operatorname{DWC}_{k_i}(X_i) \tag{3}$$

其中 $\operatorname{DWC}_{k_i}$ 是核长为 $k_i$ 的**深度卷积**。**注意这里是门控结构：$\operatorname{DWC}$ 的输出同时走两条路——一条经 $\operatorname{PWC}$ 产生门，另一条作为被门控的值，再逐元素相乘。**

**Step 3 —— 四组分别用四个质数核，再沿通道维拼接**（Eq. 4）：

$$\operatorname{GPGU}(X) = \operatorname{CONCAT}\Big(\operatorname{DFG}_i\big(a_i,k_i\big)\ \big|\ a_i=\operatorname{chunk}(X)[i],\ i\in\{1,2,3,4\}\Big) \tag{4}$$

论文明确给出四个核（p.3）：

> "For the grouped $a_1, a_2, a_3$, and $a_4$, DFG is computed with **prime number kernel sizes of $\{3, 11, 23, 31\}$** respectively."

**Step 4 —— GPFN 用 point-wise conv 融合四组多尺度特征并调整通道维**。

> [!important] {3, 11, 23, 31} 这组数值的三个性质（这是本文最值得记住的一格）
> | 性质 | 说明 |
> |---|---|
> | **全是质数** | 论文的主张是"避免周期性响应/重叠"。任意两个互质 ⇒ 不存在共享的周期结构 |
> | **跨越大尺度范围** | 3（短程）→ 31（长程），跨度 10×，覆盖"瞬态与持续语音变化"两个极端 |
> | **同时是频域核** | GPFN 作用在**频率轴**上（TS 结构中 GPFCA 替换 Conformer 的位置）⇒ 核长 31 意味着**一次覆盖 31 个频点**的局部结构——这对捕捉**谐波间距**是合理的尺度 |
>
> **但论文没有给出 {3, 11, 23, 31} 的选型依据**——为什么不是 {3, 13, 29, 37}？为什么是四个而不是三个？Table III 只对比了"单尺度 / 非质数多尺度 / 质数多尺度"三档，**没有做核尺寸的敏感性扫描**。

### 3.3 Trick B：DSDDB = 把空洞卷积分解成 depthwise + pointwise

**DDB 的问题**（p.3 §II-B）：

> "the number of parameters and computational complexity of the model **increase significantly as the channel size of the model grows**, particularly with an increase in the number of layers in the dilated dense convolution module."

**分解方式**（p.3 §II-B）：

> "Similar to the strategy of **depth-wise separable convolutions [23]**, **each dilated convolution is decomposed into a combination of depthwise dilated convolutions and point convolutions**."

**复杂度推导（Eq. 5–8）** —— 设输入谱维度 $t\times f$，第 $i$ 层：

| 量 | 公式 | 出处 |
|---|---|---|
| 标准空洞卷积 | $\Omega(\text{DC}) = iC\times CK^2tf$ | Eq. (5) |
| 深度可分离空洞卷积 | $\Omega(\text{DSDC}) = iC\times K^2tf + iC\times Ctf$ | Eq. (6) |
| $n$ 层 DDB | $\Omega(\text{DDB}) = \sum_{i=1}^{n} iC^2K^2tf$ | Eq. (7) |
| $n$ 层 DSDDB | $\Omega(\text{DSDDB}) = \sum_{i=1}^{n} iCK^2tf + \sum_{i=1}^{n} iC^2tf$ | Eq. (8) |

**参数量（Eq. 9–10）**：

$$P(\text{DDB}) = \sum_{i=1}^{n} iC^2K^2 \tag{9}$$

$$P(\text{DSDDB}) = \sum_{i=1}^{n} iCK^2 + \sum_{i=1}^{n} iC^2 \tag{10}$$

**论文的结论**（p.3）：

> "where **$n=4$, $C=64$ and $K=3$**. Since $C^2$ is significantly larger than $K^2$, the **complexity and parameter count of DSDDB are only 12.7% of DDB**, with only a **minor loss in performance**."

> [!note] 把 "12.7%" 这个数字代入算一遍（本页独立复算）
> 取 $n=4$、$C=64$、$K=3$ ⇒ $K^2=9$，$C^2=4096$。
> - 分子 $P(\text{DSDDB}) = \sum_{i=1}^{4}iCK^2 + \sum_{i=1}^{4}iC^2 = (1+2+3+4)\cdot(64\cdot 9) + (1+2+3+4)\cdot 4096 = 10\cdot 576 + 10\cdot 4096 = 5760 + 40960 = 46720$
> - 分母 $P(\text{DDB}) = \sum_{i=1}^{4}iC^2K^2 = 10\cdot 4096\cdot 9 = 368640$
> - 比值 $= 46720/368640 = \mathbf{12.67\%}$ ✅ **与论文的 12.7% 一致**
> **这个数字是可以独立复算的**——是本页对 PrimeK-Net 做的最有价值的一次核对，因为它同时验证了论文的 Eq. (9)(10) 与常数取值。

**Table II 的实证**：`DSDDB→DDB` 一行显示 **PESQ 3.61 → 3.61（不变）、CSIG 4.81→4.82、CBAK 3.98→3.98、COVL 4.35→4.36**，而**参数量 1.41M → 2.37M**。

> **+68% 参数换 +0.00 PESQ** ⇒ 这就是"12.7%"论证在**参数量维度**上的实证。（注意：Table II 只报了参数量差异，**没有报 DDB 版的 FLOPs**，所以"复杂度 12.7%"在表中未被直接验证，只在 Eq. (7)(8) 里推导。）

### 3.4 损失函数：两套，用来区分"公平对比"与"最佳性能"（Eq. 11–12）

论文沿用 MP-SENet [5] 的两套损失（p.3–4 §II-C）：

$$\mathcal{L}_{\text{old}} = \lambda_1\mathcal{L}_{\text{Metric}} + \lambda_2\mathcal{L}_{\text{Mag}} + \lambda_3\mathcal{L}_{\text{Pha}} + \lambda_4\mathcal{L}_{\text{Com}} + \lambda_5\mathcal{L}_{\text{Time}} \tag{11}$$

$$\mathcal{L}_{\text{new}} = \lambda_1\mathcal{L}_{\text{Metric}} + \lambda_2\mathcal{L}_{\text{Mag}} + \lambda_3\mathcal{L}_{\text{Pha}} + \lambda_4\mathcal{L}_{\text{Com}} + \lambda_6\mathcal{L}_{\text{Con}} \tag{12}$$

> "This updated function is a **minor modification of $\mathcal{L}_{\text{old}}$, which removes the time loss and incorporates a consistency loss [24]**."

**两套损失的分工**（p.3 §II-C 明确）：

> "**To facilitate comparison with previous state-of-the-art methods**, we used the original loss function from MP-SENet [5], denoted as $\mathcal{L}_{\text{old}}$."

即：**$\mathcal{L}_{\text{old}}$ 用于与既有方法公平对比，$\mathcal{L}_{\text{new}}$ 是论文的默认（最佳）配置**。五个分项的含义：

| 分项 | 含义 |
|---|---|
| $\mathcal{L}_{\text{Metric}}$ | MetricGAN 风格的判别式指标损失 |
| $\mathcal{L}_{\text{Mag}}$ | 幅度谱损失 |
| $\mathcal{L}_{\text{Pha}}$ | 相位谱损失（沿 MP-SENet 的并行相位估计） |
| $\mathcal{L}_{\text{Com}}$ | 复数谱损失 |
| $\mathcal{L}_{\text{Time}}$ | 时域损失（仅 $\mathcal{L}_{\text{old}}$） |
| $\mathcal{L}_{\text{Con}}$ | 一致性损失 [24]（仅 $\mathcal{L}_{\text{new}}$） |

> [!question] $\lambda$ 权重全部未给出
> 论文写了 $\lambda_1 \ldots \lambda_6$ 六个符号，但**从未给出任何具体数值**。只说"沿用 MP-SENet"。⇒ **损失无法凭本文复现**，必须回查 MP-SENet [5] 原文。
> 这一点对 **LaCo-SENet 有直接影响**：LaCo-SENet 写「损失 $\mathcal{L}=0.9\mathcal{L}_{\text{mag}}+0.3\mathcal{L}_{\text{pha}}+0.1\mathcal{L}_{\text{com}}+0.05\mathcal{L}_{\text{con}}+0.05\mathcal{L}_{\text{gan}}$（沿用 PrimeK-Net [3]）」，**给出了具体权重，反而比 PrimeK-Net 原文更完整**。⇒ **库内记录 LaCo-SENet 的损失权重时，其来源是 PrimeK-Net，但 PrimeK-Net 本身没写这些数**——这是一个**引用链上的信息断点**（见 §4.5 的 `[!question]`）。

## 4. 实验里哪个消融最关键？

### 4.1 实验设置（p.4 §III-A）

| 项 | 论文明确内容 |
|---|---|
| 数据集 | **VoiceBank+DEMAND [20]** |
| 片段长度 | 语音切成 **2 秒**片段做 STFT |
| **STFT** | **FFT size 400 / window length 400 / hop length 100** |
| batch size | **2** |
| 优化器 | **AdamW [25]** |
| 训练步数 | 最多 **1000k steps** |
| 默认损失 | **$\mathcal{L}_{\text{new}}$**（除特别说明） |
| 指标 | PESQ（$-0.5$–$4.5$）、CSIG / CBAK / COVL（$1$–$5$） |

> [!warning] STFT 400/400/100 的时延含义（本页换算）
> 论文**未说明采样率**，但 VoiceBank+DEMAND 标准为 **16 kHz**。按 16 kHz 换算：
> - window 400 samples = **25 ms**
> - hop 100 samples = **6.25 ms**
> ⇒ **与 LaCo-SENet 的 STFT 配置（25.0 / 6.25 / 400 ms/samples）完全一致**——**这证实了 LaCo-SENet 确实原样沿用了 PrimeK-Net 的前端**。
> ⇒ **25 ms 窗远超本库约 2 ms 目标，差一个数量级以上。** 且论文**未报告 STFT center** ⇒ 与库内多数论文一样，算法延迟**双向不确定**。
> **PrimeK-Net 是"低时延方向的非因果质量上界"，不是低时延候选。**

### 4.2 Table I：同框架同损失的三方对照（**本文最干净的一张表**）

> "To ensure a fair comparison, the methods listed in this table use the **same loss function** (Without Consistency Loss and with Time Loss)."

| Model | PESQ | CSIG | FLOPs | Para. |
|---|---|---|---|---|
| Noisy | 1.97 | 3.35 | — | — |
| MP-SENet [5] | 3.50 | 4.73 | **74.52G** | 2.05M |
| SE-Mamba [16] | 3.52 | 4.75 | **65.46G** | 2.25M |
| **PrimeK-Net-S** $\mathcal{L}_{\text{old}}$ | 3.53 | 4.76 | **26.45G** | **0.79M** |
| **PrimeK-Net** $\mathcal{L}_{\text{old}}$ | **3.57** | **4.79** | **44.64G** | **1.41M** |

论文的小结（p.4）：

> "under the same framework and loss function, PrimeK-Net **not only significantly outperforms the other models but also achieves this with fewer parameters and reduced computational cost in terms of FLOPs**."

**这张表能读出的三条对照（本页的计算）**：

| 对照 | 结果 |
|---|---|
| PrimeK-Net vs MP-SENet | PESQ **+0.07**、CSIG +0.06；**FLOPs 降 40.1%**（74.52→44.64G）、参数降 31.2% |
| PrimeK-Net vs SE-Mamba | PESQ **+0.05**、CSIG +0.04；**FLOPs 降 31.8%**（65.46→44.64G）、参数降 37.3% |
| PrimeK-Net-S vs MP-SENet | PESQ **+0.03**；**FLOPs 降 64.5%**、参数降 **61.5%** |

> [!important] Table I 的关键价值：**它把"框架差异"这个变量消掉了**
> 三个模型（MP-SENet / SE-Mamba / PrimeK-Net）用**同一个 TS 框架、同一套损失**，只有内部组件不同（分别是 **Conformer / Mamba / GPFCA**），编解码器的密集块也不同（DDB vs **DSDDB**）。
> ⇒ 这是库内少见的**控制变量对照**，比"各家自己报的 SOTA 数字横向抄在一张表里"强得多。
> **但它仍有两个未被消掉的变量**：① 三个模型是否都**重训到收敛**、是否**用同一份数据和同一划分**——论文只说"same advanced framework and loss functions"，未说明是否重训（也可能是引用原文数字）；② 表里**没有种子数、没有方差**。

### 4.3 Table II：模块消融（六行）

| Model | PESQ | CSIG | CBAK | COVL | Para. |
|---|---|---|---|---|---|
| **PrimeK-Net** | **3.61** | **4.81** | **3.98** | **4.35** | 1.41M |
| GPFN → Wide FFN | 3.51 | 4.74 | 3.93 | 4.27 | **1.41M** |
| DSDDB → DDB | 3.61 | 4.82 | 3.98 | 4.36 | **2.37M** |
| w/o SCA | **3.42** | 4.70 | 3.82 | 4.16 | 1.34M |
| w/o CL | 3.59 | 4.79 | 3.95 | 4.32 | 1.41M |
| w/o CL + w/ TL ($\mathcal{L}_{\text{old}}$) | 3.57 | 4.79 | 3.97 | 4.30 | 1.41M |

**逐行解读（含本页的增量计算）**：

| 行 | PESQ 变化 | 参数量变化 | 结论 |
|---|---|---|---|
| **GPFN → Wide FFN** | **−0.10** | **0（1.41M 完全不变）** | ⭐ **最关键的一行**：**性能提升不是来自参数增加**，而是来自"组质数核的多尺度设计"本身 |
| **DSDDB → DDB** | **±0.00**（3.61→3.61） | **+0.96M（+68%）** | ⭐ **第二关键**：DDB 多花 68% 参数**换不到任何 PESQ**；这就是 §3.3 的"12.7%"在参数维度的实证 |
| **w/o SCA** | **−0.19** | **−0.07M**（1.34M） | ⭐ **第三关键**：**SCA 是性价比最高的一块**——只用 0.07M 参数（占总量的 5%）就贡献 **0.19 PESQ**，远超 GPFN 的 0.10 |
| w/o CL | −0.02 | 0 | 去掉一致性损失，代价很小 |
| w/o CL + w/ TL（= $\mathcal{L}_{\text{old}}$） | −0.04 | 0 | 回到旧损失，再降 0.02 ⇒ **$\mathcal{L}_{\text{new}}$ 比 $\mathcal{L}_{\text{old}}$ 好 0.04 PESQ** |

> [!important] 本文消融真正的"信号"是**参数效率**，不是"哪个模块最重要"
> 把三行并排看，这张表实际上回答了一个更有用的问题：**每一份参数买到多少 PESQ？**
> | 模块 | 参数增量 | PESQ 贡献 | 每 0.01M 参数的 PESQ |
> |---|---|---|---|
> | SCA | 0.07 M | **0.19** | **0.027** |
> | GPFN（相对 Wide FFN） | 0 M | 0.10 | ∞（零参数代价） |
> | DSDDB（相对 DDB） | **−0.96 M** | 0.00 | 省参数不损质量 |
> ⇒ **GPFN 与 DSDDB 都是"零/负参数代价的改进"，SCA 是唯一真正花了参数但买到最多质量的地方。**
> **这个读法论文自己没有做**，但它解释了为什么 PrimeK-Net 能在 1.41 M 上打 2.25 M 的 SE-Mamba。

### 4.4 Table III：质数核消融（**本文最干净的对照**）

> "we perform ablation experiments on the kernel size selection for DFG ... We compare the performance differences among **single-scale, non-prime multi-scale, and prime multi-scale configurations with equivalent computational and parameter costs**."

| Kernel Size | PESQ | CSIG | FLOPs | Para. |
|---|---|---|---|---|
| **(17, 17, 17, 17)**（单尺度） | 3.57 | 4.77 | 44.64G | 1.41M |
| **(5, 15, 21, 27)**（非质数多尺度） | 3.59 | 4.79 | 44.64G | 1.41M |
| **(3, 11, 23, 31)**（**质数多尺度**） | **3.61** | **4.81** | 44.64G | 1.41M |

**本页的增量分析**：

| 对照 | PESQ 变化 | 归因 |
|---|---|---|
| 单尺度 → 非质数多尺度 | 3.57 → 3.59（**+0.02**） | **多尺度本身**的贡献 |
| 非质数多尺度 → 质数多尺度 | 3.59 → 3.61（**+0.02**） | **质数性**的贡献（额外） |
| 单尺度 → 质数多尺度（合计） | 3.57 → 3.61（**+0.04**） | 多尺度的总贡献 |

> [!note] 这张表是全文方法论上最强的一格，但它的解释力也有边界
> **强在哪**：三行 **FLOPs 与参数完全相同**（44.64G / 1.41M），唯一的差异是核尺寸的具体取值 ⇒ **把"参数量"和"算力"这两个混杂变量彻底消掉了**。这是库内少见的干净对照，与 [[wiki_low_latency/sources/2025/FastEnhancer 2025]] 的「BN→LN：参数量与 MACs 完全不变，RTF +27%」在**实验设计思路上完全同构**（都把"零算术变化的对照"当作因果证据）。
> **边界在哪**：
> - **对比组 (5,15,21,27) 的中位数 ≈ 21 与质数组 (3,11,23,31) 的中位数 ≈ 23 并不对齐**，且**平均核长差 5.2× vs 4.5×**（质数组平均 17.0，非质数组平均 17.0 —— 实际上平均是相同的，但分布形态不同）。**论文没有说明为什么选这组非质数**——若换一组非质数（例如 (4,12,20,28) 或 (3,9,21,27)），结论未必相同。
> - **+0.02 的效应量**：库内第 6 条判定口径要求"**小效应量的增益必须配统计证据**"（凡 ≤0.05 量级的增益，都必须标注"未经显著性检验"，实验里也要带种子方差）。**本文 +0.02 与 +0.04 两个增量都落在这个量级，而论文无方差、无置信区间、无显著性检验、无种子数。** ⇒ 按库内纪律，**"质数优于非质数"这个结论应标注为未经显著性检验**。

### 4.5 消融之外的实验缺口（本页审计）

> [!question] 论文未报告、且对库内判定有直接影响的字段
> | # | 缺失项 | 影响 |
> |---|---|---|
> | ① | **采样率未明确写出** | 400/400/100 无法换算成 ms（本页按 VB-DEMAND 惯例取 16 kHz ⇒ 25 / 6.25 ms，**属推断**） |
> | ② | **STFT center / 帧锚定未报告** | 库内一等审计项；无法确定前端是否含 look-ahead |
> | ③ | **损失权重 $\lambda_{1..6}$ 全部未给** | 损失不可复现；LaCo-SENet 引用的具体权重在本文中**找不到出处** |
> | ④ | **模型总深度 / GPFCA 堆叠数 / TS Blocks 数未在正文给出** | PrimeK-Net-S 的定义（"1 GPFCA module"）暗示默认是 2 个，但只在表题里 |
> | ⑤ | **无 RTF / 无 ms / 无硬件 / 无量化 / 无内存实测** | 算力证据停在 **L0**（仅解析 FLOPs）——**不能做速度排序** |
> | ⑥ | **无种子数、无方差、无置信区间** | 而 Table II/III 的核心增量低至 0.02 PESQ |
> | ⑦ | **无 WER/ASR、无负 SNR 分层、无噪声类型分层、无 false-suppression** | 人声保留维度空白 |
> | ⑧ | **Fig. 3(b) 的"线性复杂度 vs $O(t^2)$"只有曲线，无数值表** | 显存优势未量化到具体数字 |
> | ⑨ | **无局限性/未来工作节**（结论只写"未来会用于 ASR 与语音分离"） | 典型 4 页会议短文 |
> | ⑩ | **Table I 的 MP-SENet / SE-Mamba 是否重训未说明** | "同框架同损失"的可比性依赖这一点 |

> [!question] 🔴 **引用链上的一个真实断点（对 LaCo-SENet 有直接影响）**
> [[wiki_low_latency/sources/2026/LaCo-SENet 2026]] 写：「损失 $\mathcal{L}=0.9\mathcal{L}_{\text{mag}}+0.3\mathcal{L}_{\text{pha}}+0.1\mathcal{L}_{\text{com}}+0.05\mathcal{L}_{\text{con}}+0.05\mathcal{L}_{\text{gan}}$（沿用 PrimeK-Net [3]）」。
> **但 PrimeK-Net 原文只给出 $\lambda_1 \ldots \lambda_6$ 六个符号，从未给出任何具体数值。**
> ⇒ 两种可能：**(a)** LaCo-SENet 从 PrimeK-Net 的**官方代码仓库**（`github.com/huaidanquede/PrimeK-Net`）读到了权重，但在文字上归因给了论文；**(b)** LaCo-SENet 的归因不准确。
> **本库的处置**：**两个页面都如实记录**——PrimeK-Net 页记"未给出 $\lambda$ 数值"，LaCo-SENet 页保留其原述，并在两页**互相标注这一断点**，**不替任何一方补齐**。
> **这也印证了库内第 14 条（锚点数值必须先钉死口径）的必要性**：连"沿用某篇的损失"这种看似明确的表述，都可能在数值层面断链。

### 4.6 本文的消融与本库方法论的呼应

PrimeK-Net 的两张消融表（Table II 的 GPFN→Wide FFN、Table III 的三档核尺寸）**恰好是库内第 10 条判定口径（算力证据等级 L0–L3）的典型样本**：

- 它**极其认真地控制了参数量与 FLOPs**（两组对照都做到"完全不变"）——这是 **L0 内部的最高标准**；
- 但它**完全没有跳出 L0**：没有 RTF、没有硬件、没有量化、没有实测耗时。

⇒ **"把解析算力控制得再干净，也不等于知道它跑得快不快"。** 这正是 [[wiki_low_latency/sources/2025/FastEnhancer 2025]] 与 [[wiki_low_latency/sources/2026/Early Exit Compute-Matched 2026]] 从两个不同机理（算子可融合性 / accelerator launch 次数）论证的同一件事。

## 5. 这个方向还剩什么问题没解决？（future work / limitation）

### 5.1 论文自己承认的

论文的"未来工作"只有一句（p.4 §IV）：

> "In the future, We will apply our approach to **other tasks such as ASR and speech separation**."

**没有局限性讨论。** 这在一篇 4 页 ICASSP 短文里是常见的，但对本库意味着：**论文的任何边界都必须由读者自己审计**。

### 5.2 本页读出的问题（按对低时延方向的重要性排序）

| # | 问题 | 为什么重要 |
|---|---|---|
| **①** | **它是非因果的，且未声明** | 两阶段结构 + 频率轴全局操作（GPFN 的核长 31 沿频率轴）+ 未报告的 STFT center ⇒ **实质上读取未来，且论文对此零讨论**。作为 LaCo-SENet 的"非因果上界"，它的 3.61 是**质量天花板**而不是**可达目标** |
| **②** | **算力证据停在 L0** | 只有解析 FLOPs（44.64G），**没有任何实测速度**。按库内第 10 条，**不能参与速度排序** |
| **③** | **FLOPs 量级本身对端侧不友好** | 44.64 G FLOPs（Table I）与库内超轻量锚点 [[wiki_low_latency/entities/GTCRN]] 的 39.6 MMACs/s **不在同一量级**（差约 3 个数量级）⇒ PrimeK-Net 在算力轴上也是"上界"而非候选 |
| **④** | **+0.02 量级的结论无统计证据** | Table III 的两个增量（+0.02 / +0.02）正压在库内第 6 条的警戒线内 |
| **⑤** | **$\lambda$ 权重缺失造成引用链断点** | 直接影响 LaCo-SENet 的可复现性记录（见 §4.5） |
| **⑥** | **"边缘设备"动机无实测支撑** | 第 ① 条缺陷用 $O(t^2)$ 论证边缘设备受限，但**没有任何边缘设备实验**——Fig. 3(b) 只是显存随序列长度的曲线 |
| **⑦** | **GPFCA 因果化后的代价未知** | 这是**库内最直接的开放问题**：若把 GPFN 的频率轴核也做因果 padding、把 TS 结构做因果化，**还剩多少 3.61？** LaCo-SENet 用一个训练期旋钮回答了这个问题（12.5 ms 保留 93%），但**那是 LaCo-SENet 的答案，不是 PrimeK-Net 的** |
| **⑧** | **质数核的性质未被理论化** | 只有 Table III 的经验对照；且对比组的选择未说明理由 |

### 5.3 对库内两条判定口径的呼应

- **第 10 条（算力证据等级）**：PrimeK-Net 是 **L0 的"模范样本"**——它把 L0 能做的一切都做到位了（参数量与 FLOPs 的干净控制），但**依然只是 L0**。
- **第 15 条（引用即负有义务）**：PrimeK-Net 引用了 NAFNet（把 attention/FFN 换成高效结构的**效率论证**）与 MobileNets（depthwise separable convolution 的**效率论证**），**但自己不报任何速度**。⇒ 与 GTCRN 引用 ShuffleNetV2 的情形**完全同构**，应同样标注 **"引用即负有义务而未履行"**。

## 6. 本论文在库中的位置关联（cross-reference matrix）

### 6.1 前身 / 基石

| 前身 | 关系 | 留下的 gap |
|---|---|---|
| **MP-SENet [5]**（Interspeech 2023） | **损失函数与 TS 范式的直接来源**（$\mathcal{L}_{\text{old}}$ 与 $\mathcal{L}_{\text{new}}$ 都来自它） | 算力与显存未优化（74.52G FLOPs / 2.05M） |
| **TSTNN [2]**（ICASSP 2021） | TS 结构的源头 | 用的是 Transformer |
| **CMGAN [3]** | 证明 Conformer 在 TS 里有效 | $O(t^2)$ |
| **DDB [9]**（ICASSP 2020） | 被 DSDDB 替换的对象 | $C^2$ 膨胀 |
| **NAFNet [19]**（ECCV 2022） | **GPFCA 的方法论模板**（"替换 attention 与 FFN 即可保持竞争力而获得线性复杂度"） | 图像任务，未适配 SE 的 TS |
| **GDFN [22]**（Restormer） | DFG（depth-wise gate）的结构来源 | 单尺度 |
| **HIFI-GAN 的 MPD [17]** | **质数核的灵感来源**（跨任务迁移） | 是判别器设计，未用于卷积核选择 |

### 6.2 后续 / 扩展（**库内最直接的一条**）

| 后续 | 怎么改的 | 改了多少 |
|---|---|---|
| **[[wiki_low_latency/sources/2026/LaCo-SENet 2026]]** | **直接沿用 PrimeK-Net 骨干**（encoder + TS blocks + 并行 mask/phase 双 decoder）与**同一套损失**，把「未来访问」参数化为训练期超参数 $r=(r_L,r_R)$，并引入 dual-buffer streaming + SSU 使 chunk-wise ≡ full-sequence | 参数 **1.41M → 1.37M**（略减）；质量：12.5 ms 全因果点 **3.35**，保留非因果上界 3.61 的 **93%**；对称参考 ($r_R{=}0.5$) @200 ms 达 **3.47** |

> [!important] LaCo-SENet ↔ PrimeK-Net 是库内**配对最紧的一对**
> 这三件事完全共享：**骨干分解方式、损失、STFT 配置（25 ms / 6.25 ms / 400）**。
> ⇒ 库内由此获得一个**罕见的干净对照**：**同一模型，非因果上界 3.61 vs 因果 12.5 ms 的 3.35** ⇒ **"未来上下文"在这一骨干上值 0.26 PESQ**。
> **这是全库对"因果化的代价"最接近定量的一次测量**——虽然它仍受单一种子、无方差的限制（LaCo-SENet 与 PrimeK-Net 都没有报方差）。

### 6.3 同分支竞品

| 竞品 | 内部组件 | 与 PrimeK-Net 的关系 |
|---|---|---|
| **MP-SENet [5]** | Conformer | Table I 直接对照：**PESQ −0.07、FLOPs +67%** |
| **SE-Mamba [16]** | Mamba | Table I 直接对照：**PESQ −0.05、FLOPs +47%** |
| **CMGAN [3]** | Conformer + MetricGAN | Fig. 3(a) 对照 |
| **TridentSE [26]** | 32 global tokens | Fig. 3(a) 对照 |

### 6.4 跨分支类比（**本页认为最有价值的一格**）

| 类比对象 | 相似点 | 差异 |
|---|---|---|
| **[[wiki_low_latency/entities/SlowFast-SSM]]**（2024） | 都在处理"多尺度"问题 | SlowFast 用**双支路 + 不同帧率**，PrimeK-Net 用**单支路 + 多核尺寸**。前者的多尺度是**时间轴**的，后者是**频率轴**的 |
| **[[wiki_low_latency/entities/FastEnhancer]]**（2025，BN/LN 消融） | **都把"零算术变化的对照"当作因果证据** | FastEnhancer 控制的是 **RTF**（实测），PrimeK-Net 控制的是 **FLOPs**（解析）⇒ **同一种实验设计，证据等级差两级（L2 vs L0）** |
| **[[wiki_low_latency/entities/GTCRN]]** | 都被后继论文当成"上界/锚点"引用 | GTCRN 是**算力轴**的锚点（被 4 篇引用），PrimeK-Net 是**质量轴**的上界（被 LaCo-SENet 引用） |
| **HIFI-GAN 的 MPD → GPFN** | 质数周期的想法迁移 | 判别器 → 卷积核；论文未论证迁移的必然性 |
| **[[wiki_low_latency/entities/PercepNet]] / [[wiki_low_latency/entities/DeepFilterNet2]]** | 都在做"频带分工" | 那两篇用 **ERB 非均匀频带**（人耳分辨率），PrimeK-Net 用**质数核长**（周期互质性）。**两种"频域分工"的哲学完全不同** |

### 6.5 与全库主线的接点

- **与 [[wiki_low_latency/overview]] 第 10 条（算力证据等级 L0–L3）**：PrimeK-Net 是 **L0 的模范**，但仍是 L0。
- **与第 15 条（引用即负有义务）**：引用 NAFNet / MobileNets 的效率论证却不报速度 ⇒ **未履行**。
- **与第 6 条（小效应量须配统计证据）**：Table III 的 +0.02 / +0.02 落在警戒线内且无方差。
- **与第 14 条（锚点数值先钉口径）**：$\lambda$ 权重的引用链断点是**新的一类**——不是数值矛盾，而是**上游未提供**。

## 7. 一句话总结"江湖地位"

```text
2025 | SE 高效架构 | 用「组质数核多尺度 + 深度可分离空洞密集块」把两阶段 SE 推到 1.41M / PESQ 3.61，
     并用两组「参数量与 FLOPs 完全不变」的对照证明了增益来自设计而非规模
     → 2026 被 LaCo-SENet 直接选作骨干，成为「时延可配置」改造的**非因果质量上界**（3.61）；
       因果化到 12.5 ms 后保留其 93%（3.35），这 0.26 PESQ 就是「未来上下文」的价格
```

## 参考资料

- 原 PDF：`raw/papers/low_latency_causal_se/2502.19906.pdf`（5 页，5,637,523 bytes）
- 文本抽取：`tmp/pdf_extract/primeknet.txt`（20,880 chars）
- 页图渲染：`wiki_low_latency/assets/primek-net_2025/primek-page1..5.png`（150 dpi）
- 官方代码：https://github.com/huaidanquede/PrimeK-Net
- arXiv：https://arxiv.org/abs/2502.19906 （v1，2025-02-27 提交；Comments 字段：**"This paper was accepeted by ICASSP 2025"**）
- DOI：`10.48550/arXiv.2502.19906`
- 相关页面：[[wiki_low_latency/entities/PrimeK-Net]] · [[wiki_low_latency/concepts/2502.19906-prime-kernel-multiscale-dense-block]] · [[wiki_low_latency/sources/2026/LaCo-SENet 2026]] · [[wiki_low_latency/entities/LaCo-SENet]]

> [!warning] 版本与 venue 说明
> 本页依据的是 **arXiv v1（2025-02-27）**。arXiv Comments 字段明确写 **"This paper was accepeted by ICASSP 2025"**（原文拼写错误 "accepeted"）——按库内 venue 判定规则，**arXiv 的 Comments 字段是唯一被承认的录用证据**。
> **但库内没有本地 ICASSP 正式出版版 PDF**（IEEE 付费墙）。因此：
> - `venue: ICASSP 2025` · `venue_status: published`（依据 Comments 字段）
> - **页码、卷号、正式 DOI（10.1109/...）均未核验** ——与 [[wiki_low_latency/sources/2024/GTCRN 2024]] 的"用户提供 PDF 补摄"不同，本篇**只有 arXiv 版**，其 ICASSP 版的页码与 DOI **尚待核验**。
> - 若后续获得正式版 PDF，需按库内第 16 条做四项版本核验并更新本页。
