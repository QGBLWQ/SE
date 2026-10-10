---
title: DP-IPD 直达路径通道间相位差
type: concept
created: 2026-09-08
updated: 2026-09-08
tags:
  - doa-estimation
  - sound-source-localization
  - spatial-feature
  - phase-difference
  - deep-learning
sources:
  - IPDnet 2024
  - FA-Stateformer 2025
related:
  - "[[wiki_array/concepts/DOA 波达方向估计]]"
  - "[[wiki_array/concepts/TDOA 到达时延差]]"
  - "[[wiki_array/concepts/GCC-PHAT 广义互相关]]"
  - "[[wiki_array/sources/2025/FA-Stateformer 2025]]"
---

# DP-IPD 直达路径通道间相位差

## 定义

**DP-IPD（Direct-Path Inter-channel Phase Difference，直达路径通道间相位差）** 是由声源到各麦克风的**直达声**所产生的相对相位。它保留了与入射方向直接对应的空间线索，并刻意排除混响、多径与干扰在观测相位中引入的偏差。

它应与普通 **IPD** 区分：

| 名称 | 表示什么 | 是否含混响/干扰 |
|---|---|---|
| **IPD** | 两路观测 STFT 的相位差 | 是 |
| **DP-IPD** | 两路信号中仅由直达路径产生的相位差 | 否（作为理想监督目标） |

在 IPDnet 中，网络从混合的多通道信号中估计 DP-IPD；再将其与候选方向的理论 DP-IPD 比较，以完成单/多声源定位。

## 从 STFT 到 IPD

设第 $m$ 个麦克风在时间帧 $t$、频点 $f$ 的 STFT 为 $X_m(t,f)$。对麦克风对 $(m,n)$，观测 IPD 为：

$$operatorname{IPD}_{m,n}(t,f)=\angle X_m(t,f)-\angle X_n(t,f)
=\angle\!\left(X_m(t,f)X_n^*(t,f)\right).$$

相位是 $2\pi$ 周期量。实际送入网络或计算损失时，常把它编码为：

$$\mathbf p_{m,n}(t,f)=
\begin{bmatrix}
\cos(\operatorname{IPD}_{m,n}(t,f))\\
\sin(\operatorname{IPD}_{m,n}(t,f))
\end{bmatrix},$$

从而避免 $-\pi$ 与 $\pi$ 附近的相位绕回不连续。

## DP-IPD 的几何含义

在远场平面波、无混响的近似下，方向单位向量为 $\mathbf u(\theta,\phi)$，麦克风位置为 $\mathbf r_m$。两麦克风的传播时延差为：

$$\tau_{m,n}(\theta,\phi)=\frac{(\mathbf r_m-\mathbf r_n)^\mathsf T\mathbf u(\theta,\phi)}{c},$$

对应的直达路径相位差（符号随 STFT 与方向约定而可能整体相反）为：

$$
\operatorname{DP\!\text{-}\!IPD}_{m,n}(f;\theta,\phi)
=2\pi f\,\tau_{m,n}(\theta,\phi) \pmod {2\pi}.
$$

因此，给定阵列几何，**候选方向会产生确定的跨麦相位模式**；DP-IPD 就是这一模式的可学习、连续角度表示。它与 [[TDOA 到达时延差]] 编码的是同一几何事实：TDOA 在时延域表达，DP-IPD 在频率—相位域表达。

## 为什么不能直接使用观测 IPD

真实观测通常包含直达声、早期反射、晚期混响、噪声及其他声源：

$$X_m=X_m^{\mathrm{direct}}+X_m^{\mathrm{reverb}}+X_m^{\mathrm{noise}}+\cdots$$

对这个和直接取相位，得到的 IPD 不再等于由几何决定的直达路径相位差。尤其在低 SNR、强混响或多声源重叠时，观测 IPD 会偏离目标方向的理论模式。

DP-IPD 学习将问题改写为：

```text
混合多通道 STFT ──→ 网络抑制混响/干扰 ──→ 估计直达路径 DP-IPD
                                              │
候选 DOA + 阵列几何 ──→ 理论 DP-IPD ─────────┘
                                              ↓
                                      相似度 / 匹配得分 → DOA
```

这不是“直接把 IPD 当输入预测角度”，而是先恢复一个**可由物理几何验证的中间空间表征**。

## 多声源：多轨 DP-IPD

单个时频点可能由不同声源主导；当多个声源同时活跃时，一个 DP-IPD 轨无法表示所有方向。IPDnet 因而输出多条 DP-IPD 轨，每条对应一个潜在声源，并采用**置换不变训练（PIT）**：训练时在所有预测轨—真值声源的配对中选择总误差最小的一种。

| 设计 | 作用 |
|---|---|
| 多轨 DP-IPD 输出 | 同时容纳多个声源的方向线索 |
| PIT 匹配 | 避免网络必须固定“第几轨对应第几个声源” |
| 全频带 + 窄频带建模 | 分别利用跨频率的全局结构与每个频带的局部相位模式 |
| 理论模板匹配 | 从连续 DP-IPD 表征恢复候选 DOA 的空间得分 |

## 与相关特征的区别

| 特征/方法 | 主要表征 | 与 DP-IPD 的关系 |
|---|---|---|
| [[TDOA 到达时延差]] | 麦克风对的到达时间差 | DP-IPD 是 TDOA 在各频率上的相位表达 |
| [[GCC-PHAT 广义互相关]] | 全频带相位一致性形成的时延峰 | 直接从观测相位找时延；DP-IPD 先估计直达声相位 |
| 普通 IPD | 观测 STFT 的相对相位 | DP-IPD 是去除多径/干扰影响后的目标表征 |
| SRP-PHAT | 对候选方向扫描并累积响应 | DP-IPD 同样可与方向模板匹配，但匹配对象由网络估计 |

## 优势与限制

| 优势 | 限制 |
|---|---|
| 显式保留阵列几何与相位物理先验 | 高频会发生 $2\pi$ 相位绕回与空间混叠 |
| 以直达声为监督目标，可提高混响/噪声下的稳健性 | 依赖已知且准确的麦克风几何、采样率和声速假设 |
| 多轨 + PIT 适合未知排列的多声源 | 声源重叠、直达混响比很低时，直达相位本身难以恢复 |
| 连续相位表征避免离散角度格点的量化误差 | 全频带/窄频带双分支可能带来较高计算开销 |

## 在库中的位置

- [[FA-Stateformer 2025]] 将 IPDnet 列作多说话人 DOA 基线：IPDnet 以全频带/窄频带融合和多轨 DP-IPD 目标获得较低 MAE，但计算量显著更高。
- 对研究“语音增强是否破坏定位”的问题，DP-IPD 是关键约束：增强前后应尽可能保持目标声源的跨麦直达路径相位关系，而不只是提高单通道幅度质量。

## 一句话总结

> **DP-IPD 是“由阵列几何和声源方向决定的理想跨麦相位差”；IPDnet 学习从受混响和干扰污染的观测中恢复它，再用其与方向模板匹配进行定位。**
