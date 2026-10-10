---
title: TF 竞争加权损失 × 严格因果骨干：有效区间测绘与频率周期建模的因果化迁移
type: experiment
status: planned
started: 2026-10-07
completed:
hypothesis: "第 11 批的两篇论文各给出一个**与因果性不冲突**的模块/损失，但它们都在**与库内目标不同的场景**里验证：① TF Weighted Losses 的竞争加权 SDR 在**多通道 + 空间可分 + 中高 SIR** 下有效，且论文实测**极低 SIR 反转、SSN 下纯学习失败**；② SEMamba++ 的 Frequency GLP 只作用在频率轴上、**理论上不引入时间 lookahead**，但论文自陈**线性层硬编码频率 bin 数 ⇒ 无法用于变采样率/变窗长**。**主假设**：竞争加权损失可以**零因果风险、零推理开销**地迁移到单通道严格因果骨干上，但其**有效区间下界在单通道下会比多通道更早出现**（因为缺少空间线索、强竞争 bin 覆盖更广）。**次假设**：GLP 可以插进 GTCRN 的 SFE 位置并在**不破坏因果性**的前提下带来质量增益，但增益幅度受限于'固定 bin 数 vs 库内短窗前端'的冲突。"
baseline: "① [[wiki_low_latency/entities/TF-Weighted-Losses]]（Interspeech 2026, pp. 7075–7079）：WN 下 $\\mathcal{L}_{SIR\\cdot SP\\cdot SF}$ 的 **SIR 17.2 / FW-SIR 8.4 / FW-SDR 5.2 / STOI 0.64**（平均输入 SIR −8~8 dB），基线 $\\mathcal{L}_T$ 为 **13.3 / 5.1 / 4.7 / 0.63**；辅音 PA **34.0 → 36.1**（WN）/ **43.6 → 45.5**（SSN），元音 PA **43.7 → 45.5** / **46.4 → 47.9**；**代价**：辅音 SSN 的 SDR **0.5 → 0.0**、FW-SDR **6.4 → 6.1**，元音 WN 的 FW-SDR **8.4 → 7.7**；**失效边界**：极低 SIR（−8 dB）时基线在 band 6 以上更接近干净谱、基线 PA 略高；$\\mathcal{L}_{learn}$ 在 SSN 下**全部 SIR 都差于基线**。② [[wiki_low_latency/entities/SEMamba++]]（Interspeech 2026, pp. 5166–5175）：Frequency GLP 在 DNS2020 test 的 **UTMOS 3.02 / OVRL 3.21**，去掉 GP 模块后降至 **2.64 / 3.09**（且 RTF **0.021 → 0.030** 反升）；`FAN→Linear` 为 **2.96 / 3.17**（RTF 0.019）；`Serial` 为 **2.82 / 3.11**；SR（单分辨率、C 48→144）为 **2.19 / 2.48**（参数 2.7 → 9.0 M）。③ 迁移目标骨干 [[wiki_low_latency/entities/GTCRN]]：**23.7 K / 39.6 MMACs per second**（原文声称口径），PESQ 2.87（FastEnhancer 官方 checkpoint 复现值），**无 RTF / STFT center 未报告**。④ [[wiki_low_latency/entities/LiSenNet]]：**37 k / 56 MMACs per second**，VoiceBank+DEMAND PESQ **3.07**、RTF **0.028**（Xeon E5-2620 v4）。"
results:
  - metric: 竞争加权损失在单通道严格因果骨干上的 PESQ/STOI 变化（相对同骨干原损失）
    baseline: "GTCRN 原损失下 PESQ 2.87（FastEnhancer 复现口径）；LiSenNet 原损失下 PESQ 3.07（VBD）"
    current: ""
  - metric: ★ 有效区间下界：单通道下的反转点 SNR
    baseline: "多通道 + 空间可分场景下反转点在 **−8 dB 或更低**（TF Weighted Losses Fig.2/Fig.3）；单通道预期**更早出现**，但**具体值未知**"
    current: ""
  - metric: 辅音 PA / 元音 PA（Wav2Vec2，按类别分列）的变化
    baseline: "多通道基线：辅音 PA 34.0（WN）/ 43.6（SSN）；元音 PA 43.7 / 46.4（$\mathcal{L}_T$）"
    current: ""
  - metric: ★ 代价侧：SDR / SAR / FW-SDR 的下降幅度
    baseline: "多通道下辅音 SSN 的 SDR 0.5 → 0.0（−0.5）、FW-SDR 6.4 → 6.1（−0.3）；元音 WN 的 FW-SDR 8.4 → 7.7（−0.7）"
    current: ""
  - metric: GLP 插入 GTCRN SFE 位置后的质量变化（同 MAC/s 对齐）
    baseline: "GTCRN 原 SFE：PESQ 2.87 / 39.6 MMACs per second；GLP 在 SEMamba++ 内的对照增益为 GP 模块贡献 **DNS UTMOS +0.38（3.02 vs 2.64）**"
    current: ""
  - metric: 因果性是否被破坏（逐层审计）
    baseline: "预期 GLP **不引入时间 lookahead**（只作用频率轴），但需逐层核验；GTCRN 的 GT-Conv/SFE/TRA 均已声明因果"
    current: ""
  - metric: 变窗长/变采样率下的失效边界
    baseline: "SEMamba++ 自陈 GLP **无法用于采样率无关场景**（线性层硬编码 bin 数）；库内目标为 16 kHz 固定前端，若短窗化（窗长 ≤ 32 样本 @16 kHz）则 bin 数变化 ⇒ 预期**必须重训**"
    current: ""
notes:
  - "第一步（零因果风险、零推理开销、可立刻做）：把 $\\mathcal{L}_{SIR\\cdot SP\\cdot SF}$ 直接替换 [[wiki_low_latency/entities/GTCRN]] 或 [[wiki_low_latency/entities/LiSenNet]] 的原训练损失。权重的三个因子（$g_{SIR}$、$g_{SP}$、$SF$）全部用**训练期可得的干净 $S$ 与噪声 $N$** 计算 ⇒ **推理期零额外计算、不引入 lookahead、不影响因果性**（详见 [[wiki_low_latency/concepts/tf-weighted-sdr-2026]] §7 建议 1）"
  - "第二步（★ 本实验的核心产出）：在**单通道**下扫加权强度（$k$ 与阈值 $\\tau_1,\\tau_2$ 的取值范围），按输入 SNR 分档（0 / −5 / −10 dB babble）画出 **PA vs SNR** 与 **FW-SDR vs SNR** 两条曲线，**找出反转点**。若反转点高于 −5 dB，则这套加权**不能用于库内的低 SNR 目标** ⇒ 这是可判定的负结果"
  - "第三步：把**音素准确率 PA（按辅音/元音分列）**加入库内统一评估卡片。库内现用 PESQ/STOI/DNSMOS 对**辅音误抑制不敏感**（正是库内核心关切），而本篇证明 PA 能测出 PESQ 看不见的差异（辅音 34.0 vs 36.1），且辅音 PA 与元音 PA 差约 10 个百分点"
  - "第四步（次假设）：把 Frequency GLP 插进 GTCRN 的 SFE 位置，**在同等 MAC/s 对齐下**测 PESQ/STOI。注意 GTCRN 是 ERB 频带压缩 + 分组 DPRNN 结构，SFE 的输入维度与 SEMamba++ 的 $F_{eff}$ 不同 ⇒ 需先对齐频率维"
  - "第五步：GLP 的**因果性逐层核验**——虽然它只作用频率轴，但要确认实现中**没有跨帧的归一化或全局池化**（库内已踩过：PrimeK-Net 的 SCA 用 `AdaptiveAvgPool1d` 且作用域未说明）"
  - "第六步（压缩比扫描，由 HALO 触发）：若把 HALO 的帧率压缩思想用到 2 ms 短窗前端，**压缩比不应默认 1/2**——HALO 论文**未做压缩比扫描**（见 [[wiki_low_latency/concepts/halo-2026-half-frame-rate-operator]] §7），而短窗下窗-hop 关系不同 ⇒ 重叠冗余程度不同"
  - "与 [[wiki_low_latency/entities/Hybrid-Continuity-Loss]] 互补：那一篇从**损失侧**解决过抑制，本篇验证**另一种损失机制**（竞争加权）在单通道下的有效区间 ⇒ 两者可并列对照"
  - "与 [[wiki_low_latency/concepts/低 SNR 人声保留评估]] 直接对应：本实验的第 2–3 步就是在给'低 SNR 人声保留'建立**可量化的评测口径**"
  - "与 overview 判定口径第 6 条（小效应量须配统计证据）、第 19 条（保人声加权的有效区间有上下界）、第 21 条（结构化先验优于纯学习）直接对应"
  - "与 [[wiki_low_latency/concepts/semamba-pp-2026-frequency-glp]] §6 建议 1–3 直接对应（GLP 是逐帧独立、因果兼容，但硬编码 bin 数）"
  - "与 [[wiki_low_latency/concepts/2409.13285-subband-stride-and-convglu-compensation]] 的**边际收益递减曲线**呼应：本实验第 4 步若在 GTCRN 这种已高度优化的骨干上做，预期增益会**小于** SEMamba++ 内的 +0.38 UTMOS（对照 HALO 在 UL-UNAS 上只有 +0.016）"
---

# 实验：TF 竞争加权损失 × 严格因果骨干

## 来源

本实验由 **2026-10-07 第 11 批摄取**（5 篇 INTERSPEECH 2026 论文）触发，主要来自两篇：

| 论文 | 提供了什么可迁移的东西 | 为什么它自己没在库内场景验证 |
|---|---|---|
| [[wiki_low_latency/entities/TF-Weighted-Losses]] | 一套**只用训练期 oracle 权重**的 TF 竞争加权损失 ⇒ **推理期零开销、零因果风险** | 它在**多通道（4 通道双耳助听器）+ 空间可分**（干扰固定 45°）下验证，骨干是 FaSNet 波束形成器 ⇒ **空间信息承担了主要分离工作** |
| [[wiki_low_latency/entities/SEMamba++]] | **Frequency GLP**：FAN 直接作用频率轴学谐波周期 + 卷积学局部，**并联** ⇒ **只作用频率轴、不引入时间 lookahead** | 它是**非因果离线 GSR** 框架，且自陈 GLP **无法用于采样率无关场景**（线性层硬编码 bin 数） |

**关键判断**：这两件东西**在因果性上都与库内约束兼容**（一个是训练期 oracle 权重、一个只动频率轴），
**但都在错误的场景里被验证**。本实验的任务就是**把它们搬到库内的场景（单通道、严格因果、低 SNR）并测绘有效区间**。

---

## 假设

### 假设 1（主）：竞争加权损失的**有效区间下界**在单通道下会比多通道更早出现

TF Weighted Losses 把权重压向"**语音活跃但 SIR 低**"的 TF bin。论文实测：

| 条件 | 观察 |
|---|---|
| 中高 SIR + WN | ★ 最有效（WER 最低、PA 最高） |
| **极低 SIR（−8 dB）+ WN** | ⚠️ **反转**：基线在 band 6 以上更接近干净谱；基线 PA 略高 |
| 0 dB 以下 + SSN | ⚠️ **基线 WER 最低** |

**论文未讨论反转的机制**。本库提出的候选机制是：
> 极低 SIR 下，"语音活跃但 SIR 低"的 bin **几乎覆盖整个时频面** ⇒ 所有 bin 都满足加权条件 ⇒ **加权退化为近似均匀、失去区分度**。

**推论**：这个机制在**单通道**下会**更早触发**——因为多通道场景中波束形成已经把干扰压制了一部分，
剩下的"强竞争区"在时频面上**更稀疏**；而单通道没有空间线索，强竞争区**覆盖更广** ⇒ **加权更早退化**。
⇒ **可检验预测：单通道下的反转点高于 −8 dB。**

### 假设 2（次）：GLP 可以因果化迁移，但增益受限于"固定 bin 数"

GLP 只作用频率轴 ⇒ **逐帧独立、不引入 lookahead** ⇒ 理论因果兼容。
但它的线性层**硬编码频率 bin 数** ⇒ 与库内"为了压到 2 ms 而必须换短窗前端"直接冲突。

**推论**：在 **16 kHz 固定前端**下，GLP 可以插入 GTCRN 并带来增益；
但一旦为压延迟而改变窗长/hop，**GLP 必须重训**。
⇒ **可检验预测：GLP 在 GTCRN 上的增益 < 在 SEMamba++ 内的 +0.38 UTMOS**（因为 GTCRN 已高度优化，且库内轻量化收益普遍边际递减）。

---

## 实验设计

### Arm A（主）：竞争加权损失的迁移与有效区间测绘

| 项 | 设定 |
|---|---|
| 骨干 | [[wiki_low_latency/entities/GTCRN]]（23.7 K，因果）与 [[wiki_low_latency/entities/LiSenNet]]（37 k，因果）各一组 |
| 对照损失 | 原论文损失（GTCRN / LiSenNet 各自） |
| 处理损失 | $\mathcal{L}_{SIR\cdot SP\cdot SF}$（$w=g_{SIR}\cdot g_{SP}\cdot(1+k\sigma(SF(t)))$） |
| 消融 | 另加 $\mathcal{L}_{SIR\cdot SP}$、$\mathcal{L}_{logSIR}$、$\mathcal{L}_{learn}$（**后者预期在 SSN 下失败**，用于复现负结果） |
| 数据 | **单通道** VoiceBank+DEMAND（与库内可比）**+ 自建 −5 / −10 dB babble 集** |
| 评测 | PESQ / STOI / DNSMOS + **辅音 PA / 元音 PA（Wav2Vec2，分列）** + SDR/SAR/FW-SDR（**代价侧**） |
| 统计 | **Wilcoxon signed-rank，α = 5%**（沿本篇做法） |

**核心产出**：按 SNR 分档（0 / −5 / −10 dB）的 **PA vs SNR** 与 **FW-SDR vs SNR** 曲线 ⇒ **定出反转点**。

### Arm B（次）：GLP 的因果化迁移

| 项 | 设定 |
|---|---|
| 骨干 | [[wiki_low_latency/entities/GTCRN]] |
| 处理 | 用 Frequency GLP 替换 GTCRN 的 SFE（子带特征提取）模块，**先对齐频率维** |
| 对照 | GTCRN 原 SFE；`FAN→Linear`（隔离周期性贡献）；`Serial`（隔离并联贡献） |
| 对齐 | **同 MAC/s**（沿 HALO 的做法） |
| 评测 | PESQ / STOI + **逐层因果性审计** |
| 预期 | 增益 < +0.38 UTMOS（见假设 2） |

### Arm C（探索）：HALO 帧率压缩比在短窗前端上的扫描

| 项 | 设定 |
|---|---|
| 前端 | 2–4 ms 因果 STFT（库内 2 ms 路径） |
| 处理 | HALO 式降帧率+恢复，**扫压缩比 1/2、1/3、2/3** |
| 对照 | 不压缩；朴素抽帧+复制（**预期比基线更差**，复现 HALO 的边界条件） |
| 评测 | PESQ vs **平均 MAC/s** 前沿；**同时报峰值每步算力**（HALO 自陈不降峰值） |

---

## 待验证的关键点

1. ★ **单通道下的反转点在哪？** 若高于 −5 dB ⇒ 竞争加权**不能用于库内低 SNR 目标**（可判定的负结果）。
2. **辅音 PA 与元音 PA 的差距在单通道下是否更大？**（多通道下是 34–36 vs 43–48）
3. **代价是否可接受？** 多通道下 PA 上升伴随 SDR/SAR/FW-SDR 下降 ⇒ 单通道下代价可能更大。
4. **GLP 插入后因果性是否真的不破？** 需逐层核验（库内已踩过 `AdaptiveAvgPool1d` 的坑）。
5. **GLP 的增益是否随骨干容量递减？**（对照 HALO：DPCRN-ultralight +0.187 vs UL-UNAS +0.016）
6. **HALO 的压缩比在短窗下是否仍以 1/2 最优？**（论文未做压缩比扫描）

---

## 风险与前置条件

| 风险 / 前置 | 说明 |
|---|---|
| **缺少 babble 集** | 库内现有的低 SNR 评测集不统一；−5/−10 dB babble 需自建或从公开集构造 |
| **PA 评测需要 Wav2Vec2 音素模型** | 需引入 `vitouphy/wav2vec2-xls-r-300m-timit-phoneme`（本篇所用）或等价模型 ⇒ 新增依赖 |
| **GLP 的频率维对齐** | GTCRN 用 ERB 频带压缩（子带数远小于 FFT bin 数），SEMamba++ 用原始频率 bin ⇒ **两者维度语义不同，直接替换需要重新设计输入映射** |
| **训练成本** | Arm A 需 4 种损失 × 2 骨干 = 8 次训练；Arm B 需 3 次；Arm C 需 3 次压缩比 × 2 对照 |
| **HALO 无可复现代码之外的参考实现** | 其代码已开源（`github.com/dddaniel-z/HALO`），但 Arm C 需要自行接到短窗前端 |
| **Arm C 的峰值算力口径** | HALO 自陈不降峰值 ⇒ 必须**同时报平均与峰值**，否则会重复库内第 5 条判据的错误 |

---

## 交叉链接

- 触发论文：[[wiki_low_latency/sources/2026/TF Weighted Losses 2026]]、[[wiki_low_latency/sources/2026/SEMamba++ 2026]]、[[wiki_low_latency/sources/2026/HALO 2026]]
- 概念页：[[wiki_low_latency/concepts/tf-weighted-sdr-2026]]、[[wiki_low_latency/concepts/semamba-pp-2026-frequency-glp]]、[[wiki_low_latency/concepts/halo-2026-half-frame-rate-operator]]
- 迁移目标骨干：[[wiki_low_latency/entities/GTCRN]]、[[wiki_low_latency/entities/LiSenNet]]
- 相关既有实验：[[outputs/experiments/低时延不确定性感知人声保留基线]]、[[outputs/experiments/短窗前端×非对称padding的2ms路径]]、[[outputs/experiments/锚点口径复核×超轻量延迟账本]]
- 口径：[[wiki_low_latency/concepts/低 SNR 人声保留评估]]、[[wiki_low_latency/overview]]
