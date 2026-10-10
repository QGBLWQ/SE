---
title: DeepASA 2025 — 面向对象的多功能听觉场景分析网络
type: source
created: 2026-06-21
updated: 2026-06-21
tags:
  - auditory-scene-analysis
  - mimo
  - source-separation
  - seld
  - multi-task
  - transformer
source_type: paper
year: 2025
authors:
  - Dongheon Lee
  - Younghoo Kwon
  - Jung-Woo Choi
affiliation: KAIST
venue: NeurIPS 2025
arxiv: "2509.17247"
code: https://huggingface.co/spaces/donghoney22/DeepASA
related:
  - [[wiki_array/concepts/SELD 声事件定位与检测]]
  - [[wiki_array/concepts/波束成形 Beamforming]]
  - [[CST-former 2025]]
---

# DeepASA — Object-Oriented Multi-Purpose Network for Auditory Scene Analysis

> Lee, Kwon & Choi, KAIST, NeurIPS 2025

> [!warning] PDF 转换状态
> MinerU 解析失败（-60010），以下内容来自 WebSearch + HuggingFace 获取的信息。建议手动查看原 PDF 补充细节。

## 核心贡献

**一个统一的 MIMO 框架**同时处理 5 个任务：源分离、去混响、SED、音频分类、DOA 估计。

## 三大创新机制

| 机制 | 全称 | 作用 |
|---|---|---|
| **OOP** | Object-Oriented Processing | 将听觉特征封装为面向对象的表示 |
| **CoI** | Chain-of-Inference | 多任务级联推理链 |
| **TCM** | Temporal Coherence Matching | 时间一致性匹配，修复早期分离错误 |

## 架构

```
多通道音频 → Dynamic Temporal Kernel Feature Extractor
                         ↓
                 Transformer Aggregator
                         ↓
                 Object Separator → Per-Object Features
                         ↓
        ┌────────────────┼────────────────┐
        ↓                ↓                ↓
   Source Sep      SED + DOA         Classification
   Dereverb
```

## 与传统 Track-wise 方法的区别

传统 SELD 方法的 track-wise 设计（如 EINV2）存在**参数关联歧义**（哪个 track 对应哪个声源）。DeepASA 的 object-centric 表示天然解决了这个问题。

## 评测

| 数据集 | 内容 |
|---|---|
| ASA2 | 听觉场景分析 |
| MC-FUSS | 多通道远场语音分离 |
| STARSS23 | 真实场景 SELD (DCASE) |

在**所有任务上**达到 SOTA。


### 6. 本论文在库中的位置关联

| 维度 | 论文 | 关系 |
|------|------|------|
| **前身/基石** | [[CST-former 2025]] | 同一实验室 (KAIST, Jung-Woo Choi)，CST 做 SELD → DeepASA 做 5 任务统一 |
| **前身/基石** | [[CRNN DOAnet 2017]] | Adavanne-Politis-Virtanen line 的 SELD 任务 + EINV2 的 track-wise 设计 |
| **同分支竞品** | [[EINV2]] | EINV2 track-wise 有关联歧义 → DeepASA 用 object-centric 天然解决 |
| **同分支竞品** | [[ResNet-Conformer SELD 2025]] | ResNet-Conformer 基于 EINV2 → DeepASA 是 EINV2 的范式替代 |
| **跨分支类比** | [[DBnet Beamforming 2020]] | 都做多任务统一：DBnet DOA+分离 → DeepASA 分离+去混响+SED+分类+DOA |

### 7. 江湖地位

```
2025 | 统一听觉分析 | 面向对象五任务统一 (NeurIPS 2025) → 范式转变：从"分任务独立"到"对象驱动统一"
          → 来自 KAIST Choi 实验室，和 CST-former 是同一血统的两个分支
```


---

*代表了从"分任务独立模型"到"统一多任务对象驱动模型"的范式转变。与 [[CST-former 2025|CST-former]] 同出 KAIST Choi 实验室。*
