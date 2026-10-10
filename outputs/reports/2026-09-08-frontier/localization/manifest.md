---
title: 2026-09-08 声源定位前沿论文包清单
type: report
created: 2026-09-08
updated: 2026-09-08
tags:
  - sound-source-localization
  - doa
  - frontier-papers
---

# 声源定位前沿论文包（5 篇）

检索截止日期为 **2026-09-08**。筛选优先级是：与麦克风阵列声源/说话人定位直接相关、2026 年最新进展、方法或评测问题具有新意、官方来源可核验且可取得全文。检索前已读取 `CLAUDE.md`、`wiki_array/index.md` 与 `raw/` 论文清单；以下 5 篇在本轮开始时均未被项目收录。这里的“前沿”表示选题和方法较新，**不等同于已经被独立复现的 SOTA**；所有性能措辞均限于论文自己的实验设置。

## 文件完整性

| # | PDF | 可读全文 | 页数 | 官方全文来源 |
|---|---|---|---:|---|
| 1 | `01_neuralmusic_2606.18664v3.pdf` | 同名 `.html`、`.txt` | 13 | arXiv |
| 2 | `02_sff_multispeaker_doa_2606.17258v1.pdf` | 同名 `.html`、`.txt` | 34 | arXiv |
| 3 | `03_sarl_benchmark_2606.05544v2.pdf` | 同名 `.html`、`.txt` | 5 | arXiv |
| 4 | `04_vine_robot_acoustic_localization_2607.20392v1.pdf` | 同名 `.html`、`.txt` | 8 | arXiv |
| 5 | `05_fault_resilient_tta_ieee_access_2026.pdf` | 同名 `.txt` | 24 | IEEE Xplore（开放获取） |

所有 PDF 已用 `pypdf` 成功打开并逐页提取文本；`.txt` 中保留 `===== PDF page N =====` 分页标记，便于笔记回查。4 份 arXiv HTML 是官方实验性全文，公式通常比 PDF 文本抽取更可靠。第 5 篇以正式出版 PDF 为准。

## 1. NeuralMUSIC

**精确题目**：*NeuralMUSIC: A Hybrid Neural-Subspace Framework for Robot Sound Source Localization*  
**作者**：Yizhuo Yang, Junqiao Fan, Shenghai Yuan, Lihua Xie  
**日期与状态**：arXiv v1 2026-06-17；本地保存 v3，2026-07-08；论文页注明 accepted by IROS 2026。  
**官方链接**：[摘要](https://arxiv.org/abs/2606.18664)｜[PDF v3](https://arxiv.org/pdf/2606.18664v3)｜[HTML v3](https://arxiv.org/html/2606.18664v3)  
**代码**：[yizhuoyang/NeuralMUSIC](https://github.com/yizhuoyang/NeuralMUSIC.git)

**入选理由**：把神经网络用于宽带空间协方差估计，同时保留 MUSIC 的 EVD、噪声子空间与伪谱结构；再加入未知源数预测、Frequency Attention Fusion（FAF）和利用无标签多通道录音的 SSCL。它直接针对机器人环境中的低 SNR、混响、跨房间和跨阵列泛化，兼顾物理可解释性和数据效率。

**供精读的公式/结果锚点**：

- PDF p.3-4，Eq. (13)-(14)：网络回归复空间协方差矩阵，并以 `(R + R^H)/2` 强制 Hermitian；Eq. (17) 是在估计噪声子空间上的 MUSIC 伪谱。
- PDF p.4，Eq. (19)-(21)：FAF 从各角度的频率谱得到注意力权重，并作加权宽带谱融合；Eq. (22)-(25) 是 Gaussian 角度目标、DOA MSE、源数交叉熵和总损失。
- PDF p.5，Table I：在作者测试的 GSC/AV16.3/单源任务中，本文行的 MAAE 分别为 `1.41/2.25/2.14`、`7.64/11.17/13.51`、`2.91/10.24` 度；须按数据集和已知/未知源数列理解，不能跨设置概括成统一 SOTA。
- PDF p.7-8，Table III-IV：跨房间和跨阵列迁移；适合核查“泛化优于纯神经基线”的适用范围。PDF p.11-12，Table V-VI：稀疏训练角度与少量训练数据下的补充结果。

## 2. SFF-PHAT-env 多说话人双麦 DOA

**精确题目**：*Single frequency filtering based multi-speaker direction of arrival estimation from stereo recordings*  
**作者**：Sushmita Thakallapalli, Sudarsana Reddy Kadiri, Nilesh Madhu, Suryakanth V. Gangashetty  
**日期与状态**：arXiv v1，2026-06-15；摘要页未列正式会议/期刊，按预印本记录。  
**官方链接**：[摘要](https://arxiv.org/abs/2606.17258)｜[PDF v1](https://arxiv.org/pdf/2606.17258v1)｜[HTML v1](https://arxiv.org/html/2606.17258v1)  
**代码**：论文和 arXiv 页面未提供代码仓库；实验使用公开 SiSEC 与 LOCATA 真实房间录音。

**入选理由**：它没有简单堆叠深网，而是重新利用语音产生中的激励源结构。SFF 同时强调谐波的高频率分辨率与 epoch-like 激励的高时间分辨率；提出的 SFF-PHAT-env 对双通道同频 envelope 作 PHAT 加权相关，再跨频聚合，目标是增强噪声和混响中的多说话人 DOA 稳健性。

**供精读的公式/结果锚点**：

- PDF p.5，Eq. (1)-(3)：远场几何下 TDOA 与 DOA 的关系；注意该文主要实验是固定间距双麦，且假设源数已知。
- PDF p.9-10，Sec. 5.1、Eq. (11)-(13)：`J_SFF-PHAT-env` 的逐频 envelope GCC-PHAT、跨频求和与逐帧 `arg max`；最终从帧级 DOA 直方图取多个峰。
- PDF p.24-25，Table 4：SiSEC 上 SFF-PHAT 为 F=1.00、MAE=0.78°、MAE_fine=0.77°；提出的 SFF-PHAT-env 为 1.00、0.79°、0.77°，GCC-PHAT 为 0.97、1.33°、0.83°。LOCATA 高混响下 SFF-PHAT MAE 10.65°，GCC-PHAT 12.44°，但 GCC-PHAT 的 F-measure/检测比例更高，结论需保留这一取舍。
- PDF p.26-28，Table 5：加入 white/babble/machine-gun/volvo/factory noise 后的完整比较；PDF p.30，Table 6：speech-dominant-bin 加权 GCC-NMF 与最佳 SFF/GCC 方法的比较。作者结论是“superior or comparable”，不是所有指标都全面领先。

## 3. SARL 空间音频表征探测基准

**精确题目**：*Probing Spatial Structure in Pretrained Audio Representations*  
**作者**：Chuyang Chen, Sivan Ding, Adrian S. Roman, Juan P. Bello  
**日期与状态**：arXiv v1 2026-06-04；本地保存 v2，2026-07-16；accepted to Interspeech 2026。  
**官方链接**：[摘要](https://arxiv.org/abs/2606.05544)｜[PDF v2](https://arxiv.org/pdf/2606.05544v2)｜[HTML v2](https://arxiv.org/html/2606.05544v2)  
**代码与数据**：[chuyangchencd/SARL](https://github.com/chuyangchencd/SARL)

**入选理由**：这是“空间预训练模型到底编码了什么”的可复现诊断基准，而不是新的端到端定位器。它用统一线性 probing 分离模型表征质量与下游架构影响，覆盖 azimuth、elevation、distance、class、RT60、room volume、shape，并比较 mono/stereo/binaural/FOA 以及自监督、监督、codec 训练范式。对后续选择定位基础模型和输入格式很有价值。

**供精读的公式/结果锚点**：

- PDF p.2，Sec. 3.3：连续任务分箱（azimuth 36、elevation 12、distance 20、RT60 29），分数为 `1 - MAE/R`；聚合时用 `phi(x;b)=(x-b)/(1-b)` 将随机基线映射到 0。
- PDF p.2-3，Sec. 3.4：以只改变 source 或 room 因素的配对场景，用冻结 embedding 的余弦距离衡量 sensitivity。
- PDF p.3，Fig. 1：逐任务 probing 热图；PDF p.4，Fig. 2：source semantic、localization、room 三组归一化结果。全文支持的稳健趋势是 source 因素普遍比 room 因素易解码，FOA 整体较强，监督 SELD 模型在 azimuth 强但 room 因素弱，自监督模型更均衡；不要把图中单一模型排序外推为真实定位 SOTA。
- PDF p.4-5，Fig. 3-4：表征对 source/room perturbation 的敏感性及其与 probing 性能的相关性；这是本文的主要诊断证据。

## 4. 软体藤蔓机器人分布式声定位

**精确题目**：*Distributed Acoustic Localization Array Deployed Using a Soft Everting Vine Robot*  
**作者**：Sebastian Lorca Godoy, Ciera McFarland, Michael Val, Antonio Alvarez Valdivia, Nathaniel Hanson, Margaret McGuinness  
**日期与状态**：arXiv v1，2026-07-22；摘要页注明将发表于 IEEE IROS 2026。  
**官方链接**：[摘要](https://arxiv.org/abs/2607.20392)｜[PDF v1](https://arxiv.org/pdf/2607.20392v1)｜[HTML v1](https://arxiv.org/html/2607.20392v1)  
**代码**：论文和 arXiv 页面未提供代码仓库。

**入选理由**：把阵列几何从固定硬件扩展到随 soft everting vine robot 生长而部署的动态、可变形分布式阵列，在同一 SRP-PHAT 框架中切换远场 DOA 与近场 3D/位置搜索。其贡献重点在传感器部署、安装位置、阵列形状、SNR、距离和逐步增加麦克风数的系统实验，适合灾后狭窄空间搜救场景。

**供精读的公式/结果锚点**：

- PDF p.3，Eq. (1)-(4)：麦克风对 GCC-PHAT、候选位置理论 TDOA、所有麦克风对累加的 SRP-PHAT functional，以及在候选网格上取最大值。
- PDF p.4-5，Fig. 4-5：安装位置与 SNR。远场 SNR>0 dB 时 pressurized-body/wall 平均方位误差约 0.51°/1.49°；近场 wall-mounted 平均位置误差 0.17 m，tail 约 2.3 m 饱和，说明安装声学路径会显著改变结果。
- PDF p.5-6，Fig. 6-7：阵列形状。圆阵远场平均方位误差 1.1°（单 fiber 45.9°），近场平均位置误差 0.034 m（double fiber 0.083 m、sinusoidal 0.079 m）。
- PDF p.6-7，Fig. 8-9：距离和逐步部署。0.5 m 时平均误差 0.03 m；两麦到三麦时从约 2.4 m 降至 0.216 m（91.0%），四/五麦在该特定几何上未单调继续改善。作者也指出 1.5 m 外范围估计方差很高，不能只看平均误差。

## 5. 面向麦克风故障的置信度测试时自适应

**精确题目**：*Confidence-Aware Test-Time Adaptation for Fault-Resilient Sound Source Localization Guided by Lightweight Diagnosis*  
**作者**：Inkyu An  
**日期与状态**：received 2026-03-26，accepted 2026-04-09，published 2026-04-16，current version 2026-04-22；IEEE Access, Vol. 14, pp. 60569-60592。DOI `10.1109/ACCESS.2026.3684240`，正式发表、CC BY 4.0。  
**官方链接**：[DOI](https://doi.org/10.1109/ACCESS.2026.3684240)｜[IEEE Xplore document 11482118](https://ieeexplore.ieee.org/document/11482118/)｜[官方 PDF](https://ieeexplore.ieee.org/stampPDF/getPDF.jsp?tp=&arnumber=11482118)  
**代码**：论文与 IEEE 页面未提供代码仓库。

**入选理由**：研究深度定位器在真实硬件故障下的在线恢复，而不是只做干净阵列精度。轻量 Frequency-Time Projection 诊断网络与 Fault Queue 先识别 no sound、attenuation、impulsive/continuous noise、signal replication，再由故障语义指导干预，并用动态置信阈值、hard pseudo-label 与 test-time self-training 无标签适配。

**供精读的公式/结果锚点**：

- PDF p.6-8，Sec. IV-A：故障诊断网络与 Fault Queue；PDF p.9，Eq. (8) 给出置信峰、置信静默和 uncertainty mask 的统一伪标签逻辑。
- PDF p.10，Eq. (9)：按 batch、序列步和有效角度 bin 归一化的 masked MSE 自训练目标；Eq. (10)-(11) 是 dominant-peak batch confidence 与 EMA 动态阈值。
- PDF p.15，Table 3：三种 SSL 模型、五种故障的 Before TTA/TENT/soft pseudo-label/本文/oracle。本文把跨模型跨故障平均 MAE 从 21.99° 降至 9.91°（摘要给出的总体汇总）；例如 MPT-HiFTA 的平均 MAE 11.83°→4.88°，GCC-PHAT-SM 24.10°→12.94°。
- PDF p.18，Table 4：动态阈值与伪标签组件消融；PDF p.22，Table 8：拔掉真实四麦阵列的一路，故障检测 100%，MAE 29.20°→16.57°、accuracy 61.48%→70.66%，仍低于无故障基线 9.54°/82.33%，体现恢复上限。

## 已比较但未入选

- *Bayesian direction-of-arrival estimation for moving sound source in high-interference environments*（JASA, 2026-07-01, DOI `10.1121/10.0044368`）：日期和方法很强，但本轮只能稳定取得摘要，无法取得可落盘的开放全文，因此不占 5 篇名额。
- *End-to-End 3-D Sound Source Localization from the Raw Waveform Based on Stereo Microphone Array*（Sensors, 2026-04-12, DOI `10.3390/s26082372`）：开放 XML 可读，选题相关；与已选的 2026-04 IEEE 故障自适应相比，后者更聚焦部署中的新问题，故作为备选保留。
- *Multichannel Acoustic Beamforming for Speaker Localization and DOA-Based Tracking*（Electronics, 2026-08-01）：更新，但主要是 GCC-PHAT + DAS + smoothing 的嵌入式工程整合；没有为了日期而替换方法更具新意的论文。
- *Entropy-Based Geometry Design for SRP-PHAT Acoustic Source Localization*（IEEE SPL, 2026-03-19, DOI `10.1109/LSP.2026.3675914`）：阵列熵优化值得关注，但日期较早且开放全文取得不如本包稳定。

