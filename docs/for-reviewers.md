# 给评审者的 10 分钟指南

> 这是一份 **AI + 模拟电路设计** 的参考架构笔记，不是已完成的 EDA 产品。
> 目标读者：模拟/混合信号设计工程师、EDA/Agent 研究者、面试官或简历评审。

## 1. 一句话

**AnalogLoop 把模拟电路的 sizing 闭环拆成：策略层、确定性工具链、两层验证、语义网表、面积门、ASST 执行层和可重放账本。**

## 2. 它想解决什么

- 仿真次数是瓶颈，不是 token；
- 代理模型可以快，但不能替代签核；
- LLM 不应该直接改网表、拼 CLI、做数值搜索；
- 设计意图、面积、执行环境都应该显式化、可校验、可复原。

## 3. 六个设计主张

1. **两层验证 + 晋级门**：代理负责探索，SPICE 负责签核；误接受率是一等指标。
2. **预算一等公民**：每次评估有成本，停机条件可检查。
3. **语义网表**：器件角色、匹配、比例写进 `roles.yaml`，validator 仲裁。
4. **面积进入闭环**：角色感知的 `low / nominal / high`，三值面积门，Pareto 而不是加权和。
5. **执行层固化**：ASST 把 CLI、配置、measure、Excel/archive 固化；config 是单一事实源。
6. **可复原性**：config + netlist + PDK/model + simulator + scripts + seeds + measure + archive，缺一不可。

## 4. 10 分钟阅读顺序

1. [architecture.md](architecture.md)：五段架构、两条回路、语义/面积/执行层。
2. [fast-verification.md](fast-verification.md)：两层验证、晋级门、95% 怎么定义。
3. [netlist-semantics.md](netlist-semantics.md)：角色 manifest、validator、角色级补丁。
4. [area-and-layout.md](area-and-layout.md)：面积模型、三值门、layout handoff。
5. [asst-and-execution.md](asst-and-execution.md)：ASST、CLI 固化、AI/脚本/人分工。
6. [reconstructability.md](reconstructability.md)：可复原性的硬标准。
7. [evidence-boundaries.md](evidence-boundaries.md)：哪些是事实、哪些是假设。

## 5. 哪些是原创，哪些是借用

**借用/对照：** agent loop、工具调用、BO/RL sizing、gm/ID、代理模型、模拟版图自动化、SABLE/AnalogCoder/AnalogAgent 等。

**本仓库的工程增量：**

- 把“预算账本 + 晋级门 + 误接受率”写成可执行契约；
- 把网表角色做成设计师声明 + sidecar + validator + 角色级工具；
- 把面积做成角色感知、带区间、进入 Pareto 的闭环约束；
- 把 ASST 风格的执行层写成 plan/run/collect + config SSOT；
- 把可复原性写成 checklist，而不是口号；
- 用 MCU 类比降低沟通成本。

**没有主张：** 新算法、SOTA、流片验证、完整 EDA 产品、自动版图。

## 6. 怎么评审

可以问五个问题：

1. 这个架构有没有把“策略”和“机制”分开？
2. 代理模型的误接受率有没有被当成安全指标？
3. 角色 manifest 能不能被 validator 检查，而不是只靠命名？
4. 面积/执行环境有没有进入闭环，而不是事后统计？
5. 给定一个 run，能不能在另一台机器上复原？

如果这五个问题都有明确答案，这份笔记就达到了目的；如果没有，就是下一版要补的。

## 7. 简历一句话

> **AnalogLoop**：面向 AI + 模拟电路设计的开源参考架构，提出语义网表、两层验证与晋级门、面积感知闭环、ASST 执行层与可复原性检查表；含 7 张原创图、工具契约与可校验 spec。

英文版：

> **AnalogLoop**: an open reference architecture for AI-assisted analog design, covering semantic netlists, two-speed verification with a promotion gate, area-aware Pareto optimization, an ASST-style execution layer, and a reconstructability checklist.

## 8. 状态

- Release: **v1.0.0 — architecture note freeze**
- 不是运行时发布；没有 mock 闭环、没有 ngspice demo、没有流片。
- 下一版：v1.1 mock 闭环（预算、门、账本、重放、config SSOT）。
