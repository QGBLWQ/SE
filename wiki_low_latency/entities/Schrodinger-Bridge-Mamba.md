---
title: SBM (Schrödinger Bridge Mamba)
type: entity
created: 2026-10-07
updated: 2026-10-07
tags:
  - entity
  - model
  - generative
  - schrodinger-bridge
  - mamba
  - ssm
  - one-step-inference
  - limited-lookahead
  - interspeech-2026
source_paper: "[[wiki_low_latency/sources/2026/Schrodinger Bridge Mamba 2026]]"
related:
  - [[wiki_low_latency/sources/2026/Schrodinger Bridge Mamba 2026]]
  - [[wiki_low_latency/concepts/sbm-2026-schrodinger-bridge-mamba]]
  - [[wiki_low_latency/entities/RT-SEMamba]]
  - [[wiki_low_latency/entities/PSMSE]]
  - [[wiki_low_latency/concepts/严格因果与算法延迟]]
---

# SBM（Schrödinger Bridge Mamba）

> 一句话定义：把 **Schrödinger Bridge（SB）训练范式**与 **Mamba 骨干**协同起来的**一步**生成式语音增强模型——SB 显式计算最优传输（OT）路径上的中间态 $x_t$ 充当训练"锚点"，Mamba 的选择性状态空间递推天然模拟状态演化，训练期把 SB 变换**蒸馏进 Mamba 动力学**，从而在**单次前向**中重建干净语音。

- **出处**：Interspeech 2026, pp. 1363-1368, DOI `10.21437/Interspeech.2026-682`
- **作者**：Jing Yang（通讯）, Sirui Wang, Chao Wu, Lei Guo, Fan Fan —— **华为中央媒体技术院**
- **演示页**：https://sbmse.github.io
- **源页**：[[wiki_low_latency/sources/2026/Schrodinger Bridge Mamba 2026]]

---

## 1. 定义与定位

| 项 | 内容 |
|---|---|
| 类型 | **完整模型**（生成式，但推理是确定性的单步） |
| 任务 | **联合去噪 + 去混响** |
| 输入 / 输出 | 退化语音 STFT 谱 → 干净语音 STFT 谱 |
| 参数量 | **3.93 M** |
| RTF | **0.0048**（GPU，**型号未指明**；10 段 10 秒音频平均） |
| 推理步数 | **1**（设 $t=1$ 起，单次前向） |
| 骨干 | oSpatialNet-Mamba-Cond（+ fullband Mamba 层） |
| 因果性 | **半因果**：2–4 帧 lookahead（论文自称 "balance causality and enhancement quality"） |
| **算法延迟（论文声称）** | **"under 40 ms"** |
| **算法延迟（按库内口径）** | **50–70 ms**（论文漏计 30 ms 的 $\tau_{enc}$） |
| 库内定位 | **"生成式能不能靠近实时"的当前最佳回答**；**不可参与严格因果排名** |

> [!warning] 定位纪律
> SBM **不是严格因果方法**（有 2–4 帧 lookahead），且**算法延迟口径与库内不一致**。它**不能参与因果排名**，但**可以参与"生成式离实时有多远"的讨论**。

---

## 2. 组件表

| 组件 | 作用 | 实现 | 关键超参 |
|---|---|---|---|
| **SB 数据生成器** | 训练期采样中间态 | $x_t=\mu_x(t)+\sigma_x(t)z$；$\mu_x(t)=w_x(t)x+w_y(t)y$ | **VE** 噪声调度 |
| **oSpatialNet-Mamba** | 主骨干 | 依 oSpatialNet 设计 | — |
| **Gaussian Fourier 时间嵌入** | 把时间步注入骨干 | $\mathrm{emb}(t)$ **加到 Mamba 输入** | ⇒ 构成 oSpatialNet-Mamba-**Cond** |
| **fullband Mamba 层** | 补 oSpatialNet 的时间局限 | 捕捉全局谱动态与帧间依赖 | — |
| 其余结构 | 频率压缩 / 时间压缩 / 时间解压缩 / cross-band block / linear projection | — | — |
| **数据预测损失** | 训练目标 | $\mathcal{L}=\lambda_1\mathcal{L}_{mse}(S,\hat S)+\lambda_2\mathcal{L}_{mse}(\|S\|,\|\hat S\|)+\lambda_3\mathcal{L}_{mr,mse}(S,\hat S)+\lambda_4\mathcal{L}_{mr,mse}(\|S\|,\|\hat S\|)$ | $\lambda=1000,1000,500,500$ |

> [!note] "SB 训练"在本篇的实现方式
> **SB 不是通过求解反向 SDE 实现的**，而是：在插值路径上**采样中间态 $x_t$**，让模型学"从中间态回到干净目标"。论文强调 Eq.(1) "**在训练中充当数据生成器**"。
> ⇒ 这是"一步推理"能成立的前提：**生成能力被压进了骨干的参数里，推理时不需要迭代**。

---

## 3. Table 1 三测试集完整结果

列序 = Para.[M] / RTF↓ / SIG / BAK / OVRL / P808MOS / NISQA / SpeechBERTScore / Similarity / PESQ / ESTOI。

### 3.1 DNS With Reverb

| Model | Para | RTF | SIG | BAK | OVRL | P808 | NISQA | SBS | Sim | PESQ | ESTOI |
|---|---|---|---|---|---|---|---|---|---|---|---|
| SB-NCSN++(50) | 25.16 | 0.767 | 3.395 | 3.938 | 3.085 | 3.884 | 3.879 | 0.703 | 0.947 | 1.532 | 0.629 |
| SB-NCSN++(10) | 25.16 | 0.156 | 3.425 | 3.97 | 3.126 | 3.896 | 4.087 | 0.728 | 0.947 | 1.597 | 0.671 |
| SB-NCSN++(1) | 25.16 | 0.0155 | 3.281 | 3.871 | 2.948 | 3.559 | 3.323 | 0.730 | 0.943 | 1.586 | 0.67 |
| SBCTM | 65.98 | 0.02 | 2.927 | 3.859 | 2.623 | 3.035 | 2.578 | 0.494 | 0.859 | 1.218 | 0.281 |
| SB-UFOGen | 25.16 | 0.0152 | 2.964 | 3.664 | 2.596 | 3.337 | 2.131 | 0.662 | 0.918 | 1.383 | 0.601 |
| ZipEnhancer | 2.04 | 0.105 | 2.771 | 3.164 | 2.264 | 2.85 | 1.926 | 0.534 | 0.84 | 1.227 | 0.288 |
| Mamba-base | 3.61 | **0.0048** | 3.202 | 3.898 | 2.895 | 3.665 | 3.514 | 0.766 | 0.963 | 1.895 | 0.696 |
| FM-Mamba | 3.93 | **0.0048** | 3.164 | 3.956 | 2.887 | 3.461 | 3.148 | 0.682 | 0.930 | 1.643 | 0.634 |
| **SBM** | **3.93** | **0.0048** | **3.653** | **3.995** | **3.367** | **4.055** | **4.053** | **0.784** | **0.965** | **1.971** | **0.71** |

### 3.2 DNS No Reverb（关键行）

| Model | Para | RTF | SIG | BAK | OVRL | P808 | NISQA | SBS | Sim | PESQ | ESTOI |
|---|---|---|---|---|---|---|---|---|---|---|---|
| SBCTM | 65.98 | 0.02 | 3.523 | 4.128 | 3.298 | 3.906 | 4.574 | 0.870 | 0.986 | 2.835 | 0.898 |
| **ZipEnhancer** | 2.04 | 0.105 | 3.578 | 4.136 | **3.35** | 4.015 | 4.289 | **0.922** | **0.992** | **3.419** | **0.952** |
| Mamba-base | 3.61 | 0.0048 | 3.515 | 4.053 | 3.253 | 3.997 | 4.468 | 0.887 | 0.99 | 2.73 | 0.916 |
| **SBM** | 3.93 | 0.0048 | **3.751** | 4.129 | 3.292 | **4.187** | **4.657** | 0.893 | 0.99 | 2.825 | 0.921 |

### 3.3 VoiceBank-Demand（关键行）

| Model | Para | RTF | SIG | BAK | OVRL | P808 | NISQA | SBS | Sim | PESQ | ESTOI |
|---|---|---|---|---|---|---|---|---|---|---|---|
| SBCTM | 65.98 | 0.02 | 3.4 | 4.085 | 3.156 | 3.533 | 4.646 | 0.891 | 0.978 | 3.558 | 0.868 |
| **ZipEnhancer** | 2.04 | 0.105 | 3.484 | 3.988 | 3.183 | 3.544 | 4.621 | **0.925** | **0.986** | **3.628** | **0.894** |
| **SBM** | 3.93 | 0.0048 | 3.412 | **4.135** | 3.253 | **3.616** | **4.737** | 0.820 | 0.981 | 3.503 | 0.891 |

> [!contradiction] 判别式 ZipEnhancer 在 PESQ / ESTOI / SpeechBERTScore 上仍领先
> | 测试集 | 指标 | ZipEnhancer（2.04 M） | SBM（3.93 M） |
> |---|---|---|---|
> | DNS No Reverb | PESQ | **3.419** | 2.825 |
> | DNS No Reverb | ESTOI | **0.952** | 0.921 |
> | DNS No Reverb | SpeechBERTScore | **0.922** | 0.893 |
> | VoiceBank-Demand | PESQ | **3.628** | 3.503 |
> | VoiceBank-Demand | ESTOI | **0.894** | 0.891 |
> | VoiceBank-Demand | SpeechBERTScore | **0.925** | 0.820 |
>
> **SBM 的优势集中在 SIG / OVRL / P808MOS / NISQA（对齐无关指标）。**
> **论文的论证**：引用 **Blau & Michaeli 的 perception-distortion tradeoff**，指出"严格对齐敏感指标对偏离结构的惩罚重于对过度平滑的惩罚"，因此**把对齐无关指标定为主指标**。
> **另一处自陈**：训练混入 **25% double-talk** 以保留次要说话人 ⇒ 在单说话人隔离测试上 SpeechBERTScore 被拉低；论文称这是"策略性设计选择"。
> **库内处置：并列记录 + 标注作者解释，不判定谁对。**

---

## 4. Table 2：DNS Real Recordings（无干净参考）

| Model | SIG | BAK | OVRL | P808MOS | NISQA |
|---|---|---|---|---|---|
| SB-NCSN++(50) | 3.369 | 3.939 | 3.052 | 3.685 | 3.604 |
| SB-NCSN++(10) | 3.332 | 3.933 | 3.024 | 3.723 | 3.865 |
| SB-NCSN++(1) | 3.297 | 3.924 | 2.979 | 3.514 | 3.541 |
| SBCTM | 3.224 | 3.841 | 2.894 | 3.506 | 3.647 |
| SB-UFOGen | 3.255 | 3.838 | 2.911 | 3.485 | 3.196 |
| ZipEnhancer | 3.323 | 3.918 | 3.002 | 3.639 | 3.264 |
| Mamba-base | 3.284 | 3.974 | 2.993 | 3.683 | 3.644 |
| FM-Mamba | 3.32 | 4.031 | 3.052 | 3.562 | 3.797 |
| **SBM** | **3.459** | **4.106** | **3.198** | **3.742** | **3.937** |

⇒ **SBM 在真实录音上全项最高。**

---

## 5. "范式 × 骨干"消融表（Table 3）+ 差值列

**(M)** = mapping 范式，**(SB)** = SB 范式。

| Model | Params | SIG | BAK | OVRL | P808MOS | NISQA |
|---|---|---|---|---|---|---|
| MHSA(M) | 8.37 M | 2.975 | 3.809 | 2.676 | 3.233 | 2.358 |
| MHSA(SB) | 8.41 M | 3.221 | 3.941 | 2.927 | 3.60 | 3.24 |
| LSTM(M) | 17.38 M | 3.083 | 3.904 | 2.799 | 3.331 | 2.585 |
| LSTM(SB) | 17.42 M | 3.289 | 3.965 | 3.00 | 3.674 | 3.819 |
| Mamba(M) | 3.61 M | 3.284 | 3.974 | 2.993 | 3.683 | 3.644 |
| **Mamba(SB) = SBM** | **3.93 M** | **3.459** | **4.106** | **3.198** | **3.742** | **3.937** |

**范式维度（SB − mapping）**：

| 骨干 | Δ SIG | Δ BAK | Δ OVRL | Δ P808MOS | Δ NISQA |
|---|---|---|---|---|---|
| MHSA | **+0.246** | +0.132 | +0.251 | +0.367 | +0.882 |
| LSTM | **+0.206** | +0.061 | +0.201 | +0.343 | +1.234 |
| **Mamba** | **+0.175** | +0.132 | **+0.205** | +0.059 | **+0.293** |

**骨干维度（同等范式下）**：

| 对比 | 观察 |
|---|---|
| Mamba(SB) 3.93 M vs MHSA(SB) 8.41 M | Mamba **用不到一半参数**在 SIG/BAK/OVRL/P808/NISQA 上**全部更高**（3.459 vs 3.221 / 4.106 vs 3.941 / 3.198 vs 2.927 / 3.742 vs 3.60 / 3.937 vs 3.24） |
| Mamba(SB) 3.93 M vs LSTM(SB) 17.42 M | Mamba **用约 1/4.4 参数**在**全部五项**上更高（3.459 vs 3.289 / 4.106 vs 3.965 / 3.198 vs 3.00 / 3.742 vs 3.674 / 3.937 vs 3.819） |
| **Mamba(M) 3.61 M vs LSTM(SB) 17.42 M** | ⚠️ **LSTM(SB) 的 OVRL（3.00 vs 2.993）与 NISQA（3.819 vs 3.644）高于 Mamba(M)** ⇒ **范式与骨干各有独立贡献，是相乘而非替代关系** |

> [!important] 这是一条设计得很干净的消融
> 用 **3 骨干 × 2 范式**的完整交叉，把两个变量**解耦**：
> - 若只看 Mamba(SB) vs Mamba(M)，会误以为"SB 只对 Mamba 有效"；
> - 交叉证明 **SB 对 MHSA/LSTM 同样有效**（+0.246 / +0.206）⇒ **SB 是范式层面的普遍贡献**；
> - 同时 **Mamba(M) 3.61 M 已能与 LSTM(SB) 17.42 M 打平**（OVRL 2.993 vs 3.00，NISQA 3.644 vs 3.819 略低）⇒ **骨干选择的价值也很大**。
> ⇒ **库内可复用模板**：凡"新训练范式 × 新骨干"的论文，都应做这种交叉消融，否则无法分离两个变量的贡献。
> **公平性说明（论文原话）**："为给每个骨干可比容量，MHSA 与 LSTM 块的设计、隐藏维与超参按其与 Mamba 的结构对应关系精心配置，故模型规模不同。"

---

## 6. RTF / 参数量对照表

| Model | 参数量 (M) | RTF | 推理步数 | 相对 SBM 的 RTF 倍数 |
|---|---|---|---|---|
| SB-NCSN++(50) | 25.16 | 0.767 | 50 | **160×** |
| SB-NCSN++(10) | 25.16 | 0.156 | 10 | 32.5× |
| SBCTM | 65.98 | 0.02 | 1 | 4.2× |
| SB-UFOGen | 25.16 | 0.0152 | 1 | 3.2× |
| SB-NCSN++(1) | 25.16 | 0.0155 | 1 | 3.2× |
| ZipEnhancer（判别式） | **2.04** | 0.105 | 1 | 21.9× |
| Mamba-base | 3.61 | **0.0048** | 1 | **1.0×** |
| FM-Mamba | 3.93 | **0.0048** | 1 | **1.0×** |
| **SBM** | 3.93 | **0.0048** | **1** | — |

> [!important] "零推理开销"的关键证据
> **Mamba-base（3.61 M / RTF 0.0048）→ SBM（3.93 M / RTF 0.0048）**：
> 参数只增 **0.32 M**（时间嵌入模块），**RTF 完全不变**。
> ⇒ **SB 范式的收益是在"零推理开销"下获得的。** 论文也点出实用含义："**相同骨干结构意味着针对 Mamba 的端侧优化技术同样适用于 SBM，进一步便利其部署。**"
> 这与 [[wiki_low_latency/entities/LCA-Latency-Control-Adapter]] 的"adapter bank 只增存储不增运行时算力"是**同类设计性质**。

> [!warning] RTF 口径警告：与库内不可比
> - SBM：**GPU 上测，型号未指明**
> - [[wiki_low_latency/entities/LiSenNet]]：**Xeon E5-2620 v4 CPU**，RTF 0.028
> ⇒ **硬件类别不同、型号信息完整度不同 ⇒ 数值不可直接比较。**
> 按库内算力证据等级：SBM 属 **L1**（有 RTF + 硬件类别，但**无硬件型号、无算法延迟工作点、无 chunk 配置**）。
> 且 [[wiki_low_latency/entities/FastEnhancer]] 已证伪"名义算力低 = 快"⇒ 引用 SBM 的 RTF 时须标注硬件缺口。

---

## 7. "吞吐 vs 延迟"双轴结论表（★ 本篇对库内最重要的产出）

| 轴 | 结论 | 证据 |
|---|---|---|
| **吞吐（RTF）** | ✅ **生成式已接近实时** | 一步推理 + RTF **0.0048**（全表最低），比 SB-NCSN++(50) 快 **160×**；且**零推理开销**获得 SB 收益（RTF 与 Mamba-base 相同） |
| **算法延迟** | ❌ **生成式尚未进入严格因果超低时延区** | 2–4 帧 lookahead + 30 ms 窗 ⇒ **50–70 ms**；距库内约 2 ms 目标 **25–35 倍** |
| **质量** | ⚠️ **在 PESQ/ESTOI 上仍输给判别式** | ZipEnhancer 2.04 M：PESQ 3.628 vs 3.503（VBD）、3.419 vs 2.825（DNS No Rev）；SBM 优势在 SIG/OVRL/P808/NISQA |

> [!important] 这两个结论必须分开写
> **"生成式能不能靠近实时"这个问题，本篇的回答是分裂的**：
> - **能靠近"吞吐"**——这是工程意义上的实时（RTF ≪ 1）；
> - **不能靠近"算法延迟"**——这是库内关心的严格因果约束。
> **混为一谈会导致误读**：把 SBM 当作"生成式已经能用于 2 ms 场景"的证据，或把它的 50–70 ms 当作"生成式在延迟上无可救药"。
> ⇒ 库内记录方式：**在两个轴上分别记录，明确 SBM 只在吞吐轴上接近库内需求。**

---

## 8. 低时延账本与因果性审计

### 8.1 延迟账本（★ 含口径修正）

| 项 | 值 | 依据 |
|---|---|---|
| STFT 窗长 | 480 样本 @ 16 kHz = **30 ms** | 论文 §3.1 |
| STFT hop | 160 样本 @ 16 kHz = **10 ms** | 同上 |
| $\tau_{enc}=L_{len}/f_s$ | **30 ms** | 库内口径 |
| $\tau_{sep}=T_{la}\cdot L_{shift}/f_s$ | $T_{la}=2\sim4$ 帧 ⇒ **20–40 ms** | 论文 §2.2 |
| **论文声称的"算法延迟"** | **"under 40 ms"** | = $4\times10$ ms ⇒ **仅 $\tau_{sep}$** |
| **按库内口径的实际算法延迟** | **50 – 70 ms** | $\tau=\tau_{enc}+\tau_{sep}$ |
| RTF | 0.0048（GPU 型号未指明） | 论文 §3.2 |
| STFT center | **未报告** | — |
| 端到端延迟 | 未报告 | — |

> [!question] 这是"漏计 $\tau_{enc}$"的典型案例
> 论文的 "under 40 ms" **恰好等于 4 帧 lookahead × 10 ms hop** ⇒ 它**只计算了 lookahead 项，未计入 30 ms 的窗缓冲**。
> 而 [[wiki_low_latency/entities/LCA-Latency-Control-Adapter]] 论文 §3.2 恰恰明确警告过："**Note that some studies report latency without explicitly accounting for this buffering term, so care is needed when comparing them.**"
> ⇒ **SBM 正是它警告的那类文献。**
> **处置：按库内口径记录为 50–70 ms，并标注这是口径差异而非论文错误。不要替论文判定 "40 ms 成立"。**

### 8.2 因果性审计（逐项）

| 检查项 | 结论 |
|---|---|
| 是否严格因果？ | **否**（有 2–4 帧 lookahead） |
| 论文自称 | "a small lookahead of 2-4 frames" + "balance causality and enhancement quality" ⇒ 记为 **`limited-lookahead` / 半因果** |
| **fullband Mamba 层的作用域** | ⚠️ **未交代**。论文说它捕捉"全局谱动态与**帧间依赖**"（动机是 oSpatialNet 的时间局限）⇒ **若该层双向或全序列，则"2–4 帧 lookahead"的流式主张不成立**。**记为一处未闭合的因果缺口（`[!question]`），不替它判定** |
| 是否有全局池化 / 全序列统计量？ | **未说明** |
| 能否参与库内严格因果排名？ | **不能** |
| STFT center | **未报告**（记入"STFT center 审计表"待办） |

---

## 9. 与库内模型对照

| 模型 | 路线 | Mamba 方向 | 推理步数 | 参数量 | RTF | 算法延迟 | 训练数据 |
|---|---|---|---|---|---|---|---|
| **SBM** | **生成式（SB）** | 流式（2–4 帧 lookahead） | **1** | 3.93 M | **0.0048（GPU 未指明）** | **50–70 ms（论文称 <40 ms）** | **800 h** |
| [[wiki_low_latency/entities/RT-SEMamba]] | **判别式**（渐进蒸馏） | **因果** | 1 | 未报告 | 未报告 | **25 ms 约束** | 未报告 |
| [[wiki_low_latency/entities/PSMSE]] | 判别式（脉冲） | 因果 | 1 | 0.26 M | – | 30 ms | 未报告 |
| [[wiki_low_latency/entities/SEMamba++]] | 判别式（GAN） | **双向（非因果）** | 1 | 2.7 M | 0.021（A6000） | **无约束** | **44 h** |
| [[wiki_low_latency/entities/LiSenNet]] | 判别式 | 因果 | 1 | **37 K** | 0.028（Xeon CPU） | 未报告 | 未报告 |
| [[wiki_low_latency/entities/GTCRN]] | 判别式 | 因果 | 1 | **23.7 K** | 未报告 | 未报告 | 未报告 |

> [!important] 库内"判别式 vs 生成式在流式 Mamba 上"的直接对照
> **[[wiki_low_latency/entities/RT-SEMamba]]（判别式）vs SBM（生成式）** 是库内最直接的一对：
> | | RT-SEMamba | SBM |
> |---|---|---|
> | 范式 | 判别式（渐进知识蒸馏 8 层→1 层） | **生成式（SB 轨迹 + 一步）** |
> | Mamba | **因果** | 半因果（2–4 帧） |
> | 延迟 | **25 ms 约束** | **50–70 ms（论文称 <40 ms）** |
> | 测试集 | VoiceBank+DEMAND | DNS / VoiceBank-Demand |
> | PESQ | **3.32** | 3.503（VBD）/ 2.825（DNS No Rev） |
> | 参数量 | 未报告 | 3.93 M |
>
> ⇒ **判别式路线在"延迟约束"上更进取（25 ms 因果），生成式路线在"感知质量"上更强（SIG/OVRL/P808/NISQA）但在 PESQ 上不占优。**
> **这印证了库内"生成式与低延迟是两个几乎不相交的圈子"这一判断**——SBM 是"最接近相交"的一篇，但仍未相交。

---

## 交叉链接

- 源页：[[wiki_low_latency/sources/2026/Schrodinger Bridge Mamba 2026]]
- 概念页：[[wiki_low_latency/concepts/sbm-2026-schrodinger-bridge-mamba]]
- 同族 Mamba 流式：[[wiki_low_latency/entities/RT-SEMamba]]、[[wiki_low_latency/entities/PSMSE]]
- 同族非因果：[[wiki_low_latency/entities/SEMamba++]]
- 同类设计性质：[[wiki_low_latency/entities/LCA-Latency-Control-Adapter]]
- 口径：[[wiki_low_latency/concepts/严格因果与算法延迟]]、[[wiki_low_latency/concepts/低时延前端与延迟账本]]、[[wiki_low_latency/concepts/2409.10358-ultra-low-latency-benchmark]]
- 速度-算力纪律：[[wiki_low_latency/entities/FastEnhancer]]
- 全库判定口径：[[wiki_low_latency/overview]]
