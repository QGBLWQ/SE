---
title: Conformer
type: concept
created: 2026-08-03
updated: 2026-09-14
tags:
  - conformer
  - transformer
  - self-attention
  - convolution
  - speech-enhancement
sources: [Conformer 2020]
related:
  - [[wiki/concepts/膨胀卷积 Dilated Convolution]]
  - [[wiki/concepts/可学习编码器 Learnable Encoder]]
  - [[wiki/concepts/时序卷积网络 TCN]]
---

# Conformer

## 一句话记忆点

> Conformer = Transformer 的全局自注意力 + CNN 的局部模式提取。它同时看“远处的上下文”和“附近的连续结构”，因此特别适合语音这类既有长程依赖、又有局部时频规律的序列。

## 定义

Conformer 是面向语音序列建模提出的混合结构。Transformer 的自注意力能够建立任意两个时间帧之间的联系，但缺少卷积的局部归纳偏置；Conformer 在自注意力模块之外加入卷积模块，让模型显式学习局部连续模式。

一个标准 Conformer block 通常包含：

1. 前馈网络（Feed-Forward Module）；
2. 多头自注意力（Multi-Head Self-Attention, MHSA）；
3. 卷积模块（Convolution Module）；
4. 第二个前馈网络；
5. 层归一化和残差连接。

## 结构示意

```text
输入 x
  ↓
半步前馈网络 FFN
  ↓ + 残差
多头自注意力 MHSA —— 建模全局依赖
  ↓ + 残差
卷积模块 Conv —— 建模局部连续模式
  ↓ + 残差
半步前馈网络 FFN
  ↓
LayerNorm
  ↓
输出 y
```


### 架构图（直观理解）

![[wiki_array/assets/conformer-block-architecture.png]]

**看图时抓住三件事：**
- 两个 FFN / 2：前后各走半步，合起来完成一次完整的前馈变换。
- MHSA：建立远距离时间帧之间的联系，负责全局上下文。
- Convolution Module：通过 GLU、Depthwise Conv 等提取局部连续模式。
Conformer 使用两个半步 FFN，并在前后使用残差连接。可以抽象表示为：

$$
\mathbf{x}' = \mathbf{x} + \frac{1}{2}\operatorname{FFN}(\mathbf{x})
$$

$$
\mathbf{x}'' = \mathbf{x}' + \operatorname{MHSA}(\mathbf{x}')
$$

$$
\mathbf{x}''' = \mathbf{x}'' + \operatorname{Conv}(\mathbf{x}'')
$$

$$
\mathbf{y} = \operatorname{LayerNorm}\left(\mathbf{x}''' + \frac{1}{2}\operatorname{FFN}(\mathbf{x}''')\right)
$$

## 多头自注意力做了什么

自注意力通过 Query、Key 和 Value 计算不同时间帧之间的相关性：

$$
\operatorname{Attention}(Q,K,V)=\operatorname{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V
$$

它不要求信息必须沿时间轴逐步传播，因此一个时间帧可以直接关注很远之前或很远之后的语音片段。例如，当前帧可以利用整个音节、词语甚至更长上下文来判断某个局部结构是语音还是噪声。

## 卷积模块做了什么

Conformer 中的卷积模块通常包含以下步骤：

```text
LayerNorm
  ↓
Pointwise Conv
  ↓
GLU 门控
  ↓
Depthwise Conv
  ↓
BatchNorm
  ↓
激活函数
  ↓
Pointwise Conv
```

其中，Depthwise Conv 负责在每个通道内提取局部时间模式，GLU 用门控机制控制信息通过。卷积模块为注意力层补充了语音中的局部归纳偏置，例如：

- 相邻帧之间的连续变化；
- 谐波和共振峰结构；
- 音素边界和瞬态爆破音；
- 短时间范围内的噪声纹理。

## Conformer 与纯 Transformer 的区别

| | Transformer | Conformer |
|---|---|---|
| 全局依赖 | 自注意力 | 自注意力 |
| 局部模式 | 主要依靠注意力学习 | **额外使用卷积模块** |
| 语音归纳偏置 | 较弱 | **更强** |
| 长程建模 | 强 | 强 |
| 局部时频建模 | 需要间接学习 | 更直接 |
| 计算开销 | 注意力开销较高 | 注意力 + 卷积，结构更复杂 |

## 在语音增强中的作用

语音增强需要同时判断局部时频结构和较长时间范围内的语音连续性。Conformer 可以被放在编码器、掩码估计器或增强—识别联合网络中，用于：

- 区分持续噪声和具有语音结构的信号；
- 利用跨帧上下文恢复被噪声遮挡的语音；
- 同时处理幅度谱、复数谱或多通道空间特征；
- 建模语音增强与语音识别、声源定位之间的共享表示。

CMGAN 是一个典型例子：它把 Conformer 的局部卷积与全局注意力用于时频特征建模，再结合 MetricGAN 思路优化感知质量。

## 在实时系统中的限制

标准自注意力的计算和显存开销通常随序列长度平方增长：

$$
O(T^2D)
$$

其中 $T$ 是时间帧数，$D$ 是特征维度。因此，实时语音增强或端侧部署通常需要做以下改造：

- 使用局部注意力或分块注意力；
- 使用因果注意力，避免依赖未来帧；
- 缓存历史 Key/Value，减少重复计算；
- 降低特征维度和 block 数量；
- 使用深度可分离卷积和轻量化 FFN。

## Conformer 与膨胀卷积的关系

二者都能扩大模型的时间上下文，但方式不同：

| | 膨胀卷积 | Conformer |
|---|---|---|
| 核心机制 | 按固定间隔采样 | 自注意力动态选择相关帧 |
| 感受野 | 由卷积核和膨胀率决定 | 理论上可覆盖整个序列 |
| 局部建模 | 强 | 由卷积模块负责 |
| 全局建模 | 通过堆叠间接获得 | 由 MHSA 直接获得 |
| 实时性 | 更容易实现低延迟 | 需要局部/因果化优化 |

一种合理的组合方式是：前端使用普通卷积或膨胀卷积提取多尺度局部特征，后端使用 Conformer 融合长程上下文。这样可以在计算成本和建模能力之间取得平衡。

## 相关概念

- [[wiki/concepts/膨胀卷积 Dilated Convolution]] — 通过间隔采样扩大卷积感受野
- [[wiki/concepts/可学习编码器 Learnable Encoder]] — 可作为 Conformer 的时域输入前端
- [[wiki/concepts/时序卷积网络 TCN]] — 纯卷积式长程序列建模方法
- [[CMGAN 2022]] — Conformer 用于语音增强的代表性工作