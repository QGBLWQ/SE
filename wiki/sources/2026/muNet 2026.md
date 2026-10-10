---
title: "μNet — 面向嵌入式 DSP 的超低内存语音增强"
type: source
created: 2026-09-08
updated: 2026-09-08
tags:
  - speech-enhancement
  - embedded-dsp
  - int8
  - low-latency
  - low-memory
  - quantization
source_type: paper
year: 2026
authors: "Shrishti Saha Shetu, Jose Miguel Martinez Aponte, Nagashree K. S. Rao, Sharvin Vittappan, Oliver Thiergart, Emanuël A. P. Habets"
affiliation: "International Audio Laboratories (Erlangen), Fraunhofer IIS"
venue: 2026 APSIPA ASC（arXiv 预印本；arXiv 页面未声明接收状态）
arxiv: "2608.21155"
url: "https://arxiv.org/abs/2608.21155"
related:
  - [[RNNoise 2018]]
  - [[PercepNet 2020]]
  - [[DeepFilterNet 2023]]
  - [[实时与离线语音增强]]
  - [[理想比率掩蔽 IRM]]
  - [[理想掩蔽 Ideal Mask]]
  - [[STFT与频谱图]]
  - [[2026 语音增强前沿五篇比较]]
---

```yaml
- 论文: [μNet](2026)
  ├── 要解决什么问题: 嵌入式 DSP（助听器/hearables/耳戴）上同时满足四重约束——超低内存 + 低复杂度 + 极低延迟 + 全整数(int8)运算，此前文献没有统一框架
  ├── 核心方法: ULCNet 启发的两阶段网络（先估幅度掩蔽、再估复数比值掩蔽 CRM），子带共享 GRU + 共享线性投影压参数，C-SubFR/C-SamFR 混合特征重排，全 int8
  ├── 属于哪个分支: 嵌入式/极低延迟/低复杂度语音增强（混合 DSP-DL、帧级逐帧处理）
  ├── 输入/输出: 16 kHz 带噪复数 STFT（幂律压缩幅度 + 相位）→ 增强复数谱 / 波形
  ├── 关键trick: ① 子带共享 GRU + 共享线性投影（权重复用，90 KB 静态内存主来源）② 标准卷积替代深度可分离卷积 + 全 int8 ③ NAL 可控噪声衰减 ④ 幂律压缩 PF α=0.3
  ├── 数据集: Interspeech 2020 DNS Challenge（非混响测试集）；约 1000 h 合成 16 kHz 训练数据
  ├── 对比了谁: RNNoise、GTCRN，以及自设基线 μNet V2（共享子带因果自注意力）/ V3（门控卷积）
  ├── 性能上限: 46 K 参数 / 28 MMACs / 90 KB 静态内存；μNet_MSE DNS 非混响 PESQ 1.90 / SI-SDR 13.24 / BAK(MOS) 4.03；16 ms int8 ΔSI-SDR 3.55（与相近复杂度方法相当，非全局 SOTA）
  ├── 参数量: 46 K（主模型 μNet_MSE/MT/MS/-25dB/-30dB 同一配置）
  ├── 消融关键发现: GRU 优于同规模自注意力/门控卷积且更省参数与算力；NAL -30 dB 把 PESQ 抬到 2.27，但 BAK 降到 3.71（抑噪↔保真权衡）；4 ms int8 ΔSI-SDR 仅 0.50 dB（GRU 状态漂移退化）
  ├── 遗留问题(你的机会): 4 ms int8 严重退化、未做 quantization-aware training（论文未来工作）；90 KB 不含动态工作区；无开源代码；MUSHRA 样本小且无显著性检验
  └── 跟哪篇像: [[RNNoise 2018]]、[[PercepNet 2020]]、[[DeepFilterNet 2023]]
```

# μNet：面向嵌入式 DSP 的超低内存语音增强

> Shrishti Saha Shetu, Jose Miguel Martinez Aponte, Nagashree K. S. Rao, Sharvin Vittappan, Oliver Thiergart, Emanuël A. P. Habets，*μNet: Ultra-Low-Memory and Low-Complexity Speech Enhancement for Embedded Digital Signal Processors*，arXiv:2608.21155v1（2026-08-21 提交），PDF 页眉标注 2026 APSIPA ASC，arXiv 页面未声明接收状态。[官方摘要](https://arxiv.org/abs/2608.21155)｜[HTML](https://arxiv.org/html/2608.21155)｜[演示](https://sshetu-iis.github.io/uNet/ulm/)｜[[outputs/reports/2026-09-08-frontier/enhancement/2608.21155_muNet.pdf|本地 PDF]]。无官方代码仓库。

## 1. 动机：他们为什么这么做？（motivation）

最近 DNN 语音增强在指标上大幅领先传统统计方法，但主流 SOTA 模型复杂度高、内存占用大，且通常运行在 10–40 ms 的高延迟档位——这对通用电信可行，对助听器、hearables（透传模式）、内容实时对白增强等**可穿戴/耳戴**场景不可接受。

这些场景真正的瓶颈不在单一指标，而在四个**同时出现**的工程约束：内存占用（memory footprint）、计算复杂度、算法延迟（需极低，如 ≤10 ms 量级）、以及对整数运算（int8/定点）的支持——消费级 DSP 如 Cadence Tensilica HiFi 4/5 往往只允许整数运算。

论文据此把问题定义为：**此前没有一个统一的框架能同时满足这四者**，μNet 的目标就是在一个方案里同时拿下"90 KB 静态内存 + 28 MMACs + 最低 4 ms 算法延迟 + 全 int8 可量化"，且性能"与相近复杂度的 SOTA 方法相当"（文中 abstract 原话，**不是**全局绝对 SOTA）。

## 2. 前人局限：之前的人怎么做不了？（limitation → gap）

- **逐项解决、没有合体**：已有工作在各自方向上优化——例如 ERB 滤波器组特征 + 分组卷积 + RNN 降计算量（文献 [14]）；ULCNet（文献 [13]）在 STFT 域用 channel-wise feature reorientation + 两阶段（幅度掩蔽 + 相位校正）提效率。但都把内存、延迟、定点三件事分开处理。
- **低延迟技术带不动**：文献里已有非对称分析-合成窗对、可学习变换、可训练滤波器组均衡器、未来帧预测等降延迟手段（文献 [16,20,21,22]），但这些往往依赖计算很重的模型，与"苛刻算力预算"冲突。
- **深度可分离卷积的硬件坑**：μNet 反过来指出 ULCNet 的深度可分离卷积虽降低**理论**参数量，但在消费 DSP 上因内存访问碎片化而硬件利用率差，并影响量化支持。

**gap 一句话**：文献长期没解决"延迟 × 内存 × 复杂度 × 定点"的**联合**优化。μNet 的贡献就是把这四件事放进一个可部署到 HiFi 4/5、ARM Cortex M、ADI SHARC、Qualcomm Hexagon、Airoha AB159x 的模型里。

## 3. 核心 Trick：这个做法关键在哪？（⭐ 分级）

μNet 的两阶段骨干（第一级估幅度掩蔽 $\tilde{\mathbf{M}}_m\in[0,1]$，第二级细化为 **CRM** complex ratio mask）直接继承自 ULCNet；论文的新改动在 Fig. 1 中用灰色块标出，即 C-SubFR/C-SamFR 混合重排、共享子带 GRU、共享线性投影三处，外加 §2.4 的 NAL 控制在 DNN 之外。

**⭐⭐ 权重复用（90 KB 静态内存的主要来源）**

- 扁平化特征切成两子带，用**同一个 64-hidden GRU** 处理（weight sharing），得到 128 维隐变量 $\mathbf{h}$。
- $\mathbf{h}$ 再按四段**重叠**滑窗切成 $h_k$（长度 40，索引区间 $[0,40],[24,64],[56,96],[88,128]$），用**同一**线性层投影：
  $$\mathbf{m}_k=\sigma(\mathbf{W}\mathbf{h}_k+\mathbf{b}),\qquad \mathbf{W}\in\mathbb{R}^{64\times 40}$$
  拼接四个 $\mathbf{m}_k\in\mathbb{R}^{64\times 1}$ 得到 256 点实幅度掩蔽 $\tilde{\mathbf{M}}_m\in\mathbb{R}^{256\times 1}$（Eq. 3）。
- 共享权重既削参数量，又保证滤波器在特征空间不同片段上不变。整篇文章的"90 KB"就是这套权重 + 参数在 DSP 上的静态存储。

**⭐⭐ 全 int8 可量化 + 标准卷积替代深度可分离卷积**

- 论文有意识地牺牲"理论参数量最少"，把 ULCNet 的深度可分离卷积换成**标准卷积**，换取嵌入式硬件的高利用率和 int8 量化支持；并直接用 TensorFlow TFLite post-training 量化到全 int8（10 个校准样本调变量）。
- 这是工程决策：**硬件友好 > 理论 MAC 最小**。

**⭐ 幂律压缩特征（Eq. 1–2）与 C-SubFR/C-SamFR 混合重排**

$$\tilde X_{r/i}=\operatorname{sign}(X_{r/i})\odot|X_{r/i}|^\alpha,\quad \tilde X_m=\sqrt{\tilde X_r^2+\tilde X_i^2},\quad \tilde X_p=\arctan(\tilde X_i/\tilde X_r).$$
- PF（power-law factor，幂律压缩因子）默认 $\alpha=0.3$，压缩动态范围。注意：$\alpha$ 在原文中正式名称为 power-law factor；"感知重点"体现在 C-SubFR 对低频两个 43-bin 子带的强调（§2.2 "perceptually significant low-frequency bands"），而不是这个 $\alpha$ 的名称。
- C-SubFR + C-SamFR：偏重**感知重要的低频段**，取 2 个各 43-bin 的子带；C-SamFR 以采样因子 6 跨非连续频点取 6 组 43 维特征，重排为 $\tilde X_c\in\mathbb{R}^{B\times T\times 43\times 8}$（F=43, C=8）。4 层（32 滤波器、kernel (1,3)、末三层 stride-2）卷积 + 1×1 点卷积（24 通道）展平成 144 维。
- 中间复谱特征（Eq. 4）：$\tilde Y_r=\tilde M_m\odot\cos\tilde X_p,\ \tilde Y_i=\tilde M_m\odot\sin\tilde X_p$，再 C-SubFR 到 $\tilde Y_c\in\mathbb{R}^{64\times 8}$；第二级 CNN（2 层 32 滤波器 + 1×1 到 8 通道）经 CRM 乘法 + 幂律解压输出增强谱。

**⭐ NAL 可控噪声衰减（noise attenuation level，用户可调）**

$$\hat s_{-\text{dB}}=\hat s+\beta\hat n,\quad \hat n=x-\hat s,\quad \beta=\sqrt{\frac{P_{\hat s}}{P_{\hat n}\cdot 10^{\,NAL_{dB}/10}}}$$
- $P_{\hat s},P_{\hat n}$ 分别是增强语音与残余噪声的平均功率；$\beta$ 由目标衰减量 $NAL_{dB}$ 决定，把受控残余回添到输出，让用户在"背景噪声压得多狠"与"语音保真"之间权衡。
- 注意：这是**后处理**，不是训练损失。调 NAL（如 -25/-30 dB）会改变输出，但不能当成训练目标去梯度下降。

**训练损失（§2.3）** —— MSE 在**压缩频域**算，服务于激进抑噪；多尺度 MS 损失把时域余弦相似 + 频域 MSE 结合：
$$L_{MS}=\sum_j\frac1K\sum_{k=1}^{K}\text{CS}(s_{jk},\hat s_{jk})+\underbrace{\sum_i\lVert |S_i|^\alpha-|\hat S_i|^\alpha\rVert_F^2}_{L_{spec}}$$
多目标 MT 损失再追加显式相位误差项：
$$L_{MT}=L_{spec}+\sum_i\lVert |S_i|^\alpha e^{j\phi_S}-|\hat S_i|^\alpha e^{j\phi_{\hat S}}\rVert_F^2$$

## 4. 实验里哪个消融最关键？

主结果（DNS **非混响**测试集，Table 1；下标表示不同损失或 NAL）：

| 方法 | Params(K) | MMACs | PESQ | SI-SDR | BAK(MOS) |
|---|---:|---:|---:|---:|---:|
| Noisy | – | – | 1.58 | 9.07 | 2.62 |
| RNNoise | 60 | 40 | 2.04 | 12.66 | 3.95 |
| GTCRN | 48 | 33 | 2.26 | **14.62** | 3.98 |
| μNet V2（自注意力） | 52 | 32 | 1.81 | 12.28 | 3.92 |
| μNet V3（门控卷积） | 55 | 32 | 1.85 | 12.44 | 3.96 |
| μNet_MSE | 46 | 28 | 1.90 | 13.24 | **4.03** |
| μNet_MT | 46 | 28 | 2.18 | 12.74 | 3.95 |
| μNet_MS | 46 | 28 | 2.13 | 13.27 | 3.99 |
| μNet_-25dB | 46 | 28 | 2.24 | 13.61 | 3.55 |
| μNet_-30dB | 46 | 28 | **2.27** | 13.53 | 3.71 |

> 加粗为各指标列的全表最优值（PESQ/SI-SDR/BAK 越高越好）。μNet 五个变体（MSE/MT/MS/-25dB/-30dB）共享同一参数与算力（46 K / 28 MMACs）。

> [!contradiction] **GTCRN 的 48 K / 33 与 GTCRN 原文的 23.7 K / 39.6 无法调和（2026-09-27 补注）**
> 本表把 GTCRN 记为 **48 K 参数 / 33 MMACs**，而 GTCRN 原文（[[wiki_low_latency/sources/2024/GTCRN 2024]]，ICASSP 2024, pp. 971–975）在 Abstract、§3.2、§4 **三处一致**声称 **23.7 K 参数 / 39.6 MMACs per second**，且该值与原文 Table 1 末行（23.67 K / 39.63 M/s）**内部自洽**。
> 两者**参数差 2.03×（48 / 23.7）、MACs 差 0.83×（33 / 39.6）——方向相反**，**不可能来自同一模型的同一配置**。
> **一个高度吻合的线索**：本表的 **48 K / 33** 与 GTCRN **官方 repo** 的更新值 **48.2 K / 33.0 MMACs** 几乎完全一致 ⇒ 强烈提示**本表引的是官方实现的实测规模，而 23.7 K / 39.6 是论文的设计声称值**。差异原因 GTCRN 论文从未说明。
> **本页不单方面采信任何一方**：保留 48/33（与官方实现吻合），同时标注原文的 23.7/39.6。**引用本表做效率比较时，必须同时声明口径。**
> 另注：本表 GTCRN 的 **PESQ 2.26 / SI-SDR 14.62** 与原文 Table 2 的 **2.87 / 18.83** 不同，说明两者用的**测试集/口径不同**（本表 Noisy 为 PESQ 1.58 / SI-SDR 9.07；原文 Table 2 的 Noisy 为 1.97 / 8.45）。

四条关键结论：

1. **时序模块即消融（最关键）**：把共享子带 GRU 换成共享子带因果自注意力（V2）或门控卷积（V3），三个指标全面退步（PESQ 1.90→1.81/1.85；SI-SDR 13.24→12.28/12.44；BAK 4.03→3.92/3.96），还更贵（46K→52/55K、28→32 MMACs）。**GRU 是又省又好**的选择。
2. **NAL 取舍可量化**：MSE 版 BAK 4.03 是全场最好（激进抑噪，但如文献 [13] 所言有过度抑制倾向）；调到 -30 dB 把 PESQ 抬到 2.27（全场最高），代价是 BAK 掉到 3.71。直观呈现"残余噪声 ↔ 语音失真"权衡。
3. **相对 GTCRN**：SI-SDR 上 GTCRN 14.62 最高（μNet 13.24）；μNet 的卖点是 BAK 最好 + 逐帧处理。论文脚注强调 GTCRN 有效复杂度更高（需缓冲最多 16 帧中间特征，无法与 RNNoise/μNet 的逐帧处理直接比）。
4. **量化 × 延迟退化（Table 2，Δ 相对 Noisy）**：

| 延迟 | float32 ΔPESQ / ΔSI-SDR | int8 ΔPESQ / ΔSI-SDR |
|---|---:|---:|
| 16 ms | 0.35 / 3.59 | 0.40 / 3.55 |
| 8 ms | 0.34 / 3.09 | 0.24 / 2.31 |
| 4 ms | 0.21 / 2.52 | 0.10 / 0.50 |

16 ms 下 int8 几乎无损；延迟越低退化越明显，论文归因于 GRU 状态在低延迟下更新更频繁导致的漂移。**不能把"全 int8"写成所有延迟档都无损**——4 ms int8 的 ΔSI-SDR 仅约 0.50 dB。

主观听测（webMUSHRA，10 听者 × 10 样本）记为：16 ms float32 下 μNet_MSE 均值 77.78，高于 GTCRN 74.24（Fig. 3，95% 置信区间）；延迟维度上 4 ms 掉到 57.87，明显低于 8 ms（69.20）/16 ms（72.44）（Fig. 5）。样本极小，**原文未给显著性检验**，只能当方向性证据。

## 5. 这个方向还剩什么问题没解决？（future work / limitation）

**论文自己承认的**：
- 结论段明确：future work 是引入 **quantization-aware training**，进一步缩小超低延迟下 int8 的性能缺口——即承认当前 post-training 量化在 4 ms 档退化明显。

**读出来的隐藏问题**：
- **90 KB 是不完全记账**：它只含模型参数/权重的静态存储，**不含推理时的平台相关动态工作区**（§3.5 原文括号明确）。引用时不能把 90 KB 当"总内存"。
- **性能口径要严**：全文主张是"与相近复杂度的 SOTA 相当"，并非全面 SOTA（SI-SDR 落后 GTCRN，且只测 DNS 非混响单数据集）。
- **无法复现**：无官方代码；声称 70 MHz 在 HiFi 4 / NXP RT685 上实时，需以具体 DSP 工具链复核。
- **主观证据弱**：10×10 的 MUSHRA 无显著性检验，样本极小，结论只能定性参考。
- **单通道、16 kHz**：论文称可改参数适配更高采样率，但正文只验证了 16 kHz 单通道。

## 6. 本论文在库中的位置关联（cross-reference matrix）

| 维度 | 论文/页面 | 关系 |
|---|---|---|
| 前身/基石 | [[RNNoise 2018]] | 同属"轻量端侧实时"哲学；μNet 的全 int8/定点目标呼应 RNNoise 的 8-bit 权重量化；ULCNet→μNet 的 channel 重排与 RNNoise 的频带思路同源 |
| 前身/基石 | ULCNet（文献 [13]，库内无独立页，⚠️ 未建页） | μNet 的两阶段（幅度掩蔽→CRM）+ channel-wise feature reorientation + 幂律压缩均直接继承 ULCNet；μNet 的灰色改动块就是"对 ULCNet 的增量" |
| 同分支竞品 | [[PercepNet 2020]] | 都在助听器/耳戴类低功耗实时场景；PercepNet 走感知频带 + 后滤波，μNet 走静态内存 + 全 int8 的嵌入式 DSP 路线，二者目标设备重叠但优化点不同 |
| 同分支竞品 | [[DeepFilterNet 2023]] | 都是 DSP-DL 混合实时路由；量级差很大（DeepFilterNet 约 0.5M 参数 vs μNet 46K），一个求复数深度滤波表达能力，一个求极致轻量 |
| 跨分支类比 | [[理想比率掩蔽 IRM]] / [[理想掩蔽 Ideal Mask]] | μNet 第二级输出是 CRM（复数比值掩蔽），是掩蔽类方法谱系里的嵌入式实例，可与掩蔽概念页互相印证 |
| 跨分支类比 | [[实时与离线语音增强]] | μNet 是"实时 / 极低延迟"档（4–16 ms 算法延迟、逐帧因果）的典型代表，概念页可作为归类锚点 |
| 库内索引 | [[2026 语音增强前沿五篇比较]] | 主题页把 μNet 与其余四篇 2026 前沿并排，强调"不得跨设置排 SOTA"，并点出 90 KB 不含动态工作区、4 ms int8 仅 0.50 dB 等边界 |
| 后续/扩展 | ⚠️ 疑似无 | 库中暂未收录直接基于 μNet 的后续工作。**2026-09-27 更新：对比对象 GTCRN 已补摄入库**，见 [[wiki_low_latency/entities/GTCRN]] 与 [[wiki_low_latency/sources/2024/GTCRN 2024]]（ICASSP 2024, pp. 971–975） |

## 7. 一句话总结"江湖地位"

```text
2026 | 嵌入式语音增强 | ULCNet 之上用子带共享 GRU/共享线性投影把静态内存压到 90 KB、28 MMACs、可全 int8、4–16 ms → 与 RNNoise/GTCRN 等相近复杂度方法并立的"耳戴/助听器可部署"工程标杆（性能相当而非 SOTA）
```

## 附：复现范围（训练细节）

约 1000 h Interspeech 2020 DNS 合成数据，16 kHz、SNR -10–30 dB，50% 随机 RIR 卷积；32 ms sqrt-Hann 窗 STFT（低延迟实验用非对称 Hann 分析 + 更短 Hann 合成窗对，逐帧 overlap-add，延迟由合成窗长决定）；Adam 初值 $4\times10^{-4}$、每 3 epoch 降 10 倍；随机低通、上采样、不同 STFT 窗增强。TFLite post-training int8 用 10 个校准样本。论文未公开实现。