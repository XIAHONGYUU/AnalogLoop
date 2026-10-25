# 预算与收敛

## 为什么预算要一等公民

在普通 agent 里，工具调用是“免费”的；在模拟设计里，每一次 SPICE 都有真实成本。如果预算不进入决策，agent 会倾向于：

- 反复微调同一个点，而不是换策略；
- 在不可行区域里烧仿真；
- 用“再多跑一次”代替“想清楚”。

预算控制器的作用不是省钱，而是**让策略层对成本负责**。

## 成本单位

建议用三种成本，不要混算：

| 单位 | 含义 | 典型量级 |
|---|---|---|
| `fast_call` | 一次代理评估 | ms–s |
| `spice_call` | 一次 SPICE（按分析/角落加权） | s–min |
| `human_minute` | 人工审核/签核 | min–hour |

权重可以配置，例如：

```yaml
cost_weights:
  fast_call: 1
  spice_call: 1000
  human_minute: 60000
```

这样“1 次 SPICE ≈ 1000 次快评估”的直觉可以直接进入评分函数。

## 账本字段

每条 case 至少记录：

```yaml
case_id: "case-000123"
created_at: "2026-10-25T12:00:00+08:00"
spec_id: "spec-two-stage-opamp-v1"
candidate:
  topology: "two-stage-opamp-v1"
  params: {w1_um: 20, l1_um: 0.5, ...}
evaluation:
  mode: "fast"           # fast | spice | both
  model_id: "gp-v3"
  metrics: {gain_db: 61.2, ugb_mhz: 102.4, pm_deg: 58.7}
  sigma: {gain_db: 0.6, ugb_mhz: 3.1, pm_deg: 1.8}
  ood_score: 0.04
  spice: null
budget:
  fast_calls: 1
  spice_calls: 0
  wall_ms: 12
decision:
  accepted: true
  reason: "margin > 3 sigma; in trust region"
provenance:
  contract_version: "0.1"
  tool_version: "0.1.3"
  simulator: null
  netlist_sha256: null
```

## 分配策略

### 固定比例

简单、可预测：

- 探索：90% 快 + 10% SPICE；
- 精修：70% 快 + 30% SPICE；
- 确认：0% 快 + 100% SPICE。

适合第一版实现，便于解释。

### 分阶段递减（successive halving）

1. 用快路径筛掉 80% 候选；
2. 对前 20% 跑 SPICE；
3. 对前 5% 做多角落；
4. 对前 1% 做 MC / 签核。

每一阶段的预算按上一阶段的结果分配。

### 不确定性采样

把 SPICE 预算优先给：

- sigma 大；
- 靠近 spec 边界；
- OOD 分数高；
- 关键指标（PM、启动）权重高。

这是晋级门的自然延伸。

### 角落配额

PVT 角落不能被“平均掉”。建议给每个角落设最低配额：

```yaml
corner_quota:
  tt: 0.4
  ss: 0.3
  ff: 0.3
```

最差角落决定成败，配额应该向最差角落倾斜。

## 停机条件

建议实现为可组合的谓词：

```text
stop if SPEC_MET and margin >= margin_target
stop if budget_remaining <= 0
stop if iter >= max_iter
stop if no_improvement >= patience
stop if infeasible_proven
stop if ood_ratio > ood_limit
stop if sim_failures > failure_limit
stop if human_stop
```

每个条件都要在 case 记录里留下证据。不要用“LLM 说可以停了”作为唯一条件。

## 指标

### simulations-to-spec

达到 spec（含裕量）所需的 SPICE 调用次数。报告：

- 中位数；
- p90；
- 失败率（预算内未达到）。

### cost-to-spec

加权成本：

$$
C = n_f \cdot c_f + n_s \cdot c_s + n_h \cdot c_h
$$

其中 `c_f, c_s, c_h` 是快评估、SPICE、人工的权重。

### fast-path ratio

$$
r = \frac{n_f}{n_f + n_s}
$$

### false-accept rate

见 [fast-verification.md](fast-verification.md)。预算报告必须同时给出这个安全指标，否则“省了很多仿真”没有意义。

## 一个例子

两级运放，目标 Gain ≥ 60 dB、UGB ≥ 100 MHz、PM ≥ 60°、Power ≤ 5 mW，预算 50 次 SPICE：

| 阶段 | 快评估 | SPICE | 目的 |
|---|---|---|---|
| 可行性预检 | 0 | 0 | 排除不可能 spec |
| 探索 | 800 | 8 | 找可行区域 |
| 精修 | 200 | 25 | 逼近边界 |
| 确认 | 0 | 12 | 三角落 + 抽样 |
| 签核 | 0 | 5 | 最终候选 |

总计 1000 次快评估 + 50 次 SPICE，快路径占比 95.2%。

这个例子只是预算模板，不是实验结果。

## 与策略层的交互

策略层不应该直接“调用 SPICE”，而应该：

1. 调 `request_budget({kind: "spice", n: 3})`；
2. 控制器根据剩余预算、当前阶段、候选风险决定批准/拒绝；
3. 批准后，策略层再调 `simulate_spice`。

这样预算成为**显式的控制信号**，而不是隐式的副作用。
