# 外部证据、可迁移范围与来源修订

[导航](README.zh-CN.md) · [Phase A 登记](../phase-a/source-register.tsv) · [Phase B 增补](source-addendum.tsv) · [实验](experiments-and-results.zh-CN.md)

## 正文重新核验与证据冲突

| 观察及访问级别 | 可支撑的 Phase B 结论 | 仍缺的条件 |
|---|---|---|
| Brown–Cai–DasGupta 原刊链接在本轮直取只回验证页；Web 索引可见原文图 9 和端点讨论，未把返回 200 当已读该 PDF。 | 公开段落支持 Wald 覆盖及宽度问题、端点修正的区分。B-E001 独立重算冻结 v1 的未改端点版本。 | 论文多种近端点变体未逐一复刻，实际设备独立性及未来识别未知。 [S0001](https://web.pdx.edu/~ihd/stat563.S17/brown.pdf) |
| Schmidli 等的 Wiley 摘要、Viele 全文操作特性、Hobbs 及 Ibrahim 等的 PMC 正文/公式。 | 具备合法历史、条件交换性及充分目标时，可在偏差、方差、功效上比较借用强度。摘要中的 mixture robustness 与本轮零数据无适应不冲突。 | B-E002 使用已观察的固定历史与构造弱成分，未复现真实临床试验、MAP 混合拟合或一类错误。 [S0006](https://onlinelibrary.wiley.com/doi/abs/10.1111/biom.12242) · [S0007](https://pmc.ncbi.nlm.nih.gov/articles/PMC3951812/) · [S0030](https://pmc.ncbi.nlm.nih.gov/articles/PMC3134568/) · [S0096](https://pmc.ncbi.nlm.nih.gov/articles/PMC4626399/) |
| JMLR 查看协变量偏移假设；Barber 等 PDF §2、Choe–Ramdas/Howard 作者稿相关定理已查看。 | 若 X 目标变化而 P(Y∣X) 不变且支持正，标准化可识别；预测边际覆盖与逐点条件覆盖不同。固定时点评分不转化为任意停止。 | B-E003/B-E005 的估计误差和公平符号不证明某应用的条件机制、exchangeability 或 martingale 条件。 [S0009](https://www.jmlr.org/papers/v8/sugiyama07a.html) · [S0010](https://www.stat.berkeley.edu/~ryantibs/papers/limits.pdf) · [S0091](https://arxiv.org/abs/2110.00115) · [B-S0002](https://arxiv.org/abs/1810.08240) |
| 医疗竞争风险原综述及 BMJ 方法案例相关段落已查；独立 sepsis 验证报告住院级 AUC .63，阈值警报覆盖全部住院 18%、漏识别 67% 病例。 | 竞争事件改变实际发生的风险集；任务端点、分母和动作成本可以改变模型评价。AUC 和报警负担是不同对象。 | 该院和版本的回顾性指标不识别未来干预效果，不能划给 C 核心一个通用阈值。 [B-S0001](https://pmc.ncbi.nlm.nih.gov/articles/PMC4741409/) · [S0089](https://www.bmj.com/content/378/bmj-2022-071349) · [S0023](https://pmc.ncbi.nlm.nih.gov/articles/PMC8218233/) |
| Obermeyer 原作者存档与 Cornell 选择标签论文的机制/观测设计部分。 | 费用作为健康代理使子群目标偏移；选择性观测可令全体效能不识别。二者分别涉及测量和选择，不能指望简单加样本修复。 | 须有真实标签审计、随机验证或在领域允许下的识别结构；无额外反事实观测不能证明某决策策略的因果效果。 [S0022](https://www.law.berkeley.edu/wp-content/uploads/archive/2025/09/Obermeyer-Science-Dissecting-Racial-Bias-in-Algorithm-used-to-manage-the-health-of-populations.pdf) · [S0029](https://www.cs.cornell.edu/home/kleinber/kdd17-selective.pdf) |
| Nature 期刊正文复核，FluSight 2021–22/2022–23 的集合按 WIS 分别第二、第五，较长提前期技能和 95% 覆盖多数变差；WIS 的数学定义见 Bracher 等。 | 操作评价需按时距及共同数据配对。季节排名不同与 B-E005 的“固定并声明评价对象”一致。 | 未取得/比较实时首次发布与修订双快照，真实排名翻转是否由真值修订造成不可推定。 [S0034](https://www.nature.com/articles/s41467-024-50601-9) · [S0013](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1008618) |
| 1975 原文表 1（1970 赛季）与 Stan 固定原始 TSV 均复核，B-E007 实际重算后续真值评分。 | 原文变换尺度的平方误差改善和这次 Brier/log 改善不冲突；同样合理的打数与球员平均可以得不同的排序。 | 选择进组机制、未来打数和球队依赖未知，场景不验证新组，也没有重做原文 Stein 损失。 [S0087](https://jhanley.biostat.mcgill.ca/bios602/MultilevelData/EfronMorrisJASA1975.pdf) · [B-S0003](https://github.com/stan-dev/example-models/blob/e5b7d9e2e9ecc375805c7e49e4a4d4c1882b5e3b/knitr/pool-binary-trials/efron-morris-75-data.tsv) |
| DLMF §8.17 的 Beta 积分与对称，及现行数值合同、源码与 Issue #5/#6。 | 表示网格可限制 quantile 残差；绝对容差不保证极小远尾相对误差；同表示阈值的高精度比较为计算证据。 | 一个 Linux/libm 组合、五形状组，未覆盖平台或全参数合同；无退化输入邻接之外的产品改动证据。 [S0050](https://dlmf.nist.gov/8.17) · [数值契约](../../NUMERICAL_CONTRACT.md) |

Phase A 行业案例帮助界定观察设计。磁盘年度 drive-days 是暴露量，欲验证“下一完整 100 小时的首次故障”须跟踪纳入队列、版本、观察结束及重复主体，并以同期实测检查校准。天气的同一次气象过程配对不独立，集合成员是预测分布；市场价格带风险/交易机制，时距及合约与事件概率有关。三者不能给同一个“借用强度”标签。年度磁盘、市场和真实设备记录在本轮未下载重跑；仅保留经 Phase A 登记的设计差异作为背景。 [S0038](https://www.backblaze.com/blog/backblaze-drive-stats-for-2025/) · [S0033](https://www.ecmwf.int/sites/default/files/elibrary/2017/18198-25-years-ensemble-forecasting-ecmwf.pdf) · [S0042](https://people.duke.edu/~clemen/bio/Published%20Papers/45.PredictionMarkets-Page%26Clemen-EJ-2013.pdf)

## 来源登记与访问范围

Phase A 登记保留原样。TSV 使用 UTF-8、首行英文列名、制表符分隔，空字段表示无对应字段。id 与 record_kind 标示新增或历史 ID 的 erratum；title、authors_or_org、year_or_version 是书目；doi_or_identity 是 DOI 或输入哈希；original_url、checked_text_or_data、immutable_source 分别保存原址、实际替代正文和代码树；access_date_utc、access_level 区分检索结果与材料；supports、limits 用于主张反向核验。S0029 的 DOI 经 Crossref 和论文元数据确认，作者和访问记录没有回改。S0001 的其他镜像只作为佐证，未增加为不同作品。新来源是按竞争风险、序贯可选停止、已发表数据的具体缺口发现。没有转载原文或第三方数据。
