# ProbSpan 维护规则

- 先核对当前分支、工作区和实际源码。已发布 v1.0.0 是兼容性基线；公共声明以 `include/probspan/probspan.h` 为准，行为、数值与兼容性约束见 `docs/API.md`、`docs/BEHAVIOR_SPEC.md`、`docs/NUMERICAL_CONTRACT.md`、`docs/COMPATIBILITY.md`。发现源码与契约矛盾时报告并定位，不擅自改写契约。
- 阅读四份源码指南：`docs/IMPLEMENTATION_WALKTHROUGH.zh-CN.md`、`docs/IMPLEMENTATION_API_REFERENCE.zh-CN.md`、`docs/IMPLEMENTATION_INTERNALS.zh-CN.md`、`docs/IMPLEMENTATION_VALIDATION.zh-CN.md`。永久问题账本为 `docs/TECHNICAL_DEBT.zh-CN.md`。
- 改动公共 API/字段、函数行为、内部调用、数学或数值求值、校验/错误、测试/夹具、CMake、平台、版本/兼容性/发布行为时，必须在同一分支/PR 审查并更新受影响指南、权威文档、README 导航和账本。替换过时解释，不保留互相矛盾的现行描述；确无文档影响时在变更报告中说明理由。
- 区分源码审查、断言审查、本地实际执行、历史 CI 和未验证性质。测试通过不证明文档正确；不得声称这些文字规则已由 CI 自动强制执行。
- 问题 ID 永不复用，条目永不删除。解决时记录 RESOLVED、实际改动、提交、测试、首次可用版本和剩余限制；拒绝/延期时保留原因与决定。
- 提案必须经所有者批准才能实现；不得擅自扩展模型、数据库、融合、存储或 GUI，不得擅自更改版本、标签、发布或 Issue。保持 v1 Jeffreys 先验、gate、主观宽度、赔率语义、因果顺序与独立版本含义。
- 不为通过测试重写冻结 oracle 或数值参考政策。不自动修改其他项目、工作区或 Codex 会话。遵守 `CONTRIBUTING.md` 的职责边界与验证要求。
