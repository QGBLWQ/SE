---
title: SBM - 薛定谔桥 Mamba 实现一步生成式语音增强
type: source
created: 2026-10-07
updated: 2026-10-07
tags:
  - speech-enhancement
  - generative
  - schrodinger-bridge
  - mamba
  - ssm
  - one-step-inference
  - joint-denoising-dereverberation
  - limited-lookahead
  - interspeech-2026
source_type: paper
year: 2026
authors: Jing Yang; Sirui Wang; Chao Wu; Lei Guo; Fan Fan
venue: Interspeech 2026, pp. 1363-1368
venue_status: published
doi: 10.21437/Interspeech.2026-682
local_pdf: raw/papers/low_latency_causal_se/SchrodingerBridgeMamba-Interspeech2026.pdf
evidence_policy: local_pdf_only
related:
  - [[wiki_low_latency/entities/Schrodinger-Bridge-Mamba]]
  - [[wiki_low_latency/concepts/sbm-2026-schrodinger-bridge-mamba]]
  - [[wiki_low_latency/entities/RT-SEMamba]]
  - [[wiki_low_latency/entities/PSMSE]]
  - [[wiki_low_latency/concepts/严格因果与算法延迟]]
---

~~~yaml
- 论文: [Schrödinger Bridge Mamba for One-Step Speech Enhancement](2026)
  ├── 要解决什么问题: 薛定谔桥（SB）类生成式增强推理慢（常需 >10 步迭代）妨碍实时；且现有工作忽略 SB 范式与骨干架构之间的内在协同
  ├── 核心方法: 把 SB 训练范式与 Mamba 骨干结合——SB 显式计算 OT 路径上的中间态 x_t 作为训练"锚点"，Mamba 的递推结构天然模拟状态演化，训练期把 SB 变换"蒸馏"进 Mamba 动力学
  ├── 属于哪个分支: 生成式增强 / 一步推理 / Mamba-SSM / 联合去噪去混响
  ├── 输入/输出: 退化语音 STFT 谱 → 干净语音 STFT 谱（单次前向，t=1 起）
  ├── 关键trick: SB 的受控系统结构与 Mamba 递推 h_t = A h_{t-1} + B u_t 的对应——A 为自然动力学、(B,C) 为输入依赖的控制项，训练 Mamba 即学 SB 的最优控制策略
  ├── 数据集: DNS clean + AI-Shell3 + LibriSpeech ≈ 800 小时；噪声 FSD50K/DNS/自采；RIR SLR26/28 + pyroomacoustics；16 kHz；SNR ∈ [−10,20]
  ├── 对比了谁: SB-NCSN++(50/10/1)、SBCTM、SB-UFOGen、ZipEnhancer、Mamba-base（mapping 同骨干）、FM-Mamba（flow matching 同骨干）
  ├── 性能上限: DNS With Reverb SIG 3.653 / OVRL 3.367 / PESQ 1.971；DNS Real Recordings 全项最高（SIG 3.459 / BAK 4.106 / OVRL 3.198 / P808 3.742 / NISQA 3.937）
  ├── 参数量: 3.93 M；RTF 0.0048（GPU，未指明型号）——全表最低
  ├── 消融关键发现: SB 范式在 MHSA/LSTM/Mamba 三种骨干上一致优于 mapping（SIG +0.246 / +0.206 / +0.175）；SB 优于 flow matching（同骨干同步数）
  ├── 遗留问题(你的机会): "under 40 ms 算法延迟"漏计了 30 ms 窗的 τ_enc ⇒ 实际约 50–70 ms；非严格因果（2–4 帧 lookahead）；在 PESQ/ESTOI 上仍输给判别式 ZipEnhancer
  └── 跟哪篇像: 与 [[wiki_low_latency/entities/RT-SEMamba|RT-SEMamba]] 同为 Mamba + 流式，但 RT-SEMamba 是判别式渐进蒸馏、SBM 是生成式一步；与 [[wiki_low_latency/entities/PSMSE|PSMSE]] 同为 Mamba 流式家族
~~~

> [!warning] PDF 来源与质量
> ISCA Archive 的 Interspeech 2026 官方录用版 PDF（`SchrodingerBridgeMamba-Interspeech2026.pdf`，6 页，`pdfTeX-1.40.27` 生成）。第 1 页页脚印有 `1363 / Interspeech 2026 / 27 September - 1 October 2026, Sydney, Australia / 10.21437/Interspeech.2026-682`，逐页页码 1363→1368 递增 ⇒ **venue 证据等级 (a) 已正式出版**。
> 文本抽取缺陷：标题与正文里的 `Schr¨odinger` 是 umlaut 编码问题（正常写作 Schrödinger）；Figure 1 的架构图元素被打散成独立词。

> [!warning] 本篇是**半因果（2–4 帧 lookahead）**，不可参与严格因果排名
> 论文 §2.2 明确：Mamba 骨干"以 **2–4 帧的小 lookahead** 运行，产出**低于 40 ms 的算法延迟**，以平衡因果性与增强质量"。
> ⇒ 它**有 lookahead**，且"低于 40 ms"这一数字**漏计了 $\tau_{enc}$**（详见 §5）。**不能参与库内严格因果排名。**

---

## 1. 他们为什么这么做？(motivation)

**现有方法的不足（两层）**：

**第一层：SB 类方法推理慢。**
深度生成模型用于语音增强的吸引力在于"**直接学习干净语音分布** ⇒ 取得更优的感知质量、重建确定性回归丢失的细节"。但论文指出早期基于分数的生成模型有 **mean prior mismatch（均值先验失配）** 问题。

**薛定谔桥（SB）** 通过随机微分方程（SDE）建模**最优传输（OT）路径**，把退化先验直接输运到干净目标，从而解决这一问题。SB 已在去噪/去混响、超分、inpainting、图像生成、TTS 上取得显著成功。但：

> 这些 SB 类方法的**推理缓慢**（常需 **>10 次迭代步**）**妨碍实时应用**。

近期加速路线包括：专门的调度器与求解器、对抗训练、一致性轨迹建模。其中一些已实现去噪或去混响的**一步推理**。但论文指出了一个被忽略的点：

> 现有工作**通常忽略了 SB 范式与骨干架构之间的内在协同**，在高效建模上留下了显著空间。

**第二层：Mamba 用于 SE 时没有用上生成式轨迹学习。**
Mamba（选择性状态空间模型）已在长程音频依赖建模上展现能力，也被用于 SE（oSpatialNet、SEMamba、USEMamba）。但：

> 这些工作使用**确定性映射或掩蔽**训练策略，**未能利用生成式轨迹学习的潜力**。

**为什么这个不足重要**：论文的核心论点是——

> **让训练范式与骨干架构的归纳偏置对齐，对效率与有效性都至关重要。**

⇒ 这既是一个工程主张（效率），也是一个方法学主张（有效性）。

---

## 2. 之前的人怎么做不了？(limitation → gap)

| 维度 | 先前做法 | 留下的 gap |
|---|---|---|
| **SB 骨干** | 绝大多数 SB-SE 用 **NCSN++**（SB-NCSN++） | NCSN++ 的**规模与效率问题**未被解决（SBCTM 65.98 M、SB-UFOGen 25.16 M） |
| **加速手段** | 调度器/求解器、对抗训练（SB-UFOGen）、一致性轨迹建模（SBCTM） | 这些手段**加速了推理但没换骨干** ⇒ "未能解决 NCSN++ 结构固有的规模与效率问题"（论文原话） |
| **Mamba 用于 SE** | 确定性映射或掩蔽训练 | **未利用生成式轨迹学习** |
| **训练范式与骨干的关系** | 默认两者独立选择 | **"协同"这一维度未被探索** |

**这个 gap 为什么至今没解决**：论文认为障碍在于**"SB 与 Mamba 的适配性没有被识别"**。它给出的论证是三条：

1. **结构相似性**：Mamba 的离散递推

$$h_t = A h_{t-1} + B u_t,\qquad y_t = C h_t$$

把它看作一个**受控系统**时，$A h_{t-1}$ 表示**自然的、不受控的动力学**，而输入依赖的参数 $(B, C)$ 充当**控制项**。⇒ **训练 Mamba 就类似于学习 SB 内在的最优控制策略**，其中选择性机制根据当前状态**动态参数化传输路径**。

2. **Mamba 的数学最优性**：近期有工作证明 Mamba 在捕捉**马尔可夫序列动力学**上的数学最优性（文献 [24]）⇒ 说明它适合建模 SB 范式的随机演化过程。

3. **SB 提供"锚点"**：与"盲"的确定性映射或掩蔽（**只看到起点与终点**）不同，SB 范式**显式计算 OT 路径上的中间态 $x_t$**，这些态被用作训练输入，**充当"锚点"引导骨干学习底层演化过程**。

⇒ 三条合起来就是："**SB 需要能模拟状态演化的骨干，Mamba 需要能提供中间态监督的训练范式。**"

---

## 3. 这个做法核心 trick 是什么？

**核心是一个"范式 × 骨干"的匹配论证，工程上只叠了两件事（时间嵌入与 fullband Mamba 层）。**

### 3.1 SB 形式化

与标准扩散（依赖高斯先验 ⇒ 均值先验失配）不同，SBM 把语音增强表述为**退化分布 $p_T$ 与干净分布 $p_0$ 之间的直接 OT 过程**。中间态 $\{x_t\}_{0:T}$ 可用配对样本（干净 $x\sim p_0$、退化 $y\sim p_T$）构造。

为高效训练，中间态可显式参数化为**边界条件的插值 + 随机 Wiener 过程项**：

$$x_t = \mu_x(t) + \sigma_x(t)z,\qquad z\sim\mathcal{N}_{\mathbb{C}}(0,I) \tag{1}$$

其中 $\mu_x(t) = w_x(t)x + w_y(t)y$。方差 $\sigma_x(t)$ 与系数 $w_x(t), w_y(t)$ 来自 **Variance Exploding (VE)** 噪声调度参数。

> [!important] Eq.(1) 在训练中的角色
> 论文强调："**Eq.(1) 在训练中充当数据生成器**：对每一批，我们采样随机时间步 $t$ 并计算 $x_t$，训练模型通过学底层数据分布来重建干净目标 $x$。"
> ⇒ 也就是说，**SB 不是通过求解反向 SDE 实现的，而是通过"在插值路径上采样中间态、让模型学从中间态回到干净目标"实现的**。这是"一步推理"能成立的前提。

### 3.2 Mamba 骨干架构

| 组件 | 说明 |
|---|---|
| **主组件** | **oSpatialNet-Mamba**（依文献 [16] 的 oSpatialNet 设计） |
| **时间嵌入** | 训练一个 **Gaussian Fourier 模块**嵌入时间步（文献 [2][4]），把 $\mathrm{emb}(t)$ **加到 Mamba 的输入**上 ⇒ 称 **oSpatialNet-Mamba-Cond** |
| **全局建模补充** | 受 [16][25] 启发，集成一个 **fullband Mamba 层**以捕捉**全局谱动态与帧间依赖**（动机是 oSpatialNet 的**时间局限**） |
| **其余** | 频率压缩 / 时间压缩 / 时间解压缩 / cross-band block / linear projection |
| **表示** | **STFT 谱**（遵循相关工作的通行做法） |

### 3.3 训练与一步推理

**损失**：采用**数据预测损失**，结合幅度与复数域约束：

$$\mathcal{L} = \lambda_1\mathcal{L}_{mse}(S,\hat{S}) + \lambda_2\mathcal{L}_{mse}(|S|,|\hat{S}|) + \lambda_3\mathcal{L}_{mr,mse}(S,\hat{S}) + \lambda_4\mathcal{L}_{mr,mse}(|S|,|\hat{S}|)$$

$S,\hat{S}$ 为目标与建模的 STFT，$mr$ 表示 multi-resolution，$|S|$ 为幅度谱。**$\lambda_1,\lambda_2,\lambda_3,\lambda_4 = 1000, 1000, 500, 500$**。

**一步推理**：标准 SB 方法需**迭代求解反向 SDE**；SBM 设计为**一步生成**。推理时把时间步设为反向过程的起点（$t=1$，对应退化先验），模型**在单次前向中直接重建干净目标**。

论文的表述："**这大幅降低延迟，同时利用从 SB 轨迹中学到的分布建模能力。**"

### 3.4 实现细节

| 项 | 值 |
|---|---|
| 段长 | 训练时把音频**任意切成 3 秒段** |
| **STFT** | **NFFT 512、Hann 窗长 480、hop 160**（16 kHz ⇒ **30 ms 窗 / 10 ms hop**，66.7% 重叠） |
| 优化器 | AdamW + cosine 学习率调度，起始 lr $1\times10^{-3}$ |
| 数据 | DNS clean + AI-Shell3 + LibriSpeech，**合计约 800 小时**；噪声 FSD50K + DNS + 自采；RIR SLR26/28 + pyroomacoustics |
| SNR | **∈ [−10, 20]** |
| 采样率 | 16 kHz |
| 训练规模 | 800 小时（**远大于库内轻量模型的 44 小时量级**） |
| 测试集 | DNS Real Recordings、DNS Synthetic With Reverb、DNS Synthetic Without Reverb、VoiceBank-Demand |
| 指标 | DNSMOS（SIG/BAK/OVRL/P808MOS）、NISQA、SpeechBERTScore、Similarity、PESQ、ESTOI |
| RTF | **GPU 上测（未指明型号）**，对 10 段 10 秒音频取平均 |

---

## 4. 实验里哪个消融最关键？

**最关键的是 Table 3 的"范式 × 骨干"交叉消融**——它把"SB 范式"与"Mamba 骨干"各自的贡献分离开。

### 4.1 Table 3：范式 × 骨干（DNS Real Recordings）

列序 = Params / SIG / BAK / OVRL / P808MOS / NISQA。**(M)** = mapping 范式，**(SB)** = SB 范式。

| Model | Params | SIG | BAK | OVRL | P808MOS | NISQA |
|---|---|---|---|---|---|---|
| MHSA(M) | 8.37 M | 2.975 | 3.809 | 2.676 | 3.233 | 2.358 |
| MHSA(SB) | 8.41 M | 3.221 | 3.941 | 2.927 | 3.60 | 3.24 |
| LSTM(M) | 17.38 M | 3.083 | 3.904 | 2.799 | 3.331 | 2.585 |
| LSTM(SB) | 17.42 M | 3.289 | 3.965 | 3.00 | 3.674 | 3.819 |
| Mamba(M) | 3.61 M | 3.284 | 3.974 | 2.993 | 3.683 | 3.644 |
| **Mamba(SB) = SBM** | **3.93 M** | **3.459** | **4.106** | **3.198** | **3.742** | **3.937** |

**范式维度（同一骨干下 SB − mapping 的差值）**：

| 骨干 | Δ SIG | Δ BAK | Δ OVRL | Δ P808MOS | Δ NISQA |
|---|---|---|---|---|---|
| MHSA | **+0.246** | +0.132 | +0.251 | +0.367 | +0.882 |
| LSTM | **+0.206** | +0.061 | +0.201 | +0.343 | +1.234 |
| **Mamba** | **+0.175** | +0.132 | **+0.205** | +0.059 | **+0.293** |

⇒ **SB 范式在三种骨干上一致占优** ⇒ 论文的核心论点（"训练范式是独立于骨干的贡献"）得到验证。

**骨干维度**：

| 对比 | 观察 |
|---|---|
| Mamba(SB) 3.93 M vs MHSA(SB) 8.41 M | Mamba 用**不到一半参数**在 SIG/BAK/OVRL/P808 上更高（3.459 vs 3.221 / 4.106 vs 3.941 / 3.198 vs 2.927 / 3.742 vs 3.60），但 **NISQA 更低**（3.937 vs 3.24？——**注意 LSTM(SB) 的 NISQA 3.819 与 MHSA(SB) 的 3.24**；Mamba(SB) 的 3.937 是最高的） |
| Mamba(SB) 3.93 M vs LSTM(SB) 17.42 M | Mamba 用**约 1/4.4 参数**在 SIG/BAK/OVRL/P808/NISQA 上**全部更高**（3.459 vs 3.289 / 4.106 vs 3.965 / 3.198 vs 3.00 / 3.742 vs 3.674 / 3.937 vs 3.819） |
| **Mamba(M) 3.61 M vs LSTM(SB) 17.42 M** | ⚠️ **LSTM(SB) 在 OVRL（3.00 vs 2.993）与 NISQA（3.819 vs 3.644）上高于 Mamba(M)** ⇒ **范式与骨干各有独立贡献**，不能写成"骨干决定一切" |

> [!important] 这条消融的方法学价值
> 论文用"**三种骨干 × 两种范式**"的完整 2×3 交叉设计，把两个变量**解耦**了：
> - 若只看 Mamba(SB) vs Mamba(M)，会以为"SB 只对 Mamba 有效"；
> - 交叉设计证明 **SB 对 MHSA/LSTM 同样有效**（+0.246 / +0.206）⇒ **SB 是范式层面的普遍贡献**；
> - 同时 **Mamba(M) 3.61 M 已能与 LSTM(SB) 17.42 M 打平**（OVRL 2.993 vs 3.00，NISQA 3.644 vs 3.819 略低）⇒ **骨干选择的价值也很大**。
> ⇒ **两者是相乘而非替代关系。** 这是一个设计得很干净的消融，值得作为库内"分离范式与骨干贡献"的模板。

**论文对公平性的说明**："为给每个骨干可比的容量以公平比较，MHSA 与 LSTM 块的设计、隐藏维与超参**按其与 Mamba 的结构对应关系精心配置**，故模型规模不同（8.37–17.42 M vs 3.61–3.93 M）。"

### 4.2 Table 1：主结果（三个测试集）

列序 = Para.[M] / RTF↓ / SIG / BAK / OVRL / P808MOS / NISQA / SpeechBERTScore / Similarity / PESQ / ESTOI。

**DNS With Reverb**：

| Model | Para | RTF | SIG | BAK | OVRL | P808 | NISQA | SBS | Sim | PESQ | ESTOI |
|---|---|---|---|---|---|---|---|---|---|---|---|
| SB-NCSN++(50) | 25.16 | 0.767 | 3.395 | 3.938 | 3.085 | 3.884 | 3.879 | 0.703 | 0.947 | 1.532 | 0.629 |
| SB-NCSN++(10) | 25.16 | 0.156 | 3.425 | 3.97 | 3.126 | 3.896 | 4.087 | 0.728 | 0.947 | 1.597 | 0.671 |
| SB-NCSN++(1) | 25.16 | 0.0155 | 3.281 | 3.871 | 2.948 | 3.559 | 3.323 | 0.730 | 0.943 | 1.586 | 0.67 |
| SBCTM | 65.98 | 0.02 | 2.927 | 3.859 | 2.623 | 3.035 | 2.578 | 0.494 | 0.859 | 1.218 | 0.281 |
| SB-UFOGen | 25.16 | 0.0152 | 2.964 | 3.664 | 2.596 | 3.337 | 2.131 | 0.662 | 0.918 | 1.383 | 0.601 |
| ZipEnhancer | 2.04 | 0.105 | 2.771 | 3.164 | 2.264 | 2.85 | 1.926 | 0.534 | 0.84 | 1.227 | 0.288 |
| Mamba-base | 3.61 | **0.0048** | 3.202 | 3.898 | 2.895 | 3.665 | 3.514 | 0.766 | 0.963 | 1.895 | 0.696 |
| FM-Mamba | 3.93 | **0.0048** | 3.164 | 3.956 | 2.887 | 3.461 | 3.148 | 0.682 | 0.930 | 1.643 | 0.634 |
| **SBM** | **3.93** | **0.0048** | **3.653** | **3.995** | **3.367** | **4.055** | **4.053** | **0.784** | **0.965** | **1.971** | **0.71** |

**DNS No Reverb**（关键行）：

| Model | Para | RTF | SIG | BAK | OVRL | P808 | NISQA | SBS | Sim | PESQ | ESTOI |
|---|---|---|---|---|---|---|---|---|---|---|---|
| SBCTM | 65.98 | 0.02 | 3.523 | 4.128 | 3.298 | 3.906 | 4.574 | 0.870 | 0.986 | **2.835** | 0.898 |
| **ZipEnhancer** | 2.04 | 0.105 | 3.578 | 4.136 | **3.35** | 4.015 | 4.289 | **0.922** | **0.992** | **3.419** | **0.952** |
| Mamba-base | 3.61 | 0.0048 | 3.515 | 4.053 | 3.253 | 3.997 | 4.468 | 0.887 | 0.99 | 2.73 | 0.916 |
| **SBM** | 3.93 | 0.0048 | **3.751** | **4.129** | 3.292 | **4.187** | **4.657** | 0.893 | 0.99 | 2.825 | 0.921 |

**VoiceBank-Demand**（关键行）：

| Model | Para | RTF | SIG | BAK | OVRL | P808 | NISQA | SBS | Sim | PESQ | ESTOI |
|---|---|---|---|---|---|---|---|---|---|---|---|
| SBCTM | 65.98 | 0.02 | 3.4 | 4.085 | 3.156 | 3.533 | 4.646 | 0.891 | 0.978 | **3.558** | 0.868 |
| **ZipEnhancer** | 2.04 | 0.105 | 3.484 | 3.988 | 3.183 | 3.544 | 4.621 | **0.925** | **0.986** | **3.628** | **0.894** |
| **SBM** | 3.93 | 0.0048 | 3.412 | **4.135** | 3.253 | **3.616** | **4.737** | 0.820 | 0.981 | 3.503 | 0.891 |

> [!contradiction] 判别式模型在 PESQ / ESTOI / SpeechBERTScore 上仍领先 SBM
> **必须如实并列记录**（不替论文消解）：
> | 测试集 | 指标 | ZipEnhancer（2.04 M，判别式） | SBM（3.93 M，生成式） |
> |---|---|---|---|
> | DNS No Reverb | PESQ | **3.419** | 2.825 |
> | DNS No Reverb | ESTOI | **0.952** | 0.921 |
> | DNS No Reverb | SpeechBERTScore | **0.922** | 0.893 |
> | VoiceBank-Demand | PESQ | **3.628** | 3.503 |
> | VoiceBank-Demand | ESTOI | **0.894** | 0.891 |
> | VoiceBank-Demand | SpeechBERTScore | **0.925** | 0.820 |
>
> ⇒ **SBM 的优势集中在 SIG / OVRL / P808MOS / NISQA 这类"对齐无关"（alignment-agnostic）指标**。
> **论文的论证**（如实转述）：它引用 **Blau & Michaeli 的 perception-distortion tradeoff [39]**，指出"**严格对齐敏感指标往往对偏离结构的预测惩罚重于对过度平滑的预测**"，因此**把对齐无关指标定为主指标**，对齐敏感指标作为全面评估的补充。
> **另一处论文自陈**：训练时**混入 25% double-talk 场景以保留次要说话人**，因此在要求单说话人隔离的测试上 **SpeechBERTScore 被拉低**——论文称这是"**面向真实多说话人环境的策略性设计选择，而非增强能力的缺陷**"。
> **库内记录方式：并列记录、标注作者的解释，不判定谁对。** 引用 SBM 时**必须同时说明这两点**，否则会误读为"生成式全面超越判别式"。

### 4.3 Table 2：DNS Real Recordings（无干净参考，故不报侵入指标）

| Model | SIG | BAK | OVRL | P808MOS | NISQA |
|---|---|---|---|---|---|
| SB-NCSN++(50) | 3.369 | 3.939 | 3.052 | 3.685 | 3.604 |
| SB-NCSN++(10) | 3.332 | 3.933 | 3.024 | 3.723 | 3.865 |
| SB-NCSN++(1) | 3.297 | 3.924 | 2.979 | 3.514 | 3.541 |
| SBCTM | 3.224 | 3.841 | 2.894 | 3.506 | 3.647 |
| SB-UFOGen | 3.255 | 3.838 | 2.911 | 3.485 | 3.196 |
| ZipEnhancer | 3.323 | 3.918 | 3.002 | 3.639 | 3.264 |
| Mamba-base | 3.284 | 3.974 | 2.993 | 3.683 | 3.644 |
| FM-Mamba | 3.32 | 4.031 | 3.052 | 3.562 | 3.797 |
| **SBM** | **3.459** | **4.106** | **3.198** | **3.742** | **3.937** |

⇒ **SBM 在真实录音上全项最高。**

### 4.4 与 SB 家族基线的对比（论文的三条结论）

1. **相对 SB-NCSN++(1)**（同一步推理协议，NCSN++ 骨干）：DNS With Reverb SIG **3.653 vs 3.281**、OVRL **3.367 vs 2.948**、PESQ **1.971 vs 1.586**。且 SBM **RTF 0.0048 vs 0.0155（快 3.2 倍）**、参数量 **3.93 M vs 25.16 M（少 6.4 倍）**。
   ⇒ **换骨干（NCSN++ → Mamba）本身带来巨大效率与质量收益。**
2. **相对 SBCTM / SB-UFOGen**：论文指出"虽然 CTM 与对抗训练技术加速了推理并维持了性能，但**它们未能解决 NCSN++ 结构固有的规模与效率问题**"。⇒ SBM 的优势来自**结构改变**，不是加速技巧。
3. **相对 Mamba-base（mapping 同骨干）与 FM-Mamba（flow matching 同骨干）**：SBM 在**无 RTF 退化**的前提下全面领先（RTF 三者同为 0.0048）。

> [!important] "零推理开销"的证据
> **Mamba-base（3.61 M / RTF 0.0048）→ SBM（3.93 M / RTF 0.0048）**：
> 参数只增 **0.32 M**（时间嵌入模块），**RTF 完全不变**。
> ⇒ **SB 范式的收益是在"零推理开销"下获得的**——这与 [[wiki_low_latency/entities/LCA-Latency-Control-Adapter]] 的"adapter bank 只增存储不增运行时算力"是**同类设计性质**。
> 论文也点出实用含义："**相同骨干结构意味着针对 Mamba 的端侧优化技术同样适用于 SBM，进一步便利其部署。**"

---

## 5. 这个方向还剩什么问题没解决？

### 5.1 论文自陈的局限与 future work

**结论段给出的 future work**：
> 我们计划把 SBM 扩展到更广的音频处理任务，如**超分辨率**与**语义级修复**，并进一步研究其底层机制。

**正文中的自陈**（散落在 §3.4）：
- 在 DNS No Reverb 与 VoiceBank-Demand 上**仅含噪声伪影**的数据集上，SBM 与判别式 ZipEnhancer"**有竞争力**"（**未声称超越**）；
- **25% double-talk 训练导致 SpeechBERTScore 在单说话人隔离测试上被拉低**（"策略性设计选择"）；
- "未来工作将进一步研究基于轨迹建模的训练的贡献"⇒ **即 SB 收益的机制本身尚未被完全解释**。

**论文没有独立的 limitations 章节。**

### 5.2 ★ 延迟账本：论文的 "under 40 ms" 漏计了 $\tau_{enc}$

**论文原文（§2.2）**：

> "For streaming feasibility, the Mamba backbone operates with a small lookahead of **2-4 frames**, yielding an **algorithmic latency under 40 ms** to balance causality and enhancement quality."

**独立核算**：

| 项 | 计算 | 值 |
|---|---|---|
| STFT 窗长 | 480 样本 @ 16 kHz | **30 ms** |
| STFT hop | 160 样本 @ 16 kHz | **10 ms** |
| $\tau_{enc} = L_{len}/f_s$ | 480 / 16000 | **30 ms** |
| $\tau_{sep} = T_{la}\cdot L_{shift}/f_s$ | $T_{la}=2\sim4$ 帧 × 10 ms | **20 – 40 ms** |
| **论文声称的"算法延迟"** | $4 \times 10$ ms = 40 ms | **仅 $\tau_{sep}$** |
| **按库内口径的实际算法延迟** | $\tau = \tau_{enc} + \tau_{sep}$ | **50 – 70 ms** |

> [!question] 这是"漏计 $\tau_{enc}$"的典型案例
> 论文的 "under 40 ms" 恰好等于 **4 帧 lookahead × 10 ms hop** ⇒ **它只计算了 lookahead 项，未计入 30 ms 的窗缓冲**。
> 而 [[wiki_low_latency/entities/LCA-Latency-Control-Adapter]] 论文 §3.2 恰恰明确警告过这一现象："**Note that some studies report latency without explicitly accounting for this buffering term, so care is needed when comparing them.**"
> ⇒ **SBM 正是它警告的那类文献。**
> **处置：按库内 `[[wiki_low_latency/concepts/严格因果与算法延迟]]` 与 `[[wiki_low_latency/concepts/低时延前端与延迟账本]]` 的口径，记录 SBM 的算法延迟为 50–70 ms（而非 40 ms），并标注这是口径差异而非论文错误。**
> **不要替论文判定 "40 ms 成立"。**

### 5.3 未报告、但库内口径要求报告的字段

| 字段 | 状态 | 说明 |
|---|---|---|
| **$\tau_{enc}$ 是否计入** | **未计入**（见 §5.2） | 论文的 "algorithmic latency" 只含 lookahead |
| **RTF 的 GPU 型号** | **未指明** | 只说 "measured on a GPU"，对 10 段 10 秒音频取平均 |
| **STFT center** | **未报告** | 记入"STFT center 审计表"待办 |
| 内存 / 参数量分布 | 只报总参数（3.93 M） | — |
| 冷启动 / 稳态区分 | 未报告 | — |
| 端到端延迟 | 未报告 | — |
| 实时工作点 / deadline | 未报告 | — |

> [!warning] RTF 口径警告：与库内 LiSenNet 不可比
> SBM 的 **RTF 0.0048 在 GPU 上测（型号未指明）**；
> [[wiki_low_latency/entities/LiSenNet]] 的 **RTF 0.028 在 Xeon E5-2620 v4 CPU 上测**。
> ⇒ **硬件类别不同（GPU vs CPU）、型号信息完整度不同 ⇒ 两者不可直接比较。**
> 且两者的 RTF 定义都是"处理 1 秒语音所需时间"（同分母），但**硬件差异使数值失去可比性**。
> 按库内算力证据等级：SBM 属 **L1**（有 RTF、有硬件类别，但无硬件型号、无算法延迟工作点、无 chunk 配置）。

### 5.4 我读出来的隐藏问题

**1. "一步推理"的真实含义：一步 ≠ 便宜。**
SBM 的单步仍是一次**完整的 Mamba 前向**（3.93 M 参数、oSpatialNet-Mamba + fullband Mamba 层）。⇒ **它压缩的是"推理步数"，不是"单步成本"**。
论文的对比基线是 SB-NCSN++(50/10/1)，其中 **SB-NCSN++(1) 也是单步**——SBM 相对它的优势（SIG 3.653 vs 3.281）主要来自**换骨干**，而非"步数更少"。
⇒ **"生成式能不能靠近实时"这个问题，本篇的回答是"能靠 RTF，不能靠算法延迟"**（见 §7）。

**2. 算法延迟的口径问题掩盖了一个更重要的事实：50–70 ms 的前端决定了它离 2 ms 目标约 25–35 倍。**
即使把 lookahead 降到 0，30 ms 的窗长本身就使它无法进入库内的量级。⇒ **SBM 的贡献与库内的核心约束正交**：它优化的是"生成式推理步数"，不是"算法延迟"。

**3. `fullband Mamba 层` 的因果性未被讨论。**
论文说集成 fullband Mamba 是为了"捕捉**全局谱动态与帧间依赖**"（动机是 oSpatialNet 的**时间局限**）。但**"帧间依赖"这个说法暗示它可能跨帧（甚至跨全序列）** ⇒ **若该层是双向或全序列的，则"2–4 帧 lookahead"的流式主张不成立**。
论文**没有交代该层的因果性/作用域**。⇒ **记为一处未闭合的因果缺口（`[!question]`），不替它判定。**

**4. 25% double-talk 训练是一个未被量化的设计选择。**
论文把它作为 SpeechBERTScore 偏低的解释（"策略性设计选择"），但**没有给出"去掉 double-talk 会怎样"的消融** ⇒ **无法判断这个选择是净收益还是净损失**。

**5. 训练数据 800 小时，远超库内其他模型。**
库内轻量模型（[[wiki_low_latency/entities/GTCRN]]、[[wiki_low_latency/entities/LiSenNet]]）的训练数据在 44 小时量级（VoiceBank+DEMAND）。⇒ **SBM 的数字与库内任何模型都不可比**（数据规模 + 测试集 + 指标族三者都不同）。

**6. SB vs flow matching 的对比只有一个配置。**
FM-Mamba 用 OT-CFM 公式计算中间态，其余与 SBM 完全相同。⇒ 这是一次干净的单点对比（SIG 3.653 vs 3.164）。但**只做了一个配置**，且论文自陈"**未来工作将进一步研究基于轨迹建模的训练的贡献**"⇒ **SB 优于 FM 的结论强度有限**。

---

## 6. 本论文在库中的位置关联（cross-reference matrix）

### 前身 / 基石

| 关系 | 论文 | 留下了什么 gap 由本篇解决 |
|---|---|---|
| **SB 骨干基线** | **SB-NCSN++**（Jukić et al., Interspeech 2024，文献 [2]） | 绝大多数 SB-SE 用 NCSN++ 骨干 ⇒ **规模与效率问题未解决**（25.16 M / RTF 0.767 @50 步） |
| SB 加速 | **SBCTM**（Nishigori et al., WASPAA 2025，文献 [6]） | 用一致性轨迹建模实现一步推理，但**未换骨干**（65.98 M） |
| SB 加速 | **SB-UFOGen**（Han et al., Interspeech 2025，文献 [5]） | 用对抗训练实现一步推理，**未换骨干**（25.16 M） |
| 骨干 | **oSpatialNet**（Quan & Li, IEEE SPL 2024，文献 [16]） | 提供 oSpatialNet-Mamba 的架构基础；但**有时间局限** ⇒ 本篇加 fullband Mamba 层 |
| 骨干 | **SpatialNet**（Quan & Li, TASLP 2024，文献 [25]） | 提供全局建模的启发 |
| **同族 SE 骨干** | **SEMamba**（Chao et al., SLT 2024，文献 [17]） | 用双向 Mamba 做 SE，但**用确定性映射/掩蔽训练** ⇒ **未利用生成式轨迹学习** |
| 同族 SE 骨干 | **USEMamba**（Chao et al., Interspeech 2025，文献 [18]） | 扩到 GSR（回归 + flow matching），但**仍是映射/回归范式** |
| SSM 基础 | **Mamba**（Gu & Dao，文献 [15]） | 提供选择性状态空间递推 |
| Mamba 理论 | **From Markov to Laplace**（Bondaschi et al., ICLR 2025 Workshop，文献 [24]） | 证明 Mamba 在捕捉马尔可夫序列动力学上的数学最优性 ⇒ 支撑"SB 与 Mamba 适配"的论证 |
| 判别式强基线 | **ZipEnhancer**（Wang & Tian, ICASSP 2025，文献 [20]） | 判别式 SOTA（2.04 M）⇒ **在 PESQ/ESTOI/SpeechBERTScore 上仍领先 SBM** |
| 理论依据 | **Blau & Michaeli, perception-distortion tradeoff**（文献 [39]） | 用于论证"对齐敏感指标惩罚偏离结构过重"⇒ 支持以对齐无关指标为主指标 |
| flow matching 对照 | **OT-CFM**（文献 [43][44]） | 提供 FM-Mamba 基线的中间态计算方式 |

> [!note] 一个值得注意的引用
> SBM 的文献 **[44]** 是 "**Rethinking Flow and Diffusion Bridge Models for Speech Enhancement**"，arXiv:2602.18355, 2026，作者 **D. Wang, J. Gao, T. Lei, Y. Hu, C. Zhu, K. Chen, J. Lu**。
> ⇒ **这是库内 [[wiki_low_latency/entities/GTCRN]] / UL-UNAS 的南京大学课题组（Jing Lu）** 的流/扩散桥工作。说明该组在 2026 年也在做桥模型的理论梳理。⚠️ **库内暂无该篇页面。**

### 后续 / 扩展

**库内暂无。** SBM 是 2026-10-07 新进库。

### 同分支竞品（★ 库内最重要的对照）

| 论文 | 与 SBM 的关系 |
|---|---|
| [[wiki_low_latency/entities/RT-SEMamba]] | **两者都是"Mamba + 流式增强"，但路线相反**：<br>• **RT-SEMamba：判别式**，8 层因果 Mamba，**渐进知识蒸馏**到 1 层，25 ms 约束，VoiceBank+DEMAND PESQ 3.32<br>• **SBM：生成式**，SB 轨迹训练，**一步推理**，2–4 帧 lookahead（实际 50–70 ms），DNS/VBD<br>⇒ **这是库内"判别式 vs 生成式在流式 Mamba 上的直接对照"**。注意两者都引用/被 SEMamba 家族串联（SBM 引 SEMamba [17]、USEMamba [18]）。 |
| [[wiki_low_latency/entities/PSMSE]] | 并行脉冲 Mamba（0.26 M / 0.11 G/s，30 ms）⇒ 同为 Mamba 流式家族，但**用脉冲网络压算力**，路线又不同 |
| [[wiki_low_latency/entities/SEMamba++]] | **同期、同族（SEMamba 家族）、相反约束**：SEMamba++ 是非因果离线 GSR（双向 Mamba，无延迟约束）；SBM 是半因果流式增强（SB 轨迹 + 一步）。**两篇都引 SEMamba，但互不引用** |
| [[wiki_low_latency/entities/FastEnhancer]] | 提供 5 档 T–L 权衡与"名义 MACs 会给出错误排序"的证伪 ⇒ SBM 的 RTF 0.0048 **有硬件（GPU）但无型号**，按 FastEnhancer 的教训需谨慎解读 |

### 跨分支类比

| 论文 | 类比价值 |
|---|---|
| [[wiki_low_latency/entities/LCA-Latency-Control-Adapter]] | **同类设计性质**：LCA 的 adapter bank **只增存储不增运行时算力**；SBM 的时间嵌入**只增 0.32 M 参数不增 RTF**。⇒ 都是"用存储换能力、运行时零代价"的设计 |
| [[wiki_low_latency/concepts/2409.10358-ultra-low-latency-benchmark]] | Wu & Braun 的综述是库内延迟口径的来源 ⇒ **SBM 的 "under 40 ms" 正是该综述警告的"漏计 buffering"案例** |
| [[wiki_low_latency/concepts/严格因果与算法延迟]] | 库内口径的直接应用对象 |

> [!contradiction] 生成式与严格因果低时延"几乎不相交"这一判断，被本篇再次印证
> 库内 2026-10-06 趋势报告的结论是：INTERSPEECH 2026 的 13 篇低延迟增强论文**没有一篇用扩散或流匹配，全是判别式或传统 DSP** ⇒ **生成式与低延迟是两个几乎不相交的圈子**。
> **SBM 是"最接近相交"的那一篇**——它是生成式（SB）、做了一步推理、RTF 0.0048、明确声称 "for streaming feasibility"。
> **但它仍然**：① 有 2–4 帧 lookahead（非严格因果）；② 实际算法延迟 50–70 ms（含 30 ms 窗）；③ 在 PESQ/ESTOI 上输给判别式 ZipEnhancer。
> ⇒ **"生成式靠近实时"在本篇里的答案是：能靠近"吞吐（RTF）"，不能靠近"算法延迟"。** 详见 [[wiki_low_latency/concepts/sbm-2026-schrodinger-bridge-mamba]] §6。

---

## 7. 一句话总结"江湖地位"

```
2026 | 生成式增强 / 一步推理 | 首个把薛定谔桥训练范式与 Mamba 骨干协同起来的框架——用 SB 的 OT 中间态当"锚点"、用 Mamba 的递推结构学最优控制，训练期把 SB 变换蒸馏进 Mamba 动力学 → 3.93 M 参数、RTF 0.0048（全表最低）、DNS Real Recordings 全项最高；但算法延迟口径漏计 30 ms 窗（实际 50–70 ms），且在 PESQ/ESTOI 上仍输给判别式 ZipEnhancer
```

**更实用的定位**：SBM 在库内的价值是**三层**——
1. **它回答了"生成式能不能靠近实时"这个问题的前半段**：**在吞吐（RTF）意义上可以**——一步推理 + Mamba 骨干 + RTF 0.0048（比 SB-NCSN++(50) 快 160 倍），且**零推理开销地获得了 SB 的收益**（RTF 与 Mamba-base 相同）。
2. **它同时回答了后半段**：**在算法延迟意义上不能**——2–4 帧 lookahead + 30 ms 窗 ⇒ 50–70 ms，距库内 2 ms 目标约 25–35 倍。
3. **它提供了一个干净的消融模板**：用"3 骨干 × 2 范式"的交叉设计把"训练范式"与"骨干架构"的贡献**解耦**，证明 SB 在 MHSA/LSTM/Mamba 上一致有效（+0.246 / +0.206 / +0.175）。

**但它在库内不可作基线**：非严格因果、无 RTF 硬件型号、训练数据 800 小时、测试集与指标族都与库内不同。

---

## 参考资料

1. J. Yang, S. Wang, C. Wu, L. Guo, F. Fan, "Schrödinger Bridge Mamba for One-Step Speech Enhancement," in *Proc. Interspeech 2026*, pp. 1363-1368. DOI: 10.21437/Interspeech.2026-682
2. 本地归档：`raw/papers/low_latency_causal_se/SchrodingerBridgeMamba-Interspeech2026.pdf`（952,896 bytes，6 页）
3. 演示页：https://sbmse.github.io
4. 抽取全文：`tmp/pdf_extract/sbm.txt`
5. 页面渲染：`wiki_low_latency/assets/sbm_2026/sbm-page1.png` … `sbm-page6.png`（150 dpi）
6. 库内相关页面：[[wiki_low_latency/entities/Schrodinger-Bridge-Mamba]]、[[wiki_low_latency/concepts/sbm-2026-schrodinger-bridge-mamba]]、[[wiki_low_latency/entities/RT-SEMamba]]、[[wiki_low_latency/entities/PSMSE]]、[[wiki_low_latency/concepts/严格因果与算法延迟]]
7. 单位：**Central Media Technology Institute, Huawei（华为中央媒体技术院）**
8. 通讯作者：Jing Yang

> [!note] venue 说明
> Interspeech 2026 正式录用论文，ISCA Archive 官方页脚版（逐页页码 1363–1368 + DOI `10.21437/Interspeech.2026-682`）⇒ **venue 证据等级 (a) 已正式出版**。
> 论文声明生成式 AI 工具**仅用于语言编辑与润色**。
