---
title: Robust Sound Source Tracking Using SRP-PHAT and 3D Convolutional Neural Networks
type: source
created: 2026-09-15
updated: 2026-09-15
tags:
  - doa-estimation
  - sound-source-tracking
  - srp-phat
  - 3d-cnn
  - causal-cnn
  - cross3d
  - locata
  - tracking
  - regression
  - real-time
  - single-source
source_type: paper
year: 2021
authors:
  - David Diaz-Guerra
  - Antonio Miguel
  - Jose R. Beltran
affiliation: University of Zaragoza, Spain
venue: IEEE/ACM Transactions on Audio, Speech, and Language Processing
arxiv: "2006.09006"
url: https://arxiv.org/abs/2006.09006
doi: 10.1109/TASLP.2020.3040031
related:
  - "[[SRP-PHAT]]"
  - "[[GCC-PHAT 广义互相关]]"
  - "[[DOA 波达方向估计]]"
  - "[[LOCATA Challenge 2019]]"
  - "[[SSLIDE 2021]]"
  - "[[Icosahedral CNN DOA 2023]]"
  - "[[DeepWave Acoustic Imaging 2019]]"
  - "[[SELD CRNN 2018]]"
  - "[[Direct-Path Dominance Test 2020]]"
  - "[[Mechanical Fault SSL 2024]]"
  - "[[CNN DOA Estimation with Noise Training 2017]]"
  - "[[Multi-Speaker CNN DOA 2018]]"
---

# Cross3D — 用 SRP-PHAT 时序功率图 + 因果 3D CNN 做单声源稳健跟踪

> David Diaz-Guerra, Antonio Miguel, Jose R. Beltran (University of Zaragoza). IEEE/ACM Transactions on Audio, Speech, and Language Processing, 2021. [arXiv:2006.09006](https://arxiv.org/abs/2006.09006) · DOI: 10.1109/TASLP.2020.3040031 · 本地 PDF：[raw/articles/2006.09006.pdf](../../../raw/articles/2006.09006.pdf) · 代码：[DavidDiazGuerra/Cross3D](https://github.com/DavidDiazGuerra/Cross3D)

```yaml
- 论文: Cross3D (SRP-PHAT 时序功率图 + 因果 3D CNN) — 2021
  ├── 要解决什么问题: 单声源 DOA 估计+跟踪在强混响/低信噪比下不稳；DNN 方法普遍用双向 RNN（非因果），实时不可行
  ├── 核心方法: SRP-PHAT 每帧生成 2D 球面功率图，拼成"时间×仰角×方位角"三维体，用全因果 3D CNN（含注入每图 argmax 坐标的额外通道）做时间维度上的端到端跟踪
  ├── 属于哪个分支: 声源定位与跟踪的"空间图 + 学习式时空建模"路线（DSP 前端 + 3D CNN 后端）
  ├── 输入/输出: 输入 (C=3, T, Nφ, Nθ) 张量（SRP-PHAT 图 + 仰角/方位角最大值坐标两通道）/ 输出 3×T 单位向量 XYZ 坐标（回归，非分类网格）
  ├── 关键trick: ① 用物理空间图而非谱做输入（对混响噪声鲁棒）② 全因果卷积（无双向 RNN，实时）③ 双分支"垂直方向各池化"的 Cross3D 结构（保留位置信息）④ 把每图 argmax 坐标作为额外输入通道显式喂给网络 ⑤ 训练时在线生成随机轨迹 = 无限数据集 ⑥ VAD 静音帧置零避免跟踪定向噪声 ⑦ 笛卡尔 XYZ 回归
  ├── 数据集: 全模拟（LibriSpeech 语音 + gpuRIR 房间冲激响应，T60∈[0.2,1.3]s，SNR∈[5,30]dB，随机轨迹）；实采测试用 LOCATA Task 1/3/5
  ├── 对比了谁: 经典 SRP-PHAT 取最大值、1D CNN over GCCs、1D CNN over 图最大值坐标、2D CNN over 谱、SELDnet（复现 DOA-only）
  ├── 性能上限: LOCATA 总平均 RMSAE 7.96°（64×128 图）；静止源 Task1 可到 3.77°；模拟 T60=1.5s 时仅退化约 5° 而 SRP-PHAT 直接失效
  ├── 参数量: Cross3D 0.53M(4×8)~21.35M(64×128)；常用 32×64=5.63M；baseline 1D CNN(GCC) 11.28M / 2D CNN 1.88M / SELDnet 0.10M
  ├── 消融关键发现: 输入用"全图"远优于只喂"图最大值坐标"（1D CNN over 64×128 最大值 < 3D CNN over 4×8 全图）；谱输入模型在混响噪声下崩（LOCATA 2D CNN 78.01°、SELDnet 50.94°）；每帧 192ms 出新 DOA 且全因果即可达 SOTA
  ├── 遗留问题(你的机会): 只做单声源（多声源要靠源消除迭代，仅是"思路"）；换阵列需重训；机器人头散射未建模；无距离/3D 位置估计；低分辨率图需 45°×60° 粗网格
  └── 跟哪篇像: [[DeepWave Acoustic Imaging 2019]]（声学成像+递归）、[[SSLIDE 2021]]（空间 likelihood 图）、[[Icosahedral CNN DOA 2023]]（球面 SRP-PHAT 图，补旋转等变）——同属"空间图→DNN"分支
```

## 一、研究任务与对象

| 维度                | 详情                                                                                                |
| ----------------- | ------------------------------------------------------------------------------------------------- |
| **任务**            | 单声源（single source）DOA 估计 + 跟踪（tracking），假设"始终有一个活动声源"                                             |
| **核心问题**          | SRP-PHAT 功率图在混响/低 SNR 下出现大量局部极大（Fig.2），仅取每帧最大值会错判；且逐帧独立估计不稳定，需要时序跟踪                               |
| **方法类型**          | SRP-PHAT 前端（物理空间图）→ 全因果 3D CNN（时间×仰角×方位角三维卷积）后端                                                   |
| **阵列类型**          | 紧凑阵列（compact array），12 麦克风装在 NAO 机器人头上（LOCATA 数据集的阵列），最小/最大阵元间距 1.3cm / 12.1cm；**任意几何可用，但换阵列需重训** |
| **声场假设**          | 方向估计（输出单位向量，不做距离/位置估计），等同远场方向扫描；源在室内可移动                                                           |
| **输出格式**          | **回归**（3D 笛卡尔单位向量 XYZ），非分类网格；每 192ms 出一个新 DOA                                                     |
| **采样率**           | fs = 16 kHz（LibriSpeech）                                                                          |
| **窗口**            | Hanning 窗 K=4096 样本（256ms），hop = 3K/4 = 192ms                                                     |
| **SRP-PHAT 图分辨率** | 多档实验：4×8 / 8×16 / 16×32 / 32×64 / 64×128（仰角 φ × 方位角 θ）                                            |
| **参数量**           | Cross3D 从 0.53M（4×8）到 21.35M（64×128）                                                              |

> **先看一个对照。** Fig.1 是高 SNR、低混响时的 SRP-PHAT 功率图：最大值（黑点）基本贴近真实 DOA（红点）。Fig.2 则展示了低 SNR、强混响下的多个局部极大，正是本文需要用时序模型解决的问题。

![[语音定位+语音增强/wiki_array/assets/Cross3D-Fig1-SRP-PHAT-favorable-scenario.png]]

> **Fig. 1.** 有利场景（SNR=30 dB，$T_{60}=0.3$ s）：不同分辨率下的 SRP-PHAT 功率图。

![[语音定位+语音增强/wiki_array/assets/Cross3D-Fig2-SRP-PHAT-adverse-scenario.png]]

> **Fig. 2.** 不利场景（SNR=5 dB，$T_{60}=0.9$ s）：不同分辨率下的 SRP-PHAT 功率图；红点为真实 DOA，黑点为功率图最大值。

## 二、整体架构

```
多通道音频 (12 麦克风, NAO 机器人头, fs=16kHz)
    │
    ▼
分帧加窗 (Hanning, K=4096=256ms, hop 3K/4=192ms)
    │
    ▼
GCC-PHAT 广义互相关 → SRP-PHAT 求和 (式(4))
    │  每帧生成一张 2D 球面功率图 (Nφ 仰角 ∈[0,π] × Nθ 方位角 ∈[-π,π))
    │  减去均值 / 除以最大值 → 归一化到 [-1,1]
    ▼
拼接 T 帧时序图 → 输入张量 (C=3, T, Nφ, Nθ)
    ├─ 通道1: SRP-PHAT 功率图本身
    ├─ 通道2: 各图 argmax 的仰角坐标 φ̂ (归一化 [0,1])
    └─ 通道3: 各图 argmax 的方位角坐标 θ̂ (归一化 [0,1])
    │
    ▼
3D 因果卷积 (32 核, 5×5×5, PReLU)  ← 时间轴全因果
    │
    ├──────────────── 双分支 (Cross) ─────────────────┐
    ▼                                                 ▼
分支 A: 4×(conv5×3×3+PReLU+1×1×2 maxpool)    分支 B: 4×(conv5×3×3+PReLU+1×2×1 maxpool)
  只在 θ 方位角方向下采样(保留仰角位置)            只在 φ 仰角方向下采样(保留方位角位置)
    │                                                 │
    └──────────────── 拼接 + reshape + transpose ─────┘
    │
    ▼
1D 因果卷积 (128 ch, kernel 5, dilation 2, PReLU)
    │
    ▼
1D 因果卷积 (3 ch, kernel 5, dilation 2, tanh)
    │
    ▼
输出: 3×T 单位向量 XYZ 坐标 → 每帧一个 DOA (每 192ms 一个新估计)
```

![[figures/cross3d-pipeline.png]]

> **方法总览图。** Cross3D 不把每帧功率图压缩成一个峰值，而是保留空间图序列，并用因果 3D CNN 同时利用空间结构与历史帧。

### 关键设计说明

1. **模型名 Cross3D 的由来**：3D 卷积后拆成**两个互相垂直的分支**，一个只在方位角 θ 维度做 1×1×2 池化、另一个只在仰角 φ 维度做 1×2×1 池化。这样每个分支保留另一个坐标的位置信息，池化的"降参数、增泛化"收益和"保留位置信息"需求兼得。

![[figures/cross3d-cross-branch.png]]

> **Cross3D 的直觉。** 两条分支分别保留仰角和方位角的位置线索，最后再融合；因此它不像普通池化那样把空间位置一并抹掉。

2. **注入 argmax 坐标作为输入通道**：argmax 高度非线性且不可微，网络很难自己学；作者把每张图最大值位置的归一化 (φ̂, θ̂) 作为第 2、3 通道拼进输入，让第一层卷积就能"看到"峰值位置。这是**条件化 CNN 输出**的最简做法。
3. **全因果**：3D 卷积 + 1D 卷积在时间轴全部用因果卷积，无任何双向 RNN → 实时可行，每来一张新图就出一个新 DOA。
4. **时间感受野**：最后两级 1D 因果卷积用 dilation 2 扩大感受野而不增参数；每个 DOA 估计依赖最近 **37 张 SRP-PHAT 图（≈7.17s 跟踪记忆）**。
5. **笛卡尔回归优于球面回归**：输出 XYZ 单位向量，避免角度 ±180° 环绕不连续（与 [22][38][39] 结论一致）。

## 三、为什么这么做？（Motivation）

1. **SRP-PHAT 是鲁棒性和计算效率的折中**，但存在两个顽疾：① 混响/低 SNR 下功率图出现多个局部极大，最大值可能不是真 DOA（Fig.2）；② 语音等非平稳信号需要额外的**跟踪阶段**（传统用 Kalman/粒子滤波）。
2. **传统两步法（先估计后跟踪）有信息损失**：只在"取最大值"这一步就已经丢掉了整张图的其余信息——比如某个次极大其实离上一帧估计更近，或者某帧的峰特别"宽"（源弱）应该降权。把这些信息塞进传统跟踪会让复杂度暴增。
3. **谱输入 DNN 对混响噪声不鲁棒**：大量 SOTA 用幅度/相位谱做输入，在好场景还行，但在强混响+低 SNR 下崩（本文 Table II 里 2D CNN 达 78°，SELDnet 达 51°）。
4. **双向 RNN 让系统不可实时**：很多 CNN 架构在尾部加双向 GRU/RNN，本质上是"偷看未来"，无法流式部署。
5. **带标签的移动声源实测数据几乎拿不到** → 需要一种能"无限续杯"的训练数据方案。

## 四、之前的人怎么做不了？（Limitation → Gap）

| 方法 | 能做 | 不能做 |
|------|------|--------|
| SRP-PHAT + Kalman/粒子滤波 | 单源跟踪 | 两步法，只用每帧最大值，丢整图信息；强混响下 SRP-PHAT 本身失效 |
| GCC 特征 + MLP（早期 DNN） | 逐帧 DOA 分类 | 输出 1°/类的分类头对 2D/3D 方向不可扩展；不做跟踪 |
| 谱相位图 + 2D CNN（Chakrabarty 路线） | 多声源/单声源 DOA | 对频率平移等变无物理意义；不做时序跟踪 |
| 谱 + CNN + 双向 GRU（SELDnet 等） | SED+DOA 联合 | 双向 GRU 非因果，实时不可行；强混响噪声下不鲁棒 |
| **Cross3D（本文）** | **全因果实时跟踪、强混响鲁棒、低分辨率图可超网格分辨率** | **只有单声源；换阵列需重训；无距离估计** |

**这个 gap 为什么现在才被填？** 不是算力或架构问题，而是**数据问题**：需要"已知真值、且覆盖各种混响/SNR/轨迹"的移动声源训练集，实测采集代价极高。本文用 gpuRIR 把冲激响应模拟加速两个数量级，才让"训练时在线模拟随机轨迹"变成可实现的无限数据集。

## 五、核心 trick：一个 idea + 一组合理工程选择

**核心 idea 只有一个**：把 SRP-PHAT 空间图当成"图像序列"，用因果 3D CNN 在时间维度上做端到端定位+跟踪，取代"先取峰值再跟踪"的两步法。

```
配上的工程选择（每个都可单独消融验证）:
  ✓ 物理空间图做输入        → 对混响/噪声鲁棒（谱输入崩掉的原因是对手）
  ✓ 全因果卷积(无双向RNN)    → 实时可行，每 192ms 出新 DOA
  ✓ 双分支垂直池化(Cross3D)  → 池化降参的同时保留位置信息
  ✓ argmax 坐标注入输入通道  → 帮网络跨过"学 argmax"的不可微障碍
  ✓ 在线随机轨迹模拟         → 无限数据集 + 可 curriculum learning
  ✓ VAD 静音帧置零           → 避免真实录音里跟踪到定向噪声(如风扇)
  ✓ 笛卡尔 XYZ 回归          → 避免角度环绕不连续
```

不算"叠 trick"——是一个干净的 idea 加几个各自可验证的工程决策，且论文对其中最关键的几个都做了对照（见第六节）。

## 六、实验里哪个消融最关键？

论文没有用"消融表"的形式，而是用**多组对照 baseline** 隔离每个设计的作用。最关键的三个发现：

### 关键发现 1：输入"全图" ≫ 只喂"图最大值坐标"

> 作者设计了 1D CNN，只用 64×128 高分辨率图的**最大值坐标序列**做跟踪（与 Cross3D 同感受野 37 帧），用来验证模型是不是真在读"整张图"而不只是"峰值"。

```
模拟实验 (Fig.8, 文中原话):
  1D CNN over 64×128 图最大值坐标  <  3D CNN over 4×8 全图
  → 即使喂给它高分辨率图的峰值，也打不过读低分辨率全图的 Cross3D
  → 证明 Cross3D 确实在利用峰值之外的整图模式（峰宽、次峰结构、阵列几何纹理）

LOCATA (Table II, 总平均):
  1D CNN over 最大值坐标 (64×128):  14.64°
  Cross3D 4×8 全图:                 18.74°   ← 低分辨率全图略输
  Cross3D 16×32 全图:               9.83°    ← 分辨率上来了就反超
  Cross3D 32×64 全图:               8.31°    ← 完胜
```

> [!note] 口径说明
> "全图优于峰值"在模拟实验里是 4×8 全图就成立（Fig.8 原话）；搬上 LOCATA 后，最大值坐标法因输入分辨率高（64×128）而不掉精度，4×8 全图反而略输，但 Cross3D 图分辨率一旦到 16×32 就用明显更少的误差反超。两次实验共同指向同一结论——**全图含峰值邻域模式信息，网络学到了超越搜索网格的分辨率**（4×8 图在 T60=0.3s/SNR=30dB 的好场景可估得远细于 45°×60° 网格，Fig.7b）。这是"先取峰值再跟踪"的两步法永远做不到的。

### 关键发现 2：输入"空间图" 对混响噪声的鲁棒性碾压"谱输入"

| 输入 | LOCATA 总平均 RMSAE |
|------|:---:|
| Cross3D 32×64 空间图 | **8.31°** |
| 1D CNN over GCCs | 12.08° |
| 1D CNN over 最大值 | 14.64° |
| SELDnet（谱） | 50.94° |
| 2D CNN（谱） | **78.01°** |

→ 谱输入模型在好场景（低噪声/消声）里 SELDnet 甚至能赢 Cross3D，但一转混响+噪声直接崩掉。这一条是全文最有说服力的结论。

### 关键发现 3：全因果 + 192ms 就能做到 SOTA，不需要双向 RNN 偷看未来

Listed as结论而非牺牲项：Cross3D 无任何非因果组件，仍在强混响移动源上领先。

### 附：curriculum learning 有效（训练细节，原话见 IV-C）

```
前 20 epoch: 只用 SNR=30dB, batch=5, lr=1e-4
后续 60 epoch: 全 SNR∈[5,30]dB, batch=10, lr 降到 1e-5
→ 高 SNR 下收敛更快，故先用"简单样本"预热
```

## 七、整体结果

### LOCATA 数据集（真实录音，本文最优硬指标）

LOCATA 用的是与训练模拟一致的 NAO 机器人头阵列；房间 T60≈0.5s。Task1=静态扬声器+静态阵列、Task3=移动说话人+静态阵列、Task5=移动说话人+移动阵列，各 3 段录音。**训练全用模拟信号，LOCATA 只用于测试**（唯一事后改动是加了 VAD）。

![[figures/cross3d-training-evaluation.png]]

> **训练-测试图。** 训练端通过 gpuRIR 在线随机生成带真值的移动声源轨迹；测试端则直接把真实 LOCATA 录音送入同一套 SRP-PHAT + Cross3D 流程。

| 模型 | 输入 | Task1 | Task3 | Task5 | **总平均** |
|------|------|:---:|:---:|:---:|:---:|
| Cross3D 4×8 | SRP-PHAT 图 | 15.72° | 21.69° | 18.81° | 18.74° |
| Cross3D 8×16 | SRP-PHAT 图 | 8.65° | 14.85° | 15.08° | 12.86° |
| Cross3D 16×32 | SRP-PHAT 图 | 5.99° | 11.21° | 12.31° | 9.83° |
| Cross3D 32×64 | SRP-PHAT 图 | 4.26° | 9.49° | 11.19° | 8.31° |
| Cross3D 64×128 | SRP-PHAT 图 | **3.77°** | **8.58°** | 11.52° | **7.96°** |
| 1D CNN (GCCs) | GCC 时序 | 5.94° | 13.12° | 17.18° | 12.08° |
| 1D CNN (最大值坐标) | 图 argmax | 13.45° | 14.32° | 16.13° | 14.64° |
| SELDnet (仅 DOA) | 幅度+相位谱 | 40.98° | 52.86° | 58.97° | 50.94° |
| 2D CNN | 幅度+相位谱 | 99.38° | 78.92° | 55.74° | 78.01° |

> 单位均为 RMSAE（Root Mean Squared Angular Error，度），静音帧计入。单看 Task5（阵列也动）最难，所有方法误差都抬升。

### 模拟数据集（Fig.6 / Fig.8 中的趋势，图中无逐点表格数字）

- **强混响**：T60 升到 1.5s（超过训练见过的任何值，训练上限 1.3s）时 Cross3D 仅退化约 5°，而经典 SRP-PHAT 取最大值"无法给出合理估计"。
- **低分辨率图**：4×8 图在方位角每 45°、仰角每 60° 才采样一次，整张球面只需 **18 次** SRP-PHAT 求和（式(4)）；即便如此，在好场景仍能估出远细于网格的 DOA。
- **快速变化跟踪**：因果系统通常"稳了就跟不上快变"，但 Fig.7a 显示 Cross3D 能在源 azimuth 第 5s 突变时及时跟上。

![[语音定位+语音增强/wiki_array/assets/Cross3D-Fig6-RMSAE-vs-reverberation.png|700]]

> **Fig. 6.** 模拟数据上的 RMSAE 随混响时间 $T_{60}$ 变化。蓝色 Cross3D 曲线随混响上升得较慢，而直接取 SRP-PHAT 最大值的橙色曲线在低 SNR 下快速恶化。

![[语音定位+语音增强/wiki_array/assets/Cross3D-Fig7-tracking-examples.png]]

> **Fig. 7.** 跟踪示例：上图是在 $T_{60}=0.9$ s、SNR=5 dB 下使用 32×64 图，下图是在 $T_{60}=0.3$ s、SNR=30 dB 下使用 4×8 图。实线是真值，虚线是 Cross3D 估计，叉号是每张 SRP-PHAT 图的最大值，灰色区域是静音帧。

![[语音定位+语音增强/wiki_array/assets/Cross3D-Fig8-tracking-error-baselines.png]]

> **Fig. 8.** 不同 SNR 与混响条件下的跟踪误差对比。Cross3D 在多种功率图分辨率下都明显优于“只取最大值”和谱输入 baseline；即使使用 4×8 低分辨率图，性能仍有竞争力。

### 参数量对照（Table I）

| 模型 | 参数量 | 时间感受野 | 窗长 | 因果 |
|------|:---:|:---:|:---:|:---:|
| Cross3D 4×8 | 0.53M | 5.63s | 4096 | ✓ |
| Cross3D 8×16 | 0.95M | 6.40s | 4096 | ✓ |
| Cross3D 16×32 | 1.69M | 7.17s | 4096 | ✓ |
| Cross3D 32×64 | 5.63M | 7.17s | 4096 | ✓ |
| Cross3D 64×128 | 21.35M | 7.17s | 4096 | ✓ |
| 1D CNN (GCCs) | 11.28M | — | 4096 | ✓ |
| 1D CNN (最大值坐标) | 6.90M | — | 4096 | ✓ |
| 2D CNN (谱) | 1.88M | — | 512 | ✓ |
| SELDnet (谱) | 0.10M | — | 512 | ✗ (双向 GRU) |

## 八、还剩什么问题没解决？

1. **只做单声源**：假设始终有一个活动源，无数据关联、无"源生灭"处理；多声源"更困难"，仅在 III-A 提了"单源估计器 + 源消除 [40] 迭代"的思路，未实现。
2. **换阵列必须重训**：不同阵列几何的模式完全不同；作者建议利用紧凑阵列图之间的相似性做 transfer learning，但未做。
3. **机器人头散射未建模**：训练模拟忽略了 NAO 头的声散射，若建模可能进一步提升 LOCATA 结果（但会拖慢模拟）。
4. **无距离/3D 位置**：输出单位向量只有方向；用分布式阵列算 3D SRP-PHAT 图 + 4D CNN 可直推 3D 定位，但同样只是"straightforward"的展望。
5. **SRP-PHAT 计算有近似**：分数时延被近似到最近采样点，未做插值——可能限制高分辨率图的精度上限。
6. **长静音脆弱**：LOCATA 的静音比模拟长，谱输入方法因此变差；作者建议把静音段纳入训练模拟、并增大时间感受野（加深/加宽时间核/更大 dilation）。
7. **经典 2D CNN 无旋转等变**：对球面图而言理想的是球面等变 CNN（Spherical CNN），作者因计算效率放弃——这是后来 [[Icosahedral CNN DOA 2023]] 的主攻点。

## 九、跟哪篇像

**直接延续**：
- Diaz-Guerra & Beltran, SAM 2018「DOA Estimation with SRP-PHAT and Neural Networks」[42] → 同作者前作，SRP-PHAT 图 + 全连接 MLP，本篇把后端升级成因果 3D CNN + 跟踪。
- [[SRP-PHAT]]（DiBiase）/ [[GCC-PHAT 广义互相关]] → 前端算法本身。

**同路线（空间图 → DNN）**：
```
DeepWave Acoustic Imaging 2019 (声学成像 + 递归时序)
        ↓
Cross3D 2021 (SRP-PHAT 时序图 + 因果 3D CNN 跟踪)  ← 本篇
        ↓
SSLIDE 2021 (空间 likelihood 图 + 双 decoder)
Icosahedral CNN DOA 2023 (球面 SRP-PHAT 图 + 球面等变，补旋转等变)
Mechanical Fault SSL 2024 (SRP-PHAT 图复原)
Beamformed 360 Sound Maps 2025 (DAS 360° 声学图 + U-Net 分割)
```

**被对照的谱路线（本组作为 baseline）**：
- [[SELD CRNN 2018]]（SELDnet 被复现成 DOA-only baseline）
- [[CNN DOA Estimation with Noise Training 2017]] / [[Multi-Speaker CNN DOA 2018]]（Chakrabarty 相位图 2D CNN 谱路线）


### 6. 本论文在库中的位置关联

| 维度 | 论文 | 关系 |
|------|------|------|
| **前身/基石** | [[SRP-PHAT]] | 输入特征的前端算法，本文 = SRP-PHAT 图的时序序列 + 3D CNN |
| **前身/基石** | [[LOCATA Challenge 2019]] | 提供真实录音测试基准 + NAO 机器人头阵列几何 |
| **前身/基石** | [[GCC-PHAT 广义互相关]] | SRP-PHAT 的底层计算式(4)由 GCC 求和而来 |
| **后续/扩展** | [[Icosahedral CNN DOA 2023]] | 用球面等变 CNN 补上本文"经典 CNN 无旋转等变"的短板 |
| **后续/扩展** | [[Mechanical Fault SSL 2024]] | 延续 SRP-PHAT 图 + U-Net 图复原路线，扩展到强混响多故障 |
| **同分支竞品** | [[SSLIDE 2021]] | 同一年、空间 likelihood 图 + 室内定位，比本文多了位置(非仅方向) |
| **同分支竞品** | [[DeepWave Acoustic Imaging 2019]] | 声学成像思路近亲，但用递归网络且更偏实时成像 |
| **同分支竞品** | [[Direct-Path Dominance Test 2020]] | U-Net 直达声图 + SRP-PHAT，同属"先做空间图再学习" |
| **跨分支类比** | [[SELD CRNN 2018]] | 本文把它当 spectral-input baseline 复现；两者是"物理图 vs 谱"在 DOA 任务的正面交锋 |
| **跨分支类比** | [[Multi-Speaker CNN DOA 2018]] | Chakrabarty 谱相位图路线，本文引为对照，相位信息被 SRP 图取代 |

> ⚠️ 疑似关联，需用户确认：[[DeepWave Acoustic Imaging 2019]] 与 [[Beamformed 360 Sound Maps 2025]] 是否确有方法学继承关系，库中暂无直接证据，仅"空间图→DNN"串线属性相同。

### 7. 江湖地位

```
2021 | DOA跟踪 | SRP-PHAT 时序功率图 + 全因果 3D CNN (Cross3D)，LOCATA 平均 RMSAE 7.96°，
        证明"物理空间图 + 因果时空网络"对强混响噪声的鲁棒性碾压谱输入 → "空间图→DNN"路线的代表/基线
        → 被 Icosahedral CNN DOA 2023 以球面等变换掉旋转非等变补强
        → 被 360°声学图 + U-Net (2025) 与 SRP-PHAT 图复原 (2024) 沿同一路线扩展
```


---

*Cross3D 的价值不在模型本身多精巧，而在它用一组干净的对照实验钉死了一个分野：在混响+噪声的真实场景里，"先把阵列信号变成有物理意义的空间图、再让因果网络读时序"远胜于"直接喂谱"。它的 7.96°（LOCATA 移动源）和"低到 4×8 图仍能超网格分辨率"是这条路线此后所有工作的共同锚点。*
