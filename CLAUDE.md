# LLM Wiki — Schema & Conventions

This document defines how this wiki is structured, maintained, and expanded. Every LLM session should read this file first before performing any wiki operations.

---

## 目录结构 Directory Structure

```
/
├── CLAUDE.md              # ← 本文档：Schema / 配置
├── raw/                   # 原始资料（不可变，LLM 只读不写）
│   ├── assets/            # 下载的图片、附件
│   ├── papers/            # 学术论文 PDF
│   ├── articles/          # 教程、博客、技术文章
│   └── notes/             # 用户自写笔记、草稿
├── wiki/                  # 语音增强 & 音源分离 Wiki
│   ├── index.md           # 内容目录
│   ├── log.md             # 操作日志
│   ├── overview.md        # 顶层综述
│   ├── entities/          # 实体页面（模型、工具等）
│   ├── concepts/          # 概念页面（理论、方法、术语等）
│   ├── sources/           # 资料摘要页面
│   └── topics/            # 主题页面（跨实体的综合论述）
├── wiki_array/            # 声源定位 & 阵列处理 Wiki
│   ├── index.md           # 内容目录
│   ├── log.md             # 操作日志
│   ├── overview.md        # 顶层综述
│   ├── entities/          # 实体页面
│   ├── concepts/          # 概念页面（DOA、相位图、波束成形等）
│   ├── sources/           # 资料摘要页面
│   └── topics/            # 主题页面
├── wiki_low_latency/      # 严格因果超低时延语音增强 Wiki
│   ├── index.md           # 内容目录
│   ├── log.md             # 操作日志
│   ├── overview.md        # 顶层综述
│   ├── entities/          # 实体页面
│   ├── concepts/          # 概念页面（延迟、因果性、保真等）
│   ├── sources/           # 资料摘要页面
│   └── topics/            # 主题页面
├── flashcards/             # 概念记忆卡（易忘概念的自测卡片）
│   ├── index.md           # 卡片索引
│   └── ...                # 每个易忘概念一个 .md 文件
├── outputs/               # 会话产出（工作性中间产物）
│   ├── qa/                # 问答笔记
│   ├── reports/           # 报告
│   ├── figures/           # 图表
│   └── experiments/       # 实验计划与记录
```

## 文件规范 Page Conventions

### YAML Frontmatter

每个 wiki 页面都应当包含 YAML frontmatter：

```yaml
---
title: 页面标题
type: entity | concept | source | topic | overview | flashcard | experiment
created: 2026-05-28
updated: 2026-05-28
tags:
  - tag1
  - tag2
sources: [source-page-1, source-page-2]  # 关联的源材料
related:                                 # 关联的 wiki 页面
  - [[related-page]]
---

### 链接规范

- 内部链接使用 Wiki 格式：`[[页面名]]` 或 `[[目录/页面名]]`
- 所有跨页面引用都应使用 Wiki 链接（便于 Obsidian 图谱视图）
- 外部链接使用 Markdown：`[文字](url)`
- 图片使用嵌入：`![[图片名.png]]`

### 写作风格

- 中文为主，术语保留英文原文（首次出现时标注）
- 保持客观中立，标注不确定或存疑的内容
- 每个页面聚焦一个主题，如果内容过长应考虑拆分

## 工作流程 Workflows

### 1. 摄取 Ingest

当用户放入新的原始资料并说"请处理这篇"时：

1. **读取**原始资料（raw/ 目录下的文件）
2. **讨论**：与用户确认关键要点和需要强调的方向
3. **写入资料摘要**：在 wiki/sources/ 下创建摘要页面（**必须填写第6节关联矩阵 + 第7节江湖地位**）
4. **更新实体/概念页**：查找并更新涉及的实体和概念页面
5. **更新 index.md**：添加新页面的条目
6. **更新 log.md**：追加操作记录
7. **自动关联搜索** ← NEW！
   a) **标签匹配**：用本论文 tags 搜库 index，找同标签论文
   b) **方法匹配**：搜库中"用了相同方法关键词"的论文
   c) **反向前身匹配**：搜库中"future work 提到本论文技术"的论文
   d) **竞品匹配**：搜"同一年+同任务+不同方法"的论文
   搜索结果 → 填入 source 第6节"关联矩阵"
   不确定的 → 标注"⚠️ 疑似关联，需用户确认"
8. **通知交叉关系** ← NEW！
   - 告诉用户新增了哪些交叉链接
   - 如果这些交叉关系触发了"新实验想法" → 写入 outputs/experiments/（见工作流6）
9. **检查 consistency**：如新资料与现有内容矛盾，在相关页面标注

> 一篇源文章可能涉及 5-15 个 wiki 页面。建议一次处理一篇。

### 2. 查询 Query

当用户提问时：

1. **读 index.md**：确定哪些页面与问题相关
2. **读相关页面**：深入阅读
3. **综合回答**：引用来源，提供带链接的回答
4. **存档有价值的回答**：如果回答涉及新的洞察、对比或分析，写入 outputs/qa/ 或 wiki/ 的适当位置

### 3. 检查 Lint

定期或应要求检查 wiki 健康度：

- 页面间是否存在矛盾
- 是否有过时的信息需要更新
- 是否有孤立页面（没有入链）
- 是否有重要概念被提及但没有独立页面
- 是否有缺失的交叉引用
- 是否需要添加新的标签或分类

### 4. 更新现有页面

当新信息影响已有页面时：

- 追加内容而非删除（除非确认错误）
- 在页面顶部标注 `> [!updated]` 提示
- 对于矛盾的信息，使用 `> [!contradiction]` 标注
- 更新页面的 `updated` 字段

### 5. 概念记忆卡 Flashcard ← NEW！

#### 目的

用户经常忘记或混淆的概念 → 写入 flashcards/ 目录 → 定期自动复习 → 加深记忆。

#### 触发条件

当用户表现出对某个概念的不熟悉时（包括但不限于追问定义、说"忘了"、混淆两个概念），LLM **必须**：

1. 检查 `flashcards/index.md` 中是否已有该概念
2. **如果有** → 更新卡片（追加新的解释角度、增加自测题、更新 `last_reviewed`）
3. **如果没有** → 创建新的 flashcard
   - 文件名：`概念名.md`
   - 放入对应域的 `flashcards/` 下
   - 按下方模板填写
4. 在回答末尾提醒用户：📌 已将此概念写入 flashcards/

#### 触发事件对照表

| 用户行为 | LLM 处理 |
|---------|---------|
| 问"XX是什么意思" | 解释 + 创建/更新 flashcard |
| 说"又忘了XX" | 更新现有卡片（加新的记忆角度） |
| 把 A 和 B 搞混 | 创建"区别对比"闪卡 |
| 问了一个好问题 | 把问题+答案转为闪卡 |
| 说"这个很重要" | 提升卡片优先级 |
| 说"这个我不需要记" | 降低卡片优先级或归档 |

#### Flashcard 模板

```yaml
---
title: 概念名
type: flashcard
created: 2026-07-06
last_reviewed: 2026-07-06
review_count: 0
tags:
  - flashcard
  - wiki_array
difficulty: ⭐⭐
related:
  - [[关联概念页]]
---

## 💡 一句话记忆点

> 最精炼的直觉记忆

## ❓ 问题

触发此卡的问题

## ✅ 答案

分点回答

## 🔍 自测题（下次复习用）

- [ ] 自测题1
- [ ] 自测题2
```

#### 定期复习机制

在每次用户提出新问题前（即在回答的开头或末尾），LLM 应：
- 检查 `flashcards/index.md`，选择最久未复习的 1-2 张卡片
- 在回答后附上：
  > 📌 **今日复习**：[[概念名]] → [一句话记忆点]
  > 想深入回忆可以让我抽问
- 更新卡片的 `last_reviewed` 和 `review_count`

## 论文摘要模板 Paper Note Template

每篇 source 笔记必须包含以下**5 个分析维度**（写在笔记正文中，可作为章节标题）：

```
1. **他们为什么这么做？（motivation）**
   - 现有方法有什么不足？
   - 这个不足为什么重要？

2. **之前的人怎么做不了？（limitation → gap）**
   - 之前的 SOTA 有什么局限？
   - 这个 gap 为什么至今没解决？（算力？数据？架构？）

3. **这个做法核心 trick 是什么？**
   - 只有一个 idea 有用，还是叠了十个 trick？
   - 哪个 trick 最关键？

4. **实验里哪个消融最关键？**
   - 去掉某个模块，性能掉多少？
   - 哪个设计决定最敏感？

5. **这个方向还剩什么问题没解决？（future work / limitation）**
   - 论文自己承认的局限
   - 你读出来的隐藏问题

6. **本论文在库中的位置关联（cross-reference matrix）** ← NEW！
   - **前身/基石**：它基于或受哪篇启发？那篇留下了什么 gap 是这篇解决的？
   - **后续/扩展**：库中哪些论文扩展或改进了这篇？怎么改的？改了多少？
   - **同分支竞品**：同一时期、同一任务、不同方法——和这篇比优劣在哪？
   - **跨分支类比**：不同任务但用了类似思路的论文——思路迁移的价值在哪？
   - 不确定的关联用"⚠️ 疑似关联，需用户确认"标注

7. **一句话总结"江湖地位"** ← NEW！
   格式：[年份] [方向] [核心贡献] → [被谁怎么用了/被谁超越了]

   例子：
   ```
   2018 | SELD | 奠基任务定义+CRNN基线 → 所有后续 SELD 的对比 baseline
   2023 | SELD | 提出 S+T 分离注意力 → 2025 被 C+S+T 三维注意力 (CST) 超越
   2025 | SELD | 0.39M 达到 SOTA → 轻量化 SELD 的方向标
   ```

```

同时，在笔记开头用 YAML 代码块做**快速索引卡片**：

```yaml
- 论文: [论文名称](年份)
  ├── 要解决什么问题: ...
  ├── 核心方法: ...
  ├── 属于哪个分支: ...
  ├── 输入/输出: ...
  ├── 关键trick: ...
  ├── 数据集: ...
  ├── 对比了谁: ...
  ├── 性能上限: ...
  ├── 参数量: ...
  ├── 消融关键发现: ...
  ├── 遗留问题(你的机会): ...
  └── 跟哪篇像: ...
```

以上模板适用于本 vault 中所有域（wiki/ 和 wiki_array/）的论文笔记。

## 标记规范 Callout Conventions

```markdown
> [!note] 补充信息
> 对正文的补充说明

> [!question] 存疑
> 不确定的内容或需要进一步验证的信息

> [!warning] 需要注意
> 该信息可能已过时或需要谨慎对待

> [!contradiction] 矛盾
> 不同来源对此存在不同说法
```

## Dataview 查询示例

所有 wiki 页面都包含 YAML frontmatter，因此可以使用 Dataview 插件生成动态列表：

~~~dataview
TABLE type, created, updated
FROM "wiki"
SORT updated DESC
~~~

## 日常维护建议

- **每次处理一篇源文章**，与用户讨论后再更新 wiki
- **回答后归档**：有复用价值的问答写入 outputs/qa/
- **定期 Lint**：每周或每 10 次摄取后做一次健康检查
- **git 提交**：定期 commit，保持版本历史清晰
- **概念复习**：每次对话末尾附 1-2 张 overdue flashcard

### 6. 实验笔记 Experiment Notebook ← NEW！

当论文摄取完成 + 关联分析完成，LLM 应主动思考：

"这篇论文的技术和库里哪篇可组合形成新实验？"

- **有新想法** → 在 `outputs/experiments/index.md` 创建实验计划并通知用户
- **无组合思路** → 记录"当前无组合思路"

#### 实验笔记模板

```yaml
---
title: 实验名称
type: experiment
status: planned | running | completed | failed
started: 2026-07-06
completed:
hypothesis: "一句话假设"
baseline: "被对比的方法"
results:
  - metric: SELD Score
    baseline: "0.422"
    current: ""
  - metric: Params (M)
    baseline: "0.39"
    current: ""
notes:
  - "待跑：先做 S-Mamba 单轴替换"
  - "代码位置：outputs/experiments/s_mamba_ablation.py"
---
```

---

## 领域特化 Domain Specialization

本 vault 覆盖三个独立方向，分别由独立的 wiki 目录管理：

| Wiki 目录 | 方向 | 核心任务 |
|---|---|---|
| `wiki/` | 语音增强 & 音源分离 | 去噪、去混响、分离、DSP+DL 混合 |
| `wiki_array/` | 声源定位 & 阵列处理 | DOA 估计、波束成形、空间滤波 |
| `wiki_low_latency/` | 严格因果超低时延语音增强 | 约 2 ms 算法时延、低 SNR 噪声抑制、人声保留、端侧部署 |

三个 wiki 通过交叉链接关联（DOA/阵列处理可作为增强前置步骤），但页面独立管理，互不混杂。

### wiki/ — 语音增强与音源分离

处理该领域内容时，除遵守上述通用流程外，还必须遵循以下特化规则。

#### 论文处理重点

当摄取 `raw/` 中的音频/语音论文时，除了常规 source 摘要外，必须特别关注：

1. **研究任务与对象**
   - 任务类型：语音增强 (Speech Enhancement)、音源分离 (Source Separation)、语音分离 (Speech Separation)、去混响 (Dereverberation)
   - 噪音类型：稳态噪声 (stationary)、非稳态噪声 (non-stationary)、人声噪声 (babble)、环境噪声 (car, street, office, crowd)、混响
   - 采样率：8k/16k（窄带/宽带）/ 48k（全频带）
   - 实时性要求：实时 (real-time, RTF<1) vs 离线 (offline)
   - 输出目标：掩蔽 (mask) vs 频谱幅度 (spectral magnitude) vs 波形 (raw waveform)

2. **技术路线**
   - 信号域：时域 (waveform domain) vs 时频域 (T-F domain) vs 复数域 (complex domain)
   - 传统 DSP 方法：MMSE、谱减法 (Spectral Subtraction)、Wiener Filter、谱幅度估计器
   - 深度学习架构：RNN/GRU/LSTM、CNN、Transformer、Dual-Path RNN、TCN
   - 关键设计：复数网络 (complex-valued networks)、注意力机制、跳跃连接 (skip connection)
   - 特征类型：BFCC、MFCC、log-mel spectrogram、raw waveform、复数频谱特征
   - 混合架构：DSP + DL（如 RNNoise 用 RNN 替代传统估计器）

3. **公式与推导**
   - 论文中出现的关键公式必须单独整理
   - 不仅要摘录公式，要解释每个符号的物理意义、作用和在论文中的用途
   - 如果论文包含推导过程，应尽可能按步骤重写推导逻辑
   - 重点关注的公式类型：
     - **信号变换**：STFT、iSTFT、DFT 窗函数定义
     - **掩蔽类**：理想比率掩蔽 (IRM)、理想二值掩蔽 (IBM)、复数 IRM (cIRM)
     - **损失函数**：MSE on magnitude、SI-SNR loss、加权损失、感知损失
     - **评价指标**：PESQ、STOI、ESTOI、SI-SNR/SDR、MOS 的计算公式
   - 对重要公式，应在 `wiki/concepts/` 下建立或更新对应概念页，例如：
     - `理想比率掩蔽 IRM.md`
     - `理想二值掩蔽 IBM.md`
     - `Bark 尺度与临界频带.md`
     - `STFT 短时傅里叶变换.md`
     - `PESQ 感知语音质量评估.md`
     - `SI-SNR 尺度不变信噪比.md`

4. **结果与图表**
   - 总结每张关键图/表说明了什么：频谱图对比 (noisy vs denoised vs clean)、指标对比表格、消融实验
   - 如果图表对应某个公式、指标或模型组件，应建立链接
   - 对结论强度做判断：哪些是客观指标直接支持的，哪些是主观听感结论，哪些可能需要复现验证
   - 注意图表是否有缺失（如只有 PESQ 却没有 STOI，或只有宽带结果没有全频带结果）

5. **可复现性**
   - 提取可能影响复现的参数：模型参数量、训练数据规模与来源、数据增强方式、优化器与学习率、损失函数超参数
   - 开源代码链接、预训练模型、commit hash（如有）
   - 如果论文缺少关键训练细节或评估设置的说明，应在"不确定性说明"中明确指出

### PDF 转 Markdown 质量检查

当读取由 PDF 转换得到的 Markdown 论文时，必须检查文本质量。如果发现以下问题，**不能假装理解**，必须向用户反馈：

- 大量乱码、断字、错行
- 公式丢失或公式符号无法识别
- 希腊字母、上下标、矩阵、积分、求和符号显示异常
- 参考文献混入正文，影响理解
- 页面页眉页脚反复插入正文
- 表格结构严重错乱
- 频谱图、框图等图片完全缺失（图片在 PDF 转换中丢失是常见问题，需提醒用户查看原 PDF）

遇到这些问题时，可以先输出文件，但要说明文件中某处公式需要检查，告知用户问题位置或文件名。

在**无法可靠识别公式**时，必须明确写：
> 该公式在当前 Markdown 中无法可靠识别，需要查看原 PDF 或重新 OCR。

### 音频模型/算法处理规则

当摄取 `raw/` 中的音频模型、算法实现、开源项目或技术教程时，应整理关键的技术要点，而不只是总结文字。

每个模型/算法应尽量提取：

1. **模型目标**
   - 这个模型要解决什么任务？语音增强还是音源分离？
   - 最终要达到什么性能指标或工程目标（实时性、低复杂度、高保真等）？

2. **模型架构**
   - 网络结构图或整体管线框图
   - 层数与各层配置：隐藏层数、每层单元数/通道数、总参数量
   - 关键设计元素：Skip connection、Dual-path 结构、Attention、复数网络层、归一化方式
   - 输入输出的维度和格式

3. **输入输出**
   - 输入形式：raw waveform 波形 / 频谱幅度 (magnitude) / 复数频谱 / 对数功率谱 / MFCC/BFCC 特征
   - 输出形式：mask (掩蔽) / 频谱幅度 / 波形 / 理想比值 (如 IRM)
   - 输入输出的数学关系（如 mask = estimated_output / input_magnitude）

4. **训练细节**
   - 损失函数设计：公式形式、多任务损失、加权策略
   - 优化器与学习率策略
   - 训练数据规模、来源、数据增强方法
   - 训练中值得注意的技巧或 trick

5. **关键公式**
   - 损失函数公式及其中各符号含义
   - Mask 计算方式
   - 特征提取公式
   - 后处理公式（如增益平滑、相位重建）

6. **评估指标**
   - 使用了哪些客观指标：PESQ, STOI, ESTOI, SI-SNR, SDR, SNR, LSD 等
   - 是否包含主观评估：MOS 听感测试、A/B 测试
   - 各指标的数值结果与对比基线

7. **可迁移性**
   - 该模型的方法是否可迁移到类似任务（如语音增强 → 去混响）
   - 已知限制：对特定噪声类型的偏好、对未见噪声的泛化能力
   - 计算复杂度：Mflops / MACs / RTF (实时因子) / CPU/GPU 使用率
   - 常见使用场景和注意事项

对于重要模型，应在 `wiki/sources/` 创建模型摘要，在 `wiki/concepts/` 更新相关概念，在 `wiki/topics/` 中维护"语音增强模型对比"或"音源分离方法演进"等综合页面。

### wiki_low_latency/ — 严格因果超低时延语音增强

该 Wiki 是语音增强方向的约束型子方向，重点不是单纯追求 PESQ 或 RTF，而是在**不读取未来观测样本**的前提下，研究约 2 ms 算法延迟、低 SNR 抑噪和人声保留的共同约束。其专用规则如下：

1. **延迟与因果性必须拆开报告**
   - 严格因果 (strict causal)：任意输出样本只依赖当前/过去输入和历史状态；禁止 centered STFT、右侧 padding、双向统计和完整 chunk 的 future attention。
   - 约 2 ms 是算法/缓冲目标，不等于模型计算耗时；必须分别记录算法延迟、模型 p50/p95/p99、I/O buffer、ADC/DAC 和端到端 capture-to-playback。
   - `RTF < 1` 只能说明平均吞吐足够，不能代替 deadline 或 p99 证据。

2. **论文与模型页面必须增加低时延字段**
   - 采样率、分析/合成窗、hop、chunk、look-ahead、warm-up、group delay、状态和最新可读输入样本。
   - 对每一层审计 padding、归一化统计、缓存状态和 future leakage；标记为 `strict_causal`、`low_look_ahead` 或 `non_causal`，并给出证据。
   - 参数量、MAC/s 或 FLOPs、峰值 RAM/SRAM、量化精度、运行时和目标硬件必须与质量结果一起记录。

3. **人声保留是独立的一等目标**
   - 低 SNR 至少按 −10/−5/0/5 dB 和噪声类型分层，重点覆盖 babble、竞争说话人、瞬态噪声和未见噪声。
   - 除 PESQ、STOI/eSTOI、SI-SDR/SI-SNR、DNSMOS SIG/BAK/OVL 外，应记录 false-suppression、SPP/VAD 校准、ASR WER（如可用）、F0/formant/prosody continuity 和 voiced energy 保留。
   - 不能把 BAK 提升而 SIG/可懂度下降描述为无条件改进；需要报告 SIG–BAK trade-off 和失败案例。

4. **部署与恢复属于结果的一部分**
   - 流式 batch=1、长流稳定性、state reset、warm-up、underrun/overrun、deadline miss 处理和 bypass/recovery 必须单独记录。
   - “理论 2 ms”与“目标设备端到端 ≤2 ms”不得混写；没有硬件测量时明确标记为待验证。

5. **本方向的默认最小基线**
   - 优先使用单通道、16 kHz 起步的短 learned-filterbank/causal waveform 或短窗因果 STFT + GRU/小 SSM。
   - 推荐先验证 `baseline → gain floor → SPP 调制 → continuity loss`，再考虑 uncertainty、deep filtering、蒸馏或多通道空间特征。
   - 大型双向 Transformer、diffusion、默认 25–40 ms 前端模型可作上界或参照，不得作为 2 ms 合格系统。

### wiki_array/ — 声源定位与阵列处理

处理 DOA 估计、波束成形、空间滤波等阵列处理方向的论文时，必须遵循以下特化规则：

#### 论文处理重点

1. **研究任务与对象**
   - 任务类型：DOA 估计 / 声源定位 / 波束成形 / 空间滤波 / 声场重建
   - 阵列类型：均匀线阵 (ULA)、均匀圆阵 (UCA)、球阵列 (Spherical Array)、任意阵列
   - 声源数：单声源 vs 多声源
   - 声场假设：近场 (球面波) vs 远场 (平面波)
   - 输出形式：离散分类 (角度网格) vs 连续回归

2. **技术路线**
   - 传统方法：MUSIC、ESPRIT、GCC-PHAT、SRP-PHAT、MVDR、GSC
   - 深度学习：CNN 相位图、GCC 特征 + DNN、特征值分解 + DNN、端到端方法
   - 输入表示：相位图 (Phase Map)、GCC 向量、协方差矩阵、原始波形
   - 关键设计：空间混叠处理、相位卷绕处理、阵列几何泛化

3. **关键概念映射**
   - 涉及的核心概念应在 `wiki_array/concepts/` 下创建独立页面：
     - `DOA 波达方向估计.md`
     - `STFT 相位图与相位信息.md`
     - `SRP-PHAT.md`
     - `GCC 广义互相关.md`
     - `MUSIC 算法.md`
     - `波束成形 Beamforming.md`
     - `空间混叠 Spatial Aliasing.md`

4. **评价指标**
   - 帧级准确率 (Frame Level Accuracy)
   - 角度误差 (MAE / RMSE)
   - 定位成功率 (在一定容差范围内的比例)
   - 混淆矩阵（多声源场景）

---

*本文档会随 wiki 的演化而持续更新。*
