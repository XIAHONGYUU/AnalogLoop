# CURRENT_TASK

## 当前目标

维护 AnalogLoop v0.1.4（语义网表 + 面积层 + ASST 执行层 + 单一 config 真相源），
并推进 v0.2 mock 闭环：让 agent 通过角色级补丁修改网表，在花 SPICE 之前完成
角色、面积和 config 校验，再通过 ASST 风格的批次接口执行仿真。

## 状态

- v0.1 已发布：AnalogLoop（https://github.com/XIAHONGYUU/AnalogLoop）
- 七张原创图：architecture、fast-verification、mcu-mapping、pdk-fastpath、
  netlist-semantics、area-aware-loop、asst-execution。
- 语义网表：`spec/device-roles.yaml`、`spec/netlist-manifest.schema.json`、
  示例 netlist/roles、validator 已落地。
- 面积层：`estimate_area` / `export_layout_intent` 工具契约、三值 area gate、
  layout handoff 文档与图。
- 执行层：ASST 文档、22 个工具、execution case 字段；
  config 是单一真相源，run 引用 `config_sha256` / plan hash。
- 本地验证通过；CI 已配置（docs 校验 + SVG 确定性检查）。
- 尚未实现可运行的 mock 闭环；尚未接 ngspice。

## 下一步原子动作

1. 建立 `analogloop/` Python 包骨架。
2. 实现 mock 仿真器、预算账本、晋级门、JSONL 哈希链。
3. 实现角色 manifest 解析、角色级补丁、面积估计与 ASST 风格批次适配。
4. 实现 config 读取/提议 patch/校验，确保 run 中途不能改配置。
5. 在 README 增加 v0.2 的复现命令。

## 约束

- 不上传用户提供的原始架构图；只使用本仓库脚本生成的图。
- 不包含任何 NDA / 商业 PDK 数据；公开示例只用 open PDK。
- ASST 的代码不进入本仓库；只保留接口、mock 和分工。
- 不把“95%”“面积误差”“执行层收益”写成已验证结论；只作为目标与评测协议。
- 文档 CC BY 4.0，代码 MIT。

## 完成标准

- 七张 PNG 视觉检查通过。
- `spec/tool-contract.yaml` 可被 YAML 解析。
- `spec/case-record.schema.json` 可被 JSON Schema 校验器加载。
- `examples/two-stage-opamp/roles.yaml` 通过 manifest schema 与角色校验。
- 面积报告包含 low/nominal/high、by_role、rule pack 版本。
- ASST config snapshot / plan / metrics / summary 可追溯，run 中途改配置被拒绝。
- mock 闭环可在固定种子下重放。
- GitHub 仓库公开可访问，README 首图正常渲染。
