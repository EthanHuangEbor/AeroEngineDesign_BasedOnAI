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
| L-06 | V0.2-02 发动机代理 | 未完成 | 待实现 | CLAUDE.md | TSFC、推力、轴功率 penalty |
| L-07 | V0.2-03 任务剖面求解 | 未完成 | 待实现 | CLAUDE.md | 燃油消耗、航程 |
| L-08 | V0.2-04 混合电 SOC 模型 | 未完成 | 待实现 | CLAUDE.md |电池动态管理 |
| L-09 | V0.2-05 敏感性分析 | 未完成 | 待实现 | CLAUDE.md | 参数影响龙卷风图 |

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