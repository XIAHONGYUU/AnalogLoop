# CURRENT_TASK

## 当前目标

按用户要求调整项目首页，先确认AnalogLoop的表达，再处理其他项目。
本轮仅修改README与当前入口，不实现优化运行时，不改v1.0.0标签或发布记录。

## 本轮状态（2026-10-25）

- 已形成首页修改稿：AI仿真优化Loop、AI/ASST/工程师分工、ASST实际实践来源、两级运放说明示例、当前可检查产物。
- 原完整架构图与深入文档保留；首页将完整图折叠，先展示简化流程。
- 用户已有ASST实践与本仓库拟议运行时明确分开；说明示例不作为实跑结果。
- 用户已授权提交并推送本轮首页，供GitHub在线审阅；表达方式尚未最终验收。
- 原首页可由Git基线8224866恢复；v1.0.0发布仍为已冻结架构笔记。

## 唯一下一步

用户在GitHub审阅首页表达与层次；按反馈定稿。优化运行时开发不在本轮范围内。

## 状态

- Release：**v1.0.0 — architecture note freeze**（tag / GitHub Release）。
- 七张原创图：architecture、fast-verification、mcu-mapping、pdk-fastpath、
  netlist-semantics、area-aware-loop、asst-execution。
- 语义网表：18 个角色、manifest schema、示例 netlist/roles、validator。
- 面积层：角色感知面积模型、三值 area gate、layout handoff。
- ASST 执行层规范：22 项工具契约、config 单一事实源、可复原性检查表；不等于22个工具运行时已实现。
- 文档：研究问题、证据边界、评测协议、相关工作、路线图、评审指南。
- v1.0.0基线曾通过本地验证与CI；本轮首页修改稿已通过38项仓库校验，远程CI结果以GitHub Actions为准。
- **未包含**：mock 闭环、真实 ASST adapter、ngspice demo、代理模型、流片。

## 后续开发方向（v1.1，非本轮动作）

1. 建立 `analogloop/` Python 包骨架。
2. 实现 mock 仿真器、预算账本、晋级门、JSONL 哈希链。
3. 实现角色/面积/config 校验与 ASST 风格 plan/run/collect。
4. 实现重放命令与单元测试。
5. 发布 v1.1。

## 约束

- 不上传用户提供的原始架构图；只使用本仓库脚本生成的图。
- 不包含任何 NDA / 商业 PDK 数据；公开示例只用 open PDK。
- ASST 的代码不进入本仓库；只保留接口、mock 和分工。
- 不把“95%”“面积误差”“执行层收益”写成已验证结论。
- 文档 CC BY 4.0，代码 MIT。

## 完成标准（v1.0.0）

- 七张 PNG 视觉检查通过。
- `spec/tool-contract.yaml` 可被 YAML 解析。
- `spec/case-record.schema.json` 可被 JSON Schema 校验器加载。
- `examples/two-stage-opamp/roles.yaml` 通过 manifest schema 与角色校验。
- 面积报告、execution 字段、可复原性检查表齐全。
- GitHub Release v1.0.0 可访问。
