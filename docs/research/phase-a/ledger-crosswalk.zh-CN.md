# 52 项证据交叉表

[研究导航](README.zh-CN.md) · [源登记](source-register.tsv) · [方法](methods-and-assumptions.zh-CN.md) · [新增问题](new-questions-and-gaps.zh-CN.md)

标题、状态和既有行为直接对应固定版[永久账本](../../TECHNICAL_DEBT.zh-CN.md)。既有行为栏保留账本的 v1.0.0 叙述，v1.1.0 的窄范围调用方补充见下方及[设备 Preview](../../PREVIEW_DEVICE_HISTORY.zh-CN.md)。分类是本次研究维度。状态 OPEN 的 C28 是输入证据语义限制。RESOLVED A01/A06/A07/D43 只代表限定能力。R 条目是已解决历史。研究关系引用账本后由下列问题检验，产品依赖尚待决定。

证据的适用层级见源登记：理论证明、经验验证、软件实现、讨论各自有不同支持范围。外部材料链接只指本项问题及假设，当前支持以账本和固定源码为证据。涉及 Preview 的 B13/B14/B18–B21/D37–D39/E46/E47 均先读准入和标准化的真实边界。

## A01 — 充分且可比的二元事件历史

RESOLVED · 计算、证据准入 · [A01 原始条目](../../TECHNICAL_DEBT.zh-CN.md#a01)

- 既有行为：history_estimate 接收非负计数，给 Jeffreys 后验与 gate；不审核工厂的抽样论证。
- 目标和前提：固定端点下下一同类单位的 Bernoulli 风险 p；条件 iid、机制稳定。条件交换性与目标总体稳定是外部假设，更多样本不能消除系统偏差。
- 仓库验证线索：oracle_parity/check_history 与 large_numerics 检查后验与 gate，真实工厂适用性须域外验证。
- 相关研究问题：B13、D37 是输入合法性的先决条件。
- 外部贡献与待查：比较同条件独立批次与随机同一批次的覆盖；后者不能由 gate 核验。 [S0001](https://projecteuclid.org/journals/statistical-science/volume-16/issue-2/Interval-Estimation-for-a-Binomial-Proportion/10.1214/ss/1009213286.full) · [S0044](https://itl.nist.gov/div898/handbook/pmc/section6/pmc611.htm) · [S0052](https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc332.htm)

## A02 — 稀疏历史与统计就绪

PARTIAL · 验证、决策语义 · [A02 原始条目](../../TECHNICAL_DEBT.zh-CN.md#a02)

- 既有行为：n>0 提供均值/区间，未过 gate 为 INSUFFICIENT；历史决策不可用。
- 目标和前提：稀疏目标 p 与是否足以出决策为两问。缩窄区间可能仅来自额外假设，不代表新增独立证据。
- 仓库验证线索：现有 check_history 覆盖不足状态；未来需比较覆盖率、借用偏差与零样本行为。
- 相关研究问题：B14→B15/B16；先 #10 可比性再 #9 借用强度。
- 外部贡献与待查：比较区间覆盖与拒绝率，保留无借用基线，避免用宽度反推适用。 [S0001](https://projecteuclid.org/journals/statistical-science/volume-16/issue-2/Interval-Estimation-for-a-Binomial-Proportion/10.1214/ss/1009213286.full) · [S0002](https://www.jhanley.biostat.mcgill.ca/c607/ch08/wilson_jasa_1927.pdf) · [S0003](https://jhanley.biostat.mcgill.ca/Reprints/If_Nothing_Goes_1983.pdf) · [S0065](https://github.com/statsmodels/statsmodels) · [S0071](https://stats.stackexchange.com/questions/82720/confidence-interval-around-binomial-estimate-of-0-or-1)

## A03 — 无自身历史的一次性事件

RESEARCH · 识别 · [A03 原始条目](../../TECHNICAL_DEBT.zh-CN.md#a03)

- 既有行为：可输入主观估计；0/0 历史为 NO_HISTORY，不凭空生成该并购的证据。
- 目标和前提：一次事件对条件参考类的预测风险。参考类选择偏差、定义迁移和专家依赖可能主导结果。
- 仓库验证线索：未来预注册可比任务与留出案例，检验区间与校准；不能用一次结果验真。
- 相关研究问题：A05、B14、C22、D44。
- 外部贡献与待查：预先定义参考类并留出事件；多个参考类风险差异可以报告为敏感性。 [S0019](https://faculty.wharton.upenn.edu/wp-content/uploads/2015/07/2014---psychological-strategies-for-winning-a-tournament.pdf) · [S0055](https://aanzfta.asean.org/AECSP/ASEAN-SPS-Guide/files/media/2020/09/EFSA_Guidance-on-expert-knowledge-elicitation-in-food-and-feed-safety-risk-assessment.pdf)

## A04 — 低重复任务与跨事件预测表现历史

RESEARCH · 验证 · [A04 原始条目](../../TECHNICAL_DEBT.zh-CN.md#a04)

- 既有行为：核心无预测日志、评分或跨任务校准；provenance 只有暴露因果标记。
- 目标和前提：任务族、时距与信息条件下的预测者表现。任务组交换性、结果完整性、选择性上报、预测时可见信息和分布漂移。
- 仓库验证线索：未来防止同事件多次预测泄漏，按事件/时间分割，比较未校准基线与校准误差。
- 相关研究问题：D35、D36、D38、B19/B20。
- 外部贡献与待查：按题分块，与基准配对；同事例多预报需要明确定义权重。 [S0004](https://sites.stat.washington.edu/raftery/Research/PDF/Gneiting2007jrssb.pdf) · [S0012](https://kylewoodward.com/blog-data/pdfs/references/dawid-journal-of-the-american-statistical-association-1982A.pdf) · [S0019](https://faculty.wharton.upenn.edu/wp-content/uploads/2015/07/2014---psychological-strategies-for-winning-a-tournament.pdf) · [S0027](https://doi.org/10.1145/2382577.2382579) · [S0033](https://www.ecmwf.int/sites/default/files/elibrary/2017/18198-25-years-ensemble-forecasting-ecmwf.pdf) · [S0035](https://pubmed.ncbi.nlm.nih.gov/35394862/) · [S0043](https://html.rhhz.net/yyqxxb/html/20020103.htm) · [S0047](https://doi.org/10.1016/j.ijforecast.2019.04.014) · [S0060](https://otexts.com/fpp3/tscv.html) · [S0075](https://github.com/scikit-learn/scikit-learn/issues/19072)

## A05 — 无相关历史也无支持证据

FUNDAMENTAL_LIMIT · 不可识别 · [A05 原始条目](../../TECHNICAL_DEBT.zh-CN.md#a05)

- 既有行为：不从文字生成概率；0/0 返回无历史；主观路径要求调用者自报数值。
- 目标和前提：同一无信息输入可对应任意 p。任意先验可数值化信念，但其精确数字不是被数据识别的事实。
- 仓库验证线索：验证无历史标志与 UI 不读取不可用字段；没有一次测试能证明通用无信息推断。
- 相关研究问题：A03、C22、D44。
- 外部贡献与待查：保持无法判断；先验结果须标信念，依赖假设时用识别集。 [S0010](https://www.stat.berkeley.edu/~ryantibs/papers/limits.pdf) · [S0028](https://ageconsearch.umn.edu/record/292716/files/uwmad-0066.pdf) · [S0029](https://www.kdd.org/kdd2017/papers/view/the-selective-labels-problem-evaluating-algorithmic-predictions-in-the-pres) · [S0049](https://pmc.ncbi.nlm.nih.gov/articles/PMC4476974/) · [S0058](https://www.ipcc.ch/site/assets/uploads/2017/08/AR5_Uncertainty_Guidance_Note.pdf) · [S0092](https://pmc.ncbi.nlm.nih.gov/articles/PMC7034331/)

## A06 — 无历史的主观概率

RESOLVED · 决策语义 · [A06 原始条目](../../TECHNICAL_DEBT.zh-CN.md#a06)

- 既有行为：subjective_estimate(60) 可独立调用，保留 raw/used 和模型版本。
- 目标和前提：用户自报百分数和约定范围。主观区间不是置信区间，0/100 的 clamp 不表示真实绝对确定。
- 仓库验证线索：check_subjective 的 101 raw 与半宽边界；未来保持离散字段精确。
- 相关研究问题：D39 区间解释、D38 来源记录。
- 外部贡献与待查：区间质量需专家种子题/留出，clamp 不提供经验覆盖。 [S0012](https://kylewoodward.com/blog-data/pdfs/references/dawid-journal-of-the-american-statistical-association-1982A.pdf) · [S0020](https://academic.oup.com/reep/article/12/1/113/4835830) · [S0049](https://pmc.ncbi.nlm.nih.gov/articles/PMC4476974/) · [S0058](https://www.ipcc.ch/site/assets/uploads/2017/08/AR5_Uncertainty_Guidance_Note.pdf)

## A07 — 无主观值或赔率的历史概率

RESOLVED · 计算 · [A07 原始条目](../../TECHNICAL_DEBT.zh-CN.md#a07)

- 既有行为：history_estimate(12,8) 独立成功，gate 未过仍可按 has_estimate 读取区间。
- 目标和前提：计数条件下 p 的后验均值和区间。计数仍须可比，统计就绪不等于业务适用。
- 仓库验证线索：oracle_parity/check_history；导读提供无赔率完整示例。
- 相关研究问题：A01、D37；不依赖主观模型。
- 外部贡献与待查：区分估计可用与历史分析可用；调用方不得编造决策输入。 [S0001](https://projecteuclid.org/journals/statistical-science/volume-16/issue-2/Interval-Estimation-for-a-Binomial-Proportion/10.1214/ss/1009213286.full) · [S0052](https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc332.htm)

## A08 — 不同概率任务需要不同模型

PARTIAL · 测量、估计量 · [A08 原始条目](../../TECHNICAL_DEBT.zh-CN.md#a08)

- 既有行为：只有冻结主观规则和 Bernoulli Jeffreys；没有通用分布目录。
- 目标和前提：二元、次数、连续、时间目标各自似然。错误路由会产生数值合理但语义无效的结果。
- 仓库验证线索：未来用不支持任务拒绝案例与类型/版本兼容测试。
- 相关研究问题：C25、C30–C34、E46。
- 外部贡献与待查：优先复核把暴露小时当失败数的反例；保留竞争风险和计数界限。 [S0016](https://doi.org/10.2307/2344614) · [S0040](https://papers.ssrn.com/sol3/Delivery.cfm/SSRN_ID3548665_code769240.pdf?abstractid=3164764&mirid=1&type=2) · [S0049](https://pmc.ncbi.nlm.nih.gov/articles/PMC4476974/)

## B09 — 同一主体但条件变化

RESEARCH · 迁移 · [B09 原始条目](../../TECHNICAL_DEBT.zh-CN.md#b09)

- 既有行为：仅处理输入计数，不知道升级日期或条件；不会自动打折旧历史。
- 目标和前提：同主体新工艺下固定时距风险。概念漂移时只重加权协变量不足以恢复条件结果机制。
- 仓库验证线索：[RC 断言地图](../../IMPLEMENTATION_VALIDATION.zh-CN.md#preview-device-history-validation)列出 `test_definitions_regime_censoring_and_identity、test_declaration_and_zero_target` 的现行行为。
- 相关研究问题：B14、D40；通过后才 B17 借用。
- 外部贡献与待查：工艺标签变化与潜在机制变化分开，做时间留出并报告可比区间。 [S0008](https://bpb-us-w2.wpmucdn.com/u.osu.edu/dist/7/36891/files/2017/07/PearlBareinboimStatSci2014ExternalValidityDoCalculus-10csxyf.pdf) · [S0009](https://jmlr.org/papers/volume8/sugiyama07a/sugiyama07a.pdf) · [S0032](https://pubmed.ncbi.nlm.nih.gov/18239110/) · [S0038](https://www.backblaze.com/blog/backblaze-drive-stats-for-2025/) · [S0051](https://www.fda.gov/media/164960/download)

## B10 — 不同主体的可比历史

RESEARCH · 迁移 · [B10 原始条目](../../TECHNICAL_DEBT.zh-CN.md#b10)

- 既有行为：可计算调用者提供的聚合计数，不判断聚合是否正当。
- 目标和前提：不同主体同条件或交换组风险。门店规模、客户组成和选择偏差会破坏完全汇聚假设。
- 仓库验证线索：[RC 断言地图](../../IMPLEMENTATION_VALIDATION.zh-CN.md#preview-device-history-validation)列出 `test_strict_and_pool_counts、test_declaration_and_zero_target` 的现行行为。
- 相关研究问题：B14→B15/B16，B18/B21。
- 外部贡献与待查：区分共享参数及组参数交换，要求留出整个主体；池化效率非准入证据。 [S0007](https://pmc.ncbi.nlm.nih.gov/articles/PMC3951812/) · [S0008](https://bpb-us-w2.wpmucdn.com/u.osu.edu/dist/7/36891/files/2017/07/PearlBareinboimStatSci2014ExternalValidityDoCalculus-10csxyf.pdf) · [S0038](https://www.backblaze.com/blog/backblaze-drive-stats-for-2025/) · [S0051](https://www.fda.gov/media/164960/download)

## B11 — 跨领域或上下文迁移

RESEARCH · 迁移、识别 · [B11 原始条目](../../TECHNICAL_DEBT.zh-CN.md#b11)

- 既有行为：不接收特征或域标签，不做 domain adaptation。
- 目标和前提：P_T(Y∣X) 与可观测的源风险。需要支持集重叠与明确 shift 假设；概念迁移无法仅靠无标签重加权保证。
- 仓库验证线索：未来测试 source-only、target-only 与适配基线；无重叠必须能弃答。
- 相关研究问题：B13、B14、B21、C26。
- 外部贡献与待查：分别测试协变量、标签、概念漂移；零支持时无一般权重修复。 [S0008](https://bpb-us-w2.wpmucdn.com/u.osu.edu/dist/7/36891/files/2017/07/PearlBareinboimStatSci2014ExternalValidityDoCalculus-10csxyf.pdf) · [S0009](https://jmlr.org/papers/volume8/sugiyama07a/sugiyama07a.pdf) · [S0011](https://proceedings.neurips.cc/paper/2019/file/8fb21ee7a2207526da55a679f0332de2-Paper.pdf) · [S0085](https://proceedings.mlr.press/v80/lipton18a/lipton18a.pdf)

## B12 — 完全不相关的历史数据

FUNDAMENTAL_LIMIT · 不可识别 · [B12 原始条目](../../TECHNICAL_DEBT.zh-CN.md#b12)

- 既有行为：不会识别不相关性，错误计数仍可能产生区间；调用者负责任务准入。
- 目标和前提：无结构联系的未知目标参数。偶然相关、数据挖掘和后见选择不能建立可迁移因果关系。
- 仓库验证线索：未来加入明显无关和语义未知反例，评估错误接受率而非只看接受数。
- 相关研究问题：A05、B14。
- 外部贡献与待查：同一来源分布与两个目标风险共存；拒绝自动选择类别。 [S0008](https://bpb-us-w2.wpmucdn.com/u.osu.edu/dist/7/36891/files/2017/07/PearlBareinboimStatSci2014ExternalValidityDoCalculus-10csxyf.pdf) · [S0010](https://www.stat.berkeley.edu/~ryantibs/papers/limits.pdf) · [S0028](https://ageconsearch.umn.edu/record/292716/files/uwmad-0066.pdf)

## B13 — 事件定义不兼容

PARTIAL · 测量 · [B13 原始条目](../../TECHNICAL_DEBT.zh-CN.md#b13)

- 既有行为：API 只有 e/c，无法存事件定义或检查兼容性。
- 目标和前提：同一端点版本、互补规则与随访时距。映射可能损失信息；未成熟观察不能当失败；定义版本不能静默覆盖。
- 仓库验证线索：[RC 断言地图](../../IMPLEMENTATION_VALIDATION.zh-CN.md#preview-device-history-validation)中 `test_definitions_regime_censoring_and_identity` 验证有限用例。现有 C 断言仍以 v1 冻结参考为准。
- 相关研究问题：E45、D38，先于所有汇聚。
- 外部贡献与待查：语义转换需标签审计；观测相同率不能证明事件等价。 [S0014](https://jhanley.biostat.mcgill.ca/bios601/SurvivalAnalysis/KaplanMeier1958.pdf) · [S0022](https://www.law.berkeley.edu/wp-content/uploads/archive/2025/09/Obermeyer-Science-Dissecting-Racial-Bias-in-Algorithm-used-to-manage-the-health-of-populations.pdf) · [S0038](https://www.backblaze.com/blog/backblaze-drive-stats-for-2025/) · [S0051](https://www.fda.gov/media/164960/download) · [S0053](https://www.itl.nist.gov/div898/handbook/apr/section1/apr131.htm) · [S0054](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/e9r1-statistical-principles-clinical-trials-addendum-estimands-and-sensitivity-analysis-clinical) · [S0066](https://github.com/CamDavidsonPilon/lifelines) · [S0084](https://doi.org/10.7326/M18-1377) · [S0089](https://www.bmj.com/content/378/bmj-2022-071349)

## B14 — 历史适用性未知

PARTIAL · 证据准入 · [B14 原始条目](../../TECHNICAL_DEBT.zh-CN.md#b14)

- 既有行为：gate 可能 VALID；无历史适用性枚举或准入器。
- 目标和前提：来源到目标准入判断及其证据不确定性。自动相似度阈值可能误接受；不可识别时必须保留 unknown。
- 仓库验证线索：[RC 断言地图](../../IMPLEMENTATION_VALIDATION.zh-CN.md#preview-device-history-validation)中 `test_declaration_and_zero_target、test_missing_context_and_path_mismatch` 验证有限用例。现有 C 断言仍以 v1 冻结参考为准。
- 相关研究问题：B13、D37、D38；是 #9 的前置。
- 外部贡献与待查：把领域声明、未验证迁移和实测区分；部分识别需最小额外界限。 [S0008](https://bpb-us-w2.wpmucdn.com/u.osu.edu/dist/7/36891/files/2017/07/PearlBareinboimStatSci2014ExternalValidityDoCalculus-10csxyf.pdf) · [S0028](https://ageconsearch.umn.edu/record/292716/files/uwmad-0066.pdf) · [S0029](https://www.kdd.org/kdd2017/papers/view/the-selective-labels-problem-evaluating-algorithmic-predictions-in-the-pres) · [S0051](https://www.fda.gov/media/164960/download)

## B15 — 稀疏主体的经验贝叶斯

RESEARCH · 计算、验证 · [B15 原始条目](../../TECHNICAL_DEBT.zh-CN.md#b15)

- 既有行为：先验固定 .5/.5，不估计群体超参数。
- 目标和前提：可交换组超参数以及稀组风险。交换性、组数不足、超参数不确定性；plug-in 区间可能过窄。
- 仓库验证线索：未来模拟覆盖、偏差、超参数退化和目标主体留出，比较 v1 基线。
- 相关研究问题：B14、B10、B19/B21。
- 外部贡献与待查：留出整个组检验 plug-in 覆盖；估计超参不确定性可能主导。 [S0030](https://pmc.ncbi.nlm.nih.gov/articles/PMC3134568/) · [S0087](https://jhanley.biostat.mcgill.ca/bios602/MultilevelData/EfronMorrisJASA1975.pdf) · [S0096](https://pmc.ncbi.nlm.nih.gov/articles/PMC4626399/) · [S0097](https://stats.stackexchange.com/questions/5727/james-stein-estimator-how-did-efron-and-morris-calculate-sigma2-in-shrinkag)

## B16 — 分层贝叶斯部分汇聚

RESEARCH · 识别、验证 · [B16 原始条目](../../TECHNICAL_DEBT.zh-CN.md#b16)

- 既有行为：没有多组输入、超先验、采样器或分层结果。
- 目标和前提：组层新单位预测与组总体分布。交换性、超先验敏感性、收敛诊断、可识别性与计算成本。
- 仓库验证线索：未来模拟校准、组间留出、后验预测与采样诊断；不能只比均值。
- 相关研究问题：B14、B15、E46、D39。
- 外部贡献与待查：检验超先验、组权重、组内风险和未见组校准；合格标签仍需定义。 [S0006](https://onlinelibrary.wiley.com/doi/full/10.1111/biom.12242) · [S0030](https://pmc.ncbi.nlm.nih.gov/articles/PMC3134568/) · [S0087](https://jhanley.biostat.mcgill.ca/bios602/MultilevelData/EfronMorrisJASA1975.pdf) · [S0094](https://github.com/stan-dev/math) · [S0097](https://stats.stackexchange.com/questions/5727/james-stein-estimator-how-did-efron-and-morris-calculate-sigma2-in-shrinkag)

## B17 — 历史与目标冲突的稳健借用

RESEARCH · 迁移、验证 · [B17 原始条目](../../TECHNICAL_DEBT.zh-CN.md#b17)

- 既有行为：固定 Jeffreys，不接收外部历史先验或动态折扣。
- 目标和前提：目标风险与先验混合权更新。折扣不可事后迎合结论；混合先验仍依赖可迁移前提。
- 仓库验证线索：未来系统扫描冲突强度、覆盖、误判率与敏感性，比较零借用。
- 相关研究问题：先 B14/#10，后 #9；B16、D40。
- 外部贡献与待查：比较冲突强度和目标样本数；零目标时宽混合项不能学到冲突。 [S0006](https://onlinelibrary.wiley.com/doi/full/10.1111/biom.12242) · [S0007](https://pmc.ncbi.nlm.nih.gov/articles/PMC3951812/) · [S0030](https://pmc.ncbi.nlm.nih.gov/articles/PMC3134568/) · [S0031](https://onlinelibrary.wiley.com/doi/10.1002/sim.9124) · [S0051](https://www.fda.gov/media/164960/download) · [S0096](https://pmc.ncbi.nlm.nih.gov/articles/PMC4626399/)

## B18 — 群体汇总与辛普森悖论

PARTIAL · 迁移、测量 · [B18 原始条目](../../TECHNICAL_DEBT.zh-CN.md#b18)

- 既有行为：只看聚合 e/c，不识别分层或混杂。
- 目标和前提：指定目标混合权下层风险加权。层间稀疏、未测混杂、权重选择和无支持层会使调整不可靠。
- 仓库验证线索：[RC 断言地图](../../IMPLEMENTATION_VALIDATION.zh-CN.md#preview-device-history-validation)中 `test_known_heterogeneous_and_population_change、test_phase_two_mix_shift` 验证有限用例。现有 C 断言仍以 v1 冻结参考为准。
- 相关研究问题：B13、B21、C25。
- 外部贡献与待查：按因果/描述目标决定分层；弱支持层的权重不宜自动归给其他层。 [S0024](https://doi.org/10.1111/j.2517-6161.1951.tb00088.x) · [S0072](https://proceedings.mlr.press/v286/bhadane25a.html)

## B19 — 相关观察与重复用户

PARTIAL · 验证、计算 · [B19 原始条目](../../TECHNICAL_DEBT.zh-CN.md#b19)

- 既有行为：接受计数，不接收 cluster ID 或估计相关结构。
- 目标和前提：聚类设计下 p 或群体平均风险。有效样本量不是随意缩放常数，相关结构和观察选择必须明确。
- 仓库验证线索：[RC 断言地图](../../IMPLEMENTATION_VALIDATION.zh-CN.md#preview-device-history-validation)中 `test_unmodelled_dependence_preserves_records` 验证有限用例。现有 C 断言仍以 v1 冻结参考为准。
- 相关研究问题：B20、B16、E45。
- 外部贡献与待查：估计簇数、大小、相关及跨簇冲击；同实体不同键也会相关。 [S0038](https://www.backblaze.com/blog/backblaze-drive-stats-for-2025/) · [S0039](https://aws.amazon.com/message/41926/) · [S0044](https://itl.nist.gov/div898/handbook/pmc/section6/pmc611.htm) · [S0052](https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc332.htm) · [S0057](https://sre.google/workbook/error-budget-policy/) · [S0075](https://github.com/scikit-learn/scikit-learn/issues/19072) · [S0077](https://www.thousandeyes.com/blog/aws-s3-outage-likely-caused-by-internal-network-issue) · [S0078](https://github.com/scikit-learn/scikit-learn/issues/32076)

## B20 — 重复证据与重叠查询

PARTIAL · 证据准入 · [B20 原始条目](../../TECHNICAL_DEBT.zh-CN.md#b20)

- 既有行为：仅存 e/c，不去重或检测查询重叠。
- 目标和前提：独立事实贡献与逻辑事件身份。隐私匿名化、键重用与迟到更新可能破坏去重；不能仅减一个估算 overlap。
- 仓库验证线索：[RC 断言地图](../../IMPLEMENTATION_VALIDATION.zh-CN.md#preview-device-history-validation)中 `test_duplicates_and_conflicts、test_cutoff_excludes_later_outcome_even_on_same_identity` 验证有限用例。现有 C 断言仍以 v1 冻结参考为准。
- 相关研究问题：E45、D38、B13。
- 外部贡献与待查：查询重叠和修订冲突须溯源；先研究版本优先与拆并事件身份。 [S0027](https://doi.org/10.1145/2382577.2382579) · [S0039](https://aws.amazon.com/message/41926/) · [S0074](https://github.com/scikit-learn-contrib/MAPIE/issues/799) · [S0075](https://github.com/scikit-learn/scikit-learn/issues/19072) · [S0078](https://github.com/scikit-learn/scikit-learn/issues/32076) · [S0082](https://pmc.ncbi.nlm.nih.gov/articles/PMC10499856/) · [S0088](https://www.w3.org/TR/2013/REC-prov-o-20130430/)

## B21 — 抽样偏差与目标总体变化

PARTIAL · 迁移、识别 · [B21 原始条目](../../TECHNICAL_DEBT.zh-CN.md#b21)

- 既有行为：不接收抽样权重、纳入概率或目标总体结构。
- 目标和前提：目标总体下经正确标准化的风险。权重需要可识别纳入机制和 overlap，未观察混杂不可凭数据量消除。
- 仓库验证线索：[RC 断言地图](../../IMPLEMENTATION_VALIDATION.zh-CN.md#preview-device-history-validation)中 `test_target_weights_and_support、test_phase_two_mix_shift` 验证有限用例。现有 C 断言仍以 v1 冻结参考为准。
- 相关研究问题：B14、B18、B11。
- 外部贡献与待查：选择概率、正性、权不确定性须另外验证；有选择性标签时做敏感性。 [S0008](https://bpb-us-w2.wpmucdn.com/u.osu.edu/dist/7/36891/files/2017/07/PearlBareinboimStatSci2014ExternalValidityDoCalculus-10csxyf.pdf) · [S0009](https://jmlr.org/papers/volume8/sugiyama07a/sugiyama07a.pdf) · [S0011](https://proceedings.neurips.cc/paper/2019/file/8fb21ee7a2207526da55a679f0332de2-Paper.pdf) · [S0022](https://www.law.berkeley.edu/wp-content/uploads/archive/2025/09/Obermeyer-Science-Dissecting-Racial-Bias-in-Algorithm-used-to-manage-the-health-of-populations.pdf) · [S0024](https://doi.org/10.1111/j.2517-6161.1951.tb00088.x) · [S0028](https://ageconsearch.umn.edu/record/292716/files/uwmad-0066.pdf) · [S0029](https://www.kdd.org/kdd2017/papers/view/the-selective-labels-problem-evaluating-algorithmic-predictions-in-the-pres) · [S0040](https://papers.ssrn.com/sol3/Delivery.cfm/SSRN_ID3548665_code769240.pdf?abstractid=3164764&mirid=1&type=2) · [S0051](https://www.fda.gov/media/164960/download) · [S0072](https://proceedings.mlr.press/v286/bhadane25a.html) · [S0084](https://doi.org/10.7326/M18-1377) · [S0085](https://proceedings.mlr.press/v80/lipton18a/lipton18a.pdf)

## C22 — 无历史的结构化专家判断

RESEARCH · 测量、验证 · [C22 原始条目](../../TECHNICAL_DEBT.zh-CN.md#c22)

- 既有行为：只接受一个 raw 百分数并套冻结半宽，没有专家访谈或共识模型。
- 目标和前提：专家给定信息集的预测分布。过度自信、从众、共同信息和区间形状选择会影响结论。
- 仓库验证线索：未来检查输入可理解性、独立判断保留、任务组表现与敏感性。
- 相关研究问题：A03、A05、D38、D36。
- 外部贡献与待查：比较等权和种子表现权，留出题检验可迁移性；共同材料不独立。 [S0019](https://faculty.wharton.upenn.edu/wp-content/uploads/2015/07/2014---psychological-strategies-for-winning-a-tournament.pdf) · [S0020](https://academic.oup.com/reep/article/12/1/113/4835830) · [S0021](https://cooke-aspinall.net/Cross%20Validation%20SEJ%20RESS.pdf) · [S0055](https://aanzfta.asean.org/AECSP/ASEAN-SPS-Guide/files/media/2020/09/EFSA_Guidance-on-expert-knowledge-elicitation-in-food-and-feed-safety-risk-assessment.pdf) · [S0058](https://www.ipcc.ch/site/assets/uploads/2017/08/AR5_Uncertainty_Guidance_Note.pdf)

## C23 — 参考群体先验与新主体更新

RESEARCH · 迁移 · [C23 原始条目](../../TECHNICAL_DEBT.zh-CN.md#c23)

- 既有行为：0/0 无历史，先验固定 .5/.5；不能注入自定义 alpha/beta。
- 目标和前提：新组的先验预测及少量组数据后验。重复利用目标数据估先验会双重计证，群体差异造成负迁移。
- 仓库验证线索：未来零目标样本、顺序更新等价性、先验敏感性和冲突场景测试。
- 相关研究问题：B14、B15/B16、B20、B17。
- 外部贡献与待查：留出新主体并保留参考群体不匹配的拒绝方案。 [S0006](https://onlinelibrary.wiley.com/doi/full/10.1111/biom.12242) · [S0030](https://pmc.ncbi.nlm.nih.gov/articles/PMC3134568/) · [S0087](https://jhanley.biostat.mcgill.ca/bios602/MultilevelData/EfronMorrisJASA1975.pdf) · [S0097](https://stats.stackexchange.com/questions/5727/james-stein-estimator-how-did-efron-and-morris-calculate-sigma2-in-shrinkag)

## C24 — 收到新证据后的贝叶斯更新

RESEARCH · 证据准入、计算 · [C24 原始条目](../../TECHNICAL_DEBT.zh-CN.md#c24)

- 既有行为：可用累计新增完成事件更新历史计数；不接受任意证据似然或 Bayes factor。
- 目标和前提：同一目标在增量证据下的 posterior。条件独立误设、重复证据、似然来源和零概率会主导结果。
- 仓库验证线索：未来已知解析案例、顺序一致性、相关证据和重复更新拒绝测试。
- 相关研究问题：D38、B20、C30、E46。
- 外部贡献与待查：预测时点冻结且独立新似然只使用一次；复用旧信息会双计。 [S0006](https://onlinelibrary.wiley.com/doi/full/10.1111/biom.12242) · [S0012](https://kylewoodward.com/blog-data/pdfs/references/dawid-journal-of-the-american-statistical-association-1982A.pdf) · [S0030](https://pmc.ncbi.nlm.nih.gov/articles/PMC3134568/) · [S0031](https://onlinelibrary.wiley.com/doi/10.1002/sim.9124) · [S0049](https://pmc.ncbi.nlm.nih.gov/articles/PMC4476974/) · [S0096](https://pmc.ncbi.nlm.nih.gov/articles/PMC4626399/)

## C25 — 基于特征的事件预测

PROPOSED · 验证 · [C25 原始条目](../../TECHNICAL_DEBT.zh-CN.md#c25)

- 既有行为：不接收特征，不训练/运行回归或树模型。
- 目标和前提：有 x 条件下的固定期概率。数据泄漏、混杂、外推和训练群体不代表目标群体。
- 仓库验证线索：未来事件/时间分组留出、基准比较、校准、特征可用时点与外推拒绝。
- 相关研究问题：A08、B14、C26、E46。
- 外部贡献与待查：按未来/实体留出并检查外部校准、代理标签和完全分离。 [S0016](https://doi.org/10.2307/2344614) · [S0017](https://people.eecs.berkeley.edu/~jordan/courses/281B-spring04/readings/ferguson.pdf) · [S0022](https://www.law.berkeley.edu/wp-content/uploads/archive/2025/09/Obermeyer-Science-Dissecting-Racial-Bias-in-Algorithm-used-to-manage-the-health-of-populations.pdf) · [S0023](https://pmc.ncbi.nlm.nih.gov/articles/PMC8218233/) · [S0040](https://papers.ssrn.com/sol3/Delivery.cfm/SSRN_ID3548665_code769240.pdf?abstractid=3164764&mirid=1&type=2) · [S0046](https://web.stanford.edu/~lutian/coursepdf/cox1972paper.pdf) · [S0078](https://github.com/scikit-learn/scikit-learn/issues/32076) · [S0082](https://pmc.ncbi.nlm.nih.gov/articles/PMC10499856/) · [S0084](https://doi.org/10.7326/M18-1377)

## C26 — 外部预测概率校准

RESEARCH · 验证 · [C26 原始条目](../../TECHNICAL_DEBT.zh-CN.md#c26)

- 既有行为：无 calibrator 或训练数据接口，主观半宽不修复分类器校准。
- 目标和前提：外部模型分数条件下的真实发生频率。小样本、训练校准泄漏和部署漂移；总 Brier 改善不等于所有子群校准。
- 仓库验证线索：未来分组/时间留出、校准误差区间、未校准基线与失效场景。
- 相关研究问题：D35、D36、D40、E47。
- 外部贡献与待查：比较 sigmoid/isotonic 与原输出；分离训练、校准、测试。 [S0004](https://sites.stat.washington.edu/raftery/Research/PDF/Gneiting2007jrssb.pdf) · [S0005](https://sites.stat.washington.edu/raftery/Research/PDF/Gneiting2007jasa.pdf) · [S0023](https://pmc.ncbi.nlm.nih.gov/articles/PMC8218233/) · [S0042](https://people.duke.edu/~clemen/bio/Published%20Papers/45.PredictionMarkets-Page%26Clemen-EJ-2013.pdf) · [S0064](https://github.com/scikit-learn/scikit-learn) · [S0085](https://proceedings.mlr.press/v80/lipton18a/lipton18a.pdf) · [S0086](https://www.sciencedirect.com/science/article/pii/S0169207014000533)

## C27 — 由预测分布计算阈值事件概率

RESEARCH · 计算、测量 · [C27 原始条目](../../TECHNICAL_DEBT.zh-CN.md#c27)

- 既有行为：不接收连续分布、预测样本或阈值查询。
- 目标和前提：一次新结果超过阈值的预测质量。模拟成员相关、模型偏差、离散阈值包含关系和尾部稀疏。
- 仓库验证线索：未来解析分布基准、阈值单调性、时间/空间一致的留出检验。
- 相关研究问题：C31、C28、D36、D39。
- 外部贡献与待查：说明严格/含等号与点质量；分位数稀疏会限制尾分辨率。 [S0011](https://proceedings.neurips.cc/paper/2019/file/8fb21ee7a2207526da55a679f0332de2-Paper.pdf) · [S0033](https://www.ecmwf.int/sites/default/files/elibrary/2017/18198-25-years-ensemble-forecasting-ecmwf.pdf) · [S0043](https://html.rhhz.net/yyqxxb/html/20020103.htm) · [S0056](https://www.cma.gov.cn/zfxxgk/gknr/flfgbz/bz/202209/P020220921682224502673.pdf) · [S0080](https://confluence.ecmwf.int/spaces/WLS/pages/394992254/Verification)

## C28 — 模拟情景与真实观察历史

OPEN · 证据准入 · [C28 原始条目](../../TECHNICAL_DEBT.zh-CN.md#c28)

- 既有行为：计数 API 无来源标签，不能阻止把模拟计数伪装为真实样本。
- 目标和前提：模拟 DGP 的目标与实际总体风险。相关随机样本、失配模型和未校准分布可能使模拟区间极窄但错误。
- 仓库验证线索：未来验证模拟/真实来源不可静默合并，并独立评估 Monte Carlo 与预测误差。
- 相关研究问题：D38、D39、C27、E45。
- 外部贡献与待查：在源登记区分合成路径和现实观测；有效集合大小不能代替现实 n。 [S0033](https://www.ecmwf.int/sites/default/files/elibrary/2017/18198-25-years-ensemble-forecasting-ecmwf.pdf) · [S0043](https://html.rhhz.net/yyqxxb/html/20020103.htm) · [S0070](https://github.com/cdcepi/FluSight-forecast-hub)

## C29 — 合并多个预测来源

OUT_OF_SCOPE · 验证、决策语义 · [C29 原始条目](../../TECHNICAL_DEBT.zh-CN.md#c29)

- 既有行为：明确保留主观/历史独立输出，只分类关系，不概率融合。
- 目标和前提：同一目标的组合分布。重复信息、负迁移、训练泄漏和模型不确定性；融合可比单源更差。
- 仓库验证线索：现有 relation 回归保持无融合；未来需独立组合基线、校准和依赖反例。
- 相关研究问题：B20、C26、D38、D43。
- 外部贡献与待查：必须观察来源共因果/共数据；等权与最强单项是基线。 [S0018](https://academic.oup.com/jrsssb/article/72/1/71/7076442) · [S0021](https://cooke-aspinall.net/Cross%20Validation%20SEJ%20RESS.pdf) · [S0034](https://www.nature.com/articles/s41467-024-50601-9) · [S0035](https://pubmed.ncbi.nlm.nih.gov/35394862/) · [S0081](https://www.cdc.gov/flu-forecasting/evaluation/2024-2025-report.html)

## C30 — 相关事件的联合与条件概率

PROPOSED · 识别 · [C30 原始条目](../../TECHNICAL_DEBT.zh-CN.md#c30)

- 既有行为：只处理一个事件及其互斥补事件，不计算两个任意事件的联合。
- 目标和前提：联合和条件事件概率。不识别依赖时只能给界或假设敏感性，不能默认独立。
- 仓库验证线索：未来 Fréchet 界、完全相关/互斥/独立解析案例与条件分母零处理。
- 相关研究问题：A08、B19、D38、E46。
- 外部贡献与待查：只给边际时用 Fréchet 界，只有联合记录或额外结构可收紧。 [S0015](https://doi.org/10.1080/01621459.1999.10474144) · [S0039](https://aws.amazon.com/message/41926/) · [S0077](https://www.thousandeyes.com/blog/aws-s3-outage-likely-caused-by-internal-network-issue)

## C31 — 连续变量预测与不确定性

PROPOSED · 计算、验证 · [C31 原始条目](../../TECHNICAL_DEBT.zh-CN.md#c31)

- 既有行为：没有连续分布拟合、预测区间或回归 API。
- 目标和前提：连续新观测的分布与时距。预测区间、参数区间和 conformal coverage 含义不同；交换性失效影响保证。
- 仓库验证线索：未来单位/变换、异方差、覆盖与区间宽度、时间漂移验证。
- 相关研究问题：A08、C27、D39、E46。
- 外部贡献与待查：比较预测/参数区间，报告边际覆盖及尾损失。 [S0004](https://sites.stat.washington.edu/raftery/Research/PDF/Gneiting2007jrssb.pdf) · [S0005](https://sites.stat.washington.edu/raftery/Research/PDF/Gneiting2007jasa.pdf) · [S0011](https://proceedings.neurips.cc/paper/2019/file/8fb21ee7a2207526da55a679f0332de2-Paper.pdf) · [S0013](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1008618) · [S0017](https://people.eecs.berkeley.edu/~jordan/courses/281B-spring04/readings/ferguson.pdf) · [S0036](https://agupubs.onlinelibrary.wiley.com/doi/10.1029/2025GL119088) · [S0037](https://doi.org/10.1016/j.ijforecast.2016.02.001) · [S0044](https://itl.nist.gov/div898/handbook/pmc/section6/pmc611.htm) · [S0067](https://github.com/tidyverts/fabletools) · [S0090](https://hess.copernicus.org/articles/27/1809/2023/index.html)

## C32 — 事件次数和失效率模型

PROPOSED · 测量、计算 · [C32 原始条目](../../TECHNICAL_DEBT.zh-CN.md#c32)

- 既有行为：history_estimate 接受二元事件计数，没有 exposure 或强度参数。
- 目标和前提：暴露率或未来计数分布。独立增量、平稳强度、过度离散与零膨胀可能影响建模。
- 仓库验证线索：未来 exposure 缩放、零暴露、模拟恢复、过度离散与预测检查。
- 相关研究问题：A08、C34、D39、E46。
- 外部贡献与待查：分离零暴露和零事件；检查过离散与过程依赖。 [S0016](https://doi.org/10.2307/2344614) · [S0038](https://www.backblaze.com/blog/backblaze-drive-stats-for-2025/) · [S0040](https://papers.ssrn.com/sol3/Delivery.cfm/SSRN_ID3548665_code769240.pdf?abstractid=3164764&mirid=1&type=2) · [S0041](https://erm.ncsu.edu/az/erm/i/chan/library/pelletier-research-partners-2009.pdf)

## C33 — 到事件时间与生存预测

PROPOSED · 测量、识别 · [C33 原始条目](../../TECHNICAL_DEBT.zh-CN.md#c33)

- 既有行为：不接收时长、删失或风险集，不能做 survival analysis。
- 目标和前提：固定期生存或特定事件累积发生。信息性删失、竞争风险和非比例风险不能自动忽略。
- 仓库验证线索：未来删失解析案例、风险集构造、时间单调性、竞争风险和预测校准。
- 相关研究问题：B13、A08、D39、E46。
- 外部贡献与待查：审核删失、延迟入组、竞争过程；短随访与未失败不可混列。 [S0014](https://jhanley.biostat.mcgill.ca/bios601/SurvivalAnalysis/KaplanMeier1958.pdf) · [S0015](https://doi.org/10.1080/01621459.1999.10474144) · [S0038](https://www.backblaze.com/blog/backblaze-drive-stats-for-2025/) · [S0046](https://web.stanford.edu/~lutian/coursepdf/cox1972paper.pdf) · [S0053](https://www.itl.nist.gov/div898/handbook/apr/section1/apr131.htm) · [S0054](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/e9r1-statistical-principles-clinical-trials-addendum-estimands-and-sensitivity-analysis-clinical) · [S0066](https://github.com/CamDavidsonPilon/lifelines) · [S0089](https://www.bmj.com/content/378/bmj-2022-071349)

## C34 — 时间趋势、季节性与动态模型

PROPOSED · 验证、迁移 · [C34 原始条目](../../TECHNICAL_DEBT.zh-CN.md#c34)

- 既有行为：没有日期、滚动窗、时间权重或动态参数。
- 目标和前提：随时间和季节变化的目标概率。时间泄漏、季节样本稀疏、变化点和人为窗口选择。
- 仓库验证线索：未来 rolling-origin、季节留出、延迟标签与 regime 切换测试。
- 相关研究问题：D40、B09、C25、E47。
- 外部贡献与待查：滚动起点留出与季节朴素基线，考察报告延迟和突变。 [S0032](https://pubmed.ncbi.nlm.nih.gov/18239110/) · [S0033](https://www.ecmwf.int/sites/default/files/elibrary/2017/18198-25-years-ensemble-forecasting-ecmwf.pdf) · [S0034](https://www.nature.com/articles/s41467-024-50601-9) · [S0035](https://pubmed.ncbi.nlm.nih.gov/35394862/) · [S0036](https://agupubs.onlinelibrary.wiley.com/doi/10.1029/2025GL119088) · [S0037](https://doi.org/10.1016/j.ijforecast.2016.02.001) · [S0041](https://erm.ncsu.edu/az/erm/i/chan/library/pelletier-research-partners-2009.pdf) · [S0047](https://doi.org/10.1016/j.ijforecast.2019.04.014) · [S0059](https://www.bis.org/publ/bcbs22.htm) · [S0060](https://otexts.com/fpp3/tscv.html) · [S0067](https://github.com/tidyverts/fabletools) · [S0070](https://github.com/cdcepi/FluSight-forecast-hub) · [S0074](https://github.com/scikit-learn-contrib/MAPIE/issues/799) · [S0079](https://github.com/scikit-learn/scikit-learn/issues/22523) · [S0080](https://confluence.ecmwf.int/spaces/WLS/pages/394992254/Verification) · [S0081](https://www.cdc.gov/flu-forecasting/evaluation/2024-2025-report.html) · [S0090](https://hess.copernicus.org/articles/27/1809/2023/index.html) · [S0095](https://github.com/robjhyndman/forecast)

## D35 — Brier Score 与 Log Loss 等预测评分

DEFERRED · 验证 · [D35 原始条目](../../TECHNICAL_DEBT.zh-CN.md#d35)

- 既有行为：无评分、日志或概率质量统计；provenance 不保存预测结果。
- 目标和前提：相同目标、时距与真值下期望分数。样本选择、相关事件、目标难度和 endpoint 无穷损失；分数包含多种性能成分。
- 仓库验证线索：未来解析端点、极值、组权重、缺失结果及事件/时间分割验证。
- 相关研究问题：A04、D36、D38。
- 外部贡献与待查：按事件聚类比较评分差，报告覆盖与分辨率，不由一个数字推出全部。 [S0005](https://sites.stat.washington.edu/raftery/Research/PDF/Gneiting2007jasa.pdf) · [S0013](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1008618) · [S0019](https://faculty.wharton.upenn.edu/wp-content/uploads/2015/07/2014---psychological-strategies-for-winning-a-tournament.pdf) · [S0033](https://www.ecmwf.int/sites/default/files/elibrary/2017/18198-25-years-ensemble-forecasting-ecmwf.pdf) · [S0034](https://www.nature.com/articles/s41467-024-50601-9) · [S0035](https://pubmed.ncbi.nlm.nih.gov/35394862/) · [S0036](https://agupubs.onlinelibrary.wiley.com/doi/10.1029/2025GL119088) · [S0037](https://doi.org/10.1016/j.ijforecast.2016.02.001) · [S0041](https://erm.ncsu.edu/az/erm/i/chan/library/pelletier-research-partners-2009.pdf) · [S0043](https://html.rhhz.net/yyqxxb/html/20020103.htm) · [S0045](https://journals.ametsoc.org/view/journals/mwre/78/1/1520-0493_1950_078_0001_vofeit_2_0_co_2.xml) · [S0047](https://doi.org/10.1016/j.ijforecast.2019.04.014) · [S0056](https://www.cma.gov.cn/zfxxgk/gknr/flfgbz/bz/202209/P020220921682224502673.pdf) · [S0059](https://www.bis.org/publ/bcbs22.htm) · [S0060](https://otexts.com/fpp3/tscv.html) · [S0067](https://github.com/tidyverts/fabletools) · [S0070](https://github.com/cdcepi/FluSight-forecast-hub) · [S0074](https://github.com/scikit-learn-contrib/MAPIE/issues/799) · [S0075](https://github.com/scikit-learn/scikit-learn/issues/19072) · [S0078](https://github.com/scikit-learn/scikit-learn/issues/32076) · [S0079](https://github.com/scikit-learn/scikit-learn/issues/22523) · [S0080](https://confluence.ecmwf.int/spaces/WLS/pages/394992254/Verification) · [S0081](https://www.cdc.gov/flu-forecasting/evaluation/2024-2025-report.html) · [S0082](https://pmc.ncbi.nlm.nih.gov/articles/PMC10499856/) · [S0090](https://hess.copernicus.org/articles/27/1809/2023/index.html) · [S0091](https://arxiv.org/pdf/2110.00115) · [S0095](https://github.com/robjhyndman/forecast)

## D36 — 不同预测任务间的校准

RESEARCH · 验证、迁移 · [D36 原始条目](../../TECHNICAL_DEBT.zh-CN.md#d36)

- 既有行为：没有跨任务校准，也不依据历史成绩改变主观半宽。
- 目标和前提：任务/子群条件校准。任务定义后见选择、稀疏组、选择性上报和域漂移。
- 仓库验证线索：未来留出整个任务族与时间段，测试无关任务拒绝及区间稳定性。
- 相关研究问题：A04、D35、B11、D40。
- 外部贡献与待查：总体表现可掩盖特定组，需独立任务样本并保留评价不确定性。 [S0004](https://sites.stat.washington.edu/raftery/Research/PDF/Gneiting2007jrssb.pdf) · [S0005](https://sites.stat.washington.edu/raftery/Research/PDF/Gneiting2007jasa.pdf) · [S0010](https://www.stat.berkeley.edu/~ryantibs/papers/limits.pdf) · [S0012](https://kylewoodward.com/blog-data/pdfs/references/dawid-journal-of-the-american-statistical-association-1982A.pdf) · [S0019](https://faculty.wharton.upenn.edu/wp-content/uploads/2015/07/2014---psychological-strategies-for-winning-a-tournament.pdf) · [S0021](https://cooke-aspinall.net/Cross%20Validation%20SEJ%20RESS.pdf) · [S0022](https://www.law.berkeley.edu/wp-content/uploads/archive/2025/09/Obermeyer-Science-Dissecting-Racial-Bias-in-Algorithm-used-to-manage-the-health-of-populations.pdf) · [S0023](https://pmc.ncbi.nlm.nih.gov/articles/PMC8218233/) · [S0029](https://www.kdd.org/kdd2017/papers/view/the-selective-labels-problem-evaluating-algorithmic-predictions-in-the-pres) · [S0042](https://people.duke.edu/~clemen/bio/Published%20Papers/45.PredictionMarkets-Page%26Clemen-EJ-2013.pdf) · [S0064](https://github.com/scikit-learn/scikit-learn) · [S0084](https://doi.org/10.7326/M18-1377) · [S0086](https://www.sciencedirect.com/science/article/pii/S0169207014000533) · [S0091](https://arxiv.org/pdf/2110.00115)

## D37 — 统计就绪与历史真实适用性

PARTIAL · 证据准入、决策语义 · [D37 原始条目](../../TECHNICAL_DEBT.zh-CN.md#d37)

- 既有行为：statistically_ready 与 state 仅由冻结 gate 算出，没有 applicability 字段。
- 目标和前提：计数 readiness 与来源适用性。大样本错误迁移尤其危险，未知不能由精度替代。
- 仓库验证线索：[RC 断言地图](../../IMPLEMENTATION_VALIDATION.zh-CN.md#preview-device-history-validation)中 `test_installed_v1_values_and_states、test_declaration_and_zero_target` 验证有限用例。现有 C 断言仍以 v1 冻结参考为准。
- 相关研究问题：B14、B13、D38。
- 外部贡献与待查：宽度不能代替语义、抽样审核，分别报告数值失败与无证据。 [S0007](https://pmc.ncbi.nlm.nih.gov/articles/PMC3951812/) · [S0008](https://bpb-us-w2.wpmucdn.com/u.osu.edu/dist/7/36891/files/2017/07/PearlBareinboimStatSci2014ExternalValidityDoCalculus-10csxyf.pdf) · [S0051](https://www.fda.gov/media/164960/download) · [S0054](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/e9r1-statistical-principles-clinical-trials-addendum-estimands-and-sensitivity-analysis-clinical) · [S0084](https://doi.org/10.7326/M18-1377)

## D38 — 概率来源与 provenance 表示

PARTIAL · 证据准入 · [D38 原始条目](../../TECHNICAL_DEBT.zh-CN.md#d38)

- 既有行为：provenance 仅记录实际暴露与后续修订；结果保留独立模型版本。
- 目标和前提：因果时间与证据来源追踪。隐私、重复证据、来源真实性、schema 兼容与历史重放。
- 仓库验证线索：[RC 断言地图](../../IMPLEMENTATION_VALIDATION.zh-CN.md#preview-device-history-validation)中 `test_strict_and_pool_counts、test_declaration_and_zero_target、test_cutoff_excludes_later_outcome_even_on_same_identity` 验证有限用例。现有 C 断言仍以 v1 冻结参考为准。
- 相关研究问题：B20、E47、C28、A04。
- 外部贡献与待查：需可观察的发布时间、版本、实际曝光事实；不能由哈希识别意图。 [S0027](https://doi.org/10.1145/2382577.2382579) · [S0055](https://aanzfta.asean.org/AECSP/ASEAN-SPS-Guide/files/media/2020/09/EFSA_Guidance-on-expert-knowledge-elicitation-in-food-and-feed-safety-risk-assessment.pdf) · [S0070](https://github.com/cdcepi/FluSight-forecast-hub) · [S0088](https://www.w3.org/TR/2013/REC-prov-o-20130430/)

## D39 — 模型特定的不确定性区间

PARTIAL · 计算、验证 · [D39 原始条目](../../TECHNICAL_DEBT.zh-CN.md#d39)

- 既有行为：有主观模型区间和历史 95% posterior interval，二者不互换。
- 目标和前提：模型参数、未见结果及规则区间的不同对象。可信水平不等于频率覆盖，conformal 边际覆盖不等于逐条件后验。
- 仓库验证线索：[RC 断言地图](../../IMPLEMENTATION_VALIDATION.zh-CN.md#preview-device-history-validation)中 `test_known_heterogeneous_and_population_change、test_boundary_and_budget_failure、test_numerical_faults_do_not_expose_estimates` 验证有限用例。现有 C 断言仍以 v1 冻结参考为准。
- 相关研究问题：A08、C31/C33、E46。
- 外部贡献与待查：边际 conformal 不给逐点覆盖；模型专属数值误差另计。 [S0001](https://projecteuclid.org/journals/statistical-science/volume-16/issue-2/Interval-Estimation-for-a-Binomial-Proportion/10.1214/ss/1009213286.full) · [S0002](https://www.jhanley.biostat.mcgill.ca/c607/ch08/wilson_jasa_1927.pdf) · [S0004](https://sites.stat.washington.edu/raftery/Research/PDF/Gneiting2007jrssb.pdf) · [S0010](https://www.stat.berkeley.edu/~ryantibs/papers/limits.pdf) · [S0011](https://proceedings.neurips.cc/paper/2019/file/8fb21ee7a2207526da55a679f0332de2-Paper.pdf) · [S0013](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1008618) · [S0049](https://pmc.ncbi.nlm.nih.gov/articles/PMC4476974/) · [S0054](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/e9r1-statistical-principles-clinical-trials-addendum-estimands-and-sensitivity-analysis-clinical) · [S0058](https://www.ipcc.ch/site/assets/uploads/2017/08/AR5_Uncertainty_Guidance_Note.pdf) · [S0063](https://github.com/wch/r-source) · [S0065](https://github.com/statsmodels/statsmodels) · [S0089](https://www.bmj.com/content/378/bmj-2022-071349)

## D40 — 历史漂移与机制变化

RESEARCH · 迁移、验证 · [D40 原始条目](../../TECHNICAL_DEBT.zh-CN.md#d40)

- 既有行为：无时间索引、漂移检测或自动遗忘。
- 目标和前提：漂移后时变目标风险。检测误报、延迟标签、季节性与多重检验；检测到变化不说明原因或正确替代模型。
- 仓库验证线索：[RC 断言地图](../../IMPLEMENTATION_VALIDATION.zh-CN.md#preview-device-history-validation)列出 `test_definitions_regime_censoring_and_identity、test_cutoff_excludes_later_outcome_even_on_same_identity` 的现行行为。
- 相关研究问题：B09、C34、B14、E47。
- 外部贡献与待查：回测只用当时信息，区别能检测的边际变化和缺标签机制变化。 [S0009](https://jmlr.org/papers/volume8/sugiyama07a/sugiyama07a.pdf) · [S0023](https://pmc.ncbi.nlm.nih.gov/articles/PMC8218233/) · [S0032](https://pubmed.ncbi.nlm.nih.gov/18239110/) · [S0033](https://www.ecmwf.int/sites/default/files/elibrary/2017/18198-25-years-ensemble-forecasting-ecmwf.pdf) · [S0034](https://www.nature.com/articles/s41467-024-50601-9) · [S0035](https://pubmed.ncbi.nlm.nih.gov/35394862/) · [S0036](https://agupubs.onlinelibrary.wiley.com/doi/10.1029/2025GL119088) · [S0039](https://aws.amazon.com/message/41926/) · [S0044](https://itl.nist.gov/div898/handbook/pmc/section6/pmc611.htm) · [S0052](https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc332.htm) · [S0057](https://sre.google/workbook/error-budget-policy/) · [S0060](https://otexts.com/fpp3/tscv.html) · [S0064](https://github.com/scikit-learn/scikit-learn) · [S0074](https://github.com/scikit-learn-contrib/MAPIE/issues/799) · [S0077](https://www.thousandeyes.com/blog/aws-s3-outage-likely-caused-by-internal-network-issue) · [S0079](https://github.com/scikit-learn/scikit-learn/issues/22523) · [S0081](https://www.cdc.gov/flu-forecasting/evaluation/2024-2025-report.html) · [S0085](https://proceedings.mlr.press/v80/lipton18a/lipton18a.pdf) · [S0090](https://hess.copernicus.org/articles/27/1809/2023/index.html) · [S0091](https://arxiv.org/pdf/2110.00115)

## D41 — 罕见或零观察事件概率

PARTIAL · 识别、计算 · [D41 原始条目](../../TECHNICAL_DEBT.zh-CN.md#d41)

- 既有行为：e=0,c>0 有 Beta(.5,c+.5) 后验与非零均值/区间；0/0 仍无估计。
- 目标和前提：观察窗口内罕见风险及其上界。模型失配、漏报、相关性和浮点尾部抵消可能比抽样误差更大。
- 仓库验证线索：large_numerics 偏斜与 INT64_MAX；未来极小尾概率相对精度、漏报和稀有事件场景。
- 相关研究问题：B21、C32、E48。
- 外部贡献与待查：单侧零事件上界、Jeffreys 后验和极端数值各自核验。 [S0001](https://projecteuclid.org/journals/statistical-science/volume-16/issue-2/Interval-Estimation-for-a-Binomial-Proportion/10.1214/ss/1009213286.full) · [S0002](https://www.jhanley.biostat.mcgill.ca/c607/ch08/wilson_jasa_1927.pdf) · [S0003](https://jhanley.biostat.mcgill.ca/Reprints/If_Nothing_Goes_1983.pdf) · [S0014](https://jhanley.biostat.mcgill.ca/bios601/SurvivalAnalysis/KaplanMeier1958.pdf) · [S0032](https://pubmed.ncbi.nlm.nih.gov/18239110/) · [S0038](https://www.backblaze.com/blog/backblaze-drive-stats-for-2025/) · [S0041](https://erm.ncsu.edu/az/erm/i/chan/library/pelletier-research-partners-2009.pdf) · [S0052](https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc332.htm) · [S0053](https://www.itl.nist.gov/div898/handbook/apr/section1/apr131.htm) · [S0059](https://www.bis.org/publ/bcbs22.htm) · [S0065](https://github.com/statsmodels/statsmodels) · [S0071](https://stats.stackexchange.com/questions/82720/confidence-interval-around-binomial-estimate-of-0-or-1)

## D42 — 概率下的回报与效用决策

PARTIAL · 决策语义 · [D42 原始条目](../../TECHNICAL_DEBT.zh-CN.md#d42)

- 既有行为：给 p*O-1 的事件/补事件 EV 区间、S 与后验正 EV 质量。
- 目标和前提：本金归一 EV、后验阈值质量和行动损失。效用选择主观、尾部损失与资本约束可能改变最优行动。
- 仓库验证线索：现有 check_ev/check_geometry；未来成本/效用解析案例及概率模型不确定性敏感性。
- 相关研究问题：D39、C30、E46。
- 外部贡献与待查：尾质量不等于赢的概率；风险偏好、共同暴露和信息价值属于另一层。 [S0041](https://erm.ncsu.edu/az/erm/i/chan/library/pelletier-research-partners-2009.pdf) · [S0042](https://people.duke.edu/~clemen/bio/Published%20Papers/45.PredictionMarkets-Page%26Clemen-EJ-2013.pdf) · [S0057](https://sre.google/workbook/error-budget-policy/) · [S0059](https://www.bis.org/publ/bcbs22.htm) · [S0086](https://www.sciencedirect.com/science/article/pii/S0169207014000533) · [S0092](https://pmc.ncbi.nlm.nih.gov/articles/PMC7034331/)

## D43 — 主观与历史结论冲突

RESOLVED · 决策语义 · [D43 原始条目](../../TECHNICAL_DEBT.zh-CN.md#d43)

- 既有行为：classify_model_relation 返回 CONFLICT，两侧估计保持原值；任一跨阈值为 UNCERTAIN。
- 目标和前提：独立渠道的阈值冲突。模型 agreement 也不证明共同正确；来源可能共享偏差。
- 仓库验证线索：analysis_parity/check_classifiers 的关系案例和 state_parity 组合字段对照。
- 相关研究问题：D37、D38；不依赖 C29 融合。
- 外部贡献与待查：聚合可以掩盖分歧；调查是否同一目标、信息相依及估计层级。 [S0018](https://academic.oup.com/jrsssb/article/72/1/71/7076442)

## D44 — 一次兑现不能验证概率预测

FUNDAMENTAL_LIMIT · 不可识别 · [D44 原始条目](../../TECHNICAL_DEBT.zh-CN.md#d44)

- 既有行为：返回模型条件结果，不根据单次结果认证/否定模型。
- 目标和前提：预测者长期表现或本次信念是否正确。选择性展示成功案例、结果后见偏差与稀疏任务组。
- 仓库验证线索：未来用校准模拟展示偶发失败与长期可靠度的区别，不以一个 outcome 作唯一验收。
- 相关研究问题：A04、D35、D36。
- 外部贡献与待查：一次 Bernoulli 兑现只贡献一次损失，不能识别校准曲线。 [S0005](https://sites.stat.washington.edu/raftery/Research/PDF/Gneiting2007jasa.pdf) · [S0012](https://kylewoodward.com/blog-data/pdfs/references/dawid-journal-of-the-american-statistical-association-1982A.pdf) · [S0029](https://www.kdd.org/kdd2017/papers/view/the-selective-labels-problem-evaluating-algorithmic-predictions-in-the-pres) · [S0045](https://journals.ametsoc.org/view/journals/mwre/78/1/1520-0493_1950_078_0001_vofeit_2_0_co_2.xml)

## E45 — 数据库接入与事件计数提取

DEFERRED · 证据准入、工程 · [E45 原始条目](../../TECHNICAL_DEBT.zh-CN.md#e45)

- 既有行为：无 DB 运行时依赖；已有 history_estimate 可接收预先审核计数。
- 目标和前提：版本化抽取的独立目标单位数。重叠查询、删失/未成熟结果、隐私、事务快照和错误汇聚。
- 仓库验证线索：未来跨查询去重、幂等、快照一致、事件版本、unknown applicability 与权限隔离测试。
- 相关研究问题：#10/B14→#9 借用策略→#8；B13、B20。
- 外部贡献与待查：快照、迟到/修订、重复与暗漏要用实际调用方数据审计。 [S0027](https://doi.org/10.1145/2382577.2382579) · [S0088](https://www.w3.org/TR/2013/REC-prov-o-20130430/)

## E46 — 模型专属 API 路由与结果类型

PARTIAL · 工程、决策语义 · [E46 原始条目](../../TECHNICAL_DEBT.zh-CN.md#e46)

- 既有行为：13 个明确函数已有估计/分析分层，只有两类冻结模型。
- 目标和前提：已知模型结果与失败语义。ABI 扩展、无效联合状态、类型擦除和版本混淆。
- 仓库验证线索：[RC 断言地图](../../IMPLEMENTATION_VALIDATION.zh-CN.md#preview-device-history-validation)中 `test_missing_context_and_path_mismatch、test_installed_v1_values_and_states、test_phase_two_mix_shift` 验证有限用例。现有 C 断言仍以 v1 冻结参考为准。
- 相关研究问题：A08、D39、E47。
- 外部贡献与待查：外部模型需要独立估计量与状态，不从其他库接口推出产品范围。 [S0064](https://github.com/scikit-learn/scikit-learn) · [S0066](https://github.com/CamDavidsonPilon/lifelines) · [S0070](https://github.com/cdcepi/FluSight-forecast-hub)

## E47 — 版本化持久化与历史重现

PARTIAL · 工程、证据准入 · [E47 原始条目](../../TECHNICAL_DEBT.zh-CN.md#e47)

- 既有行为：组合返回独立版本及有意义结果，调用者拥有存储；无数据库/文件 schema。
- 目标和前提：原输入、版本及计算环境能否复验。padding/字节序/枚举宽度、数值编码、旧模型可得性与历史覆盖。
- 仓库验证线索：[RC 断言地图](../../IMPLEMENTATION_VALIDATION.zh-CN.md#preview-device-history-validation)中 `test_strict_and_pool_counts、test_numerical_range_failure_preserves_review；可执行示例 JSON` 验证有限用例。现有 C 断言仍以 v1 冻结参考为准。
- 相关研究问题：D38、E46、E45。
- 外部贡献与待查：区分重读结果、重跑同模型和重建过去可用证据；后者依赖外部快照。 [S0027](https://doi.org/10.1145/2382577.2382579) · [S0082](https://pmc.ncbi.nlm.nih.gov/articles/PMC10499856/) · [S0088](https://www.w3.org/TR/2013/REC-prov-o-20130430/)

## E48 — 数值精度、极端输入与平台验证

PARTIAL · 计算、表示 · [E48 原始条目](../../TECHNICAL_DEBT.zh-CN.md#e48)

- 既有行为：大参数 Beta、精确十进制、正 Gamma 与畸形 provenance 修复已进入 v1；覆盖并非无限。
- 目标和前提：有限精度数值及状态可复核性。极窄后验的 x 量化、libm/FTZ/编译标志、非常小尾部相对误差。
- 仓库验证线索：large_numerics、decimal_parity、五 CI 作业；未来 ARM/浮点环境按实际执行记录。
- 相关研究问题：R01–R03、D41、E47。
- 外部贡献与待查：检验相邻点、极端尾、平台模式、舍入与参考独立性；算法不能跨越表示分辨率。 [S0025](https://docs.oracle.com/cd/E19957-01/806-3568/ncg_goldberg.html) · [S0026](https://doi.org/10.1145/131766.131776) · [S0048](https://www.ampl.com/REFS/rounding.pdf) · [S0050](https://dlmf.nist.gov/8.17) · [S0061](https://github.com/scipy/scipy) · [S0062](https://github.com/boostorg/math) · [S0063](https://github.com/wch/r-source) · [S0068](https://github.com/mpmath/mpmath) · [S0069](https://github.com/bminor/glibc) · [S0073](https://github.com/scipy/scipy/issues/21725) · [S0076](https://github.com/scipy/scipy/issues/17631) · [S0093](https://github.com/boostorg/math/issues/1198) · [S0094](https://github.com/stan-dev/math)

## R01 — 大计数 Beta 与独立数值参考

RESOLVED · 历史修复、计算 · [R01 原始条目](../../TECHNICAL_DEBT.zh-CN.md#r01)

- 既有行为：变换后的真实 Beta 密度积分、补偿中心与独立高精度参考已进入 v1。
- 目标和前提：原 Jeffreys 分布的极端求值。binary64 x 的邻接间隔仍限制极窄后验分位，Issue #5 未因此关闭。
- 仓库验证线索：large_numerics：28 历史/140 CDF、190 stress/570 quantiles；18 corrected threshold 分析。
- 相关研究问题：E48、D41；未来额外保证依赖 #5/#6。
- 外部贡献与待查：区分 80/60 位独立参考与外部软件结果；不把邻接限制当回归。 [S0026](https://doi.org/10.1145/131766.131776) · [S0050](https://dlmf.nist.gov/8.17) · [S0061](https://github.com/scipy/scipy) · [S0062](https://github.com/boostorg/math) · [S0063](https://github.com/wch/r-source) · [S0068](https://github.com/mpmath/mpmath) · [S0073](https://github.com/scipy/scipy/issues/21725) · [S0093](https://github.com/boostorg/math/issues/1198)

## R02 — 精确十进制到 binary64 与正零

RESOLVED · 历史修复、计算 · [R02 原始条目](../../TECHNICAL_DEBT.zh-CN.md#r02)

- 既有行为：精确整数中点比较与 ties-to-even，零明确构造为 +0，保留完整 ASCII 文法。
- 目标和前提：给定十进制文本的最接近 binary64 位型。文法/范围仍有限；精确转换不代表所有后续 libm 逐位一致。
- 仓库验证线索：41 exact-bit 向量、四可用舍入模式、可用逗号 locale；历史 6099 差分含 100000 字符模式。
- 相关研究问题：E48、R03 共享兼容审查而非共享转换规则。
- 外部贡献与待查：标准库可能按当前模式舍入；精确 parser 与其他数学输出是独立合同。 [S0025](https://docs.oracle.com/cd/E19957-01/806-3568/ncg_goldberg.html) · [S0048](https://www.ampl.com/REFS/rounding.pdf) · [S0069](https://github.com/bminor/glibc)

## R03 — provenance 不变量与正 Gamma 可重入求值

RESOLVED · 历史修复、工程 · [R03 原始条目](../../TECHNICAL_DEBT.zh-CN.md#r03)

- 既有行为：拒绝畸形旧值且保持输出含原地别名；正参数 Gamma 避开 lgamma/signgam。
- 目标和前提：状态不变量与正 Gamma 求值。调用者同对象数据竞争仍不安全；浮点环境与全 libm 线程性质不由此全面证明。
- 仓库验证线索：api_contract/check_provenance_invariant 的组合/别名/优先级，state_parity 23 转移；Beta 回归间接覆盖归一化。
- 相关研究问题：D38、E48；全架构额外验证见 #6。
- 外部贡献与待查：浮点外部来源仅给工程对照，实际归因见引入提交 a085776。 [S0025](https://docs.oracle.com/cd/E19957-01/806-3568/ncg_goldberg.html)

## R04 — v1.0.0 正式标签与发布

RESOLVED · 历史修复、发布审计 · [R04 原始条目](../../TECHNICAL_DEBT.zh-CN.md#r04)

- 既有行为：正式 annotated v1.0.0 与 stable Release 已完成，source-only 无自制平台二进制。
- 目标和前提：标签对象、目标提交、Release 与 CI 身份。Release 页面存在不能替代 tag peeled commit 和 CI 精确 SHA 核对。
- 仓库验证线索：独立 Git 远程 refs、Release API 与 run head_sha；不以单个 push 成功消息作唯一证据。
- 相关研究问题：R01–R03、[发布规则](../../RELEASING.md)。
- 外部贡献与待查：外部方法文献不适用；以 Git/ref/Release 记录独立证明。 以账本和公开 GitHub 正式发布记录复核。
