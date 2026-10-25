# 记忆与重放

## 三种记忆，三种可信度

| 存储 | 内容 | 可信度 | 写入方式 | 读取方式 |
|---|---|---|---|---|
| Case 账本 | 每次评估的事实 | 高 | 只追加 | 查询 / 重放 |
| 技能库 | 规则、playbook、负知识 | 中（可错） | 审核后写入 | 检索 / 提示 |
| 代理模型 | 表 / GP / NN | 中（有分布） | 训练后注册 | 预测 + 校准 |

不要把三者混在一个向量库里。它们的生命周期、验证方式、失败模式都不同。

## Case 账本

### 只追加

账本一旦写入，不修改。修正用“新 case + 指向旧 case 的 supersedes 字段”，而不是覆盖。

原因：

- 重放需要稳定的历史；
- 失败案例也是资产；
- 审计需要看到“当时为什么这么判断”。

### 哈希链

每条记录包含：

- `prev_hash`：上一条记录的哈希；
- `record_hash`：本条规范化 JSON 的 SHA-256；
- `provenance`：工具/模型/仿真器版本。

这样任何一条被篡改，后续哈希都会断。

### 最小字段

见 [../spec/case-record.schema.json](../spec/case-record.schema.json)。核心字段：

- 身份：case_id、时间、spec_id、candidate_id；
- 输入：topology、params、corner、temperature；
- 评估：mode、model_id、metrics、sigma、ood、spice；
- 预算：fast_calls、spice_calls、wall_ms；
- 决策：accepted、reason、promotion；
- 溯源：contract/tool/simulator/model 版本与哈希。

## 负知识

大多数记忆系统只存成功案例。模拟设计里，**“为什么不行”往往更有价值**：

- 哪个参数区域必然进入线性区；
- 哪个角落的 PM 永远不够；
- 哪类拓扑在给定负载下无法达到 UGB；
- 哪种补偿方式会引入右半平面零点。

负知识记录建议包含：

```yaml
negative:
  claim: "W1 > 40um at L=0.5um drives M1 into triode at ss/125C"
  evidence_case_ids: ["case-000123", "case-000124"]
  scope: {topology: "two-stage-opamp-v1", corner: "ss", temp_c: 125}
  confidence: "medium"
  reviewed_by: "human"
```

负知识必须是**有范围的**，不能写成“这个拓扑不行”。

## 重放

### 目标

给定账本，重放出一条相同的决策链：

- 相同的候选顺序；
- 相同的快/慢路径选择；
- 相同的停机点；
- 相同的最终报告。

### 前提

- 工具版本固定；
- 仿真器版本固定；
- PDK/模型哈希固定；
- 随机种子固定；
- 代理模型哈希固定；
- LLM 输出可重放（温度 0 或记录原始输出）。

### 分层重放

不是所有层都能完全重放：

| 层 | 可重放性 | 方法 |
|---|---|---|
| 工具链 | 高 | 固定版本 + 确定性算法 |
| SPICE | 高（同版本） | 固定 netlist + 种子 + 版本 |
| 代理 | 高 | 固定权重 + 固定输入 |
| LLM | 中 | 记录原始输出；或温度 0 + 固定 prompt |
| 人 | 低 | 记录决定与理由 |

实践上，**记录 LLM 的原始输出**比追求“重新生成一模一样”更可靠。

### 重放命令（计划）

```bash
python -m analogloop.replay --ledger cases/2026-10-25.jsonl --until case-000123
```

输出：每个 case 的决策、预算消耗、最终指标、与原始记录的差异。

## 查询接口

不要让 LLM 读全量账本。提供聚合查询：

```text
best_case(spec_id, corner="ss", feasible=true)
recent_failures(spec_id, limit=5)
similar_cases(spec_id, params, k=10)
negative_knowledge(topology, corner)
budget_summary(spec_id)
```

返回值带 `provenance` 与 `confidence`，LLM 只看到摘要。

## 保留与压缩

- 原始 SPICE 文件（.raw）体积大，存哈希 + 可重新生成的 netlist，不一定要存全量；
- 指标与决策永久保留；
- 代理训练集用内容寻址存储（hash → blob）；
- 定期做“账本体检”：schema 校验、哈希链校验、孤儿记录检查。

## 一条原则

**账本记录事实，技能记录判断，代理记录近似。** 三者分开，系统才能既快又可信。
