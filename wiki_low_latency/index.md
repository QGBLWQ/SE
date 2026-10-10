---
title: 严格因果超低时延语音增强 Wiki 内容目录
type: index
created: 2026-09-16
updated: 2026-10-07
tags:
  - index
  - strict-causal
  - ultra-low-latency
  - speech-enhancement
  - speech-preservation
---

# 严格因果超低时延语音增强 Wiki

> 方向边界：在不读取未来观测样本的前提下，面向实时通信、嵌入式和端侧设备，研究约 2 ms 算法延迟下的噪声抑制与人声保留。

## 综述

- [[wiki_low_latency/overview|严格因果超低时延语音增强 Wiki 综述]]
- [[wiki_low_latency/方法全景：动机·前后端·网络设计|**方法全景：动机、前后端处理与网络设计**]] — 30 篇横向概括：动机地图（9 类矛盾）· 前后端处理（5 条前端路线 + 3 种砍延迟手法 + 前端配置总表）· 网络设计（5 种骨干 + 8 项延迟判据）
- [[ultra_low_latency_causal_se/research_map|已有研究地图与选题建议]]

## 方向边界

- **硬约束**：strict causal、约 2 ms algorithmic latency、streaming batch=1。
- **优先任务**：单通道、16 kHz 起步的低 SNR 语音增强/噪声抑制。
- **核心质量目标**：降低噪声的同时减少弱辅音、气声、音节边缘和有声周期结构的误抑制。
- **必须区分**：算法延迟、模型计算延迟和 capture-to-playback 端到端延迟；`RTF < 1` 不能替代 deadline 证据。

## 实体 (Entities)

*模型、架构、运行时与部署组件；已摄取论文均建立对应实体页，后续只补充审核发现。*

- [[wiki_low_latency/entities/GCFSnet|GCFSnet]] — 低比特率双耳链路、复数 filter-and-sum 与量化感知部署
- [[wiki_low_latency/entities/CRUSE-Latency-Study|CRUSE latency study]] — 统一比较超低算法延迟前端与模型规模
- [[wiki_low_latency/entities/SlowFast-SSM|SlowFast-SSM]] — 计算高效的低时延状态空间增强
- [[wiki_low_latency/entities/STFT-Very-Low-Latency-SE|短窗 STFT 低时延增强]] — 窗函数、look-ahead 与算法延迟
- [[wiki_low_latency/entities/On-TasNet|On TasNet]] — 因果 learned-filterbank 单说话人增强
- [[wiki_low_latency/entities/FSB-LSTM|FSB-LSTM]] — full-band/sub-band 集成建模
- [[wiki_low_latency/entities/Noise-Suppression-Losses|噪声抑制损失]] — 语音失真与 ASR 影响
- [[wiki_low_latency/entities/Hybrid-Continuity-Loss|Hybrid Continuity Loss]] — 降低过抑制的连续性损失
- [[wiki_low_latency/entities/Uncertainty-Aware-SE|不确定性感知增强]] — 用不确定性调节抑制风险
- [[wiki_low_latency/entities/PercepNet|PercepNet]] — 感知、谐波与包络保留
- [[wiki_low_latency/entities/DeepFilterNet2|DeepFilterNet2]] — 低复杂度复数深滤波
- [[wiki_low_latency/entities/DCCRN|DCCRN]] — 复数谱与相位感知增强
- [[wiki_low_latency/entities/DPCRN|DPCRN]] — 双路径复数卷积循环增强
- [[wiki_low_latency/entities/RT-SEMamba|RT-SEMamba]] — Mamba 与渐进式知识蒸馏
- [[wiki_low_latency/entities/Teacher-Student-WaveUNet|Teacher-Student Wave-U-Net]] — 离线 teacher → 在线分块 student（6.71 ms）
- [[wiki_low_latency/entities/Two-Step-KD-Tiny-SE|Two-Step KD Tiny SE]] — 两步蒸馏、62 k 参数 student（32 ms 前端）
- [[wiki_low_latency/entities/Distil-DCCRN|Distil-DCCRN]] — AT-KL 特征蒸馏的小规模 DCCRN
- [[wiki_low_latency/entities/RaD-Net-2|RaD-Net 2]] — 因果两阶段修复+去噪、复数轴向自注意力
- [[wiki_low_latency/entities/Dynamic-Frequency-Adaptive-KD|Dynamic Frequency-Adaptive KD]] — 频率自适应蒸馏权重（跨域方法学类比）
- [[wiki_low_latency/entities/DISPATCH|DISPATCH]] — 选择性 patch 蒸馏
- [[wiki_low_latency/entities/Privileged-Self-Distillation|Privileged Self-Distillation]] — 特权信息蒸馏（推荐系统，跨域参照）
- [[wiki_low_latency/entities/LaCo-SENet|LaCo-SENet]] — 非对称 padding 实现时延可配置（12.5–200 ms，1.37M）
- [[wiki_low_latency/entities/RT-Tango|RT-Tango]] — 双耳分布式助听器增强（GRNN + 非对称 STFT + FRS，8 ms）
- [[wiki_low_latency/entities/PSMSE|PSMSE]] — 并行脉冲 Mamba（0.26M / 0.11 G/s，30 ms）
- [[wiki_low_latency/entities/Skip-DPCRN|Skip-DPCRN]] — 并行 RNN 推理期状态跳过 + VAD 引导（48 ms）
- [[wiki_low_latency/entities/D-GRU|D-GRU]] — 神经元级动态门控，零额外参数
- [[wiki_low_latency/entities/Tsunoo-Causal-SSL-SE|Tsunoo 因果 SSL SE]] — 因果 SSL 特征 + 未来语义 token 预测 MTL（延迟账本为空）
- [[wiki_low_latency/entities/FastEnhancer|FastEnhancer]] — 5 档流式族（92K/262M/RTF 0.022）；「MACs ≠ 速度」的最强证据集合
- [[wiki_low_latency/entities/Early-Exit-Conv-FSENet|Early-Exit Conv-FSENet]] — 4 级 exit ladder + one-shot GRU router；STM32N6 真机 int8 实测（82–137 µs/MMAC）
- [[wiki_low_latency/entities/GTCRN|GTCRN]] — **"超轻量"档的锚点**（23.7K/39.6 MMACs per second，被 4 篇同时引用）；ERB 频带压缩 + G-DPRNN + GT-Conv + SFE/TRA，hop 16 ms，**无 RTF / STFT center 未报告**
- [[wiki_low_latency/entities/PrimeK-Net|PrimeK-Net]] — **LaCo-SENet 的骨干与"非因果质量上界"**（1.41M，PESQ 3.61 = 本库同类最高）；GPFCA（SCA + 素数核 GPFN {3,11,23,31}）+ DSDDB，复杂度压到 DDB 的 **12.67%**；**非因果**、STFT 400/400/100（25 ms/6.25 ms）、**无任何延迟/RTF/硬件数据 ⇒ 算力证据等级 L0**
- [[wiki_low_latency/entities/LiSenNet|LiSenNet]] — **"超轻量三角"中参数第二小**（37k / 56 MMACs per second，PESQ **3.07** 反超 FSPEN）；子带 **stride 差异化**（低频 1 / 高频 3）+ DPR + **ConvGLU 容量补偿** + 可选**帧级噪声检测器**；**纯预印本**（投稿 ICASSP 2025 未中）、hop 16 ms、**无算法延迟 / STFT center 未报告**、是库内**唯一有外部独立复训值**的超轻量模型
- [[wiki_low_latency/entities/HALO|HALO]] — **半帧率可学习算子**（GTCRN+HALO 46.87k / 32.85 M MAC/s / PESQ 2.198）；把 STFT **重叠引入的时域冗余**当独立算力瓶颈，骨干前降帧率（可学习动态卷积融合相邻两帧）+ 骨干后恢复，**不改 STFT 流程、不增算法延迟**；**论文自陈不降峰值每步算力**、无 RTF、无算法延迟绝对值 ⇒ **算力证据 L0**
- [[wiki_low_latency/entities/LCA-Latency-Control-Adapter|LCA]] — **运行时延迟旋钮**（单模型 7 档 5–650 ms，MACs 恒定 1.46 G/s，参数 16.5/24.5 M vs 多模型 104.1 M）；LAM 用膨胀卷积二值因果 pattern 组合出 $T_{la}=\sum b_i 2^{i-1}$；**§3.2 给出与库内逐字同构的算法延迟定义**（本库口径首次获外部正式发表论文背书）；最低 5 ms、其余 6 档全依赖 lookahead ⇒ **不可用，但方法论价值高**
- [[wiki_low_latency/entities/SEMamba++|SEMamba++]] — **频率建模工具箱**（2.7M / RTF 0.021 @A6000，VCTK-GSR test UTMOS 3.55 / OVRL 3.14，DNS2020 test OVRL 3.206）；Frequency GLP（**FAN 直接作用于频率轴**捕捉周期性 + 卷积局部，**并联**而非串联）+ 多分辨率并行 TFDP（**仅频率轴下采样**）+ 可学习 softplus 映射 + LSGAN；**非因果离线 GSR**，**自陈 GLP 无法直接用于采样率无关场景**
- [[wiki_low_latency/entities/TF-Weighted-Losses|TF-Weighted Losses]] — **"哪里该增强、哪里不该杀语音"的损失侧答案**；$w=g_{SIR}\cdot g_{SP}\cdot(1+k\sigma(SF))$，把权重压在"语音活跃但 SIR 低"的强竞争 bin；辅音 PA 34.0→36.1（WN）/ 43.6→45.5（SSN）；**但 SDR/SAR/FW-SDR 普遍略降**，且**增益只在中高 SIR、极低 SIR 反转**；多通道双耳助听器场景，**不可外推单通道**
- [[wiki_low_latency/entities/Schrodinger-Bridge-Mamba|SBM]] — **生成式一步推理**（3.93M / RTF 0.0048 全表最低，比 SB-NCSN++(50) 快 160×）；薛定谔桥 OT 中间态当训练"锚点" + Mamba 递推结构学最优控制 ⇒ **训练期把 SB 蒸馏进 Mamba 动力学**；DNS Real Recordings 全项最高；**但论文 "under 40 ms" 漏计 30 ms 窗（实际 50–70 ms）**、半因果（2–4 帧 lookahead）、PESQ/ESTOI 仍输给判别式 ZipEnhancer

> 后续补充：跨论文统一实体别名、目标硬件实现和实测 p99 deadline 证据。

## 概念 (Concepts)

*延迟账本、严格因果性、语音保留、过抑制与端侧评估；已摄取论文均建立对应概念页。*

- [[wiki_low_latency/concepts/低比特率双耳特征链路]] — 延迟/量化跨耳特征作为低时延增强的辅助条件
- [[wiki_low_latency/concepts/2409.10358-ultra-low-latency-benchmark|超低时延基准与前端账本]]
- [[wiki_low_latency/concepts/2411.02019-slowfast-ssm|SlowFast 状态空间建模]]
- [[wiki_low_latency/concepts/2204.09911-short-asymmetric-stft|短窗与非对称 STFT]]
- [[wiki_low_latency/concepts/2103.14882-causal-tasnet|因果 TasNet 与竞争说话人]]
- [[wiki_low_latency/concepts/2304.08707-full-sub-band-modeling|Full-/sub-band 集成建模]]
- [[wiki_low_latency/concepts/2111.11606-speech-distortion-losses|语音失真—ASR 损失权衡]]
- [[wiki_low_latency/concepts/2203.16843-continuity-loss|连续性损失与过抑制]]
- [[wiki_low_latency/concepts/2305.08744-uncertainty-aware-suppression|不确定性感知抑制]]
- [[wiki_low_latency/concepts/2008.04259-perceptual-speech-preservation|感知驱动人声保留]]
- [[wiki_low_latency/concepts/2205.05474-deep-filtering|复数深滤波与嵌入式实时]]
- [[wiki_low_latency/concepts/2008.00264-complex-phase-enhancement|复数相位增强]]
- [[wiki_low_latency/concepts/2107.05429-dual-path-recurrent-context|双路径长上下文]]
- [[wiki_low_latency/concepts/2608.12099-mamba-distillation|实时 Mamba 蒸馏]]
- [[wiki_low_latency/concepts/nakaoka21-wave-unet-distillation|在线分块 Wave-U-Net 蒸馏]]
- [[wiki_low_latency/concepts/2309.08144-two-step-distillation|两步式蒸馏 vs 加权混合]]
- [[wiki_low_latency/concepts/2408.04267-feature-distillation|特征级蒸馏（AT-KL）]]
- [[wiki_low_latency/concepts/2406.07498-two-stage-causal-repair|两阶段级联的因果性与延迟累加]]
- [[wiki_low_latency/concepts/2502.04711-frequency-adaptive-distillation|频率自适应蒸馏权重]]
- [[wiki_low_latency/concepts/2509.15922-selective-patch-distillation|选择性 patch 蒸馏]]
- [[wiki_low_latency/concepts/2607.27055-privileged-information-distillation|特权信息蒸馏（跨域类比）]]
- [[wiki_low_latency/concepts/2606.19688-latency-configurable-asymmetric-padding|非对称 padding 与选择性状态更新]] — 时延旋钮、双缓冲流式、SSU
- [[wiki_low_latency/concepts/2607.01834-distributed-binaural-low-latency|分布式双耳低时延五件套]] — ERB 压缩 / GRNN / 非对称 STFT / FRS / 在线 SCM
- [[wiki_low_latency/concepts/S2542660526001769-spiking-mamba-streaming|脉冲神经网络与 SSM 的并行融合]] — 事件驱动稀疏性、并行分支、spike 发放率
- [[wiki_low_latency/concepts/2207.11108-inference-skipping-parallel-rnn|推理期状态跳过与更新率控制]] — 并行 RNN 是规避伪影的前提、VAD 引导跳步
- [[wiki_low_latency/concepts/2408.12425-dynamic-gated-rnn|神经元级动态门控]] — 固定比例稀疏 vs 整步跳过、每步算力恒定
- [[wiki_low_latency/concepts/2412.19248-causal-ssl-semantic-prediction|因果 SSL 与未来语义预测]] — 截断式因果化的代价、one-stage VQ、因果专属的语义预测 MTL
- [[wiki_low_latency/concepts/2509.21867-speed-optimized-streaming-design|速度优化流式设计]] — 可融合性、算子分轴、流式化代价与结构审计清单
- [[wiki_low_latency/concepts/2609.29867-compute-matched-dynamic-depth|算力对齐下的动态深度]] — 算力对齐是前提、早退增益的归属、真机 MACs 排序失效、gate-sum 评测陷阱
- [[wiki_low_latency/concepts/gtcrn-2024-ultralight-subband-grouped-dprnn|超轻量锚点的口径与结构审计]] — 锚点数值必须钉死、分组是三条正交压缩轴、补偿模块的双坐标性价比、引用 ShuffleNetV2 却不报速度、声明级因果七项清单
- [[wiki_low_latency/concepts/2502.19906-prime-kernel-multiscale-dense-block|素数核多尺度与稠密块的复杂度记账]] — 素数核为何反直觉地省算力的两条论证、DSDDB 12.67% 的独立复核、SCA 的全局池化因果缺口、「零算术变化对照」在库中的三次出现
- [[wiki_low_latency/concepts/2409.13285-subband-stride-and-convglu-compensation|子带 stride 差异化与 ConvGLU 容量补偿]] — 零预算重新分配、三种分组压缩的正交性、补偿模块的性价比对照、由 N 扫描导出的**边际收益递减曲线**、动态算力峰值为负的反例
- [[wiki_low_latency/concepts/halo-2026-half-frame-rate-operator|重叠帧冗余可被可学习算子压缩]] — 与架构瘦身正交的算力轴、**朴素抽帧+复制比基线更差**的边界条件、结构性平均-峰值分离、外推帧（奇数帧）的代价
- [[wiki_low_latency/concepts/lca-2026-latency-control-adapter|延迟应是可配置的运行时参数]] — LAM/LCA 机制、参数共享为何是自然选择、**库内延迟账本口径首次获外部背书**（§3.2）、旋钮的另一端在库内约束之外
- [[wiki_low_latency/concepts/semamba-pp-2026-frequency-glp|频率轴的全局-局部-周期应并联建模]] — FAN 放置位置的新颖性、并联 vs 串联的选择性、**IoU + Wilcoxon 把"互补性"落成统计量**、频率轴全连接与变采样率的冲突
- [[wiki_low_latency/concepts/tf-weighted-sdr-2026|TF 加权应按语音-噪声竞争强度分配]] — 竞争感知加权的三个因子、**有效区间有上下界**（极低 SIR 反转、SSN 下纯学习失败）、**结构化先验优于纯学习**（与 SEMamba++ 跨层同构）
- [[wiki_low_latency/concepts/sbm-2026-schrodinger-bridge-mamba|训练范式应与骨干归纳偏置对齐]] — SB 与 Mamba 的结构对应、**零推理开销**的范式收益、**吞吐 vs 算法延迟双轴结论**（生成式靠近实时只在吞吐轴上成立）
- [[wiki_low_latency/concepts/严格因果与算法延迟|严格因果与算法延迟]] — 逐层因果、算法延迟和端到端 deadline 的区分
- [[wiki_low_latency/concepts/低时延前端与延迟账本|低时延前端与延迟账本]] — window、hop、look-ahead、计算和 I/O 的分账
- [[wiki_low_latency/concepts/低 SNR 人声保留评估|低 SNR 人声保留评估]] — 低 SNR 下的人声保真与过抑制评估

> 上述 3 个共用概念页用于统一各论文的验收字段；后续可继续补充 speech-preservation scorecard、SPP/gain floor、SIG–BAK trade-off 和 deadline robustness 对比页。

## 资料摘要 (Sources)

- [[wiki_low_latency/sources/2023/GCFSnet 2023]] — 低比特率双耳链路与超低时延多通道增强（本轮随机抽取）
- [[wiki_low_latency/sources/2024/Ultra-Low Latency Speech Enhancement Comprehensive Study 2024]] — 统一超低时延前端/模型对照
- [[wiki_low_latency/sources/2024/SlowFast-SSM 2024]] — SlowFast-SSM 计算效率
- [[wiki_low_latency/sources/2022/STFT-Domain Very Low Algorithmic Latency 2022]] — 短窗 STFT 与很低算法延迟
- [[wiki_low_latency/sources/2021/On TasNet Low-Latency SE 2021]] — 因果 TasNet 低时延增强
- [[wiki_low_latency/sources/2023/FSB-LSTM 2023]] — full-/sub-band 低复杂度建模
- [[wiki_low_latency/sources/2021/Noise Suppression Losses 2021]] — 损失函数、语音失真与 ASR
- [[wiki_low_latency/sources/2022/Hybrid Continuity Loss 2022]] — 连续性损失与过抑制
- [[wiki_low_latency/sources/2023/Uncertainty-Aware Speech Enhancement 2023]] — 不确定性感知增强
- [[wiki_low_latency/sources/2020/PercepNet Low-Latency Direction 2020]] — 感知驱动全带实时增强
- [[wiki_low_latency/sources/2022/DeepFilterNet2 2022]] — 嵌入式全带深滤波
- [[wiki_low_latency/sources/2020/DCCRN Low-Latency Direction 2020]] — 复数卷积循环与相位
- [[wiki_low_latency/sources/2021/DPCRN Low-Latency Direction 2021]] — 双路径复数循环
- [[wiki_low_latency/sources/2026/RT-SEMamba 2026]] — 渐进式知识蒸馏实时 Mamba
- [[wiki_low_latency/sources/2021/Teacher-Student Wave-U-Net 2021]] — 离线 teacher 引导低时延在线 student（ICASSP，无 arXiv）
- [[wiki_low_latency/sources/2023/Two-Step Knowledge Distillation for Tiny SE 2023]] — 两步蒸馏、tiny student
- [[wiki_low_latency/sources/2024/Distil-DCCRN 2024]] — AT-KL 特征蒸馏的小规模 DCCRN
- [[wiki_low_latency/sources/2024/RaD-Net 2 2024]] — 因果两阶段修复+去噪
- [[wiki_low_latency/sources/2025/Dynamic Frequency-Adaptive KD 2025]] — 频率自适应蒸馏权重
- [[wiki_low_latency/sources/2025/DISPATCH 2025]] — 选择性 patch 蒸馏
- [[wiki_low_latency/sources/2026/Privileged Self-Distillation 2026]] — 特权信息蒸馏（推荐系统，跨域参照）
- [[wiki_low_latency/sources/2026/LaCo-SENet 2026]] — 非对称 padding 时延族、12.5–200 ms
- [[wiki_low_latency/sources/2026/RT-Tango 2026]] — 分布式双耳助听器、8 ms 论文级算法延迟
- [[wiki_low_latency/sources/2026/PSMSE 2026]] — 并行脉冲 Mamba 轻量流式（期刊长文）
- [[wiki_low_latency/sources/2022/Skip-DPCRN 2022]] — 并行 RNN 推理期跳过、VAD 引导
- [[wiki_low_latency/sources/2024/D-GRU 2024]] — 神经元级动态门控、零额外参数
- [[wiki_low_latency/sources/2024/Tsunoo Causal SSL Semantic 2024]] — 因果 SSL + 未来语义预测 MTL（ICASSP 2025）
- [[wiki_low_latency/sources/2025/FastEnhancer 2025]] — 速度优化流式族、RNNFormer、Pareto 前沿
- [[wiki_low_latency/sources/2026/Early Exit Compute-Matched 2026]] — 算力对齐下的逐帧早退、STM32N6 真机 int8 延迟
- [[wiki_low_latency/sources/2024/GTCRN 2024]] — **已正式出版（ICASSP 2024, pp. 971–975, DOI 10.1109/ICASSP48485.2024.10448310）**；超轻量子带增强、ERB 压缩 + 分组 DPRNN，23.7K/39.6 MMACs
- [[wiki_low_latency/sources/2025/PrimeK-Net 2025]] — **已正式出版（ICASSP 2025, arXiv:2502.19906）**；素数核分组频率卷积注意力 + 稠密块，1.41M / PESQ 3.61，**非因果**（LaCo-SENet 的质量上界与骨干来源）
- [[wiki_low_latency/sources/2024/LiSenNet 2024]] — **纯预印本（arXiv:2409.13285，投稿 ICASSP 2025 未中）**；超轻量子带增强，37k / 56M / PESQ 3.07；被 FastEnhancer 点名批评并**替它补做了流式化改造**（^b→^c）
- [[wiki_low_latency/sources/2026/HALO 2026]] — **已正式出版（Interspeech 2026, pp. 2999–3003, DOI 10.21437/Interspeech.2026-601）**；半帧率可学习算子压缩 STFT 重叠冗余，DNS3 上 6 个轻量骨干一致提升；**论文自陈不降峰值算力**
- [[wiki_low_latency/sources/2026/Latency Controllable SE 2026]] — **已正式出版（Interspeech 2026, pp. 3009–3014, DOI 10.21437/Interspeech.2026-2997）**；LAM/LCA 运行时延迟旋钮、单模型 7 档；**§3.2 的算法延迟定义与库内口径逐字同构**
- [[wiki_low_latency/sources/2026/SEMamba++ 2026]] — **已正式出版（Interspeech 2026 [Long Track], pp. 5166–5175, DOI 10.21437/Interspeech.2026-665）**；通用语音修复的频率 GLP + 多分辨率并行 TFDP；**非因果离线**，与 PrimeK-Net / LaCo-SENet 共享 400/100 前端
- [[wiki_low_latency/sources/2026/TF Weighted Losses 2026]] — **已正式出版（Interspeech 2026, pp. 7075–7079, DOI 10.21437/Interspeech.2026-3416）**；语音-噪声竞争感知的 TF 加权 SDR；多通道双耳助听器 + FaSNet，**主动做了 Wilcoxon 显著性检验**
- [[wiki_low_latency/sources/2026/Schrodinger Bridge Mamba 2026]] — **已正式出版（Interspeech 2026, pp. 1363–1368, DOI 10.21437/Interspeech.2026-682）**；薛定谔桥 + Mamba 一步生成式增强（华为）；RTF 0.0048 全表最低；**算法延迟口径漏计 30 ms 窗**

> 37 篇原件均已完成逐篇 PDF 摄取；索引只汇总页面入口，不替代各 source 页中的证据边界和质量 warning。> **知识蒸馏子群（7 篇，2026-09-18 新增）**：上述 2021/2023/2024/2025/2026 中的 7 篇构成「蒸馏 + 低时延」子群。需注意其中 `Dynamic Frequency-Adaptive KD` 与 `Privileged Self-Distillation` **不面向低时延语音增强**（前者为频率自适应蒸馏的方法学类比，后者为推荐系统跨域参照），不可与其他篇横向排名。
> **2026-09-20 新增 3 篇**：`LaCo-SENet`、`RT-Tango`、`PSMSE`。三篇都**不满足**约 2 ms 硬约束（12.5 ms / 8 ms / 30 ms），但分别提供了本库目前最完整的逐层因果证据链、最完整的分布式双耳账本、以及最低 MACs 的模型；其中 `RT-Tango` 与 `PSMSE` 各自带有一处必须随结论一起读的方法论 caveat（在线 SCM 无限预热、Mamba 状态不跨帧）。
> **2026-09-22 新增 2 篇（推理期动态算力子群）**：`Skip-DPCRN`（48 ms）与 `D-GRU`（未报任何延迟）。两篇是同一问题谱系的**正反两面**：Skip-DPCRN 跳**整步**状态更新（省平均算力 33%，但峰值只降 ~15%、算力随输入波动），D-GRU 跳**神经元**（固定比例，每步算力恒定）。D-GRU 在 Related Work 里点名批评的 Skip RNN 系列，引文 [31] 正是 Skip-DPCRN。**注意两篇都不满足约 2 ms**，且都缺端侧 p99 与人声保留证据。
> **2026-09-24 新增 1 篇（语义先验子群）**：`Tsunoo Causal SSL Semantic 2024`（arXiv:2412.19248，ICASSP 2025）。它是本库**首篇以"SSL 语义 token + 未来语义预测"为机制的因果 SE**，也是目前**延迟账本最空**的一篇——**未报告任何延迟、RTF、MACs、参数量、目标硬件，STFT 前端参数也全缺**。其因果性判定为 `paper-claimed-causal`（**近似实现**：限制输入为过去帧 + 只取末帧，Eq. 5，非架构级改造），且该实现属**重算型**（$O(T^2)$ 量级）而非流式型。正面价值是一条干净原则：**"预测未来语义"在因果下 +0.05 PESQ、非因果下 Δ=0.00**（Table IV C1/C2 vs N1/N2）。
> **2026-09-26 新增 1 篇（速度优化子群）**：`FastEnhancer 2025`（arXiv:2509.21867，首尔大学）。它是本库**"MACs ≠ 速度"命题最完整的证据集合**——同一个 BN→LN 替换在**参数量与 MACs 完全不变**下把 RTF 抬高 27%（Xeon）/12%（M1），时间轴 kernel 1→3 使 Para. 翻倍、RTF 涨 27%/42% 而 **SISDR/STOI 一格不动**；FastEnhancer-B 以 92K/262M 取得表内第二低 RTF 0.022，**MACs 比 GTCRN 高 6.5× 却快 2.7×**。因果性为 `paper-claimed-causal`（结构证据较强：时间轴 kernel 恒 1 + 单向 GRU + 频率轴注意力不需 cache，**但仍无逐层 padding/state certificate，STFT 帧锚定未报告**）。**无任何算法延迟数字**；本库按 Table 1 的 $H$ 列推得 hop = 16/10/6.25 ms ⇒ 延迟下界在**十几毫秒**量级（若 center=True 再加 16 ms 前端），**不是 2 ms 候选**。
> **2026-09-27 新增 1 篇（算力对齐的动态深度）**：`Early Exit Compute-Matched 2026`（arXiv:2609.29867，GN A/S + DTU）。它是本库**算力证据最硬**的一篇（STM32N6 真机 int8 逐图实测），也是**第一篇先做算力对齐、再问"动态是否值得"**的论文。结论是**动态深度在语音密集集上几乎不值**：修掉 exits 的非单调性后，mono-repaired 前沿与 routed 前沿**几乎重合（差 <0.01 PESQ）**。它同时给出两条对全库有普适价值的方法论资产：**名义 MACs 在真实 NPU 上会给出错误排序**（µs/MMAC 差 1.7×；同 MMAC/s 却差 33 % 延迟；MACs 多 21 % 却快 15 %），以及**"gated sum"式离线评测会制造虚假的动态收益**。与 FastEnhancer 的关系：**同样主张"MACs ≠ 速度"，但机理归因不同**——FastEnhancer 归因于**算子可融合性/内存操作**，本篇归因于**accelerator launch 次数与 NPU 利用率**。**注意venue：两篇均为纯 arXiv 预印本**（见各自 source 页的 `venue_status`）。

## 主题 (Topics)

*跨模型比较和研究问题页面；论文已摄取，统一比较待后续建立。*

> 待添加：2 ms 方法对比、低 SNR 人声保留、延迟/质量 Pareto、严格因果部署审计。

## 关联 Wiki

- [[wiki/index|语音增强与音源分离 Wiki]] — 一般语音增强、音源分离和传统/端到端方法
- [[wiki_array/index|声源定位与阵列处理 Wiki]] — DOA、波束成形和空间滤波前置任务
- [[wiki/entities/RNNoise|RNNoise]] — 极低复杂度实时增强的历史参照
- [[wiki/entities/Conv-TasNet|Conv-TasNet]] — 短窗 learned-filterbank/时域掩蔽的架构参照

## 本轮已归档的论文原件与摄取状态

论文 PDF 保存在 `raw/papers/low_latency_causal_se/`。14 篇原件均已完成 PDF 摄取；
2307.08858 是首篇随机抽取样例，其余 13 篇随后按同一格式完成 source/entity/concept 页面。
**2026-09-18 追加 7 篇知识蒸馏子群论文**（见下表 #15–#21），其中 6 篇来自 `raw/articles/` 同源副本。

| # | arXiv ID | 标题 | 年份 | 方向角色 | 本地 PDF |
|---:|---|---|---:|---|---|
| 1 | `2409.10358` | Ultra-Low Latency Speech Enhancement - A Comprehensive Study | 2024 | 统一低时延对照与延迟研究 | [PDF](../raw/papers/low_latency_causal_se/2409.10358.pdf) |
| 2 | `2411.02019` | Modulating State Space Model with SlowFast Framework for Compute-Efficient Ultra Low-Latency Speech Enhancement | 2024 | SlowFast-SSM、低 MAC | [PDF](../raw/papers/low_latency_causal_se/2411.02019.pdf) |
| 3 | `2204.09911` | STFT-Domain Neural Speech Enhancement with Very Low Algorithmic Latency | 2022 | 短/非对称 STFT、低算法延迟 | [PDF](../raw/papers/low_latency_causal_se/2204.09911.pdf) |
| 4 | `2103.14882` | On TasNet for Low-Latency Single-Speaker Speech Enhancement | 2021 | 因果 TasNet、竞争说话人 | [PDF](../raw/papers/low_latency_causal_se/2103.14882.pdf) |
| 5 | `2304.08707` | Neural Speech Enhancement with Very Low Algorithmic Latency and Complexity via Integrated Full- and Sub-Band Modeling | 2023 | full-/sub-band LSTM | [PDF](../raw/papers/low_latency_causal_se/2304.08707.pdf) |
| 6 | `2111.11606` | Effect of noise suppression losses on speech distortion and ASR performance | 2021 | 损失函数、语音失真与 ASR | [PDF](../raw/papers/low_latency_causal_se/2111.11606.pdf) |
| 7 | `2203.16843` | A Hybrid Continuity Loss to Reduce Over-Suppression for Time-domain Target Speaker Extraction | 2022 | 连续性损失、过抑制 | [PDF](../raw/papers/low_latency_causal_se/2203.16843.pdf) |
| 8 | `2305.08744` | Integrating Uncertainty into Neural Network-based Speech Enhancement | 2023 | 不确定性与保守抑制 | [PDF](../raw/papers/low_latency_causal_se/2305.08744.pdf) |
| 9 | `2008.04259` | A Perceptually-Motivated Approach for Low-Complexity, Real-Time Enhancement of Fullband Speech | 2020 | PercepNet、感知/周期性保留 | [PDF](../raw/papers/low_latency_causal_se/2008.04259.pdf) |
| 10 | `2205.05474` | DeepFilterNet2: Towards Real-Time Speech Enhancement on Embedded Devices for Full-Band Audio | 2022 | deep filtering、嵌入式实时 | [PDF](../raw/papers/low_latency_causal_se/2205.05474.pdf) |
| 11 | `2307.08858` | Low bit rate binaural link for improved ultra low-latency low-complexity multichannel speech enhancement in Hearing Aids | 2023 | 助听器、多通道/双耳链路 | [PDF](../raw/papers/low_latency_causal_se/2307.08858.pdf) |
| 12 | `2008.00264` | DCCRN: Deep Complex Convolution Recurrent Network for Phase-Aware Speech Enhancement | 2020 | 复数谱与相位感知参照 | [PDF](../raw/papers/low_latency_causal_se/2008.00264.pdf) |
| 13 | `2107.05429` | DPCRN: Dual-Path Convolution Recurrent Network for Single Channel Speech Enhancement | 2021 | 双路径 CRN、长上下文参照 | [PDF](../raw/papers/low_latency_causal_se/2107.05429.pdf) |
| 14 | `2608.12099` | RT-SEMamba: Real-Time Speech Enhancement Mamba via Progressive Knowledge Distillation | 2026 | Mamba、蒸馏与实时参照 | [PDF](../raw/papers/low_latency_causal_se/2608.12099.pdf) |

### 2026-09-18 追加：知识蒸馏子群（7 篇）

| # | arXiv/DOI | 标题 | 年份 | 方向角色 | 因果与延迟结论 | 本地 PDF |
|---:|---|---|---:|---|---|---|
| 15 | `2309.08144` | Two-Step Knowledge Distillation for Tiny Speech Enhancement | 2023 | 两步蒸馏、tiny student | teacher **因果**；student `paper-claimed-causal`；**32 ms** | [PDF](../raw/papers/low_latency_causal_se/2309.08144.pdf) |
| 16 | `2408.04267` | Distil-DCCRN: A Small-footprint DCCRN Leveraging Feature-based Knowledge Distillation | 2024 | AT-KL 特征蒸馏 | teacher 非因果；student 仅半句声明因果；**延迟未报告** | [PDF](../raw/papers/low_latency_causal_se/2408.04267.pdf) |
| 17 | `2406.07498` | RaD-Net 2: A causal two-stage repairing and denoising SE network with KD and complex axial self-attention | 2024 | 因果两阶段 + 复数 ASA | Stage-1 student 自称因果、teacher 非因果；**Stage-2 未声明**；延迟/RTF 未报告 | [PDF](../raw/papers/low_latency_causal_se/2406.07498.pdf) |
| 18 | `2502.04711` | Dynamic Frequency-Adaptive Knowledge Distillation for Speech Enhancement | 2025 | 频率自适应蒸馏权重 | 不面向低时延；student 因果性零提及 → 非因果 | [PDF](../raw/papers/low_latency_causal_se/2502.04711.pdf) |
| 19 | `2509.15922` | DISPATCH: Distilling Selective Patches for Speech Enhancement | 2025 | 选择性 patch 蒸馏 | teacher 非因果；student 未声明；32 ms 窗 / 8 ms hop | [PDF](../raw/papers/low_latency_causal_se/2509.15922.pdf) |
| 20 | `2607.27055` | Learning from the Future: Privileged Self-Distillation for Sequential Recommendation | 2026 | **跨域参照（推荐系统）** | 非语音任务；特权信息蒸馏的跨域类比 | [PDF](../raw/papers/low_latency_causal_se/2607.27055.pdf) |
| 21 | ICASSP 2021 | Teacher-Student Learning for Low-Latency Online Speech Enhancement Using Wave-U-Net | 2021 | 离线 teacher → 在线 student | teacher 非因果；student `low_look_ahead`；**6.71 ms** | [PDF](../raw/papers/low_latency_causal_se/2021-Nakaoka-TeacherStudent-WaveUNet-ICASSP.pdf) |

> [!warning] 知识蒸馏子群的关键结论
> **7 篇中没有一篇满足本 wiki 约 2 ms 的硬约束**：最近的是 Nakaoka 2021（6.71 ms，约差 3.4 倍），
> 其余为 32 ms、25 ms 窗量级或完全未报告延迟。因此这个子群的价值在于**蒸馏方法学**（teacher 如何补足 student 的上下文缺失、
> 特征级 vs 输出级蒸馏、两步 vs 加权混合），而不是「已达到 2 ms」的正向证据。
> 另需注意：`2408.04267` 与 `2309.08144` 在「student 是否需要预训练」及「两步 vs 加权混合」上**结论直接对立且互不引用**，
> 详见 [[wiki_low_latency/concepts/2309.08144-two-step-distillation]]。

> [!note] 论文状态
> 上表是论文入口登记，不代表不同论文的指标可以直接横向排名。各 source 页均单独标注 PDF 抽取质量、论文自身实验边界、strict-causal 证据和端到端 p99 缺失。

### 2026-09-20 追加：可配置时延 / 分布式双耳 / 脉冲 Mamba（3 篇）

| # | arXiv/DOI | 标题 | 年份 | 方向角色 | 因果与延迟结论 | 本地 PDF |
|---:|---|---|---:|---|---|---|
| 22 | `2606.19688` | LaCo-SENet: Latency-Configurable Streaming Speech Enhancement via Asymmetric Temporal Padding | 2026 | 非对称 padding 时延族 | 卷积骨干 `paper-claimed strict causal` + SSU 消融 + 分块/全序列等价声明；前端含 **12.5 ms** STFT center delay（不可消除下界） | [PDF](../raw/papers/low_latency_causal_se/2606.19688.pdf) |
| 23 | `2607.01834` | RT-Tango: Real-Time Distributed Binaural Speech Enhancement for Low-Power Hearing Aid Devices | 2026 | 分布式双耳助听器 | `paper-claimed strict causal`，**8 ms** 论文级算法延迟（无推导式）；在线 SCM 用「重复到收敛」评测 | [PDF](../raw/papers/low_latency_causal_se/2607.01834.pdf) |
| 24 | `10.1016/j.iot.2026.102046` | Lightweight streaming speech enhancement for AIoT-enabled wearable hearing aids using parallel spiking mamba | 2026 | 脉冲 Mamba、极低 MACs | `paper-claimed strict causal`；**30 ms** = 帧长；Mamba 状态每次调用重置、不跨帧 | [PDF](../raw/papers/low_latency_causal_se/1-s2.0-S2542660526001769-main.pdf) |

> [!warning] 这 3 篇同样没有一篇满足约 2 ms 硬约束
> 最近的是 RT-Tango 的 8 ms（约差 4 倍），LaCo-SENet 的 12.5 ms 是 STFT center delay 硬下界，
> PSMSE 的 30 ms 差 15 倍。三篇的正面价值分别是：**逐层因果证据链**（LaCo-SENet 给出 Eq. (1)(2)(5) 与 SSU 消融）、
> **分布式双耳账本**（RT-Tango 把 ERB/GRNN/非对称 STFT/FRS/在线 SCM 逐项消融）、
> **最低 MACs 标杆**（PSMSE 0.26 M / 0.11 G/s）。
> 两条必须随结论一起读的 caveat：RT-Tango-OS 的在线 SCM「重复到收敛后只算最后一次」等于无限预热；
> PSMSE 明确不缓存 Mamba 状态，其「长程建模」实际只发生在单帧（约 47 步）内部。

### 2026-09-22 追加：推理期动态算力子群（2 篇）

| # | arXiv | 标题 | 年份 | 方向角色 | 因果与延迟结论 | 本地 PDF |
|---:|---|---|---:|---|---|---|
| 25 | `2207.11108` | Inference skipping for more efficient real-time speech enhancement with parallel RNNs（社区通称 **Skip-DPCRN**） | 2022 | 并行 RNN 推理期状态跳过 + VAD 引导 | `paper-claimed-causal`（仅 inter-frame 单向一句声明，卷积 padding 未报告）；**48 ms total latency**（32 ms 窗 + 16 ms hop，论文未拆分） | [PDF](../raw/papers/low_latency_causal_se/2207.11108.pdf) |
| 26 | `2408.12425` | Dynamic Gated Recurrent Neural Network for Compute-efficient Speech Enhancement（**D-GRU**） | 2024 | 神经元级动态门控、零额外参数 | `paper-claimed-causal`（三个骨干均为 causal 的集合声明，无逐层清单）；**论文完全未报告任何延迟数字与 RTF** | [PDF](../raw/papers/low_latency_causal_se/2408.12425.pdf) |

> [!warning] 这 2 篇同样不满足约 2 ms
> Skip-DPCRN 的 48 ms 是 2 ms 目标的 **24 倍**；D-GRU 连延迟都没报。
> 两篇的真正价值在**方法论对照**：它们代表了「推理期动态算力」的两条对立路线——
> **时间步级跳过**（Skip-DPCRN，省平均算力但算力随输入波动，且必须有并行 RNN 宿主才不出伪影）
> vs **神经元级固定比例稀疏**（D-GRU，每步算力恒定、可直接作用于串行 GRU、零额外参数）。
> D-GRU 论文的 Related Work 明确把 Skip RNN 系列列为「每步算力波动、不适合硬件实时约束」的反面，
> 其引文 [31] 正是 Skip-DPCRN——**两篇必须并读**。
> 另需注意：Skip-DPCRN 的峰值算力只降约 15%，D-GRU 的 top-A 选择在真实硬件上的 gather/scatter 开销也未测，
> 两者都缺目标端侧的墙钟证据。

### 2026-09-24 追加：语义先验子群（1 篇）

| # | arXiv | 标题 | 年份 | 方向角色 | 因果与延迟结论 | 本地 PDF |
|---:|---|---|---:|---|---|---|
| 27 | `2412.19248` | Causal Speech Enhancement with Predicting Semantics based on Quantized Self-supervised Learning Features | 2024 | 因果 SSL 特征 + 未来语义 token 预测 MTL | `paper-claimed-causal`（**近似实现**：$c(X)=\{s(X_{\le t})_t\}$，限制输入 + 取末帧，Eq. 5；**无逐层审计、非架构级**）；**延迟/RTF/MACs/参数量/STFT 参数全部未报告** | [PDF](../raw/papers/low_latency_causal_se/2412.19248.pdf) |

> [!warning] 这一篇的账本空白程度是本库之最，引用时必须极其小心
> **它不是"延迟很大"，而是"没有任何延迟数据"**——无算法延迟、无 RTF、无 MACs、无参数量、无目标硬件，
> 连 STFT 的 window/hop/FFT/center 都没写。因此**不能**与库中任何一篇做延迟横向比较。
> 更要注意两点：
> ① **因果化是"截断式"而非"架构式"**——$c(X)$ 需要重跑 $s(X_{\le t})$ 并取末帧，字面实现为 $O(T^2)$ 量级重算，
> 论文对这个代价**零量化**。真正的流式化需要缓存或重训因果 SSL。
> ② **核心机制的失败模式未被检验**——"预测未来音素"在低 SNR / 竞争说话人下可能预测错误，
> 而掩蔽若依赖了错误语义就可能**抑制掉真实辅音**。论文无失败案例、无低 SNR 分层、无针对性诊断指标。
>
> 它的正面价值仍然清晰且可复用：**语义预测的增益只在因果条件下出现**（因果 +0.05，非因果 Δ=0.00），
> 这给"用未来预测补偿因果上下文缺口"提供了一条干净的条件对照证据（唯一可惜是效应量小且无显著性检验）。
> 另注：论文**未声称超过 SOTA**——Table II 里 LFSFNet 是 2.91 高于本文 2.88，原文措辞是
> "comparable to state-of-the-art method that, unlike our model, estimates appropriate phase information"。

### 2026-09-26 追加：速度优化子群（1 篇）

| # | arXiv | 标题 | 年份 | 方向角色 | 因果与延迟结论 | 本地 PDF |
|---:|---|---|---:|---|---|---|
| 28 | `2509.21867` | FastEnhancer: A Fast and Lightweight Framework for Streaming Speech Enhancement | 2025 | 速度优化流式族（T/B/S/M/L 五档）、RNNFormer | `paper-claimed-causal`（结构证据较强：**时间轴卷积 kernel 恒 = 1**、时间轴单向 GRU、频率轴 MHSA「doesn't require caching」；**但无逐层 padding / state certificate，STFT 帧锚定（center）未报告**）。**论文完全无算法延迟数字**；本库按 Table 1 的 $H$ 推得 hop = 256/160/100 samples ⇒ **16 / 10 / 6.25 ms**，若 center=True 再加 16 ms 前端 ⇒ **十几毫秒量级** | [PDF](../raw/papers/low_latency_causal_se/2509.21867.pdf) |

> [!note] 这一篇的正面价值不在延迟，而在"速度的支配因素"这一方法论议题
> **它是本库目前"MACs / 参数量 ≠ 实际速度"命题最完整的论据集合**，含四条：
> ① **跨模型**——FastEnhancer-B（262M MACs）RTF 0.022 对 GTCRN（40M MACs）0.060：MACs 高 6.5×、RTF 低 2.7×；
> ② **零算术变化**——BN→LN 在参数量 92K 与 MACs **完全不变**下 RTF 0.022→0.028（Xeon +27%）/ 0.026→0.029（M1 +12%），SISDR 19.0→**18.9**、STOI 不变；
> ③ **纯内存变化**——时间轴 kernel 1→3：Para. 92K→187K、RTF +27%(Xeon)/+42%(M1)，而 **SISDR 19.0→19.0、STOI 94.5→94.5 一格不动**；
> ④ **参数更少却更慢**——DPT 消融（时间轴 GRU→MHSA）参数量反而更少，因 **KV cache** 而 RTF 显著升高。
> 它同时给出一条可迁移的**结构审计清单**（时间轴 kernel / 归一化可融合性 / KV cache / global pooling / 数据相关访问 / 算力是否固定 / 全序列统计），可在**作者不报告延迟**的情况下只凭架构描述做初判——详见 [[wiki_low_latency/concepts/2509.21867-speed-optimized-streaming-design]]。

> [!warning] 引用本篇时必须同时读的四条边界
> ① **延迟账本为"零"，不是"大"**——论文通篇无窗口−hop、无 $W/2$、无推导式、无 group delay、无 look-ahead；本库的 16/10/6.25 ms 是**推读**，不是论文主张。
> ② **RTF 是吞吐指标，不是 deadline 指标**——论文称 "under a streaming condition" 但**未定义 chunk 大小、是否有 look-ahead、batch 是否为 1、是否含 STFT/iSTFT**；无 p50/p95/p99、无 deadline miss、无 underrun/overrun、无峰值 RAM/SRAM、无 INT8 量化、无功耗。
> ③ **"state-of-the-art" 的主张范围必须限定**——对比集合只有 5 个低复杂度模型，且 FastEnhancer-**L 的 MACs 达 11G，是 GTCRN 的 275×**；Pareto 前沿也没有形式化定义（无 hypervolume）。
> ④ **论文内部自相矛盾两处**——Table 2 标题写 "Voicebank-Demand" 而 §4 正文写 "**VTCK**-Demand"（疑为 VCTK 笔误，引文 [14] 指向 Valentini-Botinhao 的 VoiceBank-DEMAND）；§5.2 称 DPT look-behind 为「31 frames (corresponding to 0.5 seconds)」⇒ **2 ms/帧，与 Table 1 的任何 hop 都不符**。两处均**不静默修正**，按原文并列记录。
> 另注：5 个随机种子**只报均值不报方差**，故 0.01 量级差异（如 M 的 P.808 3.48 vs S 的 3.49）**无法判定显著性**。

### 2026-09-27 追加：算力对齐的动态深度（1 篇）

| # | arXiv | 标题 | 年份 | 方向角色 | 因果与延迟结论 | 本地 PDF |
|---:|---|---|---:|---|---|---|
| 29 | `2609.29867` | Does per-frame early exit pay? A compute-matched study of dynamic depth for on-device speech enhancement | 2026 | 逐帧早退 / 动态深度 + STM32N6 真机 int8 部署 | `paper-claimed-causal`（仅一句 "All networks are causal at a 16 ms hop"；**无逐层 padding / state certificate、STFT 的 center 未报告**；但**被跳过的 stack 状态不更新** ⇒ 结构上不可能引入未来依赖，是本库见过对「动态执行下因果性」最清晰的工程交代）。**论文没有任何"算法延迟"数字**；**hop = 256 @16 kHz = 16 ms**；实测 **0.640–3.584 ms/frame**（Table 1）/ **0.751–2.472 ms/frame**（Table 2），**均为平均、无 p99** | [PDF](../raw/papers/low_latency_causal_se/2609.29867.pdf) |

> [!note] 这是本库**算力证据最硬**的一篇，但它的结论是"动态深度在语音密集集上几乎不值"
> **算力证据等级最高**：真机 **STM32N6570-DK**（Neural-ART NPU @1 GHz + Cortex-M55 @800 MHz）、**post-training int8**（per-channel + entropy calibration）、**十张完整可部署图**逐张实测、**ms/frame** 而非 MACs 量纲——高于 FastEnhancer 的单线程 RTF（吞吐量纲）、远高于 D-GRU 的解析 MACs。
> **核心方法贡献**（四条）：
> ① **把 exits 修成单调之后，再看路由还剩多少价值**——knee target 从"当前 exits"定义，不要求质量随深度改善；更深 exit 更差时，策略"看起来有用"可能只是在回避有害的深 exit。用 2000 步、只动 **4×33k** 参数的 heads-only 微调加单调性正则 $\mathcal L_{mono}$ 把该信号抽掉。
> ② **mono-repair 是全文分水岭**：修复前 routed 明显优于专用静态前沿（routed H=64：**2.719 PESQ @ 8.48 MMAC/s**，同算力静态前沿约 **2.60**）；修复后 **mono-repaired 前沿几乎与 routed 前沿重合**（共同区间差 **< 0.01 PESQ**；三个点 8.48 / 12.18 / 20.22 MMAC/s 上分别 **+0.009 / −0.001 / +0.007**）。
> ③ **名义 MACs 在真实加速器上给出错误排序**：十图中 **µs/MMAC 差 1.7×（82–137）**；**(H=32,R=2) 与 (H=64,R=1) 的 MMAC/s 完全相同（7.30），却是 1.001 vs 0.751 ms/frame**；**(H=96,R=1) 比 (H=32,R=2) MACs 多 21.4 % 却快 14.9 %**。机理：**深度贵在每多一个 stack 就多一次 accelerator launch，宽度能更吃满 NPU**。
> ④ **评测协议本身会制造虚假的动态收益**：常见离线协议把 routed 输出算成 **gated sum**，因而**即使某 exit 没被用到也在更新它的状态**；本篇改为"跳过 stack 状态不更新"，代价 **−0.005±0.011 PESQ / 0.14 dB SI-SDR**，且路由决策在两 arm 间 **bit-identical**。

> [!warning] 引用本篇时必须同时读的五条边界
> ① **"sota" 类措辞无、但"30% less compute"无对应模型对**——Abstract 写「match the best PESQ at 30 % less compute」，§5 补"代价是 **1.0 dB SI-SDR 下降**"，但**论文未给出是哪两个模型的对照**，读者无法从论文数据复原这条主张。
> ② **承诺的 "seed spreads" 未兑现**——§1 贡献 3 写 "with seed spreads and controls"，**正文无任何 seed spread 数值**；而核心结论正依赖 0.01–0.05 量级的 PESQ 差值（+0.009 / −0.001 / +0.007）。**这比 FastEnhancer「5 seeds 只报均值」的同类问题更严重**（后者至少报了均值）。
> ③ **26 µs/frame 与 +2.2 % latency overhead 只出现在 Abstract**，正文 §4.3 无任何支撑；口径不明。
> ④ **账本缺口仍在**：**STFT/iSTFT/masking 留在 host**，**未计入 Table 1/2**；**无 p50/p95/p99、无 deadline miss、无 underrun**；**无峰值内存/SRAM**（只说编译器报告含 memory requirements）、**无功耗**（动机是 battery budget 却零功耗数据）；**全模型参数量未报告**（只有 exit heads 的 4×33k）；**无长流/state reset/warm-up 报告**。
> ⑤ **人声保留只有 whole-clip SI-SDR + wideband PESQ** —— **无 DNSMOS SIG/BAK、无 WER/ASR、无负 SNR 分层**（仅 Fig. 4 一条 0.46 dB 示例语句）、**无 false-suppression / F0 / prosody**。
> 论文**自陈局限**：主张**仅限语音密集数据集（VoiceBank–DEMAND）**；长停顿工作负载不在研究范围内，而"router 在稀疏工作负载上是否更有价值"被列为**重要下一步**。

### 2026-09-27 追加：超轻量锚点（1 篇，**补摄**）

| # | 主页 | 标题 | 年份 | 方向角色 | 因果与延迟结论 | 本地 PDF |
|---:|---|---|---:|---|---|---|
| 30 | [[wiki_low_latency/sources/2024/GTCRN 2024]] | GTCRN: A Speech Enhancement Model Requiring Ultralow Computational Resources | 2024 | **"超轻量"档的锚点** / 子带-ERB 路线代表 | `paper-claimed-causal`（仅一句 `so that the causality of the model can be guaranteed`，指 inter-frame 用单向 GRU；**无逐层 padding、无 state certificate、STFT 的 center 未报告**）。**原文无任何算法延迟数字**；唯一时延锚点是 **hop 256 @16 kHz = 16 ms**（窗 32 ms / FFT 512）；**无 RTF、无 p99、无目标硬件、无量化、无端侧实测**；算力证据停在**名义 MACs（L0）** | [PDF](../raw/papers/low_latency_causal_se/GTCRN-ICASSP2024.pdf) |

> [!important] 这是本库第 30 篇，也是**第一篇"已正式出版且有卷页 DOI"却由用户提供 PDF 才得以补摄**的论文
> **venue 等级为本库最高档**：**ICASSP 2024 正式出版**，版权行 `979-8-3503-4485-1/24/$31.00 ©2024 IEEE`，DOI `10.1109/ICASSP48485.2024.10448310`，**pp. 971–975**（p.1→971 … p.5→975 逐页页脚可核）。它**没有 arXiv 版本**，此前因 IEEE 付费墙而**无法合法获取**——用户于 2026-09-27 直接提供 PDF 后解除了这一阻塞。
> **它为什么必须进库**：GTCRN 是本库**被引用次数最多的"内部外"锚点**——`FastEnhancer`（RTF 0.060，最主要的对照）、`RT-Tango`（借用其 ERB 压缩，并重配到 4 ms hop）、`PSMSE`（归入"超轻量网络"并批评其容量受限）、`muNet`（主要竞品）**四篇同时引用它**。此前本库只能通过这四篇的**二手转述**认识 GTCRN，现在有了**一手证据**。
> **补摄立即产生的三项更正**：
> ① **页码冲突定案**（971–975 正确，10286–10290 为 `Early Exit Compute-Matched 2026` 的误著录）；
> ② **参数量三方口径矛盾浮出**——原文 **23.7 K / 39.6 MMACs per second**（内部自洽，恰为 Table 1 末行）vs FastEnhancer 的 **24 K / 40 M**（≈四舍五入）vs **`muNet 2026` 的 48 K / 33**（**参数 2.03×、MACs 0.83×，方向相反，无法用例差解释**）；
> ③ **Table 1 补出一组论文回避的对照**——**TRA 用 +0.56 M/s MACs 换 SISNR +0.38，而 SFE 用 +5.16 M/s 只换 +0.23**；但参数上 TRA 贵 4.1×（+8.30 K vs +2.02 K）⇒ **是双向 trade-off，不是单向优劣**（论文只把 TRA 与 TA 比）。
> **延迟账本仍然为空**：hop 16 ms、**STFT 的 center 未报告**（若 `center=True` 则前端再含 16 ms 未来样本）、逐层 padding 未报告、DD-Conv2D 时间感受野未给 ⇒ **本库只能把它的算法延迟记为"双向不确定的 ≈16 或 ≈32 ms"，不是 2 ms 候选**。
> **与 FastEnhancer 的直接冲突（必须并读）**：GTCRN 是**子带路线的代表**，而 FastEnhancer §2.2 **点名批评** BSRNN / FSPEN / **GTCRN** / LiSenNet 这类方案「increased architectural complexity and memory operations paradoxically led to higher RTFs」。**GTCRN 全文无 RTF，因此无法回应**。**第三条批评来自 PSMSE**（容量受限）。⇒ 子带路线在**参数与 MACs** 上赢、在 **RTF** 上与**容量**上被质疑，而 GTCRN 原文对后两条都没有数据。
> **一条方法学警示（本库新增）**：GTCRN 用 **ShuffleNetV2** 设计 GT-Conv，而 ShuffleNetV2 正是本库"MACs 不是速度"命题的出处之一——**引用它却没有报告速度**，属"引用即负有义务"未被履行的情形。

> [!question] 论文内部三处存疑（`[!question]`，不静默修正）
> ① **GTCRN 页码冲突——已于 2026-09-27 定案**：本篇 [2] 引作 **pp. 10286–10290**，而库内 FastEnhancer / RT-Tango / UL-UNAS 三篇均引作 **pp. 971–975**。**摄取 GTCRN 原始 PDF 后已判定 971–975 正确**——依据是**论文 PDF 自身逐页印刷页码**（p.1→971 … p.5→975，一手证据），而 10286–10290 是第三方参考文献著录（二手转录）。详见 [[wiki_low_latency/sources/2024/GTCRN 2024]] §参考文献核对。**篇内印刷的 10286–10290 维持原样记录，不静默修正。**
> ② **`ε` 与 `asym4` 均未定义**：$\varepsilon$ 在 §2.2 是 knee target 容差，Table 2 又有 `ε=2·10⁻³` / `ε=5·10⁻⁴` 两档，是否同一量未澄清；**`asym4` 全文只出现一次**（§4.4），无定义（唯一对应的 Table 2 行已确认）。
> ③ **"延迟只涨 3.1×"无法由 Table 1 复现**：原文称「increasing H from 32 to 256 raises the MACs within a stack by 8×, but its measured latency by only **3.1×**」。"MACs 涨 8×"自洽（**stack 内通道宽度比** 256/32），但同-$R$ 试算的最大延迟比只有 **2.47**（$R=2$），**没有任何一对能对上 3.1**。论文未说明是哪两个拓扑。

### 2026-09-27 追加：LaCo-SENet 的非因果上界与骨干来源（1 篇，**补摄**）

| # | 主页 | 标题 | 年份 | 方向角色 | 因果与延迟结论 | 本地 PDF |
|---:|---|---|---:|---|---|---|
| 31 | [[wiki_low_latency/sources/2025/PrimeK-Net 2025]] | PrimeK-Net: Boosting Speech Enhancement with Prime Kernel and Multi-Scale Dense Block | 2025 | **本库"非因果质量上界"的原始出处** / LaCo-SENet 的骨干与损失来源 | **非因果**（SCA 用 `AdaptiveAvgPool1d` 全局池化 ⇒ 显式聚合未来帧；论文自身也承认这是"性能优先"选择）。**论文无任何算法延迟、无 RTF、无硬件、无量化**；唯一时延线索是 STFT **FFT 400 / window 400 / hop 100 @16 kHz = 25 ms 窗 / 6.25 ms 跳**（与 LaCo-SENet 同口径）。⇒ **算法延迟下界 12.5 ms（$W/2$），且因非因果实际无界**；**算力证据等级 L0**（只有 1.41M 参数 + 44.64 G FLOPs） | [PDF](../raw/papers/low_latency_causal_se/2502.19906.pdf) |

> [!important] 这是本库第 31 篇，也是**第一篇先以"引用方"身份进库、后补一手证据**的论文
> **进库路径与 GTCRN 相反**：GTCRN 是"被四篇同时引用 → 用户提供 PDF 补摄"；PrimeK-Net 则是**库内 LaCo-SENet 页早已反复引用它**（作为骨干、损失来源、以及 Table 1 的**非因果上界 3.61**），而它自己一直没有页面。补摄后，**库内三条悬空的引用链全部落地**：骨干（1.37M vs 1.41M）、损失（五个权重系数）、质量上界（3.61）。
> **venue 等级**：**ICASSP 2025**，arXiv:2502.19906 的 Comments 字段写明 "This paper was accepeted by ICASSP 2025"（原文拼写如此）——按本库第 16 条口径，arXiv `Comments` 是**唯一被承认的录用证据**。有官方代码 `github.com/huaidanquede/PrimeK-Net`。
> **它对全库的定位价值**：本库此前所有"因果化代价"的讨论都缺少**同一架构内的紧上界**。PrimeK-Net 提供了这个上界——**同一骨干、同一损失、同一数据、同一前端**，只差"能不能看未来"。因此 **3.61（非因果）vs 3.35（12.5 ms 全因果）= 0.26 PESQ 的因果化代价**，是全库**口径最干净**的一组因果-非因果对照（远优于跨论文拼接）。
> **同时它给出一条反向警示**：非因果模型在本库**不能参与因果排名**（LaCo-SENet 自己也是这么处理的，标为 ‡），但**可以且应该参与"上界"与"代价"的度量**。两类用途必须分开记账。

> [!contradiction] 补摄暴露的两处口径/引用问题（**不静默修正，并列记录**）
> ① **算力量纲在库内首次出现 FLOPs**：PrimeK-Net 报 **44.64 G FLOPs**，而本库其余论文绝大多数报 **MACs**（如 GTCRN 的 39.6 MMACs/s、FastEnhancer 的 262M MACs）。按通行约定 **1 MAC ≈ 2 FLOPs**，44.64 G FLOPs ≈ **22.3 G MACs**，与 GTCRN 的 39.6 M/s **差三个数量级**——但这个换算**本身也不能直接比**，因为前者是"每句（全序列）"、后者是"每秒"。**结论：这两个数字禁止放进同一次效率比较**；引用 PrimeK-Net 的算力时必须写明量纲是 FLOPs。
> ② **引用链断点：损失权重**。`LaCo-SENet 2026` 明确写"损失完全沿用 PrimeK-Net [3]"并给出 $0.9/0.3/0.1/0.05/0.05$ 五个系数，但**PrimeK-Net 全文未给出任何 $\lambda$ 数值**（只定义了两个损失 $\mathcal L_{old}$ 与 $\mathcal L_{new}$ 的形式）。⇒ "沿用"的对象**不可能是原文的数值**。本库**不判定谁对**，按原文并列记录，并标注为**引用链断点**（与第 14 条"锚点数值先钉口径"同源）。

> [!question] PrimeK-Net 自身的一处因果缺口（结构审计，未在原文承认）
> **SCA 的 `AdaptiveAvgPool1d` 作用域未定义**。PrimeK-Net 的 SCA（Simplified Channel Attention）用自适应平均池化产生通道描述子——若池化跨**整个时间轴**（LaCo-SENet §3.4 明确记载其原始形式为 `AdaptiveAvgPool1d(1)`，即全局），则**每一帧的注意力权重都依赖全句所有帧**，模型严格非因果且**无法流式**。PrimeK-Net 原文**未说明该池化的时间作用域**，也**未声明自己有流式版本**。这个缺口正是 LaCo-SENet 动手改造的点（改为 depthwise `CausalConv1d`, $K_{\text{sca}}=11$ ⇒ 未来访问被参数化）。**库内判定：PrimeK-Net 的因果性为"结构上非因果"（由 SCA + 无因果声明共同确定），但作者从未正面讨论这一点。**

> [!note] 补摄同时独立复核了论文的一个关键数字
> PrimeK-Net 声称 DSDDB 复杂度仅为 DDB 的 **12.7%**。本库按论文 Eq. (5)–(10) 用 $n=4$、$C=64$、$K=3$ **独立重算**：$46720 / 368640 = 12.67\%$ ⇒ **论文内部自洽，该数字可信**。这是本库第一次对"复杂度压缩比"这类主张做**逐式复核**并给出正结果，可作为后续同类主张的复核模板（详见 [[wiki_low_latency/concepts/2502.19906-prime-kernel-multiscale-dense-block]]）。

### 2026-09-27 追加：超轻量三角的第三边（1 篇，**补摄**）

| # | 主页 | 标题 | 年份 | 方向角色 | 因果与延迟结论 | 本地 PDF |
|---:|---|---|---:|---|---|---|
| 32 | [[wiki_low_latency/sources/2024/LiSenNet 2024]] | LiSenNet: Lightweight Sub-band and Dual-Path Modeling for Real-Time Speech Enhancement | 2024 | **"超轻量三角"中参数第二小** / 被 3 篇同时引用（FastEnhancer 批评 + PSMSE 归入容量受限 + GTCRN 并列） | `paper-claimed-causal`（唯一依据是一句 *"we apply Bi-GRU for frequency modeling and unidirectional GRU for temporal modeling"*；**无逐层 padding、无 state certificate、STFT center 未报告**）。**全篇无任何算法延迟数字**；唯一时延线索是 **STFT window 512（32 ms）/ hop 256（16 ms）@16 kHz**；有 **RTF 0.028**（Xeon E5-2620 v4）但**缺 runtime / chunk / batch / 是否含 GLA**；**算力证据等级 L1** | [PDF](../raw/papers/low_latency_causal_se/2409.13285.pdf) |

> [!important] 这是本库第 32 篇，补齐了**"超轻量三角"的第三边**，也是本库**第一例"纯预印本但被多篇引用"**的补摄
> **三篇对照**（**来源各异，禁止横向排名**）：
> | 模型 | 参数 | 算力 | PESQ | 因果性 | 算力证据 | venue |
> |---|---|---|---|---|---|---|
> | [[wiki_low_latency/entities/GTCRN\|GTCRN]] | **23.7 K** | 39.6 MMACs/s | 2.87\* | `paper-claimed-causal` | **L0** | ICASSP 2024（pp. 971–975） |
> | **LiSenNet** | **37 k** | 56 MMACs/s | **3.07** | `paper-claimed-causal` | **L1**（RTF + CPU 型号） | **纯预印本** |
> | FSPEN | **79 k** | 89 M（本篇）/ 64 M（FastEnhancer ^d） | 2.97 | 未知 | L1 | ICASSP 2024（pp. 10671–10675） |
> \* GTCRN 的 2.87 来自 FastEnhancer Table 2 的官方 checkpoint 评测，**非 GTCRN 原文值**。**库中暂无 FSPEN 页**（付费墙、无 arXiv，需用户提供 PDF）。
> **本篇最硬的价值不在它自己，而在它被 FastEnhancer 引用时产生的三条外部证据**：① LiSenNet^b **不可流式的原因**（"input normalization and griffin-lim"）——**本篇原文从未提**；② 可流式子版本 **^c 的 PESQ 2.98**——**本篇从未报告**；③ 扩展指标 SCOREQ / SISDR / BAK / WER——**本篇全部未报**。⇒ **本篇与 FastEnhancer 对"LiSenNet 有几个版本"的指称不一致**（1 个 vs 2 个），已立 `[!contradiction]`。
> **一处必须与原文并读的因果缺口**：GLA 相位精修（k=2）是**整段迭代式**后处理（Eq. 5），但论文自陈 "for **real-time** applications" 且**从未说明 GLA 如何流式实现、也未把它的开销计入 RTF**。FastEnhancer 独立指出这是它不可流式的原因之一。⇒ 本库判定 **GLA 是本篇"实时"声称中最薄弱的一环**。

> [!note] 本篇对本库的**正面价值**：它是一个"引用链干净"的对照组
> 参数量与算力 **37k / 56M** 在 Abstract、§I、Table I、Table III **四处原文**以及 FastEnhancer 的 **^b/^c 两行**中**完全一致，无任何矛盾**。
> ⇒ 与 [[wiki_low_latency/entities/GTCRN\|GTCRN]]（三套口径）和 [[wiki_low_latency/entities/PrimeK-Net\|PrimeK-Net]]（FLOPs 新量纲 + 损失权重断点）形成对照。**当一个锚点的多份记录完全一致时，说明该方向的引用是干净的**——这为第 14 条判据提供了正例。

> [!warning] 本篇最极端的一条**反例**：帧级动态算力的峰值为负收益
> 噪声检测器（ND）把 MACs 从 56M 变成区间 **15M ∼ 70M**（随噪声比例浮动）。但：
> ① ND 是**帧级**门控、**无状态跳过** ⇒ 尾延迟不变，**最坏情况（全程有噪）下 MACs = 70M，比不加 ND 的 56M 还高 25%**；
> ② 每帧仍要走一次 ND 前向（64 维 Mel + 4 层卷积），其开销**是否计入该区间未说明**；
> ③ 代价是 PESQ **3.08 → 3.00**（论文自陈源于"detection 不精确 + 干净区间信息损失"）。
> ⇒ 按本库第 5 条判定口径（**平均算力 ≠ 可用算力**），这是库内**最极端的一个反例**——另三个动态算力案例（Skip-DPCRN / D-GRU / Early Exit）**都讨论过峰值**，**只有本篇零讨论**。**记录为"平均算力收益成立、峰值负收益、论文未讨论"。**

### 2026-10-07 追加：INTERSPEECH 2026 主题八篇（5 篇新摄 + 3 篇已在库）

| # | 主页 | 标题 | 年份 | 方向角色 | 因果与延迟结论 | 本地 PDF |
|---:|---|---|---:|---|---|---|
| 33 | [[wiki_low_latency/sources/2026/HALO 2026]] | HALO: Half-Frame-Rate Adaptive Learnable Operator for Lightweight STFT-Based Speech Enhancement | 2026 | **算力冗余**：把"重叠引入的时域冗余"当独立瓶颈 | **严格因果**（D 只用 $(2l-1,2l)$、U 不访问未来，不增 lookahead）；但**奇数帧是外推**；**算法延迟未报告绝对值**（继承前端 32 ms）；无 RTF ⇒ **算力证据 L0** | [PDF](../raw/papers/low_latency_causal_se/HALO-Interspeech2026.pdf) |
| 34 | [[wiki_low_latency/sources/2026/Latency Controllable SE 2026]] | Latency Controllable Speech Enhancement | 2026 | **future context / 运行时延迟旋钮** | 半因果：7 档中 6 档依赖 lookahead；**仅 $T_{la}=0$ 档因果，但延迟 5 ms**；**§3.2 定义 $\tau=\tau_{enc}+\tau_{sep}$ 与库内逐字同构** | [PDF](../raw/papers/low_latency_causal_se/LatencyControllableSE-Interspeech2026.pdf) |
| 35 | [[wiki_low_latency/sources/2026/SEMamba++ 2026]] | SEMamba++: A General Speech Restoration Framework Leveraging Global, Local, and Periodic Spectral Patterns | 2026 | **频率结构建模**（非低时延） | **非因果离线 GSR**（双向 Mamba，全文无 latency/causal 讨论）；RTF 0.021 @A6000 是吞吐非延迟；**GLP 自陈无法用于采样率无关场景** | [PDF](../raw/papers/low_latency_causal_se/SEMambaPP-Interspeech2026.pdf) |
| 36 | [[wiki_low_latency/sources/2026/TF Weighted Losses 2026]] | Time–Frequency Weighted Losses for Phoneme Reconstruction in DNN-Based Speech Enhancement | 2026 | **该增强/不该杀语音（损失侧）** | 多通道 + FaSNet 波束形成，**非因果**；**无任何延迟/算力报告**（尽管资助项目名含 Real-time）⇒ 算力证据 **低于 L0** | [PDF](../raw/papers/low_latency_causal_se/TFWeightedLoss-Interspeech2026.pdf) |
| 37 | [[wiki_low_latency/sources/2026/Schrodinger Bridge Mamba 2026]] | Schrödinger Bridge Mamba for One-Step Speech Enhancement | 2026 | **生成式能否靠近实时** | **半因果**（2–4 帧 lookahead）；论文称 "under 40 ms" **漏计 30 ms 窗** ⇒ 按库内口径 **50–70 ms**；RTF 0.0048（GPU 型号未指明）⇒ **L1** | [PDF](../raw/papers/low_latency_causal_se/SchrodingerBridgeMamba-Interspeech2026.pdf) |

> [!important] 本批的**方法学**背景：用户按"八个主题"点名，其中 3 篇（LaCo-SENet、RT-SEMamba、RT-Tango）**已在库**，5 篇为新增
> 用户点名的八篇与库内对应关系：
> | 用户点名的主题 | 论文 | 库内状态 |
> |---|---|---|
> | 计算冗余 | **HALO** | ✅ 本批新摄（#33） |
> | future context / algorithmic latency | [[wiki_low_latency/entities/LaCo-SENet\|LaCo-SENet]] | 已在库（#31，2026-09-27） |
> | future context / algorithmic latency | **Latency Controllable SE (LCA)** | ✅ 本批新摄（#34） |
> | past state / long-term modeling | [[wiki_low_latency/entities/RT-SEMamba\|RT-SEMamba]] | 已在库（#20，2026-09-20） |
> | 频率结构怎么建模 | **SEMamba++** | ✅ 本批新摄（#35） |
> | 哪里该增强、哪里不该杀语音 | **TF Weighted Losses** | ✅ 本批新摄（#36） |
> | 极低延时 pipeline | [[wiki_low_latency/entities/RT-Tango\|RT-Tango]] | 已在库（#21，2026-09-20） |
> | 生成式能不能靠近实时 | **SBM** | ✅ 本批新摄（#37） |
>
> ⇒ **本批是库内首次按"方法学维度"（而非任务/年份）成组补摄**，覆盖了"冗余—延迟旋钮—状态建模—频率结构—损失加权—pipeline—生成式"七个互不重叠的设计轴。**八篇中只有 RT-Tango（8 ms）与 LaCo-SENet（12.5 ms 起）是低延迟方法，其余六篇要么非因果、要么延迟口径不合格。**

> [!important] 本批最重的一条外部背书：**库内延迟账本口径首次获正式发表论文独立确认**
> [[wiki_low_latency/entities/LCA-Latency-Control-Adapter\|LCA]] §3.2 独立给出：$\tau=\tau_{enc}+\tau_{sep}$、**"causal 当且仅当 separator 不用未来帧，尽管 $\tau_{enc}$ 依然存在"**、以及"**存在漏报 buffering 项的文献，比较时须小心 [29]**"。
> ⇒ **与库内 `[[wiki_low_latency/concepts/严格因果与算法延迟]]`、`[[wiki_low_latency/concepts/低时延前端与延迟账本]]` 的立场逐字同构**，且它引用的 [29] 正是 Wu & Braun（已在库内）。
> **证据链闭合**：原始提出（Wu & Braun）→ 库内采纳（overview 判定口径）→ **外部独立确认（LCA §3.2）**。
> **并且这条口径立刻抓到了一个新误报**：[[wiki_low_latency/entities/Schrodinger-Bridge-Mamba\|SBM]] 声称 "algorithmic latency under 40 ms"，但按其 STFT（480 样本窗 = 30 ms）计算，实际应为 **50–70 ms** ⇒ **正是"漏计 $\tau_{enc}$"的案例**。

> [!warning] 本批最需要警惕的一处口径混比风险：**GTCRN 算力出现第三个记录**
> [[wiki_low_latency/entities/HALO\|HALO]] Table 1/2 报 GTCRN 为 **23.67 k 参数 / 33.83 M MAC/s**。
> | 口径 | 参数量 | 算力 | 出处 |
> |---|---|---|---|
> | 原论文声称值 | 23.7 K | **39.6 MMACs per second** | GTCRN 原文 |
> | 引用方 B | 48 K | **33 MMACs** | 库内既有记录 |
> | **HALO** | **23.67 k** | **33.83 M MAC/s** | HALO Table 1/2 |
>
> ⇒ **HALO 是混合口径**（参数吻合原文、算力吻合"33"那一族）。**三方并列记录、不选边**，并提示：**引用 GTCRN 算力前必须声明取哪个口径**。
> **反面正例**：HALO 报 LiSenNet 为 **36.78 k / 55.77 M MAC/s**，与 LiSenNet 原文自报 **37 k / 56 M** 吻合（误差 0.6% / 0.4%）⇒ **库内首次出现外部论文对 LiSenNet 参数-算力口径的独立复现确认**。

> [!note] 本批的两条**跨论文结构性发现**
> **① "平均算力 ≠ 可用算力"出现第四种机制：结构性平均-峰值分离。**
> [[wiki_low_latency/entities/HALO\|HALO]] 自陈"**不降低峰值每步算力**，因为帧率恢复算子在同一次推理步里生成两个相邻帧"。
> ⇒ 与已有的动态算力案例（Skip-DPCRN 整步跳过、D-GRU 神经元级稀疏、Early Exit 逐帧早退）**机制不同但后果相同**：**当平均节省来自"步内合并"时，峰值可能完全不变**。库内判定口径第 5 条（平均算力 ≠ 可用算力）由此获得一个**非动态算力**的新分支。
>
> **② "轻量化收益边际递减"在两条不同自变量的曲线上重复出现。**
> [[wiki_low_latency/entities/HALO\|HALO]] 沿**骨干容量**递减（DPCRN ultralight **+0.187** → light +0.101 → middle +0.062 → large **+0.014**；UL-UNAS +0.016）；
> [[wiki_low_latency/entities/LiSenNet\|LiSenNet]] 沿**模块数量**递减（每 +10M MACs 的 PESQ 增益 **+0.171 / +0.059 / −0.006**）。
> ⇒ **两条不同自变量、同一现象** ⇒ 合并说明：**在轻量区间，任何单一手段的收益都会很快见底。** 这正是库内"低延迟 × 低 SNR 人声保留"仍属空白的方法学背景。

> [!contradiction] 本批带出的一处**对库内既有假设的反例**
> [[wiki_low_latency/entities/TF-Weighted-Losses\|TF-Weighted Losses]] 把权重压向"**语音活跃但 SIR 低**"（即最该保护人声的区域）。朴素直觉是"**SNR 越低越该有用**"。
> **实测方向相反**：极低 SIR（−8 dB）时**基线在 band 6 以上的爆破音频谱更接近干净参考、PA 略高**；SSN 下 **0 dB 以下基线 WER 最低**；纯可学习权重 $\mathcal{L}_{learn}$ 在 SSN 下**全面失败**。
> ⇒ **"保人声"加权策略的有效区间是中高 SIR，不是极低 SIR。** 这是对库内"低 SNR 人声保留"目标的**边界证据**——不能假设"更强的保人声加权在更低 SNR 下更有效"。可能机制（论文未讨论）：极低 SIR 下"语音活跃但 SIR 低"的 bin 几乎覆盖整个时频面 ⇒ **加权退化为近似均匀、失去区分度**。

> [!contradiction] 本批确认了一处**生成式 vs 判别式**的张力，并把它拆成两个轴
> [[wiki_low_latency/entities/Schrodinger-Bridge-Mamba\|SBM]] 是库内**最接近"生成式 ∩ 低时延"的一篇**（生成式 + 一步 + RTF 0.0048 + 明确声称 streaming feasibility）。
> **但结论是分裂的**：
> | 轴 | 结论 |
> |---|---|
> | **吞吐（RTF）** | ✅ 生成式已接近实时（0.0048，比 SB-NCSN++(50) 快 160×；且与 Mamba-base **零 RTF 代价**获得 SB 收益） |
> | **算法延迟** | ❌ 2–4 帧 lookahead + 30 ms 窗 ⇒ **50–70 ms**，距库内约 2 ms 目标 **25–35 倍** |
> | **质量** | ⚠️ **PESQ/ESTOI/SpeechBERTScore 上仍输给判别式 ZipEnhancer（2.04M）**（VBD PESQ 3.628 vs 3.503） |
> ⇒ **库内 2026-10-06 趋势报告的判断（"生成式与低延迟是两个几乎不相交的圈子"）被再次印证——"最接近相交"仍未相交。**
> **记录纪律：两个轴必须分开写**，混为一谈会双向误导。

## 操作日志

- [[wiki_low_latency/log|操作日志]]
