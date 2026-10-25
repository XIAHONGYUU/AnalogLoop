# 路线图

## 原则

- 每一阶段都有**可验收的产物**，不是“继续完善”；
- 先做可复现的 mock，再接真实仿真器；
- 先做安全门，再追求覆盖率；
- 每一阶段都保留失败记录。

## 阶段

| 阶段 | 产物 | 验收标准 | 状态 |
|---|---|---|---|
| v0.1 架构笔记 | README、docs、6 张图、工具契约、case schema、netlist role manifest、area model、评测协议 | 链接可解析、schema 可加载、角色校验通过、图可重建 | 当前 |
| v0.2 mock 闭环 | Python 包、mock 仿真器、预算账本、重放脚本、CI | 给定种子，重放决策链一致；预算不超 | 计划 |
| v0.3 真实 SPICE | ngspice + Sky130 两级运放、测量契约、基线 | 5 个种子跑通；报告 simulations-to-spec | 计划 |
| v0.4 快速代理 | gm/ID 表 + 电路级 GP、晋级门、校准 | 报告 FAR、覆盖率、加速比 | 计划 |
| v0.5 报告页 | Quarto/Pages、图表、复现实验说明 | 公开页面可访问；图与数据可下载 | 计划 |
| v1.0 可复用规范 | 第二 PDK、社区评审、稳定 schema | 两种 PDK 跑通；外部复现 | 计划 |

## v0.1（当前）

已完成：

- 五段架构 + 两层验证 + 预算控制器的文字与图；
- MCU 类比；
- gm/ID 与学习型 PDK 数据库的对比；
- 工具契约 YAML；
- case 记录 JSON Schema；
- 语义网表：角色词表、manifest schema、示例 netlist/roles、validator；
- 面积：角色感知模型、三值 area gate、layout handoff 文档与图；
- 评测协议；
- 证据边界。

未完成：

- 可运行代码；
- 真实仿真；
- 代理模型；
- 公开页面。

## v0.2：mock 闭环

目标：在不接仿真器的情况下，验证**预算、晋级门、账本、重放、角色校验**五条逻辑。

产物：

- `analogloop/` Python 包；
- `analogloop.mock`：一个可配置的假仿真器（带噪声、角落、失败模式）；
- `analogloop.budget`：预算账本与控制器；
- `analogloop.gate`：晋级门；
- `analogloop.roles`：角色 manifest 解析与校验；
- `analogloop.area`：预布局面积估计（core / ring / routing / dummy / periphery）；
- `analogloop.layout_intent`：floorplan intent 与 layout delta 的接口；
- `analogloop.ledger`：append-only JSONL + 哈希链；
- `analogloop.replay`：重放；
- 测试与 CI。

验收：

- 给定种子，重放得到相同决策链；
- 预算耗尽时必定停机；
- 篡改账本会被哈希链检测；
- 角色违规（匹配、比例、开关）在仿真前被拒绝；
- 面积超限在仿真前被 area gate 拒绝；
- 单元测试覆盖预算、门、角色、账本。

## v0.3：真实 SPICE

目标：跑通一个真实的两级运放 sizing。

产物：

- Sky130 两级运放 netlist、roles.yaml 与测试台；
- 测量脚本（Gain、UGB、PM、Power）；
- 三条基线（random、grid、DoE+BO）；
- 报告模板与结果表。

验收：

- 5 个种子跑通；
- 角色 manifest 通过校验；
- 面积报告包含 low/nominal/high 与 by_role；
- 每个指标可追溯到 raw 文件与哈希；
- 报告包含失败案例与删失样本；
- 重放最优 case 一致。

## v0.4：快速代理

目标：验证“两层验证”是否真的省仿真，且安全。

产物：

- gm/ID 表（Sky130）；
- 电路级 GP/NN 代理；
- 晋级门 + 校准环；
- FAR / 覆盖率 / 加速比报告。

验收：

- 在 0.5% FAR 约束下，快路径覆盖 ≥ 80%；
- 相对全 SPICE，wall-clock 加速 ≥ 5×；
- 边界 10% 带的 FAR 单独报告；
- 代理版本与训练集哈希可追溯；
- 面积模型与 rule pack 版本可追溯，报告估计误差与 rank correlation。

## v0.5：报告页

- Quarto/Reveal.js 或静态 HTML；
- 图、表、复现命令；
- 与 README 一致的叙事；
- 通过 GitHub Pages 发布。

## v1.0：可复用规范

- 第二 PDK（GF180 或 IHP）；
- schema 稳定；
- 外部复现；
- 社区评审与贡献指南。

## 风险

| 风险 | 影响 | 缓解 |
|---|---|---|
| 代理精度不够 | 覆盖率上不去 | 先做 L0 + 小范围 L2；接受更低的 r |
| SPICE 不收敛 | 数据缺口 | 预检 + 重试策略 + 失败案例 |
| PDK 许可 | 不能公开数据 | 只用 open PDK；商业 PDK 只报方法 |
| 评测过拟合 | 结论不可信 | 固定测试集、多种子、反作弊 |
| 范围膨胀 | 做不完 | 固定拓扑、pre-layout、先两级运放 |
| LLM 不稳定 | 重放困难 | 记录原始输出 + 工具契约 |

## 下一步

如果 v0.1 通过评审，下一步是 v0.2 的 mock 闭环。它不需要仿真器，却能验证整个控制逻辑；这是投入最小、信息量最大的一步。