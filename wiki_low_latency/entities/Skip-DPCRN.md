---
title: Skip-DPCRN
type: entity
created: 2026-09-22
updated: 2026-09-22
tags:
  - model
  - speech-enhancement
  - single-channel
  - streaming
  - dpcrn
  - dual-path-rnn
  - skip-rnn
  - inference-skipping
  - state-skipping
  - update-rate
  - vad-guided
  - model-compression
  - input-dependent-compute
  - paper-claimed-causal
  - 48ms-total-latency
sources:
  - [[wiki_low_latency/sources/2022/Skip-DPCRN 2022]]
related:
  - [[wiki_low_latency/entities/DPCRN]]
  - [[wiki_low_latency/concepts/2207.11108-inference-skipping-parallel-rnn]]
  - [[wiki_low_latency/concepts/2107.05429-dual-path-recurrent-context]]
  - [[wiki_low_latency/sources/2021/DPCRN Low-Latency Direction 2021]]
  - [[wiki_low_latency/concepts/严格因果与算法延迟]]
  - [[wiki_low_latency/concepts/低时延前端与延迟账本]]
  - [[wiki_low_latency/entities/CRUSE-Latency-Study]]
  - [[wiki_low_latency/entities/RT-Tango]]
---

# Skip-DPCRN

## 定义

**Skip-DPCRN** 是本地论文 2207.11108（Le, Lei, Chen, Lu，arXiv 2022 / IEEE-ACM TASLP 2022）提出的单通道时频域语音增强模型。它**不改变 DPCRN 的架构拓扑**，而是在其 **parallel RNN** 骨架上引入 **Skip-RNN** 的二值门控状态更新：RNN 的状态间歇更新，但输出掩蔽仍由其余并行通路持续更新，因此**在显著降低推理算力时没有出现引文 [20]（TinyLSTM）报告的音频伪影**。

它同时是「**推理期算力压缩**」这一子方向的代表作：算力节省发生在推理期、**无需重训练**（$\gamma$ 缩放式），并且**与剪枝/量化/蒸馏正交**（论文明确把卷积层的量化留给别人做）。参数量几乎不变：DPCRN-base 0.5286 M → All-skip 0.5291 M，只多一个门控 FC。

论文口径：16 kHz、32 ms 窗 / 16 ms hop、**"total latency of 48 ms"**（= 窗长 + hop，未拆分算法/计算/端到端）。这是本 Wiki 约 2 ms 目标的 **24 倍**，不是合格系统。

> [!note] 命名
> 论文标题里没有 "Skip-DPCRN" 这个词；这个名字来自作者的代码仓库 `SKIP-DPCRN`，也是社区里最常用的称呼。论文正文使用的变体名是 **DPCRN-Intra-skip / DPCRN-Inter-skip / DPCRN-All-skip**。

## 证据

| 属性 | 本地 PDF 证据 |
|---|---|
| 任务 | 单通道 streaming speech enhancement；WSJ0 SI-84（14633 条 ≈25 h、120 说话人）+ DNS-3 噪声（60000 条、150 h），p.4–5 §III.A |
| 输入 | 三通道 $\mathbf X\in\mathbb R^{T\times F\times C}$，$C=3$：带噪谱实部 $X_r$、虚部 $X_i$、对数功率谱 $X_p$；STFT 512、$F=257$、sine window，p.2 §II.B.1、p.5 §III.B |
| 输出 | 三通道掩蔽：幅度掩蔽 $M$ + 相位掩蔽 $\Phi$ 的实部/虚部；$\widetilde S=X\odot M\odot\Phi$，Eq. (3)，p.2 |
| 骨干 | encoder（5 层 Conv2D，strides $\{(2,1),(2,1),(2,1),(1,1),(1,1)\}$）→ **2 × Skip-DPRNN** → 转置卷积 decoder + encoder-decoder skip connections；通道 3→32→32→32→64→128 对称回 3，Fig. 1/Fig. 4，p.2–4 |
| 相对原版 DPCRN 的三处改动 | ① LSTM → **GRU**（省 1/4 算力）；② 卷积核 $(2,5)/(2,3)$ → $(1,5)/(1,3)$；③ 最后两层 stride 保持 $(1,1)$ 以保住频率分辨率；$C_{hid}=128$，p.3 §II.B.1 |
| DPRNN 模块 | intra-frame RNN（沿频率轴、**双向** Bi-RNN，每向 $C_{hid}/2$）+ FC + iLN + 残差（Eq. 4–6）；inter-frame RNN（沿时间轴、**单向**、在 $F_{in}$ 个子带上**并行**）+ FC + iLN + 残差（Eq. 7–9），p.2–3 |
| Skip-RNN 门控 | $g_t=\mathrm{round}(\tilde p_t)$，$s_t=g_t\tilde s_t+(1-g_t)s_{t-1}$，$\Delta\tilde p_t=\sigma(W_ps_{t-1}+b_p)$，$\tilde p_{t+1}=g_t\Delta\tilde p_t+(1-g_t)(\tilde p_t+\min(\Delta\tilde p_t,1-\tilde p_t))$，Eq. (11)–(14)，p.3 |
| 更新率旋钮 | $\Delta\tilde p_t=\gamma\,\sigma(W_ps_{t-1}+b_p)$，**推理期可直接实施、无需重训练**，Eq. (20)，p.4 |
| VAD 分支 | encoder 特征 → 1×1 Conv（压到 1 通道）→ GRU（隐维 32）→ FC → Sigmoid；BCE 优化；标签由干净语音能量阈值生成，p.4 §II.B.2、Fig. 4 |
| VAD 平滑 | 连续 10 帧估计值全为 0 才判 0，否则判 1；**以牺牲准确率换召回率**，Eq. (27)，p.6 |
| 损失 | $L=L_{SD}+\alpha L_{Skip}$，Eq. (26)；$L_{SD}=\lambda\,\mathrm{MSE}(S^c,\hat S^c)+(1-\lambda)\,\mathrm{MSE}(|S|^c,|\hat S|^c)$，$c=0.3$、$\lambda=0.1$，Eq. (21)(22)；$L_{Skip}$ 三形式 Eq. (23)/(24)/(25)，p.4–5 |
| 参数量 | DPCRN-base 0.5286 M；Intra-skip 0.5288 M；Inter-skip 0.5288 M；**All-skip 0.5291 M**，Table III，p.6 |
| 算力 | DPCRN-base **1115 M MACs/s**；All-skip $\alpha=1\times10^{-4}$ 降到 **749.8 M**；Intra-skip $\alpha=3\times10^{-4}$ 为 849.7 M；Inter-skip $\alpha=3\times10^{-4}$ 为 814.0 M，Table III，p.6 |
| 最优配置（质量） | NOISEX：base SDR 9.527 / PESQ 2.688 / STOI 89.13%；MUSAN：base 11.54 / 3.105 / 93.69%，Table II，p.6 |
| 训练 | Adam，batch 16，lr 1e-3（10 epoch 不降减半、20 epoch 不降早停）；TensorFlow；Nvidia TITAN Xp，p.6 §III.B |
| 泛化宿主 | CRUSE（8.58 M，8 层卷积 + 4 并行 GRU 子组，UR 0.496/0.491）与 GCRN（7.66 M，LSTM→GRU，UR 0.697/0.642），均 20 ms 帧 / 10 ms hop，Table IV，p.9 |

## 架构与状态

~~~text
noisy waveform
  → STFT (16 kHz, win 32 ms / hop 16 ms, FFT 512, sine window, F=257)
  → X ∈ R^{T×F×3}   (Xr, Xi, Xp)
  → BatchNorm
  → Encoder : 5 × Conv2D, strides {(2,1),(2,1),(2,1),(1,1),(1,1)}
              ch 3→32→32→32→64→128      [stride 只压频率轴]
      ├──────────────────────────────┐
      │                              ▼
      │                    1×1 Conv (ch→1) → GRU(32) → FC → Sigmoid
      │                              = VAD 分支（多任务，BCE）
      ▼
  → 2 × Skip-DPRNN module
      intra-frame RNN block : 沿频率轴切片 → Bi-RNN(C_hid/2) → FC → iLN → +residual
                              └─ 可替换为 Skip-intra-RNN（Eq. 15）
      inter-frame RNN block : 沿时间轴切片（F_in 个子带并行）→ 单向 RNN(C_hid)
                              → FC → iLN → +residual
                              └─ 可替换为 Skip-inter-RNN（Eq. 16）
      ★ 关键：RNN 状态可跳步，但 mask 由其他并行通路继续更新
  → Decoder : 转置卷积（对称结构）+ encoder-decoder skip connections
              ch 128→64→32→32→32→3
  → 3 通道输出 : [ M , Re(Φ) , Im(Φ) ]
  → S̃ = X ⊙ M ⊙ Φ   (Eq. 3)
  → iSTFT + overlap-add
  → enhanced waveform

Skip 控制三条路径
  ├─ L_Skip 正则 : Eq.23 压门均值 / Eq.24 拉向目标率 μ / Eq.25 MAE 版
  ├─ γ 缩放     : Δp̃ = γ·σ(W_p s_{t-1}+b_p)，推理期直接调，免重训练（Eq. 20）
  └─ VAD 引导   : 纯噪帧 γ=0.4、语音帧 γ=1（按估计 VAD 判决，Eq. 27 平滑）
~~~

## 低时延账本

| 字段 | Skip-DPCRN 证据/边界 |
|---|---|
| 采样率 | 16 kHz（p.3 §II.B.1） |
| 窗 / hop / FFT | $W=32$ ms（512 samples）/ $h=16$ ms（256 samples，50% overlap）/ FFT 512，频率维 $F=257$（自洽），sine window + OLA，p.5 §III.B |
| 帧率 | 62.5 帧/s（由 hop 换算；论文未直接给出） |
| 论文延迟口径 | 「resulting in a **total latency of 48 ms**」（p.5 §III.B）——**只有这一句，无公式、无拆分**。48 = 32（窗）+ 16（hop） |
| 逐层因果性 · intra-frame RNN | 双向 Bi-RNN，但双向性**只发生在单帧内部的频率轴上**，不跨帧读未来观测 → 时间维 `strict_causal` |
| 逐层因果性 · inter-frame RNN | **单向**，在 $F_{in}$ 个子带上并行，「to guarantee the causality of the whole model」（p.3）→ `strict_causal`（论文级声明，**全文唯一的因果性论据**） |
| 逐层因果性 · 卷积 | kernel $(1,5)/(1,3)$、strides $\{(2,1),\dots\}$，**padding 完全未报告**。若 stride 元组第一项对应频率轴（唯一自洽读法），则时间轴核长为 5/3，卷积跨帧，padding 方式直接决定是否读未来帧 → **`unreported`，无法证明卷积层严格因果** |
| 逐层因果性 · STFT | center / padding 设置**未报告**。按 "48 ms = 窗 + hop" 的口径推定前端需要约一个窗的未来样本 → `low_look_ahead`（**推定，非论文声明**） |
| 归一化 | 输入 BatchNorm [28] + 块内 iLN [29]（按帧统计、不跨时间）；BN 的 running statistics 是否冻结**未讨论** |
| 状态 | RNN hidden state、门概率 $\tilde p_t$、二值门 $g_t$、VAD GRU 隐状态（32）；**warm-up、state reset、长流漂移、丢帧/抖动策略全部未报告** |
| 算力 | 1115 M MACs/s（base）→ 749.8 M（All-skip $\alpha=1\times10^{-4}$）；**全部为测试集平均值**，Fig. 6 只给帧级分布与"峰值降约 15%"的说法，**无 worst-case / p99 算力** |
| 运行时与 deadline | RTF、目标硬件、p50/p95/p99、per-frame wall-clock、deadline miss **全部未报告**。**算力下降 ≠ 延迟下降**：条件跳步会引入分支与数据依赖停顿，论文未做任何 wall-clock 验证 |
| 部署资源 | 目标 SoC、峰值 RAM/SRAM、量化/定点、功耗、编译器/算子差异**全部未报告** |
| 端到端 | 只到 "total latency of 48 ms"；ADC/DMA、I/O buffer、DAC/playout、underrun/overrun、capture-to-playback **未验证** |

实体判定：**`paper-claimed-causal`（只有一句 inter-frame 单向的结构声明，卷积 padding / STFT center / 归一化统计 / 状态生命周期四项均无证据）/ 48 ms 未拆分的 total latency（= 窗 + hop，论文口径）/ 输入相关的平均 MACs，无峰值与 deadline 证据**。

> [!warning] 「平均省 33%、峰值只省 15%」
> 这是本篇最容易被误读的数字。论文报告的 1115 → 749.8 M 是**测试集平均**；唯一关于尾部的信息是 Fig. 6 的「the peek [sic] computational load is reduced by about **15%**」。
> 对需要按最坏情况预留预算的实时系统，Skip-RNN 省下的是**平均功耗/发热**，而不是**最坏情况 deadline 余量**。论文没有讨论这个区分，也没有给出任何分位数。

> [!warning] 「28%」是分段条件数
> 论文写的是「the computational load of the DPRNN modules **at pure noise segments** is only **28%** of the baseline」（$\gamma=0.5$，长音频测试集）。因为语音帧的更新率被刻意保持在基线水平，**整段平均的节省必然远小于 72%**。论文没有给出语音/噪声时间占比，也没有给出整段平均节省量。

## 结果与证据边界

- **支持**：在同一架构与几乎相同的参数量下，更新率可被 $\alpha$ 单调控制（Intra-skip：intra 更新率 0.696→0.265，MACs 1005→849.7 M）；All-skip $\alpha=1\times10^{-4}$ 把 MACs 从 1115 降到 749.8 M（−32.8%）而 NOISEX SDR 只从 9.527 掉到 9.337；在**同算力**下（Fig. 5）多数点上优于"直接训小模型"与"结构化剪枝"；同一策略在 CRUSE（8.58 M）与 GCRN（7.66 M）上也能在显著更低更新率下保持性能；$\gamma$ 可在推理期直接调节、无需重训练；VAD 引导下纯噪段的 DPRNN 算力可降到基线 28%。
- **不支持**：约 2 ms 级系统已达成（48 ms 是 24 倍）；最坏情况算力已显著下降（峰值仅降约 15%）；wall-clock 延迟/功耗已下降（完全未测）；目标端侧 deadline 已通过；端到端 capture-to-playback 已测；低 SNR 人声保留已证明；卷积层严格因果；"任何 parallel RNN 模型都能融合"以外更广的普适性。
- **未报告**：RTF、目标硬件、p50/p95/p99、峰值 RAM/SRAM、量化/定点、功耗、batch=1 长流稳定性、state reset、warm-up、underrun/overrun、per-SNR 分层（−5/0/5 dB 被合并）、DNSMOS SIG/BAK/OVL、false-suppression、VAD recall/precision、voiced energy 保留、F0/formant/prosody continuity、ASR WER、训练总步数/种子数、$L_{Skip}$ 的 $\mu$ 具体取值、VAD 分支损失的加权方式。
- **可比性提醒**：① 本文的 baseline 是作者重新调过的 DPCRN（**0.5286 M / 1115 M MACs**），不是 DNS-3 榜上那个 DPCRN（论文自述 **0.8 M / 3.7 G MACs**，本库 [[wiki_low_latency/entities/DPCRN]] 记的也是 0.8 M），引用时须写清是哪一版。② 本文的 MACs 是**输入相关**的平均值，且随测试集噪声难度变化（MUSAN 上更新率低于 NOISEX），不能与固定 MACs 的模型直接横比。③ 48 ms 是"窗 + hop"口径，与按 $(W-h)/f_s$ 或 $W/2$ 记账的论文不同尺子。

## 交叉链接

- 源论文：[[wiki_low_latency/sources/2022/Skip-DPCRN 2022]]
- 概念展开：[[wiki_low_latency/concepts/2207.11108-inference-skipping-parallel-rnn]]
- 宿主模型：[[wiki_low_latency/sources/2021/DPCRN Low-Latency Direction 2021]]、[[wiki_low_latency/entities/DPCRN]]、[[wiki_low_latency/concepts/2107.05429-dual-path-recurrent-context]]
- 直接竞品（同问题谱系的反面）：[[wiki_low_latency/sources/2024/D-GRU 2024]]（⚠️ 并行摄取中）
- 同思路的另一实现：[[wiki_low_latency/sources/2026/RT-Tango 2026]]、[[wiki_low_latency/entities/RT-Tango]]
- 泛化宿主所在的统一审计研究：[[wiki_low_latency/entities/CRUSE-Latency-Study]]、[[wiki_low_latency/sources/2024/Ultra-Low Latency Speech Enhancement Comprehensive Study 2024]]
- 最严因果口径对照：[[wiki_low_latency/sources/2026/LaCo-SENet 2026]]、[[wiki_low_latency/entities/LaCo-SENet]]
- 延迟审计口径：[[wiki_low_latency/concepts/严格因果与算法延迟]]、[[wiki_low_latency/concepts/低时延前端与延迟账本]]
- 损失与数据增强来源：[[wiki_low_latency/sources/2021/Noise Suppression Losses 2021]]
- 人声保留缺口：[[wiki_low_latency/concepts/低 SNR 人声保留评估]]

> [!question] 待验证
> ① 卷积层的 padding 方式（决定是否读未来帧）在本地 PDF 中完全缺失，需要回查作者代码 `SKIP-DPCRN` 才能把判定从 `paper-claimed-causal` 升级。
> ② Table III 中 Inter-skip 的前两行 MACs（1011、994.4）与本页按 Table I + 更新率复算的值（994.4、920.1）不一致，疑似错位一行，需回查代码或原始表。
> ③ Table II 的 Update rate 与 Table III 的 intra/inter 分项更新率无法互相复算，聚合口径未说明。
> ④ 论文把 $c=0.3$、$\lambda=0.1$ 都归因于引文 [21]，但本库 [[wiki_low_latency/sources/2021/Noise Suppression Losses 2021]] 记录该文自选 $\lambda=0.3$，疑为引用笔误。
> ⑤ frontmatter/本页采用的 venue「IEEE/ACM TASLP, vol. 30, pp. 2411-2421, 2022」来自外部元数据；本地 PDF 的页眉与 DOI 均为 LaTeX 模板占位符，无法自证。
