---
title: Multi-Speaker DOA — 多声源 CNN 相位图 DOA 估计
type: source
created: 2026-06-21
updated: 2026-06-21
tags:
  - doa-estimation
  - multi-speaker
  - cnn
  - microphone-array
  - phase-processing
  - noise-training
  - w-disjoint-orthogonality
source_type: paper
year: 2018
authors:
  - Soumitro Chakrabarty
  - Emanuël A. P. Habets
affiliation: International Audio Laboratories Erlangen
venue: IEEE Journal (Selected Topics in Signal Processing)
arxiv: "1807.11722"
code:
related:
  - [[CNN DOA Estimation with Noise Training 2017]]
  - [[wiki_array/concepts/DOA 波达方向估计]]
  - [[wiki_array/concepts/STFT相位图与相位信息]]
  - [[wiki_array/concepts/SRP-PHAT]]
---

# Multi-Speaker DOA Estimation Using Deep Convolutional Networks Trained with Noise Signals

> Soumitro Chakrabarty, Emanuël A. P. Habets, AudioLabs Erlangen, IEEE, 2018 (extended from WASPAA 2017)
>
> arXiv: [1807.11722](https://arxiv.org/abs/1807.11722)

## 一、研究任务与对象

| 维度 | 详情 |
|---|---|
| **任务** | **多声源** DOA 估计（2+ 个同时活跃说话人） |
| **与上篇关系** | [[CNN DOA Estimation with Noise Training 2017|WASPAA 2017]] 的扩展：单声源 → 多声源 |
| **方法类型** | CNN 多标签分类 (multi-label multi-class) |
| **阵列类型** | ULA，M=4，间距 8cm（主实验）；也测试了 M=6, M=8 |
| **DOA 范围** | 0°–180°，5° 分辨率 → 37 类 |
| **采样率** | 16 kHz，DFT 长度 512，K=257 频率 bin |
| **块长度** | 50 帧 (0.8s) 的块级平均 → 最终 DOA 估计 |

## 二、核心创新与增量

相比于 [[CNN DOA Estimation with Noise Training 2017|WASPAA 2017 单声源版]]，本文的核心增量：

| 增量 | WASPAA 2017 | 本文 (2018) |
|---|---|---|
| **声源数** | 单声源 | **多声源**（2+个同时活跃） |
| **输出策略** | Softmax 多分类 | **Sigmoid 多标签**（binary relevance） |
| **滤波器** | 2×2（跨频率+跨麦克风） | **2×1**（仅跨麦克风，频率 bin 独立） |
| **数据生成** | 单声源噪声训练 | **W-Disjoint Orthogonality 拼接** |
| **推理** | 逐帧 argmax | **块级平均 + Top-L 选取** |
| **最优层数** | 未探讨 | **证明 M-1 卷积层最优** |
| **基线对比** | SRP-PHAT | **SRP-PHAT + MUSIC** |
| **噪声泛化** | 白噪声 | **白噪声 + 未见 babble 噪声** |

## 三、技术方法

### 3.1 多标签分类框架

DOA 估计被建模为 **I 类多标签分类**（I=37 类，每类对应一个 DOA 角度），使用 **Binary Relevance** 方法：

- 输出层：**I 个 Sigmoid 单元**（而非 Softmax），每个独立判断"该角度是否有声源"
- 损失函数：**二元交叉熵** (Binary Cross-Entropy)，每个输出神经元独立优化
- 假设：声源位置相互独立 (independent source DOA model)

### 3.2 块级 DOA 估计

逐帧 CNN 输出 $p(\theta_i|\Phi_n)$，在 $N$ 帧的块上平均：

$$p_n(\theta_i) = \frac{1}{N} \sum_{n}^{n+N-1} p(\theta_i | \Phi_n) \tag{2}$$

已知声源数 $L$，取 $L$ 个最高概率的 DOA 类作为最终估计。

> [!note] 关键设计
> 本文假设 $L$ 已知。也可通过峰值检测自动估计声源数，但留待未来工作。

### 3.3 CNN 架构变化

```
Input (4×257 Phase Map)
    │
    ▼
Conv2D (64 filters, 2×1) → ReLU   ← 仅跨麦克风, 不跨频率!
    │  
    ▼
Conv2D (64 filters, 2×1) → ReLU
    │  
    ▼
Conv2D (64 filters, 2×1) → ReLU   ← M-1 = 3 层 (M=4)
    │  ↓ Flatten → 1×K feature maps
    ▼
FC (256 units) → ReLU → Dropout(0.5)
    │
    ▼
FC (256 units) → ReLU → Dropout(0.5)
    │
    ▼
Output: 37 Sigmoid units (多标签)
```

**为什么用 2×1 而非 2×2**：多声源场景下，相邻频率 bin 可能被不同说话人主导（W-Disjoint Orthogonality），因此不跨频率学习，仅学习麦克风间的相位相关性。

### 3.4 M-1 卷积层最优性（实验证明）

| 阵列 | 最优层数 | 原因 |
|---|---|---|
| M=4 | 3 层 (M-1) | 2×1 滤波器每次向相邻麦克风扩展感受野，M-1 层后覆盖所有麦克风对 |
| M=6 | 5 层 (M-1) | 同上 |
| M=8 | 7 层 (M-1) | 同上 |

减少层数 → 特征图尺寸增大 → 参数量**反而增加**且性能下降。

### 3.5 多声源噪声训练数据生成（WDO 方法）

利用语音信号的 **W-Disjoint Orthogonality (WDO)** 假设——两个同时说话人的 STFT 在单个 TF bin 上几乎不重叠：

1. 为每个 DOA 生成单声源训练信号（噪声 + RIR 卷积）
2. 将两个不同 DOA 的训练信号沿时间轴**拼接**
3. **逐频率子带**随机打乱时间帧（所有麦克风同步打乱）
4. 得到每帧约 50% bin 来自 $\theta_1$、50% 来自 $\theta_2$ 的混合信号

**关键**：打乱后每个 TF bin 的相位对所有麦克风仍来自**同一方向**，CNN 学习的是空间关系而非信号混合模式。

## 四、关键公式

### Eq. 2 — 块级后验概率平均

$$p_n(\theta_i) = \frac{1}{N} \sum_{n}^{n+N-1} p(\theta_i | \Phi_n)$$

### Eq. 3 — 平均绝对误差 (MAE)

$$\text{MAE}(^\circ) = \frac{1}{LC} \sum_{c=1}^{C} \sum_{l=1}^{L} |\theta_l^c - \hat{\theta}_l^c|$$

### Eq. 4 — 定位准确率

$$\text{Acc.}(\%) = \frac{\hat{C}_{\text{acc.}}}{C} \times 100$$

- "准确" = 所有声源的估计 DOA 与真实 DOA 偏差均 ≤ 5°

## 五、实验结果

### 5.1 未见声学环境泛化 (Table 3)

> 训练：5 个房间 (RT60 0.2-0.8s) × 7 阵列位置 × 2 距离 → 测试：2 个新房间

| 方法 | Room1 10dB | Room1 20dB | Room1 30dB | Room2 10dB | Room2 30dB |
|---|---|---|---|---|---|
| **Proposed** MAE/Acc | 14.5°/73.5% | 3.5°/93.2% | 1.5°/98.1% | 16.8°/63.4% | 2.7°/96.3% |
| MUSIC | 23.3°/43.4% | 16.2°/63.4% | 13.4°/71.3% | 27.1°/37.7% | 16.6°/59.6% |
| SRP-PHAT | 26.7°/37.7% | 22.7°/49.3% | 18.9°/60.4% | 29.2°/28.2% | 21.6°/48.3% |

### 5.2 未见噪声类型泛化 (Table 4)

> 测试加入 **babble 噪声**（训练中未见过），同时有 40dB 白噪声

| 方法 | Room1 -5dB babble | Room1 +5dB babble | Room2 -5dB babble | Room2 +5dB babble |
|---|---|---|---|---|
| **Proposed** MAE/Acc | 5.0°/91.9% | 1.1°/98.7% | 7.1°/82.9% | 2.0°/97.5% |
| MUSIC | 23.9°/39.2% | 16.3°/59.9% | 25.9°/36.3% | 18.1°/52.1% |

> [!note] 关键发现
> 即使 CNN 从未见过 babble 噪声，在 -5dB 时仍达 ~90% 准确率。原因：babble 主要能量在低频，CNN 的卷积核从全频带学习，高频 SNR 高的区域可补偿低频信息不足。

### 5.3 真实 RIR 实测 (Table 5)

> Bar-Ilan 数据库，8 麦 ULA 取中间 4 麦，RT60 0.16-0.61s

CNN 在所有条件下优于 MUSIC 和 SRP-PHAT，最差情况 (2m, RT60=0.61s) 仍有 80.2% 准确率。

### 5.4 动态声源数场景 (Fig. 7)

6s 场景分 4 段：1 源 → 2 源 → 3 源 → 1 源。虽然 CNN 仅训练为估计最多 2 源的帧级概率，但在块级仍能清晰显示 3 个峰值。证明了框架对动态变化声源数的适应能力。

## 六、可复现性

| 项目 | 详情 |
|---|---|
| **训练数据量** | ~1240 万帧（上篇：560 万） |
| **训练房间数** | 5 个房间 × 7 阵列位置 × 2 距离 (1m, 2m)，RT60 0.2-0.8s |
| **训练 SNR** | 0-30 dB 均匀采样 |
| **测试语音** | LIBRI 语料库，5 组双人混合，每组 2s |
| **优化器** | Adam，lr=0.001，batch=512 |
| **正则化** | Dropout 0.5（Conv 层后 + FC 层后） |
| **框架** | Keras |
| **采样率** | 16 kHz（上篇未指定） |
| **DFT** | 512 点，50% 重叠，K=257（上篇：256 点，K=129） |
| **阵列间距** | 8cm（上篇：3cm） |

> [!question] 不确定性
> - 代码未开源
> - 测试仅在已知声源数 L 的条件下进行，实际部署需配合声源计数模块
> - WDO 假设对非语音信号可能不成立
> - 未给出计算复杂度 (Mflops/RTF)

## 七、贡献与局限

### 核心贡献

1. **多声源扩展**：将相位图 CNN 框架从单声源推广到多声源，提出 WDO 噪声训练方法
2. **M-1 卷积层规则**：实验证明对小滤波器 (2×1)，最优卷积层数 = 麦克风数-1
3. **未见噪声类型泛化**：证明 multi-condition training 使网络对未见噪声（babble）也鲁棒
4. **动态声源数适应**：仅训练 2 源，块级可处理 3 源
5. **全面基线对比**：同时对比 SRP-PHAT 和 MUSIC

### 局限性

1. 假设声源数 L 已知
2. 仅限 ULA（均匀线阵）
3. 块级平均引入了 0.8s 的延迟
4. 5° 离散分辨率可能不够精细


### 6. 本论文在库中的位置关联

| 维度 | 论文 | 关系 |
|------|------|------|
| **前身/基石** | [[CNN DOA Estimation with Noise Training 2017]] | 直接扩展 (同组)：单源 Softmax → 多源 Sigmoid；2×2→2×1 滤波器 |
| **同分支竞品** | [[CRNN DOAnet 2017]] | 同方向不同架构：CNN 相位图+ULA → CRNN+Ambisonics |
| **同分支竞品** | [[Multi-Speaker Detection Likelihood 2017]] | 同年 (2018 ICRA)：似然编码 vs Sigmoid 多标签——两种不同的多声源输出策略 |
| **同分支竞品** | [[ISSL 2022]] | 后续 (2022)：都解决多声源问题，但 ISSL 用迭代减法消除声源间干扰 |
| **同分支竞品** | [[MIMO-DoAnet 2022]] | 后续 (2022)：MIMO 并行多输出比逐类 Sigmoid 在解声源间干扰上更强 |
| **跨分支类比** | [[SELD CRNN 2018]] | 同年 (2018)：SELDnet 的 SED 头也是 Sigmoid 多标签——但加了 DOA 回归 |

### 7. 江湖地位

```
2018 | 纯 DOA | 相位图 CNN 多声源版 + M-1 层规则 + WDO 数据生成
          → 被 CRNN/SELD 线路取代——但 M-1 层规则和 WDO 拼接方法仍被引用
          → 是库里直接有复现代码的唯一论文 (outputs/chakrabarty_repro/)
```


---

*Chakrabarty & Habets 系列第二篇，将 CNN 相位图 DOA 从单声源推进到多声源场景，是该方向的代表作。*
