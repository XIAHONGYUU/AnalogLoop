# 路线图

## 原则

- 每一阶段都有**可验收的产物**，不是“继续完善”；
- 先做可复现的 mock，再接真实仿真器；
- 先做安全门，再追求覆盖率；
- 每一阶段都保留失败记录；
- 文档版本与 contract/schema 版本分开：release 可以冻结，schema 仍可独立演进。

## 阶段

| 阶段 | 产物 | 验收标准 | 状态 |
|---|---|---|---|
| v1.0.0 架构笔记冻结 | README、docs、7 张图、工具契约、case schema、role manifest、area model、ASST 执行层、可复原性检查表 | 链接可解析、schema 可加载、角色校验通过、图可重建、release tag | **当前，已冻结** |
| v1.1 mock 闭环 | Python 包、mock 仿真器、预算账本、角色/面积/config 校验、重放、CI | 给定种子，重放决策链一致；预算不超；中途改 config 被拒绝 | 计划 |
| v1.2 真实 SPICE | ngspice + Sky130 两级运放、roles/manifest、测量契约、基线 | 5 个种子跑通；报告 simulations-to-spec | 计划 |
| v1.3 快速代理 | gm/ID 表 + 电路级 GP、晋级门、校准、面积校准 | 报告 FAR、覆盖率、加速比、面积误差 | 计划 |
| v2.0 可复用规范 + 报告 | 第二 PDK、Quarto/Pages 报告、外部复现 | 两种 PDK 跑通；外部复现；公开页面 | 计划 |

## v1.0.0（当前，冻结）

已完成：

- 五段架构 + 两层验证 + 预算控制器的文字与图；
- 语义网表：18 个角色、manifest schema、示例 netlist/roles、validator；
- 面积：角色感知模型、三值 area gate、layout handoff 文档与图；
- ASST 执行层：config → plan → run → collect → summarize 的接口与图；
- 单一 config 事实源与可复原性检查表；
- 工具契约 22 个、case 记录 schema、评测协议、证据边界；
- 7 张原创图、CI、LICENSE/CITATION/CHANGELOG。

未包含：

- 可运行代码、mock 闭环；
- 真实 ASST adapter、ngspice demo；
- 代理模型、真实 layout/PEX 校准；
- 流片、外部复现。

## v1.1：mock 闭环

目标：在不接仿真器的情况下，验证**预算、晋级门、账本、重放、角色校验、面积门、config SSOT**。

产物：

- `analogloop/` Python 包；
- `analogloop.mock`：可配置的假仿真器（带噪声、角落、失败模式）；
- `analogloop.budget`：预算账本与控制器；
- `analogloop.gate`：晋级门；
- `analogloop.roles`：角色 manifest 解析与校验；
- `analogloop.area`：预布局面积估计（core / ring / routing / dummy / periphery）；
- `analogloop.asst`：ASST 风格的 plan/run/collect 适配层（mock 后端），以单一 config 为 SSOT；
- `analogloop.ledger`：append-only JSONL + 哈希链；
- `analogloop.replay`：重放；
- 测试与 CI。

验收：

- 给定种子，重放得到相同决策链；
- 预算耗尽时必定停机；
- 篡改账本会被哈希链检测；
- 角色违规（匹配、比例、开关）在仿真前被拒绝；
- 面积超限在仿真前被 area gate 拒绝；
- run 中途改 config 会被拒绝，必须生成新 snapshot/plan；
- 单元测试覆盖预算、门、角色、面积、config、账本。

## v1.2：真实 SPICE

目标：跑通一个真实的两级运放 sizing。

产物：

- Sky130 两级运放 netlist、roles.yaml、config 与测试台；
- 测量脚本（Gain、UGB、PM、Power）；
- 三条基线（random、grid、DoE+BO）；
- 报告模板与结果表。

验收：

- 5 个种子跑通；
- 角色 manifest 通过校验；
- 面积报告包含 low/nominal/high 与 by_role；
- ASST config/plan/metrics/summary 可追溯；
- 每个指标可追溯到 raw 文件与哈希；
- 报告包含失败案例与删失样本；
- 重放最优 case 一致。

## v1.3：快速代理

目标：验证“两层验证”是否真的省仿真，且安全。

产物：

- gm/ID 表（Sky130）；
- 电路级 GP/NN 代理；
- 晋级门 + 校准环；
- FAR / 覆盖率 / 加速比 / 面积误差报告。

验收：

- 在 0.5% FAR 约束下，快路径覆盖 ≥ 80%；
- 相对全 SPICE，wall-clock 加速 ≥ 5×；
- 边界 10% 带的 FAR 单独报告；
- 代理版本与训练集哈希可追溯；
- 面积模型与 rule pack 版本可追溯，报告估计误差与 rank correlation。

## v2.0：可复用规范 + 报告

- 第二 PDK（GF180 或 IHP）；
- Quarto/Reveal.js 或静态 HTML 报告；
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
| Excel/JSON 双维护 | config 分叉 | 单一 canonical hash；另一格式只导出 |

## 下一步

v1.0.0 已经冻结。下一步是 **v1.1 mock 闭环**：它不需要仿真器，却能验证预算、门、角色、面积、config SSOT 和重放六条逻辑；这是投入最小、信息量最大的一步。
