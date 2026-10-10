---
title: CLIP SSL 2025 — 基于 CLIP 的自监督视听声源定位
type: source
created: 2026-06-21
updated: 2026-06-21
tags:
  - audio-visual
  - self-supervised
  - clip
  - cross-modal
  - sound-source-localization
source_type: paper
year: 2025
authors:
  - Sooyoung Park
  - Arda Senocak
  - Joon Son Chung
affiliation: KAIST
venue: IJCV 2025
arxiv: "2505.05343"
related:
  - [[wiki_array/concepts/DOA 波达方向估计]]
---

# CLIP-based Self-Supervised Sound Source Localization

> Park, Senocak & Chung, KAIST, 2025

> [!note] 方向说明
> 本文属于**视听声源定位** (Audio-Visual SSL)——定位图像/视频中哪个物体在发出声音，而非阵列信号处理的 DOA 估计。列入 Wiki 是因为代表了"声源定位"的另一重要分支。

## 核心创新

利用 **CLIP** 预训练模型的跨模态对齐能力，实现无需文本输入的自监督视听声源定位。

## 方法

```
音频 → Audio Encoder → Audio Tokens
                            ↓
                  CLIP Text Encoder → Audio-Driven Embeddings
                            ↓
                  生成发声区域 Mask → 提取视觉特征
                            ↓
                  对比学习损失 (Audio ↔ Visual)
```

## 关键优势

- **无需文本标签**或类别标注（音频驱动，不依赖 text prompt）
- 利用 CLIP 的预训练视觉-语言对齐先验 → 更完整紧凑的定位
- 可选的 LLM 蒸馏增强对齐

## 评估

5 个任务全覆盖：单源/多源/分割/交互/鲁棒性，**全面超越** state-of-the-art，零样本泛化强。


### 6. 本论文在库中的位置关联

| 维度 | 论文 | 关系 |
|------|------|------|
| **跨分支类比** | [[SSL Survey 2021]] | SSL Survey 不包含视听方法 → CLIP SSL 是另一个分支 |
| **跨分支类比** | [[LAM Self-Supervised DOA 2025]] | 同年 (2025) 自监督：CLIP 视听跨模态 → LAM 纯音频声学映射 |
| **跨分支类比** | [[Robotics SSL Review 2025]] | 机器人应用场景有交集——视听 SSL 在 HRI 中有天然优势 |

### 7. 江湖地位

```
2025 | 视听 SSL | CLIP 跨模态 + 自监督 → 5 任务全 SOTA
          → 属于"视听定位"的并行分支，和"阵列 DOA"互补而不竞争
```


---

*将大规模视觉-语言模型的跨模态知识迁移到视听声源定位，代表了该方向的前沿范式。*
