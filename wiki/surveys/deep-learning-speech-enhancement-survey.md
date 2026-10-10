# 语音增强深度学习综述：从传统DSP到生成式模型（2017–2025）

---

## 摘要

语音增强（Speech Enhancement, SE）旨在从带噪语音信号中恢复干净的语音信号，是自动语音识别、助听器、远程通信和语音交互系统等众多下游任务的关键前端处理步骤。过去十年，该领域经历了从传统数字信号处理到深度学习驱动的深刻范式转变。本综述全面回顾了语音增强领域的最新研究进展，涵盖五大技术路线：传统统计信号处理方法、时频域深度学习方法、端到端时域方法、混合DSP-深度学习方法以及生成式模型方法。我们梳理了从SEGAN到Conv-TasNet、DPRNN、SepFormer、RNNoise、DeepFilterNet到扩散模型和Mamba等架构的演进脉络，分析了PESQ、STOI、SI-SNR等关键评估指标和代表性数据集，识别出包括相位感知处理、复杂噪声泛化、实时部署和生成失真控制在内的核心开放挑战。特别关注混合DSP-DL方法和生成式模型这两个正在快速发展的新兴方向。最后，我们总结了有前景的未来研究方向。

---

## 1. 引言

语音增强——从噪声背景中提取干净的语音信号——是音频信号处理中最基本的问题之一，其应用覆盖自动语音识别的前端处理、助听器降噪、远程通信回声消除、智能音箱语音唤醒以及移动设备的通话降噪等场景。传统上该问题通过统计信号处理方法解决，如谱减法、维纳滤波、MMSE估计器以及基于子空间的信号处理方法。

然而，深度学习的出现从根本上重塑了该领域。从2017年SEGAN首次将生成对抗网络引入语音增强开始，该领域经历了快速的技术演进：时频域掩蔽方法（2017–2020）、时域端到端方法（2019–2022）、Transformer与注意力架构（2021–2023）、混合DSP深度学习方法（2018–2024）以及生成式模型（2022–2025）。特别是混合方法（RNNoise、DeepFilterNet）在实时低功耗设备上的成功部署，以及扩散模型在语音生成质量上的突破，代表了当前两个最有前景的方向。

本综述覆盖2017–2025年的文献，重点关注核心架构演进。我们沿五条技术路线组织文献：

1. **传统DSP方法** — 谱减法、维纳滤波、MMSE估计
2. **时频域深度学习方法** — CNN、CRNN、复数网络、掩蔽方法
3. **端到端时域方法** — Conv-TasNet、DPRNN、Demucs、Wave-U-Net
4. **混合DSP-深度学习方法** — RNNoise、PercepNet、DeepFilterNet
5. **生成式模型** — 扩散模型、得分匹配、流匹配

---

## 2. 传统基础与深度学习的转向

### 2.1 传统语音增强方法

传统方法可归类如下：

| 方法类别 | 代表性技术 | 主要局限 |
|---------|-----------|---------|
| **谱减法** | 幅度谱减法、过减法 | 音乐噪声伪影；噪声估计非平稳场景失效 |
| **维纳滤波** | 最优线性滤波器 | 需要准确已知信号和噪声功率谱 |
| **MMSE估计** | Ephraim-Malah MMSE、log-MMSE | 高斯假设在大噪声下不成立 |
| **子空间方法** | KLT分解、信号子空间 | 有色噪声下性能退化 |

### 2.2 为何转向深度学习？

深度学习解决了传统方法的几个根本性局限：
- **非平稳噪声处理**：神经网络能够从大量数据中学习噪声模式，无需稳态假设
- **端到端优化**：直接优化感知质量指标（PESQ、STOI），而非中间统计量
- **上下文建模**：CNN和RNN能够利用时间和频率上的长程上下文信息
- **隐式相位估计**：时域方法可绕过STFT的幅度-相位解耦问题

然而，深度学习方法也引入了新的挑战：对大规模标注数据的高度依赖、对未见噪声条件泛化能力有限、较高的计算成本以及模型黑箱的可解释性问题。

---

## 3. 深度学习语音增强：时频域方法

### 3.1 问题建模

语音增强在时频域中通常基于短时傅里叶变换（STFT）进行建模。给定带噪语音的STFT表示 (t,f) = X(t,f) + N(t,f)$，目标是在每个时频点估计一个掩蔽（Mask）(t,f)$，使得增强后的语音 $\hat{X}(t,f) = M(t,f) \cdot Y(t,f)$。

常用的训练目标包括：
- **理想比例掩蔽（IRM）**：{\text{IRM}}(t,f) = \frac{|X(t,f)|}{|Y(t,f)|}$
- **复数理想比例掩蔽（cIRM）**：同时调整幅度和相位
- **频谱幅度映射（Spectral Mapping）**：直接预测 $|X(t,f)|$ 或复数频谱

### 3.2 卷积与循环架构

早期的深度学习方法采用全连接网络处理帧级特征。2017年的SEGAN首次将生成对抗网络用于语音增强，其生成器采用编码器-解码器结构处理波形切片。之后，卷积神经网络（CNN）和循环神经网络（RNN/LSTM/GRU）的组合——即CRNN架构——成为时频域方法的标准构建模块 [FullSubNet: A Full-Band and Sub-Band Fusion Model, 2021]。

**FullSubNet** (2021) 提出了全带-子带融合机制：全带分支捕获全局频谱结构，子带分支在窄频率区域进行精细处理。这种方法在DNS Challenge上取得了领先性能。

**A Time-Frequency Attention Module for Neural Speech Enhancement** (2023) 在CRNN框架中引入可学习的时频注意力机制，使网络能够自适应地关注重要的时频区域。这种注意力机制的引入显著提升了对非平稳噪声的抑制能力。

**MetricGAN+** (2021) 提出了受指标驱动的生成对抗训练，使用可微分的指标网络（Metric Mentor）替代传统的判别器，直接优化PESQ等感知指标而非信号级距离。该方法首次将目标评估指标直接融入训练过程。

### 3.3 复数域方法

一个关键洞察是：STFT表示本质上是复数值，但大多数网络只处理幅度谱，丢弃了相位信息。

**PHASEN** (2020) 提出了一种双流架构来解决这个问题：幅度流和相位流分别处理频谱幅度和相位，并通过频率-时间关注块在两者间交换信息。实验证明，相位信息的显式建模显著提升了对语音谐波结构的保持能力。

更根本的解决方案来自**复数域神经网络**。**DCCRN** (2020) 首次将复数卷积循环网络引入语音增强，使网络能够在统一的复数表示中处理幅度和相位。复数卷积定义为  \ast Z = (A \ast x - B \ast y) + i(A \ast y + B \ast x)$，其中  = A+iB$ 和  = x+iy$ 分别为复数的卷积核和输入。这种操作保留了实部与虚部之间的结构性关系，而非在拼接或解耦后丢失信息。

### 3.4 感知驱动与Conformer方法

**CMGAN** (2022) 将Conformer块（结合卷积模块和多头自注意力）与Metric GAN训练相结合。Conformer架构同时提供局部特征提取（卷积）和全局上下文建模（自注意力）能力，显著提升了增强语音的自然度。

**MP-SENet** (2023) 提出了并行去噪的多路径架构，通过不同感受野的并行子网络处理频谱的不同尺度的信息后融合，兼顾了谐波结构保持和噪声抑制。

---

## 4. 端到端时域方法

### 4.1 从频谱到时域的跨越

时频域方法存在一个根本性限制：STFT固化了时频分辨率的折中关系（海森伯不确定性），且将幅度和相位解耦——即使幅度估计完美，也因相位失配导致重建质量有理论上限。时域方法直接在原始波形上操作，绕过了这些限制。

### 4.2 Conv-TasNet与里程碑突破

**Conv-TasNet** (2019) 证明了纯时域架构能够超越理想时频幅度掩蔽——这是一个里程碑式的发现。其核心设计是**可学习编码器-分离-解码器**框架：编码器将波形映射到高维特征空间，TCN分离模块应用时域掩蔽，解码器重建波形。

TCN（时域卷积网络）通过指数递增的膨胀因子实现大感受野： = 1, 2, 4, 8, \ldots, 2^{R-1}$，使得深层网络能覆盖数秒的上下文窗口。实验表明，在WSJ0-2mix语音分离任务上，Conv-TasNet以少量参数超越了所有之前的时频域方法。

### 4.3 Dual-Path RNN

**DPRNN** (2020) 针对Conv-TasNet感受野固定、长程依赖建模不足的问题，提出了**双路径处理**机制：将输入序列分割为重叠块（chunks），**块内RNN**（Intra-chunk RNN）建模局部细节，**块间RNN**（Inter-chunk RNN）捕获全局依赖。这种简单而巧妙的策略用更少的参数（约2.6M）实现了更强的性能。

DPRNN的设计思想——对3D张量沿两个轴分别建模——后来被广泛应用于SELD（DST、CST-Former）、语音合成等众多音频任务中。

### 4.4 其他时域架构

**Wave-U-Net** (2018) 将医学图像分割中的U-Net架构引入音频，通过跳跃连接保留多尺度信息。**Demucs** (2019) 将其扩展到音乐源分离，并提出了时域-时频域混合架构。**Real Time Speech Enhancement in the Waveform Domain** (2020) 则专门针对实时增强场景对Conv-TasNet进行了优化。

### 4.5 时域方法的局限性

尽管取得了令人瞩目的成果，时域方法仍面临挑战：可学习的编码器基函数缺乏STFT的物理可解释性；通常需要比时频域方法更多的训练数据；缺乏显式相位约束可能导致感知上不自然的伪影；且序列操作（RNN、TCN）在超长序列上推理速度受限。

---

## 5. Transformer与注意力架构

### 5.1 Transformer进入语音增强

**SepFormer** (2021) 证明了纯Transformer架构能够在语音分离任务上匹配甚至超越基于RNN的方法。其设计沿用了DPRNN的双路径思想：将输入分割为块后，每个Transformer块分别在时间维和块维上执行自注意力。多头自注意力使得SepFormer能够对序列中任意两个位置进行直接建模，不受RNN梯度消失的限制。

### 5.2 MossFormer与可扩展Transformer

**MossFormer** (2022) 进一步改进了SepFormer，引入了门控注意力机制并减小了二次复杂度。通过精心设计的线性注意力变体，MossFormer在保持长程建模能力的同时显著降低了计算开销，在WSJ0-2mix和LibriMix基准上达到了当时的最高水平。

### 5.3 注意力机制与CRNN的融合

除了纯Transformer架构，注意力机制也被广泛集成到CRNN框架中。**A Time-Frequency Attention Module for Neural Speech Enhancement** (2023) 在CRNN的每个时间步上加入了频谱注意力权重，**CMGAN** (2022) 则用Conformer块替代了传统LSTM层。这种融合设计代表了当前的主流趋势：既有卷积的局部提取效率，又有注意力的全局建模能力。

---

## 6. 混合DSP-深度学习架构

### 6.1 混合方法的设计哲学

混合DSP-深度学习方法代表了与纯端到端方法截然不同的范式：**用神经网络替代传统信号处理管线中难以手工调参的估计模块，保留经过数十年验证的DSP处理链**。这种设计的核心优势是：（1）极低的计算开销（~0.1 GFLOP/s）；（2）低延迟（5-10ms）；（3）模型规模小（<1M参数）；（4）行为可预测、可调试。

### 6.2 RNNoise

**RNNoise** (2018) 是该方向的奠基性工作，由Mozilla的Jean-Marc Valin提出。其核心思想是只使用深度学习替代传统噪声抑制中的三个估计器——语音活动检测（VAD）、噪声功率谱密度（PSD）估计和增益计算——而保持DSP处理链（窗函数、FFT、Bark尺度变换、感知权重、增益应用）不变。

RNNoise每帧只使用42个手工特征（Bark尺度26频带能量、频谱平坦度、音调相关性等），通过一个单层GRU（96隐节点，约96,000参数）处理后输出增益。这样的极轻量级设计即使在树莓派等低功耗设备上也能实现实时处理。值得强调的是，RNNoise经过适当再训练后，在多项测试中的性能可与比其大两到三个数量级的纯深度模型相媲美 [RNNoise: Hybrid DSP/Deep Learning Approach to Real-Time Full-Band Speech Enhancement, 2018]。

### 6.3 PercepNet

**PercepNet** (2020) 将混合哲学推向了感知驱动的方向。其核心设计包括：在Bark刻度滤波器组上操作、对每个临界频带独立预测增益、使用感知加权的损失函数（$\gammahBc指数加权MSE）。PercepNet的参数量仅为~500K，在DNS Challenge 2020上取得了极具竞争力的PESQ分数。

### 6.4 DeepFilterNet

**DeepFilterNet** (2023) 代表了混合方法的最新进展，引入了一个关键创新：**深度滤波**——网络不再预测标量增益，而是预测时变线性滤波器的系数。DeepFilterNet在多个STFT频带上的预测复数滤波器系数比单纯的增益更灵活，能够对特定频率成分进行精确的相位和幅度调整。在极低计算量（<1 GFLOP/s）下，DeepFilterNet实现了与大规模模型（如CMGAN）可比的性能。

### 6.5 混合方法的优势总结

| 指标 | 混合方法 | 纯深度端到端方法 |
|------|---------|----------------|
| **参数量** | 0.1–1M | 5–100M |
| **计算量** | <1 GFLOP/s | 10–100 GFLOP/s |
| **延迟** | 5–10ms (实时) | 10–100ms |
| **能耗** | ~10mW | 100mW–10W |
| **可解释性** | 可追溯到DSP组件 | 黑箱 |
| **泛化性** | 依赖手工特征设计 | 端到端学到的特征 |

---

## 7. 生成式模型

### 7.1 扩散模型的基本原理

扩散概率模型是一类强大的生成模型，其核心思想是定义一个**前向过程**将干净语音逐步变为纯噪声，然后学习**反向过程**去噪恢复干净语音。前向过程由随机微分方程（SDE）描述：

171714dx = -\frac{1}{2}\beta(t)x\,dt + \sqrt{\beta(t)}\,dw171714

其中 $\beta(t)$ 是噪声调度，$ 是维纳过程。反向过程通过**得分匹配**（Score Matching）学习——估计对数概率密度的梯度。

对于语音增强，扩散过程以带噪语音为条件进行建模：模型学习 (x_t | y, t)$——给定带噪观测 $，在第 $ 扩散步的干净语音分布。

### 7.2 基于得分的语音增强

**SGMSE** (2022) 及其扩展版本SGMSE+首次将基于得分的扩散模型引入语音增强，证明通过迭代精炼生成干净语音可以在困难噪声条件下超越判别式方法。**Investigating the Design Space of Diffusion Models for Speech Enhancement** (2023) 对预条件（preconditioning）、训练损失加权、SDE类型和采样随机性等设计空间进行了系统分析，发现合理选择的预条件策略和SDE能够在保持质量的同时将采样步数从50-100步减少到约25步。

**Conditional Diffusion Probabilistic Model for Speech Enhancement** (2022) 展示了条件扩散模型在SE中的应用。**Audio-Visual Speech Enhancement with Score-Based Generative Models** (2023) 进一步将扩散模型扩展到视听场景。

### 7.3 流匹配与快速采样

扩散模型的主要限制是迭代采样的高计算成本（通常需要50-100次网络评估）。**流匹配（Flow Matching）** 通过学习噪声和数据分布之间的**确定性**映射，在保持生成质量的前提下将所需步数大幅减少。近期的工作（DiT-Flow, Geneses, 2025–2026）表明，基于潜在空间的流匹配模型能够将采样步数减少到10步以下而不损失质量。

### 7.4 生成式方法的优势与局限

| 维度 | 生成式方法 | 判别式方法 |
|------|-----------|-----------|
| **自然度** | 高（生成式先验保持语音流形） | 中（可能过度平滑） |
| **噪声泛化** | 强（分布外噪声也可处理） | 弱（依赖训练数据分布） |
| **计算开销** | 极高（50-100次NFE） | 低（单次前馈） |
| **幻觉风险** | 存在（可能生成不存在的成分） | 低 |
| **实时可行性** | ❌ 目前不可行 | ✅ 可实时 |

---

## 8. 评估指标与数据集

### 8.1 客观评估指标

| 指标 | 范围 | 测量什么 | 常用场景 |
|------|------|---------|---------|
| **PESQ** | -0.5 ~ 4.5 | 感知语音质量 | 标准SE基准 |
| **STOI** | 0 ~ 1 | 语音可懂度 | 噪声条件下的SE |
| **SI-SNR (dB)** | 无上界 | 信号失真 | 时域方法训练目标 |
| **DNSMOS** | 1 ~ 5 | 盲质量评估（无参考） | DNS Challenge |
| **MOS** | 1 ~ 5 | 主观听感质量 | 感知评估 |

### 8.2 主要数据集

| 数据集 | 年份 | 描述 | 典型用途 |
|--------|------|------|---------|
| **Voice Bank + DEMAND** | 2017 | 56说话人+多类噪声 | 标准SE基准（28dB SI-SNR） |
| **DNS Challenge** | 2020–2024 | 微软大规模SE竞赛 | 真实场景评测 |
| **WSJ0-2mix** | 2018 | 2说话人混合（语音分离） | Conv-TasNet等标准 |
| **LibriMix** | 2020 | LibriSpeech+Freesound混合 | 可扩展分离基准 |
| **VCTK + DEMAND** | 2017 | 110说话人+DEMAND噪声 | T-F域方法评测 |

---

## 9. 开放挑战与未来方向

### 9.1 已识别的研究空白

#### 挑战一：复杂噪声环境泛化
当前最先进的模型在匹配的训练-测试条件下表现良好，但在**未见噪声类型**或**动态信噪比**条件下性能急剧下降。领域对抗训练和测试时自适应是部分解决方案，但在根本上缺乏对泛化机制的深入理解。

#### 挑战二：生成式模型的实用化
扩散模型和流匹配模型在语音质量上已达到或超越判别式方法，但其**50-100倍的采样成本**严重限制了实际部署。加速采样（知识蒸馏、一致性模型、潜空间扩散）仍是一个开放问题。

#### 挑战三：非加性失真处理
实际语音中不仅是加性噪声，还包括**混响、削波、编解码失真**等多种非加性损伤。如何在一个统一框架中同时处理这些不同类型的失真是一个重要但研究不足的问题。

#### 挑战四：相位感知与复数处理
尽管DCCRN等复数网络已取得显著进展，但相位信息的建模仍远未成熟。如何在复数域中有效利用结构信息、避免复数梯度传播的不稳定性以及设计适用于复数域的规范化方法仍需进一步探索。

#### 挑战五：轻量化与实时部署
在计算资源受限的助听器、蓝牙耳机和移动设备上部署高性能SE系统仍面临巨大挑战。混合DSP-DL方法（如DeepFilterNet）已展示出潜力，但**精度-效率帕累托前沿**仍需进一步推进。

#### 挑战六：目标说话人提取
从多人混合中提取目标说话人——结合说话人嵌入的身份信息——与传统SE不同，需要跨模态（声纹嵌入+带噪语音）的融合策略。这一任务在智能助理和听力设备中具有重要应用价值。

#### 挑战七：语言模型与离散编码
[SELM: Speech Enhancement using Discrete Tokens and Language Models, 2023] 展示了将语音增强转化为离散token序列预测的范式可行性。这种方法可以利用大语言模型的先验知识，但其实时性和频谱保真度仍是关键限制。

### 9.2 有前景的研究方向

| 方向 | 理由 | 难度 |
|------|------|------|
| **混合DSP-DL的自动化设计** | 用神经架构搜索或强化学习自动化手工特征和DSP模块选择 | ⭐⭐⭐ |
| **高效生成式模型** | 一致性模型、潜空间扩散——在保持生成质量的同时大幅降低采样成本 | ⭐⭐⭐⭐ |
| **统一退化处理框架** | 同时处理噪声+混响+削波+编解码失真的单一模型 | ⭐⭐⭐ |
| **复数基础模型** | 在大规模复值频谱数据上预训练的复数神经网络基础模型 | ⭐⭐⭐⭐ |
| **自监督预训练用于SE** | 利用无标签数据预训练SE模型，类比w2v-SELD在定位领域的成功 | ⭐⭐ |
| **物理信息约束的SE** | 将声传播物理模型作为归纳偏置嵌入网络 | ⭐⭐⭐ |
| **语言模型引导的语音增强** | 利用语义先验（ASR输出、语言模型）指导增强过程 | ⭐⭐⭐ |

---

## 10. 结论

语音增强领域已被深度学习深刻改变，从传统统计方法发展到包括时频域深度学习、端到端时域方法、混合DSP-DL架构和生成式模型的多元化技术生态。Conv-TasNet证明时域方法可超越理想掩蔽上限；DPRNN的双路径处理成为跨任务的设计范式；RNNoise和DeepFilterNet开创的混合方法在实时部署中展现出不可替代的优势；扩散模型则在生成质量上打开了新的性能空间。

然而关键缺口依然存在。复杂噪声泛化、生成式模型的实用化、非加性失真统一处理以及轻量化部署仍是需要重大突破的活跃领域。对于进入这一领域的研究者，混合DSP-DL方法的自动化设计、高效生成式模型和自监督预训练是当前最具研究价值的方向。

我们希望本综述既能作为当前技术水平的全面参考，也能作为基于深度学习的语音增强未来研究的路线图。

---

## 参考文献

1. "SEGAN: Speech Enhancement Generative Adversarial Network." *Interspeech*, 2017.
2. "RNNoise: Hybrid DSP/Deep Learning Approach to Real-Time Full-Band Speech Enhancement." *IEEE/ACM TASLP*, 2018.
3. "Wave-U-Net: A Multi-Scale Neural Network for End-to-End Audio Source Separation." *ISMIR*, 2018.
4. "Conv-TasNet: Surpassing Ideal Time-Frequency Magnitude Masking for Speech Separation." *IEEE/ACM TASLP*, 2019.
5. "Demucs: Music Source Separation in the Waveform Domain." arXiv:1909.09559, 2019.
6. "PHASEN: A Phase-and-Harmonics-Aware Speech Enhancement Network." *AAAI*, 2020.
7. "DCCRN: Deep Complex Convolution Recurrent Network for Phase-Aware Speech Enhancement." *Interspeech*, 2020.
8. "PercepNet: A Perceptually-Motivated Approach for Low-Complexity Real-Time Enhancement." *ICASSP*, 2020.
9. "DPRNN: Dual-Path RNN Efficient Long Sequence Modeling for Time-Domain Speech Separation." *ICASSP*, 2020.
10. "Real Time Speech Enhancement in the Waveform Domain." *Interspeech*, 2020.
11. "FullSubNet: A Full-Band and Sub-Band Fusion Model for Real Time Speech Enhancement." *ICASSP*, 2021.
12. "MetricGAN+: An Improved Version of MetricGAN for Speech Enhancement." *ICASSP*, 2021.
13. "SepFormer: Attention Is All You Need in Speech Separation." *ICASSP*, 2021.
14. "Conditional Diffusion Probabilistic Model for Speech Enhancement." *ICASSP*, 2022.
15. "CMGAN: Conformer-based Metric GAN for Speech Enhancement." *IEEE/ACM TASLP*, 2022.
16. "MossFormer: Pushing the Performance Limit Beyond." arXiv:2210.07399, 2022.
17. "SGMSE: Score-Based Generative Speech Enhancement." *ITG Conference*, 2022.
18. "A Time-Frequency Attention Module for Neural Speech Enhancement." *IEEE/ACM TASLP*, 2023.
19. "DeepFilterNet: Perceptually Motivated Real-Time Speech Enhancement." *ICASSP*, 2023.
20. "Investigating the Design Space of Diffusion Models for Speech Enhancement." *IEEE/ACM TASLP*, 2023.
21. "MP-SENet: A Speech Enhancement Model with Parallel Denoising." *Interspeech*, 2023.
22. "Audio-Visual Speech Enhancement with Score-Based Generative Models." *ITG Conference*, 2023.
23. "SELM: Speech Enhancement using Discrete Tokens and Language Models." *ICASSP*, 2023.
24. "An Investigation of Incorporating Mamba For Speech Enhancement." arXiv:2405.06573, 2024.

---

> **综述生成日期：2026-07-06** · 覆盖2017–2025年文献 · 语音增强、深度学习、阵列信号处理
