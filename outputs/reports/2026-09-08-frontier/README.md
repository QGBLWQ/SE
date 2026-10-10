# 2026-09-08 前沿论文收录

检索截止：2026-09-08。范围为麦克风声源定位 / DOA 与语音增强，各五篇。项目根目录没有 README，本次笔记遵循根目录 `CLAUDE.md` 的 Wiki 规范。

## 阅读入口

- 定位笔记与相关概念：[[wiki_array/index]]
- 增强笔记与相关概念：[[wiki/index]]
- 定位论文原件与检索证据：`localization/`
- 增强论文原件与检索证据：`enhancement/`

PDF、官方页面和全文提取件保存在本目录的两个子文件夹，原有 `raw/` 资料保持原样。各子文件夹的 `manifest.md` 记录论文元数据、官方链接及选题依据。Wiki source 页是中文技术笔记，提取的英文全文仅用于核验。

## 筛选与阅读边界

### 定位五篇

| 论文 | 首发 / 所收版本 | 收录重点 | 官方来源 |
|---|---|---|---|
| NeuralMUSIC | 2026-06-17 / v3，07-08 | 神经协方差、MUSIC、自监督与域迁移 | [arXiv](https://arxiv.org/abs/2606.18664v3) |
| Single frequency filtering based multi-speaker direction of arrival estimation from stereo recordings | 2026-06-15 / v1 | 双麦多说话人、激励包络与 PHAT | [arXiv](https://arxiv.org/abs/2606.17258v1) |
| Probing Spatial Structure in Pretrained Audio Representations（SARL） | 2026-06-04 / v2，07-16 | 空间表征基准；为定位模型选型提供诊断 | [arXiv](https://arxiv.org/abs/2606.05544v2) |
| Distributed Acoustic Localization Array Deployed Using a Soft Everting Vine Robot | 2026-07-22 / v1 | 可变形阵列与近远场 SRP-PHAT | [arXiv](https://arxiv.org/abs/2607.20392v1) |
| Confidence-Aware Test-Time Adaptation for Fault-Resilient Sound Source Localization Guided by Lightweight Diagnosis | 2026-04-16 / 04-22 期刊版本 | 麦克风故障诊断与测试时自适应 | [IEEE Access](https://doi.org/10.1109/ACCESS.2026.3684240) |

定位选题包括直接 DOA 算法、表征评估及实物阵列系统。SARL 是基准论文；藤蔓机器人实验使用白噪声源，不能当作已完成真实语音搜救验证。它们与直接语音 DOA 的区别已在笔记中说明。

### 增强五篇

| 论文 | arXiv 首次提交（UTC） | 收录重点 | 官方来源 |
|---|---|---|---|
| U-PAST | 2026-08-31，编号 2609.00431 | 复数谱 Transformer 与跨域增强 | [arXiv](https://arxiv.org/abs/2609.00431v1) |
| Towards Balanced Spectral Reconstruction | 2026-08-31 | 流式增强的频谱自适应损失 | [arXiv](https://arxiv.org/abs/2608.30739v1) |
| μNet | 2026-08-21 | 低内存、低延迟、整数 DSP 推理 | [arXiv](https://arxiv.org/abs/2608.21155v1) |
| Cloud-Boosted Low-Compute Multi-Channel Speech Enhancement | 2026-08-07 | 延迟云端信息与边端多通道 Wiener 滤波 | [arXiv](https://arxiv.org/abs/2608.07423v1) |
| FlowSE-GRPO | 2026-01-23 | 流匹配的在线强化学习后训练与奖励偏差 | [arXiv](https://arxiv.org/abs/2601.16483v1) |

FlowSE-GRPO 虽然较早，仍保留为在线强化学习这一独立路线；其余四篇覆盖 8 月的新工作。U-PAST 的 arXiv 编号进入 9 月，但首提交通用时间为 8 月 31 日，PDF 封面日期为 9 月 2 日，三者不混写为同一个日期。

“前沿五篇”是截至检索日、结合新近程度、方法创新、项目相关性与全文可核验性的精选，不代表整个领域公认排名，也不等于引用量最高的五篇。优先 2026 年工作；较早但代表独立新路线的工作可保留，并明确首发时间。

仅以官方论文、出版方页面、作者代码仓库核验主要事实。区分预印本与已确认的会议 / 期刊发表状态；搜索结果的抓取日期不作为发表日期。未检索到更新且适合的论文，不等于此后没有新论文。

比较不同论文时需核对数据集、噪声与混响、阵列、采样率、因果性、延迟和运行硬件，不能跨测试集直接按数值排榜。论文报告的结果与本次独立复现严格区分：本次完成文献收录与笔记，不训练或运行论文模型。

## 协作方式

按用户要求并行分工：两个检索 agent 分别负责定位与增强，笔记任务交给较低成本的 Terra 模型；主 agent 负责选题取舍、跨文件整合和最终检查。全文在共享文件夹中交接，避免重新检索同一篇。未获得各模型实际账单与耗电测量，因此不声称量化成本或能源节约。

## 文件检查

`validate_collection.py` 是只读检查脚本，用于核对 PDF 文件头、计算 SHA-256，以及检查本次新增 Wiki 页的元数据和链接。检查结果见最终生成的 `validation.json`。

<!-- frontier-2026-09-08:start -->
## 中文笔记直达

### 定位

- [[wiki_array/topics/2026 前沿声源定位五篇比较]]
- [[NeuralMUSIC 2026]]
- [[SARL 空间表征探测基准 2026]]
- [[SFF 多说话人 DOA 2026]]
- [[容错 SSL 诊断引导测试时自适应 2026]]
- [[软体藤蔓机器人分布式声定位 2026]]

### 增强

- [[wiki/topics/2026 语音增强前沿五篇比较]]
- [[Balanced Spectral Reconstruction 2026]]
- [[Cloud-Boosted MCSE 2026]]
- [[FlowSE-GRPO 2026]]
- [[muNet 2026]]
- [[U-PAST 2026]]
<!-- frontier-2026-09-08:end -->
