---
title: RT-Tango - 实时分布式双耳助听器语音增强
type: source
created: 2026-09-20
updated: 2026-09-20
tags:
  - speech-enhancement
  - binaural
  - distributed
  - hearing-aid
  - multichannel
  - strict-causal
  - real-time
  - streaming
  - ultra-low-latency
  - 8ms-algorithmic-latency
  - online-scm
  - grouped-recurrent-network
  - asymmetric-stft
  - temporal-sparsification
source_type: paper
year: 2026
authors: Zahra Benslimane; Pierre Chouteau; Martyna Poreba; Fabrice Auzanneau; Michal Szczepanski; Fabian Chersi; Romain Serizel
venue: arXiv preprint (arXiv:2607.01834v1 [cs.SD], 2 Jul 2026, 5 pages)
arxiv: https://arxiv.org/abs/2607.01834
local_pdf: raw/papers/low_latency_causal_se/2607.01834.pdf
evidence_policy: local_pdf_only
related:
  - [[wiki_low_latency/entities/RT-Tango]]
  - [[wiki_low_latency/concepts/2607.01834-distributed-binaural-low-latency]]
  - [[wiki_low_latency/concepts/低比特率双耳特征链路]]
  - [[wiki_low_latency/concepts/2204.09911-short-asymmetric-stft]]
  - [[wiki_low_latency/sources/2023/GCFSnet 2023]]
---

~~~yaml
- 论文: [RT-Tango: Real-Time Distributed Binaural Speech Enhancement for Low-Power Hearing Aid Devices](2026)
  ├── 要解决什么问题: 现有高效语音增强几乎都是单通道；双耳分布式助听器要同时满足严格因果、超低算法延迟、低算力和低带宽跨耳通信
  ├── 核心方法: 在 Tango 两阶段分布式框架上叠加四项效率化设计——ERB 特征压缩、分组循环网络 GRNN、非对称 STFT、时间稀疏化 FRS；SCM 改为在线 EMA 递归更新，形成流式变体 RT-Tango-OS
  ├── 属于哪个分支: 多通道/双耳分布式语音增强 / 助听器 / 严格因果超低时延 / 掩蔽+空间滤波混合
  ├── 输入/输出: 每耳节点 2 麦（前/后）共 4 麦 STFT → ERB 特征 → SN-DNN/MN-DNN 估计 mask → 逆 ERB 回线性频域 → SDW-MWF 空间滤波 → 双耳增强输出
  ├── 关键trick: 用短合成窗（8 ms）把算法延迟从频率分辨率预算里解耦；用 GRNN 分组把循环复杂度从 O(H²) 降到 O(H²/G)；用 FRS 固定间隔复用 mask 而不是每帧推理
  ├── 数据集: 训练按 Monir et al. 协议仿真（LibriSpeech 干净语音 + speech-shaped noise + 真实环境噪声，4 麦助听器配置）；评测 BinauRec 子集 1200 条混合（PHL 实测 RIR、假人头佩戴 BTE 助听器），输入 SNR −5/0/5 dB
  ├── 对比了谁: 未处理混合、CNN 版 Tango、因果 Tango-RNN、分布式 GTCRN（16 ms 与 4 ms）
  ├── 性能上限: RT-Tango（4 ms hop）SI-SDR 4.4/4.7 dB、SI-SIR 20.8/24.6 dB、PESQ 1.66/1.71、STOI 0.84/0.84；RT-Tango-OS 严格因果流式、论文口径 algorithmic latency = 8 ms，SI-SDR 降到 2.9/3.8 dB
  ├── 参数量: **未报告**（论文只给 MACs；Tango-RNN 的 DNN 为 2 层 stateful RNN、每层 128 hidden units，但不是参数总量）
  ├── 消融关键发现: SN-DNN 分组 G=8 几乎不掉点（DNN 1.06→0.59 MMAC/frame）；MN-DNN G=8 掉 0.8–1 dB 故取 G=2；FRS 1/4+1/2 在 0.2 dB 内保持而 learned skipping 反而伤害 MN-DNN；32/8 asyHann 是最佳窗配置，32/8 sqrtHann 崩到 SI-SDR 1.2/1.8 dB
  ├── 遗留问题(你的机会): 在线 SCM 用「重复到收敛、只算最后一次」评测，等于无限预热，真实流式不成立；8 ms 延迟的记账依据未给；未报告目标 DSP/MCU 的 p99、峰值内存、量化、功耗、underrun/overrun、state reset；未报告 false-suppression/F0/prosody/ASR WER；最低 SNR 只到 −5 dB
  └── 跟哪篇像: [[wiki_low_latency/sources/2023/GCFSnet 2023]]（双耳助听器链路）、[[wiki_low_latency/sources/2022/STFT-Domain Very Low Algorithmic Latency 2022]]（非对称 STFT）、[[wiki_low_latency/entities/DeepFilterNet2]]（嵌入式低复杂度）
~~~

# RT-Tango: Real-Time Distributed Binaural Speech Enhancement for Low-Power Hearing Aid Devices

> Zahra Benslimane 等，arXiv:2607.01834v1 [cs.SD]，2 Jul 2026，共 5 页。单位：Université Paris-Saclay, CEA, List（F-91120 Palaiseau）；Université de Lorraine, CNRS, Inria, LORIA（F-54000 Nancy）。基金：法国国家科研署 REFINED 项目（ANR21-CE19-0043）。
> 本页把论文的 real-time 拆成**因果性、算法延迟、每帧算力、在线 SCM 评测口径**四个独立证据来审。

> [!warning] PDF 转换质量与阅读说明
> 原 PDF 共 5 页，Poppler 页面渲染清晰，正文文本抽取基本可用。但以下几点必须看原 PDF/页面渲染核对，不能只信文本：
> - **Figure 1 框图**：文本抽取把框图内标签打散成孤立词（`SN-DNN`、`GRNN+FC`、`Inv ERB`、`SDW-MWF`、`Rear R/Front R` 等），无法还原左右节点与两阶段拓扑；本页用第 2 页渲染图 `2607.01834-page2-block-diagram.png` 视觉核对。
> - **Table 1**：列头是双耳 L/R 成对排列，文本抽取把左右耳数字压成单行序列，极易错配；本页用第 3 页渲染图 `2607.01834-page3-table1-comparison.png` 逐格核对。
> - **Table 2–5**：同样存在多列错位；本页用第 3、4 页渲染图核对（`-page3-table1-comparison.png`、`-page4-table3-5-ablation.png`）。
> - **公式**：论文正文对 GRNN 复杂度只给文字+一行量级推导；SCM 的 EMA 更新、SDW-MWF 代价函数、非对称 STFT 窗函数/延迟关系**均未在原文给出完整公式**，本页明确标注为「原文未给出该式，仅文字描述」，不代作者补写。
> - **未报告项**：参数量、RTF、训练轮数/批大小/随机种子、跨耳通信比特率均未在 5 页内出现，本页一律写「未报告」。

## 1. 他们为什么这么做？（motivation）

### 1.1 任务与对象

RT-Tango 研究**双耳分布式实时语音增强**：左右两只 behind-the-ear（BTE）助听器各自本地处理音频，只交换极少量信息，最终各自输出本侧增强语音。约束来自三方面：

- **延迟**：助听器实时链路要求严格因果、超低算法延迟；
- **算力/内存**：每只设备的 SoC 预算极低，且语音增强是回归任务，对激进量化特别敏感（论文引用 [5] 指出这会放大量化噪声、阻碍全整型部署）；
- **跨耳通信带宽**：麦克风物理分布在两个节点上，集中式处理需要持续高带宽无线传输，在能量与带宽约束下不可行。

论文的关键判断是：**高效语音增强的现有工作几乎都在单通道**，而高效多麦方法要么算力仍高于超轻量单耳模型，要么默认集中式、能访问全部麦克风信号。因此「双耳分布式 + 低延迟 + 低算力」三者的联合约束仍是开放问题。

### 1.2 论文动机

论文没有从零设计网络，而是**系统级重构 Tango 框架**（Furnon et al. 2021 [16]），理由是 Tango 的两阶段分布式结构在空间无约束麦克风配置下已被证明有效。Tango 的原始公式**不施加任何延迟或复杂度约束**，所以 RT-Tango 要做的就是把这套结构压到助听器可承受的延迟和算力。

## 2. 之前的人怎么做不了？（limitation → gap）

| 路线 | 能力 | 仍然卡在哪里 |
|---|---|---|
| 模型压缩（剪枝+量化）[1,2,3] | 降内存与计算 | 回归任务对激进量化敏感，难以全整型部署 [5] |
| 硬件导向稀疏度研究 [4] | 揭示结构与吞吐—内存—质量折中 | 仍是单通道视角，不解决双耳通信 |
| 分组处理 [8,9] / 子采样 [10] / ERB 压缩（GTCRN [11]） | 架构层面降算力 | 绝大多数面向单麦 |
| 高效多麦架构 [12,13] | 开始利用空间线索 | 算力仍高于超轻量单耳模型，且默认集中式、需访问全部麦克风 |
| 分布式无融合中心框架 [14,15] | 避免集中式高带宽传输 | 未同时满足低延迟与低复杂度 |
| 低带宽分布式双耳增强 [16]（Tango） | 证明降带宽双耳增强可行 | 原版无延迟/复杂度约束 |

论文自述的 gap：**「据我们所知，没有任何现有方法在分布式双耳框架内同时组合这些必需设计要素，并满足显式的实时延迟与算力约束。」** 这句话是本文立论的核心，也是它的自我定位边界——它主张的是**组合**与**约束满足**，而不是单个模块的原创。

### 2.1 严格因果与延迟账本

| 审计项 | PDF 证据 | 本 Wiki 判定 |
|---|---|---|
| 分析窗 aW | 32 ms（Table 5 全部行；训练用 32 ms 分析窗 + 16 ms hop） | 长窗保频率分辨率；**帧锚定方式未报告**，若为中心对齐则含 look-ahead → `low_look_ahead`（待确认），不能仅凭「非对称」就判 strict |
| 合成窗 sW | RT-Tango-OS 选 8 ms asyHann（Table 5、3.2.3） | 决定重建延迟，是论文 **8 ms algorithmic latency** 的来源 |
| hop | RT-Tango/RT-Tango-OS = 4 ms；Tango、分组消融、FRS 用 16 ms；learned skipping 与 GTCRN(4 ms) 用 4 ms | 4 ms 更新率 |
| 帧率 | ≈62 frames/s @16 ms；≈250 frames/s @4 ms（Table 1 题注） | — |
| look-ahead | **未报告**（无显式 future frame 说明，也无逐层 receptive field） | `low_look_ahead` 未能排除；论文的 strict causal 属**论文级声明**，非逐层 certificate |
| 递归状态 | GRNN/stateful RNN 隐状态；SN-DNN、MN-DNN 各自独立 | 结构上支持 batch=1 流式；warm-up、state reset、长流漂移未报告 |
| SCM 在线更新 | EMA 遗忘因子 α = 0.995，每 8 帧更新一次 @4 ms 输入率 → 有效更新间隔 32 ms（≈31 次/s） | 递归在线更新，**判定为因果**（只依赖历史统计）；但见下一行 |
| **在线 SCM 评测口径** | 论文把每条混合**重复足够多次让 SCM 收敛**，指标只在**最后一次重复**上计算（p.3、Section 3.2.4） | 相当于**无限长 warm-up**；真实流式首段无法复现该结果 → 属「部署与恢复」维度的证据缺口，标 `未验证` |
| 每帧 MACs | RT-Tango-OS 0.49 MMACs/frame（DNN 0.27 + SDW-MWF 0.22） | 单节点口径；MACs 计入 DNN + ERB/逆 ERB + SDW-MWF，**不含 FFT/iFFT** |
| 端到端 | ADC/DMA、I/O buffer、DAC/playout、capture-to-playback、underrun/overrun 均**未报告** | `未验证` |

> [!warning] 关于「严格因果」与「8 ms」
> 论文原文只有一句：「RT-Tango-OS enables strictly causal streaming with an algorithmic latency of 8 ms, through the asymmetric STFT and online SDW-MWF updates.」它**没有给出 8 ms 的推导式**，也没有给出逐层的 padding / 状态 / 最后可读输入样本清单。按本库 [[wiki_low_latency/concepts/严格因果与算法延迟]] 的判定规则，RT-Tango-OS 应标为「论文级 strict causal、8 ms algorithmic latency」，而**不是**「已认证 strict_causal / 已通过端侧 deadline」。

> [!contradiction] 非对称 STFT 与严格因果的张力
> 本库 [[wiki_low_latency/concepts/2204.09911-short-asymmetric-stft]] 记录：2204.09911 的同类双窗配置（长分析窗 + 短合成窗）被明确标为 **low_look_ahead / frame_online**，而非严格 sample-causal，因为长输入窗对要输出的尾段仍要看前方若干毫秒。RT-Tango 复用同一思路（引用 [20,21]）却直接声明 strictly causal，且未说明帧锚定与 look-ahead。两篇的处理口径不一致，需按原始实现核对后才能采信 RT-Tango 的 strict 标签。

## 3. 这个做法核心 trick 是什么？

论文的答案很明确：**不是一个 idea，而是四个互补设计叠在同一个两阶段分布式骨架上**。它自己称之为「complementary architectural and algorithmic design principles」，并强调不是孤立优化。

### 3.1 骨架：Tango 的两阶段分布式管线

论文第 2 页 Figure 1 的拓扑（视觉核对自页面渲染图）：

~~~text
Stage 1（每耳本地）
  4 麦 STFT（Rear R / Front R / Rear L / Front L）
    → ERB Features
    → SN-DNN（GRNN + FC）
    → Inv ERB（回线性频域）
    → SDW-MWF
    → 本耳压缩信号 Out R / Out L
       （跨耳传给对侧节点，作为 MN-DNN 的额外输入）
Stage 2（每耳本地，融合本地 + 对侧表征）
    → MN-DNN（ERB Features / GRNN + FC / Inv ERB）
    → SDW-MWF
    → iSTFT
    → 双耳增强输出 Out L / Out R
~~~

![[wiki_low_latency/assets/2607.01834/2607.01834-page2-block-diagram.png]]

> 图注：原论文第 2 页 Figure 1 的页面渲染。用于核对两阶段分布式拓扑：Stage 1 的 SN-DNN（GRNN+FC）+ 逆 ERB + SDW-MWF，跨耳交换后进入 Stage 2 的 MN-DNN，再做第二次 SDW-MWF 与 iSTFT。论文用黄色标效率相关改动、斜体标低延迟流式相关改动。图片为 PDF 页面复制，不是 AI 重画。

### 3.2 Trick A：ERB 感知特征压缩

两个 mask 估计网络（SN-DNN、MN-DNN）都以 **ERB 表征**为前端。动机是：人耳在高频的分辨率更粗，而语音能量与关键线索集中在低频。用 ERB 尺度对齐后，输入维度下降，后续层参数量与运算量随之下降。**mask 估计完成后用逆 ERB 变换映射回线性频域**，以恢复空间滤波所需的频谱分辨率。

> [!note] 来源
> ERB 压缩明确借鉴 GTCRN [11]。本文把它用于**双耳分布式**场景，并对 SN-DNN 与 MN-DNN 同时使用。

### 3.3 Trick B：分组循环网络 GRNN

论文用 GRNN [18] 替换 Tango-RNN 的循环层。动机是**语音的频谱依赖是局部化的**——频带内邻近区域的依赖通常更强，因此可以分区独立递归，再用 **representation rearrangement** 机制交换跨组信息以恢复全局频谱建模。

复杂度论证是论文给出的**唯一一行显式推导**：循环层计算量随隐状态维度 $H$ 近似二次增长，即 $O(H^2)$；把特征空间切成 $G$ 组、每组 $H/G$，则总复杂度为

$$
G \cdot O\!\left(\left(\frac{H}{G}\right)^{2}\right) = O\!\left(\frac{H^{2}}{G}\right),
$$

即相对全频带 RNN 降低约 $G$ 倍。注意这只是**循环层**的量级论证，论文没有给出常数项、FC 层或 rearrangement 机制的额外开销公式。

### 3.4 Trick C：非对称 STFT——把频率分辨率与算法延迟解耦

这是论文回答「超低延迟」的核心手段。论文采用**非对称 STFT**（引用 [20] Wang et al. 2023 与 [21] Wood & Rouat 2019）：

- **长分析窗 aW** 保持频率分辨率；
- **短合成窗 sW** 降低重建延迟（OLA 只需等到较短尾段即可输出）。

Table 5 的结论是 32 ms 分析窗 + 8 ms 合成窗 + asyHann 为最佳折中（见 §4）。

> [!question] 原文未给出该式
> 论文**没有给出**非对称 STFT 的窗函数定义、perfect-reconstruction 归一化式，或「算法延迟 = f(aW, sW, hop)」的推导。它只写「a longer synthesis window would increase latency while a shorter one would degrade reconstruction」，以及把 8 ms 归因于该配置。**8 ms 的具体记账方式（等于 sW？等于 sW − hop？是否含 look-ahead？）原文未说明**，本页不代作者补齐。

### 3.5 Trick D：时间稀疏化——FRS 与 learned skipping 的对比

论文利用输入信号的**时间冗余**做 skip inference：不是每帧都跑网络，而是在输入变化有限时**复用上一次估计的 mask**。定义了两种策略：

- **Fixed-Rate Skipping (FRS)**：按固定间隔执行 mask 估计器，中间帧复用旧 mask。RT-Tango 采用 **SN-DNN 更新率 1/4、MN-DNN 更新率 1/2**（即分别每 4 帧、每 2 帧推理一次）。
- **learned skip gates** [3,19]：用门控机制逐帧决定是否更新递归状态（对比对象为 SkipRNN [19] 与 TinyLSTM [3]）。

### 3.6 Trick E：SCM 在线递归更新

SDW-MWF 需要空间协方差矩阵（SCM）。离线 RT-Tango 用**整句估计的 SCM**；流式变体 RT-Tango-OS 改为**递归 EMA 在线更新**，遗忘因子 $\alpha = 0.995$，在 4 ms 输入率下**每 8 帧更新一次**，有效更新间隔 32 ms（≈31 次/s）。

> [!warning] 原文未给出该式，仅文字描述
> 论文只写「updated online using a recursive exponential moving average (EMA)」并给出 $\alpha=0.995$ 与更新节奏，**没有给出** SCM 的递归更新方程、初始化、正则化或逆矩阵更新方式。标准 EMA 形式应为
> $$\hat{\mathbf R}_{\Phi\Phi}(t) = \alpha\,\hat{\mathbf R}_{\Phi\Phi}(t-1) + (1-\alpha)\,\mathbf\Phi(t)\mathbf\Phi^{H}(t),$$
> 但**该式并非论文所写**，此处仅作读者理解参考，不作为论文证据引用。

> [!warning] 原文未给出 SDW-MWF 公式
> 论文对 SDW-MWF 只给引用 [17]（Doclo et al. 2007）和一句功能描述（「语音失真加权的多通道维纳滤波」），**没有写出代价函数或滤波形式**。因此本页不列 SDW-MWF 的显式公式；如需复现须回到 [17]。

## 4. 实验里哪个消融最关键？

### 4.1 数据与评价设置

| 项目 | 论文设置 |
|---|---|
| 训练数据 | 按 Monir et al. [22] 协议仿真的双耳数据；LibriSpeech [23] 干净语音 + speech-shaped noise + 真实环境噪声；4 麦助听器配置（每耳 2 麦） |
| 评测数据 | BinauRec [24] 子集，1200 条混合；用便携式听力实验室（PHL）[25] 的**实测 RIR**，假人头佩戴 BTE 助听器 |
| 空间布置 | 目标声源在正前方；噪声在目标右侧 45° 与 90° → **右耳 SIR 低于左耳** |
| 输入 SNR | −5 / 0 / 5 dB（干信号先按此 SNR 混合，再与 RIR 卷积） |
| 指标 | SI-SDR / SI-SIR / SI-SAR（dB）[26] + PESQ [27] + STOI [28]；左右耳分别报告 |
| 算力口径 | MACs/s 或 MACs/frame，**单处理节点**；计入 DNN mask 估计器 + ERB/逆 ERB + SDW-MWF；**不含 FFT/iFFT** |
| 训练 | PyTorch；Adam，lr = $10^{-3}$；损失 = 估计 TF mask 与目标 IRM 的 MSE（论文仅文字描述，未给公式） |
| 前端配置 | 分组消融 / FRS / RT-Tango / RT-Tango-OS 用 32 ms 分析窗 + 16 ms hop；learned skipping 与 GTCRN(4 ms) 用 4 ms hop 以对齐帧率 |

对比系统：CNN 版 Tango、因果 Tango-RNN（SN-DNN 与 MN-DNN 均为 2 层 stateful RNN、每层 128 hidden units + 一层 FC）、分布式 GTCRN [11]（每节点一个实例，输入 4 麦信号，mask 作用于本地参考通道）。

### 4.2 主结果（Table 1）

![[wiki_low_latency/assets/2607.01834/2607.01834-page3-table1-comparison.png]]

> 图注：原论文第 3 页 Table 1 与 Table 2 页面渲染。Table 1 的列头为双耳 L/R 成对；Table 2 为分组消融。用于逐格核对本页所有 MMACs/s 与 SI-* 数字。图片为 PDF 页面复制，不是 AI 重画。

| Model | STFT Hop | Total | DNN | SDW-MWF | SI-SIR L/R | SI-SDR L/R | SI-SAR L/R | STOI L/R | PESQ L/R |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Unprocessed | − | − | − | − | 0.0 / −4.0 | −0.6 / −4.6 | − / − | 0.68 / 0.56 | 1.14 / 1.10 |
| Tango | 16 ms | 605.98 | 604.5 | 1.48 | 20.8 / 24.1 | 4.2 / 4.4 | 4.7 / 4.7 | 0.83 / 0.84 | 1.61 / 1.64 |
| GTCRN | 16 ms | 48.98 | 48.98 | − | 16.1 / 14.1 | 5.6 / 3.7 | 6.4 / 4.5 | 0.76 / 0.69 | 1.47 / 1.34 |
| GTCRN | 4 ms | 197.5 | 197.5 | − | 16.6 / 13.8 | 6.0 / 4.0 | 6.7 / 5.0 | 0.79 / 0.71 | 1.52 / 1.36 |
| Tango-RNN | 16 ms | 67.20 | 65.72 | 1.48 | 21.6 / 25.0 | 4.7 / 5.0 | 5.2 / 5.2 | 0.84 / 0.85 | 1.66 / 1.70 |
| + GRNN SN=8, MN=2 (⋆) | 16 ms | 18.22 | 16.74 | 1.48 | 21.3 / 24.8 | 4.5 / 4.8 | 5.1 / 5.0 | 0.84 / 0.84 | 1.66 / 1.70 |
| **RT-Tango (ours)** | 4 ms | 33.41 | 28.08 | 5.33 | 20.8 / 24.6 | 4.4 / 4.7 | 5.0 / 5.0 | 0.84 / 0.84 | 1.66 / 1.71 |
| **RT-Tango-OS (ours)** | 4 ms | 35.14 | 28.08 | 7.01 | 20.5 / 24.7 | 2.9 / 3.8 | 3.4 / 4.0 | 0.80 / 0.82 | 1.54 / 1.63 |

论文从中读出的结论（原话转述，不做外推）：

- Tango 与 Tango-RNN 在 PESQ、STOI、SI-SIR 上**一致优于** GTCRN（双耳）；GTCRN 只在噪声较轻的左耳于 SI-SDR/SI-SAR 上略胜。Tango 系方法左右耳更均衡，论文认为这种 interaural balance 对助听器的稳定空间感和聆听舒适度更有利。
- Tango-RNN 把 Tango 复杂度降到 67.2 MMAC/s；RT-Tango 在**更高帧率**下达 33.4 MMAC/s；在同等条件下比 GTCRN(197.5) 高效近 6 倍（197.5 / 33.41 ≈ 5.9）。
- RT-Tango-OS 的 SI-SIR 与离线 RT-Tango 相当（20.5/24.7 vs 20.8/24.6），但 SI-SDR/SI-SAR 明显下降（4.4/4.7 → 2.9/3.8）。论文把下降归因于**先由非对称 STFT 引入、再被在线 SCM 放大**。

> [!note] 一个容易被忽略的对照
> RT-Tango 的 SDW-MWF 单项从 1.48 涨到 5.33 MMACs/s（RT-Tango-OS 再涨到 7.01），而 DNN 从 65.72 降到 28.08。也就是说**帧率翻 4 倍后，空间滤波本身成了不可忽略的成本项**——这类「前端提速反而抬高 DSP 支路占比」的现象在单通道低时延论文里看不到，是双耳多麦系统的特有账目。

### 4.3 消融一：分组策略（Table 2）——最关键的架构消融

![[wiki_low_latency/assets/2607.01834/2607.01834-page4-table3-5-ablation.png]]

> 图注：原论文第 4 页 Table 3（SN-DNN 时间稀疏化）、Table 4（MN-DNN 时间稀疏化）、Table 5（窗长/窗型）页面渲染。用于逐格核对本页所有消融数字。图片为 PDF 页面复制，不是 AI 重画。

| Model | DNN (SN+MN) MMACs/frame | SI-SDR L/R | SI-SAR L/R |
|---|---:|---:|---:|
| Tango-RNN | 1.06 | 4.7 / 5.0 | 5.2 / 5.2 |
| + GRNN SN=2 | 0.69 | 4.7 / 4.9 | 5.2 / 5.2 |
| + GRNN SN=8 | 0.59 | 4.7 / 4.9 | 5.1 / 5.1 |
| + GRNN MN=2 | 0.74 | 4.7 / 4.9 | 5.2 / 5.1 |
| + GRNN MN=8 | 0.64 | 3.8 / 4.1 | 4.2 / 4.3 |

**最关键的发现**：SN-DNN 与 MN-DNN 对分组的敏感度**完全不同**。

- SN-DNN 用 G=8，把总 DNN 复杂度从 1.06 降到 0.59 MMAC/frame（≈44%），SI-SDR 仍保持 4.7/4.9 dB，PESQ/STOI 不变 → **几乎免费**。
- MN-DNN 用 G=8 则 SI-SDR/SI-SAR 掉约 **0.8–1 dB**；只有 G=2 才保住性能。

这直接决定了最终配置 **(SN=8, MN=2)**，即 Table 1 中带 ⋆ 的行。论文给出的解释是：第二阶段要融合跨耳表征，跨频带的全局依赖更强，因此不能像第一阶段那样激进分组。这是一个「同一模块在不同阶段收益不对称」的干净证据。

### 4.4 消融二：时间稀疏化（Table 3 / Table 4）

**SN-DNN（Table 3）**：

| Model | MMACs/frame w/o Skip | w/ Skip | SI-SDR L/R | SI-SAR L/R |
|---|---:|---:|---:|---:|
| SN-DNN of (⋆) | 0.09 | − | 4.5 / 4.8 | 5.1 / 5.0 |
| (⋆) + FRS 1/2 | 0.09 | 0 | 4.4 / 4.7 | 5.1 / 5.0 |
| (⋆) + FRS 1/4 | 0.09 | 0 | 4.3 / 4.6 | 5.0 / 4.9 |
| (⋆) + SkipRNN [19] | 0.09 | 0.01 | 4.4 / 4.3 | 5.0 / 4.6 |
| (⋆) + TinyLSTM [3] | 0.12 | 0.09 | 4.3 / 4.4 | 5.0 / 4.7 |

**MN-DNN（Table 4）**：

| Model | MMACs/frame w/o Skip | w/ Skip | SI-SDR L/R | SI-SAR L/R |
|---|---:|---:|---:|---:|
| MN-DNN of (⋆) | 0.18 | − | 4.5 / 4.8 | 5.1 / 5.0 |
| (⋆) + FRS 1/2 | 0.18 | 0 | 4.4 / 4.8 | 5.1 / 5.1 |
| (⋆) + FRS 1/4 | 0.18 | 0 | 4.3 / 4.8 | 4.8 / 5.0 |
| (⋆) + SkipRNN [19] | 0.18 | 0.02 | 3.8 / 4.7 | 4.5 / 5.0 |
| (⋆) + TinyLSTM [3] | 0.21 | 0.07 | 3.3 / 4.6 | 3.9 / 4.8 |

**最有信息量的对照**是同一 stage 上 FRS 与 learned skipping 的对比：

- SN-DNN 上 FRS 在 1/2 与 1/4 下都保持基线 **0.2 dB 以内**，且非更新帧 MMACs = 0；
- learned skipping 虽然达到 **80% 的有效 skip 率**，却仍有轻微退化（主要在有噪声的右声道），因为门控本身要每帧评估、引入额外 MACs；
- MN-DNN 对 learned skipping **明显更敏感**：左耳 SI-SDR 从 4.5 dB 掉到 3.8 dB（SkipRNN）和 3.3 dB（TinyLSTM），而 FRS 仍保持在 0.2 dB 内。

结论：论文选择 FRS（SN 1/4、MN 1/2，即 SN-DNN 跳 75% 帧、MN-DNN 跳 50% 帧），理由是**稳定性 + 可预测的算力节省**。在 4 ms hop 下，这把 DNN 成本从无稀疏化的 **67.5 MMACs/s 降到 28.08 MMACs/s**。

> [!question] 表内 0 的解释
> Table 3/4 中 FRS 的「w/ Skip」列为 0，指的是**非更新帧不再执行 DNN**，不是整帧零成本。复用 mask 的逻辑、缓存读取与帧对齐开销未单独计量。

### 4.5 消融三：窗长与窗型（Table 5）

| aW (ms) | sW (ms) | Window | SI-SDR L/R | SI-SAR L/R |
|---:|---:|---|---:|---:|
| 32 | 32 | sqrtHann | 4.4 / 4.7 | 5.0 / 5.0 |
| 32 | 8 | sqrtHann | **1.2 / 1.8** | 1.4 / 1.9 |
| 32 | 8 | asyHann | 3.7 / 4.3 | 4.3 / 4.5 |
| 32 | 4 | asyHann | 3.4 / 4.0 | 3.9 / 4.1 |

这是**最戏剧性的消融**：把合成窗从 32 ms 缩到 8 ms，普通平方根 Hann 直接**崩塌**（SI-SDR 4.4/4.7 → 1.2/1.8 dB，几乎退到未处理水平），而 asyHann 只掉到 3.7/4.3 dB。再缩到 4 ms，asyHann 继续掉到 3.4/4.0 dB。

论文的解读是：**标准平方根 Hann 在短合成长度下退化很快，非对称 Hann [21] 在低延迟下保持更好**；8 ms 是延迟与质量的最优折中，故 RT-Tango-OS 选 32/8 asyHann。该组实验用 **batch（离线）SCM** 计算，以把 STFT 配置的影响与在线 SCM 分离——这个实验设计本身是干净的。

### 4.6 消融四：在线 SCM 收敛（Section 3.2.4）

论文只做定性描述：RT-Tango-OS 的 SI-SIR 与离线 RT-Tango 相当，但 SI-SDR/SI-SAR 略降，**先由非对称 STFT 引入，再被在线 SCM 需求放大**；不过 STOI/PESQ 仍接近同帧率的 GTCRN。**论文没有给出 SCM 收敛曲线、收敛所需帧数或不同 α 的对比**。

### 4.7 最关键消融的判断

如果只能保留一个结论：**Table 5（窗型/窗长）和 Table 3/4（FRS vs learned skipping）是两个决定性实验**。

- Table 5 说明：低延迟的瓶颈不在网络，而在**重建前端**——同样的网络、同样的离线 SCM，仅换窗型就从 1.2 dB 变成 3.7 dB。这印证了本库「延迟账本」的核心立场：**算法延迟由前端决定，不由模型决定**。
- Table 3/4 说明：**learned skipping 在低延迟高帧率场景下反而不划算**——门控每帧都要算，且对需要跨耳融合的 MN-DNN 有害。这是一个反直觉但很有工程价值的负结果。

## 5. 这个方向还剩什么问题没解决？（future work / limitation）

### 5.1 论文自身没有展开的（= 明确缺口）

论文的 Conclusions 只做了正面总结（「satisfy the stringent real-time, latency, and computational constraints」「well suited for practical deployment」），**没有写 future work 段落**，也没有讨论局限性。以下缺口是从正文与方法中读出的。

### 5.2 最严重的方法论缺口：在线 SCM 的「无限预热」评测

> [!warning] 这是本页认为最重要的证据缺口
> 论文原文：*"As online SCM estimation requires an adaptation period, RT-Tango-OS was evaluated in steady state by repeating each mixture a sufficient number of times to allow for convergence. The metrics are computed on the final repetition."*
>
> 这意味着：**RT-Tango-OS 的所有指标都是在一个已经收敛的 SCM 上算的**。在真实助听器流式部署里，设备开机后没有「先把同一段话重复 N 遍」的机会——用户说的第一句话必须直接被处理。因此：
> - 该结果**不能**代表冷启动/前几秒的增强质量；
> - 论文**没有报告**收敛需要多少帧、收敛前 SI-SDR 掉多少、α 取值的敏感性；
> - 这条评测口径使「8 ms 严格因果流式」在**质量维度上**失去了最关键的现场验证，只保留了**算力/延迟维度**的可信度。
>
> 本页据此把「部署与恢复」标记为**证据缺口**，而非「已通过」。

### 5.3 其他缺口

1. **8 ms 延迟的记账依据缺失**：论文只声明结果，未给推导，也未区分 algorithmic latency 与模型计算耗时。本库要求「延迟与因果性拆开报告」，此篇只满足一半。
2. **strict causal 无逐层 certificate**：未列 padding、归一化统计、缓存状态、最后可读输入样本；且非对称 STFT 与 2204.09911 的 low_look_ahead 判定存在张力。
3. **无目标硬件证据**：没有 DSP/MCU 型号、p50/p95/p99、峰值 RAM/SRAM、量化精度、功耗、deadline miss、underrun/overrun、编译器与 runtime。
4. **无 RTF**：全篇没有报告任何 RTF 或 wall-clock 测量，只有 MACs 理论值。
5. **无 state reset / warm-up 策略**：递归状态与 SCM 状态的初始化、flush、丢帧抖动下的恢复均未描述。
6. **人声保留专项指标全缺**：没有 false-suppression、SPP/VAD 校准、ASR WER、F0/formant/prosody continuity、voiced energy 保留。SI-SIR/SI-SAR 只能作**间接代理**（SI-SIR 升说明干扰被压，SI-SAR 降说明引入伪影；但两者都无法直接证明弱辅音未被误抑制）。
7. **SNR 覆盖不足**：最低只到 **−5 dB**，未覆盖本库要求的 −10 dB、babble、竞争说话人、瞬态噪声与未见噪声。
8. **参数量未报告**：只有 MACs。这在「低功耗助听器」语境下是明显缺失——MACs 低不等于内存/能耗低。
9. **跨耳通信未量化**：Tango 系会传输耳侧压缩信号，但 RT-Tango 论文**没有报告**该链路的比特率、延迟、丢包/抖动处理，也没有像 GCFSnet 那样做链路量化消融。这对「分布式」这一核心卖点是关键空白。
10. **训练细节不全**：未报告 epochs、batch size、随机种子、训练时长、是否早停、SCM 训练/推理的一致性处理。
11. **SCM 估计量本身**：离线用整句 SCM，是**非因果**统计；RT-Tango（非 OS）因此不能算流式系统，只是上界参照。

### 5.4 对当前方向的可迁移启示

- **非对称 STFT 是低时延前端最直接的杠杆**：Table 5 证明换窗型比换网络更能决定低延迟下的质量。做约 2 ms 系统时应优先做窗型/窗长扫描，而不是先堆模型。
- **FRS 这类「无参数时间稀疏化」在极高帧率下优于 learned gating**：如果目标是 2 ms 级前端，帧率会非常高（≈500 frames/s），此时门控开销与状态更新频率成正比，FRS 的固定间隔复用更划算。这个结论可迁移到单通道。
- **分组敏感度不对称**：任何两阶段/多阶段架构都应**分阶段**做分组消融，不能把「G 越大越好/越差」当成全局结论。
- **在线统计（SCM/EMA）必须按冷启动评测**：这是本库可以立刻吸收的验收要求——任何「在线递归统计」的方法都应报告收敛前曲线，否则其质量数字不可用于流式部署论证。

## 6. 本论文在库中的位置关联（cross-reference matrix）

| 关系 | 库中页面 | 关联与差异 |
|---|---|---|
| 同分支竞品（双耳助听器链路） | [[wiki_low_latency/sources/2023/GCFSnet 2023]] | 两者都是双耳助听器低时延增强。GCFSnet 把跨耳信息压成低比特率 log-magnitude/IPD 特征并做链路量化消融，过滤框架约 2 ms；RT-Tango 继承 Tango 的耳侧压缩信号交换，但**未量化通信比特率**，延迟目标也更大（8 ms vs 2 ms 级） |
| 概念接口 | [[wiki_low_latency/concepts/低比特率双耳特征链路]] | 该概念页提出「低时延主路径只读当前本地观测、迟到的对侧信息进辅助支路」；RT-Tango 的两阶段交换符合这一原则，但没有报告链路延迟/丢包/抖动，也未做比特率消融，是**该概念的一个未闭环实例** |
| 前身/基石（非对称 STFT） | [[wiki_low_latency/concepts/2204.09911-short-asymmetric-stft]] | RT-Tango 的非对称 STFT 直接引用 [20]（即 2204.09911）。该概念页明确把同类配置标为 `low_look_ahead / frame_online`，而 RT-Tango 自称 strictly causal → **判定口径冲突**，见 §2.1 的 contradiction |
| 前身/基石（非对称 STFT 原始论文） | [[wiki_low_latency/sources/2022/STFT-Domain Very Low Algorithmic Latency 2022]] | 该文系统研究双窗 STFT 与 future-frame prediction 的延迟账本；RT-Tango 只取「长分析窗 + 短合成窗」这一半，未使用 future-frame prediction |
| 跨分支类比（嵌入式低复杂度） | [[wiki_low_latency/entities/DeepFilterNet2]] | DeepFilterNet2 用深滤波在嵌入式设备上做全带实时增强，强项是复数后滤波与极低 MAC；RT-Tango 强项是双耳分布式 + 空间滤波。两者的「低复杂度」路线不同（后滤波 vs 多麦 SDW-MWF） |
| 同分支竞品（低复杂度时频建模） | [[wiki_low_latency/sources/2023/FSB-LSTM 2023]] | FSB-LSTM 用 full-/sub-band 集成建模降复杂度，与 RT-Tango 的 GRNN 分组都是「把频率轴切开」的思路；但 FSB 面向单通道，RT-Tango 面向分布式双耳 |
| 统一延迟基准 | [[wiki_low_latency/sources/2024/Ultra-Low Latency Speech Enhancement Comprehensive Study 2024]] | 该研究把窗长、look-ahead、计算与质量分开记账；RT-Tango 的 8 ms 应放入同一 ledger，且需补 look-ahead 与端到端项 |
| 严格因果判定规则 | [[wiki_low_latency/concepts/严格因果与算法延迟]] | 该页要求逐层 padding/状态证据；RT-Tango 只有论文级声明 → 按规则只能标「论文级 causal」 |
| 延迟账本 | [[wiki_low_latency/concepts/低时延前端与延迟账本]] | RT-Tango 的 8 ms 属 algorithmic latency 项；computation/system/speech-preservation/failure-handling 四项均缺失 |
| 人声保留验收 | [[wiki_low_latency/concepts/低 SNR 人声保留评估]] | RT-Tango 缺 false-suppression、F0/prosody、ASR WER、负 SNR 分层；SI-SIR/SI-SAR 仅间接代理 |
| 同域实体 | [[wiki_low_latency/entities/GCFSnet]] | 双耳助听器链路的另一实体，可与 RT-Tango 组成「跨耳信息如何服务实时增强」的对比对 |
| 后续/扩展（低时延 Mamba） | [[wiki_low_latency/sources/2026/RT-SEMamba 2026]] | 同为本库 2026 年的实时增强工作，但路线完全不同：RT-SEMamba 是单通道因果 Mamba + 蒸馏（25 ms），RT-Tango 是双耳分布式 + 掩蔽/空间滤波（8 ms）。两者都缺目标端侧 p99 |
| 方法学类比 | [[wiki_low_latency/concepts/2409.10358-ultra-low-latency-benchmark]] | 该基准页的「window/hop/look-ahead/compute 分账」可直接套用于 RT-Tango 的延迟审计 |

> [!question] 关联不确定性
> 库中暂无与 Tango/RT-Tango 同源的后续论文，因此「被谁怎么用了」目前无法填写。RT-Tango 的 Tango 基线（Furnon et al. 2021）**不在本库**，本页对其描述完全依据 RT-Tango 论文第 2 页 §2.1 的转述，未独立核验原版 Tango。

## 7. 一句话总结「江湖地位」

~~~text
2026 | 双耳分布式助听器语音增强 | 在 Tango 两阶段分布式框架上叠加 ERB 压缩 + GRNN 分组 + 非对称 STFT + FRS，
把算力从 605.98 压到 33.41 MMACs/s 并给出 8 ms 论文级算法延迟 → 为「分布式 + 严格因果 + 低算力」的联合约束
提供了一个完整的设计组合与干净的消融证据；但其在线 SCM 用无限预热评测、缺端侧 p99 与人声保留证据，
尚未构成约 2 ms 严格因果系统的正向验证。
~~~

## 参考资料

- [arXiv:2607.01834](https://arxiv.org/abs/2607.01834)
- 本地原件：raw/papers/low_latency_causal_se/2607.01834.pdf
- 页面渲染图：`wiki_low_latency/assets/2607.01834/2607.01834-page2-block-diagram.png`（Figure 1）、`2607.01834-page3-table1-comparison.png`（Table 1/2）、`2607.01834-page4-table3-5-ablation.png`（Table 3/4/5）
- 论文关键引用（原文编号）：[16] Furnon et al. 2021（Tango 基线）、[17] Doclo et al. 2007（SDW-MWF）、[18] Gao et al. 2018（GRNN）、[19] Campos et al. 2018（SkipRNN）、[20] Wang et al. 2023（低算法延迟 STFT）、[21] Wood & Rouat 2019（非对称 Hann）、[22] Monir et al. 2025（训练协议）、[24] BinauRec 数据集、[25] PHL 便携听力实验室
