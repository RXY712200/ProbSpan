# Contributing to ProbSpan

ProbSpan is deliberately small: a deterministic C11 core for probability uncertainty, EV/decision classification, and information-provenance semantics. The authoritative product boundary is [Issue #1](https://github.com/RXY712200/ProbSpan/issues/1). Please open an issue explaining the concrete decision-analysis use case before proposing broad features or alternate models.

## Before changing code

1. Identify whether your change is a bug fix, a numerical evaluation correction, a public contract change, or a new mathematical model. These are **not interchangeable**.
2. Keep the original v1 model, Jeffreys prior, odds grammar, policy thresholds, causal ordering and independent version meanings unchanged in a compatible patch.
3. Do not change frozen oracle values to make a test pass. The only authorized exceptional reference method is documented in [Numerical contract](docs/NUMERICAL_CONTRACT.md). Changes to that reference policy need a separate explicit decision and evidence.
4. Prefer small modules with one responsibility, clear comments for non-obvious numerical decisions, and no runtime heavy dependencies, global mutable state or workflow/storage/UI code.

## Local development

```sh
cmake -S . -B build -DPROBSPAN_BUILD_EXAMPLES=ON
cmake --build build
ctest --test-dir build --output-on-failure
cmake --install build --prefix /tmp/probspan-install
cmake -S tests/consumer -B consumer-build -DCMAKE_PREFIX_PATH=/tmp/probspan-install
cmake --build consumer-build
ctest --test-dir consumer-build --output-on-failure
```

Adapt multi-config commands on MSVC. For a pure C build set `-DCMAKE_DISABLE_FIND_PACKAGE_Python3=TRUE`; Python, SciPy and mpmath are development-only oracle tools. Reference/check commands, tool versions, and precision rules are in [Testing](docs/TESTING.md). Avoid unsafe floating flags such as `-ffast-math`.

## Review expectations

- Explain affected API/ABI/model versions and compatibility implications.
- Include focused edge cases and unchanged-output-on-error tests where applicable.
- State whether exact discrete results, elementary numeric parity, Beta parity, or bit-exact decimal semantics apply.
- Keep changes to [API](docs/API.md), [Behavior specification](docs/BEHAVIOR_SPEC.md), [Numerical contract](docs/NUMERICAL_CONTRACT.md) and examples synchronized.
- Ensure the multi-platform CI passes, including installed consumer and sanitizer job.

New probability distributions, calibration scores, probability fusion, persistence, and workflow machinery are **not** automatically in scope. Please use an issue to discuss any future-version design rather than introducing it through a compatibility patch.

## 永久文档与账本维护要求

权威公共声明在 `include/probspan/probspan.h`；现行行为、数值与兼容性约束见 [API](docs/API.md)、[行为规范](docs/BEHAVIOR_SPEC.md)、[数值契约](docs/NUMERICAL_CONTRACT.md)、[兼容性](docs/COMPATIBILITY.md)。源码是当前实现的证据；若与契约矛盾应定位报告，不擅自改写契约或冻结参考。新维护者依次阅读 [导读](docs/IMPLEMENTATION_WALKTHROUGH.zh-CN.md)、[API 全表](docs/IMPLEMENTATION_API_REFERENCE.zh-CN.md)、[内部实现](docs/IMPLEMENTATION_INTERNALS.zh-CN.md)、[验证地图](docs/IMPLEMENTATION_VALIDATION.zh-CN.md)，并查询 [永久账本](docs/TECHNICAL_DEBT.zh-CN.md) 与 [AGENTS](AGENTS.md)。

修改公共 API/结构字段、函数行为、内部调用、数学模型或数值求值、错误/校验、测试/夹具、CMake、支持平台、版本/兼容性/发布行为时，必须在同一分支/PR 审查并更新受影响四指南、权威文档、README 导航和账本。替换过时解释，不仅追加互相矛盾的描述；过去行为必须明确标记版本。确无文档影响时，在变更报告或 PR 中说明理由。

问题条目和 ID 永不删除、永不复用。解决后改为 RESOLVED，记录实际改动、精确提交、验证结果、首次可用版本和剩余限制；延期或拒绝保留理由、决定与日期；新问题分配新的永久 ID。第三方工具存在不等于本项目完成实现，提案优先级不等于已批准路线图。

完成前须复核四指南与源码、API 与头、测试引用与实际断言、README 链接、账本状态及所有者批准边界。明确区分源码审查、断言审查、本地执行、历史 CI 与未验证性质。绿色测试不建立文档准确性；上述政策不会自动在 CI 中强制执行。

所有者批准前不得实施账本提案或扩展概率模型/数据库/融合/存储/GUI，不擅自改版本、标签、发布或 Issues；不以测试失败为由重写冻结 oracle/参考政策，不自动修改其他项目。v1 Jeffreys、gate、主观半宽、赔率与因果语义以及独立版本含义持续受兼容性约束。

## License

By contributing code or documentation you agree that the contribution is provided under the project's [MIT License](LICENSE), unless a different arrangement is explicitly agreed with the maintainer. Do not paste unlicensed third-party code or large copyrighted reference passages.
