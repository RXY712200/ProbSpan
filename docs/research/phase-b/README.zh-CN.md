# ProbSpan Phase B 数学比较

问题是同一可观测信息和估计目标下，模型或验证方法的收益、失败和可识别边界。保持既有推断合同和 Phase A 历史，所有实验与解释限定在给定条件。

| 入口 | 内容 |
|---|---|
| [问题与估计量](problem-estimand-map.zh-CN.md) | 48 个永久候选、7 个 Phase A 临时问项、4 个历史修复 |
| [模型及前提](candidate-models-and-assumptions.zh-CN.md) | 目标、假设、基线及失败方式 |
| [推导与反例](derivations-and-counterexamples.zh-CN.md) | 识别、覆盖、风险集、持续监测及数值分辨率 |
| [实验与结果](experiments-and-results.zh-CN.md) | 7 个已执行比较、命令、精度/Monte Carlo SE、输出 |
| [外部证据](external-evidence-and-limitations.zh-CN.md) | 实地与文献证据、访问层级和迁移限制 |
| [条件判定](conditional-findings.zh-CN.md) | 结论矩阵及临时新问题 |
| [完整性及移交](verification-and-phase-c-handoff.zh-CN.md) | 检查证据及后续问题 |
| [来源增补](source-addendum.tsv) · [实验目录](../../../research/phase-b/README.md) | 新来源、S0029 DOI 补注、可重跑命令及先验协议 |

## 基线与主要发现

- 公开 main 起点 `e47c038cd2b1997d87b7fe303f9037c80e6eb955` 是 [Phase A PR #17](https://github.com/RXY712200/ProbSpan/pull/17) 的合并点，接受的研究提交为 `4bc0e28d60bf7c618543aa0d789f34a29d0f4ec6`。本任务起点 `dad36d284e9a06f12cabba4316fcbdd569dceb04` 的相对 main 差异只有[任务简报](../../PHASE_B_MODEL_COMPARISON_BRIEF.md)。产品 Stable v1.1.0 是 `46ff21847c5522eb983d3f58e396354461a64f34`，树 `0cf4a495a547e4c6f4a434e334a9a3809027e386`。 [Stable Release](https://github.com/RXY712200/ProbSpan/releases/tag/v1.1.0)
- 同一历史在目标相同与目标漂移时，汇聚影响相反；零目标时稳健混合的弱成分权不会变化。符合 gate 的历史仍可在科学上不适用。 [B-E001/B-E002](experiments-and-results.zh-CN.md#b-e002)
- 在共享样本的构造中，忽略权与风险的协方差令覆盖从 .9373 降为 .8707；净风险与实际竞争原因 CIF 在同一人群内也不同。 [B-E003](experiments-and-results.zh-CN.md#b-e003) · [B-E004](experiments-and-results.zh-CN.md#b-e004)
- 对公平符号序列，每次使用固定时点阈值的首次跨界率约 .30435。真实棒球留出上，完整汇聚和层级的相对名次随测试权改变。 [B-E005](experiments-and-results.zh-CN.md#b-e005) · [B-E007](experiments-and-results.zh-CN.md#b-e007)
- 极偏后验的分位可因相邻 binary64 网格返回 1，邻接夹逼仍成立。同一赔率编码对精确文字的不同单边差异无法保真。 [B-E006](experiments-and-results.zh-CN.md#b-e006)

首先根据公共合同和对应源码确认现行行为，再用执行测试与独立数值证据检查。统计结论按解析、指定生成机制、真实留出或外部场地观察分别解释。没有目标真实设备样本、多平台复验或采购/临床等领域效用数据。 [接受的 Phase A 全套导航](../phase-a/README.zh-CN.md)
