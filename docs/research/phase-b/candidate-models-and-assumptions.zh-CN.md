# 候选模型与比较条件

[导航](README.zh-CN.md) · [对象图](problem-estimand-map.zh-CN.md) · [推导](derivations-and-counterexamples.zh-CN.md) · [结果](experiments-and-results.zh-CN.md)

## B-E001 固定二元参数

单位须在固定截止 h 有互斥、穷尽且已经确定的结局。目标序列在给定 p 下 iid；单个纳入单位的下一次风险在该模型下也为 p。频率学派在未知固定 p 下对 X∼Bin(n,p) 反演，Bayes 在条件似然下给 p 的后验。两者可对同一个 p 检查覆盖和宽度，同时仍有不同概率解释。

| 方法 | 定义、意义与边界 |
|---|---|
| v1 Jeffreys | Binomial 与 Beta(1/2,1/2) 共轭，使用未调整的 .025/.975 后验分位。若 n=0 实际接口给 NO_HISTORY，若 n>0 但未过 gate 仍可估计；二元独立与语义一致在库外。 |
| Beta(1,1) | 分布平坦的先验敏感性对照，参数化改变会改变平坦含义；覆盖指标能检验稀有端点偏差。 |
| Wilson | 反演 score 不等式 (x/n−p)²≤z²p(1−p)/n，求二次根；无先验，近似覆盖，n=0 无区间。 |
| Clopper–Pearson | 反演上下二项尾各 .025，边界事件给 0 或 1。固定 n 且模型正确时至少 95% 覆盖，离散保守性可能使区间较宽。 |
| clipped Wald | 以样本比例 plug-in 方差的正态对照；裁剪只改范围，x=0 时仍退化。 |

Brown–Cai–DasGupta 的推荐和端点处理按其定义解读。本轮明确使用 v1 的原始 Jeffreys 端点；不能用论文中端点修饰的变体设为 v1 的外部认证。另分单侧零事件界与中心 95% 两侧区间。 [S0001](https://doi.org/10.1214/ss/1009213286) · [S0002](https://www.jhanley.biostat.mcgill.ca/c607/ch08/wilson_jasa_1927.pdf) · [S0003](https://jhanley.biostat.mcgill.ca/Reprints/If_Nothing_Goes_1983.pdf) · [现行行为](../../BEHAVIOR_SPEC.md)

## B-E002/B-E007 同一目标风险的借用

共同前提为事件语义、时距及目标相同。完整汇聚增加共享参数前提。条件交换性允许不同组参数但需要有意义的参考总体及足够多组来辨识异质性；先验本身不能识别隐瞒的机制漂移。组级外推与同一球员后续预测的验证分母不同。

| 方法 | 模型、控制与失败 |
|---|---|
| 目标独立 Jeffreys | 只使用目标已兑现计数，空目标弃权为实际 v1 基线。有估计后的决策门槛在 B-E002 另定义以对齐所有方法。 |
| 池化 | 起点 Beta(1/2,1/2)，累计来源目标 successes/failures；若 p 同一且观测独立则使用正确总似然，冲突则偏差随来源占比增加。 |
| 固定幂折扣 | 历史似然取 0.1 幂后更新，形式为 Beta(.5+.1x_s,.5+.1(n_s−x_s))。0.1 是预定敏感性点，随机幂时需要依赖幂参数的归一化。 |
| 宽成分混合 | 来自来源平滑均值 m 的 Beta(20m,20(1−m)) 加权，与 Beta(.5,.5) 混合，弱权 .2/.5。只有目标似然更新成分权；不同于从多试验层级拟合的完整 robust MAP。 |
| EB | 假定 p_j∼Beta(µκ,(1−µ)κ)。最大化组计数边际似然，在固定超参数下计算组 posterior mean。混合分量或无界 κ 有近不可辨识风险。 |
| 小网格 full Bayes | 同组似然，µ∼Unif(.05,.65)，logκ∼Unif(0,log M)，梯形积分传播超参不确定性。不同的 M 会改变先验，网格变细仅检查积分。一般规模的层级模型、commensurate priors 和 MAP 的推导可比较，尚无普适性能排名。 |

模型评价需要在合法关系下比较无借用、证据强度、异质性及冲突；给每个同义目标评估偏差/RMSE、覆盖、拒绝率与请求级损失。固定来源的精确枚举不平均新来源选择误差。实测棒球只比较预先给出的 18 名球员，而不证明新球队、别赛季或样本选择无偏。 [S0006](https://onlinelibrary.wiley.com/doi/abs/10.1111/biom.12242) · [S0007](https://pmc.ncbi.nlm.nih.gov/articles/PMC3951812/) · [S0030](https://pmc.ncbi.nlm.nih.gov/articles/PMC3134568/) · [S0096](https://pmc.ncbi.nlm.nih.gov/articles/PMC4626399/) · [S0087](https://jhanley.biostat.mcgill.ca/bios602/MultilevelData/EfronMorrisJASA1975.pdf)

## B-E003 目标混合、正性和依赖

目标 r=Σwₕpₕ，先要端点一致、条件机制可传递且每个正权层可测。若样本按均衡层数收集，粗样本率对应另一总体。权固定时使用层方差及层间协方差，权估计时考虑联合抽样。已知重复/簇键时按独立原子或独立簇诊断；未知重叠无法只从总数推断有效样本。按行 iid 做负对照，簇均值正态近似的条件是独立簇和足够簇数。嵌套层级/相关模型需要更多结构，按簇重抽须保持权和风险共同抽样的事实。无重叠时给部分识别范围。 [S0008](https://doi.org/10.1214/14-STS486) · [S0009](https://www.jmlr.org/papers/v8/sugiyama07a.html)

## B-E004 事件时间与观测机制

Aalen–Johansen 把原因专属 hazard 按全因无事件生存加权，目标是实际固定期发生概率；将竞争事件当独立删失的 1−KM 在本设计中估净风险量，对真正发生作误用对照。在无额外区间失访的构造中，最先完全失访以后的完整记录上的经验发生率等于 AJ；因此不能把两者相等当一般删失定理。部分失访要有风险集和独立删失（或经调整的条件独立及正性）。Fine–Gray 的亚分布风险面向类似 CIF 目标，但回归需要协变量和验证，此处检验绝对风险及识别。结果缺测/误标需要先验证机制。 [B-S0001](https://pmc.ncbi.nlm.nih.gov/articles/PMC4741409/) · [S0089](https://www.bmj.com/content/378/bmj-2022-071349)

## B-E005 评价、顺序和效用

同样冻结的预测，Brier=(p−y)²，log loss=−y log p−(1−y) log(1−p)。两者的期望在报真实概率时最小。这个性质依赖评分对象/结局过程，不能保证每期样本排名。连续分位预报的 WIS、CRPS 对分布风险使用，不能与事件 Brier 共用名次。可检查按组校准、发出时距、修订版本、条件覆盖和是否有标签，报告已发预测占比与全请求成本。以固定时点检验为监测基线，逐次窥视与明确界的对比只在给定 filtration 及独立或鞅条件下解释。 [S0005](https://sites.stat.washington.edu/raftery/Research/PDF/Gneiting2007jasa.pdf) · [S0013](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1008618) · [S0091](https://arxiv.org/abs/2110.00115) · [B-S0002](https://arxiv.org/abs/1810.08240)

## B-E006 计算对象、表示与数值预算

CDF/quantile 要比较相同形状与相同实数 x。生产普通路径用 log Gamma 和连分式，大参数路径用标准化 logit 积分。以高精度独立密度积分、参数反射和解析 arcsine 对照，分开计算点误差、分位邻点夹逼和 odds 舍入造成的实数门槛改变。精确十进制合同止于正确 binary64 舍入，本比较不把 C 的下游概率当无限精度赔率评估。数值失败状态与业务拒绝含义分别记录。 [S0050](https://dlmf.nist.gov/8.17) · [数值契约](../../NUMERICAL_CONTRACT.md) · [不完全 Beta 源码](../../../src/beta.c)

## 结构化保留的其他比较

- 同一时距的条件二元预测可比较基准率、logistic 与非参数预测；需要当时特征、校准集和实体外/时间外标签。仅计数不能检验外推。连续阈值可用 P(Y>t)=1−F(t)，遇点质量有 P(Y≥t)=1−F(t−)，稀疏分位网格难以识别阈值间质量。连续输出可用 CRPS/WIS；同一尺度、时距、真值和分位集合是比较条件。 [S0013](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1008618)
- 在齐次 Poisson 过程下，暴露 T 的零事件概率 e^(−λT)，不同时距的计数仅在过程假设下换算。过度离散、停机和反复故障应保留风险暴露/事件路径来对比，不把每设备故障次数当二项成功数。 [S0053](https://www.itl.nist.gov/div898/handbook/apr/section1/apr131.htm)
- 两边际给出 P(A∩B) 的 Fréchet 范围 [max(0,p_A+p_B−1),min(p_A,p_B)]。若 p_A=p_B=.4，A=B 或互斥分别达到 .4 或 0；乘积 .16 是额外独立设定。相同事件的两个预测不是两个事件；平均、专家贝叶斯信息汇合和相关输出校准需要同题表现及共享信息证据。故本轮不凭独立性假设做联合/融合排行榜。
