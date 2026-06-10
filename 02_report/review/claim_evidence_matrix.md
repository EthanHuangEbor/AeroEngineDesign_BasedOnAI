# 证据-声明矩阵

本文档追踪 MTA-VHEP V0.2 报告中所有关键声明的可追溯性。每条声明均标注来源类型，便于审查和审计。

## 声明来源类型定义

| 类型 | 缩写 | 说明 |
|------|------|------|
| Design Assumption | DA | 来自设计冻结决策或配置文件 |
| Model Output | MO | 来自仿真模型输出（V0.2 中均为占位符） |
| Literature/Source-Based Statement | LSB | 来自公开文献、数据表或适航文件 |
| Engineering Inference | EI | 基于工程判断的定性评估 |
| Future Work | FW | 属于未来升级路径，不计入当前设计 |

## 证据-声明列表

| 序号 | 声明内容 | 类型 | 来源/依据 | 状态 |
|------|----------|------|-----------|------|
| 1 | 25 t 有效载荷已冻结 | DA | aircraft_baseline.yaml | FROZEN |
| 2 | 3200 km 设计航程已冻结 | DA | aircraft_baseline.yaml | FROZEN |
| 3 | 主发动机数量为 2 台已冻结 | DA | aircraft_baseline.yaml, propulsion.yaml | FROZEN |
| 4 | 电动吹气襟翼风扇数量为 4 台已冻结 | DA | propulsion.yaml | FROZEN |
| 5 | Jet-A / SAF 为场景模型 | LSB | aircraft_baseline.yaml, README.md | 有效 |
| 6 | 氢燃料为未来升级路径 | DA | propulsion.yaml (future_hydrogen_enabled: false) | FW |
| 7 | 爆震推进为未来升级路径 | DA | propulsion.yaml (future_detonation_enabled: false) | FW |
| 8 | 电动风扇不作为巡航主推进手段 | EI | propulsion.yaml (cruise_operation: off_or_low_drag) | 有效 |
| 9 | 轴功率提取须计入推力 penalty | EI | propulsion.yaml (supports_shaft_power_extraction: true) | 待仿真 |
| 10 | STOL 能力未经仿真验证，不得声称已实现 | MO | 当前无仿真输出 | 待仿真 |
| 11 | 噪声降低未经仿真验证，不得声称已证明 | MO | 当前无仿真输出 | 待仿真 |
| 12 | 燃油消耗降低未经仿真验证，不得声称已证明 | MO | 当前无仿真输出 | 待仿真 |
| 13 | SAF 碳中和不得声称已实现 | LSB | SAF 为场景模型，非认证声明 | 有效 |
| 14 | 模型非认证等级 | DA | CLAUDE.md (certification_grade: false) | FROZEN |
| 15 | 阻力极曲线为概念阶段假设 | DA | aircraft_baseline.yaml (cd0_cruise_initial: 0.026) | 占位符 |
| 16 | 吹气襟翼增升系数为占位符 | MO | 当前无气动仿真输出 | 待仿真 |
| 17 | 任务求解器尚未实现 | EI | CLAUDE.md (excluded: mission_solver) | 待实现 |
| 18 | 发动机代理模型尚未实现 | EI | CLAUDE.md (excluded: propulsion_physics) | 待实现 |
| 19 | 混合电 SOC 模型尚未实现 | EI | CLAUDE.md (excluded: hybrid_electric_solver) | 待实现 |
| 20 | 敏感性分析尚未实现 | EI | CLAUDE.md (excluded: sensitivity_analysis) | 待实现 |
| 21 | 主机海平面静态推力初始值为 115000 N/台 | DA | propulsion.yaml | DA |
| 22 | 主机推力扫描范围为 100000–150000 N/台 | DA | propulsion.yaml | DA |
| 23 | 单台电动风扇功率初始值为 1000000 W | DA | propulsion.yaml | DA |
| 24 | 电动风扇总功率扫描范围为 0–8000000 W | DA | propulsion.yaml | DA |
| 25 | 总线电压初始值为 1500 V | DA | propulsion.yaml | DA |
| 26 | 发电机效率为 0.94 | EI | propulsion.yaml (Engineering Inference) | EI |
| 27 | 电机效率为 0.95 | EI | propulsion.yaml (Engineering Inference) | EI |
| 28 | 逆变器效率为 0.98 | EI | propulsion.yaml (Engineering Inference) | EI |
| 29 | 电池 SOC 最小值为 0.20 | DA | propulsion.yaml | DA |
| 30 | 电池 SOC 初始值为 0.90 | DA | propulsion.yaml | DA |
| 31 | 电池容量初始值为 500000 Wh | DA | propulsion.yaml | DA |
| 32 | 电池容量扫描范围为 0–1000000 Wh | DA | propulsion.yaml | DA |
| 33 | 巡航马赫数为 0.75 | DA | aircraft_baseline.yaml | FROZEN |
| 34 | 巡航高度为 10668 m | DA | aircraft_baseline.yaml | FROZEN |
| 35 | 最大马赫数为 0.80 | DA | aircraft_baseline.yaml | DA |
| 36 | 最大飞行高度为 12000 m | DA | aircraft_baseline.yaml | DA |
| 37 | 翼面积为 160.0 m² | DA | aircraft_baseline.yaml | DA |
| 38 | 展弦比为 9.5 | DA | aircraft_baseline.yaml | DA |
| 39 | 奥斯瓦尔德效率为 0.78 | DA | aircraft_baseline.yaml | DA |
| 40 | 零升阻力系数 CD0 为 0.026 | DA | aircraft_baseline.yaml | 占位符 |
| 41 | 升阻比范围为 13.0–18.0 | EI | aircraft_baseline.yaml (Engineering Inference) | EI |
| 42 | 起飞场长目标为 1700 m（TARGET，非保证值） | DA | aircraft_baseline.yaml | TARGET |
| 43 | 着陆场长目标为 1400 m（TARGET，非保证值） | DA | aircraft_baseline.yaml | TARGET |
| 44 | MTOW 初始值为 87500 kg | DA | aircraft_baseline.yaml | DA |
| 45 | OEW 初始值为 52000 kg | DA | aircraft_baseline.yaml | DA |
| 46 | 备油政策状态为 TBD | DA | mission_profile.yaml (status: TBD) | TBD |
| 47 | 主机支持轴功率提取 | DA | propulsion.yaml | FROZEN |
| 48 | 第三流道模型为参数化模型 | DA | propulsion.yaml | DA |
| 49 | 风扇压比范围为 1.05–1.25 | DA | propulsion.yaml | DA |
| 50 | 电动风扇定义三种故障模式 | DA | propulsion.yaml | FROZEN |
| 51 | V0.2 模型不得声称认证等级 | DA | CLAUDE.md | FROZEN |
| 52 | V0.2 数值结果均为占位符 | MO | 所有性能章节 | 占位符 |
| 53 | 氢燃料和爆震推进不计入当前需求 | FW | propulsion.yaml | FW |
| 54 | ISA 大气模型（0–12 km）已实现 | MO | V0.2-01 atmosphere_table.csv | 已填充 |
| 55 | 燃料性质辅助模块已实现 | MO | V0.2-01 燃料辅助函数 | 已填充 |
| 56 | 概念阻力极曲线已实现 | MO | V0.2-01 aero_check_table.csv | 占位符，非 CFD |
| 57 | stall speed 随 CLmax 增加而下降（概念关系） | MO | V0.2-01 aero_check_table.csv | 已验证趋势 |
| 58 | 吹气襟翼增升系数仍为占位符 | MO | config/aero_model.yaml | 待气动仿真 |
| 59 | 发动机代理模型尚未实现 | EI | CLAUDE.md (excluded: propulsion_physics) | 待 V0.2-02 |
| 60 | 任务求解器尚未实现 | EI | CLAUDE.md (excluded: mission_solver) | 待 V0.2-03 |
| 61 | 混合电 SOC 模型尚未实现 | EI | CLAUDE.md (excluded: hybrid_electric_solver) | 待 V0.2-04 |
| 62 | 敏感性分析尚未实现 | EI | CLAUDE.md (excluded: sensitivity_analysis) | 待 V0.2-05 |
| 63 | 无经验证的 STOL 结果 | MO | 当前无起飞场长仿真 | 不得声称 |
| 64 | V0.2-02 发动机代理模型已实现 | MO | engine_design_points.csv | 已完成 |
| 65 | 基准固定循环和自适应循环变体均已评估 | MO | engine_design_points.csv | 已完成 |
| 66 | 自适应循环巡航 TSFC 低于基准巡航 TSFC（代理模型） | MO | engine_design_points.csv | 低约14.6% |
| 67 | 起飞额定推力高于巡航额定推力（代理模型） | MO | engine_design_points.csv | 已验证趋势 |
| 68 | 轴功率提取降低净推力（代理模型） | MO | engine_power_extraction_sweep.csv | 已量化 penalty |
| 69 | 轴功率提取增加燃油流量（代理模型） | MO | engine_power_extraction_sweep.csv | 已量化增量 |
| 70 | 第三流道调度为参数化乘子，非经验证硬件设计 | LSB | engine_surrogate.yaml | 参数化 |
| 71 | 发动机代理模型不是部件级热力学循环模型 | LSB | model_limitations.md |概念代理 |
| 72 | 尚无任务燃油消耗结果 | MO | 当前无 mission_solver | 待 V0.2-04 |
| 73 | 尚无混合电 SOC 结果 | EI | CLAUDE.md (excluded) | 待 V0.2-03 |
| 74 | 轴功率提取 penalty 为功率等价代理，非真实 spool matching | LSB | model_limitations.md | 概念代理 |

## 声明追溯规则

1. **FROZEN 项**：已通过设计冻结审查，不得在未经过正式变更控制流程的情况下修改
2. **DA 项**：Design Assumption，可在设计迭代过程中更新，但须保持版本追踪
3. **MO 占位符项**：待相应仿真完成后替换为实际模型输出
4. **FW 项**：属于未来升级路径，在 V0.x 阶段不得作为当前性能声称的依据

## 审查要求

- 每条声明必须有明确的来源依据
- 报告正文中每条关键表述后应附注声明编号
- 仿真完成后，须逐一验证 MO 占位符项是否已更新