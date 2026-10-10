# 2026-09-08 语音增强前沿论文检索清单

检索口径：截至 2026-09-08；先检查 `CLAUDE.md`、`wiki/index.md` 与 `raw/papers/` 去重。以下五篇均不在原始论文清单中，PDF 与 HTML 均来自 arXiv 官方全文端点。排序按 arXiv 首次提交时间；“SOTA”只保留作者在其评测范围内的主张，不外推为全领域结论。

## 1. U-PAST: A Phase-Aware Audio Spectrogram Transformer-U-Net for Single-Channel Speech Enhancement

- arXiv: 2609.00431v1；提交：2026-08-31 22:08:36 UTC（arXiv 月份编号为 2609）；状态：预印本，arXiv 页面未注明已接收会议。
- 作者：Cao Duong Ly; Jörn Anemüller。
- 官方页：https://arxiv.org/abs/2609.00431
- PDF：https://arxiv.org/pdf/2609.00431
- 官方 HTML：https://arxiv.org/html/2609.00431
- 代码：论文和 arXiv 页面未给出官方代码仓库（截至检索日）。
- 本地：`2609.00431_U-PAST.pdf`；`2609.00431_U-PAST.html`。
- 选题理由：最新一批工作中少见的复数 STFT tokenization + Transformer encoder + U-Net decoder；1.17M–2.40M 参数，并专门比较 matched、声学失配和数据集失配，兼顾相位与小模型泛化。
- 笔记定位：方法公式/定义见 HTML §3.1（complex-valued AST encoder/tokenization）与 §3.2（decoder 和 complex spectrogram reconstruction）；结构与复杂度见 Table 1–2；主结果见 Table 3–6。结论报告 U-PAST-H 在 DNS reverb 声学失配下 SI-SDR 9.76 dB；其余三条件比作者所测最强 TF-GridNet 低 1.62–2.44 dB，避免写成全面 SOTA。

## 2. Towards Balanced Spectral Reconstruction: Spectrally Adaptive Loss for Streaming Speech Enhancement

- arXiv: 2608.30739v1；提交：2026-08-31 13:08:26 UTC；状态：作者注明 Accepted by IWAENC 2026。
- 作者：Haixin Zhao; Nilesh Madhu。
- 官方页：https://arxiv.org/abs/2608.30739
- PDF：https://arxiv.org/pdf/2608.30739
- 官方 HTML：https://arxiv.org/html/2608.30739
- 代码：未发现官方代码仓库；作者提供官方演示页：https://aspire.ugent.be/demos/IWAENC2026HZ/
- 本地：`2608.30739_Balanced-Spectral-Reconstruction.pdf`；`2608.30739_Balanced-Spectral-Reconstruction.html`。
- 选题理由：创新点直接落在训练目标，针对 phase-aware compressed loss 导致中高频过衰减，提出 sigmoid-weighted 与 signal-dependent spectrally adaptive 两种 STFT loss；同时给出低延迟 HyST-Net 骨干，适合实时增强专题。
- 笔记定位：关键损失及频率/信号依赖权重见 HTML §2.1；HyST-Net 见 §2.2；轻量流式基线比较见 Table 1，两个新损失的消融结果见 Table 2。重点核对频段重建改善与整体 PESQ/STOI/DNSMOS 的关系，不把频谱更平衡等同于所有指标都最优。

## 3. μNet: Ultra-Low-Memory and Low-Complexity Speech Enhancement for Embedded Digital Signal Processors

- arXiv: 2608.21155v1；提交：2026-08-21 14:27:52 UTC；状态：arXiv 预印本；PDF 页眉标注 2026 APSIPA ASC，arXiv 页面本身未声明接收状态。
- 作者：Shrishti Saha Shetu; Jose Miguel Martinez Aponte; Nagashree K. S. Rao; Sharvin Vittappan; Oliver Thiergart; Emanuël A. P. Habets。
- 官方页：https://arxiv.org/abs/2608.21155
- PDF：https://arxiv.org/pdf/2608.21155
- 官方 HTML：https://arxiv.org/html/2608.21155
- 代码：未发现官方代码仓库；作者演示页：https://sshetu-iis.github.io/uNet/ulm/
- 本地：`2608.21155_muNet.pdf`；`2608.21155_muNet.html`。
- 选题理由：把 90 KB 静态内存、28 MMACs、最低 4 ms 算法延迟、int8 全整数运算与可控噪声衰减放在同一嵌入式方案中，工程前沿性强。
- 笔记定位：模型与 shared subband 设计、noise attenuation level / perceptual factor 定义见 HTML §2；DNS 非混响结果与复杂度见 Table 1；float32/int8 在不同算法延迟下的量化影响见 Table 2。摘要数值是作者报告的资源占用；性能应限定为“与相近复杂度方法相当”。

## 4. Cloud-Boosted Low-Compute Multi-Channel Speech Enhancement

- arXiv: 2608.07423v1；提交：2026-08-07 17:11:35 UTC；状态：作者注明 Accepted to Interspeech 2026。
- 作者：Xulin Fan; Juan Azcarreta; Ashutosh Pandey; Jesus Alvarez; Ke Tan; Jacob Donley; Ritwik Giri; Buye Xu。
- 官方页：https://arxiv.org/abs/2608.07423
- PDF：https://arxiv.org/pdf/2608.07423
- 官方 HTML：https://arxiv.org/html/2608.07423
- 代码：论文和 arXiv 页面未给出官方代码仓库（截至检索日）。
- 本地：`2608.07423_Cloud-Boosted-MCSE.pdf`；`2608.07423_Cloud-Boosted-MCSE.html`。
- 选题理由：区别于单模型压缩，把允许通信延迟的云端 SpatialNet 与边端 TinyGRU 协同，结合 delayed server output、逐层 FiLM feature boosting 和 collaborative multichannel Wiener filtering，覆盖多通道与端云系统路线。
- 笔记定位：三项机制见 HTML §2.3–§2.5；FiLM 的 scale/shift 公式在 §2.4；协同 MCWF 的协方差融合/波束形成公式在 §2.5；完整消融在 Table 1。作者报告 64 ms 云边延迟下，相对 edge baseline，Standard/Challenging SI-SDR 分别提高 3.77/3.49 dB，边端仅增加 1.5% 参数与 2.4% 计算量；结论限定于其模拟条件。

## 5. FlowSE-GRPO: Training Flow Matching Speech Enhancement via Online Reinforcement Learning

- arXiv: 2601.16483v1；提交：2026-01-23 06:26:32 UTC；状态：作者注明 Accepted by ICASSP 2026。
- 作者：Haoxu Wang; Biao Tian; Yiheng Jiang; Zexu Pan; Shengkui Zhao; Bin Ma; Daren Chen; Xiangang Li。
- 官方页：https://arxiv.org/abs/2601.16483
- PDF：https://arxiv.org/pdf/2601.16483
- 官方 HTML：https://arxiv.org/html/2601.16483
- 代码：论文和 arXiv 页面未给出官方代码仓库；检索到的第三方个人复现不列为官方代码。
- 本地：`2601.16483_FlowSE-GRPO.pdf`；`2601.16483_FlowSE-GRPO.html`。
- 选题理由：虽早于其余四篇，但方法创新性最高之一：首次把在线 GRPO 后训练接入 flow-matching speech enhancement，研究连续时间序列/SDE 采样与 reward hacking，并以多指标奖励缓解单指标过优化。
- 笔记定位：flow-matching 速度场和训练损失见 HTML §2.1；ODE 转 SDE、GRPO loss 与训练窗口见 §2.2；多指标 reward 定义见 §2.3；DNS2020 结果见 Table 1–2。作者报告 GRPO 用 5k steps，相比 DPO 20k steps，在 No-Reverb/With-Reverb DNSMOS OVRL 上分别提升 0.176/0.274；同时必须记录单指标奖励会损伤其他维度的 reward-hacking 现象。

## 文件完整性

- 5 个 PDF 均可由 `pypdf` 打开并抽取首页文本，页数依次为：FlowSE-GRPO 5 页、Cloud-Boosted 5 页、μNet 6 页、Balanced Spectral 5 页、U-PAST 12 页。
- 5 个 HTML 均为 arXiv 官方实验性全文；公式保留 MathML/TeX annotation，表格与图题可搜索，适合笔记 agent 精读。
