# 新问题、反例与证据缺口

[研究导航](README.zh-CN.md) · [逐项交叉表](ledger-crosswalk.zh-CN.md) · [搜索记录](search-log.md) · [复核与移交](verification-and-handoff.zh-CN.md)

## 临时问题登记

| 临时 ID | 可证伪问题及观测设计 | 与现有条目的区别 |
|---|---|---|
| NEW-A-001 | 实时首发真值与成熟修订真值能否颠倒相同预测的排名？保留每个发布日期的真值及当时可得的训练版本，与固定延迟和终态分别配对评分。 [S0034](https://www.nature.com/articles/s41467-024-50601-9) · [S0081](https://www.cdc.gov/flu-forecasting/evaluation/2024-2025-report.html) | E47 保存/重算，D35 评分；此处研究标签修订政策是否改变可比结论。 |
| NEW-A-002 | 观察标签是否因使用预报而变得可见或改变？比较全人群抽查、按行动决定的有标签子集以及观测等价界。 [S0029](https://www.kdd.org/kdd2017/papers/view/the-selective-labels-problem-evaluating-algorithmic-predictions-in-the-pres) | B21 一般选择偏差；此处含部署策略→记录/结局反馈，静态抽样权不足以说明干预后验证。 |
| NEW-A-003 | 业务每周看分数并据此停止或调阈值，固定样本区间是否仍覆盖？比较预先固定窗口、有效的 confidence sequence，定义 time-varying score difference 对象并检查损失界。 [S0091](https://arxiv.org/abs/2110.00115) | C34 是过程变化，D35 是评分；本题是评估本身的可选停止。 |
| NEW-A-004 | 历史标签在同一事件版本下，测量误差是否随设备和时段改变？做独立双标、抽查及误分类敏感性，比较已知/未知灵敏度与特异度。 [S0022](https://pubmed.ncbi.nlm.nih.gov/31649194/) · [S0054](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/e9r1-statistical-principles-clinical-trials-addendum-estimands-and-sensitivity-analysis-clinical) | B13 端点语义；这里考察同一端点的观测误差模型。 |
| NEW-A-005 | 目标队列的计划构成权若同风险估计共用数据，独立层公式误差有多大？以配对簇重采样或联合模型传播权误差，比较覆盖。 [S0009](https://www.jmlr.org/papers/v8/sugiyama07a.html) · [S0008](https://doi.org/10.1214/14-STS486) | B18/B21 区分汇总与目标；这里关注估计权与估计风险的联动不确定性，超出 Preview 固定权。 |
| NEW-A-006 | 在同一输入输出精度下，数值边界附近分类有多稳定？区分输入 o 舍入引起的阈值变化、CDF 误差及分类容差；用相邻值与独立参考构造认证/未定区域。 [S0025](https://docs.oracle.com/cd/E19957-01/806-3568/ncg_goldberg.html) · [S0050](https://dlmf.nist.gov/8.17) | E48 一般数值边界与 #5 分位表示；这里追查误差穿越政策分支的条件及影响。 |
| NEW-A-007 | 方法在愿意给出估计的子集评分更优，加入弃权成本及分组输出率后是否反转？规定所有请求分母、时距及损失；比较同题共同覆盖和实际服务策略。 [S0029](https://www.kdd.org/kdd2017/papers/view/the-selective-labels-problem-evaluating-algorithmic-predictions-in-the-pres) · [S0092](https://pmc.ncbi.nlm.nih.gov/articles/PMC7034331/) | D42 给定概率决策；此处评价有选择发出概率的系统。已有 Preview 合成弃权对照，实地验证和机会成本仍缺。 |

## 会改变推断的反例

- 同样记录可来自两个在目标无支撑层风险分别 .0 和 1.0 的机制；再抽同来源无法判别。稳健 MAP 可以减轻已有数据表明的冲突，无目标数据时无法学习冲突。旧 Preview 的 `hidden_conflict_zero` 已报告宽区间仍可全错向的合成反例，不能当真实设备性能。 [S0006](https://doi.org/10.1111/biom.12242) · [S0028](https://ageconsearch.umn.edu/record/292716) · [Preview 比较](../../PREVIEW_PROBABILITY_MODELS.zh-CN.md)
- 对各占一半的两个子群，真风险 .1/.9，统一发 .5 的系统在混合总体校准且毫无分辨率，两个组均失准。记录依赖的重复还会使名义精度增加而均值和点分数几乎不动。此处是构造反例，应用证据另见软件/案例报告。 [S0004](https://sites.stat.washington.edu/raftery/Research/PDF/Gneiting2007jrssb.pdf) · [S0022](https://pubmed.ncbi.nlm.nih.gov/31649194/)
- 相同边际 P(A)=P(B)=.4 可来自 A=B 或互斥，交集 .4 或 0。两位同看一个原始信号的专家转述重复了信息。缺来源图时，识别不足不能由把两数相乘排除。 [S0018](https://academic.oup.com/jrsssb/article/72/1/71/7076442) · [S0088](https://www.w3.org/TR/2013/REC-prov-o-20130430/)
- 随访停在 50 小时且停试者截至当时无故障，若 100 小时才是目标，将其当补事件会增加虚假生存证据。若是竞争原因而非普通删失，目标和估计过程还要重新定义。 [S0014](https://doi.org/10.1080/01621459.1958.10501452) · [S0089](https://www.bmj.com/content/378/bmj-2022-071349)

## 保留给后续评价的证据需求

实际固定期设备现场数据缺少可公开复验的一致端点、入组和依赖说明。医疗、市场和天气的可比性实证不能补上这一缺口。来源—目标机制关系和选择性标签的处理依赖域主提供的实测。技术上缺替代 libm/ARM 工具链的同样本极端回归，现有结果不能证明更强数值合同。出版商响应 403/202/203 或传输失败的条目在源登记保留访问级别；仅元数据的条目用于定位研究问题。后续可优先检验 no-pool、当前严格历史及领域常数等简单基线，然后比较借用或模型扩展对同一 estimand 的作用。

若需要判断数学可行性，先问可否定义可重复的单位、观测条件和目标时间，并给出在未知目标支撑、依赖和迟报下的结论边界。若需要比较多种方法的接口或产品归属，先确认估计对象是否相同，明确调用方证据、域外验证和数值任务各自的可独立性。研究不在本文件预定范围或方案。
