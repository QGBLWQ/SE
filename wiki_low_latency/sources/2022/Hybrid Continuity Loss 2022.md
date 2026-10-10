---
title: Hybrid Continuity Loss - 过抑制与时域目标说话人提取
type: source
created: 2026-09-16
updated: 2026-09-16
tags:
  - target-speaker-extraction
  - audio-visual
  - time-domain
  - continuity-loss
  - over-suppression
  - speech-preservation
  - ASR
year: 2022
authors: Zexu Pan, Meng Ge, Haizhou Li
venue: arXiv preprint
source_type: paper
arxiv: https://arxiv.org/abs/2203.16843
local_pdf: raw/papers/low_latency_causal_se/2203.16843.pdf
related:
  - [[wiki_low_latency/entities/Hybrid-Continuity-Loss]]
  - [[wiki_low_latency/concepts/2203.16843-continuity-loss]]
  - [[wiki_low_latency/index]]
  - [[wiki/sources/2019/Conv-TasNet - Surpassing Ideal TF Masking 2019]]
  - [[wiki/sources/2021/DPCRN 2021]]
  - [[wiki_low_latency/sources/2023/GCFSnet 2023]]
---

~~~yaml
- 论文: [A Hybrid Continuity Loss to Reduce Over-Suppression for Time-domain Target Speaker Extraction](2022)
  ├── 要解决什么问题: 时域目标说话人提取会过度抑制目标语音的时频成分，产生听感伪影并伤害下游 ASR
  ├── 核心方法: 在负 SI-SDR 波形损失上叠加多分辨率 delta spectrum loss，联合约束幅度、差分和加速度连续性
  ├── 属于哪个分支: 时域目标说话人提取 / 音视频辅助 / 人声保留 / 损失函数
  ├── 输入/输出: 16 kHz 混合波形与同步目标唇部视频 → latent mask → 目标说话人时域波形
  ├── 关键trick: SI-SDR 保持波形质量，频域多分辨率差分与加速度特征惩罚过抑制；两条损失互补
  ├── 数据集: LRS2-mix 200k/5k/3k；16 kHz；另加 WHAM! babble，目标-干扰 SNR 10 到 -10 dB、噪声 SNR 15 到 -5 dB
  ├── 对比了谁: mixture speech、SI-SDR loss、Hybrid loss、clean speech；消融 Lsc/Lmag、delta 特征和单/多分辨率
  ├── 性能上限: clean Hybrid SI-SDR=13.48、PESQ=3.163、STOI=.934、AV-WER=16.1；noisy SI-SDR=5.12、PESQ=2.276、AV-WER=34.5
  ├── 参数量: 未报告；Conv1D C=256、kernel=40、stride=20；mask estimator 为 R=6 个 dual-path LSTM
  ├── 消融关键发现: 多分辨率 delta 特征把 clean AV-WER 降到 16.1；去掉 delta 后 WER=16.3，单分辨率为 16.5/17.1/16.3
  ├── 遗留问题(你的机会): 基础网络和训练损失都没有严格因果/端到端 p99 证据；under-suppression 略增，且没有低 SNR 分层的人声保留与硬件实测
  └── 跟哪篇像: [[wiki/sources/2019/Conv-TasNet - Surpassing Ideal TF Masking 2019]]、[[wiki_low_latency/sources/2023/GCFSnet 2023]]、[[wiki_low_latency/concepts/2203.16843-continuity-loss]]
~~~

# A Hybrid Continuity Loss to Reduce Over-Suppression for Time-domain Target Speaker Extraction

> Zexu Pan, Meng Ge, Haizhou Li，2022。论文以音视频目标说话人提取为验证平台，本文在严格因果低时延 Wiki 中主要作为“人声保留/过抑制损失”参照，而不是 2 ms 合格系统。

> [!warning] PDF 转换质量与阅读说明
> 原 PDF 共 5 页，页面渲染清晰。pdftotext 对下标、帽子、希腊字母、delta 符号和集合下标存在丢失或错位，尤其是公式 (5)-(10)；下文的公式、Table 1/2 和 Figure 1-3 均以原 PDF 页面视觉核对。公式中的符号若与纯文本抽取不一致，应以原 PDF 和本页的显式定义为准。

## 1. 他们为什么这么做？（motivation）

### 1.1 任务与痛点

论文研究的是目标说话人提取（target speaker extraction）：混合信号中包含目标说话人、一个或多个干扰说话人和背景噪声，系统只输出目标说话人的语音。与需要预先知道说话人数并输出所有流的 speech separation 不同，extraction 需要一个辅助目标线索；本文使用与语音同步的唇部视频。

核心痛点是 **over-suppression**：模型虽然把干扰压掉了，却同时把目标语音的某些时频单元压到过低，产生听感伪影，并使下游自动语音识别（ASR）变差。时域网络可以绕开 STFT 的相位重建问题，但单独优化 waveform-level SI-SDR 并不直接约束目标幅度谱的时间连续性。

### 1.2 为什么对当前方向有价值

本文不是严格低时延网络论文，但它把“语音保留”从一个泛化的听感描述变成了可优化的训练对象：在波形质量之外，显式观察过抑制和欠抑制误差，并用前后帧差分特征约束谱的连续性。这与本 Wiki 关注的低 SNR、弱辅音和音节边缘不被误抑制直接相连。

## 2. 之前的人怎么做不了？（limitation → gap）

### 2.1 既有路线的局限

| 路线 | 已有能力 | 没解决的缺口 |
|---|---|---|
| Speech separation | 将混合语音拆成多个说话人流 | 通常需要已知说话人数；目标说话人提取还需要额外目标线索 |
| 频域 speaker extraction | 可直接操作幅度谱；VoiceFilter-Lite 使用 asymmetric loss 惩罚过抑制 | 频域路线有相位重建问题；不确定非对称幅度损失是否损害重建质量 |
| 时域网络 + SI-SDR | 直接优化波形，避免运行时 STFT 相位重建 | 只看整体波形相似度，可能忽略局部时频连续性，造成 over-suppression |
| 仅使用频域连续性损失 | 可以约束谱的平滑或局部变化 | 不能单独保证波形重建质量；需要与时域目标互补 |

### 2.2 论文提出的 gap

论文的 gap 是：如何在保持 time-domain system 重建质量的同时，让目标语音的幅度谱在多个时间尺度上连续，从而降低过抑制并改善 ASR。作者的回答是把 negative SI-SDR 与 multi-resolution delta spectrum loss 组合起来。

### 2.3 严格因果与延迟审计

| 项目 | 论文给出的信息 | 本 Wiki 判定 |
|---|---|---|
| 运行时前端 | 16 kHz；Conv1D kernel $L=40$ samples、stride $L/2=20$ samples，约 2.5 ms 窗、1.25 ms 帧移 | 只有短时域编码器线索，不等于端到端 2 ms |
| mask estimator | $R=6$ 个 dual-path LSTM，用于捕获全局依赖 | strict_causal：未证实；global dependency 与 streaming cache 细节未报告 |
| 训练损失 | 多分辨率 STFT、delta $f_D$ 和 acceleration $f_A$；$f_D$ 同时读取 $t+l$ 与 $t-l$ | 训练目标显式使用未来帧；可作为离线训练监督，但不能作为因果运行时证据 |
| 最大损失窗 | FFT/window $\{512,1024,2048\}/\{240,600,1200\}$，最大窗 75 ms（16 kHz） | loss context 很长；不应把它写成模型 algorithmic latency |
| 输出重建 | Linear + overlap-and-add，步长 $L/2$ | 输出形式是时域波形；论文没有给设备端 buffer/p99 |
| 计算量与部署 | 未报告参数量、MAC/s、RTF、SRAM、目标硬件、deadline miss | 不能声称端侧实时，更不能声称 capture-to-playback $\leq2$ ms |

> [!question] 低时延结论边界
> 这篇论文在本 Wiki 中应标为“speech-preservation/loss reference，模型级 strict causality 未证实”。若将其 hybrid loss 迁移到 causal enhancer，需要把双侧 delta 改成 past-only 或延迟监督，并重新测量真实设备的 p99，而不是沿用论文的离线 multi-resolution loss 设置。

## 3. 这个做法核心 trick 是什么？

### 3.1 音视频时域提取管线

混合波形写为：

$$
x(\tau)=s(\tau)+\sum_{i=1}^{I}b_i(\tau)+n(\tau). \tag{1}
$$

- $x(\tau)$：混合时域波形；
- $s(\tau)$：目标说话人波形；
- $b_i(\tau)$：第 $i$ 个干扰说话人；
- $n(\tau)$：背景噪声；
- $I$：干扰说话人数。

语音编码器把波形变成 latent frame embedding：

$$
X(t)=\operatorname{ReLU}\bigl(\operatorname{Conv1D}(x(\tau),C,L,L/2)\bigr), \tag{2}
$$

其中 $C=256$ 为通道数，$L=40$ 为 kernel size，stride 为 $L/2=20$。视觉编码器用固定的预训练 ResNet18 和 5 层 temporal convolution，将同步唇部帧 $v(t)$ 映射为 viseme embedding $V(t)$。mask estimator 拼接 $V(t)$ 与 $X(t)$，由 $R=6$ 个 dual-path LSTM 建模依赖并预测目标 mask：

$$
\widehat{S}(t)=M(t)\odot X(t), \tag{3}
$$

最后用线性层和 overlap-and-add 解码：

$$
\widehat{s}(\tau)=\operatorname{OnA}\bigl(\operatorname{Linear}(\widehat{S}(t),C,L),L/2\bigr). \tag{4}
$$

这里 $\odot$ 是逐元素乘法；$\widehat S(t)$ 是 latent space 的目标 embedding，$\widehat s(\tau)$ 是输出波形。

### 3.2 核心 trick：波形 SI-SDR + 多分辨率 delta 谱连续性

负 SI-SDR 负责整体波形重建。令

$$
\alpha=\frac{\langle \widehat{s},s\rangle}{\lVert s\rVert_2^2},
\qquad
\mathcal{L}_{\mathrm{SI-SDR}}
=-20\log_{10}\frac{\lVert \alpha s\rVert_2}
{\lVert \widehat{s}-\alpha s\rVert_2}. \tag{5}
$$

其中 $s$ 是目标参考波形，$\widehat{s}$ 是提取波形，$\alpha s$ 是对目标的最优尺度投影。

Hybrid loss 为：

$$
\mathcal{L}_{\mathrm{hybrid}}
=\mathcal{L}_{\mathrm{SI-SDR}}
+\gamma\frac{1}{M}\sum_{m=1}^{M}\mathcal{L}^{m}_{\mathrm{freq-\Delta}}, \tag{6}
$$

其中 $M=3$，$\gamma=1$。三个频率分辨率分别为：

| 分辨率 $m$ | FFT bins | hop | window |
|---:|---:|---:|---:|
| 1 | 512 | 50 | 240 |
| 2 | 1024 | 120 | 600 |
| 3 | 2048 | 240 | 1200 |

$\mathcal{L}_{\mathrm{freq-\Delta}}$ 由 spectrum convergence 与 log-magnitude 两部分组成：

$$
\mathcal{L}_{\mathrm{freq-\Delta}}
=\mathcal{L}_{\mathrm{sc-\Delta}}+\mathcal{L}_{\mathrm{mag-\Delta}}. \tag{7}
$$

$\mathcal{L}_{\mathrm{sc-\Delta}}$ 在原始幅度谱、delta 幅度谱和 acceleration 幅度谱上使用归一化 Frobenius 距离；$\mathcal{L}_{\mathrm{mag-\Delta}}$ 在对应的 log-magnitude 上使用归一化 $L_1$ 距离：

$$
\mathcal{L}_{\mathrm{sc-\Delta}}
=\frac{\lVert |STFT(s)|-|STFT(\widehat{s})|\rVert_F}
{\lVert |STFT(s)|\rVert_F}
+\frac{\lVert f_D(|STFT(s)|)-f_D(|STFT(\widehat{s})|)\rVert_F}
{\lVert f_D(|STFT(s)|)\rVert_F}
+\frac{\lVert f_A(|STFT(s)|)-f_A(|STFT(\widehat{s})|)\rVert_F}
{\lVert f_A(|STFT(s)|)\rVert_F}, \tag{8}
$$

$$
\mathcal{L}_{\mathrm{mag-\Delta}}
=\frac{1}{N}\lVert \log|STFT(s)|-\log|STFT(\widehat{s})|\rVert_1
+\frac{1}{N}\lVert f_D(\log|STFT(s)|)-f_D(\log|STFT(\widehat{s})|)\rVert_1
+\frac{1}{N}\lVert f_A(\log|STFT(s)|)-f_A(\log|STFT(\widehat{s})|)\rVert_1. \tag{9}
$$

其中 $N$ 是时频单元数量，$f_D$ 是差分特征，$f_A$ 是对 $f_D$ 再做一次得到的 acceleration。论文令 $L=2$：

$$
f_D(v(t))
=\frac{\sum_{l=1}^{L}l\,[v(t+l)-v(t-l)]}
{\sum_{l=1}^{L}2l^2},\qquad f_A(v)=f_D(f_D(v)). \tag{10}
$$

**最关键的设计不是“再加一个谱损失”，而是把差分和加速度特征放到多个 STFT 分辨率中。** 这样模型会看到局部帧与更长时间范围内的谱变化，过抑制的单帧不容易孤立存在。

### 3.3 论文原图：输入、mask 和双目标损失

![[wiki_low_latency/assets/2203.16843/2203.16843-page2-pipeline.png]]

Figure 1 展示了混合波形与唇部视频如何进入双路编码器，mask 在 latent space 中提取目标语音，解码为波形后再同时计算 $\mathcal{L}_{SI-SDR}$ 与频域 $\mathcal{L}_{freq-\Delta}$。这也说明频域 loss 是训练约束，而不是论文声称的运行时后处理。

## 4. 实验里哪个消融最关键？

### 4.1 数据、训练和评估

| 项目 | 论文设置 |
|---|---|
| 原始数据 | LRS2 train/validation/test：45,839 / 1,082 / 1,243 条 clean utterances；16 kHz；视频 25 fps |
| LRS2-mix | train/validation/test：200,000 / 5,000 / 3,000 条两说话人 mixture |
| 干扰设置 | 干扰语音截断或 zero-pad 到目标长度；target-interference SNR 为 10 到 -10 dB |
| noisy 设置 | 从 WHAM! 采样 babble noise；noise SNR 为 15 到 -5 dB；测试说话人不与 train/validation 重叠 |
| 模型 | 固定预训练 ResNet18 + 5 层 temporal conv；speech Conv1D $C=256,L=40$；$R=6$ dual-path LSTM |
| 训练 | PyTorch；Adam，初始 lr=0.001；验证最优 loss 连续 6 epochs 不提升则 lr 减半，连续 10 epochs 不提升停止 |
| 长度 | 训练时 utterance 截断为 6 s；评估使用完整 utterance |
| 指标 | SI-SDR、SDR、PESQ、STOI；audio-visual/audio-only ASR 的 WER/CER；over/under-suppression MAE |

over-suppression 与 under-suppression MAE 在 FFT=512、hop=120、window=600 的 STFT 上定义：

$$
MAE_{\mathrm{over}}
=\frac{1}{N}\left\lVert \operatorname{ReLU}\bigl(|STFT(s)|-|STFT(\widehat{s})|\bigr)\right\rVert_1, \tag{11}
$$

$$
MAE_{\mathrm{under}}
=\frac{1}{N}\left\lVert \operatorname{ReLU}\bigl(|STFT(\widehat{s})|-|STFT(s)|\bigr)\right\rVert_1. \tag{12}
$$

### 4.2 主结果：ASR 和过抑制改善不等于 SI-SDR 大幅提升

| Noise | Model | SI-SDR | SDR | PESQ | STOI | AV WER/CER | Audio-only WER/CER | MAE over/under |
|---|---|---:|---:|---:|---:|---|---|---|
| Clean | Mixture speech | 0.79 | 1.10 | 1.985 | 0.708 | 59.2 / 36.5 | 80.9 / 54.7 | - / - |
| Clean | SI-SDR loss | 13.41 | 14.08 | 2.997 | 0.931 | 17.3 / 7.4 | 23.5 / 11.3 | 0.105 / 0.055 |
| Clean | Hybrid loss | **13.48** | **14.12** | **3.163** | **0.934** | **16.1 / 6.8** | **21.2 / 10.0** | **0.096 / 0.060** |
| Clean | Clean speech | 88.12 | 288.88 | 4.500 | 1.000 | 11.4 / 4.4 | 12.5 / 4.9 | - / - |
| Noisy | Mixture speech | -4.43 | -3.81 | 1.467 | 0.559 | 56.5 / 32.7 | 89.5 / 60.6 | - / - |
| Noisy | SI-SDR loss | 4.54 | 5.91 | 2.179 | 0.776 | 38.8 / 20.7 | 57.9 / 34.6 | 0.241 / 0.118 |
| Noisy | Hybrid loss | **5.12** | **6.52** | **2.276** | **0.789** | **34.5 / 17.7** | **50.8 / 29.5** | **0.223 / 0.119** |
| Noisy | Clean speech | 88.12 | 288.88 | 4.500 | 1.000 | 11.4 / 4.4 | 12.5 / 4.9 | - / - |

在 clean 集上，Hybrid 与 SI-SDR loss 的 SI-SDR 只提升 0.07 dB，但 PESQ 从 2.997 提升到 3.163，audio-visual WER 从 17.3 降到 16.1，over-suppression MAE 从 0.105 降到 0.096（约 8.6%）。代价是 under-suppression MAE 从 0.055 增至 0.060，说明“少误抑制”与“多留噪声/干扰”之间存在明确 trade-off。

在 noisy 集上，Hybrid 同时改善 SI-SDR、SDR、PESQ、STOI、两种 ASR WER/CER 和 over-suppression MAE；但 under-suppression 仍从 0.118 略升到 0.119。论文的结果支持“更适合下游 ASR 和人声连续性”，不支持“所有失真维度都无条件改善”。

### 4.3 关键消融：delta、多分辨率和两种谱项

| Sys | 频域 loss | FFT size | 使用 delta | SI-SDR | AV WER |
|---:|---|---|:---:|---:|---:|
| 1 | $L_{sc}+L_{mag}$ | {512,1024,2048} | ✓ | 13.48 | **16.1** |
| 2 | $L_{sc}$ | {512,1024,2048} | ✓ | 13.51 | 17.0 |
| 3 | $L_{mag}$ | {512,1024,2048} | ✓ | 13.28 | 16.5 |
| 4 | $L_{sc}+L_{mag}$ | {512,1024,2048} | ✗ | 13.46 | 16.3 |
| 5 | $L_{sc}$ | {512,1024,2048} | ✗ | 13.42 | 17.1 |
| 6 | $L_{mag}$ | {512,1024,2048} | ✗ | 13.44 | 16.6 |
| 7 | $L_{sc}+L_{mag}$ | 512 | ✓ | 13.25 | 16.5 |
| 8 | $L_{sc}+L_{mag}$ | 1024 | ✓ | 13.42 | 17.1 |
| 9 | $L_{sc}+L_{mag}$ | 2048 | ✓ | 13.26 | 16.3 |

最关键的消融结论是：单看 SI-SDR 不能选出最佳 loss，系统 2 的 SI-SDR 13.51 高于系统 1 的 13.48，但 WER 17.0 明显更差；完整的 $L_{sc}+L_{mag}$、delta/acceleration 和多分辨率组合让 WER 达到 16.1。去掉 delta 后 WER 只增加 0.2 个百分点，但单分辨率均未超过多分辨率配置。

![[wiki_low_latency/assets/2203.16843/2203.16843-page4-results.png]]

Figure 2 显示不同 target-interference SNR 下 Hybrid 与 SI-SDR loss 的 SI-SDR 接近；Figure 3 显示 Hybrid 的 audio-visual WER 在各 SNR 大多更低。这个组合恰好说明本论文的主张：loss 的价值主要体现在过抑制与下游 ASR，而不是单一 SI-SDR 的大幅上涨。

## 5. 这个方向还剩什么问题没解决？（future work / limitation）

### 5.1 论文明确给出的边界

论文结论只指出 hybrid loss 能减少时域 speaker extraction 的 over-suppression，并改善 downstream ASR；没有给出独立的 future-work 清单、真实设备实验或端到端延迟测量。因此，本节区分论文直接证据与读者可推导的缺口。

### 5.2 对低时延和人声保留的隐藏问题

1. **不是 strict-causal 证明。** dual-path LSTM 捕获 global dependencies；论文没有逐层说明 direction、chunk、state cache、padding 或 reset。训练的 $f_D$ 还显式访问 $t+l$ 的未来帧。
2. **短 kernel 不等于低端到端延迟。** 40-sample Conv1D 的 2.5 ms 窗和 1.25 ms hop 只是编码器局部尺度；最大 75 ms 的多分辨率 loss 是训练上下文，论文没有报告模型 p50/p95/p99、I/O buffer、warm-up、underrun/overrun 或 DAC。
3. **preservation 指标仍不完整。** over/under MAE 是有用的误抑制分解，但没有 DNSMOS SIG/BAK/OVL、false-suppression、F0/formant/prosody continuity、VAD/SPP 校准、主观听感或真实 ASR WER 的长流稳定性。
4. **数据场景集中。** 两说话人 LRS2-mix 加 WHAM! babble，视频与语音同步且测试说话人独立；没有瞬态噪声、真实房间、视频失步/缺失、多说话人数量变化和真实听障设备。
5. **质量 trade-off 没被隐藏。** Hybrid 降低 over-suppression，却在 clean/noisy 上略提高 under-suppression MAE；在低 SNR 下是否会保留过多竞争说话人，仍需按噪声类型分层验证。

### 5.3 可迁移实验机会

- 将 $f_D$ 改为只依赖当前/历史帧的 causal continuity loss，并比较不同延迟预算下的 over/under MAE、SIG/BAK 和 WER。
- 在短窗 causal STFT 或 learned-filterbank baseline 上加入 Hybrid loss，单独报告算法延迟、模型计算 p99 和 capture-to-playback。
- 将目标说话人提取改为单通道/无视频低 SNR enhancer，观察 continuity loss 是否仍能保留弱辅音和有声周期，而不依赖唇部 cue。

## 6. 本论文在库中的位置关联（cross-reference matrix）

| 关系 | 库中论文/概念 | 关联与差异 |
|---|---|---|
| 前身/基石 | [[wiki/sources/2019/Conv-TasNet - Surpassing Ideal TF Masking 2019]] | 继承时域 encoder-mask-decoder 和 overlap-add 思路；本文把主要创新放到 loss，而不是重新发明时域网络 |
| 前身/基石 | [VoiceFilter-Lite](https://arxiv.org/abs/2005.08970) | 频域 asymmetric loss 同样直接针对 over-suppression；本文把问题带到时域网络并增加连续性监督 |
| 同分支竞品 | [[wiki_low_latency/entities/DPCRN]] | DPCRN 代表复数 STFT/双路径上下文路线；可比较其相位建模与 continuity loss 对人声保留的互补性，具体结果待对应页面摄取 |
| 同分支竞品 | [[wiki_low_latency/entities/DCCRN]] | 复数谱相位感知网络重视频域重建；Hybrid loss 则使用谱连续性作训练约束，二者不应仅按 SI-SDR 排序 |
| 同分支竞品 | [[wiki_low_latency/sources/2023/GCFSnet 2023]] | GCFSnet 关注低比特率双耳空间链路和低时延部署；本论文提供可迁移的 anti-over-suppression loss，但原模型没有部署级延迟证据 |
| 损失函数关联 | [[wiki_low_latency/concepts/2203.16843-continuity-loss]] | 本页抽象的 delta/acceleration 连续性概念；可与后续 noise-suppression loss 和 uncertainty 页面比较 |
| 跨分支类比 | [[wiki/entities/RNNoise]] | RNNoise 用低复杂度 DSP+RNN 估计增益；本文提示增益/掩蔽训练还应监控 speech-preservation，而不只看整体噪声抑制 |
| 疑似关联 | [[wiki_low_latency/concepts/低比特率双耳特征链路]] | 一个解决跨设备条件新鲜度，一个解决训练中的谱连续性；两者可组合，但论文没有直接实验，需用户确认后再规划 |

> [!question] 关联不确定性
> DPCRN、DCCRN 和后续 loss 页面属于同一增强库中的相关方法，但不是本文的直接后续工作；上述关系用于研究路线索引，不表示论文之间存在明确引用或改进链。

## 7. 一句话总结“江湖地位”

> **2022 | 音视频时域目标说话人提取 / 人声保留 | 用多分辨率 delta 与 acceleration 频谱损失补上 SI-SDR 对过抑制和连续性的盲点 → 把 ASR 友好的人声保留变成可训练目标，但不是已经证明严格 2 ms 的部署方案。**

## 参考资料

1. [arXiv:2203.16843](https://arxiv.org/abs/2203.16843)
2. [作者提供的数据生成与训练代码](https://github.com/zexupan/avse_hybrid_loss)
3. [Deep-AVSR 预训练 ASR 模型](https://github.com/lordmartian/deep_avsr)
4. 本地原件：raw/papers/low_latency_causal_se/2203.16843.pdf
