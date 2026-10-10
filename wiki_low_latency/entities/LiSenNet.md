---
title: "LiSenNet"
type: entity
domain: low_latency_causal_se
category: 超轻量-子带-双路径
first_seen: 2024
source_page: "[[wiki_low_latency/sources/2024/LiSenNet 2024]]"
venue_status: preprint_only
created: 2026-09-27
updated: 2026-09-27
---

# LiSenNet

## 定义

**LiSenNet**（**Li**ghtweight **Sen**tence/speech **Net**work）是 USTC NERC-SLIP 等机构提出的**超轻量单通道语音增强网络**，arXiv:2409.13285（2024-09-20，**投稿 ICASSP 2025 未获录用**）。核心目标：在 **37k 参数 / 56M MMACs per second** 的预算内达到 VoiceBank+DEMAND **PESQ 3.07**。

结构上它有**五个组件**，其中三个是它自己的贡献：

| 组件 | 作用 | 是否本文贡献 |
|---|---|---|
| **子带 DS-Conv / US-Conv** | 低频走 stride 1、高频走 stride 3，整体频率降采样因子仍为 2 但**低频保分辨率** | ✅ 核心贡献 ① |
| **DPR（双路径循环）模块** | 频率轴 Bi-GRU + 时间轴单向 GRU；用 **ConvGLU** 补偿被砍的 RNN 容量 | ✅ 核心贡献 ② |
| **噪声检测器（ND，可选）** | 64 维 Mel 谱 → **帧级**二值门控，只把有噪帧送进后端 | ✅ 核心贡献 ③ |
| 相位差（PD）输入 | $\Delta_f P_x$、$\Delta_t P_x$（去基带偏移后）与压缩幅度谱拼接 | 沿用 [13][14] |
| GLA 相位精修 | Griffin-Lim 迭代精修相位，k=2 | 沿用 [24][25]，本文重新论证其对强幅度估计有效 |

工期口径：16 kHz、VoiceBank+DEMAND；**STFT window 512（32 ms）/ hop 256（16 ms）**。

## 证据

| 属性 | 证据（本地 PDF / 外部独立来源） |
|---|---|
| 作者与单位 | Haoyin Yan\*、Jie Zhang\*（通讯 jzhang6@ustc.edu.cn）、Cunhang Fan†、Yeping Zhou‡、Peiqi Liu‡；\* USTC NERC-SLIP，† 安徽大学多模态认知计算安徽省重点实验室，‡ **招商银行（CMB）深圳** |
| venue | **arXiv preprint (eess.AS)**；`venue_status: preprint_only`。arXiv `Comments` = "**submitted to** 2025 IEEE ICASSP" ⇒ 投稿记录，**非录用证据**（见 source 页 venue 判定） |
| 代码 | https://github.com/hyyan2k/LiSenNet（论文自陈"code and audio examples are available online"） |
| 参数量 | **37k**（Abstract / §I / Table I / Table III 四处一致） |
| 算力 | **56M MACs per second**（同上四处一致）；加 ND 时 **15M ∼ 70M**（Table II） |
| 主结果 | VoiceBank+DEMAND：**PESQ 3.07 / STOI 0.939**；WSJ0+ESC50：**PESQ 3.08 / RTF 0.028** |
| RTF 硬件 | **Intel(R) Xeon(R) E5-2620 v4 CPU**（§III.B 明写） |
| GLA 迭代 | k = 2（Table III 显示 k=2 饱和） |
| 训练 | AdamW，100 epochs，lr 5e-4（每 epoch ×0.98），梯度裁剪 L2 = 5.0 |
| 采样率与 STFT | 16 kHz；Hanning window 512（32 ms），hop 256（16 ms）；**`center` 未报告** |
| 复现件 | 论文声称 code + audio examples 公开 |
| **算力证据等级** | **L1**（有 RTF + 硬件型号）——但**缺 runtime 框架、chunk size、batch 是否为 1、是否含 STFT/iSTFT/GLA** |

### Table I 全场（VoiceBank+DEMAND，照抄原文）

| Method | Para. | MACs | PESQ | STOI |
|---|---|---|---|---|
| Noisy | – | – | 1.97 | 0.921 |
| RNNoise | 0.06M | 0.04G | 2.33 | 0.922 |
| CRN\* | 17.58M | 2.56G | 2.54 | 0.936 |
| DCCRN\* | 3.67M | 14.38G | 2.78 | 0.940 |
| FullSubNet\* | 5.64M | 30.87G | 2.89 | 0.940 |
| Fast FullSubNet\* | 6.84M | 4.14G | 2.79 | 0.935 |
| CCFNet+ (Lite) | 160k | 390M | 2.94 | – |
| **FSPEN** | 79k | 89M | **2.97** | **0.942** |
| **LiSenNet** | **37k** | **56M** | **3.07** | 0.939 |

`*` = 作者重训。**注意 FSPEN 的 STOI（0.942）高于 LiSenNet（0.939）**，论文只强调了 PESQ 的领先。

### Table II（WSJ0+ESC50，含 RTF）

| Method | Para. | MACs | RTF | PESQ |
|---|---|---|---|---|
| CRN | 17.58M | 2.56G | 0.042 | 2.80 |
| DCCRN | 3.67M | 14.38G | 0.184 | 3.05 |
| FullSubNet | 5.64M | 30.87G | 0.386 | 2.99 |
| Fast FullSubNet | 6.84M | 4.14G | 0.100 | 2.75 |
| **LiSenNet** | **37k** | **56M** | **0.028** | **3.08** |
| LiSenNet+ND | 55k | **15M∼70M** | **0.020** | 3.00 |

### Table III（消融，按 ΔPESQ 排序）

| 消融项 | Para. | MACs | PESQ | ΔPESQ | 统计证据 |
|---|---|---|---|---|---|
| **完整 LiSenNet** | 37k | 56M | **3.07** | 基准 | — |
| DPR (N=0) | 15k | 22M | 2.68 | **−0.39** | 无 |
| w/o L_pesq | 37k | 56M | 2.95 | **−0.12** | 无 |
| DPR (N=1) | 26k | 39M | 2.97 | −0.10 | 无 |
| w/o ConvGLU | 31k | 48M | 2.98 | −0.09 | 无 |
| w/o PD | 37k | 56M | 2.99 | −0.08 | 无 |
| w/o sub-band Conv | 30k | 54M | 3.01 | −0.06 | 无 |
| GLA (Noisy Phase) | 37k | 56M | 3.02 | −0.05 | 无 |
| w/o LSigmoid | 37k | 56M | 3.05 | −0.02 | ⚠️ **≤0.05，须标"未经显著性检验"** |
| DPR (N=3) | 48k | 72M | 3.06 | −0.01 | ⚠️ 同上 |
| GLA (k=1) | 37k | 56M | 3.06 | −0.01 | ⚠️ 同上 |
| GLA (k=2) / (k=3) | 37k | 56M | 3.07 | 0.00 | — |

> [!warning] **所有 ΔPESQ 均无 ± 标准差、无种子数、无显著性检验**
> 其中 **w/o LSigmoid（−0.02）、DPR N=3（−0.01）、GLA k=1（−0.01）三项 ≤0.02**，按本库第 6 条判定口径**不得用作"该模块有效"的证据**。

## 架构与状态

### ASCII 结构图（据 Fig. 1(a)，渲染图目视核对）

```
                       ┌──────────────── Optional ────────────────┐
x ──► select ──► STFT ─┤                                          │
        │              └──► (A_x)^c  ─┐                            │
        │                  Δ_f(A_x)^c ┤                            │
  ┌─────▼─────┐            Δ_t(A_x)^c ┘                            │
  │  Noise    │                     │                              │
  │ Detector  │                     ▼  concat                      │
  │  (Mel)    │              ┌─────────────┐                      │
  └───────────┘              │ Sub-band    │  ←── Conv Block      │
                             │ DS-Conv Blk │                      │
                             │  DPR  ×3    │  (N=2 ⇒ 图中 ×3 含首块)│
                             │ Sub-band    │                      │
                             │ US-Conv Blk │                      │
                             │ LSigmoid    │                      │
                             └──────┬──────┘                      │
                                    │ ──► (Â_y)^c                 │
                                    │                             │
                    ┌───────────────┴──────────┐                  │
                    │  Griffin-Lim Algorithm   │ ◄── P_x (含噪相位)│
                    │       (k = 2)            │                  │
                    └───────────────┬──────────┘                  │
                                    │ ──► iSTFT ──► ŷ             │
                                    └──────────────────────────────
```

> [!warning] Fig. 1(a) 的模块计数需要目视核对（抽取文本会丢）
> 渲染图显示 encoder 侧为 `Sub-band Conv Block → DS-Conv Block → DPR → Sub-band US-Conv Block` 的重复结构，decoder 侧标注 **×3**。
> 但 §III.A 文字写 "The DPR module is repeated **2 times** (i.e., **N = 2** in Fig. 1(a))"。
> ⇒ **图中的 ×3 与正文的 N=2 计数口径不同**（图中多半把"主体 + 2 次重复"都计数了）。**本库以正文的 N=2 为准**，并记录该计数差异。

### DPR 模块内部（Fig. 1(c)）

```
M ∈ R^{B×C×T×F}
   │
   ├─► reshape ──► BT × F × C ──► LayerNorm ──► Bi-GRU  (12 dim) ──┐
   │                                                              │ (+) ──►
   │   reshape ──► BF × T × C ──► LayerNorm ──► GRU   (24 dim) ──┐ │
   │                                                             │ │
   │        ┌──────────────── ConvGLU ────────────────┐          │ │
   └────────┤ Linear ──► DWConv ──► Mish ──► (gate) ───┤──────────┘ │
            └──────────────────────────────────────────┘            │
                                                                   ▼
                                                              LayerNorm ──► out
```

**因果性依据（论文唯一一句）**：「To ensure the causality of our model, we apply **bidirectional GRU (Bi-GRU) for frequency modeling and unidirectional GRU for temporal modeling**.」（§II.C）

### 子带 DS/US-Conv（Fig. 1(b)）

```
低频带：Conv2d stride 1 ──┐
高频带：Conv2d stride 3 ──┤──► 合并 ⇒ 整体频率降采样因子 = 2
      （升采样用 SP-Conv2d，因子 3）
```

## 损失函数

$$
\mathcal L = \lambda_1\mathcal L_{\text{mag}} + \lambda_2\mathcal L_{\text{comp}} + \lambda_3\mathcal L_{\text{pesq}} + \mathcal L_{\text{bce}},
\qquad (\lambda_1,\lambda_2,\lambda_3)=(0.9,\;0.1,\;0.05) \tag{9}
$$

| 项 | 定义 | 备注 |
|---|---|---|
| $\mathcal L_{\text{mag}}$ | 功率压缩幅度谱的 MSE（Eq. 6） | |
| $\mathcal L_{\text{comp}}$ | 功率压缩**复数谱**的 MSE（Eq. 7） | $Y^c=(A_y)^c e^{iP_y}$ |
| $\mathcal L_{\text{pesq}}$ | 判别器 $D$ 预测 PESQ 的 MSE（Eq. 8） | 源自 MetricGAN；**消融中贡献最大（−0.12）** |
| $\mathcal L_{\text{bce}}$ | ND 二分类交叉熵 | **仅含 ND 时**；无权重（系数 1） |

功率压缩比 **c = 0.3**（与库内多篇一致）。

## 低时延账本

| 项 | 值 | 证据状态 |
|---|---|---|
| 采样率 | 16 kHz | 明写 |
| STFT window | 512（**32 ms**） | 明写 |
| STFT hop | 256（**16 ms**） | 明写 |
| **STFT center** | **未报告** | ⚠️ 若 `center=True`，前端含 $W/2$ = **16 ms** 未来样本 |
| **算法延迟** | **未报告，且无处推导** | ⚠️ 论文无 window−hop、无 $W/2$、无 look-ahead、无推导式 |
| 隐含下界（本库推读） | $\ge$ hop = **16 ms**（若 center=False）；**$\approx$ 32 ms**（若 center=True） | **推读，非论文主张** |
| GLA 开销 | **未计入任何表** | ⚠️ k=2 次 STFT+iSTFT 往返，延迟与算力均未入账 |
| 模型级因果性 | `paper-claimed-causal`（**一句声明，无逐层证书**） | Bi-GRU 频率轴 / uni-GRU 时间轴 |
| chunk size | **未报告** | — |
| 峰值算力 | **未报告**（ND 只给区间 15M∼70M） | ⚠️ **最坏 70M > 无 ND 的 56M** |
| p50/p95/p99、deadline miss | **未报告** | — |
| 目标硬件 | "edge devices / hearing aids / headphones / IoT"（**泛指**）；RTF 在 **Xeon E5-2620 v4** 上测 | 无端侧真机数据 |

> [!warning] **这是一个"hop 16 ms"的模型，与本库约 2 ms 目标差一个数量级**
> 即使按最乐观读法（center=False、GLA 不计），**算法延迟下界也是 16 ms**。
> **它不是 2 ms 候选。** 本库收录它的价值在于：**它是"超轻量三角"里参数第二小的锚点，且是全库唯一有外部独立复训值的超轻量模型**（见下）。

## 因果性与结构审计

| # | 审计项 | 结果 |
|---|---|---|
| 1 | **逐层 padding 说明** | ✗ **无**（论文只有一句 Bi-GRU/uni-GRU 声明） |
| 2 | **时间轴卷积 kernel** | ⚠️ 未明确；encoder/decoder 的 Conv2d 是否沿时间轴有感受野未说明 |
| 3 | **归一化可融合性** | ⚠️ 用 **LayerNorm**（Conv Block 内）+ 另在 DPR 内用 LayerNorm。**LN 不可融合进卷积** ⇒ 按 [[wiki_low_latency/sources/2025/FastEnhancer 2025]] 的"零算术变化"证据，这是一个**实测 RTF 高于 MACs 暗示值**的候选解释 |
| 4 | **global pooling / 全序列统计** | ✓ **未发现**（未使用通道注意力或全局池化）——**比 PrimeK-Net 的 SCA 干净** |
| 5 | **STFT 帧锚定（center）** | ✗ **未报告** ⇒ 系统级因果性双向不确定 |
| 6 | **GLA 的流式可实现性** | ✗ **未说明**；**FastEnhancer 独立指出其"not streamable because of griffin-lim"** |
| 7 | **ND 是否引入跨帧依赖** | ✓ 否（帧级独立判决）——但**不省尾延迟** |
| 8 | **算力是否固定** | ✗ 否（含 ND 时随噪声比例 15M∼70M 波动，**未报峰值**） |

## 结果与证据边界

### 外部独立证据（**不并入上方表格**）

[[wiki_low_latency/sources/2025/FastEnhancer 2025]] 对 LiSenNet 有 6 处引用，其中三条为**原文没有的信息**：

| 项 | FastEnhancer 的记载 | 本篇原文 |
|---|---|---|
| **流式性** | LiSenNet^b「**Not streamable because of input normalization and griffin-lim**」 | **未提及** |
| **可流式版本** | LiSenNet^c（去掉 input normalization 与 griffin-lim 后重训），RTF **0.034**（Xeon Gold 6248R）/ 0.028（M1） | **无此版本** |
| **扩展指标** | ^b/^c 的 SCOREQ（0.425/0.335）、SISDR（13.5/18.5）、BAK（3.90/4.03）、WER（3.7/3.4） | **全部未报告** |
| PESQ | ^b **3.08**（≈本篇 3.07）/ ^c **2.98** | **3.07** |

> [!contradiction] 两篇对"LiSenNet 有几个版本"的指称不一致
> 本篇：**一个模型**，PESQ 3.07，无流式/非流式之分。
> FastEnhancer：**两个版本** ^b（官方代码、不可流式、3.08）与 ^c（自定义流式化、2.98）。
> ⇒ **3.08 ≈ 3.07 对上了官方版本**；**2.98 是本篇从未报告的"流式化之后"的值**。
> **本库不判定谁对**，按双方原文并列记录。最可能的解释已在 source 页 §5.2 的 `[!question]` 中给出。

### 与库内其他超轻量模型的三方对照

| 模型 | 参数 | 算力 | PESQ | STOI | 因果性 | 延迟 | 算力证据等级 |
|---|---|---|---|---|---|---|---|
| [[wiki_low_latency/entities/GTCRN]] | **23.7 K** | 39.6 MMACs/s | 2.87\* | — | `paper-claimed-causal` | hop 16 ms（center 未报） | **L0** |
| **LiSenNet** | **37 k** | 56 MMACs/s | **3.07** | 0.939 | `paper-claimed-causal` | hop 16 ms（center 未报） | **L1**（RTF + CPU 型号） |
| FSPEN | **79 k** | 89 M（本篇）/ 64 M（FastEnhancer ^d） | 2.97 | **0.942** | 未知（**库中无页面**） | 未知 | L1（FastEnhancer 测） |

\* GTCRN 的 2.87 来自 FastEnhancer Table 2 的 GTCRN^a（官方 checkpoint），**非 GTCRN 原文值**。

> [!important] 这条对照表本身就是一处**口径警示**
> 三个数字的**来源各不相同**：GTCRN 用官方 checkpoint（FastEnhancer 测）、LiSenNet 用**官方训练代码 + 自己的评测**、FSPEN 用**FastEnhancer 重实现重训**。
> ⇒ **禁止把它们放进同一次效率排名**。本库在 [[wiki_low_latency/sources/2024/GTCRN 2024]] 已就"基线来源不统一"立过警示，本篇是同一问题的第三个实例。

## 参数量与算力口径对照

| 口径 | 参数 | 算力 | 来源 | 可否调和 |
|---|---|---|---|---|
| **本篇原文** | 37k | 56M MACs/s | Abstract、§I、Table I、Table III（**四处内部自洽**） | **基准** |
| FastEnhancer ^b | 37 | 56M | FastEnhancer Table 2 | ✅ **完全一致** |
| FastEnhancer ^c | 37 | 56M | 同上（流式化改造**不改参数与 MACs**） | ✅ 一致（合理的，因只去了归一化与 GLA） |
| PSMSE 转述 | （归入 23.7K–79K 一组） | — | PSMSE §Related Work | ✅ 不冲突（区间转述） |

> [!note] 本篇是**锚点数值最干净的一篇**：37k/56M 在四处原文与一处外部引用间**完全一致，无任何矛盾**
> 与 [[wiki_low_latency/entities/GTCRN|GTCRN]]（三套口径）和 [[wiki_low_latency/entities/PrimeK-Net|PrimeK-Net]]（FLOPs 新量纲）形成对照。
> ⇒ **本库可以用 LiSenNet 作为"引用链可信度"的正面对照组**：当一个锚点的四份记录完全一致时，说明该领域的引用是干净的。

## 交叉链接

- source 页：[[wiki_low_latency/sources/2024/LiSenNet 2024]]
- 概念页：[[wiki_low_latency/concepts/2409.13285-subband-stride-and-convglu-compensation]]
- 同路线：[[wiki_low_latency/entities/GTCRN]]、[[wiki_low_latency/entities/FastEnhancer]]
- 被批评处：[[wiki_low_latency/sources/2025/FastEnhancer 2025]]（§2.2 + Table 2 ^b/^c）、[[wiki_low_latency/sources/2026/PSMSE 2026]]（容量受限）
- 双路径范式：[[wiki_low_latency/concepts/2107.05429-dual-path-recurrent-context]]、[[wiki_low_latency/sources/2021/DPCRN Low-Latency Direction 2021]]
- 动态算力对照组：[[wiki_low_latency/sources/2022/Skip-DPCRN 2022]]、[[wiki_low_latency/sources/2024/D-GRU 2024]]、[[wiki_low_latency/sources/2026/Early Exit Compute-Matched 2026]]
- 判据页：[[wiki_low_latency/overview]]（第 5 条"平均算力 ≠ 可用算力"、第 6 条"小效应量须配统计证据"）

> [!warning] 库中暂无 FSPEN 页面
> FSPEN（ICASSP 2024, pp. 10671–10675, DOI `10.1109/ICASSP48485.2024.10446016`）是**本篇最主要的对手与前身**，但本库目前**没有它的页面**，所有 FSPEN 数字均来自二手转述（本篇 Table I、FastEnhancer Table 2）。
> **这正是 §Table I 那处 `89M vs 64M` MACs 矛盾的根源。** FSPEN 为 **IEEE 付费墙 + 无 arXiv 版**（Semantic Scholar `openAccessPdf: CLOSED`），按本库规则**需用户提供 PDF 方可补摄**。
