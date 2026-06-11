# 仿真输出索引

本文档索引 MTA-VHEP V0.2 概念设计模型链的全部仿真输出文件，按模型层级排列。所有文件为 **Model Output**，非认证级数据。

## V0.2-01 大气、燃料与基础气动

| 序号 | 文件路径 | 描述 | 报告章节 | 行/规模 | 证据角色 |
|------|----------|------|----------|---------|----------|
| T01 | `01_simulation/results/csv/atmosphere_table.csv` | ISA 大气参数表（0–12 km） | §7 概念级仿真模型 | 7 行 | 大气参数基准输入 |
| T02 | `01_simulation/results/csv/aero_check_table.csv` | 概念阻力极曲线和 stall speed vs CLmax | §7 概念级仿真模型 | 多行 | 概念气动参数，非 CFD |

## V0.2-02 发动机代理模型

| 序号 | 文件路径 | 描述 | 报告章节 | 行/规模 | 证据角色 |
|------|----------|------|----------|---------|----------|
| T03 | `01_simulation/results/csv/engine_design_points.csv` | 基准/自适应循环设计点对比 | §4 变循环涡扇 | 10 行 | 巡航 TSFC 方向性对比 |
| T04 | `01_simulation/results/csv/engine_power_extraction_sweep.csv` | 轴功率提取 penalty 扫描 | §4 变循环涡扇, §5 混合电系统 | 15 行 | 抽功 penalty 量化 |

## V0.2-03 混合电系统

| 序号 | 文件路径 | 描述 | 报告章节 | 行/规模 | 证据角色 |
|------|----------|------|----------|---------|----------|
| T05 | `01_simulation/results/csv/hybrid_timeline.csv` | 四阶段功率时间线 | §5 混合电系统, §6 多模态 | 4 行 | 功率需求和未满足负载 |
| T06 | `01_simulation/results/csv/hybrid_summary.csv` | SOC 边界、热负荷、未满足负载汇总 | §5 混合电系统 | 1 行 | 混合电系统关键指标 |
| T07 | `01_simulation/results/csv/electric_fan_mode_summary.csv` | 各风扇模式推力代理 | §5 混合电系统 | 4 行 | 风扇推力代理，非 CFD |
| T08 | `01_simulation/results/csv/fan_failure_cases.csv` | 风扇失效场景推力代理 | §5 混合电系统, §6 多模态 | 4 行 | 失效退化接口 |
| T09 | `01_simulation/results/csv/hybrid_power_extraction_proxy.csv` | 发电机抽功 penalty 接口 | §5 混合电系统 | 4 行 | 电-机耦合量化 |

## V0.2-04 分段任务求解器

| 序号 | 文件路径 | 描述 | 报告章节 | 行/规模 | 证据角色 |
|------|----------|------|----------|---------|----------|
| T10 | `01_simulation/results/csv/mission_summary.csv` | 三方案任务燃油对比 | §8 性能分析 | 3 行 | 表观燃油差量（约束告警） |
| T11 | `01_simulation/results/csv/mission_segments.csv` | 逐段推力/燃油/SOC 明细 | §8 性能分析 | 18 行 | 分段诊断数据 |
| T12 | `01_simulation/results/csv/weight_breakdown.csv` | 重量分解与 MTOW 裕度 | §2 总方案, §8 性能分析 | 3 行 | MTOW vs 初始假设 |
| T13 | `01_simulation/results/csv/mission_diagnostics.csv` | 逐段推力裕度诊断 | §8 性能分析 | 18 行 | 约束定量依据 |
| T14 | `01_simulation/results/csv/mission_case_status.csv` | 方案结论状态 | §8 性能分析 | 3 行 | 计算闭合确认 |
| T15 | `01_simulation/results/csv/mission_constraint_violations.csv` | 约束告警逐段明细 | §8 性能分析 | 多行 | 约束类型和量值 |
| T16 | `01_simulation/results/csv/takeoff_landing_proxy.csv` | 起飞/着陆代理指标 | §8 性能分析 | 3 行 | 方向性起飞比较 |
| T17 | `01_simulation/results/csv/takeoff_landing_proxy_components.csv` | 代理指标组件分解 | §8 性能分析 | 3 行 | 推力/重量/CLmax 分解 |

## V0.2-04S 进近/着陆段审计

| 序号 | 文件路径 | 描述 | 报告章节 | 行/规模 | 证据角色 |
|------|----------|------|----------|---------|----------|
| T18 | `01_simulation/results/csv/approach_landing_diagnostics.csv` | 进近着陆段推力裕度审计 | §8 性能分析 | 多行 | 进近模型公式敏感性依据 |
| T19 | `01_simulation/results/csv/approach_sensitivity_scan.csv` | 进近敏感性参数扫描 | §8 性能分析 | 多行 | 进近模型参数敏感度 |

## V0.2-05/Q/Q2 敏感性分析

| 序号 | 文件路径 | 描述 | 报告章节 | 行/规模 | 证据角色 |
|------|----------|------|----------|---------|----------|
| T20 | `01_simulation/results/csv/sensitivity_summary.csv` | 225 行敏感性案例摘要 | §8 性能分析 | 225 行 | 参数扫描全部结果 |
| T21 | `01_simulation/results/csv/sensitivity_case_details.csv` | 逐案设计变量配置 | §8 性能分析 | 225 行 | 变量值和限制段 |
| T22 | `01_simulation/results/csv/sensitivity_constraints.csv` | 三级约束逐段分解 | §8 性能分析 | 1832 行 | 约束分类明细 |
| T23 | `01_simulation/results/csv/sensitivity_best_candidates.csv` | 诊断性候选列表 | §8 性能分析 | 11 行 | 候选筛选输出 |
| T24 | `01_simulation/results/csv/sensitivity_tornado_data.csv` | 敏感性龙卷风图数据 | §8 性能分析 | 多行 | 关键参数影响排序 |
| T25 | `01_simulation/results/csv/sensitivity_corrected_constraint_summary.csv` | 约束重分类汇总 | §8 性能分析 | 11 行 | 三级约束计数 |
| T26 | `01_simulation/results/csv/sensitivity_approach_classification.csv` | 逐行仅进近 vs 全段分类 | §8 性能分析 | 225 行 | 进近模型敏感标志 |
| T27 | `01_simulation/results/csv/sensitivity_field_semantics_audit.csv` | 字段语义审计 | §8 性能分析 | 7 行 | 字段定义和修正记录 |
| T28 | `01_simulation/results/csv/sensitivity_feasibility_reclassified.csv` | 可行性重分类 | §8 性能分析 | 225 行 | 三级可行性标志 |
| T29 | `01_simulation/results/csv/sensitivity_non_approach_constraints.csv` | 非进近约束驱动因子 | §8 性能分析 | 225 行 | 下降段/起飞段约束驱动因 |
| T30 | `01_simulation/results/csv/sensitivity_consistency_audit_summary.csv` | 一致性审计汇总 | §8 性能分析 | 9 行 | 名义回放和单调性检查 |
| T31 | `01_simulation/results/csv/sensitivity_nominal_replay_comparison.csv` | V0.2-04S vs V0.2-05Q2 回放 | §8 性能分析 | 3 行 | 仅进近修正精度验证 |
| T32 | `01_simulation/results/csv/corrected_approach_input_decomposition.csv` | 仅进近修正输入分解 | §8 性能分析 | 多行 | 修正计算输入追溯 |
| T33 | `01_simulation/results/csv/engine_thrust_monotonicity_audit.csv` | 推力单调性审计数据 | §4 变循环涡扇, §8 性能分析 | 多行 | 推力单调性检查通过 |

## 使用说明

1. 所有 CSV 文件为概念级仿真模型输出，标注为 Model Output
2. 行数基于当前版本（V0.2-05Q2），后续版本可能变化
3. 引用 CSV 数据时须同时注明其约束告警状态或诊断性质
4. 任何 CSV 输出均不构成认证级性能数据或最终设计验证
