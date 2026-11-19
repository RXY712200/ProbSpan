# 架构与兼容性

| 方案 | 收益 | 成本与结论 |
|---|---|---|
| 在 v1 库增量增加符号 | 单一链接入口 | 改包版本会让 SameMajorVersion 拒绝旧请求，且增大数值合同传播范围。 |
| 同仓独立 C11 模型库 | 旧安装路径可独立保持，新功能可以冻结自身合同 | 双安装包和测试矩阵。推荐作为核心形态。 |
| C11 双包加可选调用方工具 | 能保留 Python 标准化参考及证据审核，开发依赖不传播 | 分发文档要区分源码、默认安装与可选环境。推荐组合。 |
| 整合拟合、存储、准入与预测 | 对单一场景可能节约集成成本 | 信息集和数据结构耦合，无法遵守现有责任边界。拒绝。 |

建议保留根 ProbSpan 1.1.0 的包合同与 ProbSpan::probspan，单独由 v2 子项目安装 ProbSpanModels 2.0.0 与 ProbSpanModels::models，头目录 probspan_models/，符号 ps2_。v2 产品源发行身份由 GitHub 标签/发布元数据、源码发行清单及 v2 子包声明。根 CMake 配置仍对应 legacy 组件。共同前缀中两个包的文件、target、版本文件互不覆盖。验证 CMake 3.16 的 configure/install， 同时加载两包，验证反序加载。可选 Python CLI 继续通过 1.1.0 EXACT 及协议版本验证旧包。把旧 CMake 根包改为 2.0.0 会打破已存在的查找请求，即使链接符号兼容。若必须统一包名或替换旧产物，需先单独审批迁移合同。

依赖方向：旧应用 → 旧头和归档 → 现有私有数学叶节点。新应用 → 新专用 C11 接口 → 区间、预测、标准化、竞争风险、评分各自模块 → 同合同的有限检查、补偿求和、受限数学叶节点 → C/libm。可选设备进程 → 已安装旧公共接口。参考脚本 → 独立高精度计算与已知精确枚举，运行产物不得成为运行依赖。建议保留 MIT、无新增外部 C 运行依赖，开发参考的许可和版本单独登记。

旧边界按 [公共头](../../../include/probspan/probspan.h) 和 [兼容合同](../../COMPATIBILITY.md) 保持 13 函数、布局、ABI 1、参数检查优先级与失败写回。历史估计通过 [historical.c](../../../src/historical.c)，分析决策通过 [historical_analysis.c](../../../src/historical_analysis.c)、[decision_geometry.c](../../../src/decision_geometry.c)，赔率与因果顺序分别由 [decimal.c](../../../src/decimal.c) 与 [provenance.c](../../../src/provenance.c) 持有。Beta 内核 [beta.c](../../../src/beta.c) 和 [beta_logit.c](../../../src/beta_logit.c) 先保持私有。只有同编码输入、尾方向、数值失败和容差均经独立证明才评估提取，绝不让新域扩大旧 solver 隐含承诺。预测计数 PMF 用独立递推。标准化只叠加固定权风险。竞争风险有自己的风险集，预测评分有自己的请求掩码。EV 的概率、区间、后验 EV 质量三者不互换。多模块共用的状态字面值不能替代结果类型。

兼容验证须保留旧 EXACT 与非 EXACT CMake 配置、链接之前用旧头编译的对象到新分发的 legacy 归档、并核验旧公开符号与用例执行。测试不作跨 CRT 或跨架构链接保证。v2 数学参数合同与 ABI 独立版本化。发布前明确安装包名、二进制边界与源发行版本，禁止以产品主版本替代 ABI 协议版本。

## 产品、分发与消费的唯一推荐组合

| 层 | 推荐标识和责任 |
|---|---|
| GitHub | 一个候选产品名 ProbSpan 2.0.0，最终 tag 拟为 v2.0.0，须独立接受和另行授权。源码 ZIP/tar.gz 对应同一树，内含 legacy 与 models、参考及许可证；默认分发无编译资产。发布说明明列两个组件版本。 |
| legacy | 仓库根的 project(ProbSpan VERSION 1.1.0)、ProbSpanConfigVersion 和公开版本宏均为 1.1.0，ABI 1。目标 ProbSpan::probspan、旧头与 libprobspan 归档路径沿旧包装。 |
| models | 建议子目录 models/，project(ProbSpanModels VERSION 2.0.0)，独立 Config/ConfigVersion（SameMajorVersion）、头 probspan_models/、归档 probspan_models、导出目标 ProbSpanModels::models。由自身包报告 2.0.0，新增 ABI 代数单独定义，首版建议 1。 |
| 配置查找 | 旧调用保持 find_package(ProbSpan 1.1.0 EXACT CONFIG REQUIRED)。新调用用 find_package(ProbSpanModels 2.0 CONFIG REQUIRED) 并链接新目标，或以 2.0.0 EXACT 锁定。两者用 CMAKE_PREFIX_PATH 指向明确前缀，核对 *_DIR 实际路径。 |

分开配置与安装，例：cmake -S . -B build-legacy，cmake -S models -B build-models，各自构建后 cmake --install <build> --prefix <prefix>。先各自用清洁前缀测试本包消费且另一包不可见（禁 registry 和系统回退），再在同一干净前缀双序安装：逐路径比较 install_manifest，无重复写入，核对版本文件，分别配置 legacy EXACT、旧 1.0 请求、新包 EXACT 及混合消费者；交换 find_package 顺序并执行。用错主版本必须拒绝。解除可选运行依赖后重复。共享部署还应对照已用旧头/同 CRT 编出的对象及既有真实设备消费者。

一个统一的 ProbSpan 2.0.0 CMake 包即使保留旧符号，仍使旧 EXACT 发现失败。强制兼容 1.x 的自定义版本脚本也不能正确报称同一包 metadata 同时为 1.1.0 EXACT 和 2.0.0。另一可行方案是各自独立 GitHub 发行，两次审查和制品管理成本更高。所有者需选择是否接受一个 2.0.0 产品源码发行含两组件，根继续标 1.1.0，models 标 2.0.0，独立安装可共享前缀；若要求单一包或独立发行，先重新决定旧 EXACT 的可支持范围和回归计划。
