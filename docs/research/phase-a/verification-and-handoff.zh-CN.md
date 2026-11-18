# Phase A 自审、复核与移交

[研究导航](README.zh-CN.md) · [源登记](source-register.tsv) · [搜索记录](search-log.md) · [逐项交叉表](ledger-crosswalk.zh-CN.md) · [剩余问题](new-questions-and-gaps.zh-CN.md)

## 固定证据和交付地图

本次从 GitHub 当前 main `2cf68294a6a420d77c7fd1016157fdeb9a65d8a5`、干净任务起点 `f626c9d374c41e7e551fc6bc3d215aa7048604ae`、Stable `v1.1.0` 指向 `46ff21847c5522eb983d3f58e396354461a64f34` 树开始，三者的关系见导航页。受认证的两份当前私有治理正文仅在会话内读取；本目录无私有治理内容。公开证据使用 AGENTS、CONTRIBUTING、README、ORIGIN_AND_SCOPE、ARCHITECTURE、API、BEHAVIOR_SPEC、NUMERICAL_CONTRACT、COMPATIBILITY、PROVENANCE、TESTING、四份中文源码指南、永久账本、历史证据研究、两份 Preview 说明、脚本与结果、公共头、C 源码、断言、oracle 及调用方参考。核对 Issues #1、#5、#6、#8、#9、#10 的正文与评论接口（各 0 条评论）。#1 控制当前产品身份；#5 是表示边界，#6 是环境复核，#8 是延期，#9/#10 区分借用与可比性。

| 活动 | 已形成的材料 |
|---|---|
| A1 | 导航页的现状/源/验证/前提表与逐项交叉表，固定 48 项和 4 个历史修复 |
| A2 | [方法](methods-and-assumptions.zh-CN.md)中的目标、假设、限制和比较 |
| A3/A4/A5 | [应用与软件](real-world-and-software.zh-CN.md)中的 12 个应用族、12 个源码树及现场与讨论的反例 |
| A6 | 四次[发现/追查/缺口/对抗](search-log.md)，用[登记](source-register.tsv)保存检查级别和不可取得材料 |
| A7 | [交叉表](ledger-crosswalk.zh-CN.md)与[七项临时问题](new-questions-and-gaps.zh-CN.md) |
| A8 | 本文件的证据检查、重算、范围及自审边界 |

## 来源质量和 TSV 模式

96 个唯一记录按主要用途分为学术 45、官方/指导 15、软件 12、实地/经验 14、社区/实践讨论 10。计数互斥，例如学术期刊的应用研究按主要用途记 field；机构指导和工程手册归 official。未把同作品的镜像、作者稿或版本当成不同来源号；未验证的候选排除，因此编号允许有缺口。

证据读取级别为全文相关段落 32、摘要或公开段落 16、官方正文或文档 14、代码/配置及可取测试 12、讨论正文及可见回复 10、书目或独立佐证 6、案例正文相关结果 5、机构报告网页摘录 1。全文可读代表核对相关方法或结果段，而不是系统逐行审读每篇论文。类别、同行评审与可访问性独立。撤稿状态没有做全面数据库核验。

`source-register.tsv` 使用 UTF-8、首行字段、制表符分隔、双引号按 CSV 规则包裹、换行结束。空字段表示无该项/无可确认值，空格分隔多值代码链接和 ID 列表。列名与语义如下。

| 字段 | 内容 |
|---|---|
| `id, category, year_or_date, version, authors_or_org, title` | 稳定 ID、主用途类别、日期或年、版本、作者或组织、原标题 |
| `original_url, official_doi_url, doi, open_url, immutable_code_urls` | 检索到的原址、解析 DOI、原 DOI、开放替代、固定 Git 文件路径 |
| `availability, inspected, evidence_type, publication_status` | 访问路径和返回、实际阅读范围、证据类型、出版或版本状态 |
| `ledger_ids, supports, limitations, related_ids` | 相关账本、能支持的陈述、不能延伸的主张、核对/条件不同的其他来源 |
| `reproducibility, license, accessed_utc` | 复算或静态检查、已检查软件许可、UTC 日期 |

## 链接、争议与反向核对

- 对源登记的原址与可用替代用 `curl -sSL --max-time 18 ... -w '%{http_code} %{url_effective}'` 记录状态及终址，对 HTTP 200 再检查正文、标题或内容类型。84 个非软件原址的直接 HTTP 探测得到 45 个 200、25 个 403、3 个 202、6 个 203、5 个传输未完成。另试替代网址、DOI 与书目；200 仍可能是通行检查页。Papers、官方 PDF、代码 raw 与 GitHub API 分别检查；Crossref 核对期刊标题、版本、作者、年份和 DOI，Web 打开和出版社摘要补充被阻断原网址。代码通过 GitHub commit API 获取可复验树，再取该树的具体文件。
- 真正无法确认论文正文的例子有 Fine–Gray、Simpson、DiDonato–Morris、原始 Brier、Cox 和 GLM。它们的归属和书目可查，相关陈述同时使用其他来源或可直接导出的公式。R 的 bratio 代码用于算法路径旁证。Scholar PDF 只见摘要、扫描失败或只有索引时保留低等级。SSRN 源的 PDF 下载重定向为摘要，只给文稿覆盖。存在 403 的开放文档也不能保证另一网络同状态。 [S0015](https://doi.org/10.1080/01621459.1999.10474144) · [S0026](https://doi.org/10.1145/131766.131776) · [S0050](https://dlmf.nist.gov/8.17)
- 独立回查 flu 例的两个 WIS 排名，医疗例的 .63 AUC、67% 漏识别和 18% 报警，CDC 的时点/版本，确认比较对象和样本口径。没有把跨场景的验证解释为普适成功率。中文天气案例中英文摘要起始月不一致，已显式保留。 [S0034](https://www.nature.com/articles/s41467-024-50601-9) · [S0023](https://pmc.ncbi.nlm.nih.gov/articles/PMC8218233/) · [S0043](https://html.rhhz.net/yyqxxb/html/20020103.htm)
- 重新检查强结论的反例。MAP 混合的目标无观察时后验权等于先验。加权 conformal 与条件不可行定理分别讨论边际和条件对象。S3 外部推测与 AWS 操作记录提供不同根因证据。SciPy Beta-prime 与 Boost 非中心 F 报告为数值失败线索，未当作相同分布复现。 [S0006](https://doi.org/10.1111/biom.12242) · [S0010](https://www.stat.berkeley.edu/~ryantibs/papers/limits.pdf) · [S0011](https://proceedings.neurips.cc/paper/2019/hash/8fb21ee7a2207526da55a679f0332de2-Abstract.html) · [S0039](https://aws.amazon.com/message/41926/) · [S0077](https://www.thousandeyes.com/blog/aws-s3-outage-likely-caused-by-internal-network-issue)

## 实际验证和复算

- `git ls-remote origin refs/heads/main refs/heads/docs/phase-a-research-brief 'refs/tags/v1.1.0*'`、`git rev-parse 'v1.1.0^{tree}'`、`git diff --exit-code v1.1.0 origin/main` 核对 refs、树及 main 与 Stable 内容相同。查询 GitHub 仓库、Release 和精确历史 CI 元数据。R04 历史 run 39358543092 为 `fdfaddfb58486004ee1cc02c0f4a5c640cd17c7c` 的成功 push，归属于 v1.0.0 的证据；R01–R03 用 `git show --stat` 检查提交差异及修复归因。
- `python /tmp/phasea/check.py` 核对八个文件、全部 Markdown 本地链接和片段、源 ID 与 TSV 严格切分、DOI/URL 唯一、固定代码链接形状。对账本 52 个标题与状态逐项自动相等检查，R 项保留历史状态。执行 `git diff --cached --check` 和路径范围检查；任务起点之外只加入当前目录八个文件。main 到任务起点已有的简报本身会显示在 PR 中。
- 系统未预装 CMake，使用 `python -m venv /tmp/phasea/build-tools`，在该临时环境安装 CMake 3.31.6。Linux x86_64 / GCC 14.2.0 / Python 3.12.14 上对任务起点的相同源码（含本目录文档草稿）实际运行以下命令。根 CTest 14/14，通过安装前缀构建的独立消费者 1/1。未运行第三方测试、可选设备集成或跨架构测试；冻结参考重算仍按各历史报告的环境限定。
- 命令从仓库根执行，CMake 和 CTest 使用上述临时环境的可执行文件。

```sh
cmake -S . -B /tmp/phasea/build -DPROBSPAN_BUILD_EXAMPLES=ON -DCMAKE_BUILD_TYPE=Release
cmake --build /tmp/phasea/build --parallel 4
ctest --test-dir /tmp/phasea/build --output-on-failure
cmake --install /tmp/phasea/build --prefix /tmp/phasea/install
cmake -S tests/consumer -B /tmp/phasea/consumer -DCMAKE_PREFIX_PATH=/tmp/phasea/install
cmake --build /tmp/phasea/consumer
ctest --test-dir /tmp/phasea/consumer --output-on-failure
```

- 实测的标准库复算输出为 `P0=0.817906937597 exact_upper=0.139108340668 wald=0.182050441475 wilson=0.983140662364`。公式重算和有限枚举不构成外部病例或借用设计的复现。 [S0001](https://doi.org/10.1214/ss/1009213286) · [S0002](https://www.jhanley.biostat.mcgill.ca/c607/ch08/wilson_jasa_1927.pdf) · [S0003](https://jhanley.biostat.mcgill.ca/Reprints/If_Nothing_Goes_1983.pdf)

```python
import math

n, p, z = 20, 0.01, 1.959963984540054
wald, wilson = 0.0, 0.0
for k in range(n + 1):
    q = k / n
    w = math.comb(n, k) * p**k * (1 - p)**(n - k)
    h = z * math.sqrt(q * (1 - q) / n)
    wald += w * (q - h <= p <= q + h)
    m = (q + z*z/(2*n)) / (1 + z*z/n)
    h = z * math.sqrt(q*(1-q)/n + z*z/(4*n*n)) / (1 + z*z/n)
    wilson += w * (m - h <= p <= m + h)
print((1 - p)**n, -math.expm1(math.log(0.05)/n), wald, wilson)
```

## 独立复核重点

优先打开来源段落并比对其实际数据、假设、估计对象与引用语义；包括没有目标标签的先验冲突、真值版本 切换、截尾造成的进入风险集差异、Binomial 参数和未来计数预测、以及 binary64 邻点夹逼。源条目涉及多领域，核查其能否支持真实设备适用性或只提供研究对照。独立复核应从固定 HEAD 检查八文件、PR 范围、状态映射和来源等级。尚缺真实设备外部效度、完整的行业原始数据重跑及更多平台数值验证。当前为提交者自审，独立接受留待评审。
