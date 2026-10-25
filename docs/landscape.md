# 相关工作地图

> 截止 2026-10。这个领域移动很快，表格是“阅读入口”，不是完整 survey。
> 论文数字来自公开摘要/README；未复现。

## 一张表

| 类别 | 工作 | 关键点 | 与本仓库的关系 |
|---|---|---|---|
| 生成 + 优化 agent | [AnalogCoder](https://github.com/laiyao1/AnalogCoder)（AAAI 2025） | training-free、代码生成、技能库 | 最近的邻居之一；偏拓扑生成 |
| 生成 + 优化 agent | [AnalogCoder-Pro](https://github.com/laiyao1/AnalogCoderPro)（TCAD 2026） | 多模态诊断、BO sizing、28 个电路 | 覆盖了本仓库的大部分框 |
| 多智能体 + 记忆 | [AnalogAgent](https://github.com/TheWind-upBird/Analogagent)（KDD 2026） | 自演化 playbook、跨任务迁移 | 记忆是主角；预算不是 |
| 样本高效 sizing | [AnaFlow](https://arxiv.org/abs/2511.03697)（2025-11） | 多智能体、自适应仿真策略、可解释 | 与“最少仿真”最贴 |
| 工业闭环 | [SABLE](https://arxiv.org/abs/2607.03701)（TODAES 2026） | NDA-safe、28 个 SKILL 白名单、6 个停机条件 | “契约 + 停机”的强参照 |
| 多智能体 sizing | [AgenticSizing](https://arxiv.org/abs/2609.25873)（2026-09） | 拓扑分解、知识复用、平均 83 次迭代 | 报迭代数，未统一预算协议 |
| VLM + BO | [VLM-CAD](https://arxiv.org/abs/2601.07315)（2026-01） | Image2Net、ExTuRBO | 多模态 + 代理优化 |
| 网表语义 | [GANA](http://ece.umn.edu/users/sachin/conf/date20.pdf)（DATE 2020） | GCN 自动标注功能块 | 自动推断路线；本仓库用声明 + 校验 |
| 网表语义 | [Analog-DB](https://arxiv.org/abs/2609.01286)（2026） | 功能子块/尺寸命名参数 + 匹配约束；agent-first | 最接近“语义层”，以数据库/DSL 为中心 |
| 网表语义 | [AMSnet-q](https://arxiv.org/abs/2605.01404)（2026） | 原理图→网表 + 自动功能标注 + 仿真验证 | 自动标注参照 |
| 布局 / 面积 | ALIGN / BAG / MAGICAL 等 | 网表/约束 → 版图；面积、匹配、对称是布局输入 | 布局阶段参照；本仓库只做 pre-layout 面积约束 |
| RL sizing | [AutoCkt](https://github.com/BWRC-AMS-ML-Discovery/AutoCkt)（DATE 2020） | ngspice、RL、仿真效率基线 | 经典基线 |
| 鲁棒 RL | [RoSE-Opt](https://arxiv.org/abs/2407.19150)（2024-07） | 知识注入 RL、鲁棒优化 | 优化器参照 |
| 代理仿真 | [LASANA](https://arxiv.org/abs/2507.10748)（MLCAD 2025） | ML 代理替代子块仿真；3 个数量级加速；误差 < 7–8% | “95% 量级”可行性的证据 |
| 表模型 | [Table-based Device Modeling](https://www2.eecs.berkeley.edu/Pubs/TechRpts/2018/EECS-2018-66.html)（Berkeley） | 查表 + 插值；平滑与导数问题 | 学习型数据库的前身 |
| 神经 compact model | SPICE-compatible NN compact model（IEEE） | 网络嵌入 SPICE | 器件级加速路线 |
| 混合代理 | Cyber Wolf（IEEE） | 异构图 + 多模态代理 | 电路级代理参照 |
| 开放合成 | Opera（DAC 2025） | 数据驱动、开放平台 | 数据/流程参照 |
| gm/ID 工具 | [Mosplot / gmid](https://github.com/medwatt/gmid) | lookup table、多角落 sizing、写网表验证 | 路线 A 的工程实现 |
| gm/ID 工具 | [pygmid](https://github.com/dreoilin/pygmid) | Murmann starter kit 的 Python 版 | 路线 A 的轻量实现 |
| Agent skill | [gmoverid-skill](https://github.com/Arcadia-1/gmoverid-skill) | gm/ID + Sky130 的 agent 封装 | “工具契约”的早期形态 |
| 状态归 server | [SpiceMCP](https://github.com/oniondas/SpiceMCP) | SQLite 保存优化状态；LLM 只出策略 | 与本仓库“无状态大脑”最接近 |
| 测量级工具 | [ltspice-mcp](https://github.com/Cognitohazard/ltspice-mcp) | 按名字返回 gm/gds/PM，不暴露 raw | 工具接口设计参照 |
| 评测基座 | [AnalogGym](https://github.com/CODA-Team/AnalogGym) | 开源模拟优化 benchmark | 评测候选 |
| 通用平台 | [LLM4AD](https://github.com/Optima-CityU/LLM4AD) | LLM 驱动算法设计 | 方法论参照 |
| 综述/列表 | [Awesome-LLM-Circuit-Agent](https://github.com/qhy991/Awesome-LLM-Circuit-Agent) | 数字/模拟 LLM 工作索引 | 持续跟踪入口 |

## 这个仓库站在哪里

### 已经被覆盖的

- 五段式 agent 架构（策略、工具、仿真、记忆）；
- 多智能体、自演化记忆、技能库；
- BO / RL / 代理模型做 sizing；
- gm/ID 表与开源 PDK 流程；
- 工具调用与 MCP 化；
- 网表功能块的自动标注（GANA、AMSnet-q、AgenticSizing）；
- 布局自动化与面积估计（ALIGN、BAG、MAGICAL 等）。

### 没有被充分覆盖的

1. **预算账本**：把“每次评估的成本”做成显式对象，并在策略层与控制器之间分配。
2. **公开的工具契约**：不是某个项目的内部 JSON，而是一份可复用的 spec + schema。
3. **误接受率**：代理工作通常报误差，很少报“代理说 pass、SPICE 说 fail”的比例。
4. **负知识**：记忆系统多存成功案例；失败原因很少被结构化。
5. **MCU 叙事**：没有看到用 MCU 分工来组织整个架构的公开项目。
6. **声明式、可校验、工具原生的角色层**：自动标注已有，但把角色作为设计师声明、用 sidecar + validator 约束 agent 修改，仍然少见。
7. **面积作为 sizing 闭环约束**：面积估计通常属于 layout 阶段；把它做成角色感知、带区间、进入 Pareto 的闭环约束，仍然少见。

### 本仓库的增量

不是新算法，而是：

- 把“两层验证 + 晋级门”画成第一等结构；
- 把预算、工具契约、case 账本写成可执行的 spec；
- 把误接受率、校准、信任域写成评测协议；
- 把设计意图做成 `roles.yaml` sidecar + validator + role-aware tools；
- 把 `role_map_sha256` 写进 case 记录；
- 把面积做成角色感知、带 low/high 区间、进入 Pareto 的闭环约束；
- 用 MCU 类比降低沟通成本。

## 引用说明

- 论文数字来自公开摘要或 README，未在本仓库复现；
- 日期为公开版本/仓库更新时间，可能与正式出版日期不同；
- 如果发现遗漏或错误，欢迎开 Issue 补充。