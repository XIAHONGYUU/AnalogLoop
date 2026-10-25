# 评测协议

## 目标

这个协议要回答三个问题：

1. 在固定预算下，能否达到 spec？
2. 达到 spec 需要多少次 SPICE？
3. 快路径是否安全（误接受率）？

它不是“跑几个电路看结果”，而是一套可复现、可比较、可审计的流程。

## 电路与 PDK

### 第一版（v0.3）

- 两级运放（two-stage op-amp），固定拓扑，sizing 变量 8–12 个；
- 电流镜（current mirror），验证偏置与输出摆幅；
- LDO（可选，作为更难的第二个电路）。

### PDK

- [SkyWater Sky130](https://github.com/google/skywater-pdk)（Apache-2.0）；
- 第二 PDK 可选 [GF180MCU](https://github.com/google/gf180mcu-pdk) 或 [IHP SG13G2](https://github.com/IHP-GmbH/IHP-Open-PDK)。

### 仿真器

- ngspice（版本固定，记录在 case 记录里）；
- 可选适配器：HSPICE / Spectre（不进入公开 CI）。

## 测试台契约

测试台是设计的一部分，不是附属品。每个指标必须有**固定的测量定义**：

| 指标 | 定义 | 条件 |
|---|---|---|
| Gain | 低频小信号增益 | 指定负载、共模、电源 |
| UGB | 单位增益带宽 | 开环，指定负载 |
| PM | 相位裕度 | 开环，指定负载；记录 crossover 频率 |
| Power | 静态功耗 | 无输入，典型角落 |
| Noise | 输入参考积分噪声 | 带宽、源阻抗指定 |
| Offset | 输入失调 | 统计量；记录样本数 |
| Slew Rate | 大信号压摆率 | 指定输入阶跃 |
| Settling | 建立时间 | 指定误差带 |
| THD | 总谐波失真 | 指定频率/幅度 |
| Area | pre-layout low/nominal/high | rule pack + role manifest；不是 signoff |

**测量定义必须版本化。** 如果 PM 的定义从“crossover 处相位 + 180”改成“相位裕度减去负载效应”，优化器会立刻“进步”，但设计没有变好。

## 角落与温度

最小集合：

- 工艺：TT、SS、FF；
- 温度：-40°C、27°C、125°C；
- 电源：标称 ±10%。

完整 PVT 组合是 3×3×3 = 27 个点。第一版可以只跑 9 个（TT/SS/FF × 3 温度），但必须在报告里说明。

## 数据划分

- 按**拓扑 + 角落**分组划分，不随机打散；
- 训练集、验证集、测试集的设计点不重叠；
- 用参数哈希去重，防止同一设计换个名字泄漏；
- 测试集只在最后评估，不参与调参。

## 基线

至少四条：

1. **Random / Latin Hypercube**：随机采样，固定预算；
2. **Grid**：粗网格，固定预算；
3. **DoE + BO**：Sobol/LHS 初始化 + GP/EI 或 TuRBO；
4. **LLM 策略 + BO**：本架构；
5. **Oracle（可选）**：全 SPICE + 大量预算，给上界参考。

报告时必须说明每条基线的预算、初始化、停止条件。

## 指标

### 主指标

- **Success rate**：在预算内达到 spec（含裕量）的比例；
- **Simulations-to-spec**：达到 spec 所需 SPICE 次数的中位数 / p90；
- **Cost-to-spec**：加权成本（快评估、SPICE、人工）；
- **False accept rate**：代理说 pass、SPICE 说 fail 的比例；
- **Fast-path ratio**：快路径占比；
- **Area**：area_low / nominal / high、by_role、超出 budget 的比例；
- **Area error**（若有 layout）：估计 vs 实际面积的 median / p95、rank correlation。

### 次指标

- Wall-clock time（含 I/O、排队、代理推理）；
- OOD 比例；
- 角色校验失败次数（应在 SPICE 之前被拦截）；
- 重放一致率；
- 失败类型分布（不收敛、指标不达标、越界）。

## 面积报告

面积必须和性能一起报告，不能只放在附录：

- 每个候选给出 `area_low / nominal / high`、主导角色、rule pack 名称与置信度；
- 报告 `area_high ≤ budget`、`area_low > budget`、`uncertain` 三类的比例；
- 若有已完成 layout，报告面积误差、rank correlation、low/high 覆盖率；
- 面积与功耗、速度一起画 Pareto，不压成加权和；
- 面积超限的解不能进入“可行解”统计。

## 执行批次

ASST 的 plan / run / collect 必须产生可复现的产物：

- `plan.json`：run dir、PVT/参数矩阵、config/plan 哈希；
- `metrics.json`：固定 measure 定义的结果；
- `summary.xlsx`：人的视图；
- `archive/`：配置、netlist、log、退出码、哈希。

Excel 不是事实来源；case 记录以 JSON/哈希为准。

run 中途不允许改 config；要改就生成新 snapshot、新 plan，旧 run 保留旧 hash。

## 统计

- 每个配置至少 5 个随机种子；
- 报告中位数与 IQR，不只报均值；
- 用 bootstrap 给 95% 置信区间；
- 对“成功率”用 Wilson 区间；
- 对“simulations-to-spec”用生存分析（未达到的样本是删失数据，不要直接丢掉）。

## 报告模板

```text
Circuit: two-stage-opamp-v1
PDK: sky130A
Corners: TT/SS/FF x -40/27/125C
Budget: 50 SPICE, 2000 fast calls
Seeds: 5

Method            Success   Sims-to-spec (med / p90)   FAR     Fast ratio
Random            0.20      48 / >50                     -      0.00
Grid              0.40      41 / >50                     -      0.00
DoE + BO          0.60      28 / 47                      -      0.00
Ours (no gate)    0.60      18 / 35                      0.061   0.94
Ours (gate)       0.60      22 / 38                      0.004   0.91
Oracle           100        -                           -      0.00
```

上面的数字是模板占位，不是实验结果。

## 可复现清单

- [ ] 仿真器版本、PDK 版本、模型哈希记录在案；
- [ ] 每个 case 有 netlist 哈希、role manifest 哈希、area 报告哈希与原始输出哈希；
- [ ] ASST plan/config/summary/archive 哈希记录在案；
- [ ] 面积 rule pack 版本与 area_model_sha256 记录在案；
- [ ] 随机种子固定；
- [ ] 代理模型版本与训练集哈希记录；
- [ ] 测量脚本版本化；
- [ ] 报告包含失败案例与删失样本；
- [ ] 一键重放脚本可复现最优 case。

## 反作弊

- 角色 manifest 与网表一起冻结，不能在测试阶段改；
- 面积 budget 与 rule pack 在测试阶段冻结；
- 测试集不参与任何调参；
- 不允许针对测试电路手写启发式；
- 测量定义修改必须升版本，并重跑全部基线；
- 代理训练数据不能包含测试集；
- 报告必须包含失败案例，不能只展示成功案例。