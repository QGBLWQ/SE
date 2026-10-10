---
title: Acoustic Imaging for UAV Detection: Dense Beamformed Energy Maps and U-Net SELD
type: source
created: 2026-09-15
updated: 2026-09-15
tags:
  - doa-estimation
  - acoustic-imaging
  - u-net
  - source-segmentation
  - beamforming
  - seld
  - uav
  - semantic-segmentation
  - tversky-loss
source_type: paper
year: 2025
authors:
  - Belman Jahir Rodríguez
  - Sergio F. Chevtchenko
  - Marcelo Herrera Martínez
  - Yeshwanth Bethi
  - Saeed Afshar
affiliation: International Centre for Neuromorphic Systems (ICNS), Western Sydney University, Australia; Universidad de San Buenaventura, Colombia
venue: arXiv preprint (v4, 17 Jul 2026)
arxiv: "2508.00307"
url: https://arxiv.org/abs/2508.00307
dataset_doi: "10.26183/07nm-4p35"
related:
  - [[SSLIDE 2021]]
  - [[Mechanical Fault SSL 2024]]
  - [[LAM Self-Supervised DOA 2025]]
  - [[DeepWave Acoustic Imaging 2019]]
  - [[Direct-Path Dominance Test 2020]]
  - [[SELD CRNN 2018]]
---

# Acoustic Imaging for UAV Detection — DAS 波束形成能量图 + U-Net 的 360° 声学图分割定位

> Belman Jahir Rodríguez, Sergio F. Chevtchenko, Marcelo Herrera Martínez, Yeshwanth Bethi & Saeed Afshar（ICNS, Western Sydney University ＋ Universidad de San Buenaventura），arXiv:2508.00307（2025 预印本，v4 于 2026-07-17）。这是整个"把 DOA 变成声学图语义分割"路线的一个外向实例：**不回归角度，而是分割整个空间声场。**

> [!note] 标题/文件名说明
> arXiv v4 的正式标题为 **"Acoustic Imaging for UAV Detection: Dense Beamformed Energy Maps and U-Net SELD"**。本页早期草稿及 `index.md` 使用的标题 "Beamformed 360° Sound Maps" 对应较早版本（v1 的副题），**文件名保持不变**以免断链，但正文以 PDF v4 的标题与内容为准。

本地 PDF：[raw/articles/2508.00307.pdf](../../../raw/articles/2508.00307.pdf)

```yaml
- 论文: Acoustic Imaging for UAV Detection (U-Net SELD) — 2025
  ├── 要解决什么问题: 户外长距离声源/无人机定位在低 SNR 下受限——高频成分快速衰减、环境噪声部分空间相干，传统 DAS 峰值法误检高；端到端回归又依赖大训练集和固定阵列。把 SSL/SELD 重构为"波束形成能量图上的密集语义分割"
  ├── 核心方法: DAS 波束形成 az-el 能量图 → 频域分箱 → 极坐标重投影 → (Attention)U-Net 分割 → 质心后处理出 DoA
  ├── 属于哪个分支: 波束形成声学图 + 语义分割的 SSL/SELD（DSP 前端 + DL 后端的混合路线）
  ├── 输入/输出: 输入 (2E×2E×F) 波束能量谱张量（无人机 F=16 / TAU F=64）；输出 2E×2E 二值或 per-class 占据 mask → 质心 → (azimuth, elevation)
  ├── 关键trick: 极坐标重投影对齐球面几何；GPS 遥测监督 + 10° 半径阈值造 mask；"no-drone" 静音增强 + Tversky loss 压误检；操作在能量图 → 阵列无关可迁移；skip-attention（Optuna 选出）
  ├── 数据集: 自建 24 通道 DJI Air 3 无人机数据集（46GB 公开，DOI 10.26183/07nm-4p35）+ 交叉验证用 DCASE 2019 TAU Spatial Sound Events (Task 3)
  ├── 对比了谁: （Test 1 unseen）DAS-FD / DAS-TD / MUSIC / MVDR / SRP-PHAT；（TAU）SELDnet / Baseline SELDnet / w2v-SELD
  ├── 性能上限: 无无人机 5min 误检率 14.9%（波束形成 67.0%）；TAU 单源 F1=79.0% DoA=3.0°；两源 F1=68.0% DoA=4.9°
  ├── 参数量: 论文未报总参数——U-Net 64 base filters、depth 3、3×3 核、skip-attention
  ├── 消融关键发现: 单源→两源 F1 79.0→68.0（缺时序关联）；静音增强 + Tversky 使 FP 67%→14.9%；极坐标重投影是半球场景必需（TAU 仰角窄则不用）
  ├── 遗留问题(你的机会): 时序关联（未来 Mask R-CNN/YOLACT++/VisTR）；多实例跟踪；重叠声源 F1 仍低；总参数量/RTF 未量化；E 值/网格尺寸未明确
  └── 跟哪篇像: DeepWave(声学成像/polar 灵感) + Direct-Path Dominance Test(U-Net+波束图) + Mechanical Fault SSL(图复原再定位)
```

## 一、研究任务与对象

| 维度 | 详情 |
|------|------|
| **任务** | 声源定位（[[DOA 波达方向估计]]）/ [[SELD 声事件定位与检测]]，但把输出**重参数化**为球面语义分割（spherical semantic segmentation）：分割 az-el 能量图上的"有声区域" |
| **核心问题** | 传统 DoA 是点估计（角度回归/分类），不如"分割整个声场"——检测（有没有源）、定位（在哪）、分类（什么类型）可从**一张 mask** 联合涌现 |
| **方法类型** | 混合（hybrid）：DAS 波束成形前端（廉价、可解释的空间图）+ U-Net 后端（去噪/正则化图结构、锐化主瓣、抑制旁瓣）+ 质心后处理 |
| **阵列类型** | 自建 **24 通道**阵列：3 条腿各 6 个 Rode 麦克风（共 18，直立四面体）+ 6 个水平圆环（"yellow" ring）；阵元间距 4 cm–1.1 m，为 **200–4000 Hz** 频段的混叠与方向分辨率折中优化；TAU 交叉验证用 4 麦正四面体（有效半径 4.2 cm） |
| **声场假设** | 远场（平面波），DAS 延迟叠加 |
| **输出形式** | 二值（无人机）/ per-class（TAU 多分类）空间占据 mask ∈ {0,1}^(2E×2E) → 质心 → (az, el)，**离散网格但质心恢复连续方向** |
| **数据集** | 自建 UAV 数据集（DJI Air 3，46GB 公开）+ DCASE 2019 TAU Spatial Task 3 |
| **参数量** | U-Net：64 base filters、depth 3、3×3 核（论文未报总参数量） |

## 二、整体架构

```
24 通道麦克风阵列 (18 四面体 + 6 圆环; 间距 4cm–1.1m)
    │  采样 48kHz；4× Zoom F6 (各 6ch) 用合成脉冲同步 → ±1 sample ≈ 7mm 声学误差
    ▼
DAS 波束成形：方位 [-180°,180°] × 仰角 [0°,90°]，4° 分辨率，100ms 窗
    → 每个方向延迟-叠加出 4800 点波形 → 3D tensor (A × E × T)
    │
    ▼
实数 FFT（矩形窗、无重叠）→ 只保留 200–2200 Hz（DJI Air 3 主能量）
    → 均匀分成 F=16 bins → 每帧跨方向全局归一化 → tensor (A × E × F)
    │
    ▼
极坐标重投影：仰角→径向距离（90°=圆心，0°=外缘）；方位→圆周角度
    → 方形网格 (2E × 2E × F)  ← 对齐球面几何，减少卷积畸变
    │
    ▼
(Attention) U-Net：64 base filters, depth 3, 3×3 核, skip-attention
    │  Optuna 搜出的最佳配置；loss 见下
    ├─ 无人机二分类：Tversky loss（控制 FP/FN 权衡，对抗前景极度稀疏）
    └─ TAU 多分类：multilabel Dice + BCE-with-logits + per-class 正权重
    │
    ▼
预测 mask ∈ [0,1]^(2E×2E)
    │  sigmoid 阈值 0.5 → 3×3 腐蚀（若腐蚀清空则回退到未滤波 mask）
    ▼
质心 centroids：对激活像素集 S 求算术平均 → (azimuth, elevation) 方向估计
```

关键尺寸：A = 方位 bin 数 = 360°/4° = 90；E = 仰角 bin 数（0–90° / 4° = 22.5，论文未显式给出 E 值，详见 §八存疑）。输入张量实际约为 46×46×16。

## 三、为什么这么做？（Motivation）

1. **户外长距离是 SNR 受限问题**：距离一远，无人机高频分量快速衰减，而环境噪声（风、植被、车流）又部分空间相干，等效阵增益下降。→ 传统 DAS 峰值法在这种场景分辨率和鲁棒性都撑不住。
2. **纯端到端回归的两难**：全训练 DL 模型抗噪、能检测+定位+分类，但通常要大型标注训练集，且把网络绑死在原始多通道输入和固定阵列几何上。
3. **混合路径的分工**：保留一个计算极简单的 DAS 前端产生**可解释的空间图**，让学习只做"去噪 + 正则化图结构"（锐化主瓣、抑制旁瓣、补低频谱宽），而不是直接啃原始多通道波形。→ 低延迟、可实时、阵列无关可迁移。
4. **点估计 → 密集分割**：分类型 mask 同时回答"有没有源 / 在哪 / 是什么"，与声学相机（acoustic camera）的"把声音变成图像"直觉一致，可复用成熟的 CV 语义分割架构。

## 四、之前的人怎么做不了？（Limitation → Gap）

| 方法 | 能做 | 不能做 |
|------|------|--------|
| 传统 DAS / [[GCC-PHAT 广义互相关]] / [[SRP-PHAT]] / [[MUSIC 算法]] / [[MVDR 最小方差无失真响应]] | 低噪声单源高精度 | 噪声/混响/多源退化；[[MUSIC 算法]]/ESPRIT 假设窄带非相干 + 完美阵列校准；不做分类 |
| 端到端 SELD（[[SELD CRNN 2018]] / w2v-SELD） | raw 多通道上高 F1 + 低 DoA 误差 | 依赖原始多通道 + 固定阵列几何；无法直接给出"空间占据图 / 声学成像"；需要大训练集 |
| 声学相机 / [[DeepWave Acoustic Imaging 2019]] | 学习式实时声学成像 | 早期多为单帧或 RNN，未做"分割式多分类 SELD" |
| 之前 U-Net 类思想（Lee et al. 2021 MSSP 校正 DAS；AVS Zhou et al. 2023） | 子度级 / 视听分割 | AVS 依赖视觉（视野外/不可见就失效）；rectangular az-el 网格在半球上有球面畸变 |
| **本文** | DAS 前端 + 轻 U-Net 分割，检测+定位+分类单输出联合，阵列无关 | 单帧分割**无时序关联** → 重叠/瞬时事件 F1 掉（见 §六/§七） |

## 五、核心 trick：这篇文章到底靠一个 idea 还是叠 trick？

**核心只有一个 idea**：把 SSL/SELD 的输出参数化从"类别活动 + DoA 回归"换成"az-el 网格上 per-class 空间占据 mask"，DoA 不再回归、改用质心（centroiding）这个简单几何后处理从 mask 里读出——检测、定位、分类从一张分割图一次性涌现。

围绕这个 idea 叠了几个**聪明的工程选择**：

```
✓ 极坐标重投影 (polar reprojection)：仰角映射成半径、方位映射成角度
    → 把半球 az-el 矩形网格在近天顶处的畸变摊平，让卷积贴合球面几何（明确致敬 DeepWave）
✓ GPS 监督 + 10° 半径阈值造 mask：以 GT 方向为中心，10° 内的像素标 1 其余标 0
    → 物理宽容：低频频谱宽、高频旁瓣导致的模糊都被允许，模型学的是"平滑、可解释"的高斯状源区域
✓ no-drone 静音增强 + Tversky loss：训练集混入 ~静音段，Tversky 显式控 FP/FN 权衡
    → 防 "ghost detection"（单纯在含源段上训练会学出大量假阳）
✓ 阵列无关可迁移：网络吃的是波束能量图而非原始多通道 → 换麦克风配置只需重新做 DAS 前端
✓ skip-attention (Attention U-Net)、64 base filters、depth 3、3×3 核、lr=0.005 —— 全部由 Optuna 统一搜出
```

不是"十层 trick 堆叠"，而是一个干净的范式 + 若干避坑工程。

## 六、实验里哪个消融最关键？

这篇**没有做经典的结构消融表**，最接近"消融"的是四处设计决定的证据：

1. **静音增强 + Tversky loss 的效力（最硬的数字）**：在 5 分钟"无无人机"录音上，波束形成峰值法误检率 **67.0%**，U-Net 降到 **14.9%**。这是"在仅含源段上训练会学出一堆假阳"最直接的量化证据，也是 [31] Yalta et al. 结论（训练集要掺静音帧）在分割范式下的复现。

2. **极坐标重投影的必要性（几何）**：UAV 场景覆盖上半球（仰角 0–90°），近天顶采样与标签几何急剧畸变 → 必须 polar；TAU 场景仰角被限制在 -40°~40°、矩形网格无需 polar。同一条 pipeline 两种投影，凸显这是**按几何适用性选择**而非万能组件。

3. **Optuna 选出的最佳配置**：F=16 bins、64 base filters、depth 3、3×3 核、lr=0.005、skip-attention（注意力门加在跳连上）。注意力门被选中，说明"让 U-Net 聚焦声源区域"对该任务有真实增益。

4. **单源 vs 两源子集（最能暴露问题的一条）**：TAU 上，只保留单个活跃源帧时 F1=79.0% / DoA=3.0°；完整"最多两源"评估掉到 F1=68.0% / DoA=4.9°。这个**79→68 的落差**是整篇最关键的"隐性消融"——它证明逐帧分割缺少显式时序关联与多实例跟踪，重叠/瞬时事件（敲、关门、键盘、抽屉声）是纯粹 frame-wise 分割的天花板。

## 七、整体结果

### 无人机数据集（自建，两个测试切分）

> 说明：UAV 部分的角误差（Fig.5）、FNR（Fig.4）、Test 1 对比（Fig.6）**均以柱状/曲线图呈现，正文没有给出逐点数值**。下面是文本中可落实的确定数字与趋势。

| 指标 | 结果 |
|------|------|
| **误检率（FP rate，5min 无无人机）** | 波束形成 **67.0%** → U-Net **14.9%** |
| **无无人机场景判定** | 无目标信号，用预测质心的标准差衡量——U-Net 显著更稳 |
| **FNR vs 距离**（0–50 / 50–100 / 100–200 m 三 bin） | 波束形成在三 bin 全高于 U-Net，**100–200 m 差距最大**（能量弱）；U-Net 更抗衰减与环境变化 |
| **角误差 vs 距离** | 波束形成随距离单调增大（>100 m 尤其明显）；U-Net 全距离 bin 更低，**50–100 m 的挑战区在 Test 1 环境不匹配下仍稳定** |
| **101 m 实例（Fig.3）** | 波束形成最大能量点偏离 GT（黑 X）；U-Net 质心（蓝三角）几乎正中 GT |
| **Test 1（unseen，Site 2）vs 经典 SSL** | 对比 DAS-FD、DAS-TD、[[MUSIC 算法]]、[[MVDR 最小方差无失真响应]]、[[SRP-PHAT]]：短距相当，**~90 m 起经典方法误差陡增**；U-Net 误差同样随距离上升但退化明显更慢（能抑制伪峰） |

### DCASE 2019 TAU Spatial Sound Events（多分类交叉验证，Table 1）

TAU 预处理差异：4 麦正四面体（有效半径 4.2 cm）、1–2 个同时活跃事件、距阵列 1 m/2 m、SNR ≈ 30 dB；DAS 网格 4°、10° 容差造 mask；**不用 polar**、频率范围 100–10,000 Hz、**F=64 bins**；Dice+BCE per-class 加权、macro-F1 选模。

| 模型 | F1 (%) | DoA 误差 (°) |
|------|:------:|:-----------:|
| SELDnet [Kapka & Lewandowski] | **94.7** | 3.7 |
| Baseline SELDnet [Adavanne] | 83.1 | 38.1 |
| w2v-SELD | **94.7** | 4.7 |
| **U-Net（全评估，最多两源）** | 68.0 | **4.9** |
| **U-Net（单源子集）** | 79.0 | **3.0** |

→ 定位精度（DoA 误差）**能打**：两源 4.9° 接近 w2v-SELD 的 4.7°，单源 3.0° 甚至优于所有 baseline；但**检测 F1（68%）明显落后**于端到端 SELD（94.7%），差距正是叠加重叠源头缺失时序关联所致。

## 八、还剩什么问题没解决？

1. **没有时序关联**：重叠/瞬时事件 F1 掉（79→68）。论文自认正在开发多帧输入的时序变体，future work 点名用实例分割范式 **Mask R-CNN / YOLACT++ / VisTR** 做显式时序关联 + 多源实例跟踪。
2. **多实例跟踪缺位**：分割是逐帧独立的，同一帧多个重叠源会被合并或分裂成竞争假设。
3. **检测落后于定位**：TAU 上 F1 68% vs 端到端 SELD 94.7%——分割范式目前"定位好、检测弱"。
4. **UAV 指标图化、无单值汇总**：角误差/FNR 只在柱状图里，正文无总平均角误差数字；>100 m 的误差仍在上升。
5. **参数量与实时性未量化**：论文强调"低延迟/可实时"但没给 RTF、FLOPs 或总参数量。
6. **mask 容差 10° 是超参**：论文自己也指出，mask 半径应匹配阵列有效分辨率——麦少主瓣宽就放大容差，孔径大/麦密可收窄。
7. **声源数上限低**：无人机单源 + TAU 最多两源，更多源/更强混响未验证。

### 存疑 / 需查原 PDF

> [!question] E 值（仰角 bin 数）未显式给出
> 论文只写"分辨率 4°"与"方形网格 (2E × 2E)"。仰角 [0°,90°]/4° = 22.5，非整数；E 到底是 22、23 还是别的取整方式，输入张量的确切边长（约 46×46）需查原 PDF 或代码确认。

> [!question] Tversky loss 的 α/β 权重未给出
> 正文只说明用 Tversky 控制 FP/FN 权衡，未给具体的 α、β 值；Dice+BCE 的 per-class 权重也只描述为"按负/正像素比计算"，无具体数值。

## 九、跟哪篇像

**直接灵感 / 前身**
- [[DeepWave Acoustic Imaging 2019]] — 实时声学成像 + "空间图对齐球面几何"（polar 重投影明确致敬 DeepWave）
- Lee et al. 2021（MSSP 107959，**未入库** ⚠️）— U-Net 校正 DAS 低频/抑制高频旁瓣、子度级精度，是"U-Net 吃波束图"最直接的同类
- [[Direct-Path Dominance Test 2020]] — U-Net + 波束成形图的前驱（但它筛 TF bin 喂 SRP-PHAT，不是分割声场）
- Attention U-Net（Oktay et al. 2018，**未入库** ⚠️）— skip-attention 来源

**架构演进链（CV 迁移 → 声学图）**
```
U-Net (2015, 医学分割)
    ↓
Attention U-Net (2018, 注意力门)
    ↓
DeepWave (2019, 声学成像 + 球面几何) / AVS (2023, 视听分割, 依赖视觉)
    ↓
本文 (2025, 去视觉、DAS 前端、GPS 监督、Tversky 分割式 SSL/SELD)
    ↓ (future work)
Mask R-CNN / YOLACT++ / VisTR 实例分割 → 时序关联 + 多源跟踪
```

### 6. 本论文在库中的位置关联

| 维度 | 论文 | 关系 |
|------|------|------|
| **前身/基石** | [[DeepWave Acoustic Imaging 2019]] | 声学成像 + "极坐标对齐球面几何"的直接灵感来源，论文在结论里点名致敬 |
| **前身/基石** | [[Direct-Path Dominance Test 2020]] | 库内最早的 "U-Net + 波束成形图" 先例——但它用 U-Net 选直达声 TF bin 再喂 SRP-PHAT，本文则直接分割整个声场 |
| **前身/基石** | Lee et al. 2021 MSSP ⚠️ 疑似关联，需用户确认 | 未入库；是"U-Net 校正 DAS 低频/旁瓣、子度级多源"最同类的工作，论文 [28] 引用了它 |
| **后续/扩展** | 无 | 2025 前沿预印本，库内暂无直接继承本文的后续页（future work 指向 Mask R-CNN/YOLACT++/VisTR 实例分割路线）⚠️ 待随库扩充 |
| **同分支竞品** | [[SSLIDE 2021]] | 同为"空间 likelihood 图 + 图复原后定位"，但用双 decoder 解耦定位/混响缓解，本文用单 U-Net + 质心 |
| **同分支竞品** | [[Mechanical Fault SSL 2024]] | 同为"SRP-PHAT 图 → U-Net → clean map → 定位"的图复原范例，本文是 DAS 图 → 分割 mask，思路同源、任务域不同（机械 vs 无人机） |
| **同分支竞品** | [[Robust Sound Source Tracking SRP-PHAT 3D CNN 2021]] | 同为时序声学图 + CNN，但它用因果 3D CNN 做时序跟踪，本文是单帧 2D 分割（缺时序正是它被本文 future work 指出要补的） |
| **同分支竞品** | [[Icosahedral CNN DOA 2023]] | 都解决"球面几何对齐"——本文用 polar 重投影，它用 icosahedral 网格 + 几何 CNN，两种几何策略可对照 |
| **跨分支类比** | [[SELD CRNN 2018]] | 本文在 TAU Task 3 上直接对比 SELDnet 及其 baseline——分割式 SELD vs CRNN 回归式 SELD 的胜负手（定位追平、检测落后） |
| **跨分支类比** | [[LAM Self-Supervised DOA 2025]] | 都为球面声学映射，但 LAM 走自监督免标签，本文靠 GPS 遥测强监督——监督源是两条线的分水岭 |
| **跨分支类比** | [[GRAM Spatial Foundation Model 2025]] | 空间音频基础模型（大模型/自监督路线）vs 本文轻量 DAS+U-Net，代表"通用表征"与"可解释空间图"两种范式 |

### 7. 江湖地位

```
2025 | SSL/声学成像 | 把 SSL/SELD 重构为"DAS 波束形成能量图上的语义分割"，感知输出从点回归升级为
           空间占据 mask（检测+定位+分类一图出），并开源 24 通道无人机 + GPS 监督数据集 (46GB) →
           → 为"声学相机分割式定位 / 阵列无关可转移"提供范式
           → 但检测 F1（68%）被端到端 SELD（94.7%）压制，"单帧分割缺时序"成为被后续
             实例/时序分割路线（Mask R-CNN / VisTR）明确填补的短板
```

---

*一句话 takeaway：把"找方向角"换成"分割整个声场"——让便宜的 DAS 前端产出一张可解释能量图，轻量 U-Net 从 mask 里一次吐出检测、定位、分类，定位精度能打（TAU 单源 3.0°、两源 4.9°），但失去时序的逐帧分割接不住重叠声源（F1 从 79 掉到 68），下一棒交给时序/实例分割。*