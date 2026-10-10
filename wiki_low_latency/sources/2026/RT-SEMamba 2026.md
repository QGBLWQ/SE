---
title: RT-SEMamba - 渐进式知识蒸馏与因果时频 Mamba 语音增强
type: source
created: 2026-09-16
updated: 2026-09-20
tags:
  - speech-enhancement
  - single-channel
  - mamba
  - ssm
  - streaming
  - knowledge-distillation
  - paper-claimed-causal
  - 25ms-algorithmic-latency
source_type: paper
year: 2026
authors: Rong Chao; Sung-Feng Huang; Moreno La Quatra; Sabato Marco Siniscalchi; Wen-Huang Cheng; Szu-Wei Fu; Yu Tsao
venue: arXiv preprint
arxiv: https://arxiv.org/abs/2608.12099
local_pdf: raw/papers/low_latency_causal_se/2608.12099.pdf
evidence_policy: local_pdf_only
related:
  - [[wiki_low_latency/entities/RT-SEMamba]]
  - [[wiki_low_latency/concepts/2608.12099-mamba-distillation]]
  - [[wiki_low_latency/concepts/2409.10358-ultra-low-latency-benchmark]]
  - [[wiki/sources/2024/Mamba for SE 2024]]
---

~~~yaml
- 论文: [RT-SEMamba: Real-Time Speech Enhancement Mamba via Progressive Knowledge Distillation](2026)
  ├── 要解决什么问题: 将时频 Mamba 改造成有固定状态、无未来帧的流式增强器，并压缩深层模型的质量损失
  ├── 核心方法: causal time-frequency Mamba + 8-layer teacher → 1/2-layer student 的 progressive KD，同时蒸馏 magnitude/phase/complex 输出和中间表征
  ├── 属于哪个分支: 单通道复数时频增强 / SSM-Mamba / streaming / knowledge distillation
  ├── 输入/输出: noisy waveform → causal STFT magnitude/phase → cTF-Mamba → magnitude/phase/complex spectrum → causal iSTFT
  ├── 关键trick: 固定 recurrent SSM state 避免 KV cache 增长；先训练 teacher，再把蒸馏权重逐步 ramp-up 到浅层 student
  ├── 数据集: VCTK-DEMAND；训练 SNR 0/5/10/15 dB，测试 2.5/7.5/12.5/17.5 dB
  ├── 对比了谁: 1/2/8-layer RT-SEMamba、naive student 与 8-layer teacher；表中还列出既有 SEMamba/实时系统
  ├── 性能上限: 8-layer teacher PESQ=3.32；8→1 KD student PESQ=3.18、RTF=0.11；论文 algorithmic latency=25 ms
  ├── 参数量: 1-layer 1.05M、2-layer 1.29M、8-layer 2.74M；MAC/s 20.56/24.39/47.35
  ├── 消融关键发现: 8→1 KD 将 naive 1-layer PESQ 3.06 提升到 3.18，表内 steady-state RTF 不变；2-layer KD 也优于 naive 2-layer
  ├── 遗留问题(你的机会): 25 ms 前端不满足约 2 ms；缺少目标 SoC p99、RAM/量化、低 SNR 人声保留和真实端到端验证
  └── 跟哪篇像: [[wiki_low_latency/concepts/2409.10358-ultra-low-latency-benchmark]]、[[wiki_low_latency/sources/2024/SlowFast-SSM 2024]]、[[wiki_low_latency/sources/2023/FSB-LSTM 2023]]
~~~

# RT-SEMamba: Real-Time Speech Enhancement Mamba via Progressive Knowledge Distillation

> Rong Chao 等，arXiv:2608.12099v1，12 Aug 2026。论文的 real-time 在本页拆成因果性、RTF 与前端 algorithmic latency 三个独立证据。

> [!warning] PDF 转换质量与阅读说明
> 原 PDF 共 5 页。Poppler 页面清晰，但文本抽取中的选择性状态符号、指数 $e^{jP}$、上下标和表格列会发生错位；Figure 1 与 Tables 1-3 以原 PDF 第 2-4 页视觉核对。对未在页面明确给出的训练、缓存和硬件信息不作补写。

> [!updated] 2026-09-20 追加：因果性判定口径被更严标准挑战
> 新增摄取 [[wiki_low_latency/sources/2026/LaCo-SENet 2026]]（arXiv:2606.19688）后，本页的因果性结论需要补一个前置条件。详见下方「因果性判定口径」小节，本页原有的 25 ms 与 `paper-claimed-causal` 判定**未被推翻，但降级为需要额外验证**。

## 因果性判定口径（2026-09-20 追加）

本页原判定为「paper-level strict temporal causal / 25 ms algorithmic latency」，依据是论文自述 center=False、时间卷积只做左侧 $K-1$ padding、Time-Mamba 无 lookahead。

LaCo-SENet（arXiv:2606.19688）Table 1 脚注 † 提出了一个**更严的判定标准**：

> "Labeled unidirectional, but encoder convolutions use non-causal symmetric padding; algorithmic latency not deterministically computable."

它据此把 **SEMamba 与 xLSTM-SENet 排除出因果排名**——尽管这两者都自称 unidirectional。而 RT-SEMamba 正是 SEMamba 的因果化改造版本。

> [!contradiction] 两条记录必须一起读
> - RT-SEMamba 的自证是「论文级声明 + 部分结构证据」（center=False、时间卷积右侧不 padding、Time-Mamba 单向）。
> - LaCo-SENet 的口径是「**只要 encoder 存在非因果对称 padding，算法延迟就不可确定，即便模型自称 unidirectional**」。
> - 两者的分歧点在于：**RT-SEMamba 未给出逐层的 padding/state certificate**（本页「低时延账本」中已注明），因此无法从现有材料证明其 encoder 全部为因果 padding。25 ms 的算法延迟依赖「one-window bounded」这一论文口径，未被独立复算。
> - **处置**：本库从此采用 LaCo-SENet 的更严口径——「自称单向」与「逐层可核验的因果」分开记账。RT-SEMamba 保持 `paper-claimed-causal`，但其 25 ms **不得**与其他给出逐层 padding 式的模型（如 LaCo-SENet）放在同一可信度层级上比较。
> - 待办：若取得 RT-SEMamba 代码，应逐层审计 padding 与 state，再决定是否能升级为 `strict_causal`。

## 1. 他们为什么这么做？（motivation）

### 1.1 任务与对象

RT-SEMamba 研究单通道实时语音增强：从 noisy waveform $x(t)$ 得到增强波形 $\hat x(t)$，用于助听器、AR/VR、实时会议等受延迟、计算和内存约束的场景。输入 noisy waveform 经过 causal STFT：

$$
X(f,\tau)=\operatorname{STFT}(x(t))
=M(f,\tau)e^{jP(f,\tau)},
$$

其中 $M$ 是 magnitude，$P$ 是 phase，$\tau$ 是帧索引。网络预测 $\hat M,\hat P,\hat C$，其中：

$$
\hat C=\hat M e^{j\hat P},
$$

再经 causal inverse STFT 得到 $\hat x(t)$。

### 1.2 论文动机

Transformer/Conformer 的 KV cache 随长流增长；非因果 Mamba/SEMamba 又可能使用未来时间帧。论文因此把 time-frequency Mamba 改成显式单向时间状态，并用 8-layer teacher 指导 1/2-layer student，试图同时压低计算和长期内存带宽。

## 2. 之前的人怎么做不了？（limitation → gap）

| 路线 | 能力 | 仍然卡在哪里 |
|---|---|---|
| Transformer/Conformer SE | 全局上下文强 | KV cache、未来上下文或内存带宽不适合长流低延迟 |
| 非因果 SEMamba | 时频状态空间建模有效 | offline/non-causal 组件不能直接作为 streaming 系统 |
| 浅层 causal Mamba | 固定状态、计算小 | 深度不足造成质量损失 |
| 8-layer causal model | 质量较高 | 参数、MAC/s 和 RTF 更大 |
| 普通 KD | 可将 teacher 行为传给 student | 只蒸馏单一输出时，复数谱与中间时频结构利用不足 |

论文的 gap 是：能否让 Mamba 以固定递归状态运行，并把深层 teacher 的复数时频表征压缩到浅层 causal student，同时保持相同前端延迟口径。

### 2.1 严格因果与延迟账本

| 审计项 | PDF 证据 | 本 Wiki 判定 |
|---|---|---|
| STFT window | 400 samples at 16 kHz | 25 ms algorithmic latency，超过约 2 ms 目标 23 ms |
| hop | 100 samples | 6.25 ms frame shift，不等于完整算法延迟 |
| time path | Time-Mamba 单向，temporal convolution 使用左侧 causal padding | paper_claimed_causal；但缺少样本级 padding/state certificate |
| frequency path | 在已形成的当前帧内做 Frequency-Mamba | 不等于跨时间 look-ahead |
| state | temporal feature buffer、depthwise-conv buffer、SSM hidden state | 支持流式设计；warm-up、reset、长流稳定性未报告 |
| compute | RTX 5090 warm-up 后 RTF 0.11-0.29 | GPU steady-state 证据，不是目标 SoC p99/deadline |
| end-to-end | ADC/DMA、I/O、DAC、underrun/overrun、capture-to-playback 未报告 | 未验证 |

因此 RT-SEMamba 可以标为“论文级 causal、25 ms algorithmic latency”，不能标为本方向约 2 ms 已验证系统。

## 3. 这个做法核心 trick 是什么？

### 3.1 因果时频 Mamba 管线

~~~text
noisy waveform
  → causal STFT, center=False
  → magnitude/phase compression + concatenate + permute
  → cTF-Mamba × N
      ├─ Time-Mamba：沿时间单向递归
      └─ Frequency-Mamba：在当前帧频率轴建模
  → causal magnitude/phase decoders
  → complex spectrum
  → causal iSTFT
  → enhanced waveform
~~~

![[wiki_low_latency/assets/2608.12099/2608.12099-page2-architecture.png]]

> 图注：原论文第 2 页 Figure 1 的页面渲染；用于核对 causal STFT、Time/Frequency-Mamba、双 decoder 和 iSTFT 的结构。图片为 PDF 页面复制，不是 AI 重画。

### 3.2 Trick A：固定状态而不是增长的 KV cache

论文用简化 SSM 说明：

$$
h_n=\bar A h_{n-1}+\bar Bx_n,\qquad y_n=Ch_n.
$$

$h_n$ 是当前时间步的固定维状态，$\bar A,\bar B$ 是离散状态转移矩阵，$C$ 是输出投影。对长序列而言，状态大小不随 $n$ 线性增长；但这只是模型状态复杂度解释，不替代实际 SRAM、功耗和 deadline 测量。

### 3.3 Trick B：输出级 + 中间表征的 progressive KD

设 8-layer teacher $T$ 和 1/2-layer student $S$ 分别输出：

$$
(\hat M_t,\hat P_t,\hat C_t)=T(M,P),\qquad
(\hat M_s,\hat P_s,\hat C_s)=S(M,P).
$$

输出蒸馏为：

$$
\mathcal L_{\mathrm{KD}}^{out}
=w_{mag}\lVert\hat M_s-\hat M_t\rVert_2^2
+w_{pha}\lVert\hat P_s-\hat P_t\rVert_2^2
+w_{com}\lVert\hat C_s-\hat C_t\rVert_2^2,
$$

论文设置 $w_{mag}=1.0,\ w_{pha}=0.3,\ w_{com}=0.5$。把 8 个 teacher block 的中间输出平均：

$$
H_{agg}^{t}=\frac{1}{8}\sum_{i=1}^{8}H_i^t,
$$

并对 student 与 teacher aggregate 做样本归一化后的 L2 feature loss。蒸馏权重逐步 ramp-up：

$$
\gamma(k)=\min\left(\frac{k}{K_{ramp}},1\right),
$$

其中 $K_{ramp}$ 是总训练步的 10%；总损失将输出蒸馏和特征蒸馏以 $\lambda_{out}=0.5,\lambda_{feat}=0.1$ 加入 task loss。论文未在本文完整展开所有 task loss 项，因此不补写未给出的公式。

## 4. 实验里哪个消融最关键？

### 4.1 数据与评价

论文使用 VCTK-DEMAND：训练噪声条件为 0/5/10/15 dB，测试条件为 2.5/7.5/12.5/17.5 dB。主要报告 PESQ、CSIG、CBAK、COVL、STOI、参数量、MACs/s 和 steady-state RTF。测试集没有本 Wiki 所需的负 SNR 分层或人声保留专门指标。

### 4.2 结构与结果

![[wiki_low_latency/assets/2608.12099/2608.12099-page4-results.png]]

> 图注：原论文第 4 页结果/比较表渲染；用于核对模型深度、KD 对照、PESQ 与语音质量指标。

| Model | Params (M) | MACs (G/s) | RTF | PESQ | CSIG | CBAK | COVL | STOI |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| naive 1-layer | 1.05 | 20.56 | 0.11 | 3.06 | 4.38 | 3.61 | 3.79 | 0.94 |
| 8→1 distilled | 1.05 | 20.56 | 0.11 | 3.18 | 4.43 | 3.68 | 3.89 | 0.95 |
| naive 2-layer | 1.29 | 24.39 | 0.13 | 3.19 | 4.51 | 3.66 | 3.93 | 0.95 |
| 8→2 distilled | 1.29 | 24.39 | 0.13 | 3.22 | 4.55 | 3.69 | 3.97 | 0.95 |
| 8-layer teacher | 2.74 | 47.35 | 0.29 | 3.32 | 4.64 | 3.72 | 4.08 | 0.95 |

8→1 KD 将 naive 1-layer 的 PESQ 从 3.06 提高到 3.18，表内 RTF 保持 0.11；8→2 也略优于 naive 2-layer。这支持“progressive KD 恢复浅层模型的一部分深度能力”，不支持“student 与 teacher 等价”。

### 4.3 最关键的消融判断

最有信息量的对照是同层数的 naive student 与 distilled student：它隔离了蒸馏监督，而不是把“更多层”误当作 KD 收益。输出级 magnitude/phase/complex 联合目标和中间多层聚合共同构成方法；论文没有独立证明每一个蒸馏分量都是必要的，因此后续应补做 loss component ablation。

## 5. 这个方向还剩什么问题没解决？（future work / limitation）

- 25 ms window 距离约 2 ms 目标仍有 23 ms；固定 SSM state 解决的是长流 memory/cache，不是前端算法延迟。
- RTX 5090 RTF 是 steady-state GPU 证据；没有目标 SoC 的 p99、峰值 RAM/SRAM、功耗、量化、deadline miss 或 buffer underrun。
- 论文未报告状态 reset、warm-up、丢帧/抖动、长流稳定性和样本级输出锚点。
- VCTK-DEMAND 训练/测试 SNR 非负，没有竞争说话人、瞬态噪声、-10/-5 dB 人声 retention、false-suppression、F0/formant/prosody continuity 或 ASR WER。
- Table 3 中既有系统的训练语料、窗长和测时口径不同，不能直接当作同条件排行榜。

对当前方向的可迁移启示是：可以借用 progressive KD 做小模型质量恢复，但必须配合短窗/非对称前端、低 SNR 人声保留指标和真实端侧 p99；不能只报告 RTF。

## 6. 本论文在库中的位置关联（cross-reference matrix）

| 关系 | 库中论文/概念 | 关联与差异 |
|---|---|---|
| 统一延迟基准 | [[wiki_low_latency/sources/2024/Ultra-Low Latency Speech Enhancement Comprehensive Study 2024]] | 该研究把窗长、look-ahead、计算和质量分开；RT-SEMamba 的 25 ms 可放入同一 ledger |
| 同类 SSM | [[wiki_low_latency/sources/2024/SlowFast-SSM 2024]] | SlowFast-SSM 关注低 MAC 的状态空间调制；RT-SEMamba 关注 causal 化和深度蒸馏 |
| 历史参照 | [[wiki/sources/2024/Mamba for SE 2024]] | 旧 Wiki 的 Mamba-for-SE 探索；RT-SEMamba 明确增加流式状态和 KD |
| 复数时频参照 | [[wiki_low_latency/sources/2020/DCCRN Low-Latency Direction 2020]] | DCCRN 用 complex CNN/RNN 建模 phase；RT-SEMamba 同样输出 complex spectrum，但主干是 Mamba |
| 人声保留缺口 | [[wiki_low_latency/concepts/2111.11606-speech-distortion-losses]] | RT-SEMamba 仍缺 speech distortion/ASR/WER 分析，可沿用损失-失真审计 |
| 概念页 | [[wiki_low_latency/concepts/2608.12099-mamba-distillation]] | 展开 fixed-state、输出/特征 KD 与 ramp-up 公式 |
| 因果口径冲突（2026-09-20 追加） | [[wiki_low_latency/sources/2026/LaCo-SENet 2026]] | LaCo-SENet 把 SEMamba 判为「算法延迟不可确定」并排除排名，而本篇是 SEMamba 的因果化改造 → 见页首「因果性判定口径」 |
| 同路线对照（2026-09-20 追加） | [[wiki_low_latency/sources/2026/PSMSE 2026]] | 同走 Mamba 流式，但 PSMSE **不缓存跨帧状态**（0.26 M / 0.11 G·s）；本篇**缓存固定 SSM state 跨帧传播**（1.05 M / 20.56 G·s）。两条「Mamba 流式」语义的正面对照 |

## 7. 一句话总结“江湖地位”

> **RT-SEMamba 是“因果 Mamba + progressive KD”在 25 ms 前端上的有价值参照，证明浅层 student 可以追回一部分质量，但距离约 2 ms、目标端侧 p99 和人声保留仍有明确缺口。**

## 参考资料

- [arXiv:2608.12099](https://arxiv.org/abs/2608.12099)
- 本地原件：raw/papers/low_latency_causal_se/2608.12099.pdf
