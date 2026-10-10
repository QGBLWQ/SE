# 声源定位深度学习综述：从DOA估计到三维声事件定位与检测（2020–2025）

---

## 摘要

声源定位（Sound Source Localization, SSL）在过去十年经历了从传统信号处理方法到深度学习驱动的范式转变。本综述全面回顾了SSL的最新研究进展，涵盖三个主要子领域：波达方向（DOA）估计、声事件定位与检测（SELD）、以及音视频多模态声源定位。我们梳理了从基础CRNN到现代ResNet-Conformer混合架构和Transformer模型的演进脉络，分析了关键数据集和评估指标，识别出包括三维空间感知、真实环境鲁棒性、数据效率和跨模态融合在内的核心开放挑战。特别关注自监督预训练、状态空间模型和开放词汇定位等新兴范式。最后，我们提出了有前景的未来研究方向路线图。

---

## 1. 引言

声源定位——确定声学事件的空间来源——是音频信号处理中的基本问题，其应用涵盖机器人、智能环境、视频会议、监控、自动驾驶和增强现实等领域。传统上该问题通过信号处理技术解决，如到达时间差（TDOA）、广义互相关相位变换（GCC-PHAT）、导向响应功率（SRP）以及MUSIC和ESPRIT等子空间方法。

然而，深度学习的出现从根本上重塑了该领域。现代SSL系统能够在复杂的、具有混响的多源环境中联合执行声事件的检测、分类和定位。DCASE（声学场景与事件检测及分类）挑战赛系列一直是推动进展的主要驱动力，尤其是其中的声事件定位与检测（SELD）任务。

本综述覆盖2020–2025年的文献，重点关注最新进展。我们沿三条轴线组织文献：

1. **DOA估计** — 使用深度神经网络的纯方向估计
2. **SELD** — 声事件检测与定位的联合任务
3. **音视频SSL** — 利用视觉线索的多模态方法

---

## 2. 传统基础与深度学习的转向

### 2.1 传统SSL方法

传统SSL方法可归类如下 [Sound Source Localization: A Survey, 2025]：

| 方法类别 | 代表性技术 | 主要局限 |
|---------|-----------|---------|
| **基于时间差** | TDOA, GCC-PHAT | 对混响敏感；多声源处理能力差 |
| **基于波束成形** | SRP-PHAT, MVDR | 分辨率受限于阵列孔径 |
| **基于子空间** | MUSIC, ESPRIT | 假设窄带、远场、已知声源数量 |
| **基于声强** | 声强矢量 | 空间分辨率低 |

### 2.2 为何转向深度学习？

深度学习解决了传统方法的几个根本性局限：
- **混响鲁棒性**：神经网络能够学习将直达路径与混响成分解耦
- **多声源处理能力**：端到端模型可处理同类别重叠事件
- **联合优化**：在统一框架内同时完成检测与定位
- **阵列灵活性**：可适应任意麦克风几何布局

然而，深度学习方法也引入了新的挑战：对标注训练数据的高度依赖、对未见声学环境泛化能力有限、以及较高的计算成本 [Xu等, *Applied Sciences*, 2025]。

---

## 3. 深度学习DOA估计

### 3.1 问题建模

DOA估计旨在从多通道音频记录中估计一个或多个声源的入射角 $(\theta, \phi)$。深度学习方法通常将其建模为：
- **分类问题**：将角度空间离散化，预测每个网格点是否存在声源
- **回归问题**：直接预测连续角度值
- **混合方法**：先分类后精细回归

### 3.2 输入表示

输入表示的选择对性能有决定性影响 [CANN, 2025; DeepSSE, 2025]：

| 输入类型 | 优势 | 劣势 | 代表性工作 |
|---------|------|------|-----------|
| **I/Q波形** | 完整的信号信息 | 输入量大，需要复值网络 | 基于ResNet的方法 |
| **协方差矩阵/向量** | 紧凑，保留空间信息 | 需要足够的快照数 | CANN, DCAE, DeepSSE |
| **时频图** | 联合频谱-时间特征 | 预处理成本较高 | CMOR-CoAtNet |
| **STFT相位** | 轻量级表示 | 可能丢失信息 | 基于CNN的方法 |

2025年的系统性对比研究发现，**协方差向量在大多数实际场景中提供了最佳的复杂度-性能权衡** [LTDDOA-Net, 2025]。

### 3.3 主要架构家族

#### 3.3.1 基于CNN的方法

卷积神经网络因其高效性和强大的空间特征提取能力仍被广泛使用：
- **SE-ResNet** (2025)：在残差网络中加入Squeeze-and-Excitation通道注意力机制，在低信噪比多信号DOA估计中显著降低平均角度误差
- **DCAE + DCNN** (2025)：使用深度卷积自编码器补全稀疏阵列的协方差矩阵，使互质阵列/嵌套阵列能够进行类MUSIC处理
- **FCN时变阵列方法** (2025)：全卷积网络通过代理到共享空间频谱的映射，处理几何结构时变的阵列

#### 3.3.2 注意力机制与混合方法

- **CMOR-CoAtNet** (2025)：使用CoAtNet（CNN+自注意力混合架构）处理Complex Morlet小波时频图。通过两阶段训练（合成数据预训练+真实数据微调），在真实室内录音上达到**98.22%准确率**
- **MDTP + IRTCN** (2025)：膨胀邻域注意力Transformer配合时序卷积网络，用于无网格相干极化DOA估计，通过多并行注意力联合提取空间-极化特征

#### 3.3.3 波束成形启发的网络

- **BeamformNet** (2025)：基于RNN的框架，隐式学习最优空间滤波器。理论上有坚实的统计最优波束成形近似基础。在仿真和真实（RealMAN）语音定位数据上均达到最先进水平，全面超越SubspaceNet、DA-MUSIC和经典MUSIC方法

### 3.4 应对实际挑战

#### 未知/可变数量的声源
**DeepSSE** (2025) 通过模拟MUSIC峰值搜索的角度网格搜索（AGS）过程，结合非对称损失函数实现泛化。该工作还将**OSPA（最优子模式分配）指标**首次引入DOA评估。

#### 有限训练数据
**LTDDOA-Net** (2025) 提出"学会学习"框架，利用损失函数的二阶导数进行元学习，在极少标注数据下实现良好性能。

#### 阵列非理想性
**CANN** (2025) 使用卷积注意力和频率token化，对互耦合、增益/相位不一致和传感器位置误差具有鲁棒性。

#### 轻量化部署
**LightDOA** (2025) 采用深度可分离CNN+GRU用于资源受限的边缘设备，而**LLM辅助模拟声学场景** (2025) 探索在LLM生成的多样化空间音频场景上进行训练。

---

## 4. 声事件定位与检测（SELD）

### 4.1 任务定义与演进

SELD联合解决*什么声音出现*（声事件检测，SED）和*声音从哪里来*（波达方向估计，DOAE）。该任务通过DCASE挑战赛系列逐步标准化：

| DCASE届次 | 任务 | 关键进展 |
|-----------|------|---------|
| 2019 | Task 3 | 首个SELD竞赛；FOA格式；CRNN基线 |
| 2020 | Task 3 | 多声源重叠；合成TAU-NIGENS数据集 |
| 2021 | Task 3 | STARSS21真实录音；ACCDOA输出格式 |
| 2022 | Task 3 | STARSS22数据集；真实世界复杂度提升；MIC阵列 |
| 2023 | Task 3 | STARSS23；纯音频；强调鲁棒性 |
| 2024 | Task 3 | **三维SELD（SELDDE）：加入声源距离估计** |
| 2025 | Task 3 | **立体声SELD**，常规视频场景；屏内外预测 |

### 4.2 架构演进

该领域经历了四个架构代际 [npj Acoustics综述, 2025]：

#### 第一代：CRNN（2018–2020）
- **SELDNet** (2018)：首个端到端CRNN，联合SED+DOAE
- 标准结构：CNN编码器 → Bi-GRU → 独立的SED/DOA分支
- 受限于顺序处理和对同类重叠事件的处理能力

#### 第二代：ACCDOA及其改进（2021–2022）
- **ACCDOA** (2021)：统一的SED+DOAE回归目标——单一向量同时编码事件活动性和方向
- **Multi-ACCDOA** (2022)：多输出轨迹处理同类别重叠事件
- **EINV2** (2022)：增强的声强矢量特征，配合置换不变训练
- **SALSA特征**：空间线索增强对数频谱（Spatial Cue-Augmented Log-Spectrogram），取代基本的log-mel+GCC-PHAT

#### 第三代：ResNet-Conformer与Transformer（2023–2024）
- **ResNet-Conformer**：CNN前端+Conformer块（自注意力+卷积），取代CRNN成为主导架构
- **音频通道交换（ACS）**：有效的空间多样性数据增强
- **SE-ResNet-Conformer**：Squeeze-and-Excitation增强变体 [DCASE 2024]

#### 第四代：先进架构（2024–2025）

| 模型 | 架构 | 创新点 | 性能 |
|------|------|--------|------|
| **SELD-Mamba** (2024) | 双向Mamba状态空间模型 | 线性复杂度替代自注意力；两阶段训练（先SED+DOA，再加SDE） | 更低成本下与Transformer媲美 |
| **CST-Former** (2024) | 通道-频谱-时序Transformer | 三维独立自注意力；仅~0.39M参数（ResNet-Conformer ~58M） | DCASE 2022上SELD得分0.4162（提升22.1%） |
| **w2v-SELD** (2024) | wav2vec 2.0空间适配 | 在无标注4通道Ambisonics上自监督预训练；对比学习 | TAU-2019提升66%；TAU-2020提升57% |
| **Cross-Modal Conformer** (2025) | CLAP + OWL-ViT融合 | 语言对齐的音视频嵌入用于立体声SELD | DCASE 2025 Task 3最强 |

### 4.3 输出表示

输出格式的演进反映了领域的成熟：

- **独立SED+DOA分支**（2018–2020）：事件检测和定位使用独立输出头
- **ACCDOA**（2021）：每类每轨单一向量 `[activity, x, y, z]`，统一两个任务
- **Multi-ACCDOA**（2022至今）：多输出轨迹，实现同类别重叠事件处理
- **ADPIT损失**（2022）：置换不变训练目标，最优匹配预测轨迹与真实标注
- **Multi-ACCDDOA**（2024）：扩展为 `[activity, x, y, z, d]`，支持三维SELD

### 4.4 特征工程

特征提取日益精细化 [npj Acoustics, 2025]：

| 特征 | 年份 | 描述 |
|------|------|------|
| **Log-mel + GCC-PHAT** | 2019–2021 | 标准频谱-时间特征 + 空间特征 |
| **FOA声强矢量** | 2019 | 从B-format提取有功能量/无功能量 |
| **EINV2** | 2021 | 增强声强矢量，加入相位信息 |
| **SALSA** | 2022 | 空间线索增强对数频谱；多通道频谱+空间编码 |
| **NGCC-PHAT** | 2024 | 可训练的神经广义互相关；可学习的TDOA特征提取 |

### 4.5 SELD的核心挑战

1. **密集多声源**：真实场景常含多个同时发声的声源；轨迹方法有上限
2. **同类别重叠**：同类事件的多个实例（如两人同时说话）本质上有歧义
3. **真实场景泛化**：尽管已有STARSS等数据集，仿真到真实的鸿沟依然显著
4. **数据标注成本**：强标注需要事件类型、起止时间和三维轨迹——极其昂贵
5. **计算效率**：当前最先进的模型集成方案无法满足实时部署需求

---

## 5. 音视频多模态声源定位

### 5.1 多模态优势

视觉信息提供了补充线索，尤其在复杂声学条件下能显著改善定位性能。音视频SSL已成为一个活跃的研究领域，在CVPR/WACV等计算机视觉会议上受到的关注不亚于音频会议。

### 5.2 基础模型集成

#### 基于CLIP的方法
- **Can CLIP Help Sound Source Localization?** (WACV 2024)：将CLIP文本编码器适配为处理音频token，生成音频驱动的嵌入来指导视觉掩膜生成。推理时无需任何文本输入，大幅超越先前SSL方法
- **Hearing and Seeing Through CLIP** (2025)：在上述工作基础上加入LLM引导的知识蒸馏，在五个不同的定位任务上实现零样本泛化

#### 语言作为桥梁模态
- **T-VSL** (CVPR 2024)：利用AudioCLIP三模态嵌入，将文本作为中间模态。先预测发声实体类别，再利用文本表示来解耦多源混合中的细粒度音视频对应关系。对未见的声源类别展示零样本迁移能力
- **Object-aware SSL** (CVPR 2025)：利用多模态大语言模型（MLLM）生成上下文描述，显式区分发声前景物体与静默背景物体。引入对象感知对比对齐（OCA）和对象区域隔离（ORI）两种新损失函数

### 5.3 三维音视频定位

- **Sound3DVDet** (WACV 2024)：基于Transformer，融合多视角RGB+麦克风阵列。学习最小化跨模态重投影误差。发布了Sound3DVDet数据集（~6k仿真场景）
- **SoundLoc3D** (WACV 2025)：RGB-D声学相机，可定位不可见声源（如气体泄漏、机器故障）。将任务建模为集合预测问题，利用深度图像的物理表面线索

### 5.4 带视觉线索的SELD

- **AV-Conformer** (DCASE 2024)：音视频Conformer，通过Depth-Anything模型提取深度图进行距离估计。360°视频转换为立方体贴图表示。DOA误差减半，F1分数比基线提升3倍以上
- **Cross-Modal Conformer** (DCASE 2025)：CLAP音频嵌入+OWL-ViT视觉嵌入，通过跨模态Conformer模块融合。立体声SELD最先进，支持屏内外预测

---

## 6. 三维SELD与距离估计

### 6.1 超越方位角和仰角

DCASE 2024挑战赛是一个分水岭——首次将声源距离估计（SDE）纳入SELD任务，将定位问题从二维角度空间 $(\theta, \phi)$ 扩展到全三维 $(\theta, \phi, d)$。

### 6.2 距离线索

距离估计依赖不同于角度定位的物理线索：
- **直达-混响能量比（DRR）**：距离近的声源DRR更高
- **声压级**：平方反比定律（但被声源自身响度混淆）
- **双耳/多麦克风频谱差异**：适用于双耳/多麦克风录音
- **视觉深度**：当有RGB/RGB-D相机时

### 6.3 前沿方法

- **SELD-Mamba** (2024)：两阶段训练——第一阶段SED+DOA，第二阶段加入SDE损失，解决不同物理量联合优化的不稳定性
- **SE-ResNet-Conformer** (DCASE 2024)：SALSA特征+SE注意力+距离缩放，实现均衡的多任务学习
- **利用混响和视觉深度线索** (DCASE 2024)：显式建模直达/混响成分和深度图以提高距离估计精度

### 6.4 评估挑战

距离估计带来了新的评估复杂性：
- **相对距离误差**：使用百分比误差而非绝对误差
- **帧级别 vs 事件级别指标**：如何跨事件聚合
- **与检测的相互依赖**：漏检会影响距离指标
- DCASE 2024评估指标将F-score、角度误差和相对距离误差合并为单一聚合分数

---

## 7. 新兴研究范式

### 7.1 自监督与数据高效学习

由于SELD数据标注成本极高（事件类型+起止时间+三维轨迹），减少监督需求成为研究热点：

- **w2v-SELD** (2024)：将wav2vec 2.0适配到多通道Ambisonics。在无标注三维音频上使用对比学习预训练，然后在小型标注数据集上微调。比基线提升57-66%
- **DOA-Aware Audio-Visual Self-Supervised Learning** (2025)：以DOA作为训练信号的音视频联合自监督学习
- **PSELDNet** (2024)：SELD网络的预训练策略
- **半监督SELD**：通过自训练和一致性正则化利用无标注或弱标注数据的新兴工作

### 7.2 状态空间模型与高效架构

Transformer自注意力的二次复杂度促使探索替代方案：

- **SELD-Mamba** (2024)：率先将双向Mamba（结构化状态空间模型）用于SELD。线性时间复杂度和具有竞争力的性能
- **QSELD-TCN** (2024)：量化时域卷积网络，实现高效推理
- **CST-Former** (2024)：仅0.39M参数的多维注意力（vs. ResNet-Conformer ~58M），证明高效架构不必牺牲性能

### 7.3 开放词汇与文本引导SELD

一个新兴前沿是超越固定声源类别分类体系：

- **开放词汇SELD**：基于文本提示的检测，可定位用自然语言描述的任意声源类别
- **T-VSL** (CVPR 2024)：通过文本嵌入实现音视频定位对未见过类别的零样本迁移
- **文本引导的音频源分离+定位**：用语言指定混合声中*哪个*声源需要定位

### 7.4 领域自适应与泛化

对未见声学环境的鲁棒性仍是关键挑战：

- **领域对抗训练**：梯度反转层用于学习环境不变特征
- **测试时自适应**：推理时调整模型统计量以适应目标环境
- **合成数据多样性**：LLM辅助的场景生成以增加训练数据多样性
- **阵列无关模型**：朝不依赖重训练的跨麦克风几何布局SSL系统发展

### 7.5 音频多任务与基础模型

统一的音频基础模型趋势可能重塑SELD：
- 音频基础模型（如CLAP, AudioLDM, Pengi）可提供预训练表示
- 多任务模型联合处理SSL、ASR、音频字幕和场景理解
- 挑战：在以语义音频理解为优化目标的模型中如何保留细粒度空间信息

---

## 8. 数据集与评测基准

### 8.1 主要SELD数据集

| 数据集 | 年份 | 环境 | 格式 | 标注 | 关键特点 |
|--------|------|------|------|------|---------|
| **TAU-NIGENS** | 2019-2020 | 仿真 | FOA | 11类，1-2重叠 | DCASE 2019基线 |
| **STARSS21** | 2021 | 真实房间 | FOA | 13类，追踪声源 | 首个真实SELD数据集 |
| **STARSS22** | 2022 | 真实房间 | FOA+MIC | 13类，光学追踪 | 真实世界复杂度 |
| **STARSS23** | 2023 | 真实房间 | FOA | 13类 | 纯音频侧重 |
| **STARSS24** | 2024 | 真实房间 | FOA | 13类+距离 | 三维SELD；距离真值 |
| **Sony-TAU** | 2022 | 真实 | 立体声 | 多种 | 真实空间录音 |

### 8.2 DOA估计数据集

| 数据集 | 年份 | 关键特性 |
|--------|------|---------|
| **Pyroomacoustics（合成）** | — | 可配置房间、阵列、信噪比；用于预训练 |
| **LOCATA** | 2018 | 真实录音，多种阵列，移动声源 |
| **RealMAN** | 2024 | 真实世界语音定位；DOA标准评测 |
| **SoS** | 2024 | 室内SSL，含背景噪声增强 |
| **SLoClas** | 2025 | SSL方法鲁棒性评测基准 |

### 8.3 音视频数据集

| 数据集 | 年份 | 描述 |
|--------|------|------|
| **MUSIC** | 2018 | YouTube乐器演奏视频；音视频SSL基准 |
| **VGGSound** | 2020 | 20万+视频，309类别；音视频对应 |
| **Sound3DVDet** | 2024 | SoundSpaces约6k场景；多视角RGB+麦克风阵列 |
| **FAIR-Play** | — | 双耳音乐演出视频 |

### 8.4 评估指标

#### SELD指标
- **F-score**：事件检测精度与召回率的调和平均（按类别+跨类别）
- **DOA误差**：预测方向与真实方向的角度距离
- **相对距离误差**：用于三维SELD
- **SELD分数**：F-score、DOA误差和（可选）距离误差的加权组合

#### DOA指标
- **平均绝对误差（MAE）** / **均方根误差（RMSE）**：角度误差
- **K度准确率**：预测在K度范围内的百分比
- **OSPA** (2025)：适用于可变数量声源的最优子模式分配指标

---

## 9. 开放挑战与未来方向

### 9.1 已识别的研究空白

基于本综述，我们识别出以下关键开放问题：

#### 挑战一：全三维空间感知
尽管DCASE 2024引入了距离估计，SDE的性能仍远落后于角度估计。距离线索本质上存在歧义（声源响度混淆、房间特性依赖混响），当前模型在未知环境中难以胜任。**物理信息约束的多任务学习**是一个有前景的方向。

#### 挑战二：数据效率
SELD需要昂贵的强标注（类别+轨迹+起止时间）。自监督预训练（w2v-SELD）显示出潜力但尚处于早期阶段。**少样本和半监督SELD**大部分未被探索。基于扩散模型的合成数据生成和主动学习是潜在的突破路径。

#### 挑战三：真实环境泛化
从仿真到真实环境，性能显著下降。领域对抗训练和测试时自适应是部分解决方案，但在根本上缺乏对SSL模型鲁棒性来源的理论理解。**系统化泛化测试基准框架**亟待建立。

#### 挑战四：密集多声源与同类别重叠
当前基于轨迹的方法（Multi-ACCDOA）可处理2-3个重叠声源，但在鸡尾酒会场景中失效。受计算机视觉DETR启发的**集合预测公式**和**连续空间表示**可克服这些限制。

#### 挑战五：轻量化与实时系统
最先进的SELD系统是运行在GPU上的大模型集成。对于机器人、助听器、AR眼镜和边缘设备，**高效架构**（CST-Former、SELD-Mamba、QSELD-TCN）至关重要，但仍牺牲了精度。硬件-算法协同设计几乎未被探索。

#### 挑战六：多麦克风阵列泛化
大多数方法针对特定阵列几何形状（FOA、四面体）训练。适用于任意麦克风配置的**阵列无关模型**将极大扩展应用范围。

#### 挑战七：与音频基础模型的集成
如何利用大型预训练音频模型（CLAP、AudioLDM、Pengi）同时保留细粒度空间信息是一个开放问题。当前音频基础模型的**空间理解能力**几乎未被测试。

#### 挑战八：可解释性与可信度
SELD系统是黑盒。理解模型*为什么*预测某个位置（例如"它使用了200Hz处直达路径的耳间时间差"）将帮助调试和安全关键部署。**空间任务的可解释音频AI**是一个新兴领域。

#### 挑战九：运动声源与动态场景
当前评估是基于帧的且基本是静态的。真实声源会移动，在遮挡和路径交叉中跟踪声源研究不足。具有运动先验的**时空跟踪模型**可弥补这一差距。

#### 挑战十：跨模态对齐质量
音视频方法假设音视频一致对应，但对于画面外、被遮挡或非视觉声源会失效。当某一模态不可靠时优雅降级的**鲁棒融合策略**亟待开发。

### 9.2 有前景的研究方向总结

| 方向 | 理由 | 难度 |
|------|------|------|
| **物理信息驱动的神经SELD** | 将声波传播物理作为归纳偏置 | ⭐⭐⭐ |
| **基于扩散模型的空间音频生成** | 生成具有可控声学特性的多样化训练场景 | ⭐⭐⭐ |
| **基础模型微调用于SELD** | 利用CLAP/AudioLDM表示实现数据高效学习 | ⭐⭐ |
| **连续神经场表示空间音频** | 声场的隐式神经表示 | ⭐⭐⭐⭐ |
| **神经形态音频处理** | 基于事件的音频传感器实现超低延迟SSL | ⭐⭐⭐⭐⭐ |
| **多智能体声学SLAM** | 将声源定位与环境建图结合 | ⭐⭐⭐⭐ |
| **跨模态少样本定位** | 从文本描述和少量示例定位声源 | ⭐⭐⭐⭐ |
| **因果音视频推理用于SELD** | 从相关到因果理解——真正理解发声事件 | ⭐⭐⭐⭐⭐ |

---

## 10. 结论

声源定位领域已被深度学习深刻改变，从狭义的DOA估计发展到整体的环境声学智能。DCASE SELD挑战赛推动了显著的架构创新——从CRNN到ResNet-Conformer，再到CST-Former和SELD-Mamba——而视觉模态和基础模型的集成则指向越来越强大和泛化的系统。

然而关键缺口依然存在。全三维空间感知、真实环境鲁棒性、数据效率和可解释性仍是需要重大突破的活跃领域。对于进入这一领域的研究者，自监督学习、高效架构和多模态融合的交叉融合提供了丰富且有影响力的研究机会。

我们希望本综述既能作为当前技术水平的全面参考，也能作为基于深度学习的声源定位未来研究的路线图。

---

## 参考文献

1. "Environmental Acoustic Intelligence through Sound Event Localization and Detection: A Review." *npj Acoustics*, Vol. 1, Art. 31, 2025.
2. Xu, K., Zong, Z., Liu, D., Wang, R., & Yu, L. "Deep Learning-Based Sound Source Localization: A Review." *Applied Sciences*, Vol. 15, Art. 7419, 2025.
3. Jalayer, R., Jalayer, M., & Baniasadi, A. "A Review on Sound Source Localization in Robotics: Focusing on Deep Learning Methods." *Applied Sciences*, Vol. 15, Art. 9354, 2025.
4. "A Survey of Machine Learning Techniques for Signal Source Localization and Emitter Tracking." *IEEE Access*, Vol. 13, pp. 198390–198409, 2025.
5. "Sound Source Localization: A Survey." *IJATEIS*, Vol. 4, No. 2, pp. 295–314, 2025.
6. "CMOR-CoAtNet: A Complex Morlet-Convolutional Attention Network Framework for Robust DOA Estimation." *Digital Signal Processing*, 2025.
7. "DOA Estimation Method for Sparse Arrays Based on Deep Convolutional Autoencoder and Deep Convolutional Neural Network." *Digital Signal Processing*, 2025.
8. "Gridless Coherent Polarization-DOA Estimation with Dilated Neighborhood Attention and Temporal Convolutional Network." *Digital Signal Processing*, 2025.
9. "Deep Learning-Based DOA Estimation via Grid Search Approach for Unknown and Variable Number of Signals." *IEEE Access*, 2025.
10. "DOA Estimation with Lightweight Network on LLM-Aided Simulated Acoustic Scenes." *IEEE Access*, 2025.
11. "Enhanced Residual Networks with Squeeze-and-Excitation Blocks for Multi-Signal DOA Estimation." Zenodo, 2025.
12. "DOA Estimation with Deep Learning: A Limited Training Data Framework." *IEEE Access*, 2025.
13. "BeamformNet: Deep Learning-Based Beamforming Method for DOA Estimation via Implicit Spatial Signal Focusing and Noise Suppression." arXiv:2512.18647, 2025.
14. "Learning-Based Robust DOA Estimation with Array Imperfections." *Signal Processing*, 2025.
15. "DOA Estimation Method for Time-Varying Arrays Using FCN-Based Deep Learning." *IEICE Trans. Commun.*, 2025.
16. "CANN: Convolutional Attention Neural Network for Robust DOA Estimation." 2025.
17. "SELD-Mamba: Selective State-Space Model for Sound Event Localization and Detection with Source Distance Estimation." arXiv:2408.05057, 2024.
18. "w2v-SELD: A Sound Event Localization and Detection Framework for Self-Supervised Spatial Audio Pre-Training." *IEEE Access*, 2024.
19. "CST-Former: Channel-Spectro-Temporal Transformer for Sound Event Localization and Detection." 2024.
20. "Squeeze-and-Excite ResNet-Conformers for DCASE 2024 Challenge." arXiv:2407.09021, 2024.
21. "The LU System for DCASE 2024 Sound Event Localization and Detection Challenge." DCASE 2024 Workshop, 2024.
22. "Leveraging Reverberation and Visual Depth Cues for SELD with Distance Estimation." arXiv:2410.22271, 2024.
23. "Spatial and Semantic Embedding Integration for Stereo SELD in Regular Videos." DCASE 2025, 2025.
24. "DOA-Aware Audio-Visual Self-Supervised Learning for SELD." arXiv:2410.22803, 2024.
25. Park, S. et al. "Can CLIP Help Sound Source Localization?" *WACV*, 2024.
26. Park, S. et al. "Hearing and Seeing Through CLIP." arXiv:2505.05343, 2025.
27. Mahmud, T. et al. "T-VSL: Text-Guided Visual Sound Source Localization in Mixtures." *CVPR*, 2024.
28. Um, S.J. et al. "Object-aware Sound Source Localization via Audio-Visual Scene Understanding." *CVPR*, 2025.
29. He, Y. et al. "SoundLoc3D: Invisible 3D SSL Using Multimodal RGB-D Acoustic Camera." *WACV*, 2025.
30. He, Y. et al. "Sound3DVDet: 3D Sound Source Detection Using Multiview Mic Array and RGB." *WACV*, 2024.

---

> **综述生成日期：2026-06-29** · 覆盖2020–2025年文献 · 声源定位、SELD、DOA估计
