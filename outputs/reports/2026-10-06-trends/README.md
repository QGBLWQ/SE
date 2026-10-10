---
title: 2026 语音领域研究方向调研（INTERSPEECH 2026 及主要期刊/会议）
type: topic
created: 2026-10-06
updated: 2026-10-06
tags:
  - 调研
  - trends
  - interspeech
  - icassp
  - taslp
related:
  - [[wiki/topics/2026 语音增强前沿五篇比较]]
  - [[wiki_array/topics/2026 前沿声源定位五篇比较]]
---

# 2026 语音领域研究方向调研

> 检索日期：2026-10-06。范围：INTERSPEECH 2026 全部录用论文索引（ISCA Archive）+ ICASSP 2026 官方主题分类 + 语音方向主要期刊（TASLP / Computer Speech & Language / Speech Communication）的特刊与近期卷目。

## 0. 一句话结论

2026 年语音领域的重心已经从「把语音识别/合成做准」整体转向 **「语音大模型（Speech/ Audio LLM）为中枢、生成式方法（扩散 / 流匹配）为引擎、低资源与多语言为覆盖面、健康与安全为落地出口」** 四条主线；同时 **端侧/实时/低时延的工程约束** 成为几乎所有任务线的共同副标题。

---

## 1. INTERSPEECH 2026 全景

| 项目 | 内容 |
|---|---|
| 时间 / 地点 | 2026-09-27 ~ 10-01，澳大利亚悉尼 |
| 大会主席 | Beena Ahmed, Michael Proctor, Vidhyasharan Sethu, Felicity Cox |
| 技术程序主席 | Carlos Busso, Berrak Sisman, Bhuvana Ramabhadran, Jeesun Kim, Petra Wagner |
| 论文规模 | ISCA Archive 已索引 **1379 篇**、**184 个 session**（不含 keynote / challenge 专场） |
| DOI | 10.21437/Interspeech.2026 |

### 四场 Keynote 已经点明了会议的四条主线

| Keynote | 讲者 | 主题 |
|---|---|---|
| 1 | John Hansen | 在 AI 时代平衡语音/语言/听觉科学与机器学习建模：「了解你的问题、数据与解决方案」 |
| 2 | Steven Bird | 语音技术与语言多样性 |
| 3 | Jennifer Hay | 什么叫做「认识一个词」（心理词汇 / 语音—语义接口） |
| 4 | Junichi Yamagishi | 生成式语音 AI 滥用的对抗（防伪/水印/溯源） |

### 六个官方 Challenge

- **Audio Reasoning Challenge** — 大音频语言模型的深度音频推理
- **Transfer of Pragmatic Intent in Speech-to-Speech Translation** — 语音到语音翻译中的语用意图迁移
- **Unsupervised Speech in the Wild** — 无监督真实场景语音
- **IQRA 2026** — 阿拉伯语标准语发音自动评测
- **NeckVibe Challenge** — 嗓音障碍检测（利用颈部振动信号）
- **TidyVoice Challenge** — 跨语言说话人验证

---

## 2. 主题分布量化（基于 1379 篇论文标题的关键词命中）

> 说明：按标题关键词统计，一个标题可命中多个方向，仅用于**相对热度**排序，不是严格分类。

| 排名 | 方向 | 命中数 | 占比 |
|---|---|---|---|
| 1 | 鲁棒 / 高效 / 流式 / 端侧（robust、efficient、quantization、pruning、edge、real-time、streaming、low-latency） | 211 | 15.3% |
| 2 | 大模型 / Speech LLM / 基础模型 | 172 | 12.5% |
| 3 | ASR / 语音识别 | 152 | 11.0% |
| 4 | 评估 / 基准 / 质量（含 MOS、可懂度、benchmark） | 117 | 8.5% |
| 5 | 发音 / 音系 / 韵律 | 111 | 8.0% |
| 6 | 多语言 / 跨语言 / 低资源 / 方言 / 语码转换 | 108 | 7.8% |
| 7 | TTS / 语音合成 | 105 | 7.6% |
| 8 | 情感 / 副语言 | 86 | 6.2% |
| 9 | 医疗 / 病理 / 临床（含痴呆、ALS、帕金森、抑郁） | 71 | 5.1% |
| 10 | 说话人（验证 / 日志 / 匿名化） | 67 | 4.9% |
| 10 | 语音增强 | 67 | 4.9% |
| 10 | 自监督表征（wav2vec / HuBERT / SSL） | 67 | 4.9% |
| 13 | 深度伪造 / 反欺骗 / 水印 | 56 | 4.1% |
| 14 | 神经编解码器 | 46 | 3.3% |
| 14 | 扩散 / 流匹配 | 46 | 3.3% |
| 16 | 空间音频 / DOA / 双耳 / HRTF | 42 | 3.0% |
| 17 | 声学事件 / 音乐 / 歌声 | 34 | 2.5% |
| 18 | 语音分离 / 目标说话人提取 / 波束成形 | 33 | 2.4% |
| 19 | 语音转换 / 声音编辑 | 25 | 1.8% |
| 20 | 助听 / 辅听 / 可穿戴 | 9 | 0.7% |

### Session 层面的分组（更接近会议实际编排）

| 主题簇 | session 数 | 代表 session |
|---|---|---|
| 合成 / TTS / VC / 编解码 / 音乐 | 25 | Long-Form Speech Synthesis、Neural Speech Codecs、Flow Matching for Speech Synthesis、Voice Conversion |
| ASR / 识别 | 19 | Robust and Efficient ASR、Code-Switching ASR、ASR Under Real-World Constraints |
| 增强 / 分离 / 去混响 / 阵列 | 18 | Real-Time, Low-Latency and Edge Speech Enhancement、SE Architectures, Adaptation and Audio Front-Ends、Multi-Channel Beamforming and Spatial Speech Enhancement、Source Separation 1/2 |
| 评估 / 基准 / 数据集 | 18 | Speech Benchmarks, Evaluation, and Resources、Benchmarking Foundation Models |
| 副语言 / 情感 / 韵律 / 对话 | 18 | Speech Emotion Recognition and Representation 1/2/3、Empathetic Dialogue and Interaction Dynamics |
| 健康 / 病理 / 临床 | 17 | Pathological Speech Assessment 1–4、Clinically Useful Speech Representations 1/2、Beyond Speech Technologies in Healthcare |
| 说话人 / 日志 / 隐私 | 15 | Speaker Diarization 1/2、Speaker Privacy Preservation and Anonymization |
| 发音 / 音系 / 语音科学 | 15 | Modeling Articulation、Neurophysiology of Speech、Speech Production and Perception 1/2 |
| 鲁棒 / 高效 / 端侧 | 14 | Efficient Inference for ASR and Speech LMs、SE Architectures, Adaptation and Audio Front-Ends |
| 多语言 / 低资源 | 12 | Indigenous Voices、Low-Resource & Endangered Language Speech Processing、Pacific Voices |
| 声学事件 / 音频分析 | 10 | Acoustic Event Detection 1–4、Audio Coding and Signal Analysis |
| 语言模型 / 音频理解 | 8 | Audio Language Models: Reasoning, Reliability, and Multimodal Understanding、Post-Training of Speech Foundation Models |
| 反欺骗 / 水印 / 安全 | 8 | Spoofing and Deepfake Detection 1–3、Audio Watermarking and Source Verification |

---

## 3. 十大方向详述

### 3.1 语音/音频大模型（Speech & Audio LLM）—— 2026 的绝对主线

从「级联 ASR→LLM」转向**原生语音 LLM**，今年的焦点已经从「能不能做」变成「做得可不可靠」：

- **推理能力**：Audio Reasoning Challenge、Audio-Cogito、Audio-DeepThinker（渐进式推理感知 RL）
- **幻觉治理**：`Silence is Golden: Mitigating Hallucinations in Large Audio-Language Models`、`Whisper Hallucination Detection and Mitigation`、`Robust ASR: Hallucinations and Biases` 专场
- **失败模式诊断**：`A Closer Look at Failure Modes in Temporal Understanding of Large Audio-Language Models`、`Entity Binding Failures in Speech LLM Reasoning`
- **后训练**：`Post-Training of Speech Foundation Models`、`FlowTTS-GRPO`（流匹配 TTS 的在线 RL）、`VoiceTTA`（RL 测试时自适应）
- **跨模态蒸馏**：`X-OPD: Cross-Modal On-Policy Distillation for Capability Alignment in Speech LLMs`
- **表征问题**：`Which Speech Representation Better Matches Text-Native Reasoning?`（语音表征与文本原生推理的对齐）

> 关键判断：这一方向已经把「评测与可靠性」内化为核心子课题——**有专门的 evaluation / benchmarking / hallucination 三个 session 群**。

### 3.2 生成式语音增强与分离 —— 扩散 / 流匹配 / Schrödinger Bridge

这是本项目最相关的一条线。今年出现明显的**方法论统一**：几乎全部新工作都建立在扩散或流匹配框架上。

- **流匹配（Flow Matching）**：`HFMSE`（谐波引导）、`PhASE-Flow`（音素条件化声学流匹配）、`FlowTTS-GRPO`
- **Schrödinger Bridge**：`Schrödinger Bridge Mamba for One-Step Speech Enhancement`、`Learnable Schrödinger Bridge and Activations for Efficient Diffusion-based SE`、`BridgeCodec`
- **吸收态离散扩散**：`Absorbing Discrete Diffusion for Speech Enhancement`
- **漂移模型（Drifting Models）**：`Speech Enhancement Based on Drifting Models`
- **解耦式生成**：`Seed-Enh: Generative Speech Enhancement in Decoupled Semantic and Timbre Spaces`
- **语言模型做增强**：`UniSE`（decoder-only 自回归 LM）、`DelayGSE`（延迟文本感知条件）、`StuPASE`（低幻觉录音室级）、`Post-Training Speech Enhancement Language Models with Perceptual Rewards`
- **编解码器令牌域增强**：`Language-Model and Codec-Token Speech Enhancement` 专场

**低时延/端侧增强**已独立成 session：`Real-Time, Low-Latency and Edge Speech Enhancement`、`SE Architectures, Adaptation and Audio Front-Ends`。相关工作如 `VAD to the Bone`（超小语音活动检测）、`μNet`（低内存整数 DSP 推理）——与本项目 [[wiki_low_latency/index]] 的约束完全同构。

**分离与提取**：`Source Separation 1/2`、`Target Speaker Extraction, Speech Separation and Audio Understanding`、`Audio-Visual and Generative Target Speaker Extraction`。趋势是**音视频联合 + 生成式**（`AV-SyncBench`、`Speech-to-See`）。

### 3.3 空间音频与阵列处理

- **HRTF/HRIR 个性化与重建**：`HRIR-Former`（无网格时域重建）、`HRTF Personalization via Sim-to-Real Neural Field`
- **双耳前端**：`BiEAR: Human Auditory-Inspired Adaptive Binaural Front-end`
- **DOA 估计**：`End-Fire Degradation-Robust DOA Estimation for Compact Linear Microphone Arrays`
- **声场/声区**：`Active Noise and Echo Control, Sound Zones and Packet-Loss Concealment`
- **多通道采集**：`Multi-Channel Processing and Specialized Acquisition (UAV, Radar, Hearables)`

> 与本项目 [[wiki_array/index]] 的对应：**紧凑阵列的端射退化鲁棒 DOA** 和 **可穿戴/助听设备的多通道前端** 是今年新出现的、值得优先精读的两类工作。整体上空间音频的 session 数（4 个 Spatial Audio + 若干多通道专场）说明该方向在 INTERSPEECH 的体量仍然稳定，但**已经明显被「神经化」**：传统 MUSIC/SRP-PHAT 更多作为对照基线或先验出现。

### 3.4 神经语音编解码器

`Neural Speech Codecs: Low-Bitrate and Disentangled Coding`、`Neural Audio Codec Architectures` 两个专场。关键词是**低码率 + 解耦**：

- `VoCodec`（低码率可流式）、`BridgeCodec`（Mamba + Schrödinger Bridge）、`An Ultra-Low-Bitrate Neural Speech Codec with Synergistic Vector Quantization`
- `Pitch-Injected Residual Adapter for Tonal Language`（声调语言特化）
- 与增强/合成打通：codec token 直接作为生成或增强的中间表示

### 3.5 自监督表征与音系分析

`InsideSSL`、`MSR-HuBERT`（多采样率自监督预训练）、`Online Predictive Coding for Dual-Mode SSL`。今年的特色是**用 SSL 模型做音系学/语言学分析**：

- `Pretrained self-supervised speech models can recognize unseen consonants`
- `Prosodic ABX: A Language-Agnostic Method for Measuring Prosodic Contrast`
- `Layer-wise Probing of wav2vec 2.0 and Whisper`（方言、辅音簇、AAE）

### 3.6 说话人技术：嵌入、日志、隐私

- **嵌入**：`Beyond Short Segments: Expanding Speaker Embeddings with Vector Archives`、`Revisiting Label-Free Speaker Embedding Enhancement with vMF Profile Likelihood`
- **日志（Diarization）**：2 个专场 + `MCA-DCF-DS`（统一日志与分离）
- **隐私 / 匿名化**：`Speaker Privacy Preservation and Anonymization`、`Speaker Privacy and Anonymization`（两个专场，明显升温）
- **与 LLM 融合**：`Speaker Verification: Architectures, Losses, and LLMs`

### 3.7 反欺骗、深度伪造与音频水印

这是**增长速度最快的方向之一**（8 个 session，且主题细分明显）：

- 泛化与溯源：`Diffusion Reconstruction towards Generalizable Audio Deepfake Detection`、`Dual-Branch Gated Fusion for Open-Set Audio Deepfake Source Tracing`、`Who Synthesized This? Joint Deepfake Detection and Generative Source Attribution`
- 鲁棒性：`Hard Positive-targeted Training`、`When Spoof Detectors Travel: Evaluation Across 66 Languages`
- 主动防御 / 水印：`A Training-Free Proactive Defense Against Partial Speech Manipulation`、`Audio Watermarking and Source Verification`
- 伦理与法规：`Safeguards for Synthetic Speech: Ethical, Technical, and Legal Perspectives`、`AI Regulation and the Technical Language of Speech Synthesis`、`Rethinking Consent Acquisition for Voice Synthesis`

### 3.8 医疗与临床语音

`Pathological Speech Assessment 1–4`（4 个专场）+ `Clinically Useful Speech Representations 1/2`，是**体量最大的垂直应用方向**：

- 认知/神经退行：痴呆、认知衰退、ALS、帕金森（`Speech and Video Biomarkers in Early Parkinson's Disease`）
- 数字生物标志物：`Reducing Measurement Noise in Digital Speech Biomarkers for ALS Monitoring`、`Contrastive Time-Proximity Pre-Training for Speech-Based Heart Failure Monitoring`
- 呼吸音 / 非语音：`Zero-Shot Respiratory Sound Classification`、`BACH: Benchmarking Audio Codecs for Bio-Acoustic Health`
- 可解释性：`From Black-Box to Clinical Insight: Multi-Stage Explainable Framework for Cognitive Impairment Detection`

### 3.9 多语言、低资源与语言多样性

呼应 Keynote 2（Steven Bird，语言多样性），今年有 `Pacific Voices`、`Indigenous Voices in Speech Science and Technology`、`Low-Resource & Endangered Language Speech Processing` 等专场：

- 数据集建设：`WazobiaSpeech`（尼日利亚语言）、`GigaAM Multilingual`、`GLAD-CSpeech`（汉语方言）
- 方法：`Upcycling Pretrained Transformers into Mixture-of-Experts for Multilingual ASR`、`GC-LoRA`、`BELLA`
- 语言政策视角：`Decolonizing Linguistic Policies in Automatic Speech Recognition`

### 3.10 评估、基准与数据集

评估本身成为一个大方向（18 个 session）：

- **TTS 评估**：3 个专场（`Speech Synthesis Evaluation 1/2`、`Speech Synthesis Evaluation and Benchmarking`）。核心问题是 MOS/MUSHRA 已不适用，需要**面向任务效用的评估**（`Is Natural Always Appropriate?`、`NV-Bench` 非语言发声合成基准）
- **ASR 评估**：`RAS: a Reliability Oriented Metric`、`WER Are We (Really)`、`Read What You Hear`（无参考假设评估）
- **大模型评估**：`UG-Bench`（大音频语言模型基准）、`AURA Score`、`PrefSQA`
- **公平性**：`The Voice Behind the Words: Quantifying Intersectional Bias in SpeechLLMs`
- **新数据集**：`Earnings25`（500 小时金融语音）、`SoniSpeech`（三模态默读语音接口）、`Dialogs`（俄语对话语料）

---

## 4. 其他主要会议与期刊

### 4.1 ICASSP 2026（2026-05-04 ~ 05-08，西班牙巴塞罗那）

主题口号 "Where Signals Meet Intelligence"。官方分类中与语音直接相关的是 **SL（Speech and Language Processing）** 和 **AA（Audio and Acoustic Signal Processing）** 两大类：

| 类别 | 子主题 |
|---|---|
| **SL** | 10.1 人类语言处理（对话、语义理解、检索摘要、解析、NLP ML、生成、问答）；10.2 多模态/跨模态语音语言处理；10.3 说话人识别/确认/反欺骗；10.4 **语音增强与提取**；10.5 语音事件检测（含情感识别）；10.6 语音生成（VC/克隆、TTS、神经声码器与编解码、音频/音乐/歌声生成、水印与反欺骗）；10.7 语音资源；10.8 语音识别（多语言、多说话人、建模、自适应）；10.9 语音翻译 |
| **AA** | 9.1 音频信号处理（增强/恢复/提取、音源分离、编码传输与表征、质量与可懂度、听觉建模与助听器、系统辨识与去混响、**声学传感器阵列处理**、基础理论算法）；9.2 声学场景与事件；9.3 声学环境处理（信道建模、空间音频录制与重放、主动降噪与回声/反馈消除）；9.4 音乐分析/处理/生成；9.5 应用（生物声学与医学声学、音频安全、音视频多媒体、数据与开源） |

**ICASSP 2026 URGENT Speech Enhancement Challenge**：Track 1 通用语音增强，Track 2 语音质量评估——与本项目增强方向直接相关，值得关注其 baseline 与评测协议。

### 4.2 IEEE/ACM TASLP（Transactions on Audio, Speech, and Language Processing）

语音方向公认的**第一档期刊**（原 TASLP，2024 年起与 ACM 合办）。近期录用工作的热点与会议高度一致：**LLM 的高效微调（PEFT）在语音多任务中的应用**、语音增强/分离的生成式建模、自监督表征分析。作为期刊，TASLP 偏好**方法完整、消融充分、有理论分析**的工作，是会议短文之后扩展投稿的首选。

### 4.3 Computer Speech & Language（Elsevier）

2026 年的特刊征稿直接反映了领域走向（按征稿时间倒序）：

| 特刊主题 | 投稿截止 |
|---|---|
| Learner Speech Processing for Closed-Loop CALL（闭环计算机辅助语言学习中的学习者语音处理） | 2027-05-31 |
| Spoken Language Generation: Methods, Evaluation, and Applications（口语生成） | 2026-12-31 |
| **Speech Processing with Wearable and Multimodal Technologies**（可穿戴与多模态语音处理：智能眼镜、耳机、助听器、头戴设备、体感传感器；涵盖噪声鲁棒性、多通道处理、**语音增强**、**源分离**、日志、识别、编码传输、可懂度预测） | 2026-12-01 |
| Speaker Characterization Beyond Words: Identity, Health and Emotion from Speech | 2026-10-31 |
| Acoustical Intelligence in the Wild: **Continual and Life-long Learning for Speech and Audio**（开放环境持续学习：非平稳噪声下的在线域自适应增强、灾难性遗忘、开放集检测、边缘设备持续学习） | 2027-05-31 |
| Evaluation of speech and speech synthesis（超越 MOS/MUSHRA 的面向任务评估） | 2026-10-31 |

> 对本项目最有价值的是 **"Speech Processing with Wearable and Multimodal Technologies"**（可穿戴/多通道增强与分离）和 **"Acoustical Intelligence in the Wild"**（非平稳噪声下的在线自适应增强）两个特刊。

### 4.4 Speech Communication（Elsevier）

偏**语音科学 + 工程**的混合定位。2026 年第 181 卷的近期文章体现了这一特征：

- 传统工程线：`Robust beamforming guided by prior directional information for speech enhancement in ship engine rooms`（先验方向信息引导的鲁棒波束成形——与本项目直接相关）
- 健康线：`An efficient lightweight Spike Neuron Network applied to Post-stroke Dysarthria speech recognition`、`A new lung disorder detection model based on graphene pattern using respiratory sounds`
- 自适应/低资源线：`Exploring LoRA variants to adapt whisper models for robust recognition of children's speech`
- 情感/感知线：`Joint acoustic–semantic alignment network for advanced speech emotion recognition`、`Perception of humanness is affected by speech content`
- 司法语音：`Detection of impersonated speech for forensic automatic speaker recognition`

### 4.5 其他值得跟踪的刊物与会议

| 名称 | 定位 |
|---|---|
| IEEE JSTSP（Selected Topics in Signal Processing） | 以特刊为主，语音/音频特刊常见，偏信号处理视角 |
| IEEE Signal Processing Letters (SPL) | 短文快报，方法类新点子的常见首发地 |
| EURASIP Journal on Audio, Speech, and Music Processing | 开放获取，音频/音乐处理 |
| JASA（Journal of the Acoustical Society of America） | 声学与语音感知/产生的权威刊，偏物理与心理声学 |
| Applied Acoustics | 应用声学、房间声学、噪声控制 |
| ICASSP / INTERSPEECH / SLT / ASRU / Odyssey / WASPAA / IWAENC | 会议矩阵：ICASSP 与 INTERSPEECH 为两大综合会；SLT/ASRU 偏识别与语言技术；Odyssey 专攻说话人；WASPAA/IWAENC 专攻音频与声学信号处理（**阵列/波束成形/去混响的主场**） |

---

## 5. 与本项目的关联与可行动建议

本项目三个 wiki（[[wiki/index]] 语音增强、[[wiki_array/index]] 声源定位、[[wiki_low_latency/index]] 超低时延因果增强）对应的三条线，在 2026 年的位置上如下：

| 本项目方向 | 2026 领域位置 | 值得优先跟踪的具体线索 |
|---|---|---|
| **语音增强**（[[wiki/index]]） | 已被扩散/流匹配统一，正被 Speech LLM 渗透 | `FlowSE-GRPO`、`Seed-Enh` 解耦语义/音色、`Absorbing Discrete Diffusion`、codec-token 域增强 |
| **超低时延因果增强**（[[wiki_low_latency/index]]） | INTERSPEECH 已设独立 session，是明确的活跃赛道 | `Real-Time, Low-Latency and Edge Speech Enhancement` 专场；`μNet`（整数 DSP 低内存）、`VAD to the Bone`（超小 VAD）、`Pushing the Limits of Compression: Sub-1-Bit Conformer` |
| **声源定位 / 阵列**（[[wiki_array/index]]） | 体量稳定但明显"神经化"；传统算法退居基线/先验 | `End-Fire Degradation-Robust DOA`（紧凑线阵）、`HRTF Personalization via Sim-to-Real Neural Field`、`BiEAR` 双耳前端、`NeuralMUSIC`（神经协方差 + MUSIC） |
| **多通道增强 + 定位联合** | 今年以「目标说话人提取」和「音视频联合」为主要出口 | `Enroll-on-Wakeup`（唤醒即注册的目标说话人提取对比研究）、`AV-SyncBench`、`Multi-Channel, Beamforming and Spatial Speech Enhancement` 专场 |

**三条可落地的建议**：

1. **投稿出口**：低时延增强可瞄准 Computer Speech & Language 的 "Wearable and Multimodal" 特刊（2026-12-01 截止）或 "Acoustical Intelligence in the Wild"（2027-05-31）；阵列/波束成形可瞄准 IWAENC / WASPAA / ICASSP AA 类。
2. **方法借鉴**：今年的增强主流是流匹配与 Schrödinger Bridge，若本项目仍以因果 GRU/短窗 STFT 为基线，值得评估**一步式 SB / 流匹配在严格因果约束下的可行性**（注意这与 [[wiki_low_latency/index]] 的"不读未来样本"约束存在张力，需单独审计 look-ahead）。
3. **评测对齐**：INTERSPEECH 2026 与 ICASSP 2026 都强化了评测专场。建议在实验记录中显式对齐 DNSMOS SIG/BAK/OVL 分层报告与 SIG–BAK trade-off，这已是该赛道的默认要求。

---

## 6. 方法与局限说明

- **数据来源**：INTERSPEECH 2026 的 session 与论文标题来自 ISCA Archive 官方索引页（`isca-archive.org/interspeech_2026/index.html`），本地抓取后解析，共 184 个 session、1379 条论文记录。
- **统计口径**：第 2 节的关键词统计基于**论文标题**的字符串匹配，一个标题可命中多个方向，因此各行占比之和大于 100%；该表用于相对热度排序，**不是严格的论文分类**，也不等同于最终录用数（可能仍有少量论文未进入索引）。
- **ICASSP 2026**：主题分类来自官方 paper topics 页面；由于会议已于 2026 年 5 月举行，具体录用论文的分布未逐篇统计。
- **期刊部分**：TASLP 的"热点"为定性归纳（IEEE Xplore 未提供可批量统计的公开分类）；Computer Speech & Language 与 Speech Communication 的信息来自官方征稿页与卷目页，**特刊截止日期以官方页面为准**。
- 本报告是**文献与会议趋势调研**，不包含任何模型训练或复现；所引论文的结论强度未经独立验证。
