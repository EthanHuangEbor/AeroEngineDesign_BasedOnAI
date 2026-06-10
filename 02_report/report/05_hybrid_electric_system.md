# 5. 混合电系统

## 5.1 系统架构概述

MTA-VHEP 混合电系统由以下核心组件构成：

```
主机发动机 → 发电机 → 电气总线 → 逆变器 → 电动吹气襟翼风扇
                                       ↑
                                  电池/缓冲储能
```

- **发电机（Generator）**：安装在主发动机上，将机械轴功率转化为电能
- **电气总线（Bus）**：连接发电机和电动风扇的功率传输通道
- **电池/缓冲储能（Battery/Buffer）**：在峰值功率需求时补充供电，支持短时高功率输出
- **逆变器（Inverter）**：将直流电转换为变频交流电驱动电动风扇电机
- **电动吹气襟翼风扇（Electric Fan）**：将电能转化为推力/增升气流

## 5.2 关键参数

| 参数 | 初始值 | 范围 | 状态 |
|------|--------|------|------|
| 总线电压（初始值） | 1500 V | 1000–3000 V | Design Assumption |
| 发电机效率 | 0.94 | 估算值 | Engineering Inference |
| 电缆分配效率 | 0.985 | 估算值 | Engineering Inference |
| 电池/缓冲储能容量（初始值） | 500000 Wh | 0–1000000 Wh | Design Assumption |
| 电池 SOC 最小值 | 0.20 | 安全限制 | Design Assumption |
| 电池 SOC 初始值 | 0.90 | Design Assumption |
| 电机效率 | 0.95 | Engineering Inference |
| 逆变器效率 | 0.98 | Engineering Inference |
| 最大总电动风扇功率 | 8000000 W | 模型上限 | Design Assumption |

## 5.3 V0.2-03 混合电系统与电气总线输出

V0.2-03 层已实现概念级混合电系统，为 V0.2-04 分段任务剖面求解器提供电气功率时间线和 SOC 边界。

### 5.3.1 实现文件

| 文件 | 用途 |
|------|------|
| `config/hybrid_electric.yaml` | 混合电系统配置参数 |
| `mta_vhep/electrical/motor.py` | 电机效率模型 |
| `mta_vhep/electrical/inverter.py` | 逆变器效率模型 |
| `mta_vhep/electrical/battery_buffer.py` | 电池/缓冲储能模型 |
| `mta_vhep/electrical/bus.py` | 电气总线模型 |
| `mta_vhep/electrical/thermal.py` | 热负荷估算模型 |
| `mta_vhep/propulsion/electric_fan.py` | 电动风扇推力代理模型 |
| `scripts/run_03_hybrid.py` | 混合电仿真脚本 |

### 5.3.2 输出文件

| 文件 | 内容 |
|------|------|
| `hybrid_timeline.csv` | 4阶段功率时间线（起飞/初始爬升/巡航/进近） |
| `hybrid_summary.csv` | 汇总：SOC 边界、热负荷、未满足负载 |
| `electric_fan_mode_summary.csv` | 各风扇模式推力代理 |
| `fan_failure_cases.csv` | 风扇失效场景推力代理 |
| `hybrid_power_extraction_proxy.csv` | 发电机抽功 penalty 接口 |
| `electric_power_soc.png` | SOC 时间线图 |
| `electric_fan_thrust_proxy.png` | 风扇推力代理图 |
| `hybrid_thermal_load.png` | 热负荷图 |
| `fan_failure_power_available.png` | 失效场景功率图 |

### 5.3.3 模型局限性声明

V0.2-03 混合电模型的局限性：

1. **风扇推力为功率-速度代理**：风扇推力使用 `P/v` 代理，非 CFD 或风洞数据，不得声称 STOL 验证
2. **吹气系数为代理**：blowing coefficient 使用推力/动压/翼面积代理，非 CFD 验证数据
3. **电气总线为准稳态**：总线模型为稳态功率分配，不含瞬态响应
4. **电池为短时峰值功率缓冲**：电池仅用于短时峰值功率支持，非巡航能量存储
5. **热管理为集总参数模型**：热负荷模型为集总估算，非换热器设计
6. **发电机抽功使用 V0.2-02 功率等价代理**：抽功 penalty 使用 V0.2-02 的功率等价代理，非真实 spool matching

**不证明**：STOL 改进、噪声降低、燃油消耗降低、认证级安全设计。

### 5.4关键参数

| 参数 | 初始值 | 范围 | 状态 |
|------|--------|------|------|
| 总线电压（初始值） | 1500 V | 1000–3000 V | Design Assumption |
| 发电机效率 | 0.94 | 估算值 | Engineering Inference |
| 电缆分配效率 | 0.985 | 估算值 | Engineering Inference |
| 电池/缓冲储能容量（初始值） | 500000 Wh | 0–1000000 Wh | Design Assumption |
| 电池 SOC 最小值 | 0.20 | 安全限制 | Design Assumption |
| 电池 SOC 初始值 | 0.90 | Design Assumption |
| 电机效率 | 0.95 | Engineering Inference |
| 逆变器效率 | 0.98 | Engineering Inference |
| 最大总电动风扇功率 | 8000000 W | 模型上限 | Design Assumption |

## 5.5 轴功率提取 penalty（V0.2-03 输出）

V0.2-03 使用 V0.2-02 的功率等价代理，将发电机功率需求转换为每台主发动机的轴功率提取。以下数值来自 `hybrid_power_extraction_proxy.csv`（Model Output）：

| 阶段 | 发电机总功率 W | 每台发动机抽功 W | 推力损失 N |燃油流量增量 kg/s |
|------|--------------|----------------|----------|-------------------|
| 起飞 | 2000000 | 1063829.8 | 42215.5 | +0.0128 |
| 初始爬升 | 1500000 | 797872.3 | 19788.5 | +0.0096 |
| 巡航 | 0 | 0 | 0 | 0 |
| 进近 | 1000000 | 531914.9 | 21107.7 | +0.0064 |

**说明**：起飞阶段每台发动机抽功约 1.06 MW，产生约 42.2 kN 推力损失。进近阶段存在未满足负载（battery unmet power）938.7 W，表明电池在峰值需求时提供补充供电。

## 5.6 电池/缓冲储能管理（V0.2-03 输出）

以下数值来自 `hybrid_summary.csv`（Model Output）：

| 参数 | 值 | 说明 |
|------|------|------|
| 阶段数 | 4 | 起飞/初始爬升/巡航/进近 |
| SOC 最小值 | 0.20 | 安全保障下限 |
| SOC 最大值 | 0.90 | 初始值上限 |
| SOC 变化范围 | 0.90 → 0.20 | 起飞→进近 |
| 峰值总风扇推力代理 | 35750.4 N | 起飞阶段（assist 模式，4 台风扇） |
| 峰值热负荷 | 464573.3 W | 起飞阶段 |
| 总未满足负载能量 | 131285.7 Wh | 主要来自进近阶段 |

SOC 最低点在进近阶段达到 0.20（安全保障下限），表明进近阶段的电池放电压力最大。

## 5.7 风扇失效场景推力代理（V0.2-03 输出）

以下数值来自 `fan_failure_cases.csv`（Model Output）：

| 场景 | 可用风扇数 | 总风扇推力代理 N | 单台风扇推力代理 N |
|------|-----------|----------------|-------------------|
| 全风扇可用（assist） | 4 | 35750.4 | 8937.6 |
| 单风扇失效 | 3 | 26812.8 | 8937.6（失效风扇为 0） |
| 单侧双风扇失效 | 2 | 17875.2 | 8937.6（失效风扇为 0） |
| 全电动辅助不可用 | 0 | 0.0 | 0.0 |

**说明**：风扇推力代理在 assist/degraded 模式下为正值，failed/off 模式下为零。

## 5.8 电动风扇推力代理（V0.2-03 输出）

以下数值来自 `electric_fan_mode_summary.csv`（Model Output）：

| 模式 | 单台风扇输入功率 W | 单台风扇轴功率 W | 推力代理 N | blowing coefficient |
|------|-------------------|-----------------|------------|---------------------|
| off | 0 | 0 | 0 | 0 |
| assist | 1000000 | 931000 | 8937.6 | 0.0162 |
| degraded | 500000 | 465500 | 4468.8 | 0.0081 |
| failed | 0 | 0 | 0 | 0 |

**模型说明**：推力代理使用 `P_shaft / v_aircraft` 公式，不含 CFD 或风洞验证，不得声称为真实气动推力。

## 5.9 混合电系统与主发动机的耦合关系

混合电系统通过以下接口与 V0.2-02 发动机代理模型耦合：

1. **发电机功率需求** → `hybrid_power_extraction_proxy.csv` → 每台发动机轴功率提取 → V0.2-02 推力 penalty
2. **电池放电补充** → 在发电机功率不足时补充供电（`hybrid_timeline.csv` 中 battery_power_W）
3. **SOC 边界** → 进近阶段 SOC 降至 0.20 安全保障下限，限制进一步放电

## 5.10 参数来源

本章 V0.2-03 输出参数标注为 **Model Output**，来源为 CSV 输出文件。V0.2-03 之前的占位符参数标注为 **待仿真结果填充**。