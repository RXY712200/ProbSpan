# 方法、估计对象与关键假设

[研究导航](README.zh-CN.md) · [源登记](source-register.tsv) · [逐项交叉表](ledger-crosswalk.zh-CN.md)

## 概率与区间

同一个数 .2 可能是特定总体的频率参数、个人在当前信息集下的信念、条件预测分布对事件区域的质量，或对未知参数的后验均值。先写出单位、端点、风险期、可用时点、总体及条件，再问哪些机制可重复。采用一致概率公理并不能识别参考类。Bayesian posterior 依赖似然和先验，频率覆盖依赖重复取样设计。Dawid 的内部校准论证及 Gelman–Shalizi 的外部模型批判回答不同问题。 [S0012](https://doi.org/10.1080/01621459.1982.10477856) · [S0049](https://pmc.ncbi.nlm.nih.gov/articles/PMC4476974/)

95% credible interval 对给定数据和模型下参数赋予后验质量；95% confidence interval 是重复取样过程的覆盖性质；prediction interval 对一个指定时距的新结果或新批次定义覆盖。离散分布的区间通常不能任意精确达到名义覆盖。不确定性可按条件分解为结果随机性与参数/模型不确定性，但分类随信息集变化。给定模型内的后验不会自动传播端点误判、模型结构或未知选择偏差。ProbSpan 的主观区间是冻结的 logit 宽度规则，概率输入的 clamp 和区间端点均无法给出经验保证。 [S0001](https://doi.org/10.1214/ss/1009213286) · [S0004](https://sites.stat.washington.edu/raftery/Research/PDF/Gneiting2007jrssb.pdf) · [S0058](https://www.ipcc.ch/site/assets/uploads/2017/08/AR5_Uncertainty_Guidance_Note.pdf)

一次性事件可用明确的参考类、特征模型或 elicitation 表达当前信念。种子题需与目标领域、难度及时距相当，先独立给出分位数/理由再讨论以降低锚定；共同证据需单列。可用等权作为专业表现加权的基线，使用未见种子题比较区间覆盖、信息度和评分，不把专家共识误当新观测。不同观点可并列并由决策者显式承担假设。 [S0020](https://doi.org/10.1093/reep/rex022) · [S0021](https://doi.org/10.1016/j.ress.2017.02.003) · [S0055](https://doi.org/10.2903/j.efsa.2014.3734)

## 单参数二项、稀有事件及后验预测

给定共同参数 p，独立观测的似然与 p^e(1−p)^c 成比例。Beta(a,b) 先验更新为 Beta(a+e,b+c)；Jeffreys 取 a=b=1/2，均匀先验取 1/1。目标无观测时这些分布只表达假设；v1 此时给 NO_HISTORY。单次新单位的预测概率为后验均值 m。未来 k 个可比单位共用未知 p 时，积分得到 Beta-binomial，方差为 k m(1−m)+k(k−1) Var(p)。把后验均值当已知并使用 Binomial 会丢失第二项。 [S0001](https://doi.org/10.1214/ss/1009213286) · [S0007](https://pmc.ncbi.nlm.nih.gov/articles/PMC3951812/)

Wilson 区间反演 score 检验。Clopper–Pearson 反演二项尾得到保守覆盖，宽度、端点和方向应与目标比较。零次失败、n 次独立试验时，单侧上界 U 解 (1−U)^n=.05，故 U=1−.05^(1/n)，大 n 下约为 2.996/n。双侧中心区间上尾应用 .025；Jeffreys 后验的上尾是不同估计对象。Wald 的样本方差在零事件退化到零。v1 gate 还要求 n≥20 且中心后验区间宽≤.25。即使通过，也需要验证抽样、时距和适用性。 [S0001](https://doi.org/10.1214/ss/1009213286) · [S0002](https://doi.org/10.1080/01621459.1927.10502953) · [S0003](https://jhanley.biostat.mcgill.ca/Reprints/If_Nothing_Goes_1983.pdf)

反例复算（Python 标准库，执行结果见[复核](verification-and-handoff.zh-CN.md)）采用 Wilson 公式及二项枚举。比较真实 p=.01, n=20 的无事件概率、单侧上界与 Wald/Wilson 覆盖。枚举可重复检查方法的条件覆盖，并不模拟制造或设备记录。

## 迁移、借用与识别

定义来源 S 与目标 T。若 p_T(y|x)=p_S(y|x)，且目标每个正权点在来源有支持，则 q_T=Σ_x p_S(Y=1|x)P_T(x)，连续 x 用积分。可比较模型中用 w(x)=dP_T/dP_S 权重；截断会改变偏差/方差与目标，权重估计和证据生成联合变化需重采样。label shift 假定 p(x|y) 稳定、类比例变动；concept shift 指条件机制变动；协变量重叠既不能检验潜在机制一致，也不能修复结局测量不同。因果 transportability 要另外明确干预、选择节点及可识别条件。 [S0008](https://doi.org/10.1214/14-STS486) · [S0009](https://www.jmlr.org/papers/v8/sugiyama07a.html) · [S0085](https://proceedings.mlr.press/v80/lipton18a.html) · [S0051](https://www.fda.gov/media/164960/download)

若未覆盖层目标权 u，已覆盖层贡献为 L，且仅知未覆盖风险位于 [0,1]，则目标风险在 [L,L+u]；这只是识别集，还未计入已覆盖层及权重估计误差。若两个机制具有相同可观测分布但该层风险分别为 0 和 1，则任意基于同样输入的估计器无法在两机制同时一致。该反例也适用于完全无相关历史。缺失结局的可观测边际同理；无约束时未验证个案可全为事件或全为补事件。 [S0028](https://ageconsearch.umn.edu/record/292716) · [S0029](https://www.kdd.org/kdd2017/papers/view/the-selective-labels-problem-evaluating-algorithmic-predictions-in-the-pres)

无汇聚基线保留目标辨识及大方差；完全汇聚额外要求共同参数；层级模型要求各组参数在特定协变量/超参数下交换。Beta-binomial 经验 Bayes 从独立组估计 (a,b)，plug-in 忽略超参数变动；全层级 Bayes 联合传播但仍受超先验、组数量、不平衡和选组机制影响。目标标签已参与超参数拟合时，评估必须按部署时可见信息重建，不能当未见组。MAP 预测的是新组参数，稳健 MAP 以弱先验混合，后验权随目标边际似然比更新。零目标数据时边际似然比为 1。power prior 用历史似然 L_0(θ)^a 更新，若随机 a 则归一化常数 C(a) 影响其分布；commensurate prior 显式刻画组间参数差异。宽成分、折扣及收缩都依赖候选历史有正当关系。对每个方法应同时观察目标留出、共机制/漂移、零/少目标、覆盖、阈值错误及偏差。 [S0006](https://doi.org/10.1111/biom.12242) · [S0007](https://pmc.ncbi.nlm.nih.gov/articles/PMC3951812/) · [S0030](https://pmc.ncbi.nlm.nih.gov/articles/PMC3134568/) · [S0031](https://doi.org/10.1002/sim.9124) · [S0096](https://pmc.ncbi.nlm.nih.gov/articles/PMC4626399/)

## 证据生成、相关和测量

端点需有互补定义、风险期起止、单位身份、纳排及标签确认规则。重复键可由来源标识、逻辑版本、时间窗及快照解释；不同键仍可能共享主体或故障。m 个等长的组内记录、组内相关 ρ 时，均值方差的设计效应为 1+(m−1)ρ，需独立组及共同方差。仅把 n 除以该量不能一般地恢复二项似然或精确尾。可比较 cluster bootstrap、随机截距和 GEE，并检查小簇数、信息性簇大小及跨簇的时间冲击。总体权变化可在所有层的关联方向不变时产生 Simpson 反转；先定目标及因果问题，再决定分层变量。 [S0024](https://doi.org/10.1111/j.2517-6161.1951.tb00088.x) · [S0072](https://proceedings.mlr.press/v286/bhadane25a.html) · [S0039](https://aws.amazon.com/message/41926/)

右删失说明到某时刻尚未发生，之后未知。报告延迟产生报告日期与事件日期两个时钟；幸存者进入队列可产生左截断。信息性缺失、误标、选择在结果发生以后产生选择偏差；欲校正需抽样概率、验证样本或行为模型。若二类测量灵敏度 Se、特异度 Sp 均已知且可迁移，观测率 r = Se·p+(1−Sp)(1−p)，当 Se+Sp≈1 时反演不稳定。若 Se、Sp 未知，更多同样的带误差标签不能独立识别 p。训练时误用后填字段、重复对象跨集合或用未来真值标准化，是评价泄漏的不同路径。 [S0022](https://pubmed.ncbi.nlm.nih.gov/31649194/) · [S0027](https://doi.org/10.1145/2382577.2382579) · [S0029](https://www.kdd.org/kdd2017/papers/view/the-selective-labels-problem-evaluating-algorithmic-predictions-in-the-pres) · [S0053](https://www.itl.nist.gov/div898/handbook/apr/section1/apr131.htm)

## 其他目标和模型

| 目标 | 可比较方法及适用条件 | 失败边界 |
|---|---|---|
| P(Y=1∣x)，例如下一个同条件个体固定时距事件 | logistic GLM 或分层 logistic，样本外校准；柔性模型可用非参数先验、树模型或曲线平滑 | 完全分离、罕见特征、域漂移、遗漏交互、输入不存在于预测时。 [S0016](https://doi.org/10.2307/2344614) · [S0017](https://doi.org/10.1214/aos/1176342360) |
| 下一时期事件次数或单位暴露率 | Poisson GLM log(均值)=log(exposure)+xβ；负二项能表达方差增长；间歇事件另比较 hurdle/零膨胀 | 0 次可能是零暴露、结构性零或尚未报告；Poisson 到至少一件的 1−exp(−λt) 依赖过程假设。 [S0016](https://doi.org/10.2307/2344614) · [S0040](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3164764) |
| P(T≤h) 或特定原因的累积发生 | Kaplan–Meier 适用于适当删失，Cox 相对 hazard 需基线才能给绝对风险；竞争风险可用 cause-specific hazards 加全因生存，或 Fine–Gray 模型 | 把竞争原因当普通删失会估计另一目标，固定期状态不可把中途停试算补事件。 [S0014](https://doi.org/10.1080/01621459.1958.10501452) · [S0015](https://doi.org/10.1080/01621459.1999.10474144) · [S0046](https://doi.org/10.1111/j.2517-6161.1972.tb00899.x) |
| 连续 Y 的分位与阈值事件 | 预测 CDF F，P(Y>t)=1−F(t)，P(Y≥t)=1−F(t−)，点质量使两者不同；集合/分位输出只能给分辨率内信息 | 直接插值稀疏分位数会隐藏尾和跳点假设；连贯性需检验。 [S0004](https://sites.stat.washington.edu/raftery/Research/PDF/Gneiting2007jrssb.pdf) · [S0013](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1008618) |
| 新日期、固定时距的条件预测 | 季节朴素基准、动态 GLM/状态空间、滚动窗口或在线更新 | 随机切分含未来信息；旧季节的条件分布、剧变后的过程及真值修订需单列。 [S0032](https://pubmed.ncbi.nlm.nih.gov/18239110/) · [S0060](https://otexts.com/fpp3/tscv.html) |
| P(A∩B) 或组合决策 | Fréchet 界 max(0,p_A+p_B−1) 到 min(p_A,p_B)；联合观测、潜因子、copula 或明确条件概率可缩小范围 | 单独边际不确定相关，p_Ap_B 需要独立；P(A∣B) 需要 p_B>0。 [S0028](https://ageconsearch.umn.edu/record/292716) · [S0039](https://aws.amazon.com/message/41926/) |
| 多个对同一事件的信念/模型分布 | 检查定义、共同先验和数据血缘；用单模型/等权作基线并评估重新校准、权重正则化及依赖组合 | 校准输入的线性池也可能失校准；共享一个数据源的两个概率不能当两次独立似然。 [S0018](https://academic.oup.com/jrsssb/article/72/1/71/7076442) · [S0034](https://www.nature.com/articles/s41467-024-50601-9) |

## 预测核验、决策与数值

对二元已兑现 y，Brier=(p−y)²，log loss=−y log p−(1−y)log(1−p)。前者的校准/分辨率/不确定性分解与分箱方案有关，后者强罚自信错误，裁剪改变评分规则的使用条件。排序/AUC、可靠性、尖锐度各回答不同问题。CRPS 积分 CDF 对阈值的误差；中心分布预测 WIS 由宽度及超界罚构成。基线应随任务变化，二元常数频率、季节朴素和未校准模型均可作为事先明确的比较；用同一问题、提交时距、真值版本作配对，按事件/地点/时间块处理相关，报告组间异质性及评分差的不确定性。模型准则与评价指标若使用同一测试集调参，需保留新的检验数据。 [S0004](https://sites.stat.washington.edu/raftery/Research/PDF/Gneiting2007jrssb.pdf) · [S0005](https://sites.stat.washington.edu/raftery/Research/PDF/Gneiting2007jasa.pdf) · [S0013](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1008618)

split conformal 在交换数据下利用校准残差秩得到边际预测覆盖。精确无分布条件覆盖在连续 x 下通常迫使区间无信息；加权 conformal 对指定 covariate shift 与密度比要求具有不同保证。平均预测校准可掩盖子群失准，proper score 优势不证明真实因果解释或可安全迁移。在选择性真值、罕见子群和频繁回测中应报告缺失比例、多个时点和相对基线，必要时弃答并说明原因。 [S0010](https://www.stat.berkeley.edu/~ryantibs/papers/limits.pdf) · [S0011](https://proceedings.neurips.cc/paper/2019/file/8fb21ee7a2207526da55a679f0332de2-Paper.pdf) · [S0022](https://pubmed.ncbi.nlm.nih.gov/31649194/) · [S0029](https://www.kdd.org/kdd2017/papers/view/the-selective-labels-problem-evaluating-algorithmic-predictions-in-the-pres)

单位本金、含本金返还赔率 o 下，EV=op−1，阈值 1/o。历史正 EV 概率为参数后验质量 P(p>1/o∣D)；下一次有正回报的概率是预测 P(Y=1∣D)。若非线性效用、行动成本、共同暴露或多个行动存在，需要行动条件下的联合损失；会影响事件结果的行动还需因果识别。可在识别集上比较支配、最坏后悔或条件价值。信息价值衡量知道新增数据后可改善的最优期望损失，依赖现行信念、成本和行动集，不能从区间宽度直接得出。 [S0028](https://ageconsearch.umn.edu/record/292716) · [S0041](https://pubsonline.informs.org/doi/abs/10.1287/mnsc.1080.0964)

正则化不完全 Beta I_x(a,b) 用积分除以 B(a,b)。补尾可用 I_(1−x)(b,a)，极小尾从 1−CDF 相减会消失；邻端点的 1−x 自身也可能舍入。lgamma 相减未必保留大参数相对小增量；可比较区域化渐近、连分式、logit 积分和高精度基准。单调 bracket 与残差共同检查逆函数；在极集中参数区一个 ulp 的 x 跨越相当概率质量，应报告相邻浮点夹逼。缩放、浮点模式与错误状态属于计算契约，不能代替有效似然。十进制转换关注完整输入相对中点和 tie-even；模式/locale 与词法范围需显式。 [S0025](https://docs.oracle.com/cd/E19957-01/806-3568/ncg_goldberg.html) · [S0026](https://doi.org/10.1145/131766.131776) · [S0048](https://www.ampl.com/REFS/rounding.pdf) · [S0050](https://dlmf.nist.gov/8.17)
