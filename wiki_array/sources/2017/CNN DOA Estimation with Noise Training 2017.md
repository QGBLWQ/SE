---
title: CNN DOA Estimation — 基于相位图的噪声训练宽带 DOA 估计
type: source
created: 2026-06-21
updated: 2026-06-21
tags:
  - doa-estimation
  - source-localization
  - cnn
  - microphone-array
  - phase-processing
  - noise-training
source_type: paper
year: 2017
authors:
  - Soumitro Chakrabarty
  - Emanuël A. P. Habets
affiliation: International Audio Laboratories Erlangen
venue: WASPAA 2017
arxiv: "1705.00919"
code:
related:
  - [[wiki_array/concepts/DOA 波达方向估计]]
  - [[wiki_array/concepts/STFT相位图与相位信息]]
  - [[wiki_array/concepts/SRP-PHAT]]
---

# CNN DOA Estimation — Broadband DOA Estimation Using Convolutional Neural Networks Trained with Noise Signals

> Soumitro Chakrabarty, Emanuël A. P. Habets, International Audio Laboratories Erlangen, WASPAA 2017
>
> arXiv: [1705.00919](https://arxiv.org/abs/1705.00919)

## 一、研究任务与对象

| 维度 | 详情 |
|---|---|
| **任务** | 宽带 DOA (Direction of Arrival) 估计 / 声源定位 |
| **核心问题** | 在噪声和混响环境中，从麦克风阵列信号估计声源方向 |
| **方法类型** | 有监督深度学习分类（CNN），无显式特征提取 |
| **阵列类型** | 均匀线阵 (ULA)，M = 4 或 8 麦克风 |
| **DOA 范围** | 0°–180°（ULA 半平面），5° 分辨率 → 37 类 |
| **采样率** | 未显式指定（256 点 DFT，取决于采样率） |
| **实时性** | 离线逐帧分类（每 STFT 帧独立估计） |

**核心创新**：只用 STFT 的**相位分量**作为输入，用**合成噪声信号**训练，却能泛化到语音声源定位。

## 二、技术路线

### 整体管线

```
麦克风阵列信号 
    │
    ▼
┌─────────────┐
│   STFT      │  256点 DFT, 50%重叠
│   (每麦克风)  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  相位图      │  取 φ_m(n,k) → M×K 矩阵
│  Phase Map  │  M=麦克风数, K=129 (频率bin)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   CNN       │  3层Conv (2×2 filter) + FC + Softmax
│   分类器     │  无池化层
└──────┬──────┘
       │
       ▼
  P(θ_i | Φ_n) → argmax → θ̂_n (DOA 估计)
```

### 信号模型

麦克风 $m$ 在时频 bin $(n,k)$ 处的 STFT 系数：

$$Y_m(n,k) = A_m(n,k) e^{j\phi_m(n,k)} \tag{1}$$

- $A_m(n,k)$：幅度分量
- $\phi_m(n,k)$：相位分量
- **关键选择**：仅使用 $\phi_m(n,k)$，丢弃幅度信息

### 相位图 (Phase Map)

将第 $n$ 帧所有麦克风、所有频率 bin 的相位拼接为 $M \times K$ 矩阵：

$$\Phi_n = \begin{bmatrix} \phi_1(n,1) & \cdots & \phi_1(n,K) \\ \vdots & \ddots & \vdots \\ \phi_M(n,1) & \cdots & \phi_M(n,K) \end{bmatrix}$$

- 对于 $M=4, N_f=256$：输入为 $4 \times 129$ 的矩阵
- 这是 CNN 的直接输入——**不做 GCC、不做特征值分解、不做 MFCC**

### DOA 估计：分类而非回归

DOA 估计被建模为 $I$ 类分类问题（$I=37$，对应 0°–180°, 5° 步长）：

$$\hat{\theta}_n = \mathop{\arg\max}_{\theta_i}\; p(\theta_i \mid \Phi_n) \tag{2}$$

CNN 输出层用 Softmax，损失函数为交叉熵。

### CNN 架构

```
Input (4×129 Phase Map)
    │
    ▼
Conv2D (F filters, 2×2) → ReLU
    │  ↓ 无池化
    ▼
Conv2D (F filters, 2×2) → ReLU
    │  ↓ 无池化
    ▼
Conv2D (F filters, 2×2) → ReLU
    │  ↓ Flatten
    ▼
FC Layer → ReLU → Dropout(0.5)
    │
    ▼
FC Layer → ReLU → Dropout(0.5)
    │
    ▼
FC Layer → Softmax → 37 DOA classes
```

**关键设计决策**：

| 决策 | 做法 | 动机 |
|---|---|---|
| **小滤波器** | 2×2 | 学习相邻麦克风间局部频率区域的相位相关性 |
| **无池化层** | 跳过 Pooling | 实验发现池化降低性能（相位细节不宜下采样） |
| **ReLU 激活** | 所有 Conv/FC 层 | 标准选择 |
| **Dropout 0.5** | 每个 Conv 层后 + 每个 FC 层后 | 防止过拟合 |
| **权重共享** | Conv 核跨输入滑动 | 提供对局部相位畸变（如麦克风位置扰动）的鲁棒性 |

## 三、关键公式

### Eq. 1 — STFT 系数表示

$$Y_m(n,k) = A_m(n,k) e^{j\phi_m(n,k)}$$

- 幅度 $A_m$ 和相位 $\phi_m$ 分离
- 本文只取 $\phi_m$，丢弃 $A_m$
- 这是实现"噪声训练 → 语音泛化"的关键：噪声和语音的差别主要在幅度谱，相位信息则与声源的空间位置相关

### Eq. 2 — DOA 估计（最大后验）

$$\hat{\theta}_n = \mathop{\arg\max}_{\theta_i}\; p(\theta_i \mid \Phi_n)$$

- $p(\theta_i \mid \Phi_n)$：由 CNN Softmax 层输出的后验概率
- 取最大概率对应的 DOA 角度作为估计值
- 逐帧独立估计

### Eq. 3 — 帧级准确率 (Frame Level Accuracy)

$$A(\%) = \frac{\hat{N}_c}{N_s} \times 100$$

- $N_s$：测试集中语音活跃帧总数
- $\hat{N}_c$：估计 DOA 等于真实 DOA 的帧数
- 使用干净语音信号确定语音活跃帧（避免了 VAD 误差）

### 交叉熵损失（训练）

$$\mathcal{L} = -\sum_{i=1}^{I} y_i \log p(\theta_i \mid \Phi_n)$$

- $y_i$：真实 DOA 类别的 one-hot 编码
- 标准多分类交叉熵

## 四、结果与评估

### 4.1 泛化到语音 (Table 3)

> 训练：噪声 → 测试：TIMIT 语音，匹配声学条件

| 方法 | SNR=0dB | SNR=10dB | SNR=20dB |
|---|---|---|---|
| **CNN** | 62.3% | 75.1% | 90.8% |
| SRP-PHAT | 19.1% | 37.6% | 43.2% |

> [!note] 关键发现
> 用纯噪声训练的 CNN 在语音声源上取得了远优于 SRP-PHAT 的准确率，证明了**相位信息本身包含充分的声源空间位置信息**，且该信息对信号类型（噪声/语音）不敏感。

### 4.2 不同声学环境泛化 (Table 4)

> 训练房间 (R1: 6×6m, RT60=0.3s / R2: 5×5m, RT60=0.2s) vs 测试房间 (Room1: 7×6m, RT60=0.45s / Room2: 8×8m, RT60=0.53s)

| 方法 | Room1 5dB | Room1 15dB | Room2 5dB | Room2 15dB |
|---|---|---|---|---|
| **CNN** | 56.2% | 69.8% | 54.1% | 68.2% |
| SRP-PHAT | 22.6% | 33.6% | 21.8% | 38.4% |

虽然比匹配条件略有下降，但 CNN 仍显著优于 SRP-PHAT（差距 30-36 个百分点）。

### 4.3 麦克风位置扰动鲁棒性 (Table 4 括号值)

中间两个麦克风分别移动 5mm 和 3mm（沿阵列轴向、相反方向）：

| 方法 | Room1 5dB | Room1 15dB |
|---|---|---|
| **CNN** | 57.8% (+1.6) | 68.3% (-1.5) |
| SRP-PHAT | 17.7% (-4.9) | 30.5% (-3.1) |

CNN 几乎不受影响，而 SRP-PHAT 明显下降。原因：CNN 的**权重共享机制**天然对局部相位畸变鲁棒。

### 4.4 真实环境实测 (Table 5)

> Bar-Ilan 多通道 RIR 数据库，8 麦 ULA ([8,8,8,8,8,8,8] cm 间距)，15s 语音，SNR≈30dB

| 方法 | RT60=0.16s, 1m | RT60=0.16s, 2m | RT60=0.36s, 1m | RT60=0.36s, 2m | RT60=0.61s, 1m | RT60=0.61s, 2m |
|---|---|---|---|---|---|---|
| **CNN** | 91.8% | 88.7% | 86.8% | 79.4% | 72.3% | 67.3% |
| SRP-PHAT | 94.4% | 69.0% | 87.1% | 68.3% | 71.7% | 62.4% |

> [!note] 分析
> - 近距离 (1m)、低混响 (RT60=0.16s) 时 SRP-PHAT 略优（8 麦提升了其空间选择性）
> - 远距离 (2m) 和中等以上混响时 CNN 优于 SRP-PHAT
> - 混响增加使两者性能都下降，但 CNN 下降更平缓

### 关键图表说明

- **Figure 1**：卷积操作示意图 — 展示 $J \times J$ 滤波器在 $M \times K$ 输入上滑动产生特征图的机制
- **Figure 2**：CNN 架构图 — 3 层 Conv + 3 层 FC 的完整结构
- **Figure 3**：DOA 概率分布对比 — 真实声源在 135°：CNN 在 135° 有清晰峰值；SRP-PHAT 分布平坦且出现 120° 的伪峰

## 五、可复现性

| 项目 | 详情 |
|---|---|
| **训练信号** | 合成白噪声，不同位置/距离，与模拟 RIR 卷积 |
| **RIR 生成** | [RIR Generator](https://github.com/ehabets/RIR-Generator) (E.A.P. Habets) |
| **训练房间** | R1: 6×6m (RT60=0.3s), R2: 5×5m (RT60=0.2s)，每种 7 个阵列位置 × 2 个距离 |
| **训练数据量** | ~560 万 STFT 帧，37 个 DOA 类 |
| **测试语音** | TIMIT 数据库，500 个 4s 样本 |
| **优化器** | Adam |
| **Mini-batch** | 512 帧 |
| **正则化** | Dropout(0.5) 在所有 Conv 层后和所有 FC 层后 |
| **STFT 参数** | DFT 长度 256，50% 重叠，$K=129$ 频率 bin |
| **阵列配置** | ULA，阵元间距 3cm（M=4）/ [8,8,8,8,8,8,8]cm（M=8） |
| **DOA 分辨率** | 5° → 37 类 (4 麦) / 15° (8 麦真实实验) |
| **SNR 条件** | 训练：0–20 dB 均匀采样；测试：0/5/15/20/30 dB（分实验） |

> [!question] 不确定性
> - CNN 的具体层数、每层滤波器数量 F、FC 层单元数**未明确给出**（只说通过验证集选择最小验证损失的配置）
> - 训练 epoch 数、学习率策略未说明
> - 权重共享对鲁棒性的定量解释是定性的（"可以带来鲁棒性"），未做消融实验验证
> - 代码未开源
> - Figure 1-3 在 PDF→Markdown 转换中丢失，需查看原 PDF
> - 仅测试了白噪声训练 → 语音泛化，其他噪声类型（色噪声、冲击噪声）的影响未知

## 六、贡献与局限

### 核心贡献

1. **相位图输入范式**：证明了 STFT 相位分量本身包含充分的 DOA 信息，无需显式特征提取（GCC/特征值分解/MFCC）
2. **噪声训练 → 语音泛化**：开创性地用合成噪声信号训练 DOA 估计网络，避免了对语音数据库和 VAD 的依赖
3. **CNN 的天然鲁棒性**：权重共享机制使网络对麦克风位置微扰、噪声和混响具有良好鲁棒性
4. **简单架构**：3 层 Conv + FC，无需复杂特征工程

### 局限性

1. **单声源假设**：无法处理多声源场景
2. **ULA 阵列限定**：仅验证了均匀线阵，其他阵列几何（圆阵、球阵）待测试
3. **混响衰减**：RT60 从 0.16s→0.61s 时准确率下降约 20 个百分点
4. **离散分类**：5° 分辨率可能不足以满足高精度应用
5. **逐帧独立**：未利用帧间时序信息（与后续 RNN/Attention 方案对比）
6. **仅白噪声训练**：未测试训练噪声类型对泛化能力的影响

## 七、与其他方法的关联

| 对比维度 | 传统方法 (SRP-PHAT) | 本文 CNN | 后续 DNN 方向 [9-11] |
|---|---|---|---|
| **特征** | GCC 向量 | 原始相位图 | GCC / 特征向量 |
| **学习** | 无学习 | 端到端特征学习 | 浅层 DNN |
| **训练数据** | 不需要 | 合成噪声 | 语音 + 标签 |
| **计算** | 高（搜索空间） | 低（前向传播） | 中 |
| **噪声鲁棒性** | 弱 | 强 | 中 |


### 6. 本论文在库中的位置关联

| 维度 | 论文 | 关系 |
|------|------|------|
| **后身/扩展** | [[Multi-Speaker CNN DOA 2018]] | 同一作者 (Chakrabarty & Habets)：单声源 Softmax → 多声源 Sigmoid + 2×1 滤波器 + M-1 层规则 |
| **同分支竞品** | [[CRNN DOAnet 2017]] | 同年 (2017)：Chakrabarty CNN 用相位图+ULA → Adavanne CRNN 用幅度相位+Ambisonics |
| **同分支竞品** | [[Multi-Speaker Detection Likelihood 2017]] | 同年 (2017)：GCC 手工特征+似然编码 → CNN 端到端相位图 |
| **跨分支类比** | [[SELD CRNN 2018]] | 次年 (2018)：Chakrabarty 相位图+Sigmoid 的多标签输出方案被 SELDnet 的 SED+DOA 框架吸收 |
| **跨分支类比** | [[STM 相位图与相位信息]] | 本论文开创了"相位图"输入范式——白噪声训练→语音泛化是核心洞察 |

### 7. 江湖地位

```
2017 | 纯 DOA | 首次证明"白噪声训练+相位图CNN→泛化到语音"→ DOA 深度学习奠基作
          → 被自己的 2018 多声源版扩展 → 被 CRNN/SELD 线取代
          → 相位-only 的核心洞察至今仍有价值（库里专门建了概念页）
```


---

*WASPAA 2017 论文，标志着 CNN 首次被应用于基于相位信息的端到端 DOA 估计。*
