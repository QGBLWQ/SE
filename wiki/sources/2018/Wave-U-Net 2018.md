---
title: Wave-U-Net — 波形域 U-Net 音源分离
type: source
created: 2026-07-06
updated: 2026-07-13
tags:
  - source-separation
  - u-net
  - waveform-domain
  - end-to-end
source_type: paper
year: 2018
authors: Daniel Stoller, Sebastian Ewert, Simon Dixon
venue: ISMIR 2018
related:
  - [[Conv-TasNet 2019]]
  - [[Demucs 2019]]
  - [[SEGAN 2017]]
---

```yaml
- 论文: [Wave-U-Net](2018)
  ├── 要解决什么问题: 摆脱 STFT 频域分离的相位和窗函数限制，直接在原始波形上做音源分离
  ├── 核心方法: 1D U-Net；编码器逐层下采样，解码器逐层上采样，skip connection 保留高分辨率细节
  ├── 属于哪个分支: 音源分离 / 波形域端到端 / U-Net
  ├── 输入/输出: 混合波形 → 各源波形
  ├── 关键trick: 把图像分割中的 U-Net 迁移到一维音频波形，多尺度处理音频结构
  ├── 数据集: 音乐源分离数据集，具体设置需回看原文
  ├── 对比了谁: 传统频域分离、后续可与 Conv-TasNet/Demucs 比较
  ├── 性能上限: 当前笔记未记录完整指标
  ├── 参数量: 当前笔记未记录
  ├── 消融关键发现: 旧笔记未记录；skip connection 和多尺度深度是关键
  ├── 遗留问题(你的机会): 长程依赖不足、实时性和重建细节受限，后续被 Conv-TasNet/Demucs 推进
  └── 跟哪篇像: [[Demucs 2019]]、[[Conv-TasNet 2019]]、[[SEGAN 2017]]
```

# Wave-U-Net: A Multi-Scale Neural Network for End-to-End Audio Source Separation

> Stoller, Ewert, Dixon, Queen Mary University of London, ISMIR 2018。

## 1. 动机：他们为什么这么做？（motivation）

传统音源分离多在 STFT 频谱上估计 mask，再用混合相位重建。这个范式和语音增强一样受限于固定窗函数、频率-时间分辨率折中以及相位处理。Wave-U-Net 的动机是直接在波形上建模，让网络自己学习多尺度音频表示。

它借鉴医学图像分割中的 U-Net：编码器提取多尺度特征，解码器恢复原始分辨率，跳跃连接保留细节。音频虽然是一维信号，但同样存在局部纹理和全局结构，因此 U-Net 可以自然迁移。

## 2. 前人局限：之前的人怎么做不了？（limitation → gap）

频域方法的局限主要有三点：

- 依赖混合相位，源信号相位无法准确恢复；
- STFT 分辨率固定，难以同时兼顾瞬态和长音；
- mask 估计本身绕了一圈，不能端到端优化波形重建质量。

Wave-U-Net 填补的 gap 是：证明不经过 STFT，也能用多尺度卷积直接从波形分离音源。

## 3. 核心 Trick：这个做法关键在哪？

核心结构：

```text
混合波形
  → Encoder Conv1D × N（逐层下采样）
  → bottleneck
  → Decoder TransposedConv1D × N（逐层上采样）
  → 分离波形
     ↑ skip connection 连接同尺度 encoder 特征
```

关键 trick 是**一维多尺度 U-Net + skip connection**。下采样让模型看到更长上下文，上采样恢复时域分辨率，跳连避免细节在瓶颈中丢失。

## 4. 实验里哪个消融最关键？

当前旧笔记未记录原文消融数值。按模型结构，最关键的消融应是：

- 是否使用 skip connection；
- 下采样层数 / 感受野大小；
- 输出方式是直接预测源波形还是预测残差；
- 与频域 mask 方法比较；
- 与后续 Demucs/Conv-TasNet 比较。

> [!question] 待补
> 原论文的 SDR/SIR/SAR、层数和消融表需要回看原 PDF。

## 5. 这个方向还剩什么问题没解决？（future work / limitation）

- U-Net 的卷积感受野仍有限，长程依赖不如 TCN、DPRNN、Transformer；
- 音乐源分离和语音分离的结构差异较大；
- 波形域模型的可解释性弱于 STFT；
- 后续 [[Conv-TasNet 2019]] 用可学习编码器 + TCN 更系统地解决时域语音分离。

## 6. 本论文在库中的位置关联（cross-reference matrix）

| 维度 | 论文 | 关系 |
|---|---|---|
| 前身/基石 | [[SEGAN 2017]] | 都是早期波形域端到端音频处理；SEGAN 做增强，Wave-U-Net 做分离 |
| 后续/扩展 | [[Demucs 2019]] | 继承 U-Net 思路并增强音乐源分离能力 |
| 后续/扩展 | [[Conv-TasNet 2019]] | 同为波形域分离，但 Conv-TasNet 用可学习编码器 + TCN 取代 U-Net |
| 跨分支类比 | [[可学习编码器 Learnable Encoder]] | Wave-U-Net 仍是卷积多尺度；Conv-TasNet 才真正把编码基函数任务化 |

## 7. 一句话总结“江湖地位”

```text
2018 | 音源分离 | 把 U-Net 搬到波形域的早期代表 → 被 Demucs 和 Conv-TasNet 分别沿音乐/语音方向推进
```
