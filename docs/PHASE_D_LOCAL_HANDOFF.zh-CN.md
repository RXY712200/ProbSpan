# ProbSpan 本地开发交接

本交接记录已验收的 Phase A–C 研究、现行产品合同和后续工程的进入条件。Phase C 已独立接受并合并。默认保留小型确定性 C 内核；具体 Phase D 实施范围由所有者另选。本文可从零对话历史开始使用。

- [可信基线和阅读顺序](#baseline)
- [A、B、C 证据及其边界](#research)
- [实际源码与公开合同](#contracts)
- [九项待决事项](#decisions)
- [条件工程路线](#engineering)
- [Windows 恢复、构建和验证](#windows)
- [长期维护、复核与授权停点](#continuity)

<a id="baseline"></a>

## 1. 可信基线和阅读顺序

| 对象 | 2026-11-19 核对的身份与用途 |
|---|---|
| 仓库 | 公开 `RXY712200/ProbSpan`，默认分支 `main`，远端 `https://github.com/RXY712200/ProbSpan.git`。 |
| 本交接所依据的 main | `7c25a4dee76d6203eeaddeb9cac6c012d6c3ee94`，树 `a74f6af7c8b2e7f80a3a32736633fdfbd2557c46`，等于已接受的 Phase C HEAD 树。 |
| Phase A | [PR #17](https://github.com/RXY712200/ProbSpan/pull/17) 已合并，merge `e47c038cd2b1997d87b7fe303f9037c80e6eb955`，研究 HEAD `4bc0e28d60bf7c618543aa0d789f34a29d0f4ec6`。八件研究资料含来源登记与逐 ID 交叉表。[入口](research/phase-a/README.zh-CN.md) |
| Phase B | [PR #18](https://github.com/RXY712200/ProbSpan/pull/18) 已合并，merge `45075a1da4adedf871299d148ef7dfa502335d72`，研究 HEAD `b6cff295748b53e565ff5e661ddde7beba5b9a95`。八份研究文档、来源增补、协议、可执行实验与三份结果。[入口](research/phase-b/README.zh-CN.md) · [复现](../research/phase-b/README.md) |
| Phase C | [PR #19](https://github.com/RXY712200/ProbSpan/pull/19) 已合并；HEAD `70ab0b8c5b050ee304ae4d06563920dc8993a3bf`。八份设计文档与两份登记，设计选项未获实施批准。[入口](research/phase-c/README.zh-CN.md) |
| Stable | v1.1.0 annotated tag `ca4e3a413d0e4dc0c21b4891a84a61b0f67a6bc3` 指向 `46ff21847c5522eb983d3f58e396354461a64f34`，树 `0cf4a495a547e4c6f4a434e334a9a3809027e386`。正式非 draft、非 prerelease，无上传的自制 assets。v1.0.0 建立的兼容合同仍适用，v1.1.0 产品版本与 ABI、模型及策略版本各自独立。此 main 相对 Stable 添加研究及任务简报；源码和安装合同未变。[Release](https://github.com/RXY712200/ProbSpan/releases/tag/v1.1.0) · [兼容性](COMPATIBILITY.md) |

新会话先读当次授权和经认证的当前两份私有政策。项目入口为 [AGENTS](../AGENTS.md)、[CONTRIBUTING](../CONTRIBUTING.md)、[README](../README.md)、[起源与范围](ORIGIN_AND_SCOPE.md) 和 [Issue #1](https://github.com/RXY712200/ProbSpan/issues/1)。实际签名、类型与代码以[安装头](../include/probspan/probspan.h)及关联源为证；公开承诺见 [API](API.md)、[行为](BEHAVIOR_SPEC.md)、[数值](NUMERICAL_CONTRACT.md)、[兼容性](COMPATIBILITY.md)、[provenance](PROVENANCE.md)。[架构](ARCHITECTURE.md)和四份指南提供逐层定位：[导读](IMPLEMENTATION_WALKTHROUGH.zh-CN.md)、[公开用法](IMPLEMENTATION_API_REFERENCE.zh-CN.md)、[内部实现](IMPLEMENTATION_INTERNALS.zh-CN.md)、[验证](IMPLEMENTATION_VALIDATION.zh-CN.md)。发现合同与源码差异时记录具体路径、输入、行为和版本，提交独立评审，不从实现细节擅自重定义合同。

正交证据依次查 [测试](TESTING.md)、[oracle](../oracle/README.md)、[历史证据研究](HISTORICAL_EVIDENCE_RESEARCH.zh-CN.md)、[旧模型 Preview](PREVIEW_PROBABILITY_MODELS.zh-CN.md)、[设备 Preview](PREVIEW_DEVICE_HISTORY.zh-CN.md)和 A/B/C。运行日志只证明相应提交和环境。研究册解释假设和结果，提案无执行权限。[永久账本](TECHNICAL_DEBT.zh-CN.md)保存固定问题和修复史，Issue 开放状态与账本批准范围不同。[#5](https://github.com/RXY712200/ProbSpan/issues/5) 是分位可表示性，[#6](https://github.com/RXY712200/ProbSpan/issues/6) 是工具链和浮点环境，[#8](https://github.com/RXY712200/ProbSpan/issues/8) 是未授权 DB 方向，[#9](https://github.com/RXY712200/ProbSpan/issues/9) 是合法关系后的借用，[#10](https://github.com/RXY712200/ProbSpan/issues/10) 是先建立可比关系。

这些 SHA 是历史锚点。以后先 fetch，再比较实际远端，按文件和祖先关系检查增量、标签目标及工作区；若 main 前进，说明新差异与当次授权的影响。不要把历史 SHA 当最新，也不要为回到历史而重置已有工作。命令见 [Windows 恢复](#windows)。

<a id="research"></a>

## 2. A、B、C 的证据和可用边界

### Phase A：问题、资料与可观察性

[Phase A 来源登记](research/phase-a/source-register.tsv)记录 96 个唯一项，按主要用途分为 45 学术、15 官方/指南、12 软件、14 实地、10 社区。访问层级对证据强弱有实质影响，摘要或书目信息不能替代论文结果。其[交叉表](research/phase-a/ledger-crosswalk.zh-CN.md)和[搜索记录](research/phase-a/search-log.md)覆盖 48 个永久候选 A01–E48 和历史已解决的 R01–R04；后四项分别涉及大形状 Beta、准确十进制和正零、provenance/Gamma、历史发行。不能把 52 项计为待修缺陷。

三种资料要按各自观测单位与时钟处理。**兑现的二元历史**要求端点、目标人群、时距、完整观测和依赖明确；**特征–结局资料**要求特征在预测时可见、训练及留出按实体/时间正确划分；**发出的预报–兑现配对**用于评价，须保留预测原值、时点、真值版本和评价分母。目标没有支持时，可存在相同源数据而目标 p 不同的两个世界；增加同源 n 无法解决识别。场地来源显示存在删失、代理标签、暴露率、依赖和修订等实际问题，但未证实本项目的特定真实设备工作流。 [方法](research/phase-a/methods-and-assumptions.zh-CN.md) · [实地及软件](research/phase-a/real-world-and-software.zh-CN.md)

[NEW-A-001–007](research/phase-a/new-questions-and-gaps.zh-CN.md)分别记录真值版本、选择性标签、可选停止、误标、权与风险联合不确定性、数值表示、弃权分母/成本。NEW-B-001 单独问同答复集合按实体或机会加权是否反转排名。它们是临时研究问题。 [Phase B 条件发现](research/phase-b/conditional-findings.zh-CN.md)

### Phase B：同估计量的比较

| 实验 | 实际结果与后续约束 |
|---|---|
| [B-E001](research/phase-b/experiments-and-results.zh-CN.md#b-e001) | 固定 iid 二项 p 的精确覆盖枚举比较未修饰 Jeffreys、均匀先验、Wilson、精确反演和 Wald。n=20、p=.001 时 gate 通过率约 .9998，但均匀先验在该点覆盖 0。参数覆盖、下一次 Bernoulli 风险和未来批次预测分布各自有含义。 |
| [B-E002](research/phase-b/experiments-and-results.zh-CN.md#b-e002) | 固定来源 18/180、目标 n=20，p=.1 时完整汇聚 RMSE .0070 对目标独立 .0667；p=.5 时 .3584 对 .1065。幂权与弱混合的收益随冲突和代价变化；零目标时混合似然因子全为 1，无法从无观察识别冲突。 |
| [B-E003](research/phase-b/experiments-and-results.zh-CN.md#b-e003) | 20,000 次合成重复中，共享权/风险协方差纳入与忽略时覆盖 .9373/.8707；配对差 .0666±.00176 MC SE。按行误当独立时覆盖下降。无正支持的目标层保留界，例如 [.04,.24]，不能重分配其权。 |
| [B-E004](research/phase-b/experiments-and-results.zh-CN.md#b-e004) | 离散竞争风险真 CIF=.24，竞争作删失的 1−KM 目标=.28。独立失访下 AJ 均值约 .24005；信息性失访下 .17828。缺风险集、时点/原因或可辩护失访机制时，e/c 无法重建它们。 |
| [B-E005](research/phase-b/experiments-and-results.zh-CN.md#b-e005) | 公平符号例固定临界值只看终点的跨越 .05597，重复窥视 .30435，有限并集界 .000307。真值版本可翻转同批预测排名，边际校准可掩盖子群失败。相同可见标签率 .5 与总体 .25/.75 相容；计入弃权成本可翻转成绩。 |
| [B-E006](research/phase-b/experiments-and-results.zh-CN.md#b-e006) | C 私有 Beta 探针与高精度独立求积的存档比较。Phase C 对存档端点重新计数：**严格 10/15，概率容差 1e−10 下 15/15**。极偏后验多个分位取 binary64 的 1；同码赔率的精确十进制解释仍能不同。观察不能升级为全域严格夹逼，也没有据此确立 v1 数值合同缺陷。 |
| [B-E007](research/phase-b/experiments-and-results.zh-CN.md#b-e007) | 18 名已见球员的季内数据留出，按打数 Brier pool .201831、层级 .201859；按球员 .196769 与 .196660，方向改变。未来新组、赛季和机会分母不可由该观察认证。 |

[B 的推导](research/phase-b/derivations-and-counterexamples.zh-CN.md)和[外证](research/phase-b/external-evidence-and-limitations.zh-CN.md)分别定位证明、合成、观察留出和文献结果。B 的 [addendum](research/phase-b/source-addendum.tsv)为 S0029 补 DOI `10.1145/3097983.3098066`，未更改 A 原登记。复现实验只能验证其估计量和机制下的行为；现场独立性、设备适用性、部分标签和跨平台数值仍需不同证据。

### Phase C：复用层级与反例

[26 项登记](research/phase-c/overlap-register.tsv)按真正数值/数学重叠、工程重叠、概念共用而职责分离、不当合并分类；[事实图](research/phase-c/current-state-and-evidence-map.zh-CN.md)覆盖全部固定和临时问题及历史修复。

| 典型登记 | 可复用边界、失败和停止条件 |
|---|---|
| C-O015、C-O004 | 私有正赔率 EV 线性映射及补事件反序确已共用；主观 S、历史 EV 后验尾、下一次事件概率和模型关系各自计算。 |
| C-O001、C-O014、C-O016、C-O025 | Beta/Gamma 叶节点与精确 parser 是局部数值对象；只有形状域、输入编码、尾定义、预算和失败合同兼容才共享。旧 event 是 1−CDF；直接 survival 数学等值也可改分支结果。验证骨架可共享，参考后端必须独立。 |
| C-O002、C-O003、C-O026 | 二项似然和条件矩可共用；共同参数的合法计数加法不能替代组后验、超先验整合、新组预测、混合逆分位或未来批次变化。 |
| C-O005–010、C-O017、C-O018、C-O020、C-O023、C-O024 | e/c、簇、风险集、率/次数、连续尾、信念与联合事件必须保留不同对象。版本/簇/端点可机械比对；源到目标资格、误标、支持和共同信号不能自动认证。 |
| C-O011–013、C-O019、C-O021、C-O022 | 可共用外部标识、截止和证据收据词汇；公开 v1 readiness、观测真值版本、选择性评分、实际暴露、存储和打包责任分开。Preview 安装消费依赖公开接口且版本检查独立。 |

[四方案](research/phase-c/architecture-alternatives.zh-CN.md)分别为现状不变、保守独立扩展、外部纵向适配、广集成库。现状没有新迁移和维护成本；保守 C 扩展需确切第二用途和数值证据；外部适配可撤回但增加协议、依赖及验证；广集成在多个真实同生命周期需求下才有价值，当前证据不足。[七项走查](research/phase-c/proposed-boundaries-and-contracts.zh-CN.md)覆盖借用与冲突、重复/删失、条件预测对历史率与评分、后验尾对下一次、表示、真值/选择、新方法隔离。结论是保留现状；有资格场景及实测提升才比较外部适配，不把合成设计验证视为部署验证。决策详见第 4 节。

<a id="contracts"></a>

## 3. 实际代码和公开合同

头文件只有以下 13 个函数（表中省略共同前缀 `probspan_`）。通过 `<probspan/probspan.h>` 消费，C++ 有 C linkage。私有符号和测试夹具不随公共头安装。

| 入口 | 调用与关键语义 |
|---|---|
| `abi_version` | 返回 ABI generation 1，无状态。[源码](../src/probspan.c) |
| `subjective_half_width` / `subjective_estimate` | 前者 p∈[.01,.99]；后者收 0–100 整数，保留 raw，0/100 的数学值夹到 1/99，p=used/100。分段 logit 半宽 d 使用 ln(1.5)、ln(2)、ln(1.4)、ln(1.2)，[.55,.85] 为平台；端点为 logistic(logit(p)±d)。这是模型规则区间，不是统计置信区间。[源码](../src/subjective.c) |
| `history_estimate` | 非负 int64 e/c，先转换为 uint64 再求精确和。n=0 返回 OK/NO_HISTORY，`has_estimate=false`；否则固定 Jeffreys Beta(e+.5,c+.5)、均值和中央 95% 区间，用 binary64 `(1-.95)/2` 与补尾。均值源码按 `((double)e+.5)/((double)n+.5+.5)`，不要擅改算术次序。n≥20 且宽≤.25 才 VALID。INSUFFICIENT 有估计，历史 EV 不可用。[估计](../src/historical.c) · [常量](../src/model_v1.h) · [形参](../src/history_model_private.h) |
| `odds_validate` / `odds_parse` | 总回报含本金，有限且 ≥1。完整 ASCII 十进制数字与可选有数字小数，无符号、指数、空格或本地小数符；精确 ties-to-even 之后才验范围。NULL、词法错误、范围错误先后区分。[入口](../src/odds.c) · [转换](../src/decimal.c) |
| `classify_ev` / `classify_odds_combination` / `classify_model_relation` | 裸 EV 分类只检查输出指针，再直接比较端点；赔率组合按事件赔率先验再补侧；关系先查适用枚举，历史不可用优先于 crossing，不读不可用历史状态。[策略](../src/decision_policy.c) · [几何](../src/decision_geometry.c) |
| `analyze_subjective` | 检查输出/输入、有限有序概率、内部中心和正有限 d，再检查赔率；两个 EV 与 S，恰 O=1 仅该侧 S 不可用。[源码](../src/subjective_analysis.c) |
| `analyze_historical` | 先验指针；非 VALID 直接 OK/available=false，忽略赔率及区间。VALID 检查字段和计数后验证赔率，从 e/c 重建 Jeffreys 形参计算两个后验尾，成功才提交；不重验 gate、版本或出处。必须使用相应估计器结果。[源码](../src/historical_analysis.c) |
| `provenance_transition` | 指针→前态不变量→raw 验证；旧暴露加随后主体或 raw 改变可 compromise，并列的新暴露不追溯。两标志粘滞，compromised 蕴含 exposed，支持同对象写回，无 reset。[源码](../src/provenance.c) |
| `compose_analysis` | 输出→主观→历史→事件赔率→补赔率→主观分析→历史分析→两关系。首错退出，整个结果一次提交。即使无历史也验证赔率，区别于单独的历史分析。无自动 provenance 转换或融合。[源码](../src/analysis_composition.c) |

**类型清单。** 五枚举是 `probspan_status`（调用、参数、数值错误）、`probspan_history_state`（NO_HISTORY/INSUFFICIENT/VALID）、`probspan_ev_state`（正/负/跨阈值）、`probspan_odds_combination`（逆赔率和的三态）、`probspan_model_relation`（一致正/负、冲突、不确定、历史不可用）。十结构按角色为 `probspan_subjective_result`、`probspan_history_result`，`probspan_ev_interval`、`probspan_odds_geometry`，`probspan_subjective_side`、`probspan_subjective_analysis`，`probspan_historical_side`、`probspan_historical_analysis`，`probspan_provenance`、`probspan_analysis`。ABI=1，主观/历史模型、gate、主观赔率分析版本各为 1。历史分析没有额外版本。详细字段及限界见 [API](API.md) 和[公共头](../include/probspan/probspan.h)。

**决策和失败。** 两侧 gross odds 的盈亏阈值是 1/O；补侧在事件轴是 1−1/Oc。EV = pO−1 先乘再减，补事件区间反序。最小值严格 >1e−12 才 ROBUST_POSITIVE，最大值严格 <−1e−12 才 ROBUST_NEGATIVE，其余跨阈值；逆赔率和与 1 差在 ε 内为 CRITICAL。主观 S 是 logit 中心到阈值距离除以半宽。历史事件尾保持 1−I_(1/Oe)(a,b)，补侧是 I_(1−1/Oc)(a,b)，结果限于 [0,1]；后验参数质量、下一次兑现概率和整个区间的分类各有意义。各 status API 的 non-OK 保持调用者输出，必须先查成功再读本次值。零占位不能当估计；分别检查 `has_estimate`、`available`、`has_robust_margin`。任意重叠参数未支持，provenance 的原地转换是明确例外。 [行为细则](BEHAVIOR_SPEC.md)

**数值内核。** [Beta](../src/beta.c)普通路径采用正 Gamma 归一化的连分式与有界求逆。a,b≥.5 且和>10000 用 [logit 积分](../src/beta_logit.c)；[正 Gamma](../src/gamma.c)避开共享 signgam。十进制比较精确中点，支持正常合同中指定的 locale/舍入模式；这不延伸到下游一般 libm。浮点需 binary64 和受支持的环境、无 fast-math。离散结果及 parser 位精确；普通数值误差≤1e−12+1e−12×|ref|，Beta≤1e−10+1e−10×|ref|，极端分位按合同做相邻值夹逼。计数精确、表示后的形状/阈值可能舍入以及 ulp 可能跨显著概率质量，诊断不能假定每种 libm 逐位一致。 [政策](../oracle/numerical_policy.json) · [数值合同](NUMERICAL_CONTRACT.md)

**所有权、构建和可选路径。** 根静态 C11 `ProbSpan::probspan` 只安装 archive、公开头、CMake package，非 MSVC 链 libm。无 Python/DB/文件/环境访问、库堆分配或全局可变状态；调用者负责采集、身份、时钟、实际暴露、资格、快照和持久化，以字段和含义保存，不将结构体位流跨编译器重放。provenance 是状态转换，不会判断证据真实或改变数学。在[根构建](../CMakeLists.txt)与[安装消费者](../tests/consumer/main.c)对照声明和打包。稳定库继续排除训练、泛统计/评分、模型融合、工作流、序列化、自动资格及通用特函数 API。

[设备证据 review](../integrations/device_history/evidence.py)可检查该固定 100 小时设备周期的声明、工况、截止、成熟、别名/冲突、跨角色重叠、可见依赖和正权层支持；返回收据及可选计数，不能从声明认证独立。严格/池化走 [Python 桥](../integrations/device_history/v1.py)与[已安装 C 消费者](../integrations/device_history/v1_consumer.c)，有 timeout、版本和 payload 检查。其 [EXACT 查找](../integrations/device_history/CMakeLists.txt)与根的 SameMajorVersion 不同。固定两层、独立 Jeffreys 的[标准化](../integrations/device_history/standardization.py)用 NumPy/SciPy 和 CDF 包络，返回目标参数区间及数值状态，没有 v1 gate 或 EV。不能通过构造 v1 history struct 传入，否则 EV 区间与重建的 Beta 尾会错配。参考与其依赖在根安装之外。 [设备说明](PREVIEW_DEVICE_HISTORY.zh-CN.md)

<a id="decisions"></a>

## 4. 九项仍开放的决策

状态逐行核对 [Phase C 决策登记](research/phase-c/decision-register.tsv)。批准 Phase C 研究不转化成这里的实施许可。

| ID／状态 | 选项、证据、条件默认及影响 |
|---|---|
| C-D001 · OWNER_REQUIRED | 现状、限域外部试点或扩大产品。C-O006/C-O012/C-O022、B-E002 说明资格风险与边界。默认现状；实际用户和可观察净收益才比较试点。阻塞范围扩展，不阻塞维护基线。 |
| C-D002 · OWNER_REQUIRED | 保留现有 Preview、选择真实固定期设备或另论证其它端点。C-O006–008/B-E004 表明删失、依赖和观察期影响资格。需负责人、数据许可、独立审查、真实总体/端点/时间。阻塞真实试点。 |
| C-D003 · PROPOSED | 调用方校验、限定的可追踪 receipt 或中央认证。C-O012/C-O013/C-O020/B-E002 表明可记录检查与声明，不能自动知道机制。默认调用方；试点可经批准加明确未知和失败的收据，拒绝通用认证。可延后。 |
| C-D004 · OWNER_REQUIRED | 维持两层参考、独立模型工具或根内多模型。C-O002/C-O005/C-O026、B-E003/007。默认保持；支持、权/依赖及组外验证成立后才比较独立结果。阻塞标准化扩展/借用，简单同义计数路径可单独研究。 |
| C-D005 · DEFERRED | 调用方、独立 evaluator 或根库存储/评分。C-O011/C-O019/C-O021、B-E005/007。保留外部责任；有版本化配对、分母和时序假设才评独立工具。无需阻塞二元试点。 |
| C-D006 · PROPOSED | 现有私有核、同域二次使用或不同精度后端。C-O001/C-O014/C-O016/C-O025、B-E006。默认私有原样；两个真实同合同的消费者、独立高精度及冻结分支证据才讨论共享。外部适配不依赖这一决定。 |
| C-D007 · OWNER_REQUIRED | 保持安装、独立可选组件或共享根安装。C-O022/C-O025。分离可卸载、隔离依赖；新包仍需维护协议、许可证、EXACT 兼容检查及旧消费者回归。选择阻塞任何新分发。 |
| C-D008 · DEFERRED | 调用方处理风险集/计数/连续/联合，或在有任务时独立垂直模块，泛模型 API 无现证。C-O008–010/C-O018、B-E004。每种对象需数据及专属验证；与同义计数无依赖。 |
| C-D009 · OWNER_REQUIRED | 条件效果、领域代价含未答或强行统一阈值。C-O004/C-O019/C-O020、B-E002/005。由域及所有者选误纳、误拒、未答、延时成本和验证分母，保持 v1 gate。阻塞有效果目标的试点评判。 |

<a id="engineering"></a>

## 5. 条件式工程路线

- **必须保留**：同一已发行输入的 ABI/字段、数学、分支、舍入、版本、安装与输出保持承诺。保持可重入和独立 oracle。任何打破兼容的目标需明确的旧轨/迁移和单独许可。
- **可选候选**：当所有者选择真实固定时距任务，优先用直接调用者验证＋安装 v1 与现有设备 Preview 对照。只补被结果证实的外部缺口，技术授权以单次可结束工程单元为度；没有净收益就停止。
- **仍需科学证据**：潜在依赖、代表性和工业外效度、无支持层及共估权、标签误差或选择性、真值版本及工具链覆盖。#10 先证明语义及目标支持；#9 再评借用。合格但零目标不会让不存在的冲突观测出现。
- **调用方拥有**：定义和身份、实际披露、采样/观测/可用时点、权、内容和许可证、付款与效用、存档及迁移。只有匹配且完整的成熟计数进旧 API，合法拒绝留下原因，不伪造 NO_HISTORY。
- **独立或延期**：标准化、风险集、预测评价和分布模型各自可被选择，均非试点前置。保持现有私有核；拒绝默认 fusion、共享 VALID、跨估计量结果复用、中央工作流和由计数猜风险集。

**若获批一个试点。** 先固定端点、人群、独立单位、固定 h、信息 cutoff、真实成熟规则及声明链。准备有授权的数据、可复核的错误案例和域审查标签，以实体/簇和时间切分，预先定义误纳/误拒/拒绝成本、延迟和停止条件。用同一快照比较 ①调用者已有检查直接进 C，②既有设备参考，③仅在前两者有可测缺口时设计的新适配。依次对比拒绝原因、合格 e/c、时序及重复、直连 v1 的逐字段输出、端到端请求损失、改动与部署成本。三条路径使用同一数据与估计量。样本应含同 ID 不同工况、跨源重复、已知相关、失访、未知键、正权空层、迟到修订、空但合格和失败旧输出。既有最佳方案已经足够或无法验证净价值时结束。真实应用不能靠合成套件认证。 [Phase C 条件门槛](research/phase-c/conditional-phase-d-plan.zh-CN.md)

**编码到独立验收。** 取得明确允许目录和 Git 动作后冻结小范围任务、候选输入输出、兼容假设、独立数值预算及判别标准。实现后按领域适用、数值精度、软件集成、包兼容分别出证据；旧消费者用净安装前缀重建，独立审查对比真实 Git diff。缺字段、不可识别、负责人数据未授权或平台未测，均如实标限。未来若另获授权考虑发布，再绑定实际候选或发布提交、相关工作流与平台、产物和许可，提独立 review 及所有者选择。没有自动版本、发布日期或 Preview/RC 次数。

<a id="windows"></a>

## 6. Windows 本地恢复与核验

以下 PowerShell 从实际检出的 ProbSpan 开始。仅在当次许可已明确时创建实施分支。检查用的临时 build/install 放在系统临时目录，能保留日志且不污染仓库。Windows 未在本交接任务运行；这些是未来可执行步骤。

### 6.1 查远端、工作区、政策

先查看 Git 与托管信息；任一异常先止于读取，核对差异。

```powershell
git rev-parse --show-toplevel
git remote -v
git status --porcelain=v1 -b
git worktree list
git branch -avv
git rev-parse HEAD
git rev-parse --verify refs/heads/main
git ls-remote origin refs/heads/main refs/tags/v1.1.0 'refs/tags/v1.1.0^{}'
git fetch origin
git rev-parse origin/main 'origin/main^{tree}'
git log --left-right --oneline HEAD...origin/main
git diff --name-status HEAD..origin/main
git merge-base --is-ancestor 7c25a4dee76d6203eeaddeb9cac6c012d6c3ee94 origin/main
git diff --name-status 7c25a4dee76d6203eeaddeb9cac6c012d6c3ee94..origin/main
```

本地没有 main 时对应的 `rev-parse --verify` 会失败，记录无该 ref 即可；祖先检查非零时需要确认历史或授权基线变化。分别检查 staged/unstaged/untracked，必要时用 `git diff` 和 `git diff --cached`，不要清空或混入未知变更。建议开新 worktree；在任务允许时，将已核验提交和唯一获准分支写入下列变量。已存在同名分支时，先查看归属和变化，保留原有工作。示例里的分支名及历史 SHA 只是变量模板。

```powershell
$verifiedBase = '7c25a4dee76d6203eeaddeb9cac6c012d6c3ee94'
$approvedBranch = Read-Host 'Branch name explicitly authorized for this task'
git branch --list $approvedBranch
git ls-remote origin "refs/heads/$approvedBranch"
$taskDir = Join-Path ([System.IO.Path]::GetTempPath()) ('probspan-work-' + [guid]::NewGuid())
# Run only after verifying the branch name, base, authorization and absence of conflicts.
git worktree add -b $approvedBranch $taskDir $verifiedBase
if ($LASTEXITCODE -ne 0) { throw 'Worktree creation failed' }
Set-Location $taskDir
git status --porcelain=v1 -b
git rev-parse HEAD
```

通过已获批准的 GitHub 连接读两份私有政策的当前完整正文。若用已认证的 `gh`，先取 main SHA，再按该 SHA 读取，避免读取期间发生漂移。只在私有终端看，不进公开日志。连不上时记录缺正文和受影响动作，不凭旧快照假设；授权连接器可替代 gh。

```powershell
gh auth status
$policyRepo = Read-Host 'Authorized private policy repository (owner/name)'
$policyRef = gh api "repos/$policyRepo/commits/main" --jq .sha
if ($LASTEXITCODE -ne 0 -or $policyRef -notmatch '^[0-9a-f]{40}$') { throw 'Policy revision unavailable' }
foreach ($name in @('WORKFLOW.md','RELEASE_POLICY.md')) {
    gh api "repos/$policyRepo/contents/${name}?ref=$policyRef" -H 'Accept: application/vnd.github.raw+json'
    if ($LASTEXITCODE -ne 0) { throw "Unable to read $name" }
}
```

核对 `gh pr view 17/18/19 --json state,mergeCommit,headRefOid`（分别传入编号）、`gh release view v1.1.0 --json url,isDraft,isPrerelease`，用 `git rev-parse 'v1.1.0^{}' 'v1.1.0^{tree}'` 区分对象。按第 1 节入口读源码和研究。明确测试与调用链关联，例如 `git grep -n -E 'ps_beta_(cdf|quantile)|probspan_history_estimate' -- src include tests integrations`，再查冻结参考、公开脚本与分支覆盖。可对 [C 图谱](research/phase-c/current-state-and-evidence-map.zh-CN.md)核对路径。

### 6.2 发现实际工具，构建根和安装消费者

用已启动的同架构工具链终端。VS/MSVC 可用 Developer PowerShell；MinGW/UCRT64 用有对应 CMake/构建器和编译器 PATH 的环境。先验版本、架构与可用 generator，不能混用 MSVC 和 MinGW 对象/安装前缀。CMake ≥3.16，要求 C11、binary64 与合同浮点设置。下面复用一次选择的 generator，各构建用不同目录。跟实际命令失败停止，通过 `CMakeCache.txt` 复核编译器和 generator。

```powershell
Get-Command git,gh,cmake,ctest,cl,gcc,clang,ninja,mingw32-make,python,py -ErrorAction SilentlyContinue |
    Select-Object Name,Source
cmake --version
cmake --help

function Invoke-Checked {
    param([string]$Tool, [string[]]$Arguments)
    & $Tool @Arguments
    if ($LASTEXITCODE -ne 0) { throw "$Tool exited $LASTEXITCODE" }
}
$generatorArgs = @()   # Default from selected terminal; or set @('-G','MinGW Makefiles') if verified.
# For an explicitly chosen VS generator use its installed name, and -A for the intended architecture if needed.
$sessionRoot = Join-Path ([System.IO.Path]::GetTempPath()) ('probspan-build-' + [guid]::NewGuid())
New-Item -ItemType Directory -Path $sessionRoot | Out-Null
$core = Join-Path $sessionRoot 'core'
$prefix = Join-Path $sessionRoot 'install'
$consumer = Join-Path $sessionRoot 'consumer'
$device = Join-Path $sessionRoot 'device'

Invoke-Checked cmake (@('-S','.','-B',$core,'-DBUILD_TESTING=ON',
    '-DPROBSPAN_BUILD_EXAMPLES=ON','-DCMAKE_BUILD_TYPE=Release') + $generatorArgs)
Select-String -Path (Join-Path $core 'CMakeCache.txt') -Pattern '^CMAKE_(GENERATOR|C_COMPILER|BUILD_TYPE)'
Invoke-Checked cmake @('--build',$core,'--config','Release','--parallel')
Invoke-Checked ctest @('--test-dir',$core,'-C','Release','--output-on-failure')
Invoke-Checked cmake @('--install',$core,'--config','Release','--prefix',$prefix)
Get-ChildItem $prefix -Recurse -File
Invoke-Checked cmake (@('-S','tests/consumer','-B',$consumer,"-DCMAKE_PREFIX_PATH=$prefix",
    '-DCMAKE_BUILD_TYPE=Release') + $generatorArgs)
Invoke-Checked cmake @('--build',$consumer,'--config','Release')
Invoke-Checked ctest @('--test-dir',$consumer,'-C','Release','--output-on-failure')
```

`--config Release` 适用于多配置，单配置由 `CMAKE_BUILD_TYPE` 选 Release。Python 未配置时五项 freshness 不注册，核心构建无 Python 运行依赖。记录实际 CTest 项数；用 `ctest --test-dir $core -C Release -N` 区分未注册和已运行。安装消费者必须指向新前缀的公开 `find_package`，不能用源头/内部路径替换。检查实际导出文件、编译器和体系结构。根包版本配置为 SameMajorVersion；后续可选消费者另行使用 EXACT。

### 6.3 可选设备参考

只有需要核验该集成且平台有相容 Python/wheel 时运行。用实际可用解释器，先查它的版本/架构；没有 `python` 命令但有 launcher 时先用 `py -0p` 选可用解释器，再用该路径。以下假定已发现的 `python` 满足要求。v1.1.0 此参考钉住 NumPy 2.4.4、SciPy 1.17.1；以后读实际文件，不凭本页历史值。安装只在 `$sessionRoot` 隔离环境，缺轮子或 EXACT 不相符时说明失败和不能验证的部分。

```powershell
Invoke-Checked python @('-c','import platform; print(platform.python_version(), platform.machine())')
$venvDir = Join-Path $sessionRoot 'device-venv'
Invoke-Checked python @('-m','venv',$venvDir)
$devicePython = Join-Path $venvDir 'Scripts\python.exe'
Invoke-Checked $devicePython @('-m','pip','install','-r','integrations/device_history/requirements.txt')
Invoke-Checked $devicePython @('-c','import numpy,scipy; print(numpy.__version__, scipy.__version__)')
Invoke-Checked cmake (@('-S','integrations/device_history','-B',$device,
    "-DCMAKE_PREFIX_PATH=$prefix",'-DCMAKE_BUILD_TYPE=Release') + $generatorArgs)
Invoke-Checked cmake @('--build',$device,'--config','Release')
$exePaths = @(
    (Join-Path $device 'Release\device-history-v1.exe'),
    (Join-Path $device 'device-history-v1.exe')
)
$deviceExe = $exePaths | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $deviceExe) { throw 'Built device-history-v1.exe not found' }
$env:PROBSPAN_DEVICE_CONSUMER = $deviceExe
$env:PYTHONDONTWRITEBYTECODE = '1'
Invoke-Checked $devicePython @('-m','unittest','-v','integrations.device_history.test_device_history')
Invoke-Checked $devicePython @('-m','integrations.device_history.example',$deviceExe)
```

不要为通过设备测试而改发布版本、临时放宽 EXACT 或跳过状态。Windows 上 MSVC 与 MinGW 的实际行为、Python 运行环境及可用 sanitizer 要分别报告。 [构建安装](BUILD_AND_INSTALL.md) · [设备参考命令](PREVIEW_DEVICE_HISTORY.zh-CN.md)

### 6.4 失败诊断、验证证据及独立审查

| 检查 | 原因追踪与记录要求 |
|---|---|
| API/state | 先定位哪个入口、哪个首错以及输出是否保持。用 `api_contract` 查非法对象、版本和顺序，用 `state_parity` 区分 provenance、单个分析和聚合；`analysis_parity` 独立检查 EV/赔率边界和后验尾。 |
| 数值 | 对照 `oracle_parity`、`large_numerics`、`decimal_parity`。记录精确/舍入形参、计算和参考的误差、C rounding mode、编译器/libm 和容差。表示断层不等同算法失败；不要改冷冻参考以过测试。fixture freshness 与独立重生成分别报告。 |
| 安装或可选集成 | 看导出路径、公共头、精确安装版本、编译器/位宽、实际 exe 和依赖。区分工具缺失、接口错误、科学资格失败、数值失败。对历史参考和真实数据的范围分别说明。 |
| 精确 SHA 的 CI | `gh run list --commit <完整提交SHA>` 或 PR `gh pr checks <编号>` 只获取对应证据。阅读 `gh run view <run-id> --json headSha,status,conclusion,jobs,url`，失败再取批准范围内日志。区分 PR 检查展示和实际 run headSha、job、事件和环境；如另有 merge commit 要标明。Linux/Windows 本地成功不能替代 CI，旧绿标不能自动套用。 |

针对失败重跑可用 `ctest --test-dir $core -C Release -R probspan_large_numerics --output-on-failure`，保存输入、退出码、预期与实际，再检查相关接口、版本和旧轨。维护者按 [TESTING](TESTING.md)和[验证导航](IMPLEMENTATION_VALIDATION.zh-CN.md)取参考方法与依赖 pin。当前 handoff 未更改 oracle，未发起跨平台 CI。

**本交接实际运行。** 在 `7c25a4dee76d6203eeaddeb9cac6c012d6c3ee94` 的独立 Linux 云 worktree，GCC 14.2.0、glibc 2.41、CMake 3.31.6、Python 3.12.14、NumPy 2.4.4、SciPy 1.17.1，使用临时前缀执行 `cmake -S . -B "$p/core" -DPROBSPAN_BUILD_EXAMPLES=ON -DCMAKE_BUILD_TYPE=Release`、`cmake --build "$p/core" --parallel 4`、`ctest --test-dir "$p/core" --output-on-failure`、`cmake --install "$p/core" --prefix "$p/install"`。分别以 `cmake -S tests/consumer -B "$p/consumer" -DCMAKE_PREFIX_PATH="$p/install"` 和 `cmake -S integrations/device_history -B "$p/device" -DCMAKE_PREFIX_PATH="$p/install"` 配置并构建，`ctest --test-dir "$p/consumer" --output-on-failure`、`PROBSPAN_DEVICE_CONSUMER="$p/device/device-history-v1" python -m unittest integrations.device_history.test_device_history`。根 14/14，外部消费者 1/1，设备用例 15/15；检查了 archive、公开头与 CMake 配置。Windows 步骤、额外平台与现场试点均未运行。文档自审核对 13/10/5 API 计数、9 个决策状态、26 个重叠 ID、7 项实验引用、91 处相对路径/锚点及正文 Git 对象；外部 GitHub 工件用实际 Issue、PR 和 Release 查询核对。

<a id="continuity"></a>

## 7. 长期维护、交付与停止

新会话从第 1 节证据锚点和当次授权开始，无需此前对话。记录实际当前提交、相关合同是否同历史锚点及有意义差异。A/B/C 为独立的接受快照，发现元数据更正、相反证据或新失效应留可追溯补注并说明适用范围。Provisional ID 与已解决修复不改成待实现任务。实际工程改动时按维护入口更新受影响 API/行为/数值/兼容、四份指南、测试和必要 README，账本只在授权且有实质证据时附可追溯变化。旧输出可重现/解释时保留版本、原始输入、可用标志和相关快照。无需复制整份旧报告或新增治理权威。

后续英文 Codex 报告应包含实际起止 local/remote SHA、工作区/branch、完整文件和行为影响、命令参数、实际 OS/编译器/架构/依赖、结果及失败日志、精确 CI headSha/job、未测试或无证据项、回滚/兼容和 Technical Debt Impact；通过 `git diff --check`、`git diff --stat <base>...HEAD` 和逐文件检查保证授权范围。独立 ChatGPT 审查实际提交、契约、断言和 CI，再给 PASS、FAIL 或证据不足；实施者自审不能替代。尚缺真实设备场地有效性、跨域代表性、部分标签和时间修订机制、更多环境数值证据。发生结果对象变化、新依赖、跨平台误差、公开承诺、数据使用或发行边界变化时交所有者决定。

本次 Git 范围仅此交接文档。Phase C 已接受；Phase D 实施须等待所有者选定下一工程目标及足够证据。当前文本不批准功能 backlog、公共 API 或架构改变，也没有 ABI 升级、Stable 更新、标签或发布。完成文档的单个独立评审 PR 后停止。
