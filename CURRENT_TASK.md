# CURRENT_TASK

## 当前目标

发布 AnalogLoop v0.1：一份以“仿真预算 + 两层验证”为中心的模拟电路设计
Agent 架构笔记，包含原创图、工具契约、case schema、评测协议和证据边界。

## 状态

- 仓库已创建，文档、图、spec 已落地。
- 已生成四张原创图：architecture、fast-verification、mcu-mapping、pdk-fastpath。
- 尚未实现可运行的 mock 闭环；尚未接 ngspice。
- 尚未公开推送（等待最终检查）。

## 下一步原子动作

1. 运行 `scripts/validate.py` 与链接检查。
2. 本地提交。
3. 创建 `XIAHONGYUU/analogloop` 公开仓库并推送。
4. 补充 topics 与仓库描述。

## 约束

- 不上传用户提供的原始架构图；只使用本仓库脚本生成的图。
- 不包含任何 NDA / 商业 PDK 数据；公开示例只用 open PDK。
- 不把“95%”写成已验证结论；只作为目标与评测协议。
- 文档 CC BY 4.0，代码 MIT。

## 完成标准

- 所有相对链接可解析。
- `spec/tool-contract.yaml` 可被 YAML 解析。
- `spec/case-record.schema.json` 可被 JSON Schema 校验器加载。
- 三张 PNG 视觉检查通过。
- GitHub 仓库公开可访问，README 首图正常渲染。
