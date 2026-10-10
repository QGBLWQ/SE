---
title: Integrating Uncertainty into Neural Network-based Speech Enhancement
type: source
created: 2026-09-16
updated: 2026-09-16
tags:
  - speech-enhancement
  - single-channel
  - time-frequency
  - uncertainty
  - aleatoric-uncertainty
  - epistemic-uncertainty
  - Bayesian-deep-learning
  - Wiener-filter
  - AMAP
  - low-latency-audit
source_type: paper
paper_id: 2305.08744
year: 2023
authors:
  - Huajian Fang
  - Dennis Becker
  - Stefan Wermter
  - Timo Gerkmann
venue: "arXiv preprint v1; formal venue 未报告"
pdf_pages: 12
local_pdf: raw/papers/low_latency_causal_se/2305.08744.pdf
related:
  - [[wiki_low_latency/entities/Uncertainty-Aware-SE]]
  - [[wiki_low_latency/concepts/2305.08744-uncertainty-aware-suppression]]
  - [[wiki_low_latency/sources/2023/GCFSnet 2023]]
  - [[wiki_low_latency/sources/2023/FSB-LSTM 2023]]
  - [[wiki_low_latency/entities/Noise-Suppression-Losses]]
  - [[wiki_low_latency/concepts/2111.11606-speech-distortion-losses]]
---

~~~yaml
- 论文: [Integrating Uncertainty into Neural Network-based Speech Enhancement](2023)
  ├── 要解决什么问题: 单通道时频监督增强通常只给一个点估计，遇到未充分覆盖的声学输入时缺少与误差相关的可靠性信号
  ├── 核心方法: 复高斯语音后验同时估计 Wiener filter 与 aleatoric variance；用 AMAP 幅度估计显式把 variance 写入抑制器；用 MC dropout/Deep ensembles 估计 epistemic uncertainty
  ├── 属于哪个分支: 单通道时频语音增强 / 概率化抑制 / Bayesian deep learning / 质量与可靠性基线
  ├── 输入/输出: noisy complex STFT X 的幅度 |X| → U-Net → W^WF 与 λ；WF 或 AMAP 幅度 + noisy phase → iSTFT → 增强波形
  ├── 关键trick: 把不确定性从离线诊断量变成 posterior NLL 与 AMAP gain 的显式变量，并用 ensemble 合并 aleatoric 与 epistemic
  ├── 数据集: DNS Challenge 训练子集 100 h；DNS reverb-free test；WSJ0 si_et_05 + CHiME3 四类噪声；16 kHz
  ├── 对比了谁: Baseline WF、Baseline SI-SDR、Aleatoric-WF/MAP、MC dropout、Deep ensembles、DE-Aleatoric-WF/MAP
  ├── 论文内最佳 DNS test: DE-Aleatoric-AMAP，PESQ=2.83+/-0.10、ESTOI=0.92+/-0.01、SI-SDR=17.90+/-0.78 dB
  ├── 参数量与实时性: 参数量、MAC/s、FLOPs、RAM、RTF、硬件平台、p99 deadline 均未报告；整体 uncertainty 分析用 M=16
  ├── 消融关键发现: 联合 aleatoric+epistemic 的 AUSE=0.067，低于单独 aleatoric=0.110 和 epistemic=0.094；AMAP 比同模型 WF 的 PESQ 更高
  ├── 遗留问题(本方向机会): 32 ms Hann/50% overlap、时间 kernel=5/padding=2 的 U-Net 没有 strict-causal、streaming、端到端时延或人声误抑制证据
  └── 跟哪篇像: [[wiki_low_latency/sources/2023/GCFSnet 2023]] 将辅助信息放在估计器支路；[[wiki_low_latency/sources/2023/FSB-LSTM 2023]] 则是低时延结构对照
~~~

# Integrating Uncertainty into Neural Network-based Speech Enhancement

> Huajian Fang、Dennis Becker、Stefan Wermter、Timo Gerkmann；PDF 标题页标注 arXiv:2305.08744v1 [eess.AS]，日期为 15 May 2023。本文只把本地 raw PDF 作为论文证据。

> [!warning] PDF 抽取质量 warning
> 原 PDF 共 12 页。Poppler 渲染时报告缺少 Symbol 与 ArialUnicode 显示字体，但相关页面的字、图和表仍可视觉辨认。已有文本抽取对希腊字母、上下标、帽子/波浪符号和数学公式存在乱码、错序或丢失；参考文献页也会混入抽取流。该公式在当前 Markdown 中无法可靠识别，需要查看原 PDF 或重新 OCR。下文 Eq. (1)-(16)、Figure 1/2、Figure 8、Table I/II 已按原 PDF 第 3-10 页视觉核对；嵌入的 PNG 是原 PDF 页面渲染，不是 AI 重画。

## 1. 他们为什么这么做？（motivation）

### 1.1 任务背景

论文研究的是**单通道监督语音增强**：带噪语音经 STFT 转到时频域，网络从 noisy-clean speech pairs 学习乘性滤波器，以恢复 clean speech。作者指出，常规 supervised masking 通常对每个输入只给一个点估计；当输入包含训练数据没有充分覆盖的噪声或声学条件时，点估计没有同时给出“这次预测有多可靠”的量。

论文把预测不确定性分成两类：

- **Aleatoric uncertainty**：来自语音和噪声随机性的 data uncertainty；在本文的复数 clean-speech posterior 中体现为方差。
- **Epistemic uncertainty**：来自网络参数本身的不确定性；不同参数样本会给出不同 clean-speech estimates。

论文的动机不是把 U-Net 做成一个低时延系统，而是让增强器在没有 ground truth 的推理时刻也能输出与误差相关的可靠性信号，并且让这份信号真正参与语音幅度估计。

### 1.2 论文目标

论文要同时回答三个问题：

1. 能否用复高斯语音后验让网络学习逐时频 bin 的 Wiener filter 与 aleatoric variance？
2. 能否把 variance 写进 AMAP（approximate maximum a posteriori）幅度估计，让高不确定度时减少目标过抑制？
3. 能否用 MC dropout 与 Deep ensembles 估计 epistemic uncertainty，并用 law of total variance 合并两种来源？

因此，这篇论文在本库中的角色是“**不确定性感知的质量/可靠性基线**”：它对低时延方向有一个重要接口启示——让辅助置信度调制 suppression——但论文没有把系统验证为 strict-causal 端侧模型。

## 2. 之前的人怎么做不了？（limitation → gap）

### 2.1 既有路线的缺口

| 路线 | 能做到什么 | 论文问题意识中的缺口 |
|---|---|---|
| 统计 MMSE/Wiener 估计 | 在 speech/noise 统计假设下构造滤波器 | 需要估计统计量；难以直接表达复杂未见场景中的逐 bin 可靠性 |
| 普通 supervised masking | 由 noisy-clean pairs 直接学习时频乘性滤波器 | 通常只输出点估计；错误结果不一定伴随可用的不确定性 |
| 固定方差的 MSE 训练 | 训练稳定、目标明确 | 将所有时频 bin 视作同一误差尺度，不能学习 data-dependent variance |
| 只用 NLL 学异方差 | 可以让方差进入 posterior | 论文指出直接最小化 posterior negative log loss 可能过拟合，并影响均值/Wiener estimate 的训练 |
| 单模型点估计 | 推理成本较低 | 无法表示网络参数的 spread，不能刻画 epistemic uncertainty |
| MC dropout/Deep ensembles 的常规 Bayesian 用法 | 可用多个参数样本产生预测分布 | 论文将其引入语音增强 uncertainty 分析，并比较其可靠性与增强收益；这里不把外部文献数字带入本页 |

### 2.2 研究 gap

论文把 gap 压缩成一个耦合设计：一方面需要通过 posterior distribution 学到“这个时频估计可能错多少”，另一方面需要让 uncertainty 改变 clean-speech estimation，而不是只在结果旁边画 heatmap；若还要得到 overall predictive uncertainty，则需要再处理 model parameter uncertainty。

论文的解决路线是：

~~~text
complex Gaussian speech-plus-noise assumption
  → Wiener mean + posterior variance λ
  → posterior NLL regularized by waveform SI-SDR
  → AMAP magnitude estimator uses W^WF and λ
  → MC dropout / Deep ensembles estimate epistemic spread
  → law of total variance combines both sources
~~~

### 2.3 strict-causal 与 latency ledger

| ledger 项目 | PDF 直接证据 | 低时延审计结论 |
|---|---|---|
| 任务/系统声明 | 论文研究 single-channel speech enhancement；未声明 causal、streaming 或 real-time | 不能标为论文已验证的 strict-causal 系统 |
| 采样率 | noisy-clean pairs 为 16 kHz | 已报告 |
| STFT 窗与重叠 | 32 ms Hann window，50% overlap | 帧移可由 50% 计算为 16 ms；这不是论文报告的端到端算法延迟 |
| FFT size | 未报告 | 不可补写 |
| STFT 对齐/center/边界 | 未报告 | 无法从 32 ms/16 ms 确定 look-ahead 或 group delay |
| 网络输入时间范围 | U-Net 输入维度写为 (T,F)；未给 chunk、warm-up 或 state contract | 不是可复现的 batch=1 流式接口 |
| 时间卷积 | kernel=(5,5)、stride=(1,2)、padding=(2,2) | 论文没有 causal padding 说明；按通常对称 padding 解读会有未来帧风险，这是结构审计推断，不是论文测量 |
| 网络状态/缓存 | 未报告 state、cache、reset、overlap-save 或长流处理方式 | strict-causal certificate 缺失 |
| nominal algorithmic latency | 未报告 | 不能把 window、hop 或一次 forward 直接写成系统时延 |
| 参数量/计算量 | 参数量、MAC/s、FLOPs、峰值 RAM、量化均未报告 | 无模型预算证据 |
| uncertainty 推理次数 | Figure 6/7 分析 M∈{2,4,8,16,32}；overall predictive uncertainty 取 M=16；论文只说计算时间随 M 增大而显著增加 | 多次 forward 的成本方向明确，但没有时间数值 |
| RTF/硬件 | 未报告 CPU/DSP/NPU/SoC、batch=1 wall-clock、RTF、能耗 | 不能声称 RTF<1 |
| deadline | 未报告 p50/p95/p99、deadline miss、overrun/underrun、capture-to-playback | 无 deadline 通过证据，也没有 ADC/DMA/I/O/DAC 端到端账本 |

> [!question] 低时延证据边界
> 本文可以作为 uncertainty-aware suppression 的方法基线，但不能认证为约 2 ms 或任意端到端低时延模型。32 ms 窗、U-Net 的时间 kernel/padding、未定义的 STFT 对齐和可能的 M=16 多次推理，都需要在严格因果目标上重新设计与实测。

## 3. 这个做法核心 trick 是什么？

### 3.1 任务、输入、输出与整体管线

论文在公式层面把带噪、目标语音和噪声的复数 STFT 写成：

$$
X_{ft}=S_{ft}+N_{ft}. \tag{1}
$$

其中 f 是频率 bin，t 是时间帧；X、S、N 分别是 mixture、clean speech 和 additive noise 的复数谱系数。目标是在时频域估计 clean speech，再通过 iSTFT 得到波形。

论文的实际 DNN 输入是 noisy complex STFT 的幅度 |X|，而不是把复数的实部和虚部直接送进 U-Net：

~~~text
noisy speech x
  → STFT X → magnitude |X| → U-Net
                                  ├─ W^WF_ft
                                  └─ λ_ft > 0
  → W^WF_ft |X_ft| 或 W^AMAP_ft |X_ft| + noisy phase
  → iSTFT → estimated waveform ŝ
~~~

| 项目 | 论文内容 | 证据边界 |
|---|---|---|
| 任务 | single-channel supervised speech enhancement | 论文直接报告 |
| 输入 | X_ft 的幅度 | 论文的 architecture description 直接报告 |
| 主要输出 | multiplicative Wiener filter W^WF_ft | 论文直接报告 |
| aleatoric 输出 | posterior variance λ_ft；网络输出其 logarithm，再以 exponential 恢复为正值 | 论文直接报告 |
| WF 输出 | 复数 posterior 的 clean estimate 使用 W^WF_ft X_ft | 公式直接给出 |
| AMAP 输出 | AMAP 估计的幅度与 noisy phase 合成后 iSTFT | 论文直接报告 |
| 时域目标 | clean speech s；用于 SI-SDR 项 | 论文直接报告 |
| 流式输出格式 | chunk、状态、逐帧时间戳、输出调度 | 未报告 |

### 3.2 U-Net 估计器

所有实验使用同一 U-Net 主干，以便把差异尽量归因于 loss、uncertainty 和推理组合：

- 每个 block 是 2-D convolution + instance normalization + Leaky ReLU，Leaky ReLU slope=0.2。
- Encoder channel progression 为 1-16-32-64-128-256-512，共 6 个 block。
- Decoder channel progression 为 512-256-128-64-32-16-16，encoder 与 decoder 之间有 skip connections。
- 所有 block 的 kernel size 为 (5,5)，stride 为 (1,2)，padding 为 (2,2)，输入维度为 (T,F)。
- 末端为 1x1 convolution；点估计模型输出与输入同形状的 multiplicative filter，aleatoric 版本拆为 Wiener-filter head 与 variance head。
- Wiener-filter head 使用 sigmoid；variance head 使用 log-exp 技巧约束 λ>0。

该网络的频率 stride 为 2，但时间轴仍有 kernel=5 和 padding=2；论文没有将其改写为 causal convolution，也没有描述 frame cache。因此，结构上不能直接得到严格因果结论。

### 3.3 复高斯后验：Wiener filter 与 aleatoric variance

论文假设 speech 与 noise 系数不相关，且分别服从零均值 circularly symmetric complex Gaussian：

$$
S_{ft}\sim\mathcal N_{\mathbb C}(0,\sigma^2_{s,ft}),\qquad
N_{ft}\sim\mathcal N_{\mathbb C}(0,\sigma^2_{n,ft}). \tag{2}
$$

给定 S_ft，mixture 的 likelihood 为：

$$
p(X_{ft}\mid S_{ft})
=\frac{1}{\pi\sigma^2_{n,ft}}
\exp\left(-\frac{|X_{ft}-S_{ft}|^2}{\sigma^2_{n,ft}}\right). \tag{3}
$$

结合先验与 likelihood，clean speech posterior 为：

$$
p(S_{ft}\mid X_{ft})
=\frac{1}{\pi\lambda_{ft}}
\exp\left(-\frac{|S_{ft}-W^{\mathrm{WF}}_{ft}X_{ft}|^2}{\lambda_{ft}}\right). \tag{4}
$$

其中：

$$
W^{\mathrm{WF}}_{ft}
=\frac{\sigma^2_{s,ft}}{\sigma^2_{s,ft}+\sigma^2_{n,ft}},
\qquad
\lambda_{ft}
=\frac{\sigma^2_{s,ft}\sigma^2_{n,ft}}
{\sigma^2_{s,ft}+\sigma^2_{n,ft}}. \tag{5}
$$

W^WF 是 Wiener filter；λ 是 posterior variance。由于复高斯 posterior 对称，MAP 与 MMSE 的复数系数估计相同：

$$
\widetilde S_{ft}=W^{\mathrm{WF}}_{ft}X_{ft}. \tag{6}
$$

网络同时估计 W 与 λ，最小化平均 negative log posterior：

$$
\begin{aligned}
\widetilde W^{\mathrm{WF}}_{ft},\widetilde\lambda_{ft}
=\arg\min_{W^{\mathrm{WF}}_{ft},\lambda_{ft}}
\frac{1}{FT}\sum_{f,t}
\left[
\log(\lambda_{ft})
+\frac{|S_{ft}-W^{\mathrm{WF}}_{ft}X_{ft}|^2}{\lambda_{ft}}
\right]\\
&\equiv \mathcal L_{p(S\mid X)}.
\end{aligned} \tag{7}
$$

若把每个 bin 的 uncertainty 固定为常数 λ*，并且不再显式优化它，则退化为：

$$
\mathcal L_{\mathrm{MSE}}
=\frac{1}{FT}\sum_{f,t}
|S_{ft}-W^{\mathrm{WF}}_{ft}X_{ft}|^2. \tag{8}
$$

因此，这里的 aleatoric uncertainty 不是另加一个分类标签，而是异方差 posterior NLL 中和残差共同学习的误差尺度。

### 3.4 AMAP suppression：让 uncertainty 进入增益

对 Eq. (4) 积分掉 phase 后，spectral magnitude 的 posterior 是 Rician 分布：

$$
p(|S_{ft}|\mid X_{ft})
=\frac{2|S_{ft}|}{\lambda_{ft}}
\exp\left(
-\frac{|S_{ft}|^2+
(W^{\mathrm{WF}}_{ft})^2|X_{ft}|^2}{\lambda_{ft}}
\right)
I_0\left(
\frac{2|X_{ft}||S_{ft}|W^{\mathrm{WF}}_{ft}}{\lambda_{ft}}
\right). \tag{9}
$$

I_0 是第一类 modified zeroth-order Bessel function。Rician mode 没有简单解析式，论文采用 Bessel approximation 得到 AMAP 幅度估计：

$$
\begin{aligned}
|\widehat S_{ft}|
&\approx W^{\mathrm{AMAP}}_{ft}|X_{ft}|\\
&=\left(
\frac{1}{2}W^{\mathrm{WF}}_{ft}
+\sqrt{
\left(\frac{1}{2}W^{\mathrm{WF}}_{ft}\right)^2
+\frac{\lambda_{ft}}{4|X_{ft}|^2}
}
\right)|X_{ft}|.
\end{aligned} \tag{10}
$$

当 λ 增大且其它项固定时，Eq. (10) 的 AMAP estimator value 增大，因而对目标的 attenuation 更保守；代价是可能保留更多 residual noise。论文用 Figure 2 直观展示 AMAP 与 Wiener filter 的输入输出特性：AMAP 对 noisy input 是 nonlinear 的，尤其对低输入更少衰减目标。

![[wiki_low_latency/assets/2305.08744/2305.08744-page04-architecture-amap.png]]

> 图证据：上图是原 PDF 第 4 页的直接页面渲染，保留 Figure 1/2、连线、图例与公式位置；它不是 AI 重画。由于页面字体抽取存在 Symbol/ArialUnicode warning，公式与图标签以该页面视觉证据为准。

### 3.5 Hybrid loss：把 variance 与增强波形耦合

论文把 AMAP 幅度与 noisy phase 合成后做 iSTFT 得到时域估计 ŝ，再使用 SI-SDR loss：

$$
\mathcal L_{\mathrm{SI\text{-}SDR}}
=-10\log_{10}\left(
\frac{\|\alpha s\|^2}{\|\alpha s-\widehat s\|^2}
\right),
\qquad
\alpha=\frac{\widehat s^{T}s}{\|s\|^2}. \tag{11}
$$

最终 hybrid loss 为：

$$
\mathcal L
=\beta\mathcal L_{p(S\mid X)}
+(1-\beta)\mathcal L_{\mathrm{SI\text{-}SDR}},
\qquad \beta\in[0,1]. \tag{12}
$$

实验中 β=0.001。论文的设计意图是：posterior NLL 训练 W 与 λ，SI-SDR 直接约束由 AMAP 产生的波形；这样 variance 不只是“无监督地自己找数值”，而要对 speech reconstruction 有用。

### 3.6 Epistemic 与 overall predictive uncertainty

将网络参数记为 θ、训练集记为 D，论文用近似参数分布 q(θ) 对 predictive distribution 积分：

$$
p(S\mid X,\mathcal D)
=\int p(S\mid X,\theta)p(\theta\mid\mathcal D)\,d\theta
\approx\frac{1}{M}\sum_{m=1}^{M}
p(S\mid X,\theta_m),
\qquad \theta_m\sim q(\theta). \tag{13}
$$

- **MC dropout**：推理时保持 dropout 开启，从多次 stochastic forward 得到 M 个 estimates。
- **Deep ensembles**：用不同随机初始化与随机 data shuffling 重复训练同一 U-Net，得到 M 个确定性参数实例；论文将它们视为近似参数分布的样本。

只输出点估计的 ensemble/dropout 用经验均值和方差表示 epistemic uncertainty：

$$
\widetilde S=\frac{1}{M}\sum_{m=1}^{M}\widetilde S_{\theta_m},
\qquad
\widetilde\Sigma=\frac{1}{M}\sum_{m=1}^{M}
|\widetilde S_{\theta_m}-\widetilde S|^2. \tag{14}
$$

若每个模型还输出 aleatoric variance，则用全方差定律得到 overall predictive uncertainty：

$$
\widetilde S=\frac{1}{M}\sum_{m=1}^{M}\widetilde S_{\theta_m},
\qquad
\widehat\Sigma=\frac{1}{M}\sum_{m=1}^{M}
\left(
|\widetilde S_{\theta_m}-\widetilde S|^2
+\widetilde\lambda_{\theta_m}
\right). \tag{15}
$$

对每个成员用 Eq. (10) 产生 AMAP clean-speech estimate，再平均：

$$
\widehat S=\frac{1}{M}\sum_{m=1}^{M}\widehat S_{\theta_m}. \tag{16}
$$

这里要区分：\widetilde S 是平均 Wiener estimate，\widehat S 是平均 AMAP estimate；\widetilde\Sigma 是 epistemic spread，\widehat\Sigma 是 aleatoric 与 epistemic 的合成量。

### 3.7 关键符号表

| 符号 | 含义 | 作用 |
|---|---|---|
| X_ft | 带噪语音复数 STFT 系数 | Eq. (1) 的输入混合 |
| S_ft、N_ft | clean speech、additive noise 的复数 STFT 系数 | 定义目标与噪声 |
| t、f、T、F | 时间帧、频率 bin 及其总数 | 对时频 loss 求平均 |
| σ²_s,ft、σ²_n,ft | speech/noise 的复高斯方差 | 导出 Wiener filter 与 posterior variance |
| W^WF_ft | Wiener filter / multiplicative gain | 复数 posterior 的均值估计 |
| λ_ft | clean-speech posterior variance | aleatoric uncertainty、NLL 分母、AMAP 输入 |
| W^AMAP_ft | 使用 W^WF 与 λ 的幅度增益 | 生成更少目标 attenuation 的 magnitude estimate |
| \widetilde S_ft、\widehat S_ft | Wiener 估计、AMAP 幅度估计 | 频域增强输出 |
| s、ŝ | clean waveform、估计 waveform | SI-SDR 的 target 与 estimate |
| θ、D、q(θ) | 网络参数、训练集、近似参数分布 | epistemic sampling |
| M | forward passes 或 ensemble 成员数 | 估计均值、方差、整体 uncertainty |
| \widetilde\Sigma | epistemic variance | 参数 spread |
| \widehat\Sigma | overall predictive variance | aleatoric + epistemic |
| β | hybrid loss 权重 | 实验设置为 0.001 |

### 3.5 原论文图示

下图来自本地 PDF 的方法页和结果页：前者核对联合 Wiener/uncertainty/AMAP 管线，后者核对 uncertainty reliability 与增强结果。它们补充了文字公式无法表达的估计器分支和实验对照。

![[wiki_low_latency/assets/2305.08744/2305.08744-page4-architecture-amap.png]]

![[wiki_low_latency/assets/2305.08744/2305.08744-page9-uncertainty-results.png]]

## 4. 实验里哪个消融最关键？

### 4.1 数据、前端与训练

| 项目 | PDF 直接报告 |
|---|---|
| 训练集 | DNS Challenge training set 的 100 h synthetic audio；SNR 均匀分布在 -5 到 20 dB；随机分为 80 h train 与 20 h validation |
| DNS 测试 | 与训练/验证不相交的 reverb-free synthetic test；由 12 类噪声与 speech 组成，SNR 分布在 0 到 25 dB |
| 第二测试集 | WSJ0 evaluation subset si_et_05 clean speech + CHiME3 的 cafe、street、pedestrian、bus 四类噪声；SNR 随机取 {-10,-5,0,5,10} dB |
| 采样率/分析 | 16 kHz；32 ms Hann；50% overlap |
| batch / optimizer | batch size=64；Adam；learning rate=0.001；weight decay=0.0005 |
| 停止与调度 | validation loss 连续 10 epochs 不下降则停止；连续 3 epochs 不下降则 learning rate 减半 |
| MC dropout | 三个 dropout layer 放在 encoder 最深的三个 block 后；drop probability=0.5；推理时开启；论文说每层都加 dropout 会过度正则 |
| Deep ensembles | 重复训练同一设置，使用 random initialization；正文还说明随机 data shuffling |
| M 的分析 | Figure 6/7 使用 M∈{2,4,8,16,32}；整体 predictive uncertainty 取 M=16；Deep ensembles 的分析基于 33 个训练模型中随机选择的 disjoint sets |
| 复现信息 | 论文脚注提及 model code；PDF 未给 commit、预训练权重、随机种子、训练硬件、最大 epoch 或完整复现实验命令 |

### 4.2 对比方法

| 方法 | 训练/推理 | uncertainty | clean-speech estimate |
|---|---|---|---|
| Baseline WF | U-Net + Eq. (8) MSE | 否 | Wiener filter |
| Baseline SI-SDR | 固定方差假设 + Eq. (11) | 否 | multiplicative filter |
| Aleatoric-WF | hybrid Eq. (12) | aleatoric λ | Eq. (6) Wiener estimate |
| Aleatoric-MAP | hybrid Eq. (12) | aleatoric λ | Eq. (10) AMAP estimate |
| MC dropout | Baseline WF 设置；推理开启 dropout | epistemic | 多次 Wiener estimates 的均值/方差 |
| Deep ensembles | Baseline WF 设置；随机初始化重复训练 | epistemic | 多成员 Wiener estimates 的均值/方差 |
| DE-Aleatoric-WF | Aleatoric 设置重复训练 M 次 | aleatoric + epistemic | Eq. (15) 的平均 Wiener estimate |
| DE-Aleatoric-AMAP | Aleatoric 设置重复训练 M 次 | aleatoric + epistemic | Eq. (16) 的平均 AMAP estimate |

> [!note] 表名口径
> PDF 的方法段写 Aleatoric-WF & Aleatoric-AMAP，而 Table II 的对应行印作 Aleatoric-MAP。本页在表格转录中保留 Table II 的写法，在公式和方法解释中使用 AMAP。

### 4.3 Uncertainty 可靠性：sparsification 与 AUSE

论文把每个时频 bin 的 error 定义为估计复数谱系数与 ground truth 之间的 absolute square。按 uncertainty 从高到低移除 bin 后，观察 residual RMSE 如何下降：

- 越接近按真实 error 排序得到的 oracle curve，uncertainty 排序越可靠。
- sparsification error 是实际曲线与 oracle curve 的差；AUSE 是该误差曲线下面积，越低越好。
- Figure 3/4 的 DNS 示例和全测试集结果显示，高 uncertainty 区域通常对应较大估计 error；移除最高 uncertainty 的 20% 时，RMSE 约下降三分之二。
- Figure 5/6 中，MC dropout 与 Deep ensembles 的 uncertainty 曲线均随移除 bin 而下降；论文观察到 Deep ensembles 与 error 更一致，而 MC dropout 对部分错误预测会低估 uncertainty。
- Figure 7 中 M 增大通常改善 AUSE，但从 M=16 到 M=32 的进一步收益变小。

PDF Table I 的 AUSE：

| uncertainty source | AUSE |
|---|---:|
| Aleatoric | 0.110 |
| Epistemic | 0.094 |
| Aleatoric & epistemic | **0.067** |

### 4.4 DNS test 的增强结果

以下转录 PDF Table II；数值是 mean +/- 95% confidence interval。PESQ、ESTOI、SI-SDR 只代表该论文所用 DNS synthetic reverb-free test 上的结果，不跨论文排名。

| 方法 | Unc. | PESQ | ESTOI | SI-SDR |
|---|:---:|---:|---:|---:|
| Noisy (DNS) | - | 1.58 +/- 0.07 | 0.81 +/- 0.02 | 9.07 +/- 0.89 |
| Baseline WF | 否 | 2.48 +/- 0.10 | 0.90 +/- 0.01 | 16.84 +/- 0.74 |
| Baseline SI-SDR | 否 | 2.63 +/- 0.10 | 0.91 +/- 0.01 | 17.49 +/- 0.78 |
| MC dropout | 是 | 2.53 +/- 0.10 | 0.90 +/- 0.01 | 16.88 +/- 0.74 |
| Deep ensembles | 是 | 2.66 +/- 0.10 | 0.91 +/- 0.01 | 17.16 +/- 0.73 |
| Aleatoric-WF | 是 | 2.62 +/- 0.11 | 0.91 +/- 0.01 | 17.54 +/- 0.78 |
| Aleatoric-MAP | 是 | 2.69 +/- 0.10 | 0.91 +/- 0.01 | 17.54 +/- 0.78 |
| DE-Aleatoric-WF | 是 | 2.77 +/- 0.11 | 0.92 +/- 0.01 | 17.88 +/- 0.78 |
| DE-Aleatoric-AMAP | 是 | **2.83 +/- 0.10** | **0.92 +/- 0.01** | **17.90 +/- 0.78** |

论文还在 Figure 9 中报告 WSJ0+CHiME3 第二测试集的 PESQ improvement、ESTOI improvement 和 SI-SDR improvement，横轴为 -10、-5、0、5、10 dB SNR，误差条为 95% confidence interval。原文的结论是：Deep ensembles 与 MC dropout 在 PESQ 上优于 Baseline WF；联合模型在 ESTOI/SI-SDR 尤其低 SNR 下更好；DE-Aleatoric-AMAP 的 PESQ 更高。Figure 9 没有给出可逐柱精确转录的数值表，因此本页不臆测柱高。

![[wiki_low_latency/assets/2305.08744/2305.08744-page09-uncertainty-results-table2.png]]

> 图表证据：上图是原 PDF 第 9 页的直接页面渲染，保留原表头、mean +/- 95% confidence interval、图例和页面编号；不是 AI 重画。

### 4.5 哪个消融最关键？

如果只选一项，最关键的是 **联合 aleatoric + epistemic uncertainty 与单一 uncertainty 来源的 AUSE 对照**：AUSE 从 0.110/0.094 降到 0.067，直接检验了论文最核心的“两个 uncertainty 来源互补”主张，而不是只检验网络换了一个输出头。

但对“uncertainty 是否真正改变语音抑制”这个工程问题，第二个不可替代的 paired ablation 是同一 aleatoric 模型的 **WF vs AMAP**：

- Aleatoric-MAP 的 DNS PESQ=2.69，高于 Aleatoric-WF 的 2.62；
- DE-Aleatoric-AMAP 的 PESQ=2.83，高于 DE-Aleatoric-WF 的 2.77；
- Eq. (10) 解释了方向：λ 高时 gain 更保守，语音失真可能下降，但 residual noise 可能增加。

因此，AUSE 组合消融回答“可靠性排序是否更好”，WF/AMAP 消融回答“可靠性是否进入 suppressor 并影响增强质量”。二者不能互相替代。

### 4.6 噪声抑制、人声保留与结果证据边界

| 审计目标 | 论文直接支持 | 不能从本文推出 |
|---|---|---|
| 噪声抑制 | DNS 与 WSJ0+CHiME3 测试上，PESQ/ESTOI/SI-SDR 相对论文内 baseline 有改善；SI-SDR 同时受噪声和 speech distortion 影响 | 没有 noise-only BAK、频段抑制曲线、突发噪声/竞争说话人分层或残余噪声独立分数 |
| 人声保留 | AMAP 的公式与 Figure 3 说明高 uncertainty 时少衰减，且 Table II 的 PESQ/ESTOI/SI-SDR 有整体收益 | 没有 false-suppression、弱辅音/气声、F0/formant/prosody continuity、ASR WER、DNSMOS SIG/BAK/OVL 或主观听感测试 |
| uncertainty 可靠性 | AUSE/sparsification 表明 uncertainty 排序与谱误差排序相关 | 没有 calibration curve、coverage、selective risk 或“95% uncertainty interval 覆盖率”证据 |
| 泛化 | 两个未见测试集、第二集包含 -10 到 10 dB SNR；论文报告跨域 improvement 趋势 | 未验证真实房间/真实录音/真实设备、packet loss、长流状态恢复或更多 OOD 类型 |

## 5. 这个方向还剩什么问题没解决？（future work / limitation）

### 5.1 论文明确与隐含的限制

论文没有单列一个具体 future-work 清单；结论只说希望推动后续 uncertainty 研究。以下限制均以 PDF 的报告范围或结构为边界，不把未做实验写成已验证事实：

1. **不是 strict-causal 证书。** 论文没有 causal/streaming 声明；32 ms Hann、50% overlap、时间 kernel=5/padding=2 的 U-Net 以及未说明的 STFT 对齐，不能支持逐样本 future-context 审计。
2. **没有端侧计算证据。** 参数量、MAC/s、FLOPs、RAM、量化、CPU/DSP/NPU、RTF、能耗、p50/p95/p99 和 deadline miss 均未报告。M=16 的 ensemble 还会放大推理成本。
3. **不确定性指标主要是排序指标。** AUSE 低说明高 uncertainty bin 更可能对应高误差，但不等于概率校准、覆盖率或可安全触发 bypass。
4. **人声保留没有被分解测量。** AMAP 的设计明确是以较少目标 attenuation 换取可能更多 residual noise；本文没有单独报告 false-suppression 或下游 ASR。
5. **测试覆盖有限。** 训练/评估是 DNS synthetic、WSJ0 speech 与 CHiME3 noise 的组合；没有真实设备、真实 capture-to-playback、移动声源、packet loss 或长时稳定性结果。
6. **复现字段仍不完整。** PDF 给出 batch、Adam、学习率、weight decay 和停止规则，但未报告 FFT size、STFT centering、随机种子、训练硬件、最大 epoch、模型参数量及完整 streaming implementation。
7. **Figure 9 精确数值不完整。** 第二测试集只以柱状图和 95% confidence interval 展示；精确 bar values 未在 PDF 表格中给出。

### 5.2 面向当前低时延方向的可检验延伸

下面是本 Wiki 的后续实验建议，不是 2305.08744 已报告的结果：

- 将 U-Net 改成单向/状态化小模型，逐层标注最后可读输入样本，再在 batch=1 目标硬件上测 p50/p95/p99、RTF 和 deadline miss。
- 保留 λ 或 total variance 作为轻量 auxiliary head，把它用于 gain floor、保守 suppression 或 bypass；同时报告 AUSE、calibration、selective risk 与人声 false-suppression。
- 若使用 Deep ensemble，先把多模型作为离线 teacher 或蒸馏目标；端侧只保留单次 forward，并重新核算内存与 worst-case deadline。
- 在 -10/-5/0/5/10 dB、babble/竞争说话人/瞬态/未见噪声上分开报告 speech preservation、noise residual 和 ASR/音素连续性，而不是只给 pooled PESQ/ESTOI/SI-SDR。

## 6. 本论文在库中的位置关联（cross-reference matrix）

| 关系 | 库中页面 | 关联与边界 |
|---|---|---|
| 当前论文实体 | [[wiki_low_latency/entities/Uncertainty-Aware-SE]] | 记录 U-Net、WF/AMAP、两类 uncertainty 与 DNS 结果；本 source 是唯一论文证据汇总 |
| 当前论文概念 | [[wiki_low_latency/concepts/2305.08744-uncertainty-aware-suppression]] | 抽象“variance 进入 suppression”的机制；不把 AUSE 当成 calibration |
| 低比特率/迟到辅助信息对照 | [[wiki_low_latency/sources/2023/GCFSnet 2023]] | GCFSnet 将迟到跨耳特征限制在 filter estimator 支路；本文将 uncertainty 写入 AMAP 与 loss。两者输入、数据和部署证据不同，数字不可直接横比 |
| 低时延结构对照 | [[wiki_low_latency/sources/2023/FSB-LSTM 2023]] | FSB-LSTM 报告低算法时延与 GMAC/s；本文不报告 RTF/MAC/s，不能把两篇结果当作同条件排名 |
| speech distortion/loss 对照 | [[wiki_low_latency/entities/Noise-Suppression-Losses]] | 本文的 posterior NLL + SI-SDR 把 error scale 与波形重建耦合；本文未覆盖该页所需的完整人声保留分解 |
| continuity/过抑制对照 | [[wiki_low_latency/concepts/2203.16843-continuity-loss]] | AMAP 的“高 uncertainty 少衰减”与保留语音方向相关，但原论文没有 continuity loss 或 false-suppression 实验 |
| 阵列/空间滤波类比 | [[wiki_array/concepts/波束成形 Beamforming]] | 都涉及不确定条件下的抑制-保真权衡；本文是单通道时频 posterior，不是阵列/DOA 方法 |

> [!question] 交叉引用证据边界
> 本矩阵只说明本地 Wiki 页面之间的研究问题关系，不引入其他页面的数字作为本论文证据。不同数据集、窗长、网络、指标和推理预算下的 PESQ/ESTOI/SI-SDR 不应直接决定跨论文“谁更强”。

## 7. 一句话江湖地位

~~~text
2023 | 单通道不确定性感知语音增强 | 用复高斯 posterior variance、AMAP 与 MC dropout/Deep ensembles 把“增强结果有多可信”写进抑制和评估，在 DNS test 上证明联合 uncertainty 的收益；但 32 ms STFT + U-Net 没有 strict-causal、RTF、p99 或端侧部署证据，因此它是可靠性/质量方法基线，不是已验证的超低时延模型。
~~~

### 参考资料

- [本地原始 PDF](../../../raw/papers/low_latency_causal_se/2305.08744.pdf)
- [[wiki_low_latency/entities/Uncertainty-Aware-SE]]
- [[wiki_low_latency/concepts/2305.08744-uncertainty-aware-suppression]]
