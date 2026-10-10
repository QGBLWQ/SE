# 语音增强与声源定位学习资料

这里整理了语音增强、音源分离、低时延增强和麦克风阵列声源定位的学习笔记、论文摘要与实验记录。建议先按下面顺序入门，再进入专题。

## 给新同学：先读基础

第一次接触这个方向，请先读这两篇：

1. [语音增强评价指标：PESQ、STOI、MOS、SI-SNR 等](wiki/concepts/语音增强评价指标.md)
2. [声学物理直觉学习路径](outputs/learning/00-声学物理直觉-学习路径.md)

读完后，试着用自己的话回答：

- PESQ、STOI 和 SI-SNR 分别主要衡量什么？为什么一个分数不能代表全部效果？
- 有干净参考和没有干净参考时，分别能用哪些评价方法？
- 为什么论文还需要听音、分场景统计，并报告测试条件？
- 麦克风间距、波长和到达时间差如何影响声源方向估计？

## 推荐阅读顺序

1. **基础概念**：先读上面的评价指标和声学物理直觉。
2. **语音增强概览**：[语音增强 Wiki](wiki/index.md) 与[深度学习语音增强综述](wiki/surveys/deep-learning-speech-enhancement-survey.md)。
3. **声源定位概览**：[阵列处理 Wiki](wiki_array/index.md)，再看 [TDOA](wiki_array/concepts/TDOA%20到达时延差.md)、[GCC-PHAT](wiki_array/concepts/GCC-PHAT%20广义互相关.md) 和 [DOA](wiki_array/concepts/DOA%20波达方向估计.md)。
4. **低时延增强**：[低时延 Wiki](wiki_low_latency/index.md)，关注模型、因果性、算法延迟和实验记录。
5. **专题与实验**：从[实验目录](outputs/experiments/index.md)和 `wiki*/sources/` 中选主题；阅读结论时核对对应记录里的数据、设置和适用范围。

## 目录

| 路径 | 内容 |
|---|---|
| `wiki/` | 语音增强与音源分离基础概念、模型和论文笔记 |
| `wiki_array/` | 麦克风阵列、声源定位与空间音频笔记 |
| `wiki_low_latency/` | 严格因果、超低时延语音增强与相关论文 |
| `outputs/learning/` | 面向入门的学习路径 |
| `outputs/experiments/` | 研究问题、实验设计和实验记录 |
| `outputs/reports/` | 文献调研与专题报告 |
| `raw/papers/` | 论文 PDF；请遵守各资料的版权和许可要求 |
| `raw/books/` | 书籍与教材资料 |
| `raw/notes/` | 原始阅读笔记 |
| `flashcards/` | 简短概念卡片 |

## 阅读说明

- 论文摘要是阅读笔记，不替代原论文；重要结论请回到原文核对。
- 指标比较只有在采样率、裁剪、对齐、数据划分和计算实现一致时才有意义。
- 区分实验观察、假设和已验证结论；不要把探索性结果当作普遍结论。
- GitHub 可以直接阅读 Markdown；本地使用 Obsidian 时，双链体验更完整。
