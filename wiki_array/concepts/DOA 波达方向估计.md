---
title: DOA 波达方向估计
type: concept
created: 2026-06-21
updated: 2026-06-21
tags:
  - doa-estimation
  - source-localization
  - microphone-array
  - signal-processing
sources:
  - CNN DOA Estimation with Noise Training 2017
related:
  - [[wiki_array/concepts/STFT相位图与相位信息]]
  - [[wiki_array/concepts/SRP-PHAT]]
---

# DOA 波达方向估计 (Direction of Arrival Estimation)

## 定义

**波达方向估计 (DOA Estimation)** 是指从麦克风阵列接收到的多通道信号中，估计声源相对于阵列的入射方向。通常用方位角 (azimuth) $\theta$ 表示，有时也包含仰角 (elevation) $\phi$。

$$
\theta = \text{声源入射方向与阵列法线方向的夹角}
$$

## 问题形式化

给定 $M$ 个麦克风在第 $n$ 帧接收到的信号 $\mathbf{y}(n) = [y_1(n), y_2(n), \dots, y_M(n)]^T$，估计声源的 DOA：

$$\hat{\theta}_n = f(\mathbf{y}(n))$$

其中 $f(\cdot)$ 是估计函数（可以是传统信号处理方法或深度学习模型）。

## 为什么需要 DOA 估计

DOA 估计是许多音频应用的**前置步骤**：

| 应用 | DOA 的作用 |
|---|---|
| **波束成形 (Beamforming)** | 知道声源方向才能对准主瓣、抑制旁瓣干扰 |
| **语音增强** | 空间滤波需要目标方向信息 |
| **音源分离** | 基于空间线索区分不同方向的声源 |
| **自动语音识别 (ASR)** | 远场 ASR 需要定位说话人以优化前端处理 |
| **免提通信** | 视频会议中跟踪活跃说话人 |
| **机器人听觉** | 机器人利用声源定位导航和交互 |

## 主要方法类别

### 1. 基于子空间的方法

- **MUSIC (MUltiple SIgnal Classification)** [Schmidt, 1986]
- 利用信号子空间与噪声子空间的正交性
- 高分辨率，但计算量大，对混响敏感

### 2. 基于时延估计 (TDOA) 的方法

- **GCC (Generalized Cross-Correlation)** [Knapp & Carter, 1976]
- **GCC-PHAT**：相位变换加权的 GCC
- 计算不同麦克风对之间的时延 → 几何关系求解 DOA
- 简单高效，但对噪声和混响敏感

### 3. 基于波束扫描的方法

- **SRP-PHAT (Steered Response Power with Phase Transform)** [Brandstein & Silverman, 1997]
- 在候选方向上扫描，计算波束形成器输出功率
- 对混响较鲁棒，但计算量大（全空间搜索）
- → 详见 [[SRP-PHAT]]

### 4. 基于最大似然的方法

- 建模为参数估计问题，最大化信号似然函数
- 统计最优，但需要噪声和混响的先验知识

### 5. 基于深度学习的方法

- **DNN 分类/回归**：直接从多通道信号特征预测 DOA
- **CNN 相位图方法**：端到端方案 → [[CNN DOA Estimation with Noise Training 2017]]
- **GCC 特征 + DNN**：用 GCC 向量作为输入特征 [Xiao et al., 2015]
- **特征值分解 + DNN**：噪声子空间特征向量作为输入 [Takeda & Komatani, 2016]

## DOA 估计的挑战

| 挑战 | 说明 |
|---|---|
| **混响 (Reverberation)** | 多径反射破坏直达波与角度的对应关系 |
| **噪声** | 低 SNR 时相位/时延信息被噪声淹没 |
| **多声源** | 多个声源同时存在时，需要估计每个声源的 DOA |
| **近场 vs 远场** | 近场需考虑球面波前（距离 + 角度），远场可简化为平面波（仅角度） |
| **阵列几何** | 不同阵列（线阵/圆阵/球阵）有不同的空间分辨率和角度模糊性问题 |
| **宽带信号** | 语音是宽带信号（0.1–8 kHz），不同频率的阵列响应不同 |

## 评价指标

### 帧级准确率 (Frame Level Accuracy)

$$A(\%) = \frac{\text{正确估计帧数}}{\text{总语音活跃帧数}} \times 100$$

- 最常用于分类式 DOA 估计
- 需要在离散角度网格上定义"正确"（通常 ±1 格以内算正确）

### 角度误差 (Angular Error / MAE)

$$\text{MAE} = \frac{1}{N}\sum_{n=1}^{N} |\hat{\theta}_n - \theta_n|$$

- 回归式 DOA 估计使用
- 更精细地反映估计精度

## DOA 与语音增强的关系

```
DOA 估计 ──→ 空间滤波 (波束成形) ──→ 增强语音
    │                                      │
    └── 深度学习端到端方案 ──────────────────┘
       (将 DOA 估计与增强联合优化)
```

DOA 估计是**阵列信号处理**的核心任务，是声源定位、波束成形和空间滤波的基础。部分后续工作（如基于神经波束成形的方法）将 DOA 估计与语音增强联合建模。

## 与本 Wiki 其他概念的关联

- [[STFT相位图与相位信息]] — CNN DOA 估计中使用的输入表示
- [[SRP-PHAT]] — 作为基线对比的传统 DOA 估计方法
- [[CNN DOA Estimation with Noise Training 2017]] — 本节依托的源文章
