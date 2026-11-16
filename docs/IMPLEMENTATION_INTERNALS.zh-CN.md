# ProbSpan 内部数学、数值与职责边界

## 1. 基线与依赖方向

本篇审查 v1.0.0 源码 `fdfaddfb58486004ee1cc02c0f4a5c640cd17c7c`，日期 2026-11-16。配套：[导读](IMPLEMENTATION_WALKTHROUGH.zh-CN.md)、[API](IMPLEMENTATION_API_REFERENCE.zh-CN.md)、[验证](IMPLEMENTATION_VALIDATION.zh-CN.md)、[账本](TECHNICAL_DEBT.zh-CN.md)。现行边界由 [架构](ARCHITECTURE.md)、[行为规范](BEHAVIOR_SPEC.md)、[数值契约](NUMERICAL_CONTRACT.md) 和公共头共同约束。

依赖从组合/公共适配向模型与决策，再向数学原语流动；数值求解器不认识 UI、provenance 或产品工作流。源码的模块分工不是“一文件一种未来模型”的插件框架，而是围绕已存在的独立职责形成边界。

```text
analysis_composition.c → subjective.c / historical.c / odds.c
                      → subjective_analysis.c / historical_analysis.c
                      → decision_policy.c
subjective.c → subjective_input.h / probability_math.h / model_v1.h
historical.c → history_model_private.h / beta_private.h → beta.c
historical_analysis.c → history_model_private.h / decision_private.h / beta.c
subjective_analysis.c → decision_private.h / probability_math.h
decision_geometry.c ↔ decision_private.h → decision_policy.c 的分类原语
odds.c → decimal_private.h → decimal.c
beta.c → beta_logit.h / gamma_private.h
beta_logit.c → gamma_private.h
provenance.c → subjective_input.h（不调用计算组合器）
probspan.c → 公共头（ABI 查询）
```

上图 `↔` 表示声明与实现配合，不是两个编译模块的循环调用。私有头的函数声明、`ps_probability_interval`、辅助类型不安装，不构成 ABI。完整 14 C/9 H 文件地图见导读；这里展开各主要 helper 家族。

## 2. 冻结参数的权威位置

[model_v1.h](../src/model_v1.h) 集中定义行为参数；不能在调用处复制并修改一个“差不多”的版本。

| 家族 | 实值与含义 |
| --- | --- |
| `PS_SUBJECTIVE_VERSION`, `PS_HISTORY_VERSION`, `PS_HISTORY_GATE_VERSION`, `PS_ODDS_ANALYSIS_VERSION` | 分别为 1，分别对应结果中的模型/gate/分析版本 |
| `PS_STATS_VERSION` | 1，冻结参考常量之一，不是新的公共版本接口 |
| `PS_FLOAT_EPSILON` | 1e-12，决策分类边界，不是 Beta 积分误差 |
| 主观 p 节点 | MIN=.01，LOW=.45，MID_HIGH=.55，HIGH=.85，VERY_HIGH=.95，MAX=.99 |
| 主观因子 | LOW=1.5，MID=2，HIGH=1.4，MAX=1.2，先取自然对数 |
| Jeffreys / gate | alpha=beta=.5，可信水平 .95，最小 n=20，最大宽度 .25 |

Beta 求解阈值与十进制表示常量分别留在数值模块，因为它们是求值算法参数，不是主观/历史模型选择。改数值算法必须保持现行模型与 [容差](../oracle/numerical_policy.json)，不能借修数值悄悄改先验。

## 3. 主观输入与分段区间

[subjective_input.h](../src/subjective_input.h) 的 `ps_valid_raw_percent` 验证整数 0..100；[subjective.c](../src/subjective.c) 保存 raw，clamp used 至 1..99，令 p=used/100。

定义 `L=log(1.5), M=log(2), H=log(1.4), X=log(1.2)`，半宽为：

```text
p <= .45          : L
.45 < p < .55     : fraction=(p-.45)/(.55-.45); L + fraction*(M-L)
.55 <= p <= .85   : M
.85 < p < .95     : fraction=(p-.85)/(.95-.85); M - fraction*(M-H)
.95 <= p <= .99   : fraction=(p-.95)/(.99-.95); H - fraction*(H-X)
```

最后一段包括 .95；分段在节点连续，但分支归属与 binary64 求值次序仍是兼容性事实。[probability_math.h](../src/probability_math.h) 的 ps_logit 使用 `log(p/(1-p))`；subjective.c 的私有 logistic 使用 `1/(1+exp(-z))`，上下界为 logistic(logit(p)±d)。即使另一种 log1p 写法代数等价，也不应未经回归就替换冻结求值顺序。直接 half_width 的 p 必须在 [0.01,0.99]；它不执行 clamp。NaN 比较不能通过域检查。

## 4. 历史后验、表示与 gate

[history_model_private.h](../src/history_model_private.h) 的 `ps_history_shapes` 共用 `a=(double)e+.5,b=(double)c+.5`。`historical.c` 在验证非负后先转 `uint64_t` 再求和，最大 2*INT64_MAX，不发生有符号溢出。n=0 成功返回无估计，但仍保留输入、状态和版本。

n>0 的中心按源码计算 `((double)e+.5)/((double)n+.5+.5)`，而不是先构造 a+b 再除；极大数时两种代数写法可能不同。区间两端调用 Beta 分位数，尾概率按 `(1-.95)/2` 求值；不要将其强行替换成另一个浮点字面量而假定逐位相同。两端都成功后 `n>=20 && upper-lower<=.25` 决定 VALID。gate 不检验去重、抽样偏差、条件漂移或观察独立性。

int64 计数精确保存，但超过 2^53 时转 double 不能逐个表示整数，`.5` 也可能被吸收。这是模型求值的 binary64 表示条件，不是允许偷偷截断输入计数的理由。实际极端参考区分精确计数后验分位数与 CDF 的已表示 binary64 参数，详见验证篇。

## 5. 普通 Beta 路径

[beta.c](../src/beta.c) 的 `ps_beta_cdf`/`ps_beta_quantile` 为私有成功/失败接口；公共层将失败映射到 NUMERICAL_FAILURE，并保持输出。正有限 a,b 与概率边界是内部前提。

CDF 先拒绝非有限或超出 [0,1] 的 x 及非正/非有限形状，再对恰好 x=0/x=1 返回 0/1；内部以正参数 log-Gamma 构成归一化 log-front，选择 `x<(a+1)/(a+b+2)` 的直接或反射支路，减少不利尾区求值。Lentz 连分数上限 20000 次，相对收敛阈值 `8*DBL_EPSILON`；过小分母以 `DBL_MIN/DBL_EPSILON` 保留负值符号（零取正小量），避免除零而不能无条件改成正小量。结果限幅到 [0,1]。

普通分位数使用 [0,1] 二分，最多 200 次；当中点等于端点时表明表示区间不再可分，可成功退出。不是所有分位数都以 CDF 残差达到某个统一阈值停止；不得把这种浮点邻接停止改述为无限精度逆函数保证。概率端点 0/1 单独处理。a,b>=.5 且 a+b>10000 时派发到 transformed-logit；这不是正态近似切换。

## 6. 正参数 Gamma 与可重入性

[gamma.c](../src/gamma.c) 的 `ps_log_gamma_positive` 与 `ps_stirling_remainder` 专用于正参数归一化。参数低于 8 使用 log(tgamma)，较大参数用 Stirling 主项与到 z^-17 的余项；z>=8 时下一省略项低于约 1e-17。`gamma_private.h` 保存共享归一化定义。

避免 `lgamma` 的原因是一些平台实现通过共享 `signgam` 暴露符号状态；模型只需正参数，没必要引入这一共享状态。这里的修复不是通用复数/负参数 Gamma 库，也不意味着宿主所有数学函数和浮点环境都已审计。不要因“标准库已有 lgamma”就恢复旧问题。

## 7. 大计数 transformed-logit 求解

[beta_logit.c](../src/beta_logit.c) 保留真实 Beta 密度，在标准化 logit 坐标积分；不是把 Jeffreys 后验换成 Gaussian。令 c=a/(a+b)，s=sqrt(1/a+1/b)，u=logit(c)+s*t，x=logistic(u)。变换后 log 密度包含 `a*log(x)+b*log(1-x)-log B(a,b)+log(s)`，因为 dx/du=x(1-x)。直接展开大项再相减会丢掉中心附近的小曲率，源码采用补偿形式。

| helper 家族 | 维护要点 |
| --- | --- |
| `sum_roundoff`、`make_density` | 保留 a+b 加法误差、中心舍入误差；用 fma 保留 `a-c*(a+b)` 的残差；`logit_density` 携带 alpha、sum、center、center_roundoff、scale、log_density_at_zero |
| `log1p_minus_x`、`expm1_minus_x` | abs(x)<.125 用至多 40 阶的级数保留二阶小量，防止 log1p(x)-x/expm1(x)-x 消差 |
| `density_at` | 将线性大项的抵消提前代数处理，保留局部密度变化；不能改回分别计算巨大 log-Gamma 再相减 |
| `gauss_panel` | 16 点 Gauss-Legendre，存 8 个正节点及权重，利用对称性 |
| `adaptive_panel`、`integrate` | 比较整面板与两半面板，误差预算随细分分配；面板宽度 2，总绝对预算 2e-14，递归深度上限 12 |
| `transformed_cdf` | 对较近尾部积分，t 截至 ±64；针对 a,b>=.5 的变换尾界小于 1e-19，不能推广到任意形状参数 |
| `centered_difference`、`ps_beta_logit_cdf` | 以乘法残差保留 x-c；a>b 时反射；abs(delta)<.1*c*(1-c) 用 log1p 形式，远处用对数比，最后标准化 |
| `probability_at` | 中心附近通过 expm1 与 center_roundoff 回映射，远处选避免抵消的乘法表达式 |
| `ps_beta_logit_quantile` | 标准化 bracket [-64,64]；安全 Newton 候选越界/无效则二分，反射处理参数交换 |

分位迭代最多 100，CDF 残差阈值 2e-14，bracket 相对阈值 `8*DBL_EPSILON`；这些是算法停止标准，不等于公共 1e-10 Beta 对照容差。整/半面板差是实际采用的自适应误差估计，不是对所有输入的形式化全局误差证明。所有上限都是维护边界：失败向上返回，不能不收敛时交出貌似合理的值。

极大平衡参数下，邻接 double 的 x 可跨过可观后验质量。要求 `CDF(quantile)==q` 在表示上可能不可能；应检查邻接点夹住目标概率，并保留 [Issue #5](https://github.com/RXY712200/ProbSpan/issues/5) 的研究限制。`1-x` 自身舍入也会影响互补恒等式；测试不能把不同实数输入误当完全互补。跨架构/浮点环境边界见 [Issue #6](https://github.com/RXY712200/ProbSpan/issues/6)。

## 8. 精确十进制转换的架构

[odds.c](../src/odds.c) 先检查完整字符串文法，再调用私有 [decimal.c](../src/decimal.c) `ps_decimal_to_binary64`。私有转换前提是合法非负十进制文本；它不是另一个公开的宽松 parser。

实现静态断言基数 2、53 位尾数与 binary64 指数范围。`decimal_view` 保存原字符串视图与十进制位置，不将任意长输入拷入固定小缓冲。`view_decimal` 跳过无意义前导零，并以可证明的十进制数量级提前识别过大或极小值；MAX_DECIMAL_POSITION=309、324 个前导小数零等是表示边界，不是字符串长度上限。

`decode_finite` 将非负有限编码还原为 significand*2^exponent。相邻 binary64 的中点写成 `(2*significand+1)*2^(exponent-1)`，包括正规/次正规以及溢出边界。`compare_midpoint` 用 base=10^9 的 86 个 limb 构建中点的精确十进制系数，乘 2 或乘 5 处理二进制指数；774 位中点容量来自 binary64 表示范围，不限制输入总长度。

`integer_from_uint64`、`multiply_small`、`decimal_digits` 只维护该中点整数；先比十进制位置，再逐位比输入，后续很远的非零尾数仍会影响恰中点判定。因此不能以“前 17 位足够往返”丢弃其余输入。编码空间在 0 与 `0x7ff0000000000000`（正无穷）间二分；在精确中点时按编码奇偶 ties-to-even。

`value_from_encoding` 对零明确返回 +0，对无穷单独返回，其余由精确整数 significand 与 ldexp 构造。这样避免向下舍入时计算负表达式意外产生 -0。不能改成逐个十进制数位做 double 乘加，也不能借 strtod 的 locale/舍入环境改变已发布语义。运行时不 malloc；测试 `stream_vectors` 的 realloc 只是开发输入 harness。

## 9. 几何、策略与分析适配

[decision_private.h](../src/decision_private.h) 的内部 `ps_probability_interval` 只有 center/lower/upper；`ps_valid_probability_interval` 验证有限、有序、[0,1]。`ps_validate_odds_pair` 固定先事件后补事件。`ps_complement_interval` 将 center→1-center，端点→1-upper/1-lower。

[decision_geometry.c](../src/decision_geometry.c) 的 `ps_ev_interval` 对三个概率求 q*O-1，乘积经 volatile 中间值保留分离乘减，防止编译器融合 FMA 改变冻结结果。`ps_odds_geometry` 构造两个坐标系中的阈值与倒数和；只有分类策略依赖 epsilon，不应在几何层再复制阈值规则。

[decision_policy.c](../src/decision_policy.c) 的 `ps_ev_state` 用严格端点不等式；公开 classify_ev 不检查端点有效性。`ps_odds_combination` 先临界带再 overlap。模型关系只比较三个合法 EV 状态，历史不可用时忽略其枚举，无可用历史优先于跨阈值。

[subjective_analysis.c](../src/subjective_analysis.c) 对合法估计计算两侧 EV，S=(logit(q)-logit(1/O))/d，其中 q 是对应事件/补事件中心，d 保留原主观半宽，不重新把补事件 p 送入非对称分段宽度。赔率 1 时阈值 logit(1) 不有限，故标记 S 不可用，但 EV 正常返回。不能通过给 odds 加 epsilon 来制造可用 S。

[historical_analysis.c](../src/historical_analysis.c) 先检查 state，非 VALID 立即输出 unavailable，早于赔率和概率字段检查。VALID 才构造几何与 shapes。`posterior_probability` 调私有 CDF 并按事件侧 1-CDF、补事件侧 CDF 返回，限幅 [0,1]。先在局部对象求完两侧；任一失败整次不提交。输入估计对象只做局部完整性检查，不重新认证版本、gate 或来源。

## 10. provenance、组合与输出提交

[provenance.c](../src/provenance.c) 先检查指针和旧状态不变量，再检查两个 raw。令 E=old exposed，C=old compromised，N=now，R=subject_changed OR raw_changed，则 `E'=E OR N`，`C'=C OR (E AND R)`。新暴露不倒因果地影响同一操作；显示请求不是暴露事实。用局部结果支持 previous/result 别名；无重置入口。

[analysis_composition.c](../src/analysis_composition.c) 完整委托估计、赔率、分析、分类，只有末尾写 `*result`。此边界保证各输入错误优先级与不交付半成品；不要复制单项算法到组合器，否则未来数值修复会出现两套规则。[probspan.c](../src/probspan.c) 独立返回 ABI=1，不参与模型派发。

## 11. 症状到不变量的排查表

| 症状 | 首查源与不变量 | 对应测试 |
| --- | --- | --- |
| raw 0/100 报错或被丢失 | subjective、subjective_input；raw 与 used 分离 | oracle_parity `check_subjective` |
| n 大时溢出/区间 NaN | historical 无符号求和、beta_logit 补偿与上限 | large_numerics `check_stress` |
| 中点十进制末位不符/-0 | decimal 精确尾数比较、value_from_encoding | decimal_parity `check_vectors` |
| 补事件 EV 上下反转 | decision_geometry 反向端点映射 | analysis_parity `check_ev` |
| S 不对称或赔率 1 异常 | subjective_analysis 保留原 d、可用性 | analysis_parity `check_subjective` |
| 无历史遇坏赔率报错 | 单历史分析短路 vs 组合器仍需主观赔率 | analysis_parity `check_arguments`、api_contract |
| 首次暴露即 compromised | provenance 使用旧 E，不使用 E' | state_parity `check_provenance` |
| 失败后部分字段更新 | 局部对象到最终提交路径 | state_parity、api_contract 的 unchanged 检查 |

## 12. 维护要求

公共 API/字段、行为、内部调用、数学/数值、校验错误、测试/夹具、CMake、平台、版本/兼容性/发布行为改变时，在同一分支/PR 更新四指南、权威契约、README 和账本；改写过时段落并区分历史，不叠加矛盾描述。审查头文件对齐、真实断言和模型批准边界；无文档影响要说明。绿色测试不证明解释准确，文字政策不等于 CI 自动强制。问题 ID 不删除/复用，解决记录提交、验证、版本、剩余限制，拒绝/延期保留理由；提案及版本发布必须另获所有者批准。见 [CONTRIBUTING](../CONTRIBUTING.md)。
