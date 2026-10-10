---
title: 可融合性结构体检 × 端侧 RTF 实测
type: experiment
status: planned
started: 2026-09-26
completed:
hypothesis: "把 FastEnhancer 2025 提出的『结构审计清单』（时间轴 kernel / 归一化可融合性 / 注意力 KV cache / global pooling / 数据相关访问 / 算力是否固定 / 全序列统计）落成全库统一体检表，并挑选本库中『延迟账本为空但架构上看起来严格因果』的模型做端侧 RTF 实测——预期结论是：**参数量与 MACs 完全不能预测 RTF 排序，而清单 ② 与 ③ 能**；且 FastEnhancer 的 BN→LN 惩罚（+27%）在其自身架构之外能否复现，直接决定『可融合性』是一条普适设计定律还是单篇论文的运行时偶然"
baseline: "FastEnhancer 2025 Table 2 / Table 3：BN→LN 在参数量 92K 与 MACs 完全不变下 RTF 0.022→0.028（Xeon +27%）/ 0.026→0.029（M1 +12%）；时间轴 kernel 1→3 使 Para. 92K→187K、RTF +27%/+42% 而 SISDR/STOI 一格不动"
results:
  - metric: 全库结构审计清单完成覆盖度
    baseline: "0 个模型（本清单由 FastEnhancer 首次提出，库里尚无任何模型做过）"
    current: ""
  - metric: BN→LN 的 RTF 惩罚（Xeon / M1，跨模型复现）
    baseline: "FastEnhancer-B: +27% (Xeon) / +12% (M1)——单篇论文单架构"
    current: ""
  - metric: 时间轴 kernel 1→3 的 RTF 代价（质量零收益下）
    baseline: "FastEnhancer-B: Para 92K→187K, RTF +27%/+42%, SISDR/STOI 不变"
    current: ""
  - metric: MACs 排序与 RTF 排序的秩相关
    baseline: "FastEnhancer-B 262M/0.022 vs GTCRN 40M/0.060 —— 秩相关为负"
    current: ""
  - metric: 结构审计预测 RTF 排序的准确率
    baseline: "未验证"
    current: ""
notes:
  - "第一步（不依赖任何新论文、可立刻做）：对 wiki_low_latency 全库逐模型填 7 项审计表，标注证据来源（论文明确 / 本库推读）"
  - "第二步：挑 3–5 个『延迟账本为空但结构上无危险项』的模型（Tsunoo 2024 / D-GRU / FastEnhancer）做同一硬件同一运行时的 RTF 实测，验证清单的预测力"
  - "第三步：BN→LN 与 kernel 1→3 这两个消融在本库骨干上重做一遍，检验 +27% 是否可迁移"
  - "与 [[wiki_low_latency/concepts/2509.21867-speed-optimized-streaming-design]] §2.3 的结构审计清单直接对应"
  - "与 overview 第 8、9 条判定口径直接对应"
---

# 实验：可融合性结构体检 × 端侧 RTF 实测

## 来源

[[wiki_low_latency/sources/2025/FastEnhancer 2025]]（arXiv:2509.21867，首尔大学 2025）。

它的四条证据（全部来自同一套实验，可比性远高于跨论文拼接）指向同一个结论——
**决定实际速度的是"算子能不能在推理图上消失"，不是算术量**：

| # | 证据 | 数值 | 排除了什么解释 |
|---|---|---|---|
| A | 跨模型 | FastEnhancer-B：**262M MACs → RTF 0.022**；GTCRN：**40M → 0.060**；FSPEN：64M → 0.046；BSRNN：245M → 0.059 | 排除"MACs 决定 RTF"——6.5× 的 MACs，2.7× **更低**的 RTF |

> **⚠️ GTCRN 数值口径补注（2026-09-27，补摄 GTCRN 原文后）**：本页 GTCRN 的 **40M / 0.060** 全部来自 **FastEnhancer 的复现**（其 Table 2，脚注 a = 官方 checkpoint 评测）。
> 补摄 GTCRN 原文（[[wiki_low_latency/sources/2024/GTCRN 2024]]，ICASSP 2024）后发现：原文三处一致声称 **23.7 K / 39.6 MMACs per second**（与 40 一致 ✓），
> 但 **μNet 引用为 48 K / 33 MMACs**，且 **GTCRN 官方 repo 更新值为 48.2 K / 33.0**。
> ⇒ **GTCRN 的算力在库内有 39.6（原文）/ 40（FastEnhancer 复现）/ 33（μNet ≈ 官方实现）三套口径**。
> **本页证据 A 的结论方向不变**（33–40 M 同量级，均远低于 262 M），但**秩相关计算若把三套口径混用会出错**。
> 另注：**GTCRN 原文没有任何 RTF**——本页用的 0.060/0.042 是 FastEnhancer 的**第三方复现值**，不是 GTCRN 自报。
| B | **零算术变化**（最强） | BN→LN：**Para. 92K 不变、MACs 不变**、SISDR 19.0→**18.9**、STOI 不变，RTF 0.022→0.028（Xeon **+27%**）/ 0.026→0.029（M1 **+12%**） | 排除"参数/MACs/质量变化导致变慢"——**只剩算子可融合性与内存操作** |
| C | 纯内存变化 | 时间轴 kernel 1→3：Para. 92K→187K、RTF **+27%(Xeon) / +42%(M1)**，而 **SISDR 19.0→19.0、STOI 94.5→94.5 一格不动** | 排除"质量提升的代价"——只买到缓存开销 |
| D | 参数更少却更慢 | DPT（时间轴 GRU→MHSA）：**参数比 RNNFormer 更少**，因 **KV cache** 而 RTF 显著升高 | 排除"参数量决定 RTF" |

机理（论文原话）：时间轴 kernel $k$ 需缓存 $k-1$ 帧，「These **memory operations** significantly increase processing time」——
用的是 **memory operations** 而不是 computation。BN 在推理期可折进相邻卷积/全连接层（把 $\gamma/\sqrt{\sigma^2+\epsilon}$ 折进权重、
$-\gamma\mu/\sqrt{\sigma^2+\epsilon}+\beta$ 折进偏置），推理图上**完全不留下额外算子**；
LN 的统计量是**逐样本、逐时间步动态计算**的，依赖当前输入，**无法预先折叠**，推理图上会多出一批 reduce/mean/rsqrt 算子及随之而来的内存读写。

## 假设

本实验有两个假设层，后一层以前一层为前提。

### 假设 1（结构层）：速度排序可由"结构审计清单"预测，而不需要作者报告延迟

FastEnhancer 论文自己只做了清单中的两项（kernel、BN/LN），且没有把它一般化。
本库可以把这张清单**直接落成全库统一体检表**，并且——这是关键——**只靠架构描述即可填写，不需要作者配合**：

| # | 审计项 | 问什么 | 判"危险"的条件 | 本库现状 |
|---|---|---|---|---|
| ① | **时间轴卷积 kernel** | 是否存在时间轴 kernel $>1$ 的卷积？ | 是 ⇒ 需缓存 $k-1$ 帧，产生内存往返 | FastEnhancer 已验（危险：+27%/+42%） |
| ② | **归一化层可融合性** | 用 BN 还是 LN / InstanceNorm？ | LN / InstanceNorm ⇒ 无法折进相邻层 | FastEnhancer 已验（危险：+27%/+12%）；**本库其余模型几乎未审计** |
| ③ | **注意力是否需 KV cache** | 时间轴上是否用了 self-attention？ | 是 ⇒ 缓存随流增长 | FastEnhancer 已验（危险）；**本库 Transformer 系模型未逐一体检** |
| ④ | **是否有 global pooling** | 是否存在对整段/整块做池化或全局统计的算子？ | 是 ⇒ 要么聚合未来帧（破因果），要么必须改造 | LaCo-SENet 的 SCA 用 `AdaptiveAvgPool1d`，论文自己识别并改掉 |
| ⑤ | **是否有数据相关的不规则访问** | 是否存在 gather/scatter / 依赖输入的行选择？ | 是 ⇒ MAC 计数与实际耗时脱钩 | D-GRU 的 top-$A$ 选择、Skip-DPCRN 的整步跳过 |
| ⑥ | **算力是否固定** | 每帧的算术量是否恒定？ | 否 ⇒ 硬件按最坏情况预留，平均节省兑现不了 | Skip-DPCRN 已验（平均省 33% / 峰值只降 ~15%） |
| ⑦ | **是否有全序列统计** | 归一化/注意力是否依赖整段序列长度？ | 是 ⇒ 跨 chunk size 不一致，需改造 | **本库普遍未审计** |

> [!note] 为什么这张清单在本库特别有价值
> 本库的大多数模型（Tsunoo 2024、D-GRU、FastEnhancer……）**不报告算法延迟**。
> 但 ①–③ 可以只靠架构描述判定，**不需要作者配合**。因此它是本库在"延迟账本为空"已成为常态的情况下
> **唯一能给出判定的工具**——这恰好是本库最紧迫的方法论缺口。

### 假设 2（迁移层）："+27%"不是一个常数，甚至不一定同号

论文自己没讨论，但它的数据已经暴露了这一点：
同一次 **BN→LN**，Xeon +27% / M1 +12%；同一次 **kernel 1→3**，Xeon **+27%** / M1 **+42%**。
**两个平台给出的相对代价方向都不一致。**

所以本实验必须回答：**"可融合性"是一条算法层的设计定律，还是"这个特定模型在特定运行时上的偶然"？**
判据是：把同样的替换搬到**本库其他骨干**上，若惩罚仍显著为正，则定律成立（只是数值与硬件相关）；
若在某个骨干上惩罚为零或反向，则说明"可融合性"必须与运行时绑定讨论。

## 待验证的关键点

- **[!] 清单的预测力尚未被检验。** 清单是**规范性**的（"应该"危险），不是**实证**的。必须挑出若干"结构上无危险项"的模型做实测：
  如果它们的 RTF 排名确实优于"有危险项"的模型，清单才有资格进入本库判定口径。**这是本实验最关键的一步。**
- **[!] BN→LN 的惩罚能否跨架构复现。** 论文只在一个架构上测过。**必须先在本库 2–3 个骨干上重做**，
  否则"可融合性是一等约束"只是单篇论文的观察。
- **[!] 是否要区分"训练期可融合性"与"推理期可融合性"。** BN 与 LN 在训练期行为完全不同
  （BN 依赖 batch 统计、LN 不依赖）。"BN 更快"**只在下游推理成立**——实验中必须固定推理路径，
  不能把训练期开销混进 RTF。
- **[!] 清单 ④–⑦ 缺可测量的量化。** 论文对 ①–③ 给了 RTF 数字，但 ④–⑦ 没有对应的实验。
  本实验应给每一项至少一个**可测量的代理量**（如 ④ 的 pool 算子数、⑤ 的 gather 次数、
  ⑥ 的帧级算力方差、⑦ 的 chunk-size 敏感性曲线）。
- **[!] 不能把 MACs 与 RTF 混在同一张排名表里。** 论文的全部核心论证都建立在"两者会背离"上，
  所以本实验的输出必须**分两栏**呈现，并显式给出**秩相关**作为背离程度的度量。

## 与库中其他工作的组合可能

- **与延迟审计三件套组合**：[[wiki_low_latency/concepts/严格因果与算法延迟]]、
  [[wiki_low_latency/concepts/低时延前端与延迟账本]]、[[wiki_low_latency/concepts/2409.10358-ultra-low-latency-benchmark]]。
  本实验补的正是这三者共同缺失的一环：**在作者不报告延迟时，如何从架构反推速度**。
  三件套回答"该记哪些字段"，本实验回答"字段全空时怎么判"。
- **与 LaCo-SENet 的逐层因果尺子组合**：两者是同一审计的两个方向——
  LaCo-SENet 的尺子问"**因果性**能否逐层核验"，本实验的清单问"**速度**能否逐层预测"。
  合并后可以得到一张 `(因果性, 速度)` 二维的模型体检表，这是本库可以直接动手做、**不依赖任何新论文**的工作。
  参考 [[wiki_low_latency/concepts/2606.19688-latency-configurable-asymmetric-padding]]。
- **与动态算力子群组合**：清单 ⑤⑥ 正是 D-GRU / Skip-DPCRN 的战场。本实验可以把它们的
  "平均 vs 峰值"证据与清单的"算力是否固定"合并成一条口径。
  参考 [[wiki_low_latency/concepts/2408.12425-dynamic-gated-rnn]]、
  [[wiki_low_latency/concepts/2207.11108-inference-skipping-parallel-rnn]]。
- **不能与"只有 MACs 没有 RTF"的模型直接比较**：本库多篇（Tsunoo 2024）连参数量都没报，
  对这类模型清单只能填"未知"，**不得**用清单结果反推它们的速度排序。

## 风险与前置条件

> [!warning] 这个实验有三个前置条件
> 1. **必须固定硬件 + 运行时 + 是否含前端。** 论文的数据已经证明这两个平台给出的比例不同号，
>    所以任何跨模型的 RTF 比较都必须同机、同 ONNXRuntime 版本、同线程数、同是否含 STFT/iSTFT。
>    参照口径：FastEnhancer 用单线程 ONNXRuntime（Xeon Gold 6248R / M1），LaCo-SENet 用单线程 ONNXRuntime（Xeon Silver 4510）。
> 2. **RTF 不是延迟。** 本实验的输出**不能**被读成"这些模型离 2 ms 有多远"。
>    RTF < 1 只说"平均处理时间 < 音频时长"，与"每个 hop 必须在 deadline 前算完"是两件事。
>    即使清单全绿、RTF 全 < 0.05，也仍需 p99 / deadline / underrun 证据才能认证实时性。
>    本实验的定位是"淘汰明显不合格者"，不是"认证合格者"。
> 3. **第一步不依赖任何新论文，可以立刻开始。** 全库结构审计表是纯文本工作，
>    也是本库目前**投入产出比最高**的一项——它能立刻暴露出"哪些模型的'快'有结构依据、哪些只是声称"。
