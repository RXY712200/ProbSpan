# 真正复用、语义相似与隔离

[导航](README.zh-CN.md) · [26 项登记](overlap-register.tsv) · [事实与问题地图](current-state-and-evidence-map.zh-CN.md) · [风险](integration-risks-and-validation.zh-CN.md)

登记分 numerical（精确数学对象的内核）、mathematical（公式或条件似然）、engineering（验证/打包等边界）、separate（共用概念，结果或实现隔离）、unrelated（直接合并缺乏语义依据）。每行说明替代做法、反例与复用准入。TSV 的 ID 连到本页及[决定记录](decision-register.tsv)；`related_ids` 是问题，`evidence_ids` 是实际研究来源/实验。共享的输入表示、操作次序和误差预算与方程本身同样重要。

## 第一层有现实复用

- **已有的私有 EV 几何是正例（C-O004、C-O015）。** 对同一个事件的概率区间 [l,u] 与正总回报 o，线性单调映射给 [ol−1,ou−1]；补事件区间 [1−u,1−l]。该映射对多个区间解释都可成立，但其覆盖含义由输入决定。见 `ps_ev_interval` 和 `ps_complement_interval`。两条分析路径各自计算 S 或后验阈值质量；这两个结果既不从区间距离相互推出，也无需新增公共“通用分析器”。解析与裸分类皆已有不同前置条件，合并时不可搬移验证顺序。 [源码](../../../src/decision_geometry.c) · [现行行为](../../BEHAVIOR_SPEC.md)
- **Beta 核可以有第二个消费者（C-O001、C-O025）。** 对固定表示 a,b,x，积分正则化得到同一个 CDF；逆函数问题可约定尾、目标和邻点判据。现有实现是候选而非普适特函数承诺。Jeffreys 的添加半计数、选择 95% 中央区间和 readiness 仍属旧模型。若新形状跨越 .5，或要求极小尾相对精度、log-tail、不同舍入下稳定分类，先单独证明/测试；不扩张原私有函数的假定域。第二个合格消费者出现才承担共享的 ABI/内部契约传播成本。 [S0050](https://dlmf.nist.gov/8.17) · [B-E006](../phase-b/experiments-and-results.zh-CN.md#b-e006)
- **确定的文本输入也是有限复用（C-O014）。** ASCII、范围、ties-to-even 和结果位型共同定义 `probspan_odds_parse`。同约定的应用可调用安装函数；带指数、当地小数符或无限精度支付文字须另解析。把赔率文本转换共用到未声明语法的权重会形成兼容问题。若旧路径中 CDF 尾从 `1-CDF` 改为直接 survival，数学等价也需核对数值和状态差。
- **重用测试骨架，保留不同参考（C-O016、C-O024）。** 输入 manifest、确定 seed、结果版本和例程驱动可共享；参考值生成不能仅用被测后端。SciPy 与 Boost/Stan 的部分路径有依赖重合，不能按库名数“独立”票。不同后验、CIF、得分和观察集应有分开的 oracle 与样本检验。Linux 数字反例的严格与容差结果必须一起记录。 [Phase A 软件记录](../phase-a/real-world-and-software.zh-CN.md) · [B-E006](../phase-b/experiments-and-results.zh-CN.md#b-e006)

## 可复用公式，推断仍分离

C-O002/C-O026。共同 θ 下独立、无重叠的两个二项块的似然核可相乘，因此整数计数可相加；若模型固定不同 θ_j，则乘积保留各组指数，按总数坍缩会丢组间信息。固定幂权可用相同 log-likelihood 项，但有效形状分数不该塞进旧整数写法。混合后验的 CDF 是分量 CDF 的加权和，量化应先求混合逆，不是分位数加权。完整层级还需超参混合，经验 Bayes 则在拟合的超参条件下给结果；既有组预测与新组预测须分别留出。当前复用程度限公式/稳定 log-Beta 评估的潜在叶节点，没有共享 posterior object 的必要。 [S0006](https://onlinelibrary.wiley.com/doi/abs/10.1111/biom.12242) · [B-E002](../phase-b/experiments-and-results.zh-CN.md#b-e002) · [B-E007](../phase-b/experiments-and-results.zh-CN.md#b-e007)

C-O005/C-O008/C-O009。Σwₕpₕ 与合并行数只在明确总体/同参数条件下偶有数值相等。已知固定权且独立层时，Preview 的方差可按平方权相加；权和风险共估时该变换少掉协方差。同名风险若来自 survival 的 1−KM、竞争 CIF 或 recurrent exposure 强度，先问真实目标、分母及风险集。仅在业务已得到完整同义 horizon 标签时才可进入二项路径；丢失了时间的 e/c 无法恢复删失估计。另保留隔离分析，以便变更某个科学假设时不改其它模型。 [B-E003](../phase-b/experiments-and-results.zh-CN.md#b-e003) · [B-E004](../phase-b/experiments-and-results.zh-CN.md#b-e004)

## 可共用名称或收据，决策权留在各层

- **资格和可用性（C-O006、C-O007、C-O012、C-O020、C-O023）。** 机械比较端点、时间、已知身份及支持；声明可信程度由领域独立验证。同一观察的两个有效别名可以折叠，同一人的两个真实事件不能都当 alias，也不能直接当 iid。检查何时分样本需要已有簇、分层、抽样调查或复核标签。没有正支持或真实独立性证据，清晰的“未知”/界比共享 `VALID` 更有用。夹带真实标签的模拟输出仍不能冒充新证据。 [S0022](https://pubmed.ncbi.nlm.nih.gov/31649194/) · [B-E003](../phase-b/experiments-and-results.zh-CN.md#b-e003)
- **生命周期与验证（C-O011、C-O013、C-O019、C-O021）。** 发布时点、可用时点、成熟和修订版本都可用外部词汇，但查询、重放和验证取样是应用职责。如果训练端自动读评分库的“最新真值”，会因反馈形成逆因果依赖。评价程序接受已冻结的预测与明确版本的配对集合，单独给原始分母、可见覆盖、损失与监测规则。监测的 filtration 不能由一个时间戳字段自动实现。 [S0088](https://www.w3.org/TR/2013/REC-prov-o-20130430/) · [B-E005](../phase-b/experiments-and-results.zh-CN.md#b-e005)
- **主观、参数、预测和联合（C-O003、C-O010、C-O017、C-O018）。** CDF 数据结构不提供端点定义或受评群；主观 logit 宽度不能写成“95%”。同样当模型都输出 .4 时，两个同题预测不对应两个独立证据，两个不同事件的边际也不确定联合概率。保持输出对象及验证协议分别命名。 [Phase B 推导](../phase-b/derivations-and-counterexamples.zh-CN.md)

## 不抽象也是维护选择

两条模型分析器的少量状态提交和输入校验可故意局部重复，其 precedence 与错误可用性不同。将每个 `if` 放进一处构建高耦合 dispatcher 将扩大回归面。设备层的不同后验计算和 C 内核重复使用“+ .5”，但使用不同依赖、支持域、预算和输出；共用适配器并非共用推断。先度量一个具体第二用例的重复成本、稳定输入合同及引用独立性，再考虑共享；没有该证据时首选当前小规模实现。 [设备标准化](../../../integrations/device_history/standardization.py) · [C 历史求值](../../../src/historical.c)
