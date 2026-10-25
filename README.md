# AnalogLoop

**以仿真预算为中心、可复现的模拟电路设计 Agent 架构**  
*A two-speed, budget-aware agent architecture for analog circuit sizing.*

> 状态：v0.1 架构构想（design note）。不是已完成的系统，没有流片验证，也不主张 SOTA。  
> 这份仓库首先是一份设计思路，其次才是一份可执行的规范。

![AnalogLoop architecture](diagrams/png/architecture.png)

## 一句话

让 LLM 只做它擅长的事——选策略、读失败、决定何时停；让确定性工具链做执行，让代理模型承担大部分快速迭代，让真实 SPICE 守住最后一道签核。

## 为什么需要“两层验证”

模拟电路设计的真正瓶颈不是 token，而是**仿真次数**。一次 DC/AC 仿真可能几秒，瞬态、PVT、蒙特卡洛可能是分钟到小时。LLM agent 如果把每次“想一想”都变成一次 SPICE，迭代速度不会比人快多少。

但直接用代理模型替换 SPICE 也不安全：

- 95% 的平均精度，可能意味着在 spec 边界上 10% 的误接受；
- 代理模型只在训练分布内可信，拓扑、角落、偏置一换就可能失效；
- 相位裕度、启动、失真、失配这些指标，靠近边界时往往是非线性的。

所以这里采用**两种速度**：

| 路径 | 角色 | 典型成本 | 何时使用 |
|---|---|---|---|
| 快速代理 | 探索、排序、筛选 | ms–s | 大多数候选 |
| 真实 SPICE | 签核、边界、抽样复核 | s–min | 少量关键候选 |

中间由一个显式的**晋级门**（promotion gate）决定走哪条路。门看四件事：不确定度、到 spec 的裕量、是否在信任域内、以及这条 case 的关键程度。

> 核心立场：**代理模型是仿真器的 cache，不是仿真器的替代品。** 95% 是预算，不是承诺。

## 架构

五个模块、两条回路、一个横切控制器：

1. **目标与约束**：设计目标、约束、参数空间、PVT 角落，以及一个可行性预检。
2. **策略层（LLM）**：理解目标、选择搜索策略、诊断失败、决定何时停；**不做数值计算，不持有数值状态**。
3. **工具链（确定性）**：渲染 deck / 测试台、DoE/BO、调用代理、测量、写账本；只暴露白名单工具。
4. **验证层（两种速度）**：4a 快速代理；4b 真实 SPICE；中间是晋级门。
5. **记忆与知识**：case 账本、技能/规则、代理模型、负知识；支持重放。

两条回路：

- **内环**：单条 case 的“提出 → 评估 → 修正”。
- **外环**：用历史结果修正目标、约束和策略。

横切的**预算与晋级控制器**负责：每条 case 的仿真预算、快慢路径比例、晋级阈值、停机条件。

更完整的说明见 [docs/architecture.md](docs/architecture.md)。

## 三条设计原则

1. **无状态的大脑，有状态的实验台。** LLM 不记住“上次跑到第几个点”；所有数值、版本、候选都在账本里。
2. **仿真预算是一等公民。** 每个决策都要能回答：这次评估花多少、预期换回多少信息、什么时候停止。
3. **一切可重放。** 网表、模型、种子、工具版本、代理版本都有哈希；给定账本，可以重放出一条相同的决策链。

## 两条快速验证路线

| | A. gm/ID 表 | B. 学习型 PDK 数据库 |
|---|---|---|
| 本质 | 物理启发的低维中间表示 | 器件/电路级代理模型 |
| 数据 | DC 扫描得到的 gm/ID、fT、gm/gds、Id/W | I-V、C-V、噪声、失配、寄生 |
| 优点 | 可移植、可解释、数据小 | 快、可微、可覆盖高维空间 |
| 缺点 | 仍需 SPICE 提取；二阶效应/失配有限 | 需要训练数据；分布外风险；角落覆盖难 |
| 适合 | 跨 PDK 的早期 sizing | 固定 PDK 内的大量候选筛选 |

两者不是互斥的。更现实的组合是：**用 gm/ID 做特征与约束，用学习型代理做快速打分，用 SPICE 做签核。** 详见 [docs/gm-id-and-pdk-database.md](docs/gm-id-and-pdk-database.md)。

## 95% 怎么定义

不要用一个“全局准确率”验收代理。至少拆成四个指标：

- **精度**：逐指标 |Δ| ≤ 5%（Gain、UGB、PM、Power、Noise、Offset 各自不同）；
- **工作量**：80–95% 的候选走快路径；
- **安全**：误接受率（代理说 pass、SPICE 说 fail）≤ 0.5%；
- **覆盖**：95% 的角落/工况落在信任域内。

其中**误接受率**比平均误差重要。一个平均误差 2%、但在边界上经常误接受的代理，不能用于签核。详见 [docs/fast-verification.md](docs/fast-verification.md)。

## 与现有工作的关系

这个架构不是凭空出现的。2025–2026 年已经有一批非常接近的工作：

- [AnalogCoder-Pro](https://github.com/laiyao1/AnalogCoderPro)（TCAD 2026）把生成、波形诊断和 BO sizing 串起来；
- [AnalogAgent](https://github.com/TheWind-upBird/Analogagent)（KDD 2026）用多智能体和自演化记忆做跨任务迁移；
- [AnaFlow](https://arxiv.org/abs/2511.03697) 明确以 sample-efficient、explainable sizing 为目标；
- [SABLE](https://arxiv.org/abs/2607.03701)（TODAES 2026）在工业 NDA 约束下做闭环，并给出严格的 action contract 与停机条件；
- [SpiceMCP](https://github.com/oniondas/SpiceMCP) 把优化状态放在 server/SQLite，LLM 只出策略；
- [AutoCkt](https://github.com/BWRC-AMS-ML-Discovery/AutoCkt) 是 RL sizing 的仿真效率基线；
- [LASANA](https://arxiv.org/abs/2507.10748) 用 ML 代理替代模拟子块仿真，报告最高三个数量级加速、误差 < 7–8%。

**本仓库不主张一个新算法。** 它主张三件工程上的事：把预算账本显式化、把工具契约公开化、把失败知识一等公民化。完整的对照见 [docs/landscape.md](docs/landscape.md)。

## 仓库导航

| 文件 | 内容 |
|---|---|
| [docs/research-question.md](docs/research-question.md) | 问题、范围、三个可证伪假设 |
| [docs/architecture.md](docs/architecture.md) | 五段架构、两条回路、失败模式 |
| [docs/fast-verification.md](docs/fast-verification.md) | 两层验证、晋级门、95% 的度量 |
| [docs/gm-id-and-pdk-database.md](docs/gm-id-and-pdk-database.md) | gm/ID 与学习型 PDK 数据库 |
| [docs/mcu-analogy.md](docs/mcu-analogy.md) | ISA、中断、存储层次 |
| [docs/tool-contract.md](docs/tool-contract.md) | 工具白名单与调用契约 |
| [docs/budget-and-convergence.md](docs/budget-and-convergence.md) | 预算账本与停机条件 |
| [docs/memory-and-replay.md](docs/memory-and-replay.md) | case 账本、负知识、重放 |
| [docs/benchmark-protocol.md](docs/benchmark-protocol.md) | simulations-to-spec 怎么测 |
| [docs/landscape.md](docs/landscape.md) | 与现有工作的对照 |
| [docs/evidence-boundaries.md](docs/evidence-boundaries.md) | 哪些是事实、假设、未知 |
| [spec/tool-contract.yaml](spec/tool-contract.yaml) | 机器可读的工具契约 |
| [spec/case-record.schema.json](spec/case-record.schema.json) | case 账本 schema |

## 不是什么

- 不是已经完成的 EDA 产品；
- 不是“LLM 取代模拟设计师”；
- 不是拓扑生成或版图自动化；
- 不是流片验证过的结论；
- 不包含任何受 NDA 约束的 PDK 数据。

## 路线图

- **v0.1（当前）**：架构笔记、四张原创图、工具契约、评测协议。
- **v0.2**：mock 闭环（不接仿真器）+ 预算账本 + 重放脚本 + CI。
- **v0.3**：ngspice + Sky130 两级运放 demo，比较 grid / DoE+BO / LLM 策略。
- **v0.4**：快速代理 + 晋级门，报告误接受率。
- **v1.0**：Quarto/Pages 报告 + 可复现实验。

详见 [docs/roadmap.md](docs/roadmap.md)。

## 许可与引用

- 文档、图、文字：CC BY 4.0（[LICENSE](LICENSE)）。
- 代码与脚本：MIT（[LICENSE-CODE](LICENSE-CODE)）。
- 引用信息：[CITATION.cff](CITATION.cff)。

欢迎在 Discussions 里讨论，尤其是：你会在什么指标上接受 5% 的代理误差？你的“误接受”红线是多少？
