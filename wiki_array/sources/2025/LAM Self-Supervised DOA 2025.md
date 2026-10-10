---
title: LAM 2025 — 自监督潜在声学映射 DOA 估计
type: source
created: 2026-06-21
updated: 2026-09-15
tags:
  - doa-estimation
  - self-supervised
  - acoustic-mapping
  - autoencoder
  - spherical-acoustic-map
  - csm
  - cross-spectral-matrix
  - locata
  - starss
source_type: paper
year: 2025
authors:
  - Adrian S. Roman
  - Iran R. Roman
  - Juan P. Bello
affiliation: USC (A.S. Roman) / QMUL (I.R. Roman) / NYU (J.P. Bello)
venue: WASPAA 2025 (arXiv:2507.07066v1 [cs.SD], 8 Jul 2025)
arxiv: "2507.07066"
url: https://arxiv.org/abs/2507.07066
related:
  - [[wiki_array/concepts/DOA 波达方向估计]]
  - [[SSL Survey 2021]]
  - [[DeepWave Acoustic Imaging 2019]]
  - [[LOCATA Challenge 2019]]
  - [[SELD CRNN 2018]]
  - [[EINV2]]
  - [[FA-Stateformer 2025]]
  - [[GRAM Spatial Foundation Model 2025]]
  - [[MUSIC 算法]]
  - [[波束成形 Beamforming]]
---

# LAM — Latent Acoustic Mapping（自监督声学映射 DOA 估计）

> **Adrian S. Roman** (University of Southern California) · **Iran R. Roman** (QMUL) · **Juan P. Bello** (NYU) — WASPAA 2025 / arXiv:2507.07066v1 [cs.SD]（2025-07-08）。
> 原文：[arXiv:2507.07066](https://arxiv.org/abs/2507.07066)｜本地 PDF：[raw/articles/2507.07066.pdf](../../../raw/articles/2507.07066.pdf)｜代码：[adrianSRoman/LAM](https://github.com/adrianSRoman/LAM)
>
> **一句话：把"阵列协方差矩阵 → 高分辨率球面声学图"这条声学成像管线做成自监督 autoencoder——不要任何 DOA 标签，只靠"用固定 steering matrix 重建 CSM"这个物理先验当损失，就能学出可解释的高分辨率声学图，16K 参数反超有监督的 DeepWave / SELDnet / EINV2。**

```yaml
- 论文: LAM (Latent Acoustic Mapping) — 2025
  ├── 要解决什么问题: 传统声学成像(DAS 受衍射极限、MUSIC 需源数/不相关假设、压缩感知需迭代求解)与有监督深度学习(需昂贵标注、只学特定阵列、泛化差)都难以跨阵列/跨声学环境通用
  ├── 核心方法: 自监督 autoencoder：CSM → 可学习 back-projection encoder(映射为潜在 SAM) → 4 步去噪 → steering matrix 引导的 decoder 重建 CSM，用"重建 CSM"当自监督损失，全程无标签
  ├── 属于哪个分支: 自监督 DOA / 球面声学成像（DeepWave 支线的自监督升级版）
  ├── 输入/输出: 输入 CSM C∈C^{M×M}(32ch Eigenmike 或 4ch tetrahedral→上采样) / 输出高分辨率球面 SAM x^(4)；下游 DOA = 无监督 K-means(K=3) 或 GRU-MHSA→multi-ACCDOA
  ├── 关键trick: ①自监督 CSM 重建损失(steering 解码 = 物理先验)；②CDBPN 复数值上采样 4×4→32×32 适配低分辨率阵列；③4 步 1D 去噪卷积(kernel 3/5/7/9)+残差；④ℓ1 稀疏 + TV 平滑正则
  ├── 数据集: Eigenscape(真实 10h)+SpatialScaper 模拟(10h) 自监督训练；LOCATA + STARSS 评估
  ├── 对比了谁: MUSIC、DeepWave、SELDnet、EINV2（4 个基线）
  ├── 性能上限: LOCATA 32ch LAM→GRU-MHSA LE=13.41°(全榜最优)；STARSS 4ch UpLAM→GRU-MHSA LE=18.31°(†验证集扩充)
  ├── 参数量: 16K/频带（9 频带可能共享权重），远小于 SELDnet(0.51M)、EINV2(85M)
  ├── 消融关键发现: 本文无模块消融；最接近的两组：(a) 加监督 head 压 LE 但掉 LR(23.48→14.44° 但 LR 97.8→84.26，LOCATA 4ch)；(b) 验证集扩充实验证明是 GRU-MHSA 过拟合而非 UpLAM 缺陷(LR 57.6→64.6)
  ├── 遗留问题(你的机会): 没有"去掉去噪步/去掉 TV/去掉 CDBPN"的模块消融；4ch 下游 LR 短板；只有 9 个窄频带(1.5–4.5kHz)；K=3 固定源数；需已知阵列几何(P)；没给 RTF/MFLOPs
  └── 跟哪篇像: DeepWave(最像，监督→自监督)；GRAM Spatial Foundation Model(同年自监督空间，但 MAE 路线)；Beamformed 360 Sound Maps(声学图思路但监督)
```

## 一、研究任务与对象

| 维度 | 详情 |
|------|------|
| **任务** | DOA 估计 (Direction-of-Arrival Estimation, DoAE) + 声学成像 (acoustic imaging)，核心产物是球面声学图 SAM |
| **核心问题** | 传统方法受衍射极限 / 迭代求解 / 强模型假设拖累；有监督 DNN 需昂贵标注且只对特定阵列 + 有限声学环境有效 |
| **方法类型** | 自监督 autoencoder（denoising 结构）：CSM → encoder(可学习 back-projection) → 潜在 SAM → 去噪 → steering decoder 重建 CSM |
| **信号/特征域** | 频域（复数 STFT），基于交叉谱矩阵 CSM（Cross Spectral Matrix） |
| **阵列类型** | 主：32ch Eigenmike（球阵列）；兼容 4ch tetrahedral（通过 CDBPN 上采样） |
| **声源数** | 多声源（下游 K-means 固定 K=3，最多 3 个） |
| **声场假设** | 远场平面波（steering matrix `A = exp(−j·2π/λ₀·PᵀR)` 定义，见式 2） |
| **输出形式** | 潜在 SAM `x^(4)`（球面能量图，Fibonacci 网格）+ 重建 `Ĉ`；下游 = K-means 离散方向 或 GRU-MHSA → multi-ACCDOA 连续跟踪 |
| **数据集** | Eigenscape(真实 10h) + SpatialScaper 模拟(10h) 自监督训练；LOCATA(32ch) + STARSS(4ch) 评估 |
| **参数量** | **16K**（每频带 base model），对比 SELDnet ≈0.51M、EINV2 ≈85M |

## 二、整体架构

```
多通道音频 y (M ch, T 时长)
    │  STFT → Y(n,k) ∈ C^M
    ▼
交叉谱矩阵 CSM   C_k = (1/N) Σₙ Y(n,k) Y(n,k)^H ∈ C^{M×M}     (式1)
    │
    │  [UpLAM 分支] CDBPN 复数值上采样: C^{4×4} → C^{32×32}   (4ch → 32ch)
    ▼
Encoder / Back-projection（线性，可学习矩阵 B ∈ C^{M×N}）
    x^(0) = [B̄ ∘ B]^H vec(C) ∈ R^N                            (式3, Khatri-Rao 积)
      → "dirty image"（噪声 SAM，落在 Fibonacci 球面 tessellation 上）
    │
    ▼
4 步 Denoising（每步 1D 卷积，kernel 3→5→7→9；残差接 x^(0)；ReLU）
    x^(1) → x^(2) → x^(3) → x^(4)      （x^(4) = 干净的最优 SAM）
    │
    ▼
Decoder（steering matrix A 固定、非学习）
    Ĉ = A · diag(x^(4)) · A^H = (Ā ∘ A) x^(4)                 (式4)
    │
    ▼
重建 CSM Ĉ  vs  真值 C   →   自监督损失（无需任何 DOA 标签）
    L = MSE(C, Ĉ) + γ( ‖x^(4)‖₁ + Σ_{i,j∈Nᵢ}|x_i−x_j| )       (式6, ℓ1稀疏 + TV平滑)
    │
    ▼
─────────────  完成自监督预训练后，冻结 SAM 做下游 DOA  ─────────────
SAM x^(4)（9 个频带堆叠成 F×A×E 张量）
    ├── 无监督:  加权 K-means（K=3，取最亮 18 个像素，15° 内合并）→ 方向簇心
    └── 有监督:  GRU-MHSA（2×GRU + 2×MHSA）→ multi-ACCDOA → 逐帧活动+方向
```

### 为什么按这个管线搭？

1. **CSM 是复数域的标准"中间表示"**：压缩感知式声学成像都以 CSM + steering matrix 为起点（承袭射电天文/阵列信号处理的经典设定），所以 LAM 不需要回到原始波形，直接在这个物理量上做自监督。
2. **back-projection 是可学习化了的传统投影**：`x^(0)` 本质是"dirty image"（噪声 SAM），物理上等于把阵列快照反投影到空间网格；这里把投影矩阵 `B` 变成可学习参数，但结构仍是线性的——保留了可解释性。
3. **denoising 是"从 dirty 到 clean"的深度学习版 CLEAN**：4 步 1D 卷积渐进增大感受野（3/5/7/9），残差连接保底，输出干净的 `x^(4)`——对应传统方法里的迭代去卷积过程，但用前馈网络一次做完。
4. **decoder 用 fixed steering matrix**：`A` 是阵列几何决定的已知矩阵（不是学习的），`Ĉ = A diag(x) A^H` 的物理含义是"把球面能量图按 steering 向量展开成通道协方差"，从而把 SAM 的内容直接约束在"能解释观测 CSM"这件事上。

> [!note] 术语对照
> - **CSM**（Cross Spectral Matrix，交叉谱矩阵）：各麦克风通道间的空间协方差，DOA 信息的载体。
> - **SAM**（Spherical Acoustic Map，球面声学映射）：把空间能量投到球面方向网格上的"热力图"，即声学成像的输出。
> - **steering matrix**（导向矩阵）：预先把阵列相位差按方向编码好的矩阵，DOA 扫描/波束成形的核心。

## 三、为什么这么做？（Motivation）

1. **传统声学成像三难全**：DAS 高效可解释但受衍射极限（阵列尺寸/波长决定角分辨率），低频或紧凑阵列下方向模糊；MUSIC 超分辨但要"源数已知 + 源不相关"的假设，噪声下鲁棒性差；压缩感知（DAMAS / PGD 变体）分辨率高但要迭代求解、收敛慢——所以现场声学相机至今死守 DAS。
2. **DeepWave 开了口子但留了个天花板**：DeepWave(2019) 用图卷积 + 递归网络前馈生成高分辨率 SAM，证明了"深度声学成像"可行；但它的真值是压缩感知迭代器生成的标签，等于把自己性能钉死在"迭代器能解到什么程度"上，且是有监督、怕过拟合。
3. **有监督 SELD 泛化差**：SELDnet/EINV2 在 LOCATA/STARSS 上强，但它们针对特定阵列和有限声学环境优化，标注又贵，换阵列/换环境就得重来。
4. **本文的赌注**：既然"用 steering matrix 从 SAM 重建 CSM"是一个**物理恒等式**（不依赖标签），那就拿它当自监督信号——让网络学出的 SAM 必须能解释观测 CSM，等于把"物理可解释性 + 深度学习的前馈高效 + 无标注可扩展"三者缝在一起。

## 四、之前的人怎么做不了？（Limitation → Gap）

| 方法 | 能做 | 不能做 |
|------|------|--------|
| DAS 波束成形 | 高效、可解释、无标签 | 角分辨率受衍射极限限制，低频/小阵列方向粗 |
| MUSIC | 超分辨（突破衍射极限） | 需源数先验、要求源不相关、噪声下鲁棒性差 |
| DAMAS / PGD（压缩感知） | 高保真、稀疏先验 | 迭代求解收敛慢，实时代价高 |
| DeepWave（有监督声学成像） | 前馈快、图卷积生成高分辨率 SAM | 依赖压缩感知生成的真值标签 → 有性能天花板；有监督易过拟合 |
| SELDnet / EINV2（有监督 SELD） | 在基准上 DoAE 精度高 | 需昂贵标注；只对特定阵列/环境优化，泛化差 |
| **LAM（本文）** | **纯自监督、无标注、前馈、16K 参数、跨 32ch/4ch 阵列** | **下游 LR 在域漂移下仍掉；只验证到 3 源；仅 9 窄频带** |

> 一句话 gap 定位：**DeepWave 证明了"深度学习能前馈生成高分辨率声学图"，但它的标签来自迭代器 → 天花板 + 标注成本。LAM 的 gap 突破 = 把那个迭代器产生的标签换成"CSM 重建"这个自监督信号。**

## 五、核心 trick：一个 idea + 三个工程件

**这篇论文只有 1 个核心 idea**：把声学成像的"编码—去噪—解码"整条管线做成**自监督 autoencoder**，用 `Ĉ = A diag(x) A^H` 的物理结构当 decoder，从而让"重建 CSM"成为不需要标签的训练目标。

```
配三个工程件（缺一不可的组合）:
  ✓ 自监督 CSM 重建损失（式5/式6）——本质是压缩感知里"协方差矩阵拟合"的老公式，被拿来当 pre-text task
  ✓ CDBPN 复数值上采样（4×4 → 32×32）——让低分辨率的 4ch tetrahedral 也能喂进 32ch 模型
  ✓ 4 步 denoising 卷积（kernel 3/5/7/9 + 残差 + ReLU）——"dirty image → clean SAM"的前馈版去卷积
```

细节逐个说清：

1. **式 3（back-projection encoder）**：`x^(0) = [B̄ ∘ B]^H vec(C)`，其中 `B` 是**可学习**的 `C^{M×N}` 矩阵，`∘` 是 Khatri-Rao 积（列向 Kronecker 积），`vec` 展平 `C^{M×M} → C^{M²}`。合起来是先做一次空间投影，把 `M²` 维的复数协方差压缩到 `N` 维实数球面网格（N = Fibonacci tessellation 方向数）。`x^(0)` 就是"dirty image"——传统声学成像里反投影得到的带噪声 SAM。
2. **去噪块**：`x^(0)` 之后接 4 步 1D 卷积，kernel 从 3→5→7→9 递增（越大感受野=在球面网格上"看得越宽"），每步带残差连接（接回 `x^(0)`）和 ReLU。这一步是 DeepWave 图卷积 + DnCNN 残差去噪思想的合体；但注意这里是**1D 卷积（沿球面方向维度）**，不是严格意义上的图卷积（这点和 DeepWave 不同）。

   > [!note] 勘误：不是"积分图卷积"
   > 任务草稿里"积分图卷积"这个短语与 PDF 不符。PDF 原文是："inspired by the **graph convolutions** from DeepWave... applying **denoising 1D convolutions** (kernel 3,5,7,9)"。即灵感来自 DeepWave 的图卷积，但 LAM 实际用的是去噪 1D 卷积，没有"积分图 (integral image)"概念。建议以"图卷积启发的去噪 1D 卷积"为准。

3. **式 4（steering decoder）**：`Ĉ = A diag(x^(4)) A^H = (Ā ∘ A) x^(4)`，`A` 是**固定已知**的 steering matrix（式 2：`A = exp(−j·2π/λ₀·PᵀR)`，由麦克风坐标 `P`、球面网格 `R`、波长 `λ₀` 决定）。`diag(x^(4))` 把 SAM 的每个网格能量当成一个"假想源"的功率，`A diag(x) A^H` = 所有方向 steering 外积按能量加权求和 = 重建的协方差。**这就是 trick 的灵魂：decoder 不学，直接用物理。**

4. **式 6（损失）**：`L = MSE(C, Ĉ) + γ(‖x^(4)‖₁ + Σ_{i,j∈Nᵢ}|xᵢ−xⱼ|)`，三项 = (a) CSM 重建 MSE；(b) ℓ1 稀疏（让 SAM 只有少数方向有能量）；(c) TV 平滑（邻近方向能量相近，鼓励"一个源扩散得平滑"而非点状噪声）。`γ = 1e-4`。

> [!question] 存疑：γ 是否同时乘 TV 项
> PDF 正文说三部分：(a) 重建损失、(b) "dispersion term" 用 ℓ1、由 `γ>0` 控制、(c) 单独的 TV 正则。但式 6 的排版把 `γ(‖x‖₁ + Σ...)` 写成 TV 也在 γ 的括号内。二者不一致，需查原 PDF 排版确认。

**一句话：这篇不是叠了十个 trick，是"一个自监督 idea（CSM 重建）+ 三个必要工程件（可学习 back-projection、CDBPN、去噪卷积）"。**

## 六、实验里哪个消融最关键？

> [!warning] 注意：本文**没有**传统意义的模块消融表
> 全文没有"去掉去噪步 / 去掉 TV / 去掉 CDBPN"的对照实验，所以"哪个 trick 最关键"无法从论文内部直接回答。下面用最接近消融的两组实验 + 我读出的缺口来替代。

### 最接近消融的实验 1：无监督 head vs 加监督 head（K-means vs GRU-MHSA）

LOCATA 4ch 上对比（Table 1）：

```
UpLAM→K-means      （纯无监督读出）:  LE 23.48°  LR 97.8
UpLAM→GRU-MHSA     （SAM + 监督 head）: LE 14.44°  LR 84.26   ← LE 大降，LR 反掉
```

→ 加一个监督 head 能把定位误差再打掉 9°，说明 SAM 里的信息是"够用且富余"的；但 LR 掉 13.5 个点，说明 **读出的覆盖率是个问题**——监督 head 变"挑剔"了。

### 最接近消融的实验 2：域漂移排除（验证集扩充，Table 2 的 † 行）

STARSS 上 UpLAM→GRU-MHSA 的 LR 偏低（57.6），作者怀疑是 dataset 太小 + 域漂移。于是把 LOCATA + RSoANU 塞进验证集再训（**全程冻结 UpLAM，只训 GRU-MHSA**）：

```
STARSS dev-test-sony, 4ch:
  UpLAM→GRU-MHSA       :  LE 18.65°  LR 57.6
  UpLAM→GRU-MHSA†      :  LE 18.31°  LR 64.6    ← LR 回升 7 个点
  对照 SELDnet → SELDnet†: LE 20.8°  LR 66.4     ← 对照几乎不动
```

→ 这是全文**最关键的因果证据**：冻结 UpLAM 只改监督 head，LR 就从 57.6 涨到 64.6。作者据此断言"**是 GRU-MHSA 过拟合了，UpLAM 的 SAM 本身包含足够信息**"。这也反向证明了自监督部分的鲁棒性。

### 我读出的关键消融缺口（本文没做，是你的机会）

```
✗ 去掉 4 步去噪（只用 x^(0) 当 SAM）→ LE 掉多少？    ← 最该做的消融，没做
✗ 去掉 TV / ℓ1 正则 → 稀疏性对可解释性/精度各贡献多少？ ← 没做
✗ 拿掉 CDBPN 直接训练 4ch 模型 vs 上采样到 32ch → 上采样到底值多少？ ← 没做
✗ B 可学习 vs B = 固定 steering back-projection → 可学习投影值多少？ ← 没做
```

→ 如果这些消融存在，"哪个 trick 最关键"才有答案。目前只能推论：**自监督 CSM 重建损失是灵魂（没了它整个任务不成立），去噪块和 CDBPN 是"增益件"（量级未知）。**

## 七、整体结果

### LOCATA（Table 1，32ch 与 4ch 分列）

| 输入 | 模型 | LE ↓ (°) | LR ↑ |
|------|------|:------:|:----:|
| 32ch | MUSIC → K-means | 56.95 | 97.2 |
| 32ch | DeepWave → K-means | 14.8 | 99.20 |
| 32ch | **LAM → K-means**（纯自监督） | **13.69** | 94.0 |
| 32ch | **LAM → GRU-MHSA**（自监督+监督head） | **13.41** | 94.7 |
| 4ch | MUSIC → K-means | 61.83 | 94.4 |
| 4ch | DeepWave → K-means | 27.10 | 99.20 |
| 4ch | **UpLAM → K-means** | **23.48** | 97.8 |
| 4ch | **UpLAM → GRU-MHSA** | **14.44** | 84.26 |
| 4ch | SELDnet | 16.8 | 77.96 |
| FOA | SELDnet | 22.43 | 80.7 |
| FOA+4ch | EINV2 | 19.83 | 80.6 |

### STARSS "dev-test-sony"（Table 2）

| 模型 | 输入 | LE ↓ (°) | LR ↑ |
|------|------|:------:|:----:|
| MUSIC → GRU-MHSA | 4ch | 39.9 | 73.5 |
| DeepWave → GRU | 4ch | 20.5 | 70.1 |
| **UpLAM → GRU-MHSA** | 4ch | **18.65** | 57.6 |
| SELDnet | 4ch | 23.3 | 82.3 |
| SELDnet | FOA | 21.9 | 83.0 |
| EINV2 | FOA+4ch | 24.0 | 84.2 |
| **UpLAM → GRU-MHSA†** | 4ch | 18.31 | 64.6 |
| SELDnet† | 4ch | 20.8 | 66.4 |

（† = 验证集额外加入 LOCATA + RSoANU）

### 关键结论（逐条落实，无"以原文为准"）

1. **碾压传统方法**：LAM 相对 MUSIC 的 LE 一致降 40° 上下——32ch 上 56.95° → 13.69°（−43.3°）；4ch 上 61.83° → 14.44°（−47.4°，取 UpLAM→GRU-MHSA）。这直接兑现"不做强假设、不加迭代求解"的收益。
2. **纯自监督就够打平 DeepWave**：32ch 上 `LAM→K-means`（13.69°, 94.0）几乎追平有监督 DeepWave→K-means（14.8°, 99.20），而且 LAM 一点标签都没用——这是全文最亮的一句话。
3. **加监督 head 后反超所有有监督模型**：LOCATA 上 `UpLAM→GRU-MHSA`（LE 14.44°）同时优于 SELDnet(4ch 16.8° / FOA 22.43°) 和 EINV2(19.83°)；STARSS 上 LE 18.65° 同样是全榜最低。
4. **AR 指标 LR 是软肋**：4ch 的 UpLAM 在 LR 上掉队（STARSS 57.6 vs SELDnet-FOA 83.0），原因是 GRU-MHSA head 在 STARSS 小数据集上过拟合/域漂移，而非 SAM 本身信息不足（见第六节的 † 实验）。
5. **16K 参数 vs 百万级**：base model 每频带仅 16K，结论明说"显著少于百万级参数的 SELD DNN"，适合边缘端实时部署。

> [!note] 关于指标
> LE（Localization Error）= 每个检出事件的预测方向与真值方向的角误差（度，越低越好）；LR（Localization Recall）= 被成功定位的事件占总标注事件的比例（越高越好）。表中 LR 数值为 0–100 的百分数量级。

## 八、还剩什么问题没解决？

**论文自己承认的局限：**

1. 只做了 DOA / 声学成像，future work 是声事件分类、天线阵列等其它信号处理域。
2. 下游 LR 在域漂移下掉——作者也点出 GRU-MHSA head 因 STARSS 太小而过拟合。

**我读出来的隐藏问题（你的机会）：**

1. **完全没有模块消融**——去噪步数、TV、ℓ1、CDBPN、可学习 `B` 的各自贡献不可知，论文里"哪个 trick 最值钱"无法回答。
2. **只用了 9 个窄频带（1.5–4.5 kHz）**：贴着语音主能量带，低频方向性（DAS/MUSIC 也犯难的频段）和高频宽带信息都丢了，宽带/全频一步步退环境没验证。
3. **K=3 硬编码源数**：K-means 聚类数固定，遇到 >3 个声源或 0 声源场景无法自适应；这跟传统方法"要源数先验"的毛病没彻底脱钩。
4. **依赖已知阵列几何**：steering matrix `A` 需要麦克风坐标 `P`，对任意 ad-hoc / 未知几何阵列无法直接迁移（CDBPN 只是换分辨率，不是换几何）。
5. **4ch 上游要和 32ch 对齐靠通道子采样**（取 Eigenmike 的 6/10/22/26 四个 channel），这种"模拟 tetrahedral"和真实 4ch 硬件（如 STARSS 的 mic 布局）之间的 gap 没有量化。
6. **没测实时性/算力**：只强调 16K 参数，没给 RTF、MFLOPs、端侧实测。
7. **可解释性只到"S AM 是能量图"**：没有对"去噪后的 SAM 相比 dirty image 到底修正了什么"做可视化归因（除了 Fig.1 的三张样例图）。

## 九、跟哪篇像

**直接继承（最像）**:
- [[DeepWave Acoustic Imaging 2019]] → 同一支线：图卷积递归网络前馈生成高分辨率 SAM。LAM 把它的"有监督压缩感知标签"替换为"自监督 CSM 重建"，是这个支线的自监督升级版。
- （库外）Roman et al. 2024 "Robust DOA from deep acoustic imaging"（本文作者的 ICASSP 2024）→ 提了 CDBPN 复数值上采样 + K-means-on-SAM 的整套下游流程，LAM 是它去掉标签的前传。

**同思路（声学图 / 空间图复原）**:
- [[Beamformed 360 Sound Maps 2025]]、[[Mechanical Fault SSL 2024]]、[[SSLIDE 2021]] → 都把"声学能量图"当中间表示，差别在监督 vs 自监督、图生成方式（DAS / SRP-PHAT / likelihood vs CSM 重建）。
- [[Icosahedral CNN DOA 2023]] → 球面离散化（icosahedral vs Fibonacci tessellation）是同族几何思路。

**自监督路线（跨分支）**:
- [[GRAM Spatial Foundation Model 2025]] → 同年自监督空间学习，但走 MAE 掩码预训练路线；LAM 走物理约束（CSM 重建）路线。
- [[CLIP Audio-Visual SSL 2025]] → 异源自监督（视听对齐）做定位，与纯音频自监督互补。

```
声学成像/声学图 演进:
DAS/MUSIC/压缩感知（传统）→ DeepWave(2019, 有监督图卷积) → [作者 ICASSP2024, CDBPN+K-means] → LAM(2025, 自监督 CSM 重建)
                                                                        ↓ 并行
                                                              GRAM(2025, MAE 自监督空间基础模型)
```

### 6. 本论文在库中的位置关联

| 维度 | 论文 | 关系 |
|------|------|------|
| **前身/基石** | [[DeepWave Acoustic Imaging 2019]] | 直接继承：图卷积递归网络前馈生成高分辨率 SAM；LAM 把"有监督压缩感知标签"换成"自监督 CSM 重建"→ 去掉性能天花板 |
| **前身/基石** | （库外）Robust DOA from Deep Acoustic Imaging (Roman et al., ICASSP 2024) | 本文作者自己的前作，贡献 CDBPN 复数值上采样 + K-means-on-SAM 流程。⚠️ 库内无此页，建议新建 |
| **前身/基石** | [[LOCATA Challenge 2019]] | 评估基准 + DAS/MUSIC 传统基线来源 |
| **前身/基石** | [[SSL Survey 2021]] | 自监督 SSL 方向综述背景 |
| **后续/扩展** | （暂无） | WASPAA 2025 太新；future work = 声事件分类 / 天线阵列。⚠️ 疑似无后续，需用户确认 |
| **同分支竞品** | [[SELD CRNN 2018]]（SELDnet） | 本文用其当监督 baseline 直接碾压（LOCATA 4ch：LE 16.8° vs 14.44°；但 STARSS 上 UpLAM 的 LR 落后）|
| **同分支竞品** | [[EINV2]] | 监督重模型 baseline（85M），被 UpLAM→GRU-MHSA 在 LE 上超越 |
| **同分支竞品** | [[FA-Stateformer 2025]] | 同年纯 DOA，有监督 Mamba+SA 协同；LAM 自监督——"泛化 vs 精度"的路线之争 |
| **跨分支类比** | [[GRAM Spatial Foundation Model 2025]] | 同年自监督空间：LAM 物理约束(CSM 重建) vs GRAM 数据约束(MAE)，两种自监督路线可互鉴 |
| **跨分支类比** | [[Beamformed 360 Sound Maps 2025]] | 都用"声学图"表示，但后者 DAS 图 + U-Net 分割(有监督)；LAM 自监督 |
| **跨分支类比** | [[Icosahedral CNN DOA 2023]] | 球面几何 DOA 同族：icosahedral vs Fibonacci tessellation 的离散化选择 |
| **跨分支类比** | [[CLIP Audio-Visual SSL 2025]] | 异源自监督定位（视听）vs 纯音频自监督，可组多模态自监督 |

### 7. 江湖地位

```
2025 | 纯 DOA / 声学成像 | 自监督 CSM 重建生成高分辨率 SAM，16K 参数 → LE 反超 MUSIC(降~40°)、DeepWave、SELDnet、EINV2
          → 建立在 DeepWave(2019) 声学成像管线之上，用自监督(物理 decoder)替换有监督标签，去掉性能天花板
          → 与 GRAM(2025) 共同标志 DOA 方向的"自监督化"；是 DeepWave 支线的下一棒
          → 把声学成像从"传统 DSP vs 有监督 DL"的二选一，改写为"物理先验当损失"的第三条路
```

---

*LAM 是整个库里第一张真正"零标签做 DOA"的牌：它没有发明新网络结构，而是发现"用固定 steering matrix 从声学图重建 CSM"这个物理恒等式本身就能当训练信号。代价是——它极其依赖已知阵列几何、只覆盖 9 个窄频带、下游召回率在域漂移下仍会掉。理解 LAM 的价值，不在于它 13° 的定位误差，而在于它证明了"从原始多通道音频到可解释空间图"这件事可以不用一张标注就学会。*