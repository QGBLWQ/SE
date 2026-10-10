---
title: GTCRN 2024 - 23.7K 参数的超轻量子带分组 DPRNN（ICASSP 2024）
type: source
created: 2026-09-27
updated: 2026-09-27
tags:
  - speech-enhancement
  - single-channel
  - tf-domain
  - complex-ratio-mask
  - ultralight
  - 23.7k-parameters
  - subband
  - erb-filterbank
  - band-merging
  - band-splitting
  - grouped-rnn
  - grnn
  - dual-path-rnn
  - grouped-dprnn
  - grouped-temporal-convolution
  - shufflenet
  - subband-feature-extraction
  - temporal-recurrent-attention
  - dpcrn-backbone
  - paper-claimed-causal
  - unreported-center
  - 16ms-hop
  - latency-ledger-gap
  - vctk-demand
  - dns3
  - icassp-2024
source_type: paper
year: 2024
authors: Xiaobin Rong; Tianchi Sun; Xu Zhang; Yuxiang Hu; Changbao Zhu; Jing Lu
venue: ICASSP 2024
venue_status: published
arxiv: 无（非 arXiv 论文）
doi: 10.1109/ICASSP48485.2024.10448310
local_pdf: raw/papers/low_latency_causal_se/GTCRN-ICASSP2024.pdf
evidence_policy: local_pdf_only
related:
  - [[wiki_low_latency/entities/GTCRN]]
  - [[wiki_low_latency/concepts/gtcrn-2024-ultralight-subband-grouped-dprnn]]
  - [[wiki_low_latency/entities/DPCRN]]
  - [[wiki_low_latency/concepts/2107.05429-dual-path-recurrent-context]]
  - [[wiki_low_latency/entities/FastEnhancer]]
  - [[wiki_low_latency/sources/2025/FastEnhancer 2025]]
  - [[wiki_low_latency/sources/2026/RT-Tango 2026]]
  - [[wiki_low_latency/sources/2026/PSMSE 2026]]
  - [[wiki_low_latency/sources/2026/Early Exit Compute-Matched 2026]]
  - [[wiki_low_latency/entities/RT-Tango]]
  - [[wiki_low_latency/entities/Early-Exit-Conv-FSENet]]
  - [[wiki_low_latency/concepts/2509.21867-speed-optimized-streaming-design]]
  - [[wiki_low_latency/concepts/2609.29867-compute-matched-dynamic-depth]]
  - [[wiki_low_latency/concepts/严格因果与算法延迟]]
  - [[wiki_low_latency/concepts/低时延前端与延迟账本]]
  - [[wiki_low_latency/concepts/低 SNR 人声保留评估]]
  - [[wiki/sources/2026/muNet 2026]]
---

~~~yaml
- 论文: [GTCRN: A Speech Enhancement Model Requiring Ultralow Computational Resources](2024)
  ├── 要解决什么问题: DNN 语音增强的 SOTA 从数 GMACs 到数十 GMACs，"难以部署到耳机/助听器这类低功耗端侧设备"；已有的轻量方案里只有 RNNoise 足够小，但性能有限，其余（TRU-Net / DeepFilterNet / PercepNet / DPCRN-CF）"对低功耗端侧仍太大"
  ├── 核心方法: 以 DPCRN 为 backbone，用**分组策略**把模型压到极小 —— ① BM/BS 只在 2 kHz 以上按 ERB 尺度压频带（192→64，低频 65 维保留 ⇒ 129 维）；② **G-DPRNN**（GRNN 的分组循环 + DPRNN 的双路径，组数=2，inter-frame 用单向 GRU 保因果）；③ **GT-Conv**（ShuffleNetV2 unit + 时间膨胀深度可分离卷积，channel split → 两路 → concat → channel shuffle）；④ 可选 **SFE**（频率轴 unfold 把子带关系搬进 channel 维）与 **TRA**（时间能量 → 池化 → GRU → FC → sigmoid 乘性掩蔽）。输出 tanh 约束的 CRM
  ├── 属于哪个分支: 单通道时频域复数掩蔽增强 / **超轻量架构设计（< 0.05 M）** / 子带-ERB 压缩路线；**不是**知识蒸馏、**不是**动态算力、**不是**严格因果低时延前端（hop 16 ms）
  ├── 输入/输出: 输入 = 带噪谱的**实部、虚部、幅度**在 channel 维拼接（STFT：sqrt-Hanning 窗 32 ms、hop 16 ms、FFT 512）；输出 = tanh 约束在 [-1,1] 的**复数比率掩蔽 CRM**（实部与虚部），不是幅度掩蔽
  ├── 关键trick: 把"分组"同时用在三处 —— 通道（GT-Conv 的 channel split/shuffle）、循环层（GRNN 的 2 组）、频带（ERB 频带压缩）。最关键的是 **TRA 用极低成本换到质量**：只加 **+0.47 M/s** MACs（33.91→34.47）与约 **+8.3 K** 参数（13.35→21.65，含 TRA 自身权重），SISNR 9.87→10.25、PESQ 1.87→1.91；对照 SFE 花 **+5.16 M/s** 只换到 SISNR 9.87→10.10
  ├── 数据集: **VCTK-DEMAND** [20]（16 kHz；训练 11,572 条/28 说话人，验证 1,572 条，测试 824 条/2 说话人）；**DNS3** [21]（大规模；加入 DiDiSpeech [22] 中文语料；SNR −5~15 dB，保留前 100 ms 反射；训练 720,000 对 10 秒数据，验证 840 / 测试 800 对）+ **DNS challenge 3 blind test set**。两数据集间的消融用的是 DNS3 中约 100 小时的子集
  ├── 对比了谁: 消融里比 **TA**（[24] 的 time-dimension attention）；主结果比 **RNNoise (2018) / PercepNet (2020) / DeepFilterNet (2022) / S-DCCRN (2022)**（VCTK-DEMAND，Table 2）与 **RNNoise / S-DCCRN**（DNS3 blind，Table 3）
  ├── 性能上限: VCTK-DEMAND 上 **SISNR 18.83 / PESQ 2.87 / STOI 0.940**（Table 2，表内 PESQ/SISNR 最高）；DNS3 blind 上 **DNSMOS-P.808 3.44 / BAK 3.90 / SIG 3.00 / OVRL 2.70**（Table 3，P.808 与 BAK/OVRL 表内最高，SIG 与 RNNoise 持平于 3.00）；DNS3 test 消融中最好配置 **SISNR 10.39 / PESQ 1.94 / STOI 0.844**
  ├── 参数量: 摘要、§3.2、结论三处一致写作 **23.7 K 参数 / 39.6 MMACs per second**（对应 Table 1 的 SFE✓+TRA✓ 行）；但**库内三方口径不一致**：本篇 23.7 K/39.6，FastEnhancer 记为 24 K/40 M，μNet 记为 48 K/33，PSMSE 记为 23.7 K（与原文一致）。详见 §4.8 的 `[!contradiction]`
  ├── 消融关键发现: **Table 1 的 7 行构成 2×2×2 的部分因子设计**（SFE/TA/TRA 三开关）。TRA 相对 TA：MACs 33.91→34.47（+0.56 M/s）+ 参数 14.84→21.65（+6.81 K），SISNR 9.87→10.25（+0.38）/ PESQ 1.87→1.91（+0.04）。SFE 相对 baseline：MACs 33.91→39.07（+5.16 M/s）+ 参数 13.35→15.37（+2.02 K），SISNR 9.87→10.10（+0.23）/ PESQ 1.87→1.90（+0.03）。**两开关同时打开的增幅（+0.42 SISNR / +0.05 PESQ）小于单独打开之和（+0.61 SISNR / +0.07 PESQ）** —— 论文未讨论这个次可加性
  ├── 遗留问题(你的机会): ① **通篇无算法延迟、无 RTF、无目标硬件、无实时因子**，唯一时延相关数字是 hop 16 ms；② **STFT 的 center 锚定完全未报告**（本库一等审计项）；③ 所有 conv 的 padding 方式未报告、GT-Conv2D 的时间感受野未给出（本库推得 3/5/11 帧）；④ **无逐层因果证据链**，因果性只有一句"so that the causality of the model can be guaranteed"；⑤ 评测只有 SISNR/PESQ/STOI + DNSMOS，**无 WER/ASR、无主观 MOS、无负 SNR 分层、无噪声类型分层、无 false-suppression**；⑥ 无种子数、无方差、无置信区间；⑦ **Table 2 的 RNNoise/PercepNet 的 SISNR/STOI 为空、S-DCCRN 的 MACs 为空**，不是完整矩阵
  └── 跟哪篇像: [[wiki_low_latency/entities/DPCRN]]（直接 backbone，GTCRN = DPCRN + 分组 + ERB + SFE/TRA）；[[wiki_low_latency/entities/FastEnhancer]]（同属子带超轻量路线，但 FastEnhancer 明确批评子带方案抬高 RTF —— **本库一对直接冲突**）；[[wiki_low_latency/entities/RT-Tango]]（借用 GTCRN 的 ERB 压缩，并在 4 ms hop 下把 GTCRN 重配到 197.5 MMAC/s）
~~~

# GTCRN: A Speech Enhancement Model Requiring Ultralow Computational Resources

> Xiaobin Rong<sup>1,2</sup>; Tianchi Sun<sup>1,2</sup>; Xu Zhang<sup>3</sup>; Yuxiang Hu<sup>2</sup>; Changbao Zhu<sup>2</sup>; Jing Lu<sup>1,2</sup>
> <sup>1</sup> Key Laboratory of Modern Acoustics, Nanjing University, Nanjing 210093, China（南京大学近代声学重点实验室）。
> <sup>2</sup> NJU-Horizon Intelligent Audio Lab, Horizon Robotics, Beijing 100094, China（地平线）。
> <sup>3</sup> Jiangsu Thingstar Information Technology Co., Ltd., Nanjing 210046, China。
> ICASSP 2024, **pp. 971–975**，DOI `10.1109/ICASSP48485.2024.10448310`，5 页。
> 基金：National Natural Science Foundation of China, Grant No. 12274221（§5 Acknowledgements）。
> 开源代码：[https://github.com/Xiaobin-Rong/gtcrn](https://github.com/Xiaobin-Rong/gtcrn)（§3.3.2 正文给出）。
> **本页的核心不是复述它的 PESQ，而是把"超轻量"这个档位钉在账本上**：GTCRN 是本库"**23.7 K 参数达到 PESQ 2.87**"的**锚点**，也是 [[wiki_low_latency/entities/FastEnhancer]] 攻击子带路线时的**靶子**。本页把它拆成四笔账分别审计：**参数量/算力口径**、**因果性与延迟账本**、**消融的可分离性**、**人声保留与评测完整性**。

> [!note] 发表状态：**已正式出版的会议论文**（本库 `venue` 可信度最高档）
> 依 `evidence_policy: local_pdf_only`，本页核对的是**本地 PDF 上的出版级证据**：
> 1. **版权行**（p.1 页脚，逐字）：`979-8-3503-4485-1/24/$31.00 ©2024 IEEE`；
> 2. **会议名**（同处）：`ICASSP 2024 - 2024 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP)`；
> 3. **DOI**（同处）：`DOI: 10.1109/ICASSP48485.2024.10448310`；
> 4. **页码**：p.1 页脚 **971**、p.2 → **972**、p.3 → **973**、p.4 → **974**、p.5 → **975**，即 **pp. 971–975**。
>
> 四项齐备 ⇒ `venue: ICASSP 2024` + `venue_status: published`，**不是**"作者声称"、**不是**预印本。
>
> **本论文没有 arXiv 版本**——这一点在 frontmatter 写为 `arxiv: 无（非 arXiv 论文）`。它是**先投会议、直接出版**的工作；本库此前收录的多数 low_latency 条目是 arXiv 预印本，**本篇是例外**，因此本库**无法**用 arXiv 元数据（Comments / Journal-ref）交叉核对，**只能以本地 PDF 的版权行与页码为唯一证据**。

> [!contradiction] **页码冲突——本库第二次遇到同一篇文献的页码不一致，本次可以定案**
> - **本篇本地 PDF**（p.1/p.5 页脚逐字核对）：**pp. 971–975**。
> - **[[wiki_low_latency/sources/2026/Early Exit Compute-Matched 2026]] 的引文 [2]**（据其 page5 渲染图逐字核对）：**pp. 10286–10290**。
> - 更早，[[wiki_low_latency/sources/2025/FastEnhancer 2025]]、[[wiki_low_latency/sources/2026/RT-Tango 2026]] 等页面按 **971–975** 引用。
>
> **本页可以判定 971–975 是正确的**：证据来自**论文 PDF 自身的页脚印刷页码**（971/972/973/974/975 逐页递增，且与 5 页篇幅完全吻合），这是**一手证据**；而 10286–10290 来自**第三方论文的参考文献著录**（二手转录）。
> **处置**：本页把 GTCRN 记为 **pp. 971–975**，并在本页 re-submit 该结论给主 agent，建议在 [[wiki_low_latency/sources/2026/Early Exit Compute-Matched 2026]] 第 774–782 行的 `[!question]` 上补一条"已由 GTCRN 原文页码定案"。**本页不修改那个文件**（按分工，中央页面与既有页面由主 agent 处置）。

> [!warning] PDF 转换质量与阅读说明
> 原 PDF 共 5 页，PyMuPDF 文本抽取（`tmp/pdf_extract/gtcrn.txt`，3,697 行）**结构上可读**，但**双栏排版与公式排版导致大量行碎片化**（几乎每个词组独占一行）。本页对以下七类问题用**页面渲染图**逐条核对，`wiki_low_latency/assets/gtcrn_2024/`：
> 1. **Eq. (1) 的括号结构在抽取文本中完全错乱**（`gtcrn.txt` 第 1574–1594 行把 $\mathcal L$、$\alpha$、$\beta$、下标拆散到 6 行）。**看 page3 渲染图可完全确认**：$\mathcal L=\alpha\mathcal L_{\text{SISNR}}(\tilde s,s)+(1-\beta)\mathcal L_{\text{mag}}(\tilde S,S)+\beta\left(\mathcal L_{\text{real}}(\tilde S,S)+\mathcal L_{\text{imag}}(\tilde S,S)\right)$。**注意这与本任务 brief 给出的骨架不同，见下方 `[!contradiction]`。**
> 2. **Table 1 的勾选标记 `✓`/`✗` 在文本抽取中丢失整齐度**（`gtcrn.txt` 第 2273–2355 行能看到 `✗`/`✓` 但列归属易错）。**page4 渲染图**逐格核对 7 行 × 8 列，确认 SFE/TA/TRA 三列的勾选分布与数值配对。
> 3. **Table 2 的加粗在抽取中丢失**（`0.02`、`0.04`、`18.83`、`2.87`、`0.940` 在 GTCRN 行为粗体；`0.942` 在 DeepFilterNet 的 STOI 列为粗体）。以**page4 渲染图**为准。
> 4. **Table 3 的表头是双层结构**（`DNSMOS-P.808` 单列 + `DNSMOS-P.835` 下挂 `BAK / SIG / OVRL` 三列）——抽取文本把它们平铺（`gtcrn.txt` 第 2609–2615 行），**必须看 page4 渲染图**才能确认列归属。**特别注意**：page4 渲染图上 `DNSMOS-P.835` 表头下**只有三个子列 BAK/SIG/OVRL**，其位置恰在 `DNSMOS-P.808` 列右侧，**本页据此确认 Noisy 行的 `2.96` 属 P.808，`2.65 / 3.20 / 2.33` 属 BAK/SIG/OVRL**。
> 5. **Fig. 5 的 PESQ/STOI 数字在文本流里没有面板标签**，需靠坐标 + 裁剪图目视双重复核才能定归属（见下方 §4.6 的 `[!question]`，**初稿曾误判为"与正文矛盾"，已改正为一致**）。
> 6. **Fig. 1–Fig. 4 的图体在抽取中全部丢失**，只留下模块名（`BM`、`Conv`、`GT-Conv`、`G-DPRNN`、`BS`、`DeConv`、`SFE`、`P-Conv2D`、`DD-Conv2D`、`TRA`、`Channel Split`、`Concat`、`Channel Shuffle`、`Reshape`、`Unfold`、`GRU`、`FC`、`Avg Pool`、`Square`、`Sigmoid`、`Aggregation`、`Generation`）。本页对 Fig. 1–4 的描述来自**page2 渲染图**。
> 7. **参考文献的卷页号在抽取中被拆行**（如 `ICASSP` 与 `, 2020, pp. 46–50` 分成两行）。本页引用的 [3][7][15][16][17][18][19][24][25] 等条目已按**page5 渲染图**核对。
>
> 论文**未报告**的字段（**算法延迟口径与数值**、**STFT center/帧锚定**、**look-ahead**、**group delay**、**warm-up**、**state reset**、**逐层 padding**、**RTF**、**p50/p95/p99**、**目标硬件**、**峰值 RAM/SRAM**、**功耗**、**量化**、**端侧实测**、**长流稳定性**、**ASR WER**、**主观 MOS**、**负 SNR 分层**、**噪声类型分层**、**false-suppression**、**SPP/VAD**、**F0/formant/prosody**、**voiced energy**、**随机种子数与方差**、**GRU 隐层维度**）在本页一律写「未报告」，**不作任何补写**。

---

## 1. 他们为什么这么做？（motivation）

### 1.1 任务与对象

单通道语音增强，面向**"低功耗端侧设备，例如耳机与助听器"**（p.1 §1 原文：`practical deployment in end devices with low power consumption requirements, e.g., earphones and hearing aids`）。论文在 §1 把动机写成一条**算力落差**（p.1 §1 逐字）：

> "Most state-of-the-art (SOTA) SE models call for **substantial computational resources ranging from several GMACs to tens of GMACs**, making them **infeasible to be deployed on edge devices** for practical applications."

即：**SOTA 的算力量级（GMACs ~ 数十 GMACs）与端侧预算之间存在 3–4 个数量级的落差**。这个落差的量级感很重要——它决定了本文的目标不是"再省 20 %"，而是"**换个量级**"。

> [!note] 与本库其他条目的动机差异
> 本库绝大多数低时延论文的动机是**延迟约束**（约 2 ms、严格因果、助听器端到端）。
> **GTCRN 的动机是算力预算，不是延迟**——它的目标场景（耳机/助听器）虽然也受延迟约束，但论文**全文未把延迟写进 motivation**，也没有任何延迟数字。这一点决定了它在库中的定位：**它是"超轻量"这个横轴的锚点，而不是"低时延"这个横轴的候选**。详见 §5.3。

### 1.2 前人方案的三种路线与各自的不足

论文把轻量化路线分成三类（p.1 §1），并逐一指出不足：

| 路线 | 代表 | 论文的评述（逐字） |
|---|---|---|
| **① 压缩已有大模型** | pruning / quantization [8, 9] | 论文只提了一句，未批评，也未采用 |
| **② 高效架构设计** | **TRU-Net [10]**（一维卷积沿频率/时间轴解耦 + depth-wise conv 替代标准卷积）；**parallel GRUs + optimized skip connections [11]** | 论文把它们列为"可以设计出 tiny SE model"的另一类，未批评 |
| **③ 轻量模型 + 后处理** | **RNNoise [12]**、**PercepNet [13]**（低分辨率谱包络上粗增强 + pitch comb filter 做谐波间细节抑制）；**DeepFilterNet [14]**（PercepNet 基础上用 UNet-like DNN 增强谱包络 + deep filtering 增强周期成分）；**DPCRN-CF [15]**（DNN pitch estimator + learnable comb filter） | 论文的批评最重（见下） |

论文对路线 ③ 的批评（p.1 §1 逐字）：

> "**However, despite the impressive reduction in computational overhead achieved by these approaches, they are still too large for practical deployment in end devices with low power consumption requirements, e.g., earphones and hearing aids, with the exception of RNNoise, which is compact enough whereas suffers from limited performance.**"

这条批评的结构值得拆开看，因为它**同时否定了两端**：

- **PercepNet / DeepFilterNet / DPCRN-CF**：算力降了，但**仍然太大**；
- **RNNoise**：**足够小**（0.06 M 参数 / 0.04 G MACs，Table 2），但**性能有限**（Table 2 的 PESQ 2.29，表内最低）。

⇒ **gap = "够小"与"够好"之间没有交集**。这正是 GTCRN 要填的位置：**在 RNNoise 的算力量级上，做到接近 DeepFilterNet 级别的质量**。

### 1.3 论文的自我定位：用词是 "competitive"，不是 "state-of-the-art"

这一条对本库很重要，因为**论文自己的措辞与它的实际结果有落差**。逐字摘录三处：

| 出处 | 原文 |
|---|---|
| Abstract（p.1） | "our proposed model **not only surpasses RNNoise** ... **but also achieves competitive performance** when compared to recent baseline models with significantly higher computational resources requirements." |
| §4 结论（p.4） | "our model **not only outperforms RNNoise by a substantial margin** on the VCTK-DEMAND and DNS3 dataset, **but also achieves competitive performance** compared to several baseline models with significantly higher computational overhead." |
| §3.3.2（p.4） | "It is evident that GTCRN **not only outperforms RNNoise by a substantial margin** with a comparable computational load and fewer parameters, but also **surpasses other baseline models with significantly more parameters and MACs in terms of SISNR and PESQ**." |

**三处的用词是 `competitive`（有竞争力）与 `surpasses ... in terms of SISNR and PESQ`（在 SISNR 和 PESQ 两项上超过）——不是 `state-of-the-art`。**

> [!note] "competitive" 是自谦措辞，但实际结果确实是表内最佳——本页如实呈现这个反差
> 就 Table 2（VCTK-DEMAND）的数字看，**GTCRN 的 PESQ 2.87 与 SISNR 18.83 都是表内最高**（DeepFilterNet 16.63/2.81；S-DCCRN 2.84，无 SISNR；RNNoise 2.29，无 SISNR；PercepNet 2.73，无 SISNR）。**但在 STOI 上不是**：GTCRN **0.940**，与 S-DCCRN **0.940** 持平，**低于 DeepFilterNet 的 0.942**。
> 因此"surpasses ... in terms of SISNR and PESQ"这句是**精确的**（它只说这两项），而"competitive"是**低于实际表现**的自谦。
> **本页的处置**：如实记录"PESQ/SISNR 表内最高、STOI 并列/略低"，**但不替作者把主张升级为 SOTA**——因为 ① 对比集合只有 4 个模型，② S-DCCRN 的 MACs 为空无法比算力，③ RNNoise/PercepNet 的 SISNR/STOI 为空，④ **RNNoise 的数字取自其官方 repo 而非同口径复现**（见 §4.4）。

## 2. 之前的人怎么做不了？（limitation → gap）

### 2.1 backbone 的选择：DPCRN，以及为什么可以压

GTCRN 的 backbone 是 **DPCRN [3, 16]**（p.1 §1 逐字：`Using DPCRN [3, 16] as the backbone, various strategies are utilized to significantly shrink the model.`）。注意此处引了两个来源：

- **[3]** = X. Le, H. Chen, K. Chen, and J. Lu, "DPCRN: Dual-Path Convolution Recurrent Network for Single Channel Speech Enhancement," Interspeech 2021, pp. 2811–2815；
- **[16]** = X. Le, T. Lei, K. Chen, and J. Lu, "Inference skipping for more efficient real-time speech enhancement with parallel RNNs," IEEE/ACM TASLP, vol. 30, pp. 2411–2421, 2022。

即 **DPCRN 的原作者（Le 等，与本文作者 J. Lu 有共同作者）也是本文的"前身"**。本库已有 [[wiki_low_latency/entities/DPCRN]] 与 [[wiki_low_latency/sources/2022/Skip-DPCRN 2022]]（对应引文 [16]），构成一条完整的谱系。

### 2.2 gap 的具体形状：DPCRN 的三个可压缩点

论文没有用"gap 表格"的写法，但从 §1 的两句话可以反推它认为 DPCRN 哪里"肥"（p.1 §1 逐字）：

> "An **equivalent rectangular bandwidth (ERB) filter bank is used to reduce the redundancy of the input features**. **Grouped convolution [17] and grouped RNN [18] are employed to decrease the model complexity.** To boost the performance without incurring too much computational overhead, we further apply **subband feature extraction (SFE) modules** and **temporal recurrent attention (TRA) modules**."

三个动作对应三个可压缩点：

| # | 可压缩点 | 手段 | 引文来源 |
|---|---|---|---|
| 1 | **输入特征在频率轴上的冗余** | ERB filter bank（BM/BS） | 论文自己的工作（§2.1） |
| 2 | **卷积层与循环层的参数冗余** | grouped convolution（ShuffleNetV2 [17]）+ grouped RNN（GRNN [18]） | [17] Ma 等 ECCV 2018；[18] Gao 等 NAACL 2018 |
| 3 | **性能损失**（压完之后要补回来） | SFE + TRA（**论文自己的两个模块**） | §2.4、§2.5 |

**这个"1 + 2 压、3 补"的结构是本文的核心叙事**：压缩本身不新（ERB、grouped conv、grouped RNN 都是既有工作），**新颖点在于组合方式 + 两个补偿模块**。

> [!note] 这篇论文的"新颖性"需要准确地界定
> 逐项看：**ERB 压缩**不是新想法；**ShuffleNetV2 的 channel split/shuffle**不是新的；**GRNN 的分组循环**不是新的；**DPRNN 的双路径**不是新的；**时间维度注意力**在与它对照的 TA [24] 里已有；**CNN + GRU 的 squeeze-excitation 式能量池化**在视觉与语音里都有先例。
> **本文真正自己提出的只有两个模块：SFE（§2.4）与 TRA（§2.5）**，以及把它们与前述所有组件**组装进 DPCRN 并压到 23.7 K** 的工程。
> 这不是贬低——**"把已知部件组装到一个新量级"本身就是贡献**，而且 Table 1 显示 TRA 是有效的。但本库记录时必须把这个边界划清，**不得把 ERB/grouped conv/GT-Conv 读成本文的原创**。

### 2.3 与原始 DPCRN 的规模落差（本页的读法）

论文**没有给出 DPCRN 本身的参数量与 MACs**（Table 2 里没有 DPCRN 行）。因此本库**无法**从本篇数据算出"压了多少倍"。

> [!question] 论文通篇没有一个"DPCRN baseline"的算力量级
> 论文说 `various strategies are utilized to significantly shrink the model` 与 `Multiple strategies are applied to DPCRN to effectively reduce the model while maintaining speech enhancement performance`（§4 结论），**但从未给出 DPCRN 的参数量或 MACs**。
> 本库能拿到的间接参照只有 Table 2 的 **S-DCCRN (2.34 M)** —— 但 S-DCCRN 是 DCCRN 的扩展（引 [28]），**不是 DPCRN**，不能当 DPCRN 的算力代理。
> 因此"压了多大倍数"**在本篇内不可算**，本页记录为**未报告**，不代填。

## 3. 这个做法核心 trick 是什么？

### 3.1 整体架构（§2 开头 + Fig. 1）

论文的总述（p.2 §2 开头逐字）：

> "The GTCRN architecture consists of **band merging (BM) and band splitting (BS) modules, an optional SFE module, an encoder, a grouped dual-path RNN (G-DPRNN) module, and a decoder**, as shown in Fig. 1."

![[wiki_low_latency/assets/gtcrn_2024/gtcrn-page2.png]]

> 图注：原论文第 2 页页面渲染，用于核对 **Fig. 1（整体架构）+ Fig. 2（GT-Conv block）+ Fig. 3（SFE）+ Fig. 4（TRA）** 与 §2.1–§2.4 前半全文。**Fig. 1** 是一条 U 形结构：左侧 **Encoder**，右侧 **Decoder**，顶部标 `BM` 与 `BS`，中部标 `G-DPRNN`，`SFE` 标在 encoder/decoder 之间的旁路上。**注意**：抽取文本（`gtcrn.txt` 第 638–651 行）把 Fig. 1 的模块名平铺成两行（`BM / Conv / GT-Conv / Conv / GT-Conv / GT-Conv / G-DPRNN / BS / DeConv / DeConv / GT-Conv / GT-Conv / GT-Conv / Encoder / Decoder / SFE`），**无法从文本流判断 skip connection 的连线方式**；渲染图可看出 U 形对称结构与 BM/BS 的位置，但**连线细节在 150 dpi 下仍不足以逐条确认**。**Fig. 2** 是 GT-Conv block 的框图（含 `Channel Split` → 两路 → `Concat` → `Channel Shuffle`，以及 `P-Conv2D`、`DD-Conv2D`、`BN PReLU`、`SFE`、`TRA`）。**Fig. 3** 是 SFE 的 `Unfold` → `Reshape` 两步示意（标注三个张量尺寸，但因字体过小，**本页未能从渲染图读出其中的字母符号**）。**Fig. 4** 是 TRA 的 `Square → Avg Pool → GRU → FC → Sigmoid → ⊗` 流程与 `Aggregation` / `Generation` 两个阶段标注。图片为 PDF 页面复制，不是 AI 重画。

### 3.2 Encoder / Decoder（§2 开头）

论文对 encoder 的逐字描述（p.2 §2 开头）：

> "The encoder consists of **two convolution (Conv) and three grouped temporal convolution (GT-Conv) blocks** ... **Each Conv block is a sequence of a convolution layer, a batch normalization, and a PReLU activation**, which maps the input spectrum to a high-dimensional embedding and **down-samples the frequency-axis size**. **Skip connection is utilized to alleviate the information loss during the encoding phase.**"

> "The decoder is the **mirror version of the encoder**, where each Conv block is replaced by a **deconvolution (DeConv) block**, which has the same components as the Conv block with the exception of **substituting the convolution layer with a transposed convolution layer** to recover the original size. Moreover, the **last DeConv block uses tanh instead of PReLU activation to constrain output values between -1 and 1. These values are interpreted as the real and imaginary parts of the estimated complex ratio mask (CRM) [19]**."

**四个必须记住的结构事实**：

| # | 事实 | 为什么重要 |
|---|---|---|
| 1 | **Conv block = conv + BN + PReLU**；**DeConv block = 转置卷积 + BN + PReLU** | 归一化全用 **BN**（不是 LN）——按 [[wiki_low_latency/concepts/2509.21867-speed-optimized-streaming-design]] 的"可融合性"清单，BN 可融合进相邻层，这对端侧速度是有利的（FastEnhancer 的消融正是 BN vs LN） |
| 2 | **最后一个 DeConv 用 tanh，不用 PReLU** | 把输出**约束到 [-1, 1]**，使它能被解释为 CRM 的实部/虚部。**这是 CRM 的前提条件**，不是普通的激活函数选择 |
| 3 | **输出是 CRM（complex ratio mask），不是幅度掩蔽** | 本库 [[wiki_low_latency/concepts/低时延前端与延迟账本]] 要求区分 mask 类型；**GTCRN 同时输出实部与虚部**，iSTFT 阶段**不做相位替换**（虽然论文未明说重建流程——见 §4.7） |
| 4 | **skip connection** | 论文只说"用于缓解编码阶段的信息损失"，**未给出跳连的具体层对**（Fig. 1 的连线在 150 dpi 下不足以逐条确认） |

> [!question] STFT 的 window / hop 与 **STFT center** —— 本库一等审计项，论文只给了一半
> 论文给出（p.3 §3.2 逐字）：`STFT is computed using a square root Hanning window of a length of 32 ms, a hop length of 16 ms, and an FFT length of 512.`
>
> | 参数 | 值 | 换算 |
> |---|---|---|
> | 窗函数 | **square root Hanning（sqrt-Hanning）** | —— |
> | 窗长 | **32 ms** | @16 kHz = **512 samples**（**恰好等于 FFT 长度**） |
> | hop | **16 ms** | @16 kHz = **256 samples**（= 50 % overlap） |
> | FFT 长度 | **512** | 单边谱 $F = 512/2+1 = 257$ |
> | **STFT center / 帧锚定** | **未报告** | —— |
>
> **窗长 512 samples 与 FFT 长度 512 相等，意味着 no zero-padding**——这是本页的推读（论文未明说，但两个数字相同使这个读法最自然）。
> **关键缺口**：`center` 参数**完全未报告**。若 `center=True`，每帧分析窗相对帧锚点前后各取 $W/2$，**前端含 16 ms 未来样本**，整个系统的算法延迟直接多出 16 ms；若左对齐则不含。**论文对此完全沉默**——它连一个字都没提帧锚定。（本库基调见 [[wiki_low_latency/concepts/严格因果与算法延迟]]。）

### 3.3 Band Merging / Band Splitting（§2.1）

论文的动机（p.2 §2.1 逐字）：

> "We can **down-sample the spectral features by a BM operation**, and **restore the original resolution using a BS operation**. However, it is important to note that **harmonics are more likely to be present in low-frequency bands and rarely occur in high-frequency bands. Therefore, the merging of features is only performed in the high-frequency bands above 2 kHz according to the ERB scale.**"

实现细节（p.3 §3.2 逐字）：

> "For BM, we map the **192 high-frequency bands to 64 ERB bands**, while **keeping the 65 low-frequency bands unaltered**, leading to a **129-dimensional compressed feature map**."

| 项 | 值 | 说明 |
|---|---|---|
| 高频段合并阈值 | **2 kHz** | 论文只说"above 2 kHz"，**未说明 2 kHz 对应第几个 bin**（@16 kHz、FFT 512 时，2 kHz ≈ bin 64，与本页的 65 个低频带高度接近——**但这是本页的算术，论文未给出对应关系**） |
| 高频 band 数 | **192** → **64** ERB bands | 压缩比 3:1 |
| 低频 band 数 | **65**（不变） | —— |
| 压缩后维度 | **129** = 65 + 64 | —— |
| **未压缩时的维数** | **未报告** | 若取 $\text{FFT}/2+1=257$，则 65+192 = **257** ✓（**本页的算术核对，论文未给这个数**） |

> [!note] 129 这个数字与本页的算术完全自洽，但它依赖一个论文没写的假设
> 65（低频保留）+ 192（高频原带）= **257** = 512/2 + 1 —— 即**完整的单边谱**。
> 因此 BM 的输入是 257 维、输出是 129 维，**压缩率约 50 %**。
> **但论文从未写出 257 这个数**，也未说明 BM 的输入是否就是完整的单边谱（是否含直流与 Nyquist）。本页的核对**自洽但不是论文的明述**，故标注为推读。

> [!note] 这是本库 **ERB 路线**的源头之一，也是被借用得最广的一处
> - [[wiki_low_latency/sources/2026/RT-Tango 2026]] **明确借鉴**：其页面第 148 行记录「ERB 压缩明确借鉴 GTCRN [11]」，并把它用于**双耳分布式**场景；
> - [[wiki_low_latency/entities/FastEnhancer]] 则把子带路线（BSRNN / FSPEN / **GTCRN** / [[wiki_low_latency/entities/LiSenNet|LiSenNet]]）整体批评为「**increased architectural complexity and memory operations paradoxically led to higher RTFs**」（**LiSenNet 与 FSPEN 均已于 2026-09-27 补摄/建档，见 §6 末尾的库内缺口说明**）。
>
> 即：**同一个 ERB 压缩，被一篇当作可复用的降算力手段，被另一篇当作被批判的对象**。这是本库一对直接冲突，见 §6。

### 3.4 Grouped Dual-path RNN（§2.2）

论文的构造（p.2 §2.2 逐字）：

> "We combine **grouped RNN (GRNN) [18]** with **dual-path RNN (DPRNN) [7]** to construct G-DPRNN. **GRNN utilizes a group of smaller recurrent layers to approximate a large standard recurrent layer. Specifically, both the input features and hidden states are split into 2 disjoint groups, each of which is fed into a recurrent layer with 2 times fewer parameters than the original, before a representation rearrangement layer is applied to obtain the final output.**"

> "**DPRNN was originally proposed to model 1D long sequences, whereas it is also well-suited for time-frequency domain features, as presented in [3]. The intra-frame RNNs can model the spectral patterns in a single frame, while the inter-frame RNNs model the time dependence of a certain frequency bin. We use grouped bidirectional GRU for intra-frame modeling, and grouped unidirectional GRU for inter-frame modeling, so that the causality of the model can be guaranteed.**"

**三个必须拆开讲的点**：

| # | 点 | 论文原话 | 本库的读法 |
|---|---|---|---|
| 1 | **组数 = 2** | "split into **2 disjoint groups**" | 固定 2 组，**不是超参**。GRNN 的"2 倍少参数"是相对**同等隐层维度**的标准 RNN 而言 |
| 2 | **intra-frame 用双向、inter-frame 用单向** | "grouped **bidirectional** GRU for intra-frame ... grouped **unidirectional** GRU for inter-frame" | **因果性靠 inter-frame 单向保证**（论文明确这么说） |
| 3 | **双向在哪个轴上** | intra-frame = "model the spectral patterns **in a single frame**" | **intra-frame 的双向是沿频率轴、在单帧内部**，**不跨越时间** |

> [!important] 本库的关键区分：「频率轴双向」不等于「时间轴非因果」
> 论文的原文是 `causality of the model can be guaranteed`，**但没有解释为什么 intra-frame 的双向不破坏因果**。本页认为**这个论证成立，但需要读者自己补上**：
> - **intra-frame RNN 处理的是一帧内的频谱模式**（沿频率轴），其"双向"是**在同一个时间帧 $t$ 内部、沿频率方向**的双向；
> - **inter-frame RNN 处理的是"某个频点在时间上的依赖"**（沿时间轴），它**是单向的** —— 这才是决定因果性的那一条；
> - 因此 **intra-frame 的双向不引入任何未来时间帧的依赖**。
>
> **但本库必须把这个区分写清楚，不能简单地写"用了双向 GRU ⇒ 非因果"**——这是本库易犯的误判。同时也要注意：**这只是一个论证，不是证据**——论文没有给逐层张量依赖图。
>
> **反过来说**：如果 intra-frame 的双向在实现上跨越了帧边界（例如把整段 T-F 图按频率轴做双向），那么它就**不**限于单帧；而论文**没有交代 inter-frame 与 intra-frame 的切分边界**（即 DPRNN 的 chunk 长度 / segment 长度）。这一点见 §4.7 的 `[!question]`。

> [!question] G-DPRNN 的三个结构性参数全部未报告
> | 参数 | 状态 |
> |---|---|
> | GRU 隐层维度（每组多少单元） | **未报告** |
> | DPRNN 的 chunk / segment 长度（决定 intra/inter 的切分边界与缓存长度） | **未报告** |
> | 层数（intra / inter 各几层） | **未报告** |
>
> 论文只给了"组数 = 2"与"intra 双向 / inter 单向"。**因此本库无法估算 G-DPRNN 的算力占比、状态大小或跨帧缓存长度**——而这些恰恰是低时延审计的核心字段。
> 值得注意：[[wiki/sources/2026/muNet 2026]] 的页面（第 125 行）记录 μNet 论文的脚注称「**GTCRN 有效复杂度更高（需缓冲最多 16 帧中间特征，无法与 RNNoise/μNet 的逐帧处理直接比）**」——**这个"16 帧缓冲"的说法不见于 GTCRN 原文**，是 μNet 论文的转述。本页记录为**外部转述，本页未从 GTCRN 原文核实**。

### 3.5 Grouped Temporal Convolution（§2.3，Fig. 2）

论文的构造（p.2 §2.3 逐字）：

> "**Leveraging the ShuffleNetV2 [17] unit as a basis**, the GT-Conv block **introduces a temporal dilation into the depth-wise convolution**, improving its capacity for **long-range temporal dependency modeling**. ... **The input features are split in half along the channel axis into two branches. While one branch remains unaltered, the other undergoes an efficient pattern-capturing and processing procedure, which is accomplished by a sequence of convolutional layers made up of two 2D pointwise convolution (P-Conv2D) layers and a 2D dilated depthwise convolution (DD-Conv2D) layer. The outputs from both branches are ultimately concatenated to restore the original size. A channel shuffle operation is performed to facilitate information exchange between the two branches. To further enhance the model performance, the optional SFE module and TRA module can be applied in the second branch.**"

~~~text
GT-Conv block（Fig. 2，本页按论文文字转写）

                输入 X（C 通道）
                     │
                     ├──────────► Channel Split（沿 channel 轴切两半）
                     │
        ┌────────────┴────────────┐
        │                         │
   identity branch          pattern-capturing branch
   （保持不变）                     │
        │                    ┌────┴────┐
        │                    │ P-Conv2D│      ← 2D pointwise conv
        │                    └────┬────┘
        │                    ┌────┴─────────┐
        │                    │ DD-Conv2D    │  ← 2D **dilated depthwise** conv
        │                    │ k=(3,3)      │     时间膨胀率 = 1 / 2 / 5
        │                    └────┬─────────┘
        │                    ┌────┴────┐
        │                    │ P-Conv2D│
        │                    └────┬────┘
        │                    [可选 SFE]  ← 论文原文：加在"the second branch"
        │                    [可选 TRA]
        │                         │
        └────────────┬────────────┘
                     ▼
                  Concat（恢复原尺寸）
                     │
              Channel Shuffle（促进两路信息交换）
                     │
                   输出
~~~

**实现细节**（p.3 §3.2 逐字）：

> "The DD-Conv2D layers in three GT-Conv blocks **share a common channel number of 16, a common kernel size of (3, 3), and have time dilations of 1, 2 and 5, respectively**."

| 项 | 值 |
|---|---|
| DD-Conv2D 通道数 | **16**（三个 GT-Conv 共用） |
| DD-Conv2D kernel size | **(3, 3)** |
| 三个 GT-Conv 的时间 dilation | **1, 2, 5** |

> [!note] 「时间 dilation 1/2/5 + kernel (3,3)」⇒ 本页推得时间轴感受野 3 / 5 / 11 帧，**论文未给**
> 对**因果（左对齐）**的一维膨胀卷积，在 kernel $k$ 与 dilation $d$ 下的**历史帧需求**为 $(k-1)\cdot d$：
>
> | GT-Conv | 时间 dilation $d$ | kernel 时间维 $k=3$ | 单块历史帧需求 $(k-1)d$ | 单块感受野（含当前帧）$=1+(k-1)d$ |
> |---|---:|---:|---:|---:|
> | 第 1 个 | **1** | 3 | $2\times 1 = 2$ | **3** |
> | 第 2 个 | **2** | 3 | $2\times 2 = 4$ | **5** |
> | 第 3 个 | **5** | 3 | $2\times 5 = 10$ | **11** |
>
> 三个 GT-Conv **若串联**，累计感受野为 $1 + 2 + 4 + 10 = 17$ 帧（即 **17 帧共 272 ms @16 ms hop** 的历史跨度）。
> **但这整段推算是本页的读法，论文未给出任何感受野数字**，也未说明 DD-Conv2D 的 padding 方式（若为 `same` padding 的对称填充，则**含未来帧**，结论会改变）。本库在此**只记录推算，不作因果判定依据**（见 §5）。

> [!note] GT-Conv 是"分组"思路在本篇里的第二次出现，且与 ShuffleNetV2 的原始动机一致
> Channel split → 一半恒等 → 另一半做变换 → concat → shuffle，这套流程与 **ShuffleNetV2 [17]** 的 unit 同构。ShuffleNetV2 的原始论文正是本库 [[wiki_low_latency/concepts/2509.21867-speed-optimized-streaming-design]] 与 [[wiki_low_latency/concepts/2609.29867-compute-matched-dynamic-depth]] 反复引用的"**MACs 不是速度**"的出处（那里的引文 [19]，此处是 [17]——**同一个 ShuffleNetV2**）。
> 因此本库有一个有趣的事实：**GTCRN 用 ShuffleNetV2 的 unit 来降算力，而 ShuffleNetV2 自己就是"算力不等于速度"的提出者**。GTCRN **没有报告任何速度**（无 RTF、无延迟），所以本文无法回应其自身所引方法论的这一警告。这一点是本页认为最值得记录的**结构性讽刺**，见 §5。

### 3.6 Subband Feature Extraction（§2.4，Fig. 3）

论文的机制描述（p.2 末 – p.3 §2.4 逐字）：

> "The SFE module, as illustrated in Fig. 3, is designed to **enhance the capability of a convolution layer in capturing and utilizing frequency information**. It achieves this by first performing an **unfold operation on the input features with a kernel size of $k$ in the frequency dimension**, which **combines each frequency band with its adjacent $k-1$ bands to form subband units**. Subsequently, **a reshape operation is applied to stack each subband unit along the channel dimension, leading to subband interweaved features**. Throughout this process, the SFE module **integrates the subband relationship, originally existing solely in the frequency dimension, into the channel dimension, empowering the following convolution layer to leverage frequency information more efficiently**."

~~~text
SFE（Fig. 3，本页按论文文字转写）

  输入特征  [C, T, F]
      │
      ▼ Unfold（**在频率维**，kernel size = k）
      │   每个频带 f 与其相邻 k-1 个频带组合成一个 subband unit
      ▼
  subband units（频率维被展开成 k 份）
      │
      ▼ Reshape（把每个 subband unit **沿 channel 维**堆叠）
      ▼
  subband interweaved features

  效果：子带关系从【频率维】被搬进【channel 维】
        → 后续卷积层（在 channel 维做混合）能更高效地利用频率信息
~~~

实现细节（p.3 §3.2 逐字）：

> "For all the optional SFE modules, we **uniformly use a kernel size of 3**."

| 项 | 值 |
|---|---|
| kernel size $k$ | **3**（所有可选 SFE 统一） |
| unfold 轴 | **频率维** |
| reshape 后堆叠轴 | **channel 维** |
| 输出通道数变化 | **未报告**（论文只说"stack along the channel dimension"，未给变换后的通道数） |

> [!note] SFE 的本质是"用 reshape 换取信道维度上的频域混合能力"——但它有一个未报告的代价
> 把一个 $C$ 通道、$F$ 频带的特征做 $k=3$ 的频率轴 unfold 后沿 channel 堆叠，**通道数会变成原来的 $k$ 倍**（若每个频点都展开）或**频率维缩小**（若用 stride）。论文**没有报告 SFE 后的通道数或特征图尺寸**。
> 但从参数代价可以反推它的规模很小：Table 1 显示 SFE 只增加约 **2.02 K** 参数（13.35 → 15.37）与 **5.16 M/s** MACs（33.91 → 39.07）。
> **5.16 M/s 是 TRA 的 0.47 M/s 的约 11 倍** —— 即 SFE 是本篇里**真正花钱的那个模块**，而它的收益（SISNR +0.23）**小于** TRA 的收益（+0.38）。这是 Table 1 最重要的读法，见 §4.3。

### 3.7 Temporal Recurrent Attention（§2.5，Fig. 4）

论文的机制描述（p.3 §2.5 逐字）：

> "The TRA module aims to perform **temporal feature recalibration utilizing a multiplicative attention mask** by effectively **modeling the energy distribution along the time axis**. The attention mask is generated in two steps: **global information aggregation and attention generation** ... Given $V \in \mathbb{R}^{C \times T \times F}$ as the input features, the **temporal energy representation $Z \in \mathbb{R}^{C \times T}$ is first computed via global average pooling**, formulated as $Z(c,t)=\frac{1}{F}\sum_{f=1}^{F}V^2(c,t,f)$, where $C, T, F$ denote channel, time and frequency axis lengths respectively. Then the temporal energy representation is processed by **a GRU followed by a fully connected (FC) layer, where the GRU doubles the input channels and the FC layer restores the original channel number**. Subsequently, **a sigmoid activation function is applied to generate a 1D attention mask, which is then replicated along the frequency axis to produce a 2D T-F mask $A \in \mathbb{R}^{C \times T \times F}$**. The final output is given as $\tilde V = V \otimes A$, where $\otimes$ denotes the element-wise multiplication operation."

~~~text
TRA（Fig. 4，本页按论文文字转写）

  输入 V ∈ R^{C×T×F}
      │
      ▼ ① Global Information Aggregation
      │   Square（**注意：是平方，不是取绝对值**）
      │   Avg Pool（**沿频率轴 F 求平均**）
      ▼
  Z(c,t) = (1/F) Σ_f V²(c,t,f)   ∈ R^{C×T}    ← 时间能量表示
      │
      ▼ ② Attention Generation
      │   GRU（**把输入通道数翻倍**：C → 2C）
      │   FC （**恢复到原通道数**：2C → C）
      │   Sigmoid
      ▼
  1D 注意力掩蔽 ∈ R^{C×T}
      │
      ▼ 沿**频率轴**复制（replicate）
  2D T-F mask  A ∈ R^{C×T×F}
      │
      ▼ ⊗ 逐元素乘
  Ṽ = V ⊗ A
~~~

**四个必须准确的细节**：

| # | 细节 | 论文原话 | 常见误读 |
|---|---|---|---|
| 1 | **平方是"能量"的关键** | $Z(c,t)=\frac{1}{F}\sum_{f=1}^{F}V^2(c,t,f)$ | 不是一阶均值 $\frac1F\sum V$，也**不是平方后再开方**（不是 RMS）。论文用**能量**而非幅度 |
| 2 | **池化沿频率轴** | "global average pooling"，$T$ 被保留 | 池化掉的是 $F$，**保留时间轴 $T$** ——因为目的是建模时间的能量分布 |
| 3 | **GRU 通道翻倍、FC 恢复** | "the **GRU doubles the input channels** and the **FC layer restores the original channel number**" | 这是一个 **bottleneck 的反向结构**（先升维再降维），与 SE-Block 的"先降维再升维"**相反** |
| 4 | **掩蔽沿频率轴复制** | "**replicated along the frequency axis**" | 广播的是 $T$ 方向上的 1D 掩蔽，**频率维度上每个 channel 的所有频点共用同一个权重** |

> [!note] TRA 是本库最值得拿来做"类比迁移"的一个模块
> 它的结构 —— **"能量统计 → 池化 → GRU → FC → sigmoid → 乘性掩蔽"** —— 与视觉里的 **SE-Block（Squeeze-and-Excitation）**、语音里的**注意力池化**同构：
>
> | 模块 | 池化轴 | 是否有时序模型 | 掩蔽维度 |
> |---|---|---|---|
> | **Squeeze-and-Excitation** | 空间（H×W） | 无 | channel |
> | **TRA（本篇）** | 频率 F | **有（GRU）** | channel × **time** |
> | **TA [24]（对照）** | 时间 T（本页推读） | —— | 见 §4.2 |
>
> **TRA 相比 SE-Block 的关键差别是那个 GRU**：它让注意力权重**跨时间有记忆**，因此掩蔽不是逐帧独立统计出来的，而是随时间平滑的。这解释了为什么在 Table 1 里 TRA 相对 TA 的质量增益（SISNR +0.38）恰好落在"时间连续性"这个维度上。
> **但论文没有讨论这一点**，也没有给出注意力 mask 的可视化或跨帧平滑性的任何证据。

### 3.8 损失函数（§2.6，Eq. 1–5）

> [!contradiction] **Eq. (1) 的系数位置与本任务 brief 给出的骨架不同——渲染图以论文为准**
> 本任务 brief 给出的公式是：
> $$\mathcal L = \alpha \mathcal{L}_{\text{SISNR}} + (1-\alpha)\left[\beta \mathcal{L}_{\text{mag}} + (1-\beta)\left(\mathcal{L}_{\text{real}} + \mathcal{L}_{\text{imag}}\right)\right]$$
> **`gtcrn-page3.png` 渲染图（600 dpi 放大核对）显示论文原式为：**
> $$\mathcal L = \alpha\mathcal L_{\text{SISNR}}(\tilde s, s) + (1-\beta)\mathcal L_{\text{mag}}(\tilde S, S) + \beta\left(\mathcal L_{\text{real}}(\tilde S, S) + \mathcal L_{\text{imag}}(\tilde S, S)\right)$$
> **差异**：⑧ brief 版把 $\beta$ 放在**内层**（$\mathcal L_{\text{mag}}$ 与 $(\mathcal L_{\text{real}}+\mathcal L_{\text{imag}})$ 之间做凸组合），**论文原版把 $\beta$ 放在外层**（$(1-\beta)$ 乘 $\mathcal L_{\text{mag}}$，$\beta$ 乘 $(\mathcal L_{\text{real}}+\mathcal L_{\text{imag}})$，并直接挂在 $\alpha\mathcal L_{\text{SISNR}}$ 之后，**没有一个 $(1-\alpha)$ 的总系数**）。
> **本页以渲染图为准**，按论文原式记录。**注意两式在 $\alpha \to 0$ 时行为不同**：brief 版在 $\alpha=0$ 时系数和为 $(1-0)=1$；论文原式在 $\alpha=0$ 时系数和为 $(1-\beta)+\beta=1$ ✓，**但 $\alpha\mathcal L_{\text{SISNR}}$ 项完全独立，不参与归一化** —— 即谱损失的总权重恒为 1，**与 $\alpha$ 无关**。
> 这个差异会改变"$\alpha$ 增大时谱损失权重如何变化"的答案（brief 版：谱损失权重从 1 降到 0；论文版：谱损失权重**恒为 1**，$\alpha$ 只决定波形项占多大比重），**因此不是排版差异而是实质差异**。

**论文原式（Eq. 1，p.3 渲染图逐字）**：

$$\mathcal L = \alpha\mathcal L_{\text{SISNR}}(\tilde s, s) + (1-\beta)\mathcal L_{\text{mag}}(\tilde S, S) + \beta\left(\mathcal L_{\text{real}}(\tilde S, S) + \mathcal L_{\text{imag}}(\tilde S, S)\right) \tag{1}$$

论文对符号的说明（p.3 §2.6 逐字）：

> "Our loss function is applied on **both the waveform domain and spectrogram domain** ... where $\tilde s$ and $s$ are **enhanced and clean waveform**. $\tilde S$ and $S$ are **enhanced and clean spectrogram**, respectively. **$\alpha$ and $\beta$ are set to 0.01 and 0.3 respectively.**"

**四个子项**（Eq. 2–5，p.3 渲染图逐字，**已用 600 dpi 放大逐条核对**）：

$$\mathcal L_{\text{SISNR}} = -10\log_{10}\left(\frac{\|s_t\|^2}{\|\tilde s - s_t\|^2}\right); \quad s_t = \frac{\langle \tilde s, s\rangle s}{\|s\|^2} \tag{2}$$

$$\mathcal L_{\text{mag}}(\tilde S, S) = \text{MSE}\!\left(|\tilde S|^{0.3},\ |S|^{0.3}\right) \tag{3}$$

$$\mathcal L_{\text{real}}(\tilde S, S) = \text{MSE}\!\left(\tilde S_r/|\tilde S|^{0.7},\ S_r/|S|^{0.7}\right) \tag{4}$$

$$\mathcal L_{\text{imag}}(\tilde S, S) = \text{MSE}\!\left(\tilde S_i/|\tilde S|^{0.7},\ S_i/|S|^{0.7}\right) \tag{5}$$

> [!important] **功率压缩指数 c = 0.3 / 0.7 —— 这是本库 FastEnhancer 页面所引 `c=0.3` 的出处之一**
> | 项 | 压缩指数 | 作用对象 |
> |---|---|---|
> | $\mathcal L_{\text{mag}}$ | **0.3** | 幅度谱 $|\tilde S|$、$|S|$ |
> | $\mathcal L_{\text{real}}$ | **0.7** | **归一化后的**实部 $\tilde S_r/|\tilde S|^{0.7}$、$S_r/|S|^{0.7}$ |
> | $\mathcal L_{\text{imag}}$ | **0.7** | **归一化后的**虚部 $\tilde S_i/|\tilde S|^{0.7}$、$S_i/|S|^{0.7}$ |
>
> **两件事必须分清**：
> 1. **0.3 是幅度项的压缩指数**（$|\cdot|^{0.3}$，功率律压缩，把动态范围压扁）；
> 2. **0.7 不是"另一个压缩指数"，而是"单位化（unit-normalization）的指数"**：$\tilde S_r/|\tilde S|^{0.7}$ 把实部**除以幅度的 0.7 次幂**，得到一个**落在单位圆附近的方向量（实部）**。注意 $0.3 + 0.7 = 1$，这两个指数**是配对的**：$\mathcal L_{\text{mag}}$ 在压缩后的幅度上做回归，$\mathcal L_{\text{real/imag}}$ 在**同一压缩尺度下的相位方向**上做回归。
> 3. 因此本篇的谱损失 = **"压缩幅度 MSE" + "压缩后相位（实/虚部）MSE"**，两项的压缩尺度**一致**（都由 0.3 决定）。
>
> **本库关联**：[[wiki_low_latency/entities/FastEnhancer]]（其页面 §2509.21867 记录 FastEnhancer 的损失亦用 $c=0.3$ 的功率律压缩）与 [[wiki_low_latency/concepts/2609.29867-compute-matched-dynamic-depth]] 记录的 Conv-FSENet 损失（$|X|^{0.3}$ 压缩、$c=0.3$）**都属同一谱系**。**GTCRN 是这条谱系在库内的早期锚点之一**。

> [!question] 论文**没有说明** $\mathcal L_{\text{real}}$ / $\mathcal L_{\text{imag}}$ 为什么用 0.7 而不是 0.3，也没有说明单位化的动机
> 论文对 Eq. (3)–(5) 只有一句话："Each term in the aforementioned formula is calculated as follows"——**没有对任何一项给出解释**。
> 特别是 $|S|^{0.7}$ 这个分母：**它使得损失对全局电平不变**（$\tilde S_r/|\tilde S|^{0.7}$ 在 $\tilde S$ 缩放为 $a\tilde S$ 时变为 $a\tilde S_r/(a^{0.7}|\tilde S|^{0.7}) = a^{0.3}\cdot\tilde S_r/|\tilde S|^{0.7}$，**只残留 $a^{0.3}$ 的依赖**）。
> 这个"部分电平不变性"是否是刻意设计、0.7 是否由 0.3 推导而来，**论文未说明**。本页记录为**未解释的设计选择**。

## 4. 实验里哪个消融最关键？

### 4.1 数据集与训练设置（§3.1、§3.2）

| 项目 | VCTK-DEMAND [20] | DNS3 [21] |
|---|---|---|
| 类型 | paired clean / **pre-mixed** noisy speech | 大规模；含 clean sets / noise sets / **RIRs**；另加 **DiDiSpeech [22]** 中文语料 |
| 训练 | **11,572** utterances / **28** speakers | **720,000** pairs of **10-second** noisy-clean |
| 验证 | 训练集中选 **1,572** utterances | **840** pairs |
| 测试 | **824** utterances / **2** speakers | **800** pairs；另有 **DNS challenge 3 blind test set** |
| 采样率 | **重采样到 16 kHz** | **16 kHz**（All the utterances are sampled at 16 kHz） |
| 混音方式 | 论文未述（pre-mixed） | clean speech **先与随机选的 RIR 卷积**，再与随机噪声按 **SNR −5 到 15 dB** 混合 |
| 训练目标 | 论文未述 | **保留前 100 ms 反射**（preserving the first 100 ms reflections） |

> [!note] DNS3 的"保留前 100 ms 反射"是**去混响强度的直接定义**，也是本篇唯一与"混响"相关的设置
> 即训练目标是**部分去混响（partial dereverberation）**：早反射（< 100 ms）保留，晚反射当作噪声抑制掉。
> **但论文没有报告任何去混响指标**（无 C50、无 DRR、无 SRMR），也没有说明测试用的 DNS3 test set 的反射保留方式是否与训练一致。因此**本库无法判断它的"性能"里有多少来自去混响**。

**噪声类型**（DNS3）：论文只写 `a wide range of clean sets, noise sets, and RIRs`，**没有列出噪声类别**（无 babble / 竞争说话人 / 瞬态噪声分类）。**本库关注的"低 SNR 人声保留"所需的分类报告全部缺失**。

**训练超参**（p.3 §3.2 逐字）：

| 项目 | 值 |
|---|---|
| 优化器 | **Adam [23]** |
| 初始学习率 | **0.001** |
| 学习率调度 | 验证损失**连续 5 个 epoch** 不下降 ⇒ 学习率**减半** |
| batch size | VCTK-DEMAND **4**；DNS3 **16** |
| DNS3 训练 | utterances **chunked to 8 seconds**；每 epoch 随机选 **40,000** noisy-clean pairs |
| 训练总 epoch | **未报告** |
| 随机种子 | **未报告** |
| 权重初始化 | **未报告** |

> [!question] 「每 epoch 随机选 40,000 对」× 未知 epoch 数 = 无法估算总更新步数
> 论文给出 DNS3 每个 epoch 的采样量（40,000 对）与 batch size（16），因此**每 epoch = 2,500 次参数更新**。但**总 epoch 数未报告**，所以总步数不可知。
> 这直接影响可复现性与"训练是否充分"的判断。本页记录为**未报告**。

**消融用的数据**（p.3 §3.3.1 逐字）：

> "We validate the efficacy of SFE and compare our TRA against **time-dimension attention (TA) proposed in [24]** on a **relatively small training set (around 100 hours) sampled from the DNS3 dataset**."

**关键**：**Table 1 的消融不是在全量 DNS3（720,000 对）上做的，而是在约 100 小时的 DNS3 子集上**。而 Table 2/3 的主结果用的数据量论文未在同一处说明。这是一个**口径提醒**：Table 1 的绝对数值不可与 Table 2/3 直接横比。

### 4.2 Table 1 的正确读法：TRA 的"性价比"高在哪里（**本节是全篇最重要的消融读法**）

![[wiki_low_latency/assets/gtcrn_2024/gtcrn-page4.png]]

> 图注：原论文第 4 页页面渲染，用于核对 **Fig. 5 + Table 1 + Table 2 + Table 3 + §3.3.1 + §3.3.2 + §4 + §5**。**Fig. 5** 是 2 行 × 4 列的 DNS3 频谱图（每幅纵轴 `0/1/2/5 kHz`、横轴 `0/1/2/3 s`），上标 `(a) Noisy / (b) Enhanced by RNNoise / (c) Enhanced by GTCRN / (d) Clean`，下标 `(e)(f)(g)(h)` 同序。**Table 1** 标题为 "Ablation study results on DNS3 test set."，8 列 `SFE / TA / TRA / Para. (K) / MACs (M/s) / SISNR / PESQ / STOI`，共 **7 行**（第 1 行为全 `-`），且**渲染图上可见 7 行被 2 条横向分隔线分成 3 段**（第 1 行独立、第 2–4 行一段、第 5–7 行一段），**这与 SFE 列的 `✗/✗/✗/✓/✓/✓` 分组完全吻合**。**Table 2** 标题为 "Performance on VCTK-DEMAND test set."，6 行。**Table 3** 标题为 "Performance on DNS3 blind test set."，4 行，表头为双层（`DNSMOS-P.808` 单列 + `DNSMOS-P.835` 下挂 `BAK / SIG / OVRL`）。**RNNoise 行带脚注上标 `1`**，脚注内容在**本页页脚**：`Metrics are measured with source code provided at https://github.com/xiph/rnnoise/`。图片为 PDF 页面复制，不是 AI 重画。

**Table 1 全文照抄（逐格核对 page4 渲染图）**：

| SFE | TA | TRA | Para. (K) | MACs (M/s) | SISNR | PESQ | STOI |
|---|---|---|---|---|---|---|---|
| - | - | - | - | - | 3.92 | 1.30 | 0.789 |
| ✗ | ✗ | ✗ | 13.35 | 33.91 | 9.87 | 1.87 | 0.834 |
| ✗ | ✓ | ✗ | 14.84 | 34.00 | 10.00 | 1.89 | 0.838 |
| ✗ | ✗ | ✓ | 21.65 | 34.47 | 10.25 | 1.91 | 0.840 |
| ✓ | ✗ | ✗ | 15.37 | 39.07 | 10.10 | 1.90 | 0.838 |
| ✓ | ✓ | ✗ | 16.86 | 39.16 | 10.29 | 1.92 | 0.841 |
| ✓ | ✗ | ✓ | **23.67** | **39.63** | **10.39** | **1.94** | **0.844** |

> [!question] 第 1 行（全 `-`）是什么？——渲染图**不能**确定
> 该行 `SFE / TA / TRA / Para.(K) / MACs(M/s)` 五列全为 `-`，只有三项指标：**SISNR 3.92 / PESQ 1.30 / STOI 0.789**。
> 从数值特征看，这**几乎肯定是未处理的 noisiy 混合**（DNS3 test set 的 noisy baseline）——因为 ① 参数量与算力列用 `-` 表示"不是模型"，② PESQ 1.30 与 STOI 0.789 是典型的噪声污染水平，③ DNS3 是**混响+噪声**数据，noisy 的 SI-SNR 只有 3.92 dB 属合理范围（而 VCTK-DEMAND 的 noisy 是 8.45 dB，Table 2）。
> **但 page4 渲染图上这一行没有行标签**（论文只给了 5 个 `-`，没有写 "Noisy"）。**本页因此记录为"极可能是 noisy baseline，但论文未标注"**，**不代填**。同类问题在 Table 2 里不存在（那里明确写了 `Noisy`）。

**本页对 Table 1 的三组关键对照（全部写成数值对，差值留给读者）**：

**对照 A —— TRA vs TA（同为 SFE ✗ 的第三行 vs 第二行）**

| 指标 | TA ✓ / TRA ✗ | TA ✗ / TRA ✓ | 差 |
|---|---:|---:|---:|
| Para. (K) | 14.84 | 21.65 | **+6.81 K** |
| MACs (M/s) | 34.00 | 34.47 | **+0.47 M/s** |
| SISNR | 10.00 | 10.25 | **+0.25** |
| PESQ | 1.89 | 1.91 | **+0.02** |
| STOI | 0.838 | 0.840 | **+0.002** |

**对照 B —— TRA vs 无任何 attention（同为 SFE ✗ 的第三行 vs 第一行）**

| 指标 | ✗/✗/✗ | ✗/✗/✓ | 差 |
|---|---:|---:|---:|
| Para. (K) | 13.35 | 21.65 | **+8.30 K** |
| MACs (M/s) | 33.91 | 34.47 | **+0.56 M/s** |
| SISNR | 9.87 | 10.25 | **+0.38** |
| PESQ | 1.87 | 1.91 | **+0.04** |
| STOI | 0.834 | 0.840 | **+0.006** |

**对照 C —— SFE vs 无 SFE（同为 TA ✗ / TRA ✗ 的第四行 vs 第一行）**

| 指标 | SFE ✗ | SFE ✓ | 差 |
|---|---:|---:|---:|
| Para. (K) | 13.35 | 15.37 | **+2.02 K** |
| MACs (M/s) | 33.91 | 39.07 | **+5.16 M/s** |
| SISNR | 9.87 | 10.10 | **+0.23** |
| PESQ | 1.87 | 1.90 | **+0.03** |
| STOI | 0.834 | 0.838 | **+0.004** |

> [!important] Table 1 最重要的读法：**TRA 与 SFE 在 MACs 代价上相差约一个数量级，而质量增益的量级相当**
> 把上面 A/C 两组对照并列（**全部写数值对，不下判断词**）：
>
> | 模块 | MACs 增量 | 参数增量 | SISNR 增量 | PESQ 增量 |
> |---|---:|---:|---:|---:|
> | **TRA**（✗/✗/✗ → ✗/✗/✓） | 33.91 → 34.47 = **+0.56 M/s** | 13.35 → 21.65 = **+8.30 K** | 9.87 → 10.25 = **+0.38** | 1.87 → 1.91 = **+0.04** |
> | **SFE**（✗/✗/✗ → ✓/✗/✗） | 33.91 → 39.07 = **+5.16 M/s** | 13.35 → 15.37 = **+2.02 K** | 9.87 → 10.10 = **+0.23** | 1.87 → 1.90 = **+0.03** |
>
> **两行对比可得三个事实**（请读者自行比较）：
> - **MACs 代价**：TRA `+0.56 M/s` vs SFE `+5.16 M/s`（比值 $5.16/0.56 = 9.2$）；
> - **参数代价**：TRA `+8.30 K` vs SFE `+2.02 K`（TRA 的参数代价更大，比值 $8.30/2.02 = 4.1$）；
> - **质量增益**：TRA 在 SISNR 上 `+0.38` vs SFE `+0.23`；PESQ 上 `+0.04` vs `+0.03`。
>
> **即：TRA 用约 1/9 的 MACs 换到了更大的 SISNR 增益，但付出了约 4 倍的参数。** 这是一个**双维度上的 trade-off**，而不是单向优劣。论文的措辞是 `our proposed TRA outperforms TA with a very limited increment in computational resources`（**只与 TA 比，未与 SFE 比**）与 `The advantages of SFE are also evident in Table 1`（**未给量化**）。
> **本页认为论文回避了一组最值得写的对照：TRA vs SFE 的 MACs/参数 双坐标比较。** 这是本页从渲染图重算后补上的（**论文自身未提供**）。

**对照 D —— 两开关同时打开是否可加？（本页的推算）**

| 组合 | SFE | TRA | SISNR | 相对 baseline（9.87）的增量 |
|---|---|---|---|---|
| baseline | ✗ | ✗ | 9.87 | — |
| 只 SFE | ✓ | ✗ | 10.10 | **+0.23** |
| 只 TRA | ✗ | ✓ | 10.25 | **+0.38** |
| **同时** | ✓ | ✓ | **10.39** | **+0.52** |
| **单独之和** | — | — | — | **+0.61** |

**同时打开的增量 `+0.52` 小于单独打开之和 `+0.61`**（差 `0.09`），即两者**存在次可加性（sub-additive）**——**它们的收益有部分重叠**。同理 PESQ：单独 `+0.03` 与 `+0.04`（和 `+0.07`）vs 同时 `+0.07`（**3.87 → 1.90 与 1.91 → 1.94，即 +0.03 + 0.04 = +0.07 vs +0.07，PESQ 上则不呈现次可加**）。

> [!question] 次可加性的来源论文未讨论——但从模块机制上可以提出一个假设
> SFE 把**频率维**的子带关系搬进 channel 维，TRA 沿**时间轴**做能量加权重标定。**两者作用的轴不同**（一个频率、一个时间），因此**按理应当近似可加**。但 SISNR 上出现了 `-0.09` 的次可加。
> 一个可能的原因是：**在 SFE ✓ 时特征已经被重塑，TRA 的时序池化所统计的"能量"分布已经改变**（SFE 改变了 channel 的语义）。**但这只是一个假设，论文没有讨论，也没有做交叉验证实验**。本页记录为**未解释**，并标注：**`-0.09` 的 SISNR 差值在无种子数/无方差的情况下，无法判断其是否显著**。

### 4.3 TA 是什么，以及为什么它是本篇唯一的"内部对照"（§3.3.1）

TRA 的对照是 **TA（time-dimension attention），引自 [24]**：

> [24] Q. Zhang, Q. Song, et al., "Time-Frequency Attention for Monaural Speech Enhancement," in **ICASSP 2022**, pp. 7852–7856.

**论文只说了 `compare our TRA against time-dimension attention (TA) proposed in [24]`，没有描述 TA 的具体结构**。

> [!question] TA 这个对照臂在本篇里几乎是黑箱
> 论文**没有给出**：TA 的结构、它与 TRA 的结构差异（是池化轴不同？是没有 GRU？是掩蔽维度不同？）、TA 的复现方式（是否用了 [24] 的官方实现）。
> **Table 1 显示 TA 是"性价比最低"的模块**（MACs `+0.09 M/s`、参数 `+1.49 K`、SISNR `+0.13`、PESQ `+0.02`），但**在不知道 TA 结构的情况下，本库无法判断这个结论是对"时间维注意力"这一类的评价，还是仅对 [24] 这一个具体实现的评价**。
> 本页记录为**对照臂描述不足**。这是本篇消融设计上的一个真实弱点。

### 4.4 Table 2：VCTK-DEMAND 对比（全文照抄 + 逐条口径标注）

| 模型 | Para. (M) | MACs (G/s) | SISNR | PESQ | STOI |
|---|---|---|---|---|---|
| Noisy | - | - | 8.45 | 1.97 | 0.921 |
| RNNoise (2018) | 0.06 | 0.04 | - | 2.29 | - |
| PercepNet (2020) | 8.00 | 0.80 | - | 2.73 | - |
| DeepFilterNet (2022) | 1.80 | 0.35 | 16.63 | 2.81 | **0.942** |
| S-DCCRN (2022) | 2.34 | - | - | 2.84 | 0.940 |
| **GTCRN (proposed)** | **0.02** | **0.04** | **18.83** | **2.87** | 0.940 |

> [!warning] Table 2 不是完整矩阵——四行有空格子，横比有结构性缺口
> | 模型 | Para. | MACs | SISNR | PESQ | STOI |
> |---|---|---|---|---|---|
> | RNNoise | ✓ 0.06 | ✓ 0.04 | **✗ 空** | ✓ 2.29 | **✗ 空** |
> | PercepNet | ✓ 8.00 | ✓ 0.80 | **✗ 空** | ✓ 2.73 | **✗ 空** |
> | DeepFilterNet | ✓ 1.80 | ✓ 0.35 | ✓ 16.63 | ✓ 2.81 | ✓ 0.942 |
> | S-DCCRN | ✓ 2.34 | **✗ 空** | **✗ 空** | ✓ 2.84 | ✓ 0.940 |
>
> **后果**：① **RNNoise 与 PercepNet 无法在 SISNR/STOI 上与 GTCRN 比较**——尽管 Abstract 声称 `surpasses RNNoise`，可比的只有 PESQ 一项（2.29 vs 2.87）；② **S-DCCRN 无法在算力上与 GTCRN 比较**——而 S-DCCRN 是表内唯一 PESQ 接近 GTCRN 的模型（2.84 vs 2.87）；③ **论文 §3.3.2 写 `surpasses other baseline models ... in terms of SISNR and PESQ`，但 SISNR 实际上只与 DeepFilterNet 一个模型可比**（16.63 vs 18.83）。
>
> **本库记录为：Table 2 的横比能力被空格子大幅削弱，"surpasses" 的主张在 SISNR 上只有 1 个可比对象、在 STOI 上则完全不成立（GTCRN 0.940 = S-DCCRN 0.940 < DeepFilterNet 0.942）。**

> [!note] 表内最硬的一条事实：GTCRN 与 RNNoise 的算力完全相同
> **GTCRN：0.02 M 参数 / 0.04 G MACs；RNNoise：0.06 M 参数 / 0.04 G MACs。**
> 即 **MACs 相同（0.04 G/s）、参数量约为 RNNoise 的 1/3**，而 **PESQ 2.87 vs 2.29（+0.58）**。
> **这是本篇最干净的对照**（同算力量级、同数据集、同指标），也是 Abstract `surpasses RNNoise, a typical lightweight model with similar computational burden` 这句的支撑。
> **但必须注意口径**（见下一条 `[!contradiction]`）：**RNNoise 的数字不是同口径复现的**。

> [!contradiction] **RNNoise 的数字来自它自己的官方 repo，与其他各行口径不同——本篇唯一的脚注就在这里**
> `gtcrn-page4.png` 渲染图显示 **Table 3 的 RNNoise 行带脚注上标 `1`**，而**该脚注印在第 4 页的页脚**（逐字）：
> > `1 Metrics are measured with source code provided at https://github.com/xiph/rnnoise/`
>
> **两个问题**：
> 1. **脚注只挂在 Table 3**（渲染图上 Table 3 的 RNNoise 带 `1`），但 **Table 2 也有 RNNoise 行且同样没有标注**——两个表的 RNNoise 数字是否同源、Table 2 的 RNNoise 是否也是用官方 repo 代码测的，**论文未说明**；
> 2. **口径不同意味着不可直接横比**：用 RNNoise 官方 repo 的代码测出的 PESQ 2.29 / DNSMOS-P.808 3.15，**与论文自己重训/复现的其他模型不是同一套评估流程**（其他模型显然来自各自论文报告的数字）。
>
> **本页的处置**：把这一条作为**引用 Table 2/3 时的一等警示**记录。这与 [[wiki_low_latency/sources/2025/FastEnhancer 2025]] 的"GTCRN^a 用官方 checkpoint、LiSenNet^c 等是作者重实现重训"是**同类问题**（基线来源不统一），但本篇的脚注**只覆盖了 Table 3 的一行**，比 FastEnhancer 的交代更不完整。

### 4.5 Table 3：DNS3 blind test set（全文照抄 + 表头归属核对）

| 模型 | Para. (M) | MACs (G/s) | P.808 | BAK | SIG | OVRL |
|---|---|---|---|---|---|---|
| Noisy | - | - | 2.96 | 2.65 | 3.20 | 2.33 |
| RNNoise<sup>1</sup> (2018) | 0.06 | 0.04 | 3.15 | 3.45 | 3.00 | 2.53 |
| S-DCCRN (2022) | 2.34 | - | 3.43 | - | - | - |
| **GTCRN (proposed)** | **0.02** | **0.04** | **3.44** | **3.90** | 3.00 | **2.70** |

**表头归属（`gtcrn-page4.png` 逐格核对）**：渲染图上表头是双层——`DNSMOS-P.808` 是**单列**（值 2.96 / 3.15 / 3.43 / 3.44），紧邻其右的 `DNSMOS-P.835` 下挂**三个子列 `BAK / SIG / OVRL`**。**本页据此确认**：

| 模型 | P.808 | BAK | SIG | OVRL |
|---|---|---|---|---|
| Noisy | 2.96 | 2.65 | 3.20 | 2.33 |
| RNNoise<sup>1</sup> | 3.15 | 3.45 | 3.00 | 2.53 |
| S-DCCRN | 3.43 | — | — | — |
| GTCRN | 3.44 | 3.90 | 3.00 | 2.70 |

**四项读法（全部写数值对）**：

| 指标 | GTCRN | 最接近的对照 | 差值 |
|---|---|---|---|
| P.808 | **3.44** | S-DCCRN **3.43** | +0.01 |
| BAK（背景噪声抑制） | **3.90** | RNNoise **3.45** | +0.45 |
| **SIG（语音保真）** | **3.00** | **RNNoise 3.00** | **0.00（完全相同）** |
| OVRL（总体） | **2.70** | RNNoise **2.53** | +0.17 |

> [!warning] **SIG 3.00 是 Table 3 里最需要注意的一项：GTCRN 与 RNNoise 的 SIG 完全相同**
> DNSMOS P.835 的 SIG 分衡量**语音信号本身的保真度**（是否有语音损伤/失真），是"人声保留"的核心指标。
> **GTCRN 的 SIG = 3.00，RNNoise 的 SIG = 3.00** —— 即 **GTCRN 在背景噪声抑制（BAK 3.90 vs 3.45，+0.45）与整体（OVRL 2.70 vs 2.53，+0.17）上明显领先，但在语音保真上没有任何提升**。
> 按本库 [[wiki_low_latency/concepts/低 SNR 人声保留评估]] 的口径，**"BAK 提升而 SIG 不升"正是需要报告 SIG–BAK trade-off 的情形**。论文对此**完全没有讨论**——它只写 `our model outperforms RNNoise by a wide margin`。
> **本页记录为：GTCRN 在 DNS3 blind 上的收益集中在"噪声抑制"，"语音保真"项上无增益。**（另需注意 **Noisy 的 SIG 是 3.20，高于 GTCRN 与 RNNoise 的 3.00** —— 即**两个增强器都使 SIG 低于未处理信号**。这个现象在 DNSMOS 评测里常见（增强引入失真），但论文未提。）

> [!question] Table 3 只有 4 行，S-DCCRN 的 BAK/SIG/OVRL 全空
> 论文声称 `also surpasses the large-scale S-DCCRN model`，但 **S-DCCRN 只有 P.808 一格数字（3.43）**，GTCRN 的 3.44 比它高 **+0.01**。
> 在 0.01 的量级上、**无种子数、无方差、无置信区间**的情况下，本库**无法判断这个差值是否显著**。论文用了 `surpasses` 这个较强的动词，但支撑它的只有 0.01 的差距。本页记录为**证据强度不足**。

### 4.6 Fig. 5：两个典型案例（**复核后确认与正文一致；文本流无面板标签，需坐标复核**）

Fig. 5 是 DNS3 test set 的两个典型样本，2 行 × 4 列：`(a,e) Noisy / (b,f) Enhanced by RNNoise / (c,g) Enhanced by GTCRN / (d,h) Clean`。

> [!question] **Fig. 5 的标注经复核后确认「与正文一致」，不是矛盾（本页曾一度误判，此处改正）**
> **从 PDF 文本流读出的四个数字**（`gtcrn.txt` 第 2186–2197 行）：`PESQ: 1.16 / STOI: 0.66`、`PESQ: 1.42 / STOI: 0.87`、`PESQ: 1.28 / STOI: 0.73`、`PESQ: 1.94 / STOI: 0.93`。
> **用 PyMuPDF 提取这四个标注的坐标**（`p.get_text('dict')`，单位：PDF point）：
> | 标注 | PESQ | STOI | 块左上角 (x, y) | 所属行/列 |
> |---|---|---|---|---|
> | #1 | **1.16** | **0.66** | (255, **69**) | **第 1 行**（y≈65–135），第 **2** 列 |
> | #2 | **1.42** | **0.87** | (363, **69**) | **第 1 行**，第 **3** 列 |
> | #3 | **1.28** | **0.73** | (255, **170**) | **第 2 行**（y≈165–235），第 **2** 列 |
> | #4 | **1.94** | **0.93** | (363, **170**) | **第 2 行**，第 **3** 列 |
>
> **面板标签的坐标**（同一提取，`gtcrn.txt` 第 2174–2185 行）：
> - 第 1 行：`(a) Noisy` / `(b) Enhanced by RNNoise` / `(c) Enhanced by GTCRN` / `(d) Clean`
> - 第 2 行：`(e) Noisy` / `(f) Enhanced by RNNoise` / `(g) Enhanced by GTCRN` / `(h) Clean`
>
> **坐标对齐结果（本页已用 700 dpi 裁剪逐图确认）**：标识 `(b) Enhanced by RNNoise` 的面板其**图内标注**确实是 **PESQ 1.16 / STOI 0.66**；标识 `(c) Enhanced by GTCRN` 的面板其**图内标注**是 **PESQ 1.42 / STOI 0.87**。
>
> **⇒ 复核结论（2026-09-27 主 agent 用 600 dpi 单面板裁剪二次确认）**：**GTCRN 在两行上都高于 RNNoise** ——
> 第 1 行：GTCRN **1.42** > RNNoise **1.16**（+0.26 PESQ）；第 2 行：GTCRN **1.94** > RNNoise **1.28**（+0.66 PESQ）。
> STOI 同向：0.87 > 0.66、0.93 > 0.73。
> **这与正文 §3.3.2 的定性描述（`GTCRN exhibits superior noise suppression than RNNoise`）以及 Table 2 / Table 3 的结论方向完全一致。**
>
> **⚠️ 本页初稿曾把这两组数读成"RNNoise 更高"，那是本页自己的归组错误，现已改正。** 教训：Fig. 5 的四个数字在 PDF 文本流里**没有面板标签**，
> 必须靠坐标（x 在 168–290 为第 2 列、295–417 为第 3 列）与裁剪图目视**双重复核**才能定归属。**本页的记录以裁剪图目视结果为准。**

**Fig. 5 数值按"渲染图实际标注"照录**（本页只报事实，不做归属修正）：

| 行 | 列位置 | 面板标签（论文印刷） | 图内实际标注 PESQ | 图内实际标注 STOI |
|---|---|---|---|---|
| 1 | 第 1 列 | (a) Noisy | 无标注 | 无标注 |
| 1 | 第 2 列 | (b) Enhanced by RNNoise | **1.16** | **0.66** |
| 1 | 第 3 列 | (c) Enhanced by GTCRN | **1.42** | **0.87** |
| 1 | 第 4 列 | (d) Clean | 无标注 | 无标注 |
| 2 | 第 1 列 | (e) Noisy | 无标注 | 无标注 |
| 2 | 第 2 列 | (f) Enhanced by RNNoise | **1.28** | **0.73** |
| 2 | 第 3 列 | (g) Enhanced by GTCRN | **1.94** | **0.93** |
| 2 | 第 4 列 | (h) Clean | 无标注 | 无标注 |

> [!note] 这两个样本的绝对数值偏低（PESQ 1.16–1.94），说明它们是**困难样本**
> 即便按实测数值（1.42 / 1.94），GTCRN 在这两条样本上的 PESQ 仍**远低于 Table 2 的平均 2.87**。因此 Fig. 5 是**故意挑选的困难案例**——论文的用意应是"展示 GTCRN 在困难样本上仍比 RNNoise 保留更多谐波结构"（从频谱图上看确实如此：粗看 GTCRN 面板的高频谐波条纹比 RNNoise 面板清晰）。
> **但这也意味着 Fig. 5 不能作为"平均性能"的证据**，它只是两个样本。论文未说明挑选标准。

### 4.7 STFT 重建流程与 padding：本库关心的两处空白

> [!question] 论文从未说明"如何用 CRM 重建波形"，也从未说明任何 padding
> 论文只说了 ① 最后一个 DeConv 用 tanh、② 输出被解释为 **CRM 的实部与虚部**（`These values are interpreted as the real and imaginary parts of the estimated complex ratio mask (CRM) [19]`），然后**直接跳到结论**。
> **未说明的**：
> | 缺失项 | 为什么重要 |
> |---|---|
> | **CRM 如何与带噪谱相乘**（$\tilde S = \text{CRM} \odot X$？） | 这是 CRM 类方法的标准步骤，但论文未写 |
> | **iSTFT 的窗与 hop**（是否与 STFT 相同） | 决定合成阶段是否有额外延迟 |
> | **OLA / overlap-add 的方式** | 影响合成延迟与重建质量 |
> | **相位是否替换**（CRM 已含相位信息，理论上不需替换） | 本库要求区分 mask 类型 |
> | **所有 conv 的 padding 方式** | **因果性的直接判据**——`same` padding 常用于对称填充（含未来），`causal` padding 则不含 |
> | **隐层状态的跨帧传递方式**（是否有 ring buffer / state） | 流式部署的前提 |
> | **DPRNN 的 chunk 长度**（决定 intra/inter 切分边界） | 决定跨帧缓存长度 |
>
> **论文对以上全部沉默。** 按本库 [[wiki_low_latency/concepts/严格因果与算法延迟]] 的审计要求，这些都是**必填字段**。
> **本页的结论：GTCRN 的因果性是"声明级"的，架构级的证据链在本篇内完全不存在。**

### 4.8 参数量/算力口径的三方矛盾（**本节是本页最重要的跨页发现**）

论文在**三处**（Abstract、§3.2、§4 结论）一致声称：

> **23.7 K parameters and 39.6 MMACs per second**

§3.2 的完整句（p.3 逐字）：

> "For the whole model, the number of parameters is **23.7 K** and the computational cost is **39.6 MMACs per second**."

**23.7 K 与 39.6 M/s 恰好对应 Table 1 最后一行**（SFE ✓ / TA ✗ / TRA ✓：Para. 23.67 K、MACs 39.63 M/s）——即**这是"全部模块打开"的完整模型**，与 §2 描述的完整 GTCRN 一致。**内部自洽。**

> [!contradiction] **库内三方对 GTCRN 的参数量/算力口径不一致，且都与论文正文不同或需要解释**
> | 来源 | 记录值 | 出处 |
> |---|---|---|
> | **GTCRN 原文**（本篇） | **23.7 K 参数 / 39.6 MMACs per second** | Abstract、§3.2、§4；对应 Table 1 的 SFE✓+TRA✓ 行（23.67 K / 39.63 M/s） |
> | [[wiki_low_latency/entities/FastEnhancer]]（第 191 行，其 Table 2） | **24 K 参数 / 40 M MACs**（记为 GTCRN<sup>a</sup>，脚注 a = `Evaluated using the official checkpoint`） | FastEnhancer 作者的复现口径（**四舍五入 + 官方 checkpoint**） |
> | [[wiki/sources/2026/muNet 2026]]（第 110 行，其对比表） | **48 K 参数 / 33 MMACs** | μNet 论文的转述（**与原文差异最大**） |
> | [[wiki_low_latency/sources/2026/PSMSE 2026]]（第 109 行） | **23.7 K**（写作 `23.7K–79K 参数` 区间，与原文一致） | PSMSE 论文的引用 |
>
> **本页的读数**：
>
> **(1) 24 K / 40 M 与 23.7 K / 39.6 M 是同一个数的四舍五入** —— 差值仅 `+0.3 K` 与 `+0.4 M/s`（相对误差 1.3 % 与 1.0 %），**不构成矛盾**。FastEnhancer 用"官方 checkpoint"评测，其 checkpoint 的**实际参数量可能与论文声称值略有出入**（论文常按设计值报告，代码实现可能含额外的可学习参数如 BN 的 affine 参数）。
>
> **(2) 48 K / 33 MMACs 与原文的差异无法用例差解释** —— 参数 **48 K vs 23.7 K**（约 **2.03×**），MACs **33 vs 39.6**（约 **0.83×**）。**两者方向相反**（参数翻倍，算力反降），**不可能来自同一模型的同一配置**。
>
> > [!question] 库内另有记录称"官方 repo 更新后是 48.2 K / 33.0 MMACs"
> > 本任务 brief 提到：此前核查发现**官方 repo（`https://github.com/Xiaobin-Rong/gtcrn`）更新后是 48.2 K / 33.0 MMACs**。**本页无法独立核实这一点**（`evidence_policy: local_pdf_only`，本页只核对本地 PDF，**没有网络访问权限，也没有克隆该 repo**）。
> > **但值得注意的是：48.2 K / 33.0 与 μNet 论文的 48 K / 33 高度吻合** —— 这强烈提示 μNet 引用的是**官方 repo 的实测值**，而不是论文的声称值。
>
> **(3) 因此"48 K / 33"这一口径很可能是官方实现（或更新后的实现）的真实规模，而"23.7 K / 39.6"是论文正文的设计声称值。** 两者差 2 倍的原因论文**从未说明**。
>
> **可能的解释（本页列出，均未验证）**：
> | 假设 | 支持 | 反对 |
> |---|---|---|
> | **A. 官方 repo 含论文未计入的参数**（如 BN 的 affine、GRU 的 bias、TRA 的 FC） | 论文报告 23.7 K 恰好等于 Table 1 的表内值，**可能是"按设计算"而非"按 `sum(p.numel())` 算"** | 2 倍的差距偏大，普通 BN/GRU 参数不至于翻倍 |
> | **B. repo 的默认配置与论文不同**（如 GRU 隐层更大、SFE 全开 + 额外层） | MACs 从 39.6 降到 33 说明**计算结构变了**（不是单纯加参数） | 变小的 MACs 通常意味着变小，与参数翻倍矛盾 |
> | **C. 论文与 repo 的 MACs 统计口径不同**（per-second vs per-frame；是否含 STFT；是否按 16 ms hop） | `MMACs per second` 是**时间归一化**的量，与 hop 直接相关 | —— |
> | **D. μNet 的数字有其他来源错误**（如引用了别的模型的数字） | —— | 48.2 K / 33.0 的高度吻合降低了这个可能 |
>
> **本页的处置（依 brief 要求，不单方面采信任何一方）**：
> - **本页在正文与实体页一律以论文原文的 23.7 K / 39.6 MMACs per second 为主记录**（因为它有 PDF 一手证据，且与 Table 1 内部自洽）；
> - **同时在 `[!contradiction]` 中并列列出 48 K / 33（μNet 口径）与 24 K / 40（FastEnhancer 口径）**；
> - **明确标注：24 K/40 是四舍五入，48 K/33 无法与原文调和，且与"官方 repo 更新值"高度吻合**；
> - **建议主 agent 把这一条登记入跨页矛盾清单**，并在有网络条件时**直接核查 `https://github.com/Xiaobin-Rong/gtcrn` 的 `model.py` 与 README 的参数量声明**。
>
> **这一条是本页最重要的跨页发现之一**：它意味着**本库目前对 GTCRN 这个"超轻量锚点"的记录是不一致的**，而 GTCRN 恰是被 FastEnhancer、μNet、PSMSE、RT-Tango 四篇引用为参照的锚点——**锚点的数值错了，四条引用链一起偏**。

## 5. 这个方向还剩什么问题没解决？（future work / limitation）

### 5.1 论文自己承认的局限

**几乎没有。** 论文全文**没有 Limitation 或 Future Work 章节**；§4 结论只有 5 句总结性陈述，最后 3 句是致谢。逐字：

> "In this paper, we present GTCRN, a speech enhancement model that requires **only 23.7 K parameters and 39.6 MMACs per second**. **Multiple strategies are applied to DPCRN to effectively reduce the model while maintaining speech enhancement performance.** Experiments show that our model not only outperforms RNNoise by a substantial margin on the VCTK-DEMAND and DNS3 dataset, but also achieves **competitive performance** compared to several baseline models with significantly higher computational overhead."

**唯一接近自我限定的是 `competitive performance` 这个措辞**（而非 `state-of-the-art`），但论文**没有说明这个"competitive"的边界在哪里**（哪一项指标、哪一个对比集合）。

> [!warning] 本库口径下的评价：**这篇论文的诚实性体现在用词，而不是体现在数据**
> 它的 Abstract/结论用 `competitive` 而非 `SOTA`（这是好的），但：
> - **没有 limitations 章节**；
> - **没有 future work**；
> - **没有报告任何本库关心的一等字段**（延迟、因果证据、人声保留分层）；
> - **Table 2/3 有大量空格子**；
> - **RNNoise 的数字口径不同且只在 Table 3 标注**。
>
> 这是一篇**典型的 4 页 ICASSP 短文**：贡献是"一个极小的可用模型"，而不是"一套完整的评估"。本库记录它时**必须把这两者分开**。

### 5.2 本页读出的隐藏问题（本库关注）

**(a) 延迟账本：几乎空白——本库最严重的缺口**

| 字段 | 本篇状态 |
|---|---|
| 采样率 | **16 kHz**（§3.1、§3.2） |
| 窗函数 | **sqrt-Hanning**（§3.2） |
| 窗长 | **32 ms**（§3.2；@16 kHz = 512 samples） |
| **hop** | **16 ms**（§3.2；@16 kHz = 256 samples） |
| FFT 长度 | **512**（§3.2） |
| 频率点数 | **未直接报告**（本页推得 257 = 512/2+1） |
| **STFT center / 帧锚定** | **未报告**（一等审计项） |
| **look-ahead** | **未报告** |
| **group delay** | **未报告** |
| **逐层 padding** | **未报告** |
| **算法的 ms 级延迟** | **未报告**（论文**没有这个概念的数值，也没有定义**） |
| **RTF** | **未报告** |
| **p50 / p95 / p99** | **未报告** |
| **目标硬件 / 平台** | **未报告** |
| **模型执行时间** | **未报告** |
| **峰值 RAM / SRAM** | **未报告** |
| **功耗** | **未报告** |
| **量化** | **未报告**（无 int8、无 PTQ、无 QAT） |
| **端侧实测** | **未报告** |
| **warm-up / state reset** | **未报告** |
| **长流稳定性** | **未报告** |
| **batch=1 / chunk 大小** | **未报告** |
| **算力证据的形式** | **只有名义 MMACs（39.6 M/s）**——本库的 **L0 级**（最低） |

> [!warning] GTCRN 的延迟下界只能由 hop 推得，且这个推导依赖两组未报告的信息
> **唯一的时延相关数字是 hop = 16 ms**。按本库 [[wiki_low_latency/concepts/严格因果与算法延迟]] 的口径：
> - **算法延迟下界 ≈ hop = 16 ms**（若采用 `center=False` 的左对齐 STFT）；
> - **若 `center=True`，则还要加上 $W/2 = 16$ ms**，即 **约 32 ms**。
>
> **因此 GTCRN 不是约 2 ms 候选** —— 按最乐观的读法（16 ms hop、左对齐、无 look-ahead），它的算法延迟下界也比 2 ms 目标**高约 8 倍**。
>
> **但本页必须同时把另一半说清楚**：因为 **`center` 未报告**，本库**既不能判定它 ≥ 16 ms，也不能排除它 ≤ 16 ms** —— 能确定的只有"hop 是 16 ms，因此**帧率是 62.5 Hz**"。这是一条**"证据不足，双向都不能判定"**的性质，是本页认为最该传给本库的一条判断纪律。详见 §5.3。

**(b) 因果性：一句声明，零证据链**

论文关于因果性的**全部**表述（p.2 §2.2，逐字）：

> "We use grouped bidirectional GRU for intra-frame modeling, and grouped unidirectional GRU for inter-frame modeling, **so that the causality of the model can be guaranteed**."

**这是全文唯一一处提 causality（本页已 grep 全文确认，见 §5.4）。**

| 审计项 | 本篇 |
|---|---|
| 作者声明 | ✓ 一句（`so that the causality of the model can be guaranteed`） |
| 逐层 padding certificate | ✗ **未给** |
| state certificate（哪些层有状态、如何跨帧传递） | ✗ **未给** |
| STFT center | ✗ **未报告** |
| DD-Conv2D / P-Conv2D 的 padding 方式 | ✗ **未报告** |
| DPRNN chunk 长度（intra/inter 切分边界） | ✗ **未报告** |
| 时间轴感受野 | ✗ **未给**（本页推得 3/5/11 帧，见 §3.5） |
| skip connection 的层对 | ✗ **未给** |
| 隐层维度与跨帧缓存长度 | ✗ **未报告** |

**本库判定**：记为 **`paper-claimed-causal`** —— **作者自述，非架构级认证**。

> [!important] 本页的**结构审计（7 项 + accelerator launch）**——按 [[wiki_low_latency/sources/2026/Early Exit Compute-Matched 2026]] 的写法补全
> | # | 审计项 | GTCRN 的状态 | 影响 |
> |---|---|---|---|
> | 1 | **采样率** | 16 kHz（§3.1） | 明确 |
> | 2 | **窗长 / hop / FFT** | 32 ms / 16 ms / 512（§3.2） | 明确 |
> | 3 | **STFT center / 帧锚定** | **未报告** | **决定性**：若 `center=True` 则前端含 **16 ms 未来样本** |
> | 4 | **inter-frame 循环方向** | **单向 GRU**（论文明确） | **正向**：这是论文的因果性支柱，且**理由合理**（inter-frame 建模的是"某频点在时间上的依赖"） |
> | 5 | **intra-frame 循环方向** | **双向 GRU**（论文明确） | **本页判定为不破坏因果**——因为它在**单帧内、沿频率轴**双向，不跨时间帧（见 §3.4 的 `[!important]`） |
> | 6 | **卷积层的 padding 方式** | **未报告**（全部 Conv / DeConv / P-Conv2D / DD-Conv2D） | **决定性**：`same` padding 常含未来帧；`causal` padding 不含 |
> | 7 | **时间轴感受野与缓存需求** | **未给**；本页推得 DD-Conv2D 分别为 **3 / 5 / 11 帧**（kernel 时间维 3、dilation 1/2/5），单条链累计 **17 帧** | 若为因果卷积，则需缓存 **$(k-1)d$** 帧历史（分别是 2 / 4 / 10 帧） |
> | 8 | **accelerator launch / 图的段数** | **不适用**（论文无任何硬件或部署讨论） | 本库新增的第 8 项（[[wiki_low_latency/concepts/2609.29867-compute-matched-dynamic-depth]] 命题 ③），本篇**完全空白** |
>
> **判定**：`paper-claimed-causal`。**7 项中 3 项（#3 / #6 / #7）为未报告，且都是决定性的。**本页**不能**把它升级为 `strict_causal`，也**不能**判为 `non_causal`。

**(c) 人声保留：指标只有三项，且没有一项分层**

| 本库要求字段 | GTCRN 报告情况 |
|---|---|
| SISNR | **有**（Table 1/2；[25] SI-SNR，源自 Le Roux 等 ICASSP 2019） |
| PESQ | **有**（Table 1/2；[26] ITU-T P.862） |
| STOI | **有**（Table 1/2；[27] Taal 等 ICASSP 2010） |
| DNSMOS P.808 | **有**（Table 3；[29]） |
| DNSMOS P.835（BAK/SIG/OVRL） | **有**（Table 3；[30]）——**但只有 2 个模型有全三项**（Noisy 与 GTCRN），RNNoise 有全三项但口径不同，S-DCCRN 只有 P.808 |
| **ASR WER（可懂度）** | **未报告** |
| **主观 MOS / MUSHRA** | **未报告** |
| **负 SNR 分层（−10/−5/0/5 dB）** | **未报告**（DNS3 训练 SNR 是 −5~15 dB，**但测试结果没有按 SNR 分层**） |
| **噪声类型分层（babble / 竞争说话人 / 瞬态 / 未见噪声）** | **未报告**（未列出噪声类别） |
| **false-suppression（语音误抑）** | **未报告** |
| **SPP / VAD 校准** | **未报告** |
| **F0 / formant / prosody continuity** | **未报告** |
| **voiced energy 保留** | **未报告** |
| **混响指标（C50 / SRMR / DRR）** | **未报告**（尽管 DNS3 训练含 RIR 与前 100 ms 反射设置） |
| **eSTOI** | **未报告** |

> [!warning] 本库口径下最需要警示的一点：**GTCRN 的 SIG 没有提升**
> Table 3 中 **GTCRN 的 SIG = 3.00，与 RNNoise 的 3.00 相同**，且**两者都低于 Noisy 的 3.20**。
> 按本库 [[wiki_low_latency/concepts/低 SNR 人声保留评估]] 的规则——「**不能把 BAK 提升而 SIG/可懂度下降描述为无条件改进；需要报告 SIG–BAK trade-off 和失败案例**」——GTCRN 的这篇论文**恰好落在需要报告这个 trade-off 的情形上，但它没有报告**。
> **本页记录为：GTCRN 在 DNS3 blind 上的 DNSMOS 收益完全来自 BAK（+0.45 vs RNNoise）与 OVRL（+0.17），SIG 上没有增益。**

**(d) 算力证据等级：本库最低级（L0）**

| 维度 | GTCRN |
|---|---|
| 是名义 MACs 还是实测 | **名义 MMACs**（39.6 M/s） |
| 目标硬件 | **未报告** |
| 量化 | **未报告** |
| RTF / 执行时间 | **未报告** |
| 是否含端到端 | **无法判断**（连 STFT 是否计入 MMACs 都没说） |
| 是否报功耗 / 内存 | **未报告** |

**⇒ 按 [[wiki_low_latency/concepts/2609.29867-compute-matched-dynamic-depth]] 建议的算力证据五级，GTCRN 属 **L0（名义 MACs，无任何测量、无目标硬件）**。这与本库对它的引用方式形成张力：**GTCRN 被库内四篇用作"超轻量"的锚点，但它自己提供的算力证据是最低等级。**

**(e) 可复现性**

| 项 | 状态 |
|---|---|
| 开源代码 | **有**（`https://github.com/Xiaobin-Rong/gtcrn`，§3.3.2 给出） |
| 训练超参 | **部分**（Adam、lr 0.001、half on 5-epoch plateau、batch 4/16、DNS3 8 s chunk、40,000 pairs/epoch） |
| **训练总 epoch / 步数** | **未报告** |
| **随机种子数** | **未报告** |
| **方差 / 置信区间** | **未报告** |
| **预训练模型** | 论文未提（repo 是否提供，**本页无法核实**） |
| **GRU 隐层维度** | **未报告** |
| **DPRNN chunk 长度** | **未报告** |
| **SFE 后的通道数** | **未报告** |
| **skip connection 的层对** | **未报告** |

> [!question] 无种子、无方差 —— 而论文有多处 `+0.01` 量级的结论依赖
> Table 1 的若干差值是 `+0.01 PESQ`（如 TA→TRA 的 1.89→1.91、加上 SFE 后 1.92→1.94）、Table 3 的 P.808 差值是 `+0.01`（S-DCCRN 3.43 vs GTCRN 3.44）。
> **在没有种子数与方差的情况下，本库无法判断这些差值是否落在训练波动之内。** 论文用了 `surpasses`（Table 3 的 S-DCCRN）这样的强动词，但支撑只有 0.01。
> 这与 [[wiki_low_latency/sources/2026/Early Exit Compute-Matched 2026]] 的问题是**同构的**，但**更严重**——那里至少有 824 条测试样本与多次运行的框架，这里连样本层面的方差都没提。

### 5.3 与约 2 ms 约束的距离

| 项 | GTCRN |
|---|---|
| 论文给出的算法延迟 | **无**（论文没有这个概念） |
| 唯一可用的时延锚点 | **hop = 16 ms** |
| 算法延迟下界（本页推） | **≈ 16 ms**（若 `center=False`）；**≈ 32 ms**（若 `center=True`，需加 $W/2$） |
| look-ahead | **未报告** |
| 模型执行时间 | **未报告** |
| 目标硬件 | **未报告** |

**本库判定**：

1. **GTCRN 不是约 2 ms 候选**：即使按最乐观的读法，其算法延迟下界（16 ms）也是 2 ms 目标的**约 8 倍**；论文本身也**没有声称**任何低时延性质。
2. **但也不是"确定的非候选"**：因为 **`center` 未报告**，本库**无法排除**某些实现变体（例如把 hop 改小）能落入更低延迟档。—— 这一点有**库内直接证据**：见下。
3. **本篇应归入"超轻量"议题，而非"约 2 ms 严格因果"议题。**

> [!important] **GTCRN 可以被重新配置到 4 ms hop —— 库内已有直接证据，且代价被量化了**
> [[wiki_low_latency/sources/2026/RT-Tango 2026]] 把**分布式 GTCRN** 用作双耳对照，并**在两种帧率下各跑了一次**（其 Table 1，页面第 219–221 行逐字）：
>
> | 配置 | hop | DNN MACs (MMAC/s) | SI-SDR（左/右） | PESQ（左/右） |
> |---|---:|---:|---|---|
> | GTCRN | **16 ms** | **48.98** | 5.6 / 3.7 | 1.47 / 1.34 |
> | GTCRN | **4 ms** | **197.5** | 6.0 / 4.0 | 1.52 / 1.36 |
>
> **三个直接结论**：
> 1. **GTCRN 的架构可以被重新配置到 4 ms hop**（即帧率从 62.5 Hz 提到 250 Hz），**因此它不是"被架构锁死在 16 ms"的模型**；
> 2. **代价是算力从 48.98 涨到 197.5 MMAC/s（约 4.03×，即 $197.5/48.98 = 4.03$）** —— 与帧率提升倍数（250/62.5 = **4.0**）几乎完全一致，说明**GTCRN 的算力几乎正比于帧率**（逐帧计算，无跨帧复用）；
> 3. **质量反而略升**（SI-SDR 5.6→6.0，PESQ 1.47→1.52）—— 因为帧率提高让时频分辨率与状态更新更细。
>
> **口径提醒**：RT-Tango 报的 **48.98 / 197.5 MMAC/s 是"每节点分布式 GTCRN"的口径**（输入是 4 麦信号、mask 作用于本地参考通道），**与 GTCRN 原文的 39.6 MMACs/s 不是同一配置**（48.98 vs 39.6 差 1.24×）。**两者不可直接相减**，只能用于说明"**该架构可被重配到 4 ms**"这一质性事实。
>
> **本库意义**：这条对照把 GTCRN 从"16 ms 的模型"变成了"**一个可跨帧率重配的架构，其算力随帧率线性增长**"。若要把 GTCRN 拉到 2 ms hop，按同样比例需要约 **$197.5 \times (4/2) = 395$ MMAC/s**（**本页的线性外推，RT-Tango 未测 2 ms**）——这个量级已超出"超轻量"的范畴（RNNoise 是 0.04 G/s = 40 MMAC/s，GTCRN 原位是 39.6 M/s）。**即：GTCRN 靠"提高帧率"进 2 ms 档，会以牺牲其唯一卖点（超低算力）为代价。**

## 6. 本论文在库中的位置关联（cross-reference matrix）

| 关系 | 库中论文/概念 | 关联与差异 |
|---|---|---|
| **前身/基石** | [[wiki_low_latency/entities/DPCRN]]、[[wiki_low_latency/concepts/2107.05429-dual-path-recurrent-context]]、[[wiki_low_latency/sources/2022/Skip-DPCRN 2022]] | **GTCRN 明确以 DPCRN [3, 16] 为 backbone**（p.1 §1：`Using DPCRN [3, 16] as the backbone`）。引文 [3] 是 DPCRN 原文（Le 等，Interspeech 2021，本库概念页 2107.05429 对应），引文 [16] 是 Inference Skipping（Le 等，TASLP 2022，本库 [[wiki_low_latency/sources/2022/Skip-DPCRN 2022]] 对应）——**两者共享作者 J. Lu，即本条谱系是同一课题组的连续工作**。DPCRN 留下的 gap 是"参数量与 MACs 对端侧仍过大"，GTCRN 用 ERB + grouped conv + grouped RNN 填上。**但 GTCRN 未给出 DPCRN 的算力数字**，因此"压了多少倍"在本篇内不可算 |
| **被谁用了（最主要）** | [[wiki_low_latency/sources/2025/FastEnhancer 2025]]、[[wiki_low_latency/entities/FastEnhancer]] | FastEnhancer 把 GTCRN 列为**最主要的对照**：`GTCRN^a`（脚注 a = **用官方 checkpoint 评测**）记为 **24 K / 40 M MACs / RTF 0.060（Xeon）/ 0.042（M1）**，P.808 3.43 / SDR 18.8 / PESQ 2.87 / STOI 0.940 / **WER 3.6**。**口径核对**：24 K/40 M 与原文 23.7 K/39.6 M 是同一数的四舍五入 ✓；PESQ 2.87 与 STOI 0.940 与原文 Table 2 **完全一致** ✓；SDR 18.8 对应 SISNR 18.83 ✓。**FastEnhancer 提供了本篇完全没有的两项：RTF 与 WER** —— 即本库能从 FastEnhancer 间接获得 GTCRN 的**速度与可懂度**，**但必须注意这是第三方复现，不是 GTCRN 自报** |
| **被谁用了（架构借用）** | [[wiki_low_latency/sources/2026/RT-Tango 2026]]、[[wiki_low_latency/entities/RT-Tango]] | RT-Tango **明确借鉴 GTCRN 的 ERB 压缩**（其页面第 148 行：「ERB 压缩明确借鉴 GTCRN [11]」），并把**分布式 GTCRN** 用作双耳对照，**在 16 ms 与 4 ms 两个帧率下各测一次**：16 ms → **48.98 MMAC/s**、4 ms → **197.5 MMAC/s**（其 Table 1）。**数字核对**：这两个数**与 GTCRN 原文的 39.6 MMACs/s 不是同一配置**（分布式、4 麦输入、mask 作用于本地参考通道），**不可直接横比**，但可用于证明"**该架构可被重配到 4 ms**"。RT-Tango 还在同帧率下比 GTCRN **高效约 5.9 倍**（197.5 / 33.41 ≈ 5.91） |
| **被谁用了（分类引用）** | [[wiki_low_latency/sources/2026/PSMSE 2026]]、[[wiki_low_latency/entities/PSMSE]] | PSMSE 把 GTCRN 归入「**超轻量网络 FSPEN / GTCRN / [[wiki_low_latency/entities/LiSenNet\|LiSenNet]] / UL-UNAS**」，记其参数量区间为 **23.7K–79K**（**与本篇原文的 23.7 K 一致** ✓），并批评这一路线：「**performance tends to degrade due to the limited capacity of their simplified designs**」。**即 PSMSE 用 GTCRN 作为"容量受限"的例证**——这是与 FastEnhancer 立场不同的第三种态度（PSMSE 批评的是容量，FastEnhancer 批评的是 RTF） |
| **被谁用了（参照点）** | [[wiki_low_latency/sources/2026/Early Exit Compute-Matched 2026]]、[[wiki_low_latency/entities/Early-Exit-Conv-FSENet]] | 该篇把 GTCRN 列为**引文 [2]**，作为极轻量端的参照。**⚠️ 其页码著录为 pp. 10286–10290，与本篇 PDF 页脚的 971–975 冲突**（见本页开头的 `[!contradiction]`）。本页已用一手证据定案为 **971–975** |
| **被谁用了（主要竞品）** | [[wiki/sources/2026/muNet 2026]] | μNet 把 GTCRN 当**主要竞品**，其对比表（第 110 行）记为 **48 K / 33 MMACs / PESQ 2.26 / SI-SDR 14.62 / BAK 3.98**，并称 GTCRN 的 SI-SDR 是其表内最高。**⚠️ 48 K / 33 与原文的 23.7 K / 39.6 差异无法用例差解释**（见 §4.8）。**另**：μNet 论文脚注称「GTCRN **需缓冲最多 16 帧中间特征**」——**这个说法不见于 GTCRN 原文**，属外部转述。**PESQ 2.26 与 SI-SDR 14.62 也与本篇 Table 2 的 2.87 / 18.83 不同**，说明 μNet 用的是**另一套测试集/口径**（其表内 Noisy 是 1.58，而本篇 Table 2 的 Noisy 是 1.97） |
| **同分支竞品（子带/超轻量路线）** | [[wiki_low_latency/entities/PercepNet]]、[[wiki_low_latency/entities/DeepFilterNet2]]、[[wiki_low_latency/sources/2022/DeepFilterNet2 2022]]、[[wiki_low_latency/entities/DCCRN]]、[[wiki_low_latency/sources/2024/Distil-DCCRN 2024]] | **直接对照**：① **RNNoise**（0.06 M / 0.04 G/s，PESQ 2.29）——同算力量级、性能最低；② **PercepNet**（8.00 M / 0.80 G/s，PESQ 2.73）——算力 20 倍于 GTCRN；③ **DeepFilterNet**（1.80 M / 0.35 G/s，SISNR 16.63 / PESQ 2.81 / STOI 0.942）——**算力 8.75 倍而 STOI 反高 0.002**；④ **S-DCCRN**（2.34 M，PESQ 2.84 / STOI 0.940）——**MACs 空格无法比算力**。另：论文 §1 提到的 **TRU-Net [10]**、**DPCRN-CF [15]**、**parallel GRUs [11]** 三条路线在本库中**部分有页面**（DPCRN 相关有，TRU-Net 与 DPCRN-CF 暂无独立页） |
| **🔴 关键冲突：子带路线的存废** | [[wiki_low_latency/sources/2025/FastEnhancer 2025]]（§2.2）、[[wiki_low_latency/sources/2026/PSMSE 2026]]、[[wiki_low_latency/concepts/2509.21867-speed-optimized-streaming-design]]、[[wiki_low_latency/entities/FSB-LSTM]]、[[wiki_low_latency/concepts/2304.08707-full-sub-band-modeling]]、[[wiki_low_latency/entities/LiSenNet]] | **这是本库一对直接冲突，必须点明**：**GTCRN 是子带路线的代表**（ERB 压频带 + SFE 把子带关系搬进 channel 维）。而 **FastEnhancer 在 §2.2 明确批评**：BSRNN / FSPEN / **GTCRN** / LiSenNet 这一类子带方案「**increased architectural complexity and memory operations paradoxically led to higher RTFs**」，并主张"简单的 encoder-decoder 就够"。**证据形式**：FastEnhancer 用 RTF 说明（GTCRN RTF 0.060 vs FastEnhancer-B 0.022，**MACs 高 6.5 倍而快 2.7 倍**）；**GTCRN 论文内没有任何 RTF，因此无法回应**。**而 PSMSE 从第三个角度批评同一路线**（容量受限）。**⇒ 本库应把这三篇并读**：子带路线在**参数与 MACs** 上赢（GTCRN 0.02 M / 0.04 G/s）、在 **RTF** 上被质疑（FastEnhancer）、在**容量**上被质疑（PSMSE）。**GTCRN 原文对后两条都没有数据**，这正是它作为"锚点"的脆弱之处。**2026-09-27 补摄 [[wiki_low_latency/sources/2024/LiSenNet 2024\|LiSenNet]] 后，这条批评链的双方首次都有了一手证据**：LiSenNet 自报 **RTF 0.028（Xeon E5-2620 v4）**，与 FastEnhancer 在 Xeon Gold 6248R 上测的 **0.034** 同量级——**说明"子带方案 RTF 高"这一批评在本篇上并不成立**（LiSenNet 的 RTF 低于同表所有非子带基线 CRN 0.042 / DCCRN 0.184 / FullSubNet 0.386） |
| **跨分支类比：分组思路的两端** | [[wiki_low_latency/entities/D-GRU]]、[[wiki_low_latency/concepts/2408.12425-dynamic-gated-rnn]] | GTCRN 的 **G-DPRNN（GRNN [18]）**把输入与隐状态**固定切成 2 组**、每组用一个"参数少 2 倍"的循环层，再 **representation rearrangement** 重组。**D-GRU 的神经元级稀疏**则是**按比例 $P$ 动态挑神经元更新**。**两者是"分组"这个思路的两端**：GTCRN 是**静态、结构化、通道划分**（组数是超参，训练后固定）；D-GRU 是**动态、非结构化、按重要性选择**（比例可扫描）。**共同点**：都用"分组"降低循环层的单位算力；**共同缺口**：都不报告实际延迟（D-GRU 只有 MACs，GTCRN 连 MACs 都只有名义值） |
| **跨分支类比：TRA 与 SE-Block / 注意力池化** | [[wiki_low_latency/entities/Hybrid-Continuity-Loss]] 相关页、[[wiki_low_latency/concepts/2203.16843-continuity-loss]] | **TRA 的"能量 → 池化 → GRU → sigmoid → 乘性掩蔽"与视觉的 SE-Block 同构**，但**多了一个 GRU**——这使掩蔽**跨时间有记忆**，与 continuity loss 所关心"帧间连续性"是**同一动机的两种实现**（一个是损失层正则，一个是结构层平滑）。**GTCRN 没有报告任何连续性/平滑性指标**，因此这只停留在结构类比层面 |
| **跨分支类比：ERB 压缩的借用链** | [[wiki_low_latency/sources/2026/RT-Tango 2026]]、[[wiki_low_latency/entities/RT-Tango]] | **GTCRN 的 ERB 压缩（2 kHz 以上、192→64）被 RT-Tango 直接借用**并用于双耳场景。这条借用链说明：**GTCRN 最有生命力的部分不是它的 G-DPRNN 或 GT-Conv，而是那个 20 行的频带映射表**——因为它足够简单、足够正交，可以被搬到任何时频域模型上。**本库建议把"ERB 频带压缩"作为一个可复用算子单独建概念页**（若尚未有） |
| **同命题：MACs 不是速度** | [[wiki_low_latency/concepts/2509.21867-speed-optimized-streaming-design]]、[[wiki_low_latency/concepts/2609.29867-compute-matched-dynamic-depth]] | GTCRN **引用了 ShuffleNetV2 [17]**（= 那两页用来论证"MACs 不是速度"的同一篇）来设计 GT-Conv，**却全文没有报告任何速度**。**这是本篇在方法学上的一处结构性缺失**：它引用了"算力不是速度"的出处，却没有回应这个警告。**本库应记录为一条警示**：**引用 ShuffleNetV2 的架构论文，尤其应当报告速度** |
| **框架对照：超轻量 vs 低时延** | [[wiki_low_latency/entities/RT-SEMamba]]、[[wiki_low_latency/entities/LaCo-SENet]]、[[wiki_low_latency/concepts/严格因果与算法延迟]]、[[wiki_low_latency/concepts/低时延前端与延迟账本]] | GTCRN 与本库主流条目（2 ms 档）**不在同一约束面上**：GTCRN 优化**参数量/MACs**，那些优化**算法延迟与因果性**。**两者可以叠加**：把 GTCRN 当骨干 + 用 LaCo-SENet 的因果 padding 分配式改造 + 用 [[wiki_low_latency/concepts/2204.09911-short-asymmetric-stft]] 的短窗非对称 STFT —— 这是本库一个**尚未被做的组合实验** |
| **概念页** | [[wiki_low_latency/concepts/gtcrn-2024-ultralight-subband-grouped-dprnn]] | 抽象出"超轻量锚点的口径必须钉死""分组是三种正交压缩""补偿模块的性价比需要双坐标比较""引用 ShuffleNetV2 却不报速度""声明级因果的审计清单"五条可复用命题 |
| **实体页** | [[wiki_low_latency/entities/GTCRN]] | 架构 ASCII、参数速查、Table 1/2/3 全表、延迟账本、五段式证据边界、口径矛盾 |
| **索引** | [[wiki_low_latency/index]]、[[wiki_low_latency/overview]] | 本页应由主 agent 登记入超轻量分支与引文核对清单 |

## 7. 一句话总结"江湖地位"

> **2024 | 超轻量语音增强 / 子带-ERB 路线 / ICASSP | 用"ERB 频带压缩（2 kHz 以上 192→64，共 129 维）+ G-DPRNN（GRNN 的 2 组划分 + intra 双向/inter 单向）+ GT-Conv（ShuffleNetV2 unit + 时间膨胀深度可分离卷积，dilation 1/2/5）+ 可选的 SFE 与 TRA"把 DPCRN 压到 **23.7 K 参数 / 39.6 MMACs per second**，在 VCTK-DEMAND 上取得 **SISNR 18.83 / PESQ 2.87 / STOI 0.940**（PESQ 与 SISNR 表内最高；STOI 0.940 与 S-DCCRN 持平、低于 DeepFilterNet 0.942），在 DNS3 blind 上 **P.808 3.44 / BAK 3.90 / SIG 3.00 / OVRL 2.70**（BAK 与 OVRL 表内最高，**但 SIG 与 RNNoise 完全相同于 3.00，且两者都低于 Noisy 的 3.20**）→ 它是本库 **"超轻量"档的锚点**（被 FastEnhancer、RT-Tango、PSMSE、μNet 四篇同时引用），也是 **FastEnhancer 攻击子带路线时的靶子**；它的 ERB 频带压缩被 RT-Tango 直接借用进双耳场景，并被重配到 **4 ms hop（48.98 → 197.5 MMAC/s，约 4.03×，与帧率比 4.0× 吻合）** —— **但它自身几乎没有延迟账本**：唯一时延锚点是 **hop 16 ms**，**STFT center 未报告**、逐层 padding 未报告、时间感受野未给、**无 RTF / 无 p99 / 无目标硬件 / 无量化 / 无端侧实测**，算力证据停在**名义 MACs（本库 L0 最低级）**；因果性只有一句 `so that the causality of the model can be guaranteed`（记 **`paper-claimed-causal`**）；Table 1 的消融显示 **TRA 用 +0.56 M/s 换 SISNR +0.38，而 SFE 用 +5.16 M/s 只换 +0.23**（论文只把 TRA 与 TA 比，回避了与 SFE 的 MACs 对照）；并且**库内对它的参数量有三个互不相容的口径（23.7 K / 24 K / 48 K，其中 48 K/33 与官方实现高度吻合而无法与原文调和）**，Table 2 的 RNNoise PercepNet 的 SISNR/STOI、S-DCCRN 的 MACs **全部为空**，**全文无 limitations / future work 章节**。**
> 一句话版：**"它是本库的 23.7 K / PESQ 2.87 锚点——但锚点自己的口径有三套、延迟账本几乎是空的"**。

## 参考资料

- 本地原件：`raw/papers/low_latency_causal_se/GTCRN-ICASSP2024.pdf`（5 页；页脚 971–975；版权行 `979-8-3503-4485-1/24/$31.00 ©2024 IEEE`；DOI `10.1109/ICASSP48485.2024.10448310`）
- 本地文本抽取：`tmp/pdf_extract/gtcrn.txt`（3,697 行；**每页有 `===== PAGE N =====` 标记**）
- 页面渲染核对：`wiki_low_latency/assets/gtcrn_2024/`（`gtcrn-page1.png` ~ `gtcrn-page5.png`，150 dpi，1277×1654）。本页的核对方式：**page1**（标题 / 作者 / 三个单位 / 邮箱 / Abstract / Index Terms / 页脚版权行与页码 971）、**page2**（Fig. 1 整体架构、Fig. 2 GT-Conv、Fig. 3 SFE、Fig. 4 TRA，及 §2–§2.4 前半）、**page3**（§2.4 后段–§2.6 全文、**Eq. 1–5**、§3.1 数据集、§3.2 实现细节、页码 973）、**page4**（Fig. 5 与四组 PESQ/STOI 标注、**Table 1 七行八列**、**Table 2 六行**、**Table 3 四行与双层表头**、RNNoise 脚注 1、§3.3.1–§3.3.2、§4 结论、§5 致谢）、**page5**（References [1]–[30] 与页码 975）
- **本页额外做的核对**（用 PyMuPDF 高 dpi 裁剪 + `get_text('dict')` 坐标提取，脚本在 `tmp/gtcrn_zoom*.py`）：
  - **Eq. (1) 的括号与系数位置**（600/700 dpi 裁剪，确认论文原式为 $\alpha\mathcal L_{\text{SISNR}}+(1-\beta)\mathcal L_{\text{mag}}+\beta(\mathcal L_{\text{real}}+\mathcal L_{\text{imag}})$，**与本任务 brief 的骨架不同**）；
  - **Eq. (2)–(5) 的四个指数**（0.3 / 0.3 / 0.7 / 0.7，其中 0.7 为单位化指数而非压缩指数）；
  - **Fig. 5 的四个 PESQ/STOI 标注的 PDF 坐标**（用于确认标注与面板的归属；**复核结果：GTCRN 1.42/1.94 > RNNoise 1.16/1.28，与正文一致**，见 §4.6）；
  - **Table 3 的双层表头归属**（确认 `2.96` 属 P.808、`2.65/3.20/2.33` 属 BAK/SIG/OVRL）；
  - **Table 1 的三段分隔线**（与 SFE 列的 `✗✗✗/✓✓✓` 分组吻合）
- **本页嵌入 1 张**：`gtcrn-page2.png`（Fig. 1 整体架构 + Fig. 2 GT-Conv + Fig. 3 SFE + Fig. 4 TRA）、`gtcrn-page4.png`（Fig. 5 + Table 1 + Table 2 + Table 3 + §3.3–§5）
- 论文内关键引用：[1] CRN for real-time SE（Tan & Wang，Interspeech 2018）；[2] **DCCRN**（Hu 等，Interspeech 2020）；[3] **DPCRN**（Le 等，Interspeech 2021，pp. 2811–2815）—— **GTCRN 的 backbone**；[4] TF-GridNet（Wang 等，TASLP 2023）；[5] Wave-U-Net；[6] Conv-TasNet（Luo & Mesgarani，TASLP 2019）；[7] **DPRNN**（Luo 等，ICASSP 2020，pp. 46–50）—— **G-DPRNN 的双路径来源**；[8] TinyLSTMs（Fedorov 等，Interspeech 2020）；[9] 模型压缩（Tan & Wang，TASLP 2021）；[10] **TRU-Net**（Choi 等，ICASSP 2021，pp. 5789–5793）；[11] 高效实时 DNNS（Braun 等，ICASSP 2021，pp. 656–660）；[12] **RNNoise**（Valin，MMSP 2018）；[13] **PercepNet**（Valin 等，Interspeech 2020，pp. 2482–2486）；[14] **DeepFilterNet**（Schröter 等，ICASSP 2022，pp. 7407–7411）；[15] **DPCRN-CF**（Le 等，Interspeech 2023，pp. 3894–3898）；[16] **Inference Skipping for parallel RNNs**（Le 等，TASLP 2022，vol. 30, pp. 2411–2421）= 本库 Skip-DPCRN；[17] **ShuffleNetV2**（Ma 等，ECCV 2018，pp. 116–131）—— **GT-Conv 的 unit 来源，也是"MACs 不是速度"的出处**；[18] **GRNN**（Gao 等，NAACL 2018，pp. 799–808）—— **G-DPRNN 的分组来源**；[19] **CRM**（Williamson 等，TASLP 2015，vol. 24, no. 3, pp. 483–492）；[20] **VCTK-DEMAND**（Valentini-Botinhao 等，SSW 2016，pp. 146–152）；[21] **DNS Challenge 2021**（Reddy 等，2021）；[22] **DiDiSpeech**（Guo 等，ICASSP 2021，pp. 6968–6972）；[23] **Adam**（Kingma & Ba，CoRR 2014）；[24] **TA / Time-Frequency Attention**（Zhang 等，ICASSP 2022，pp. 7852–7856）—— **TRA 的对照臂**；[25] **SI-SDR**（Le Roux 等，ICASSP 2019，pp. 626–630）；[26] **PESQ**（Rix 等，ICASSP 2001，vol. 2, pp. 749–752）；[27] **STOI**（Taal 等，ICASSP 2010，pp. 4214–4217）；[28] **S-DCCRN**（Lv 等，ICASSP 2022，pp. 7767–7771）；[29] **DNSMOS P.808**（Reddy 等，ICASSP 2021，pp. 6493–6497）；[30] **DNSMOS P.835**（Reddy 等，ICASSP 2022，pp. 886–890）
- 开源代码：[https://github.com/Xiaobin-Rong/gtcrn](https://github.com/Xiaobin-Rong/gtcrn)（§3.3.2 正文给出；**本页未克隆核实**，因 `evidence_policy: local_pdf_only`）

> [!question] 待核实（本页留给主 agent 与后续读者的清单）
> **(1) 参数量口径矛盾**：原文 **23.7 K / 39.6 MMACs per second**（内部自洽，对应 Table 1 最后一行）vs μNet 的 **48 K / 33** vs FastEnhancer 的 **24 K / 40**。**24 K/40 可解释为四舍五入；48 K/33 无法解释**（参数 2.03×、MACs 0.83×，方向相反）。建议**直接核查 `https://github.com/Xiaobin-Rong/gtcrn` 的 README 与模型定义**。本页无法做（无网络）。
> **(2) 页码定案**：本页已用**论文自身页脚**（971/972/973/974/975）判定 **pp. 971–975 正确**，[[wiki_low_latency/sources/2026/Early Exit Compute-Matched 2026]] 引文 [2] 的 10286–10290 为误著录。**建议在该页的 `[!question]` 上追加定案**（本页不改动该文件）。
> **(3) STFT center 未报告** —— 本页**一等缺口**。若 `center=True`，前端含 16 ms 未来样本，算法延迟下界从 16 ms 变 32 ms，因果判定需下调。
> **(4) 逐层 padding 未报告**（Conv / DeConv / P-Conv2D / DD-Conv2D 全部）——因果性的直接判据缺失。
> **(5) DD-Conv2D 的时间感受野未给**。本页推得 kernel 时间维 3、dilation 1/2/5 ⇒ 单块 **3/5/11 帧**、三条链累计 **17 帧**（若左对齐），但**这是本页的推算，论文未给**。若用 `same` padding 则含未来帧。
> **(6) 参数量增量归属未报告**：Table 1 中 `✗/✗/✗ → ✗/✗/✓` 的参数从 13.35 K 涨到 21.65 K（**+8.30 K**），而 SFE 只涨 2.02 K。**但论文未明确这 8.30 K 是否全部属于 TRA**（可能含全连接/归一化的连带变化）。
> **(7) Fig. 5 的标注归属需坐标复核**（本页 §4.6）—— 初稿曾误判为"标注放反、与正文矛盾"，**经 600 dpi 单面板裁剪二次确认后已改正：GTCRN 在 1.42/1.94 两处均高于 RNNoise 的 1.16/1.28，与正文方向一致**。此处仅作为"PDF 文本流丢失面板标签时的复核方法"记录，**不再是论文缺陷**。
> **(8) TA [24] 的结构未描述**：Table 1 的第三列对照臂在本篇内是黑箱，无法判断结论是对"时间维注意力"这一类的评价还是仅对 [24] 该实现的评价。
> **(9) 论文承诺了却未给的数据**：Table 2 的 RNNoise/PercepNet 的 SISNR 与 STOI（空格）、Table 3 的 S-DCCRN 的 BAK/SIG/OVRL（空格）、DPCRN 的参数量（全文未给）、训练总 epoch 数、随机种子数、GRU 隐层维度、DPRNN chunk 长度。
> **(10) 无种子、无方差**：Table 1/Table 3 有若干 `+0.01` 量级的结论（PESQ 1.89→1.91、P.808 3.43→3.44），**均无法判断显著性**。
