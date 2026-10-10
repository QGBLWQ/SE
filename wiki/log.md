---
title: 操作日志
type: log
created: 2026-06-05
updated: 2026-06-21
tags:
  - log
---

# 操作日志

## [2026-07-20] ingest | TF-GridNet 2023 — 时频域语音分离的"伟大复兴"

- 下载 PDF: `raw/papers/TF-GridNet 2023.pdf` (620 KB, arXiv:2211.12433)
- 创建 [[TF-GridNet 2023]] — 全带+子带交替 BLSTM + 跨帧 attention 的时频域分离模型
- 核心叙事："时频域不是本身不好，是架构设计没跟上"——TF-GridNet 用交替 Unfold+BLSTM+Deconv 模式替代 CRNN，SI-SDRi=23.5 dB 超越时域 SOTA
- 关键跨域连接：FullSubNet (级联全带+子带) vs TF-GridNet (交替全带+子带)——语音领域最需要而从未发生的公平对比
- 与 CST-former 的同构分析：三模块 ≈ 三维注意力（全带=S-attention, 子带=T-attention, 跨帧=另一种 T-attention）
- 更新 [[语音定位+语音增强/wiki/index]] — Sources 列表 +1

## [2026-07-20] concept | 创建概念页：log-mel 频谱 + 更新全带与子带模型

- 创建 [[log-mel 频谱]] — Mel 尺度公式、log 压缩三重作用、DCASE 7ch 标准输入解释、与线性幅度/MFCC/BFCC/Bark 的对比、为什么增强用线性幅度多而定位用 log-mel 多
- 更新 [[全带与子带模型]]：
  - 全带模型图重绘：显式展示 Conv2D 只压频率不压时间、fc 升维 + uni-LSTM 沿 T 轴逐帧串行、33 条频率序列共享 LSTM 权重并行跑、保留 T 维的输出
  - 子带模型图重绘：显式展示"同一频率窗口 × 所有帧"的局部邻域取法、帧对齐的 concat 注入（h_global 每一帧都在变）、子带 LSTM 的因果时序推进、双重时序叠加的解释
  - 级联 vs 并行消融重写：两种方案的具体架构对比图、为什么级联更好的物理解释（全局信息"参与推理" vs "参与投票"）、具体场景演示（f=47 语音初期被并行误削）
- 更新 [[语音定位+语音增强/wiki/index]] — Concepts 列表 +1

## [2026-07-13] rewrite | 批量规范化 wiki/sources 论文笔记

- 按 `CLAUDE.md` 的 source 笔记规范批量重写 `wiki/sources/` 下旧版骨架笔记 20 篇：补全 YAML 快速索引卡片、动机、前人局限、核心 trick、关键消融、future work/limitation、cross-reference matrix、江湖地位。
- 统一轻修 6 篇已重写长笔记的章节标题：[[Conv-TasNet 2019]], [[DCCRN 2020]], [[DPCRN 2021]], [[FullSubNet 2021]], [[PHASEN 2020]], [[RNNoise 2018]]。
- 对缺少原文表格/消融数值的论文使用 `> [!question] 待补` 标注，避免假装理解或补造指标。
- 结构复查：`wiki/sources/` 共 26 篇 source 笔记，均保留 frontmatter、快速索引卡片、7 个规范分析部分与交叉引用章节。

## [2026-07-14] rewrite | 重写 CMGAN 2022 笔记

- 按 CLAUDE.md 模板全面重写 [[CMGAN 2022]]
- 核心叙事："好目标 × 好 backbone = ?" → CMGAN 证明了 1+1>2，MetricGAN 目标贡献 (0.26) > Conformer 架构贡献 (0.16)，但两者可叠加
- 新增 Conformer 块结构详解 (MHSA+Conv+FFN 的分工) + "卷积注意力混合 vs 纯Transformer vs 纯CNN"的分析
- 消融明确了"目标>架构"的反直觉结论及其数据集依赖的可能性
- 江湖定位："目标+架构双优路线的奠基者"，Connecting MetricGAN+ → CMGAN → MP-SENet 演化链

## [2026-07-14] update | 语音增强评价指标概念页重写

- 重写 [[语音增强评价指标]] — 从 3 个指标扩展到 6 个指标 (PESQ, MOS, STOI, CSIG, CBAK, COVL, SI-SNR)
- 新增 CSIG/CBAK/COVL 的完整解释：三维分解的直觉（三种"坏"的对比）、计算公式、为什么 Voice Bank+DEMAND 社区偏好这三个
- 新增 SI-SNR vs PESQ 的对比（波形精度 vs 感知质量）
- 新增使用指南表：不同任务/数据集应该用哪些指标

## [2026-07-14] rewrite | 重写 MetricGAN+ 2021 笔记

- 按 CLAUDE.md 模板全面重写 [[MetricGAN+ 2021]]
- 核心叙事："训练目标比 backbone 重要"——最普通的 BLSTM + 聪明的训练策略 > 同年精心设计的 DCCRN/PHASEN
- 新增完整框架图 (G/D 交替训练 + 经验回放池) + 三大稳定化改进的详细解释 + 消融敏感度排序 (经验回放 –0.20 > 数据增强 –0.13 > mask 输出 –0.10)
- 遗留问题含"单指标剃刀效应"、"D 输入分布 ≠ PESQ 函数输入分布"、"分离社区完全忽略——可微 SI-SNR 代理？"、"指标导师的跨任务通用性"

## [2026-07-10] concept | 创建概念页：全带与子带模型

- 创建 [[全带与子带模型]] — 全带（全局频谱结构）vs 子带（局部频率细节）的完整对比 + 级联>并行的原因分析 + 与时间维双路径的对照表 + 子带窗口 K 的选取逻辑
- 更新 [[FullSubNet 2021]] — 添加双向链接
- 更新 [[语音定位+语音增强/wiki/index]] — Concepts 列表 +1

## [2026-07-10] rewrite | 重写 FullSubNet 2021 笔记

- 按 CLAUDE.md 模板全面重写 [[FullSubNet 2021]]
- 新增 YAML 快速索引卡片 + 5 个分析维度
- 核心叙事："全带看森林，子带看树木"——频率维分治 vs 同年 DPCRN 的时间维分治
- 新增数据流模拟：3 秒语音 → Encoder 五层降采样的逐层形状变化 → 全带 LSTM 插值 → 子带逐频率处理（每频率拼接 31 bin 局部+256 维全局特征）→ mask 生成 → 参数/推理时间分解
- 遗留问题含"Complex FullSubNet"和"频率×时间×复数三维分治"的未竟方向
- frontmatter: 补全 authors/venue/code/related links

## [2026-07-10] rewrite | 重写 DPCRN 2021 笔记

- 按 CLAUDE.md 模板全面重写 [[DPCRN 2021]]（原笔记仅 40 行骨架）
- 新增 YAML 快速索引卡片 + 5 个分析维度
- 核心叙事："DCCRN 证明了复数好，DPRNN 证明了分块好，DPCRN 说为什么不两个都要？" → 证明复数+双路径增益可叠加 (+0.09 PESQ)
- 关键设计洞察：分块夹在编码器和解码器之间——频率维度的复数卷积不受分块影响
- 遗留问题含"复数双路径→定位的跨域迁移"和"时域可学习编码器+复数+双路径三者结合的终极方案"
- frontmatter: 补全 authors/venue/code/related links

## [2026-07-09] update | 补充 STFT相位图与相位信息——四种维度全景

- 在 [[STFT相位图与相位信息]] 中新增"相位信息的四种维度"章节（通道间 / 频率间 / 时间间 / 混合干净间）
- 四个维度的物理全景图（声带振动 → 频率间关系 → 声波传播 → 通道间差异 → 单通道处理 → 混合vs干净差距）
- 跨域迁移注释：复数网络主要利用维度 2+3+4，相位图方法主要利用维度 1+2，交集未被探索
- 更新 frontmatter: 改名、补标签、加跨域 links

## [2026-07-09] concept | 创建概念页：FTB 频时注意力块

- 创建 [[FTB 频时注意力块]] — 三步详解（频率 attn → 时间 attn → 跨流融合）+ O(F+T) 复杂度分析 + 与其他注意力方法的对比表 + 堆叠效应阐述
- 更新 [[PHASEN 2020]] — 添加双向链接
- 更新 [[语音定位+语音增强/wiki/index]] — Concepts 列表 +1

## [2026-07-09] rewrite | 重写 DCCRN 2020 笔记

- 按 CLAUDE.md 模板全面重写 [[DCCRN 2020]]
- 新增 YAML 快速索引卡片，突出"复数统一 vs 双流解耦"的哲学对比
- 新增 5 个分析维度：动机（实虚部结构关系的数学事实）/ 前人局限（全链路复数化的组件缺失 + 公平对比难做）/ 核心 Trick（⭐⭐⭐ 复数卷积块结构 +0.15 > 复数 LSTM +0.06 → "相位信息主要在频率维度被保留"）/ 消融分析（因果版仅 –0.14 PESQ vs Conv-TasNet 的 –4.7 dB → STFT 域因果约束更宽松）/ 遗留问题（8 个 gap 含"复数网络不可解释性"和"定位领域零篇使用"）
- 补全 江湖地位："2020 相位双子星"中更工程化的一方 + 复数网络→定位的跨域空白
- 修复 frontmatter: 去引号、补完整路径、加 `code` 字段

## [2026-07-09] rewrite | 重写 PHASEN 2020 笔记

- 按 CLAUDE.md 模板全面重写 [[PHASEN 2020]]
- 新增 YAML 快速索引卡片
- 新增 5 个分析维度：动机（相位被忽视的"偷懒"范式）/ 前人局限（相位卷绕、幅相不搭、无跨流机制）/ 核心 Trick（⭐⭐⭐ 双流非对称 + FTB 跨流注意力 + 反卷绕相位损失）/ 消融分析（相位流 –0.17 > FTB –0.11 > 预测相位 vs 带噪相位 –0.14）/ 遗留问题（8 个 gap + 填补对照表）
- 补全 江湖地位："两种相位建模哲学的代表作" + 未竟之业（显式谐波 + Pitch 滤波器融合方向）
- 修复 frontmatter: 去引号、补完整路径、加 `code` 字段、添加缺失标签

## [2026-07-08] report | 语音增强与 DOA/SELD 时序模型与特征提取全景对比

- 创建 `outputs/reports/语音增强与DOA-SELD-时序模型与特征提取全景对比.md`
- 覆盖 26 篇增强/分离 + 17 篇 DOA/SELD 方法论文的系统性跨域对比
- 核心发现：① 可学习编码器 42% vs 0% ② TCN 4篇 vs 0篇 ③ BiGRU 在定位长寿7年 vs 增强2020年后被淘汰
- 识别 6 个跨域研究空白，优先级最高：TCN 替代 BiGRU 做 SELD、可学习编码器+IPD 约束做 DOA

## [2026-07-08] report | 可学习编码器 + TCN 在 DOA/SELD 中的迁移可行性分析

- 创建 `outputs/reports/可学习编码器在DOA-SELD的迁移可行性分析.md`
- 遍历 wiki_array/ 17 篇论文确认：零篇使用可学习编码器 → 确认无人区
- 分析三层障碍：相位角色相反（分离=麻烦 vs 定位=信号）、多通道×数据稀缺、物理先验vs数据驱动
- 提出三个突破方向：A) 共享编码器+IPD约束 B) 混合架构 C) 可学习波束成形
- 标注 MIMO-DoAnet (cRF) 和 DBnet (可微分DOA) 为相近前例

## [2026-07-06] concept | 创建概念页：扩张卷积、TCN、理想掩蔽

## [2026-07-06] concept | 创建概念页：可学习编码器

- 创建 [[可学习编码器 Learnable Encoder]] — 1-D 卷积编码器的完整解释：数学公式、与 STFT 的逐项对比、训练好的基函数可视化结论（>60% 低频偏置 + 多相位编码）、分析可学习编码器如何解决相位问题和任务适配问题
- 更新 [[Conv-TasNet 2019]] — 添加双向链接
- 更新 [[语音定位+语音增强/wiki/index]] — Concepts 列表 +1

- 重写 [[扩张卷积与TCN]] — 聚焦扩张卷积本身：直观图示、堆叠策略、深度可分离变体、感受野公式、局限分析
- 创建 [[时序卷积网络 TCN]] — TCN 架构全景（R 组 × M 块）、gLN vs cLN 对比、TCN vs LSTM 性能对照表、在语音领域的泛化应用
- 创建 [[理想掩蔽 Ideal Mask]] — IBM/IRM/WFM 三种 oracle mask 的完整对比，Conv-TasNet 超越 WFM +1.9 dB 的深层含义（证明了 STFT 本身的相位信息损失），PESQ vs MOS 的反直觉矛盾
- 更新 [[Conv-TasNet 2019]] — 添加双向链接
- 更新 [[语音定位+语音增强/wiki/index]] — Concepts 列表 +3

## [2026-07-06] rewrite | 重写 Conv-TasNet 2019 笔记

- 按 CLAUDE.md 模板全面重写 [[Conv-TasNet 2019]]
- 新增 YAML 快速索引卡片
- 新增 5 个分析维度：动机 (STFT 相位-幅度天花板) / 前人局限 (序列长度爆炸, TCN 被低估) / 核心 Trick (⭐⭐⭐ 可学习编码器 + 扩张卷积 TCN) / 消融分析 (段长 L=16 反直觉最优, 因果 –4.7 dB) / 遗留问题 (8 个 gap + 填补对照表)
- 补全 江湖地位："时域语音分离的分水岭时刻"
- 修复 frontmatter: 去引号、补完整路径、添加相关论文链接
- 修复章节编号冲突: 原一~七 + 八(关联矩阵) + 九(江湖地位)

## [2026-07-06] concept | 创建概念页：谐波 & Pitch 滤波器

- 创建 [[谐波]] — 谐波的物理定义、语音中的谐波结构、浊音vs清音频谱差异、在语音增强中的意义
- 创建 [[Pitch滤波器]] — 频域梳状滤波器的完整原理：pitch 延迟信号、跨频带互相关 $p_b$、滤波系数 $\alpha_b$ (Eq. 6)、三步数学推导、局限分析
- 更新 [[RNNoise 2018]] — 添加双向 Wiki 链接至新概念页
- 更新 [[语音定位+语音增强/wiki/index]] — Concepts 列表新增两个条目

## [2026-07-06] ingest-batch | 批量摄入24篇语音增强论文

批量创建了24篇语音增强领域的source笔记，完整覆盖2017-2024年的主要工作：

### 时频域方法 (9篇)
- [[SEGAN 2017]] — 首个GAN for SE，时域端到端
- [[PHASEN 2020]] — 双流幅度-相位架构
- [[DCCRN 2020]] — 首个完整复数CNN+RNN
- [[FullSubNet 2021]] — 全带-子带融合，DNS冠军
- [[MetricGAN+ 2021]] — 可微分PESQ优化 (PESQ=3.15)
- [[CMGAN 2022]] — Conformer+MetricGAN (PESQ=3.41)
- [[TF Attention Module 2023]] — 可学习时频注意力CRNN
- [[MP-SENet 2023]] — 幅相并行去噪 (PESQ=3.50 SOTA)
- [[CRAFT 2022]] — CRNN+交叉注意力

### 时域方法 (5篇)
- [[Wave-U-Net 2018]] — 首个时域U-Net源分离
- [[DPRNN 2020]] — 双路径RNN序列建模 (2.6M超越Conv-TasNet)
- [[Real Time SE Waveform 2020]] — Conv-TasNet实时化
- [[Demucs 2019]] — 混合时域+频域音乐分离
- [[SuDoRM-RF 2020]] — Conv-TasNet高效压缩版

### Transformer/Mamba (3篇)
- [[SepFormer 2021]] — 纯Transformer语音分离 (SI-SNRi=20.4)
- [[MossFormer 2022]] — 门控线性注意力 (SI-SNRi=21.0)
- [[Mamba for SE 2024]] — Mamba SSM首次用于SE探索

### 混合DSP-DL (2篇)
- [[PercepNet 2020]] — Valin的感知驱动增强 (~500K参数)
- [[DeepFilterNet 2023]] — 深度滤波+感知驱动 (<1 GFLOP/s)

### 生成式模型 (4篇)
- [[SGMSE+ 2023]] — 得分匹配扩散SE
- [[Conditional Diffusion SE 2022]] — 条件扩散模型
- [[Investigating Design Space of Diffusion for SE 2023]] — 扩散设计空间系统分析
- [[SELM 2023]] — 离散token+LM的SE

### 复数网络 (1篇)
- [[DPCRN 2021]] — DCCRN+DPRNN融合

### 交叉分析
- 更新 [[cross-pollination-analysis]] — 增强与定位的交叉方法分析


## [2026-07-06] survey | 语音增强深度学习综述

- 创建 comprehensive survey: wiki/surveys/deep-learning-speech-enhancement-survey.md
- 覆盖 24 篇论文 (2017–2024)，8 个章节
- 新增下载 4 篇 PDF: SGMSE+, DCCRN, Demucs, CRAFT → raw/papers/
- 调查路线: 传统DSP → 时频域DL → 时域DL → Transformer/Attention → 混合DSP-DL → 生成模型 → 前沿方向

## [2026-06-21] split | 声源定位/阵列处理方向独立为 wiki_array/

- 将 DOA 相关页面从主 Wiki 分离，建立独立 `wiki_array/` 目录
- 迁移 4 个页面 + 创建独立的 `index.md`, `overview.md`, `log.md`
- 主 Wiki 保留语音增强与音源分离方向，通过 "其他 Wiki" 互链
- 更新 `CLAUDE.md` 添加双 wiki 目录说明

## [2026-06-05] ingest | RNNoise — 混合 DSP/深度学习的实时全频带语音增强

- 论文：Jean-Marc Valin, Mozilla, 2018
- 创建 [[RNNoise 2018]] — 完整摘要（9 条公式详解、复杂度分析、可复现性评估）
- 创建 [[RNNoise]] — 实体页（架构图、应用场景、与后续方法的关系）
- 创建 [[理想比率掩蔽 IRM]] — IRM 定义、变体（IBM/cIRM/sqrt-IRM）、与 RNNoise 的关系
- 创建 [[Bark尺度与临界频带]] — 感知尺度、22 频带设计、BFCC 特征
- 创建 [[感知加权损失函数]] — γ-指数加权、与交叉熵/SI-SNR 的对比
- 更新 [[语音定位+语音增强/wiki/index]] — 所有新页面入链
- 更新 CLAUDE.md — 领域特化从分子动力学适配为音频方向

## [2026-06-05] config | CLAUDE.md 领域适配：分子动力学 → 音频

- 重写 `领域特化 Domain Specialization` 整章
- "论文处理重点"：传统DSP → 深度学习 → 公式 → 评价指标 → 可复现性
- "LAMMPS 案例处理规则" → "音频模型/算法处理规则"（7 个关注点）
- 添加音频领域关键词覆盖：PESQ、STOI、SI-SNR、IRM、STFT、Bark、RTF 等

## [2026-06-05] init | Wiki 初始化与目录重组

- 按照 `CLAUDE.md` 和 `LLM wiki.md` 标准重组 vault 目录结构
- 创建 `raw/`（papers, articles, notes, assets）
- 创建 `wiki/`（entities, concepts, sources, topics）
- 创建 `outputs/`（qa, reports, figures）
- 迁移原有文件：
  - `papers_pdf/` → `raw/papers/`（12 篇 PDF）
  - `literature/` → `raw/articles/`（1 篇笔记）
  - `temp/` → `raw/articles/`（7 篇转换/概念笔记）
  - 根目录笔记 → `raw/notes/`（入门手册）
- 创建 wiki 骨架：`overview.md`, `index.md`, `log.md`
- 清理空目录：`papers_pdf/`, `literature/`, `temp/`

<!-- frontier-2026-09-08:start -->
## [2026-09-08] ingest | 语音增强前沿论文五篇

- 收录 5 篇 2026 前沿论文及中文技术笔记；全文位于 [[outputs/reports/2026-09-08-frontier/README|论文包]]。
<!-- frontier-2026-09-08:end -->
