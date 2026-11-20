# ProbSpan 内部数学、数值与职责边界

## 1. 基线与依赖方向

v1.1.0 沿用候选版的打包方式，并调整产品标识与消费版本校验；ABI、模型及数值实现沿用 v1.0.0。见 [兼容说明](COMPATIBILITY.md)。

本篇审查 v1.0.0 源码 `fdfaddfb58486004ee1cc02c0f4a5c640cd17c7c`，日期 2026-11-16。配套：[导读](IMPLEMENTATION_WALKTHROUGH.zh-CN.md)、[API](IMPLEMENTATION_API_REFERENCE.zh-CN.md)、[验证](IMPLEMENTATION_VALIDATION.zh-CN.md)、[账本](TECHNICAL_DEBT.zh-CN.md)。现行边界由 [架构](ARCHITECTURE.md)、[行为规范](BEHAVIOR_SPEC.md)、[数值契约](NUMERICAL_CONTRACT.md) 和公共头共同约束。

依赖从组合/公共适配向模型与决策，再向数学原语流动；数值求解器不认识 UI、provenance 或产品工作流。源码的模块分工不是“一文件一种未来模型”的插件框架，而是围绕已存在的独立职责形成边界。

合并的 [Preview 设备历史参考](PREVIEW_DEVICE_HISTORY.zh-CN.md) 引入独立调用方依赖图：`evidence.py` 只用 Python 标准库，筛选后返回计数或不可用回执；`v1.py` 通过有时限的子进程调用 `v1_consumer.c`，后者只链接已安装的公共 C 档案；`standardization.py` 使用 NumPy/SciPy 完成等质量分箱的 CDF 包络。两条估计路径从已审查的回执出发，Python 无需调用 C 私有 Beta。标准 C 构建、公共头和 CMake 导出均不依赖此目录。测试才借用 Phase II 生成器重放 mix-shift；独立的有理数矩和直接积分另外核验。v1 Beta、十进制转换与 provenance 的下列实现事实仍按原源码基线解释。

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

<a id="helper-atlas"></a>

## 12. 私有函数图谱：从公共边界向下定位

下面列出生产源码中实际有函数体的 helper；同名头声明不是另一份实现。表格的前提由上层校验建立，不能把 static helper 直接链接成公共 ABI。`model_v1.h` 没有函数，负责参数与版本；`beta_private.h/beta_logit.h/decimal_private.h/gamma_private.h/decision_private.h` 定义私有可调用边界，另外三个小头定义 inline 原语。测试简称对应验证篇的真实源文件。

| helper / 定义位置 | 输入→输出及调用方向 | 实际责任、关键分支/不变量 | 验证入口 |
| --- | --- | --- | --- |
| `ps_valid_raw_percent` / subjective_input.h | int32→bool；subjective/provenance 调用 | 0<=raw<=100，不做 clamp；provenance 比较 raw 而非 used | oracle_parity、state_parity |
| `ps_logit` / probability_math.h | p→log(p/(1-p))；subjective、analyze_side | 调用者保证通常的主观中心在 (0,1)；本身不返回状态 | oracle_parity、analysis_parity |
| `logistic` / subjective.c | z→1/(1+exp(-z))；estimate 调用 | 正常主观模型 z 有限，保留冻结求值式；无专门求解循环 | check_subjective |
| `ps_history_shapes` / history_model_private.h | 两个 int64 与两输出指针→double a/b | 显式转 double 后加 .5；历史估计和历史阈值分析共用 | check_history、check_reference |
| `use_logit_integration` / beta.c | a/b→bool；两个 Beta 入口 | a,b 均>=.5 且 sum>10000 才切换；不是后验模型选择 | large_numerics |
| `nonzero` / beta.c | double→tiny floor 后 double | abs(v)<tiny 才替换；负值取负 tiny，±0 比较不负，取正 tiny | 普通 CDF parity，非每个符号值的独立专测 |
| `beta_fraction` / beta.c | a/b/x 与输出→bool | 两半步 Lentz，c/d/fraction/delta 的含义见下节 | check_beta_cdf |
| `ps_beta_cdf` / beta.c | x/a/b/out→bool | 完整私有域校验、端点、派发、反射、有限性与限幅 | oracle_parity、large_numerics |
| `ps_beta_quantile` / beta.c | q/a/b/out→bool | 校验与端点后派发，普通二分以邻接停止 | check_quantile_bracket |
| `ps_log_gamma_positive` / gamma.c | 正参数→log Gamma | <8 用 log(tgamma)，否则 Stirling；不是任意实数 Gamma 接口 | 两 Beta 路径的归一化回归 |
| `ps_stirling_remainder` / gamma.c | z>0→小余项 | z<8 从 log Gamma 减主项；较大用 inverse/square 多项式 | 同上，间接验证须如实标注 |
| `sum_roundoff` / beta_logit.c | a/b/已算 sum→被丢掉的低位 | caller 提供与 a+b 对应的 sum，返回浮点补偿，不调用扩展精度 | large_numerics |
| `log1p_minus_x` / beta_logit.c | x→log1p(x)-x | 小量保留二阶项，n=3..40 或相对项足够小即停 | large_numerics 的极窄密度 |
| `expm1_minus_x` / beta_logit.c | x→expm1(x)-x | 小量从 x²/2 开始递推，避免差值归零 | 同上 |
| `make_density` / beta_logit.c | a/b→logit_density 值 | sum/center/roundoff/scale/normalizer 一次构造，无分配 | large_numerics、修正阈值 |
| `density_at` / beta_logit.c | density,t→密度 | abs(displacement)/abs(weighted) 任一个小于 .125 用消差式；否则直接差 | 同上 |
| `gauss_panel` / beta_logit.c | density,lower,upper→积分 | 8 对节点共 16 次密度调用，按半宽映射 | 同上，无独立全函数域形式证明 |
| `adaptive_panel` / beta_logit.c | panel,tol,depth,out→bool | 非有限失败；先接受误差再判深度上限；预算分半递归 | large_numerics |
| `integrate` / beta_logit.c | density,lo,hi,out→bool | 宽度<=2 的串行面板；按长度分配容差；首次失败停止 | large_numerics |
| `transformed_cdf` / beta_logit.c | density,t,out→bool | 截尾或近尾积分；t<=0 积左尾，否则 1-右尾 | check_complement、check_reference |
| `centered_difference` / beta_logit.c | x/a/b→补偿 x-a/(a+b) | 两个乘积残差+加法残差，不依赖 long double | 极大 CDF/邻接夹逼 |
| `ps_beta_logit_cdf` / beta_logit.c | 已验证 x/a/b/out→bool | a>b 反射；delta 中心形式或对数比，转标准化 t | large_numerics |
| `probability_at` / beta_logit.c | density,t→x | abs(expm1(displacement))<.125 加小偏移和 center_roundoff；否则乘法式 | 极窄分位/反射回归 |
| `ps_beta_logit_quantile` / beta_logit.c | 已验证 q/a/b/out→bool | 反射、残差/bracket 停止、安全 Newton 或二分、迭代上限 | check_quantile_bracket |
| `valid_decimal_syntax` / odds.c | 非 NULL NUL 字符串→bool | 三标记扫描 ASCII，完整词法先于数值解析 | check_odds |
| `integer_from_uint64` / decimal.c | uint64→decimal_integer 值 | do/while 至少一个 limb，零有规范表示 | check_vectors 经转换路径 |
| `multiply_small` / decimal.c | integer*,factor→原地整数 | base 10^9，uint64 保存 product+carry，进位扩 limb | 同上 |
| `decimal_digits` / decimal.c | integer→调用者 digits/count | 最高 limb 不补零，低 limb 固定 9 位；返回长度不写 NUL | 同上 |
| `view_decimal` / decimal.c | 合法文法字符串→视图 | first_digit 借用输入，position 有界；零/证明下溢用 NULL | decimal_parity、差分工具 |
| `decode_finite` / decimal.c | 非负有限 encoding→significand/exponent | 次正规无 hidden bit；正规加 2^52，偏置/位数分开 | exact-bit 向量 |
| `compare_midpoint` / decimal.c | 视图、下编码→-1/0/1 | 精确整数中点、位置/数字/远尾比较；不 float 累计 | exact-bit/远端扰动 |
| `value_from_encoding` / decimal.c | 最终编码→double | 0、infinity 单独；其余整数+ldexp 精确构造 | 四舍入模式、+0 向量 |
| `ps_decimal_to_binary64` / decimal.c | 合法文本→double | 零/溢出提前返回，否则中点二分；相等按奇偶 | decimal_parity |
| `ps_valid_probability_interval` / geometry | interval→bool | finite 且 0<=lower<=center<=upper<=1 | check_arguments |
| `ps_complement_interval` / geometry | interval→interval | 端点倒序，不重新估计模型 | check_ev/check_subjective |
| `expected_value` / geometry | q/O→double | volatile product 后减 1，冻结乘减分离 | epsilon 边界 parity |
| `ps_ev_interval` / geometry | interval/O→public ev 值 | 先在独立语句算端点，返回初始化器分别算中心与分类；不依赖两者先后 | check_ev |
| `ps_validate_odds_pair` / geometry | Oe/Oc→status | 先事件再补事件，公共数值校验复用 | check_arguments |
| `ps_odds_geometry` / geometry | 已验证两赔率→geometry | 两概率坐标、倒数和分类 | check_geometry |
| `ps_ev_state` / policy | minimum/maximum→枚举 | 严格 epsilon，min 分支优先，无数值校验 | check_classifiers |
| `ps_odds_combination` / policy | inverse_sum→枚举 | 临界优先，再 overlap，再双正窗口 | check_classifiers |
| `valid_ev_state` / policy | 枚举→bool | 只接受三个命名值；历史不可用时不调历史校验 | api_contract 枚举案例 |
| `analyze_side` / subjective_analysis | interval/d/O/threshold→side 值 | EV 总算；O==1 仅禁用 S，否则有符号 logit 差/d | check_subjective_side |
| `posterior_probability` / historical_analysis | threshold/a/b/event_side/out→bool | CDF 失败传播；事件 1-CDF、补事件 CDF；限幅 | check_historical_side、修正阈值 |

输入检查只在职责所在层做。beta_logit 的两个私有入口依赖 beta.c 先排除非法形状与端点；直接从测试/应用越过 beta.c 传入任意参数不构成支持路径。小头 inline 并不自动安全验证输出指针，前提由所属公共函数建立。

<a id="ordinary-beta-steps"></a>

## 13. Lentz 两半步与普通逆函数，怎样逐步排错

`beta_fraction` 的 c/d 是连分数更新的中间比值，fraction 是累计乘积；它不是原始 Beta CDF，CDF 的 front 和除 a/b 在 caller 才加入。初始化 `sum=a+b`、`a_plus_one=a+1`、`a_minus_one=a-1`，c=1，d=1/nonzero(1-sum*x/(a+1))，fraction=d。

第 m 次迭代执行两种系数（代码保持乘除次序）：

```text
m2 = 2*m
term1 = m*(b-m)*x / ((a-1+m2)*(a+m2))
d = 1/nonzero(1+term1*d)
c = nonzero(1+term1/c)
fraction *= d*c
term2 = -(a+m)*(a+b+m)*x / ((a+m2)*(a+1+m2))
d = 1/nonzero(1+term2*d)
c = nonzero(1+term2/c)
delta = d*c
fraction *= delta
```

第二半步后检查 fraction 有限，随后 `abs(delta-1)<=8*DBL_EPSILON` 成功；达到第 20000 次仍不满足则 false。不能只看 fraction 的绝对大小来判收敛，CDF 尚未归一化。tiny 防除零不是任意改变分布的参数，不能当 gate 调整。

CDF 的 log-front 是 `logΓ(a+b)-logΓ(a)-logΓ(b)+a*log(x)+b*log1p(-x)`；小 x 侧返回 exp(front_log)*fraction/a，另一侧交换 a/b、x→1-x 后返回 1-exp(front_log)*fraction/b。相等 `x==(a+1)/(sum+2)` 走反射侧；结果非有限失败，有限结果最后 clamp。x 超出 [0,1] 在派发前拒绝，而不是 clamp 输入。

普通 quantile 从 [0,1] 取 `middle=lower+(upper-lower)/2`，先检查 middle 是否已等于端点，再查 CDF；若 CDF<q 更新 lower，否则更新 upper。q=0/1 在前面单独成功，NaN/非法形状先失败。最大 200 次并不意味着所有 q 的 CDF 残差都达 1e-10；成功邻接返回是表示空间终止。复现普通路径可从历史 19/1 开始，先检查 a/b、switch=false，再看迭代端点，不必直接跳进大计数积分器。

<a id="logit-detail"></a>

## 14. transformed-logit 的补偿、积分与分位逐层展开

### 14.1 先区分模型常数与坐标补偿

`make_density` 中 center 是舍入的 a/(a+b)，center_roundoff 是保留的除法/求和低位，scale=sqrt(1/a+1/b) 使 t 的有效宽度为普通量级。normalizer 从 Stirling 余项直接构造，不形成三个巨大的 log Gamma 再相减。`sum_roundoff` 用 `b_part=sum-a` 分离两个操作数在 sum 中被吸收的部分；其多个 caller 必须传入对应的 rounded sum。

在 `density_at`，令 v=scale*t，z=expm1(v)，w=center*z。直接写差值 `a*v-sum*log1p(w)`，线性大项接近抵消。小量支路利用 sum*center≈a 消掉线性项，计算 `-a*expm1_minus_x(v)-sum*log1p_minus_x(w)`。这两个小函数分别从 ±x²/2 开始，递推到 n=40 或 `abs(term)<=DBL_EPSILON*abs(sum)`。支路是 **abs(v)<.125 OR abs(w)<.125**，不能改成 AND；调用时可能位移不小而极偏斜中心使 weighted 很小。

### 14.2 积分单元、预算和失败传播

gauss_panel 将 [lo,hi] 映射到中心 middle、半宽 half_width，累加 8 个正节点的左右密度乘权重，再乘 half_width。adaptive_panel 每次算 whole 和两个 halves，成本是本次三个 16 点 panel；若 halves 非有限失败，若差<=tolerance 成功交 halves，之后才检查 depth==12。故在最大深度上达到误差标准仍可成功，不能把“进入深度12”误写成无条件失败。

integrate 每次 end=min(upper,lower+2)，tol=2e-14*(end-lower)/原总长度，面板失败立即返回 false；递归时 tol/2。lo==hi 时 while 不执行，积分 0；因此不会执行零长度除法。transformed_cdf 对 t<=-64 或 t>=64 直接 0/1；其余 t<=0 积左尾，t>0 用 1 减去右尾积分（1-integral，不能反向相减）。尾界只适用派发保证的 shapes>=.5；这是源码的分析前提与参考验证范围，不是对任意用户新分布的通用截尾定理。

### 14.3 x 到 t 与 t 到 x 的不对称难点

`centered_difference` 先算 ax=a*x、bx=b*x，用 fma 分别取乘法残差，加上 ax+bx 的求和残差；再对 `(ax+bx)-a` 取减法残差，最后除 sum。这比直接 x-rounded(center) 保留更多有效信息，尤其在 x 的一个 ulp 跨越大量后验质量时。

CDF 先在 a>b 时递归交换形状并反射 x，最多一次交换。近中心 `abs(delta)<.1*c*(1-c)` 时用 `log1p(delta/c)-log1p(-delta/(1-c))`；否则用对数比。这个 delta 表示补偿后的 x-c，而不是将两个 rounded 概率随意相减。

quantile 也先反射到 a<=b，再用 t=0、[-64,64] bracket。每次先求 cdf、检查 residual 或 bracket 标准；不满足才更新 bracket，尝试 `candidate=t-residual/density_at(t)`。候选有限且严格在更新后的开区间内才采用，否则取中点；最多100次。`probability_at` 在 abs(expm1(v))<.125 时先加 offset+center_roundoff 再加 center，远处用 center*exp(v)/(1+center*expm1(v))，避免接近端点的抵消。这里既需要中心补偿，也需要最终 x 的邻接测试，单看 t 收敛不足以证明最终 x 能精确实现目标质量。

<a id="decimal-detail"></a>

## 15. 十进制从词法状态到编码二分

### 15.1 词法与归一化视图不能混为一层

valid_decimal_syntax 的 fractional、digit_before_dot、digit_after_dot 三个布尔量记录是否进入小数段、点前是否有数字、点后是否有数字。空串立即 false；点只能出现一次且点前已有数字；非 ASCII 0..9（含空白、指数符号、全角数字）立即 false；末尾有点无小数数字也 false。先扫描完整输入，故一个很长的前缀看似溢出，但末尾有 x，公共结果仍为 ODDS_SYNTAX，而不是先溢出返回 ODDS_RANGE。

view_decimal 只在文法已合法后运行。first_digit 指向输入首个有效非零位，position 表示有效数值的十进制位置：`12.5→2`、`0.0125→-1`。若首段有>=310个有效整数位则 position>309 足以证明 binary64 溢出；若小数中先见>=324个零再有非零位，则值低于最小次正规数的一半，可以转换为 +0。普通零也用 first_digit=NULL 表示。这个 NULL 不是错误状态，不等于公共 parser 的 NULL 参数。public odds 对 +0 再报范围错误，保持旧输出。

### 15.2 中点整数与流式全尾比较

decimal_integer 是小端 base 10^9 limbs，used>=1。integer_from_uint64 通过反复除 base 构造；multiply_small 的 product 用 uint64 避免 limb*5/2+carry 溢出 uint32。decimal_digits 顶 limb 不补零，其余每个恰9位，返回 count 而不依赖 NUL。86 limbs/774 字符容量覆盖 binary64 中点的最多768位系数，不覆盖输入长度，二者不能交换解释。

decode_finite 对 field=0 给 exponent=-1074 且无隐藏位；正规为 `(field-1023-52)` 幂并补 hidden bit。compare_midpoint 先 exponent--，系数为 2*significand+1；负指数乘5^(-e)并把小数位计入 position，非负指数乘2^e。先比较 position，若相等则逐位比较完整数值，输入提前结束当补零；匹配中点位数后仍扫输入尾部，任何远端非零使输入严格大于中点。没有“读取17位后忽略剩余”的捷径。

例：1 与其后继的中点是 `1.00000000000000011102230246251565404236316680908203125`。相等时编码下端为偶数，舍入到 1；同串很远处再增加一个正的末位则选后继。十进制本身略小于1但舍入到1仍可通过公共范围；数学实数范围判断和 binary64 后判断不能混淆。

### 15.3 二分、下溢、上溢与舍入方向

正有限编码按数值有序，ps_decimal_to_binary64 在 [0,positive infinity encoding] 搜索舍入单元边界。comparison<0 收缩 upper=middle，>0 令 lower=middle+1，恰中点选 `middle+(middle&1)`，奇下端向上取偶。编码最大有限值和溢出结果之间也用同一中点规则，不先把输入 clamp 为 DBL_MAX。

value_from_encoding 零明确返回 0.0，无穷返回 INFINITY，其余 significand 可精确转 double，再以 ldexp 作精确可表示的二进制缩放。测试中的四舍入模式改变调用环境，但这条构造不依赖逐位浮点十进制累计；+0 分支专门避免某些 Clang unsigned 转换在 FE_DOWNWARD 下通过抵消构造出 -0。输入不能带负号，所以 -0 文本是词法错误，而不只是范围错误。

<a id="composition-detail"></a>

## 16. 决策 helper、provenance 与组合的提交边界

`ps_valid_probability_interval` 以有限、有序、[0,1] 检查模型结果的共用数值外壳。subjective analyzer 额外要求 center 严格在(0,1)和有限正 d；historical analyzer 对 VALID 还要求 has_estimate 和非负原计数，但允许中心端点，也不重算 sample_size/版本/gate/均值。不能将这些局部断言描述为“认证调用者对象来自原模型”。

expected_value 中 volatile gross_return 冻结先乘后减；ps_ev_interval 先在两个独立语句得到 lower/upper 的 EV，再在返回结构初始化器中计算中心EV与纯分类。C 不保证这两个初始化表达式按文字顺序求值；它们无相互副作用，文档不能据排版声称“中心先于分类”。valid_ev_state 只接受三个枚举，关系分类不接收任意整数代号；unavailable 时历史输入枚举忽略。`analyze_side` 的 has_robust_margin 取 odds!=1，S 的正负对应中心超过/低于该侧 break-even，补事件 d 仍是原始 d，不能再调用 width(1-p)。`posterior_probability` 的 event_side 决定 1-cdf 还是 cdf；event mass 的尾部相减可能损失非常小质量，契约是既有绝对+相对容差，不是任意尾概率相对精度保证。

provenance 先读完整旧值并形成局部 next，再赋 *result；这是支持同一对象别名的具体原因。非法 predecessor 在任何 raw 检查前失败，不能自动“修好 exposed”再继续。compose 用一个局部 analysis={0}；每个委托失败立即 return，只有最后一次整体赋值交新结果。历史 unavailable 时关系用条件表达式选择占位，绝不读取不可用的 ha side。失败保持不是外部事务：如果应用在调用前已经改数据库或 UI，本库不会回滚那些副作用。

<a id="cost-and-change"></a>

## 17. 成本、失败定位与不能随意“简化”的实现

| 路径 | 资源/复杂度（源码推导，不是性能测量） | 出现问题先记录什么 |
| --- | --- | --- |
| 主观、几何、policy、provenance | 固定数量标量运算，无动态分配；含 libm 延迟 | raw/used、d 节点、EV 端点与 epsilon、旧 exposure |
| 普通 Beta CDF/quantile | 单 CDF 最多20000连分数迭代；quantile 最多200次调用；固定局部存储 | a/b/x、反射支路、delta、iteration、front |
| transformed CDF | 最多128宽度范围内的宽<=2面板；每 panel 自适应树最大深度12，栈深有界但工作量不小 | t、哪侧尾、panel边界、tol/depth、whole/halves 是否有限 |
| transformed quantile | 最多100轮，每轮调用积分并可能额外求密度；有一次参数反射 | residual、bracket、candidate 是否越界、最终 x 邻接 |
| 十进制 | 文法 O(L)；编码搜索至多约63次精确中点比较；整数容量固定，输入尾扫描可反复发生 | 文法最早坏字符、position、mid编码、比较相等/远尾、最终位型 |
| 组合 | 上述委托成本之和，一份局部聚合对象；无历史不调用 Beta | 首个错误状态与已执行委托，不读半成品 |

积分上限是防止无界求解的保护，不是硬实时期限；常数上限不代表所有输入等耗时。编译器栈布局、libm、调试工具额外内存没有由源码表给出 RSS 字节保证。测试 harness 中的动态输入、Python参考临时数据库与库运行时资源不同。

| 诱人的改动 | 可能破坏的事实 | 安全修改前必须做什么 |
| --- | --- | --- |
| 将分段宽度改成关于 .5 对称 | 冻结非对称模型，而非数值修复 | 获批新模型，不改原参考 |
| 用 signed e+c 或 a/(a+b) 重写中心 | 溢出或改变极大值求值顺序 | 审核 int64 全域与历史均值参考 |
| 所有 Beta 都套正态近似 | 换分布，Jeffreys .5 尾部失真 | 新算法须同分布独立参考，不偷换模型 |
| 删除 fma/补偿、直接减 rounded center | 极窄后验 CDF/量化位置误差 | 复现 INT64_MAX/2^53 邻域与阈值参考 |
| 普通EV用 fma 一次算完 | epsilon附近离散分类变化 | 先证明冻结乘减顺序仍保持 |
| 用 strtod/固定17位截断 | locale、文法、舍入模式、远尾中点错误 | 精确位、长输入、四模式与范围回归 |
| 用新 exposed 判 compromised | 把同次首次暴露倒因果应用到旧修订 | 23状态、原地与非法前态回归 |
| 非 VALID 也先检查赔率 | 改 unavailable 短路与错误契约 | 保持现行顺序；改变须明确契约批准 |

## 18. 维护要求

公共 API/字段、行为、内部调用、数学/数值、校验错误、测试/夹具、CMake、平台、版本/兼容性/发布行为改变时，在同一分支/PR 更新四指南、权威契约、README 和账本；改写过时段落并区分历史，不叠加矛盾描述。审查头文件对齐、真实断言和模型批准边界；无文档影响要说明。绿色测试不证明解释准确，文字政策不等于 CI 自动强制。问题 ID 不删除/复用，解决记录提交、验证、版本、剩余限制，拒绝/延期保留理由；提案及版本发布必须另获所有者批准。见 [CONTRIBUTING](../CONTRIBUTING.md)。


## D2.2 Models

D2.2 的 Wilson 使用正态生存函数反演及稳定 score 根。CP 通过二项权的尾和包围决定二分方向。见 [独立 Models 数值设计](../models/API.md#numerical-implementation-and-bounds)。


## D2.3 Models

D2.3 的对数质量来自上升乘积与组合系数，使用补偿加法，空间 O(1)。见 [Models API](../models/API.md#explicit-beta-update-and-batch-prediction)。


## D3.1 Models

F003 用 2⁻²¹⁴⁸ 整数单位累计并按整型长除法编码。见 [数值证明](../models/tests/STANDARDIZE_QUALIFICATION.md)。
