# ProbSpan 2.0.0 工程计划

D1 评审入口。产品方向已明确要求新增统计能力。本文推荐在同一源码树提供同质二项推断、显式 Beta 先验与批次预测、目标标准化、竞争风险及离线预测评价。具体合同、排期和分发方式均待独立评审与所有者授权。

| 基线 | 精确对象 |
|---|---|
| Stable v1.1.0 | 46ff21847c5522eb983d3f58e396354461a64f34 |
| Phase A / #17 | e47c038cd2b1997d87b7fe303f9037c80e6eb955 |
| Phase B / #18 | 45075a1da4adedf871299d148ef7dfa502335d72 |
| Phase C / #19 | 7c25a4dee76d6203eeaddeb9cac6c012d6c3ee94 |
| Phase D 交接 / #20 | a838344bd93b81ca26713d48ae8b6b1bf6969a62 |
| D1 指令提交 | 9d70d6cf699e2a6be06dac3600f37cd771be3bf0 |

- D1.1–2 [范围与证据](feature-scope-and-evidence.zh-CN.md) · [特性登记表](feature-register.tsv)
- D1.3 [估计对象与合同](estimands-models-and-contracts.zh-CN.md) · [架构与兼容](architecture-and-compatibility.zh-CN.md)
- D1.4 [固定工作单元](stages-and-fixed-work-units.zh-CN.md) · [单元登记表](work-unit-register.tsv)
- D1.5 [验证矩阵](verification-and-test-matrix.zh-CN.md) · [发布门槛](preview-rc-stable-strategy.zh-CN.md)
- D1.6 [决策与交接](owner-decisions-risks-and-handoff.zh-CN.md)

恢复工作先核对上述 Git 对象与当前独立评审，再由获准单元入口定位合同和测试。数学推导、合成试验和历史留出具有不同证据范围。[Phase A](../../research/phase-a/README.zh-CN.md) · [Phase B](../../research/phase-b/README.zh-CN.md) · [Phase C](../../research/phase-c/README.zh-CN.md) · [原任务](../../PHASE_D1_V2_ENGINEERING_PLAN_BRIEF.md)

基线核对通过 Git first-parent 追踪 #17–20，v1.1.0 tag peeled 到上述发行源。Stable 与 D1 主线的变更清单限于研究与交接文档。比对入口使用 local Windows 工作树。现有合同查看公共头、冻结策略、私有 Beta 和 legacy 消费者。Issue #1、#5、#6、#8、#9、#10 提供边界或研究问题，均不构成实施权限。Phase B 的 comparisons.py 承载 E001–005，numerical.py 和 beta_probe.c 承载 E006，batting.py 承载 E007。本轮引用已记录实验结果；未重跑研究或构建生产库。
