# 图表索引

本文档记录 MTA-VHEP V1.0 概念设计报告中引用的所有图表，按报告章节顺序排列。所有图表标注为 **Model Output**，非认证级性能数据。

| 序号 | 图路径 | 标题 | 报告章节 | 证据角色 | 不证明的内容 |
|------|--------|------|----------|----------|-------------|
| F01 | `01_simulation/figures/png/atmosphere_profile.png` | ISA 大气剖面（0–12 km） | §7 概念级仿真模型 | 大气参数基准 | 认证级大气模型 |
| F02 | `01_simulation/figures/png/stall_speed_vs_clmax.png` | 失速速度 vs CLmax 关系 | §2 总方案, §7 概念级仿真模型 | 低速增升概念关系 | CFD/风洞验证，STOL 认证 |
| F03 | `01_simulation/figures/png/tsfc_mode_map.png` | TSFC 模式图（基准 vs 自适应循环） | §4 变循环涡扇 | 巡航 TSFC 方向性对比 | 部件级循环验证，认证发动机性能 |
| F04 | `01_simulation/figures/png/thrust_lapse_map.png` | 推力随高度/马赫数变化图 | §4 变循环涡扇 | 推力 lapse 趋势 | 真实推力 deck 验证 |
| F05 | `01_simulation/figures/png/power_extraction_penalty.png` | 轴功率提取 penalty 曲线 | §4 变循环涡扇, §5 混合电系统 | 抽功 penalty 量化 | 真实 spool matching 验证 |
| F06 | `01_simulation/figures/png/electric_power_soc.png` | 电池 SOC 时间线（四阶段） | §5 混合电系统 | SOC 变化趋势和边界 | 电池详细设计，认证热管理 |
| F07 | `01_simulation/figures/png/electric_fan_thrust_proxy.png` | 电动风扇推力代理图 | §5 混合电系统 | 风扇推力代理方向性 | CFD/风洞推力验证，STOL 认证 |
| F08 | `01_simulation/figures/png/hybrid_thermal_load.png` | 混合电热负荷时间线 | §5 混合电系统 | 热负荷分布 | 认证级换热器设计 |
| F09 | `01_simulation/figures/png/fan_failure_power_available.png` | 风扇失效场景功率可用性 | §5 混合电系统, §6 多模态 | 失效退化接口 | 认证级故障安全分析 |
| F10 | `01_simulation/figures/png/mission_profile.png` | 设计任务剖面图 | §3 推进系统架构, §8 性能分析 | 任务剖面可视化 | 轨迹优化，认证航程 |
| F11 | `01_simulation/figures/png/fuel_burn_comparison.png` | 三方案燃油消耗对比 | §8 性能分析 | 方向性燃油差异 | 验证的燃油消耗降低 |
| F12 | `01_simulation/figures/png/mission_energy_breakdown.png` | 任务能量分解图 | §8 性能分析 | 能量流分配 | 能量自洽验证 |
| F13 | `01_simulation/figures/png/takeoff_proxy_comparison.png` | 起飞/着陆代理指标对比 | §8 性能分析 | 方向性起飞性能比较 | 认证场长，STOL 能力 |
| F14 | `01_simulation/figures/png/mission_constraint_status.png` | 任务约束状态图 | §8 性能分析 | 约束告警可视化 | 约束已消除 |
| F15 | `01_simulation/figures/png/approach_thrust_margin_audit.png` | 进近推力裕度审计 | §8 性能分析 | 进近段推力裕度诊断 | 认证着陆性能 |
| F16 | `01_simulation/figures/png/approach_sensitivity_scan.png` | 进近敏感性扫描 | §8 性能分析 | 进近段参数敏感性 | 最优进近方案 |
| F17 | `01_simulation/figures/png/constraint_tornado.png` | 约束敏感性龙卷风图 | §8 性能分析 | 关键约束参数识别 | 最优设计方向 |
| F18 | `01_simulation/figures/png/thrust_margin_vs_engine_rating.png` | 推力裕度 vs 主机推力等级 | §8 性能分析 | 推力对约束的影响 | 最优推力选择 |
| F19 | `01_simulation/figures/png/hybrid_power_sizing_map.png` | 混合电功率 sizing 地图 | §8 性能分析 | 混合电尺寸空间 | 最优功率配置 |
| F20 | `01_simulation/figures/png/pareto_fuel_vs_mtow.png` | Pareto 前沿：燃油 vs MTOW | §8 性能分析 | 设计权衡可视化 | 最终最优设计点 |
| F21 | `01_simulation/figures/png/takeoff_proxy_sensitivity.png` | 起飞代理指标敏感性 | §8 性能分析 | 起飞性能影响因子 | 认证起飞场长 |
| F22 | `01_simulation/figures/png/corrected_constraint_feasibility_map.png` | 修正约束可行性地图 | §8 性能分析 | 全段修正可行性分布 | 全段可行设计已验证 |
| F23 | `01_simulation/figures/png/raw_vs_corrected_thrust_margin.png` | 原始 vs 修正推力裕度对比 | §8 性能分析 | 三级约束分类可视化 | 约束已消除 |
| F24 | `01_simulation/figures/png/approach_model_sensitivity_classification.png` | 进近模型敏感性分类 | §8 性能分析 | 进近模型敏感案例分布 | 全段可行性 |
| F25 | `01_simulation/figures/png/approach_only_vs_all_segment_margin.png` | 仅进近 vs 全段裕度对比 | §8 性能分析 | 两级修正裕度关系 | 全段可行候选已验证 |
| F26 | `01_simulation/figures/png/sensitivity_feasibility_reclassified.png` | 可行性重分类柱状图 | §8 性能分析 | 三级可行性计数 | 候选已验证 |
| F27 | `01_simulation/figures/png/non_approach_constraint_drivers.png` | 非进近约束驱动因子分布 | §8 性能分析 | 下降段 vs 起飞段约束比例 | 约束已消解 |
| F28 | `01_simulation/figures/png/v04s_vs_v05r_margin_replay.png` | V0.2-04S vs V0.2-05R 裕度回放 | §8 性能分析 | 名义回放一致性 | 模型等效性 |
| F29 | `01_simulation/figures/png/engine_thrust_monotonicity_audit.png` | 发动机推力单调性审计 | §4 变循环涡扇, §8 性能分析 | 推力单调性验证 | 认证级推力映射 |

## 图表使用说明

1. 所有图表为概念级模型输出，不得作为认证性能数据
2. 图表中出现的数值均为代理模型输出或诊断性分析结果
3. 引用图表时须附带其"证据角色"和"不证明的内容"说明
4. 所有"约束告警"、"代理指标"、"诊断性"标注的图表不得用于最终性能声明
