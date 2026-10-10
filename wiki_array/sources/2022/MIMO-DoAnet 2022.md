---
title: MIMO-DoAnet 2022 — 多输出 DOA 网络（解决阈值和角度假设问题）
type: source
created: 2026-06-21
updated: 2026-06-21
tags:
  - doa-estimation
  - mimo
  - spatial-spectrum
  - cRF
  - unknown-source-count
source_type: paper
year: 2022
authors:
  - Haoran Yin
  - Meng Ge
  - Yanjie Fu
  - Gaoyan Zhang
  - Longbiao Wang
  - Lei Zhang
  - Lin Qiu
  - Jianwu Dang
affiliation: Tianjin University / Huawei / JAIST
venue: Interspeech 2022
arxiv: "2207.07307"
related:
  - [[ISSL 2022]]
  - [[wiki_array/concepts/DOA 波达方向估计]]
---

# MIMO-DoAnet — Multi-Input Multi-Output DOA Network

> Yin, Ge, Fu et al., Tianjin University / Huawei, Interspeech 2022

## 核心问题

传统 **MISO** (多输入单输出) DOA 网络有两大固有问题：

1. **阈值问题**：空间谱峰值检测依赖经验阈值，场景变化不稳定
2. **角度假设问题**：两个相近声源 (< 波束宽度)，第一个峰值的波束掩蔽第二个

## 核心创新：MIMO 替代 MISO

```
6ch 波形 → STFT → [Mag, IPD]
              ↓
      GRU cRF Estimator
       ↓              ↓
    cRF_S (语音)   cRF_N (噪声)
       ↓              ↓
    协方差 Φ_S     协方差 Φ_I
       ↓              ↓
       └──────┬───────┘
              ↓
      GRU SPS Estimator (×N)
       ↓       ↓       ↓
     SPS_1   SPS_2   SPS_N  (每个输出独立检测一个声源)
```

**cRF (complex-valued Ratio Filter)**：在 STFT 域估计复数比率滤波器，将混合信号分离为独立声源。

## 关键优势

| 问题 | MISO | MIMO-DoAnet |
|---|---|---|
| 阈值 | 检测"有几个活跃声源" | 检测"该输出是否有声源"(更简单) |
| 角度假设 | 主峰掩蔽旁峰 | 各输出独立，无相互干扰 |
| 近距离声源 | 无法区分 | 可区分 (cRF 分离) |
| 延迟 | 取决于模型 | 32ms 输入 + GRU → 低延迟 |

## 实验结果

| 场景 | F1 相对提升 | F1 绝对提升 |
|---|---|---|
| 3 声源 | +18.6% | +13.3% |
| 4 声源 | +34.4% | +20.2% |

在小角度间距测试集上，MIMO 显著优于 MISO 基线。

## 与 ISSL 的关系

ISSL (迭代减法) 和 MIMO-DoAnet (并行多输出) 是同一团队从两个不同角度解决未知声源数问题的方案。MIMO-DoAnet 的优势在于**消除了声源间的相互干扰**。


### 6. 本论文在库中的位置关联

| 维度 | 论文 | 关系 |
|------|------|------|
| **前身/基石** | [[CRNN DOAnet 2017]] | CRNN+SPS 架构的血统继承——cRF 是 MIMO-DoAnet 的核心创新 |
| **同分支竞品** | [[ISSL 2022]] | 同一团队 (Tianjin Uni)：MIMO 并行多输出 → ISSL 迭代减法，互补 |
| **同分支竞品** | [[Multi-Speaker CNN DOA 2018]] | Sigmoid 多标签 vs MIMO——MIMO 的声源间无干扰是核心优势 |
| **跨分支类比** | [[DBnet Beamforming 2020]] | cRF (复数比率滤波器) 和 DBnet 的联合优化波束成形有概念相通之处 |

### 7. 江湖地位

```
2022 | 纯 DOA | MIMO 多输出 + cRF 复数滤波器 → 4声源 F1 提升 34.4%
          → 和 ISSL 互补，Tianjin Uni 团队在未知声源数方向的两开花
```


---
