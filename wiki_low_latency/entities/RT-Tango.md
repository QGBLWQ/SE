---
title: RT-Tango
type: entity
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
  - online-scm
  - grouped-recurrent-network
  - asymmetric-stft
sources:
  - [[wiki_low_latency/sources/2026/RT-Tango 2026]]
related:
  - [[wiki_low_latency/concepts/2607.01834-distributed-binaural-low-latency]]
  - [[wiki_low_latency/concepts/低比特率双耳特征链路]]
  - [[wiki_low_latency/concepts/2204.09911-short-asymmetric-stft]]
  - [[wiki_low_latency/concepts/严格因果与算法延迟]]
  - [[wiki_low_latency/entities/GCFSnet]]
  - [[wiki_low_latency/entities/DeepFilterNet2]]
---

# RT-Tango

## 定义

**RT-Tango** 是本地论文 2607.01834 提出的**双耳分布式实时语音增强框架**，面向低功耗助听器。它系统级重构 Tango（Furnon et al. 2021）的两阶段分布式架构，在每个耳节点本地运行 SN-DNN 估计 mask 并做 SDW-MWF，把耳侧压缩信号传给对侧后由 MN-DNN 精修 mask、再做第二次 SDW-MWF 输出双耳增强语音。

效率化改动有四项：**ERB 特征压缩**、**分组循环网络 GRNN**、**非对称 STFT**、**时间稀疏化 FRS**。把 SCM 换成在线 EMA 递归更新后，得到严格因果流式变体 **RT-Tango-OS**，论文声明其 algorithmic latency 为 **8 ms**。

RT-Tango-OS 是论文级 strict causal 声明 + 8 ms 算法延迟，**不是**本 Wiki 约 2 ms 目标的已验证系统；其在线 SCM 评测存在无限预热问题（见下）。

## 证据

| 属性 | 本地 PDF 证据 |
|---|---|
| 任务 | 双耳分布式语音增强；训练按 Monir et al. [22] 协议仿真，评测 BinauRec [24] 子集 1200 条混合（PHL 实测 RIR、假人头 BTE 助听器），p.1、p.3 |
| 麦克风 | 每耳 2 麦（Front/Rear），共 4 麦；目标在正前方、噪声在右 45°/90°，故右耳 SIR 更低，p.3、Figure 1 |
| 骨架 | Tango 两阶段：Stage 1 SN-DNN + SDW-MWF → 耳侧压缩信号跨耳传输；Stage 2 MN-DNN + SDW-MWF → iSTFT 双耳输出，Figure 1，p.2 |
| SN-DNN 配置 | 输入 ERB 特征 → **GRNN（G=8）+ FC** → 逆 ERB；FRS 更新率 **1/4**（每 4 帧一次），p.2、p.3 |
| MN-DNN 配置 | 融合本地信号与对侧交换表征 → **GRNN（G=2）+ FC** → 逆 ERB；FRS 更新率 **1/2**（每 2 帧一次），p.2、p.3 |
| STFT 配置 | 分析窗 **32 ms**、合成窗 **8 ms asyHann**（非对称 Hann [21]）、hop **4 ms**（RT-Tango/RT-Tango-OS）；训练与分组/FRS 消融用 16 ms hop，Table 1、Table 5、§3.2.3 |
| SCM 更新 | 离线 RT-Tango：整句估计 SCM；RT-Tango-OS：递归 EMA，α = **0.995**，每 **8 帧**更新一次 @4 ms → 有效间隔 **32 ms（≈31 次/s）**，p.3 |
| 时间稀疏化 | FRS：SN-DNN 1/4、MN-DNN 1/2（SN 跳 75% 帧、MN 跳 50% 帧）；DNN 成本 67.5 → 28.08 MMACs/s，Table 3/4、§3.2.2 |
| 因果性 | 论文声明 RT-Tango-OS 为 strictly causal streaming；未给逐层 padding/状态清单，也未给 look-ahead，p.4 §3.2、p.4 Conclusions |
| 算法延迟 | 论文口径 **8 ms**，归因于非对称 STFT + 在线 SDW-MWF；**未给推导式**，p.4 |
| 参数量 | **未报告**（全文只给 MACs；Tango-RNN 的 DNN 为 2 层 stateful RNN、每层 128 hidden units，但非参数总量） |

## 架构与状态

~~~text
每耳节点（左右对称，独立运行）
  Front/Rear 两麦 → STFT
    → ERB Features
    → SN-DNN = GRNN(G=8) + FC        ← FRS 1/4：每 4 帧推理一次，其余帧复用旧 mask
    → Inv ERB（回线性频域）
    → SDW-MWF（Stage 1）             ← 使用本耳 SCM
    → 耳侧压缩信号 ──跨耳传输──→ 对侧节点
  ─────────────────────────────────────────────
    → MN-DNN = GRNN(G=2) + FC        ← FRS 1/2：每 2 帧推理一次
       （输入：本地信号 + 对侧交换表征）
    → Inv ERB
    → SDW-MWF（Stage 2）             ← RT-Tango-OS：SCM 递归 EMA 在线更新
    → iSTFT
    → 本耳增强输出
~~~

结构要点：

- **两个 DNN 各自独立**，且**分组数不同**（SN=8、MN=2）；这是论文 Table 2 消融直接决定的配置。
- **GRNN 组间靠 representation rearrangement [18] 交换信息**，论文以此论证「局部递归 + 全局频谱建模」可兼得。
- **两阶段各自带一次 SDW-MWF**，Stage 1 的空间滤波结果既是对侧的辅助表征，也是本侧的中间产物。
- 论文强调架构的混合性：**神经网络引导空间滤波器，而不是直接重建信号**（"neural networks guide the spatial filter rather than directly reconstructing the signal"）。这解释了它对高帧率压缩的鲁棒性。

## 低时延账本

| 字段 | RT-Tango / RT-Tango-OS 证据与边界 |
|---|---|
| 采样率 | 论文未在正文显式给出采样率；数据集与前端未标注（**未报告**） |
| 分析窗 / 合成窗 | aW = 32 ms；sW = 8 ms（asyHann）；非对称配置引用 [20,21] |
| hop / 帧率 | 4 ms → ≈250 frames/s（RT-Tango/RT-Tango-OS）；16 ms → ≈62 frames/s（Tango、分组消融、FRS 消融） |
| 算法延迟 | RT-Tango-OS：论文口径 **8 ms**；**记账依据未给出**；离线 RT-Tango 未声明算法延迟 |
| look-ahead | **未报告**；非对称 STFT 通常隐含 low_look_ahead（对照 [[wiki_low_latency/concepts/2204.09911-short-asymmetric-stft]]） |
| 时间因果 | 论文声明 strict causal；GRNN 为递归结构、FRS 只复用历史 mask → 方向一致，但无逐层 certificate |
| 递归状态 | GRNN 隐状态（每 stage 独立）；SCM 递归统计。**state reset、warm-up、长流漂移均未报告** |
| 在线统计收敛 | 评测把每条混合**重复到 SCM 收敛**、只算最后一次 → 相当于**无限 warm-up**，真实冷启动未验证 |
| 每帧算力 | RT-Tango-OS：**0.49 MMACs/frame**（DNN 0.27 + SDW-MWF 0.22）；RT-Tango：33.41 MMACs/s；RT-Tango-OS：35.14 MMACs/s；无稀疏化时 RT-Tango-OS 为 124 MMACs/s |
| MACs 口径 | 单节点；计入 DNN + ERB/逆 ERB + SDW-MWF；**不含 FFT/iFFT** |
| 运行时 / RTF | **未报告**（无 GPU/CPU/DSP 上的 wall-clock 或 RTF） |
| 端到端与 deadline | p50/p95/p99、per-hop wall-clock、deadline miss、ADC/DMA、I/O、DAC、underrun/overrun **均未报告** |
| 部署资源 | 目标 DSP/MCU、峰值 RAM/SRAM、量化/fixed-point、能耗、编译器 **均未报告** |

实体判定：**paper-level strict causal / 8 ms algorithmic latency（记账未公开）/ MACs-only complexity**。不能简化为「已验证的 8 ms 端侧实时系统」，更不能当作约 2 ms 系统。

## 复杂度分解（Table 1 数字）

| 变体 | Hop | Total MMACs/s | DNN | SDW-MWF | 备注 |
|---|---:|---:|---:|---:|---|
| Tango（CNN 基线） | 16 ms | 605.98 | 604.5 | 1.48 | 无延迟/复杂度约束 |
| Tango-RNN（因果） | 16 ms | 67.20 | 65.72 | 1.48 | 2 层 stateful RNN ×128 |
| Tango-RNN + GRNN(SN=8,MN=2) | 16 ms | 18.22 | 16.74 | 1.48 | 分组后的 ⋆ 配置 |
| **RT-Tango** | 4 ms | 33.41 | 28.08 | 5.33 | 4 ms 帧率，离线 SCM |
| **RT-Tango-OS** | 4 ms | 35.14 | 28.08 | 7.01 | 在线 SCM；0.49 MMACs/frame |
| 参考：GTCRN（分布式） | 16 ms | 48.98 | 48.98 | − | 单通道基线改造 |
| 参考：GTCRN（分布式） | 4 ms | 197.5 | 197.5 | − | 同帧率对照 |

要点：**帧率从 16 ms 提到 4 ms 后，SDW-MWF 成本从 1.48 涨到 5.33（在线版 7.01）**，DSP 支路占比显著上升；而 DNN 因 GRNN+FRS 反而下降。RT-Tango 在 4 ms 帧率下比同帧率的 GTCRN 高效约 5.9 倍。

## 结果与证据边界

- **支持**：在 BinauRec 子集（−5/0/5 dB）上，RT-Tango 以 33.41 MMACs/s 达到 SI-SDR 4.4/4.7 dB、SI-SIR 20.8/24.6 dB、PESQ 1.66/1.71；SN-DNN 分组到 G=8 几乎无质量损失；FRS 在 0.2 dB 内保持；32/8 asyHann 明显优于 32/8 sqrtHann。
- **不支持**：8 ms 已在目标设备通过 deadline、端到端 capture-to-playback 已测、冷启动流式质量已证明、低 SNR 人声保留/false-suppression 已证明、跨耳通信比特率已优化。
- **未报告**：参数量、RTF、采样率、训练 epochs/batch/seed、SCM 收敛曲线与 α 敏感性、跨耳链路比特率/丢包/抖动、量化、峰值内存、能耗、state reset 策略。

## 交叉链接

- 源论文：[[wiki_low_latency/sources/2026/RT-Tango 2026]]
- 概念页：[[wiki_low_latency/concepts/2607.01834-distributed-binaural-low-latency]]
- 双耳链路：[[wiki_low_latency/concepts/低比特率双耳特征链路]]、[[wiki_low_latency/entities/GCFSnet]]、[[wiki_low_latency/sources/2023/GCFSnet 2023]]
- 非对称 STFT：[[wiki_low_latency/concepts/2204.09911-short-asymmetric-stft]]、[[wiki_low_latency/sources/2022/STFT-Domain Very Low Algorithmic Latency 2022]]
- 延迟与因果：[[wiki_low_latency/concepts/严格因果与算法延迟]]、[[wiki_low_latency/concepts/低时延前端与延迟账本]]
- 人声保留验收：[[wiki_low_latency/concepts/低 SNR 人声保留评估]]
- 低复杂度参照：[[wiki_low_latency/entities/DeepFilterNet2]]、[[wiki_low_latency/sources/2023/FSB-LSTM 2023]]
