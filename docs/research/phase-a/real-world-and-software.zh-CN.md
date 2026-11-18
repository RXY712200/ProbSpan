# 实际应用与软件证据

[研究导航](README.zh-CN.md) · [完整源登记](source-register.tsv) · [方法](methods-and-assumptions.zh-CN.md)

## 应用与评价

以下证据包括实时提交后的回顾性评分、历史回测、过程监控及个案复盘。验证类型及分母决定可推广的范围。涉及专业判断的场景仅比较方法。

| 应用、执行者 | 目标、总体、单位、时距与数据 | 方法、实测比较与限制 |
|---|---|---|
| 天气 · ECMWF 与中国国家气象中心 | 特定网格/时点与阈值的降水等事件；初始化后的预报时距；多个模型成员对应一份实况。中国案例用 2000 年实况核验 32 成员集合，中文摘要从 5 月、英文摘要从 6 月起，精确样本窗须查正文。 | 比较奇异向量与滞后集合，检查 Talagrand、离散度、BS/BSS、命中和空报，BSS 以气候概率为参照。ECMWF 长期回顾记录扰动、分辨率及卫星/同化变化；时距与半球的改进不均一。不能把成员数作现实分母。 [S0033](https://www.ecmwf.int/sites/default/files/elibrary/2017/18198-25-years-ensemble-forecasting-ecmwf.pdf) · [S0043](https://html.rhhz.net/yyqxxb/html/20020103.htm) |
| 水文 · NOAA/NWS HEFS，USGS 历史对照 | 流域预报点的未来径流分布，时距与汇水面积相关；观测站记录结合气象驱动和水文模式。 | HEFS 样本覆盖 97 个点、水文年 2014–2025 和提前 1–14 日；HEFS 若干时距和指标改善，预报不确定性表征的进步较有限；USGS 以 Kling–Gupta efficiency 和气候值基准比较连续美国历史径流。历史模拟使用的信息集、状态初始化及已知气象驱动不同于业务预测。季节、枯洪、测站选择和极端流量的支撑须单列。 [S0036](https://agupubs.onlinelibrary.wiley.com/doi/10.1029/2025GL119088) · [S0090](https://hess.copernicus.org/articles/27/1809/2023/index.html) |
| 制造 · NIST/SEMATECH 光刻案例 | 光刻工艺线宽，层级为批次、晶圆、测点；目标是工艺的中心和批间/批内波动，不是任意时期的二元良率。 | 真实过程数据配对批内、批间图及方差成分；控制限按过程组定义。另有二项 p 图用于固定检测规则的不合格比例；需要纯抽样和稳定机制。把各测点当独立产品可高估有效数据量，初始过程控制限也不担保未来新工艺。 [S0044](https://itl.nist.gov/div898/handbook/pmc/section6/pmc61.htm) · [S0052](https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc332.htm) |
| 硬件 · Backblaze | 在线磁盘型号在报告期的故障率，分母 drive-days；设备群由数据中心部署、替换及筛选形成；既有存活盘继续贡献暴露。 | 按型号报告故障及 AFR，以历史/总体和型号相比较，以盘数和 drive-days 门槛入表；年度 AFR 从 2024 的 1.55% 到 2025 的 1.36%。部署时代、型号与报废策略混杂。年度乘倍率不能直接变成「新盘下一 100 小时故障」概率，须重新核对生存队列和删失。无此前瞻比较。 [S0038](https://www.backblaze.com/blog/backblaze-drive-stats-for-2025/) · [S0053](https://www.itl.nist.gov/div898/handbook/apr/section1/apr131.htm) |
| 软件服务 · AWS S3 / 外部网络监测 | US-EAST-1 2017-02-28 GET/LIST 与其他请求可用性及恢复过程；请求共享区域子系统和依赖。 | AWS 记录索引及放置子系统重启，索引恢复后分阶段恢复请求。ThousandEyes 从外部观测到异常并早期推测内部网络原因；视角不具根因识别力。SLO 可按请求分母及四周错误预算衡量；没有公开请求级独立测试、预测基准或事故概率。此案是实际依赖失败证据。 [S0039](https://aws.amazon.com/message/41926/) · [S0077](https://www.thousandeyes.com/blog/aws-s3-outage-likely-caused-by-internal-network-issue) · [S0057](https://sre.google/workbook/error-budget-policy/) |
| 公共卫生 · CDC FluSight 与 COVID-19 Forecast Hub | 地区/周、提前 1–4 周；FluSight 目标为实验室确诊相关住院，COVID 案例为死亡数。提交的是分位数，结果由监测系统发布和修订。 | FluSight 用 WIS、相对 WIS 和覆盖；2021–22 与 2022–23 集成的 WIS 排名分别第二和第五，部分模型/地点优于集成；相同集成不能假设两季同表现。COVID 多地点研究支持集成作比较基线，远端时距和波峰误差仍重要。按共同地点/时距配对，显式选择 truth vintage。 [S0034](https://www.nature.com/articles/s41467-024-50601-9) · [S0035](https://pubmed.ncbi.nlm.nih.gov/35394862/) · [S0081](https://www.cdc.gov/flu-forecasting/evaluation/2024-2025-report.html) |
| 医疗预后 · Michigan Medicine 外部验证 | 一个医疗系统住院就诊的脓毒症评分，逐时报警与临床结局，依赖 EHR 记录定义。 | Wong 等的回顾性队列显示 AUC .63；常用阈值漏掉 67% 脓毒症病例却对 18% 住院触发报警，报告了临床基准及报警负担。Obermeyer 等在另一任务发现费用代理导致同分数病情严重程度不同；这是不同终点和机制的第二个反例。后续新版本与真实介入影响还需新研究。 [S0023](https://pmc.ncbi.nlm.nih.gov/articles/PMC8218233/) · [S0022](https://pubmed.ncbi.nlm.nih.gov/31649194/) |
| 能源 · GEFCom2014 | 分任务对负荷、价格、风、太阳给出时间索引预测分位；真实历史能源资料与天气信息，按供给的预测轮次出样本。 | 以分位损失排名并用基准模型比较；指标对每个分位有明确非对称惩罚。预测端可用的温度 vs 事后天气是不同设置，参赛榜与新地区/长期实时投运不同。 [S0037](https://doi.org/10.1016/j.ijforecast.2016.02.001) |
| 保险 · freMTPL 法国车险 | 保单在观察期的理赔频数与暴露，另有理赔金额；目标可能是每单位保单年频率、损失严重度或两者组合。 | 比较 Poisson GLM、树及柔性模型，按 holdout 偏差/校准表现对照。低暴露时零赔不等同低长期风险，拆分同保单或在金额量中引入事故后变量会影响评价。公开案例没有新地区现场定价验证。 [S0040](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3164764) |
| 金融风险 · 交易部门 VaR | 风险模型给条件损失尾分位，单位为部门-交易日，回测比较真实或假设持仓收益是否越界。 | Berkowitz 等比较无条件例外率、独立性与基于持续时间等诊断；频率正确而异常成簇仍会失败。Basel 历史交通灯计数便于执行，但规则与样本大小相关，例外幅度、交易损益定义及制度变化外推有限。 [S0041](https://pubsonline.informs.org/doi/abs/10.1287/mnsc.1080.0964) · [S0059](https://www.bis.org/publ/bcbs22.htm) |
| 地缘事件 · Good Judgment Project | 以预先定义的截止和结算规则对异质问题提交概率，可随事件时间更新，单位应保留问题 ID 和预测日。 | Mellers 等比较训练、团队与聚合和替代条件的 Brier 等表现，图 1 对照含无训练组，第一年概率训练改善 Brier；同题多个时点不是多个结局。参与者选择、开放题数、公共信息时间和结算争议限制迁移。 [S0019](https://escholarship.org/uc/item/4rg4n9vr) |
| 事件市场与体育 · Intrade 与多家赔率数据 | 兑现合约价格和结局随到期时距变化；足球/其他运动以赛前赔率和赛事结算作配对；不同市场决定手续费/利润率。 | Page–Clemen 讨论距到期时间与热门/冷门失校准；Štrumbelj 比较 Shin、直归一和回归方法，结果随市场来源和运动变化。价差、共同流动性和赔率公布时点影响比较。后见的 closing odds 与较早预测不能混成同一信息集。 [S0042](https://people.duke.edu/~clemen/bio/Published%20Papers/45.PredictionMarkets-Page%26Clemen-EJ-2013.pdf) · [S0086](https://www.sciencedirect.com/science/article/pii/S0169207014000533) |

## 软件源码、测试和移植风险

固定树、文件和许可证见 TSV。下列为代码/断言检查，未运行第三方测试。许可证是仓库/文件许可线索，直接复用时应逐文件重新核验，本研究未引入第三方代码。

| 软件 | 代码路径与方法、错误处理 | 测试或限制及与 ProbSpan 的关系 |
|---|---|---|
| SciPy v1.15.3 | `beta_gen` 把 PPF/ISF 派给私有包装器，CDF 走 `scipy.special.betainc`；通用连续分布支持 loc/scale。 | `test_distributions.py` 用分布级回归和边缘输入；C++ Boost 依赖及双 wrapper 的维护差异可能导致版本差异。ProbSpan 冻结参考不是该版本，SciPy 与 Boost 不能算完全独立的数值复核。 [S0061](https://github.com/scipy/scipy/blob/e29dcb65a2040f04819b426a04b60d44a8f69c04/scipy/stats/_continuous_distns.py) · [S0073](https://github.com/scipy/scipy/issues/21725) |
| Boost.Math 1.88.0 | `beta.hpp` 选 Lanczos、连分式、级数与递推路径，并通过 policy 报域错误和收敛错误。 | `test_ibeta.cpp` 分类型及数据区间运行并核尾接口；C++ 模板、策略与头文件不适合直接映射 C11 的状态/容差合同。 [S0062](https://github.com/boostorg/math/blob/529f3a759d83aa9437613666ea6293c9336d4069/include/boost/math/special_functions/beta.hpp) · [S0093](https://github.com/boostorg/math/issues/1198) |
| R nmath 固定快照 | `pbeta_raw` 用 TOMS 708 `bratio` 同时产生两尾，支持 log 与方向，检查端点、形参和警告。 | 检查了 `toms708.c` 的 ierr 路径，未检查完整 R 回归；standalone 构建及 R 依赖和 GPL 范围与 C 库不同。算法难点可比较，代码不引入。 [S0063](https://github.com/wch/r-source/blob/6dc685bb80c715fe31e1a88348fd5d738b4f3dc2/src/nmath/pbeta.c) |
| scikit-learn 1.6.1 | `CalibratedClassifierCV` 对响应分数交叉拟合 sigmoid/isotonic，输入检查包括类数和切分限制。 | `test_calibration.py` 覆盖二元/多类、概率可用和拟合集合。NumPy/SciPy/Python；CV 的分组及时间可用性不由校准器保证。 [S0064](https://github.com/scikit-learn/scikit-learn/blob/f159b78dc59f250cdde8fe391a21f0bc871960ad/sklearn/calibration.py) |
| statsmodels 0.14.4 | `proportion_confint` 可选 normal、Wilson、beta、Jeffreys 等，离散尾与双侧 alpha 按方法处理。 | `test_proportion.py` 检查方法与端点；SciPy 数值和适用证据仍独立问题。函数统一返回区间不等于其统计解释统一。 [S0065](https://github.com/statsmodels/statsmodels/blob/054a626210d919ebdd6296fa6b8d895f767bd544/statsmodels/stats/proportion.py) |
| lifelines 0.30.0 | `KaplanMeierFitter.fit` 接受观察时长、是否发生、入组时点与权重；right-censor 和 interval-censor 有不同计算路径。 | `lifelines/tests/test_estimation.py` 覆盖例子与生存曲线。Python/pandas/NumPy；警告或拟合成功无法证明独立删失，固定期二项 API 不可直接接受此型输入。 [S0066](https://github.com/CamDavidsonPilon/lifelines/blob/47afb1c1a272b0f03e0c8ca00e63df27eb2a0560/lifelines/fitters/kaplan_meier_fitter.py) |
| fabletools 0.5.0 | `accuracy.R` 按键和时点合并预测及实际，允许点/区间/分布指标。 | 检查 `test-accuracy.R` 的实验数据和指标路径，R/tsibble/distributional 依赖。相同包不同 metric 适用范围各异，真实数据按时点的可用性仍由调用者提供。 [S0067](https://github.com/tidyverts/fabletools/blob/d8a0fbc3fc82d7d315db00ad58524b164dfbeafc/R/accuracy.R) |
| mpmath 1.3.0 | `betainc` 由幂函数/超几何实现并可正规化，区间可由端点式相减。 | `test_functions.py` 的一般任意精度证据不担保每个 Beta 极尾（该测试文件并无专门 Beta 断言）。ProbSpan 的 80/60 位参考使用独立 logit 密度积分，而非直接信任同名函数。 [S0068](https://github.com/mpmath/mpmath/blob/b5c04506ef0cd4a1f1213f8389ee21c9c3551582/mpmath/functions/expintegrals.py) |
| glibc 2.41 | `strtod_l.c` 区分舍入模式、有效位、subnormal、overflow 与 errno，使用 libc/GMP 型内部多字运算。 | `tst-strtod-round.c` 对多模式和边界舍入进行回归。通用 libc parser 的 locale、指数与模式合同超出 ProbSpan ASCII odds 文法，正零和后续域检查也不同。 [S0069](https://github.com/bminor/glibc/blob/74f59e9271cbb4071671e5a474e7d4f1622b186f/stdlib/strtod_l.c) |
| CDC FluSight Forecast Hub 固定快照 | `hub-config/tasks.json` 指定目标、时点、时距及输出层；`model-output/README.md` 指定团队提交和目录规范。 | 这两份文件是数据契约，未审查整套验证执行。Hub 不合并成独立二项计数，版本、提交有效性及真值修订是调用方集成证据。 [S0070](https://github.com/cdcepi/FluSight-forecast-hub/blob/987c9b005dda15938a638c2f66830d951fb9cd01/hub-config/tasks.json) |
| Stan Math 4.9.0 | `inc_beta.hpp` 检查数域，调用 Boost 并把标量接口推广到向量；宿主还有自动微分体系。 | 特例 CDF 与域验证测试提供适配证据，Boost 后端并非独立数值路径。层级 Bayes 等上层模型也不由此函数证明可适用。 [S0094](https://github.com/stan-dev/math/blob/8a09048f5187662687e04c14d7737cf4d20a18a1/stan/math/prim/fun/inc_beta.hpp) |
| forecast 8.24.0 | `tsCV` 按每个起点截取序列，调用用户预测函数并记录逐时距误差，可传窗口和初始训练信息。 | 读取实现及失败产生缺失值的路径，未取得指定测试路径。R/forecast 的点预测误差不是分布评分，也不自动处理分组与数据发布时间。 [S0095](https://github.com/robjhyndman/forecast/blob/58df83568ac79c03171bd54f56cfae2260b5b898/R/tscv.R) |

## 讨论和失败线索

- **端点与小样本。** Cross Validated 问答按构造区分 0/1 端点，社区反例可用二项概率独立复算；要分频率和后验、单侧和双侧才可比。问答不认证现实代表性。 [S0071](https://stats.stackexchange.com/questions/82720/confidence-interval-around-binomial-estimate-of-0-or-1) · [S0001](https://doi.org/10.1214/ss/1009213286)
- **数值极限与否证。** SciPy issue 21725 的维护者指出 wrapper 路径及极大形状分布近似阶跃，Boost #1198 讨论不完全 Beta 极端输入。Beta-prime #17631 另有尾部变换问题，不能作为同一 Beta 缺陷计数。复现需要当时依赖/版本和确切输入，本次未重跑 issue 示例。 [S0073](https://github.com/scipy/scipy/issues/21725) · [S0076](https://github.com/scipy/scipy/issues/17631) · [S0093](https://github.com/boostorg/math/issues/1198)
- **验证泄漏。** MAPIE #799 对教程预测时点发问；scikit-learn #19072 指出分组+时序+gap 同时存在的需求，#32076 针对 TargetEncoder 内部分割，#22523 针对滚动窗口控制。替代解释需核对索引或已有 splitter 参数。公开讨论是可重现线索，未在本研究重跑或用以否定整套库。独立论文说明信息集污染与简单基线比较可改变结论。 [S0074](https://github.com/scikit-learn-contrib/MAPIE/issues/799) · [S0075](https://github.com/scikit-learn/scikit-learn/issues/19072) · [S0078](https://github.com/scikit-learn/scikit-learn/issues/32076) · [S0079](https://github.com/scikit-learn/scikit-learn/issues/22523) · [S0082](https://pmc.ncbi.nlm.nih.gov/articles/PMC10499856/)
- **子群、代用标签与低技能。** 总体拟合或同一数据上的历史回测可能掩盖新医院、子群或峰值失准。药物外部对照草案独立要求结局、纳排和测量一致；这类证据支持元数据审核，无法推出跨行业同一效果量。分位数覆盖和点分数也可能同时改善或冲突。 [S0022](https://pubmed.ncbi.nlm.nih.gov/31649194/) · [S0023](https://pmc.ncbi.nlm.nih.gov/articles/PMC8218233/) · [S0034](https://www.nature.com/articles/s41467-024-50601-9) · [S0051](https://www.fda.gov/media/164960/download)
- **聚合与弃权。** 同事转述同一传感器预警时，两个专家的边际概率没有第二个独立似然。预测池化比较有意义的条件是相同目标和可保留的原始提交。缺失目标组有正权时报告界或 unknown；该限制可用两个观察等价 DGP 检验。 [S0018](https://academic.oup.com/jrsssb/article/72/1/71/7076442) · [S0028](https://ageconsearch.umn.edu/record/292716)

### 争议线索的复核

| 线索及日期 | 提出与回应 | 独立核对及边界 |
|---|---|---|
| 端点区间，2014 | 提问者追问样本比例在端点时如何给区间；答复用不同构造，区间目标需另核。 | 零事件反演和 Brown 频率覆盖枚举可独立检查。 [S0071](https://stats.stackexchange.com/questions/82720/confidence-interval-around-binomial-estimate-of-0-or-1) · [S0001](https://doi.org/10.1214/ss/1009213286) |
| SciPy #21725，2024-10-19 | dschmitz89 讨论两 wrapper；jzmaddock 指出极窄支持与双精度变化尺度。后续评论把关闭关联到上游修订。 | 用 DLMF 恒等式和相邻点标准复核条件；无法从合并/关闭状态推出冻结 SciPy 已修复所有输入。 [S0073](https://github.com/scipy/scipy/issues/21725) · [S0050](https://dlmf.nist.gov/8.17) |
| SciPy #17631，2022-12-19 | chrisb83 报 Beta-prime CDF/PPF；WarrenWeckesser 将 CDF 丢失归因于 x/(1+x) 舍入到 1。 | 机制与浮点消去一致。未运行当时环境；变换输入和 Beta 核精度须分别查。 [S0076](https://github.com/scipy/scipy/issues/17631) · [S0025](https://docs.oracle.com/cd/E19957-01/806-3568/ncg_goldberg.html) |
| Boost #1198，2024-09-13 | dschmitz89 报非中心 F 边缘条件。jzmaddock 复现并提出 incomplete beta 的大参数近似方向。 | 补充分布依赖路径线索。不能直接将非中心 F 的异常转算为 ProbSpan Beta 误差。 [S0093](https://github.com/boostorg/math/issues/1198) · [S0062](source-register.tsv) |
| MAPIE #799，2025-11-14 | samuelefiorini 质疑 ENBPI 教程，allglc 同意可能有问题、表示无法量化影响，提出独立验证集。 | 泄漏论文独立支持按当时信息切分原则；尚未复算教程指标。 [S0074](https://github.com/scikit-learn-contrib/MAPIE/issues/799) · [S0027](https://doi.org/10.1145/2382577.2382579) |
| scikit-learn #19072/#32076，2020/2025 | getgaurav2 提出 group+time+gap，无回复；MatthiasLoefflerQC 指出目标编码分组需求，thomasjpfan 提到 GroupKFold 接口思路。 | 需重新检查部署时是否会遇到组内重复及未来标签，不能拿功能讨论当既有版本承诺。 [S0075](https://github.com/scikit-learn/scikit-learn/issues/19072) · [S0078](https://github.com/scikit-learn/scikit-learn/issues/32076) |
| scikit-learn #22523，2022-02-17 | cmp1 请求 rolling window；thomasjpfan 给现有 max_train_size 例子并说明删除 n_splits 会破坏兼容。 | 时间轴索引需真实对照，既有窗口参数不说明统计效果。 [S0079](https://github.com/scikit-learn/scikit-learn/issues/22523) · [S0060](https://otexts.com/fpp3/tscv.html) |
| S3 外部告警，2017 | ThousandEyes 从网络观测提出故障推测，AWS 后续复盘指出容量移除和依赖恢复。 | 证据不同：监测可确认影响时段，厂商掌握内部操作；独立流量样本未公开，不能复算总体错误率。 [S0077](https://www.thousandeyes.com/blog/aws-s3-outage-likely-caused-by-internal-network-issue) · [S0039](https://aws.amazon.com/message/41926/) |
| 棒球收缩，2010 | 问答复算 arcsine 变换中的近似方差，原文以早期命中率预测同一批选手。 | 变换方差与 Beta-binomial 参数后验不同，同主体季内表现不证明新主体可比。 [S0097](https://stats.stackexchange.com/questions/5727/james-stein-estimator-how-did-efron-and-morris-calculate-sigma2-in-shrinkag) · [S0087](https://jhanley.biostat.mcgill.ca/bios602/MultilevelData/EfronMorrisJASA1975.pdf) |
