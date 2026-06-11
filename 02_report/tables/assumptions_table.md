# 假设表

本文档汇总 MTA-VHEP V0.2 概念设计模型中使用的所有关键设计假设，用于审查和变更追踪。

## 假设状态定义

| 状态 | 说明 |
|------|------|
| FROZEN | 已冻结，不得随意修改，须通过正式变更控制流程 |
| DA | Design Assumption，可在设计迭代中更新，须版本追踪 |
| TBD | 待确定，需要进一步分析或决策 |
| TBR | 待审查，需要相关方确认 |

## 飞机总体假设

| ID | 参数 | 值 | 状态 | 来源 |备注 |
|----|------|------|------|------|------|
| A-01 | 飞机级别 | 中型运输机 | FROZEN | 设计冻结 | 不得修改 |
| A-02 | 设计有效载荷 | 25000 kg | FROZEN | aircraft_baseline.yaml | 已冻结 |
| A-03 | 设计航程 | 3200 km | FROZEN | aircraft_baseline.yaml | 已冻结 |
| A-04 | 主发动机数量 | 2 台 | FROZEN | aircraft_baseline.yaml | 已冻结 |
| A-05 | 电动风扇数量 | 4 台 | FROZEN | propulsion.yaml | 已冻结 |
| A-06 | 巡航马赫数 | 0.75 | FROZEN | aircraft_baseline.yaml | 已冻结 |
| A-07 | 巡航高度 | 10668 m | FROZEN | aircraft_baseline.yaml | 已冻结 |
| A-08 | 最大马赫数 | 0.80 | DA | aircraft_baseline.yaml | 可更新 |
| A-09 | 最大飞行高度 | 12000 m | DA | aircraft_baseline.yaml | 可更新 |
| A-10 | MTOW 初始值 | 87500 kg | DA | aircraft_baseline.yaml | 扫描范围 80000–95000 kg |
| A-11 | OEW 初始值 | 52000 kg | DA | aircraft_baseline.yaml | 扫描范围 45000–58000 kg |
| A-12 | 翼面积 | 160.0 m² | DA | aircraft_baseline.yaml | 可优化 |
| A-13 | 展弦比 | 9.5 | DA | aircraft_baseline.yaml | 可优化 |
| A-14 | 奥斯瓦尔德效率 | 0.78 | EI | aircraft_baseline.yaml |估算值 |
| A-15 | 零升阻力系数 CD0 | 0.026 | EI | aircraft_baseline.yaml | 占位符，待 CFD 验证 |
| A-16 | 升阻比范围 | 13.0–18.0 | EI | aircraft_baseline.yaml | 估算范围 |
| A-17 | 起飞场长目标 | 1700 m | TARGET | aircraft_baseline.yaml | 目标值，非保证值 |
| A-18 | 着陆场长目标 | 1400 m | TARGET | aircraft_baseline.yaml | 目标值，非保证值 |

## 推进系统假设

| ID | 参数 | 值 | 状态 | 来源 | 备注 |
|----|------|------|------|------|------|
| P-01 | 发动机类型 | 三流道变循环涡扇 | FROZEN | propulsion.yaml | 已冻结 |
| P-02 | 海平面静态推力（初始值） | 115000 N/台 | DA | propulsion.yaml | 扫描范围 100000–150000 N/台 |
| P-03 | 是否支持轴功率提取 | 是 | FROZEN | propulsion.yaml | 已冻结 |
| P-04 | 第三流道模型 | 参数化模型 | DA | propulsion.yaml | 可升级为物理模型 |
| P-05 | 起飞油门 | 1.00 | DA | propulsion.yaml | 第三流道 0.10，喷管 0.85 |
| P-06 | 爬升油门 | 0.88 | DA | propulsion.yaml | 第三流道 0.15，喷管 0.70 |
| P-07 | 巡航油门 | 0.65 | DA | propulsion.yaml | 第三流道 0.40，喷管 0.55 |
| P-08 | 进近油门 | 0.35 | DA | propulsion.yaml | 第三流道 0.50，喷管 0.45 |
| P-09 | 怠速油门 | 0.10 | DA | propulsion.yaml | 第三流道 0.30，喷管 0.40 |
| P-10 | 未来氢燃料 | 未启用 | FROZEN | propulsion.yaml | future_hydrogen_enabled: false |
| P-11 | 未来爆震推进 | 未启用 | FROZEN | propulsion.yaml | future_detonation_enabled: false |
| P-12 | 使用燃料 | Jet-A / SAF | FROZEN | propulsion.yaml | 场景模型 |

## 电动系统假设

| ID | 参数 | 值 | 状态 | 来源 | 备注 |
|----|------|------|------|------|------|
| E-01 | 单台电动风扇功率（初始值） | 1000000 W | DA | propulsion.yaml | 扫描范围待确定 |
| E-02 | 总电动风扇功率扫描范围 | 0–8000000 W | DA | propulsion.yaml | 模型上限 8 MW |
| E-03 | 电动风扇角色 | 低速增升辅助 | FROZEN | propulsion.yaml | 非巡航主推进 |
| E-04 | 风扇压比范围 | 1.05–1.25 | DA | propulsion.yaml | 估算范围 |
| E-05 | 电机效率 | 0.95 | EI | propulsion.yaml | 工程估算 |
| E-06 | 逆变器效率 | 0.98 | EI | propulsion.yaml | 工程估算 |
| E-07 | 总线电压（初始值） | 1500 V | DA | propulsion.yaml | 扫描范围 1000–3000 V |
| E-08 | 发电机效率 | 0.94 | EI | propulsion.yaml | 工程估算 |
| E-09 | 电缆分配效率 | 0.985 | EI | propulsion.yaml | 工程估算 |
| E-10 | 电池容量（初始值） | 500000 Wh | DA | propulsion.yaml | 扫描范围 0–1000000 Wh |
| E-11 | 电池 SOC 最小值 | 0.20 | DA | propulsion.yaml | 安全限制 |
| E-12 | 电池 SOC 初始值 | 0.90 | DA | propulsion.yaml | 设计初值 |
| E-13 | 巡航期间电动风扇状态 | 关闭或低阻力 | DA | propulsion.yaml | 待详细设计确认 |

## 任务剖面假设

| ID | 参数 | 值 | 状态 | 来源 | 备注 |
|----|------|------|------|------|------|
| M-01 | 设计任务 | 有效载荷-航程任务 | FROZEN | mission_profile.yaml | 已冻结 |
| M-02 | 设计有效载荷（任务） | 25000 kg | FROZEN | mission_profile.yaml | 与飞机设计一致 |
| M-03 | 设计航程（任务） | 3200 km | FROZEN | mission_profile.yaml | 与飞机设计一致 |
| M-04 | 备油政策 | TBD | TBD | mission_profile.yaml | 待确定 |
| M-05 | 备油比例（初始值） | 0.08 | DA | mission_profile.yaml | 状态为 TBD |
| M-06 | 备降航段（初始值） | 200 km | TBR | mission_profile.yaml | 待确认 |
| M-07 | 滑行时间 | 900 s | DA | mission_profile.yaml | 估算值 |
| M-08 | 起飞速度 | 75 m/s | DA | mission_profile.yaml | 估算值 |
| M-09 | 进近速度 | 70 m/s | DA | mission_profile.yaml | 估算值 |

## 模型层级假设

| ID | 参数 | 值 | 状态 | 来源 | 备注 |
|----|------|------|------|------|------|
| L-05 | V0.2-01 基础层 | 已完成 | FROZEN | V0.2-01 输出 | ISA 大气、燃料辅助、概念气动 |
| L-06 | V0.2-02 发动机代理 | 已完成 | FROZEN | V0.2-02 输出 | TSFC、推力、轴功率 penalty（概念代理） |
| L-07 | V0.2-03 混合电系统/电气总线/SOC | 已完成 | FROZEN | V0.2-03 输出 | 功率时间线、SOC 边界、风扇失效 |
| L-08 | V0.2-04 分段任务剖面求解器 | 已完成 | Model Output | V0.2-04 输出 | 约束告警状态，不作为最终收益声明 |
| L-09 | V0.2-05 敏感性分析 | 已完成（诊断性） | Model Output | sensitivity_summary.csv | 225 行 OAT + 网格扫描，诊断性输出 |

## 敏感性分析假设（V0.2-05/Q/Q2）

| ID | 参数 | 值 | 状态 | 来源 | 备注 |
|----|------|------|------|------|------|
| S-01 | 敏感性扫描策略 | one_at_a_time + selected_grid | DA | sensitivity.yaml | 非全因子，OAT 为主 |
| S-02 | 总案例数 | 225 行 | Model Output | sensitivity_summary.csv | 含 3 个 baseline + 78 个 OAT + 144 个 selected_grid |
| S-03 | 设计变量数 | 10 个 | DA | sensitivity.yaml | 推力/TSFC/L/D/MTOW/电功率/电池容量/发电机功率/混合电质量系数/吹气襟翼/进近下降角 |
| S-04 | 主机推力扫描范围 | 115000 / 130000 / 150000 N/台 | DA | sensitivity.yaml | 3 个水平 |
| S-05 | 巡航 TSFC 乘子范围 | 0.90 / 1.00 / 1.10 | DA | sensitivity.yaml | 3 个水平 |
| S-06 | 巡航 L/D 范围 | 13.0 / 15.0 / 17.0 / 18.0 | DA | sensitivity.yaml | 4 个水平 |
| S-07 | MTOW 上限范围 | 87500 / 90000 / 95000 kg | DA | sensitivity.yaml | 3 个水平 |
| S-08 | 总电功率范围 | 0 / 2 / 4 / 6 / 8 MW | DA | sensitivity.yaml | 5 个水平 |
| S-09 | 电池容量范围 | 250000 / 500000 / 1000000 Wh | DA | sensitivity.yaml | 3 个水平 |
| S-10 | 发电机功率范围 | 2 / 4 / 6 / 8 MW | DA | sensitivity.yaml | 4 个水平 |
| S-11 | 混合电质量系数范围 | 150 / 250 / 400 kg/MW | DA | sensitivity.yaml | 3 个水平 |
| S-12 | 吹气襟翼 CLmax 增量分数 | 0.0 / 0.10 / 0.20 / 0.40 | DA | sensitivity.yaml | 4 个水平 |
| S-13 | 进近下降角范围 | -2.5° / -3.0° / -3.5° | DA | sensitivity.yaml | 3 个水平 |
| S-14 | 约束分类体系 | 三级：原始 / 仅进近修正 / 全段修正 | Model Output | sensitivity_corrected_constraint_summary.csv | V0.2-05Q2 字段语义修复后建立 |
| S-15 | 仅进近修正裕度定义 | V0.2-04S 下降力平衡公式计算仅进近段裕度 | DA | sensitivity_field_semantics_audit.csv | 可与 V0.2-04S approach_landing_diagnostics 回放 |
| S-16 | 全段修正裕度定义 | min(仅进近修正裕度, 非进近段最小原始裕度) | DA | sensitivity_field_semantics_audit.csv | 用于全段可行性判断 |
| S-17 | 可行性基本仅进近修正定义 | 无仅进近修正低推力 + 无未满足电负荷 + 在 MTOW 范围内 | DA | sensitivity_field_semantics_audit.csv | 诊断性筛选，忽略非进近段约束 |
| S-18 | 可行性基本全段修正定义 | 无全段修正低推力 + 无未满足电负荷 + 在 MTOW 范围内 | DA | sensitivity_field_semantics_audit.csv | 主要修正可行性代理 |
| S-19 | 候选类别定义 | all_segment_infeasible / approach_corrected_only_candidate / approach_model_sensitive | Model Output | sensitivity_best_candidates.csv | 全部候选标注 screening_only_no_validation_claim |
| S-20 | 候选不等于验证 | 任何候选类别均不作为已验证设计 | DA | CLAUDE.md | 所有候选为筛选输出 |
| S-21 | V0.3 为必需下一步 | 约束消解、尺寸迭代、设计点闭合 | FW | 10_conclusion.md | V0.3 sizing/细化 |

## 任务求解器假设（V0.2-04）

| ID | 参数 | 值 | 状态 | 来源 | 备注 |
|----|------|------|------|------|------|
| M-10 | 求解器方法 | 准稳态分段方法（quasi-steady segment method） | Design Assumption | mission_solver.yaml | 非轨迹优化 |
| M-11 | 爬升/下降 | 简化模型 | Design Assumption | mission_solver.yaml | 非轨迹优化，使用固定 L/D 因子 |
| M-12 | 燃油流量 | 由发动机代理模型驱动 | Design Assumption | V0.2-02 engine_design_points.csv | 代理模型输出 |
| M-13 | 混合电质量惩罚 | 已包含 | Design Assumption | mission_solver.yaml | hybrid_fixed_mass_kg=1200, hybrid_mass_per_MW_kg=250 |
| M-14 | 备油方法 | 初始燃油比例法（reserve_fraction_initial=0.08） | Design Assumption | mission_solver.yaml | 简化方法，非适航备油政策 |
| M-15 | 起飞/着陆代理 | 非认证场长（proxy_indicator_not_certified_field_length） | Design Assumption | mission_solver.yaml | 仅用于方案间方向性比较 |

## 混合电系统模型假设

| ID | 参数 | 值 | 状态 | 来源 | 备注 |
|----|------|------|------|------|------|
| H-01 | 风扇推力代理 | P_shaft / v_aircraft | Design Assumption | hybrid_electric.yaml | 非 CFD/风洞 |
| H-02 | 电池角色 | 短时峰值功率缓冲 | FROZEN | hybrid_electric.yaml | 非巡航能量存储 |
| H-03 | SOC 边界 | 0.20–0.90 | Design Assumption | hybrid_electric.yaml | 安全限制 |
| H-04 | 热管理模型 | 集总参数 | Design Assumption | hybrid_electric.yaml | 非换热器设计 |
| H-05 | 风扇失效模式 | 离散调度场景 | Design Assumption | hybrid_electric.yaml | 非冗余设计 |
| H-06 | 发电机抽功 | 使用 V0.2-02 功率等价代理 | Design Assumption | hybrid_power_extraction_proxy.csv | 非真实 spool matching |

## 模型等级假设

| ID | 参数 | 值 | 状态 | 来源 | 备注 |
|----|------|------|------|------|------|
| L-01 | 模型等级 |概念设计 V0.2 | FROZEN | CLAUDE.md |不得提升 |
| L-02 | 认证等级 | 非认证 | FROZEN | CLAUDE.md |明确排除 |
| L-03 | 输出性质 | 全部为模型输出 | FROZEN | CLAUDE.md | 占位符或配置值 |
| L-04 | 性能声称政策 | 无未验证性能声明 | FROZEN | CLAUDE.md | 强制执行 |

## 假设变更追踪规则

1. FROZEN 项变更须通过正式设计冻结变更控制流程
2. DA 项变更须在变更记录中标注版本和变更原因
3. TBD/TBR 项须在规定时间内确定或升级为 DA/FROZEN
4. 所有假设变更须更新本文档和证据-声明矩阵