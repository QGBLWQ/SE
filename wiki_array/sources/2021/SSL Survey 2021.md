---
title: SSL Survey 2021 — 深度学习声源定位综述
type: source
created: 2026-06-21
updated: 2026-06-21
tags:
  - survey
  - doa-estimation
  - source-localization
  - deep-learning
  - review
source_type: paper
year: 2021
authors:
  - Pierre-Amaury Grumiaux
  - Laurent Girin
  - Srdan Kitić
  - Alexandre Guérin
affiliation: "Nantes Université / Grenoble-INP GIPSA-lab / Orange Labs"
venue: arXiv (Journal submission)
arxiv: "2109.03465"
related:
  - [[wiki_array/concepts/DOA 波达方向估计]]
  - [[CNN DOA Estimation with Noise Training 2017]]
  - [[Multi-Speaker CNN DOA 2018]]
---

# A Survey of Sound Source Localization with Deep Learning Methods

> Pierre-Amaury Grumiaux et al., 2021. 综述 156 篇论文 (2011–2021)

## 一、综述概述

| 维度 | 详情 |
|---|---|
| **范围** | 156 篇论文，2011–2021 |
| **焦点** | 室内环境下的单/多声源定位 (DOA estimation) |
| **排除** | 音频-视觉方法、不涉及定位的纯 SELD |
| **组织方式** | 按架构 → 输入特征 → 输出策略 → 数据集 → 学习范式 |
| **特色** | 末尾提供 4 张总表（2011-18 / 2019 / 2020 / 2021），可按特性快速检索 |

## 二、传统 SSL 方法回顾（基线）

| 方法类别 | 代表方法 | 核心原理 | 缺陷 |
|---|---|---|---|
| **TDOA** | GCC-PHAT | 互相关 + 相位白化 | 混响、噪声敏感 |
| **波束扫描** | SRP-PHAT | GCC-PHAT 多麦克风扩展 | 计算量大 |
| **子空间** | MUSIC, ESPRIT | 信号/噪声子空间正交性 | 混响敏感 |
| **概率模型** | GMM/GMR | 混合模型 + EM 估计 | 计算密集 |
| **压缩感知** | Sparse Recovery | 空间稀疏性 + 凸优化 | 需要网格假设 |
| **ICA** | 频域 ICA | 统计独立性 | 混响下退化 |

## 三、神经网络架构全景

### 3.1 架构演进时间线

```
2011-2015: FFNN/MLP (浅层)
2015-2017: CNN (Hirvonen 2015 → Chakrabarty 2017)
2018-2019: CRNN 兴起 (Adavanne 2018 SELD 基线)
2019-2020: Residual + Attention + Transformer
2020-2021: Encoder-Decoder (AE/VAE/U-Net)
```

### 3.2 架构分类速查

| 架构类型 | 代表工作 | 关键特点 | 适用场景 |
|---|---|---|---|
| **FFNN/MLP** | Xiao 2015, Takeda 2016 | 简单、GCC/特征向量输入 | 早期浅层方法 |
| **CNN** | Chakrabarty 2017, 2019 | 相位图输入、噪声训练 | 单/多声源 DOA |
| **RNN** | Wang 2019 | LSTM/GRU 时序建模 | 单独使用少 |
| **CRNN** | **Adavanne 2018, 2019** | Conv+GRU，DCASE 基线 | **SELD 主流** |
| **Residual** | Yalta 2017, He 2018 | 跳跃连接、很深网络 | 高精度 |
| **Attention/Transformer** | Schymura 2021 (PILOT) | 自注意力、概率输出 | 多声源 |
| **Autoencoder** | Le Moing 2020 | 压缩表示、无监督 | 域适应 |
| **VAE** | Bianco 2020 | 生成式、半监督 | 小标注数据 |
| **U-Net** | Chazan 2019 | 编码器-解码器+跳跃连接 | 联合分离与定位 |

### 3.3 CRNN 范式（DCASE 基石）

Adavanne et al. (2018) 提出的 CRNN + FOA 架构成为 DCASE Challenge Task 3 的**事实标准**：
- 输入：FOA 4 通道幅度+相位谱
- 4 层 Conv (3×3, 64 kernels) + MaxPool → 2 层 BiGRU (64 units) → FC
- 多任务：SED (sound event detection) + DOA 估计
- 几乎所有后续 DCASE 参赛系统都在此基础上修改

### 3.4 Chakrabarty 等人的 CNN 演进

| 版本 | 关键变化 |
|---|---|
| WASPAA 2017 | 2×2 滤波器，单声源 |
| NeurIPS 2017 Workshop | 扩展到 2 声源，WDO 数据生成 |
| **IEEE 2019** (1807.11722) | 2×1 滤波器，M-1 层规则，多标签 Sigmoid |
| ICASSP 2019 | 引入 dilated convolution 减少层数 |

## 四、输入特征分类

| 特征类别 | 具体特征 | 代表工作 | 特点 |
|---|---|---|---|
| **通道间特征** | RTF, IPD, ILD | Bianco 2020 | 窄带相位/幅度差 |
| **互相关** | **GCC-PHAT**, GCC-NON | Xiao 2015 | 传统方法衍生 |
| **频谱** | **STFT 相位图**, log-mel, CQT | Chakrabarty 2017 | 端到端学习空间特征 |
| **Ambisonics** | **FOA** (4ch), HOA | Adavanne 2018, Perotin 2018 | 球形谐波分解 |
| **强度** | 声强向量 (pseudo-intensity) | Perotin 2018 | 物理直观 |
| **原始波形** | Multichannel waveform | Vera-Diaz 2018 | 真正端到端 |

> [!note] 趋势
> 多种特征**拼接**是常见做法（如 log-mel + GCC-PHAT + 强度向量），冗余信息反而有助于网络学习。

## 五、输出策略

| 策略 | 机制 | 适用场景 | 代表 |
|---|---|---|---|
| **分类** | Softmax / Sigmoid，离散角度网格 | 单/多声源 | Chakrabarty 2017, Adavanne 2018 |
| **回归** | 直接输出连续角度值或 (x,y,z) | 高精度需求 | Vera-Diaz 2018 |
| **混合** | 先分类粗定位 + 回归精调 | 折中 | Le Moing 2020 |
| **概率** | 高斯分布参数 (μ, Σ) | 不确定性量化 | Schymura 2021 (PILOT) |
| **TF Mask** | 输出每个 DOA 的时频掩蔽 | 联合分离 | Chazan 2019 |

## 六、训练范式

| 范式 | 说明 | 代表工作 |
|---|---|---|
| **全监督** | 主流方案：合成数据 + 已知 RIR/DOA 标签 | 多数 |
| **弱监督** | 仅用 DOA 标签，无 TF 级标签 | Opochinsky 2019 |
| **半监督** | 少量标注 + 大量无标注数据 | Bianco 2020 (VAE) |
| **无监督/自监督** | 无 DOA 标签 | Le Moing 2021 (对抗训练) |
| **多任务** | 联合 SED + DOA + 声源计数 | DCASE 系统 |

## 七、与本 Wiki 的关系

本综述为 `wiki_array/` 中后续论文摄入提供**分类框架**：

- **CRNN 类** (Adavanne 等) → SELD 子方向
- **CNN 相位图类** (Chakrabarty 等) → 已在 Wiki 中建立
- **Transformer/Attention 类** (PILOT 等) → 后续摄入
- **Encoder-Decoder 类** (U-Net 等) → 联合分离与定位

后续每篇论文摄入时，可以标注其在该分类体系中的位置。


### 6. 本论文在库中的位置关联

| 维度 | 论文 | 关系 |
|------|------|------|
| **前身/基石** | 156 篇论文 (2011-2021) | 提供了本 Wiki 所有 DOA 论文的组织框架 |
| **跨分支类比** | [[Robotics SSL Review 2025]] | 互补：SSL Survey 通用 SSL → Robotics Review 专攻机器人 |
| **跨分支类比** | [[SELD CRNN 2018]] | 综述中以 SELDnet 为核心 "CRNN 范式" 的代表 |

### 7. 江湖地位

```
2021 | 综述 | 156 篇深度 SSL 综述 → 本 Wiki 的分类框架基础
          → 被 Robotics SSL Review (2025) 在机器人方向上补充
```


---

*本综述是深度学习 SSL 领域最全面的文献整理，涵盖了 2011-2021 的全部主流方法。*
