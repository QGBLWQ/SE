---
title: FA-Stateformer 2025 — 状态空间+自注意力协同 DOA 估计
type: source
created: 2026-07-01
updated: 2026-07-01
tags:
  - doa-estimation
  - state-space-model
  - mamba
  - self-attention
  - conformer
  - lightweight
  - feature-aggregation
source_type: paper
year: 2025
authors:
  - Qi You
  - Qinghua Huang
  - Yi-Cheng Lin
venue: arXiv 2025
arxiv: "2510.25193"
related:
  - "[[DOA 波达方向估计]]"
  - "[[SSL Survey 2021]]"
  - "[[CST-former 2025]]"
---

# FA-Stateformer — Feature Aggregation State-Space and Self-Attention Collaborative Network for DOA Estimation

> You, Huang & Lin, 2025. Mamba + SEConformer 协同建模用于 DOA 估计。

```yaml
- 论文: FA-Stateformer (2025)
  ├── 要解决什么问题: 移动多声源DOA估计中，时序建模能力与计算效率的平衡
  ├── 核心方法: Feature Aggregation (时频注意力) + Stateformer (Bi-Mamba+ 与 Self-Attention 并联+串联)
  ├── 属于哪个分支: Mamba+Transformer 协同架构 (非 SELD，纯 DOA)
  ├── 输入/输出: 幅度谱+相位谱 (多通道STFT系数) / 笛卡尔坐标 (x,y,z)
  ├── 关键trick: FA时频分离注意力、SEConformer (压缩FFN+时序偏移卷积)、Bi-Mamba++SA协同
  ├── 数据集: 模拟数据 (LibriSpeech+RIR)、真实数据 (LOCATA Tasks 3-6)
  ├── 对比了谁: CRNN-R, ResNet-Conformer, ConBiMamba, IPDnet, TF-Mamba
  ├── 性能上限: Acc5=71.8%, MAE=2.7° (模拟双移动声源); LOCATA Task3 Acc10=95.7%
  ├── 参数量: 2.2M (vs RC 4.3M, IPDnet 1.8M但FLOPs高10倍)
  ├── 消融关键发现: FA模块的频域注意力贡献最大；ShiftConv15优于Conv31
  ├── 遗留问题(你的机会): 纯DOA没有做SED；两麦克风限制180°方位角；多声源场景精度仍有限
  └── 跟哪篇像: ConBiMamba (Mamba替换Conformer的SA) + RC (ResNet-Conformer基线) + IPDnet (DP-IPD相位差)
```

## 一、研究任务与对象

| 维度       | 详情                                                  |
| -------- | --------------------------------------------------- |
| **任务**   | DOA 估计 (纯定位，不含声事件检测)                                |
| **核心问题** | 移动多声源场景下，时序建模能力与计算效率之间的平衡                           |
| **方法类型** | Feature Aggregation + Bi-Mamba+ + Self-Attention 协同 |
| **阵列类型** | 2-mic 平面阵列 (间距 8cm)                                 |
| **输出格式** | 笛卡尔坐标 (x, y, z) 回归，PIT 训练                           |
| **数据集**  | 模拟: LibriSpeech + gpuRIR 合成 / 真实: LOCATA            |
| **评估指标** | Acc5/10/15 (\%), MAE (°)                            |

---

## 二、整体架构

```
多通道音频 → STFT (512点, 32ms窗, 16ms hop)
    │
    ▼
输入: (C=2, F=256, T)  ← 幅度谱 + 相位谱拼接
    │
    ▼
Feature Aggregation (FA) Module:
  ResNet 前端 (通道: 4→32→64→128)
  FA 时频注意力:
    ├── Temporal Branch: 沿F平均 → 1×5+1×3卷积 → 时间注意力权重
    └── Frequency Branch: 沿T平均 → 5×1+3×1卷积 → 频率注意力权重
    │ (两个注意力权重串行施加到原始特征上)
    ▼
Stateformer Blocks × 2:
    │
    ┌──────────────── Stateformer Block ─────────────────┐
    │                                                    │
    │  Step 1: FFN_E (扩张前馈)                          │
    │      │                                              │
    │  Step 2: Bi-Mamba+ (双向状态空间建模)              │
    │      │  (前向+后向SSM，通过可学习的遗忘门           │
    │      │   选择性地融合历史信息和新输入)              │
    │      │                                              │
    │  Step 3: DyTanh + FFN_S (压缩前馈 = SE模块)        │
    │      │                                              │
    │  Step 4: MHSA (标准多头自注意力,弥补Mamba局部不敏感)│
    │      │                                              │
    │  Step 5: ShiftConv (时序偏移卷积,扩大感受野)        │
    │      │                                              │
    │  Step 6: FFN_E (扩张前馈) + LayerNorm              │
    │                                                    │
    └────────────────────────────────────────────────────┘
    │
    ▼
FC → DOA 输出 (x, y, z) for each speaker
```

---

## 三、为什么这么做？（Motivation）

1. **现有方法的矛盾**: CNN/RNN 计算效率高但建模能力有限；Transformer 建模强但 O(N²) 复杂度；Mamba 有 O(N) 复杂度但**对局部快速变化不敏感**
2. **Conformer 有冗余**: 标准 Conformer 的 FFN 采用"扩张→压缩"模式，但前后两个 FFN 叠在一起造成了大量冗余计算
3. **Mamba 的单向局限**: 标准 Mamba 只做前向处理，而 DOA 需要同时看到过去和未来的上下文

## 四、之前的人怎么做不了？（Limitation → Gap）

| 方法 | 能做 | 不能做 |
|------|------|--------|
| CRNN-R | 多声源回归 | 时序建模弱，Acc5=52.5% |
| ResNet-Conformer (RC) | 强时序+全局注意力 | 4.3M 参数，FLOPs 高 (6.4G/s) |
| ConBiMamba | Mamba 替换 SA，线性复杂度 | 缺少 SA 的局部动态捕捉 |
| IPDnet | 相位差精度极高 (MAE 低) | FLOPs 高 10 倍 (54.3G/s)，推理慢 707ms |
| TF-Mamba | 时频双维度 Mamba | 单声源假设，多声源扩展有限 |
| **FA-Stateformer** | **FA 时频注意力 + Bi-Mamba+ + SA 协同** | **纯 DOA，没有 SED；180° 限制** |

## 五、这个做法核心 trick 是什么？

这篇论文的 trick 分三个层面，按重要性排序：

### Trick 1: FA (Feature Aggregation) 时频分离注意力 ⭐⭐⭐

这是最核心的输入处理模块。它的设计和前面学的 DST/CST 的维度分解思想完全一致。

```
FA 的核心思想: 时间和频率具有不同的物理意义，不应该混在一起做 2D 建模。

在时间的1D轴上做注意力 → 告诉网络"哪些时间帧重要"
在频率的1D轴上做注意力 → 告诉网络"哪些频率 bin 重要"

具体做法很轻量:
  时间分支: 
    沿频率方向平均 → (C, T) → 1×5 + 1×3 卷积 → sigmoid → 时间权重
  频率分支:
    沿时间方向平均 → (C, F) → 5×1 + 3×1 卷积 → sigmoid → 频率权重
  
  → 总共只有 2 组小卷积核，参数极少
  → 相当于给特征图加了一个"可学习的时频滤波器"
```

消融实验中，单独频域注意力 (+FD) 比单独时域注意力 (+TD) 效果好 (69.2% vs 66.5%) → **频率信息对定位更重要**（谐波结构 + 空间混叠模式）。

### Trick 2: SEConformer (压缩 FFN + ShiftConv) ⭐⭐

标准 Conformer 的瓶颈：

```
Conformer 的冗余:
  Block N 的尾部 FFN: 扩张→激活→压缩
  Block N+1 的头部 FFN: 扩张→激活→压缩  ← 重复了高级特征的变换！
```

SEConformer 的解决：

```
去掉第一个块的尾部 FFN
将第二个块的 FFN 改为 SE (Squeeze-and-Excitation) 模块:
  → 不再做"扩张→压缩"的大矩阵乘法
  → 而是用 Swish 激活 + 通道压缩 → 选择性地强调重要通道
  → 参数从 2.4M → 2.0M
```

### Trick 3: Time-Shift Convolution ⭐⭐

ShiftConv 用**channel shifting**代替**大卷积核**：

```
标准 Conv: 增大 kernel size (如 31×1) → 更多参数
ShiftConv: 保持小 kernel (如 15×1) → 
  将 C/2 个通道分成4组:
    组1: 向前移位 +k 帧
    组2: 向后移位 -k 帧  
    组3: 向前移位 +k/2 帧
    组4: 向后移位 -k/2 帧
  然后拼接 → 小 kernel 卷积 → 实际看到了更大范围

效果: ShiftConv15 (小核+移位) 超过 Conv31 (大核无移位)
  Acc5: 71.8% vs 71.2%  ← 参数更少还更好！
```

### Trick 4: Bi-Mamba+ + Self-Attention 协同 ⭐

```
Bi-Mamba+: 前向+后向 SSM 处理，加可学习的遗忘门
  
Stateformer 中二者的角色:
  Bi-Mamba+: 全局长程依赖建模（O(N) 复杂度）
  Self-Attention: 局部动态变化捕捉（位置编码 + 短程关注）
  
  第一层用 Bi-Mamba+ 替代 SA → 第1层捕获长程结构
  后续层保留 SA → 后续层捕获细节 + 补偿 Mamba 的局部不敏感
```

### 总结：叠了几个 trick？

```
不是只有一个 idea，而是系统性的工程组合:
  ⭐⭐ FA 模块: 时频分离注意力 (最大单模块贡献)
  ⭐ SEConformer: 压缩 FFN + ShiftConv (参数效率)
  ⭐ Bi-Mamba+ + SA 协同: 长程+短程互补 (架构核心)

→ **3 个关键 trick 协同，没有一个是凑数的**
```

## 六、实验里哪个消融最关键？

### 消融 1: FA 模块的贡献（表 VII）

| 配置 | Params(M) | Acc5(%) | Acc10(%) | MAE(°) | 增量 |
|------|:--------:|:-------:|:--------:|:-----:|:---:|
| Baseline (ResNet+Stateformer) | 1.6 | 63.4 | 84.6 | 3.3 | — |
| + 时域注意力 (TD) | 1.9 | 66.5 | 86.8 | 3.2 | **+3.1** |
| + 频域注意力 (FD) | 1.9 | 69.2 | 87.4 | 3.1 | **+5.8** |
| + FA (TD+FD) | 2.2 | **71.8** | **88.1** | **2.7** | **+8.4** |

**关键发现**: 频域注意力贡献远大于时域注意力。说明在 DOA 任务中，**频率维度上哪几个 bin 对定位更重要，比时间维度上哪几帧更重要。**

### 消融 2: ShiftConv vs 大卷积核（表 IX）

| 配置 | Acc5(%) | 发现 |
|------|:------:|------|
| Conv31 (标准大核) | 71.2 | 基线 |
| Conv21 | 70.6 | 减小核 → 性能下降 |
| Conv15 | 70.4 | 继续下降 |
| **ShiftConv15** | **71.8** | **超越大核！且参数更少** |

**关键发现**: ShiftConv 用参数为零的移位操作补偿了小核的感受野损失。ShiftConv15 比 Conv31 还强。

### 消融 3: FFN 压缩策略（表 VIII）

| 配置 | Params(M) | Acc5(%) | 发现 |
|------|:--------:|:-------:|------|
| FFN(F) 压缩前端 | 2.4 | 69.1 | 前端的扩张FFN压缩了 |
| FFN(B) 压缩后端 | 2.4 | 70.2 | 后端的扩张FFN压缩了 |
| **SEConformer** | **2.0** | **70.9** | **最轻量，反而最好** |

**关键发现**: SE 机制不仅减少参数，还通过通道选择增强了特征。

### 消融 4: 整体计算效率对比（表 X）

| 方法 | Params(M) | FLOPs(G/s) | 单样本推理(ms) | Acc5(%) |
|------|:--------:|:----------:|:------------:|:-------:|
| CRNN-R | 0.7 | 2.2 | 88.3 | 52.5 |
| RC | 4.3 | 6.4 | 119.4 | 62.2 |
| ConBiMamba | 2.5 | **4.7** | **9.6** | 62.1 |
| IPDnet | 1.8 | 54.3 | 707.9 | 69.0 |
| TF-Mamba | 2.0 | 43.8 | 125.2 | 67.5 |
| **FA-Stateformer** | **2.2** | **4.7** | **9.5** | **71.8** |

**关键发现**: 
- 2.2M 参数适中 (比 RC 小一半)
- 4.7G FLOPs 极低 (仅为 IPDnet 的 1/10)
- 9.5ms 推理速度 (比 RC 快 12 倍，适合实时)
- Acc5=71.8% 是最高的

→ **FA-Stateformer 在精度-效率帕累托前沿上最优。**

## 七、整体结果

### 模拟数据 (双移动声源)

| 方法 | Acc5↑ | Acc10↑ | Acc15↑ | MAE↓ |
|------|:----:|:-----:|:-----:|:---:|
| CRNN-R | 52.5 | 75.0 | 84.4 | 3.7 |
| ResNet-Conformer | 62.2 | 84.6 | 91.4 | 3.3 |
| ConBiMamba | 62.1 | 83.5 | 90.8 | 3.3 |
| IPDnet | 69.0 | 86.8 | 91.6 | **2.8** |
| TF-Mamba | 67.5 | 86.3 | 92.0 | 3.2 |
| **FA-Stateformer** | **71.8** | **88.1** | **93.7** | **2.7** |

### LOCATA 真实数据

| 方法 | Task3 Acc10 | Task4 Acc10 | Task5 Acc10 | Task6 Acc10 |
|------|:----------:|:----------:|:----------:|:----------:|
| CRNN-R | 87.5 | 66.5 | 62.4 | 34.7 |
| RC | 94.4 | 68.2 | 76.4 | 55.6 |
| ConBiMamba | 96.6 | 69.0 | 75.1 | 56.1 |
| IPDnet | 94.9 | **88.1** | 76.8 | 58.5 |
| TF-Mamba | 94.7 | 86.4 | 76.4 | 56.1 |
| **FA-Stateformer** | **95.7** | **92.9** | **77.3** | **59.7** |

> Task6 最难（多移动声源+移动阵列），所有方法都掉到 60% 以下，FA-Stateformer 最好但仍有很大提升空间。

### 不同 SNR/RT60 下的鲁棒性

| 条件 | 趋势 |
|------|------|
| **SNR -10→20 dB** | Acc5: 56.2% → 76.5%，所有方法随 SNR 上升 |
| **RT60 0.2→0.8 s** | Acc5: 76.2% → 68.7%，所有方法随混响增大下降 |
| **FA-Stateformer vs 第二名** | 在所有 SNR/RT60 条件下都是第一 |

→ FA-Stateformer 的鲁棒性优势在全信噪比和全混响条件下都一致。

## 八、这个方向还剩什么问题没解决？（Future Work / Limitation）

1. **纯 DOA，没有 SED**: 只做定位不做检测，无法输出"什么声音在响" → 需要扩展为 SELD
2. **两麦克风 180° 限制**: 平面阵列只能覆盖 -90°~90° 方位角，多声源时前方/后方混淆
3. **多声源场景精度有限**: Task6 Acc10=59.7% 远低于 Task3 的 95.7% → 多动态声源仍是 open problem
4. **没有做域自适应**: 模拟→真实的 domain gap 没有显式处理（虽然有 LOCATA 测试）
5. **推理速度 9.5ms**: 虽然比 RC 快 12 倍，但距离严格的实时 (<5ms) 还有差距

## 九、跟哪篇像

**直接来源**: 
- FA 模块 → 来自作者自己的 FA3-Net (CIAP 2025) — 时频分离注意力
- Bi-Mamba+ → 来自 Bi-Mamba+ (Liang et al. 2024) — 双向 Mamba 增强版
- SEConformer → 来自 RC (Wang et al. 2023) + SE 机制压缩

**架构血统**:
- Conformer backbone → ResNet-Conformer (DCASE 2022 winner)
- Mamba + SA 协同 → ConBiMamba (替换 SA) 的反向设计（保留 SA 并加入 Mamba）
- 时频双维度建模 → TF-Mamba 的灵感延续
- ShiftConv → 来自图像领域的 shift 操作 (Cheng et al. 2020, Chen et al. 2019)


### 6. 本论文在库中的位置关联

| 维度 | 论文 | 关系 |
|------|------|------|
| **前身/基石** | [[SELD-Mamba 2024]] | 直接继承：BMamba → Bi-Mamba+ + Self-Attention 协同；Mamba 首次 SELD |
| **前身/基石** | [[DST Attention 2023]] | FA 模块 = DST 的 S+T 分离思想的纯 DOA 版——时频分离注意力特征聚合 |
| **前身/基石** | [[SELD CRNN 2018]] | 远端血统：CRNN DOA 基线 |
| **同分支竞品** | [[CST-former 2025]] | 同年 (2025)：CST 用 C+S+T Attention (SELD) → FA 用 Mamba+SA 协同 (纯 DOA) |
| **后续/扩展** | 无 | 2025 年纯 DOA 方向的最新 baseline——等待后续工作超越 |
| **跨分支类比** | [[LAM Self-Supervised DOA 2025]] | 同年纯 DOA，FA 有监督 → LAM 自监督，可对比泛化性 |

### 7. 江湖地位

```
2025 | 纯 DOA | FA模块 + Bi-Mamba+ + SA 协同 → Acc5=71.8%, 2.2M, 9.5ms 推理
          → 当前纯 DOA 方向的精度-效率帕累托最优
          → 频域注意力贡献 (+5.8%) 远大于时域 (+3.1%)——证明频率维度才是定位核心
```


---

*FA-Stateformer 代表了 DOA 估计从 Conformer → Mamba → Mamba+SA 协同的演进节点。它的核心贡献不是"提出一个新模块"，而是**系统地组合了 3 个已有的高效模块（FA + SEConformer + Bi-Mamba+）**，达到了精度-效率的最优平衡点。理解这篇，就能理解 2024-2025 年轻量化 DOA 估计的主流设计思路。*
