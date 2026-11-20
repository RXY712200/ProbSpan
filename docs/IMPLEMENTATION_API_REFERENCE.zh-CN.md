# ProbSpan 完整公共 API 与字段参考

## 1. 基线、契约和通用规则

源码基线：`fdfaddfb58486004ee1cc02c0f4a5c640cd17c7c`，v1.0.0，审查日期 2026-11-16。权威声明为 [安装公共头](../include/probspan/probspan.h)，现行英文契约为 [API.md](API.md)。入门见 [导读](IMPLEMENTATION_WALKTHROUGH.zh-CN.md)，算法见 [内部实现](IMPLEMENTATION_INTERNALS.zh-CN.md)，断言与执行证据见 [验证](IMPLEMENTATION_VALIDATION.zh-CN.md)，扩展提案见 [账本](TECHNICAL_DEBT.zh-CN.md)。本文不是新 API 设计。

所有输出存储由调用者拥有；库不分配堆内存、不保留传入指针、不要求销毁函数。字符串必须是可读且 NUL 结尾的有效 C 字符串；非 NULL 不意味着库能验证其地址有效。不得用悬空指针、越界对象或并发写同一输出对象。每个返回 `probspan_status` 的函数在非 OK 时保持输出不变；返回 OK 后仍要检查字段可用性。不是所有公共函数都验证每一项数学前提，下面列出实际差别。

头文件包含 `stdbool.h`、`stdint.h`，C++ 使用 `extern "C"` 链接。实现为 C11 静态库，无可变全局模型状态；不同对象调用可重入。线程安全不包括调用者共享对象的数据竞争，也不等于任意 libm、舍入模式或 fast-math 下数学结果逐位相同。十进制转换的精确位契约与一般超越函数的容差契约不同。

[合并的设备历史参考](PREVIEW_DEVICE_HISTORY.zh-CN.md) 提供源码树内的 Python 调用方入口和另行构建的 C 消费程序。它们不占公共头的 13 个函数，也不加入安装导出。严格/池化回执分别保留 `applicability`、消费进程状态以及 C 结果中的 `NO_HISTORY`、`INSUFFICIENT`、`VALID`。仅在有估计时读取 C 数值。标准化回执的 `target_parameter_posterior` 有自身算法 ID 和端点包络，不能转换为 `probspan_history_result` 交给历史 EV 入口。Python 回执的字段供调用方复验，长期存档须独立定义格式。完整失败码与输出约束见该参考。

## 2. 版本宏、枚举完整目录

v1.0.0 历史基线的四个产品宏：`PROBSPAN_VERSION_MAJOR=1`、`PROBSPAN_VERSION_MINOR=0`、`PROBSPAN_VERSION_PATCH=0`、`PROBSPAN_VERSION_STRING="1.0.0"`。v1.1.0 的数值宏为 `1,1,0`，字符串为 `"1.1.0"`，CMake 包数字版本为 `1.1.0`。头保护宏不是产品配置入口。ABI 通过函数查询；结果版本字段不应从产品字符串推断。

| 枚举类型 | 全部枚举值与含义 |
| --- | --- |
| `probspan_status` | `PROBSPAN_OK=0` 成功；`PROBSPAN_INVALID_ARGUMENT` 空指针/不合规对象或枚举；`PROBSPAN_RAW_PROBABILITY` 原始整数超出 0..100；`PROBSPAN_SUBJECTIVE_DOMAIN` 半宽直接输入不在 0.01..0.99；`PROBSPAN_HISTORY_COUNTS` 负计数；`PROBSPAN_ODDS_SYNTAX` 文法错误；`PROBSPAN_ODDS_RANGE` 非有限或小于 1 的数值赔率；`PROBSPAN_NUMERICAL_FAILURE` Beta 求解未得到可信结果 |
| `probspan_history_state` | `PROBSPAN_NO_HISTORY=0` 无样本；`PROBSPAN_INSUFFICIENT` 有估计但 gate 未达标；`PROBSPAN_VALID` gate 达标 |
| `probspan_ev_state` | `PROBSPAN_ROBUST_POSITIVE=0` 下界严格大于 epsilon；`PROBSPAN_ROBUST_NEGATIVE` 上界严格小于负 epsilon；`PROBSPAN_CROSSES_THRESHOLD` 其他情况 |
| `probspan_odds_combination` | `PROBSPAN_NORMAL_OVERLAP=0` 倒数和高于临界带；`PROBSPAN_CRITICAL` 倒数和距 1 不超过 epsilon；`PROBSPAN_DOUBLE_POSITIVE_WINDOW` 低于临界带，存在两侧正 EV 的概率窗口，不保证实际 p 在窗口内 |
| `probspan_model_relation` | `PROBSPAN_AGREEMENT_POSITIVE=0` 两模型同稳健正；`PROBSPAN_AGREEMENT_NEGATIVE` 同稳健负；`PROBSPAN_CONFLICT` 稳健方向相反；`PROBSPAN_UNCERTAIN` 至少一个跨阈值；`PROBSPAN_HISTORY_UNAVAILABLE` 历史不可用优先 |

epsilon 为冻结私有参数 `1e-12`，不是用户可调公共宏。枚举除显式第一值外按头文件顺序递增；不要将其存储格式、sizeof 或任意强转值当作跨平台协议。

## 3. 十个结构与全部字段

### `probspan_subjective_result`

| 字段（类型） | 意义 |
| --- | --- |
| `raw_percent` (`int32_t`) | 原始 0..100，保留端点 |
| `used_percent` (`int32_t`) | 数学使用的 clamp 后 1..99 |
| `probability` (`double`) | used/100 |
| `lower`, `upper` (`double`) | logit 模型区间端点，不是抽样置信区间 |
| `logit_half_width` (`double`) | 分段规则 d(p)>0 |
| `model_version` (`uint32_t`) | 主观模型版本，目前 1 |

### `probspan_history_result`

| 字段（类型） | 意义与读取条件 |
| --- | --- |
| `event_count`, `complement_count` (`int64_t`) | 原始非负计数 |
| `sample_size` (`uint64_t`) | 两计数先转无符号后求和，最大 `UINT64_MAX-1` |
| `state` (`probspan_history_state`) | 三态 gate 结果 |
| `statistically_ready` (`bool`) | gate 达标，不证明可比性或无偏 |
| `has_estimate` (`bool`) | n>0 时为 true；无历史时 false |
| `probability`, `lower`, `upper` (`double`) | 均值与中央 95% 可信区间；仅 has_estimate=true 可读 |
| `model_version`, `gate_version` (`uint32_t`) | 独立历史模型/gate 版本，目前各 1 |

### 决策结构

| 类型 | 字段及含义 |
| --- | --- |
| `probspan_ev_interval` | `double center` 中心 EV；`double minimum, maximum` 端点 EV；`probspan_ev_state state` 端点分类 |
| `probspan_odds_geometry` | `double event_break_even=1/Oe`；`double complement_event_break_even=1/Oc`（补事件概率坐标）；`double complement_break_even_as_event=1-1/Oc`（事件坐标）；`probspan_odds_combination combination` 倒数和分类 |
| `probspan_subjective_side` | `probspan_ev_interval ev`；`bool has_robust_margin`；`double robust_margin`，标记 false 时不得解释其数值 |
| `probspan_subjective_analysis` | `uint32_t analysis_version` 赔率分析版本目前 1；`probspan_odds_geometry geometry`；`probspan_subjective_side event, complement_event` 两侧结果 |
| `probspan_historical_side` | `probspan_ev_interval ev`；`double positive_ev_probability`，未知概率位于正 EV 区域的后验质量 |
| `probspan_historical_analysis` | `bool available`；`probspan_historical_side event, complement_event`，available=false 时两侧全部忽略 |
| `probspan_provenance` | `bool evidence_exposed` 已实际暴露；`bool subjective_independence_compromised` 暴露后修订，要求 compromised 蕴含 exposed |

### `probspan_analysis`

| 字段（类型） | 意义 |
| --- | --- |
| `subjective` (`probspan_subjective_result`) | 独立主观估计 |
| `event_odds`, `complement_event_odds` (`double`) | 本次合法数值赔率 |
| `subjective_analysis` (`probspan_subjective_analysis`) | 主观决策结果 |
| `history` (`probspan_history_result`) | 独立历史估计与 gate |
| `historical_analysis` (`probspan_historical_analysis`) | 可用性与历史决策结果 |
| `event_relation`, `complement_event_relation` (`probspan_model_relation`) | 两侧模型关系；没有融合概率字段 |

结构没有 provenance 字段，应用需要单独保存 provenance 与修订事实。产品、ABI、模型、gate、分析版本相互独立；不要直接序列化结构字节。保存有意义字段及版本/可用性，另定义明确字节序、schema 和升级策略；核心没有文件或数据库持久化 API。

## 4. 13 个函数的逐项契约

### 4.1 `probspan_abi_version`

```c
unsigned probspan_abi_version(void);
```

返回 1，无输入、指针、状态码或失败路径。不返回产品版本，也不认证模型一致性。源 [probspan.c](../src/probspan.c)；[smoke.c](../tests/smoke.c) 和 [consumer/main.c](../tests/consumer/main.c) 检查 ABI。用途：应用启动时核对 ABI 支持；错误用法是将返回值当作所有模型的统一版本。

### 4.2 `probspan_subjective_half_width`

```c
probspan_status probspan_subjective_half_width(double probability, double *half_width);
```

直接计算已归一化 p 的分段 logit 半宽。先查输出非 NULL，否则 INVALID_ARGUMENT；再查 `0.01<=p<=0.99`，NaN/无穷也不满足，返回 SUBJECTIVE_DOMAIN；成功写入 d。它不接受 raw 百分整数，不自动 clamp。例：`double d; s=probspan_subjective_half_width(0.6,&d);`，成功为 log(2)。边界 0.45/0.55/0.85/0.95 按冻结分支归属，详见内部篇。源 [subjective.c](../src/subjective.c)；`check_subjective`、`check_api_arguments` 见 [oracle_parity.c](../tests/oracle_parity.c)。所有错误保持 d 原值；不要传 60.0 或把返回宽度当概率区间宽度。

### 4.3 `probspan_subjective_estimate`

```c
probspan_status probspan_subjective_estimate(int32_t raw_percent,
    probspan_subjective_result *result);
```

先输出指针，再整数 0..100，分别 INVALID_ARGUMENT/RAW_PROBABILITY。成功保留 raw，used clamp 1..99，生成 p、上下界、d 与 model_version=1，全部主观字段有意义。0/100 不会报错，但不代表数学概率等于 0/1。示例 `probspan_subjective_estimate(60,&r)`；源 [subjective.c](../src/subjective.c)；[oracle_parity.c](../tests/oracle_parity.c) `check_subjective` 覆盖全部 101 个 raw，[state_parity.c](../tests/state_parity.c) 检查组合委托。错误不改 result；不要提供已经乘 100 两次的值或覆盖 raw 以隐藏 clamp。

### 4.4 `probspan_history_estimate`

```c
probspan_status probspan_history_estimate(int64_t event_count,
    int64_t complement_count, probspan_history_result *result);
```

先输出指针，再两计数非负；错误 INVALID_ARGUMENT/HISTORY_COUNTS。合法域覆盖每个计数 0..INT64_MAX；不能先用有符号加法求和。n=0 正常 OK，无估计而非 NUMERICAL_FAILURE；n>0 求 Jeffreys 均值与两分位数，求解失败 NUMERICAL_FAILURE。成功设置 counts、sample_size、state、两个标志和两个版本；概率字段须按 has_estimate 读取。gate 为 n>=20 且宽度<=0.25，等号可通过。示例 `probspan_history_estimate(12,8,&h)` 无需其他模型输入。源 [historical.c](../src/historical.c)；[oracle_parity.c](../tests/oracle_parity.c) `check_history`、[large_numerics.c](../tests/large_numerics.c) `check_reference/check_stress`。任意非 OK 均不改整个对象。不要用累计曝光数替代完成观察的补事件数，也不能用手工 state 代替该 API。

### 4.5 `probspan_odds_validate`

```c
probspan_status probspan_odds_validate(double odds, double *validated);
```

先输出指针 INVALID_ARGUMENT；然后有限且 >=1，否则 ODDS_RANGE。成功复制原 double，不进行文本解析、不设业务上限，也不把净利润倍率转换为总回报倍率。1 合法，NaN、±无穷、0、负数拒绝。示例 `probspan_odds_validate(2.5,&o)`。源 [odds.c](../src/odds.c)；[oracle_parity.c](../tests/oracle_parity.c) `check_odds/check_api_arguments`。错误不改输出；字符串应使用下一函数。

### 4.6 `probspan_odds_parse`

```c
probspan_status probspan_odds_parse(const char *text, double *validated);
```

先 text/输出非 NULL（INVALID_ARGUMENT），再完整 ASCII 文法（ODDS_SYNTAX），再精确十进制转换，最后调用数值范围检查（ODDS_RANGE）。允许前导零和任意长度的合法字符串；没有输入长度截断契约，但调用者仍需限制不可信请求的资源消耗。`"2.50"` 合法，`" 2"`、`"+2"`、`"2e0"`、`"2."` 均拒绝。判断 >=1 的是舍入后的 binary64，极接近 1 的较小十进制实数可能舍入到 1 并接受。精确最近值，中点 ties-to-even，不依赖 locale 小数点或逐位浮点累计。私有转换器不承担公共文法校验。

源 [odds.c](../src/odds.c)、[decimal.c](../src/decimal.c)；[decimal_parity.c](../tests/decimal_parity.c) `check_vectors` 检查 41 位向量、可用四舍入模式、可用逗号 locale；[decimal_differential.py](../tests/decimal_differential.py) 使用流式测试入口。错误保持输出；例 `probspan_odds_parse("2.50",&o)`。不要用 strtod/atof 的宽松文法替代，也不要把测试 harness 的动态内存误认为运行时依赖。

### 4.7 `probspan_classify_ev`

```c
probspan_status probspan_classify_ev(double ev_minimum, double ev_maximum,
    probspan_ev_state *state);
```

实际只检查输出非 NULL（INVALID_ARGUMENT），然后 `min>1e-12` 优先正，`max<-1e-12` 负，否则跨阈值。**不验证有限性、端点顺序或 min<=max**，调用者应提供合法 EV 区间。恰好 ±epsilon 都不越过严格边界；NaN 按 C 比较规则走分支，不能期待数值错误状态。合法示例 `probspan_classify_ev(-0.1,0.2,&state)` 返回跨阈值。源 [decision_policy.c](../src/decision_policy.c)；[analysis_parity.c](../tests/analysis_parity.c) `check_classifiers` 包含 epsilon 附近。非 OK 不改输出；错误用法是根据该函数 OK 认定任意输入区间已被校验。

### 4.8 `probspan_classify_odds_combination`

```c
probspan_status probspan_classify_odds_combination(double event_odds,
    double complement_odds, probspan_odds_combination *combination);
```

先输出指针，再事件赔率、补事件赔率依次校验。INVALID_ARGUMENT/ODDS_RANGE；合法后计算 T=1/Oe+1/Oc，`abs(T-1)<=epsilon` 为 CRITICAL，`T>1+epsilon` 为 NORMAL_OVERLAP，其余 DOUBLE_POSITIVE_WINDOW。它不读取概率，不能判断实际两侧均有正 EV。例 `(2.0,2.0)` 临界。源 [decision_geometry.c](../src/decision_geometry.c)、[decision_policy.c](../src/decision_policy.c)；[analysis_parity.c](../tests/analysis_parity.c) `check_geometry/check_classifiers`。错误保持输出，不能把存在窗口解释为无风险套利承诺。

### 4.9 `probspan_classify_model_relation`

```c
probspan_status probspan_classify_model_relation(probspan_ev_state subjective_state,
    bool historical_available, probspan_ev_state historical_state,
    probspan_model_relation *relation);
```

先检查输出、subjective_state 是否为三个合法枚举；仅在 historical_available=true 时校验 historical_state。任一违反返回 INVALID_ARGUMENT，保持输出。之后不可用优先于跨阈值，跨阈值优先于两种 agreement，其余 conflict。historical_available=false 时历史枚举被忽略；主观枚举仍必须有效。例 `(PROBSPAN_ROBUST_POSITIVE,false,PROBSPAN_CROSSES_THRESHOLD,&r)` 返回 HISTORY_UNAVAILABLE。源 [decision_policy.c](../src/decision_policy.c)；[analysis_parity.c](../tests/analysis_parity.c) `check_classifiers`、[api_contract.c](../tests/api_contract.c) `check_precedence_and_safety`。无概率融合输出，不能用 conflict 自动否定某模型。

### 4.10 `probspan_analyze_subjective`

```c
probspan_status probspan_analyze_subjective(const probspan_subjective_result *subjective,
    double event_odds, double complement_odds, probspan_subjective_analysis *analysis);
```

应传 estimate API 产生的结果。先输入/输出指针，再有限有序 `[0,1]` 区间、中心严格在 (0,1)、有限正半宽；失败 INVALID_ARGUMENT。然后依次验证赔率，失败 ODDS_RANGE。它不重新核对 raw、used、model_version 或用 raw 重算区间；局部检查不构成伪造对象认证。成功给出 analysis_version、geometry、两侧 EV 和 S 标记。赔率恰为 1 时对应 has_robust_margin=false，robust_margin 不可解释；其他侧不受影响。

例：先 `probspan_subjective_estimate(60,&s)` 成功，再 `probspan_analyze_subjective(&s,2.0,3.0,&a)`。源 [subjective_analysis.c](../src/subjective_analysis.c) 和 geometry；[analysis_parity.c](../tests/analysis_parity.c) `check_subjective/check_arguments`。非 OK 不改整个分析对象。不要将任意外部概率包装成该结构声称它符合主观 v1 模型；外部模型需要独立版本与接口决定。

### 4.11 `probspan_analyze_historical`

```c
probspan_status probspan_analyze_historical(const probspan_history_result *history,
    double event_odds, double complement_odds, probspan_historical_analysis *analysis);
```

先指针 INVALID_ARGUMENT；随后 **state 只要不等于 PROBSPAN_VALID 就直接 OK、available=false**，不检查赔率或不可用概率字段。实现不是对未知 history_state 枚举报错的总校验器，应传 estimate 的合法结果。VALID 时检查 has_estimate、计数非负、有限有序 `[0,1]` 区间，否则 INVALID_ARGUMENT；接着赔率检查 ODDS_RANGE，再计算两侧 EV 和 Beta 质量，失败 NUMERICAL_FAILURE。未重新证明 gate、sample_size、各版本或概率均值和计数相符。

成功 available=true 时可读两侧所有字段；false 时必须忽略两侧全部字段。例：估计成功后 `probspan_analyze_historical(&h,2.0,3.0,&a)`，再检查 available。源 [historical_analysis.c](../src/historical_analysis.c)；[analysis_parity.c](../tests/analysis_parity.c) `check_histories/check_arguments` 验证不可用时无效赔率的短路，[large_numerics.c](../tests/large_numerics.c) 验证底层数值。错误不改输出；不要将 posterior P(EV>0) 当作事件概率。

### 4.12 `probspan_provenance_transition`

```c
probspan_status probspan_provenance_transition(const probspan_provenance *previous,
    int32_t previous_raw_percent, int32_t current_raw_percent,
    bool subject_changed, bool evidence_exposed_now, probspan_provenance *result);
```

先两个指针，再旧状态 `compromised&&!exposed` 不变量（INVALID_ARGUMENT），再两个 raw 的 0..100（RAW_PROBABILITY）。成功按旧 exposed 判断本次修订是否破坏独立性，两个布尔值粘滞；无时钟、主题查找或显示动作。首次调用旧值 `{false,false}`，previous/current raw 相等。允许 result==previous；失败包括原地失败也保持对象不变。raw 从 0 到 1 虽然 used 相同，仍是 raw 变化。

例：`probspan_provenance p={false,false};` 然后以相同 raw 和 exposure=true 更新，只有 exposed；下一次 raw 改变才 compromised。源 [provenance.c](../src/provenance.c)；[state_parity.c](../tests/state_parity.c) `check_provenance` 23 冻结案例和原地更新，[api_contract.c](../tests/api_contract.c) `check_provenance_invariant` 覆盖畸形旧值及优先级。见 [provenance 示例](../examples/provenance.c)。不要用“用户请求显示”代替“用户实际看到”，也不能用改回 raw 清除粘滞标记。

### 4.13 `probspan_compose_analysis`

```c
probspan_status probspan_compose_analysis(int32_t raw_percent,
    int64_t event_count, int64_t complement_count,
    double event_odds, double complement_event_odds, probspan_analysis *result);
```

先输出指针，再主观估计、历史估计、两赔率、两分析器、两关系，局部组合全部成功才复制输出。错误集合为 INVALID_ARGUMENT、RAW_PROBABILITY、HISTORY_COUNTS、ODDS_RANGE、NUMERICAL_FAILURE；没有文本文法或直接半宽域输入。多错误优先级按实际委托顺序，不能重新排序而称兼容。无历史仍要求合法赔率；成功时历史可能不可用，对应关系 HISTORY_UNAVAILABLE，其他主观结果仍完整。

例 `probspan_compose_analysis(60,19,1,2.0,3.0,&a)`；源 [analysis_composition.c](../src/analysis_composition.c)；[state_parity.c](../tests/state_parity.c) `check_composition` 926 个组合逐字段精确比较分步调用，[api_contract.c](../tests/api_contract.c) `check_precedence_and_safety` 检查多错误与输出保持。不要从失败后的旧 a 读取“本次部分成功”结果。组合不隐式更新 provenance，不保存任何外部状态。

## 5. 可用性决策表

| 成功历史结果 | has_estimate | statistically_ready | history analysis available | 可读内容 |
| --- | --- | --- | --- | --- |
| NO_HISTORY，n=0 | false | false | false | 计数、状态、版本；不读概率或分析两侧 |
| INSUFFICIENT，n>0 gate 未过 | true | false | false | 历史均值/可信区间；不读历史决策两侧 |
| VALID | true | true | true（分析器也成功后） | 历史估计及两侧决策 |

此表描述正常 estimate→analyze 路径，不为手工伪造结构作保证。API 的错误保持保证不是字段可用性的替代品。

<a id="call-cases"></a>

## 6. 每个函数的正例、反例与检查入口

此表补充 §4 的精确签名和字段目录。变量须为正常有效的 C 对象，示例的非 NULL 地址不是“任意内存都可用”的许可；省略的函数前缀均为 `probspan_`。返回码同样省略 PROBSPAN_。每个返回错误的调用都不写输出；ABI 查询没有输出参数。

| 函数 | 正例及预期 | 反例及实际结果 | 特殊分支/接口协作 | 实现与精确测试入口 |
| --- | --- | --- | --- | --- |
| abi_version | `abi_version()==1u` | 没有输入错误案例；不要将 1 当 1.0.0 字符串 | 不查询动态模型选择 | probspan.c；smoke main、api_contract main |
| subjective_half_width | `.45→log(1.5)`；`.55/.85→log(2)` | `half_width(NAN,&d)→SUBJECTIVE_DOMAIN`；`(NAN,NULL)→INVALID_ARGUMENT` | 输出域是 logit 宽，不是 p 的宽；估计器在 clamp 后调用 | subjective.c；oracle_parity/check_subjective、api_contract/check_precedence_and_safety |
| subjective_estimate | `0→raw=0,used=1`；`100→raw=100,used=99` | `(-1,&s)→RAW_PROBABILITY`；`(-1,NULL)→INVALID_ARGUMENT` | 输出可传 analyze_subjective；半宽域错误对合法 raw 的正常内部路径不可达 | subjective.c；oracle_parity/check_subjective、check_api_arguments |
| history_estimate | `(0,0,&h)→OK+NO_HISTORY`；`(1,0)→均值.75` | `(-1,0,&h)→HISTORY_COUNTS`；同输入输出 NULL 时先 INVALID_ARGUMENT | 大计数不能仅因大而拒绝；实际求解失败才 NUMERICAL_FAILURE | historical.c；oracle_parity/check_history、large_numerics/check_reference/check_stress |
| odds_validate | `(1,&o)→OK,o=1`；`(2.5,&o)→2.5` | `(INFINITY,&o)→ODDS_RANGE`；`(NAN,NULL)→INVALID_ARGUMENT` | 有限 DBL_MAX 也在数值域；不承诺所有派生超越函数逐位一致 | odds.c；oracle_parity/check_odds、api_contract/check_precedence_and_safety |
| odds_parse | `"0002.50"→2.5` | `"2."→ODDS_SYNTAX`；`"0.5"→ODDS_RANGE`；`"invalid",NULL→INVALID_ARGUMENT` | 先扫描全串，再精确转换，再检查舍入值>=1；无 malloc 错误码 | odds.c/decimal.c；decimal_parity/check_vectors、oracle_parity/check_odds |
| classify_ev | `(-.1,.2)→CROSSES_THRESHOLD`；`(2e-12,.1)→ROBUST_POSITIVE` | `(0,0,NULL)→INVALID_ARGUMENT`；`(NAN,NAN,&v)→OK+CROSSES_THRESHOLD` 是源码推导，不是数值认证 | 逆序 `(1,-1)` 会因第一个分支得到正，说明不能依赖它检查区间 | decision_policy.c；analysis_parity/check_classifiers；NaN/逆序例用于解释实际分支，不声称已有专门断言 |
| classify_odds_combination | `(2,2)→CRITICAL`；`(3,3)→DOUBLE_POSITIVE_WINDOW` | `(.5,2,&g)→ODDS_RANGE`；`(NAN,NAN,NULL)→INVALID_ARGUMENT` | 先事件后补事件；不需要 p，不能从类别推导实际 EV 状态 | geometry/policy；analysis_parity/check_geometry/check_classifiers |
| classify_model_relation | `(POS,false,无效历史枚举,&r)→HISTORY_UNAVAILABLE` | `(POS,true,无效历史枚举,&r)→INVALID_ARGUMENT` | 只允许三个合法 subjective 枚举；无历史也不忽略非法主观状态 | policy；api_contract/check_precedence_and_safety、analysis_parity/check_classifiers |
| analyze_subjective | estimate(60) 后 `(s,2,3)→两侧 EV/S`；对应赔率 1 则仅该侧 S 不可用 | `s.lower>s.probability→INVALID_ARGUMENT`；合法 s 加赔率 .5→ODDS_RANGE | 不核对 raw/used/model_version 与区间的模型一致性；需来源可靠估计对象 | subjective_analysis/geometry；analysis_parity/check_subjective/check_arguments |
| analyze_historical | estimate(12,8) 后坏赔率仍 `OK+available=false`；estimate(19,1) 后有效赔率给质量 | 输入 history=NULL→INVALID_ARGUMENT；VALID 但 has_estimate=false 即使赔率 NaN 也先 INVALID_ARGUMENT | state!=VALID 包括未知枚举都短路，这是实现事实而非鼓励伪造状态 | historical_analysis；analysis_parity/check_histories/check_arguments |
| provenance_transition | 初值 false/false，同 raw 首次暴露→true/false；之后 raw 变→true/true | 旧 false/true 且 raw=-1/101→INVALID_ARGUMENT，先于 RAW_PROBABILITY | 允许 previous==result，含错误保持；不允许用更换 used 隐藏 raw 修订 | provenance.c；api_contract/check_provenance_invariant、state_parity/check_provenance |
| compose_analysis | `(60,19,1,2,3,&a)→完整事实`；`(60,0,0,2,3)→主观可用/历史不可用` | `(-1,-1,-1,NAN,NAN,&a)→RAW_PROBABILITY`；输出 NULL 时优先 INVALID_ARGUMENT | 没有文本输入，不返回 ODDS_SYNTAX；不包含 provenance 转移 | composition；state_parity/check_composition、api_contract/check_precedence_and_safety |

POS 在本表仅是 `PROBSPAN_ROBUST_POSITIVE` 的排版缩写，不是 C 标识。所有实际结构/枚举/参数名仍以 §2–4 和公共头为准。字段检查后的源内调用可能返回防御性错误；“可达状态码”应区分公共函数直接收到不合规对象与正常 estimate→analyze 路径，不能为展示每个错误而伪造合法输入必然失败。

<a id="precedence-matrix"></a>

## 7. 多错误、字段访问与所有权的交叉矩阵

| 同时存在的条件 | 实际状态/顺序 | 可以据此确认什么 | 不可以确认什么 |
| --- | --- | --- | --- |
| 任意 API 输出 NULL 且数值非法 | 带状态函数先 INVALID_ARGUMENT | 输出前提未满足 | 尚未到数值范围校验 |
| parse 文法非法且转换本应越界 | ODDS_SYNTAX，转换不执行 | 完整文法失败 | 不是“范围也已认证” |
| compose raw 非法、计数负、赔率 NaN | RAW_PROBABILITY | 主观输入最先失败 | 未检查后续计数/赔率 |
| compose raw 合法、计数负、赔率 NaN | HISTORY_COUNTS | 计数先于赔率 | 没有本次可提交分析 |
| compose 无历史、赔率 NaN | ODDS_RANGE | 主观分析仍需赔率 | 不会因历史短路跳过整个组合 |
| analyze_historical 非 VALID、赔率 NaN | OK + unavailable | 该路径未解释概率/赔率 | 不证明 NaN 是合法赔率 |
| analyze_historical VALID、坏区间、坏赔率 | INVALID_ARGUMENT | 对象检查先于赔率 | 不能区分所有内部字段是否真实来自模型 |
| relation history unavailable、历史枚举坏 | OK + HISTORY_UNAVAILABLE | 历史枚举未读取为有效状态 | 主观枚举仍必须合法 |
| provenance 旧状态非法且 raw 非法 | INVALID_ARGUMENT | 不变量先于 raw | 不会修复旧状态或重置标记 |

前三类多错误及 provenance 的具体回归直接见 api_contract/check_precedence_and_safety、check_provenance_invariant；分析器对象/赔率顺序由实现与 analysis_parity/check_arguments 共同定位，不把所有表格组合冒称已经逐一测试。

| 输出族 | 成功后仍要检查 | 可读字段 | 禁止推断 |
| --- | --- | --- | --- |
| subjective_result | 无额外 availability | 所有定义字段 | used 不等于 raw 的外部事实 |
| history_result | has_estimate | false 时只读计数、n、state、flags、versions；true 才读概率/区间 | INSUFFICIENT 不等于后验不存在 |
| subjective_analysis | 各侧 has_robust_margin | geometry、两侧 ev 始终有意义；S 按侧标记 | 不能因一侧 S false 隐藏另一侧全部结果 |
| historical_analysis | available | false 时两侧均不可解释；true 才读 EV/质量 | 内部初始化为零不赋予其数值意义 |
| analysis | 各嵌套对象的上述条件 | 输入、独立版本、关系及条件允许字段 | 总 OK 不提升嵌套可用性 |
| 任一非 OK 输出 | 本次状态 | 只可按之前成功调用保留的事实使用旧对象 | 未初始化旧对象不是可读回退值 |

指针/别名边界：所有对象必须足够大、对齐、可读/可写且调用期间存活。数值入参按值传递；例如 `odds_validate(o,&o)` 合理。provenance 明确支持完整同类型原地更新；其他跨类型输入/输出不通过强制转换重叠，公共契约没有为任意部分重叠提供保证。估计结构可复制后跨调用保存，分析器只在调用期间读取它；没有借出的内部缓存、引用计数或析构入口。无需为了结果生命周期锁住整个库，但同一共享对象访问必须由调用者同步。

<a id="cmake-consumer"></a>

## 8. 安装消费者、C/C++ 与结果封装

完整 CMake 消费者如下；这是应用自己的两文件工程，不是新库接口：

```cmake
cmake_minimum_required(VERSION 3.16)
project(probspan_app LANGUAGES C)
find_package(ProbSpan 1.0 CONFIG REQUIRED)
add_executable(app main.c)
target_link_libraries(app PRIVATE ProbSpan::probspan)
set_target_properties(app PROPERTIES C_STANDARD 11 C_STANDARD_REQUIRED YES)
```

main.c 可直接使用导读的 history-only 或分步完整程序。先按验证指南安装到独立 prefix，再 `cmake -S <app-dir> -B <app-build> -DCMAKE_PREFIX_PATH=<prefix>`，build 并运行。不要直接 include `src/` 来解决 package 配置错误；m 的传递链接由导出目标处理，私有 Beta/decimal 不属于已安装 API。

C++ 工程可用 `project(... LANGUAGES CXX)` 并链接同一 C 库，公共头中的 extern C 保持函数链接名；bool/int64_t 类型来自头，不能自己复制一份“相同布局”声明。没有异常回调或 C++ 资源对象，返回状态由应用处理。本次是否实际编译 C++ 消费者必须看验证记录，不能由 extern C 字样推出实测通过。

应用封装应存储“状态 + 各字段 availability + 各模型版本”，而不是仅保存几个 double。产品版本描述发行，ABI 描述链接接口，模型版本描述数学行为，gate_version 描述历史准入统计规则，analysis_version 描述赔率分析。它们当前都出现数字 1 不代表未来同步增加；historical_analysis 自身没有版本字段，应连同来源 history 与相关分析上下文一起保存，不能臆造字段。持久 schema、字节序、未知版本处理和分析事实不可变性由外部负责。

## 9. 维护与审查

公共 API/字段、函数行为、内部调用、数学/数值、校验/错误、测试/夹具、CMake、平台、版本/兼容性/发布行为改变时，须同一分支/PR 审查并更新四篇指南、权威契约、README 与账本；改写过时解释，保留明确标注的历史而非矛盾现行描述。核对 13 函数及类型目录、实际断言和可用性优先级；无文档影响须说明。绿色测试不是文档准确性证明，政策不自动成为 CI 检查。账本 ID 永不删除/复用，完成记录提交、测试、首次版本与剩余限制；延期/拒绝保留原因。模型/版本/发布/提案须经所有者批准，见 [维护规则](../CONTRIBUTING.md)。


## D2.2 Models

上述 13 个接口属于 legacy 包。D2.2 独立 Models 接口、结果和错误优先级见 [Models API](../models/API.md)。


## D2.3 Models

独立 Models 包新增 Beta 后验与预测类型，区分可信的结构一致性、批次概率表示与失败。见 [Models API](../models/API.md#explicit-beta-update-and-batch-prediction)。
