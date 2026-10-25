# 可复原性：这套环境的唯一硬标准

> CSV、Excel、JSON 都只是载体。真正的标准只有一句：
>
> **给你一个 run，能不能在另一台机器上复原出同一个仿真环境，得到同一组结果？**

如果答案是“能”，这个环境就是可复现的；如果答案是“要看当时那台机器”，那它只是一个脚本集合。

## 1. 需要复原什么

一个完整的仿真环境，至少包含下面这些层：

| 层 | 需要什么 | 为什么 |
|---|---|---|
| 配置 | design、netlist、simulator、analysis、PVT、params、measures、outputs | 唯一输入 |
| 电路 | netlist、testbench、include、subckt | 电路事实 |
| 工艺 | PDK、model、corner、version、hash | 器件真值 |
| 仿真器 | Spectre / ALPS / XA / ngspice、version、adapter | 执行引擎 |
| 代码 | 生成/解析脚本、commit hash | 生成逻辑 |
| 环境 | env vars、license、queue、并发、超时 | 可运行性 |
| 随机性 | seed、Monte Carlo 设置 | 可重复性 |
| 测量 | measure 定义、单位、条件、version | 指标含义 |
| 计划 | config_sha256、plan_sha256、run ids | 防漂移 |
| 结果 | metrics.json、summary.xlsx、raw、log、archive | 结果核对 |

少一层，复原就会变成“差不多”。

## 2. 可复原性的四个等级

| 等级 | 能复原什么 | 典型状态 |
|---|---|---|
| L0 | 只有 config | 知道“想跑什么”，但跑不起来 |
| L1 | config + netlist | 能在本地手工跑，但命令靠人 |
| L2 | + simulator/model/version | 换机器可能能跑，但结果不一定一致 |
| L3 | + scripts/env/seeds/measure contract | 能重放，结果可核对 |
| L4 | + archive/hash/log | 能审计、能对比、能交接 |

本仓库的目标是 **L3–L4 的接口设计**；实际实现还在路线图里。

## 3. CSV、Excel、JSON 怎么选

格式不重要，**单一事实源**重要。

- **CSV**：机器友好、diff 友好、适合版本控制；缺点是列多时人不好看。
- **Excel**：人友好、适合 PVT/参数矩阵和评审；缺点是公式、隐藏 sheet、手改容易漂移。
- **JSON**：机器友好、schema 友好、适合 plan 快照；缺点是人不想手写。

推荐两种模式，二选一，不要双维护：

1. **CSV/Excel 为源**：人编辑表格 → normalize 成 `config.json` + hash → plan/run 只认 snapshot。
2. **JSON 为源**：人用表格工具编辑 JSON 的导出视图 → JSON 是 canonical → CSV/Excel 只是导出/评审视图。

关键是：**同一个 run 只能有一个 canonical hash。** 如果 CSV 和 JSON 都能改，迟早会分叉。

## 4. 可复原性测试

给出一个 run archive，按下面步骤验收：

1. 在一台干净的机器上 checkout 同一个 commit；
2. 按 archive 恢复 config、netlist、PDK/model、simulator/adapter；
3. 跑 `plan`，得到与 archive 相同的 `config_sha256` / `plan_sha256`；
4. 跑 `run`，得到与 archive 相同的 metrics（在容差内）；
5. 对比 log、退出码、raw 文件哈希；
6. 如果任何一步不同，记录差异和原因。

这个测试不需要“完全相同的机器”，但需要**明确哪些差异是允许的**（例如浮点末位、license 排队时间），哪些是不允许的（例如 corner 不同、measure 定义不同）。

## 5. 什么会破坏可复原性

- 只在聊天里存在的“上次好像用的是 ss/125C”；
- 只在某台机器上的环境变量、license、wrapper；
- PDK/model 升级了但 archive 没记版本；
- Excel 里手改了单元格但没有 diff/hash；
- measure 定义悄悄改了，Excel 数字看起来“进步”了；
- seed 没记，Monte Carlo 每次不同；
- AI 持有隐藏状态，换一个会话就“跑偏”。

这些都不是“模型不够聪明”，而是**环境没有被固化**。

## 6. 和 ASST / AnalogLoop 的关系

- ASST 负责把 config 变成可复原的 run：validate → plan → run → collect → summarize → archive；
- AnalogLoop 负责把 run 变成可审计的 case：execution 字段、budget、promotion、ledger；
- 两者共同的前提是：**config 是单一事实源，run 引用 snapshot，不接受中途改配置。**

详见 [asst-and-execution.md](asst-and-execution.md) 和 [architecture.md](architecture.md)。

## 7. 这个仓库现在有什么

已有：

- ASST 的 config / plan / run / collect 接口；
- `execution` case 字段（config/plan/summary/archive 哈希）；
- case 账本与重放协议；
- 角色 manifest、面积报告、评测协议。

还没有：

- 可运行的 mock 闭环；
- 真实 ASST adapter；
- 真实 layout/PEX 校准；
- 外部复现记录。

所以 v1.0.0 是**架构笔记冻结版**，不是“可复原性已经实证”的版本。两者要分开写。

## 8. 一句话

**能复原，才算可复现；能复现，才配叫一个环境。** 格式可以是 CSV、Excel 或 JSON；不能少的，是 config、版本、脚本、measure 和 archive。
