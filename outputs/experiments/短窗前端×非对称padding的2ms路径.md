---
title: 短窗前端 × 非对称 padding 旋钮的 2 ms 路径
type: experiment
status: planned
started: 2026-09-20
completed:
hypothesis: "LaCo-SENet 的时延下界 12.5 ms 全部来自 STFT 的 W/2 center delay，与 padding ratio 无关。把它的 400-sample 对称 STFT 换成短窗/非对称合成窗前端后，下界会降到个位数 ms，此时非对称 padding 才成为真正可扫的主旋钮；预期能在 ≤2–4 ms 算法延迟下保留大部分质量。"
baseline: "LaCo-SENet (L_enc=L_dec=0, 400/100/400 STFT @16k) = 12.5 ms / PESQ 3.35 / 1.37M"
results:
  - metric: algorithmic latency
    baseline: "12.5 ms（W/2 硬下界）"
    current: ""
  - metric: PESQ (VoiceBank+DEMAND)
    baseline: "3.35 @12.5 ms"
    current: ""
  - metric: RTF @ chunk C=1
    baseline: "4.59（Xeon Silver 4510 单线程，ONNX Runtime）"
    current: ""
  - metric: 总时延 @ RTF<1
    baseline: "62.5 ms（C=8）"
    current: ""
notes:
  - "被替换项：LaCo-SENet 的 STFT 400/100/400 samples；保留其 DSDDB / TS Block / 双 decoder 骨干与 1.37M 预算。"
  - "替换候选：短窗非对称 STFT（[[wiki_low_latency/concepts/2204.09911-short-asymmetric-stft]]）或 8 ms asyHann 合成窗（[[wiki_low_latency/sources/2026/RT-Tango 2026]] Table 5 的 32/8 asyHann 配置）。"
  - "关键风险：RT-Tango Table 5 显示合成窗缩到 8 ms 时 sqrtHann 会崩到 SI-SDR 1.2/1.8 dB，只有 asyHann 能撑住（3.7/4.3）。窗型选择比窗长更敏感，必须先做窗型扫描。"
  - "关键风险 2：短窗会降低低频分辨率，可能伤 F0/formant 保真——需同步记录人声保留指标，不能只看 PESQ。"
  - "必须同时报告：算法延迟 + 对应 chunk size + RTF。LaCo-SENet 的教训是 12.5 ms 只在 C=1 成立而 C=1 的 RTF 是 4.59。"
  - "代码基础：LaCo-SENet 已开源（https://github.com/yskim3271/LaCo-SENet）。"
  - "验收：逐层 dependency certificate；分块/全序列等价性必须重新验证（换前端后 SSU 的语义可能变化）。"
---

# 短窗前端 × 非对称 padding 旋钮的 2 ms 路径

## 假设

LaCo-SENet 的贡献是「把未来上下文从架构常量降级为训练期旋钮」，但它的旋钮被前端锁死了：
延迟公式 $\tau=1000\cdot\frac{(L_{enc}+L_{dec})\cdot h+W/2}{f_s}$ 里的 $W/2=12.5$ ms 与 $r$ 无关。
即使把 $r_R$ 压到 0（全因果），下界仍是 12.5 ms。

因此 LaCo-SENet 的 padding 旋钮**只在长窗前端下有意义**。若把 $W$ 压到 2–4 ms 量级，
$(L_{enc}+L_{dec})\cdot h$ 这一项才成为主导，旋钮才真正控制延迟。

## 设计

```text
noisy waveform
  → 短窗 / 非对称 STFT（替换 LaCo-SENet 的 400/100/400）
  → LaCo-SENet 骨干（DSDDB + TS Block + mask/phase 双 decoder），1.37M
  → 非对称 temporal padding (P_L, P_R)，r 可扫
  → selective state update (SSU)  ← 换前端后必须重新验证其必要性
  → iSTFT + OLA
```

## 主要评估

- **延迟三分账**：算法延迟（含新 $W/2$）、对应 chunk size $C$、该 $C$ 下的 RTF；
- **等价性**：chunk-wise 输出与 full-sequence 输出是否仍数值一致（LaCo-SENet 的核心断言，换前端后需重验）；
- **质量**：PESQ / STOI / CSIG / CBAK / COVL，与 LaCo-SENet 各配置点逐点对照；
- **人声保留**：短窗的低频代价必须用 F0/formant continuity、voiced energy、低 SNR 分层补上，
  否则无法判断质量变化是「抑噪变好」还是「人声被伤」。

## 为什么值得做

这是目前库中唯一一条**直接朝 2 ms 走、且每一环都有现成组件**的路径：
前端来自 2204.09911 / RT-Tango，骨干与旋钮来自 LaCo-SENet，因果审计方法来自本 Wiki 的账本概念页。

## 来源关联

- [[wiki_low_latency/sources/2026/LaCo-SENet 2026]]
- [[wiki_low_latency/concepts/2606.19688-latency-configurable-asymmetric-padding]]
- [[wiki_low_latency/concepts/2204.09911-short-asymmetric-stft]]
- [[wiki_low_latency/sources/2022/STFT-Domain Very Low Algorithmic Latency 2022]]
- [[wiki_low_latency/sources/2026/RT-Tango 2026]]
- [[wiki_low_latency/concepts/低时延前端与延迟账本]]
- [[outputs/experiments/低时延不确定性感知人声保留基线]]
