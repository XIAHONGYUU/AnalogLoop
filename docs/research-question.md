# 研究问题与范围

## 背景

模拟/混合信号电路的 sizing 仍然高度依赖专家直觉和“改一版、跑一次、看波形”的循环。一次 SPICE 仿真的成本取决于分析类型：DC/AC 可能秒级，瞬态、PVT、蒙特卡洛可能是分钟到小时。

LLM agent 可以把“改什么、为什么改”自动化，但如果每次决策都调用 SPICE，内环速度仍然被仿真器锁死。另一方面，代理模型（surrogate）在器件建模和电路性能预测上已经相当成熟：

- **gm/ID 表**把器件偏置压到归一化坐标，跨 PDK 可移植，且可解释；
- **table-based device model** 用查表和插值替代解析模型；
- **神经 compact model** 用网络拟合 I-V/C-V，并可嵌入 SPICE；
- **电路级代理**直接从 sizing 预测性能，速度最快，但泛化最窄。

这些工作通常把代理模型当作独立研究对象，很少回答 agent 闭环里的两个工程问题：

1. 什么时候可以相信代理？
2. 代理错了，谁来兜底？

## 核心问题

**Q1（安全）** 在固定拓扑、pre-layout 的 sizing 中，代理模型能否承担 80–95% 的候选评估，同时把“代理说 pass、SPICE 说 fail”的误接受率控制在 0.5% 以下？

**Q2（路线）** gm/ID 表与学习型 PDK 数据库的边界在哪里？它们分别适合什么阶段、什么指标、什么 PDK？能否组合成“gm/ID 特征 + 学习型残差”的混合路线？

**Q3（预算）** 在总仿真预算固定时，快/慢路径、探索/确认、角落覆盖之间如何分配，才能最小化 simulations-to-spec，而不是最小化平均误差？

**Q4（可复现）** 如何让每条决策可重放、可审计，并把失败案例变成可复用的负知识？

**Q5（语义）** 如何让 AI 可靠地识别和修改网表？在设计侧显式声明器件角色（输入对、电流镜、cascode、dummy、使能/ADJ 开关、输出级），并用 manifest + validator 约束修改，能否降低非法编辑、提高修复准确率？

**Q6（面积）** 在固定拓扑、pre-layout 阶段，角色感知的面积模型能否给出可信的 low / nominal / high 区间，并把面积作为约束进入 sizing，而不是事后统计？

**Q7（执行）** 如何把 Spectre/ALPS/XA 的 CLI 固化成 AI/人/脚本都能用的接口，使 AI 只发意图、脚本保证可复现、人保留配置与签核？

## 范围

**做：**

- 固定拓扑、pre-layout 的 sizing / bias 优化；
- PVT 角落与蒙特卡洛的抽样策略；
- 两层验证：快速代理 + 真实 SPICE；
- 工具契约、预算账本、case 账本与重放；
- 语义网表：角色 manifest、校验器、角色级补丁；
- 面积估计与 layout handoff（floorplan intent、layout delta）；
- 开源 PDK 上的可复现实验。

**不做：**

- 拓扑生成、电路创新；
- 版图、DRC/LVS、寄生提取；
- 流片、silicon correlation；
- 商业 PDK / NDA 数据的处理与发布。

## 六个可证伪假设

**H1（契约）** 引入 typed tool contract 与仿真前检查，能显著降低非法仿真占比和无效重试。

**H2（预算）** 预算感知的策略（LLM 选策略 + BO 做数值 + 代理做筛选）比固定预算的纯 BO 有更低的 simulations-to-spec。

**H3（记忆）** append-only case ledger + 失败原因，能带来可测量的 warm-start 收益，并支持确定性重放。

**H4（语义）** 与“只有命名约定”相比，角色 manifest + validator + 角色级工具能降低非法编辑率，并减少修复所需的 SPICE 次数。

**H5（面积）** 与“只看 W·L”相比，角色感知的面积模型能更早识别面积超限，减少后期 layout 返工和面积 surprise。

**H6（执行）** 与 AI 直接拼 CLI 相比，ASST 风格的执行适配层能降低无效调用率，并提高重放/对比的一致性。

六个假设分别对应六份可交付物：

- `spec/tool-contract.yaml`
- `docs/budget-and-convergence.md`
- `docs/memory-and-replay.md`
- `spec/device-roles.yaml` + `spec/netlist-manifest.schema.json`
- `docs/area-and-layout.md` + `estimate_area` 工具
- `docs/asst-and-execution.md` + `plan/run/collect_simulation_*` 工具

即使 H2 被证伪，仓库仍然有价值：它给出了一个诚实的实验记录和一套可复用的契约。

## 成功标准

以下都是**目标**，不是当前结果：

- 相对固定预算 BO，simulations-to-spec 降低 ≥ 30%；
- 代理误接受率 ≤ 0.5%，且在边界 10% 的样本上单独报告；
- 给定账本，重放得到相同的决策链（哈希一致）；
- 在两种 open PDK 上跑通同一套契约；
- 非法编辑率（匹配/比例/开关）显著低于“只有名字”的基线；
- 面积估计的 median/p95 误差、rank correlation 可报告；
- 无效 CLI 调用率与重放一致率可报告；
- 所有结论都能追溯到 case 记录或公开引用。

## 证据状态

- **已核实**：文中引用的论文/项目标题、链接、以及它们公开摘要中的数字。
- **作者推导**：架构、预算模型、晋级门、角色词表、指标容差建议。
- **待验证**：95% 目标、30% 降幅、0.5% 误接受率、跨 PDK 可移植性、H4 的非法编辑率收益、H5 的面积估计收益、H6 的执行层收益。

详见 [evidence-boundaries.md](evidence-boundaries.md)。