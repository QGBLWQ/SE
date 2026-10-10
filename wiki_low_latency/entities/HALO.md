---
title: HALO - 半帧率自适应可学习算子
type: entity
created: 2026-10-07
updated: 2026-10-07
tags:
  - entity
  - model
  - stft
  - frame-rate-reduction
  - overlap-redundancy
  - causal-plugin
  - lightweight
  - interspeech-2026
source_paper: "[[wiki_low_latency/sources/2026/HALO 2026]]"
related:
  - [[wiki_low_latency/sources/2026/HALO 2026]]
  - [[wiki_low_latency/concepts/halo-2026-half-frame-rate-operator]]
  - [[wiki_low_latency/entities/GTCRN]]
  - [[wiki_low_latency/entities/LiSenNet]]
  - [[wiki_low_latency/entities/FastEnhancer]]
---

# HALO（Half-frame-rate Adaptive Learnable Operator）

> 一句话定义：一个**因果、即插即用**的 STFT 域模块，在骨干**前**用可学习动态卷积把内部帧率减半、在骨干**后**恢复回原始 STFT 网格，**不修改 STFT/ISTFT 流程、不改变骨干的逐帧接口、不增加算法延迟**，代价是**峰值每步算力不变**。

- **出处**：Interspeech 2026, pp. 2999-3003, DOI `10.21437/Interspeech.2026-601`
- **作者**：Jiadong Zhao, Dahan Wang, Yu Sun, Leyan Yang, Xiaobin Rong, Shiruo Sun, Yuxiang Hu, Jing Lu（南京大学近代声学国家重点实验室 / 地平线机器人 NJU-Horizon 联合实验室 / 三星电子中国研发中心）
- **代码**：https://github.com/dddaniel-z/HALO/
- **源页**：[[wiki_low_latency/sources/2026/HALO 2026]]

---

## 1. 定义与定位

| 项 | 内容 |
|---|---|
| 类型 | **骨干插件**（plug-in module），不是完整模型 |
| 输入 | 复频谱 $X=[\Re\{X\};\Im\{X\}]\in\mathbb{R}^{2\times T\times F}$ |
| 输出 | 复频谱 $\hat{S}\in\mathbb{R}^{2\times T\times F}$（与原 STFT 网格对齐） |
| 内部 | 骨干以**半帧率** $T/2$ 运行 |
| 因果性 | **严格因果**（不访问未来输入，不增加 lookahead）——但输出帧含**外推成分**，见 §5 |
| 解决什么 | STFT 重叠帧导致的**时域冗余** ⇒ 平均算力 |
| **不解决什么** | **峰值算力**（论文自陈）、**算法延迟**（继承前端 32 ms）、**速度证据**（无 RTF） |
| 库内定位 | 与 [[wiki_low_latency/entities/GTCRN]]、[[wiki_low_latency/entities/LiSenNet]] 同代轻量 STFT 骨干的**效率插件**；与 [[wiki_low_latency/entities/FastEnhancer]] 同属"改既有骨干"的效率路线 |

---

## 2. 组件表

| 组件 | 作用 | 实现 | 关键超参 |
|---|---|---|---|
| **降帧率算子 $D(\cdot)$** | 把 $T$ 帧压到 $\lceil T/2\rceil$ 帧 | 相邻两帧拼接成 $\mathbb R^4$ → kernel-bank 加权混合 | 核库 $\{W_k\}_{k=1}^{K}$，$W_k\in\mathbb R^{2\times4}$；$K=5$ |
| **恢复算子 $U(\cdot)$** | 把 $\lceil T/2\rceil$ 帧还原到 $T$ 帧 | kernel-bank 生成 $\mathbb R^4$ → 切成两个相邻复帧 | 核库 $\{V_k\}$，$V_k\in\mathbb R^{4\times2}$ |
| **gating 网络 $g_d / g_u$** | 预测依赖时频位置的混合权重 | 两个逐点卷积 + PReLU + 对核索引 softmax | 隐藏通道 8 |
| **骨干 $f_\theta$** | 实际的增强计算 | **任意** STFT 域逐帧骨干（论文验证了 GTCRN / DPCRN×4 / LiSenNet / UL-UNAS） | 通道加宽以对齐 MAC/s |

> [!note] 为什么"先混合核再卷积"被写成"先算 K 个基输出再加权求和"
> 论文指出两者**数学等价**，但后者在**时变自适应权重**下**更易实现**（kernel bank 可以预计算为矩阵乘，gating 只负责系数）。这是工程选择，不是方法贡献。

---

## 3. 证据表

### 3.1 Table 1：GTCRN 骨干上的消融（DNS3 test）

| 模型 | 参数 (k) | MAC/s (M) | PESQ | ESTOI | SI-SNR | OVRL | SIG | BAK |
|---|---|---|---|---|---|---|---|---|
| Noisy | – | – | 1.406 | 0.669 | 5.610 | 1.628 | 2.049 | 1.855 |
| GTCRN (baseline) | 23.67 | 33.83 | 2.101 | 0.754 | 11.390 | 2.629 | 2.981 | 3.809 |
| no-overlap STFT | 47.30 | 31.84 | 1.783 | 0.722 | 10.960 | 2.512 | 2.859 | 3.728 |
| D-FixedRed + U-FixedRest | 47.40 | 32.02 | 2.118 | 0.758 | 11.620 | 2.663 | 3.003 | 3.853 |
| D-Decimate + U-FixedRest | 47.32 | 32.70 | 2.104 | 0.755 | 11.510 | 2.600 | 2.936 | 3.817 |
| D-Decimate + U-Duplicate | 47.30 | 32.60 | **2.086** | 0.752 | 11.400 | 2.568 | 2.929 | 3.794 |
| HALO (w/o channel widening) | 24.07 | **22.05** | 2.093 | 0.754 | 11.430 | 2.625 | 2.970 | 3.826 |
| **HALO (w/ channel widening)** | 46.87 | 32.85 | **2.198** | **0.769** | **11.900** | **2.673** | **3.015** | **3.843** |

**三条读法**：
1. `D-Decimate + U-Duplicate` 的 PESQ **2.086 < 基线 2.101** ⇒ **朴素抽帧+复制比不动更差**，增益完全来自可学习算子。
2. `no-overlap STFT` 的 PESQ **1.783**（−0.318）⇒ **重叠不可直接丢弃**。
3. `HALO w/o channel widening`：MAC/s **33.83 → 22.05（−34.8%）**，PESQ **2.101 → 2.093（−0.008）** ⇒ 近乎免费的算力削减（**但仅平均口径**）。

### 3.2 Table 2：跨骨干验证（DNS3 test，全 16 行）

| 模型 | 参数 (k) | MAC/s (M) | PESQ | ESTOI | SI-SNR | OVRL | SIG | BAK | Δ PESQ |
|---|---|---|---|---|---|---|---|---|---|
| GTCRN-50% overlap | 23.67 | 33.83 | 2.101 | 0.754 | 11.390 | 2.629 | 2.981 | 3.809 | — |
| GTCRN-50% overlap + HALO | 46.87 | 32.85 | 2.198 | 0.769 | 11.900 | 2.673 | 3.015 | 3.843 | **+0.097** |
| GTCRN-75% overlap | 23.67 | 67.66 | 2.121 | 0.756 | 11.370 | 2.639 | 2.977 | 3.846 | — |
| GTCRN-75% overlap + HALO | 46.87 | 65.49 | 2.237 | 0.772 | 11.990 | 2.674 | 3.011 | 3.857 | **+0.116** |
| DPCRN-ultralight | 27.92 | 31.80 | 2.025 | 0.750 | 11.070 | 2.597 | 2.943 | 3.797 | — |
| DPCRN-ultralight + HALO | 55.03 | 31.34 | 2.212 | 0.771 | 11.920 | 2.648 | 2.990 | 3.826 | **+0.187** |
| DPCRN-light | 57.02 | 59.84 | 2.146 | 0.764 | 11.550 | 2.631 | 2.975 | 3.810 | — |
| DPCRN-light + HALO | 115.95 | 61.48 | 2.247 | 0.778 | 12.100 | 2.657 | 2.995 | 3.842 | +0.101 |
| DPCRN-middle | 207.22 | 225.11 | 2.340 | 0.788 | 12.350 | 2.713 | 3.048 | 3.865 | — |
| DPCRN-middle + HALO | 419.80 | 223.45 | 2.402 | 0.796 | 12.670 | 2.708 | 3.046 | 3.859 | +0.062 |
| DPCRN-large | 787.15 | 872.09 | 2.522 | 0.807 | 13.130 | 2.777 | 3.115 | 3.887 | — |
| DPCRN-large + HALO | 1440.00 | 869.86 | 2.536 | 0.809 | 13.150 | 2.766 | 3.105 | 3.882 | +0.014 |
| LiSenNet | 36.78 | 55.77 | 2.177 | 0.762 | 11.760 | 2.681 | 3.029 | 3.837 | — |
| LiSenNet + HALO | 64.52 | 55.76 | 2.275 | 0.778 | 12.390 | 2.703 | 3.047 | 3.847 | +0.098 |
| UL-UNAS | 168.98 | 33.61 | 2.245 | 0.773 | 12.100 | 2.681 | 3.011 | 3.859 | — |
| UL-UNAS + HALO | 205.16 | 31.26 | 2.261 | 0.777 | 12.240 | 2.684 | 3.027 | 3.848 | +0.016 |

**增益随骨干容量单调递减**（DPCRN 家族）：ultralight **+0.187** → light **+0.101** → middle **+0.062** → large **+0.014**。UL-UNAS 的 **+0.016** 落在同一趋势末端。

> [!important] 与 LiSenNet 的边际收益曲线同构
> HALO 沿"**骨干容量**"递减；[[wiki_low_latency/entities/LiSenNet]] 沿"**模块数量 N**"递减（每 +10M MACs 的 PESQ 增益 +0.171 / +0.059 / −0.006）。
> ⇒ **轻量化收益普遍边际递减**，任何单一手段都会很快见底。

---

## 4. 架构示意（ASCII）

```
            输入复频谱 X  (2 × T × F)    ← 原始 STFT 网格，50% 重叠
                    │
                    ▼
   ┌──────────────────────────────────────────┐
   │  D(·)  降帧率算子（可学习）               │
   │                                          │
   │  对 l = 0..L-1, L = ⌈T/2⌉:                │
   │    X̃(:,l,f) = cat( X(:,2l-1,f), X(:,2l,f) )   ∈ R^4     ← Eq.(5)
   │    α(l,f)   = g_d( X̃(:,l,f) )                  ∈ R^K     ← Eq.(6)
   │    X_{T/2}  = Σ_k α_k(l,f) · W_k X̃(:,l,f)     ∈ R^2     ← Eq.(8,9)
   │        核库 {W_k}, W_k ∈ R^{2×4}，K=5                     │
   │        g_d = PWConv → PReLU → PWConv → softmax           │
   └──────────────────────────────────────────┘
                    │  半帧率表示 (2 × ⌈T/2⌉ × F)
                    ▼
   ┌──────────────────────────────────────────┐
   │  骨干 f_θ(·)  ← 原封不动，仍为逐帧接口     │
   │  （GTCRN / DPCRN / LiSenNet / UL-UNAS…）  │
   │  通道加宽以把 MAC/s 拉回与基线对齐         │
   └──────────────────────────────────────────┘
                    │  半帧率输出 Ŝ_{T/2}
                    ▼
   ┌──────────────────────────────────────────┐
   │  U(·)  恢复算子（可学习）                 │
   │                                          │
   │    β(l,f) = g_u( Ŝ_{T/2}(:,l,f) )              ∈ R^K     ← Eq.(10)
   │    S̃(:,l,f) = Σ_k β_k(l,f) · V_k Ŝ_{T/2}      ∈ R^4     ← Eq.(12,13)
   │    Ŝ(:,2l,f)   = S̃(1:2, l, f)                            ← Eq.(14)
   │    Ŝ(:,2l+1,f) = S̃(3:4, l, f)                            ← Eq.(15)  ★外推帧
   │        核库 {V_k}, V_k ∈ R^{4×2}
   └──────────────────────────────────────────┘
                    │
                    ▼
            输出复频谱 Ŝ  (2 × T × F)   → ISTFT
```

★ **注意 `Ŝ(:,2l+1,f)`**：它来自一个只融合了 $(2l-1, 2l)$ 的表示 ⇒ **外推**。

---

## 5. 低时延账本与因果性审计

### 5.1 延迟账本

| 项 | 值 | 依据 |
|---|---|---|
| $\tau_{enc}$（前端缓冲） | **32 ms** | STFT 32 ms 平方根 Hann 窗（16 kHz），编码器须累积满一窗。**论文未给，这是从 STFT 参数推得的下界** |
| $\tau_{sep}$（骨干 lookahead） | **0**（HALO 不增加） | 论文 §2.4 结构论证：D 只用 $(2l-1,2l)$，U 不访问未来 |
| **HALO 引入的额外延迟** | **0** | 论文明确 "does not increase algorithmic latency" |
| **总算法延迟** | **≥ 32 ms**（继承前端） | ⇒ 距库内约 2 ms 目标 **约 16 倍** |
| 论文报告的延迟数字 | **未报告绝对值** | 只说 "unchanged" / "no additional lookahead" |
| RTF / 硬件 / 运行时 | **未报告** | 算力证据等级 **L0** |
| STFT center | **未报告** | 记入"STFT center 审计表"待办 |

> [!warning] HALO 的贡献在"算力"，不在"延迟"
> HALO 是严格因果的，但它**继承的 32 ms 前端**已经把它挡在库内 2 ms 目标之外。**不要因为它"因果"就把它当低延迟方法引用。** 它的定位是"在既有前端不变的前提下省算力"。

### 5.2 因果性审计（逐项）

| 检查项 | 结论 | 证据 |
|---|---|---|
| 是否读取未来输入？ | **否** | D 在 $l$ 只依赖 $X(:,2l-1,:)$ 与 $X(:,2l,:)$ |
| 是否有全局池化 / 全序列统计量？ | **无**（HALO 自身） | gating 是逐点卷积，作用于单个 $(l,f)$ bin |
| 恢复是否依赖未来？ | **否** | U 只从 $\hat S_{T/2}(:,l,:)$ 产生输出 |
| 是否严格因果？ | **是**（按库内"不读未来样本"定义） | — |
| **每个输出帧是否都基于该帧自身的观测？** | **否** ⚠️ | $\hat S(:,2l+1,:)$ 是**外推**：它对应的原始帧 $2l+1$ 从未进入降帧率表示 |
| 骨干本身的因果性 | **取决于所选骨干** | HALO 是 agnostic 的；论文验证的骨干（GTCRN/LiSenNet 等）均为因果系，但 HALO 不保证 |

> [!question] "严格因果"与"信息完整"是两件事
> HALO 满足前者、不满足后者。**库内其他严格因果方法（GTCRN、LiSenNet、D-GRU 等）的每一帧输出都基于该帧自身的观测。**
> ⇒ **HALO 是本库第一个"严格因果但输出帧含外推成分"的架构。** 建议跨论文比较时单列标注，不要直接与"每帧基于完整观测"的方法放在同一因果性等级里。

---

## 6. 外部独立证据

| 被核对对象 | HALO 报的值 | 原文/库内值 | 判定 |
|---|---|---|---|
| **LiSenNet 参数量** | 36.78 k | 37 k（LiSenNet 原文） | **相对误差 0.6% ⇒ 复现确认** ✅ |
| **LiSenNet 算力** | 55.77 M MAC/s | 56 M MMACs per second（LiSenNet 原文） | **相对误差 0.4%，同量纲同分母 ⇒ 复现确认** ✅ |
| **LiSenNet PESQ** | 2.177（DNS3） | 3.07（VoiceBank+DEMAND） | ⚠️ **数据集不同，不可比**（差 0.9 是数据集差异） |
| **GTCRN 参数量** | 23.67 k | 23.7 K（原文） | 吻合 ✅ |
| **GTCRN 算力** | 33.83 M MAC/s | 39.6 MMACs/s（原文）／33 MMACs（引用方 B） | ⚠️ **吻合"33"那一族 ⇒ 第三个记录，标 `[!contradiction]`** |

> [!contradiction] GTCRN 算力三记录并列
> | 口径 | 参数量 | 算力 | 出处 |
> |---|---|---|---|
> | 原论文声称值 | 23.7 K | **39.6 MMACs/s** | GTCRN 原文 |
> | 引用方 B | 48 K | **33 MMACs** | 库内既有记录 |
> | **HALO** | **23.67 k** | **33.83 M MAC/s** | HALO Table 1/2 |
>
> HALO 是**混合口径**（参数取原文、算力取 ≈33 那一族）。**三方并列记录，不选边。**
> ⇒ **引用 GTCRN 算力前必须声明取哪个口径。**

> [!note] 量纲守卫
> HALO 的 **MAC/s**（每秒乘加）与库内 GTCRN 的 **MMACs per second** 同分母、可直接比。
> 但 [[wiki_low_latency/entities/PrimeK-Net]] 报的是 **GFLOPs/整句** ⇒ **分母不同**。
> **禁止**把 HALO 的 22.05 / 33.83 M MAC/s 与 PrimeK-Net 的 44.64 G FLOPs 放进同一张效率表，也**不要换算后混比**。

---

## 7. 与库内模型对照

| 模型 | 参数量 | 算力 | PESQ | 数据集 | 算法延迟 | 与 HALO 的关系 |
|---|---|---|---|---|---|---|
| **HALO + GTCRN** | 46.87 k | 32.85 M MAC/s | 2.198 | DNS3 | ≥32 ms（未报告） | 本篇 |
| [[wiki_low_latency/entities/GTCRN]] | 23.7 K | 39.6 MMACs/s（原文口径） | 2.101（DNS3，HALO 测） | DNS3 / VBD | 未报告 | HALO 的骨干基线 |
| [[wiki_low_latency/entities/LiSenNet]] | 37 k | 56 MMACs/s | 2.177（DNS3）/ 3.07（VBD） | DNS3 / VBD | 未报告 | **共享 512/256 STFT 前端**；HALO 报其 2.177 |
| UL-UNAS | 168.98 k | 33.61 M MAC/s | 2.245（DNS3） | DNS3 | 未报告 | ⚠️ 库内暂无页面；HALO 收益最小的骨干（+0.016） |
| [[wiki_low_latency/entities/FastEnhancer]] | – | 262 M MACs | – | – | – | 同属"改既有骨干"效率路线；**证伪了"低 MACs = 快"** ⇒ HALO 的 MAC/s 收益不能自动等同于更快 |

> [!warning] HALO 与 FastEnhancer 的共同软肋
> [[wiki_low_latency/entities/FastEnhancer]] 已用实测证明"**名义 MACs 会给出错误的排序**"（262M MACs 反而比 40M 快 2.7×）。
> HALO **只报 MAC/s、无任何 RTF 或硬件数字** ⇒ 按同一逻辑，**HALO 的"省算力"不能自动等同于"更快"**。
> 这是本篇在库内**最需要提醒下游读者的一条**：它的效率主张停在 L0 证据等级。

---

## 交叉链接

- 源页：[[wiki_low_latency/sources/2026/HALO 2026]]
- 概念页：[[wiki_low_latency/concepts/halo-2026-half-frame-rate-operator]]
- 骨干基线：[[wiki_low_latency/entities/GTCRN]]、[[wiki_low_latency/entities/DPCRN]]、[[wiki_low_latency/entities/LiSenNet]]
- 前端对照：[[wiki_low_latency/entities/STFT-Very-Low-Latency-SE]]、[[wiki_low_latency/concepts/2204.09911-short-asymmetric-stft]]
- 效率路线对照：[[wiki_low_latency/entities/FastEnhancer]]
- 口径：[[wiki_low_latency/concepts/低时延前端与延迟账本]]、[[wiki_low_latency/concepts/严格因果与算法延迟]]
