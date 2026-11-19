# ProbSpan Phase C 架构评审

本阶段审查哪些数学、证据和工程边界可以共享，哪些必须独立表达。基线较有价值：保持既有窄 C 核心。如果有获授权、可复核的真实固定期任务，比较一条受限外部适配与调用者直接方案，优先复用已经存在的设备参考与安装入口。没有证据表明外部方案必然有收益，或现行 ABI 需要扩展。本研究是评审提案。

| 文档 | 内容 |
|---|---|
| [现行事实与证据地图](current-state-and-evidence-map.zh-CN.md) | 真实调用、类型与责任，48 + 7 + 1 个问题及 4 项修复 |
| [重叠与分离](overlap-and-separation.zh-CN.md) | 区分共用数学、基础设施、概念和不当合并 |
| [整体备选方案](architecture-alternatives.zh-CN.md) | 现状、保守、外部纵向、广集成 |
| [边界及合同](proposed-boundaries-and-contracts.zh-CN.md) | 单向依赖图与对抗性走查 |
| [集成风险与验证](integration-risks-and-validation.zh-CN.md) | 错误传播、迁移、依赖、平台与假设 |
| [条件实施计划](conditional-phase-d-plan.zh-CN.md) | 有限候选与独立进入/退出门槛 |
| [决策与移交](decision-register-and-handoff.zh-CN.md) | 所有者选择及自审证据 |
| [重叠登记](overlap-register.tsv) · [决策登记](decision-register.tsv) | 稳定复用/决策 ID，供追查 |

实际 main 为 `45075a1da4adedf871299d148ef7dfa502335d72`，与接受的 Phase B HEAD `b6cff295748b53e565ff5e661ddde7beba5b9a95` 同树 `8e357032779dae168c3fb43aaf2938d6996a1bc7`。Phase A 合并 `e47c038cd2b1997d87b7fe303f9037c80e6eb955`；Phase C 任务起点 `5406d38a62b831c2e4560b0242dd89ec1a6754a1`。Stable v1.1.0 `46ff21847c5522eb983d3f58e396354461a64f34` 保持源码和发布合同。 [Phase A](../phase-a/README.zh-CN.md) · [Phase B](../phase-b/README.zh-CN.md) · [任务简报](../../PHASE_C_INTEGRATION_ARCHITECTURE_BRIEF.md)

当前几何共享是正例；Beta 私有核的同域复用值得保留为有条件的选项。后验、风险集、预测评价、资格与生命周期各有自己的输入和校验条件。B-E002 的冲突、B-E003 的权和依赖、B-E005 的真值和时间、B-E007 的权重与 B-E006 的表示边界决定了这些分离。使用旧入口时来源资格仍在外层，不可替换 readiness。 [证据地图](current-state-and-evidence-map.zh-CN.md)
