---
title: CRNN DOAnet 2017 — 首个 CRNN 多声源 DOA 估计
type: source
created: 2026-06-21
updated: 2026-06-21
tags:
  - doa-estimation
  - crnn
  - ambisonics
  - multi-source
  - sel-doa
source_type: paper
year: 2017
authors:
  - Sharath Adavanne
  - Archontis Politis
  - Tuomas Virtanen
affiliation: Tampere University of Technology / Aalto University
venue: EUSIPCO 2018
arxiv: "1710.10059"
related:
  - [[wiki_array/concepts/DOA 波达方向估计]]
  - [[SSL Survey 2021]]
---

# DOAnet — CRNN for Multi-Source DOA with Ambisonics

> Adavanne, Politis & Virtanen, 2017. EUSIPCO 2018

## 核心贡献

**首个使用 CRNN + Ambisonics 做多声源 DOA 估计**的工作，也是后续 DCASE SELD 基线的雏形。

## 与 Chakrabarty CNN 的关键区别

| 维度 | Chakrabarty CNN | 本文 DOAnet |
|---|---|---|
| **输入** | STFT 相位图 (多麦) | **FOA 4ch 幅度+相位谱** |
| **架构** | CNN only | **CNN + BiGRU** (CRNN) |
| **输出** | Sigmoid 37 类 | SPS 回归 + DOA 分类 (432 方向) |
| **声源数** | 需要已知 L | **自动检测**(threshold=0.5) |
| **角度** | 仅方位角 | 方位角+仰角 (3D) |
| **阵列** | ULA | **Ambisonics** (阵列无关) |
| **声源类型** | 语音 | DCASE 11 类声音事件 |

## 关键设计

- **SPS 中间输出**：网络先回归 MUSIC-like 空间伪谱，再从中分类 DOA——相当于让网络学习 MUSIC 的映射
- **614 方向采样**：球面均匀采样，10° 分辨率 (432 用于 DOA，仰角限制 ±60°)
- **序列建模**：L=100 帧 (2s) 输入，BiGRU 捕捉时序依赖

## 性能亮点

- 可处理最大 3 个同时重叠声源
- 对未见混响条件保持鲁棒 (Room 2: 80% size, Room 3: 60% size)
- 无需显式特征提取 (直接幅度+相位)


### 6. 本论文在库中的位置关联

| 维度 | 论文 | 关系 |
|------|------|------|
| **后续/扩展** | [[SELD CRNN 2018]] | 同一实验室 (Adavanne, Politis, Virtanen)：DOAnet 纯 DOA → SELDnet 联合 SED+DOA |
| **同分支竞品** | [[CNN DOA Estimation with Noise Training 2017]] | 同年 (2017)：CRNN+Ambisonics → CNN+相位图+ULA，分别走不同技术路线 |
| **同分支竞品** | [[Multi-Speaker Detection Likelihood 2017]] | 同年：SPS 学习 MUSIC-like 伪谱 → 似然编码高斯分布输出 |
| **跨分支类比** | [[MIMO-DoAnet 2022]] | CRNN 架构 + SPS 中间输出的继承：MIMO-DoAnet 也输出 GRU → SPS → 检测 |
| **跨分支类比** | [[SELD 声事件定位与检测]] | DOAnet 的本质是"去掉了 SED 头的 SELDnet"——SELD 任务的基础构件 |

### 7. 江湖地位

```
2017 | 纯 DOA | 首个 CRNN+Ambisonics 多声源 DOA → SELD CRNN 2018 的直系前身
          → SPS 学习 MUSIC 的思想被 MIMO-DoAnet (2022) 继承
          → 整个 DCASE SELD 方向的"种子论文"
```


---

*奠定了 CRNN+Ambisonics 做 SELD 的技术路线，CRNN 架构后来成为 DCASE Challenge 的标准基线。*
