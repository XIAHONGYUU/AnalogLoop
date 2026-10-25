# CURRENT_TASK

## 当前目标

v1.0.0 已冻结：这是 AnalogLoop 的第一版参考架构（architecture note freeze），
用于展示 AI + 模拟电路设计的分层、契约、可复原性与执行层思路。
下一步是 v1.1 的 mock 闭环，不在本版范围内。

## 状态

- Release：**v1.0.0 — architecture note freeze**（tag / GitHub Release）。
- 七张原创图：architecture、fast-verification、mcu-mapping、pdk-fastpath、
  netlist-semantics、area-aware-loop、asst-execution。
- 语义网表：18 个角色、manifest schema、示例 netlist/roles、validator。
- 面积层：角色感知面积模型、三值 area gate、layout handoff。
- ASST 执行层：22 个工具、config 单一事实源、可复原性检查表。
- 文档：研究问题、证据边界、评测协议、相关工作、路线图、评审指南。
- 本地验证通过；CI 绿。
- **未包含**：mock 闭环、真实 ASST adapter、ngspice demo、代理模型、流片。

## 下一步原子动作（v1.1，不在 v1.0.0 内）

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
