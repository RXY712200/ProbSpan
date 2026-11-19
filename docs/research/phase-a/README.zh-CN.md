# ProbSpan Phase A 研究证据

本调查在 2026-11-18 UTC 进行。范围为已发布 C11 核心、独立的调用方设备 Preview、48 个固定候选及 4 个已完成修复。研究比较条件、目标、验证与失败方式，供独立审查与后续研究使用。

## 导航

| 内容 | 文件 |
|---|---|
| 外部来源的唯一 ID、作者、日期、访问、适用和反证 | [source-register.tsv](source-register.tsv) |
| 双语发现、引文链、针对性补查和反例核对 | [search-log.md](search-log.md) |
| 概率、估计量、借用、依赖、评分与计算 | [methods-and-assumptions.zh-CN.md](methods-and-assumptions.zh-CN.md) |
| 实际行业证据、源码、回归和社区讨论 | [real-world-and-software.zh-CN.md](real-world-and-software.zh-CN.md) |
| 52 项状态与当前证据边界 | [ledger-crosswalk.zh-CN.md](ledger-crosswalk.zh-CN.md) |
| 7 个临时问题与证据缺口 | [new-questions-and-gaps.zh-CN.md](new-questions-and-gaps.zh-CN.md) |
| 基线、源质量、完整性和移交 | [verification-and-handoff.zh-CN.md](verification-and-handoff.zh-CN.md) |

## 实际基线

| 对象 | 已核对 |
|---|---|
| 仓库、默认分支 | 公开 `RXY712200/ProbSpan`，`main` |
| main / 任务起点 | `2cf68294a6a420d77c7fd1016157fdeb9a65d8a5` / `f626c9d374c41e7e551fc6bc3d215aa7048604ae`；任务分支原先仅增加[任务简报](../../PHASE_A_RESEARCH_BRIEF.md) |
| v1.1.0 Stable | 已发布非 draft、非 prerelease；annotated tag `ca4e3a413d0e4dc0c21b4891a84a61b0f67a6bc3` 指向 `46ff21847c5522eb983d3f58e396354461a64f34`；树 `0cf4a495a547e4c6f4a434e334a9a3809027e386`，与 origin/main 树相同。 [Release](https://github.com/RXY712200/ProbSpan/releases/tag/v1.1.0) |
| 协作治理 | 经认证读取现行完整正文及 Git 基线；公开提交仅记录访问事实和本任务适用的证据。 |
| 既有研究 | 读[证据基础](../../HISTORICAL_EVIDENCE_RESEARCH.zh-CN.md)、[模型 Preview](../../PREVIEW_PROBABILITY_MODELS.zh-CN.md)、[设备 Preview](../../PREVIEW_DEVICE_HISTORY.zh-CN.md)与[研究脚本](../../../research/preview_history.py)。这些文档的合成压力测试、数值结果与真实设备场景要分别判断。 |

## 现行行为与研究边界

| 现行计算 | 源码和断言 | 保证、调用方前提及未解决问题 |
|---|---|---|
| 主观 raw 0–100 保留，数学输入 1–99%，分段 logit 宽度 | [subjective.c](../../../src/subjective.c) · [oracle_parity.c](../../../tests/oracle_parity.c) | 确定性规则区间；信念形成、专家校准及经验覆盖留在外部。 |
| 独立历史入口；非空 Jeffreys 后验均值和中心 95% 区间；冻结 gate 同时检查 n 和宽度 | [historical.c](../../../src/historical.c) · [model_v1.h](../../../src/model_v1.h) · [large_numerics.c](../../../tests/large_numerics.c) | `has_estimate` 与 `VALID` 分开；比较对象、观测独立、完整随访及适用性靠调用者，缺支持时可能不可识别。 |
| 各侧 EV、稳健裕度 S、赔率组合与独立模型关系；历史正 EV 质量在 gate 后可用 | [historical_analysis.c](../../../src/historical_analysis.c) · [decision_policy.c](../../../src/decision_policy.c) · [analysis_parity.c](../../../tests/analysis_parity.c) | 期望回报依赖给定赔率；参数后验质量与下一结果概率是两个量。联合效用、融合和策略成效都要外部证据。 |
| 粘滞的实际曝光/独立性损害、组合器版本及出错输出保持 | [provenance.c](../../../src/provenance.c) · [state_parity.c](../../../tests/state_parity.c) · [api_contract.c](../../../tests/api_contract.c) | 核心根据调用方报告编码顺序；数据血缘、真实注意、证据去重、工作流和持久性由外部负责。 |
| 精确 ASCII 十进制 parser；普通 Beta、极端参数 logit 积分 | [decimal.c](../../../src/decimal.c) · [beta_logit.c](../../../src/beta_logit.c) · [数值契约](../../NUMERICAL_CONTRACT.md) | 精确位型和 libm 容差合同分开。有限输出网格允许相邻点跨较大概率质量；未验证环境保留开放。 |
| 可选设备 Preview 对固定 100 小时证据审查，严格/声明可比可调用安装库；两层固定权参数后验 | [evidence.py](../../../integrations/device_history/evidence.py) · [standardization.py](../../../integrations/device_history/standardization.py) · [test_device_history.py](../../../integrations/device_history/test_device_history.py) | C 安装独立，调用方声明未获现场认证，数值预算失败保留收据；无通用标准化、持久格式或 EV 输出。 |

历史可分为兑现的同义事件计数、带特征和标签的训练资料，以及预测—兑现表现记录。它们对应不同 estimand。已证明可汇总的少量数据的统计强度是 Issue [#9](https://github.com/RXY712200/ProbSpan/issues/9) 的问题；来源是否可比是 Issue [#10](https://github.com/RXY712200/ProbSpan/issues/10) 的问题；外部数据库提取的延期案见 [#8](https://github.com/RXY712200/ProbSpan/issues/8)。核心范围见 [#1](https://github.com/RXY712200/ProbSpan/issues/1)。

## 跨来源观察

- 门槛和窄区间不能验证输入合法性。故障暴露量、固定时距风险、选择性可见标签及被修订真值需要不同证据。 [S0029](https://www.kdd.org/kdd2017/papers/view/the-selective-labels-problem-evaluating-algorithmic-predictions-in-the-pres) · [S0038](https://www.backblaze.com/blog/backblaze-drive-stats-for-2025/)
- 目标支持缺口可在明确条件下给识别界；强制点估计需要额外模型或数据。稳健历史先验有贡献，目标没有观察时不能从结果检测机制冲突。 [S0028](https://ageconsearch.umn.edu/record/292716) · [S0006](https://doi.org/10.1111/biom.12242)
- 边际覆盖、目标内校准、按时距的 relative skill 与行动损失可呈现不同排序。验证的真值、组依赖和时序信息集属于证据。 [S0010](https://www.stat.berkeley.edu/~ryantibs/papers/limits.pdf) · [S0034](https://www.nature.com/articles/s41467-024-50601-9) · [S0091](https://arxiv.org/abs/2110.00115)
- 源登记中 theorem/derivation、回顾性实测、官方指导、源码与讨论提供不同证据强度。真实部署、运行时复现与结论的独立接受各需自身证据。
