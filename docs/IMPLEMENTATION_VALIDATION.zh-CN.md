# ProbSpan 验证地图与可复现证据

下文第 1–13 节保存 v1 的源码映射与历史执行记录。合并的 [Preview 设备历史参考](PREVIEW_DEVICE_HISTORY.zh-CN.md) 使用独立的依赖和工作流，见[第 14 节的 RC 证据及断言地图](#preview-device-history-validation)。

## 1. 审查基线和证据等级

源码基线 `fdfaddfb58486004ee1cc02c0f4a5c640cd17c7c`，v1.0.0；文档审查/本地执行日期 2026-11-16。本篇与 [导读](IMPLEMENTATION_WALKTHROUGH.zh-CN.md)、[API 参考](IMPLEMENTATION_API_REFERENCE.zh-CN.md)、[内部实现](IMPLEMENTATION_INTERNALS.zh-CN.md)、[永久账本](TECHNICAL_DEBT.zh-CN.md) 交叉使用。权威数值要求在 [NUMERICAL_CONTRACT.md](NUMERICAL_CONTRACT.md) 和 [numerical_policy.json](../oracle/numerical_policy.json)，不是本篇另定容差。

| 等级 | 本次依据 | 不可据此宣称的内容 |
| --- | --- | --- |
| 源码审查 | 公共头、全部 14 C/9 私有 H、CMake、CI、示例、consumer、参考生成器与现有规范 | 仅阅读不等于执行通过 |
| 断言审查 | 下表测试函数及比较规则 | 有断言不等于覆盖所有输入 |
| 初轮本地实际执行 | 初轮文档提交 1a864b4：Windows x64 MSYS2 UCRT64 GCC 16.2.0，14/14、C-only 9/9、安装 consumer 1/1 | 第二轮运行独立记录在下文，不复制初轮结果冒充复测 |
| 历史 CI | [run 39358543092](https://github.com/RXY712200/ProbSpan/actions/runs/39358543092)，API 查得 completed/success，head_sha 与基线相同 | 不把历史运行说成本次重新运行 |
| 未验证/研究限制 | ARM/嵌入式/替代 libm、任意浮点标志、无限输入域、实际历史适用性 | 没有形式证明、普适预测保证或任意架构逐位相同保证 |

[正式发布](https://github.com/RXY712200/ProbSpan/releases/tag/v1.0.0) API 检查得到 ID 417950498，published_at=2026-10-20T02:50:24Z，draft=false、prerelease=false。这是既有发布证据，不是本次文档操作发布。

## 2. CMake 构建图与测试数量

v1.0.0 基线的 [根 CMake](../CMakeLists.txt) 最低 3.16，项目版本 1.0.0，`probspan` 为 STATIC、C11 required、关闭 C extensions。构建树 alias 与安装导出名均为 `ProbSpan::probspan`。非 MSVC 公共链接 m；警告选项 MSVC /W4，其他 -Wall -Wextra -Wpedantic。安装仅导出公共头、静态 archive、CMake targets/config/version，版本配置 SameMajorVersion；私有头不安装。

`BUILD_TESTING` 由 CTest 控制，默认 ON；`PROBSPAN_BUILD_EXAMPLES` 默认 OFF。Python3 Interpreter 仅影响五个 fixture freshness 测试，不影响 C 库本身。七个基本 C 测试始终在 BUILD_TESTING 下注册；examples ON 再加两个，发现 Python 再加五个。因此常规 examples ON+Python=14；C-only examples ON=9；C-only examples OFF=7。consumer 是独立 CMake 工程，另有 1 个 CTest，不能与根测试数混算。

## 3. 源码到具体断言的完整映射

下表中的测试名为可执行目标/CTest 名加 `probspan_` 前缀（consumer 除外）。测试文件里的 static 函数名是定位入口，不是公共库 API。

| 生产模块/契约 | 测试文件与函数 | 关键断言 |
| --- | --- | --- |
| probspan.c、版本常量 | [smoke.c](../tests/smoke.c)、[api_contract.c](../tests/api_contract.c) main、[consumer/main.c](../tests/consumer/main.c) | ABI=1、产品宏、组合嵌套版本，公共安装头可消费 |
| subjective.c、subjective_input.h、probability_math.h、model_v1.h | [oracle_parity.c](../tests/oracle_parity.c) `check_constants/check_subjective/check_api_arguments` | 25 常量、101 raw、16 半宽、边界与拒绝；离散精确、数值容差 |
| historical.c、history_model_private.h | oracle_parity `check_history`；[large_numerics.c](../tests/large_numerics.c) `check_reference/check_stress` | 13 普通历史、计数/版本/gate、极大样本和有估计标志 |
| beta.c、beta_private.h、gamma.c、gamma_private.h | oracle_parity `check_beta_cdf`；large_numerics `stress_pair/check_quantile_bracket/check_complement` | CDF 单调/互补、逆函数邻接夹逼；Gamma 通过 Beta 归一化路径受测，不是独立全域 Gamma 证明 |
| beta_logit.c、beta_logit.h | large_numerics 同上；[analysis_parity.c](../tests/analysis_parity.c) `check_histories` | 28 独立历史、140 CDF 探针、极端阈值质量，避免沿用错误 SciPy 极端参考 |
| odds.c、decimal.c、decimal_private.h | oracle_parity `check_odds`；[decimal_parity.c](../tests/decimal_parity.c) `check_vectors/stream_vectors` | 完整 ASCII 文法、范围、错误不写输出、41 位向量、舍入模式与 locale；流式入口供差分工具 |
| decision_geometry.c、decision_private.h | analysis_parity `check_ev/check_geometry/check_subjective_side/check_historical_side` | EV 乘减、补事件端点方向、三种赔率几何 |
| decision_policy.c | analysis_parity `check_classifiers`；api_contract `check_precedence_and_safety` | 22 EV、33 combination、12 relation；epsilon 严格边界、非法枚举、不可用优先 |
| subjective_analysis.c | analysis_parity `check_subjective/check_arguments` | 742 主观组合、S 边界、赔率 1 标志、对象校验、错误输出保持 |
| historical_analysis.c | analysis_parity `check_histories/check_arguments` | 166 普通历史分析、18 修正阈值；非 VALID 在坏赔率前短路、可用字段条件 |
| provenance.c | [state_parity.c](../tests/state_parity.c) `check_provenance`；api_contract `check_provenance_invariant` | 23 冻结转移、原地更新、非法 raw/NULL、compromised=>exposed、畸形旧状态优先 |
| analysis_composition.c | state_parity `check_composition`；api_contract `check_precedence_and_safety` | 926 组合与分步 API 每个有意义字段精确相等；多错误顺序、整体保持 |
| examples、安装接口 | [decision.c](../examples/decision.c)、[provenance.c](../examples/provenance.c)、[consumer](../tests/consumer/CMakeLists.txt) | 示例可构建运行；find_package(ProbSpan 1.0 CONFIG REQUIRED) 与导出 target，无源树 include 捷径 |

分析与组合测试使用字段比较，不把 padding 字节相等当作正常结果语义。错误前后部分测试用 memcmp 检查整个预置输出不变，目的不同。测试不能证明任意手工伪造对象都符合模型，也不检测真实数据是否可比。

## 4. 冻结 oracle 与独立参考链

[oracle/README](../oracle/README.md) 规定原始 Python 模型来自作者 `probability-calibration-tool` 精确提交 `a581f84ccd217ed45789b3566347255f56ffbeac`。`generate.py/generate_decimal.py/generate_analysis.py/generate_state.py` 在 import 前检查 HEAD 与已跟踪文件干净；必须在该参考的锁定环境运行。不能从 C 实现反推期望值。

| 提交参考 | 生成入口 | 语义与消费者 |
| --- | --- | --- |
| [v1_vectors.jsonl](../oracle/v1_vectors.jsonl) | [generate.py](../oracle/generate.py) | 244 行包含多组原始观察；C 普通测试投影为 163 estimate/width/history/odds/domain 向量与 25 常量，不把总行数等同某单项样本数 |
| [analysis_vectors.jsonl](../oracle/analysis_vectors.jsonl) | [generate_analysis.py](../oracle/generate_analysis.py) | 920 个追加分析案例（另有元数据）；七组赔率、S 阈值、坏赔率短路、分类 epsilon 邻域 |
| [decimal_vectors.jsonl](../oracle/decimal_vectors.jsonl) | [generate_decimal.py](../oracle/generate_decimal.py) | 41 exact-bit 用例，包括次正规、溢出、中点、远端扰动 |
| [state_reference.json](../oracle/state_reference.json) | [generate_state.py](../oracle/generate_state.py) | 冻结 RoundService 隔离执行所得 23 便携转移事实；临时数据库、固定时钟/ID 仅用于开发，不进入 C 核心 |
| [large_reference.json](../oracle/large_reference.json) | [generate_large.py](../oracle/generate_large.py) | 独立 28 历史/140 CDF；mpmath 1.3.0、80 位生成，60 位复核舍入后稳定性 |
| [threshold_reference.json](../oracle/threshold_reference.json) | [generate_threshold.py](../oracle/generate_threshold.py) | 18 极端正 EV 阈值；仅替换冻结 Python 的不一致 Beta 数值求值，保留 EV/gate/分支规则 |

冻结 SciPy 在约 10^18 平衡参数可产生互补 CDF 和约 1.47725、分位数异常及偏斜 NaN，故 [Issue #2](https://github.com/RXY712200/ProbSpan/issues/2) 授权单独高精度参考；这不是模型变更，也不能推广为任意失败都允许换参考。`generate_large.py` 以变换后的真实 Beta 密度作 tanh-sinh 积分（±256），检查归一化、互补与逆残差到 1e-40 级别；不是调用 C 算法自证。阈值数据区分精确整数后验估计和已表示 binary64 的 a/b/阈值，避免把输入表示差异错归为求解误差。

`tests/generate_*_fixtures.py --check` 使用已提交参考检查 C 头新鲜度，Python 标准库即可。它不重新执行原始模型，也不重新生成 80 位参考。高精度生成与冻结应用回归本次未重跑；不能将本地 freshness 通过说成重新确认所有参考计算。

参考维护者可在各自要求的环境运行以下只检查命令（本次只实际运行了 CTest 注册的五个 fixture 检查）。`<frozen-checkout>` 必须是上述精确提交且已跟踪文件干净的参考仓库；不要为检查而更新冻结数据。

```text
python tests/generate_fixtures.py --check
python tests/generate_large_fixtures.py --check
python tests/generate_decimal_fixtures.py --check
python tests/generate_analysis_fixtures.py --check
python tests/generate_state_fixtures.py --check

python oracle/generate.py --reference-root <frozen-checkout> --check
python oracle/generate_decimal.py --reference-root <frozen-checkout> --check
python oracle/generate_analysis.py --reference-root <frozen-checkout> --check
python oracle/generate_state.py --reference-root <frozen-checkout> --check
python oracle/generate_large.py --check
python oracle/generate_large.py --verify-precision
python oracle/generate_threshold.py --reference-root <frozen-checkout> --check
python tests/decimal_differential.py --reference-root <frozen-checkout> --executable <absolute-decimal-parity-executable>
```

最后一组需要冻结参考的锁定依赖；large/threshold 还需要 mpmath 1.3.0。命令可复现性以固定源码、工具版本和精度为前提，不应在缺少环境时把命令未执行写成通过。

## 5. 精确与容差的分界

- 状态、枚举、标志、计数、raw/used、版本、availability 和结构语义精确。
- elementary 数值使用 1e-12 absolute+relative；Beta 数值使用 1e-10 absolute+relative，实际 helper 形式以测试源码和 policy 为准。
- 十进制比较 binary64 位型精确，包括 +0；测试在可设置的四舍入模式下逐位比较。逗号 locale 若未安装会明确输出 unavailable，不能算已验证该 locale。
- 组合和分步同路径结果逐字段精确一致，不要求所有平台的 libm 输出逐位一致。
- 极大参数分位数受 x 的 binary64 邻接间隔限制，用 nextafter 上下邻居夹住目标 CDF，不能要求不可表示的精确实数逆。互补验证考虑 1-x 的舍入，详见 Issue #5。

[decimal_differential.py](../tests/decimal_differential.py) seed=20261006，6099 个案例来自 6000 随机、41 冻结、54 dyadic 扰动和 4 个 100000 字符模式。期望使用冻结 parser 状态和 Python float 位型；调用 decimal_parity 的 --stdin，不是自比自。本次执行了 C 的 41 位向量测试，**未重新执行这套 6099 原模型差分**；历史修复证据见 Issue #3。

large_numerics 的 190 个历史 stress、570 分位数、950 主 CDF 探针覆盖 10^k、2^53 邻域及 INT64_MAX 的平衡/偏斜模式；另有邻接/互补调用，所以 950 不是所有内部 CDF 求值总数。

## 6. 初轮（1a864b4）实际命令与结果

在既有 C: 仓库的忽略目录 `build/` 中执行，未迁移工作区。PowerShell 将 MSYS2 UCRT64 放到当前进程 PATH，使用原生 CMake 与 GCC 16.2.0；未修改全局配置。

```powershell
$env:PATH = 'D:\msys64\ucrt64\bin;' + $env:PATH
cmake -S . -B build/docs-audit -G 'MinGW Makefiles' `
  -DCMAKE_C_COMPILER=D:/msys64/ucrt64/bin/gcc.exe `
  -DPROBSPAN_BUILD_EXAMPLES=ON
cmake --build build/docs-audit -j4
ctest --test-dir build/docs-audit --output-on-failure

cmake -S . -B build/docs-audit-c-only -G 'MinGW Makefiles' `
  -DCMAKE_DISABLE_FIND_PACKAGE_Python3=TRUE -DPROBSPAN_BUILD_EXAMPLES=ON
cmake --build build/docs-audit-c-only -j4
ctest --test-dir build/docs-audit-c-only --output-on-failure
cmake --install build/docs-audit-c-only --prefix "$PWD/build/docs-audit-install"
cmake -S tests/consumer -B build/docs-audit-consumer -G 'MinGW Makefiles' `
  "-DCMAKE_PREFIX_PATH=$PWD/build/docs-audit-install"
cmake --build build/docs-audit-consumer -j4
ctest --test-dir build/docs-audit-consumer --output-on-failure
```

实测分别 14/14、9/9、1/1 通过；C-only 安装包含 archive、公共头和 CMake package，外部 consumer 构建及执行通过。另将导读两个完整 C 示例逐一提取到忽略的 build 目录，以 C11 和上述警告选项针对安装头/archive 编译运行，均成功；history-only 示例输出均值约 .595238、区间约 [.383920,.789371]、ready=0。本次未运行 sanitizer、本机其他编译器或完整原始 Python 回归。曾尝试离线 uvx CMake，因缓存没有该包失败，未进入配置；随后使用已安装原生工具完成上述验证。不要从这个工具入口失败推断源码构建失败。

通用 Linux/macOS 指令用 `cmake -S . -B build -DPROBSPAN_BUILD_EXAMPLES=ON`，再 build/ctest/install；MSVC 多配置需 `--config Debug` 与 CTest `-C Debug`。完整参数和路径说明见 [安装指南](BUILD_AND_INSTALL.md)。不要照搬本机 D: 工具链路径到其他平台。

## 7. 五个 CI 作业与限制

[ci.yml](../.github/workflows/ci.yml) 是五个作业，而不是五种操作系统：Windows MSVC、Linux GCC、Linux Clang、macOS AppleClang、Linux GCC ASan+UBSan。每个构建库与 examples，CTest，安装，再构建安装 consumer。sanitizer 作业给库和 consumer 配 address,undefined 及 frame-pointer 标志。其成功支持该运行环境的动态检查，不证明线程竞争全无、任意 libm 正确或所有未执行路径安全；没有 TSAN 作业。

当前受支持 CI 组合之外的 ARM64、嵌入式、替代数学库、FTZ/DAZ、其他舍入环境研究保留在 [Issue #6](https://github.com/RXY712200/ProbSpan/issues/6)。禁止以 -ffast-math 编译后仍不加条件地引用冻结契约。

## 8. 失败排查与安全复核

| 失败 | 优先排查 | 不应采取的“修复” |
| --- | --- | --- |
| fixture freshness | 生成器是否按当前提交参考投影，换行与真实 diff | 改 oracle 迎合 C 输出 |
| decimal bit mismatch | 中点尾数、四舍入模式、+0、文法与范围分层 | 放宽为数值近似比较 |
| extreme Beta inverse | 邻接 x 夹逼、参数表示、变换积分收敛 | 直接删掉极大计数支持或套正态模型 |
| state parity | 旧 exposure 因果顺序、raw 与 used、原地错误保持 | 用显示请求代替暴露事实 |
| installed consumer | prefix/config、导出 target、m 传递依赖 | 加源树 include 绕过安装包 |
| API precedence | 实际委托顺序、不可用短路 | 为统一风格无意重排校验 |

未来变更先分类为模型/契约/数值/工程改动，再找断言与 oracle 边界，按最小相关测试验证；必要时扩展独立参考而不是修改期望。记录实际平台、命令、结果与未测层次，最后由独立审查者评价。

## 9. 文档一致性与维护门槛

本次文档检查应分别核对：公共头 13 函数、5 枚举、10 结构及 4 版本宏；14 C/9 H 模块出现；相对 Markdown 文件及本地锚点存在；A01–E48 正式章节各恰一次；README 五入口；变更仅八个授权 Markdown。工具的名称/链接检查不能证明每句话的数学解释正确，仍需逐篇复读和独立审查。

初轮 1a864b4 实际结构检查结果：13 个归一化函数签名与头文件一致，所有枚举值和结构字段标识均在 API 参考出现；生产模块均有映射；289 个相对链接/显式锚点无缺失；Markdown 表格列数与代码围栏检查通过；48 个候选 ID 各一个正式章节，另 4 个 R 修复条目，52 条各有连续 1–18 项；README 五入口及八文件变更白名单检查通过。`git diff --check` 无错误。C 的 decimal 日志实际报告 41 向量、4 个舍入模式、逗号 locale passed。上述计数是初轮快照，第二轮的新增链接需重新计算，不把数字当固定兼容契约。

公共 API/字段、行为、内部调用、数学/数值、错误校验、测试/夹具、CMake、平台、版本/兼容性/发布改变，必须同一分支/PR 更新受影响四指南、权威契约、README 与账本，替换过时解释，区分历史。无文档影响要说明；绿色测试不建立文档准确性，这些政策没有自动新增 CI gate。账本解决记录提交、测试、首次版本、剩余限制，延期/拒绝保留原因，ID 不删除/复用；所有者未批准的功能/模型/发布不得实施。见 [CONTRIBUTING](../CONTRIBUTING.md)。

<a id="assertion-cases"></a>

## 10. 从具体输入走到源码与真实断言

| 场景/最小输入 | 源码分支及应观察结果 | 测试中的实际断言/限制 |
| --- | --- | --- |
| raw=-1 与输出NULL同时存在 | subjective_estimate 先指针，INVALID_ARGUMENT | api_contract/check_precedence_and_safety 直接调用 `(-1,NULL)`；非NULL错误用 UNCHANGED 保存字节对照 |
| raw=0/100 | 保留raw，用1/99计算 | oracle_parity/check_subjective 对 fixture 每个字段/版本；不能只比 probability 忽略 raw |
| e/c=0/0 | historical n==0，无估计 | api_contract 组合 `(0,0,0,1,1)` 检查 has_estimate/available/S flags 与关系；oracle历史向量补充单项 |
| e/c=12/8 | n达20但宽度>.25，仍不足 | 本轮导读示例实测；不属于13个普通history冻结向量。冻结的10/10、18/2等另有同类gate不足断言，不将相似场景覆盖冒充同一个输入 |
| 无历史对象概率设NaN、赔率NaN/-1 | analyze_historical 提前不可用，OK/available=false | analysis_parity/check_arguments 明确设置 history.state=NO_HISTORY，三概率NaN，调用坏赔率检查短路 |
| VALID但has_estimate=false | 分析器对象校验失败、输出不改 | 同 check_arguments 检查 INVALID_ARGUMENT 且预设 historical_output.available 保持true；该断言只直接检查标志，不宣称这里用memcmp检查全部字节 |
| EV恰好±epsilon | 严格不等号，不跨越则CROSSES_THRESHOLD | analysis_parity/check_classifiers 与冻结22向量；普通数值容差不能替代状态精确一致 |
| unavailable + 非法historical枚举 | relation忽略历史枚举，但仍查主观 | api_contract 显式999枚举在 available=false 成功，true失败且relation不改 |
| predecessor={false,true} | provenance不变量早于raw，原地同样失败 | check_provenance_invariant 的 changed/exposed 两布尔笛卡尔积、两种输出别名及非法raw；UNCHANGED比较整对象 |
| 已暴露raw 0→1 | used均1但raw不同，compromised粘滞 | api_contract 先 `(false,false),0→1,subject_changed=true,now=true` 只exposed，再1→0触发compromised；state_parity另含23冻结事实 |
| 极窄大参数分位 | 检查邻接x的CDF夹住q，不强求残差零 | large_numerics/check_quantile_bracket 的 below<=q+1e-10 且 above>=q-1e-10；允许量化，而非放弃逆函数约束 |
| 互补运算丢失tiny x | 按1-x相邻点界验证，往返精确时才查直接和 | large_numerics/check_complement 中 `1-complement==x` 条件保护直接互补恒等式 |
| 精确decimal中点与极长尾 | 位型相等而非close_enough | decimal_parity/check_vectors 用memcpy取uint64位型；stream_vectors输出原转换位型及公共状态，差分工具不由C生成期望 |
| compose失败 | 首错误立即返回，结果字节不变 | api_contract预设0xa5，依次制造raw/count/odds错误，UNCHANGED比全对象；state_parity正常926组合逐字段比较，性质不同 |

测试缺口也需准确：NaN/逆序输入 classify_ev 的表格结果是直接源码推导，不能声称22条向量必然覆盖每个NaN排列；Gamma normalizer主要经Beta间接验证；没有每个static helper独立单测，更没有穷举数学输入。源内失败上限的存在不意味着本轮人为触发了每个数值失败分支。

<a id="reproduce-family"></a>

## 11. 新维护者的最小复现命令

先配置并构建，再用锚定正则运行单个 CTest，避免名称部分匹配带入其他测试。以下是可复现指令菜单，不是声称本轮每条菜单都被重复执行：

```text
ctest --test-dir build/docs-depth -N
ctest --test-dir build/docs-depth -R "^probspan_oracle_parity$" -V
ctest --test-dir build/docs-depth -R "^probspan_large_numerics$" -V
ctest --test-dir build/docs-depth -R "^probspan_decimal_parity$" -V
ctest --test-dir build/docs-depth -R "^probspan_analysis_parity$" -V
ctest --test-dir build/docs-depth -R "^probspan_state_parity$" -V
ctest --test-dir build/docs-depth -R "^probspan_api_contract$" -V
ctest --test-dir build/docs-depth -R "fixture_freshness$" --output-on-failure
ctest --test-dir build/docs-depth-consumer -R "^installed_consumer$" -V
```

Windows 原生exe在单配置目录下，可直接 `build/docs-depth/probspan_decimal_parity.exe`；Linux/macOS去.exe；MSVC多配置通常还有Debug子目录，CTest需`-C Debug`。库没有单独“运行”命令；要运行的是测试/consumer。若只构建目标，可 `cmake --build build/docs-depth --target probspan_large_numerics`，但首次配置仍需有效编译器。

### 11.1 数值失败诊断顺序

1. 固定source SHA、编译器版本、构建类型/flags、double表示与输入。禁用意外fast-math，确认失败属于当前编译产物而非旧prefix。
2. 普通参考失败先看 actual/expected/绝对误差，核对 elementary 1e-12+1e-12*abs(ref) 或 Beta 1e-10+1e-10*abs(ref)。离散状态错即失败，不可因浮点“够近”放行。
3. 大计数先记录原int64、double a/b与x；switch要求两形状>=.5且sum>10000。若CDF中间失败，按普通fraction或logit panel/root路线查iteration、tol/depth、有限性；保持模型与参考不变。
4. 分位失败打印x及 nextafter 两邻居，按check_quantile_bracket看是否夹q；互补失败检查1-x往返是否改变实数输入。不能混合精确整数参数参考与已rounded参数CDF。
5. 十进制失败记录完整输入（长串可另保存长度和哈希）、向量index、fegetround、actual/expected十六进制位型。先区分文法/范围/位型；locale unavailable不等于逗号locale通过。检查远尾非零和+0，不用数值容差掩盖1 ulp错误。
6. 若确有新数值缺陷，先最小复现、独立参考和契约审查，再获批修实现。本次文档范围不授权改源码、夹具或容差。

### 11.2 API/状态失败诊断顺序

先记录函数入口、有效指针和前态字节，再核对第一个校验步骤。组合失败按 raw→count→odds 委托顺序；单历史分析先看state是否VALID；关系先查主观枚举，再按available决定是否看历史。provenance排查old exposed与now是否被混淆、raw是否误用used、非法旧值是否被自动修正。正常值逐字段比较，失败保持才对同一预置对象作字节快照，不能以padding相等认证正常分析。

### 11.3 安装失败诊断顺序

找不到ProbSpanConfig：确认实际install prefix和CMAKE_PREFIX_PATH而非源树目录；inspect安装日志是否含lib/cmake/ProbSpan。找不到header：确认include/probspan/probspan.h并通过导出目标传播目录。链接数学符号失败：确认链接ProbSpan::probspan且非MSVC导出的m依赖未被绕开。多配置找不到archive：配置/build/install/consumer选择同一Debug或Release。旧模型结果：核对运行时ABI与头版本，排除旧prefix/旧exe。不要添加src include路径掩盖package问题。

fixture freshness失败仅说明已提交参考与生成C头不一致；先读diff及生成器输入，不直接运行无--check生成命令覆盖。原Python模型重放需精确HEAD、tracked clean和锁定依赖；mpmath高精度生成又是独立层。基础C-only通过并不证明这些开发环境均已可用。

<a id="depth-results"></a>

## 12. 第二轮深度扩展的实际运行与观察

第二轮从文档commit `1a864b4e0d129f62398d993bffab045fa3740fff` 开始，生产源码仍是 fdfaddfb，所有新增运行产物位于忽略的build/内。原C:仓库未搬移，D:\ProbSpan仍不存在。以下记录与§6初轮执行分开。

```powershell
$env:PATH = 'D:\msys64\ucrt64\bin;' + $env:PATH
cmake -S . -B build/docs-depth -G 'MinGW Makefiles' -DPROBSPAN_BUILD_EXAMPLES=ON
cmake --build build/docs-depth -j4
ctest --test-dir build/docs-depth --output-on-failure
cmake --install build/docs-depth --prefix "$PWD/build/docs-depth-install"
cmake -S tests/consumer -B build/docs-depth-consumer -G 'MinGW Makefiles' `
  "-DCMAKE_PREFIX_PATH=$PWD/build/docs-depth-install"
cmake --build build/docs-depth-consumer -j4
ctest --test-dir build/docs-depth-consumer --output-on-failure
```

本轮上述实际执行为 GCC 16.2.0 / Windows x64：14/14 与安装consumer 1/1通过。导读三个完整C程序均逐一从Markdown提取，以`gcc -std=c11 -Wall -Wextra -Wpedantic`、安装include/archive和-lm编译并运行；未修改原测试。分步程序实际结果如下，打印小数为观察值，不是新增逐位兼容常量：

```text
subjective 0.600000000 [0.428571429, 0.750000000] d=0.693147181
history 0.928571429 [0.789181364, 0.994550967] ready=1
subjective EV event=[-0.142857143, 0.500000000] complement=[-0.250000000, 0.714285714]
posterior positive EV event=0.999995042 complement=0.001130297
relations event=3 complement=3
exposed=1 compromised=1
```

枚举3是PROBSPAN_UNCERTAIN，不能称为CONFLICT。history-only程序均值.595238、区间[.383920,.789371]、ready=0，与n到20但宽度未达标一致。本轮尚未重放冻结Python、6099原parser差分或80/60位独立参考；本地未运行ASan/UBSan/其他架构。新PR自动CI若运行，是远程证据，必须以其实际head SHA和状态另查，不替代这些记录。

本轮还实际执行独立C-only配置`build/docs-depth-c-only`（`-DCMAKE_DISABLE_FIND_PACKAGE_Python3=TRUE -DPROBSPAN_BUILD_EXAMPLES=ON`），build后CTest 9/9通过。API指南的CMake片段与history-only main.c组成临时消费者，以安装prefix配置/build/运行成功；另将工程改为LANGUAGES CXX、main.cpp、CXX_STANDARD=11，GNU C++ 16.2.0编译链接同一C静态库并运行成功。这两个临时工程都在忽略的build/docs-depth下，没有改仓库consumer测试或新增永久源文件。C++这一个实例不证明全部C++编译器/ABI组合。

### 12.1 重现三个Markdown完整程序的提取/编译

以下在仓库根执行（Python脚本中的gcc路径是本机实例，其他平台需替换）。它只写忽略的build目录，不生成/改写oracle：

```python
from pathlib import Path
import re
import subprocess

guide = Path("docs/IMPLEMENTATION_WALKTHROUGH.zh-CN.md").read_text(encoding="utf-8")
out = Path("build/docs-depth/examples")
out.mkdir(parents=True, exist_ok=True)
for i, code in enumerate(re.findall(r"```c\n(.*?)```", guide, re.S), 1):
    source = out / f"walk-{i}.c"
    source.write_text(code, encoding="utf-8")
    executable = source.with_suffix(".exe")
    subprocess.run(["D:/msys64/ucrt64/bin/gcc.exe", "-std=c11", "-Wall",
        "-Wextra", "-Wpedantic", "-Ibuild/docs-depth-install/include", str(source),
        "build/docs-depth-install/lib/libprobspan.a", "-lm", "-o", str(executable)], check=True)
    subprocess.run([str(executable.resolve())], check=True)
```

`re.findall` 针对本导读完整 c 围栏，API签名围栏不参与；未来若导读加入非完整片段，要调整提取规则而非声称所有围栏均可独立编译。显示终端如出现编码乱码，先核对原Markdown为UTF-8与终端编码；不得为修终端输出转换/损坏文档内容。

<a id="depth-audit"></a>

## 13. 第二轮审查清单、逐轮修补与可复算覆盖

### 13.1 清单规则与当前参考

Pass 0在大段编辑前按公共头、全部生产函数/私有头、七个C测试断言、oracle/数值政策、CMake/示例/consumer、维护规则与52账本条目建立下列80项：CRITICAL 30、CORE DEPTH 36、SUPPORTING DEPTH 14。按有实质解释且有证据指针记1，否则0；只出现函数名不计覆盖。分母不是“所有可能知识”，比例不是正确概率或独立PASS。某项内部发现新反例/次序限制仍纳入该项原有语义验收，不删项抬分；若出现不同的新增重要要求应另加ID再重算。

本轮直接取当前LayerKeySort GitHub默认分支四文件，记录返回blob以避免与其文中自己的生产基线混淆：

| 文档 | 当前读取的Git blob |
| --- | --- |
| WALKTHROUGH | `1e5bdce013cd7ed644771ea98be63fa474243296` |
| API_REFERENCE | `af6728f880ff4b81b752a670ac0e1130e6532551` |
| INTERNALS | `767a4688cf98a13c938949f948c97134b0d3bb18` |
| VALIDATION | `a15165adbb6580db7427ccc3541cf8ff6347dd62` |

借鉴的是按真实操作展开、helper不变量、所有权边界、具体断言及未测范围分开陈述；其Full源码基线70d7f0ef与本项目fdfaddfb不是同一对象，不复制排序机制、内存保证或测试数量。

### 13.2 完整二值清单

P0初始；P1扩写后；P2新维护者问答修补后；P3跨文档修补后；P4最终一致性回归。每行按同一标准，数字1表示本清单意义的covered，0表示not-covered。最后两轮均不代表独立验收。

| ID | 类别 | 必须回答的实质问题 | P0 | P1 | P2 | P3 | P4 | 证据指针 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C01 | CRITICAL | abi_version 的数值、生命周期与无错误路径 | 1 | 1 | 1 | 1 | 1 | [API §4.1、正反例](IMPLEMENTATION_API_REFERENCE.zh-CN.md#call-cases)；对应实现/断言见本篇§3/§10 |
| C02 | CRITICAL | subjective_half_width 的域、NULL 优先级和边界 | 1 | 1 | 1 | 1 | 1 | [API §4.2、正反例](IMPLEMENTATION_API_REFERENCE.zh-CN.md#call-cases)；对应实现/断言见本篇§3/§10 |
| C03 | CRITICAL | subjective_estimate 的 raw/used、失败保持 | 1 | 1 | 1 | 1 | 1 | [API §4.3、正反例](IMPLEMENTATION_API_REFERENCE.zh-CN.md#call-cases)；对应实现/断言见本篇§3/§10 |
| C04 | CRITICAL | history_estimate 的计数域、求解失败与 gate | 1 | 1 | 1 | 1 | 1 | [API §4.4、正反例](IMPLEMENTATION_API_REFERENCE.zh-CN.md#call-cases)；对应实现/断言见本篇§3/§10 |
| C05 | CRITICAL | odds_validate 的有限/范围与输出 | 1 | 1 | 1 | 1 | 1 | [API §4.5、正反例](IMPLEMENTATION_API_REFERENCE.zh-CN.md#call-cases)；对应实现/断言见本篇§3/§10 |
| C06 | CRITICAL | odds_parse 的文法→转换→范围 | 1 | 1 | 1 | 1 | 1 | [API §4.6、正反例](IMPLEMENTATION_API_REFERENCE.zh-CN.md#call-cases)；对应实现/断言见本篇§3/§10 |
| C07 | CRITICAL | classify_ev 的非校验行为 | 1 | 1 | 1 | 1 | 1 | [API §4.7、正反例](IMPLEMENTATION_API_REFERENCE.zh-CN.md#call-cases)；对应实现/断言见本篇§3/§10 |
| C08 | CRITICAL | classify_odds_combination 的临界带 | 1 | 1 | 1 | 1 | 1 | [API §4.8、正反例](IMPLEMENTATION_API_REFERENCE.zh-CN.md#call-cases)；对应实现/断言见本篇§3/§10 |
| C09 | CRITICAL | classify_model_relation 的枚举与可用性优先 | 1 | 1 | 1 | 1 | 1 | [API §4.9、正反例](IMPLEMENTATION_API_REFERENCE.zh-CN.md#call-cases)；对应实现/断言见本篇§3/§10 |
| C10 | CRITICAL | analyze_subjective 的对象局部校验与 S | 1 | 1 | 1 | 1 | 1 | [API §4.10、正反例](IMPLEMENTATION_API_REFERENCE.zh-CN.md#call-cases)；对应实现/断言见本篇§3/§10 |
| C11 | CRITICAL | analyze_historical 的短路和后验质量 | 1 | 1 | 1 | 1 | 1 | [API §4.11、正反例](IMPLEMENTATION_API_REFERENCE.zh-CN.md#call-cases)；对应实现/断言见本篇§3/§10 |
| C12 | CRITICAL | provenance_transition 的不变量/别名/旧暴露 | 1 | 1 | 1 | 1 | 1 | [API §4.12、正反例](IMPLEMENTATION_API_REFERENCE.zh-CN.md#call-cases)；对应实现/断言见本篇§3/§10 |
| C13 | CRITICAL | compose_analysis 的委托与一次提交 | 1 | 1 | 1 | 1 | 1 | [API §4.13、正反例](IMPLEMENTATION_API_REFERENCE.zh-CN.md#call-cases)；对应实现/断言见本篇§3/§10 |
| C14 | CRITICAL | 五枚举全部值与意义 | 1 | 1 | 1 | 1 | 1 | [API §2–3](IMPLEMENTATION_API_REFERENCE.zh-CN.md)；公共头声明逐项核对 |
| C15 | CRITICAL | 十结构所有字段与读条件 | 1 | 1 | 1 | 1 | 1 | [API §2–3](IMPLEMENTATION_API_REFERENCE.zh-CN.md)；公共头声明逐项核对 |
| C16 | CRITICAL | 产品/ABI/模型/gate/分析版本区分 | 1 | 1 | 1 | 1 | 1 | [API §2–3](IMPLEMENTATION_API_REFERENCE.zh-CN.md)；公共头声明逐项核对 |
| C17 | CRITICAL | 跨 API 多重错误优先级可复现 | 0 | 1 | 1 | 1 | 1 | [API错误/访问矩阵](IMPLEMENTATION_API_REFERENCE.zh-CN.md#precedence-matrix)；本篇§10 |
| C18 | CRITICAL | 状态到字段访问矩阵 | 1 | 1 | 1 | 1 | 1 | [API错误/访问矩阵](IMPLEMENTATION_API_REFERENCE.zh-CN.md#precedence-matrix)；本篇§10 |
| C19 | CRITICAL | 伪造估计对象校验的范围 | 0 | 1 | 1 | 1 | 1 | [API错误/访问矩阵](IMPLEMENTATION_API_REFERENCE.zh-CN.md#precedence-matrix)；本篇§10 |
| C20 | CRITICAL | 指针/别名与 C 生命周期边界 | 0 | 1 | 1 | 1 | 1 | [API错误/访问矩阵](IMPLEMENTATION_API_REFERENCE.zh-CN.md#precedence-matrix)；本篇§10 |
| C21 | CRITICAL | raw 端点及主观数学区间含义 | 1 | 1 | 1 | 1 | 1 | [API错误/访问矩阵](IMPLEMENTATION_API_REFERENCE.zh-CN.md#precedence-matrix)；本篇§10 |
| C22 | CRITICAL | 事件/补事件坐标与分类 | 1 | 1 | 1 | 1 | 1 | [API错误/访问矩阵](IMPLEMENTATION_API_REFERENCE.zh-CN.md#precedence-matrix)；本篇§10 |
| C23 | CRITICAL | 正 EV 后验概率与未来事件概率分离 | 1 | 1 | 1 | 1 | 1 | [API错误/访问矩阵](IMPLEMENTATION_API_REFERENCE.zh-CN.md#precedence-matrix)；本篇§10 |
| C24 | CRITICAL | 普通 Beta 与 transformed-logit 派发 | 1 | 1 | 1 | 1 | 1 | [内部普通Beta](IMPLEMENTATION_INTERNALS.zh-CN.md#ordinary-beta-steps)与[logit细节](IMPLEMENTATION_INTERNALS.zh-CN.md#logit-detail) |
| C25 | CRITICAL | 精确十进制含零/溢出边界 | 1 | 1 | 1 | 1 | 1 | [内部decimal](IMPLEMENTATION_INTERNALS.zh-CN.md#decimal-detail)；decimal_parity |
| C26 | CRITICAL | 具体源码—函数—断言映射 | 0 | 1 | 1 | 1 | 1 | [本篇断言案例](#assertion-cases)；tests七个C入口 |
| C27 | CRITICAL | 冻结/修正参考与 freshness 区别 | 1 | 1 | 1 | 1 | 1 | 本篇§4–5/§11；oracle README、numerical_policy及生成器 |
| C28 | CRITICAL | 52 永久条目与完成/提案区分 | 1 | 1 | 1 | 1 | 1 | [账本](TECHNICAL_DEBT.zh-CN.md)52条、18字段及44个反例增补 |
| C29 | CRITICAL | R01–R04 精确提交归因 | 0 | 0 | 0 | 1 | 1 | [提交链](TECHNICAL_DEBT.zh-CN.md#repair-history)；git show与远程tag/Release只读检查 |
| C30 | CRITICAL | 同 PR 文档维护、授权边界与有效导航 | 1 | 1 | 1 | 1 | 1 | [AGENTS](../AGENTS.md)、[CONTRIBUTING](../CONTRIBUTING.md)、README五入口及链接检查 |
| D01 | CORE DEPTH | 23 文件职责和实际依赖边界 | 1 | 1 | 1 | 1 | 1 | [导读完整流程](IMPLEMENTATION_WALKTHROUGH.zh-CN.md#separate-sequence)、[状态场景](IMPLEMENTATION_WALKTHROUGH.zh-CN.md#history-states)、[入口选择](IMPLEMENTATION_WALKTHROUGH.zh-CN.md#api-choice) |
| D02 | CORE DEPTH | 分步完整调用的中间值/最终值 | 0 | 0 | 1 | 1 | 1 | [导读完整流程](IMPLEMENTATION_WALKTHROUGH.zh-CN.md#separate-sequence)、[状态场景](IMPLEMENTATION_WALKTHROUGH.zh-CN.md#history-states)、[入口选择](IMPLEMENTATION_WALKTHROUGH.zh-CN.md#api-choice) |
| D03 | CORE DEPTH | 主观独立路径及节点行为 | 1 | 1 | 1 | 1 | 1 | [导读完整流程](IMPLEMENTATION_WALKTHROUGH.zh-CN.md#separate-sequence)、[状态场景](IMPLEMENTATION_WALKTHROUGH.zh-CN.md#history-states)、[入口选择](IMPLEMENTATION_WALKTHROUGH.zh-CN.md#api-choice) |
| D04 | CORE DEPTH | 无历史流程和字段禁读 | 0 | 1 | 1 | 1 | 1 | [导读完整流程](IMPLEMENTATION_WALKTHROUGH.zh-CN.md#separate-sequence)、[状态场景](IMPLEMENTATION_WALKTHROUGH.zh-CN.md#history-states)、[入口选择](IMPLEMENTATION_WALKTHROUGH.zh-CN.md#api-choice) |
| D05 | CORE DEPTH | 稀疏后验存在但分析不可用 | 1 | 1 | 1 | 1 | 1 | [导读完整流程](IMPLEMENTATION_WALKTHROUGH.zh-CN.md#separate-sequence)、[状态场景](IMPLEMENTATION_WALKTHROUGH.zh-CN.md#history-states)、[入口选择](IMPLEMENTATION_WALKTHROUGH.zh-CN.md#api-choice) |
| D06 | CORE DEPTH | VALID 历史门槛和阈值质量 | 1 | 1 | 1 | 1 | 1 | [导读完整流程](IMPLEMENTATION_WALKTHROUGH.zh-CN.md#separate-sequence)、[状态场景](IMPLEMENTATION_WALKTHROUGH.zh-CN.md#history-states)、[入口选择](IMPLEMENTATION_WALKTHROUGH.zh-CN.md#api-choice) |
| D07 | CORE DEPTH | 补事件完整数值计算 | 1 | 1 | 1 | 1 | 1 | [导读完整流程](IMPLEMENTATION_WALKTHROUGH.zh-CN.md#separate-sequence)、[状态场景](IMPLEMENTATION_WALKTHROUGH.zh-CN.md#history-states)、[入口选择](IMPLEMENTATION_WALKTHROUGH.zh-CN.md#api-choice) |
| D08 | CORE DEPTH | 暴露→修改→改回的连续状态 | 0 | 1 | 1 | 1 | 1 | [导读完整流程](IMPLEMENTATION_WALKTHROUGH.zh-CN.md#separate-sequence)、[状态场景](IMPLEMENTATION_WALKTHROUGH.zh-CN.md#history-states)、[入口选择](IMPLEMENTATION_WALKTHROUGH.zh-CN.md#api-choice) |
| D09 | CORE DEPTH | 任务到 13 公共函数选择表 | 0 | 1 | 1 | 1 | 1 | [导读完整流程](IMPLEMENTATION_WALKTHROUGH.zh-CN.md#separate-sequence)、[状态场景](IMPLEMENTATION_WALKTHROUGH.zh-CN.md#history-states)、[入口选择](IMPLEMENTATION_WALKTHROUGH.zh-CN.md#api-choice) |
| D10 | CORE DEPTH | 真实应用分步集成可编译例 | 0 | 1 | 1 | 1 | 1 | [导读完整流程](IMPLEMENTATION_WALKTHROUGH.zh-CN.md#separate-sequence)、[状态场景](IMPLEMENTATION_WALKTHROUGH.zh-CN.md#history-states)、[入口选择](IMPLEMENTATION_WALKTHROUGH.zh-CN.md#api-choice) |
| D11 | CORE DEPTH | 时间/空间/共享对象限制 | 0 | 1 | 1 | 1 | 1 | [导读交接](IMPLEMENTATION_WALKTHROUGH.zh-CN.md#handoff)、[内部成本/定位](IMPLEMENTATION_INTERNALS.zh-CN.md#cost-and-change) |
| D12 | CORE DEPTH | 症状→私有函数→测试的调试路线 | 0 | 1 | 1 | 1 | 1 | [导读交接](IMPLEMENTATION_WALKTHROUGH.zh-CN.md#handoff)、[内部成本/定位](IMPLEMENTATION_INTERNALS.zh-CN.md#cost-and-change) |
| D13 | CORE DEPTH | 分段求值顺序与非对称性 | 1 | 1 | 1 | 1 | 1 | 内部§3–4、§12 helper图谱；subjective/historical原始源码 |
| D14 | CORE DEPTH | 计数 shapes/求和/均值求值 | 1 | 1 | 1 | 1 | 1 | 内部§3–4、§12 helper图谱；subjective/historical原始源码 |
| D15 | CORE DEPTH | use_logit_integration 严格切换 | 0 | 1 | 1 | 1 | 1 | [普通Beta逐步](IMPLEMENTATION_INTERNALS.zh-CN.md#ordinary-beta-steps)；beta.c与large_numerics |
| D16 | CORE DEPTH | nonzero 符号和 tiny | 0 | 1 | 1 | 1 | 1 | [普通Beta逐步](IMPLEMENTATION_INTERNALS.zh-CN.md#ordinary-beta-steps)；beta.c与large_numerics |
| D17 | CORE DEPTH | beta_fraction 两个系数及收敛 | 0 | 1 | 1 | 1 | 1 | [普通Beta逐步](IMPLEMENTATION_INTERNALS.zh-CN.md#ordinary-beta-steps)；beta.c与large_numerics |
| D18 | CORE DEPTH | ps_beta_cdf log-front 与反射 | 0 | 1 | 1 | 1 | 1 | [普通Beta逐步](IMPLEMENTATION_INTERNALS.zh-CN.md#ordinary-beta-steps)；beta.c与large_numerics |
| D19 | CORE DEPTH | ps_beta_quantile 邻接停止 | 0 | 1 | 1 | 1 | 1 | [普通Beta逐步](IMPLEMENTATION_INTERNALS.zh-CN.md#ordinary-beta-steps)；beta.c与large_numerics |
| D20 | CORE DEPTH | Gamma 小/大参数与 signgam | 1 | 1 | 1 | 1 | 1 | 内部§6/§12；gamma.c/a085776 patch、间接Beta回归 |
| D21 | CORE DEPTH | sum_roundoff 与中心补偿 | 0 | 1 | 1 | 1 | 1 | [logit逐层](IMPLEMENTATION_INTERNALS.zh-CN.md#logit-detail)；beta_logit.c/large_numerics |
| D22 | CORE DEPTH | 两小量级数及停止 | 0 | 1 | 1 | 1 | 1 | [logit逐层](IMPLEMENTATION_INTERNALS.zh-CN.md#logit-detail)；beta_logit.c/large_numerics |
| D23 | CORE DEPTH | make_density/density_at 的消差 | 0 | 1 | 1 | 1 | 1 | [logit逐层](IMPLEMENTATION_INTERNALS.zh-CN.md#logit-detail)；beta_logit.c/large_numerics |
| D24 | CORE DEPTH | gauss_panel 节点映射与尺度 | 0 | 1 | 1 | 1 | 1 | [logit逐层](IMPLEMENTATION_INTERNALS.zh-CN.md#logit-detail)；beta_logit.c/large_numerics |
| D25 | CORE DEPTH | adaptive_panel 预算/深度/失败 | 0 | 1 | 1 | 1 | 1 | [logit逐层](IMPLEMENTATION_INTERNALS.zh-CN.md#logit-detail)；beta_logit.c/large_numerics |
| D26 | CORE DEPTH | integrate 面板划分与零长度 | 0 | 1 | 1 | 1 | 1 | [logit逐层](IMPLEMENTATION_INTERNALS.zh-CN.md#logit-detail)；beta_logit.c/large_numerics |
| D27 | CORE DEPTH | transformed_cdf 尾部支路 | 0 | 1 | 1 | 1 | 1 | [logit逐层](IMPLEMENTATION_INTERNALS.zh-CN.md#logit-detail)；beta_logit.c/large_numerics |
| D28 | CORE DEPTH | centered_difference 乘法残差 | 0 | 1 | 1 | 1 | 1 | [logit逐层](IMPLEMENTATION_INTERNALS.zh-CN.md#logit-detail)；beta_logit.c/large_numerics |
| D29 | CORE DEPTH | probability_at 两种回映射 | 0 | 1 | 1 | 1 | 1 | [logit逐层](IMPLEMENTATION_INTERNALS.zh-CN.md#logit-detail)；beta_logit.c/large_numerics |
| D30 | CORE DEPTH | logit quantile 安全 Newton | 0 | 1 | 1 | 1 | 1 | [logit逐层](IMPLEMENTATION_INTERNALS.zh-CN.md#logit-detail)；beta_logit.c/large_numerics |
| D31 | CORE DEPTH | valid_decimal_syntax/view_decimal 状态 | 0 | 1 | 1 | 1 | 1 | [十进制逐层](IMPLEMENTATION_INTERNALS.zh-CN.md#decimal-detail)；odds/decimal源码与exact-bit |
| D32 | CORE DEPTH | integer_from/multiply/digits 不变量 | 0 | 1 | 1 | 1 | 1 | [十进制逐层](IMPLEMENTATION_INTERNALS.zh-CN.md#decimal-detail)；odds/decimal源码与exact-bit |
| D33 | CORE DEPTH | compare_midpoint 包括远端尾数 | 0 | 1 | 1 | 1 | 1 | [十进制逐层](IMPLEMENTATION_INTERNALS.zh-CN.md#decimal-detail)；odds/decimal源码与exact-bit |
| D34 | CORE DEPTH | decode/value 编码含次正规与正零 | 0 | 1 | 1 | 1 | 1 | [十进制逐层](IMPLEMENTATION_INTERNALS.zh-CN.md#decimal-detail)；odds/decimal源码与exact-bit |
| D35 | CORE DEPTH | analyze_side/posterior_probability 家族 | 1 | 1 | 1 | 1 | 1 | [决策/提交](IMPLEMENTATION_INTERNALS.zh-CN.md#composition-detail)；analysis/state/api_contract |
| D36 | CORE DEPTH | 组合错误和局部结果提交细节 | 0 | 1 | 1 | 1 | 1 | [决策/提交](IMPLEMENTATION_INTERNALS.zh-CN.md#composition-detail)；analysis/state/api_contract |
| S01 | SUPPORTING DEPTH | 安装 CMake 消费者示例 | 0 | 1 | 1 | 1 | 1 | [API CMake工程](IMPLEMENTATION_API_REFERENCE.zh-CN.md#cmake-consumer)；本篇§12实测 |
| S02 | SUPPORTING DEPTH | C/C++ ABI 与编译链接解释 | 0 | 1 | 1 | 1 | 1 | 同上extern C解释与C++11安装消费者实测 |
| S03 | SUPPORTING DEPTH | 单测试族最小复现命令 | 0 | 0 | 1 | 1 | 1 | [单族复现](#reproduce-family)；CTest真实注册名 |
| S04 | SUPPORTING DEPTH | 数值失败分层诊断 | 0 | 0 | 1 | 1 | 1 | 本篇§11.1；large_numerics/decimal诊断 |
| S05 | SUPPORTING DEPTH | 状态/参数失败分层诊断 | 0 | 0 | 1 | 1 | 1 | 本篇§11.2；api_contract/state的具体assert |
| S06 | SUPPORTING DEPTH | 安装失败诊断 | 0 | 0 | 1 | 1 | 1 | 本篇§11.3；安装consumer实际构建 |
| S07 | SUPPORTING DEPTH | 每个未解决条目的首要反例 | 0 | 0 | 1 | 1 | 1 | 账本每个未解决条目的第二轮反例；不声称实验已执行 |
| S08 | SUPPORTING DEPTH | 每个未解决条目的实验/归属/决定 | 0 | 0 | 1 | 1 | 1 | 账本每条增补的价值检验/归属/具体所有者门槛 |
| S09 | SUPPORTING DEPTH | 看似简化但破坏兼容的改动 | 0 | 1 | 1 | 1 | 1 | [不兼容简化表](IMPLEMENTATION_INTERNALS.zh-CN.md#cost-and-change) |
| S10 | SUPPORTING DEPTH | AI 维护者分子系统阅读路线 | 1 | 1 | 1 | 1 | 1 | [AI分子系统交接](IMPLEMENTATION_WALKTHROUGH.zh-CN.md#handoff) |
| S11 | SUPPORTING DEPTH | 当前 LayerKeySort 四指南复查 | 1 | 1 | 1 | 1 | 1 | 本节四份当前GitHub参考的blob标识与实际内容复查 |
| S12 | SUPPORTING DEPTH | 本轮执行/历史/未测边界 | 1 | 0 | 1 | 1 | 1 | 本篇§1/§6/§12，初轮与二轮/历史CI分层 |
| S13 | SUPPORTING DEPTH | 可复算审计清单与通过条件 | 0 | 0 | 0 | 1 | 1 | 本节80项二值表、轮次集合与复算脚本 |
| S14 | SUPPORTING DEPTH | 全分步例实际编译和输出比对 | 0 | 0 | 1 | 1 | 1 | 本篇§12，三个完整C例的实际编译和观测输出 |

### 13.3 逐轮真实发现与修补记录

| 阶段 | CRITICAL | 全部清单覆盖 | 实际发现与处理 |
| --- | --- | --- | --- |
| P0 建清单 | 25/30 | 37/80（46.25%） | 目录/符号已齐但缺分步数值、私有递推和诊断；R03引入SHA错误；以更强行动标准重新评价旧稿 |
| P1 初始扩写并对源码复读 | 29/30 | 69/80（86.25%） | 增入口选择、完整分步程序、13函数正反例、全部helper图谱；R03先改正，完整历史链审查/测试诊断/44项反例/本轮实测记录仍未完成 |
| P2 敌对新维护者审查及修补 | 29/30 | 78/80（97.50%） | 无会话条件下逐一回答下表问题，补单测试复现/三类失败诊断/真实断言/44项反例与实验归属；实际编译示例、C-only与安装消费者；C29和S13仍留0等待历史链复核及本节可复算记录 |
| P3 跨文档一致性审查及修补 | 30/30 | 80/80（100%） | 逐commit核对R01–R04，区分引入/诊断/后续RC/正式发布；纠正C初始化器文字次序不能推出求值次序、12/8示例不属13冻结向量；分离初轮289链接/两示例与二轮实测；本节记录清单和轮次，不再仅报百分比 |
| P4 最终定向回归 | 30/30 | 80/80（100%） | 重核头/全部私有函数/52条目/链接锚点/README/维护规则、允许diff与空白；修正右尾明确为1-integral、helper表的小量条件明确取绝对值；复核后无已知事实矛盾或阻止维护的重大歧义；运行证据不外推到未测平台 |

P3明确是P1之后的第二次实质审查与修补，P4再做最终一致性检查；没有机械重写已正确段落。当前本清单剩余未覆盖项为0。有限清单的100%不等于文档绝对完备、数学形式证明或隐藏缺陷概率为0；源代码/数学解释仍等待所有者与独立审查。

### 13.4 不依赖会话的敌对问答定位

| 新人提问 | 仓库内可用回答/行动 |
| --- | --- |
| 没有主观值如何用？ | 导读history-only完整程序，直接history_estimate，无需填默认赔率 |
| 为什么有posterior仍INSUFFICIENT？ | 导读§13的1/0、12/8；API可用性矩阵，n与宽度双gate |
| 字段何时能读？ | API§3、§5、§7；失败不读取本次输出、成功按嵌套flags |
| 数字/分类从何函数来？ | 导读完整分步程序和内部helper图谱，追到geometry/policy或Beta |
| CDF/quantile究竟走哪条？ | 内部§13–14，先记录a/b、switch，再查反射/普通二分或积分Newton |
| 赔率为何拒绝？ | API parse正反例、内部§15词法→精确转换→范围；长串坏尾仍文法先失败 |
| 如何复现一类测试？ | 本篇§11锚定CTest命令；源码函数和行号随提交定位 |
| 改数学函数如何不换模型？ | 内部§17不兼容简化表、数值契约、独立参考和账本审批 |
| 旧修复证据在哪？ | 账本R01–R04及repair-history真实git show链，不仅看closed Issue |
| 提案获批了吗？ | 账本状态、TBD版本和具体所有者门槛；第三方库不是批准证据 |
| 改源文件后同步哪里？ | 导读handoff、AGENTS/CONTRIBUTING及本篇维护门槛；同PR替换过时段落 |
| 如何看待绿色测试？ | 本篇证据分层；覆盖图不是穷举、oracle新鲜度不是重算独立参考 |

### 13.5 可复算轮次计数

在仓库根将下面代码送入Python即可从本节同一80行复算；它不按文字印象猜覆盖。语义覆盖仍需人工沿证据复核，脚本只检查计数、ID唯一性和关键gate。

~~~python
from pathlib import Path
import re

text = Path("docs/IMPLEMENTATION_VALIDATION.zh-CN.md").read_text(encoding="utf-8")
pattern = r"^\| ([CDS]\d{2}) \| (CRITICAL|CORE DEPTH|SUPPORTING DEPTH) \| ([^|]+) \| ([01]) \| ([01]) \| ([01]) \| ([01]) \| ([01]) \|"
rows = re.findall(pattern, text, re.M)
assert len(rows) == 80 and len({r[0] for r in rows}) == 80
for column, name in enumerate(("P0", "P1", "P2", "P3", "P4"), 3):
    covered = sum(int(r[column]) for r in rows)
    critical = sum(int(r[column]) for r in rows if r[1] == "CRITICAL")
    print(name, f"{covered}/80", f"critical {critical}/30")
assert all(r[7] == "1" for r in rows if r[1] == "CRITICAL")
assert sum(int(r[7]) for r in rows) / len(rows) >= 0.90
~~~

新增行为/证据或独立审查发现反例时，重新打开相应项；历史轮次不回写成“从来没有缺口”。下次基线变化保留本轮记录并追加新一轮，不能把这些数字当跨版本自动成立的认证。

### 13.6 第二轮最终结构检查结果

实际检查13个签名与头归一化一致，五枚举/十结构全部字段及四产品宏齐全；14个生产C、九私有头、44个非公共函数定义（含三个inline）均有对应解释。52个canonical ID各一次且18字段完整，44个未解决条目各有反例/实验增补；R03引入SHA及R01/R02/R04证据角色已与git show核对。380个相对Markdown链接/显式锚点全部有效，表格列数、行首代码围栏闭合检查通过。README五入口、AGENTS/CONTRIBUTING同PR维护规则保留；本轮diff仅修改五份指南/账本，未改另外三份入口/政策文件，因为既有导航/规则仍适用。`git diff --check`通过。头/名称/链接检查是结构证据，语义覆盖另由逐轮源/断言复核支持，不把自动名称出现计数直接当完整解释。

<a id="preview-device-history-validation"></a>

## 14. RC 审查：最终源码清单与调用方参考的断言地图

### 版本与证据基线

1. 稳定源码 `fdfaddfb58486004ee1cc02c0f4a5c640cd17c7c` 为 v1.0.0 标签目标。PR #11 引入经审查的四篇源码指南。第 1–13 节原有执行、覆盖计数和说明以各自记录的提交为准。
2. Preview 第一、二单元由 PR #12/#13 引入，分别留下适用性框架和合成研究。第三单元实现提交为 `47e7ca52616e1eeabe2ddeba1fbbe8382101b006`，PR #14 合并为本次起点 `27d18c0611a73b96596552ad967b94222b24a5ad`。原 [Portable C11](https://github.com/RXY712200/ProbSpan/actions/runs/44270682085) 和 [可选参考](https://github.com/RXY712200/ProbSpan/actions/runs/44270682759) push 运行对应实现提交，不作为 RC 的 CI。合并提交的 [Portable C11](https://github.com/RXY712200/ProbSpan/actions/runs/44280313554) 成功，旧的可选工作流过滤条件没有在该 main push 产生运行。
3. 2026-11-18，PR #15 的初次文档协调提交 `cfcdf304ef9d337f99b17a1558be7df4cffd6784` 补充了可选参考的边界、断言映射、回归测试与 CI 路径过滤。此时产品仍标识为 `1.0.0`，模型未改。
4. 同日，PR #15 的后续提交 `66973bc55c5b36360d6e06e58a93ab7cfa9b9877` 将产品标识调整为 `1.1.0-rc.1`，CMake 包数字版本调整为 `1.1.0`，同步消费者和版本断言，并补上 main push 与手动验证入口。下文按提交记录执行证据；较新的文档修订以实际 PR HEAD 和该 HEAD 的运行验证。
5. 已发布的 `v1.1.0-rc.1` 指向 `409d545970ffd1ddf39403fe805943555f35a0af`，其完整树等于合并后的 `a237028765cefe9306b8d04861b2030d72c0d4c5`。合并后运行见 [Portable C11](https://github.com/RXY712200/ProbSpan/actions/runs/44299028313) 和 [可选参考](https://github.com/RXY712200/ProbSpan/actions/runs/44299028325)。这些运行保留为 RC 证据。v1.1.0 的执行记录须绑定其实际评审提交。

| 范围 | 实际源码、构建、依赖 | 验证与限制 |
| --- | --- | --- |
| 安装的稳定核心 | 唯一公共头、13 个函数、ABI 1、14 个 C 实现和 9 个私有头。根 CMake 为静态 C11，仅标准 C 与所需数学库 | 相对 v1.0.0 标签，`src/`、`cmake/`、`oracle/`、`examples/`、冻结夹具、[行为规范](BEHAVIOR_SPEC.md) 与 [数值契约](NUMERICAL_CONTRACT.md) 保持原样。`include/probspan/probspan.h` 仅调整产品 minor 宏及字符串，函数签名、结构布局、ABI 和各独立模型、gate、分析版本保持原值。`CMakeLists.txt` 的项目与生成包版本为 `1.1.0`。`tests/api_contract.c` 核对新产品版本和各独立版本，`tests/consumer/main.c` 期望新产品字符串。 |
| 冻结模型与参考 | Jeffreys 与 readiness、主观宽度、赔率转换、EV 和 provenance 沿用 v1。冻结历史与大形状例外见[数值契约](NUMERICAL_CONTRACT.md) | 运行已提交夹具的 C 断言，并对五份 C 夹具执行 freshness。未重建冻结上游、未改独立高精度政策或容差。 |
| 调用方参考 | `integrations/device_history/`。证据审查与进程适配用 Python 标准库，两层后验用固定 NumPy 2.4.4 / SciPy 1.17.1。`integrations/device_history/CMakeLists.txt` 要求安装包数字版本 `1.1.0 EXACT`，`integrations/device_history/v1.py` 另检查 `1.1.0` 与 ABI、历史模型、gate 均为 1 | 可选工作流 checkout 精确 PR 头、push 提交或手动指定的完整 SHA，先安装根包，再单独构建消费者、执行 Python 断言和示例。根安装没有此模块、解释器或 Python 包。 |
| 研究证据 | `research/preview_history.py` 与已记录 JSON。Phase II 生成器可复现，原结果不作为 v1 oracle | 参考测试重放 mix-shift 首个合成重复，不重跑全套 Phase II 研究。现场适用性、跨未披露群集的独立性、采样校正、估计权重及通用可移植数值保证仍未验证。 |
| 部署与发布 | 根安装包含档案、公共头和 CMake config/version/targets。源码分发才包含研究与可选集成。既有 v1.0.0 Release 公开、非预发行，无上传平台二进制 | [发布说明](RELEASING.md)记录 `v1.1.0` 的发布准备和精确版本复核办法。可选参考包含在源码分发范围，根安装维持原边界。 |

### 生产函数与具体断言

下表测试在 [test_device_history.py](../integrations/device_history/test_device_history.py) 中，`device_batch` 来自[可执行示例](../integrations/device_history/example.py)。测试构造合成记录或变更单个字段。拒绝辅助断言同时核对状态、原因、无计数、零纳入和无数值可用。表中「静态检查」明确未执行的极端/防御分支。

| 源码职责 | 对应测试及实际断言 |
| --- | --- |
| [evidence.py](../integrations/device_history/evidence.py) `review/_check_declaration/_known/_hour` | `test_strict_and_pool_counts`：严格 (3,3)、池化 (6,4) 及两范围。 `test_declaration_and_zero_target`：三种非支持声明、空引用的 `declaration_evidence_unknown`、路径假设不相容、缺来源、来源旧工艺、经声明零目标仅使用 (3,1)。`test_missing_context_and_path_mismatch`：范围缺修订、截止未知、严格路径带来源或权重拒绝。 |
| `_visible/_validate` | `test_cutoff_excludes_later_outcome_even_on_same_identity`：冲突标签迟到时不计数也不参加冲突审查，缺可用时刻则弃权。`test_definitions_regime_censoring_and_identity`：错定义/时距、同设备错工艺、50 小时空/假补事件、时刻矛盾及未知周期键。 `test_missing_context_and_path_mismatch`：错层、条件缺失、整数非布尔。 |
| `_select`、回执的纳入/排除 | `test_duplicates_and_conflicts`：同一规范键跨查询折叠一次，结果 (1,1)，冲突标签或跨源/目标重叠无计数。 `test_unmodelled_dependence_preserves_records`：共同簇或同设备异周期两条均暂扣且别名数为零。 `test_target_weights_and_support`：两层正权重缺支持弃权，零权重层排除三条后 (1,2)/(0,0)。计数聚合超过 INT64_MAX 是静态检查，C 入口另有解析超限断言。 |
| `_weight_pair` 与已知总体 | `test_target_weights_and_support`：未知、不归一、负数、NaN、错长度及布尔；`test_known_heterogeneous_and_population_change`：同记录反转目标权，均值方向正确，非样本构成替代。 |
| [standardization.py](../integrations/device_history/standardization.py) `standardize/_shapes/_moments` | `test_known_heterogeneous_and_population_change` 对 (2,18)/(9,11) 和两组固定权用 Fraction 核对两次均值和方差。 `test_boundary_and_budget_failure` 核对均值 .5、方差 .03125、镜像区间、零权重直接 Beta。 `test_numerical_range_failure_preserves_review`：10,001 条保留有效回执但无估计。 |
| `_inverse_grid/_invert/_quantile_brackets` 的数值成功 | `test_known_heterogeneous_and_population_change`、`test_boundary_and_budget_failure`：半整数 Beta 递推、变换后的独立积分和求根得到的两端落在精度包络内，零权重用独立单 Beta 求根。 `test_phase_two_mix_shift`：种子 902618 的首重复，目标 20、来源 320、生成真值 .09。与相同记录的 Phase II Monte Carlo 核对均值和两端；这项比对不替代独立求根。 |
| `standardize/_inverse_grid/_invert/_quantile_brackets` 的数值拒绝 | `test_boundary_and_budget_failure` 将可求解样例限于 256 个分箱，确认 `numerical_budget_exhausted` 且无估计。 `test_numerical_faults_do_not_expose_estimates` 拒绝超下限预算，并注入网格、单 Beta、后续 CDF 故障，分别核对 `beta_grid_failure`、`beta_quantile_failure`、`cdf_failure`。 `cdf_bracket_failure`、`invalid_numeric_result` 是静态检查的内部结果防线。 |
| [v1.py](../integrations/device_history/v1.py) `estimate_v1/_check_payload`，以及 [v1_consumer.c](../integrations/device_history/v1_consumer.c) `main/state_name/read_count` | `test_installed_v1_values_and_states` 真正调用已安装档案，空结果无估计，18/2 和 19/1 分别为 INSUFFICIENT 与 VALID，核对均值与 readiness，池化 29/1。 `test_consumer_input_and_failure_boundary` 执行缺参数、负数、语法和超限请求且无 stdout，通过 mock 核对 C 错误无估计、畸形 JSON 对象为消费失败。C 内部错误在适配层用协议注入，未声称 C 求解器实际失败。同一测试分别替换产品、ABI、模型与 gate 版本，确认不匹配时为 `consumer_failure` 且不返回估计。超时等其他分支为源码检查。 |
| `example.py` `device_batch/main` 与独立 CMake | 可执行示例脚本同时走三条路径，stdout 为结构化回执和估计。测试复用可重复的设备/周期/层生成器。CI 为 CMake 配置独立安装前缀并执行真实程序。 |

### RC 实际运行与未验证边界

2026-11-18，先在初次协调提交 `cfcdf304ef9d337f99b17a1558be7df4cffd6784` 验证 `1.0.0` 安装与消费者，再在候选版本提交 `66973bc55c5b36360d6e06e58a93ab7cfa9b9877` 用干净安装验证 `1.1.0-rc.1` 与数字包 `1.1.0`。两轮均在 Windows x64、UCRT64 GCC 16.2.0、CMake 4.4.3、Python 3.13.14、上述固定依赖的临时环境，按[参考构建命令](PREVIEW_DEVICE_HISTORY.zh-CN.md)用 MinGW Makefiles 构建 Release 并启用 examples/Python。实际退出结果为根 CTest 14/14、安装原消费者 1/1、独立参考 unittest 15/15，可执行示例三个状态为 ok。参考消费者以 `-Wall -Wextra -Wpedantic -Werror` 构建。实查安装只有公共头、静态 archive 和四个 CMake 文件。旧模型 readiness、provenance、十进制与浮点断言仍来自 v1 专项测试。新故障注入独立于冻结 fixtures。

可选 CI 在 Ubuntu 执行上述参考断言，根 Portable C11 跑 Windows MSVC、Linux GCC/Clang、macOS AppleClang 和 Linux GNU ASan/UBSan，以及各自安装消费者。初次协调的分支 push 运行见 [Portable C11](https://github.com/RXY712200/ProbSpan/actions/runs/44284631126) 与[可选参考](https://github.com/RXY712200/ProbSpan/actions/runs/44284631127)。候选版本提交的分支 push 运行见 [Portable C11](https://github.com/RXY712200/ProbSpan/actions/runs/44289270933) 与[可选参考](https://github.com/RXY712200/ProbSpan/actions/runs/44289271424)。两组均成功；后者的可选运行日志记录精确 SHA、15 项测试与候选产品字符串。现行工作流对相关源码、头文件、打包、参考和文档路径的 PR 与 main/Preview/RC 分支 push 生效；默认分支具备该入口后可按[发布说明](RELEASING.md#v110-stable-preparation)手动指定完整候选 SHA。上述运行验证了分支 push；main push 与手动启动不是这些运行的证据。没有实测可选消费者的 MSVC/macOS 运行，没有验证部署数据或任意 SciPy/浮点配置。首次 RC 归因以提交与可复现结果为准，本地自审和绿色 CI 不代替独立接受。


## D2.2 Models

D2.2 的 [Models 资格记录](../models/tests/QUALIFICATION.md) 区分编译结果、高精度尾部复核和固定 n 覆盖枚举。其 CTest 与历史 legacy oracle 分开。
