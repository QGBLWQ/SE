# Ultra-low latency causal speech enhancement research map

**课题边界。** 本报告的“2 ms”默认指**算法输出延迟**，不是模型单帧耗时；目标是单通道优先、16 kHz 起步、实时通信/嵌入式端侧。文献以 2020–2026-09 为主；早期 Conv-TasNet 仅作为架构背景。除非表中明确写出，PESQ、STOI、SI-SDR 不能跨论文横比（数据、SNR、采样率和目标信号均不同）。

## 一句话判断

“2 ms 严格因果增强”已经有**算法级可行解**：2 ms 因果 RNN、2 ms 小窗 TasNet、短合成窗 STFT、SlowFast-SSM 都已有结果；最极端的 SlowFast-SSM 报告了 62.5 µs 算法延迟。但它还不是已解决的产品问题：这些结果通常未同时证明真实端侧的 capture-to-playback p99 ≤2 ms、负 SNR/突发噪声下的弱语音保真、长期流式状态稳定，以及主观听感。因此它属于**已有核心技术、仍有明显研究与工程交界空间**，而不是“换 Transformer 就会解决”的问题。

## 1. 概念与关系

```text
Speech enhancement
├─ Real-time: 平均吞吐达到实时（RTF < 1）；不保证小缓冲或无 future
├─ Streaming: 连续分块、维护状态；可有 look-ahead
│  └─ Causal: 时刻 t 的模型只读 x(≤t) 与过去状态
│     └─ Strict causal: 还禁止居中窗、future padding、chunk/batch 统计泄漏
│        └─ Ultra-low latency: 算法+缓冲+计算+I/O 的预算约 ≤2 ms
└─ Low-SNR / speech-preserving: 是上述部署约束下的质量目标，非独立网络类别
```

“frame-online”也不自动等于严格因果：居中 STFT、`same` 卷积的右侧 padding、双向归一化、完整 chunk 的 attention，都会使用未来样本。反过来，因果 RNN/SSM 的长历史状态不增加**算法延迟**，却增加状态内存和潜在算力。必须逐层审计。

### 1.1 延迟账本（论文最常混淆之处）

令采样率为 $f_s$、输入/分析窗 $W_a$、输出/合成窗 $W_s$、hop $H$、显式 future look-ahead $A$。对 OLA 类实现，常用下界是：

\[
L_{alg} \gtrsim A +(W_s-H),\qquad
L_{capture\to\play} =L_{ADC/DMA}+L_{inbuf}+L_{alg}+L_{compute,p99}+L_{outbuf}+L_{DAC}.
\]

对对称 STFT，实践上还需凑满一帧，常被计为约 $W$ 的总帧缓冲延迟；不能只报 $W-H$。若 $W_a>W_s$，必须说明较长分析窗的右端是否越过当前输出样点；若是，仍有 future context。因果卷积/GRU 的**过去感受野**不是 $A$，但状态初始化、缓存与 p99 运行时间必须报告。

| 方案 | 可达到的理论算法延迟 | 长处 | 主要代价/风险 |
|---|---:|---|---|
| waveform / learned filterbank，窗=2 ms | 约 1–2 ms | 无 STFT 分辨率束缚，天然相位联合建模 | 窗小、帧率高；容易增大 MAC/s 和混叠敏感性 |
| 对称 STFT，20/10 ms | 常约 20 ms 总帧延迟 | 频率分辨率高、易做 mask/beamforming | 不适合 2 ms |
| 短 STFT，2–4 ms | 2–4 ms | 可继续用频域生态 | 频率分辨率和低频谐波建模变差 |
| 16 ms 分析 + 2–4 ms 合成（双/非对称窗） | 2–4 ms | 保留较长分析频率信息 | 需严格验证右端因果性和 PR/边界伪影 |
| 未来帧**预测** | 可降至 2/0 ms | 不读取未来观测，减少 OLA 等待 | 只能用 mapping；未来相位/突发语音预测会失真，泛化差 |
| 慢快双支路 | 快支路决定 2 ms 或更低 | 慢支路低频率更新环境，削减冗余算力 | 慢支路特征必须比当前快帧旧，保证因果 |

Wu 与 Braun 的受控研究特别值得用来校准直觉：20→5→3 ms 时，固定模型性能下降；把模型扩得足够大可补回 3 ms 的分数，但 MAC/s 随 hop 缩短急升。其结果中，2.5 ms FBE 的 PESQ/STOI/SI-SDR 为 1.89/81.73%/7.80（模拟集），20 ms 基线为 2.22/84.45%/10.52；并发现 Mamba 在 20 ms 好、在更低延迟显著变差。[论文 HTML](https://arxiv.org/html/2409.10358)

## 2. 主流路线及 2 ms 适配性

| 类别 | 解决的核心问题与典型模型 | 严格 2 ms 适配性 | 结论 |
|---|---|---|---|
| **A. Time-domain** | Conv-TasNet/TCN、Wave-U-Net、sample/block RNN；直接估计波形或 learned-basis mask | **高**：2 ms encoder、1 ms hop 已验证 | 首选主干；因果 TCN 要避免非因果 norm 和大缓存 |
| **B. Frequency-domain** | causal STFT magnitude/complex mask、complex mapping、DCCRN | **中**：通常 20–40 ms；只有短/非对称窗才可 | 易解释、可和波束形成结合，但窗/OLA 是硬约束 |
| **C. Hybrid TF** | DTLN、STFT+learned basis、两阶段/beamformer+postfilter | **中**：可行但默认配置多不达标 | 有相位与频率结构优势；应重设前端，而非直接复用默认模型 |
| **D. Neural filterbank** | Conv-TasNet、deep filtering、可学习分析-合成、FBE | **高到中**：短 FIR/encoder 很适合；DFN 默认不适合 | 选择可学习短 filterbank 或 2 ms FBE；不要把 DFN 的 40 ms 误标为 2 ms |
| **E. Lightweight/edge** | PercepNet、DeepFilterNet、量化/剪枝、grouped recurrent、硬件流式 | **算力高，延迟取决于前端** | RTF/参数小不等于 2 ms；需实测目标设备 p99 和 SRAM |
| **F. RNN/SSM/Mamba** | GRU/LSTM、causal Transformer、Mamba/SSM、SlowFast SSM | LSTM/GRU **高**；SSM **有潜力**；Transformer **低到中** | 固定状态的 RNN/SSM 适合；attention KV cache 和小 hop 下的 Mamba退化要实证 |

### 2.1 时序骨干比较

| 骨干 | latency | streaming memory | 长历史能力 | 端侧部署难度 |
|---|---|---|---|---|
| causal CNN | 由前端决定；过去 RF 无额外算法延迟 | 卷积 ring buffer，随 RF 增长 | 中；dilation 能扩 RF | 低；但缓存和层间激活不可忽略 |
| causal TCN | 同上 | 多层 dilation buffer | 中到高 | 中；MAC/s 和 buffer 可能大 |
| GRU/LSTM | 由帧/前端决定 | 固定 hidden/cell state | 高（有遗忘风险） | **低**；小帧已有强证据 |
| streaming Transformer | chunk/look-ahead 决定 | KV cache 常随历史增长（或滑窗） | 高 | 高；低时延收益常不抵内存/实现成本 |
| SSM/Mamba | 由前端决定 | 固定状态（理论上） | 高 | 中；选择性扫描/GPU kernel/量化成熟度是风险 |
| SlowFast-SSM | 快支路窗决定 | 快状态 + 低频慢状态 | 高且减算力 | 中；必须做跨支路因果审计 |

## 3. 重点文献卡片

标记：**SC** = 论文信息足以支持严格流式/无未来观测；**LL** = 低 look-ahead 或帧在线但不能据此认定严格 2 ms；**NC** = 非因果或不适合该约束。`—` 表示该论文未在同一任务报告该指标，不能补造。

### 3.1 直接构成 2–4 ms 基线池

1. **A Simple RNN Model for Lightweight, Low-compute and Low-latency Multichannel Speech Enhancement in the Time Domain** — Ashutosh Pandey, Ke Tan, Buye Xu; *Interspeech 2023*, [DOI](https://doi.org/10.21437/Interspeech.2023-365).
   - **方法：**多麦时域小窗输入，轻量单向 RNN 输出波形；用最小输入上下文或固定 16 ms 上下文比较。**SC（最小窗口设置）**，1–16 ms；2 ms 时无 future context。
   - **结果（模拟 2/4/8 dB SNR，H=256，2 ms）：**STOI 74.0/78.4/81.3%，PESQ 1.92/2.07/2.19，输出 SNR 3.4/4.5/5.0 dB，1.60 M 参数、1.61 G MAC/s。更大 H=512 提升至 PESQ 2.03/2.23/2.34，但 6.37 G MAC/s。论文明确区分算法与计算延迟，见[表 1–3](https://www.isca-archive.org/interspeech_2023/pandey23b_interspeech.pdf)。
   - **判断：**是最干净的 2 ms 容量—算力基线之一；多通道设定不应直接和单通道 VoiceBank 分数比较。未专门以 preservation loss 优化。

2. **STFT-Domain Neural Speech Enhancement with Very Low Algorithmic Latency** — Zhong-Qiu Wang, Gordon Wichern, Shinji Watanabe, Jonathan Le Roux; *IEEE/ACM TASLP 2023*, [DOI](https://doi.org/10.1109/TASLP.2022.3224285).
   - **方法：**16 ms 分析、4 ms 合成、2 ms hop 的 complex RI mapping；可接帧在线 MCWF 和第二 DNN。将最后 DNN 改为预测一帧前方的目标，把算法延迟从 4 降至 2 ms。属于 **SC（无未来观测）但有 future-target prediction**，不是 future-context 模型；需要单独测预测失败。
   - **单通道结果：**2 ms 的 rect/one-frame-predict DNN：2.32 M 参数、27.76 G FLOPs/4 s、SI-SDR 2.53 dB、PESQ 1.846、eSTOI 66.64%；同论文 2 ms Conv-TasNet：6.14 M、52.21 G/4 s、2.18 dB、1.774、65.08%。完整窗、hop、预测和指标见[表 I](https://arxiv.org/html/2204.09911)。
   - **判断：**证明“频域不必然排除 2 ms”；但计算假定每 2 ms 帧均能完成，作者明确未证明弱端侧硬件能做到。低 SNR preservation 是间接的 SI-SDR/eSTOI 证据，非专门目标。

3. **Neural Speech Enhancement with Very Low Algorithmic Latency and Complexity via Integrated Full- and Sub-Band Modeling** — Zhong-Qiu Wang, Samuele Cornell, Shukjae Choi, Younglo Lee, Byeong-Yeol Kim, Shinji Watanabe; *ICASSP 2023*, [DOI](https://doi.org/10.1109/ICASSP49357.2023.10095700).
   - **方法：**STFT RI 特征，full-band LSTM + shared sub-band LSTM 的残差信息高速路；时间轴卷积核为 1，只缓存 LSTM state。**LL**：16 ms input、4 ms output、2 ms hop，4 ms 算法延迟，并非 2 ms。
   - **结果（6ch）：**FSB-LSTM 1.96 M、3.373 GMAC/s，SI-SDR 7.79、PESQ 2.61、eSTOI .830；MC-ConvTasNet 是 6.37 M/3.763 GMAC/s/5.20/2.24/.764。纯 FB-LSTM 缩至 2 ms hop（4 ms oWS）仍达 6.79/2.37/.795。见[表 2–5](https://arxiv.org/html/2304.08707)。
   - **判断：**不是 2 ms 交付基线，却是“简单单向 LSTM + 小状态”优于时域大模型的强反例；非常适合改为 2 ms 输出窗的起点。

4. **Modulating State Space Model with SlowFast Framework for Compute-Efficient Ultra Low-Latency Speech Enhancement** — Longbiao Cheng, Ashutosh Pandey, Buye Xu, Tobi Delbruck, Vamsi Krishna Ithapu, Shih-Chii Liu; *ICASSP 2025*, [arXiv](https://arxiv.org/abs/2411.02019).
   - **方法：**时域快支路按 2 ms 输出，慢支路低帧率看环境并调制 SSM transition；慢支路特征严格落后于当前快帧以保持因果。**SC**；无 future context。
   - **结果（VoiceBank+DEMAND，2 ms）：**single branch 126 M MAC/s，PESQ-NB/WB 3.25/2.59、STOI 93.14%、SI-SNR 17.79；SSMM SlowFast $\delta=3$ 39 M MAC/s，3.24/2.59、93.10%、17.86，约 70% MAC 降幅。单采样 62.5 µs 实验为 100 M MAC/s、PESQ-NB 3.12、SI-SNR 16.62。详见[方法与表 I](https://arxiv.org/html/2411.02019)。
   - **判断：**当前最贴合“2 ms + 低算力”的 SSM 路线；还缺端侧 p99、低于 0 dB 的保真分层和语音误抑制统计，正好构成硕士增量空间。

5. **On TasNet for Low-Latency Single-Speaker Speech Enhancement** — Morten Kolbæk, Zheng-Hua Tan, Søren Holdt Jensen, Jesper Jensen; *arXiv 2021*（有影响力预印本）,[paper](https://arxiv.org/abs/2103.14882).
   - **方法：**learned encoder/decoder + TCN；用 cLN 与 causal convolution 实现因果。**SC** 配置可取 2 ms window / 1 ms hop（本身 2 ms 前端），无 future context。
   - **结果：**单说话人、竞争说话人噪声 `wsjf`：causal TasNet STOI .95、PESQ 2.74、SI-SDR 12.4 dB；但非因果 cLN 为 .97/3.33/16.0，显示因果代价很大。2 ms/1 ms 在 `ssn` 非因果实验为 STOI .93、PESQ 2.60、SI-SDR 11.4。见[表 1–2](https://arxiv.org/html/2103.14882)。
   - **判断：**低 SNR/竞争说话人中未来上下文价值最高，也因此是 over-suppression 研究的好 baseline；原文没有完整的“2 ms + causal”同表结果，须自行复现实测。

6. **Ultra-Low Latency Speech Enhancement – A Comprehensive Study** — Haibin Wu, Sebastian Braun; *ICASSP 2025*, [DOI](https://doi.org/10.1109/ICASSP49660.2025.10889823).
   - **方法：**统一 CRUSE + causal deep filter，比对对称/非对称/可学习窗、FBE、future-frame prediction 和 Mamba。**LL/SC 取决于窗与实现；最小直接报告为 2.5 ms FBE、3 ms 窗。**
   - **结果：**同一 0.625 M CRUSE 中，20 ms：PESQ 2.22、STOI 84.45%、SI-SDR 10.52；3 ms：2.18/84.23%/9.65；2.5 ms FBE：1.89/81.73%/7.80。结论是小窗损失可通过模型变大部分补回，但实时 MAC/s 大幅上升；future prediction 在真实 DNS 测试上并无确定优势。[原始受控表](https://arxiv.org/html/2409.10358)
   - **判断：**不是成品模型，却是本课题最重要的设计依据：避免把“非对称窗”和“future prediction”当作无代价创新。

### 3.2 实用而非 2 ms 的重要参照

| 论文（题目 — 作者；年、出处、链接） | 输入/结构；因果和延迟 | 报告结果与课题意义 |
|---|---|---|
| **Dual-Signal Transformation LSTM Network for Real-Time Noise Suppression** — Nils L. Westhausen, Bernd T. Meyer; 2020, *Interspeech*, [DOI](https://doi.org/10.21437/Interspeech.2020-2631) | STFT magnitude LSTM + learned analysis/synthesis LSTM 两阶段，<1 M 参数；one-frame-in/out，**LL**，但默认帧/OLA 不等于 2 ms | DNS real-time 轨道、平均 MOS 比 baseline 高 .24。是易复现 hybrid baseline；必须重设 32/8 ms 一类默认前端才可讨论 2 ms。 |
| **DCCRN: Deep Complex Convolution Recurrent Network for Phase-Aware Speech Enhancement** — Yanxin Hu *et al.*; 2020, *Interspeech*, [DOI](https://doi.org/10.21437/Interspeech.2020-2537) | complex STFT 编解码 + complex LSTM + complex mask；3.7 M；**LL**，DNS 实时配置帧长 37.5 ms | DNS-2020 real-time track 第一、non-real-time 第二（MOS）。复杂相位建模有效，但原配置**不满足 2 ms**。 |
| **Causal Signal-Based DCCRN with Overlapped-Frame Prediction for Online Speech Enhancement** — Julitta Bartolewska, Stanisław Kacprzak, Konrad Kowalczyk; 2023, *Interspeech*, [DOI](https://doi.org/10.21437/Interspeech.2023-2177) | complex signal filtering、overlapped-frame prediction、causal conv/deconv 和修改损失；**LL** | 相比原 DCCRN 延迟和参数各降约 30%，指标相当或更好；很适合做因果 DCCRN 消融，但论文未证明 2 ms。 |
| **A Perceptually-Motivated Approach for Low-Complexity, Real-Time Enhancement of Fullband Speech (PercepNet)** — Jean-Marc Valin *et al.*; 2020, *Interspeech*, [paper](https://arxiv.org/abs/2008.04259) | ERB 频带、pitch filtering、envelope postfilter、8 M 权重 8-bit；**LL**，10 ms frame | VCTK 48k：PESQ-WB 2.54、P.808 MOS 4.05；DNS overall MOS 3.52；1.8 GHz mobile x86 约 5.2% 核。其“谐波+包络”是 preservation 设计的好老师，但不合 2 ms。 |
| **DeepFilterNet2: Towards Real-Time Speech Enhancement on Embedded Devices for Full-Band Audio** — Hendrik Schröter, Alberto N. Escalante-B., Tobias Rosenkranz, Andreas Maier; 2022, *IWAENC*, [paper](https://arxiv.org/abs/2205.05474)；相关 **DeepFilterNet** 2022 ICASSP [DOI](https://doi.org/10.1109/ICASSP43922.2022.9747055) | ERB gains（包络）+ 低频 complex deep filter（周期性）+ GRU；**低 look-ahead，非严格 2 ms**：48k, 20 ms window, 10 ms hop, 2-frame look-ahead=40 ms | DFN2 RTF .04（notebook i5）；DFN 系列 VoiceBank PESQ 2.81/3.08/3.17、STOI .942/.943/.944。对低 SNR voiced speech 的相位/周期恢复很强，但默认 look-ahead 明确违反题设。 |
| **DPCRN: Dual-Path Convolution Recurrent Network for Single Channel Speech Enhancement** — Xiaohuai Le, Hongsheng Chen, Kai Chen, Jing Lu; 2021, *Interspeech*, [paper](https://arxiv.org/abs/2107.05429) | complex STFT CRN + intra/inter DPRNN；0.8 M；**LL**，25 ms window/12.5 ms hop，总延迟 37.5 ms | DNS-2021 WB overall MOS 3.57。长上下文强，但不是 2 ms 候选。 |
| **Streaming Dual-Path Transformer for Speech Enhancement** — Soo Hyun Bae *et al.*; 2023, *Interspeech*, [DOI](https://doi.org/10.21437/Interspeech.2023-751) | causal time/frequency attention mask + cache；zero look-ahead，**SC 结构上**，帧前端/硬件仍需单列 | 报告优于实时 baselines；KV cache/attention 的内存与 deadline 不适合把它当默认端侧方案。 |
| **RT-SEMamba: Real-Time Speech Enhancement Mamba via Progressive Knowledge Distillation** — Rong Chao *et al.*; 2026, *arXiv*, [paper](https://arxiv.org/abs/2608.12099) | causal TF-Mamba，固定 recurrent state，8层教师→1层学生；**SC**，但 25 ms | VoiceBank: teacher PESQ 3.32（25 ms）；student PESQ 3.18，速度为 teacher 2.75×。表明 SSM 的内存优势真实，但不应声称解决 2 ms。 |

### 3.3 高分离/离线模型为什么不应成为本题 baseline

**TF-GridNet**（Luo, Hu, Takahashi, 2022，[arXiv](https://arxiv.org/abs/2209.03952)）和 **MossFormer**（Zhao *et al.*, 2023，[arXiv](https://arxiv.org/abs/2302.11824)）是高性能分离模型：后者在 WSJ0-3mix 报告 21.2 dB SI-SDRi。但它们的原始设置依赖双向/全局或 chunk attention，任务又常是分离而非低 SNR 增强；应列为**NC 上界/教师候选**，不能与 2 ms 因果系统比“谁更好”。类似地，流式 Mamba 工作常是 16–30 ms（例如 2026 CHiME causal Mamba 的 16 ms 更新），也只能作结构参照。

## 4. 为什么低延迟时“抑噪上升、语音失真也上升”

1. **观测不可辨识。** 负 SNR 的弱辅音、气声和瞬态能量与噪声重叠；没有未来元音、音节连续性与语音起始线索，条件估计会把不确定语音向“噪声/零”收缩。
2. **小窗损失频率分辨率。** 2 ms @16 kHz 仅 32 samples，低频 pitch 周期远大于窗长；谐波、formant 和相位难以判别。小 hop 也使相邻帧高度冗余，若每帧跑同一大网络，计算会随帧率上升。
3. **损失的错误激励。** SI-SNR/MSE 的平均最优并不等价于“弱语音永不丢失”；强 complex/相位项可换来较高 BAK（噪声更少）却降低 SIG（语音更失真）。Braun & Gamper 的分析证明 magnitude 项能起到失真正则化作用，complex 权重过大强化抑噪但增加 speech distortion。[ICASSP 2022](https://doi.org/10.1109/ICASSP43922.2022.9746489)
4. **mask 的硬压缩与估计偏差。** 低 SNR 时 mask 往 0 饱和；speech/noise 标签或仿真噪声域偏差会把 bias 持续作用到弱语音段。递归状态若不稳定，错误会跨帧累积。
5. **指标盲区。** PESQ/STOI/SI-SDR 可以上升，而音素缺失、F0/formant 断裂、说话人音色漂移和 ASR WER 变差。主观可懂度也不能被客观 intelligibility 指标完全替代。[证据](https://doi.org/10.1016/j.specom.2023.04.001)

### 4.1 可因果实现的 speech-preservation 工具箱

| 方法 | 核心思想 | 适合 causal streaming？ | 2 ms 的具体实现 |
|---|---|---|---|
| speech-aware 多任务损失 | 主增强头外预测 VAD/SPP/音素或 voiced 概率，语音 bin 权重更高 | **是** | 使用当前/过去特征的帧级 SPP；弱语音段加权，勿用双向 VAD |
| 复合波形+多分辨率谱/continuity loss | SI-SNR 保整体，MR-STFT/delta 谱保谐波连续和瞬态 | **是（训练时可非因果算 loss）** | 波形 SI-SNR + 16/32 ms 仅用于 loss 的谱项；推理不增延迟。continuity loss 已显示可减 over-suppression。[Interspeech 2022](https://doi.org/10.21437/Interspeech.2022-157) |
| perceptual/ASR feature loss | 冻结识别器/SSL 约束语音内容或 MOS proxy | **是（只在训练）** | 小权重；须验证它不只提升 proxy。强 spectral loss 常已难被它显著超越 |
| complex + magnitude 权衡 | magnitude 给失真正则，complex 改相位/抑噪 | **是** | 扫描 $\lambda_{complex}$，以 SIG/BAK Pareto 选点，而非只取 PESQ 最大 |
| mask/gain floor 与 attack-release | 限制最小增益、抑制变化率，保留不确定弱语音 | **是** | 每 ERB/band 的可学习 floor + SPP 调制；控制时域爆音 |
| uncertainty / posterior variance | 预测均值+方差；高不确定性时收缩抑制、mix/bypass | **是** | 异方差头或小 ensemble/MC dropout（后者算力高）；可与 SPP 共享头。已有神经不确定性建模证据：[paper](https://arxiv.org/abs/2305.08744) |
| adaptive suppression | 用 SPP、局部 SNR、voicing、瞬态检测决定强度 | **是** | 只依赖递归估计；与传统 soft decision 思路一致，适合稳定 noise floor |
| deep filtering / pitch-aware | 修复周期性和相位，而非把每 bin 独立置零 | **是（取 causal taps）** | 仅低频使用过去 multi-frame taps，限制 DF 订单以控制计算 |

**评价应拆分。** 每个 SNR/noise 条件至少报告：PESQ、STOI/eSTOI、SI-SDR；DNSMOS 的 SIG/BAK/OVL；ASR WER/CER；VAD false-suppression rate（clean speech 活跃帧被压低 >x dB 的比例）；voiced/unvoiced 分层的 F0、能量和连续性误差。低 SNR 请分 −10/−5/0/5 dB，而不是只报 pooled average。

## 5. 研究 gap 与可完成的微方向（不需要“大创新”）

| # | 一句话方向 | 现有不足 / 为什么可能有效 | 最小验证实验（MVE） | 风险 |
|---:|---|---|---|
| 1 | **2 ms causal TasNet/GRU 的 SPP 调制增益下限** | 2 ms 基线多只优化信号分数，低能辅音易被归零；SPP 让抑制强度显式依赖“语音存在置信度” | 在 2 ms causal baseline 加共享 SPP head + band gain floor；−10~5 dB/语音干扰分层，报 SIG/BAK 与 false-suppression | 低 |
| 2 | **语音连续性损失用于 2 ms streaming** | SI-SNR 偏全局平均，未约束音节边缘与谐波连续；MR-delta loss 训练时不增加推理延迟 | SI-SNR vs SI-SNR+MR-STFT vs +delta-spectrum；看 VAD miss、F0 continuity、PESQ/ASR | 低 |
| 3 | **保守不确定性门控，而非更强抑噪器** | OOD 噪声/负 SNR 时模型过度自信；variance 可驱动 soft mix 或最大衰减 | 单模型异方差输出，在低置信 bin 增大输出下限；测 OOD/真实噪声的 SIG–BAK Pareto | 中 |
| 4 | **SlowFast 2 ms 中的 speech-preservation 慢状态** | 已有 SlowFast 聚焦 MAC；慢分支可只输出“speech reliability/voicing”而非完整增强 | 复现简化 SlowFast，比较普通调制 vs SPP/voicing 调制；目标在同 MAC 下提高负 SNR SIG | 中 |
| 5 | **2 ms causal 深度滤波的低频小分支** | mask 对有声周期性不够；DFN 默认 40 ms 不能直接用 | 2 ms waveform/RI baseline 后加仅过去 2–3 帧、<4 kHz 的复滤波；对 voiced 段 PESQ/F0 | 中 |
| 6 | **延迟约束的蒸馏：NC teacher → SC 2 ms student** | 高分离模型可作教师但不能部署；仅 logit/波形蒸馏未针对“误杀语音” | 以 TF-GridNet/DFN/大因果模型为 teacher，学生蒸馏干净语音+SPP/中间 voiced 表征；严格隔离 teacher 的 future | 中 |
| 7 | **2 ms 因果审计与真实端侧 deadline benchmark** | 论文通常只报算法窗口/MAC，忽略 p99、DMA、缓存、状态 reset | 选一 baseline，导出 ONNX/TFLite/目标 runtime；逐层 sample-dependency 表、p50/p99、underrun、RAM | 低（若硬件可用） |
| 8 | **轻量双麦空间特征的置信度抑制** | 竞争说话人低 SNR 仅靠单麦很难；但全 beamformer/双耳链路可能超预算 | 在 2 ms RNN 加 IPD/ILD 或两麦 filter-and-sum，比较单麦/双麦和语音保真 | 中到高（需硬件/数据） |

不要优先做：大 Transformer、diffusion、完整双向 Mamba、把 DeepFilterNet 默认模型直接压成 2 ms。这些都会把“算法质量”与“延迟不合格”混在一起，1–2 月内也难给出可信结论。

## 6. 推荐的 1–2 月硕士最小课题

### 推荐题目

**“面向 2 ms 严格因果流式语音增强的置信度调制保守抑制：在低 SNR 下减少弱语音过抑制”**

这不是声称新范式；它把企业约束转为可验证问题：在**相同 2 ms latency、相近 MAC/s**下，能否提升负 SNR 的 speech-preservation，而不牺牲过多 BAK。

### 为什么选这些 baseline

- **主 baseline：**单通道 2 ms causal learned-filterbank + GRU（可用 causal Conv-TasNet 缩小版，或复现 Pandey 小窗 RNN 的单通道版本）。它真正满足前端约束，训练/推理结构易控。
- **效率对照：**SlowFast-SSM（或只复现其快慢调制思想）。它针对 2 ms 时“每秒十倍帧数”的真正痛点，且有固定状态，不强迫使用 Transformer。
- **上界/消融参照：**DFN2（低延迟但 40 ms）和 DTLN（易复现 hybrid）只用于解释质量缺口，不进入“2 ms 合格”排名。
- **不选 DCCRN/DPCRN 作为主线：**它们适合复杂谱和相位研究，但原始 25–40 ms 前端会吞掉项目周期。
- **不选 TF-GridNet/MossFormer 主线：**它们可作 teacher/上界，原始结构不满足 strict streaming。

### 最小方法

`noisy waveform → 2 ms learned encoder (hop 1 ms) → causal GRU/小 SSM → {mask/gain head, SPP+uncertainty head} → gain floor + attack/release → decoder`。

训练目标：

\[
\mathcal L=\mathcal L_{SI\text{-}SNR}+\lambda_1\mathcal L_{MR\text{-}STFT}+\lambda_2\mathcal L_{SPP}+\lambda_3\mathcal L_{continuity}.
\]

只有在 SPP/variance 较低时放宽增益下限；高置信无语音时才强抑制。所有 loss 可用较长参考窗计算，**不会**在部署时读取未来样本。先做 gain-floor+SPP（方向 1），再加 continuity（方向 2）；不必一次做 uncertainty、蒸馏和复杂 DF。

### 数据、指标、实验设计

- **训练：**DNS Challenge 公开 clean/noise on-the-fly mixing；先 16 kHz、单通道。将 SNR 均匀覆盖 −10, −5, 0, 5, 10 dB，额外提高 babble/competing speech、transient 的比例。
- **测试：**VoiceBank-DEMAND（可与文献对齐）+ DNS 盲测/真实子集（若可访问）+ 一个未见噪声集。每个集合按 SNR/noise type 分层；不要只交 VoiceBank 平均分。
- **主要指标：**SI-SDR/SI-SNR、PESQ、STOI/eSTOI、DNSMOS SIG/BAK/OVL；**preservation 指标**为 VAD false-suppression、ASR WER（可选）、F0 continuity/voiced energy ratio。
- **延迟与端侧：**记录 $W_a,W_s,H,A$、model state、参数、MAC/s、peak RAM、streaming batch=1 的 p50/p95/p99。端到端若没有硬件链路，诚实标为“算法 2 ms，端到端待测”，绝不等同。
- **消融：**(B0) baseline；(B1) +fixed floor；(B2) +SPP gate；(B3) +SPP+continuity；(B4) 同 MAC 的更大 baseline。报告 SIG–BAK Pareto，以证明收益不是单纯少抑噪。

### 8 周排程

| 周 | 产出与止损点 |
|---:|---|
| 1 | 完成 latency/dependency certificate；2 ms causal baseline 能逐 chunk 与整段一致 |
| 2 | DNS 小规模训练 + VoiceBank smoke test；若 p99 inference >1 ms，先缩模型/改 runtime |
| 3–4 | 完整 baseline 与 SNR/noise 分层；固定可复现脚本和 MAC/RAM 测试 |
| 5 | B1/B2（SPP+floor）消融；若 SIG 无增益，检查 SPP calibration 而非加大模型 |
| 6 | B3 continuity loss；做 ASR/F0/VAD-miss preservation 分析 |
| 7 | 可选 SlowFast 或 uncertainty 之一，不同时做两项 |
| 8 | 真实设备/长流压力测、错误案例、论文图表和结论 |

## 7. 交付前必须通过的 strict-causal checklist

- 输出样本 $\hat s[t]$ 的计算图只依赖 $x[\le t+2\text{ ms}]$；记录每一层的最后可读样本。
- STFT 未使用 centered window；conv/deconv 全部左 padding；normalization 不跨未来/整 chunk；attention/SSM cache 只保存过去。
- 分块流式输出与一次性因果运行数值一致（允许浮点误差）；重新起流、state reset、长流均测试。
- 分别报告算法 delay、模型 p99、I/O buffers、ADC/DAC；`RTF<1` 不能替代 deadline。
- 负 SNR 下同时给 SIG（保真）和 BAK（抑噪）。若 BAK 高而 SIG/VAD-miss 变坏，则是失败，不是“增强更强”。

## 8. 研究地图（用于答辩选题定位）

```text
                          企业合同：strict causal, ~2 ms, low SNR, edge
                                                    │
                    ┌─────────────── latency / causality certificate ────────────────┐
                    │                                                                  │
              前端与缓冲                                                        时序核心
   short learned FB / 2 ms OLA /                                      GRU/LSTM ── SSM/SlowFast
    asymmetric STFT（须审计）                                      (首选)        (效率候选)
                    │                                                                  │
                    └──────────────────── 2 ms causal baseline ──────────────────────┘
                                                    │
                        ┌──────── speech-preservation control ────────┐
                        │ SPP/uncertainty gate │ gain floor │ continuity loss │ DF │
                        └─────────────────────────────────────────────┘
                                                    │
               质量：−10~5dB 分层 SIG/BAK + PESQ/STOI/SI-SDR + VAD miss / ASR / F0
                                                    │
                   部署：MAC/s + SRAM + batch=1 p99 + long-stream / reset / underrun
```

**最可辩护的研究 gap：**现有工作分别证明了 2 ms、低 MAC、或高质量；尚少有公开、可复现的系统在同一严格因果 2 ms 配置下，把“负 SNR 弱语音误抑制”作为一等目标，并用 SIG–BAK、false-suppression 与端侧 deadline 共同验证。这个缺口足够小、可落地，也足够贴近企业需求。

## 参考文献（本报告的关键一手来源）

- Wu & Braun, ICASSP 2025: [Ultra-Low Latency Speech Enhancement](https://doi.org/10.1109/ICASSP49660.2025.10889823)
- Wang *et al.*, TASLP 2023: [STFT-Domain Neural Speech Enhancement with Very Low Algorithmic Latency](https://doi.org/10.1109/TASLP.2022.3224285)
- Wang *et al.*, ICASSP 2023: [FSB-LSTM](https://doi.org/10.1109/ICASSP49357.2023.10095700)
- Pandey, Tan & Xu, Interspeech 2023: [Simple RNN](https://doi.org/10.21437/Interspeech.2023-365)
- Cheng *et al.*, ICASSP 2025: [SlowFast SSM](https://arxiv.org/abs/2411.02019)
- Schröter *et al.*, ICASSP 2022: [DeepFilterNet](https://doi.org/10.1109/ICASSP43922.2022.9747055)
- Braun & Gamper, ICASSP 2022: [Effect of Noise Suppression Losses](https://doi.org/10.1109/ICASSP43922.2022.9746489)
- Bartolewska *et al.*, Interspeech 2023: [Causal signal-based DCCRN](https://doi.org/10.21437/Interspeech.2023-2177)
