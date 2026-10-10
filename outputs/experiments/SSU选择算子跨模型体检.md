---
title: SSU 选择算子的跨模型体检
type: experiment
status: planned
started: 2026-09-20
completed:
hypothesis: "LaCo-SENet 的 state corruption 是『同时缓存过去状态 + 显式缓冲未来帧』这一组合的通用缺陷，不是它的特有 bug。库中所有做 lookahead 的流式模型都应做同一项体检；预计至少有一个模型的报告指标在启用选择性状态更新后会发生变化。"
baseline: "各模型论文报告值（见下表）"
results:
  - metric: 受影响模型数
    baseline: "待体检：DeepFilterNet2 / Nakaoka Wave-U-Net / RT-Tango / DISPATCH / LaCo-SENet（对照）"
    current: ""
  - metric: LaCo-SENet 对照（关 SSU 的代价）
    baseline: "L_tot=2/6/10 时 ΔPESQ = −1.56 / −2.00 / −2.09；L_tot=0 时 Δ=0.00"
    current: ""
notes:
  - "缺陷机理（LaCo-SENet §3.2 Challenge 3）：state buffer 若记录全部帧（含追加的 lookahead），这些帧会在后续 chunk 里出现两次——一次来自 state、一次作为新输入——输出被逐步扭曲。"
  - "修法：选择算子 Π_C(x)=x_1:C，只把当前 chunk 帧写进 state。lookahead 帧参与前向计算但永不入 state。"
  - "体检方法：对每个模型审计『(a) 是否有显式 future-frame 缓冲；(b) 是否有跨 chunk 的状态缓存；(c) 若两者都有，状态写入范围是否被限制在当前 chunk』。三项同时满足才是干净的。"
  - "DeepFilterNet2：lookahead 从**全局输入平移**注入，每个卷积保持纯因果 → 属于 (a) 有 + (b) 有，但未来帧不进入卷积状态，预期不受影响（待确认）。"
  - "Nakaoka 2021 Wave-U-Net：6.71 ms、`low_look_ahead`，分块 student → 最可疑，优先体检。"
  - "RT-Tango：论文未报告 look-ahead 与逐层 receptive field，无法判断 → 需先补 (a)(b)(c) 三项的证据。"
  - "DISPATCH：32 ms 窗 / 8 ms hop，选择性 patch 蒸馏 → 需确认 student 的流式状态语义。"
  - "这是**审计型实验**，不需要训练：先做代码/结构审计，只有审计发现缺陷时才需要重跑。"
---

# SSU 选择算子的跨模型体检

## 假设

LaCo-SENet 的 SSU 消融给出了一个很干净的因果证据：
关掉选择性状态更新后，凡是有 lookahead 的配置 PESQ 都**跌破 noisy 基线 1.97**，且随 lookahead 增大单调恶化
（$L_{tot}=2/6/10$ 时 ΔPESQ = −1.56 / −2.00 / −2.09）；而在 $L_{tot}=0$ 时 SSU 是完全的 no-op（Δ=0.00）。

这个形状说明缺陷机理与理论预测一致——**污染量正比于 lookahead 帧数**，而不是随机退化。

由于该缺陷来自「缓存过去 + 缓冲未来」这一组合本身，它应当是**通用**的。

## 体检清单

对库中每个流式模型逐项回答：

| 审计项 | 问题 |
|---|---|
| (a) 未来缓冲 | 是否存在显式的 future-frame buffer / 输入平移 / 右 padding？ |
| (b) 状态缓存 | 是否有跨 chunk（跨帧）保留的状态？ |
| (c) 写入范围 | 若有 (a)+(b)，状态写入是否被限制在当前 chunk 帧（等价于 $\Pi_C$）？ |

**三项同时满足（有 a、有 b、但 c 未限制）→ 存在 state corruption 风险，其报告指标可疑。**

## 优先顺序

1. **Nakaoka 2021 Wave-U-Net**（6.71 ms，`low_look_ahead`，离线 teacher → 在线分块 student）——最可疑。
2. **RT-Tango**（lookahead 与逐层 receptive field 均未报告，无法判断）——需先补证据。
3. **DeepFilterNet2**（lookahead 走全局输入平移、卷积保持纯因果）——预期安全，用于验证清单的有效性（阴性对照）。
4. **DISPATCH**（32 ms 窗 / 8 ms hop，选择性 patch 蒸馏）——需确认 student 流式语义。

## 主要评估

- 审计结论：每个模型的 (a)(b)(c) 三项判定 + 证据出处（页码/代码行）；
- 若发现缺陷：在修正前后对比报告指标，量化被污染的程度；
- 反向价值：若某模型确实**不受影响**，应说明其架构为何天然规避（例如未来帧从不进入状态路径），
  这本身是对「如何正确做 lookahead」的设计知识。

## 来源关联

- [[wiki_low_latency/sources/2026/LaCo-SENet 2026]]
- [[wiki_low_latency/concepts/2606.19688-latency-configurable-asymmetric-padding]]
- [[wiki_low_latency/entities/LaCo-SENet]]
- [[wiki_low_latency/sources/2022/DeepFilterNet2 2022]]
- [[wiki_low_latency/sources/2021/Teacher-Student Wave-U-Net 2021]]
- [[wiki_low_latency/sources/2026/RT-Tango 2026]]
- [[wiki_low_latency/sources/2025/DISPATCH 2025]]
- [[wiki_low_latency/concepts/严格因果与算法延迟]]
