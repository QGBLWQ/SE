---
title: "U-PAST：相位感知的复数谱 Transformer-U-Net（单通道语音增强）"
type: source
created: 2026-09-08
updated: 2026-09-08
tags:
  - speech-enhancement
  - single-channel
  - complex-spectrogram
  - transformer
  - phase-aware
  - u-net
source_type: paper
year: 2026
authors: Cao Duong Ly, Jörn Anemüller
affiliation: Department of Medical Physics and Acoustics, Carl von Ossietzky University Oldenburg, Oldenburg, Germany
venue: arXiv preprint（未注明接收会议）
arxiv: "2609.00431"
url: "https://arxiv.org/abs/2609.00431"
related:
  - "[[TF-GridNet 2023]]"
  - "[[DCCRN 2020]]"
  - "[[PHASEN 2020]]"
  - "[[CMGAN 2022]]"
  - "[[MP-SENet 2023]]"
  - "[[STFT与频谱图]]"
  - "[[语音增强评价指标]]"
  - "[[Conformer]]"
  - "[[2026 语音增强前沿五篇比较]]"
---

```yaml
- 论文: [U-PAST](2026)
  ├── 要解决什么问题: CNN 只能靠逐层卷积/池化间接捕捉长程时频依赖，单通道增强缺全局 T-F 上下文与显式相位重建
  ├── 核心方法: 幅相复数谱 patch tokenization + ViT 编码器(全局 self-attention) + 复数 U-Net 解码器直接重建幅度+相位，iSTFT 还原
  ├── 属于哪个分支: 语音增强 / 单通道 / 复数谱幅相(相位感知) / Transformer+U-Net 混合
  ├── 输入/输出: 16kHz 带噪 STFT → log-magnitude+phase (2×256×256) → 增强幅度+相位 → iSTFT 波形
  ├── 关键trick: Transformer 聚合全局时频上下文，复数解码器显式重建幅相(不复用带噪相位)——reverb 失配鲁棒的关键
  ├── 数据集: DNS2020(100h 训练) + 四条件评测:DNS non-reverb(匹配)、DNS reverb(声学失配)、VoiceBank-DEMAND、LibriMix(数据集失配)
  ├── 对比了谁: TF-GridNet、MP-SENet、CleanUNet、CUNet-S/B(自建复数 U-Net 基线)
  ├── 性能上限: SI-SDR 9.76 dB(reverb 全表第一);其余 15.69/16.72/10.30 dB,落后 TF-GridNet 1.62–2.44 dB;matched PESQ-wb 3.41 全表最高
  ├── 参数量: S/B/L/H = 1.17/1.51/1.96/2.40M;MAC 4.39–4.71 G;A100 RTF 0.0126–0.0151
  ├── 消融关键发现: 无经典逐组件消融;最关键证据=reverb 下仅 U-PAST 优于未处理输入(9.76 vs 9.03),CUNet/MP-SENet/TF-GridNet/CleanUNet 全部低于未处理;编码器深度 S→H 在 3/4 条件近单调增益
  ├── 遗留问题(你的机会): 无官方代码/复现缺口;"复数"只在解码器、编码器是实值 ViT;非因果不能实时;结论应限定 reverb SI-SDR 领先
  └── 跟哪篇像: [[DCCRN 2020]](复数块)、[[TF-GridNet 2023]](竞品)、[[MP-SENet 2023]](幅相并行)、[[CMGAN 2022]](transformer 混合)
```

# U-PAST: A Phase-Aware Audio Spectrogram Transformer-U-Net for Single-Channel Speech Enhancement

> Cao Duong Ly, Jörn Anemüller（Carl von Ossietzky 大学 Oldenburg，医学物理与声学系）。arXiv:2609.00431v1，2026-08-31 首次提交，预印本（未注明接收会议）。[官网摘要](https://arxiv.org/abs/2609.00431)｜[HTML 全文](https://arxiv.org/html/2609.00431)｜[PDF](https://arxiv.org/pdf/2609.00431)｜本地 HTML/PDF 见 [[outputs/reports/2026-09-08-frontier/enhancement/2609.00431_U-PAST.pdf]]。截至本笔记日期无官方代码、权重或训练命令。

## 1. 动机：他们为什么这么做？（motivation）

单通道增强没有空间信息可借，稳健的重建必须同时建模语音与噪声的谱结构与时间上下文。作者指出现有 CNN 路线只能「通过连续的卷积与池化**间接**捕捉长程时频依赖」；Transformer 类（DPT-FSNet、TSTNN）虽时序建模与可解释性强，但 DPT-FSNet 依赖子带处理、计算开销高。另一方面，[14] 曾把时/频两维堆成图像喂给 ViT 做增强，但它只预测 clean/noise mask 且 **复用带噪输入相位**——作者认为相位对感知质量至关重要，复用带噪相位直接封死了增强质量上限。

U-PAST 的切入点：把复数 STFT 明确 token 化、用 self-attention 建模全局谱-时模式（AST 思想），再配一个**复数 U-Net 解码器**重建**幅度与相位两者**，而不是回到带噪相位。

## 2. 前人局限：之前的人怎么做不了？（limitation → gap）

- **幅度谱/掩蔽路线**（掩蔽、幅度谱估计）：输出只预测幅度 mask，相位要么用带噪相位、要么靠 Griffin-Lim 一类估计，重建相位缺失。
- **纯时域路线**（CleanUNet 等）：不显式建模 STFT 的幅度-相位结构，参数往往更大。
- **Transformer-only 路线**（[14] 的 ViT 增强）：无卷积解码器、无分层上采样与 skip connection，且不处理相位，只复用带噪相位 iSTFT。
- **已有复数网络**（DCCRN/复数 U-Net 一脉）：处理复数谱，但仍是卷积/循环骨干，长程（全局 T-F）依赖仍靠堆叠卷积间接建立。

作者认为至今没解决的 gap 是：**在复数谱域，用 token-level 全局 self-attention 建模长程 T-F 依赖、同时用复数卷积解码器做相位感知的分层重建**。这一组合此前未被系统做过（作者自述为「首个混合 transformer-U-Net 且首个在复数域工作」）。

## 3. 核心 Trick：这个做法关键在哪？

每条按重要性分级（⭐ 越多越关键）。

- ⭐⭐⭐ **复数域的 hybrid Transformer→U-Net 组合**。编码器用 AST/ViT 结构把输入写成 token 序列、靠 self-attention 让每个 token 与其余全部交互，捕获全局谱-时模式；解码器是**复数卷积 U-Net**，带分层上采样与横向 skip connection，直接回归增强的幅度+相位（不是 mask，也不是复用带噪相位）。这是全文立意的核心。
- ⭐⭐ **复数解码器块**：`2×2` 转置卷积 + 两个 `3×3` 复数卷积块（含残差），每块接 CPReLU（complex parametric ReLU）、复数 BatchNorm、dropout 0.2；预测头是 `1×1` 复数卷积、输出通道 2（幅度、相位）。实部/虚部交叉耦合使相位误差能进入重建路径。
- ⭐ **幅相两通道 patch tokenization + 2D-sinusoidal 位置编码**：输入特征图 `2×256×256`（C=2 为 log-magnitude 与 phase），patch `16×16`（非重叠）→ `N=256` 个 token，hidden dim `D=96`、3 头。
- ⭐ **复合损失**（借用既有组件，非原创）：波形 L1 + multi-resolution STFT + SI-SDR，权重 `(λ1,λ2,λ3)=(1.0,1.0,0.05)`。
- ⭐ **编码器深度 scaling 研究**：S/B/L/H = 1/4/8/12 层，作为「复杂度-性能折中」的实验主轴。

### 关键公式（已核对原文）

**复数卷积 / 反卷积的实虚部耦合形式**（这是复数网络 [DCCRN / Trabelsi et al. 一脉] 的标准定义；原文 §3.2 未逐式写出，仅表述为「采用 complex-valued convolutional blocks [24]，后接 CPReLU [27]、复数 BN、dropout 0.2」，公式为从 [24] 复用的约定形式）：

$$\mathcal{C}(Z;W)=(W_r*Z_r-W_i*Z_i)+j(W_r*Z_i+W_i*Z_r).$$

其中 $Z_r,Z_i$ 为输入实、虚部，$W_r,W_i$ 为复权重实、虚部，$*$ 为卷积；反卷积同形。这使实虚部交叉耦合，区别于分别对两张实值谱各自卷积。

**训练目标**（原文 Eq. 2–7）：

$$\mathcal{L}=\lambda_1\mathcal{L}_{Wave}+\lambda_2\mathcal{L}_{MR\text{-}STFT}+\lambda_3\mathcal{L}_{SI\text{-}SDR},\qquad(\lambda_1,\lambda_2,\lambda_3)=(1.0,1.0,0.05).$$

其中 $\mathcal{L}_{Wave}=\lVert\hat{y}-y\rVert_1$，$y,\hat y$ 为目标/估计波形；$\mathcal{L}_{MR\text{-}STFT}=\mathcal{L}_{SC}+\mathcal{L}_{Mag}$，谱收敛项与对数幅度项分别为

$$\mathcal{L}_{SC}=\frac{\lambda_{sc}}{M}\sum_{m=1}^{M}\frac{\lVert\hat Y^{(m)}_{Mag}-Y^{(m)}_{Mag}\rVert_F}{\lVert Y^{(m)}_{Mag}\rVert_F},\qquad
\mathcal{L}_{Mag}=\frac{\lambda_{mag}}{M}\sum_{m=1}^{M}\frac{1}{T_mF_m}\sum_{t,f}\left|\log Y^{(m)}_{Mag}(t,f)-\log\hat Y^{(m)}_{Mag}(t,f)\right|,$$

且 $\mathcal{L}_{SI\text{-}SDR}=-\operatorname{SI\text{-}SDR}(\hat y,y)$（负号使最小化损失对应提高 SI-SDR）。$M=3$ 个 STFT 分辨率的 FFT/hop/window 分别为 512/50/240、1024/120/600、2048/240/1200，$T_m,F_m$ 为该分辨率的时间帧数与频率点数，$\lambda_{sc}=\lambda_{mag}=0.5$，$\lVert\cdot\rVert_F$ 为 Frobenius 范数。

**tokenization**（原文 §3.1 / Algorithm 1）：$X\in\mathbb{R}^{C\times F\times T}$ 按 patch $(P_f,P_t)$ 切分，$z_i=\mathrm{Flatten}(p)E+E_{pos}[i,:]$，$E\in\mathbb{R}^{(C P_f P_t)\times D}$ 可学习投影，$E_{pos}$ 为 2D-sinusoidal 位置编码（注意：§3.1 的算法用的是 **2D-sinusoidal** 位置编码，而 §2.1 回顾 AST 时提到的是 learnable 位置编码，二者不同，以 §3.1 为准）。

## 4. 实验里哪个消融最关键？（含关键结论边界）

**实验配置**：16 kHz；输入段 25,500 samples；STFT 窗 400 / hop 100 / FFT 512（去 DC 后 `2×256×256`）。训练用 100 h DNS 干净语音 + 噪声（SNR 0–20 dB 均匀采样），1 h 留作验证；Adam 初始 LR 0.001，cosine + 100 步线性 warmup，500 epoch。测试设四种「未见过」条件：匹配（DNS non-reverb，SNR 0–15）、声学失配（同数据加混响）、两个数据集失配（VoiceBank-DEMAND 与 LibriMix 的 s1+WHAM! 噪声）。

**主结果简表（按比较对象分别引用，勿跨对象混淆）**：

| 条件 | U-PAST-H SI-SDR | 最强对象及数值 | 可支持的结论 |
|---|---:|---:|---|
| DNS non-reverb（Table 3） | 15.6853 dB | TF-GridNet 18.1282 dB | H 落后 TF-GridNet **2.44 dB**；但其 PESQ-wb 3.4076 为该表最高（次高 TF-GridNet 2.8915） |
| DNS reverb（Table 4） | **9.7649 dB（全表最高）** | TF-GridNet 7.4466 dB | 唯一越过的失配条件；DNSMOS 子项仍由 TF-GridNet 领先 |
| VoiceBank-DEMAND（Table 5） | 16.7224 dB | TF-GridNet 18.3441 dB | 落后 **1.62 dB**；对 CUNet-B（17.0499）落后 0.33 dB |
| LibriMix（Table 6） | 10.2973 dB | TF-GridNet 12.0273 dB | 落后 **1.73 dB**；对 MP-SENet（10.5615）落后 **0.26 dB** |

**最关键的「消融」不是逐组件移除，而是两组对比折射同一结论——Transformer 编码器是失配鲁棒性的来源：**

1. **编码器背骨对比（transformer vs 卷积）**：CUNet-S/CUNet-B 与 U-PAST **共享同一复数解码器**，仅把 transformer 编码器换成 4 层卷积编码器。在匹配条件 CUNet-B（16.31 dB）还略高于 U-PAST-H（15.69 dB），但一进 reverb 失配，CUNet-S（8.609）、CUNet-B（8.244）、MP-SENet（8.139）、TF-GridNet（7.447）甚至 CleanUNet（3.569）**全部跌到未处理输入（9.033）以下**——即只喂非混响数据的模型在混响下「制造失真而非去噪」。**唯独 U-PAST 全系（9.658–9.765）都高于未处理输入**。这是全文最能立得住的一条经验证据。

2. **编码器深度 scaling**：S→H（1→12 层）在三个条件（匹配、VoiceBank-DEMAND、LibriMix）SI-SDR 近单调上升；唯一例外是 reverb 下 L（9.37）微低于 B（9.72），随后 H 回到 9.76 的全表第一。U-PAST-H 在每个条件都是家族最强，代价是参数/MAC 仅从 1.17M/4.39G 增到 2.40M/4.71G。

**复杂度（Table 2）**：U-PAST 家族 1.17–2.40M 参数、4.39–4.71 GMAC；对比 TF-GridNet（1.34M 但 85.58 G MAC）、MP-SENet（2.26M，164.01 G）、CUNet-B（8.34M，34.53 G）、CleanUNet（46.07M，时域）。A100 上 U-PAST RTF 0.0126–0.0151，比 MP-SENet（0.0523）和 TF-GridNet（0.1880）快，但仍慢于纯卷积 CleanUNet（0.0058）与 CUNet（0.0081–0.0115）。

> [!note] 摘要里的「0.26–0.63 dB」不是对最强基线的总差距
> 0.26 dB 对应 LibriMix 上的 MP-SENet，0.55/0.63 dB 对应匹配条件上的 MP-SENet/CUNet-B——都是「次强对象」。原文 §5 明确写出对最强 TF-GridNet 在其余三条件落后 **1.62–2.44 dB**，引用时须按比较对象分别表述。

> [!warning] 不宜外推成全面 SOTA
> 「DNSMOS 最强」不成立于全部四条件：§5 写明 TF-GridNet 在三项条件的多数 DNSMOS 子分数（MOS-sig/MOS-bak/MOS-ovr 等）最高，reverb 条件下也由它领先这些子分数。U-PAST 的优势应限定为「该评测中 reverb 失配的 SI-SDR 领先 + 较低参数/计算量 + matched 的 PESQ-wb 最高」。

## 5. 这个方向还剩什么问题没解决？（future work / limitation）

**论文自认的 future work（§6.4）**：探索更小的 patch size；优化推理效率，把小参数/低 MAC 的优势转化为 wall-clock（延迟）优势。

**论文自认的局限（§6.3）**：U-PAST 的 A100 RTF（0.0126–0.0151）仍比纯卷积 CleanUNet（0.0058）与 CUNet（0.0081–0.0115）高，说明 transformer 编码器与复数解码器「每 MAC 的硬件效率不如标准卷积」——准确率/计算量上的好折中尚未体现在真实延迟上。

**我读出的隐藏问题（比论文自认更值得警惕）**：

1. **无官方代码、权重与 checkpoint**；数据划分、随机种子、实现细节均未公开，独立复现缺口大。
2. **「复数」只在解码器层成立**：编码器是标准（实值）ViT，输入也是**幅度+相位两张实值通道**的 token（并非真正复数的 self-attention）。「phase-aware / complex spectrogram tokenization」的命名对读者略有名不副实，需自行辨别。
3. **因果性未声明，且结构性非因果**：全局 self-attention 需整段 T-F 上下文，无法流式/实时。A100 RTF≈0.013 只是离线吞吐参考，既不是算法延迟，也不代表边端实时性。
4. **无真正逐组件消融**：未隔离「相位通道 vs 仅幅度」「位置编码」「损失三项各自贡献」的影响；「关键发现」主要由 CUNet 对照与深度 scaling 间接折射。
5. **LibriMix 失配集只保留 s1 单说话人**（丢弃第二说话人、`min` 模式截断），本质是单说话人增强评测，不是两说话人增强。
6. **结论边界易被误读**：只有 reverb 失配一项 SI-SDR 领先，且该条件下各基线的 SI-SDR 都塌到未处理以下——更像「别人在失配下崩了，U-PAST 没崩」，而非「U-PAST 更强」。

## 6. 本论文在库中的位置关联（cross-reference matrix）

| 维度 | 论文 | 关系 |
|---|---|---|
| 前身/基石 | [[DCCRN 2020]] | 复数卷积块、CPReLU、复数 BN 的定义与单通道相位感知增强路线之源；U-PAST 的解码器直接复用其 complex U-Net（[24] 即 Nustede & Anemüller 复数 U-Net 一脉） |
| 前身/基石 | [[PHASEN 2020]] | 同为「相位感知」哲学但走相反路线：PHASEN 双流幅相解耦，U-PAST 单流幅相 token + 复数解码 |
| 前身/基石 | AST（Gong et al. 2021，**库外 ⚠️**） | 幅度谱 ViT tokenization 的迁移对象；U-PAST 将其扩展为幅相两通道 + 加解码重建（AST 仅分类无重建） |
| 同分支竞品 | [[TF-GridNet 2023]] | 直接对比、同参数量级（1.34M vs 2.40M）；F-T 交错注意力的时频域强基线，本文在其余三条件落后 1.62–2.44 dB，仅 reverb SI-SDR 领先 |
| 同分支竞品 | [[MP-SENet 2023]] | 同为幅相显式处理的小参数相位感知模型（2.26M）；LibriMix 仅差 0.26 dB、matched 差 0.55 dB |
| 同分支竞品 | [[CMGAN 2022]] | Conformer backbone 的 T-F 增强（transformer+conv 融合），与 U-PAST 的 hybrid 同属一类但引擎不同（Conformer vs 分层 U-Net 解码） |
| 跨分支类比 | [[Conformer]] | 「transformer 编码 + 卷积解码」的通用范式，U-PAST 可视为其在复数谱域的实例化 |
| 跨分支类比 | [[STFT与频谱图]] / [[语音增强评价指标]] | 概念锚点：复数 STFT 表示、SI-SDR / PESQ / DNSMOS 指标 |
| 后续/扩展 | 暂无（2026-08 新出）⚠️ | 未见直接后续、官方代码或被引扩展；[[2026 语音增强前沿五篇比较]] 为同批检索的主题语境页 |

## 7. 一句话总结"江湖地位"

```text
2026 | 单通道语音增强（复数谱幅相/相位感知） | 首个复数域 hybrid Transformer-U-Net：AST 编码器 + complex U-Net 解码器，1.17–2.40M 小模型显式重建幅相 → 作为「小参数幅相混合架构」的路标；但仅 reverb 失配 SI-SDR 领先，其余落后 TF-GridNet 1.62–2.44 dB，无官方代码、尚无后续
```