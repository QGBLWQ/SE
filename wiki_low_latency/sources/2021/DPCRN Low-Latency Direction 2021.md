---
title: "DPCRN: Dual-Path Convolution Recurrent Network for Single Channel Speech Enhancement"
type: source
created: 2026-09-16
updated: 2026-09-16
tags:
  - speech-enhancement
  - complex-spectrum
  - DPRNN
  - CRN
  - strict-causal
  - low-latency
  - speech-preservation
evidence_policy: local_pdf_only
source_type: paper
year: 2021
authors: Xiaohuai Le, Hongsheng Chen, Kai Chen, Jing Lu
venue: arXiv preprint; Interspeech 2021 DNS Challenge
arxiv: https://arxiv.org/abs/2107.05429
local_pdf: raw/papers/low_latency_causal_se/2107.05429.pdf
related:
  - [[wiki_low_latency/entities/DPCRN]]
  - [[wiki_low_latency/concepts/2107.05429-dual-path-recurrent-context]]
  - [[wiki_low_latency/index]]
  - [[wiki_low_latency/overview]]
  - [[wiki_low_latency/sources/2020/DCCRN Low-Latency Direction 2020]]
  - [[wiki_low_latency/sources/2021/On TasNet Low-Latency SE 2021]]
  - [[wiki/sources/2020/DCCRN 2020]]
---

~~~yaml
- 论文: [DPCRN: Dual-Path Convolution Recurrent Network for Single Channel Speech Enhancement](2021)
  ├── 要解决什么问题: 低 SNR/混响下需要长时间和频率上下文，但普通 CRN 的单一 RNN 路径难以兼顾谱结构、长时依赖和实时约束
  ├── 核心方法: 复数 STFT CRM + 卷积编码器/解码器 + 频率 intra-chunk BiLSTM + 时间 inter-chunk causal LSTM
  ├── 属于哪个分支: 复数谱增强 / DPRNN / 单通道 / DNS 实时轨道
  ├── 输入/输出: noisy complex STFT 的实部与虚部 → complex ratio mask → enhanced complex STFT → iSTFT waveform
  ├── 关键trick: 把 STFT 频率轴当作 DPRNN chunk，BiLSTM 只沿频率建模；跨时间帧用 causal LSTM，整体保持时间因果
  ├── 数据集: Interspeech 2021 DNS challenge，约 60k、500 h；55k train/5k validation；SNR -5 到 5 dB
  ├── 对比了谁: Noisy、DTLN、DCCRN、DPCRN-1/2/3、NSNet2，以及 DNS blind test 的 P.835
  ├── 性能上限: DPCRN-2 在 WSJ0-NOISEX92 平均 PESQ/STOI/SDR=2.46/86.38%/9.16；DNS blind test Speech/Background/Overall MOS=3.76/4.34/3.57
  ├── 参数量: 约 0.8M；约 7.45 GFLOPS；TensorFlow 在四核 i5-6300HQ 上单帧处理 8.9 ms
  ├── 消融关键发现: 在约相同复杂度下，加入频率 MSE 的 DPCRN-2 提高 PESQ/STOI；DPCRN-3 降低频率分辨率但加宽 RNN，质量反而变差
  ├── 遗留问题(你的机会): 25 ms window + 12.5 ms hop 的总算法延迟为 37.5 ms，不满足本 Wiki 约 2 ms 边界；没有 p99 deadline、false-suppression、ASR WER 或弱语音保留评估
  └── 跟哪篇像: [[wiki_low_latency/sources/2020/DCCRN Low-Latency Direction 2020]]、[[wiki_low_latency/sources/2021/On TasNet Low-Latency SE 2021]]、[[wiki_low_latency/sources/2023/FSB-LSTM 2023]]
~~~

# DPCRN: Dual-Path Convolution Recurrent Network for Single Channel Speech Enhancement

> Xiaohuai Le 等，2021。本文重点记录 DPCRN 的复数谱和双路径设计，同时明确其原始 37.5 ms 前端与本方向 2 ms 目标的差距。

> [!warning] PDF 转换质量与阅读说明
> 原 PDF 共 5 页。Poppler 渲染第 1-5 页时仅报告 Symbol/ArialUnicode 字体回退 warning，但页面图像清晰；PDF 文本层抽取对复数符号、上下标、希腊字母、连字和 Table 1-4 的列间距有错位。下文公式、架构图和数值以原 PDF 页面视觉核对为准；图中 f、t、c 轴分别表示 frequency、time、channel。

## 1. 他们为什么这么做？（motivation）

### 1.1 任务背景

噪声与混响会降低可懂度和 ASR 性能。时频域增强能利用语音的谐波谱结构，但复数相位难以直接估计；时间域模型又容易遇到超长序列，传统 RNN 和有限感受野 CNN 很难同时覆盖长上下文。

### 1.2 论文目标

DPCRN 将 CRN 的局部谱建模和 DPRNN 的长序列分块建模结合起来：卷积编码器先压缩局部时频结构，DPRNN 沿频率建模同一帧的谐波关系，沿时间建模帧间演化，最后由解码器估计 CRM。作者在 DNS challenge 约束下追求小参数量与实时运行，而不是 2 ms 前端。

## 2. 之前的人怎么做不了？（limitation → gap）

### 2.1 既有路线的缺口

| 路线              | 能力                            | 不能直接满足的地方                        |
| --------------- | ----------------------------- | -------------------------------- |
| IRM/TMS/PSM     | 能从 noisy spectrum 估计幅度或相位相关掩码 | 不能完整表达复数相位，谐波相关性利用不足             |
| DCCRN 等复数 CRN   | 可直接建模 real/imag 与 CRM         | 单一路径 RNN 的时间/频率上下文分工不清，长谱序列建模成本高 |
| 时间域 Conv-TasNet | 绕过显式相位估计                      | 超长 waveform context 和端侧计算压力较大    |
| BiLSTM/非因果模型    | 上下文充分                         | 未来帧依赖不适用于实时语音增强                  |

因此 gap 是：**如何把“频率内的双向谱模式”和“时间上的因果记忆”拆开，让复数谱增强同时保留谐波结构和实时时间因果。**

### 2.2 strict-causal 与 latency ledger

| 项目 | 论文给出的信息 | 本 Wiki 判定 |
|---|---|---|
| 时间因果 | inter-chunk 使用 LSTM；作者明确用它保证 strict causality | 时间递归路径论文级支持 |
| 频率 BiLSTM | intra-chunk BiLSTM 沿单帧频率/通道维处理，不沿未来时间帧处理 | 不破坏时间因果，但需实现确认维度排列 |
| 前端 | 25 ms window、12.5 ms hop、FFT 400、sine window；论文给出 total latency 37.5 ms | 远高于本 Wiki 约 2 ms 硬约束，属于低于传统长窗但非超低时延候选 |
| 模型 | Conv-2D 与 transposed Conv-2D causal computed；两层 DPRNN | 结构上适合流式时间计算，但未给逐层 buffer certificate |
| 运行时 | TensorFlow 单帧 8.9 ms、约 7.45 GFLOPS、四核 i5-6300HQ | 仅是参考硬件结果，不是 p99 deadline 或目标 SoC 证据 |
| look-ahead | Table 3 中 DPCRN-1/2 为 0 ms | 支持 paper-level no-look-ahead，不等于端到端零延迟 |
| recurrent state | inter-chunk LSTM 跨帧保留状态 | state reset、warm-up、断流恢复未报告 |
| RTF | 未报告 | 不能由 8.9 ms 单帧时间自行改写为论文 RTF |
| deadline / I/O | 论文称满足 DNS challenge requirement；ADC/DMA、buffer、DAC、capture-to-playback 未报告 | 没有 p50/p95/p99、deadline miss 或端到端证据 |

> [!question] 关键判断
> DPCRN 的“real-time”来自 DNS challenge 和单帧处理速度，不等同于本方向的约 2 ms algorithmic latency。若迁移到本方向，必须先替换/重做前端，并重新证明 DPRNN 的缓存、频率 BiLSTM 和 OLA 没有引入额外未来依赖。

## 3. 这个做法核心 trick 是什么？

### 3.1 复数 CRM 与信号近似

混合信号和 STFT 表示为：

$$
x(t)=s(t)+n(t).
$$

$$
X(t,f)=S(t,f)+N(t,f). \tag{1}
$$

DPCRN 估计复数比率掩码：

$$
M(t,f)=M_r(t,f)+iM_i(t,f),
$$

$$
\widetilde{S}(t,f)=X(t,f)\odot M(t,f). \tag{2}
$$

其中 $X,S,N$ 是 noisy、clean 和 noise 的复数 STFT，$M_r,M_i$ 是 CRM 的实部/虚部，$\odot$ 是逐元素复数乘法。展开复数乘法：

$$
\widetilde S=X_rM_r-X_iM_i+i(X_rM_i+X_iM_r), \tag{6}
$$

然后通过 iSTFT 得到 $\tilde s$。这种输出同时控制幅度和相位相关的 real/imag 结构。

$$
\widetilde s=\operatorname{iSTFT}(\widetilde S). \tag{7}
$$

### 3.2 Dual-Path CRN

![[wiki_low_latency/assets/2107.05429/2107.05429-page3-architecture-formulas.png]]

图 1（原论文第 3 页渲染）：DPCRN 的 dual-path recurrent 建模与复数时频路径。

- **Encoder**：把 noisy complex spectrum 的实部和虚部作为两路输入，经 2-D Conv 压缩局部时频模式；
- **Intra-chunk RNN**：把一帧的频率维视为 chunk，用 BiLSTM 捕获谐波/频谱结构；
- **Inter-chunk RNN**：沿时间维用 LSTM 建模连续帧，保证时间因果；
- **Decoder**：转置卷积恢复分辨率，并通过 skip connection 传回细节；
- **输出**：两路 decoder 输出 $M_r,M_i$，构成 CRM。

每层卷积后接 batch normalization 和 PReLU；DPRNN 中的 RNN 后接 FC、instant layer normalization（iLN）和残差连接。

论文给出的主配置为：encoder channels $\{32,32,32,64,128\}$；各 Conv-2D 的 frequency/time kernel 分别为 $\{(5,2),(3,2),(3,2),(3,2),(3,2)\}$，stride 分别为 $\{(2,1),(2,1),(1,1),(1,1),(1,1)\}$。模型使用 2 个 DPRNN、RNN hidden dimension=128；提交配置将送入 DPRNN 的 feature frequency dimension 设为 50，以在频率分辨率和实时计算间取平衡。DPCRN-3 将前 3 个 frequency stride 改为 $(2,1),(2,1),(2,1)$，并把 intra-chunk RNN hidden dimension 加倍，以保持相近计算量。

### 3.3 iLN 和损失

对每个时间帧独立在频率/通道轴上计算统计量，iLN 可减少输入能量变化对输出的影响：

$$
\operatorname{iLN}(F_t)=
\frac{F_t-\widehat E[F_t]}{\sqrt{\widehat D[F_t]+\epsilon}}
\odot\gamma+\beta. \tag{3}
$$

其中 $F_t\in\mathbb{R}^{N\times K}$，$N$ 和 $K$ 分别是当前 frame 的 frequency 与 channel feature dimensions，$\gamma,\beta\in\mathbb{R}^{N\times K}$ 是可训练参数，$\epsilon$ 是正则项。均值和方差为：

$$
\widehat E[F_t]=\frac{1}{NK}\sum_{f=1}^{N}\sum_{c=1}^{K}F_t[f,c]. \tag{4}
$$

$$
\widehat D[F_t]=\frac{1}{NK}\sum_{f=1}^{N}\sum_{c=1}^{K}
\left(F_t[f,c]-\widehat E[F_t]\right)^2. \tag{5}
$$

作者比较两种损失。首先是约束幅度的负 SNR：

$$
f(s,\widetilde s)=-10\log_{10}\frac{\sum_t s(t)^2}{\sum_t(s(t)-\widetilde s(t))^2}. \tag{8}
$$

DPCRN-2 在此基础上增加 real、imag 和 magnitude 的谱 MSE：

$$
\mathcal L_{\mathrm{MSE}}=f(s,\widetilde s)+\log\bigl(
\operatorname{MSE}(S_r,\widetilde S_r)+\operatorname{MSE}(S_i,\widetilde S_i)
+\operatorname{MSE}(|S|,|\widetilde S|)\bigr). \tag{9}
$$

这里 $S_r,S_i$ 与 $\widetilde S_r,\widetilde S_i$ 分别是 clean/enhanced spectrogram 的 real/imaginary parts，$|S|$ 与 $|\widetilde S|$ 是 magnitude。论文只给出三项 MSE 的组成和 logarithm 缩放，没有给出 MSE reduction、归一化维度或训练代码，因此不补造这些实现细节。

### 3.4 输入输出与符号表

| 符号/阶段 | 含义 |
|---|---|
| $x(t),s(t),n(t)$ | noisy、clean、noise waveform |
| $X(t,f),S(t,f),N(t,f)$ | noisy、clean、noise complex STFT；$t$ 是 frame，$f$ 是 frequency bin |
| $M=M_r+iM_i$ | decoder 输出的 complex ratio mask |
| $\widetilde S,\widetilde s$ | enhanced complex spectrum 与 iSTFT waveform |
| $F_t\in\mathbb{R}^{N\times K}$ | 第 $t$ 帧进入 iLN/RNN 的 feature matrix |
| $\widehat E,\widehat D$ | 当前 frame 在 frequency/channel 维度上的 mean 与 variance |
| $\gamma,\beta,\epsilon$ | iLN 的 scale、bias 与 regularizer |
| $\odot$ | noisy spectrum 与 CRM 的逐元素复数乘法 |

概念上的输入输出张量可写成：

| 阶段 | 形式 | PDF 位置 |
|---|---|---|
| 输入 | 16 kHz noisy waveform 经 25 ms/12.5 ms STFT；201 个单边 complex bins 的 real/imag 两路 | pp. 2-3 |
| 网络输出 | 与 201-bin spectrum 对齐的 $M_r,M_i$ 两路 CRM | pp. 2-3 |
| 增强谱 | $\widetilde S=X\odot M$ | Eq. (2), p. 2 |
| 最终输出 | $\widetilde s=\operatorname{iSTFT}(\widetilde S)$ | Eq. (7), p. 3 |

## 4. 实验里哪个消融最关键？

### 4.1 数据与训练设置

| 项目 | 设置 |
|---|---|
| 训练数据 | DNS 2021 challenge；约 60,000 个 reverberant speech clips（约 500 h），55,000 train、5,000 validation |
| 噪声与混响 | AudioSet、DEMAND、Freesound；openSLR26/28 随机 RIR；5 s segments；训练混合 SNR -5 到 5 dB |
| 采样率/前端 | 16 kHz；25 ms window、12.5 ms hop、FFT 400、201 维复数谱；总算法延迟 37.5 ms |
| 模型 | Conv channels {32,32,32,64,128}；2 个 DPRNN；RNN hidden=128；约 0.8M 参数 |
| 训练 | Adam，batch=8，初始 lr $10^{-3}$；验证集 5 epochs 不提升则 lr 减半，10 epochs 不提升 early stop；TensorFlow，GTX 1080Ti |
| 指标 | WSJ0 用 PESQ、STOI、SDR；DNS dev 用 DNSMOS；blind test 用 ITU-T P.835 |

WSJ0 测试语音包含 651 条 utterances、8 位说话人；测试噪声是 MUSAN 的 music，以及 NOISEX92 的 babble、factory1 和 f16。DNS 训练/验证片段与噪声的完整构造细节以本地 PDF p. 3 为准，PDF 未报告随机种子、训练时长、公开代码或 commit。

### 4.2 关键结构/损失消融

| 模型 | 改动 | 关键观察 |
|---|---|---|
| DPCRN-1 | 负 SNR loss | 低 SNR 已优于 DCCRN，但质量上限有限 |
| DPCRN-2 | 负 SNR + real/imag/magnitude 谱 MSE | PESQ/STOI 最好，选为 wide-band 提交模型 |
| DPCRN-3 | 频率 stride 降低分辨率、intra-chunk hidden 加倍以保持复杂度 | 质量变差，说明降低频率分辨率损害谐波/谱细节 |

### 4.3 主结果

![[wiki_low_latency/assets/2107.05429/2107.05429-page4-results-tables.png]]

> 图注：原论文第 4 页页面渲染，包含 Tables 1-4 与结果分析正文；具体数字以原 PDF 为准。

| 模型/数据 | PESQ avg | STOI avg (%) | SDR avg (dB) |
|---|---:|---:|---:|
| Noisy，WSJ0-MUSAN | 2.01 | 80.72 | 0.05 |
| DTLN，WSJ0-MUSAN | 2.59 | 89.34 | 9.85 |
| DCCRN，WSJ0-MUSAN | 2.84 | 92.04 | 10.76 |
| DPCRN-1，WSJ0-MUSAN | 2.83 | 91.82 | **11.04** |
| DPCRN-2，WSJ0-MUSAN | **2.85** | 92.02 | 10.99 |
| DPCRN-3，WSJ0-MUSAN | 2.66 | 90.08 | 9.88 |
| Noisy，WSJ0-NOISEX92 | 1.72 | 74.94 | 0.09 |
| DTLN，WSJ0-NOISEX92 | 2.31 | 83.91 | 8.42 |
| DCCRN，WSJ0-NOISEX92 | 2.32 | 85.59 | 7.87 |
| DPCRN-1，WSJ0-NOISEX92 | 2.43 | 86.33 | 9.25 |
| DPCRN-2，WSJ0-NOISEX92 | **2.46** | **86.38** | 9.16 |
| DPCRN-3，WSJ0-NOISEX92 | 2.29 | 84.78 | 8.50 |

DNS challenge development 表中 DPCRN-2 为 0.8M 参数、0 ms look-ahead、DNSMOS 3.472；blind test 的 DPCRN-2 为 Speech MOS 3.76、Background Noise MOS 4.34、Overall MOS 3.57，wide-band 赛道排名第三。论文同时报告约 7.45 GFLOPS 和四核 i5-6300HQ 上 8.9 ms 的 one-frame processing time。

| DNS blind 模型 | Speech MOS | Background Noise MOS | Overall MOS |
|---|---:|---:|---:|
| Noisy | 3.89 | 2.60 | 2.77 |
| NSNet2 | 3.35 | 3.88 | 3.07 |
| DPCRN-2 | 3.76 | 4.34 | 3.57 |

DPCRN-2 的 Background Noise MOS 和 Overall MOS 高于 noisy，但 Speech MOS=3.76 低于 noisy 的 3.89；这是一条直接的人声保留/噪声抑制权衡证据，不能解读为人声细节无损。

### 4.4 对低时延课题最重要的消融结论

谱 MSE 对 real/imag/magnitude 的联合约束改善了增强质量，但这不能抵消 25 ms window 带来的 37.5 ms 算法前端。DPCRN-3 的失败还提示：在低时延迁移中不能只压低频率分辨率来换算力；PDF 指标支持频率谱细节受损，但没有单独测量弱辅音保留。

## 5. 这个方向还剩什么问题没解决？（future work / limitation）

### 5.1 论文明确提出的 future work

论文结尾提出继续降低宽带谱处理的计算复杂度。

### 5.2 对当前低时延/人声保留课题的缺口

- 37.5 ms total latency 明确超过约 2 ms 方向边界；模型不能直接作为严格超低时延前端。
- “causal”主要由时间维 LSTM 和 causal Conv 保证，但没有逐层 look-ahead、OLA startup/flush、状态 reset 或硬件 p99 certificate。
- DNSMOS/P.835 反映总体质量，却没有 false-suppression、弱辅音/气声保留、F0/formant/prosody、ASR WER 或听障用户评估。
- 论文没有在负 SNR 之外系统报告突发噪声、非平稳噪声、丢帧和 long-stream drift。

### 5.3 可迁移启示

若将 DPCRN 作为教师或结构参照，可保留 CRM、频率 intra-chunk/时间 inter-chunk 分工，并把 STFT 改成 2–3 ms 非对称/可学习前端；同时用负 SNR、人声保留和 deadline p99 作为一等目标，而不是只比较 PESQ。

## 6. 本论文在库中的位置关联（cross-reference matrix）

| 关系 | 库中论文/概念 | 关联与差异 |
|---|---|---|
| 复数谱前身 | [[wiki_low_latency/sources/2020/DCCRN Low-Latency Direction 2020]] | 都输出 complex mask；DPCRN 用 dual-path 让频率/时间建模分工更清晰 |
| 时域对照 | [[wiki_low_latency/sources/2021/On TasNet Low-Latency SE 2021]] | On-TasNet 绕过相位但依赖时域编码；DPCRN 保留复数谱可解释性，前端延迟更大 |
| 同方向结构 | [[wiki_low_latency/sources/2023/FSB-LSTM 2023]] | FSB-LSTM 追求 very low algorithmic latency；DPCRN 的 37.5 ms 只能作为较高时延上界/教师候选 |
| 低复杂度保真 | [[wiki/sources/2023/DeepFilterNet 2023]] | DeepFilterNet 用 deep filtering 恢复相位/周期性；DPCRN 用 CRM 和 dual-path 谱上下文 |
| 方向概念 | [[wiki_low_latency/concepts/严格因果与算法延迟]] | DPCRN 的时间路径支持 causal，但前端窗口违反本 Wiki 的约 2 ms 目标 |
| 人声保留缺口 | [[wiki_low_latency/concepts/低 SNR 人声保留评估]] | DPCRN 的 PESQ/STOI/P.835 尚不能替代误抑制与音素级保留 |

> [!question] 关联不确定性
> DPCRN 论文的“real-time”与本 Wiki 的“ultra-low-latency”是不同标签；在索引里应标为 37.5 ms 复数谱基线，不要与 2 ms 方法直接做质量排名。

## 7. 一句话总结“江湖地位”

> **DPCRN 是复数谱语音增强中把“频率谐波建模”和“时间因果记忆”拆开的经典双路径基线：它以 0.8M 参数和 DNS 质量证明了结构价值，但原始 37.5 ms 前端使它更适合作为低时延迁移的教师/上界，而不是约 2 ms 的终端方案。**

### 参考资料

- [arXiv:2107.05429](https://arxiv.org/abs/2107.05429)
- 本地原件：raw/papers/low_latency_causal_se/2107.05429.pdf
- Figure 1、Table 1–4：原 PDF 第 3、4 页，已嵌入本页。
