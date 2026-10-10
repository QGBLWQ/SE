---
title: SlowFast-SSM
type: entity
created: 2026-09-16
updated: 2026-09-16
tags:
  - model
  - slow-fast
  - state-space-model
  - low-latency
  - speech-enhancement
  - paper-claimed-causal
  - sample-level-latency
sources:
  - [[wiki_low_latency/sources/2024/SlowFast-SSM 2024]]
related:
  - [[wiki_low_latency/sources/2024/SlowFast-SSM 2024]]
  - [[wiki_low_latency/concepts/2411.02019-slowfast-ssm]]
  - [[wiki_low_latency/entities/RT-SEMamba]]
  - [[wiki_low_latency/concepts/2409.10358-ultra-low-latency-benchmark]]
---

# SlowFast-SSM

## 定义

SlowFast-SSM 是 Cheng 等人在 2411.02019 中提出的低时延时域语音增强框架。它把增强器拆成低帧率的 Slow branch 和高帧率的 Fast branch：前者分析较长上下文并生成声学环境表征，后者在目标短 hop 上推进轻量 SSM。本文的 SSMM 接口让 Slow branch 直接调制 Fast SSM 的状态转移矩阵和输入门控。

## 管线

~~~text
时域 noisy speech
        │
        ├── Slow branch：大窗口、ΔS=δΔF、FC + 4×64-unit GRU + FC
        │                     │
        │                     └── εjS → [AjS, gjS]
        │
        └── Fast branch：LF、ΔF、高频输入 ──> FIN
                              │
                hFi = AjS hF(i-1) + gjS ⊙ FIN(xFi)
                              │
                            FOUT
                              │
                 enhanced fast frames → OLA → 输出语音
~~~

## 核心配置

| 项目 | 论文配置 |
|---|---|
| 采样率 | 16 kHz |
| 2 ms fast branch | L_F=32 samples、Δ_F=16 samples、H=32 |
| reuse factor | δ∈{1,2,3,4,5,10}，Δ_S=δΔ_F |
| slow branch | L_S=2Δ_S；1 FC + 4 个 64-unit GRU + 1 FC |
| 单采样配置 | L_F=1、Δ_F=1、Δ_S=16、L_S=32、H=8 |
| 状态转移 | A_j^S 简化为对角矩阵 |
| 快速接口 | F_IN/F_OUT 各为单个 FC；εⱼˢ 生成 A_j^S 与 g_j^S |

## 关键性质

1. **计算复用**：同一慢表征复用 δ 个 fast frames，减少重复的环境分析。
2. **因果条件**：论文要求慢表征不使用当前 fast branch 输入；这支持论文级 strict-causal 判定。
3. **SSM 调制**：环境条件进入状态动力学，而不是只作为输入拼接；δ 增大时比 EC/FiLM 更稳健。
4. **延迟边界**：2 ms 和 62.5 μs 是算法帧长度口径；目标硬件 p99、音频 I/O、OLA 和远端链路仍未验证。

## 结果摘要

在 VoiceBank + DEMAND 上，2 ms 配置的 SlowFast-SSMM δ=3 达到 39 M MAC/s，PESQ-NB/WB=3.24/2.59，STOI/ESTOI=93.10%/82.78%，HASPI=98.86%，SI-SNR=17.86；单分支 126 M MAC/s 的对应结果为 3.25/2.59、93.14%/82.56%、98.85%、17.79。单采样配置为 105 M MAC/s、PESQ-NB=3.12、SI-SNR=16.62。

## 证据

- 论文证据页：[[wiki_low_latency/sources/2024/SlowFast-SSM 2024]]
- 本地原件：`raw/papers/low_latency_causal_se/2411.02019.pdf`，共 5 页。
- 架构证据：原论文第 2 页 Figure 1，已复用 `[[wiki_low_latency/assets/2411.02019/2411.02019-page2-fig1-slowfast-ssmm.png]]`。
- 结果证据：原论文第 4 页 Table I/II，已复用 `[[wiki_low_latency/assets/2411.02019/2411.02019-page4-table1-table2.png]]`。
- 证据边界：论文未报告整网总参数量、RTF、目标硬件 p99、capture-to-playback、峰值 SRAM、功耗、丢帧恢复或逐层 strict-causal certificate。

## 关联页面

- [[wiki_low_latency/sources/2024/SlowFast-SSM 2024]]
- [[wiki_low_latency/concepts/2411.02019-slowfast-ssm]]
- [[wiki_low_latency/sources/2024/Ultra-Low Latency Speech Enhancement Comprehensive Study 2024]]
- [[wiki_low_latency/entities/RT-SEMamba]]
