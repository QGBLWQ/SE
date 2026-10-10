---
title: SSLIDE: Sound Source Localization for Indoors based on Deep Learning
type: source
created: 2026-09-15
updated: 2026-09-15
tags:
  - sound-source-localization
  - doa-estimation
  - indoor-acoustics
  - near-field
  - multipath
  - reverberation
  - encoder-decoder
  - likelihood-surface
source_type: paper
year: 2021
authors:
  - Yifan Wu
  - Roshan Ayyalasomayajula
  - Michael J. Bianco
  - Dinesh Bharadia
  - Peter Gerstoft
affiliation: University of California, San Diego (UCSD)
venue: ICASSP 2021
arxiv: "2010.14420"
url: https://arxiv.org/abs/2010.14420
related:
  - [[Robust Sound Source Tracking SRP-PHAT 3D CNN 2021]]
  - [[Mechanical Fault SSL 2024]]
  - [[Beamformed 360 Sound Maps 2025]]
  - [[Multi-Speaker CNN DOA 2018]]
  - [[DeepWave Acoustic Imaging 2019]]
  - [[Direct-Path Dominance Test 2020]]
  - [[SRP-PHAT]]
  - [[MUSIC 算法]]
---

# SSLIDE — 基于双 decoder 的空间 likelihood 图室内声源定位

> Yifan Wu, Roshan Ayyalasomayajula, Michael J. Bianco, Dinesh Bharadia, Peter Gerstoft (UC San Diego), **ICASSP 2021**。arXiv: [2010.14420](https://arxiv.org/abs/2010.14420) (v2, 2021-02-15)。本地 PDF：[raw/articles/2010.14420.pdf](../../../raw/articles/2010.14420.pdf)

```yaml
- 论文: SSLIDE (Sound Source Localization for Indoors using DEep learning) — 2021
  ├── 要解决什么问题: 室内混响下声源定位——多径伪影 (multipath) 会让 likelihood 图上的峰值偏离真实距离；传统方法 (MUSIC/SRP-PHAT) 在混响+语音下失效，而现有 DNN 方法只在小源距下有效
  ├── 核心方法: 波束成形 likelihood 图 (θ-d 极坐标 → 映射到全局笛卡尔平面) + 单编码器双 decoder：一个预测位置，一个做距离补偿/多径缓解（训练期辅助，测试期关闭）
  ├── 属于哪个分支: 室内近场定位（含距离，连续空间），"空间 likelihood 图 + 图到图回归"的 encoder-decoder 路线（从无线定位 DLoc 迁移到声学）
  ├── 输入/输出: 输入 = 未做距离补偿的 likelihood 图 (C×N×X×Y)；输出 = 定位 likelihood 热图 (C×X×Y)，argmax 视为预测位置
  ├── 关键trick: 负指数目标标签（避免 one-hot 梯度消失）；range compensation 辅助 decoder（训练期开、测试期关）；把 θ-d 极坐标 likelihood 变换到全局笛卡尔平面融合多阵列
  ├── 数据集: 仿真 RIR (image method, 房间 8×5×4 m, RT60 0.2–0.8 s, 3×ULA/每阵4麦) + MIRD 实测 RIR (8麦 ULA, RT60 0.16/0.36/0.61 s, 26 候选位置)；语音来自 LibriSpeech + Audio Set 白噪声 35 dB SNR
  ├── 对比了谁: MUSIC、SRP-PHAT、SBL (稀疏贝叶斯学习)、CNN (Chakrabarty & Habets [14])
  ├── 性能上限: 定位 MAE 0.23 m (MIRD RT60=0.16 s)；DOA MAE 3.0° (sim RT60=0.2 s)、4.3° (MIRD RT60=0.16 s)
  ├── 参数量: 论文未公开 SSLIDE 的参数量（缺省，需复现估算）；CNN baseline 结构已知 11/7 层 conv (64 核) + 2×FC512
  ├── 消融关键发现: 移除 multipath 缓解 decoder 后 MAE 全面恶化（sim RT60=0.2 s: 0.24→0.54 m；MIRD 0.16 s: 0.23→0.35 m），证明该辅助分支对混响鲁棒性至关重要
  ├── 遗留问题(你的机会): 只在 z=2 m 平面上定位、声源被限制在房间边界、单声源、ULA 简单阵列、无开源代码、参数量未公开；跨房间几何的真实泛化未验证
  └── 跟哪篇像: 架构直接迁移自 DLoc (MobiCom 2020 无线定位)，声学侧像 [[DeepWave Acoustic Imaging 2019]] 与 [[Robust Sound Source Tracking SRP-PHAT 3D CNN 2021]]
```

## 一、研究任务与对象

| 维度 | 详情 |
|------|------|
| **任务** | 室内 (indoor) **近场**声源定位——不是只有角度 θ 的远场 DOA，而是同时估计声源在房间平面内的 2D 连续位置 (x, y)（从而隐含距离 d） |
| **核心问题** | 混响产生多径，接收信号是直达声 + 大量反射的叠加，使 likelihood 图上的峰值在**距离维度**偏离真实值（角度尚可，距离被拉偏） |
| **方法类型** | 前端波束成形生成 likelihood 图 → **encoder-decoder**（1 个编码器 + 2 个并行解码器，图到图回归） |
| **阵列类型** | 均匀线阵 ULA（仿真 3 个 ULA，每阵 4 麦，阵元间距 2.6 cm / MIRD 1 个 8 麦 ULA，间距 8 cm）；近场模型（球面波，非平面波） |
| **声源数** | 单声源（论文只做单源定位，输出图取单个全局最大） |
| **声场假设** | 近场（需要估计距离）+ 混响（任意 RT60）+ 加性噪声（35 dB SNR） |
| **输出格式** | 连续回归：输出一张 Y×X 的 likelihood 热图，取 argmax 为预测位置（非角度网格分类）；与 baseline 对比时再从 (x̂, ŷ) 反算 DOA |
| **数据集** | 仿真 RIR（image method）+ MIRD 实测 RIR，共 600 (sim) + 520 (MIRD) 个 datapoint |
| **训练规模** | 帧数 C = T×S：sim 600×63 = **37,800** 帧；MIRD 520×125 = **65,000** 帧 |

> 和库里绝大多数"远场 DOA"论文不同：SSLIDE 是**近场 + 距离估计**的室内定位，输入也不是幅度/相位谱，而是**波束成形 likelihood 图**。这是它能在"空间图 / 图复原"分支里独立成篇的原因。

## 二、整体架构

```
多通道麦克风信号 y ∈ R^{M×L}   (M = N×K; sim: 3×4=12 麦; MIRD: 8 麦)
    │
    ▼
STFT (NFFT=256, 无 overlap) → Y ∈ C^{S×F×K×N}，只取正频 F=128
    │
    ▼
波束成形 likelihood (Eq.2)  P_ns(θ,d)   ← 对每个阵列 n、每帧 s 在 (θ, d) 网格扫描能量
    │   U×V 网格（sim 101×161 / MIRD 121×121）
    ▼
坐标变换: (θ, d) 极坐标 → 全局 2D 笛卡尔平面 (Y×X)  ← 让多个阵列对齐到同一全局坐标
    │
    ▼
输入 likelihood 图 (未做距离补偿)  C×N×X×Y
    │
    ▼
┌────────────── Encoder（共享）──────────────┐
│ Conv 7×7, s=1, p=3, tanh                    │
│ Conv 7×7, s=1, p=3, ReLU                    │
│ Conv 3×3, s=2, p=1, ReLU   ← 下采样 ×2      │
│ Conv 3×3, s=2, p=1, ReLU   ← 下采样 ×2      │
│ 6 × ResNet Block                            │
└────────────────┬────────────────────────────┘
                 │ 压缩后的 latent 表示
      ┌──────────┴──────────┐        ┌──────────────────────────────┐
      ▼                      ▼        ▼ (仅训练期)
 Multipath Alleviation  Localization      目标: range-compensated
 Decoder (辅助分支)      Decoder (主分支)   likelihood 图 (C×N×X×Y)
 6 × ResNet Block         3 × ResNet Block
 ConvTrans 3×3 s=2 p=1    ConvTrans 3×3 s=2 p=1
 ConvTrans 3×3 s=2 p=1    ConvTrans 3×3 s=2 p=1
 Conv 7×7 s=1 p=3 Sigmoid Conv 7×7 s=1 p=3 Sigmoid
      │                      │
      │(测试期关闭)           ▼
      │              输出 likelihood 热图 (C×X×Y)
      │                    │ argmax
      │                    ▼
      │              预测位置 (x̂, ŷ)  ← 连续空间，无需角度网格先验
```

### 两个 decoder 的分工（核心设计）

1. **Multipath Alleviation Decoder（多径缓解 / 距离补偿分支）**：以"做完 range compensation 的 likelihood 图"为目标（标签），强制网络学习混响造成的距离偏移剖面（multipath profile）并学会修正它。**只在训练期存在，测试期关闭**——它的作用纯粹是给共享编码器注入"什么是干净 likelihood 图"的监督信号。
2. **Localization Decoder（定位分支）**：以"负指数标签热图"为目标，直接输出源位置 likelihood，取 argmax 得到预测坐标。

> 这个"第二个 decoder 只训练不部署"的设计，本质是把"显式洞见（多径在距离维上造成偏移）"作为一种**辅助监督**塞进损失，而不增加推理开销——是本篇最重要的工程思想。

## 三、为什么这么做？（Motivation）

1. **混响是室内 SSL 的头号敌人**：接收信号大部分能量来自反射（multipath），是"麦克风相对于声源位置的复杂函数"，导致 likelihood 图的峰值在**距离预测**上失真（Fig.1a）——角度还能对上，距离被反射路径拉偏。
2. **传统方法在混响+语音下系统性失效**：MUSIC 对相关源（reverberant 环境普遍存在）敏感；SRP-PHAT 对非平稳信号（如语音）不鲁棒。
3. **已有 DNN 方法只在小源距下有效**：作者指出 intro 引用的各类 DNN/CNN/CRNN 方法"只能在小 sensor-source 距离下工作，限制了真实落地"——因为它们大多只估角度（远场 DOA），没有显式处理距离维的混响偏移。
4. **跨域迁移的动机**：作者组里 Bharadia 是做**无线室内定位 (WiFi/CSI)** 的（DLoc [21]、BLoc [23]）——"把信号变成 likelihood 图 + 双 decoder 解耦'定位'和'多径/测距误差'"这套东西在无线电域已经成熟，本作把它整套搬到声学域。这是理解这篇论文为何"凭空"长出双 decoder 的关键背景。

## 四、之前的人怎么做不了？（Limitation → Gap）

| 方法 | 能做 | 不能做（这篇的 gap 切入口） |
|------|------|------------------------------|
| MUSIC [8] | 低混响下高精度 DOA（子空间法） | 对相关源（混响普遍）敏感；需源数先验；**不做距离** |
| SRP-PHAT [9-11] | 波束扫描 DOA，计算简单 | 对非平稳信号（语音）不鲁棒；混响下峰值退化 |
| SBL [22][2] | 稀疏贝叶斯 + 波束成形，压制旁瓣 | 计算量大；依赖候选网格/先验 |
| CNN [14] (Chakrabarty) | 混响鲁棒的分类式 DOA | **需要知道候选 DOA 类别数**（MIRD 下"知道"13 类）；只估角度、离散分类不估距离 |
| 现有 DNN SSL [13-20] | 学习式定位 | 只在**小源距**下有效；大多只估角度，无距离/混响显式建模 |
| **SSLIDE** | **连续空间 (x,y) 定位 + 显式多径缓解 + 不依赖 DOA 先验** | 只在单平面/单声源/ULA 上验证（见第八节） |

> gap 之所以留存至今（2021 年视角）：把"距离维的混响偏移"显式建模，需要 (a) 一个能编码声源的**中间空间表示**（likelihood 图而非原始时频特征），(b) 一个能提供"干净图"监督的**构造方式**（range compensation）。这两点分别来自波束成形传统和无线定位领域的既有工具，声学界此前没把它们接起来。

## 五、核心 trick：一个 idea 还是叠了很多？

**核心只有一个 idea**：把"定位"和"多径（距离）修正"拆成两个并行 decoder，用共享编码器让定位分支**间接**学到如何抗多径——而多径缓解分支用"range-compensated likelihood 图"作为可构造的监督标签。

围绕它的几个关键工程选择：

```
✓ 前端: 波束成形 likelihood 图 (θ, d) 作为输入 —— 把"原始多通道时频"压缩成"空间假设检验"表示
✓ 坐标变换到全局笛卡尔平面 —— 多阵列 (N=3) 才能对齐到同一坐标系，共享同一声源位置
✓ range compensation 标签构造 (Eq.3) —— 用直达路径 (最小距离) 估 d̂，做频率域相位补偿得到"理想图"
✓ 负指数目标标签 (Eq.5, σ=0.25) —— 避免 one-hot 目标导致的梯度消失
✓ 辅助 decoder 训练期专用 —— 显式监督但不增加推理开销
✓ l1 稀疏正则 (Eq.7, λ=5×10⁻⁴) —— 因为输出图只有一个全局最大
```

不是"堆 trick"——是一个干净的 idea（双 decoder 解耦）+ 三个让数字能 work 起来的前处理/标签工程（likelihood 图、range compensation、负指数标签）。

## 六、实验里哪个消融最关键？

**唯一的消融实验 = 移除 multipath alleviation decoder**（Table 1 第二行）。它直接验证了核心 idea：

### 移除多径缓解 decoder 后，MAE (m) 全面恶化

| 数据 | RT60 (s) | 完整 SSLIDE (m) | 去掉多径分支 (m) | 退化幅度 |
|------|:--------:|:-----------:|:-----------:|:-------:|
| 仿真 | 0.20 | 0.24 | 0.54 | +125% |
| 仿真 | 0.40 | 0.56 | 1.10 | +96% |
| 仿真 | 0.60 | 0.77 | 1.80 | +134% |
| 仿真 | 0.80 | 0.90 | 1.50 | +67% |
| MIRD | 0.16 | 0.23 | 0.35 | +52% |
| MIRD | 0.36 | 0.29 | 0.43 | +48% |
| MIRD | 0.61 | 0.39 | 0.59 | +51% |

> 结论：**没有哪个"其它消融"比这个更重要，因为这是全文唯一做的消融**。去掉辅助分支后误差在**所有**混响条件下都上升约 50%–134%，直接证明"多径缓解辅助监督"是本方法抗混响能力的实际来源——反过来说，也说明如果换掉这个 trick，整套方法会退化成"一个 U-Net 风格的图到图回归"，与 [[Beamformed 360 Sound Maps 2025]] 那一类"波束图 + 分割"没有本质区别。

## 七、整体结果

### 定位误差 MAE (m)（Table 1，测试集第一行）

| RT60 (s) | 0.20 | 0.40 | 0.60 | 0.80 | — | 0.16 | 0.36 | 0.61 |
|----------|:----:|:----:|:----:|:----:|:-:|:----:|:----:|:----:|
| 数据 | 仿真 | 仿真 | 仿真 | 仿真 | | MIRD | MIRD | MIRD |
| MAE (m) | 0.24 | 0.56 | 0.77 | 0.90 | | 0.23 | 0.29 | 0.39 |

→ 混响越重误差越大（RT60 0.2→0.8 s 时 0.24→0.90 m），但即便在最重混响下仍保持在亚米级。

### DOA 误差对比（Table 2，MAE °）

| 方法 | sim 0.20 | sim 0.40 | sim 0.60 | sim 0.80 | MIRD 0.16 | MIRD 0.36 | MIRD 0.61 |
|------|:--------:|:--------:|:--------:|:--------:|:---------:|:---------:|:---------:|
| SRP-PHAT | 14 | 21 | 25 | 25 | 13 | 16 | 19 |
| MUSIC | 12 | 22 | 27 | 29 | 12 | 17 | 18 |
| SBL | 7.6 | 13 | 17 | 16 | 11 | 16 | 18 |
| CNN | 10 | 14 | 16 | 20 | 4.6 | 8.0 | 9.8 |
| **SSLIDE** | **3.0** | **5.0** | **6.7** | **7.9** | **4.3** | **5.7** | **8.1** |

→ **SSLIDE 在所有混响等级、两个数据集上全面领先所有 baseline**。关键反差：仿真数据里声源位置是随机的（baseline 因声源远离传感器而严重退化），SSLIDE 仍稳定；MIRD 里其它 baseline 都"享用"了候选 DOA 先验（SRP-PHAT/MUSIC/SBL 用 15° 步进的 steering vector 网格，CNN"知道"有 13 个类别），**只有 SSLIDE 不依赖任何 DOA 候选先验**还能做到最优。

### 泛化性能（Table 3，MAE）

| 训练 | 测试 | SSLIDE MAE (m) | SSLIDE DOA (°) | CNN DOA (°) |
|------|------|:---:|:---:|:---:|
| Base I (sim RT60 0.6s) | Base I 同分布 | 0.77 | 6.66 | 15.6 |
| Base I | (i) RT60 ↑到 0.7s | 0.93 | 7.85 | 17.6 |
| Base I | (ii) 阵元间距 2.6→2.7 cm | 0.78 | 6.67 | 16.9 |
| Base II (MIRD RT60 0.61s) | Base II 同分布 | 0.39 | 8.06 | 9.81 |
| Base II | (iii) 3 条未见语音 | 0.45 | 12.0 | 23.9 |

→ 对 RT60 扰动、阵元间距扰动、未见语音三者，SSLIDE 的退化都远小于 CNN（如未见语音 DOA 12.0° vs CNN 23.9°），说明学到的"多径缓解"是跨条件迁移的，不是记忆训练分布。

## 八、还剩什么问题没解决？

论文自己承认 / 我读出来的问题：

1. **只在 z = 2 m 水平面定位，声源被限制在房间边界**：随机 (x, y) 采样只取"阵列平面 z=2 m 上的房间边界"，且是**单声源**——真实室内多声源、任意 3D 位置尚未覆盖。
2. **阵列为简单 ULA**：3 个独立 ULA、近场模型；没有验证任意阵列几何 / 圆阵 / 球阵的泛化。
3. **无开源代码、无参数量、无 RTF/复杂度报告**：难以直接复现和做公平的轻量化对比（这也是草稿里"轻量化/复杂度相关性"只能定性说的原因）。
4. **MIRD 规模很小**：520 个 datapoint、26 个候选位置、20 条录音，泛化结论主要靠仿真支撑。
5. **range compensation 需要 RIR/直达路径先验来构造标签**：训练期需要知道 d̂（直达路径距离）与 d（真值），这在实际部署的未知房间里不可得——训练监督是"上帝模式"，这是它和纯无监督/自监督方法的本质差距。
6. **隐藏问题**：输出图取单个 argmax，天然不支持**多声源**；距离估计精度在重混响 (RT60 0.8s) 下已到 0.90 m，离实用还有距离。后续 [[SELD-Mamba 2024]] 把距离估计并入 SED+DOA，可看作此近场问题在 SELD 主线的并行解法。

## 九、跟哪篇像

**架构血缘（跨域）**:
- DLoc (Ayyalasomayajula et al., MobiCom 2020) → 无线室内定位，"likelihood 图 + 双 decoder"的直接来源，作者组内部迁移
- BLoc (CoNext 2018) → 2D likelihood 函数 (Eq.2) 的原始出处

**声学域直接相关**:
- [[DeepWave Acoustic Imaging 2019]] → 同为"声学 likelihood/空间图 + 图到图"路线
- [[Robust Sound Source Tracking SRP-PHAT 3D CNN 2021]] → 同一年 (2021)、同为室内 SSL、SRP-PHAT 空间图 + CNN，但用 3D CNN 做**跟踪**且不含多径缓解分支
- [[Multi-Speaker CNN DOA 2018]] → 就是本作 CNN baseline 的来源 [14]
- [[Beamformed 360 Sound Maps 2025]] → 同为"波束图 + 编码器解码器"的图分割路线（更侧重 360° 视角）
- [[Direct-Path Dominance Test 2020]] → 同主题"直达声 vs 多径"：DPD 用直达声主导 TF bin 选择，SSLIDE 用 range compensation 构造干净图

### 6. 本论文在库中的位置关联

| 维度 | 论文 | 关系 |
|------|------|------|
| **前身/基石** | DLoc (MobiCom 2020, 无线定位) | ⚠️ 疑似关联，需用户确认（不在库中）：架构（likelihood 图 + 双 decoder）与 range compensation 的直接迁移源，作者组内部跨域 |
| **前身/基石** | BLoc (CoNext 2018) | ⚠️ 疑似关联，需用户确认（不在库中）：Eq.2 波束 likelihood 函数出处 |
| **前身/基石** | [[SRP-PHAT]] | 前端 likelihood 图的波束成形基础（本文前端本质是近场 DAS 波束扫描，非 PHAT 加权） |
| **前身/基石** | [[Multi-Speaker CNN DOA 2018]] | 被用作 CNN baseline [14]，其"多通道 CNN 分类式 DOA"正是本文要超越的对象 |
| **后续/扩展** | [[Mechanical Fault SSL 2024]] | ⚠️ 疑似关联，需用户确认：同为"SRP-PHAT 图复原/去伪峰再定位"思想，用于强混响机械故障定位 |
| **后续/扩展** | [[Beamformed 360 Sound Maps 2025]] | ⚠️ 疑似关联，需用户确认：同为"波束图 + 编码器解码器"图分割路线，但走 360° DAS + U-Net 分割，无多径缓解分支 |
| **同分支竞品** | [[Robust Sound Source Tracking SRP-PHAT 3D CNN 2021]] | 同一年 (2021)、同任务（室内 SSL）、同输入类型（SRP-PHAT 空间图），但用因果 3D CNN 做跟踪、无距离补偿辅助分支——是本文最直接的同代竞品 |
| **同分支竞品** | [[DeepWave Acoustic Imaging 2019]] | 同为"空间 likelihood 图 + 递归/图到图"声学成像路线 |
| **同分支竞品** | [[Icosahedral CNN DOA 2023]] | 同为 SRP-PHAT 图 + CNN，但做球面 icosahedral、纯角度；SSLIDE 做近场平面 + 距离 |
| **跨分支类比** | [[SELD CRNN 2018]] | 都是"编码器 + 多输出头"解耦多任务，但 SELDnet 用幅度/相位谱 + 分类/回归头（远场角度），SSLIDE 用波束图 + 双 decoder（近场距离）——两个"空间信息表征 + 多任务解耦"的平行落点 |
| **跨分支类比** | [[MUSIC 算法]] / SBL | 本文直接对比的传统 baseline；SBL（稀疏贝叶斯学习）在库中尚无页面 |

### 7. 江湖地位

```
2021 | 室内近场 SSL | 空间 likelihood 图 + 双 decoder（多径缓解辅助分支）从无线定位迁移到声学
      → 用"range compensation 辅助监督"显式解耦"定位"与"多径/距离偏移"，连续空间定位无需 DOA 先验
      → 同代被 [[Robust Sound Source Tracking SRP-PHAT 3D CNN 2021]]（SRP-PHAT 3D CNN 跟踪）并行竞争
      → 后续被"波束图 + 图分割/U-Net"路线 ([[Beamformed 360 Sound Maps 2025]]) 与"空间图复原" ([[Mechanical Fault SSL 2024]]) 吸收演进
```

---

*SSLIDE 是"空间图 + 图到图回归"路线的近场定位代表：它把室内定位拆成"定位"与"多径缓解"两个可分离的问题，用一张波束成形 likelihood 图和两个 decoder 优雅地解决——代价是训练期的"上帝模式"监督（需要 RIR 来构造 range-compensated 标签）。想理解库里的"图复原/校正后定位"分支（SRP-PHAT 图、波束图、直接路径主导），这篇是把前端 likelihood 图和后端多任务解耦串起来的那块拼图。*