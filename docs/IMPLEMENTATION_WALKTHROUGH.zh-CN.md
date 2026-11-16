# ProbSpan 源码导读：从输入到分析事实

## 阅读基线与导航

本文对应 `fdfaddfb58486004ee1cc02c0f4a5c640cd17c7c`（已发布 v1.0.0），审查日期 2026-11-16。后续文档提交不代表数学模型更新。公共声明以 [probspan.h](../include/probspan/probspan.h) 为准，行为与数值约束分别见 [行为规范](BEHAVIOR_SPEC.md)、[数值契约](NUMERICAL_CONTRACT.md)。源码与契约出现分歧时应报告，不把解释文档当成修改契约的授权。

建议顺序：本篇 → [完整 API](IMPLEMENTATION_API_REFERENCE.zh-CN.md) → [内部实现](IMPLEMENTATION_INTERNALS.zh-CN.md) → [验证与证据](IMPLEMENTATION_VALIDATION.zh-CN.md)。研究与未实现能力查 [永久账本](TECHNICAL_DEBT.zh-CN.md)。四篇分工参考 [LayerKeySort 的文档导航](https://github.com/RXY712200/LayerKeySort/tree/13998b0682e56f34b401773f754e6d2c88c51206/docs)，只借鉴组织方式，不借用其排序算法或保证。

## 1. 产品解决什么问题

ProbSpan 是静态链接的 C11 概率不确定性与决策分析内核。给定主观百分数、调用者整理好的二元历史计数以及包含本金的总回报赔率，它分别计算两个模型的区间，再把同一赔率映射到 EV 区间和分类。它不训练通用预测模型、不获取数据库记录、不保存分析、不管理界面、不融合两个概率，也不替用户作决策。

适用场景是“明确事件、互斥且穷尽的补事件、同一观察单位和条件下的计数、线性单位成本回报”。例如同一流程下产品合格/不合格、同类试验成功/失败，前提是调用者已经论证可比性。数据库的一行可能是重复记录、未完成观察、不同时间窗或同一人的相关行为，不能因其有 0/1 字段就自动视为独立 Bernoulli 观察。`PROBSPAN_VALID` 只表示冻结统计门槛达标，不是历史可迁移性的证书。

主观模型与历史模型的“独立”表示计算路径不互相修改参数，不表示库能证明用户没有看过历史。后者需要调用者如实报告实际证据暴露，由 provenance 记录。计算结果不能替代领域验证。

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

产品版本宏为 1.0.0，`probspan_abi_version()` 返回 1；主观模型、历史模型、gate、赔率分析版本目前也分别为 1，但含义独立，不能用一个整数替代所有版本。原始结构含 padding、枚举与平台布局，不能直接 fwrite 当作跨版本持久格式。保存有含义字段、可用性和独立版本，历史重放不能默默用新版重算覆盖旧事实。

## 10. 新维护者的阅读与调试路线

先读公共头与本篇，再按症状定位：raw/clamp 查 subjective；计数/可用性查 historical；极端后验查 beta/beta_logit/gamma；文本末位不符查 odds/decimal；补事件方向或 EV 边界查 decision_geometry/policy；S 查 subjective_analysis；历史阈值质量查 historical_analysis；暴露顺序查 provenance；多错误优先级查 composition。每次沿 [源码—断言映射](IMPLEMENTATION_VALIDATION.zh-CN.md) 找到对应测试，区分“公式错误”“浮点表示限制”“不可用正常结果”“输入语义不足”。

## 11. 后续维护要求

改公共 API/字段、行为、内部调用、数学或数值求值、校验错误、测试/夹具、CMake、平台、版本/兼容性/发布行为，必须在同一分支/PR 更新受影响的四篇指南、权威契约、README 导航与账本。删除或改写过时描述，明确历史与现行差别；没有文档影响时说明依据。检查 API 对齐、实际测试断言、链接和所有者批准边界；绿色测试不证明文档准确。这是维护政策，不是已实现的 CI 强制机制。账本 ID 不复用、不删除；解决/延期/拒绝均保留决定与证据。详见 [CONTRIBUTING](../CONTRIBUTING.md) 和 [AGENTS](../AGENTS.md)。
