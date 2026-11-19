# 所有者决策与独立评审移交

[导航](README.zh-CN.md) · [结构化决定](decision-register.tsv) · [重叠登记](overlap-register.tsv)

## 要决定的事项

- **范围、用例和代价（C-D001、C-D002、C-D009）**。保持现状没有工程变更和新的公开责任。若选择有实际需求的外部试点，先确定端点、调用者与可合法使用的数据，确定误纳、误拒、拒绝决策、延误的代价及最小可见价值。无代表性观测或现有工具已足够时，留在现状。
- **可选分发的责任（C-D003、C-D007）**。谁保有收据/原证据，谁维护时钟和版本？显式收据让审核和重放可行，却不能保证概率适用。使用已有参考可以节省重复；新包会增加依赖、版本及安装检验成本。建议可撤除且无根依赖，仅在批准范围内比较。
- **未来推断与评价（C-D004、C-D005、C-D008）**。域内适用、重叠、同一概率对象和分母必须先明确。独立工具可保护 v1，代价是额外协议和验证。没有目标权、风险集、发出时刻真值和用户需求时，延期；保留当前原样可用。
- **私有核（C-D006）**。判定相同域和算法对象是技术工作。是否承担共同误差预算、未来维护并公开行为是后续范围决定。当前几何复用已经带来收益；额外 Beta 共用以第二个实际、同合同的消费者和通过双切面回归为前提。

状态 `OWNER_REQUIRED` 表示需所有者决定，`PROPOSED` 是随证据评审的设计建议，`DEFERRED` 暂无实施条件。记录没有已授权行。两份登记是 UTF-8 TSV，首行字段名、每行一条，空格分隔交叉 ID；兼容、可逆性及证据条件各有列。当前没有追加外界新来源；重核的来源继续使用原 ID，Phase B S0029 DOI 补注的位置保持。 [Phase A 来源](../phase-a/source-register.tsv) · [Phase B 增补](../phase-b/source-addendum.tsv)

## 审阅和差异

仓库公开、两份当前治理正文已经认证取得并阅读，未保存其内容或私库路径。用 Git 核对 `45075a1da4adedf871299d148ef7dfa502335d72` main、`5406d38a62b831c2e4560b0242dd89ec1a6754a1` 起点和 Stable SHA；PR #17/#18 已合并，main 与 Phase B HEAD 同树。任务分支原有且仅有简报差异。检查 AGENTS/CONTRIBUTING/README、产品范围、架构、API、行为、数值、兼容、provenance、测试、四份中文实现指南和账本。检查公共头与关键源码、根构建、oracle/测试、设备 Preview 和早期实验。核对全部 Phase A/B 文档、源登记及相关运行代码/输出、Issues #1/#5/#6/#8/#9/#10。文档或 issue 历史描述不能推导新权限。例如 #8 历史上提到拟议发行名，此处 Stable v1.1.0 为已经核实的产品发布，数据库提案继续独立、未授权。

| 活动 | 可独立核验的交付 |
|---|---|
| C1 | [事实地图](current-state-and-evidence-map.zh-CN.md) 记录 13 个函数、10 个结构、5 个枚举；追踪 48+7+1 个问题和四项历史修复。 |
| C2 | [重叠评审](overlap-and-separation.zh-CN.md) 与 26 个登记条目匹配，含算法共享、概念分离、存储边界及不支持的合并。 |
| C3 | [备选方案](architecture-alternatives.zh-CN.md) 以现状为可接受控制，按场景衡量三个改动选项。 |
| C4 | [蓝图](proposed-boundaries-and-contracts.zh-CN.md) 给单向数据图、职责、状态和七项对抗走查。 |
| C5 | [风险与验证](integration-risks-and-validation.zh-CN.md) 审查跨组件传播、独立验证及迁移。 |
| C6 | [后续条件](conditional-phase-d-plan.zh-CN.md) 允许只做一个可结束的随后单元、可证伪扩展或保留现状。 |
| C7 | 本页及 9 决策行记录反方证据、未来观测和权限停点。 |

## 运行和完整性

在本轮起点的无改动生产源码上，用 Linux x86_64、glibc 2.41、GCC 14.2.0、CMake 3.31.6、Python 3.12.14，以临时 venv 安装现有设备 requirements（NumPy 2.4.4/SciPy 1.17.1）。执行了以下命令，根 CTest **14/14**、安装 consumer **1/1**、设备独立参考 **15/15**。根安装只列 archive、公开头和 CMake 配置。属现行路径回归，非拟议实现验证。

```sh
cmake -S . -B /tmp/probspan-c-build -DPROBSPAN_BUILD_EXAMPLES=ON -DCMAKE_BUILD_TYPE=Release
cmake --build /tmp/probspan-c-build --parallel 4
ctest --test-dir /tmp/probspan-c-build --output-on-failure
cmake --install /tmp/probspan-c-build --prefix /tmp/probspan-c-install
cmake -S tests/consumer -B /tmp/probspan-c-consumer -DCMAKE_PREFIX_PATH=/tmp/probspan-c-install
cmake --build /tmp/probspan-c-consumer
ctest --test-dir /tmp/probspan-c-consumer --output-on-failure
cmake -S integrations/device_history -B /tmp/probspan-c-device -DCMAKE_PREFIX_PATH=/tmp/probspan-c-install
cmake --build /tmp/probspan-c-device
PROBSPAN_DEVICE_CONSUMER=/tmp/probspan-c-device/device-history-v1 python -m unittest integrations.device_history.test_device_history
```

另以 `python /tmp/probspan-c-check.py` 解析 A 的 96 源行、B 的三条新增和一条修订，核查 C 两 TSV 列数、唯一编号及全部可追踪引用；对照 ledger、A/B 问题及历史记录逐 ID 审核覆盖。检查 Markdown 围栏、表列和 122 处相对路径/锚点；核对变更只在新增目录，验证 `git diff --cached --check`、与接受的 A/B 目录和 Stable 生产子树的 Git 差异。没有擅自调用跨平台 CI 或重跑全部 B 实验。按 B 数值 JSON 重算严格 10/15、容差 15/15；记录的是现有值重判，不是高精度再求解。另核对 B-E002、B-E003、B-E004、B-E005、B-E007 关键表值。

## 独立评审检查

1. 从固定 HEAD 比对公开头、直接调用/组合器的验证次序、实际设备打包和保护范围。检查证据初始反例是否真的经过预期状态或当场停止。
2. 至少对照一个共享叶正例和一个错误合并，逐项问输出的目标、信息集、误差预算和零样本含义是否保留。特别核对 standardized risk 无法写入 v1 后验分析、资格不是 readiness、实际曝光不是数据可见时刻。
3. 反向尝试现状方案，审查外部试点是否满足其进入条件，是否比复用已有 Preview 有额外效用。缺实地设备、真实 truth vintage 或平台检查时约束结论。没有证明数据存在或所有者已经授权。
4. 验证两份登记的状态和替代退出条件，检查没有暗加公共 API、排期、融合承诺或发行计划。当前材料是自审及提案。
