---
title: SEMamba++ - 通用语音修复框架（频率 GLP + 多分辨率并行 TFDP）
type: entity
created: 2026-10-07
updated: 2026-10-07
tags:
  - entity
  - model
  - general-speech-restoration
  - mamba
  - frequency-modeling
  - fourier-analysis-network
  - multi-resolution
  - gan
  - non-causal
  - interspeech-2026
source_paper: "[[wiki_low_latency/sources/2026/SEMamba++ 2026]]"
related:
  - [[wiki_low_latency/sources/2026/SEMamba++ 2026]]
  - [[wiki_low_latency/concepts/semamba-pp-2026-frequency-glp]]
  - [[wiki_low_latency/entities/RT-SEMamba]]
  - [[wiki_low_latency/concepts/2304.08707-full-sub-band-modeling]]
  - [[wiki_low_latency/entities/GTCRN]]
---

# SEMamba++

> 一句话定义：一个 **2.7 M 参数**的通用语音修复（GSR）框架，核心是 **Frequency GLP**（把 **FAN 直接作用在频率轴**以学谐波周期性，与卷积局部模块**并联**）与**多分辨率并行 TFDP**（**仅沿频率轴下采样**），配可学习 softplus 映射与 LSGAN 训练。
> **非因果、离线、无延迟约束** ⇒ 在库中只作**频率建模工具箱**参照。

- **出处**：Interspeech 2026 [Long Track], pp. 5166-5175, DOI `10.21437/Interspeech.2026-665`
- **作者**：Yongjoon Lee, Jung-Woo Choi（KAIST）
- **代码/演示**：https://sites.google.com/view/semambapp
- **源页**：[[wiki_low_latency/sources/2026/SEMamba++ 2026]]

---

## 1. 定义与定位

| 项 | 内容 |
|---|---|
| 类型 | **完整模型**（encoder–bottleneck–decoder） |
| 任务 | **General Speech Restoration**：噪声 + 混响 + 带宽限制 + 削波 |
| 输入 / 输出 | 退化语音波形 → 干净语音波形（STFT 幅度+相位**并行**解码） |
| 参数量 | **2.7 M** |
| RTF | **0.021**（单张 A6000 GPU，"处理 1 秒语音所需时间"） |
| 骨干 | Time Mamba（**双向**）+ Frequency GLP；$N=4$ bottleneck block，$C=48$ |
| 因果性 | **非因果**（双向 Mamba；全文无 latency/streaming/causal 讨论） |
| 算法延迟 | **未报告**（且不适用——非流式） |
| 库内定位 | **"频率结构怎么建模"这一问题的当前最完整答案**；**不可参与低时延排名** |

> [!warning] 定位纪律
> 按库内"非因果模型的两类用途必须分开记"：SEMamba++ **不能参与因果排名**，但**可以参与"质量上界"与"方法学参照"讨论**。
> 特别地：**不要因为它叫 Mamba、和 RT-SEMamba 同族，就把它当作流式方法**——它是**双向** Mamba。

---

## 2. 组件表

| 组件 | 作用 | 实现 | 关键超参 |
|---|---|---|---|
| **Frequency GLP** | 频率特征提取（核心） | GP（FAN）+ L（卷积）**并联** → 拼接 → 逐点卷积选择 → Channel FFN | $d_p=C/4$；L 用 kernel 3 + GELU |
| └ **GP 模块** | 全局 + **周期性** | 两级 FAN（$F_{eff}\to 2F_{eff}\to 2F_{eff}$）+ linear gating | FAN 线性层**直接作用于频率轴** |
| └ **L 模块** | 局部（子带内） | 一串 1-D 卷积沿频率轴 | kernel size 3 + GELU |
| **多分辨率并行 TFDP** | 多尺度谱建模 | 3 个频率分辨率**并行**；仅频率轴下采样 $2^r$ | strided conv / transposed conv，kernel (3,4)、stride (1,2) |
| **Time Mamba** | 时间维建模 | SEMamba 的 Mamba 块 | 扩展因子 2 |
| **可学习 softplus 映射** | 幅度解码（替代 masking） | $y=\frac{1}{\beta_f}\log(1+e^{\beta_f x})$ | 每频带一个 $\beta_f$；8 kHz 处 $\beta=34.2$ |
| **LSGAN + MS-SB-CQTD + MRD** | 对抗训练 | 替代 MetricGAN | 3 个子判别器；octaves 8；bins/oct 12/24/36 |
| **encoder / decoder** | 前端与后端 | dilated DenseNet（**继承 MP-SENet**） | 编码器 $F\to F/2$；解码器 $F/2\to F$ |

---

## 3. 证据表

### 3.1 Table 1：主结果（VCTK-GSR test / URGENT 2025 val / URGENT 2025 test）

列序 = 每组的 SCOREQ / UTMOS / OVRL / PESQ / LSD↓ / LPS。

| Model | Method | VCTK-GSR test | URGENT val | URGENT test |
|---|---|---|---|---|
| MP-SENet | GAN, 1 step | 1.87 / 2.17 / 2.82 / 2.01 / 1.22 / 0.42 | 1.59 / 1.90 / 2.88 / 1.63 / 1.78 / 0.59 | 1.38 / 1.71 / 2.81 |
| SEMamba | GAN, 1 | 1.89 / 2.34 / 2.88 / 2.13 / 1.19 / 0.45 | 1.66 / 2.06 / 2.92 / 1.67 / 1.83 / 0.60 | 1.51 / 1.88 / 2.84 |
| USEMamba | Reg, 1 | 1.87 / 2.30 / 2.94 / 1.90 / 1.21 / 0.42 | 1.77 / 2.05 / 2.98 / 1.53 / 1.51 / 0.60 | 1.60 / 1.88 / 2.91 |
| Universe++ | Score, 8 steps | 2.32 / 2.74 / 2.74 / 1.45 / 1.34 / 0.22 | 1.26 / 1.78 / 2.45 / 1.18 / 2.13 / 0.17 | 1.20 / 1.69 / 2.38 |
| Universe++ | Score, 50 steps | 2.57 / 2.93 / 2.95 / 1.35 / 1.26 / 0.19 | 1.56 / 1.95 / 2.78 / 1.15 / 2.00 / 0.13 | 1.50 / 1.88 / 2.71 |
| LLaSE-G1* | LM, 1 | 2.30 / 2.40 / 2.47 / 1.20 / 2.62 / 0.26 | 2.17 / 2.11 / 2.69 / 1.15 / 1.93 / 0.54 | 2.03 / 1.94 / 2.62 |
| **SEMamba++** | **GAN, 1** | **3.27 / 3.55 / 3.14** / 1.77 / 1.25 / 0.45 | **2.67 / 2.82 / 3.20** / 1.51 / 1.49 / 0.61 | **2.49 / 2.61 / 3.13** |

> [!note] 论文的诚实说明
> SEMamba 在 VCTK-GSR test 上的 **PESQ / LSD / LPS 最优**；SEMamba++ 的优势在**感知质量（SCOREQ/UTMOS/OVRL）与 OOD 泛化**。
> 论文还指出："生成式方法通常在 in-domain 与 OOD 上**LPS 都低**，这与文献 [56] 一致——生成式语音增强会出现**音素替换**这类独特错误。" ⇒ **LPS 是生成式的系统性弱点**，如实记录。

### 3.2 Table 2：AATC 2025 blind test（效率 + 质量）

列序 = 参数量 (M) / RTF / SIG / BAK / OVRL / PESQ。

| Model | Params (M) | RTF | SIG | BAK | OVRL | PESQ |
|---|---|---|---|---|---|---|
| Degraded | – | – | 2.89 | 3.02 | 2.47 | 1.91 |
| MP-SENet | 2.3 | 0.022 | 3.27 | 3.89 | 2.94 | 1.83 |
| SEMamba | 1.7 | **0.013** | 3.21 | 3.88 | 2.88 | 1.68 |
| USEMamba | 3.9 | 0.045 | 3.36 | 3.99 | 3.06 | 1.73 |
| Universe++ 8 steps | 42.8 | 0.023 | 2.58 | 3.83 | 2.32 | 1.11 |
| Universe++ 50 steps | 42.8 | 0.118 | 2.98 | 3.84 | 2.68 | 1.10 |
| **LLaSE-G1*** | **1072** | **0.011** | 3.15 | 4.00 | 2.88 | 1.25 |
| **SEMamba++** | **2.7** | 0.021 | **3.45** | **4.01** | **3.18** | **1.84** |

> [!important] 参数与速度解耦的极端案例
> **LLaSE-G1：1072 M 参数，RTF 0.011（全表最低）**——比 1.7 M 参数的 SEMamba（0.013）还快。
> 论文解释："由于**利用 codec 技术的序列长度压缩**"。
> ⇒ 这是库内**"参数量不能代理速度"的又一强例证**，与 [[wiki_low_latency/entities/FastEnhancer]] 的"262M MACs 反而比 40M 快 2.7×"同类。**10 亿参数模型的 RTF 低于 170 万参数模型**——值得作为极端案例单独引用。

### 3.3 Table 3：DNS 2020 test real recordings（联合去噪+去混响）

列序 = 参数量 (M) / 训练数据 (小时) / SIG / BAK / OVRL。

| Model | Params (M) | 训练数据 | SIG | BAK | OVRL |
|---|---|---|---|---|---|
| Degraded | – | – | 3.053 | 2.509 | 2.255 |
| ANYENHANCE† | 363.6 | **3.7k h** | 3.488 | 3.977 | 3.161 |
| MaskSR-M† | 145 | **800 h** | 3.43 | 4.025 | 3.136 |
| LLaSE-G1† | 1072 | **500 h** | 3.472 | 3.996 | 3.177 |
| Voicefixer* | 111.7 | 44 h | 3.291 | 3.960 | 2.992 |
| USEMamba | 3.9 | 44 h | 3.239 | 3.937 | 2.923 |
| Universe++ 8 steps | 42.8 | 44 h | 2.646 | 3.756 | 2.374 |
| Universe++ 50 steps | 42.8 | 44 h | 3.037 | 3.841 | 2.731 |
| **SEMamba++** | **2.7** | **44 h** | **3.487** | **4.02** | **3.206** |

> [!warning] 跨数据规模的对比，引用必须标注
> 论文自陈："ANYENHANCE、MaskSR-M、LLaSE-G1 **训练数据远超**其他模型，直接比较可能不恰当。**等训练数据规模的彻底比较留待未来工作。**"
> ⇒ **SEMamba++ 用 2.7 M 参数 + 44 小时达到 1B 参数 + 500 小时模型的可比水平**，这个结论本身成立；但**"超过"的说法需谨慎**，因为数据规模不可比。

### 3.4 Table 5：IoU 检验（并行 vs 串行的互补性）

| Method | VCTK-GSR test | URGENT test | DNS2020 test |
|---|---|---|---|
| **MR-Parallel** | **0.036** | **0.036** | **0.037** |
| MR-Sequential | 0.045 | 0.047 | 0.046 |

**Wilcoxon signed-rank 检验，3.9k 样本，$p<0.05$** ⇒ 并行显著低于串行（IoU 越低 ⇒ 分辨率间关注区域差异越大 ⇒ 特征越互补）。

---

## 4. 频率建模模块横向对照（Table 6）

列序 = Params (M) / RTF / VCTK UTMOS / VCTK OVRL / URGENT UTMOS / URGENT OVRL / DNS UTMOS / DNS OVRL。所有行共享 Time Mamba + 多分辨率并行 + vocoder 训练 + 可学习映射。

| Design | Params | RTF | VCTK UTMOS | VCTK OVRL | URGENT UTMOS | URGENT OVRL | DNS UTMOS | DNS OVRL |
|---|---|---|---|---|---|---|---|---|
| Mamba | 2.7 | 0.025 | 3.55 | 3.12 | 2.50 | 3.04 | 2.70 | 3.06 |
| Transformer | 2.9 | 0.027 | 2.95 | 2.95 | 2.24 | 2.95 | 2.40 | 3.04 |
| Conformer | 2.4 | 0.028 | 3.45 | 3.06 | 2.46 | 3.04 | 2.93 | 3.17 |
| SpatialNet | 2.6 | 0.024 | 3.46 | 3.10 | 2.36 | 2.98 | 2.68 | 3.11 |
| **GLP (Ours)** | **2.7** | **0.021** | **3.55** | **3.14** | **2.61** | **3.13** | **3.02** | **3.21** |
| w/o GP module | 2.9 | 0.030 | 3.43 | 3.08 | 2.51 | 3.05 | 2.64 | 3.09 |
| Serial | 2.6 | 0.020 | 3.52 | 3.10 | 2.45 | 2.99 | 2.82 | 3.11 |
| FAN→Linear | 2.8 | 0.019 | 3.45 | 3.10 | 2.50 | 3.05 | 2.96 | 3.17 |

**三条读法**：
1. **GLP 质量全面最优，且 RTF（0.021）低于四个基线**（Mamba 0.025 / Transformer 0.027 / Conformer 0.028 / SpatialNet 0.024）。
2. **去掉 GP 模块代价最大**：RTF **0.021 → 0.030（反而变慢）** + 三数据集全面下降（DNS OVRL 3.21→3.09）⇒ **GP 是关键组件，且同时提质量与提效率**。
3. **FAN→Linear 的 RTF 0.019 < GLP 的 0.021**（FAN 有代价），但质量更低（DNS UTMOS 2.96 vs 3.02）⇒ **周期性建模是"花一点算力换质量"**。

---

## 5. 分辨率策略对照（Table 7）

| Design | Params | RTF | VCTK UTMOS | VCTK OVRL | URGENT UTMOS | URGENT OVRL | DNS UTMOS | DNS OVRL |
|---|---|---|---|---|---|---|---|---|
| **MR-Parallel (Ours)** | 2.7 | 0.021 | 3.55 | 3.14 | 2.61 | 3.13 | 3.02 | 3.21 |
| MR-Sequential | 2.7 | 0.021 | 3.54 | 3.12 | 2.53 | 3.08 | 2.91 | 3.21 |
| **SR**（单分辨率，C: 48→144） | **9.0** | **0.034** | 3.53 | 3.11 | **2.42** | **2.85** | **2.19** | **2.48** |
| w/o down.（不下采样） | 2.8 | 0.028 | 3.50 | 3.09 | 2.44 | 2.95 | 2.72 | 3.0 |
| T×4（仅时间下采样） | 2.6 | 0.019 | 3.39 | 3.04 | 2.46 | 3.03 | 2.75 | 3.15 |
| T×2 F×2（两轴都下采样） | 2.7 | 0.019 | 3.55 | 3.10 | 2.53 | 3.03 | 3.03 | 3.14 |

**四条读法**：
1. **SR 最有说服力**：参数 **2.7 → 9.0 M（3.3×）**、RTF **0.021 → 0.034（1.6×）**，in-domain 略降、**OOD 崩到 2.19/2.48** ⇒ 论文判为**过拟合**。**多分辨率并行是 OOD 泛化的主要来源。**
2. **T×4（仅时间下采样）最差**（VCTK 3.39）⇒ "**频率下采样产生的上采样伪影比时间下采样更可忽略**"。
3. **w/o downsampling 各项略降** ⇒ 仅频率下采样**既高效也有效**。
4. **T×2 F×2 与主方法几乎持平**（VCTK 3.55/3.10；DNS UTMOS 3.03 vs 3.02）且 RTF 更低（0.019）——**但论文未讨论这一变体**，见 §7 的 `[!question]`。

---

## 6. "从 SEMamba 到 SEMamba++"演进表（Table 8）

列序 = Params / RTF / VCTK UTMOS / VCTK PESQ / URGENT UTMOS / URGENT OVRL / DNS UTMOS / DNS OVRL。

| Design | Params | RTF | VCTK UTMOS | VCTK PESQ | URGENT UTMOS | URGENT OVRL | DNS UTMOS | DNS OVRL |
|---|---|---|---|---|---|---|---|---|
| SEMamba | 1.7 | 0.013 | 2.34 | **2.13** | 1.79 | 2.80 | 1.57 | 2.75 |
| LMask. → LMap. | 1.7 | 0.013 | 2.30 | 2.22 | 1.82 | 2.87 | 1.82 | 2.90 |
| **Metric. → Vocoder** | 1.7 | 0.013 | **3.32** | **1.71** | 2.28 | 2.91 | 2.14 | 2.88 |
| TFMamba-large（C 64→80） | 2.7 | 0.018 | 3.31 | 1.75 | 2.23 | 2.84 | 2.31 | 2.85 |
| **Ours** | 2.7 | 0.021 | **3.55** | 1.77 | **2.61** | **3.13** | **3.02** | **3.21** |

> [!contradiction] MetricGAN → LSGAN：UTMOS +1.02，PESQ −0.51
> 这是全篇最大的**指标方向相反**。论文解释：**MetricGAN 目标显式优化 PESQ**，换 LSGAN 后模型转向更泛化的感知质量。
> ⇒ 这也解释了 SEMamba++ 最终 PESQ 只有 1.77 / 1.84，而 SEMamba 是 2.13 —— **这是有意的取舍，不是退步**。引用其 PESQ 时必须同时说明。
> 论文用 **Blau & Michaeli 的 perception-distortion tradeoff** 支撑"对齐敏感指标对偏离结构的惩罚重于对过度平滑的惩罚"这一立场。

**参数量对齐下的架构对比**：`TFMamba-large`（2.7 M）vs `Ours`（2.7 M）—— UTMOS 3.31 vs 3.55、URGENT OVRL 2.84 vs 3.13、DNS UTMOS 2.31 vs 3.02 ⇒ 论文结论："**相同训练损失下，本文方法在架构上优于 TFMamba 与 TFMamba-large。**"

---

## 7. 因果性审计与前端配置

### 7.1 因果性审计

| 检查项 | 结论 |
|---|---|
| 是否报告算法延迟？ | **否**（且不适用——非流式） |
| 是否讨论 latency / streaming / causal？ | **全文没有** |
| 骨干 Mamba 的方向 | **双向**（SEMamba 系 Time Mamba） |
| RTF 的含义 | **吞吐量**（处理 1 秒语音的耗时），**不是延迟** |
| 能否参与库内低时延排名？ | **不能** |
| STFT center | **未报告**（记入"STFT center 审计表"待办） |
| 是否可流式？ | 论文未讨论；双向 Mamba 使流式不可行 |

### 7.2 前端配置（与库内同前端论文组）

| 项 | SEMamba++ | [[wiki_low_latency/entities/PrimeK-Net]] | [[wiki_low_latency/entities/LaCo-SENet]] |
|---|---|---|---|
| 窗长 | 400 样本 | 400 样本 | 400 样本 |
| hop | 100 样本 | 100 样本 | 100 样本 |
| FFT | 未单独报告（窗长 400） | 400 | 未报告 |
| 时间分辨率 @16 kHz | **25 ms / 6.25 ms** | **25 ms / 6.25 ms** | **25 ms / 6.25 ms** |
| 窗型 | Hann | 未报告 | 未报告 |
| 任务 | GSR | 增强 | 增强 |
| 因果性 | 非因果 | 非因果 | 因果 |

> [!note] 库内同前端论文组
> 这三篇共享**完全相同的时间分辨率（25 ms / 6.25 ms @16 kHz）**。若要做"同前端对照"，这是一个现成的论文组。
> **但注意：任务与因果性都不同（GSR vs 增强；非因果 vs 因果）⇒ 只能对前端，不能对结果。**

---

## 8. 论文自陈局限与隐藏问题

### 8.1 论文自陈（§7 Limitations，仅两条）

1. **Frequency GLP 可能无法直接部署在需要"采样率无关处理"的场景**，因为其线性运算直接作用于频率轴。
2. 同时改善感知质量与信号保真度的更先进训练目标未被充分探索。

> [!important] 局限 1 是本篇对库内最有价值的警告
> "线性层直接作用于频率轴" ⇒ **频率 bin 数被硬编码进参数**：
> - 换采样率（16 → 48 kHz）⇒ bin 数变化 ⇒ **参数形状不匹配，模型不可用**；
> - 换 STFT 尺寸（窗长/hop/FFT）⇒ **同样失效**。
> ⇒ **跨采样率迁移的硬障碍**。库内几乎所有方法都在 **16 kHz 固定前端**下评测 ⇒ 这条提示：**任何依赖"频率轴全连接"的模块（含 GLP）都不具备采样率无关性**。
> 对比：sub-band 路线（[[wiki_low_latency/entities/GTCRN]]、[[wiki_low_latency/entities/LiSenNet]]）也按频率分组，但**分组是固定的频带划分**，比"逐 bin 全连接"更容易迁移。

### 8.2 隐藏问题

| # | 问题 |
|---|---|
| 1 | **训练数据 44 h vs 基线 500–3700 h** ⇒ Table 3 的跨规模对比，论文自陈"留待未来工作" |
| 2 | **无幻觉/保真度评估**：论文自己说 GSR "**要生成缺失的语音片段**"，但**没有用 SpeechBERTScore / WER / 幻觉指标**评估生成内容。而 2026 年"生成幻觉"已是增强领域 27% 论文涉及的问题 ⇒ **明显缺口** |
| 3 | **`T×2 F×2` 变体与主方法几乎持平但论文未讨论** ⇒ "仅频率下采样"的优势**主要体现在 OOD OVRL（3.13 vs 3.03）**，而非全面。记 `[!question]` |
| 4 | **未引用 RT-SEMamba**（同组、同 Mamba 家族、因果流式版本）⇒ 两篇是**同族骨干、相反约束**的一对，但论文未建立关联 |
| 5 | **LPS 系统性偏低**（论文自己承认是生成式方法"音素替换"类错误的表现），但未提出缓解方案 |
| 6 | **无 VoiceBank+DEMAND** ⇒ 数字与库内任何论文都不可直接比 |

---

## 9. 与库内模型对照

| 模型 | 任务 | 因果性 | 参数量 | RTF | 延迟 | 频率建模哲学 |
|---|---|---|---|---|---|---|
| **SEMamba++** | GSR | **非因果**（双向 Mamba） | **2.7 M** | 0.021（A6000） | 未报告 | **FAN 频率轴 + 多分辨率并行**（为质量/泛化） |
| [[wiki_low_latency/entities/RT-SEMamba]] | 增强 | **因果** | 未报告 | 未报告 | **25 ms 约束** | Mamba + 渐进蒸馏（为流式） |
| [[wiki_low_latency/entities/GTCRN]] | 增强 | 因果 | **23.7 K** | 未报告 | 未报告 | **子带分组 + 分组循环**（为省算力） |
| [[wiki_low_latency/entities/LiSenNet]] | 增强 | 因果 | **37 K** | 0.028（Xeon CPU） | 未报告 | **子带卷积核尺寸选择**（为省算力） |
| [[wiki_low_latency/entities/PSMSE]] | 增强 | 因果 | 0.26 M | – | 30 ms | 并行脉冲 Mamba（为流式） |

> [!important] 频率建模的两条对立哲学
> - **为省算力**：[[wiki_low_latency/entities/GTCRN]]（子带分组）、[[wiki_low_latency/entities/LiSenNet]]（子带核尺寸）⇒ 频率轴**粗粒度分组**
> - **为质量/泛化**：**SEMamba++**（FAN 频率轴全连接 + 多分辨率并行）⇒ 频率轴**细粒度周期建模**
>
> ⇒ 两者在库内构成**一组对照**：**同一根频率轴，一个用来省算力、一个用来提质量**。这对理解"频率结构建模的代价与收益"很有价值。

---

## 交叉链接

- 源页：[[wiki_low_latency/sources/2026/SEMamba++ 2026]]
- 概念页：[[wiki_low_latency/concepts/semamba-pp-2026-frequency-glp]]
- 同族骨干：[[wiki_low_latency/entities/RT-SEMamba]]
- 频率建模对照：[[wiki_low_latency/entities/GTCRN]]、[[wiki_low_latency/entities/LiSenNet]]、[[wiki_low_latency/concepts/2304.08707-full-sub-band-modeling]]
- 同前端论文组：[[wiki_low_latency/entities/PrimeK-Net]]、[[wiki_low_latency/entities/LaCo-SENet]]
- 速度-参数解耦对照：[[wiki_low_latency/entities/FastEnhancer]]
- 全库判定口径：[[wiki_low_latency/overview]]
