---
title: 理想比率掩蔽 IRM
type: concept
created: 2026-06-05
updated: 2026-06-05
tags:
  - speech-enhancement
  - source-separation
  - mask
  - time-frequency
sources: [RNNoise 2018]
related:
  - [[wiki/concepts/理想二值掩蔽 IBM]]
---

# 理想比率掩蔽 (Ideal Ratio Mask, IRM)

## 定义

理想比率掩蔽 (IRM) 是语音增强和音源分离中一个**有监督学习目标**：对于时频域的每个 time-frequency bin，计算干净语音能量与带噪/混合语音能量之比。

$$
\text{IRM}(t, f) = \left(\frac{S(t,f)^2}{S(t,f)^2 + N(t,f)^2}\right)^\beta = \left(\frac{E_s}{E_x}\right)^\beta
$$

其中：
- $S(t,f)$：干净语音在时间帧 $t$、频率 $f$ 处的幅度/能量
- $N(t,f)$：噪声在对应 T-F bin 的幅度/能量
- $X(t,f) = S(t,f) + N(t,f)$：带噪信号的幅度/能量
- $\beta$：可调压缩指数，常见取值 $\beta = 0.5$（即平方根 IRM）

## 物理意义

- $\text{IRM} \in [0, 1]$，天然有界
- $\text{IRM} \to 1$：该 T-F bin 以语音为主，保留
- $\text{IRM} \to 0$：该 T-F bin 以噪声为主，抑制
- 中间值：语音和噪声混合，按比例衰减

使用时，将估计的 $\widehat{\text{IRM}}$ 乘以带噪信号频谱得到增强语音：

$$\hat{S}(t,f) = \widehat{\text{IRM}}(t,f) \cdot X(t,f)$$

## 为什么用 IRM 作为学习目标

相比直接预测干净语音频谱，预测 IRM 有若干优势：

1. **值域有界**：$[0, 1]$，天然适合 sigmoid 输出层，训练稳定
2. **数据归一化**：不受绝对信号幅度影响
3. **物理直觉**：掩蔽操作等价于对每个 T-F bin 做"音量调节"
4. **鲁棒性**：即使估计有误差，也只是局部频带的增益不精确，不会像直接预测频谱那样可能引入严重失真

## IRM 的变体

| 类型 | 定义 | 特点 |
|---|---|---|
| **IRM** | $(S^2/(S^2+N^2))^\beta$ | 连续值，最常用 |
| **IBM** (Ideal Binary Mask) | $\mathbf{1}[S^2 > N^2 \cdot \text{LC}]$ | 二值 (0/1)，简单但粗糙 |
| **cIRM** (Complex IRM) | 复数域掩蔽 | 可同时补偿幅度和相位 |
| **sqrt-IRM** | $\sqrt{S^2 / (S^2+N^2)}$ | $\beta=0.5$，RNNoise 使用的形式 |
| **IAM** (Ideal Amplitude Mask) | $|S|/|X|$ | 幅度比而非能量比 |

## 在 RNNoise 中的使用

RNNoise 使用的目标值是 $g_b = \sqrt{E_s(b)/E_x(b)}$，即对 Bark 频带 $b$ 而非每个频率 bin 的 **sqrt-IRM**。取平方根有两个效果：

- 压缩动态范围，更平滑
- 与最终使用的增益直接对应（幅度增益 ≈ 能量比的平方根）

→ 参见 [[RNNoise 2018#Eq. 3 — 理想临界频带增益]]

## 常见问题

> [!question] IRM 是"最优"掩蔽吗？
> 不是。IRM 最小化 T-F bin 级别的 MSE，但并不保证最大化感知质量（如 PESQ、MOS）。实践中往往需要结合感知加权损失函数或 discriminative loss。

> [!warning] IRM 依赖 oracle 信息
> 理想比率掩蔽需要用到的干净信号 $S$ 和噪声 $N$ 在实际部署中不可用。它仅仅是有监督学习的训练目标——训练时我们合成噪声样本，知道 ground truth；部署时模型从带噪信号直接预测 $\widehat{\text{IRM}}$。
