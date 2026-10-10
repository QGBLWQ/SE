---
title: 操作日志（严格因果超低时延语音增强）
type: log
created: 2026-09-16
updated: 2026-10-07
tags:
  - log
  - strict-causal
  - ultra-low-latency
---

# 操作日志

## [2026-09-16] init | 建立新方向 Wiki

- 读取并遵循 [[CLAUDE|CLAUDE.md]] 的 Wiki schema、链接、原始资料和论文处理要求。
- 参考现有 [[wiki/index|语音增强与音源分离 Wiki]]、[[wiki_array/index|声源定位与阵列处理 Wiki]] 和 `ultra_low_latency_causal_se/research_map.md`。
- 建立 `wiki_low_latency/` 骨架：`index.md`、`overview.md`、`log.md`、`entities/`、`concepts/`、`sources/`、`topics/`。
- 方向边界固定为：strict causal、约 2 ms 算法延迟、低 SNR 噪声抑制、人声保留、端侧部署审计。

## [2026-09-16] ingest-pdfs | 归档指定论文原件

原件保存于 `raw/papers/low_latency_causal_se/`。本轮只下载、校验和登记，不创建论文笔记或 source 摘要页。

| arXiv ID | 文件大小（bytes） | 校验 |
|---|---:|---|
| `2409.10358` | 346,274 | ✅ >10 KB |
| `2411.02019` | 996,992 | ✅ >10 KB |
| `2204.09911` | 1,683,895 | ✅ >10 KB |
| `2103.14882` | 281,632 | ✅ >10 KB |
| `2304.08707` | 320,083 | ✅ >10 KB |
| `2111.11606` | 269,206 | ✅ >10 KB |
| `2203.16843` | 756,193 | ✅ >10 KB |
| `2305.08744` | 1,833,545 | ✅ >10 KB |
| `2008.04259` | 483,828 | ✅ >10 KB |
| `2205.05474` | 694,658 | ✅ >10 KB |
| `2307.08858` | 357,554 | ✅ >10 KB |
| `2008.00264` | 844,298 | ✅ >10 KB |
| `2107.05429` | 1,800,200 | ✅ >10 KB |
| `2608.12099` | 476,557 | ✅ >10 KB |

共归档 **14 篇**，没有覆盖已有同名文件。

## 初始检查节点（已完成）

- [x] 确认新 Wiki 名称 `wiki_low_latency/` 和方向边界
- [x] 确认论文原件归档路径和 14 篇论文清单
- [x] 按用户确认后的统一格式逐篇阅读 PDF、建立 source/entity/concept 页面和论文笔记

## [2026-09-16] ingest | 随机摄取 2307.08858

- 从 `raw/papers/low_latency_causal_se/` 的 14 篇 PDF 中随机抽取 `2307.08858`。
- 阅读原 PDF 5 页并进行页面渲染核对；记录 PDF 文本抽取对 Figure 1/2 标签和特殊符号的质量问题。
- 创建 [[wiki_low_latency/sources/2023/GCFSnet 2023]]、[[wiki_low_latency/entities/GCFSnet]] 和 [[wiki_low_latency/concepts/低比特率双耳特征链路]]。
- 在 `wiki_low_latency/assets/` 中保存并嵌入架构页和结果页渲染图。
- 按本方向规则补充 strict-causal/latency ledger、低 SNR/人声保留缺口、端侧 p99 缺失和 cross-reference matrix。
- 当时其余 13 篇尚未阅读；后续完成情况见下方 `ingest-complete` 记录。

## [2026-09-16] ingest-complete | 完成 14 篇论文摄取

- 按原始清单核对到 14 篇 PDF；随机样例 `2307.08858` 加上其余 13 篇均已建立 source 页面。
- 每篇 source 均通过结构检查：YAML frontmatter、快速 YAML 卡、PDF 质量 warning、7 个必需一级章节、公式/符号、结果/消融、strict-causal/latency ledger、cross-reference matrix 和“一句话江湖地位”。
- 每篇论文均建立对应 entity 与论文概念页；13 篇新增论文均有 PDF 页面渲染资产，source 中嵌入方法图或结果/表格图；另补充 3 个共享概念页用于统一低时延和人声保留审计。
- 修正 PercepNet 的 `local_pdf` 指向导入的 `raw/papers/low_latency_causal_se/2008.04259.pdf`，并将 SlowFast-SSM 的图引用统一为 Obsidian 图片语法。
- 索引、概览与本日志均已从“仅原件归档”更新为“14 篇已摄取”；跨论文比较仍需后续建立统一指标表，不能直接把不同数据集/延迟口径的数字排名。

## [2026-09-16] experiment-seed | 关联实验计划

- 按 CLAUDE.md 的摄取后关联流程，建立 [[outputs/experiments/低时延不确定性感知人声保留基线]]。
- 组合短窗严格因果前端、轻量 uncertainty/SPP 调制、gain floor/attack-release 与 continuity loss；计划按增量消融，同时验收 p99/deadline 和弱语音保留，不把训练参考窗误认为推理端未来信息。

## [2026-09-16] audit | 主 agent 最终验收

- 原始清单实际包含 14 篇；扣除先行完成的随机样例 2307.08858 后，剩余数量是 13 篇。13 篇均已完成，未遗漏。
- 剩余论文由 gpt-5.6-luna / max reasoning 子 agent 按论文分工摄取；公共 index、overview、log 由主 agent 统一维护。
- 发现 DCCRN 的 source 页在并发写入中缺失，已依据本地 2008.00264 PDF、entity 页和 concept 页补齐，并重新纳入验收。
- 验收通过：14 个 PDF、14 个 source、14 个 entity、14 个 concept；每个 source 均有 YAML frontmatter、快速 YAML 卡、PDF warning、7 个必需章节、公式/符号、图像引用、延迟/因果证据和 cross-reference matrix。
- 链接检查通过：wiki_low_latency 内部链接 0 个断链，嵌入图像引用 0 个断链，索引/概览/日志中的 wiki、wiki_array 和 research_map 入口均存在。
- 论文级 algorithmic latency、compute latency、capture-to-playback p99 与人声保留证据仍分开记录；笔记完成不等于所有论文都满足约 2 ms strict-causal。

## [2026-09-16] verify | 主线程验收 14 篇摄取页面

- 核对通过：14 个 source、14 个 entity、14 个论文 concept、14 个本地 PDF；另有 3 个供全库复用的低时延/人声保留审计 concept。
- 逐篇检查 source 的 YAML frontmatter、`~~~yaml` 快速索引卡片、PDF 质量 warning、7 个必需一级章节、公式/符号、实验结果与消融、strict-causal/latency ledger、cross-reference matrix、“一句话江湖地位”和图像引用。
- 逐个检查 source 的 `local_pdf` 映射、14 组论文图片资产（首篇 `2307.08858` 保留平铺资产，其余论文按 arXiv ID 分目录）以及 `wiki_low_latency/index.md`、`overview.md`、`log.md` 和页面间 Obsidian/Markdown 内部链接；未发现断链。
- 证据边界保留：论文中的 RTF、算法延迟、look-ahead、质量分数和设备运行时间没有被混写为统一的端到端 p99 或 2 ms 保证；不同数据集/延迟口径不做直接横向排名。

## [2026-09-18] ingest | 知识蒸馏子群 7 篇论文

用户指定 10 篇「知识蒸馏 / 低时延」论文，其中 3 篇（`2204.09911`、`2409.10358`、`2608.12099`）此前已摄取，**本轮实际新增 7 篇**。
原件下载到 `raw/articles/`（9 篇 arXiv + 1 篇 ICASSP 机构版），并同步副本到 `raw/papers/low_latency_causal_se/`。

**未获取**：`Leveraging Non-Causal Knowledge via Cross-Network Knowledge Distillation for Real-Time Speech Enhancement`
（IEEE SPL 2024, vol.31, pp.1129-1133, DOI 10.1109/LSP.2024.3388956，Korea Univ AIDA Lab）。
该文无 arXiv 版本，IEEE 直链需订阅。缺失清单见 `raw/notes/待获取论文 - 知识蒸馏语音增强.md`。

**执行方式**：主 agent 负责规格提取、文本抽取（`pdftotext -layout`）、子 agent 分工撰写、最终审核。
3 个子 agent 撰写 source 页，2 个子 agent 撰写 entity/concept 页，主 agent 统一校验与索引维护。

### 新增页面统计

| 类型 | 数量 | 位置 |
|---|---:|---|
| source | 7 | `sources/{2021,2023,2024,2025,2026}/` |
| entity | 7 | `entities/` |
| concept | 7 | `concepts/` |
| 图片资产 | 12 | `assets/{2309.08144,2408.04267,nakaoka2021}/` |

> 注：`sources/2025/` 目录为本次新建。

### 主 agent 审核结论

- **链接检查**：`wiki_low_latency` 内部 wikilink 475 个、图片引用 38 个，**断链 0**。修正 1 处占位符链接（`DFKD` 页的 `Perceptual... 系列` → `PercepNet Low-Latency Direction 2020`）。
- **数字溯源抽查**：Nakaoka 的 `12.19 / 2.90 / 2,329,942 / 6.71`、2309.08144 的 `32 ms / 1.9M`、RaD-Net 2 的 `960 / 20 ms / 10 ms`、DISPATCH 的 `32 ms / 8 ms / 75%`、DFKD 的 `16 kHz`、Privileged KD 的 `privileged / advantage-reachability / EMA` 均**在原文中可验证**，未发现编造。
- **结构检查**：7 篇 source 均含 YAML frontmatter、`~~~yaml` 索引卡、PDF 质量 warning、7 个必需一级章节、`## 参考资料`。
- **命名规范化**：将子 agent 生成的 `page-N.png` / `hi-N.png` 重命名为库内既有规范 `<id>-pageN-<内容>.png`，并同步更新笔记中的 8 处引用。
- **因果判定纠偏**：子 agent 最初预设「教师-学生结构中 teacher 都非因果」被证伪——`2309.08144` 的 teacher（causal CRUSE）**也是因果的**，已写入对比说明。

### 关键结论

- **7 篇无一满足约 2 ms**：Nakaoka 2021 为 6.71 ms（最近），2309.08144 为 32 ms，Distil-DCCRN / RaD-Net 2 延迟未报告，DFKD 与 Privileged KD 不面向低时延。
- **发现一对文献矛盾**：`2309.08144` 主张两步蒸馏优于加权混合且 student 需纯 KD 预训练；`2408.04267` 用加权混合并明确称 student「does not require pre-training」。两文互不引用，已在 concept 页标为 `> [!contradiction]` 开放问题。
- **发现隐藏证据缺口**：`2309.08144` 在 −5/0/5 dB 三档的 ΔSIG 均不高于无蒸馏 student（0.47 vs 0.51 等），即「BAK 提升但人声质量未提升」，论文未讨论。
- **跨域收录**：`2607.27055` 为推荐系统论文，仅作特权信息蒸馏的方法学类比；已构建「推荐系统 ↔ 语音增强」11 行映射表，并标注最大不对齐风险（离散分布 KL vs 连续谱回归，dark knowledge 无天然对应物）。
- 论文级 algorithmic latency、compute latency 与 capture-to-playback p99 仍分开记录；**笔记完成不代表论文满足 strict-causal 或 2 ms**。

## [2026-09-20] ingest | 新增 3 篇（LaCo-SENet / RT-Tango / PSMSE）

用户指定 3 篇论文（2 篇 arXiv + 1 篇 Elsevier 期刊长文），要求按既有规范摄取。

### 原件归档

全部放入 `raw/papers/low_latency_causal_se/`，未覆盖同名文件：

| # | 标识 | 文件 | 大小（bytes） | 来源 |
|---:|---|---|---:|---|
| 22 | `2606.19688` | `2606.19688.pdf` | 851,902 | arXiv:2606.19688v3 [cs.SD], 18 Aug 2026 |
| 23 | `2607.01834` | `2607.01834.pdf` | 317,966 | arXiv:2607.01834v1 [cs.SD], 2 Jul 2026 |
| 24 | `10.1016/j.iot.2026.102046` | `1-s2.0-S2542660526001769-main.pdf` | 8,316,825 | Internet of Things 39 (2026) 102046（用户提供） |

`S2542660526001769` 保留用户原始文件名（未重命名为描述性名称），以便与 DOI 直连。

### 执行方式

主 agent 负责原件下载、文本抽取（PyMuPDF，`tmp/extract_pdfs.py`）、页面渲染、规格提取、子 agent 派发与最终验收；
3 个子 agent 各自独立完成一篇的 source + entity + concept 三页，主 agent 统一维护 index/log。

### 新增页面统计

| 类型 | 数量 | 位置 |
|---|---:|---|
| source | 3 | `sources/2026/` |
| entity | 3 | `entities/` |
| concept | 3 | `concepts/` |
| 页面渲染资产 | 31 | `assets/{2606.19688,2607.01834,S2542660526001769}/` |

### 主 agent 审核结论

- **结构检查**：3 篇 source 均含 YAML frontmatter、`~~~yaml` 快速索引卡、PDF 质量 warning、7 个必需一级章节、公式/符号、结果与消融表、strict-causal/latency ledger、cross-reference matrix、"一句话江湖地位"与 `## 参考资料`。
- **链接检查**：`wiki_low_latency` 内部 wikilink 与图片嵌入合计 **1515 个，断链 0**（含转义竖线与 heading anchor 两种写法）。
- **数字溯源抽查**（逐项回原文核对，未发现编造）：LaCo-SENet 的 `1.37M / 3.35 / 3.43 / 3.47 / 3.27@46.5ms / RTF 4.59→0.30 / SSU 1.86·1.45·1.39·2.04`；RT-Tango 的 `605.98 / 67.20 / 33.41 / 35.14 / 197.5 / 0.49 MMACs·frame / α=0.995`；PSMSE 的 `0.26M / 0.11 G·s / 2.85 / 2.73 / 95.1 / 93.9 / 266 MB / 0.2427·0.1876·0.1539·0.3466 / Table 8 全部 11 行 / Table 7 HASPI·HASQI` 均**在原文中可验证**。
- **命名规范化**：嵌入图统一为 `<id>-pageN-<内容>.png`，笔记引用同步更新。

### 关键结论

- **3 篇无一满足约 2 ms**：RT-Tango 8 ms（最近）、LaCo-SENet 12.5 ms（STFT center delay 硬下界）、PSMSE 30 ms。
- **LaCo-SENet 提供本库目前最完整的逐层因果证据链**：给出 padding 分配式 Eq. (1)、延迟式 Eq. (3)、状态更新式 Eq. (4)、选择算子 Eq. (5)，并有 SSU 消融（关掉后 PESQ 崩到 1.45–2.04，全部低于 noisy 1.97）与"分块/全序列数值一致"声明。
- **发现两处必须随结论一起读的方法论 caveat**：RT-Tango-OS 的在线 SCM 采用"把同一段混合重复到收敛、只在最后一次算指标"的评测，等于无限预热，真实冷启动不成立；PSMSE 明确"Mamba states are re-initialized on each call and not propagated across consecutive frames"，其"流式/长程"实为逐帧无状态映射 + 50% OLA。
- **发现多处原文内部不一致**（已在对应页面用 `> [!question]` / `> [!contradiction]` 标注）：LaCo-SENet 的 Table 1（3.35，全序列）与 Table 2（3.39，C=1 流式）PESQ 口径差异；RT-Tango 未报告采样率、参数量与 RTF；PSMSE 的 PLIF `τ=2.0` 初值与 `τ=sigmoid(a)∈(0,1)` 互斥、Table 2 把 PSMSE 年份误标 2025、`0.11 G/s` 与 `1.05 G/样本` 无法互推、§6.3 正文 DEMUCS 1.14 与 Table 5 的 1.13 不符。
- **因果判定口径升级**：LaCo-SENet 把 SEMamba / xLSTM-SENet 因"encoder 用非因果对称 padding"判为算法延迟不可确定并排除排名；本库应沿用该更严口径，把"自称单向"与"逐层可核验的因果"分开记账，这直接影响 [[wiki_low_latency/sources/2026/RT-SEMamba 2026]] 的既有结论。

## [2026-09-20] consistency | 一致性检查与关联实验（摄取后流程）

按 CLAUDE.md 摄取流程的 step 9（检查 consistency）与工作流 6（实验笔记）完成收尾。

### 一致性检查：因果口径冲突已落到相关页面

LaCo-SENet 的更严口径与库中既有结论冲突，按"追加而非删除 + `[!contradiction]` 标注"处理，**未改写任何原有判定**：

| 页面 | 追加内容 |
|---|---|
| [[wiki_low_latency/sources/2026/RT-SEMamba 2026]] | 新增「因果性判定口径」小节 + 页首 `[!updated]`；cross-reference matrix 增加 2 行（因果口径冲突、与 PSMSE 的状态语义对照） |
| [[wiki_low_latency/entities/RT-SEMamba]] | 「实体判定」后追加 `[!updated]`，说明 25 ms 不得与给出逐层 padding 式的模型同级比较 |
| [[wiki_low_latency/concepts/2608.12099-mamba-distillation]] | 时延账本后追加 `[!contradiction]`，说明 KD 方法学结论不受影响但 25 ms 不可当已审计因果延迟引用 |
| [[wiki_low_latency/overview|综述页]] | 新增「跨论文判定口径（2026-09-20 确立）」4 条通用规则；「当前状态」更新为 24 篇 / 三批次 |

**结论**：RT-SEMamba 保持 `paper-claimed-causal`，**未被推翻，但降级为待验证**（需代码级逐层 padding/state 审计）。

### 综述更新

`overview.md` 的「当前状态」原停留在 14 篇，已改为三批次 24 篇的汇总表，并明确写出
**没有任何一篇满足约 2 ms 硬约束**（最近的 Nakaoka 2021 6.71 ms 与 RT-Tango 8 ms）。

### 关联实验（工作流 6）

由这 3 篇论文的技术组合出 3 个新实验计划，写入 `outputs/experiments/`：

| 实验 | 组合 | 核心假设 |
|---|---|---|
| [[outputs/experiments/短窗前端×非对称padding的2ms路径]] | LaCo-SENet 骨干 × 2204.09911 短窗前端 | 换掉 400-sample STFT 后，padding ratio 才成为 2 ms 方向的主旋钮 |
| [[outputs/experiments/SSU选择算子跨模型体检]] | LaCo-SENet SSU × 库中所有 lookahead 模型 | state corruption 是「缓存过去 + 缓冲未来」的通用缺陷，Nakaoka 2021 最可疑 |
| [[outputs/experiments/无参数时间稀疏化×脉冲稀疏性]] | RT-Tango FRS × PSMSE SNN | 表示稀疏与时间稀疏作用在正交轴上，可叠加压低 0.11 G/s |

另在 `outputs/experiments/index.md` 提炼出 **4 条跨实验验收要求**（算法延迟须配 chunk size+RTF、
在线统计须按冷启动评测、"流式"须写明状态语义、因果性须用更严口径），供后续所有实验复用。

### 链接复核

新增/修改页面后重跑校验：`wiki_low_latency` 与 `outputs/experiments/` 合计 **1591 个链接/嵌入，断链 0**。

## [2026-09-20] fix | 行内公式定界符改为 Obsidian 可渲染格式

**问题**：用户反馈 LaCo-SENet 笔记公式渲染异常。定位后确认根因是**行内公式用了 `$ ... $`**。

**根因**：Obsidian 原生 MathJax 只识别 `$ ... $`（行内）与 `$$ ... $$`（块级）两种定界符，
`$ ... $` 与 `\[ ... \]` **不被识别**，会以原始 LaTeX 文本显示。
（来源：Obsidian 中文论坛「Obsidian 不渲染 `\[` `\]` `\(` `\)`，但可以渲染 `$` 和 `$$`」；
推荐做法即 `\[`→`$$`、`\(`→`$`。Obsidian 官方文档也只记载 `$` / `$$` 形式。）

**排查过程**（先排除再动手，避免盲改）：
1. 定界符配对检查：`$` 与 `$` 在 LaCo 三页各 131 / 53 / 74 个，**配对无误**，不是漏写。
2. 用 **MathJax（与 Obsidian 同引擎）实际解析**三页全部公式 → **142 / 53 / 83 项，0 失败**，
   说明**不是 LaTeX 语法错误**。
3. 对比全库命令集合：LaCo 独有 `\Pi`、`\angle`、`\underbrace`，但均为标准命令，非问题源。
4. 逐一排查可疑项：`\text{–}`（U+2013 非 ASCII）、`\big[`、单行 `$$`、callout 内 `$$` —— 均在库中其他笔记出现过。
5. **结论**：问题不在公式内容，而在**定界符形式**。

**修复**：三个 LaCo 页面 `$ ... $` → `$ ... $`，共 262 + 106 + 148 = **516 个定界符**。
- 转换前备份至 `tmp/backup_LaCo_{source,entity,concept}.md`。
- 跳过代码围栏（`~~~` / ` ``` `），未触碰 ASCII 架构图。
- 转换后复验：残留 `\(` / `\)` = 0；无奇数 `$` 行；**MathJax 重解析 142 / 53 / 83 项，0 失败**；
  `wiki_low_latency` 链接 1538 个断链 0；frontmatter 与 7 个必需章节完好；换行符 LF 与库内其他笔记一致。

> [!warning] 这是**全库性**问题，未一次性全改
> 全库仍有 **58 个文件、3632 处** `$ ... $`（`wiki_low_latency/` 50 个、
> `wiki_array/` 3 个、`outputs/experiments/` 4 个、`ultra_low_latency_causal_se/` 1 个）。
> 本轮按用户指定范围只修 LaCo 三页，**其余 55 个文件是否批量修复待用户确认**。
> 注意：`raw/` 目录（PDF 转换产物）用的是 `$` / `$$`，**不受影响**，且按 CLAUDE.md 属只读区不可改动。

## [2026-09-22] ingest | 新增 2 篇：推理期动态算力子群（Skip-DPCRN / D-GRU）

用户给定两个模型名「Skip-DPCRN」「D-GRU」，要求查找、下载到 low-latency 目录并按同一流程派子 agent 撰写笔记。

### 检索过程

两个名字都不是正式论文标题，需先做实体消歧：

| 用户给的名字 | 实际论文 | 依据 |
|---|---|---|
| Skip-DPCRN | arXiv:**2207.11108** *Inference skipping for more efficient real-time speech enhancement with parallel RNNs*（Le, Lei, Chen, Lu, 2022） | 官方代码仓库名即 `Le-Xiaohuai-speech/SKIP-DPCRN`；论文正是把 Skip-RNN 应用到 DPCRN |
| D-GRU | arXiv:**2408.12425** *Dynamic Gated Recurrent Neural Network for Compute-efficient Speech Enhancement*（Cheng, Pandey, Xu, Delbruck, Liu, 2024） | 摘要明确 "we further propose the Dynamic Gated Recurrent Unit (D-GRU)" |

**关键发现：两篇直接相关。** D-GRU 论文的 Related Work 把 Skip RNN 系列列为反面（"skip the update of all
neurons in some steps, therefore the computational load also changes across steps"），
而其引文 **[31] 正是 Skip-DPCRN**。两篇构成「推理期动态算力」的正反两面，必须并读。

### 原件归档

| # | arXiv | 文件 | 大小（bytes） | 来源 |
|---:|---|---|---:|---|
| 25 | `2207.11108` | `2207.11108.pdf` | 5,047,710 | arXiv:2207.11108v1 [cs.SD], 22 Jul 2022；11 页 8 图；IEEE/ACM TASLP vol.30 pp.2411-2421 |
| 26 | `2408.12425` | `2408.12425.pdf` | 396,393 | arXiv:2408.12425v2 [eess.AS], 24 Sep 2024；5 页；Meta Reality Labs 资助 |

### 新增页面统计

| 类型 | 数量 | 位置 |
|---|---:|---|
| source | 2 | `sources/2022/Skip-DPCRN 2022.md`、`sources/2024/D-GRU 2024.md` |
| entity | 2 | `entities/Skip-DPCRN.md`、`entities/D-GRU.md` |
| concept | 2 | `concepts/2207.11108-inference-skipping-parallel-rnn.md`、`concepts/2408.12425-dynamic-gated-rnn.md` |
| 页面渲染资产 | 16 | `assets/{2207.11108,2408.12425}/` |

### 主 agent 审核结论

- **公式定界符检查通过**（本次新增的前置约束）：6 个新文件 `\(` / `\)` 残留均为 **0**，无奇数 `$` 行。
  用 **MathJax 实跑** 6 页共 **638 项公式，0 失败**。
- **结构检查**：2 篇 source 均含 YAML frontmatter、`~~~yaml` 快速索引卡、PDF 质量 warning、
  7 个必需一级章节、`## 参考资料`。
- **链接检查**：`wiki_low_latency` 内部 wikilink 与图片嵌入 **1766 个，断链 0**。
- **数字溯源**：两篇的全部关键值（Skip-DPCRN 的 `1115.1 / 749.8 / 0.5286 / 0.5291 / 48 ms / 9.527 / 2.688 / 89.13 /
  9.337 / 2.645 / 88.53 / 360.6 / 458.8 / 849.7 / 814.0 / 28% / 88.2% / 15%`；
  D-GRU 的 `135.32 / 93.65 / 4878.35 / 5689.37 / 4062.92 / 3250.19 / 212.06 / 247.19 / 114.48 / 176.96 /
  1.34 / 0.28 / 0.35 / 66.66 / 83.33 / Mann-Whitney / top-A`）**均在原文中逐字可查**。
  两页中少量「原文查不到」的数字（如 Skip-DPCRN 的 `908.5 / 850.1 / 819.4 / 814.1`、D-GRU 的
  `38.4% / 25.4% / 14.3%` 等）**全部是本页按原文表格自行复算的派生量**，页面内已明确标注
  「本页按 Table I 复算」「论文未给出这两个比例」，并公开了与表值的残余差异（如
  `预测 93.66 vs 表值 93.65`），**不属于编造**。

### 关键结论

- **两篇都不满足约 2 ms**：Skip-DPCRN 的 48 ms 是目标的 **24 倍**；D-GRU **完全没报任何延迟数字与 RTF**。
- **方法论对照是本轮最大价值**：
  - **Skip-DPCRN**（时间步级跳过）：把 Skip-RNN 从「会出音频伪影的失败尝试」救回来——关键洞察是
    伪影来自**宿主结构**而非跳步本身，只要宿主是 **parallel RNN**，一部分 RNN 跳步时 mask 仍由其他通路
    继续更新，伪影即被规避。再加 γ 缩放旋钮（**推理期可调、无需重训练**）与 VAD 引导的差异化跳步
    （纯噪帧 γ=0.4，纯噪段 DPRNN 算力仅 baseline 的 28%）。DPCRN 上 MACs 从 1115 降到 749.8 M（−32.8%），
    参数量几乎不变（0.5286→0.5291 M），**同算力下胜过直接训小模型与结构化剪枝**。
  - **D-GRU**（神经元级固定比例稀疏）：直接复用 GRU 自带的 update gate $z_t$ 做 top-A 选择，
    **零额外参数**；P ≥ 50% 时 PESQ 差异统计不显著（Mann-Whitney U），整体算力降到 GRU 69% / MPT 75% / DPRNN 71%。
    论文明确否掉阈值型 gate，理由是会让**每步算力波动**——硬件仍须按最坏情况配置。
- **新增第 5 条跨论文判定口径**（写入 `overview.md`）：**输入相关的动态算力必须报峰值，不能只报平均值。**
  Skip-DPCRN 平均省 33% 但**峰值算力只降约 15%**，而实时硬件按最坏情况预留，所以「平均省 33%」
  不能当作可兑现的预算。D-GRU 正是抓这一点改用固定比例。

### 子 agent 纠错记录

主 agent 在派发 prompt 时把引文 [20]（Fedorov 的 TinyLSTM）误说成「与 Nakaoka Wave-U-Net 蒸馏相关」，
子 agent 回原文核对后**指出该关联不存在**，并在页内正确区分了两者。子 agent 的核对纪律有效。

### 原文疑点（子 agent 发现，均已在页内标注，未静默修正）

- Skip-DPCRN：Table III 中 Inter-skip 前两行 MACs 疑错位一行；Table II 与 Table III 的更新率口径不可互算；
  Eq. (19) 的 update rate 定义与正文表述矛盾；$\lambda=0.1$ 归因引文 [21] 但该文用 0.3；
  **页眉 `JOURNAL OF LATEX CLASS FILES, VOL. 18, NO. 9, SEPTEMBER 2020` 与第 1 页 DOI
  `10.1109/TASLP.2019.2915167` 都是 LaTeX 模板未替换的占位符**；Fig. 6 自称高斯实为小提琴图。
- D-GRU：摘要「average 50% reduction in GRU computes」与正文「33%」冲突（50% 实指神经元比例 P）；
  Mann-Whitney U 用于配对样本且未做多重比较校正；P=75 处 PESQ 非单调上翘未评论。

## [2026-09-22] fix | 行内公式定界符全库批量修复（承接 09-20 未完成项）

09-20 只修了 LaCo-SENet 三页，全库仍有 58 个文件用 `\( ... \)`。本轮补齐。

**执行**：`tmp/fix_math_delims_batch.py`（跳过代码围栏；跳过 `raw/` 只读区、`.workbuddy-ai`、`tmp`；
逐文件备份到 `tmp/mathfix_backup/` 并保持相对路径）。

| 项 | 数量 |
|---|---:|
| 修改文件 | **59** |
| 转换定界符 | **3649** |

**复验（全库 232 个 md 文件）**：

- 残留 `\(` / `\)`：**0**
- MathJax 实跑 **3985 项公式，真实失败 0**（唯一被标记者是 `log.md`——它本身在讲定界符，
  行内代码里有 `` `$` ``，属于校验器的已知误报；已确认该文件所有 `$` 要么在行内代码内、要么是成对的行内公式）
- `wiki_low_latency` 内部链接与图片嵌入 **1772 个，断链 0**
- 行尾保持 LF

**过程中发现并修复 3 处「非本次引入」的真实公式错误**（这些公式在 Obsidian 里会渲染成红色报错框）：

| 问题 | 文件 | 修法 |
|---|---|---|
| `\frac{q_y}` 后面直接跟 `\sqrt{...}`，分母缺花括号 → MathJax 报 `Missing argument for \sqrt` | `concepts/2008.04259-perceptual-speech-preservation.md`、`sources/2020/PercepNet Low-Latency Direction 2020.md` | 给分母补 `{ }` |
| `\tag{N}` 写在 `\begin{aligned}...\end{aligned}` **内部** → MathJax 报 `\tag not allowed in aligned environment` | `sources/2022/STFT-Domain Very Low Algorithmic Latency 2022.md`、`sources/2023/Uncertainty-Aware Speech Enhancement 2023.md` | 把 `\tag{N}` 移到 `\end{aligned}` **之后** |

> [!warning] 批量转换踩到的坑（已写入 skill）
> 脚本只跳过了**代码围栏**（`~~~` / ` ``` `），**没有跳过行内代码**（单反引号），
> 结果把 `log.md` 里 4 处「描述定界符的行内代码」`` `\(` `` 也改成了 `` `$` ``，造成自伤。
> 已逐行还原。**教训：批量替换前必须同时排除代码围栏与行内代码 span。**

## [2026-09-24] ingest | 新增 1 篇：语义先验子群（Tsunoo 因果 SSL + 未来语义预测）

**论文**：Causal Speech Enhancement with Predicting Semantics based on Quantized Self-supervised
Learning Features — arXiv:**2412.19248**v1 [eess.AS]（2024-12-26，5 页），ICASSP 2025。
作者 Emiru Tsunoo; Yuki Saito; Wataru Nakata; Hiroshi Saruwatari（The University of Tokyo）。
本地原件：`raw/papers/low_latency_causal_se/2412.19248.pdf`。

**流程**：读 `CLAUDE.md` → 读 `sources/2026/LaCo-SENet 2026.md` 与 `entities/D-GRU.md` 作模板
→ WebSearch 定位 + arXiv API `id_list` 核实元数据（标题精确搜索直接命中，模型名缩写无用这一条再次被证实）
→ `curl -sSL` 下载（HTTP 200 / 118 KB / application/pdf）→ 改 `tmp/extract_pdfs.py` 的 JOBS 单跑一篇
→ PyMuPDF 抽取 `tmp/pdf_extract/2412.19248.txt`（26086 字符）+ 5 页 150 dpi 渲染到 `wiki_low_latency/assets/2412.19248/`
→ 主 agent 通读全文后给子代理写详brief → 子代理产出 source/entity/concept 三页
→ 主 agent 核验（结构 / 定界符 / MathJax / 链接 / 图片 / **逐表回原文对数**）。

**新增页面**：

| 类型 | 文件 |
|---|---|
| source | `wiki_low_latency/sources/2024/Tsunoo Causal SSL Semantic 2024.md`（485 行） |
| entity | `wiki_low_latency/entities/Tsunoo-Causal-SSL-SE.md`（243 行） |
| concept | `wiki_low_latency/concepts/2412.19248-causal-ssl-semantic-prediction.md`（298 行） |

**论文核心（本库口径）**：

1. **动机**：因果 SE 只能用过去上下文，但"预测未来音素延续"可能有用（先例：增量 TTS [25]、流式 VC [26]）。
   SSL（WavLM）特征量化出的 semantic token 与音素状态高度相关，但 SSL 本身非因果 → 几乎没有工作做进因果系统。
2. **三处改造**：Eq. (5) 因果 SSL（限制输入为过去帧 + 取末帧）；§III-B 用 causal Transformer 替代双向 LSTM；
   Eq. (6) 用 FiLM 替代拼接做特征融合。
3. **语义预测**：one-stage VQ 离散化（Eq. 7，替代 SELM 的两阶段 k-means）→ SSL encoder $g$ 加分支**并行**预测未来 $N=5$ 个 token
   （Eq. 11–12，非自回归）→ 三项损失 MTL（Eq. 14，$\lambda=\{1,1,0.01\}$）。
4. **主结果**：VoiceBank+DEMAND PESQ **2.88**（Table I 的 codebook 隐向量配置，$N=5$）。
5. **最关键消融（Table IV）**：语义预测的增益**只在因果条件下出现**——
   因果 C1 vs C2 = 2.88 vs 2.83（**+0.05**）；非因果 N1 vs N2 = 3.14 vs 3.14（**0.00**）。
   论文的解释与非因果场景自洽：非因果的上下文里本来就有未来帧，所以"预测未来"是冗余监督。

**本库判定**：

- **因果性**：`paper-claimed-causal`（**近似实现，非架构级因果**）。Eq. (5) 是"限制访问 + 取末帧"，
  WavLM 内部位置卷积/相对位置偏置是否引入未来依赖**未做逐层审计**，按 LaCo-SENet 立的尺子过不了"逐层可核验"。
- **延迟账本：空。** 未报告算法延迟、RTF、MACs、参数量、目标硬件、p50/p95/p99、RAM/SRAM、量化；
  **STFT 的 window/hop/FFT/center 也全未写** → 无法评估它与约 2 ms 的距离（是"无数据"，不是"很大"）。
- **额外发现（本页读出的机制级风险）**：$c(X)=\{s(X_{\le t})_t\}$ 的字面实现在流式下等价于
  **每个时刻重跑一次完整 WavLM base 前向**，计算量随帧数膨胀（$O(T^2)$ 量级重算），论文对此**零量化**。
  这是"截断式因果化"的通用代价，已写入 overview 第 7 条。
- **人声保留：空白，且有针对性担忧**。"预测未来音素"在低 SNR / 竞争说话人下可能预测错音素，
  掩蔽若依赖错误语义就可能**抑制真实辅音**；论文无失败案例、无低 SNR 分层、无针对性指标。
- **不加分提醒**：论文**未声称超过 SOTA**——Table II 中 LFSFNet 2.91 > 本文 2.88，
  原文措辞是 "comparable to state-of-the-art method that, **unlike our model, estimates appropriate phase information**"。
  另 Table II 基线数字明写"based on the literature"，非统一条件下复现。

**子代理纠错记录（有效核验纪律的又一例）**：主 agent 的 brief 中有 3 处与原文不符，子代理回原文核对后**主动指出并拒绝迁就**：

| brief 的说法 | Table IV 实际 | 后果 |
|---|---|---|
| C3 = 去掉 FiLM 但保留 WavLM | C3 = `Causal Trans.` + WavLM **Causal**，FiLM ✗ Semantics ✗ | S1 vs C3 的唯一变量是**"WavLM 的有无"**，不是"去掉 FiLM"；差 −0.03 |
| S1/S2 是"无 SSL"的对照 | 正确，但 S1 vs S2 的变量是 **SE mask estimator 架构**（Causal Trans. vs LSTM） | 该对照值 +0.06，**不可与上面 −0.03 合并成 +0.09** |
| Table II 本文两行只有 PESQ/STOI | 本文两行**有** CSIG/CBAK/COVL（4.28/3.39/3.58、4.23/3.36/3.53） | 已改正 |
| （brief 隐含）采样率 16 kHz | 论文**从未写采样率** | 记为"未报告"，未代填 |

> 教训：**Table IV 的三列勾选 `✓` 在 PyMuPDF 文本抽取中会全部丢失**（只会抽出 `Causal Trans.` `Causal` 之类的标签），
> 必须看页面渲染图才能确定每行的列归属。主 agent 因只读文本抽取而误判，子代理看渲染图纠正。
> 这条已补充进 skill。

**核验结果（主 agent 执行）**：

| 项 | 结果 |
|---|---|
| 章节完整性 | source 页 7 个必填章节 + 参考资料，**齐全** |
| 违规定界符 `\(` / `\[` | 三页均为 **0** |
| MathJax 实跑（`wiki_low_latency` 全域） | 87 文件 / **3289 项公式 / 真实失败 0**（唯一标记者是 `log.md` 第 217 行的已知误报——行内代码里在描述定界符） |
| 新页公式量 | source 行内 123 + 展示 24；entity 行内 53；concept 行内 62 + 展示 4 |
| 图片嵌入 | source 页嵌入 `assets/2412.19248/2412.19248-page4.png`，文件**存在**（474 KB） |
| 断链 | 新三页 **0**（链接检查器把图片嵌入也计入，属误报类；同库另有 59 个同类既有图片嵌入误报） |
| 逐表对数 | Table I / II / III / IV **四张表全部回原文逐格核对，数值一致** |

**交叉关联（已填入 source 第 6 节）**：DPCRN/DCCRN（同为时频掩蔽因果增强，但那支做复数谱/相位，本文只用 noisy 相位）；
蒸馏子群（都在补因果模型的上下文缺失，手段是 teacher，本文是"未来语义预测"——**不同的补偿路径**）；
PSMSE / RT-SEMamba（同为流式，但那两篇都有延迟数字，本文一个都没有）；
`concepts/2309.08144-two-step-distillation`（two-stage 的两阶段训练 vs 本文 one-stage VQ）；
三个共用概念页（严格因果与算法延迟 / 低时延前端与延迟账本 / 低 SNR 人声保留评估）。

**主 agent 更新的中央页面**：`index.md`（entity/concept/source 各加 1 条 + 第 5 批表格 #27 + 计数 27）、
`overview.md`（批次表加第 5 批 + 新增判定口径第 6、7 条）、本日志。

## [2026-09-26] ingest | FastEnhancer（arXiv:2509.21867）

**论文**：Ahn / Han / Woo / Kim（首尔大学），"FastEnhancer: A Fast and Lightweight Framework for Streaming Speech Enhancement"，2025-09-26 上传 arXiv，5 页。代码与预训练权重：<https://github.com/aask1357/fastenhancer>。

**为什么收这一篇**：它是本库"**MACs 低 ≠ 跑得快**"这一命题目前**最完整的单一论据集合**——四条独立证据（跨模型 / 零算术变化 / 纯内存变化 / 参数更少却更慢）来自同一篇论文的同一套实验，可比性远高于跨论文拼接。

**论文要做的三件事**：

1. **否定"降 MACs 的轻量化路线"**：§2.2 明确批评子带方案（BSRNN / FSPEN / GTCRN / LiSenNet）「increased architectural complexity and memory operations paradoxically led to higher RTFs」，主张"简单的 encoder-decoder 就够"。
2. **架构**：精简 encoder-decoder + **RNNFormer**（dual-path：时间轴单向 GRU + 频率轴 4-head MHSA），功率压缩复数谱（$c=0.3$）+ 两通道 mask。
3. **三个"零算术代价、纯速度代价"的设计选择**：时间轴卷积 kernel 恒为 1、全模型用可融合的 BN、时间轴不用需 KV cache 的注意力。

**四条硬证据（全部逐表回原文核对）**：

| # | 证据 | 数值 | 排除了什么解释 |
|---|---|---|---|
| A | 跨模型 | FastEnhancer-B：262M MACs → RTF **0.022**；GTCRN：40M → 0.060；FSPEN：64M → 0.046；BSRNN：245M → 0.059 | 排除"MACs 决定 RTF"（6.5× 的 MACs，2.7× 更低的 RTF） |
| B | **零算术变化**（最强） | BN→LN：**Para. 92K 不变、MACs 不变**、SISDR 19.0→**18.9**、STOI 不变，但 RTF 0.022→0.028（Xeon **+27%**）/ 0.026→0.029（M1 **+12%**） | 排除"参数/MACs/质量变化导致变慢"——只剩算子可融合性 |
| C | 纯内存变化 | 时间轴 kernel 1→3：Para. 92K→187K、RTF +27%(Xeon)/+42%(M1)，而 **SISDR 19.0→19.0、STOI 94.5→94.5 一格不动** | 排除"质量提升的代价"——只买到缓存操作的开销 |
| D | 参数更少却更慢 | DPT 消融（时间轴 GRU→MHSA）：**参数比 RNNFormer 更少**，因 **KV cache** 而 RTF 显著升高 | 排除"参数量决定 RTF" |

**机理（论文原话）**：时间是 kernel $k$ 需缓存 $k-1$ 帧，「These **memory operations** significantly increase processing time」——用的是 memory operations 而不是 computation。BN 在推理期可折进相邻层（LN 因逐样本动态统计量不可折），故「LN cannot be fused in the same manner, **increasing the RTF**」。

**代价是硬件相关的（本页读出、论文未讨论）**：同一次 BN→LN 替换 Xeon +27% / M1 +12%；同一次 kernel 1→3 Xeon +27% / M1 +42%。**两个平台给出的相对代价完全不同**——说明"可融合性"在设计图上是算法属性，但兑成多少墙钟取决于运行时/编译器。**不能把某个平台的比例当常数用。**

**本库判定**：

- **因果性**：`paper-claimed-causal`。**结构证据较强**（比许多论文强）：时间轴卷积 kernel 恒 = 1（且论文明确声明"全文 kernel/stride 均指频率轴"）、时间轴单向 GRU、时间轴不用 MHSA（KV cache 会增加延迟）、频率轴 MHSA「doesn't require caching」（注意力只在当前帧内沿频率轴做）。**但仍缺**：无逐层 padding / state certificate、无 STFT 帧锚定（center 与否）说明、无样本级可读性声明 → 按 LaCo-SENet 的尺子，逐层 certificate 一栏是空的。
- **状态语义：缓存型**——时间轴 GRU 状态**跨帧传播**（这是"流式"的实质来源），频率轴 MHSA **逐帧无状态**（每帧内部独立完成）。这与 [[wiki_low_latency/entities/PSMSE]] 的"**每帧重新初始化 Mamba state、帧间无状态**"正好相反，构成本库一组**状态语义正反对照**。两者都自称流式，**必须先问清是哪一种**。
- **延迟账本：论文通篇零数字**——无 window−hop、无 $W/2$、无推导式、无 group delay、无 look-ahead、无算法延迟口径。本库按 Table 1 的 $H$ 列推得 hop = 256 / 160 / 100 samples @16 kHz ⇒ **16.00 / 10.00 / 6.25 ms**；若 STFT 用 center=True 则前端另有 $W/2=16$ ms 未来样本 ⇒ **十几毫秒量级**，**比约 2 ms 目标高一个量级或更多**。**以上全部是本库推读，论文没有做任何这类换算。** **不是 2 ms 候选**。
- **RTF 口径不可复现**——论文称 "under a streaming condition" 但**未定义** chunk 大小、是否有 look-ahead、batch 是否为 1、是否把 STFT/iSTFT 计入计时。**RTF 是吞吐指标，不是 deadline 指标**：RTF 0.012 只说明"平均处理时间 ≈ 0.012 × 音频时长"，与"每帧必须在 deadline 前算完"是两件事。全库无 p50/p95/p99、无 deadline miss、无 underrun/overrun、无峰值 RAM/SRAM、无 INT8 量化、无功耗。
- **人声保留：指标组合较全，分层维度空白**。**正面资产**：报了 DNSMOS 的 **SIG/BAK/OVL 三项**（多数论文只报 OVL）+ **WER（Whisper-large-v3-turbo）** + **ESTOI** + SCOREQ，是本库**最全的可懂度/保留指标组合之一**。**缺**：负 SNR 分层（−10/−5/0/5 dB）、噪声类型分层、babble/竞争说话人、false-suppression、SPP/VAD 校准、F0/formant/prosody continuity、voiced energy 保留、主观听感 MOS，**全部未报告**。
- **本页读出的一个读法（论文未讨论）**：从 T → L，**BAK 从 4.01 到 4.04（非常平）**，而 **SIG 从 3.34 到 3.44（明显上升）**、P.808 3.42→3.53。说明规模增长的增益主要来自**语音保真度（SIG）**而非**更强的抑噪（BAK）**——BAK 在 T 档就已基本饱和。对本库的意义：若目标是"低 SNR 下的人声保留"，信号是**正面**的；若目标是"更强的抑噪"，**不要指望靠加容量解决**。

**论文内部自相矛盾两处（`[!question]`，不静默修正）**：

1. **数据集名称**：Table 2 标题写 "Performance on **Voicebank-Demand**"（第 4 页），§4 正文写 "**VTCK**-Demand dataset [14]"（第 3 页，VTCK 疑为 VCTK 笔误）；引文 [14] 是 Valentini-Botinhao 等 VoiceBank-DEMAND（ISCA SSW 2016）。
2. **DPT 消融的帧率与 Table 1 不符**：§5.2 称 look-behind 为「**31 frames (corresponding to 0.5 seconds)**」⇒ 2 ms/帧（500 帧/s），但 Table 1 的 hop（256/160/100 samples @16 kHz）对应 62.5 / 100 / 160 帧/s，**没有任何一档是 2 ms/帧**。论文未说明该消融用的 hop。

**另两条存疑**：Fig. 1 与配置的对应关系未说明（FastEnhancer 图上是**一个点还是五个点**未交代；若为单点，"Pareto 前沿"由单点支撑）；Pareto 前沿**无形式化定义**（无数学定义、无 hypervolume 这类覆盖度指标）→ "建立新前沿"是**定性图注主张**，不是可量化验证的结论。

**"state-of-the-art" 的主张范围必须严格限定**：论文写「achieves state-of-the-art speech quality and intelligibility」，但对比集合只有 **5 个低复杂度模型**，且 FastEnhancer-**M 的 MACs 达 2.9G、L 达 11G**——分别是 GTCRN（40M）的 **72×** 与 **275×**。Pareto 前沿的表述是**合理**的，但**不能**读成"以极小代价击败所有前作"（L 档的性能是在 275× 于 GTCRN 的算力下取得的）。

**5 seeds 只报均值不报方差**：论文明确说用五个随机种子报平均分，但**未报标准差** ⇒ 0.01 量级差异（如 M 的 P.808 3.48 vs S 的 3.49）**无法判定显著性**。与 overview 第 6 条判定口径（小效应量需统计证据）一致。

**LiSenNet a/b/c 三行 = "非流式 → 流式代价"的现成教材（本库最干净的一组）**：同一模型、同参数量（37K）、同 MACs（56M），**唯一变量是"去掉 input normalization 与 griffin-lim 使其可流式"**：

| 行 | 是否可流式 | PESQ | SCOREQ | SISDR | BAK | WER |
|---|---|---|---|---|---|---|
| LiSenNet^b | **否**（脚注 b：not streamable，故 RTF 未报） | 3.08 | **0.425** | 13.5 | 3.90 | 3.7 |
| LiSenNet^c | **是** | 2.98 | 0.335 | 18.5 | 4.03 | 3.4 |

> **注意方向并不一致，不是"单向退化"**：PESQ −0.10、SCOREQ −0.090（−21%）**退化**，而 SISDR **+5.0**、BAK +0.13、WER **−0.3** 全部**改善**。说明流式化**改变了误差结构**：input normalization 依赖整段统计量（去掉后模型更保守 ⇒ BAK/SISDR 升），griffin-lim 是迭代式相位重建（去掉后 PESQ 这类对相位敏感的自然度指标掉）。
> **另一关键点**：LiSenNet^b 脚注明说 not streamable ⇒ 它的 SCOREQ 0.425（表内**最高**）与 SISDR 13.5（表内**最低**）**不能与流式模型并列解读**。同时注意 **LiSenNet^b 的 PESQ（3.08）低于 FastEnhancer-B（3.13）**——它的真正的特点是"SCOREQ 最高但 SISDR 最低"这个分裂，不是"PESQ 更高"。

**基线来源不统一（可比性提醒，论文用脚注坦白）**：GTCRN^a 用**官方 checkpoint**；LiSenNet^b 用**官方训练代码**（不可流式）；LiSenNet^c / FSPEN^d / BSRNN^d 是作者按 §4 **重实现重训**。"官方权重"与"作者重训"的数字**不宜直接横比**。

**与 LaCo-SENet 的 RTF 口径同构（本库可直接并用）**：都在**单线程 Intel Xeon** 上、都用 **ONNXRuntime**（LaCo-SENet 是 Xeon **Silver 4510**，本篇是 Xeon **Gold 6248R**）。但 LaCo-SENet 还给出**逐层 padding 分配式与算法时延公式**，本篇只有 RTF——**用 LaCo-SENet 的尺子量本篇，逐层 certificate 一栏是空的**。

**子代理纠错记录（有效核验纪律的又一例）**：主 agent 的 brief 中有 5 处与原文不符，子代理回原文核对后**主动指出并拒绝迁就**：

| brief 的说法 | 实际 | 后果 |
|---|---|---|
| LiSenNet^b 的 PESQ 比 FastEnhancer-B **更高** | 3.08 **<** 3.13，**更低** | 它的真正区分点是 SCOREQ 0.425（表内最高）配 SISDR 13.5（表内最低），已改正 |
| LiSenNet b→c 代价**单向退化** | PESQ/SCOREQ 降，但 SISDR 13.5→18.5、BAK 3.90→4.03、WER 3.7→3.4 **全部改善** | 已改为"方向不一致，改变误差结构而非单向退化" |
| M 档 DNSMOS 下降是**两项** | 是**四项**（P.808、SIG、OVL、BAK） | 已改正 |
| BN→LN 后 SISDR "基本不变" | 19.0→**18.9**（明确的 −0.1） | 已改为给出具体数字并与 STOI 的"不变"区分 |
| （未发现） | 新增论文内部矛盾：§5.2 的 "31 frames = 0.5 s" ⇒ 2 ms/帧，与 Table 1 的任何 hop 都不符 | 已作为第 2 条 `[!question]` 记录 |

**核验结果（主 agent 执行）**：

| 项 | 结果 |
|---|---|
| 章节完整性 | source 页 7 个必填章节 + 参考资料，**齐全** |
| 违规定界符 `\(` / `\[` | 三页均为 **0** |
| MathJax 实跑（`wiki_low_latency` 全域） | **90 文件 / 3438 项公式 / 真实失败 0**（唯一标记者是 `log.md` 第 217 行的已知误报） |
| 图片嵌入 | source 页嵌 `assets/2509.21867/2509.21867-page4.png`，entity 页嵌 page3/page4，文件**全部存在**（433–531 KB） |
| 断链 | 新三页 **0**（链接检查器报的 3 条是 `![[...]]` 图片嵌入的既有误报类；全库 3593 链接 / 103 broken，其中约 60 条为同类图片嵌入误报） |
| 逐表对数 | Table 1（5 档配置）/ Table 2（主结果 + 四条脚注 a/b/c/d）/ Table 3（消融）**三张表全部回原文逐格核对，数值一致**；另核对了 Fig. 1 / Fig. 2 / Fig. 3 与 Eq. (1)–(5) |

**交叉关联（已填入 source 第 6 节，共 15 组）**：DPCRN / TRU-Net（**同血脉的下一代，但砍掉了频率轴 RNN**，§2.1 明确否定 DPRNN 用在频率轴）；
FSB-LSTM / full-sub-band（**直接冲突**：子带路线的立论是"分频带更高效"，本篇批评它"架构复杂性与内存操作反而抬高 RTF"）；
DCCRN（复数谱路线对照，CRM vs 两通道 mask）；DeepFilterNet2（嵌入式实时参照）；
STFT-Very-Low-Latency-SE（**"有前端账本 vs 无前端账本"的对照**）；PercepNet（同属低复杂度实时）；
**LaCo-SENet（RTF 口径同构 + 最严因果审计尺子）**；**PSMSE（状态语义正反对照）**；RT-SEMamba（跨帧固定状态流的另一例）；
D-GRU / Skip-DPCRN（**同一类论点的另一侧面：可融合性 vs 可预测性**）；CRUSE-Latency-Study（统一低时延对照框架）；RT-Tango（速度/算力优化路线）；Tsunoo 2024（同为"延迟账本为空"，但本篇至少给了 RTF 与 hop）。

**本库改进建议（写入 concept 页）**：

1. **把 concept §2.3 的结构审计清单落成一张跨模型的表**——对库中所有低时延模型逐一体检 7 项（时间轴 kernel / 归一化可融合性 / 注意力 KV cache / global pooling / 数据相关访问 / 算力是否固定 / 全序列统计），并标注证据来源（论文明确 / 本库推读）。**这个想法直接来自本篇，库里还没有人做过**，且**只靠架构描述即可**，不依赖作者报告延迟——这在本库"延迟账本为空"是常态的情况下是唯一可用的工具。
2. **在 overview 里给"速度证据等级"分级**：① 只有 MACs/参数量；② 有 RTF 但无非流式口径与硬件说明；③ 有 RTF + 硬件 + 运行时 + chunk 定义；④ 有 p99/deadline。本篇可达 ②–③。
3. **建立"流式化代价"字段**：凡库中模型同时有流式与非流式版本的（LiSenNet b/c、PSMSE Table 2/3），都应把差值单独记一栏。
4. **一条对本篇的重要保留**：频率轴注意力既然"不需要 cache"，它是否已经隐含了"**整帧可见**"？若 STFT 用 center=True，那么"当前帧"本身就包含未来样本，频率轴的无 cache 性质**不能保证严格因果**。**本篇没有回答这个问题**（帧锚定未报告）。

**主 agent 更新的中央页面**：`index.md`（entity/concept/source 各加 1 条 + 第 6 批表格 #28 + 计数 27→28 + `updated: 2026-09-26`）、
`overview.md`（批次表加第 6 批 + 新增判定口径第 8 条）、本日志。

**事后补充核实（发表状态，2026-09-26）**：用户问"这篇是 A 会论文吗"，回原文与 arXiv 元数据核实后确认：
**不是。本篇是纯 arXiv 预印本，未见任何同行评审 venue。** 三项独立证据：
① 本地 PDF **无任何 venue 信息**（无会议名 / 无 "Submitted to" / 无版权行），页脚仅 `arXiv:2509.21867v1 [eess.AS] 26 Sep 2025`；
② arXiv 元数据**无 Comments、无 Journal-ref**（仅 DataCite 的 arXiv DOI），**只有 v1**、无后续更新；
③ 分类仅 `eess.AS`。
**易误读点（已写入 source 页 warning）**：论文**使用 ICASSP 模板**（抽象区 + Index Terms + 正文标题风格）、**自称 "state-of-the-art"**、上传时间（2025-09）落在 **ICASSP 2026 投稿周期**内——三者都容易被当成"已录用"，但**都不是录用证据**。
已在 source 页 frontmatter 加 `venue_status: preprint_only` 并写入 `[!note]` 一节。同批对照：Tsunoo 2024 的 `venue: ICASSP 2025` 来自**正文自述**（属"作者声称"，已标待验证），本篇连自述都没有——**本批两篇的 venue 可信度都低于库内（如 LaCo-SENet / PSMSE）有期刊卷页的论文**。

## [2026-09-27] ingest | Early Exit Compute-Matched（arXiv:2609.29867）

**论文**：*Does per-frame early exit pay? A compute-matched study of dynamic depth for on-device speech enhancement*（GN A/S（Laroche）+ DTU（Miccini），2026-09-24，5 页，`eess.AS` + `cs.LG` + `cs.SD`，EU grant 101194172 NeAIxt）。
**产出三页**：`sources/2026/Early Exit Compute-Matched 2026.md`（782 行）、`entities/Early-Exit-Conv-FSENet.md`（387 行）、`concepts/2609.29867-compute-matched-dynamic-depth.md`（421 行）。
**本地 PDF**：`raw/papers/low_latency_causal_se/2609.29867.pdf`（406,445 bytes）；页图 `wiki_low_latency/assets/2609.29867/2609.29867-page1..5.png`（150 dpi）。

**为什么摄它**：本库第 4 批（Skip-DPCRN / D-GRU）收录了"推理期动态算力"，但只记了"平均省多少"。本篇是**第一篇先做算力对齐、再问"动态是否值得"**的论文，且是本库唯一**真机逐图计时**的论文（STM32N6570-DK），直接补上"动态算力收益如何归因"这一空缺。

### 与既有页面/口径的挂钩

| 挂钩对象 | 关系 |
|---|---|
| **FastEnhancer（第 6 批）** | **同一论断（MACs ≠ 速度）的第二个独立机理**：FastEnhancer 归因于**算子可融合性 / 内存操作**，本篇归因于 **accelerator launch 次数 / NPU 利用率**。两篇可并列引用而互不替代。 |
| **Skip-DPCRN / D-GRU（第 4 批）** | 本篇把该批的"平均省算力"主张**降级为未归因**：不做算力对齐，动态方法必然"看起来有用"。 |
| **Conv-FSENet** | 本篇的网络骨架（stack / H / R 可配置），entity 页以它为基线建立配置速查表。 |
| **GTCRN** | 本篇引作 pp. **10286–10290**，与库内三篇的 **971–975** 冲突（见下）。 |
| **overview 判定口径** | 新增第 **10–13** 条（算力证据等级 L0–L3；µs/MMAC 离散度；算力对齐入场券；跳过状态语义审计）。 |

### 子代理纠错记录（本批最重的一次，共 11 项）

主 agent 的 brief 有 11 处与原文不符，子代理回原文逐格核对后**主动指出并拒绝迁就**：

| brief 的说法 | 实际（回原文核对） | 后果 |
|---|---|---|
| "延迟只涨 3.1×" 可从 Table 1 复现 | 原文 line 411 确有此句，但**同-$R$ 试算最大延迟比只有 2.47（$R{=}2$），没有任何一对能对上 3.1** | 已作为第 3 条 `[!question]` 记录，**不做回填** |
| "MACs 涨 8×" 是全模型 MMAC/s 比 | 8× = **stack 内通道宽度比** 256/32；全模型同-$R$ 比只有 **2.9–4.0×**（frontend ≈ FB、head ≈ BF 是固定开销） | 已改为限定"stack 内" |
| 结论是 routed **支配** 静态前沿 | Table 2 藏了一组论文**从未并列**的对照：`Static H=64,R=2`（10.4 MMAC/s / 2.716 / 1.215 ms）与 `Routed H=96`（10.51 MMAC/s / 2.683 / 1.040 ms）算力**几乎相同**却分在**不同表组** | 纠正为**真实 trade-off**（算力≈持平、质量 −0.033、速度快 14 %），削弱原文"matched or dominated"措辞 |
| "58.7 % 算力下降" 可直接引用 | 有两个被省略的限定：基线是"**永远跑最深 exit**"（**不是**阶梯里最省的配置），且只对**预热后的重复**测量 | 已补两个限定 |
| 74 % / 12 % 与 2.4–3.4× 是同一口径 | 74 %/12 %（Fig. 4）来自**一条示例语句**；2.4–3.4× 是"**across the test set**" | 已分开标注，禁止混用 |
| 4×33k 修复参数证明"阶梯本身单调" | 只证明**冻结特征下 repair 有效**；**未报残余违规率、未报收敛曲线** ⇒ 不能推出阶梯内在单调 | 已改为"双刃剑"表述 |
| （未发现） | 新增 4 处内部矛盾：GTCRN 页码 **10286–10290** vs 库内 **971–975**（已在 page5 渲染图逐字核对）；**`ε` 未定义**（§2.2 与 Table 2 两处口径不明）；**`asym4` 全文只出现一次且无定义**；**"26 µs/frame" 与 "+2.2 %" 只出现在 Abstract**，正文 §4.3 无支撑；**承诺的 "seed spreads" 未兑现**；`µ`/`ms` 前的多余逗号**系原文印刷**（不修正） | 已全部记录为 `[!question]` / `[!warning]` |

> **纪律沉淀（已写入 SKILL.md 与本日志）**：本次 11 项纠错中，**7 项发生在"判断词"而非"数值"上**（"支配"/"单向"/"基本不变"/"明显优于"）。
> 与第 6 批的 5/5 同类错误一致 ⇒ **brief 里只写 `A: <值> vs B: <值>`，让子代理自己算增量**，不写比较级。

### 核验结果（主 agent 执行）

| 项 | 结果 |
|---|---|
| 章节完整性 | source 页 7 个必填章节（`## 1.`–`## 7.` @ 96/143/179/372/623/745/760）+ `## 参考资料`，**齐全** |
| 违规定界符 `\(` / `\[` | 三页均为 **0** |
| MathJax 实跑（`wiki_low_latency` 全域） | **93 文件 / 3759 项公式 / 真实失败 0**（唯一标记者是 `log.md` 第 217 行的已知误报） |
| 图片嵌入 | source 页嵌 `2609.29867-page2.png` / `-page4.png`，entity 页亦嵌，**文件均存在** |
| 断链 | 新三页 **0**；全库 **3767 链接 / 105 broken**，较第 6 批基线（3608/103）**新增的 2 条正是上述两张页图的 `![[...]]` 嵌入既有误报类** |
| 逐表对数 | Table 1（10 行配置）/ Table 2（9 行）**全部回原文逐格核对，数值一致**；另核对了 Fig. 4 与 §2 的 knee target / 单调性正则定义 |
| **独立复算** | 主 agent 用 Python 独立复算同-$R$ 延迟比得 **max = 2.47**，确认 3.1× **不可由 Table 1 复现**；另核对 **~20** 个关键数字（8.48 / 2.719 / 2.60 / +0.009 / −0.001 / +0.007 / 58.7 % / 74 % / 12 % / 2.4–3.4× / 0.04–0.11 / 30 % / 1.0 dB / 26 µs / 2.2 %）均与原文一致 |

### 发表状态（venue）

**纯 arXiv 预印本**（`venue_status: preprint_only`）：arXiv 元数据无 Comments、无 Journal-ref；分类 `eess.AS` + `cs.LG` + `cs.SD`。
按本库第 3 级 venue 可信度表，落最末一档（**低于** Tsunoo 2024 的"作者自述 ICASSP 2025"）。
**注意**：本篇紧接第 6 批 FastEnhancer（同为纯预印本）⇒ **本库最近两批的 venue 可信度均为最低档**，引用时必须显式说明。

### 主 agent 更新的中央页面

`index.md`（entity / concept / source 各加 1 条 + 第 7 批表格 #29 + 计数 28→29 + `updated: 2026-09-27` + `[!note]` / `[!warning]` / `[!question]`）、
`overview.md`（批次表加第 7 批 + 第 7 批 note + 计数 28→29 + **判定口径第 10–13 条**：算力证据等级 L0–L3、µs/MMAC 离散度、算力对齐入场券、跳过状态语义审计 + 审计清单补第 ⑧ 项）、本日志。

### 本库改进建议

1. **把"算力证据等级 L0–L3"落成一张跨模型的表**——对库中所有低时延模型标注其证据等级（见 overview 第 10 条）。本库多数论文停在 L0/L1，这张表能一次性说明"为什么本库不能给出速度排行榜"。
2. **审计清单补第 ⑧ 项（accelerator launch / 调度次数）已完成**；建议对第 4 批的 Skip-DPCRN / D-GRU 回填该项——两者的"省算力"结论都建立在该项恒定的隐含假设上。
3. **给动态算力论文加一条摄取门槛**（overview 第 12 条的三个问题），可直接用于回填第 4 批两条页面的"证据边界"小节。
4. **收集"离线协议 vs 在线执行"的等价性声明**：本篇的 bit-identical 是正面样本；PSMSE 的 50 % OLA、RT-Tango-OS 的无限预热评测是需要并列的对照面。
5. **一条对本篇的重要保留**：论文说"All networks are causal at a 16 ms hop"却**未报告 STFT 的 center 锚定**；若 host 侧 STFT 用 `center=True`，则 16 ms hop 的"当前帧"本身已含未来样本 ⇒ **本篇的因果性是"模型级"而非"系统级"**。**论文没有回答这个问题**。

## [2026-09-27] ingest | GTCRN（ICASSP 2024，用户提供 PDF 补摄）

**论文**：*GTCRN: A Speech Enhancement Model Requiring Ultralow Computational Resources*（Xiaobin Rong, Tianchi Sun, Xu Zhang, Yuxiang Hu, Changbao Zhu, Jing Lu；南京大学近代声学重点实验室 + NJU-Horizon Intelligent Audio Lab（地平线）+ 江苏星火；**ICASSP 2024**）。
**产出三页**：`sources/2024/GTCRN 2024.md`（1095 行）、`entities/GTCRN.md`（629 行）、`concepts/gtcrn-2024-ultralight-subband-grouped-dprnn.md`（455 行）。
**本地 PDF**：`raw/papers/low_latency_causal_se/GTCRN-ICASSP2024.pdf`（4,378,652 bytes，5 页）；页图 `wiki_low_latency/assets/gtcrn_2024/gtcrn-page1..5.png`（150 dpi，1277×1654）；抽取文本 `tmp/pdf_extract/gtcrn.txt`（30,177 字符）。

### 为什么此前不摄、现在为什么摄

GTCRN **没有 arXiv 版本**（本库核查确认，从未上传），IEEE Xplore 付费墙，Semantic Scholar 标记 `openAccessPdf.status = CLOSED`。
按本库纪律**拒绝从付费墙版本摄取**，因此 2026-09-26 曾就"提供 PDF / 仅建索引 stub / 用官方 repo 数据 / 抓取"四选项征询用户（用户当时跳过，转去 2609.29867）。
**2026-09-27 用户直接放置 PDF** ⇒ 阻塞解除，按同一流水线补摄。**这是本库第一篇 venue 等级最高档（已正式出版）的论文。**

**版本核验（补摄必做，已写入 overview 第 16 条）**：
| 项 | 结果 |
|---|---|
| 页脚版权行 | `979-8-3503-4485-1/24/$31.00 ©2024 IEEE` ⇒ **正式出版版**（非作者自印稿） |
| 逐页印刷页码 | p.1→**971**、p.2→**972**、p.3→**973**、p.4→**974**、p.5→**975** ⇒ **pp. 971–975** |
| DOI | `10.1109/ICASSP48485.2024.10448310`（与 Semantic Scholar 记录一致） |
| PDF 元数据 | producer = `pdf-merger-js`、creator = `pdf-lib`、creationDate 2026-06-10 ⇒ **多页合并重导**，非出版社原始文件。**已在本库记录，不否定内容** |

### 补摄立即产生的三项更正

**① 页码冲突定案**：`Early Exit Compute-Matched 2026` 引文 [2] 著录为 **pp. 10286–10290**，与库内 FastEnhancer / RT-Tango / UL-UNAS 的 **971–975** 冲突。**GTCRN 原文页脚为一手证据 ⇒ 判定 971–975 正确**。**已在该页补记**（见下"回填"）。

**② 参数量三方口径矛盾（本批最重要的跨页发现）**：

| 口径 | 值 | 出处 | 可否调和 |
|---|---|---|---|
| **原文** | **23.7 K / 39.6 MMACs per second** | Abstract、§3.2、§4；**恰为 Table 1 末行 `✓/✗/✓`（23.67 K / 39.63 M/s）⇒ 内部自洽** | **基准** |
| FastEnhancer | **24 K / 40 M MACs** | 其 Table 2，脚注 a = 官方 checkpoint 评测 | ✅ 相对误差 1.3 % / 1.0 %，**四舍五入** |
| muNet | **48 K / 33 MMACs** | 其对比表第 110 行 | ❌ **参数 2.03×、MACs 0.83×，方向相反**，不可能同配置 |

与"官方 repo（`github.com/Xiaobin-Rong/gtcrn`）更新值 **48.2 K / 33.0 MMACs**"**高度吻合** ⇒ 强烈提示 **muNet 引的是官方实现实测值，原文 23.7 K/39.6 是设计声称值**；差异原因论文从未说明。**本库不单方面采信任何一方**，三套口径已并列写入 source 页 §4.8 与 entity 页 `[!contradiction]`。
> **⚠️ 留给后续**：本库多篇结论建立在"GTCRN = 40 M / 0.060 RTF"之上（第 6 批的 262M vs 40M 对照、experiments 的秩相关论证）。**若 33 M 才是真实值，这些论证的数值需复核**——但**结论方向不变**（33 M 与 40 M 同量级，均远低于 262 M）。

**③ Table 1 补出一组论文回避的对照**：

| 模块 | MACs 增量 | 参数增量 | SISNR 增量 | PESQ 增量 |
|---|---:|---:|---:|---:|
| **TRA** | 33.91 → 34.47 = **+0.56 M/s** | 13.35 → 21.65 = **+8.30 K** | +0.38 | +0.04 |
| **SFE** | 33.91 → 39.07 = **+5.16 M/s** | 13.35 → 15.37 = **+2.02 K** | +0.23 | +0.03 |

**即：TRA 用约 1/9 的 MACs（比值 9.2）换到更大的 SISNR 增益，但付出约 4.1 倍的参数。⇒ 双向 trade-off，不是单向优劣。**
论文的措辞只做 `TRA outperforms TA`（对 TA）与 `The advantages of SFE are also evident`（未量化），**回避了 TRA vs SFE 的 MACs/参数双坐标对照**。

### 子代理纠错记录（2 项，其中 1 项被主 agent 反向纠正）

| 子代理的说法 | 核实结果 | 处置 |
|---|---|---|
| **Eq. (1) 的系数结构**：brief 给 `αL_SISNR+(1−α)[βL_mag+(1−β)(L_real+L_imag)]`，**实际原式为 `αL_SISNR+(1−β)L_mag+β(L_real+L_imag)`**（**无外层 `(1−α)`**） | **✅ 子代理正确，主 agent brief 错**。主 agent 用 **900 dpi 裁剪**独立复核确认原式确实无 `(1−α)`；差异是实质的（原式下谱损失总权重恒为 1，与 α 无关） | 已按原式记录，并在 source 页列 brief 版 vs 原式版的差异对照 |
| **0.3 / 0.7 的分工**：brief 把两者并列成"mag 用 0.3、real/imag 用 0.7"的同类项 | **✅ 子代理正确**。0.3 是**压缩指数**，0.7 是**单位化指数**（`S_r/|S|^0.7`），**二者配对和为 1** | 已改正 |
| **Fig. 5 的 PESQ/STOI 标注与面板标签错位，RNNoise 优于 GTCRN，与正文方向相反** | **❌ 子代理错，主 agent 反向纠正**。子代理自己的坐标数据（x 在 168–290 为第 2 列 = `(b) RNNoise`，295–417 为第 3 列 = `(c) GTCRN`）与它的结论矛盾。主 agent 用 **600 dpi 单面板裁剪目视**确认：**(b) RNNoise = 1.16/0.66，(c) GTCRN = 1.42/0.87** ⇒ **GTCRN 在两行都更高**（1.42 > 1.16；1.94 > 1.28），**与正文 §3.3.2 及 Table 2/3 方向一致** | 已改正 source / entity / concept 三页共 7 处，并保留"初稿曾误判"的说明作为**复核方法**的记录 |

> **纪律沉淀（新增一条）**：**PDF 图内的浮动文本标注，其归属不能靠"文本块坐标"单独判定，必须辅以渲染图裁剪目视。**
> 本篇 Fig. 5 的四个 PESQ/STOI 数字在文本流里**没有面板标签**，`get_text()` 把它们与面板标签拆到不同块中，坐标扫描极易错配列序。**本次子代理正是在这一步出错，且它的错误结论被自己的数据否定。**
> 建议写入 SKILL.md：**凡涉及"图内标注归属"的判断，一律以渲染图目视为准，坐标只作辅助；若两者冲突，报"需看原图"，不得下结论。**

### 核验结果（主 agent 执行）

| 项 | 结果 |
|---|---|
| 章节完整性 | source 页 7 个必填章节（`## 1.`–`## 7.` @ 122/174/215/528/856/1044/1065）+ `## 参考资料` @ 1070，**齐全** |
| 违规定界符 `\(` / `\[` | 三页均为 **0** |
| `.md` 后缀 wikilink | 三页均为 **0** |
| callout 数 | source 53 / entity 25 / concept 17 |
| 独立复核 | **Eq. (1) 用 900 dpi 裁剪逐字确认**（含系数位置）；**Fig. 5 用 600 dpi 单面板裁剪目视确认**（含面板归属）；Table 1/2/3 数值与 `tmp/pdf_extract/gtcrn.txt` 逐格比对一致 |
| 页码 | 逐页页脚 971–975，与 source 页记录一致 |

### 回填（本次同步完成的既有页面修改）

1. `sources/2026/Early Exit Compute-Matched 2026.md`：**GTCRN 页码 `[!question]` 补入"已由 GTCRN 原文一手证据定案为 971–975"**。
2. `wiki/sources/2026/muNet 2026.md`：**"对比对象 GTCRN 也不在库内"的表述已过时**，改为指向 `[[wiki_low_latency/entities/GTCRN]]`，并标注其 48 K/33 与原文 23.7 K/39.6 的口径矛盾。
3. `outputs/experiments/index.md` + `可融合性结构体检×端侧RTF实测.md`：**GTCRN 40M 的口径加注**（原文 39.6 MMACs/s，官方实现 33.0，三方矛盾待复核）。

### venue

**`venue_status: published`** —— ICASSP 2024 正式出版，版权行 `979-8-3503-4485-1/24/$31.00 ©2024 IEEE`，DOI `10.1109/ICASSP48485.2024.10448310`，pp. 971–975。
**本库 venue 分级最高档**，与第 6 批（FastEnhancer，纯预印本）与第 7 批（Early Exit，纯预印本）**形成直接对照** ⇒ **本库最近三批的 venue 可信度覆盖了最高与最低两档**。

### 主 agent 更新的中央页面

`index.md`（entity / concept / source 各加 1 条 + 第 8 批表格 #30 + 计数 29→**30** + `updated: 2026-09-27` + `[!important]` 批次 note + **GTCRN 页码 `[!question]` 改为"已定案"**）、
`overview.md`（批次表加第 8 批 + 第 8 批 `[!important]` note + 计数 29→**30** + **判定口径第 14–16 条**：锚点数值先钉口径、"引用即负有义务"、用户提供 PDF 的核验要点）、本日志。

### 本库改进建议

1. **建立"锚点清单"**：把库内被 2 篇以上同时引用为基线的模型（GTCRN、DPCRN、RNNoise、DeepFilterNet2、FSNet 等）单列一页，**逐个记录其原文声称值 + 各引用方给的值 + 是否有矛盾**。本次 GTCRN 的 3 套口径说明这个需求是真实的。
2. **对库内所有"X K / Y M"型结论做一次口径复核**——特别是第 6 批 FastEnhancer 的"262M vs 40M、MACs 高 6.5× 却快 2.7×"这条**被引用了 6 次以上**的论证。
3. **把"图内浮动标注的归属必须目视确认"写入 SKILL.md**（本次子代理在此出错）。
4. **收集"子带路线"的三方评价**（GTCRN 自身无速度数据 / FastEnhancer 批评 RTF / PSMSE 批评容量），可做成一张对照页。
5. **一条对 GTCRN 的重要保留**：论文说 `All networks are causal` 之类的话并不存在，它只有一句 `so that the causality of the model can be guaranteed`（针对 inter-frame 单向 GRU）；**STFT 的 center 锚定未报告** ⇒ 若 host 侧用 `center=True`，hop 16 ms 的"当前帧"本身已含未来样本，**则该模型的因果性是"模型级"而非"系统级"**。**论文没有回答这个问题**。

---

## [2026-09-27] synthesis | 方法全景（动机 / 前后端 / 网络设计）

**用户请求**：「帮我做一下现在的 low latency 的整个库的概括，我主要想看一下这些方法的前后端处理，还有网络是如何设计的，最主要的是，他们的 motivation 是什么，总结成一份 md 放到 wiki_low_latency 下面」

**产出**：`wiki_low_latency/方法全景：动机·前后端·网络设计.md`（**445 行 / 37,689 字节**，`type: synthesis`）。

### 本页的组织结构（按用户的三条优先级）

| 节 | 内容 | 对应请求 |
|---|---|---|
| 一 | 全局约束：为什么"低时延"是一组约束 | 铺垫 |
| 二 | **动机全景** — 30 篇 → 9 类矛盾 + 6 条最值得记住的动机叙事 + 动机/定位错位表 | ⭐ 用户最看重 |
| 三 | **前后端处理** — 前端 5 条路线 / 后端 3 种砍延迟手法 / **前端配置总表（24 篇逐项）** / 掩蔽类型 7 类 | ⭐ |
| 四 | **网络设计** — 5 种骨干拓扑 / 8 项延迟判据 / 5 种轻量化手段 / GTCRN 架构解剖 | ⭐ |
| 五 | 横向对照：延迟 / 算力 / 因果性三维总表（22 篇） | 附加 |
| 六 | 四条方法论结论 | 提炼 |
| 七 | 库内尚未解决的 8 个核心问题 | 提炼 |

### 写作纪律（全部遵守）

- **不新增证据**：所有数值可回溯 source 页；source 页写「未报告」的，本页**同样不补写**（前端总表空白处即为"论文未报告"）。
- **不做跨口径排序**：算力列明确标注"禁止跨口径比较"（GTCRN 的 39.6/40/33 三套口径）。
- **因果性按库内第 1 条**：「自称单向」与「逐层可核验」分开记账。
- 非法定界符 `\(` / `\[`：**0**。

### 本页产生的新组织性发现（不是新事实，是新归类）

1. **动机可归为 9 类矛盾**（M1 算力落差 / M2 够小与够好无交集 / M3 MACs 降 RTF 升 / M4 预算须按最坏情况 / M5 无人做算力对齐 / M6 短片段训练目标信息不足 / M7 时延被当二元选择 / M8 抑噪与人声保留零和 / M9 瞬时时延下算力爆炸）——**KD 系全部论文的动机都是 M6 的变体**，差别只在"注入什么"。
2. **"砍算法延迟"在库内只有三种工程手法**：非对称/双窗 STFT（长分析窗 + 短合成窗）· 非对称 padding 分配 · 双速/双缓冲复用。**其余所有手段都不改算法延迟，只改算力或质量。**
3. **前端配置总表 24 行**是本库第一次把窗/hop/FFT/center 并排呈现 ⇒ 直接暴露出**「STFT center」在 11 篇里未报告**这个最大的系统性审计缺口。
4. **"流式"在库内有三种互不兼容语义**（跨帧固定状态 / 逐帧重置+OLA / 块间无状态靠 padding 保证等价），此前散落在各页，本页首次并列。

### 库级改进建议（供后续）

1. **建"锚点清单"页**（`wiki_low_latency/锚点清单.md`）：把被 ≥2 篇引用的库外模型逐个登记三套口径——GTCRN 的三套口径已证明这个需求是真的（本轮 `outputs/experiments/锚点口径复核×超轻量延迟账本.md` 已列为第一步）。
2. **补一份"STFT center 审计表"**：把 11 篇未报告 center 的论文列为待查，这是唯一能解除"算法延迟双向不确定"的办法。
3. **子带路线三方评价对照页**：GTCRN 自身无速度数据 / FastEnhancer 批评其抬高 RTF / PSMSE 批评其容量——本库一对直接冲突，值得单列。
4. `overview.md` 的「## 当前状态」段现在应加上"已有 1 篇 synthesis 页"的指向（本页已在 `index.md` 综述区登记）。

### 核验

| 项 | 结果 |
|---|---|
| MathJax 实跑 | **249 文件 / 4960 项 / 真实失败 0**（唯一标记者 = `log.md` L217 既有误报） |
| 断链 | 本页 **0**；全库 **4082 / 110**（broken 数与上一基线 4057/110 **完全持平**，说明本页 25 条链接全部解析成功） |
| 引用页面存在性 | 9 个被引概念页 + 30 篇 source 页 **全部 OK** |
| 非法定界符 | **0** |

---

## [2026-09-27] ingest | PrimeK-Net 2025（arXiv:2502.19906，ICASSP 2025）—— 第 31 篇

**用户请求**：「寻找一下PrimeK-Net，并且下载解析」

### 定位与获取

| 项 | 结果 |
|---|---|
| 定位 | **arXiv:2502.19906**，标题 *PrimeK-Net: Boosting Speech Enhancement with Prime Kernel and Multi-Scale Dense Block* |
| venue | **ICASSP 2025** —— arXiv `Comments` 字段写明 "This paper was accepeted by ICASSP 2025"（原文拼写如此）；按本库第 16 条，`Comments` 是**唯一被承认的录用证据** ⇒ `venue_status: published` |
| 作者 | Zizhen Lin（四川大学）/ Junyu Wang（天津大学）/ **Ruili Li（东北大学，通讯）** / Fei Shen（南京理工）/ Xi Xuan（中国香港城市大学） |
| 官方代码 | `github.com/huaidanquede/PrimeK-Net` |
| 下载 | `raw/papers/low_latency_causal_se/2502.19906.pdf`（**5,637,523 字节**，5 页） |
| 抽取 | `tmp/pdf_extract/primeknet.txt`（20,880 字符）；5 页 150 dpi 渲染 → `wiki_low_latency/assets/primek-net_2025/` |

### 建页（三页，均符合 7 段式模板）

- `wiki_low_latency/sources/2025/PrimeK-Net 2025.md`（source，含 `~~~yaml` 卡 + §1–§7 + 参考资料）
- `wiki_low_latency/entities/PrimeK-Net.md`（entity）
- `wiki_low_latency/concepts/2502.19906-prime-kernel-multiscale-dense-block.md`（concept）

### 补摄取得的三项实质性发现

1. **`12.67%` 独立复核成功**——论文声称 DSDDB 复杂度为 DDB 的 12.7%；本库按 Eq. (5)–(10) 用 $n=4, C=64, K=3$ 独立重算得 $46720/368640 = 12.67\%$ ⇒ **内部自洽，数字可信**。这是本库第一次对"复杂度压缩比"做逐式复核并给出正结果，可作为后续模板。
2. **库内首次出现 FLOPs 量纲 → 新增 `[!contradiction]`**——PrimeK-Net 报 **44.64 G FLOPs**，而库内其余绝大多数报 **MACs**（GTCRN 39.6 MMACs/s、FastEnhancer 262M MACs）。按 $1\text{ MAC}\approx 2\text{ FLOPs}$ 换算后仍**差三个数量级**，且分母不同（每句 vs 每秒）⇒ **这两个数字禁止放进同一次效率比较**。
3. **引用链断点：损失权重**——`LaCo-SENet 2026` 写"损失完全沿用 PrimeK-Net"并给出 $0.9/0.3/0.1/0.05/0.05$，但**PrimeK-Net 全文未给任何 $\lambda$ 数值**（只定义 $\mathcal L_{old}$ Eq.11 与 $\mathcal L_{new}$ Eq.12 的形式）。⇒ "沿用"的对象不可能是原文数值。**本库不判定谁对，按双方原文并列记录**。

### 同时标注的一处因果缺口（原文未承认）

**SCA 的 `AdaptiveAvgPool1d` 时间作用域未定义。** PrimeK-Net 的 SCA 用自适应平均池化产生通道描述子，若池化跨整个时间轴（LaCo-SENet §3.4 记载其原始形式为 `AdaptiveAvgPool1d(1)`，即全局），则每帧注意力依赖全句所有帧，**模型严格非因果且无法流式**。PrimeK-Net 原文**未说明该池化的时间作用域**，也**未声明有流式版本**。
⇒ 库内判定：**结构上非因果**（由 SCA + 无因果声明共同确定），但作者从未正面讨论。

### 它对全库的定位价值：补上"同一架构内的非因果质量上界"

此前本库所有"因果化代价"的讨论都**缺少同一架构内的紧上界**。PrimeK-Net 提供了这个上界——**同一骨干、同一损失、同一数据、同一前端（STFT 400/400/100 @16 kHz，与 LaCo-SENet 完全一致）**，只差"能不能看未来"：
**3.61（非因果）vs 3.35（12.5 ms 全因果）= 0.26 PESQ 的因果化代价**，是全库**口径最干净**的一组因果-非因果对照。

进库路径与 GTCRN **恰好相反**：GTCRN 是"被四篇引用 → 无一手证据 → 用户提供 PDF"；PrimeK-Net 是"**库内 LaCo-SENet 页早已把它当作骨干、损失来源、Table 1 上界反复引用，而它自身没有页面**"。补摄后**三条悬空引用链一起落地**：骨干（1.37M vs 1.41M）、损失（五个系数）、质量上界（3.61）。
**同时确立一条记账区分**：非因果模型**不能参与因果排名**（LaCo-SENet 自己标为 ‡），**但可以且应该参与"上界"与"代价"的度量**——两类用途必须分开记。

### 中心页回填

| 页 | 改动 |
|---|---|
| `index.md` | 实体区 +1 行（PrimeK-Net）；概念区 +1 行；source 区 +1 行；`30 篇` → **`31 篇`**；新增 **batch-9 表格 + 4 个 callout**（`[!important]` venue/进库路径/上界价值、`[!contradiction]` FLOPs 量纲 + 损失权重断点、`[!question]` SCA 因果缺口、`[!note]` 12.67% 复核） |
| `overview.md` | 「当前状态」表 +第 9 行；`已分八批 / 30 篇` → **`已分九批 / 31 篇`**；新增 **batch-9 `[!important]` 段** |
| `sources/2026/LaCo-SENet 2026.md` | §3.5 骨干行 + 损失行补 wikilink；损失段新增 **`[!contradiction]`**（五个 $\lambda$ 系数在 PrimeK-Net 原文不存在）；Table 1 的 PrimeK-Net 行新增 `[!note]` 口径核验；§6 cross-reference「库中暂无 PrimeK-Net 页」→ 指向新页并补两条 caveat |
| `entities/LaCo-SENet.md` | 定义段 / 骨干行（表格内转义 `\|`）/ 损失行 / 可比性提醒 **4 处**补 wikilink 与 caveat |

### 核验

| 项 | 结果 |
|---|---|
| MathJax 实跑 | 见下（本轮） |
| 断链 | 见下（本轮） |
| 非法定界符 `\(` / `\[` | 三个新页 **0** |

### 后续建议（升级优先级）

1. **"锚点清单"页现在更有必要了**：库内被 ≥2 篇引用的库外锚点已包括 GTCRN（3 套口径）、PrimeK-Net（新入）、DPCRN、RNNoise、DeepFilterNet2/DN3、aTENNuate。**且新增一类锚点问题——"引用方声称沿用、原文却没有"**（损失权重），这是 GTCRN 的"数值不一致"之外的**第二种锚点风险**。
2. **"STFT center 审计表"**：PrimeK-Net 与 LaCo-SENet 是库内少数**同前端**的两篇（400/400/100），可作为该表的基准行。
3. **子带路线三方评价对照页**：PrimeK-Net 的 GPFCA 是"分组频率卷积"路线的另一实现，可与 GTCRN 的 ERB 分组、FastEnhancer 的批评并置。

---

## [2026-09-27] ingest | LiSenNet 2024（arXiv:2409.13285）—— 第 32 篇

**用户请求**：「LiSenNethe 和FSPEN 找一下并且按照之前的流程写好笔记」

### 定位结果（**一篇成功、一篇受阻**）

| 论文 | 状态 | 细节 |
|---|---|---|
| **LiSenNet** | ✅ **已入库** | **arXiv:2409.13285**，*LiSenNet: Lightweight Sub-band and Dual-Path Modeling for Real-Time Speech Enhancement*；Haoyin Yan / Jie Zhang（通讯，USTC NERC-SLIP）/ Cunhang Fan（安徽大学）/ Yeping Zhou / Peiqi Liu（**招商银行 CMB 深圳**）；官方代码 `github.com/hyyan2k/LiSenNet` |
| **FSPEN** | ⛔ **受阻，需用户提供 PDF** | **ICASSP 2024, pp. 10671–10675**，DOI `10.1109/ICASSP48485.2024.10446016`；Lei Yang / Wei Liu / Ruijie Meng / Gunwoo Lee / Soonho Baek / Han-gil Moon（**Samsung**，ICASSP 2024 SLP-P3.6 海报）；**IEEE 付费墙 + 无 arXiv 版**（Semantic Scholar `openAccessPdf: CLOSED`）⇒ 按本库规则**不得从付费墙摄取** |

### venue 判定：LiSenNet 是**纯预印本**（本库第一次明确区分 "submitted to" 与 "accepted by"）

arXiv `Comments` 字段原文 = **"5 pages, submitted to 2025 IEEE International Conference on Acoustics, Speech, and Signal Processing (ICASSP 2025)"**。
⇒ **这是投稿记录，不是录用证据**。判定为 **(c) 档纯预印本**，`venue_status: preprint_only`，**不标任何会议**。
**与 GTCRN / PrimeK-Net 的对照**：那两篇的 `Comments`/页脚给的是 "accepted by" 或版权行（(a) 档），本篇是 "submitted to"（(c) 档）。
**新增一条判据**：arXiv `Comments` 里的会议名**只有在表示"已被录用"时才构成录用证据**；`submitted to` 语义相反。

### 进库路径：本库**首次以"纯路径 B"补摄**

库内 `FastEnhancer`（§2.2 批评 + Table 2 的 ^b/^c 两行）、`PSMSE`（归入容量受限）、`GTCRN`（并列子带路线）三页都在引用 LiSenNet，而它自身没有页面。

### 建页（三页）

- `wiki_low_latency/sources/2024/LiSenNet 2024.md`
- `wiki_low_latency/entities/LiSenNet.md`
- `wiki_low_latency/concepts/2409.13285-subband-stride-and-convglu-compensation.md`

### 技术要点（一手证据）

- **五个组件**，三个是自有贡献：**子带 DS-Conv/US-Conv**（低频 `stride=1`、高频 `stride=3`，**合并因子仍为 2 ⇒ 零预算重新分配**）· **DPR 模块**（频率轴 Bi-GRU(12) / 时间轴 uni-GRU(24) + **ConvGLU 容量补偿**）· **噪声检测器**（64 维 Mel → **帧级**二值门控）。
- 其余两个：**相位差（PD）输入**（Δt 需减 2πfQ/M 去基带偏移）· **GLA 相位精修**（k=2）。
- `L = 0.9·L_mag + 0.1·L_comp + 0.05·L_pesq + L_bce`；功率压缩 **c = 0.3**。
- 16 kHz；Hanning **window 512（32 ms）/ hop 256（16 ms）**；AdamW 100 epochs，lr 5e-4×0.98。
- **37k 参数 / 56M MMACs per second / PESQ 3.07 / STOI 0.939**（VoiceBank+DEMAND）；WSJ0+ESC50 PESQ 3.08 / **RTF 0.028（Xeon E5-2620 v4）**。

### 三项实质性发现

1. **"超轻量三角"补齐第三边**（GTCRN 23.7K / **LiSenNet 37k** / FSPEN 79k）。三者轻量化手段**正交**：GTCRN 改「通道怎么分」（ERB）、PrimeK-Net 改「核怎么取」（素数核）、**LiSenNet 改「采样率怎么变」**（strides）——**本库首次把三种分组压缩哲学并列**。
2. **库内最极端的"平均算力 ≠ 可用算力"反例**：ND 把 MACs 变成区间 **15M ∼ 70M**，而**最坏情况 70M 比不加 ND 的 56M 还高 25%**。另三个动态算力案例（Skip-DPCRN 讨论过峰值只降 ~15%、D-GRU 以恒定算力为设计目标、Early Exit 真机逐图）**都讨论过峰值，只有本篇零讨论**。
3. **由单篇论文自带的 N 扫描导出边际收益递减曲线**：N: 0→1 边际 **+0.171 PESQ/10M MACs**、1→2 **+0.059**、2→3 **−0.006** ⇒ **同一模块的边际效率在 16M MACs 尺度上衰减 29 倍并转负**。这是本库少见的、同数据同训练同评测支撑的收益递减曲线（远优于跨论文拼接的 Pareto 图）。

### 补摄引入的**三条外部独立证据**（来自 FastEnhancer，本篇原文完全没有）

| 项 | FastEnhancer 记载 | LiSenNet 原文 |
|---|---|---|
| **流式性** | ^b「**Not streamable because of input normalization and griffin-lim**」 | **从未提及** |
| **可流式子版本** | ^c（去掉 normalization + griffin-lim 后重训）PESQ **2.98** | **无此版本** |
| **扩展指标** | SCOREQ 0.425/0.335、SISDR 13.5/18.5、BAK 3.90/4.03、WER 3.7/3.4 | **全部未报告** |

⇒ 已立 `[!contradiction]`：**两篇对"LiSenNet 有几个版本"的指称不一致**（本篇 1 个 vs FastEnhancer 2 个）。最可能解释：^c 是 FastEnhancer **自行改造重训**的，而「**流式化代价 3.08→2.98**」是**它独立测量的**。

### 同时标注的一处因果缺口

**GLA 相位精修（k=2）是整段迭代式后处理，但论文自陈 "for real-time applications" 且从未说明 GLA 如何流式实现、也未把其开销计入 RTF。** FastEnhancer 独立指出它正是不可流式的原因之一。⇒ 本库判定：**GLA 是本篇"实时"声称中最薄弱的一环**。附：全篇**无任何算法延迟数字**、**STFT center 未报告** ⇒ 算法延迟在 **16 ms（center=False）或 32 ms（center=True）** 之间**双向不确定**，**不是 2 ms 候选**。

### 一条正面对照（为第 14 条判据提供正例）

LiSenNet 的 **37k / 56M** 在 Abstract、§I、Table I、Table III **四处原文**与 FastEnhancer 的 **^b/^c 两行**中**完全一致、无任何矛盾**。
⇒ 与 [[wiki_low_latency/entities/GTCRN]]（三套口径：23.7K/39.6 vs 24K/40 vs 48K/33）和 [[wiki_low_latency/entities/PrimeK-Net]]（FLOPs 新量纲 + 损失权重引用链断点）形成对照。**当锚点的多份记录完全一致时，说明该方向的引用是干净的。**

### 一条对既有结论的**修正**（回填产生）

`GTCRN` 概念页的子带路线批评表新增一行：**LiSenNet 自报 RTF 0.028，低于同表所有非子带基线**（CRN 0.042 / DCCRN 0.184 / FullSubNet 0.386）。
⇒ **"子带 ⇒ RTF 更高"不是普适规律**：FastEnhancer 的批评对 LiSenNet **不成立**。**该批评必须按模型逐个验证，不能按路线整批引用。**

### 中心页回填

| 页 | 改动 |
|---|---|
| `index.md` | 实体/概念/source 各 +1 行；`31 篇` → **`32 篇`**；新增 **batch-10 表格 + 4 个 callout** |
| `overview.md` | 批次表 +第 10 行；`已分九批 / 31 篇` → **`已分十批 / 32 篇`**；新增 batch-10 `[!important]` 段 |
| `sources/2024/GTCRN 2024.md` | 3 处补 wikilink（含关键冲突行的**反证补充**） |
| `sources/2025/FastEnhancer 2025.md` | §2.2 表格行补 wikilink；**新增 2 个 callout**：① LiSenNet 补摄后的三条对照结论 ② **FSPEN MACs 两值矛盾的根因就是本篇**（64M vs 89M，不可调和，并列不择一） |
| `sources/2026/PSMSE 2026.md` | Related Work 行补 wikilink；「库中暂无页面」表**更新补摄状态**（GTCRN/LiSenNet 已完成，FSPEN 仍缺） |
| `concepts/gtcrn-2024-ultralight-subband-grouped-dprnn.md` | 批评表 **新增反证行** + `[!important]` |

### 核验

| 项 | 结果 |
|---|---|
| MathJax 实跑 | 见下（本轮） |
| 断链 | 见下（本轮） |
| 非法定界符 `\(` / `\[` | 三个新页 **0** |

### 库内缺口（明确记录）

1. **FSPEN 仍无页面** —— IEEE 付费墙 + 无 arXiv。它是 LiSenNet 的主竞品，且其 MACs 在库内有 **89M（LiSenNet 转述原文）vs 64M（FastEnhancer 重实现）** 两个不可调和的值。**需用户提供 PDF 方可补摄。**
2. **UL-UNAS / CleanUNet2 / aTENNUate / L-DPSB / HiFi-Stream** 及 SNN 三分支（SpikingS4 / DPSNN / Spiking-FullSubNet）库中仍无页面。
3. **"锚点清单"页与"STFT center 审计表"仍未建** —— 本轮再次暴露需求：LiSenNet、FastEnhancer、GTCRN 三篇的 center 全部未报告。

---

## [2026-10-07] ingest | INTERSPEECH 2026 方法学维度成组补摄（5 篇新增，第 11 批）

### 触发

用户按**八个设计轴**点名论文并询问"仓库还缺什么"：

| 用户点名的主题 | 论文 | 库内状态 |
|---|---|---|
| 计算冗余 | HALO | ❌ 缺 → 本批补摄 |
| future context / algorithmic latency | LaCo-SENet | ✅ 已在库（#31） |
| future context / algorithmic latency | Latency Controllable SE (LCA) | ❌ 缺 → 本批补摄 |
| past state / long-term modeling | RT-SEMamba | ✅ 已在库（#20） |
| 频率结构怎么建模 | SEMamba++ | ❌ 缺 → 本批补摄 |
| 哪里该增强、哪里不该杀语音 | TF Weighted Losses | ❌ 缺 → 本批补摄 |
| 极低延时 pipeline | RT-Tango | ✅ 已在库（#21） |
| 生成式能不能靠近实时 | Schrödinger Bridge Mamba (SBM) | ❌ 缺 → 本批补摄 |

⇒ **结论：8 篇中 3 篇已在库，5 篇缺失。** 本批补摄这 5 篇，篇数 **32 → 37**。
**这是库内首次按"方法学维度"（而非任务/年份）成组补摄**，覆盖冗余 / 延迟旋钮 / 状态建模 / 频率结构 / 损失加权 / 生成式六条互不重叠的设计轴。

### 原件归档

| 文件 | 大小 (bytes) | 页数 | venue | DOI |
|---|---:|---:|---|---|
| `raw/papers/low_latency_causal_se/HALO-Interspeech2026.pdf` | 750,026 | 5 | Interspeech 2026, pp. 2999–3003 | 10.21437/Interspeech.2026-601 |
| `raw/papers/low_latency_causal_se/LatencyControllableSE-Interspeech2026.pdf` | 767,626 | 6 | Interspeech 2026, pp. 3009–3014 | 10.21437/Interspeech.2026-2997 |
| `raw/papers/low_latency_causal_se/SEMambaPP-Interspeech2026.pdf` | 1,349,947 | 10 | Interspeech 2026 [Long Track], pp. 5166–5175 | 10.21437/Interspeech.2026-665 |
| `raw/papers/low_latency_causal_se/TFWeightedLoss-Interspeech2026.pdf` | 491,198 | 5 | Interspeech 2026, pp. 7075–7079 | 10.21437/Interspeech.2026-3416 |
| `raw/papers/low_latency_causal_se/SchrodingerBridgeMamba-Interspeech2026.pdf` | 952,896 | 6 | Interspeech 2026, pp. 1363–1368 | 10.21437/Interspeech.2026-682 |

**venue 判据**：五篇均为 ISCA Archive 官方录用版 PDF，**页脚均印有 `Interspeech 2026 / 27 September - 1 October 2026, Sydney, Australia` + 对应 DOI**，且**逐页印刷页码连续递增**（2999→3003 / 3009→3014 / 5166→5175 / 7075→7079 / 1363→1368）⇒ **venue 证据等级 (a) 已正式出版**，一手确定卷页与 DOI。全部加 `venue_status: published`。

**下载方式**：ISCA Archive 直链 `https://www.isca-archive.org/interspeech_2026/<key>_interspeech.pdf`（key 分别为 `zhao26c` / `sato26` / `lee26f` / `monir26` / `yang26e`）。**全部 http_code=200、content_type=application/pdf**，无需付费墙绕过。**元数据（作者、页码、DOI）从对应的 `_interspeech.html` 的 `citation_*` meta 标签抓取**，未从 PDF 正文推断。

### 新增页面统计

| 论文 | source 行数 | entity 行数 | concept 行数 |
|---|---:|---:|---:|
| HALO | 387 | 241 | 171 |
| Latency Controllable SE (LCA) | 454 | 247 | 206 |
| SEMamba++ | 487 | 291 | 251 |
| TF Weighted Losses | 422 | 212 | 234 |
| Schrödinger Bridge Mamba (SBM) | 456 | 300 | 237 |
| **合计** | **2206** | **1291** | **1099** |

新增页面路径：
- `wiki_low_latency/sources/2026/{HALO 2026, Latency Controllable SE 2026, SEMamba++ 2026, TF Weighted Losses 2026, Schrodinger Bridge Mamba 2026}.md`
- `wiki_low_latency/entities/{HALO, LCA-Latency-Control-Adapter, SEMamba++, TF-Weighted-Losses, Schrodinger-Bridge-Mamba}.md`
- `wiki_low_latency/concepts/{halo-2026-half-frame-rate-operator, lca-2026-latency-control-adapter, semamba-pp-2026-frequency-glp, tf-weighted-sdr-2026, sbm-2026-schrodinger-bridge-mamba}.md`

**页面渲染资产**（150 dpi，共 32 张）：`wiki_low_latency/assets/{halo_2026, lca_2026, semamba-pp_2026, tf-weighted-loss_2026, sbm_2026}/`
**抽取全文**：`tmp/pdf_extract/{halo, lca, semamba-pp, tf-weighted-loss, sbm}.txt`
**抽取脚本**：`tmp/extract_5_interspeech2026.py`

### 执行方式

1. **主 agent 先通读五篇全文**（抽取文本共约 187k 字符），再落笔。**未派子 agent**——首轮派出 5 个子 agent 后返回空结果、未产出任何文件，遂改由主 agent 直接撰写。
2. 中心页与交叉链接由主 agent 统一更新。
3. 关键表格（HALO Table 1/2、LCA Table 1/2/Fig.3、SEMamba++ Table 1–8、TF Weighted Table 1/2、SBM Table 1–3）**全部逐格回抽取文本核对**；LCA Figure 3 的曲线形状与相对位置**回 150 dpi 渲染图目视核对**。

### 主 agent 审核结论

**① 结构检查**：5 篇 source 页均有 YAML frontmatter + `~~~yaml` 快速索引卡 + PDF warning + **7 个一级章节** + `## 参考资料`（脚本核验：`章节=7 参考=1 yaml卡=1`，五页全通过）。

**② MathJax 实跑**：全库 **278 文件 / 5882 公式 / 失败 1**。唯一失败是 `wiki_low_latency/log.md` 讨论定界符的既有误报。**本轮 15 个新页面失败数 = 0。**

**③ 断链**：全库 `links: 4706 / broken: 117`（上批基线 4257/111）。
- **本轮 15 个新页面贡献 0 条断链**（逐个验证：**47 个唯一 wikilink 目标，0 缺失**）。
- `broken` 从 111 → 117 的 **+6 全部来自 `outputs/reports/2026-10-06-trends/` 的 4 份趋势报告**（创建于 2026-10-06/07，晚于上批基线），指向被改名/未创建的报告页。**与本轮无关。**
- 全库 25 条非图片类断链**全部为既有**（`CLAUDE.md` 模板占位、趋势报告、`wiki/` 与 `wiki_array/` 的历史遗留），无一在本轮文件中。
- 本轮 15 个页面**无任何图片/PDF 嵌入** ⇒ 不产生检查器的图片误报。

**④ 非法定界符**：本轮 15 个页面 `\(` 与 `\[` **均为 0**。
**⑤ 坏 wikilink 自查**：`grep -n '\[\[[^]]*→'` 无命中。
**⑥ 数字溯源抽查**（逐项回原文核对，非只看结论段）：
- HALO：Table 1 的 8 行、Table 2 的 16 行逐格核对；`22.05 / 33.83` 的 −34.8% 与 `2.093 / 2.101` 的 −0.008 独立算出。
- LCA：**独立复核 Eq.(5)** —— $X=6$ 单调 pattern 得 $\{0,1,3,7,15,31,63\}$，与正文 $T_{la}$ 集合一致 ⇒ 判定 **Eq.(5) 正确、正文 "$2^i$" 是 1-based 笔误**；**独立复核七档延迟**（$160/16000=10$ ms、$40/16000=2.5$ ms）逐项吻合 ⇒ 已写明"已独立复核"；**独立算出 76% 对应 (C-2)**（$104.1\to24.5$ M = 76.5%）而 (C-1) 为 84.2% ⇒ 标 `[!question]` 两数并列。
- SEMamba++：Table 1–8 全部核对；**Table 4 的灰底（未见退化强度）在文本抽取中丢失**，列归属依据表头范围 + 训练设置（SNR ∈ [−10,20]、cutoff 2–7 kHz）推得 −15 dB 与 1 kHz 在训练范围外，并已注明"未逐格核实灰底边界"。
- TF Weighted Losses：Table 1/2 全部核对；**逐项列出"增益 vs 代价"**（辅音 SSN 的 SDR 0.5→0.0、FW-SDR 6.4→6.1；元音 WN 的 FW-SDR 8.4→7.7 均为**下降**）。
- SBM：Table 1（3 组 × 9 行）、Table 2（9 行）、Table 3（6 行）全部核对；**独立核算算法延迟**：$480/16000=30$ ms（$\tau_{enc}$）+ $4\times10=40$ ms（$\tau_{sep}$）⇒ 论文 "under 40 ms" **只含 $\tau_{sep}$**，实际 **50–70 ms**。

### 关键结论与发现的原文不一致

**（A）本轮最重要的正面发现：库内延迟账本口径首次获外部正式发表论文独立背书。**
LCA §3.2 独立给出 $\tau=\tau_{enc}+\tau_{sep}$、**"causal 当且仅当 separator 不使用未来帧，尽管 $\tau_{enc}$ 依然存在"**、以及**"存在漏报 buffering 项的文献，比较时须小心 [29]"** —— 与库内 `concepts/严格因果与算法延迟`、`concepts/低时延前端与延迟账本` **逐字同构**。
且其 [29] 正是 **Wu & Braun（arXiv:2409.10358，已在库内）** ⇒ **证据链闭合**：原始提出 → 库内采纳 → 外部独立确认。
**这条口径立刻抓到新误报**：SBM 的 "under 40 ms" 漏计 30 ms 窗 ⇒ 实际 50–70 ms。

**（B）GTCRN 算力出现第三个记录 ⇒ 锚点风险升级为三方并列。**
HALO 报 GTCRN 为 **23.67 k / 33.83 M MAC/s**（参数吻合原论文 23.7 K，算力吻合引用方 B 的"33"那一族）⇒ **混合口径**。
已三方并列记录、标 `[!contradiction]`、不选边，并提示"引用 GTCRN 算力前必须声明口径"。
**反面正例**：HALO 报 LiSenNet 为 **36.78 k / 55.77 M MAC/s**，与原文自报 **37 k / 56 M** 吻合（0.6% / 0.4%）⇒ **库内首次出现外部论文对 LiSenNet 参数-算力口径的独立复现确认**。

**（C）新增第 4 种"平均算力 ≠ 可用算力"机制：结构性平均-峰值分离。**
HALO 自陈"**不降低峰值每步算力**，因为帧率恢复算子在同一次推理步里生成两个相邻帧"。此前三个案例（Skip-DPCRN / D-GRU / Early Exit）全是**动态算力**；HALO 是**结构性**的。⇒ 已写入 overview 第 17 条判据。

**（D）"轻量化收益边际递减"在两条不同自变量的曲线上重复出现。**
HALO 沿**骨干容量**递减（DPCRN ultralight +0.187 → light +0.101 → middle +0.062 → large +0.014；UL-UNAS +0.016）；
LiSenNet 沿**模块数量**递减（+0.171 / +0.059 / −0.006）。⇒ 合并说明"**在轻量区间，任何单一手段的收益都会很快见底**"。

**（E）一处对库内既有假设的反例：保人声加权的有效区间有下界。**
TF Weighted Losses 实测：极低 SIR（−8 dB）时**基线在 band 6 以上的爆破音频谱更接近干净参考、PA 略高**；SSN 下 0 dB 以下基线 WER 最低；纯可学习权重在 SSN 下全面失败。
⇒ **不能假设"更强的保人声加权在更低 SNR 下更有效"。** 已写入 overview 第 19 条判据。

**（F）"生成式能不能靠近实时"必须拆成两个轴。**
SBM：**吞吐轴 ✅**（一步、RTF 0.0048、比 SB-NCSN++(50) 快 160×、与 Mamba-base 零 RTF 代价）；**算法延迟轴 ❌**（2–4 帧 lookahead + 30 ms 窗 ⇒ 50–70 ms，距 2 ms 目标 25–35 倍）；**质量轴 ⚠️**（PESQ/ESTOI/SpeechBERTScore 仍输给判别式 ZipEnhancer 2.04 M）。
⇒ 库内"生成式与低延迟几乎不相交"的判断被再次印证。已写入 overview 第 20 条判据。

**（G）"结构化先验优于纯学习"在损失层与架构层同时成立（跨层同构）。**
损失层：TF Weighted Losses 的 $\mathcal{L}_{SIR\cdot SP\cdot SF}$（竞争先验）在 SSN 下稳定，而 $\mathcal{L}_{learn}$（纯学习）全面失败。
架构层：SEMamba++ 的 FAN（周期先验）优于 Transformer（无偏置）与 Mamba（顺序敏感）。⇒ 已写入 overview 第 21 条判据。

**（H）新增一条消融验收纪律：「范式 × 骨干」交叉消融。**
SBM 用 3 骨干 × 2 范式解耦两个变量（SB 在三种骨干上一致 +0.246/+0.206/+0.175；但 LSTM(SB) 17.42 M 的 OVRL/NISQA 高于 Mamba(M) 3.61 M ⇒ **相乘而非替代**）。
⇒ 凡"新范式 + 新骨干"的论文，未做交叉的标"贡献未解耦"。已写入 overview 第 22 条判据。

**发现的原文自身不一致（已标 `[!question]` / `[!contradiction]`，未静默修正）**：
1. **LCA**：§3.3 正文写 "a non-causal block with dilation $2^i$ introduces $2^i$ frames"，而 Eq.(5) 为 $\sum b_i 2^{i-1}$ ⇒ **已独立复核判定 Eq.(5) 正确**。
2. **LCA**：摘要"reduces stored parameters by 76%"未说明对应 (C-1) 还是 (C-2) ⇒ 两数并列（76.5% / 84.2%）。
3. **SEMamba++**：Table 7 的 `T×2 F×2`（两轴下采样）在 VCTK UTMOS 与 DNS UTMOS 上与主方法持平甚至略高、RTF 还更低，但**论文未讨论该变体**。
4. **SBM**：`fullband Mamba 层`的作用域/因果性**未交代**（论文说它捕捉"帧间依赖"）⇒ 记为一处未闭合的因果缺口。
5. **SBM**：算法延迟 "under 40 ms" **漏计 $\tau_{enc}$**（见 A）。
6. **SBM**：25% double-talk 训练**未被消融**，论文用它解释 SpeechBERTScore 偏低。

### 因果性判定汇总（本批 5 篇）

| 论文 | 判定 | 依据 |
|---|---|---|
| HALO | **严格因果**（但输出帧含外推） | D 只用 $(2l-1,2l)$、U 不访问未来；**但 $\hat S(:,2l+1)$ 是外推** ⇒ 库内首个"严格因果但输出帧含外推成分"的架构 |
| LCA | **半因果**（7 档中仅 1 档因果） | 仅 $T_{la}=0$ 档因果，但该档延迟 5 ms（超低）/20 ms（标准） |
| SEMamba++ | **非因果**（离线 GSR） | 双向 Mamba；全文无 latency/streaming/causal 讨论 |
| TF Weighted Losses | **非因果**（多通道波束形成） | FaSNet 两阶段自适应波束形成；无延迟/算力报告 |
| SBM | **半因果**（2–4 帧 lookahead） | 论文自称 "balance causality and enhancement quality"；fullband Mamba 层作用域未交代 |

### 未报告的库内必填字段（本批暴露）

| 论文 | 算法延迟 | RTF/硬件 | 参数量 | STFT center |
|---|---|---|---|---|
| HALO | **未报告绝对值**（只说 "unchanged"） | 未报告 | ✅ 46.87 k | **未报告** |
| LCA | ✅ 七档全给 | **未报告** | ✅ 13.3/16.5/24.5 M | 不适用（时域） |
| SEMamba++ | 不适用（非流式） | RTF ✅ / **硬件仅型号** | ✅ 2.7 M | **未报告** |
| TF Weighted Losses | 未报告 | **未报告** | **未报告** | 未报告 |
| SBM | **口径漏计 $\tau_{enc}$** | RTF ✅ / **GPU 型号未指明** | ✅ 3.93 M | **未报告** |

⇒ **STFT center 审计表的需求再次被确认**：本轮 4 篇涉 STFT 的论文（HALO / SEMamba++ / TF Weighted / SBM）**全部未报告 center**，加上此前的 LiSenNet、FastEnhancer、GTCRN、PrimeK-Net，**待审计清单已增至 8 篇**。

### 中心页更新

- `index.md`：实体区 +5 行、概念区 +6 行、资料区 +5 行；篇数 `32 篇` → **`37 篇`**；`updated:` → 2026-10-07；新增第 11 批表格（5 行）+ 6 个 callout（八篇对应关系 / 延迟口径外部背书 / GTCRN 三记录 / 结构性平均-峰值分离 / 保人声加权反例 / 生成式双轴）。
- `overview.md`：批次表 +1 行（第 11 批 / 5 篇）；`已分十批完成 32 篇` → **`已分十一批完成 37 篇`**；`updated:` → 2026-10-07；**新增 6 条判定口径（第 17–22 条）**。
- `log.md`：本段；`updated:` 从 **2026-09-26 修正为 2026-10-07**（该字段此前已落后多批）。
- 回填引用方：本轮 5 篇均为**首次进库**（无既有引用方页面需要回填）；但**新建页面之间以及与既有页面的交叉链接已在各页 `related` 与 §6 关联矩阵中建立**（含指向 `RT-SEMamba`、`LaCo-SENet`、`RT-Tango`、`GTCRN`、`LiSenNet`、`PrimeK-Net`、`FastEnhancer`、`DPCRN`、`PSMSE`、`STFT-Very-Low-Latency-SE` 等既有页面的 wikilink，已逐个验证目标存在）。

### 库内缺口（更新）

1. **FSPEN 仍无页面** —— IEEE 付费墙 + 无 arXiv（ICASSP 2024, pp. 10671–10675, DOI `10.1109/ICASSP48485.2024.10446016`）。**需用户提供 PDF 方可补摄。**
2. **UL-UNAS 仍无页面** —— 本轮 HALO 与 SEMamba++ 都引用了它（HALO 报其 168.98 k / 33.61 M MAC/s / PESQ 2.245；是 HALO 收益最小的骨干 +0.016）。**它是"超轻量三角"之外的第四个锚点，建议优先补摄。**
3. **本轮新识别的库外重要文献（无页面）**：
   - **oSpatialNet / SpatialNet**（Quan & Li）—— SBM 的骨干基础，且被 SEMamba++ 引用
   - **ZipEnhancer**（ICASSP 2025）—— 在 PESQ/ESTOI 上胜过 SBM 的判别式强基线
   - **SB-NCSN++ / SBCTM / SB-UFOGen** —— SB-SE 的三条基线
   - **[44] "Rethinking Flow and Diffusion Bridge Models for Speech Enhancement"（arXiv:2602.18355, 2026）** —— 作者含 **Jing Lu**，即库内 GTCRN / UL-UNAS 的南京大学课题组
4. **"锚点清单"页仍未建** —— 本轮使需求升级：GTCRN 已是**三方记录**（23.7K/39.6、48K/33、23.67k/33.83），且出现了**第二类锚点风险**（引用方"沿用"而原文无该数）之外的新变体"**混合口径**"。
5. **"STFT center 审计表"仍未建** —— 待审计清单 **8 篇**（LiSenNet、FastEnhancer、GTCRN、PrimeK-Net、HALO、SEMamba++、TF Weighted Losses、SBM）。
6. **"延迟口径审计表"建议新建** —— 本轮出现两处口径问题（SBM 漏计 $\tau_{enc}$；LCA 的 76% 未声明变体），且 LCA §3.2 提供了权威判据，值得把库内所有论文的延迟口径统一列一张表。
