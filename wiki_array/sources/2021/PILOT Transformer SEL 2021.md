---
title: PILOT 2021 — Transformer 概率声事件定位
type: source
created: 2026-06-21
updated: 2026-06-21
tags:
  - seld
  - transformer
  - self-attention
  - probabilistic
  - gaussian
source_type: paper
year: 2021
authors:
  - Christopher Schymura
  - Benedikt Bönninghoff
  - Tsubasa Ochiai
  - Marc Delcroix
  - Keisuke Kinoshita
  - Tomohiro Nakatani
  - Shoko Araki
  - Dorothea Kolossa
affiliation: Ruhr University Bochum / NTT
venue: Interspeech 2021
arxiv: "2106.03903"
related:
  - [[SELD CRNN 2018]]
  - [[SSL Survey 2021]]
---

# PILOT — Probabilistic Localization of Sounds with Transformers

> Schymura et al., Ruhr Uni Bochum / NTT, 2021

## 核心创新

1. **Transformer 替代 RNN**：用自注意力机制替代传统 CRNN 中的 BiGRU 层
2. **概率输出**：DOA 估计输出为**多元高斯分布** $(μ, Σ)$，而非点估计——天然附带不确定性量化
3. 在三个公开数据集上**全面超越**所有对比方法

## 架构

```
STFT (K帧 × L频率bin × 2C通道)
    ↓
CNN Feature Extraction
    ↓
Positional Encoding
    ↓
Transformer Encoder (Self-Attention)
    ↓
┌───────────────┬────────────────┐
↓               ↓
γ_k,n (活动指示)   (μ_k,n, Σ_k,n) 高斯分布参数
(声事件是否存在)   (位置+不确定性)
```

## 概率输出的意义

| 方法 | 输出 | 不确定性 |
|---|---|---|
| CRNN 分类/回归 | 点估计 | ❌ |
| 传统贝叶斯方法 | 概率分布 | ✅ 但计算密集 |
| **PILOT** | 高斯分布 (μ, Σ) | ✅ 前馈计算 |

- Σ 矩阵的大特征值 → 方向不确定（可能噪声大或混响强）
- 可用于下游任务的置信度加权

## 为什么 Transformer 比 RNN 好

- 并行训练快
- 长程依赖建模能力更强（不受 gradient vanishing 限制）
- 自注意力天然适合多声源间的空间关系建模


### 6. 本论文在库中的位置关联

| 维度 | 论文 | 关系 |
|------|------|------|
| **前身/基石** | [[SELD CRNN 2018]] | 直接替换 SELDnet 的 BiGRU 为 Transformer Encoder；保留了 CNN 前端和多任务头 |
| **后续/扩展** | [[CST-former 2025]] | PILOT 只做了时序维 Self-Attention → CST 做了 C+S+T 三维注意力 |
| **同分支竞品** | [[DST Attention 2023]] | 同年（2021/2023），都是改进序列建模，但 DST 走频率保留+S+T注意力 → PILOT 走 Transformer+概率输出 |
| **跨分支类比** | [[FA-Stateformer 2025]] | 都用了 Attention，但 FA 将其用于时频分离特征聚合而非直接做序列建模 |

### 7. 江湖地位

```
2021 | SELD | Transformer 首次用于 SELD + 概率输出 (μ,Σ) → 被 CST(三维注意力) 和 FA-Stateformer(Mamba+SA) 超越
          → 概率输出的思想在后续 DCASE 工作中未被广泛采用（ACCDOA 回归更流行）
```


---

*将 NLP 领域 Transformer 成功适配到音频空间定位的标志性工作。*
