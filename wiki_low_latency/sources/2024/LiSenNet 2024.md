---
title: "LiSenNet: Lightweight Sub-band and Dual-Path Modeling for Real-Time Speech Enhancement"
type: source
domain: low_latency_causal_se
venue: "arXiv preprint (eess.AS) — 投稿 ICASSP 2025，未获录用"
venue_status: preprint_only
year: 2024
arxiv: 2409.13285
doi: 10.48550/arXiv.2409.13285
authors:
  - Haoyin Yan
  - Jie Zhang
  - Cunhang Fan
  - Yeping Zhou
  - Peiqi Liu
affiliations:
  - "NERC-SLIP, University of Science and Technology of China (USTC)"
  - "Anhui Province Key Laboratory of Multimodal Cognitive Computation, Anhui University"
  - "China Merchants Bank (CMB), Shenzhen"
local_pdf: raw/papers/low_latency_causal_se/2409.13285.pdf
code: https://github.com/hyyan2k/LiSenNet
evidence_policy: arXiv_pdf
tags:
  - 超轻量
  - 子带
  - 双路径
  - 噪声检测器
  - GLA相位精修
created: 2026-09-27
updated: 2026-09-27
---

~~~yaml
- 论文: LiSenNet: Lightweight Sub-band and Dual-Path Modeling for Real-Time Speech Enhancement (2024)
  ├── 要解决什么问题: 学习型 SE 的参数量与算力太大，无法部署到助听器/TWS耳机/IoT；已有的轻量方案（FSPEN 79k/89M、CCFNet+ 160k/390M）还不够轻
  ├── 核心方法: 子带降采样/升采样（低频保分辨率）+ DPR 双路径循环模块（频率轴 Bi-GRU、时间轴单向 GRU + ConvGLU）+ 可选噪声检测器（帧级门控）+ GLA 相位精修
  ├── 属于哪个分支: 超轻量 / 子带-双路径路线（与 GTCRN、FSPEN、BSRNN 同族）
  ├── 输入/输出: 功率压缩幅度谱 (A_x)^c（c=0.3）+ 相位差 PD（Δ_f、Δ_t 拼接）→ 幅度掩蔽 → GLA 精修相位 → 波形
  ├── 关键trick: ① 子带 DS-Conv/US-Conv 让低频走 stride 1、高频走 stride 3 ⇒ 整体 2× 降采样但低频不被压 ② 用 ConvGLU 补 RNN 节点被砍导致的容量损失 ③ 噪声检测器做**帧级**自适应计算（尾延迟不变、只省平均算力）
  ├── 数据集: VoiceBank+DEMAND（11,572/872）；自建 WSJ0+ESC50（用于评噪声检测器）
  ├── 对比了谁: RNNoise、CRN*、DCCRN*、FullSubNet*、Fast FullSubNet*、CCFNet+ (Lite)、FSPEN（* = 作者重训）
  ├── 性能上限: VoiceBank+DEMAND PESQ **3.07** / STOI 0.939 @ 37k / 56M；WSJ0+ESC50 PESQ 3.08 / RTF **0.028**（Xeon E5-2620 v4）
  ├── 参数量: **37k** / **56M MMACs per second**（自称约为 SOTA 的一半）
  ├── 消融关键发现: DPR 的 N：22M→39M→56M→72M 对应 PESQ 2.68→2.97→**3.07**→3.06（N=2 是拐点，N=3 已无增益）；GLA k=2 饱和；去掉 PD 掉 0.08、去掉 L_pesq 掉 0.12
  ├── 遗留问题(你的机会): **全篇无算法延迟、无 STFT 的 center 锚定**；**前端 16 ms hop 已超本库 2 ms 目标一个数量级**；GLA 需 2 次 STFT/iSTFT 往返（延迟与算力未入账）；噪声检测器只省平均算力不降尾延迟；模型级因果性只有"frequency 用 Bi-GRU、temporal 用 uni-GRU"一句话
  └── 跟哪篇像: FSPEN（子带+path extension，直接前身与主竞品）、GTCRN（子带+分组 DPRNN，同为超轻量锚点）、DPCRN（双路径循环）、MetricGAN+（用判别器预测 PESQ）
~~~

> [!warning] PDF 质量与来源
> 本页基于 **arXiv:2409.13285v1**（2024-09-20 提交）的 PDF 逐页抽取与渲染。PDF 由 `pdfTeX-1.40.25` 生成，5 页，文本层完整、无扫描件问题；标题/作者元数据字段为空，**作者与单位取自 PDF 正文首页**而非元数据。
> 论文首页页脚为 `arXiv:2409.13285v1 [eess.AS] 20 Sep 2024`，**无任何会议页眉或版权行**。

> [!important] venue 判定：这是**纯预印本**，且 arXiv `Comments` 明确记载它**投稿了 ICASSP 2025 但未获录用**
> arXiv `Comments` 字段原文：**"5 pages, submitted to 2025 IEEE International Conference on Acoustics, Speech, and Signal Processing (ICASSP 2025)"**。
> 按本库 venue 分级规则，arXiv `Comments` 里出现的会议名**只有在表示"已被录用"时才构成录用证据**；这里是 **"submitted to"（投稿）**，语义相反。
> ⇒ 判定为 **(c) 纯预印本**，frontmatter 记 `venue_status: preprint_only`，**不标任何会议**。
> **与 GTCRN / PrimeK-Net 的对照**：那两篇的 `Comments` 或页脚给出的是"accepted by"/版权行，属 (a) 档；本篇是 (c) 档。**"用了 ICASSP 模板"不构成录用证据**（本库已有此纪律）。
> **但它有一个客观后果**：ICASSP 2025 的投稿页数上限为 5 页，而本篇恰好 5 页——这与"投稿未中"是一致的，本库只记录事实，不揣测原因。

## 1. 他们为什么这么做？（motivation）

论文的动机链是**一条纯粹的部署驱动链**，全部三页引言都在围绕"小到能塞进设备里"展开：

- **① 学习型方法效果好，但塞不进设备**：「the large computational complexity and model size heavily limit the deployment on **latency-sensitive and low-resource edge devices**」。目标设备被明确点名：**助听器（hearing aids）、耳机（headphones）、IoT 设备**。
- **② 已有的"轻量"还不够轻**。论文点出两条它认为不够的路线：
  - **RNNoise**（0.06M / 0.04G）：极致轻，但"the coarse resolution of the bands is addressed by a **pitch filter**"——靠后处理补分辨率，**质量上限被锁死**（Table I 只有 PESQ 2.33）。
  - **FSPEN**（79k / 89M）：已经用子带+全带编码器和 inter-frame path extension，但**参数仍是本篇的 2.1×**。
- **③ 所以要么把 PESQ 再推高、要么把参数再压小，而本篇选择同时做**：Abstract 的落脚句是「**37k parameters (half of the state-of-the-art model) and 56M MAC per second**」，而 Table I 里它同时**赢过 FSPEN 的 PESQ**（3.07 vs 2.97）。⇒ 这是一次**双赢式声称**，不是纯 trade-off。

> [!note] 本条动机在本库的分类中属 **M2「够小与够好没有交集」** 的正面攻击
> 与 GTCRN 的动机（同样瞄准超轻量）、PrimeK-Net 的动机（性能优先、不设算力约束）相比，本篇是**三篇里参数目标最激进的一篇**（37k，比 GTCRN 的 23.7k 略大，但比 FSPEN 79k 小一半）。
> **真正的差异在"轻量化的手段"**：GTCRN 靠 **ERB 非均匀频带**压缩 + 分组 DPRNN；本篇靠 **子带级 stride 差异化**（低频不吃降采样）+ RNN 节点砍半后用 ConvGLU 补偿。详见 §3。

## 2. 之前的人怎么做不了？（limitation → gap）

| 之前的路线 | 论文给出的不足 | 为什么至今没解决 |
|---|---|---|
| **传统信号处理**（Wiener 类） | 「based on well-established theories and reasonable assumptions but often **suffer from non-stationary acoustic scenes**」 | 非平稳噪声需要数据驱动的先验，传统框架给不出 |
| **RNNoise**（0.06M/0.04G） | 频带分辨率太粗，靠 **pitch filter** 补救 | 极点轻量的代价是**频域表达力受限**，PESQ 停在 2.33 |
| **CRN / DCCRN / FullSubNet** | 效果上去了，但**参数量与算力爆炸**（17.58M/2.56G、3.67M/14.38G、5.64M/30.87G） | 卷积循环 / 复数运算 / 全带-子带级联都把模型撑大 |
| **FSPEN**（79k/89M） | "reaches a balance ... to some extent"——**只是"某种程度上"**；参数量仍偏高 | 子带+全带双编码器 + inter-frame path extension 本身就有固定开销 |
| **CCFNet+ (Lite)**（160k/390M） | 两阶段（粗全带掩蔽 + 低频精修）结构，**MACs 高达 390M** | 两阶段意味着**两次前向**，算力不易压 |

**gap 的准确表述**：在 **≤40k 参数 / ≤60M MACs** 这一档里，**当时没有能打过 FSPEN 的模型**。论文的赌注是「**参数还能再砍一半，而质量不掉反升**」。

> [!question] gap 的表述里有一处本库要标注的模糊：**"half of the state-of-the-art model" 指的是谁？**
> Abstract 只写 "half of the state-of-the-art model"，**未指名**。从 Table I 反推，**只有 FSPEN（79k）能被 37k 恰好"砍半"**（37/79 = 46.8%）。
> §3.2 正文另写「only **47% parameters and 63% MACs**」——这两个百分比**正好对应 FSPEN**（37/79 = 46.8% ≈ 47%；56/89 = 62.9% ≈ 63%）。
> ⇒ 本库判定："state-of-the-art model" **实指 FSPEN**，但**论文没有明写**，读者需要自己算出来。**记录为表述不严谨，不静默补全。**

## 3. 这个做法核心 trick 是什么？

论文叠了**五个模块**，但真正有辨识度的只有三个。按"如果只能保留一个"的优先级排列：

### 3.1 核心 trick ①：子带 DS-Conv / US-Conv —— 低频不参与降采样

标准做法是 encoder 里一路 stride=2 降频。本篇把它**拆成两路**：

| 频段 | 降采样（DS-Conv） | 升采样（US-Conv） |
|---|---|---|
| **低频** | `Conv2d`, **stride = 1** | `Conv2d` 对称恢复 |
| **高频** | `Conv2d`, **stride = 3** | `SP-Conv2d`（sub-pixel，因子 **3**） |

⇒ 两路合并后**整体频率维降采样因子恰为 2**（与朴素 stride=2 等价），但**低频保持原分辨率**。

**理由（论文原话）**：「in general **low-frequency bands play a more important role in human hearing** than high-frequency bands」（引 PLP 分析 [15]）。⇒ 用同样算力，把分辨率预算**按听觉重要性分配**。

> [!important] 这是本库"分组/子带压缩"路线的**第三种实现哲学**，必须与另两种分开记
> | 实现 | 分组依据 | 代表 | 本库评价 |
> |---|---|---|---|
> | **ERB 非均匀频带压缩** | **人耳临界带**（等效矩形带宽） | [[wiki_low_latency/sources/2024/GTCRN 2024]] | 频带数由感知模型定，压缩比最强（GTCRN 23.7k） |
> | **素数核分组频率卷积（GPFN）** | **周期互质性**（核长取素数 {3,11,23,31}） | [[wiki_low_latency/sources/2025/PrimeK-Net 2025]] | 不压缩通道，靠**核尺寸多样性**换感受野多样性 |
> | **子带 stride 差异化** | **听觉重要性 + 硬件 stride 约束** | **本篇 LiSenNet** | 唯一**显式区分低/高频 stride** 的一种；其余两种是在通道维或核维做文章 |
> ⇒ 三者的正交性在于：**GTCRN 改"通道怎么分"、PrimeK-Net 改"核怎么取"、LiSenNet 改"采样率怎么变"**。

### 3.2 核心 trick ②：DPR 模块 —— 用 ConvGLU 补偿被砍掉的 RNN 节点

DPR 的双路径顺序与 DPRNN/DPCRN 一致：先把 `M ∈ R^{B×C×T×F}` reshape 成 `BT × F × C` 做**频率建模**，再 reshape 成 `BF × T × C` 做**时间建模**。

**因果性处理**（论文原话）：「**To ensure the causality of our model, we apply bidirectional GRU (Bi-GRU) for frequency modeling and unidirectional GRU for temporal modeling.**」
⇒ **频率轴可以双向（因为同一帧内全部频率同时可得），时间轴必须单向**——这是本库反复出现的那条正确直觉。

**真正的新东西是 ConvGLU**：为了实时性，**RNN 隐藏维被砍到很小**（uni-GRU 24 维、Bi-GRU 12 维），论文自陈这导致 "the **decay of modeling capacity**"。补偿手段是插入一个 ConvGLU 做**通道混洗**：

$$
\text{ConvGLU}: \text{Linear} \;\rightarrow\; \text{DWConv(depthwise)} \;\rightarrow\; \text{Mish}
$$

论文说 DWConv「can aggregate the **nearest** information」，门机制「allows for a **fine-grained channel attention**」。⇒ 本质是**用一次便宜的局部卷积 + 门控，换回被砍掉的通道间交互能力**。

> [!note] 这是"**降容量的同时补容量**"这一设计模式在本库的又一次出现
> 与 GTCRN 的 **SFE/TRA**（用极便宜的模块补子带压缩造成的信息损失）是**同一思路**：**主结构压得太狠 ⇒ 必须配一个低成本补偿模块**。
> 差别在于：GTCRN 的补偿模块作用在**频带维**（SFE 做频带间融合），本篇的 ConvGLU 作用在**通道维**。
> 而两者都踩了同一个坑：**补偿模块的性价比没人算过**。GTCRN 的 TRA 是"+0.56 M/s MACs 换 SISNR +0.38、SFE 是 +5.16 M/s 只换 +0.23"，本篇的 ConvGLU 则是"**−8M MACs、−6k 参数，PESQ −0.09**"（见 §4）——**方向相反**：本篇是**去掉它反而更便宜但更差**，说明它在净收益上是正的。

### 3.3 核心 trick ③：噪声检测器（ND）—— 帧级自适应计算

**动机**：「instantaneous noises, where the noise duration can be **much shorter than the speech length**. Turning on the SE module continuously would cause a large amount of unnecessary resource consumption.」

**做法**：一个独立前端，输入 **64 维 Mel 谱**（降冗余），输出**帧级二值判决**（0 = 干净、1 = 有噪，Sigmoid 层）。**只有被判为"有噪"的帧才送进 SE 后端。**

**收益**：Table II 里 `LiSenNet+ND` 的 MACs 从 56M 变成 **15M ∼ 70M**（随噪声比例浮动）；Fig. 2 画出 RTF 随噪声比例上升的曲线，噪声比例 0% 时 RTF 最低。
**代价**：PESQ **3.08 → 3.00**（−0.08），原因是 "the imprecision of noise detection and the **information loss of clean regions**"。

> [!warning] ND 不是延迟优化，是**平均算力**优化——这篇论文没有把这句话写清楚
> **关键**：ND 是**帧级**（frame-level）门控，**没有跨帧的状态跳过**，所以：
> ① **每帧仍要走一次 ND 前向**（虽然很便宜）；
> ② **尾延迟不变**——最坏情况（全程有噪）下 MACs 是 **70M，比不加 ND 的 56M 还高 25%**！
> ③ 它降的是**平均算力**，而实时硬件必须按最坏情况预留。
> ⇒ 与本库第 5 条判定口径（[[wiki_low_latency/overview#2026-09-22 补充：平均算力 ≠ 可用算力|平均算力 ≠ 可用算力]]）**直接相关**：论文报的是区间 `15M∼70M`，**没有报峰值**，而按最坏情况看这个方案是**负收益**的。
> 论文对这一点**零讨论**。本库记录为：**ND 的算力收益必须与"噪声比例分布"绑定才成立**——在语音密集集（如 VoiceBank+DEMAND）上它没有收益，甚至有害。

### 3.4 其余两个模块（较次要）

- **GLA 相位精修**（§3.4）：不直接用含噪相位合成，而是把估出的幅度 `Â_y` 与含噪相位 `P_x` 一起送进 Griffin-Lim 迭代 `P̂_y = GLA(Â_y, P_x)`（Eq. 5）。消融显示 k=2 已饱和（3.07），不用 GLA（Noisy Phase）掉到 3.02。**注意 GLA 每个迭代要做一次 STFT + iSTFT 往返**，其延迟与算力**未计入任何表**。
- **LSigmoid 输出层**（Eq. 3）：`LSigmoid(x) = β/(1+e^{−αx})`，β=2.0 常数、**α ∈ R^F 可学习**。理由是高/低频掩蔽形状不同，让**每个频点有自己的 Sigmoid 斜率**。消融：冻结 α（w/o LSigmoid）→ 3.05。

### 3.5 损失函数（Eq. 6–9）

$$
\mathcal L = \lambda_1 \mathcal L_{\text{mag}} + \lambda_2 \mathcal L_{\text{comp}} + \lambda_3 \mathcal L_{\text{pesq}} + \mathcal L_{\text{bce}},
\qquad (\lambda_1,\lambda_2,\lambda_3) = (0.9,\;0.1,\;0.05). \tag{9}
$$

- $\mathcal L_{\text{mag}}$：功率压缩幅度谱上的 MSE（Eq. 6）
- $\mathcal L_{\text{comp}}$：功率压缩**复数谱**上的 MSE（Eq. 7），其中 $Y^c = (A_y)^c e^{iP_y}$
- $\mathcal L_{\text{pesq}}$：判别器 $D$ 预测 PESQ 的 MSE（Eq. 8），**沿用 MetricGAN [23] 的思路**
- $\mathcal L_{\text{bce}}$：噪声检测器的二分类交叉熵（**仅在含 ND 时**）

> [!note] 顺带记一条：功率压缩比 **c = 0.3**，与库内多篇一致
> 论文原话：「Similarly to [12], we set **c = 0.3** to equalize the importance of quieter sounds relative to loud ones.」
> 这与 [[wiki_low_latency/sources/2022/DeepFilterNet2 2022]] 等篇的 `c=0.3` 相同，说明**0.3 是本方向的默认值**。

## 4. 实验里哪个消融最关键？

### 4.1 主结果（Table I, VoiceBank+DEMAND）

![[wiki_low_latency/assets/lisen-net_2024/lisen-page4.png]]

> 图注：原论文第 4 页渲染，含 **Table I**（主对比）、**Table II**（WSJ0+ESC50 + RTF）、**Fig. 2**（RTF–噪声比例曲线）、**Table III**（消融）。本页所有数字均取自该页。

| Method | Para. | MACs | PESQ | STOI |
|---|---|---|---|---|
| Noisy | – | – | 1.97 | 0.921 |
| RNNoise [8] | 0.06M | 0.04G | 2.33 | 0.922 |
| CRN* [5] | 17.58M | 2.56G | 2.54 | 0.936 |
| DCCRN* [6] | 3.67M | 14.38G | 2.78 | 0.940 |
| FullSubNet* [7] | 5.64M | 30.87G | 2.89 | 0.940 |
| Fast FullSubNet* [33] | 6.84M | 4.14G | 2.79 | 0.935 |
| CCFNet+ (Lite) [9] | 160k | 390M | 2.94 | – |
| **FSPEN [10]** | **79k** | **89M** | **2.97** | **0.942** |
| **LiSenNet** | **37k** | **56M** | **3.07** | 0.939 |

`*` = 作者重训（"We retrained these models to obtain results."）

> [!contradiction] **FSPEN 的 PESQ 在库内出现了两个值：本篇 2.97 vs FSPEN 原文 2.97 —— 一致；但 MACs 口径不同**
> 本篇 Table I 记 FSPEN 为 **79k / 89M MACs**；而 [[wiki_low_latency/sources/2025/FastEnhancer 2025]] Table 2 记 FSPEN 为 **79k / 64M MACs**（且带脚注 `d` = 作者重实现重训）。
> ⇒ **参数量一致（79k），MACs 不一致（89M vs 64M，差 1.39×）**。两者都不可调和为四舍五入。
> 本库按"锚点数值先钉口径"规则**并列记录、不择一**，并指出最可能的来源：**FSPEN 原文声称 89M（本篇转录自原文），FastEnhancer 是它自己重实现后的实测 64M**。
> **另注 FSPEN 的 STOI**：本篇记 **0.942（表内最高）**，高于 LiSenNet 的 0.939。⇒ **LiSenNet 在 PESQ 上赢 FSPEN，但在 STOI 上输给 FSPEN**。论文 §3.2 只强调了 PESQ 的 +0.1，**未提 STOI 落后**。

### 4.2 噪声检测器的收益与代价（Table II, WSJ0+ESC50）

| Method | Para. | MACs | RTF | PESQ |
|---|---|---|---|---|
| Noisy | – | – | – | 1.86 |
| CRN [5] | 17.58M | 2.56G | 0.042 | 2.80 |
| DCCRN [6] | 3.67M | 14.38G | 0.184 | 3.05 |
| FullSubNet [7] | 5.64M | 30.87G | 0.386 | 2.99 |
| Fast FullSubNet [33] | 6.84M | 4.14G | 0.100 | 2.75 |
| **LiSenNet** | **37k** | **56M** | **0.028** | **3.08** |
| LiSenNet+ND | 55k | **15M∼70M** | **0.020** | 3.00 |

**RTF 的测量口径（论文原话）**：「The RTF is measured with **Intel(R) Xeon(R) E5-2620 v4 CPU**」。⇒ 有硬件、有 runtime 名称（CPU 型号），**这是本库 L1 级证据**（RTF + 硬件），但**缺 runtime 框架名、缺 chunk size、缺 batch 是否 = 1、缺是否含 STFT/iSTFT/GLA**。

### 4.3 Table III 消融（本页最关键的证据）

| 消融项 | Para. | MACs | PESQ | STOI | ΔPESQ vs 完整 |
|---|---|---|---|---|---|
| **LiSenNet（完整）** | 37k | 56M | **3.07** | 0.939 | 基准 |
| w/o PD（去掉相位差输入） | 37k | 56M | 2.99 | 0.936 | **−0.08** |
| **w/o L_pesq**（去掉 PESQ 判别器损失） | 37k | 56M | 2.95 | 0.937 | **−0.12** ← 最大 |
| w/o sub-band Conv（子带卷积换成普通卷积） | 30k | 54M | 3.01 | 0.938 | −0.06 |
| w/o ConvGLU | 31k | 48M | 2.98 | 0.937 | −0.09 |
| w/o LSigmoid（冻结 α） | 37k | 56M | 3.05 | 0.938 | −0.02 |
| DPR (N = 0) | 15k | 22M | 2.68 | 0.913 | **−0.39** |
| DPR (N = 1) | 26k | 39M | 2.97 | 0.935 | −0.10 |
| **DPR (N = 2)** | 37k | 56M | **3.07** | 0.939 | 基准 |
| DPR (N = 3) | 48k | 72M | 3.06 | 0.940 | **+0.00**（无增益） |
| GLA (Noisy Phase) | 37k | 56M | 3.02 | 0.939 | −0.05 |
| GLA (k = 1) | 37k | 56M | 3.06 | 0.939 | −0.01 |
| GLA (k = 2) | 37k | 56M | 3.07 | 0.939 | 基准 |
| GLA (k = 3) | 37k | 56M | 3.07 | 0.939 | 0.00 |

**读法（本库提炼）**：

1. **唯一"结构性"的敏感项是 DPR 的重复次数 N**：N=0（完全没有双路径模块，仅 15k/22M）时 PESQ 崩到 2.68（**−0.39**）。⇒ **这篇论文的性能主要来自 DPR 模块本身，不是子带卷积、不是损失、不是 GLA。**
2. **N=2 是明确的拐点**：N=2→3 时参数 +11k、MACs +16M（**+28.6%**），而 PESQ **从 3.07 微降到 3.06**、STOI 从 0.939 微升到 0.940。⇒ **N=3 是纯浪费**，论文的处理是对的。
3. **损失函数的贡献排名出人意料**：`L_pesq`（−0.12）> `PD`（−0.08）> `ConvGLU`（−0.09，与 PD 接近）> `sub-band Conv`（−0.06）> `GLA`（−0.05）> `LSigmoid`（−0.02）。
   ⇒ **用判别器直接优化 PESQ 这一项（−0.12）比架构上的子带设计（−0.06）贡献更大，且后者是论文的标题创新点。** 这与 MetricGAN 系列的既有结论一致。
4. **两个"零算术变化"的消融**：`w/o PD`、`w/o L_pesq`、`w/o LSigmoid`、`GLA(k≠2)` 的参数量与 MACs **完全不变**（37k/56M）——它们只改训练信号或推理后处理，**不改模型容量**。

> [!warning] 引用 Table III 时的一条硬性边界：**所有 ΔPESQ 都没有统计证据**
> Table III 只给单点值，**无 ± 标准差、无随机种子数、无显著性检验**。
> 而其中 **w/o LSigmoid（−0.02）、GLA(k=1)（−0.01）、DPR N=2→3（−0.01）三项的差值 ≤0.02**，
> 按本库第 6 条判定口径（小效应量必须配统计证据，否则标注"未经显著性检验"）——**这三项在本库不得用作"该模块有效"的证据**。
> 相对地，**DPR N=0 的 −0.39、L_pesq 的 −0.12、ConvGLU 的 −0.09、PD 的 −0.08** 量级明显更大，可信度较高（但仍无统计检验）。

> [!important] Table III 同时给出了本库需要的"**架构单元的边际性价比**"
> 把 N 与 PESQ 对照，可以算出**双路径模块的边际收益急剧递减**：
> | 区间 | 参数增量 | MACs 增量 | PESQ 增量 | 边际 PESQ / 10M MACs |
> |---|---|---|---|---|
> | N: 0→1 | +11k | +17M | **+0.29** | **+0.171** |
> | N: 1→2 | +11k | +17M | **+0.10** | **+0.059** |
> | N: 2→3 | +11k | +16M | **−0.01** | **−0.006** |
> ⇒ **同一个模块的边际效率在 16M MACs 的尺度上衰减了 29 倍，并在第三层转为负。** 这是本库少见的、由**单篇论文自带的同架构扫描**支撑的收益递减曲线。

## 5. 这个方向还剩什么问题没解决？

### 5.1 论文自己承认的局限

- **ND 的收益依赖噪声比例**：「this (of LiSenNet+ND) **depends on the noise proportion**, ranging from 15M to 70M in MACs」——即**不保证任何场景下都省算力**。
- **ND 会引入性能损失**：「At the expense of a slight performance decay, which is caused by the **imprecision of noise detection** and the **information loss of clean regions**」。
- **GLA 迭代次数有上限收益**：k=2 饱和，但论文未讨论是否与幅度估计精度相关。

### 5.2 本库读出的隐藏问题（论文未承认）

| # | 问题 | 依据 | 严重性 |
|---|---|---|---|
| 1 | **全篇无任何"算法延迟"数字** | 通篇无 window−hop、无 $W/2$、无 look-ahead、无推导式；只有 hop = 256 @16 kHz = **16 ms 这一隐含下界** | **高**——本库约 2 ms 目标下差一个数量级 |
| 2 | **STFT 的 center 锚定未报告** | §III.A 只写 "Hanning window of length 512 (32ms) and hop size of 256 (16ms)"，**未说 `center=True/False`** | **高**——若 center=True，前端再含 $W/2$ = 16 ms 未来样本，"算法延迟"在 16 或 32 ms 之间双向不确定 |
| 3 | **因果性只有一句话** | 唯一依据是 §II.C 的 "we apply Bi-GRU for frequency modeling and unidirectional GRU for temporal modeling"；**无逐层 padding 说明、无 state certificate** | **中**——按本库第 1 条属"自称单向"，非"逐层可核验" |
| 4 | **GLA 的延迟与算力完全未入账** | GLA 需 **k=2 次 STFT+iSTFT 往返**（Eq. 4–5）；Table I/II 的 MACs 与 RTF **是否含 GLA 未说明** | **高**——这是本篇**最实质的账本缺口**：一个迭代式后处理被排除在效率指标之外 |
| 5 | **噪声检测器只降平均算力，不降尾延迟** | ND 是帧级判决、无状态跳过；最坏情况（全程有噪）MACs = **70M > 56M**（不加 ND） | **高**——与库内第 5 条判定口径直接冲突，论文零讨论 |
| 6 | **训练细节不足以复现** | 未报告：GPU 型号/数量、总训练 wall-clock、验证集划分、batch size、三类子带的具体频点划分、SP-Conv2d 的通道映射方式 | 中 |
| 7 | **单种子、无方差** | 全文无 ± 标准差、无随机种子数 | 中——影响 §4.3 的所有小差值 |

> [!question] 一个必须点出的**内部不一致：GLA 与"实时/因果"的关系**
> 论文把 GLA 用作**后处理相位精修**（Eq. 5），并在 Abstract 与 §I 反复强调 "for **real-time** applications"。
> 但 GLA 的本质是**对整段信号迭代**（`iSTFT` 后重新 `STFT`，依赖全序列的频谱一致性）——**它不是流式的**。
> 论文**从未说明 GLA 如何以流式方式实现**（逐帧近似？分块？还是离线整句？），也**未把它的开销计入 RTF**。
> ⇒ 本库判定：**GLA 是本篇"实时"声称中最薄弱的一环**。若按整句 GLA 实现，则模型的"实时"只在**离线评测**下成立。
> 这与 FastEnhancer 脚注 b 指出的 LiSenNet 版本问题（"**Not streamable because of input normalization and griffin-lim**"）**指向同一处**——**FastEnhancer 的作者独立地发现了这个流式性缺口**，而 LiSenNet 原文对此零说明。

## 6. 本论文在库中的位置关联（cross-reference matrix）

| 关系 | 库中论文/概念 | 关联与差异 |
|---|---|---|
| **前身/基石（最直接）** | **FSPEN（ICASSP 2024，[10]）** —— ⚠️ **库内暂无页面，见本节末注**；另见 [[wiki_low_latency/entities/GTCRN]] | 论文引言直接把 **FSPEN [10]** 列为"已有的轻量方案"，并把它的 **inter-frame path extension** 当作双路径架构的改进先例（引 DPRNN [11] 同段）。**本篇的主竞品与主要对照就是 FSPEN**——Table I 里唯一与它参数同档的对手（79k vs 37k）。注意本库目前**没有 FSPEN 页**，所有 FSPEN 数字均来自二手转述（本篇 Table I、FastEnhancer Table 2），**这正是 §4.1 那处 89M vs 64M 矛盾的根源** |
| **同分支竞品（超轻量锚点）** | [[wiki_low_latency/sources/2024/GTCRN 2024]]、[[wiki_low_latency/entities/GTCRN]] | 三者构成"超轻量三角"：GTCRN **23.7k/39.6 MMACs per second**、LiSenNet **37k/56M**、FSPEN **79k/89M**。GTCRN 用 **ERB 压缩**、LiSenNet 用 **子带 stride 差异化**、FSPEN 用 **全带+子带双编码器**。三条路线的参数量呈 1 : 1.56 : 3.33 的梯度 |
| **同分支竞品（被点名批评）** | [[wiki_low_latency/sources/2025/FastEnhancer 2025]]、[[wiki_low_latency/entities/FastEnhancer]] | FastEnhancer §2.2 **点名批评** BSRNN / **FSPEN** / GTCRN / **LiSenNet** 四个子带方案「increased architectural complexity and memory operations **paradoxically led to higher RTFs**」。而 FastEnhancer Table 2 的 LiSenNet^c RTF = **0.034**（Xeon）/ 0.028（M1），FSPEN^d = **0.046**/0.038。⇒ **本篇自报 RTF 0.028（Xeon E5-2620 v4）**，与 FastEnhancer 在 Xeon Gold 6248R 上测的 0.034 **同量级**——两篇的硬件不同（E5-2620 v4 是 2016 年 Haswell，Gold 6248R 是 2019 年 Cascade Lake），**不可直接比** |
| **「流式化代价」的直接教材** | [[wiki_low_latency/sources/2025/FastEnhancer 2025]] | FastEnhancer Table 2 的 **LiSenNet^b / LiSenNet^c 两行**是本库最干净的"非流式→流式"对照：^b 用官方训练代码（**因 input normalization 与 griffin-lim 而 not streamable**，故 RTF 未报）、^c 去掉这两项后重训（可流式）。**这两行的存在本身，就是对本篇 §3.4 GLA 流式性的外部质疑**——见 §5.2 的 `[!question]` |
| **概念上的共有机制** | [[wiki_low_latency/concepts/2107.05429-dual-path-recurrent-context]]、[[wiki_low_latency/sources/2021/DPCRN Low-Latency Direction 2021]] | 双路径循环（DPRNN/DPCRN 系）：本篇的 DPR 是同一范式的**极轻量变体**（hidden 24/12 维 + ConvGLU 补偿）。与 DPCRN 的差别是**把"砍 RNN 节点"明确当作设计前提再补通道混洗** |
| **损失函数的来源** | [[wiki_low_latency/sources/2025/PrimeK-Net 2025]]、[[wiki_low_latency/sources/2026/LaCo-SENet 2026]] | 本篇用 **PESQ 判别器损失**（Eq. 8，源自 MetricGAN [23]）；PrimeK-Net/LaCo-SENet 用的是 mag/pha/com/con/gan 五项加权。**两套体系不同**，但都属"用可微近似直接优化感知指标"这一支 |
| **跨分支类比（自适应计算）** | [[wiki_low_latency/sources/2022/Skip-DPCRN 2022]]、[[wiki_low_latency/sources/2024/D-GRU 2024]]、[[wiki_low_latency/sources/2026/Early Exit Compute-Matched 2026]] | 本篇的 **ND 是"输入相关动态算力"的第四种实现**：Skip-DPCRN 跳**整步状态**、D-GRU 跳**神经元**、Early Exit 跳**层**、**本篇跳的是"整帧是否进后端"**。四者的共同问题都是**只报平均、不报峰值**——本篇最极端（**峰值 70M > 无 ND 的 56M**） |
| **跨分支类比（相位精修）** | [[wiki_low_latency/sources/2020/DCCRN Low-Latency Direction 2020]]、[[wiki_low_latency/concepts/2008.00264-complex-phase-enhancement]] | DCCRN 走**复数域直接建模相位**；本篇走**幅度掩蔽 + GLA 迭代精修**。两条相位路线的延迟账本完全不同：复数域是单次前向，GLA 是**多次 STFT/iSTFT 往返** |

> [!warning] 库内针对本篇的**独立外部证据**（必须与原文并读）
> `FastEnhancer 2025` 对 LiSenNet 有 **6 处引用**，其中三处是**原文没有的信息**：
> ① **^b 不可流式的原因**：「Not streamable because of **input normalization and griffin-lim**」——**本篇原文从未说明 GLA 不可流式**；
> ② **重训后的数值**：^c（去掉 input normalization 与 griffin-lim）PESQ **2.98**、SCOREQ 0.335、SISDR 18.5、BAK 4.03、WER 3.4 —— **本篇原文只报 PESQ 3.07（VoiceBank+DEMAND）且无 SCOREQ/SISDR/WER/BAK 任何一项**；
> ③ **RTF 在另一套硬件上的值**：FastEnhancer 测 ^c 为 **0.034（Xeon Gold 6248R）** / 0.028（M1），本篇自报 0.028（Xeon E5-2620 v4）。
> **本库处置**：本篇 source 页只记**原文数字**；上述三条作为**外部独立证据**单独标注，**不混入本篇的表格**。两者的**评价指标集合都不同**（本篇 PESQ/STOI；FastEnhancer 加了 SCOREQ/SISDR/BAK/WER），**不可横向排名**。

> [!contradiction] 本篇与 FastEnhancer 对"LiSenNet 是哪一版"的指称不一致
> **本篇**：只有**一个模型**，PESQ **3.07**（VoiceBank+DEMAND，Table I），**无流式/非流式之分**。
> **FastEnhancer**：把 LiSenNet 分成 **^b（官方训练代码、不可流式）** 与 **^c（去 normalization+griffin-lim 后重训、可流式）** 两行，PESQ 分别 **3.08** 与 **2.98**。
> ⇒ **3.08 ≈ 3.07**（^b 对上了本篇的官方版本），而 **^c 的 2.98 是本篇从未报告的"流式化之后"的值**。
> **本库不判定谁对**：最可能的解释是 FastEnhancer 认为"官方训练代码产出的模型因 GLA/归一化而不可流式，故自定义了一个可流式子版本"——这与本篇把 GLA 当后处理、不讨论流式性是一致的。**按双方原文并列记录。**

> [!note] 库内引用本篇的页面（补摄后需回填 wikilink）
> - [[wiki_low_latency/sources/2025/FastEnhancer 2025]]：§2.2 批评段、Table 2 的 LiSenNet^b/^c 两行、脚注 ^b/^c 的定义、§4.3 基线与可比性、§4.4 的两条读法
> - [[wiki_low_latency/sources/2024/GTCRN 2024]]：§ 子带路线三方评价（"BSRNN / FSPEN / GTCRN / LiSenNet"）
> - [[wiki_low_latency/sources/2026/PSMSE 2026]]：§Related Work 把 LiSenNet 与 FSPEN/GTCRN/UL-UNAS 并列批评为 "performance tends to degrade due to the limited capacity of their simplified designs"
> - [[wiki_low_latency/concepts/gtcrn-2024-ultralight-subband-grouped-dprnn]]：子带路线被批评的证据链

## 7. 一句话总结"江湖地位"

```
2024 | 超轻量子带 SE | 用子带 stride 差异化 + ConvGLU 补偿把参数压到 37k 且 PESQ 反超 FSPEN（3.07 vs 2.97）
     → 成为"超轻量三角"中参数第二小的一档；被 FastEnhancer 点名批评并**替它补做了流式化改造**（^b→^c 代价：PESQ 3.08→2.98）；
       被 PSMSE 归入"容量受限"一组批评；是库内唯一**同时有原文与外部独立复训两套数字**的超轻量模型
```

## 参考资料

- 原件：`raw/papers/low_latency_causal_se/2409.13285.pdf`（**646,419 字节**，5 页；PDF 由 `pdfTeX-1.40.25` 生成）
- 抽取文本：`tmp/pdf_extract/lisennet.txt`（24,419 字符，含 `===== PAGE N =====` 分页标记）
- 页面渲染：`wiki_low_latency/assets/lisen-net_2024/lisen-page1..5.png`（150 dpi）
- 官方代码与样例音频：https://github.com/hyyan2k/LiSenNet
- arXiv 元数据：`Comments = "5 pages, submitted to 2025 IEEE International Conference on Acoustics, Speech, and Signal Processing (ICASSP 2025)"` ⇒ **投稿记录，非录用证据**
- **venue 结论**：`arXiv preprint (eess.AS)`，**无会议/期刊卷页**，**无第三方出版记录**（Semantic Scholar / Crossref 均无 ICASSP 2025 版本）⇒ 本库 **(c) 档纯预印本**

> [!warning] 本页的证据边界
> ① 本页**只记 arXiv:2409.13285v1 原文的数字**；FastEnhancer 对 LiSenNet 的复训值、PSMSE 的批评、GTCRN 的并列，均以 `[!warning]`/`[!contradiction]` 形式**单独标注**，不混入本篇表格。
> ② 所有"未报告"字段（算法延迟、STFT center、GLA 开销、峰值算力、训练硬件、随机种子）**一律记"未报告"，不做常识代填**。
> ③ 本篇的 **PESQ 3.07 与 FastEnhancer 的 ^c 2.98、^b 3.08 不可混用**——三者来自不同代码版本与不同训练配置。
