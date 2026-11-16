# ProbSpan 验证地图与可复现证据

## 1. 审查基线和证据等级

源码基线 `fdfaddfb58486004ee1cc02c0f4a5c640cd17c7c`，v1.0.0；文档审查/本地执行日期 2026-11-16。本篇与 [导读](IMPLEMENTATION_WALKTHROUGH.zh-CN.md)、[API 参考](IMPLEMENTATION_API_REFERENCE.zh-CN.md)、[内部实现](IMPLEMENTATION_INTERNALS.zh-CN.md)、[永久账本](TECHNICAL_DEBT.zh-CN.md) 交叉使用。权威数值要求在 [NUMERICAL_CONTRACT.md](NUMERICAL_CONTRACT.md) 和 [numerical_policy.json](../oracle/numerical_policy.json)，不是本篇另定容差。

| 等级 | 本次依据 | 不可据此宣称的内容 |
| --- | --- | --- |
| 源码审查 | 公共头、全部 14 C/9 私有 H、CMake、CI、示例、consumer、参考生成器与现有规范 | 仅阅读不等于执行通过 |
| 断言审查 | 下表测试函数及比较规则 | 有断言不等于覆盖所有输入 |
| 本地实际执行 | Windows x64 MSYS2 UCRT64 GCC 16.2.0，14/14、C-only 9/9、安装 consumer 1/1 | 未在本次重跑所有 CI 平台、sanitizer 或冻结 Python 原应用 |
| 历史 CI | [run 39358543092](https://github.com/RXY712200/ProbSpan/actions/runs/39358543092)，API 查得 completed/success，head_sha 与基线相同 | 不把历史运行说成本次重新运行 |
| 未验证/研究限制 | ARM/嵌入式/替代 libm、任意浮点标志、无限输入域、实际历史适用性 | 没有形式证明、普适预测保证或任意架构逐位相同保证 |

[正式发布](https://github.com/RXY712200/ProbSpan/releases/tag/v1.0.0) API 检查得到 ID 417950498，published_at=2026-10-20T02:50:24Z，draft=false、prerelease=false。这是既有发布证据，不是本次文档操作发布。

## 2. CMake 构建图与测试数量

[根 CMake](../CMakeLists.txt) 最低 3.16，项目版本 1.0.0，`probspan` 为 STATIC、C11 required、关闭 C extensions。构建树 alias 与安装导出名均为 `ProbSpan::probspan`。非 MSVC 公共链接 m；警告选项 MSVC /W4，其他 -Wall -Wextra -Wpedantic。安装仅导出公共头、静态 archive、CMake targets/config/version，版本配置 SameMajorVersion；私有头不安装。

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

## 6. 本次实际命令与结果

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

本次实际结构检查结果：13 个归一化函数签名与头文件一致，所有枚举值和结构字段标识均在 API 参考出现；生产模块均有映射；289 个相对链接/显式锚点无缺失；Markdown 表格列数与代码围栏检查通过；48 个候选 ID 各一个正式章节，另 4 个 R 修复条目，52 条各有连续 1–18 项；README 五入口及八文件变更白名单检查通过。`git diff --check` 无错误。C 的 decimal 日志实际报告 41 向量、4 个舍入模式、逗号 locale passed。上述计数是本次检查快照，后续增删链接应重新计算，不把数字当固定兼容契约。

公共 API/字段、行为、内部调用、数学/数值、错误校验、测试/夹具、CMake、平台、版本/兼容性/发布改变，必须同一分支/PR 更新受影响四指南、权威契约、README 与账本，替换过时解释，区分历史。无文档影响要说明；绿色测试不建立文档准确性，这些政策没有自动新增 CI gate。账本解决记录提交、测试、首次版本、剩余限制，延期/拒绝保留原因，ID 不删除/复用；所有者未批准的功能/模型/发布不得实施。见 [CONTRIBUTING](../CONTRIBUTING.md)。
