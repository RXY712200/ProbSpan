# 自审与交接问题

[导航](README.zh-CN.md) · [条件判定](conditional-findings.zh-CN.md) · [外部证据](external-evidence-and-limitations.zh-CN.md) · [复现命令](../../../research/phase-b/README.md)

## 基线和覆盖

从干净云端 checkout 独立获取公开仓库、main `e47c038cd2b1997d87b7fe303f9037c80e6eb955`（树 `6314da50f8b5dc6d4a3da2746b9948e465da1fa0`）和任务分支 `dad36d284e9a06f12cabba4316fcbdd569dceb04`（树 `9984f55dcebf233381b4bc208b0fcf6d0cd45785`）。用 PR metadata 核证 #17 已合并、接受 HEAD `4bc0e28d60bf7c618543aa0d789f34a29d0f4ec6`；main 中的 Phase A 目录与该 HEAD 字节相同。Stable v1.1.0 为非草稿/非预发行，解析到 `46ff21847c5522eb983d3f58e396354461a64f34`；相对 Stable 的初始差异是两份任务简报和 Phase A 研究文件。已认证读取两份现行协作/发布政策完整正文；公开附件只记录验证事实。

审阅 AGENTS、CONTRIBUTING、README、ORIGIN_AND_SCOPE、ARCHITECTURE、API、BEHAVIOR_SPEC、NUMERICAL_CONTRACT、COMPATIBILITY、PROVENANCE、四份 IMPLEMENTATION 中文指南的相关路径、永久账本及八份 Phase A 资料（包括 96 源行、交叉表、案例、增补问题和验证说明）。对照历史证据研究与两份 Preview、早期脚本/输出和现行 C、公开头、数值参考及断言。查 #1/#5/#6/#8/#9/#10，均 open、当前 0 评论；未据开放状态改账本。查看冻结模型、端点和状态需回到源码，历史 Preview 研究与本轮独立执行不得互相冒充。 [Phase A](../phase-a/README.zh-CN.md) · [账本](../../TECHNICAL_DEBT.zh-CN.md)

| 固定活动 | 交付证据 |
|---|---|
| B1 | [对象图](problem-estimand-map.zh-CN.md)有 48 + 7 个问题，另列 4 个历史修复。 |
| B2 | [候选模型](candidate-models-and-assumptions.zh-CN.md)明确共同 estimand、模型、假设、负对照与解释。 |
| B3 | [推导](derivations-and-counterexamples.zh-CN.md)提供二项覆盖/预测方差、零目标权不变、联合方差、风险集、顺序检验、部分识别和输出网格证明。 |
| B4 | [实测](experiments-and-results.zh-CN.md)7 个稳定 ID、3 份 JSON，含解析、模拟及固定 C 源码探针。 |
| B5 | [外证](external-evidence-and-limitations.zh-CN.md)重新查正文、评估实际资料的可比性并补 DOI；已执行公共棒球档案对照。 |
| B6 | [条件判定](conditional-findings.zh-CN.md)及一项临时 NEW-B 问题；独立审查待评审方执行。 |

分析前写入[协议](../../../research/phase-b/protocol.md)。数值组把切换前后作为两组，故保留五组而不是协议中的四类；在 B-E003 使用联合一阶方差及真实重复，而未额外运行 bootstrap。B-E007 的 1970 档案后来检查为正式打数（at-bats），用正确分母命名，并把原猜测的论文复制界定为新指标的固定数据再分析。所有方案改变只在记录和研究对照内。

## 实际运行与完整性

- 在临时环境安装 numpy==2.2.6、scipy==1.15.3、mpmath==1.3.0，编译 C11 探针，执行[三个命令链](../../../research/phase-b/README.md)。另一次分别写到 `/tmp/probspan-b-rerun`，用 `cmp` 检查三个 JSON，与研究结果逐字节相同。验证 JSON 拒绝非有限值、每组是否恰有预定实验、数值括界和关键反例。
- Linux x86-64 / GCC 14.2.0 上临时 CMake 3.31.6 实际执行 `cmake -S . -B /tmp/probspan-b-build -DPROBSPAN_BUILD_EXAMPLES=ON -DCMAKE_BUILD_TYPE=Release`、`cmake --build /tmp/probspan-b-build --parallel 4`、`ctest --test-dir /tmp/probspan-b-build --output-on-failure`，现有套件 14/14 通过。未将该运行当作科学证据，未运行其他平台、设备现场或云端发布 CI。
- Python 完整性核对解码严格 TSV/JSON，检查固定 48+7+4 ID、四行来源增补、Phase A/Phase B 源引用、实验 ID 和 80 个内部链接/锚点，确保全部可定位。外部证据按对应访问层级保留，出版站挑战页、摘要和只核元数据均注明。文件仅在两个新增目录中；`git diff --cached --check` 及范围 diff 检查现行源代码、契约、Phase A、永久账本、oracle、预置测试、CI 与发行文件的保护范围。
- 没有重新计算完整冻结 oracle、使用其他 libm、复现医疗/工业病例或运行早期 Preview 全试验。数值重复预算给一致性证据，非形式误差认证。比较组的相对排序只在实际选择、概率目标和评价分母内解释。

## 独立审查与后续问题

- 什么时候业务认可的历史可比性声明可以用目标条件、已成熟标签和可复核抽样支撑？哪些证据可能使“低目标 n”退化为部分识别？
- 在未来应用中，风险集、标准化权和独立单位怎样定义，哪些重叠数据导致兼容限制；几类不确定性是估计对象本身，哪些只是数值/信息限制？
- 若真值修订或预测影响标签和曝光，何种可观测分母可同时支持可复现评分与决策后悔？选择权重和拒绝代价将如何受实际用户需求影响？
- 如何解释相同表示值附近的决策敏感性，什么跨工具链证据有助于区分数值误差和不充分可表示性？

独立审查请核对固定源树与输入表、计算与实测一致性、条件覆盖与数据生成过程、Phase A 保持原样及 Git 范围。此文件只保留科学问题。
