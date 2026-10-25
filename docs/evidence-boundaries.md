# 证据边界

这份文档把“已核实”“作者推导”“待验证”分开。它不是免责声明，而是阅读说明书。

## 已核实（有公开来源）

以下事实来自论文摘要、项目 README 或官方文档，链接在 [landscape.md](landscape.md)：

- AnalogCoder 是 AAAI 2025 的 training-free 模拟电路设计 agent，使用代码生成与技能库。
- AnalogCoder-Pro 是 TCAD 2026 的扩展，加入多模态诊断、BO sizing，报告 28 个电路、13 类。
- AnalogAgent 是 KDD 2026（AI4Science）工作，使用多智能体 + 自演化记忆，摘要报告 92%（Gemini）与 97.4%（GPT-5）Pass@1。
- AnaFlow 明确以 sample-efficient、explainable sizing 为目标，使用自适应仿真策略。
- SABLE 是 TODAES 2026 的 NDA-safe 闭环，包含 28 个 SKILL 白名单入口与 6 个机器可检查的停机条件。
- AgenticSizing 报告 8 个电路、最大 55 个晶体管 / 60 个 sizing 变量，LDO 上 60% 成功率、平均 83 次迭代。
- VLM-CAD 报告 12 个 sizing 任务、6 个电路、4 个工艺平台，Strict Pass@1 23.3%、Relaxed 91.7%。
- LASANA 报告最高三个数量级加速，能量/延迟/行为误差分别 < 7%、< 8%、< 2%。
- Mosplot 使用 ngspice/HSPICE/Spectre 生成 lookup table，做多角落 sizing，并写网表交给仿真器验证。
- SpiceMCP 把优化状态放在 server 侧 SQLite，LLM 只负责拓扑与策略。
- ltspice-mcp 按名字返回 gm/gds/PM 等测量值，而不是让模型解析 raw 文件。
- AutoCkt 是 DATE 2020 的 RL sizing 工作，使用 ngspice 与 Gym 环境。
- GANA（DATE 2020）用图卷积网络把模拟网表自动标注成功能块。
- AgenticSizing 把网表分解成功能块与子结构，再用于多智能体 sizing。
- Analog-DB 把功能子块与器件尺寸做成带匹配约束的命名参数，供 AI agent 发现和复用。
- AMSnet-q 从原理图自动提取网表、生成测试台，并用仿真验证功能后打标签。
- 模拟版图自动化工具（ALIGN、BAG、MAGICAL 等）通常把面积/匹配/对称约束作为布局输入；面积估算不是新问题。

## 作者推导（未实验验证）

以下内容是本仓库的设计判断，不是文献事实：

- 五段架构 + 两条回路 + 横切预算控制器的划分；
- 晋级门的四条规则（OOD、sigma × k、criticality、抽样）；
- 用“误接受率”而不是平均误差作为代理安全指标；
- 成本模型 `S = t_s / (r t_f + (1-r) t_s)` 与返工项；
- 指标容差表（Gain 1 dB、UGB 5%、PM 3° 等）是起点，不是标准；
- MCU 类比的映射与“三条边界”；
- 对 gm/ID 与学习型数据库的适用边界判断；
- 语义网表的三层表示、角色词表与 validator 规则；
- 角色感知的面积分解（core / ring / routing / dummy / periphery / reserve）与三值面积门。

这些判断可能错。它们应该被实验、反例或更好的论证修正。

## 待验证（可证伪）

| 主张 | 证伪条件 | 当前状态 |
|---|---|---|
| H1：工具契约降低非法仿真 | 引入契约后非法仿真占比无显著下降 | 未测 |
| H2：预算感知策略降低 simulations-to-spec | 相对固定预算 BO 无显著改进 | 未测 |
| H3：账本 + 负知识带来 warm-start 收益 | 冷启动与热启动无显著差异 | 未测 |
| H4：角色 manifest + validator 降低非法编辑 | 与“只有命名约定”相比无显著差异 | 未测 |
| H5：角色感知面积模型减少 layout 返工 | 与只看 W·L 相比无显著差异 | 未测 |
| 代理可承担 80–95% 候选 | 在 0.5% FAR 约束下覆盖率显著低于 80% | 未测 |
| 边界 10% 带内 FAR ≤ 0.5% | 实测 FAR 超过 0.5% | 未测 |
| gm/ID 特征跨 PDK 可迁移 | 在第二 PDK 上误差/收敛显著变差 | 未测 |
| 30% simulations-to-spec 降幅 | 多种子实验未复现 | 未测 |

## 明确的未知

- 95% 的“效果”应按哪个指标加权？不同电路的最优权重不同。
- 代理在瞬态、失真、启动、失配上的误差上界。
- 角落作为输入还是独立建模，哪个更稳。
- 表模型/网络的导数连续性对 Newton 收敛的实际影响。
- 商业 PDK 场景下，如何在 NDA 内做可复现研究。
- 人类审核在闭环中的最佳插入点。
- 多目标冲突时，Pareto 前沿如何呈现给设计者。
- 自动角色推断的准确率，以及人工审核的最小成本。
- 层级、多 finger、并联阵列如何映射到角色 group。
- 面积模型的校准误差、rank correlation、low/high 覆盖率。
- metal/EM/thermal/pad ring 对面积的实际贡献。

## 没有做的事

- 没有流片，没有 silicon correlation；
- 没有在商业 PDK 上跑过；
- 没有训练代理模型；
- 没有实现完整的 mock 闭环（v0.1 只有文档、spec、示例网表、校验器与面积接口）；
- 没有复现论文数字。

## 图与文字来源

- 所有图由 [scripts/build_diagrams.py](../scripts/build_diagrams.py) 从零生成，使用几何图元与文字；
- 没有使用用户提供的原始架构图；
- 没有嵌入第三方图片；
- 文字由作者与 AI 助手共同起草，引用处标注来源。

## 如何引用

- 引用本仓库：见 [CITATION.cff](../CITATION.cff)；
- 引用论文：请引用原文，不要引用本仓库的转述；
- 引用数字：请回到原始论文/README 核对，本仓库的数字可能随版本变化。

## 一条原则

**把“我认为”和“已验证”分开写。** 这份仓库的价值不在于看起来确定，而在于把不确定性标出来。