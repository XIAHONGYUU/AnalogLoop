# CURRENT_TASK

## 当前目标

维护 AnalogLoop v0.1.2（语义网表 + 面积层），并推进 v0.2 mock 闭环：
让 agent 通过角色级补丁修改网表，在花 SPICE 之前完成面积与角色校验。

## 状态

- v0.1 已发布：AnalogLoop（https://github.com/XIAHONGYUU/AnalogLoop）
- 六张原创图：architecture、fast-verification、mcu-mapping、pdk-fastpath、
  netlist-semantics、area-aware-loop。
- 语义网表：`spec/device-roles.yaml`、`spec/netlist-manifest.schema.json`、
  示例 netlist/roles、validator 已落地。
- 面积层：`estimate_area` / `export_layout_intent` 工具契约、
  三值 area gate、layout handoff 文档与图。
- 本地验证通过；CI 已配置（docs 校验 + SVG 确定性检查）。
- 尚未实现可运行的 mock 闭环；尚未接 ngspice。

## 下一步原子动作

1. 建立 `analogloop/` Python 包骨架。
2. 实现 mock 仿真器、预算账本、晋级门、JSONL 哈希链。
3. 实现角色 manifest 解析、角色级补丁、面积估计与重放。
4. 在 README 增加 v0.2 的复现命令。

## 约束

- 不上传用户提供的原始架构图；只使用本仓库脚本生成的图。
- 不包含任何 NDA / 商业 PDK 数据；公开示例只用 open PDK。
- 不把“95%”或“面积误差”写成已验证结论；只作为目标与评测协议。
- 文档 CC BY 4.0，代码 MIT。

## 完成标准

- 六张 PNG 视觉检查通过。
- `spec/tool-contract.yaml` 可被 YAML 解析。
- `spec/case-record.schema.json` 可被 JSON Schema 校验器加载。
- `examples/two-stage-opamp/roles.yaml` 通过 manifest schema 与角色校验。
- 面积报告包含 low/nominal/high、by_role、rule pack 版本。
- mock 闭环可在固定种子下重放。
- GitHub 仓库公开可访问，README 首图正常渲染。
