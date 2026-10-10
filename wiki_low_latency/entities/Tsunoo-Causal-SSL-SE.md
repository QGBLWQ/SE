---
title: Tsunoo-Causal-SSL-SE
type: entity
created: 2026-09-24
updated: 2026-09-24
tags:
  - speech-enhancement
  - single-channel
  - streaming
  - causal-se
  - causal-transformer
  - self-supervised-learning
  - wavlm
  - semantic-token
  - vector-quantization
  - semantic-prediction
  - multi-task-learning
  - film
  - paper-claimed-causal
  - no-latency-reported
sources:
  - [[wiki_low_latency/sources/2024/Tsunoo Causal SSL Semantic 2024]]
related:
  - [[wiki_low_latency/concepts/2412.19248-causal-ssl-semantic-prediction]]
  - [[wiki_low_latency/entities/DPCRN]]
  - [[wiki_low_latency/entities/DCCRN]]
  - [[wiki_low_latency/entities/Distil-DCCRN]]
  - [[wiki_low_latency/entities/PSMSE]]
  - [[wiki_low_latency/entities/RT-SEMamba]]
  - [[wiki_low_latency/entities/D-GRU]]
  - [[wiki_low_latency/concepts/2008.00264-complex-phase-enhancement]]
  - [[wiki_low_latency/concepts/严格因果与算法延迟]]
  - [[wiki_low_latency/concepts/低时延前端与延迟账本]]
  - [[wiki_low_latency/concepts/低 SNR 人声保留评估]]
---

# Tsunoo-Causal-SSL-SE

## 定义

**Tsunoo-Causal-SSL-SE** 指本地论文 2412.19248（Tsunoo, Saito, Nakata, Saruwatari, ICASSP 2025）提出的因果语音增强系统。它不是单个网络，而是一条**三段式管线 + 一个多任务训练目标**：

1. **近似因果的 WavLM 前端**——把非因果 WavLM base 限制为"只用过去帧、取最后一帧"（Eq. 5）；
2. **FiLM 融合的掩蔽估计器**——3 层 causal Transformer，把 log1p 谱特征与因果 SSL 特征用 FiLM 结合（Eq. 6、13）；
3. **VQ 语义量化 + 未来 token 预测分支**——把因果 SSL 特征离散成 1024 个 semantic token，并让 SSL 编码器 $g$ 并行预测未来 $N=5$ 个 token（Eq. 7、11、12），三者以 MTL 联合训练（Eq. 14）。

它在本库的核心身份是：**"用未来语义预测补偿因果上下文缺口"这条设计原则的首个 SE 实现**。论文用 Table IV 的 C1/C2 vs N1/N2 对照证明该原则**只在因果条件下有效**（因果 +0.05 / 非因果 0.00）。主结果 PESQ **2.88**（VoiceBank + DEMAND）。

本库判定：**`paper-claimed-causal`（近似实现，非架构级因果）**，且**延迟与算力账本为空**——论文未报告参数量、MACs、RTF 与任何延迟数字。这不是本 Wiki 约 2 ms 目标的已验证系统。

> [!note] 命名说明
> 实体名取"作者姓氏 + 方法定位"：`Tsunoo`（第一作者）+ `Causal-SSL-SE`（因果 + SSL 特征 + 语音增强）。论文本身**没有给方法起缩写名**（无如 "CSE-SSL" 之类的命名），因此本页不使用任何论文未出现的缩写。涉及该系统的组件时，本页沿用论文自身的符号 $c(X)$、$g$、$f$、$E$、$D$、$e$。

## 证据

| 属性 | 本地 PDF 证据 |
|---|---|
| 任务 | 单通道实时（因果）语音增强，VoiceBank + DEMAND [27–29]；p.1 §I、p.4 §V-A |
| 输入 | noisy 谱 $X\in\mathbb R^{T\times F}$；log 1p 特征 $X'=\log(1+\lvert X\rvert)$，Eq. (1)，p.2 §II |
| SSL 模型 | **WavLM base** [16]；p.3 §V-A |
| SSL 特征聚合 | 各层输出加权和 $s(X)=\sum_{i=1}^{I}w_isi(X)$，$w_i$ **可训练**，Eq. (2)，p.2 §II |
| SSL 参数更新 | 依 [19]，**只更新 SSL 模型里 Transformer 层的参数**最有效；p.2 §II |
| 因果 SSL 构造 | $c(X)=\{s(X_{\le t})_t\mid 1\le t\le T\}$（只用过去帧、取 $s(X_{\le t})$ 的**最后一帧**），Eq. (5)，p.2 §III-A；来源引 [31] = Tsunoo et al. Run-and-back stitch search, ICASSP 2022 |
| baseline 掩蔽网络 | [19] Hung et al.：线性层 + **双向 LSTM**，直接拼接（$\oplus$）SSL 特征，Eq. (3)；p.2 §II |
| 因果掩蔽网络 | **causal Transformer** [32]：「self-attention layers can only attend to past frames」，p.2 §III-B |
| 特征融合 | **FiLM** [33] 替换拼接：$X'\otimes c(X)=\gamma(c(X))\odot\alpha(X')+\beta(c(X))$，$\alpha,\beta,\gamma$ 为线性函数，Eq. (6)，p.2 §III-C |
| VQ 编码/解码 | 均为**线性层** $E(\cdot)$ / $D(\cdot)$——刻意让量化"perform similarly to k-means clustering"；p.3 §IV-A |
| VQ 损失 | $L_{\mathrm{vq}}=\lVert c(X)-D(e)\rVert_2^2+\lVert\mathrm{sg}[E(c(X))]-e\rVert_2^2+\xi\lVert\mathrm{sg}[e]-E(c(X))\rVert_2^2$，Eq. (7)，p.3 §IV-A；另用 moving average [35] |
| codebook 尺寸 | **1024**，p.3 §V-A |
| 语义预测输入形式 | 三种：$Z=c(X)$（Eq. 8）、$Z=c(X)\oplus\mathrm{emb}(\hat e)$（Eq. 9，索引）、$Z=c(X)\oplus e$（Eq. 10，隐向量）；实验中**采用 (10)**，p.3 §IV-B、p.4 Table I |
| 语义预测并联性 | 未来 $N$ 个 token **并行（simultaneously）**预测，类比 reduction factor [36]；**非自回归**；p.3 §IV-B 与 Figure 2 caption |
| 语义预测概率 | $p(e_{t+1:t+N}\lvert Z_{\le t})=\prod_{n=1}^{N}p(e_{t+n}\lvert Z_{\le t})$，Eq. (11)；**每个因子只条件于 $Z_{\le t}$** |
| 语义预测损失 | $L_{\mathrm{ce}}=\sum_{t=1}^{T-N}\sum_{n=1}^{N}q(e_{t+n})\log p(e_{t+n}\lvert Z_{\le t})$，Eq. (12)；$q(e)$ 为未来帧经 VQ 得到的参考分布 |
| 最终掩蔽 | $\hat X'=X'\odot\sigma(f(X'\otimes g(Z)))$，Eq. (13)，p.3 §IV-C |
| SE 损失 | $L_{se}=\lVert Y'-\hat X'\rVert_1$，Eq. (4)，p.2 §II |
| 总损失 | $L=\lambda_{se}L_{se}+\lambda_{vq}L_{vq}+\lambda_{ce}L_{ce}$，Eq. (14) |
| 波形重建相位 | **使用原始 noisy 相位**；p.2 §II 末 |
| 架构配置 | 3 层 causal Transformer **×2**（SSL encoder $g$ 与 SE mask estimator $f$）；**4 heads**；hidden 分别为 **512 / 256**；p.3 §V-A |
| 训练超参 | $\xi=0.1$；$\{\lambda_{se},\lambda_{vq},\lambda_{ce}\}=\{1,1,0.01\}$；**200 epochs**；lr $10^{-4}$；**Adam**；p.3 §V-A |
| 参数量 | **未报告** |
| 算力 / RTF / 延迟 | **全部未报告**——论文无任何 MACs、FLOPs、RTF、毫秒数字 |
| 采样率 / STFT 参数 | **全部未报告**（无 window / hop / FFT / center） |
| 因果性 | Eq. (5) 是 `low_look_ahead` 式近似；掩蔽网络有方向性声明；**无逐层 padding certificate、无 state 清单** |

## 架构与状态

~~~text
                    noisy waveform x
                          │
              ┌───────────┴───────────┐  ← STFT 参数【未报告】
              ▼                       ▼
      ┌───────────────┐       ┌──────────────────────────────┐
      │ WavLM base [16]│       │  log 1p 特征                 │
      │ (非因果)       │       │  X' = log(1 + |X|)   Eq. (1) │
      └───────┬───────┘       └──────────────┬───────────────┘
              │                              │
   各层输出加权和 s(X)=Σ w_i·s_i(X)  Eq. (2) │
              │  ← w_i 可训练                 │
   ┌──────────▼───────────┐                  │
   │ 因果化近似  Eq. (5)   │                  │
   │ c(X)={s(X≤t)_t | 1≤t≤T}                 │
   │ ★ 时刻 t 需 s(X≤t) 的最后一帧            │
   │   ⇒ 流式下每个时刻重跑一次 WavLM base    │
   │   ⇒ 计算量随帧数线性膨胀【论文未量化】    │
   └───┬───────┬──────────┘                  │
       │       │                             │
       │       └──────► VQ  ──────────┐      │
       │                │             │      │
       │        ┌───────▼──────┐   ┌──▼───┐  │
       │        │ Encoder E(·) │   │Decode│  │
       │        │  线性投影     │   │D(e)  │  │
       │        └───────┬──────┘   └──▲───┘  │
       │                │             │      │
       │      选最近 codebook e (1024) │      │
       │        ┌───────┴─────────────┘      │
       │        │                            │
       │        │  L_vq = ‖c(X)−D(e)‖² + ‖sg[E(c(X))]−e‖²
       │        │        + ξ‖sg[e]−E(c(X))‖²            Eq. (7)
       │        │                            │
       ▼        ▼                            │
  ┌──────────────────────────────┐           │
  │ SSL feature encoder g        │           │
  │ Z = c(X) ⊕ e        Eq. (10) │           │
  │ 3 × Causal Transformer block │           │
  │ (4 heads, hidden 512)        │           │
  └───┬──────────────────────┬───┘           │
      │                      │               │
      │                      ▼               │
      │            ┌──────────────────┐      │
      │            │ Linear → next N=5│      │
      │            │ tokens (并行)     │      │
      │            │ L_ce  Eq. (12)   │      │
      │            └──────────────────┘      │
      │                                      │
      │  g(Z)                                │
      ▼                                      │
  ┌──────────────────────────────┐           │
  │ FiLM  X' ⊗ c(X) =            │◄──────────┘
  │   γ(c(X)) ⊙ α(X') + β(c(X))  │  Eq. (6)（本例用 g(Z) 代 c(X)）
  └───────────────┬──────────────┘
                  ▼
  ┌──────────────────────────────┐
  │ SE mask estimator f          │
  │ 3 × Causal Transformer block │
  │ (4 heads, hidden 256)        │
  │ → Linear → sigmoid 掩蔽       │
  └───────────────┬──────────────┘
                  ▼
      X̂' = X' ⊙ σ(f(X' ⊗ g(Z)))     Eq. (13)
                  │
                  ▼
      L = λse·Lse + λvq·Lvq + λce·Lce   Eq. (14)
      Y' 为目标（干净语音 log 1p 谱）
                  │
                  ▼
      波形重建：掩蔽后的幅度 + **原始 noisy 相位**（论文未做相位估计）

  三处 MTL 并行训练：SE（f） / VQ（E,D,codebook） / 语义预测（g 的预测分支）
~~~

> [!warning] 图上最该盯住的一行：Eq. (5) 的因果化不是一次前向
> 图中 `c(X)={s(X≤t)_t}` 这一格是一个**集合**，不是一次计算。为了得到 $T$ 帧的 $c(X)$，需要对每个 $t$ 取一次 $s(X_{\le t})$ 的输出末帧——在流式设定下这意味着**每个时刻都跑一次完整 WavLM base**（输入长度随 $t$ 增长）。论文对这一点的处理是**零**：没有 MACs、没有 RTF、没有"用滑窗/缓存优化"的任何说明。这是本页与该源页的核心 warning（见 [[wiki_low_latency/sources/2024/Tsunoo Causal SSL Semantic 2024]] §5 第 5 条）。

## 低时延账本

| 字段 | 本篇证据/边界 |
|---|---|
| 采样率 | **未报告**（VoiceBank-DEMAND 惯例为 16 kHz，但**论文没有写过这句话**，本页不代填） |
| STFT window / hop / FFT | **全部未报告** |
| STFT center / 帧锚定 / look-ahead | **未报告**——无法判断前端是否含 $W/2$ 未来样本 |
| 算法延迟 | **未报告**——论文无任何 window−hop、$W/2$ 或推导式 |
| 模型 p50 / p95 / p99 | **未报告** |
| RTF | **未报告** |
| MACs / FLOPs | **未报告** |
| 参数量 | **未报告** |
| 前端因果性 | Eq. (5)：形式上是"只用过去帧、取最后一帧"；**非架构级因果**。WavLM base 的位置卷积 / 相对位置偏置是否引入未来依赖，**未做逐层审计** → `low_look_ahead` 近似 |
| 掩蔽网络因果性 | causal Transformer：「self-attention layers can only attend to past frames」（p.2 §III-B）；**无逐层 padding certificate、无 state 清单** → `paper-claimed-causal` |
| 前端计算代价 | 按 Eq. (5) 字面实现，**每个时刻一次完整 WavLM base 前向**，总量随帧数增长（本页推导）——**论文未量化** |
| warm-up / state reset | **未报告** |
| 长流稳定性 | **未报告** |
| 目标硬件 | **未报告** |
| 峰值 RAM / SRAM | **未报告** |
| 量化 / 定点精度 | **未报告** |
| 功耗 | **未报告** |
| 端到端 | ADC/DMA、I/O buffer、线程调度、DAC/playout、capture-to-playback、underrun/overrun **全部未报告** → 未验证 |
| 输出相位口径 | **使用原始 noisy 相位**（p.2 §II 末）——与因果性无关，但属输出口径，比较时须记账 |

实体判定：**`paper-claimed-causal`（Eq. 5 近似实现，非架构级因果）/ 延迟与算力账本全空 / 无任何硬件或 wall-clock 证据 / 输出仅幅度掩蔽、不做相位**。

> [!warning] 这个实体在本库的特殊性：**它比"只有 MACs 没有延迟"还要空一档**
> - [[wiki_low_latency/entities/D-GRU]]：只报 MAC/s，无延迟 → 至少有一个**固定算力数字**，可与其他固定算力模型横比；
> - [[wiki_low_latency/entities/LaCo-SENet]]：报了**逐层可复算的 Eq. (3)** + ONNX RTF 曲线 → 本库因果审计的最高标准；
> - **Tsunoo-Causal-SSL-SE**：**连 MACs 和参数量都没有**。它报的全是质量指标（PESQ/STOI/CSIG/CBAK/COVL）。
>
> 因此本库**不能**把它放进任何算力-质量或时延-质量的散点图上。唯一可做的定性判断是：Eq. (5) 的"每帧重跑一次 WavLM base"在计算量上与"约 2 ms 端侧"相距甚远——但**这是一个定性推理，不是论文提供的数据**。

## 结果与证据边界

- **支持**：
  - VoiceBank + DEMAND 上 **PESQ 2.88 / STOI 0.94**（Table II，w/ semantic prediction + codebook latent vector）；
  - 语义预测 MTL **在因果条件下有效**：C1 (2.88) vs C2 (2.83) = **+0.05**（Table IV，$\lambda_{ce}=0$ 即关闭）；
  - 语义预测 MTL **在非因果条件下无效**：N1 (3.14) vs N2 (3.14) = **0.00**——这是一个干净的条件对照，也是本篇最强的证据；
  - **FiLM 优于拼接**：因果下 C2 vs C3 = 2.83 vs 2.67（**+0.16**）；非因果下 N2 vs N3 = 3.14 vs 3.09（+0.05）；
  - **causal Transformer 优于单向 LSTM**：S1 vs S2 = 2.64 vs 2.58（**+0.06**）；
  - **codebook 隐向量优于索引**：2.88 vs 2.86（Table I，+0.02）；
  - **$N=5$ 为最佳预测步数**：N=1/3/5/8/10 → 2.81/2.85/**2.88**/2.83/2.82，token 预测准确率 33.7%/21.5%/17.0%/13.0%/10.3%（Table III）。
- **不支持**：
  - 约 2 ms 级系统已达成（**论文完全没有延迟数据**）；
  - 达到 SOTA——论文自己的表述是「outperformed **most of** the other conventional methods, and **comparable to** state-of-the-art method that, unlike our model, estimates appropriate phase information」；Table II 中 **LFSFNet 为 2.91 > 本篇 2.88**；
  - WavLM 已被改造成架构级因果模型（Eq. 5 只是近似，内部逐层依赖未审计）；
  - 因果 SSL 特征的构造在流式下可高效实现（Eq. 5 的字面实现需要逐帧重算完整 WavLM base）；
  - 低 SNR 下的人声保留已证明；
  - 语义预测"预测错音素 → 抑制真实辅音"的风险已被检验（**论文零失败案例分析**）。
- **未报告**：采样率、STFT window/hop/FFT/center、参数量、MACs/FLOPs、RTF、算法延迟、端到端延迟、目标硬件、p50/p95/p99、峰值 RAM/SRAM、量化/定点、功耗、deadline miss、warm-up、state reset、长流稳定性、batch size、随机种子数、学习率调度、训练/验证/测试集的确切规模与划分、$I$（参与的 SSL 层数）、负 SNR 分层、噪声类型分层、DNSMOS SIG/BAK/OVL、false-suppression、ASR WER、F0/formant/prosody、voiced energy、SPP/VAD 校准。
- **可比性提醒**：
  - Table II 明确写「The numbers of the conventional methods are based on the **literature**」——**基线数字抄自各原始论文**，不是在本文统一条件下复现的；表内各行的前端、训练数据、评价协议一致性**无法确认**。DCCRN+ 与 LFSFNet 的 CSIG/CBAK/COVL 为 `-`（未报告）。
  - 本实体与 [[wiki_low_latency/entities/DPCRN]] / [[wiki_low_latency/entities/DCCRN]] 是同一任务（时频域增强）但**不同输出口径**：本篇只做幅度掩蔽 + 用 noisy 相位，而 DPCRN/DCCRN 走复数谱/相位路线（详见 [[wiki_low_latency/concepts/2008.00264-complex-phase-enhancement]]）。跨这两条线比 PESQ 时，必须先扣掉相位这一项——本篇论文自己也做了这个归因（但**未验证**）。
  - 与 [[wiki_low_latency/entities/PSMSE]]（0.26 M / 0.11 G/s）、[[wiki_low_latency/entities/RT-SEMamba]]（25 ms）**不可做任何算力/时延比较**：本篇没有任何对应量。
- **数字口径警示**：
  1. 全文所有比较**无方差、无置信区间、无显著性检验、无多次运行**。关键效应量为 **+0.05（语义预测，因果）/ +0.02（codebook 隐向量）/ +0.03（因果 SSL 特征的有无，S1 vs C3）**——在 PESQ 的 0.01 报告粒度下，后两者属于**噪声区**，引用时须注明"未经显著性检验"。
  2. **STOI 不随语义预测变化**：C1 与 C2 的 STOI 都是 **0.94**（C1 的 PESQ 高 0.05）——即语义预测的增益**完全没有体现在可懂度上**。论文未讨论这一分离。
  3. **S1 与 C3 的对照不是"去掉 WavLM"的干净消融**：S1 (`Causal Trans.` / WavLM=None) vs C3 (`Causal Trans.` / WavLM=Causal，无 FiLM 无语义) 的**唯一变量确实是 SSL 的有无**（+0.03），但论文原文把"只有 log1p 特征时性能下降"与"causal Transformer 优于 LSTM"两件事混在一段里叙述，容易把 S1–C3 与 S1–S2 两组差值误算成一个。本库按 Table IV 的勾选结构拆开记账。
  4. **Accuracy 单调、PESQ 非单调**（Table III）：N=1 的准确率最高（33.7%）但 PESQ 最低（2.81）——说明语义预测的价值来自**信息量**而非**准确率**。这个反直觉点论文只用一句话带过。

## 交叉链接

- 源论文：[[wiki_low_latency/sources/2024/Tsunoo Causal SSL Semantic 2024]]
- 概念展开：[[wiki_low_latency/concepts/2412.19248-causal-ssl-semantic-prediction]]
- 同为时频掩蔽/因果增强（相位路线对照）：[[wiki_low_latency/entities/DPCRN]]、[[wiki_low_latency/sources/2021/DPCRN Low-Latency Direction 2021]]、[[wiki_low_latency/entities/DCCRN]]、[[wiki_low_latency/sources/2020/DCCRN Low-Latency Direction 2020]]、[[wiki_low_latency/concepts/2008.00264-complex-phase-enhancement]]
- 同为流式（都有延迟/算力数据，本篇没有）：[[wiki_low_latency/entities/PSMSE]]、[[wiki_low_latency/sources/2026/PSMSE 2026]]、[[wiki_low_latency/entities/RT-SEMamba]]、[[wiki_low_latency/sources/2026/RT-SEMamba 2026]]
- 同为"补上下文缺失"，手段是蒸馏：[[wiki_low_latency/entities/Distil-DCCRN]]、[[wiki_low_latency/sources/2024/Distil-DCCRN 2024]]、[[wiki_low_latency/concepts/2309.08144-two-step-distillation]]（two-stage vs 本篇 one-stage 的对照）
- 同为"只有算力/没有延迟"的负面参照：[[wiki_low_latency/entities/D-GRU]]、[[wiki_low_latency/sources/2024/D-GRU 2024]]
- 前端账本口径：[[wiki_low_latency/concepts/2204.09911-short-asymmetric-stft]]、[[wiki_low_latency/concepts/低时延前端与延迟账本]]
- 最严因果口径（尺子）：[[wiki_low_latency/entities/LaCo-SENet]]、[[wiki_low_latency/sources/2026/LaCo-SENet 2026]]、[[wiki_low_latency/concepts/2606.19688-latency-configurable-asymmetric-padding]]
- 延迟/因果性口径：[[wiki_low_latency/concepts/严格因果与算法延迟]]、[[wiki_low_latency/concepts/2409.10358-ultra-low-latency-benchmark]]
- 人声保留缺口：[[wiki_low_latency/concepts/低 SNR 人声保留评估]]

> [!question] 待验证
> **(1) WavLM base 是否真因果。** Eq. (5) 是"限制访问 + 取最后帧"的**近似**，不是架构级因果改造。WavLM 的位置卷积（feature extractor）与 Transformer 层的相对位置偏置是否在 $s(X_{\le t})$ 内部引入对 $t$ 之后的依赖，**论文未做逐层审计**。按本库最严口径（[[wiki_low_latency/concepts/2606.19688-latency-configurable-asymmetric-padding]]），应记为 `paper-claimed-causal` + `low_look_ahead` 近似，**不能**标 `strict_causal`。
> **(2) Eq. (5) 的流式实现代价未知。** 这是本实体最大的工程疑点：为得到 $T$ 帧的 $c(X)$，是否必须对每个 $t$ 重跑一次完整 WavLM base？论文**没有给任何实现说明、没有 MACs、没有 RTF**。若确实是重算型实现，"实时"这一动机本身就无法成立——这是可以直接补的实验（滑窗缓存 / 增量 state 的可行性研究）。
> **(3) STFT 前端口径全空。** window/hop/FFT/center/look-ahead **一个都没报**。因此即便 SSL 与掩蔽网络都完美因果，**前端的因果性在本库依然无法确认**，任何算法延迟都无从计算。
> **(4) 人声保留与机制风险的空白。** 语义预测在低 SNR / 竞争说话人下**可能预测错音素**，而错误的语义特征可能诱导掩蔽估计器**抑制真实辅音**（false suppression）。论文**完全没有**低 SNR 分层、babble、false-suppression、ASR WER、F0/prosody 任何一项证据，也没有失败案例分析。这是"用生成式先验做判别式任务"的固有风险，且与 Table IV 的增益结论**同等重要**。
> **(5) 统计证据不足。** 关键差值（+0.05 / +0.03 / +0.02）无方差、无重复运行、无显著性检验；codebook size 1024 与 $N=5$ 都**从未消融**（$N$ 只在一张表上扫过，codebook size 一个实验都没做）。
