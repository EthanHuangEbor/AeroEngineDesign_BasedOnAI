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
| 敏感性龙卷风图 | 待仿真结果填充 | 待 V0.2-05 敏感性分析 |

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
| V0.2-05 敏感性分析 | ⏳ 必需后续工作 | 约束消除与最终结论措辞选择 |