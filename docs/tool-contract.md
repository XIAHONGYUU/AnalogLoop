# 工具契约

## 原则

工具契约是策略层与执行层之间的“ISA”。它必须满足：

1. **有限**：工具数量可控，不允许 LLM 现场发明操作；
2. **typed**：参数、返回值、错误码都有 schema；
3. **白名单**：只能调用注册过的工具，不能执行任意 Python/Shell；
4. **有成本**：每次调用声明 `cost`（快评估、SPICE、人工）；
5. **有副作用**：读/写、是否落账、是否可重试；
6. **可版本化**：契约版本、工具版本、schema 版本。

机器可读版本见 [../spec/tool-contract.yaml](../spec/tool-contract.yaml)。

## 工具列表

| 工具 | 作用 | 成本 | 副作用 | 关键约束 |
|---|---|---|---|---|
| `set_spec` | 写入/更新 spec | 0 | 写 | spec 必须通过 schema |
| `get_state` | 读取受控状态视图 | 0 | 读 | 不返回全量账本 |
| `get_role_map` | 读取紧凑角色视图 | 0 | 读 | 不返回全量网表 |
| `query_devices` | 按角色/组查询器件 | 低 | 读 | 返回参数与约束 |
| `validate_roles` | 校验 manifest 与拓扑 | 低 | 写日志 | 失败不花 SPICE |
| `apply_role_patch` | 角色级修改并生成新网表 | 低 | 写 | 必须重新校验 |
| `propose_candidate` | 提出候选与理由 | 0 | 写草稿 | 参数必须在范围内 |
| `check_feasibility` | 静态/解析可行性预检 | 低 | 读 | 不调用 SPICE |
| `evaluate_fast` | 快速代理评估 | 快 | 写缓存 | 必须返回 sigma / OOD |
| `simulate_spice` | 真实 SPICE（单次） | 高 | 写原始文件 | 需要预算授权 |
| `get_simulation_config` | 读规范化 config + hash | 0 | 读 | 不返回隐藏状态 |
| `propose_config_patch` | 提议配置变更 | 低 | 写 | 返回 diff + 新 snapshot |
| `plan_simulation_batch` | 配置 → 可重放 plan | 低 | 写 | 记录 config/plan 哈希 |
| `run_simulation_batch` | 执行 ASST 批次 | 高 | 写 + 外部进程 | 需要预算/许可证 |
| `collect_simulation_results` | 解析 measure / 汇总 | 低 | 写 | 生成 summary + archive |
| `estimate_area` | 估算 pre-layout 面积 | 低 | 写 | 返回 low/nominal/high + by_role |
| `export_layout_intent` | 输出 floorplan / delta | 低 | 写 | 依赖 role manifest |
| `measure` | 按契约测量指标 | 低 | 写 | 指标定义版本化 |
| `commit_case` | 写 case 账本 | 低 | 追加 | 不可修改历史 |
| `query_memory` | 查询历史/技能 | 低 | 读 | 返回带 provenance |
| `request_budget` | 申请预算 | 0 | 写 | 控制器可拒绝 |
| `stop` | 结束并给出理由 | 0 | 写 | 理由必须匹配停机条件 |

## 一次调用的信封

所有工具调用使用同一个外层结构：

```json
{
  "action": "simulate_spice",
  "request_id": "req-20261025-0042",
  "contract_version": "0.1",
  "args": {
    "candidate_id": "cand-0017",
    "analysis": "ac",
    "corner": "ss",
    "temperature_c": 125
  },
  "budget": { "max_spice": 1 },
  "rationale": "PM margin is small; verify at worst-case corner."
}
```

执行层必须：

- 校验 `action` 是否在白名单；
- 校验 `args` 是否符合 schema；
- 校验预算是否足够；
- 记录 `request_id`、耗时、结果哈希；
- 返回 typed 结果或 typed 错误。

## 结果结构

```json
{
  "request_id": "req-20261025-0042",
  "status": "ok",
  "cost": { "spice_calls": 1, "wall_ms": 1840 },
  "result": {
    "metrics": {
      "gain_db": 61.2,
      "ugb_mhz": 102.4,
      "pm_deg": 58.7,
      "power_mw": 4.9
    },
    "raw_sha256": "...",
    "simulator": "ngspice-44",
    "model": "sky130_tt"
  },
  "warnings": ["PM below target by 1.3 deg"]
}
```

错误也必须是 typed：

```json
{
  "request_id": "req-20261025-0043",
  "status": "error",
  "error": {
    "code": "SPICE_NOT_CONVERGED",
    "message": "DC operating point failed at corner ss, T=125C",
    "retryable": true,
    "suggested_action": "reduce initial guess step or check bias"
  }
}
```

## 角色级补丁

策略层不应该直接改网表文本。唯一允许的修改入口是 `apply_role_patch`：

```json
{
  "action": "apply_role_patch",
  "args": {
    "candidate_id": "cand-0017",
    "block": "tail",
    "action": "resize",
    "factor": 1.2
  },
  "rationale": "Increase tail current 20% to raise UGB; keep input pair gm/ID."
}
```

工具链必须：

1. 检查 block 是否存在，role 是否 `tunable`；
2. 把角色级意图翻译成具体 W/L/M（同组器件一起移动）；
3. 重新生成 `netlist.cir` 与 `roles.yaml`；
4. 调 `validate_roles`；
5. 只有校验通过，才允许 `simulate_spice`。

失败时返回 typed 错误（`ROLE_NOT_TUNABLE`、`VALIDATION_FAILED`），并写进 case 记录。这样“AI 改了网表”永远是一条可审计的角色级补丁，而不是一段无法解释的文本 diff。

配置读写是 ASST 的 SSOT 入口：

- `get_simulation_config`：读 `config.json + config_sha256`，AI 只看到规范化后的真相；
- `propose_config_patch`：生成新 snapshot、diff、校验结果，不直接跑仿真；
- 人审核 diff 后，才 `plan_simulation_batch`；run 中途改配置必须走新 snapshot。

## ASST 执行批次

ASST 把 CLI 固化成一个批次接口：

```text
CSV/Excel 配置
  -> plan_simulation_batch（run dir / plan hash）
  -> run_simulation_batch（Spectre / ALPS / XA adapter）
  -> collect_simulation_results（metrics.json / summary.xlsx / archive）
```

- AI 只调用这三个工具，不拼 CLI；
- 人保留 CSV/Excel 配置面；
- case 记录写 `execution.adapter=asst`、plan/config/summary/archive 哈希；
- 失败可 resume，重试有上限；
- Excel 是人的视图，`metrics.json` 是 agent 的视图。

## 面积门

面积不是“nominal ≤ budget”的二值判断，而是带区间的三值判断：

```text
if area_high <= budget:      PASS
elif area_low > budget:      REJECT
else:                        UNCERTAIN
```

- `PASS`：可以进入 SPICE 确认；
- `REJECT`：确定超面积，不花 SPICE；
- `UNCERTAIN`：要求更准的 rule pack / 校准，或让 layout 做快速 floorplan。

优化时建议留 guardband：

```text
area_target = area_budget / (1 + area_guardband)
```

面积与功耗、速度一起进入 Pareto；不要把它压成一个加权和。

## 停机条件

停机不是“LLM 觉得够了”，而是机器可检查的条件：

- `SPEC_MET`：所有指标满足，且裕量 ≥ 阈值；
- `BUDGET_EXHAUSTED`：快/慢预算用完；
- `MAX_ITER`：达到迭代上限；
- `NO_IMPROVEMENT`：连续 N 次无改进；
- `INFEASIBLE`：可行性预检/搜索证明不可行；
- `OOD_LIMIT`：OOD 比例超阈值；
- `SIM_FAILURE_LIMIT`：仿真失败次数超阈值；
- `HUMAN_STOP`：人工停止。

每次 `stop` 必须带 `reason_code` 与证据（最好是最优 case 的 id）。

## 安全边界

- **不执行任意代码**：LLM 只能选工具，不能写 Python/Shell；
- **路径限制**：工具只能访问 workspace 下的 `runs/`、`cases/`、`netlists/`；
- **PDK 访问控制**：商业 PDK 只在受控环境，不进入公开日志；
- **限流**：每轮 SPICE 调用数、总时长、并发数都有上限；
- **审计**：每次调用都有 request_id、调用者、时间、参数哈希、结果哈希。

## 版本化

三个版本号分开：

- `contract_version`：工具集合与语义；
- `tool_version`：单个工具的实现；
- `schema_version`：参数/结果/case 记录的结构。

任何一个变化，都要在 case 记录里留下版本，否则重放会失真。