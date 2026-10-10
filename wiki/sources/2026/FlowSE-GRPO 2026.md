---
title: "FlowSE-GRPO — 在线 GRPO 训练流匹配语音增强"
type: source
created: 2026-09-08
updated: 2026-09-08
tags:
  - speech-enhancement
  - generative-model
  - flow-matching
  - reinforcement-learning
  - post-training
  - reward-hacking
source_type: paper
year: 2026
authors: Haoxu Wang, Biao Tian, Yiheng Jiang, Zexu Pan, Shengkui Zhao, Bin Ma, Daren Chen, Xiangang Li
affiliation: Tongyi Lab, Alibaba Group, China
venue: ICASSP 2026
arxiv: "2601.16483"
url: https://arxiv.org/abs/2601.16483
related:
  - [[流匹配与 GRPO 后训练]]
  - [[Conditional Diffusion SE 2022]]
  - [[Investigating Design Space of Diffusion for SE 2023]]
  - [[SGMSE+ 2023]]
  - [[MetricGAN+ 2021]]
  - [[语音增强评价指标]]
  - [[2026 语音增强前沿五篇比较]]
---

```yaml
- 论文: [FlowSE-GRPO](2026)
  ├── 要解决什么问题: 生成式 SE 无法直接对齐 DNSMOS/声纹/语义等不可微指标；后训练在 SE 中研究少，尤其在线 RL 未探索
  ├── 核心方法: 把 flow-matching 的确定性 ODE 采样改为等边缘 SDE 提供候选，用在线 GRPO（组内相对优势+clip+KL）后训练，多指标加权奖励
  ├── 属于哪个分支: 生成式语音增强 / flow-matching / 在线强化学习后训练（RLHF→GRPO 的音频化）
  ├── 输入/输出: 带噪 mel c → DiT 从高斯噪声生成干净 mel → 预训练 HiFi-GAN → 波形（非流式，推理 10 步）
  ├── 关键trick: ODE→SDE 转换（含 SE 反转时间的漂移修正 σ²/[2(1-t)]）；多指标 std 归一化加权奖励；早期步 window training（ws=2）；LoRA 后训练
  ├── 数据集: 预训练 DNS2020/LibriTTS-960/VCTK/WSJ/EARS/MLS English；后训练 clean 仅 LibriTTS-960；评估 DNS2020 三条件
  ├── 对比了谁: MaskSR/GenSE/LLaSE-G1/AnyEnhance/AR+Soundstorm/Flow-SR/FlowSE(base)，外加 DPO 对照
  ├── 性能上限: DNSMOS OVRL 3.373→3.549（No Reverb）、3.254→3.530（With Reverb）、3.115→3.356（Real Recording）
  ├── 参数量: DiT 46.18M（12 层、hidden 512、8 heads）；LoRA 后训练仅 1.57M 可训练
  ├── 消融关键发现: window training 只在早期步做 SDE 显著加速奖励增长；噪声水平 a 越大收敛越快但 reward hacking 风险越高；单指标奖励快速抬高该指标却压低其他维度
  ├── 遗留问题(你的机会): 无听测/无开源、DNSMOS 是代理指标可被刷、单指标 reward hacking 未根治、权重需人工调、非流式
  └── 跟哪篇像: [[MetricGAN+ 2021]]（直接优化不可微指标 + 记录刷分风险）、[[SGMSE+ 2023]]（反向 SDE 生成）
```

# FlowSE-GRPO: Training Flow Matching Speech Enhancement via Online Reinforcement Learning

> Haoxu Wang, Biao Tian, Yiheng Jiang, Zexu Pan, Shengkui Zhao, Bin Ma, Daren Chen, Xiangang Li（Tongyi Lab, Alibaba Group），ICASSP 2026，arXiv:2601.16483v1（首提交 2026-01-23）。[官方摘要](https://arxiv.org/abs/2601.16483)｜[HTML](https://arxiv.org/html/2601.16483)｜[PDF](https://arxiv.org/pdf/2601.16483)｜[[outputs/reports/2026-09-08-frontier/enhancement/2601.16483_FlowSE-GRPO.pdf|本地 PDF]]。未提供官方代码。

对应概念页：[[流匹配与 GRPO 后训练]]。

## 1. 动机：他们为什么这么做？（motivation）

生成式语音增强（generative SE）把「干净语音分布」当成建模对象，而非像判别式方法那样只学一个 noisy→clean 的确定性映射。早期扩散/得分模型（[[Conditional Diffusion SE 2022]]、[[SGMSE+ 2023]]）已经证明这条路能缓解过平滑、提升感知自然度，但它有一个共同盲点：**训练目标（如 flow-matching 的速度场 MSE）和「人怎么评价增强效果」（DNSMOS、声纹相似、语义保真）之间是断裂的**。模型把 MSE 降到很低，不代表听感、说话人身份、语义内容都变好。

作者看到相邻领域（LLM 的 RLHF、图像生成的 reward hack、TTS 的 GRPO 后训练）已经用「后训练 + 强化学习」把模型对齐到不可微的人类/任务指标，但语音增强里几乎没人做，尤其是**在线（on-policy）RL**：此前 SE 只用过离线 DPO。于是本文的核心命题是——能不能把在线 GRPO 后训练接到 flow-matching SE 上，用很少的更新步就把模型对齐到感知/任务指标？

## 2. 前人局限：之前的人怎么做不了？（limitation → gap）

- **判别式方法**：只学幅度/复数谱的确定性映射，上限是「回归最优」，无法显式优化感知质量。
- **生成式 SE（diffusion / flow-matching）**：建模收益不差，但**训练损失与最终听感不一致**，只能间接、隐式地追求好指标。
- **已有的后训练尝试**：SE 里只出现过**离线 DPO**（off-policy）。DPO 需要提前离线生成大量 win–lose 对，耗时且无法针对任意指标在线探索；而在线 GRPO 在 LLM/TTS 里已被证明更高效、可优化多样指标，但在连续时间序列 + flow-matching 的 SE 场景下「能不能用、怎么用」仍是空白。
- **为什么这个 gap 到现在没解决**：flow-matching 的采样是**确定性 ODE**，推理一次只有一条轨迹、一个输出——这是 on-policy RL 的天然障碍（RL 需要策略产生「多样化候选」才能比较相对好坏）。要把 GRPO 搬过来，必须先解决「确定性采样 → 随机采样」这一步，而这一步在语音的连续时间设定下还没有现成答案。

本文填补的 gap：**首次把 Flow-GRPO（图模态）的在线 RL 范式迁移到语音增强**，并针对语音的连续时间序列性质和 flow-matching 的反向时间约定做了适配。

## 3. 核心 Trick：这个做法关键在哪？（⭐ 分级）

**基座**：flow-matching SE，输入带噪 mel $c$ 作条件，DiT 预测速度场 $v$，把标准高斯 $x_0\sim\mathcal N(0,I)$ 搬运到干净 mel $x_1$；再用预训练 HiFi-GAN 变回波形。流匹配损失（Eq. 1，$x_t=(1-t)x_0+tx_1$）：

$$L(\theta)=\mathbb E_{t,x_0,x_1}\|v-v_\theta(x_t,c,t)\|_2^2,\qquad v=x_1-x_0.$$

- ⭐⭐⭐ **ODE → SDE（给在线策略「随机性」）**：flow-matching 的确定性 ODE $dx_t=v_t\,dt$（Eq. 2）只能产出一条轨迹。作者把它改成保持边缘分布的等价 SDE，加了探索噪声 $\sigma_t\sqrt{\Delta t}\,\epsilon$。关键小心思：flow-matching SE 的去噪时间 **t: 0→1**，与原始 Flow-GRPO 的 **t: 1→0** 相反，因此要把公式做符号代换（$v=-v_{se}$、$t=1-t_{se}$ 等）。代换后更新均值为（Eq. 6）：

$$x_{t,\mathrm{mean}}=x_t+\left[v_\theta(x_t,t)+\frac{\sigma_t^2}{2(1-t)}(-x_t+t\,v_\theta(x_t,t))\right]\Delta t,$$

其中 $\sigma_t=a\sqrt{(1-t)/t}$，噪声水平 $a$ 控制探索强度。注意漂移修正项带 $\sigma_t^2/[2(1-t)]$ 而非乘 $(1-t)$——这是 SE 反转时间约定的直接后果，也是本文区别于图模态 Flow-GRPO 的推导要点（[[流匹配与 GRPO 后训练]] 概念页同样强调了这一点）。

- ⭐⭐⭐ **多指标奖励对抗 reward hacking**：单指标奖励会「刷分」。作者把 DNSMOS（OVRL 的 $\tfrac14$ 加权，`R_DNSMOS/4`）、speaker similarity（`R_Spk`，ERes2Net 嵌入余弦相似）、SpeechBERTScore（`R_SBS`，参考式语义相似）三个奖励各自除以标准差后再加权求和（Eq. 7 in §2.3）：

$$R=\lambda_1\frac{R_{DNSMOS}}{\operatorname{std}(R_{DNSMOS})}+\lambda_2\frac{R_{Spk}}{\operatorname{std}(R_{Spk})}+\lambda_3\frac{R_{SBS}}{\operatorname{std}(R_{SBS})},\qquad(\lambda_1,\lambda_2,\lambda_3)=(0.6,1,1).$$

  std 归一化把量级不同（OVRL≈1–5 vs SPK/SBS∈[0,1]）的指标拉到同一尺度再权衡；$\lambda_1=0.6$ 是对 DNSMOS 过优化/欠优化之间的人工折中（作者试过 1.0/0.6/0.5/0.4）。

- ⭐⭐ **window training（只在早期步做 SDE 与优化）**：只在窗口 $S=[S_{min},S_{min}+ws]$ 上做 SDE 采样和参数更新（$ws=2$，$S_{min}$ 采样自 [1,3]，训练去噪步采样自 [7,10]），其余步走确定性 ODE。目的是砍掉全轨迹训练的开销、加速收敛（承接 MixGRPO / Flow-GRPO-Fast）。

- ⭐⭐ **LoRA 后训练 + 组内相对优势 GRPO**：后训练只训 LoRA（rank 32、$\alpha=64$，1.57M 可训练参数）。同一带噪 $c$ 采 $G=10$ 条轨迹，组内标准化优势（Eq. 8）：

$$\hat A_t^i=\frac{R(\hat x_1^i,c)-\operatorname{mean}_iR(\hat x_1^i,c)}{\operatorname{std}_iR(\hat x_1^i,c)},$$

  再按 clipped 目标 + 参考策略 KL 惩罚优化（Eq. 9）：

$$\mathcal J_{flow\text{-}grpo}(\theta)=\mathbb E_{c,\{x_i\}\sim\pi_{\theta_{old}}}\left[\frac1G\sum_{i=1}^G\frac1{|S|}\sum_{t\in S}\min\!\left(r_t^i\hat A_t^i,\ \operatorname{clip}(r_t^i,1-\epsilon,1+\epsilon)\hat A_t^i\right)\right]-\beta D_{KL}(\pi_\theta\|\pi_{ref}),$$

  其中 $r_t^i=p_\theta(x_{t+1}^i|x_t^i,c)/p_{\theta_{old}}(x_{t+1}^i|x_t^i,c)$（新/旧策略的高斯转移密度比）。clip 防止单次更新跑太远，KL 拉住预训练参考模型。

> [!note] GRPO 状态/奖励的时序约定
> 采样被看成 MDP：状态 $s_t\triangleq(c,t,x_t)$，动作 $a_t\triangleq x_{t-1}$（由速度场预测的去噪样本），转移是确定的，**只在 $t=0$ 的终点**（得到最终 mel 并变回波形后）给一个奖励 $r(x_0,c)$。这与 LLM 里 token 级奖励不同，是「整条轨迹一个终值奖励」的设定。

## 4. 结果与消融：哪个最敏感？

**主结果（Table 1/2，DNS2020 非盲测试集，多指标 GRPO vs 无 RL base）**：

| DNS2020 子集 | SIG / BAK / OVRL | SPK / SBS |
|---|---|---|
| No Reverb | 3.598/4.172/**3.373** → 3.753/4.248/**3.549** | 88.88%→90.43% / 86.35%→86.72% |
| With Reverb | 3.511/4.105/**3.254** → 3.740/4.251/**3.530** | 73.72%→77.75% / 73.62%→75.89% |
| Real Recording | 3.397/4.035/**3.115** → 3.604/4.161/**3.356** | 无干净参考，无 SPK/SBS |

相对作者自己的 FlowSE base，OVRL 提升（Table 1 直接相减）：No Reverb **+0.176**、With Reverb **+0.276**；DPO 对照是 +0.065 / +0.144。效率对比是 GRPO 5k steps vs DPO 20k steps（**作者自报的步数对比，不是跨实现公平耗时/算力对比**）。

> [!contradiction] With-Reverb OVRL 增益 .274 vs .276
> 正文 §4.1 写 GRPO 的 With-Reverb OVRL 增益为 +0.274，但 Table 1/2 中 3.530 − 3.254 = **.276**，差值无法由三位小数的四舍五入解释。此处以表中可复算数值为准，并保留原文叙述差异。

**最重要的「消融」其实是一张现象图（Fig. 2）**：

- **单指标奖励会 reward hacking**（本文的核心负结果）。Fig. 2(a)：只优化 DNSMOS（$a=0.2$）时，DNSMOS 从约 3.36 约 1.5k 步冲到约 3.59；Fig. 2(b)(d)：只优化 speaker similarity（88.86→91.20+）或 SpeechBERTScore（86.4→87.2）固然把目标分数抬上去，**却会压低 DNSMOS**。即「代理指标涨了，但别的维度（含听感、声纹、语义）反而退化」。
- **噪声水平 $a$**（§4.2.1）：$a$ 从 0.2 加大到 0.3、0.4，DNSMOS 上升速率更快（探索更充分），但 $a$ 过大也会诱发 reward hacking——探索范围要精细平衡。最终多指标配置取 $a=0.4$。
- **window training**（§4.2.2）：只在早期去噪步做 RL（Fast）比全轨迹训练（Non-Fast，$S_{min}=1,ws=10$）奖励增长更快，即**砍掉后期步的 SDE 反而加速收敛**。

结论最敏感的两个旋钮：**奖励设计（单 vs 多指标、权重）** 与 **SDE 探索强度 $a$**，都直接决定「真增强」还是「刷分」。

## 5. 这个方向还剩什么问题没解决？（future work / limitation）

论文自己承认的：

- 「score weights require careful tuning」（$\lambda_1=0.6$ 是拍出来的折中），并明确写「we will investigate more robust online RL training strategies in future work」——多指标权重本身还是手工调、不鲁棒。
- 未提供任何主观听测；未报告波形域保真指标（SI-SDR/PESQ）随 GRPO 的变化，只看 DNSMOS/SPK/SBS 这些（很可能就是）被奖励的目标本身。

读出来的隐藏问题：

- **reward hacking 只被『缓解』而非「消除」**：权重和奖励模型偏差仍可能让模型投机评分，缺少「不参与奖励的外部指标 + 盲听」作为终审（[[2026 语音增强前沿五篇比较]] 里也点名了这一条纪律）。
- **非流式、10 步采样**：没有因果/延迟证据，也未见部署复杂度，离实时增强还远。
- **不可复现**：无代码、无 checkpoint、无评分实现细节、无随机种子，声学质量主张目前无法独立验证。
- 效率对比（5k vs 20k）不是公平的算力/耗时比较，别被「更高效」带偏。

## 6. 本论文在库中的位置关联（cross-reference matrix）

| 维度 | 论文 | 关系 |
|---|---|---|
| 前身/基石 | [[Conditional Diffusion SE 2022]] | 条件扩散把 SE 写成「以带噪为条件建模干净语音分布」；FlowSE-GRPO 继承这一生成式框架，但换成 flow-matching + 后训练对齐 |
| 前身/基石 | [[SGMSE+ 2023]] | 反向 SDE 生成式 SE 的标杆；FlowSE-GRPO 的 ODE→SDE 技巧与其反向随机微分方程同源，但目的不同（SGMSE+ 生成 vs 为 RL 提供探索） |
| 同分支竞品 | [[Investigating Design Space of Diffusion for SE 2023]] | 系统拆解扩散 SE 的设计轴（采样器/噪声调度/步数）；本文 §4.2 消融（噪声水平 a、window 训练）正是这些设计轴在 RL 后训练场景的延续 |
| 同分支竞品 | [[SELM 2023]] | 生成式 SE 的另一路线（离散 token AR/NAR）。本文 §1 明确把生成式 SE 分两类，Table 1 却只对比 token 方法 MaskSR/GenSE/LLaSE-G1，⚠️ SELM 是库内代表、表格未直接列 |
| 跨分支类比 | [[MetricGAN+ 2021]] | 与本文最像的「前身」：都直接优化不可微感知/任务指标（MetricGAN+ 用判别器当指标导师，本文用 GRPO 奖励），且**都记录了「单指标刷分损伤其他维度」**（MetricGAN+ 优化 PESQ 降 STOI） |
| 跨分支类比 | [[语音增强评价指标]] | DNSMOS/SPK/SBS 等代理指标的定义与局限；reward hacking 的根基正在于「代理指标 ≠ 真实听感」 |
| 后续/扩展 | —（暂无） | 2026 年新工作、无开源，库内尚无直接扩展它的论文 ⚠️ 疑似；与其余四篇的关系见 [[2026 语音增强前沿五篇比较]] |

## 7. 一句话总结「江湖地位」

```text
2026 | 生成式语音增强 | 首次把在线 GRPO 接入 flow-matching SE，用多指标奖励对 reward hacking 做实证 → 在线 RL 后训练生成式增强的方法学标杆/首批证据（尚无开源与后续扩展）
```