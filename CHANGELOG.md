# Changelog

## v1.0.0 — 2026-10-25

**Architecture note freeze.** 第一版冻结的参考架构，不是运行时发布。

- 七张原创图：architecture、fast-verification、mcu-mapping、pdk-fastpath、
  netlist-semantics、area-aware-loop、asst-execution。
- 五段架构 + 两条回路 + 预算/晋级控制器。
- 两层验证：代理快路径、SPICE 签核、晋级门、误接受率。
- 语义网表：18 个器件角色、manifest schema、validator、两级运放示例。
- 面积层：角色感知面积模型、三值面积门、Pareto、layout handoff。
- ASST 执行层：CSV/Excel/JSON config、plan/run/collect、Excel/archive、
  config 单一事实源、可复原性检查表。
- 工具契约：22 个 typed tools；case 记录 schema（role/area/execution）。
- 文档：研究问题、证据边界、评测协议、相关工作、路线图、评审指南。

## v0.1.4

- ASST config 作为单一事实源；新增 config 读取/提议 patch 工具与 anti-drift 规则。

## v0.1.3

- ASST 执行层：CLI 固化、plan/run/collect、Excel 汇总与归档。

## v0.1.2

- 面积层：角色感知面积模型、三值 area gate、layout handoff。

## v0.1.1

- 语义网表：器件角色、manifest schema、validator、两级运放示例。

## v0.1.0

- 初始架构笔记、两层验证、MCU 类比、gm/ID 与 PDK 数据库、工具契约、评测协议。
