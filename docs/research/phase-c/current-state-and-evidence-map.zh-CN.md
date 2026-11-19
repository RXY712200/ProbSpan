# 现行实现、边界与问题证据地图

[导航](README.zh-CN.md) · [重叠登记](overlap-register.tsv) · [Phase A 交叉表](../phase-a/ledger-crosswalk.zh-CN.md) · [Phase B 估计量](../phase-b/problem-estimand-map.zh-CN.md)

以下相对源码链接以 Phase C 起点 `5406d38a62b831c2e4560b0242dd89ec1a6754a1` 为基线。生产路径逐字节等同 Stable `46ff21847c5522eb983d3f58e396354461a64f34`。公开兼容基线始于 v1.0.0，当前产品 v1.1.0；ABI、各模型、gate 和分析版本独立且均为 1。见[公共头](../../../include/probspan/probspan.h)、[契约](../../API.md)、[行为](../../BEHAVIOR_SPEC.md)。

## 真实调用图及所有权

箭头从调用者指向被调用者。为可读性省略头文件声明包含；静态链接允许独立调用各公共入口。

```text
caller -> compose_analysis -> subjective_estimate -> raw-domain / v1 logit rule
                          -> history_estimate -> history shapes -> Beta -> logit quadrature / Gamma
                          -> odds_validate          (decimal parser is a separate text entry)
                          -> analyze_subjective -> geometry / policy / logit S
                          -> analyze_historical -> geometry / policy / shapes / Beta CDF
                          -> classify_model_relation (event, complement)
caller -> provenance_transition -> raw-domain check only
caller -> odds_parse -> decimal conversion -> odds range check
external device C executable -> installed ProbSpan::probspan -> history_estimate
external device Python -> evidence.review -> v1.estimate_v1 -> C process
                                         -> standardization.standardize -> SciPy / NumPy
external evaluation/research -> explicitly selected snapshots and experiment backends
```

| 公共入口（省略 probspan_ 前缀） | 调用实体、保证与拒绝点 |
|---|---|
| `abi_version` | 返回版本整数；[probspan.c](../../../src/probspan.c)。 |
| `subjective_half_width`, `subjective_estimate` | 半宽入口要求 [.01,.99]；原始整数 0–100 估计入口保留 raw，clamp 到 1–99%，在 logit 上取分段半宽后映回区间。概率秩序可检查，主观信念、频率覆盖归外部。[subjective.c](../../../src/subjective.c) · [subjective_input.h](../../../src/subjective_input.h) |
| `history_estimate` | 有符号非负 e/c 转无符号求和。零样本 OK/NO_HISTORY，数值字段无意义。其余 Beta(e+.5,c+.5) 后验均值和两尾，n≥20 且宽≤.25 才 VALID，INSUFFICIENT 仍可有估计。输入没有主体、事件、时距、权、簇、选样或标签字段。[historical.c](../../../src/historical.c) · [history_model_private.h](../../../src/history_model_private.h) · [model_v1.h](../../../src/model_v1.h) |
| `odds_validate`, `odds_parse` | 有限赔率 ≥1，文本仅 ASCII 十进制词法，精确中点 ties-to-even，解析后再验域，失败不提交输出。[odds.c](../../../src/odds.c) · [decimal.c](../../../src/decimal.c) |
| `classify_ev`, `classify_odds_combination`, `classify_model_relation` | EV 用端点和冻结 ε=1e−12 的严格越界；裸分类入口检查输出指针，其数值上下文由调用者拥有。赔率组合校验两侧；关系检查枚举，不可用时不读历史枚举，输出独立的关系类别。[decision_geometry.c](../../../src/decision_geometry.c) · [decision_policy.c](../../../src/decision_policy.c) |
| `analyze_subjective` | 区间和半宽有效后查赔率，计算互补、几何和 EV；赔率恰 1 时该侧 S 无意义，EV 仍有效。[subjective_analysis.c](../../../src/subjective_analysis.c) |
| `analyze_historical` | 非 VALID 先返回 OK/available=false，忽略赔率及估计字段。VALID 要求 has_estimate、非负计数、有序概率区间，重建固定 Jeffreys 形状算两个 EV 后验尾；事件用 1−CDF。两个尾都成功才提交输出。结果类型的契约是由对应 estimate 产生；函数没有证明计数、区间、版本和外部资格全部相符。[historical_analysis.c](../../../src/historical_analysis.c) |
| `provenance_transition` | 校验指针、前态不变量和 raw 输入，旧暴露×随后改变才能标记 compromised；同操作首次曝光不追溯。状态粘滞，可原地转换，事实（主体变更/实际可见）由调用者提供，无时钟、原始数据或资格判断。[provenance.c](../../../src/provenance.c) · [信息合同](../../PROVENANCE.md) |
| `compose_analysis` | 主观估计→历史估计→依次验两个赔率→各分析→各关系，首错退出，局部结构一次提交。即使无历史组合也验证赔率。无融合、无 provenance 自动调用；分析事实由外部存储。[analysis_composition.c](../../../src/analysis_composition.c) |

五个枚举分别覆盖调用状态、历史状态、EV 状态、赔率组合、模型关系。十个结构为 `subjective_result, history_result, ev_interval, odds_geometry, subjective_side, subjective_analysis, historical_side, historical_analysis, provenance, analysis`（皆有 `probspan_` 前缀）。`analysis` 聚合两套估计、赔率、分析和关系；provenance 单独传递。零初始化帮助避免读垃圾，但不能凭结构体零字节推定有效估计。现行非 OK 公共调用保持输出；数值容差与离散状态的判据各自冻结。 [完整字段](../../IMPLEMENTATION_API_REFERENCE.zh-CN.md) · [数值政策](../../../oracle/numerical_policy.json)

私有 Beta 路径检查正形状及输入域；普通方法 log-Gamma/递推连分式加有界二分，a,b≥.5 且和>10000 进入标准化 logit 积分/混合求根。正 Gamma 实现避免把符号全局状态拉进计算；形状从已表示的计数产生。不可求值返回失败，不自选宽松的结果。精确十进制位型并不赋予下游倒数或 libm 位级保证。EV 映射在 `expected_value` 显式先乘再减，移动成 FMA 可能改变 ε 分类。 [内部实现](../../IMPLEMENTATION_INTERNALS.zh-CN.md) · [beta.c](../../../src/beta.c) · [beta_logit.c](../../../src/beta_logit.c) · [gamma.c](../../../src/gamma.c) · [数值契约](../../NUMERICAL_CONTRACT.md)

| 构建和证据层 | 核实的边界 |
|---|---|
| 安装目标 | 根 [CMakeLists.txt](../../../CMakeLists.txt) 静态 C11 archive、单公共头与 CMake package；非 MSVC 链接 libm。Python 只用于可选 fixture freshness。根安装不携带 NumPy/SciPy、测试、私有头或集成脚本。普通[安装消费者](../../../tests/consumer/main.c)走已安装公开目标。 |
| 冻结验证 | `oracle_parity` 保护普通 v1 数学；`large_numerics` 独立高精度参考及邻接；`decimal_parity` 精确位；`analysis_parity` 决策和阈值，`state_parity` 因果及组合；`api_contract` 输出保持、版本与异常。fixture freshness 不等于重生成独立参考。[测试](../../TESTING.md) · [参考说明](../../../oracle/README.md) |
| 设备参考 | [evidence.review](../../../integrations/device_history/evidence.py) 只接支持的调用方声明；执行版本、截止、100 小时完整观察、别名/重叠/已知依赖和两层正权支持检查。不能证明快照、真实独立或迁移。同角色同键只容许 query 别名，跨角色相同键拒绝，未知/冲突返回 receipt 且无 counts。 |
| 两条调用方结果路径 | [v1.estimate_v1](../../../integrations/device_history/v1.py) 只接受严格/汇聚收据，显式本地进程带 timeout 和版本/状态检查。可选 CMake `1.1.0 EXACT` 不同于根 SameMajorVersion 配置。[standardize](../../../integrations/device_history/standardization.py) 使用 SciPy 两个独立后验求固定权 CDF 包络和数值预算；输出 target_parameter_posterior，无 v1 gate 与 EV。Python 运行时不依赖 C 私有数字代码，早期 Preview 脚本只有测试交叉重放。[设备说明](../../PREVIEW_DEVICE_HISTORY.zh-CN.md) |
| 历史/研究 | [历史证据](../../HISTORICAL_EVIDENCE_RESEARCH.zh-CN.md) 区分三类资料；[早期实验](../../../research/preview_history.py)与[输出](../../../research/preview_history_results.json)只支持 DGP；Phase B [代码及记录](../../../research/phase-b/README.md)不是发布时依赖。 |

产品边界是带 scoped provenance 的确定性概率→不确定性→决策 C 核心。调用者负责身份、时钟、存储、工作流和历史适用性；Issue #1 与 [范围](../../ORIGIN_AND_SCOPE.md) 明确把评分、自动融合、泛统计/ML、数据库和序列化留在安装边界之外。#5/#6 分别是可表示性和平台，#8 数据库提案，#9 条件借用，#10 合法来源匹配。Phase A/B 研究提供问题证据，未扩大公开合同。

## A/B 主张复核

| 证据和等级 | 本轮重查与架构含义 |
|---|---|
| [Phase A 方法、应用和来源](../phase-a/README.zh-CN.md) · S0008 S0009 S0029 S0034 S0038 S0088 | 96 源记录等级不同。成熟 e/c、特征–结果和发出预测–兑现数据分家。天气集合/医疗标签/磁盘暴露支持分母和时距差异，不能补真实目标设备；来源存证只能帮助追踪。 |
| [B-E001/B-E002](../phase-b/experiments-and-results.zh-CN.md#b-e002) · S0006 S0007 | 固定历史合成枚举。e=18/180、目标 n=20 下，p=.1 合并 RMSE .0070 vs .0667；p=.5 合并 .3584 vs .1065。空目标时每个混合似然乘 1 是解析结论。统计就绪不是准入。 |
| [B-E003](../phase-b/experiments-and-results.zh-CN.md#b-e003) · S0009 | 同源权与风险忽略协方差覆盖 .8707，含协方差 .9373；合成事实。无高层支持的 [.04,.24] 界来自模型条件下的识别论证，不能化为设备点后验。 |
| [B-E004](../phase-b/experiments-and-results.zh-CN.md#b-e004) · B-S0001 | 竞争风险 CIF 真值 .24，1−KM 对象 .28；模拟复核及风险集公式支持分离，不能把竞争过程压进二元计数。 |
| [B-E005](../phase-b/experiments-and-results.zh-CN.md#b-e005) · S0010 S0029 S0091 B-S0002 | 精确 DP 与构造验证，固定观察约 .05597、窥看约 .30435；真值版本和选择掩码可反转排名，边际校准不推出子群保证。 |
| [B-E006](../phase-b/experiments-and-results.zh-CN.md#b-e006) · S0050 | Linux 高精度比较的存档值重算为严格 10/15、±1e−10 容差 15/15。严格判断针对 JSON 中记录的二进制浮点值，非任意精度真值或全域定理。邻点与后验解释分开，5 个不严格不构成已确认合同缺陷。 |
| [B-E007](../phase-b/experiments-and-results.zh-CN.md#b-e007) · S0087 B-S0003 | 18 个已见球员的公共观察性后续留出。按打数 Brier pool .201831 < 层级 .201859；按球员 pool .196769 > 层级 .196660。评分权改变目标，微小差值不足以建立跨组优越性。 |

## 固定问题与架构问项

链接指向归属问题及复用条件，不改变任何账本行的状态/排期。详细反例见[登记](overlap-register.tsv)。

| ID | 架构问项 | 跟踪 |
|---|---|---|
| A01 | 同义独立计数怎样从调用方进入现行入口？ | C-O002 C-O006 |
| A02 | 有估计、可决策、证据合格是否分开？ | C-O003 C-O012 |
| A03 | 一次事件的信念能否与来源可靠性分开？ | C-O017 |
| A04 | 可重评的发出预测和成熟标签由谁持有？ | C-O011 |
| A05 | 缺证据时允许输出未知/界而非补先验吗？ | C-O012 C-O024 |
| A06 | 冻结主观规则与外部校准能否各自演进？ | C-O017 |
| A07 | 历史估计可继续脱离赔率/主观输入吗？ | C-O003 |
| A08 | 什么是目标差而非接口复用问题？ | C-O009 C-O010 |
| B09 | 工况切换怎样否决迁移？ | C-O020 |
| B10 | 共同参数与交换组参数由何证据区分？ | C-O002 C-O026 |
| B11 | 跨域权重有无正性和机制约束？ | C-O005 C-O020 |
| B12 | 与目标无关的历史何处丢弃？ | C-O020 C-O024 |
| B13 | 端点、单位和实际随访谁比较？ | C-O006 C-O008 C-O023 |
| B14 | 记录声明能否避免冒充认证？ | C-O012 C-O020 |
| B15 | EB 条件参数输出能否保留 plug-in 含义？ | C-O002 C-O026 |
| B16 | 群体超参数及未见群误差如何隔离？ | C-O002 C-O026 |
| B17 | 冲突诊断为何不能取代准入？ | C-O020 |
| B18 | 目标层权由谁确定并保留总体语义？ | C-O005 |
| B19 | 已知簇、独立单位与记录行谁区分？ | C-O007 |
| B20 | 去重键、跨来源重叠及修订由谁维护？ | C-O006 C-O007 C-O021 |
| B21 | 目标选择、协变量与缺支持如何暴露？ | C-O005 C-O019 C-O023 |
| C22 | 专家 elicitation 与 v1 主观宽度的界面？ | C-O017 |
| C23 | 新组先验预报如何避免假装目标已有数据？ | C-O002 C-O026 |
| C24 | 增量批次是否业已消费或与既有样本重叠？ | C-O002 C-O026 |
| C25 | 预测时点特征和成熟标签属于何层？ | C-O010 |
| C26 | 后置校准的学习集如何隔离验证流水？ | C-O011 |
| C27 | 阈值开闭、点质量和事件时距如何传达？ | C-O010 |
| C28 | 合成 draws 怎样防误入观测计数？ | C-O007 C-O024 |
| C29 | 相同目标的 forecast pooling 是否独立于 v1？ | C-O018 |
| C30 | 如何避免用边际乘积默认联合依赖？ | C-O018 |
| C31 | 连续预测分布与参数区间如何拒绝互转？ | C-O010 |
| C32 | 暴露率、次数与二元对象在何处隔离？ | C-O009 |
| C33 | 风险集/删失/原因谁拥有？ | C-O008 C-O009 |
| C34 | 时间变化和可用时钟谁拥有？ | C-O011 C-O021 |
| D35 | 评分要求对照同一档案和分母吗？ | C-O011 |
| D36 | 分组/时距校准由哪个验证工具负责？ | C-O011 C-O019 |
| D37 | 资格和 readiness 能否不共用 VALID？ | C-O012 |
| D38 | 暴露因果与原始证据谱系各记录什么？ | C-O013 C-O021 |
| D39 | 何处保存区间对象、概率质量和数值包络区别？ | C-O003 C-O005 C-O016 C-O017 |
| D40 | 无成熟目标标签如何避免宣称漂移已查明？ | C-O020 |
| D41 | 层/尾、罕见率、未随访与 0 次怎样分流？ | C-O003 C-O008 |
| D42 | 共同线性映射是否足以共享策略或效用？ | C-O004 C-O014 C-O015 |
| D43 | 比较关系能否保留冲突而不把结果合并？ | C-O004 C-O015 C-O018 |
| D44 | 一次兑现能否作为验证记录但不认证模型？ | C-O011 |
| E45 | 谁拥有 as-of 数据查询、快照和去重？ | C-O006 C-O021 |
| E46 | 同 `double` 输出来路有哪些禁止替换？ | C-O012 C-O015 C-O022 C-O025 |
| E47 | 存档格式是否独立于 ABI、模型和数据版本？ | C-O013 C-O021 |
| E48 | 哪些误差由共享核承担，谁负责验证不同域？ | C-O001 C-O014 C-O016 C-O022 C-O025 |
| NEW-A-001 | 发出快照与初/终兑现版本如何配对？ | C-O011 C-O021 |
| NEW-A-002 | 行动改变标签可见性时谁报告未知结局？ | C-O019 |
| NEW-A-003 | 评价工具如何表达连续监测条件？ | C-O011 |
| NEW-A-004 | 同名观测误差如何与定义迁移区分？ | C-O023 |
| NEW-A-005 | 共享权与风险协方差如何随样本归档？ | C-O005 |
| NEW-A-006 | 精确文本/表示阈值/政策误差谁验证？ | C-O014 |
| NEW-A-007 | 预测子集评分与全请求弃权成本如何共存？ | C-O019 |
| NEW-B-001 | 同预测集按球员或按打数的目标权选择归谁？ | C-O011 |

## 历史修复先例

| ID | 已解决证据及约束 |
|---|---|
| R01 | 大计数 logit Beta 与独立数值参考；后续分辨率/工具链议题另计。C-O001/C-O016。 |
| R02 | 精确文本中点与正零，`95fdd96`+ `2101b6b`；后续决策不能自动继承位级承诺。C-O014。 |
| R03 | `a085776` 的畸形前态与正 Gamma 可重入；保留状态和线程语义，发布点修订不重新归因。C-O013/C-O025。 |
| R04 | v1.0.0 正式标签和发行已完成；v1.1.0 Stable 只读定位。C-O022。 |

引入/修补/发行 SHA 详见[永久账本](../../TECHNICAL_DEBT.zh-CN.md)。本轮未把历史状态转换为新修复提案。
