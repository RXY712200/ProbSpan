# ProbSpan 源码导读：从输入到分析事实

## 阅读基线与导航

本文对应 `fdfaddfb58486004ee1cc02c0f4a5c640cd17c7c`（已发布 v1.0.0），审查日期 2026-11-16。后续文档提交不代表数学模型更新。公共声明以 [probspan.h](../include/probspan/probspan.h) 为准，行为与数值约束分别见 [行为规范](BEHAVIOR_SPEC.md)、[数值契约](NUMERICAL_CONTRACT.md)。源码与契约出现分歧时应报告，不把解释文档当成修改契约的授权。

建议顺序：本篇 → [完整 API](IMPLEMENTATION_API_REFERENCE.zh-CN.md) → [内部实现](IMPLEMENTATION_INTERNALS.zh-CN.md) → [验证与证据](IMPLEMENTATION_VALIDATION.zh-CN.md)。研究与未实现能力查 [永久账本](TECHNICAL_DEBT.zh-CN.md)。四篇分工参考 [LayerKeySort 的文档导航](https://github.com/RXY712200/LayerKeySort/tree/13998b0682e56f34b401773f754e6d2c88c51206/docs)，只借鉴组织方式，不借用其排序算法或保证。

## 1. 产品解决什么问题

ProbSpan 是静态链接的 C11 概率不确定性与决策分析内核。给定主观百分数、调用者整理好的二元历史计数以及包含本金的总回报赔率，它分别计算两个模型的区间，再把同一赔率映射到 EV 区间和分类。它不训练通用预测模型、不获取数据库记录、不保存分析、不管理界面、不融合两个概率，也不替用户作决策。

适用场景是“明确事件、互斥且穷尽的补事件、同一观察单位和条件下的计数、线性单位成本回报”。例如同一流程下产品合格/不合格、同类试验成功/失败，前提是调用者已经论证可比性。数据库的一行可能是重复记录、未完成观察、不同时间窗或同一人的相关行为，不能因其有 0/1 字段就自动视为独立 Bernoulli 观察。`PROBSPAN_VALID` 只表示冻结统计门槛达标，不是历史可迁移性的证书。

主观模型与历史模型的“独立”表示计算路径不互相修改参数，不表示库能证明用户没有看过历史。后者需要调用者如实报告实际证据暴露，由 provenance 记录。计算结果不能替代领域验证。

### 设备历史的调用方路径（合并的 Preview）

以下 v1 导读仍以正式发布源码为基线。若输入是逐行的 100 小时设备周期，另有 [可选设备历史参考](PREVIEW_DEVICE_HISTORY.zh-CN.md)：先由调用方提供目标、快照、截止时刻与标明来源的适用性声明，再运行 `review()`。晚到行排除，同一角色内一致的查询别名折叠，身份冲突或不支持的依赖使整次请求弃权。通过后，严格或已声明可比的池化路径通过独立消费程序调用 v1，读取 v1 估计状态。已知固定目标权重的两层路径返回另外的参数后验；正权重层无支持时弃权。证据准入、v1 的统计 gate 和数值求解分别判定，不能把拒绝或未知编码成空历史。参见[断言地图](IMPLEMENTATION_VALIDATION.zh-CN.md#preview-device-history-validation)。

## 2. 完整源码地图

| 文件 | 责任与依赖方向 |
| --- | --- |
| [include/probspan/probspan.h](../include/probspan/probspan.h) | 唯一安装公共头；13 函数、5 枚举、10 结构、4 产品版本宏 |
| [src/probspan.c](../src/probspan.c) | ABI 版本查询，不执行模型 |
| [src/model_v1.h](../src/model_v1.h) | 冻结模型、gate、分类 epsilon 与独立版本常量 |
| [src/subjective.c](../src/subjective.c) | 原始百分数、clamp、分段 logit 半宽与区间 |
| [src/subjective_input.h](../src/subjective_input.h)、[probability_math.h](../src/probability_math.h) | 原始输入范围与 logit 小原语；logistic 私有函数在 subjective.c |
| [src/historical.c](../src/historical.c)、[history_model_private.h](../src/history_model_private.h) | 计数、Jeffreys 参数、区间、gate；形状参数共用构造 |
| [src/beta.c](../src/beta.c)、[beta_private.h](../src/beta_private.h) | 普通 Beta CDF/分位数、数值分支派发 |
| [src/beta_logit.c](../src/beta_logit.c)、[beta_logit.h](../src/beta_logit.h) | 大参数变换积分、补偿运算与安全分位求解 |
| [src/gamma.c](../src/gamma.c)、[gamma_private.h](../src/gamma_private.h) | 正参数 Gamma 归一化与 Stirling 余项，避免 signgam 共享状态 |
| [src/odds.c](../src/odds.c) | 数值赔率和完整 ASCII 文法校验 |
| [src/decimal.c](../src/decimal.c)、[decimal_private.h](../src/decimal_private.h) | 十进制文本到 binary64 的精确中点比较与 ties-to-even |
| [src/decision_geometry.c](../src/decision_geometry.c)、[decision_private.h](../src/decision_private.h) | 概率区间、补事件、EV、赔率几何、输入对象检查 |
| [src/decision_policy.c](../src/decision_policy.c) | EV/赔率/模型关系分类，不融合概率 |
| [src/subjective_analysis.c](../src/subjective_analysis.c) | 主观两侧 EV 和 robust margin S |
| [src/historical_analysis.c](../src/historical_analysis.c) | 历史可用性与正 EV 后验质量 |
| [src/provenance.c](../src/provenance.c) | 纯状态转移，不读取时钟、UI 或数据库 |
| [src/analysis_composition.c](../src/analysis_composition.c) | 委托上述公共函数，全部成功后交付完整值 |

共 14 个生产 `.c` 和 9 个私有 `.h`。`tests/` 和 `oracle/` 不是运行时库：Python、SciPy、mpmath 是开发参考工具，应用不因链接静态库而依赖它们。安装和 CI 的入口为 [CMakeLists.txt](../CMakeLists.txt)、[ci.yml](../.github/workflows/ci.yml)。

## 3. 两条估计路径

```text
probspan_subjective_estimate(raw)
  → ps_valid_raw_percent → clamp 到 used=1..99
  → probspan_subjective_half_width(p) → logit/logistic → 主观结果

probspan_history_estimate(e,c)
  → 非负检查 → 无符号样本和 → n=0 不提供估计
  → ps_history_shapes → ps_beta_quantile(两端)
      → 普通 CDF/二分 或 transformed-logit 积分/分位求解
  → 样本量与区间宽度 gate → 历史结果
```

主观 `raw=0` 与 `raw=100` 都是合法输入；保存原值，数学计算分别用 1% 和 99%。宽度由 p 所在分段决定，不由历史决定。主观区间是冻结规则给出的 logit 不确定性范围，不是从抽样得到的置信区间，也不是经过评分验证的专家可信度。

历史 e、c 分别是事件和补事件计数，均为非负 `int64_t`。先验为 Beta(½,½)，后验参数 `a=e+½,b=c+½`。n>0 时给出均值和中央 95% 可信区间。只有 `n>=20` 且 `upper-lower<=0.25` 才是 `PROBSPAN_VALID`；否则为 `PROBSPAN_INSUFFICIENT`，仍有估计。n=0 为 `PROBSPAN_NO_HISTORY`，`has_estimate=false`，不能读取三个概率字段。

## 4. 赔率、补事件与两个分析器

数值赔率必须有限且 `>=1`。文本只接受 `[0-9]+(\.[0-9]+)?` 的完整 ASCII 字符串，例如 `"2.50"`；不接受符号、空白、指数、逗号、`.5`、`2.`。先完整检查文法，再精确舍入到 binary64，最后检查舍入后的赔率范围。不要用 `atof` 替代这一契约。

```text
probspan_analyze_subjective(主观结果, Oe, Oc)
  → 检查概率区间/半宽 → 校验两赔率 → 赔率几何
  → 事件 EV(p)、补事件 EV(1-p) → 各自分类与 S

probspan_analyze_historical(历史结果, Oe, Oc)
  → state 非 VALID：立即 OK + available=false
  → VALID：检查对象、赔率 → 两侧 EV → Beta CDF 后验正 EV 概率
```

单位成本 EV 为 `p*O-1`，并对区间端点作同样变换。补事件区间必须按 `[1-upper,1-lower]` 反向映射，不能把 lower 直接变为补事件 lower。事件盈亏平衡点为 `1/Oe`；补事件阈值换到事件坐标为 `1-1/Oc`。两侧赔率可不对称。

EV 下界严格大于 `1e-12` 才稳健正；上界严格小于 `-1e-12` 才稳健负，其余跨阈值。分类看端点，不看均值正负。S 用有符号距离（logit 中心减 logit 盈亏平衡点）除以原模型半宽，保留方向而不是取绝对值；它不是 z-score 或成功概率。赔率恰为 1 时 S 不可用，EV 仍有效。

历史事件正 EV 后验概率为 `1-I_(1/Oe)(a,b)`，补事件为 `I_(1-1/Oc)(a,b)`。这是模型下未知概率落在正 EV 区域的后验质量，不是下一次事件发生概率，不是重复获利频率，更不是给定条件完全正确的保证。

## 5. 模型关系与 provenance

`probspan_classify_model_relation` 只比较两个 EV 分类。历史不可用优先返回 `PROBSPAN_HISTORY_UNAVAILABLE`；任一跨阈值返回 `PROBSPAN_UNCERTAIN`；两者同为稳健正/负分别 agreement；方向相反为 conflict。没有平均、加权或选择“更正确”的模型。

provenance 从 `{false,false}` 开始。`evidence_exposed_now` 是已经发生的暴露事实，而不是请求显示证据。新 exposed 为 old exposed OR now；新 compromised 为 old compromised OR（old exposed AND 本次主题变化或 raw 变化）。关键在 **old exposed**：首次同一操作中暴露并改 raw 不被算作“暴露之后的修订”；下一步再变更才触发。两个标记都粘滞，改回原始 raw 也不恢复独立性。`compromised=>exposed` 是可达状态不变量；传入违反不变量的旧对象返回 `PROBSPAN_INVALID_ARGUMENT`，包括原地更新。库不管理修订号、主题身份、显示生命周期与时钟。

## 6. 组合器的真实顺序

`probspan_compose_analysis`：输出指针 → subjective estimate → history estimate → 事件赔率 → 补事件赔率 → subjective analysis → historical analysis → 两侧 model relation → 一次复制最终对象。

因此多个输入同时错误时，raw 错误先于计数错误，计数先于赔率错误。历史不可用并不会使整个组合器跳过赔率检查，因为主观分析仍需要赔率。任何失败不交付半成品；不要在失败后将旧输出误认为本次结果。结果是含独立版本的分析事实，不是自动更新的缓存，provenance 需单独保存。

## 7. 完整组合示例

```c
#include <stdio.h>
#include <probspan/probspan.h>

int main(void) {
    probspan_analysis a;
    probspan_status s = probspan_compose_analysis(60, 19, 1, 2.0, 3.0, &a);
    if (s != PROBSPAN_OK) { return 1; }
    printf("raw=%d used=%d subjective=%.6f\n",
           (int)a.subjective.raw_percent, (int)a.subjective.used_percent,
           a.subjective.probability);
    printf("subjective EV=[%.6f, %.6f]\n",
           a.subjective_analysis.event.ev.minimum,
           a.subjective_analysis.event.ev.maximum);
    if (a.historical_analysis.available) {
        printf("posterior P(EV>0)=%.6f\n",
               a.historical_analysis.event.positive_ev_probability);
    }
    return 0;
}
```

这里 p=0.6、d=log(2)，主观区间约 `[0.428571,0.75]`，事件 EV 约 `[-0.142857,0.5]`，不能仅凭中心 EV=0.2 宣称稳健正。19/1 的历史后验与主观估计分开计算；是否显示历史两侧字段必须检查 available。完整可编译工程示例见 [decision.c](../examples/decision.c)，安装后的链接使用 `ProbSpan::probspan`。

## 8. 只使用历史，不提供主观值或赔率

```c
#include <stdio.h>
#include <probspan/probspan.h>

int main(void) {
    probspan_history_result h;
    if (probspan_history_estimate(12, 8, &h) != PROBSPAN_OK) { return 1; }
    if (!h.has_estimate) { puts("No history estimate"); return 0; }
    printf("posterior=%.6f interval=[%.6f, %.6f] ready=%d\n",
           h.probability, h.lower, h.upper, (int)h.statistically_ready);
    return 0;
}
```

这条路径没有赔率、主观参数或 provenance 的强制依赖。20 个观察不保证 gate 达标；仍需看区间宽度。只有主观值时调用 `probspan_subjective_estimate`；只有赔率文本时调用 `probspan_odds_parse`；已分别获得估计时按需调用对应分析器，没必要伪造完整组合所需的其他输入。

## 9. 状态、错误、版本与集成误区

`PROBSPAN_OK` 不等于“全部结果可读”。依次检查 `has_estimate`、`state/statistically_ready`、分析 `available`、S 的 `has_robust_margin`。非 OK 保持调用者输出不变；初始未初始化对象不能因输出不变而安全读取。不要手工构造假的 VALID 历史来绕过 gate；分析器不是完整的结果认证器。

v1.0.0 历史基线的产品版本宏为 1.0.0，v1.1.0 的产品字符串为 `1.1.0`。两者的 `probspan_abi_version()` 返回 1；主观模型、历史模型、gate、赔率分析版本目前也分别为 1，但含义独立，不能用一个整数替代所有版本。原始结构含 padding、枚举与平台布局，不能直接 fwrite 当作跨版本持久格式。保存有含义字段、可用性和独立版本，历史重放不能默默用新版重算覆盖旧事实。

## 10. 新维护者的阅读与调试路线

先读公共头与本篇，再按症状定位：raw/clamp 查 subjective；计数/可用性查 historical；极端后验查 beta/beta_logit/gamma；文本末位不符查 odds/decimal；补事件方向或 EV 边界查 decision_geometry/policy；S 查 subjective_analysis；历史阈值质量查 historical_analysis；暴露顺序查 provenance；多错误优先级查 composition。每次沿 [源码—断言映射](IMPLEMENTATION_VALIDATION.zh-CN.md) 找到对应测试，区分“公式错误”“浮点表示限制”“不可用正常结果”“输入语义不足”。

<a id="api-choice"></a>

## 11. 按任务选择入口，而不是强迫所有输入齐全

| 用户手中有什么/要回答什么 | 调用顺序 | 何时停止 | 不要补造什么 |
| --- | --- | --- | --- |
| 只有整数主观百分数，要模型区间 | subjective_estimate | 估计成功即可展示主观字段 | 不需要 0/0 伪历史或默认赔率 |
| 研究分段 d(p)，已有归一化 p | subjective_half_width | 得到 logit 半宽 | 不把整数 60 当 p=60 |
| 只有合格二元计数，要后验 | history_estimate | 看 has_estimate 后读取均值/区间 | 不要求主观值、赔率或 provenance |
| 用户输入文本赔率 | odds_parse | OK 才持有有效 double | 不先用 atof，否则错误文法可能被吞掉 |
| 已有 double 赔率 | odds_validate | 范围通过 | 不需要先转文本再解析 |
| 主观估计与两赔率，要 EV/S | estimate→analyze_subjective | 按侧检查 has_robust_margin | 不伪造估计对象来包装外部模型 |
| 历史估计与两赔率，要后验正 EV 质量 | history_estimate→analyze_historical | 看 available；false 是正常结果 | 不手动将 INSUFFICIENT 改为 VALID |
| 已有合法 EV 端点，要分类 | classify_ev | 得到状态；它不认证端点 | 不把 OK 当数值输入已校验 |
| 只研究赔率组合的窗口 | classify_odds_combination | 得到几何类别 | 不将窗口存在解释为实际 p 在其中 |
| 已有两个模型的 EV 状态 | classify_model_relation | 得到关系 | 不平均概率，也不自动选择赢家 |
| 输入全齐，要完整分析事实 | compose_analysis | 所有委托成功后才取新结果 | 不期待失败时保留本次部分结果 |
| 记录实际暴露后是否改判断 | provenance_transition | 保存新状态与应用修订记录 | 不把显示请求当已暴露事实 |
| 启动时检查链接 ABI | abi_version | 与支持 ABI 对照 | 不据此推导所有模型版本 |

表中省略的前缀均为 `probspan_`。13 个入口都来自公共头，未引入数据库或任意模型路由器。调用选择与真实输入语义的责任在应用；函数名含 history 并不意味着它访问历史存储。

<a id="separate-sequence"></a>

## 12. 完整分步调用：19/1 历史、60% 主观与不对称赔率

场景：应用已经审核一组可比的二元观察，有 19 次事件、1 次补事件；用户在看这组证据前报 raw=60。赔率文本是 2.00、3.00。应用需要分别保留两个模型，再比较结论，而不是将历史均值取代主观概率。

下面是独立的完整 C 程序；每一步先检查状态，最后才读取其输出。`STEP` 是示例的应用局部宏，不属于 ProbSpan API。

```c
#include <stdio.h>
#include <probspan/probspan.h>

#define STEP(call) do { if ((call) != PROBSPAN_OK) return 1; } while (0)

int main(void) {
    double oe, oc;
    probspan_subjective_result s;
    probspan_history_result h;
    probspan_subjective_analysis sa;
    probspan_historical_analysis ha;
    probspan_model_relation er, cr;
    probspan_provenance pv = {false, false};

    STEP(probspan_subjective_estimate(60, &s));
    STEP(probspan_history_estimate(19, 1, &h));
    STEP(probspan_odds_parse("2.00", &oe));
    STEP(probspan_odds_parse("3.00", &oc));
    STEP(probspan_analyze_subjective(&s, oe, oc, &sa));
    STEP(probspan_analyze_historical(&h, oe, oc, &ha));
    STEP(probspan_classify_model_relation(sa.event.ev.state, ha.available,
        ha.available ? ha.event.ev.state : PROBSPAN_CROSSES_THRESHOLD, &er));
    STEP(probspan_classify_model_relation(sa.complement_event.ev.state, ha.available,
        ha.available ? ha.complement_event.ev.state : PROBSPAN_CROSSES_THRESHOLD, &cr));

    printf("subjective %.9f [%.9f, %.9f] d=%.9f\n",
           s.probability, s.lower, s.upper, s.logit_half_width);
    if (h.has_estimate) {
        printf("history %.9f [%.9f, %.9f] ready=%d\n",
               h.probability, h.lower, h.upper, (int)h.statistically_ready);
    }
    printf("subjective EV event=[%.9f, %.9f] complement=[%.9f, %.9f]\n",
           sa.event.ev.minimum, sa.event.ev.maximum,
           sa.complement_event.ev.minimum, sa.complement_event.ev.maximum);
    if (ha.available) {
        printf("posterior positive EV event=%.9f complement=%.9f\n",
               ha.event.positive_ev_probability,
               ha.complement_event.positive_ev_probability);
    }
    printf("relations event=%d complement=%d\n", (int)er, (int)cr);

    /* 应用确认用户实际看到证据后，才记录 exposure。 */
    STEP(probspan_provenance_transition(&pv, 60, 60, false, true, &pv));
    STEP(probspan_provenance_transition(&pv, 60, 70, false, false, &pv));
    printf("exposed=%d compromised=%d\n", (int)pv.evidence_exposed,
           (int)pv.subjective_independence_compromised);
    return 0;
}
```

调用链中的实际中间事实：

1. subjective.c：raw=used=60，p=.6，落入 [.55,.85] 平台，d=log(2)。logit 中心 log(1.5)，下/上界理论值 3/7 和 3/4；打印的是 libm 与 binary64 求值，不应硬编码小数尾位作跨平台保证。
2. historical.c：n=20，a=19.5、b=1.5，均值 19.5/21≈.928571；a+b=21，没有超过 10000，故两分位走普通 Beta CDF 二分。区间宽度满足 gate，历史决策可用；这里不能只因 n=20 就省略宽度条件。
3. odds.c→decimal.c：两个完整文法通过，各舍入为精确可表示的 2 和 3。事件阈值 .5、补事件自身阈值约 1/3、换成事件坐标约 2/3。倒数和约 .833333，类别 DOUBLE_POSITIVE_WINDOW；窗口不保证主观区间整体位于其内。
4. decision_geometry.c：主观事件区间 EV≈[-.142857,.5]，补事件概率区间 [.25,4/7]，补事件 EV≈[-.25,.714286]，两侧均 CROSSES_THRESHOLD。S 事件约 .584963，补事件约 .415037，均为有符号半宽倍数；不是概率。
5. historical_analysis.c：在同一 Beta 后验上分别查询 `.5` 与 `1-1/3`。事件后验正 EV 质量接近 1，补事件很小；历史事件 EV 区间为稳健正、补事件稳健负，但两者与主观的关系仍为 UNCERTAIN，因为主观两侧跨阈值。不是 CONFLICT，也不是“主观中心与历史中心不一样所以冲突”。
6. provenance.c：首次实际暴露后 `{true,false}`；下一次 raw 60→70 后 `{true,true}`。该状态不改变前面保存的 s/h/sa/ha；新分析若要使用 70，必须重新调用估计/分析，并另存新修订事实。

上述步次与 compose_analysis 内部顺序一致（组合器接收的是 double，不解析文本，也不转移 provenance）。若历史不可用，条件表达式刻意不读 ha 两侧；给 relation 的占位枚举不意味着那个历史分类真实存在。对照 [state_parity.c::check_composition](../tests/state_parity.c)，其中正常结果逐字段与分步调用相等；错误时比较不变的旧输出，二者不是同一比较任务。

<a id="history-states"></a>

## 13. 将同一集成依次放入无历史、稀疏与就绪状态

| 输入 e/c | estimate 成功后的事实 | 后续历史分析 | 合理界面/调用层解释 |
| --- | --- | --- | --- |
| 0/0 | NO_HISTORY；has_estimate=false；两个版本仍有意义 | OK，available=false，甚至不检查坏赔率 | 没有经验估计；不得显示零值占位为 p=0 |
| 1/0 | INSUFFICIENT；有 Beta(1.5,.5) 均值 .75 和宽区间 | OK，available=false | 可以展示估计与不确定性，不能读取历史 EV 两侧 |
| 12/8 | n=20、均值≈.595238；宽度约 .405451> .25，仍不足 | OK，available=false | 已到样本下限但精度门槛未过；不是函数失败 |
| 19/1 | n=20、均值≈.928571；宽度达标 | OK 且 available=true（赔率也有效） | 只说统计就绪；来源可比性仍需外部审核 |

对 0/0 和 1/0，单历史分析器可以忽略 NaN 赔率；完整组合器却仍返回 ODDS_RANGE，因为主观分析需要赔率。这是两条调用路线的职责差异，不能以“统一错误风格”消掉短路。后验存在与可做历史决策是独立问题，故不要用 `s==OK` 代替三层条件：估计 has_estimate、gate state、分析 available。

主观独立流程不读取 e/c：raw=0 与 raw=1 都用 p=.01，但 raw 身份不同；raw=100 用 .99。调用者应保留 raw 的输入事实。暴露之后从 raw 0 改到 1，尽管数学输入相同，provenance 仍算修订；从 1 改回 0 不清除 compromised。没有“撤销看到证据”的 API。

<a id="interpretation"></a>

## 14. 六种输出分别回答不同问题

| 输出 | 它回答什么 | 它不回答什么 |
| --- | --- | --- |
| probability | 主观规则的中心或 Jeffreys 后验均值 | 不是两个模型融合后的最优值 |
| lower/upper | 该模型定义的区间 | 主观区间不是抽样置信区间；历史可信区间也不是下一次 0/1 结果的区间 |
| statistically_ready/state | 历史样本/区间宽度过 gate 吗 | 不证明独立、无偏、适用、可迁移 |
| positive_ev_probability | 模型下未知 p 落在正 EV 区域的后验质量 | 不是未来事件概率、下注获胜频率或保证获利 |
| ev.state | 给定赔率，整个区间是否严格越过 epsilon | 不由 center 的正负单独决定，不是概率评分 |
| model_relation | 两个可用模型的 EV 分类如何相对 | 不裁决谁正确，不创建第三个概率 |

实际应用应同时呈现 availability 与模型标签，避免把空白数值填成 0。若要长期存储，保存输入、版本、有意义字段和可用性；当前对象可被赋值复制，不借用库内部缓存。数据库事务、修订 ID、结果兑现、训练记录与 UI 状态都属于外部应用。

<a id="handoff"></a>

## 15. 生命周期、资源与 AI 维护交接

运行时不 malloc、不发起 I/O，没有 init/shutdown，也没有藏在全局的历史。通常标量操作成本固定，但 Beta 求解有明确迭代/积分上限；赔率字符串可任意长，完整文法扫描至少随长度增长。无堆分配不等于无栈使用、无 libm 成本或硬实时保证。不同调用者对象可重入；同一对象并发写仍是 C 数据竞争。库不替调用者恢复浮点环境，也不承诺 fast-math/FTZ 等任意环境保持现行数值契约。

输出对象只需正常 C 对齐、足够大小且在调用期间存活。除 provenance 的完整同对象别名外，不利用强制类型转换制造不同结构之间的部分重叠；没有这种别名的公共保证。字符串结束符必须可读；空字符串可被拒绝，但缺少结束符的无效内存不是可安全检测的文法错误。

| 要改的子系统 | AI/维护者先读 | 源码和最小相关验证 | 必须先问清的边界 |
| --- | --- | --- | --- |
| 主观模型/宽度 | API §4.2–4.3、内部 §3、行为规范 | subjective.c、oracle_parity/check_subjective | 是数值求值还是新模型？不得改冻结半宽冒充修复 |
| 历史/gate/Beta | API §4.4/4.11、内部 §4–7、数值契约 | historical/beta/beta_logit/gamma、large_numerics | 计数表示、分位分辨率、独立参考与 gate 分开 |
| 赔率文本 | API §4.5–4.6、内部十进制章节 | odds/decimal、decimal_parity | 文法、舍入和公共范围三个层次都保持 |
| 决策 | API §4.7–4.11、内部 §9 | geometry/policy/两分析器、analysis_parity | EPS、补事件坐标、S 可用性与不融合 |
| provenance/组合 | API §4.12–4.13、PROVENANCE | provenance/composition、api_contract/state_parity | 旧暴露因果与失败不提交，不加入工作流 |
| 安装/未来功能 | 验证指南、CONTRIBUTING、账本 | CMake/consumer/CI 静态检查及获准测试 | 未批准提案不实施；版本/tag/release 需独立授权 |

排错时先记录具体 API、输入、状态、字段可用性和环境；随后按内部指南的 helper 路线定位，最后按验证指南复现。不要先改 oracle 或输出常量。若单项输入都合理而组合失败，应检查多错误优先级与返回状态，不猜测是哪一个模型“更不可靠”。

## 16. 后续维护要求

改公共 API/字段、行为、内部调用、数学或数值求值、校验错误、测试/夹具、CMake、平台、版本/兼容性/发布行为，必须在同一分支/PR 更新受影响的四篇指南、权威契约、README 导航与账本。删除或改写过时描述，明确历史与现行差别；没有文档影响时说明依据。检查 API 对齐、实际测试断言、链接和所有者批准边界；绿色测试不证明文档准确。这是维护政策，不是已实现的 CI 强制机制。账本 ID 不复用、不删除；解决/延期/拒绝均保留决定与证据。详见 [CONTRIBUTING](../CONTRIBUTING.md) 和 [AGENTS](../AGENTS.md)。
