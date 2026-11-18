# Preview 调用方参考：100 小时设备历史证据

这是隔离的参考实现，供验证 [Phase I 证据规则](HISTORICAL_EVIDENCE_RESEARCH.zh-CN.md) 和 [Phase II 模型比较](PREVIEW_PROBABILITY_MODELS.zh-CN.md) 的窄范围用例。原始实现提交为 `47e7ca52616e1eeabe2ddeba1fbbe8382101b006`，经 PR #14 合入 `27d18c0611a73b96596552ad967b94222b24a5ad`。原实现起点是 `5778633615f90c8ee1b134e5f61e46301cdccc39`。接口随 Preview 审查演进。稳定 C11 库的安装、行为、模型、ABI 与数值语义由 [现行契约](API.md) 定义。函数、实际断言、故障注入与 CI 分工见[验证地图](IMPLEMENTATION_VALIDATION.zh-CN.md#preview-device-history-validation)。

## 输入和纳入规则

目标是 **符合资格的物理设备在一个完整观测的 100 小时运行周期内发生故障**。每周期只计一个布尔结果。输入 `Observation` 中 `failed=True/False` 都要求全时距的结果已完全确认，`None` 或 50 小时随访不算补事件。实验中的“故障”不外推到未经审查的真实设备、其他时距或删失模型。用统一非负整数小时坐标提供周期开始、结果可用时间、分析截止。结果可用时间包含入库和结果修订时刻。调用方要保存当时可得的版本，禁止把事后更正回填到早期快照。

| 输入 | 内容与责任 |
|---|---|
| `Batch(Scope(...), rows)` | 源/目标分别给出总体、快照、修订、设备/工艺版本及载荷条件。范围命名与快照引用是真实的数据管理责任，供复验本次输入。 |
| `Observation` | 全局统一的物理设备键、设备内周期键、全局簇键、查询键、low/high 层、时间、结局、时距、工艺条件、事件和观察单位。跨查询的规范键是 (device, cycle)，各命名空间必须提前对齐。 |
| `Declaration` | 适用判断、明确假设、指向论证的编号和类别（`caller_declaration` 或 `caller_supplied_audit`）。在提供给本次源/目标批和截止的前提下，调用方为抽样、可比性、目标支持、完整观察与独立性负责。即使提供的是审计引用，本组件也只保存声明，未独立读取或认证它。 |
| `weights=(w_low,w_high)` | 仅标准化使用，固定已知目标总体权重。实数须有限、非负且各自≤1，和与 1 的偏差不超过 1e−12，允许该范围内的舍入归一化。0 权重层不贡献概率。每个正权重层必须有至少一个合格单位。 |

`review(path, target, declaration, cutoff_hour=..., source=..., weights=...)` 是计数入口。使用整数小时，能确认在截止时间之后才可用的行先排除，连结局和身份都不读取。截止内行逐条检查范围、已知身份及完整性。单一角色内同快照同键的两条记录仅查询键不同，可折叠为一个观察；任何实质字段冲突均拒绝。跨源/目标重叠拒绝。若多个真正不同周期共享物理设备或不同观察共享同一簇，保留原输入，弃权整个请求。这个保守约束也适用于零权重层，语义或依赖检查没有隐式豁免。

`Review` 返回适用性、原因、原声明、范围、截止、端点/层/证据版本、归一权和每批审计计数。每批 `presented` 等于 `after_cutoff + duplicate_aliases + zero_weight + included + withheld`。拒绝时 `included=0` 且 `counts=None`，`withheld` 包含未检查及暂扣记录。审查给出第一个明确原因，调用方可以用相同数据排查后重试。状态表示本次模型和范围，而非给来源评级。

| 适用性 | 示例原因 | 输出 |
|---|---|---|
| supported | `eligible_under_supplied_assumptions` | 可用计数，仍须处理 v1 gate 或数值失败 |
| conditional | `declaration_conditional`、`incomplete_outcome`、`unmodelled_dependence`、`missing_stratum_support` | 显式弃权 |
| incompatible | `declaration_incompatible`、`assumption_mismatch`、`strict_disallows_source`、`scope_regime_mismatch`、`weights_require_standardization`、`invalid_weights`、`unknown_stratum`、`endpoint_mismatch`、`observation_regime_mismatch`、`invalid_outcome`、`invalid_observation_time`、`source_target_overlap`、`observation_conflict`、`count_range` | 显式拒绝 |
| unknown | `cutoff_unknown`、`scope_unknown`、`declaration_evidence_unknown`、`declaration_unknown`、`source_required`、`availability_time_unknown`、`observation_identity_unknown`、`observation_context_unknown`、`weights_unknown` | 缺证据，显式弃权 |

`declaration_evidence_unknown` 表示声明枚举、引用或证据类别缺失/无效。`declaration_unknown` 专指格式有效但调用方明确声明 `Applicability.UNKNOWN` 的情况。检查顺序为截止、范围/声明/路径、权重、逐记录可用时刻、字段校验、身份/依赖、支持或计数范围。输入使用定义的 Python 类型；它不是任意 JSON 的校验器。

## 三条路径和结果含义

| 路径 | 声明条件与操作 | 结果 |
|---|---|---|
| `Path.STRICT` | 目标单位独立且共享同一个目标 Bernoulli 参数。源批不可提供。 | `estimate_v1(receipt, executable_path)` 运行单独构建的 [C 消费者](../integrations/device_history/v1_consumer.c)，链接安装后的 `ProbSpan::probspan` 并调用 `probspan_history_estimate()`。 |
| `Path.POOL` | 提供来源且其工艺和条件一致。对源和目标联合作独立性、真实共享同一参数的声明。 | 同一 v1 入口。目标零观察时，只有得到对应共享声明且来源检查通过才可使用合格来源。 |
| `Path.STANDARD` | 目标内（或在各层内合并已声明可比的源和目标）有独立 Bernoulli，层内共享各自 p，跨层后验独立。按目标权而非样本份额加权。 | `standardize(receipt)` 返回 `target_parameter_posterior`、算法、工具版本、数值预算、状态及可选估计。 |

v1 返回自己的产品、ABI、历史模型和 gate 版本。已审查的空目标历史可以真正传 (0,0) 而返回 `NO_HISTORY`，其中估计为 JSON null。非空且 gate 不达给 `INSUFFICIENT` 和数值，达标给 `VALID`。证据不可用时不会调用 C。进程失败、无兼容协议返回 `consumer_failure`；稳定 C API 错误为 `c_failure` 及其数字状态。消费者文件必须是调用方信任、由指定安装构建的本地执行文件。

标准化没有 v1 gate，也没有给出未来单次或批量结果的预测区间。它返回的中央 95% 区间是参数 q 的后验分位数，不能当作主观范围。v1 历史分析从计数重建单个 Beta，严禁将此结果塞入 `probspan_analyze_historical()`。如果未来有正 EV 尾概率需求，须从对应 q 后验另行计算。当前实现不提供 EV 接口。两路径调用错误或回执不可用时返回 `unavailable_review`。标准化的 `estimate` 仅在 `ok` 时存在；`invalid_numerical_budget`、`numerical_range`、`numerical_budget_exhausted`、`beta_grid_failure`、`beta_quantile_failure`、`cdf_failure`、`cdf_bracket_failure`、`invalid_numeric_result` 保留回执并隐藏估计。

## 标准化数学与失败

各层后验为独立 `Beta(a_h,b_h)`，其中 `a=e+1/2`、`b=c+1/2`。精确模型下 `E[q]=Σ w_h a_h/(a_h+b_h)`、`Var(q)=Σ w_h² a_h b_h / ((a_h+b_h)²(a_h+b_h+1))`。对较小权重对应的层 X，写成 `F_q(t)=E[F_Y((t−w_X X)/w_Y)]`，参数超出 [0,1] 时 CDF 为 0/1。用较小权重积分可限制每箱移位，除数至少 1/2。

用 X 的等概率分位网格划 N 个箱。因被积函数随 X 单调下降，箱左端的条件 CDF 均值是上界、右端的均值是下界，精确函数下两者差不超过 1/N。反演 CDF 上界得到分位下界，反演下界得到上界。SciPy 估计网格和 CDF，检查网格递增、逆函数回代误差和有限值，概率端留 2e−9 浮点裕量。该裕量是实现检查，不是对第三方浮点库的形式证明。每尾以 42 次二分求数值包络，N 从 256 倍增，默认最多 262,144。两端各自包络宽≤2e−5 才报告中点及两包络。在精确 CDF 下，中点离真实端点最多半个包络宽。零权重走单 Beta 反 CDF；正权重层至多 10,000 行（零权重记录先排除），这些是此 Preview 的成本/验证边界。数值预算耗尽、超范围或数值检查失败时 `estimate=None`，仍返回审查收据和具体状态。分箱开销至多 O(N) 临时空间和 O(N×反演次数) 的求值。

独立测试用有理数核算均值/方差，从 arcsine CDF 的递推得到半整数形状 CDF，再以 `x=sin²(θ)` 消除端点奇性，独立做自适应积分和求根。该路径没有调用生产参考的等质量分箱或 Beta 反 CDF。它验证两个已知异质权重配置及极端 (0,1)/(1,0) 小样本，另核查零权重退化。Phase II 的混合偏移首重复用原生成器转成同义设备周期，均值及区间与早先 Monte Carlo 方法交叉验证；后者属于兼容交叉检查。

| 真值核对 | 权重 | 当地实测结果 |
|---|---|---|
| 2/20、9/20 | .8/.2 | 均值 .185714285714，方差 .003501339930，95% 区间约 [.09364387,.32294513] |
| 2/20、9/20 | .2/.8 | 均值 .385714285714，方差 .007397443826，95% 区间约 [.22243660,.55598859] |
| 0/1、1/1 | .5/.5 | 均值 .5，方差 .03125，两尾约 [.13648981,.86351020]；独立求根落于包络。将预算限为 256 时显式返回 `numerical_budget_exhausted` |

复核时发现早期的 65,536 分箱上限无法为极端小样本闭合包络，保持端点宽容差并增加有限预算。最终该例在 131,072 分箱达到要求，低预算失败测试继续验证拒绝路径。

## 构建、运行与复验

从仓库根执行下列命令，Python 3.13 与隔离依赖目录只供参考和测试。C 部分的生成器可以按平台替换。Windows MinGW 示例：

```powershell
$preview = Join-Path $env:TEMP 'probspan-device-preview'
python -m pip install --target "$preview/deps" -r integrations/device_history/requirements.txt
$env:PYTHONPATH = "$preview/deps"
cmake -S . -B "$preview/core" -G 'MinGW Makefiles' -DBUILD_TESTING=ON -DPROBSPAN_BUILD_EXAMPLES=ON -DCMAKE_BUILD_TYPE=Release
cmake --build "$preview/core" --parallel 4
ctest --test-dir "$preview/core" --output-on-failure
cmake --install "$preview/core" --prefix "$preview/install"
cmake -S integrations/device_history -B "$preview/device" -G 'MinGW Makefiles' "-DCMAKE_PREFIX_PATH=$preview/install"
cmake --build "$preview/device" --parallel 4
$env:PROBSPAN_DEVICE_CONSUMER = "$preview/device/device-history-v1.exe"
python -B -m integrations.device_history.example $env:PROBSPAN_DEVICE_CONSUMER
python -B -m unittest -v integrations.device_history.test_device_history
```

候选源码附带的消费者从干净前缀查找 `ProbSpan 1.1.0 EXACT`。适配器检查产品字符串 `1.1.0-rc.1`，ABI、历史模型与 gate 各为 1。任一不符返回 `consumer_failure`，数值结果不可用。根安装不引入 Python、NumPy 或 SciPy。

Linux 可用默认 CMake 生成器，消费者文件名没有 `.exe`。Visual Studio 多配置生成器需在 build/install/test 时选同一配置，消费者在相应配置子目录。合成示例会输出 audit、版本、两次 v1 数值和标准化估计。独立参考及候选实现为 [测试](../integrations/device_history/test_device_history.py) 和 [标准化](../integrations/device_history/standardization.py)。本地实际环境为 Windows x64、GCC 16.2.0 UCRT64、CMake 4.4.3、Python 3.13.14、NumPy 2.4.4、SciPy 1.17.1。主库 Release 14 项（含 9 个 C 执行及 5 个 fixture 检查），既有安装消费者 1 项，新增参考测试和示例均实跑。独立 CI 工作流构建安装消费者并跑这些参考测试。其余 CI 状态以实际提交为准。

回放时持久化有意义的字段（示例用 dataclasses 转 JSON），同时保留原始批快照、观察键与版本、引用的声明和目标权重、原生消费者及构建来源摘要、数值环境和输出包络。收据只记录本次决策和行数，不代替原始证据。Python 收据是应用数据值，调用方应直接使用 `review()` 结果并保存输入。不要将收据当授权、签名或长久文件格式。

此实现只支持合成测试所定义的端点、两层固定权、保守独立检查。真实可交换性、隐性跨簇依赖、机制漂移、选择偏差、外部标签、权重估计不确定性和设备现场适用性仍需论证。保留 [永续账本](TECHNICAL_DEBT.zh-CN.md) 中的借用、持久化与数值候选；无需先建设数据库、自动模型选择或通用持久化接口。
