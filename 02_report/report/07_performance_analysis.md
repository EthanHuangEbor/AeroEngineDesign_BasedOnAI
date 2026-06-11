# 7. 性能分析

## 7.1 分析框架

本章建立 V0.2 概念设计模型性能分析的框架性输出清单，用于规范仿真完成后的结果表达。所有数值结果在仿真完成前统一标注为 `待仿真结果填充`，不得编造或外推。

## 7.2 大气参数表

大气参数表（atmosphere table）用于建立标准大气条件下的环境参数基准，作为推进性能仿真的输入。

**状态**：`待仿真结果填充`

预期内容包括：
- 不同高度下的温度、压力、密度、声速
- 国际标准大气（ISA）偏差修正因子
- 雷诺数修正系数

## 7.3 燃油消耗对比

燃油消耗对比（fuel burn comparison）用于评估混合电推进相比常规方案的燃油效率收益。

**状态**：`待仿真结果填充`

注意：
- 燃油消耗降低（fuel-burn reduction）**未经仿真验证**，不得声称已证明
- 当前框架仅用于记录对比结果，不构成性能保证

预期输出：
- 设计任务剖面总燃油消耗
- 与基准（常规涡扇）方案的对比
- 敏感性扫描结果

## 7.4 TSFC 模式图

推力比燃油消耗（Thrust Specific Fuel Consumption, TSFC）模式图记录变循环发动机在不同油门和第三流道调度下的比燃油消耗。

**状态**：`待仿真结果填充`

## 7.5 电池 SOC 剖面

电池 SOC（State of Charge）剖面记录混合电系统在设计任务中的电池充放电变化。

**状态**：`待仿真结果填充`

当前版本尚未实现 SOC动态管理模型。

## 7.6 起飞性能代理

起飞性能代理（takeoff proxy）用于估算起飞场长与主机推力、电动风扇功率的近似关系。

**状态**：`待仿真结果填充`

**注意**：起飞性能代理结果**不构成 STOL 能力保证**，不得声称已实现短距起降。

## 7.7 敏感性龙卷风图

敏感性龙卷风图（sensitivity tornado）用于展示关键设计参数对任务燃油消耗的影响程度。

**状态**：`待仿真结果填充`

当前版本尚未实现敏感性分析。

预期分析的敏感性参数包括：
- 主机海平面静态推力
- 电动风扇总功率
- 翼面积
- 零升阻力系数
- 电池容量
- 轴功率提取 penalty

## 7.8 分析状态汇总

| 分析项 | 状态 | 说明 |
|--------|------|------|
| 大气参数表 | ✅ 已填充 | V0.2-01 ISA 大气模型（7.2节，7.8节） |
| 燃油消耗对比 | ✅ 已填充（约束告警） | V0.2-04 三方案对比（7.12节），不作为最终收益声明 |
| TSFC 模式图 | ✅ 已填充 | V0.2-02 TSFC 模式图（7.9节） |
| SOC 剖面 | ✅ 已填充 | V0.2-03 SOC 时间线（7.10节） |
| 起飞性能代理 | ✅ 已填充（代理指标） | V0.2-04 起飞/着陆代理（7.12节），非认证场长 |
| 敏感性龙卷风图 | ✅ 已填充 | V0.2-05/Q/Q2 敏感性分析、约束重分类与候选筛选（7.13节） |

## 7.8 V0.2-01 大气、燃料与基础气动模型输出

V0.2-01 层已完成以下建模工作，作为 V0.2 概念设计模型的基础层。

### 7.8.1 已生成的模型输出文件

| 文件路径 | 类型 | 支持的报告内容 | 不证明的内容 |
|----------|------|----------------|--------------|
| `results/csv/atmosphere_table.csv` | Model Output | 大气参数表（7.2节）的输入基准 | 推力、TSFC、任务性能 |
| `results/csv/aero_check_table.csv` | Model Output | 概念阻力极曲线、stall speed vs CLmax 关系 | 阻力极曲线非 CFD/风洞验证 |
| `figures/png/atmosphere_profile.png` | Model Output | 巡航高度大气剖面可视化 | 认证级噪声或性能预测 |
| `figures/png/stall_speed_vs_clmax.png` | Model Output | 低速增升辅助概念性分析 | STOL 能力已实现 |

### 7.8.2 大气模型（atmosphere_table.csv）

V0.2-01 已实现 ISA 大气模型（0–12 km 范围），输出包括：

| 高度 m | 温度 K | 压力 Pa | 密度 kg/m³ | 声速 m/s |
|--------|--------|---------|------------|----------|
| 0 | 288.15 | 101325 | 1.225 | 340.29 |
| 1000 | 281.65 | 89875 | 1.112 | 336.43 |
| 3000 | 268.65 | 70109 | 0.909 | 328.58 |
| 6000 | 249.15 | 47181 | 0.660 | 316.43 |
| 9000 | 229.65 | 30742 | 0.466 | 303.79 |
| 10668 | 218.81 | 23842 | 0.380 | 296.54 |
| 12000 | 210.15 | 19284 | 0.320 | 290.61 |

**状态**：Model Output — ISA 大气模型已实现，覆盖0–12 km范围，采用简单对流层 lapse rate 模型。

**不证明**：该大气模型为概念层，不适用于认证级性能计算或适航审定。

### 7.8.3 燃料性质辅助模块

V0.2-01 已实现 Jet-A / SAF 燃料性质辅助函数，提供密度、热值等基础参数查询。

**状态**：Model Output — 燃料性质辅助模块已实现，用于场景建模。

**不证明**：燃料性质模块不等于 SAF 认证或生命周期碳排放分析，不得声称 SAF 实现碳中和。

### 7.8.4 概念阻力极曲线（aero_check_table.csv）

V0.2-01 采用概念阻力极曲线公式：`CD = CD0 + k × CL²`

当前使用的阻力系数：

| 配置 | CD0 | k |
|------|-----|---|
| clean | 0.026 | 待气动仿真验证 |
| takeoff_flap | 0.054 | 待气动仿真验证 |
| landing_flap | 0.109 | 待气动仿真验证 |

起落架阻力增量使用占位符常数：`ΔCD = +0.020`

**状态**：Model Output — 概念阻力极曲线已实现。

**不证明**：该阻力极曲线为概念阶段假设，非 CFD、风洞数据或认证性能，不得作为适航依据。

### 7.8.5 Stall Speed 与 CLmax 关系（aero_check_table.csv）

V0.2-01 已建立 stall speed 与 CLmax 的概念关系：

| CLmax | stall speed m/s（clean, W=858082 N, S=160 m²） |
|-------|-----------------------------------------------|
| 1.55 | 135.0 |
| 1.67 | 130.1 |
| 1.79 | 125.6 |
| 1.91 | 121.6 |

随着 CLmax 增加，stall speed 下降，验证了概念层面的增升关系。

**状态**：Model Output — stall speed 随 CLmax 增加而下降的关系已建立。

**不证明**：吹气襟翼增升系数（blowing momentum coefficient）仍为占位符，不得声称 STOL 能力已实现。

### 7.8.6 吹气襟翼占位符

吹气襟翼系数（blowing momentum coefficient）存储于 `config/aero_model.yaml`，为概念占位符，用于后续气动仿真验证。

**状态**：占位符，非验证数据。

**不证明**：吹气襟翼输出仅作为代理模型输入，不得作为认证级 STOL 预测。

### 7.8.7 V0.2-01 与 V0.2-02 的关系

|层级 | 状态 | 说明 |
|------|------|------|
| V0.2-01 环境/燃料/基础气动 | ✅ 已完成 | 本节所述内容 |
| V0.2-02 发动机代理模型 | ✅ 已完成 | 提供推力/TSFC/抽功 penalty |
| V0.2-03 混合电系统/电气总线/SOC | ⏳ 未完成 | 等待 V0.2-02 结果输入 |
| V0.2-04 分段任务剖面求解器 | ✅ 已完成（约束告警） | 诊断输出，不作为最终收益声明 |
| V0.2-05 敏感性分析 | ⏳ 未完成 | 等待 V0.2-04 结果输入 |

### 7.9 V0.2-02 发动机设计点与抽功惩罚输出

V0.2-02 层已完成以下发动机代理模型输出，为 V0.2-03 任务剖面求解器提供发动机性能接口。

#### 7.9.1 数据规模

| 输出文件 | 行数 | 说明 |
|----------|------|------|
| `engine_design_points.csv` | 10 行数据 | 基准/自适应循环各工作点 |
| `engine_power_extraction_sweep.csv` | 15 行数据 | 轴功率提取扫描（每设计点 0/0.5/1.0/2.0/3.0 MW） |

#### 7.9.2 输出图表

| 图表 | 内容 |
|------|------|
| `figures/png/tsfc_mode_map.png` | TSFC 模式图 |
| `figures/png/thrust_lapse_map.png` | 推力 lapse 地图 |
| `figures/png/power_extraction_penalty.png` | 轴功率提取 penalty |

#### 7.9.3 这些输出支持的内容

1. **基准/自适应循环对比**：巡航 TSFC 对比（自适应循环低于基准约14.6%）用于概念级趋势分析
2. **发动机性能曲线（engine deck）**：为 V0.2-03 任务求解器提供输入
3. **轴功率提取 penalty 接口**：抽功 penalty 量化为 V0.2-03 混合电系统耦合提供接口

#### 7.9.4 这些输出不证明的内容

1. **不得声称已验证的燃油消耗降低**：须待 V0.2-04 任务剖面求解后才有意义
2. **不得声称认证级发动机性能**：代理模型 TSFC 来自 YAML 配置占位符
3. **轴功率提取非真实轴系匹配**：抽功 penalty 为功率等价代理
4. **第三流道效应为参数化调度乘子**：非经验证的循环物理

### 7.10 V0.2-03 混合电时间线、SOC 与风扇失效输出

V0.2-03 层已完成混合电系统与电气总线模型输出，为 V0.2-04 分段任务剖面求解器提供电气功率时间线和 SOC 边界。

#### 7.10.1 数据规模

| 输出文件 | 内容 |
|----------|------|
| `hybrid_timeline.csv` | 4 阶段功率时间线（起飞/初始爬升/巡航/进近） |
| `hybrid_summary.csv` |汇总：SOC 边界、热负荷、未满足负载 |
| `electric_fan_mode_summary.csv` | 各风扇模式推力代理 |
| `fan_failure_cases.csv` | 风扇失效场景推力代理 |
| `hybrid_power_extraction_proxy.csv` | 发电机抽功 penalty 接口 |

#### 7.10.2 输出图表

| 图表 | 内容 |
|------|------|
| `electric_power_soc.png` | SOC 时间线（4 阶段） |
| `electric_fan_thrust_proxy.png` | 风扇推力代理（assist/degraded/off） |
| `hybrid_thermal_load.png` | 热负荷时间线 |
| `fan_failure_power_available.png` | 失效场景功率可用性 |

#### 7.10.3 这些输出支持的内容

1. **任务求解器功率时间线**：`hybrid_timeline.csv` 为 V0.2-04 提供各阶段电气功率需求
2. **SOC 边界**：进近阶段 SOC 降至 0.20（安全保障下限），定义了电池放电极限
3. **电动辅助开/关对比**：assist vs off模式推力代理差异，用于定性增升分析
4. **风扇失效退化接口**：`fan_failure_cases.csv` 定义了4 种失效场景的推力代理
5. **发电机抽功接口**：通过 `hybrid_power_extraction_proxy.csv` 连接到 V0.2-02 发动机模型

#### 7.10.4关键数值（来自 CSV）

| 参数 | 值 | 来源 |
|------|------|------|
| 时间线阶段数 | 4 | hybrid_summary.csv |
| SOC 最小值 | 0.20 | hybrid_summary.csv |
| SOC 最大值 | 0.90 | hybrid_summary.csv |
| 峰值总风扇推力代理 | 35750.4 N | fan_failure_cases.csv（全风扇可用，assist） |
| 峰值热负荷 | 464573.3 W | hybrid_summary.csv |
| 总未满足负载能量 | 131285.7 Wh | hybrid_summary.csv |

#### 7.10.5 这些输出不证明的内容

1. **不得声称 STOL 改进**：风扇推力代理（`P_shaft/v`）非 CFD 或风洞验证，不得作为 STOL 能力证明
2. **不得声称区块燃油消耗结果**：须待 V0.2-04 任务剖面求解后才有意义
3. **不得声称声学验证**：无声学模型输出
4. **不得声称认证级热安全设计**：热负荷为集总参数估算，非换热器设计验证

#### 7.10.6 V0.2-03 与后续层级的关系

| 层级 | 状态 | 接口 |
|------|------|------|
| V0.2-04 分段任务剖面求解器 | ✅ 已完成（约束告警） | 使用 V0.2-03 功率时间线和 SOC 边界 |
| V0.2-05 敏感性分析 | ⏳ 待开始 | 使用 V0.2-04 结果 |

### 7.11 参数来源

本章所有分析项在仿真完成前均为 **Model Output** 占位符，来源为后续仿真工作的输出结果。

### 7.12 V0.2-04 分段任务求解器输出

V0.2-04 层已完成分段任务求解器（segmented mission solver），对三个方案（baseline_fixed_cycle_turbofan / adaptive_cycle_turbofan / adaptive_cycle_plus_hybrid_electric）进行了准稳态分段任务仿真。**所有结果均为带约束告警的模型输出（Model Output），不作为最终收益声明。**

#### 7.12.1 三方案任务燃油对比

| 参数 | baseline_fixed_cycle_turbofan | adaptive_cycle_turbofan | adaptive_cycle_plus_hybrid_electric |
|------|------------------------------|------------------------|-------------------------------------|
| 任务燃油 mission_fuel_kg | 13712.67 | 11946.35 | 12443.23 |
| 轮档燃油 block_fuel_kg | 12696.91 | 11061.43 | 11521.50 |
| 备油 reserve_fuel_kg | 1015.75 | 884.91 | 921.72 |
| 电能 electric_energy_Wh | 0 | 0 | 1009366.38 |
| 峰值电功率 max_electric_power_W | 0 | 0 | 4000000.0 |
| 峰值热负荷 max_thermal_load_W | 0 | 0 | 464573.28 |
| 约束告警 constraint_violations | low_thrust_margin | low_thrust_margin | low_thrust_margin;unmet_electric_load |
| 结论状态 conclusion_status | diagnostic_only_constraint_flagged | diagnostic_only_constraint_flagged | diagnostic_only_constraint_flagged |

**表观燃油差量 vs 基准（apparent fuel deltas）**：

| 方案 | 表观燃油差量 | 标注 |
|------|------------|------|
| adaptive vs baseline | -12.88% | **带约束告警的模型输出，不作为最终收益声明** |
| hybrid vs baseline | -9.26% | **带约束告警的模型输出，不作为最终收益声明** |

注意：hybrid 方案表观燃油差量（-9.26%）幅度小于 adaptive-only 方案（-12.88%），原因是混合电系统 4200 kg 质量惩罚增加了全航段燃油消耗。

#### 7.12.2 重量分解与 MTOW 裕度

| 参数 | baseline | adaptive | hybrid |
|------|----------|----------|--------|
| 有效载荷 payload_kg | 25000.0 | 25000.0 | 25000.0 |
| 使用空重 oew_kg | 52000.0 | 52000.0 | 52000.0 |
| 主机质量 main_engines_kg | 4400.0 | 4400.0 | 4400.0 |
| 混合电固定质量 hybrid_fixed_mass_kg | 0 | 0 | 1200.0 |
| 混合电功率质量 hybrid_power_mass_kg | 0 | 0 | 1000.0 |
| 电池质量 battery_mass_kg | 0 | 0 | 2000.0 |
| 混合电总质量 hybrid_total_mass_kg | 0 | 0 | 4200.0 |
| 燃油质量 fuel_kg | 13714.99 | 11948.72 | 12443.23 |
| **估算 MTOW estimated_mtow_kg** | **90714.99** | **88948.72** | **93643.23** |
| MTOW 裕度（vs 初始 87500 kg） | -3214.99 | -1448.72 | -6143.23 |
| MTOW 裕度（vs V0.1 上限 95000 kg） | 4285.01 | 6051.28 | 1356.77 |
| 在 V0.1 MTOW 范围内 | 是 | 是 | 是 |

**关键观察**：
- 全部三个方案的 estimated MTOW 均超出初始 MTOW 假设 87500 kg
- hybrid 方案 estimated MTOW 93643.23 kg，距 V0.1 上限 95000 kg 仅余 1356.77 kg
- hybrid 方案 MTOW 裕度紧张，需在 V0.2-05 敏感性分析中迭代

#### 7.12.3 约束讨论

**low_thrust_margin（推力裕度不足）**：

全部三个方案均存在 low_thrust_margin 约束告警，最严重段为 approach_landing：
- baseline approach_landing: -104611.56 N
- adaptive approach_landing: -102980.48 N
- hybrid approach_landing: -146505.56 N

此外，hybrid 方案的 climb 段也存在 low_thrust_margin（-2295.39 N）。

推力裕度不足表明当前推力/阻力模型假设需要细化，可能的调整方向包括：
- 主机推力调度优化
- 阻力模型修正（进近构型 CD0、起落架阻力增量）
- 进近速度/构型调整
- 以上均需在 V0.2-05 敏感性分析中评估

**unmet_electric_load（未满足电负荷）**：

仅 hybrid 方案存在 unmet_electric_load：
- 进近段（approach_landing）：287117.04 Wh
- 峰值未满足功率代理：约 2153377.8 W

未满足电负荷表明进近阶段电动风扇 assist 模式的功率需求超过电池和发电机的联合供给能力。可能需要调整：
- 进近阶段电动风扇功率分配策略
- 电池容量或发电机容量
- SOC 调度策略
- 以上均需在 V0.2-05 敏感性分析中评估

**对 V0.2-05 敏感性分析的影响**：
- 约束消除（constraint removal）是 V0.2-05 的核心目标之一
- 在约束消除前，所有表观燃油差量不得作为最终收益声明
- 敏感性分析应扫描推力、阻力、混合电功率、电池容量等关键参数对约束状态和燃油消耗的影响

#### 7.12.4 起飞/着陆代理讨论

起飞/着陆代理指标（takeoff/landing proxy index）为概念级方向性比较工具，**非认证场长**。

| 方案 | 起飞代理指数 | 着陆代理指数 | 方向性 |
|------|------------|------------|--------|
| baseline | 7857.67 | 1291.94 | 参考基准 |
| adaptive | 7230.17 | 1287.75 | 方向性优于 baseline |
| hybrid | 9405.57 | 1347.75 | 方向性差于 baseline |

**分析**：
- 代理指数越低，方向性越好
- adaptive 方案得益于更高的有效推力（228270.48 N vs 218466.78 N）和较低的起飞重量，起飞代理最优
- hybrid 方案起飞代理指数 9405.57 > baseline 7857.67，说明 4200 kg 混合电系统质量惩罚主导了起飞代理，尽管 hybrid 方案有 35750.4 N 电动风扇推力辅助和更高的有效 CLmax（2.545 vs 2.35）
- hybrid 方案起飞有效推力仅 179589.94 N（因轴功率提取 penalty 显著降低主机推力），低于 baseline 的 218466.78 N

**注意**：
- 起飞/着陆代理指标**不构成认证场长**
- 混合电方案起飞代理恶化是质量惩罚的直接后果，需在 V0.2-05 中评估质量预算优化空间
- 着陆代理指数 hybrid（1347.75）同样差于 baseline（1291.94），着陆有效推力仅 52183.75 N（baseline 75526.42 N）

#### 7.12.5 V0.2-04 输出文件清单

| 输出文件 | 类型 | 支持的报告内容 | 不证明的内容 |
|----------|------|----------------|--------------|
| `results/csv/mission_summary.csv` | Model Output | 三方案任务燃油对比 | 经验证的燃油消耗降低 |
| `results/csv/mission_segments.csv` | Model Output | 分段推力/燃油/SOC | 认证级航程 |
| `results/csv/weight_breakdown.csv` | Model Output | MTOW 分解与裕度 | 最终可行 sizing |
| `results/csv/mission_constraint_violations.csv` | Model Output | 约束告警清单 | 约束已消除 |
| `results/csv/mission_diagnostics.csv` | Model Output | 逐段诊断数据 | 认证级性能 |
| `results/csv/mission_case_status.csv` | Model Output | 方案结论状态 | 最终收益声明 |
| `results/csv/takeoff_landing_proxy.csv` | Model Output | 起飞/着陆代理对比 | 认证场长或 STOL 能力 |
| `results/csv/takeoff_landing_proxy_components.csv` | Model Output | 代理指标组件分解 | 认证场长或 STOL 能力 |
| `figures/png/mission_profile.png` | Model Output | 任务剖面可视化 | — |
| `figures/png/fuel_burn_comparison.png` | Model Output | 燃油对比可视化 | — |
| `figures/png/mission_energy_breakdown.png` | Model Output | 能量分解可视化 | — |
| `figures/png/takeoff_proxy_comparison.png` | Model Output | 起飞代理可视化 | — |

#### 7.12.6 V0.2-04 与 V0.2-05 的关系

| 层级 | 状态 | 说明 |
|------|------|------|
| V0.2-04 分段任务剖面求解器 | ✅ 已完成（约束告警） | 本节所述内容 |
| V0.2-05 敏感性分析 | ✅ 已完成（约束告警） | 本节所述内容 |
| V0.2-05Q 一致性审计 | ✅ 已完成 | 推力单调性和名义回放检查 |
| V0.2-05Q2 字段语义修复 | ✅ 已完成 | 分离仅进近修正和全段修正约束 |

### 7.13 V0.2-05/Q/Q2 敏感性分析、约束重分类与候选筛选

V0.2-05/Q/Q2 阶段完成了完整的敏感性扫描、一致性审计和字段语义修复，对 225 行敏感性案例进行了三级约束分类（原始、仅进近修正、全段修正），并筛选出 92 个仅进近修正候选方案和 0 个全段可行方案。**所有结果均为诊断性模型输出，不作为最终设计验证。**

#### 7.13.1 敏感性分析摘要

| 指标 | 值 | 说明 |
|------|-----|------|
| 总敏感性案例数 | 225 | 10 个设计变量 OAT 扫描 + 24 个混合电网格扫描 |
| 原始低推力告警数量 | 225 | 使用原始任务求解器约束分类 |
| 仅进近修正后低推力数量 | 121 | 使用 V0.2-04S 下降力平衡修正仅进近段分类 |
| 全段修正后低推力数量 | 225 | 进近修正 + 非进近段约束均纳入 |
| 进近模型敏感数量 | 104 | 原始进近限制但仅进近修正后清除的低推力案例 |
| 可行性基本原始数量 | 0 | 原始约束下无任何案例通过基本筛选 |
| 可行性基本仅进近修正数量 | 92 | 仅进近修正后通过基本筛选的案例数 |
| 可行性基本全段修正数量 | 0 | 全段修正后通过基本筛选的案例数（无） |
| 混合电未满足电负荷行数 | 69 | 混合电方案（hybrid）存在未满足电负荷的行数 |
| MTOW 超限行数 | 67 | 超出配置 MTOW 上限的行数 |
| 名义回放一致性 | 3/3 一致（≤ 1000 N） | V0.2-05Q2 仅进近修正裕度与 V0.2-04S 一致 |
| 推力单调性检查 | 6/6 通过 | 115000 / 130000 / 150000 N/台 推力单调性通过 |

#### 7.13.2 三级约束分类体系解释

V0.2-05Q2 引入了三级约束分类体系，明确区分不同置信度的约束信号：

**A. 原始任务约束（raw_all_segment_min_thrust_margin_N）**
- 来源：任务求解器直接输出的全段最小推力裕度
- 问题：进近着陆段的推力裕度使用了准稳态水平力平衡公式，该公式在下降进近条件下低估了可用推力
- 原始低推力计数 225 行**不能单独解读**，因为进近段约束可能受模型公式敏感性影响

**B. 仅进近修正约束（approach_only_corrected_margin_N）**
- 来源：使用 V0.2-04S 下降力平衡公式重新计算的仅进近段裕度
- 范围：**仅**替换进近着陆段的约束判断，非进近段保持原始约束不变
- 仅进近修正低推力计数 121 行，其中 104 行（121−225 的差值，即 225−121=104）的原始进近约束被识别为进近模型敏感
- **重要**：仅进近修正候选（92个）为诊断性筛选输出，**不作为最终可行设计**，因为非进近段约束未纳入考察

**C. 全段修正约束（corrected_all_segment_min_thrust_margin_N）**
- 来源：取 `approach_only_corrected_margin_N` 和 `non_approach_min_thrust_margin_N` 的最小值
- 范围：进近修正 + 非进近段（爬升/巡航/下降/起飞）约束同时纳入
- 全段修正低推力计数 225 行——说明全部案例在至少一个非进近段存在低推力裕度
- 全段修正可行性计数 0——**当前无任何设计点满足所有航段推力裕度要求**

#### 7.13.3 约束重分类表（表 A）

| 约束维度 | 涉及行数 | 说明 |
|----------|----------|------|
| 原始低推力（raw_low_thrust_margin） | 225 / 225 | 原始任务求解器全段低推力计数 |
| 仅进近修正低推力（approach_only_corrected_low_thrust_margin） | 121 / 225 | 仅进近段使用 V0.2-04S 下降力平衡修正 |
| 全段修正低推力（corrected_all_segment_low_thrust_margin） | 225 / 225 | 进近修正 + 非进近段约束同时纳入 |
| 进近模型敏感（approach_model_sensitive） | 104 / 225 | 原始进近限制但仅进近修正后清除 |
| 尺度或调度低推力（sizing_or_schedule_low_thrust） | 225 / 225 | 进近模型修正后仍存在的低推力（非进近段主导） |
| 未满足电负荷（unmet_electric_load） | 69 / 225 | 混合电方案的电负荷缺口（未被进近修正改变） |
| MTOW 超限（mtow_exceeded） | 67 / 225 | 超出配置 MTOW 上限 |
| 可行性基本原始 | 0 / 225 | 原始约束下无案例通过 |
| 可行性基本仅进近修正 | 92 / 225 | 仅进近修正后 92 个案例通过基本筛选 |
| 可行性基本全段修正 | 0 / 225 | 全段修正后无案例通过基本筛选 |

#### 7.13.4 候选类别表（表 B）

V0.2-05Q2 将全部 225 行分为以下候选类别：

| 候选类别 | 计数 | 定义 | 状态 |
|----------|------|------|------|
| 全段不可行（all_segment_infeasible） | 225 | 全段修正后至少一个非进近段存在低推力裕度 | 全部案例均属此类 |
| 仅进近修正候选（approach_corrected_only_candidate） | 92 | 仅进近修正后进近约束清除，但非进近段约束仍存在 | 诊断性筛选，非可行设计 |
| 进近模型敏感案例（approach_model_sensitive） | 104 | 原始进近限制但仅进近修正后清除 | 说明进近模型公式敏感性 |
| 混合电未满足电负荷案例 | 69 | 混合电方案存在未满足电负荷 | 混合电调度/储能需调整 |
| 全段可行设计（all_segment_feasible） | 0 | 全段修正后所有约束均清除 | **尚不存在** |

**注意**：所有候选类别均为筛选输出（screening output only），**不得将任何候选行作为已验证的设计点呈现**。

#### 7.13.5 最佳候选表（表 C）

以下为仅进近修正后燃料最低的前 5 个候选方案（全部受非进近段约束限制）：

| case_id | propulsion_case | 关键设计变量 | mission_fuel_kg | approach_only_corrected_margin_N | corrected_all_segment_min_thrust_margin_N | 修正后限制段 | 候选类别 |
|---------|----------------|-------------|-----------------|-------------------------------|----------------------------------------|------------|----------|
| V05-0009_adaptive | adaptive_cycle_turbofan | cruise_ld=18 | 10786.15 | 18237.21 | -39796.59 | descent | approach_corrected_only_candidate |
| V05-0004_adaptive | adaptive_cycle_turbofan | cruise_tsfc_multiplier=0.9 | 11035.24 | 18228.41 | -39792.38 | descent | approach_corrected_only_candidate |
| V05-0008_adaptive | adaptive_cycle_turbofan | cruise_ld=17 | 11286.13 | 18207.11 | -39808.56 | descent | approach_corrected_only_candidate |
| V05-0148_hybrid | adaptive_cycle_plus_hybrid_electric | thrust=150000, cruise_ld=18, total_electric=0 | 11923.00 | 39390.40 | -36613.03 | descent | approach_corrected_only_candidate |
| V05-0149_hybrid | adaptive_cycle_plus_hybrid_electric | thrust=150000, cruise_ld=18, total_electric=0 | 11923.00 | 39390.40 | -36613.03 | descent | approach_corrected_only_candidate |

数据来源：`sensitivity_best_candidates.csv`。所有数值为 Model Output，不作为验证的性能声明。

#### 7.13.6 关键观察

**1. 原始低推力计数 225/225 不能单独解读**

全部 225 行在原始任务求解器约束下均为低推力告警——但这并不意味着设计不可行。V0.2-05Q2 证明了 104 行（46.2%）的进近段低推力与模型公式敏感性有关，在仅进近修正后清除。

**2. 仅进近修正候选 92 个不是最终可行设计**

仅进近修正后 92 个案例通过了基本筛选（无仅进近低推力、无未满足电负荷、在 MTOW 范围内），但这些候选的非进近段约束**仍然存在**：
- 主要限制段：下降（descent），受怠速代理推力和阻力平衡假设影响
- 次要限制段：起飞（takeoff），部分高电功率案例中起飞成为限制段

**3. 全段约束仍然存在——全段可行设计为 0**

全段修正后可行数为 0 的核心原因：
- 下降段：怠速推力代理无法满足下降段阻力平衡，这是当前模型中最顽固的非进近约束
- 起飞段：部分混合电案例中轴功率提取 penalty 导致起飞可用推力不足
- 巡航和爬升段：部分案例也存在低推力裕度

**4. 主导剩余非进近约束：下降段为主，起飞段为辅**

`sensitivity_non_approach_constraints.csv` 显示：
- 下降段为非进近限制段的行数：197 行（87.6%），疑似驱动因素均为 `descent_surrogate_idle_drag_balance`
- 起飞段为非进近限制段的行数：28 行（12.4%），与高电功率或低发电机容量相关

**5. 混合电未满足电负荷仍然显式存在**

69 行混合电方案存在未满足电负荷（287117 Wh 为主，部分案例因电池/发电机调整而变化）。电负荷约束独立于推力裕度分类，不受进近模型修正影响。

**6. 自适应循环燃油趋势为条件性模型趋势**

自适应循环方案（adaptive）在所有 OAT 扫描中显示方向性燃油优势（约 -12.9% 至 -21.3%相对于基准），但此趋势：
- 依赖于当前代理模型 TSFC 假设
- 受 descent 段约束限制
- **不得作为经验证的燃油消耗降低呈现**

**7. 混合电方案受质量/电负荷/全段裕度三重约束**

混合电方案（hybrid）的表观燃油差量（约 -0.3%至 -15.8%）同时受：
- 下降段推力裕度不足
- 进近段电负荷未满足
- 混合电系统质量惩罚（4200 kg）
- MTOW 裕度紧张（hybrid 方案约 93643 kg）

#### 7.13.7 灵敏度分析输出文件

| 输出文件 | 类型 | 支持的报告内容 | 不证明的内容 |
|----------|------|----------------|--------------|
| `sensitivity_summary.csv` | Model Output | 225 行敏感性案例摘要 | 已验证的可行设计 |
| `sensitivity_case_details.csv` | Model Output | 逐案设计变量配置 | 最优方案 |
| `sensitivity_constraints.csv` | Model Output | 三级约束逐段分解 | 约束已消除 |
| `sensitivity_best_candidates.csv` | Model Output | 诊断性候选列表 | 最终可行方案 |
| `sensitivity_corrected_constraint_summary.csv` | Model Output | 约束重分类汇总 | 验证的设计点 |
| `sensitivity_approach_classification.csv` | Model Output | 逐行仅进近 vs 全段分类 | 最终可行性 |
| `sensitivity_field_semantics_audit.csv` | Model Output | 字段语义审计 | — |
| `sensitivity_feasibility_reclassified.csv` | Model Output | 可行性重分类 | 验证的设计 |
| `sensitivity_non_approach_constraints.csv` | Model Output | 非进近约束驱动因子 | 约束消除 |
| `sensitivity_consistency_audit_summary.csv` | Model Output | 一致性审计汇总 | — |
| `sensitivity_nominal_replay_comparison.csv` | Model Output | V0.2-04S vs V0.2-05Q2 回放 | — |
| `corrected_approach_input_decomposition.csv` | Model Output | 仅进近修正输入分解 | — |
| `approach_only_vs_all_segment_margin.png` | Model Output | 仅进近 vs 全段裕度对比 | — |
| `sensitivity_feasibility_reclassified.png` | Model Output | 可行性重分类可视化 | — |
| `non_approach_constraint_drivers.png` | Model Output | 非进近约束驱动因子 | — |
| `raw_vs_corrected_thrust_margin.png` | Model Output | 原始 vs 修正推力裕度 | — |
| `corrected_constraint_feasibility_map.png` | Model Output | 修正约束可行性地图 | — |
| `approach_model_sensitivity_classification.png` | Model Output | 进近模型敏感性分类 | — |
| `v04s_vs_v05r_margin_replay.png` | Model Output | V0.2-04S vs V0.2-05R 回放 | — |

#### 7.13.8 V0.2-05/Q/Q2 与 V0.3 的关系

| 层级 | 状态 | 说明 |
|------|------|------|
| V0.2-05 敏感性分析 | ✅ 已完成 | 本节所述内容 |
| V0.2-05Q 一致性审计 | ✅ 已完成 | 推力单调性和名义回放检查 |
| V0.2-05Q2 字段语义修复 | ✅ 已完成 | 分离仅进近修正和全段修正约束 |
| V0.3 sizing/细化 | ⏳ 必需后续工作 | 约束消解、尺寸迭代、设计点闭合 |