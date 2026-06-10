# 2. 基准平台

## 2.1 概述

MTA-VHEP 基准平台定义了一型中型运输机的基本参数，作为后续推进系统、混合电系统及多模式性能分析的基准载体。本章所列参数均来源于 `01_simulation/config/aircraft_baseline.yaml` 中的已冻结配置或参数扫描初值。

## 2.2 基本参数

| 参数 | 初始值 | 范围 | 状态 |
|------|--------|------|------|
| 最大起飞重量（MTOW） | 87500 kg | 80000–95000 kg | Design Assumption |
| 作业空重（OEW） | 52000 kg | 45000–58000 kg | Design Assumption |
| 设计有效载荷 | 25000 kg | FROZEN | Design Assumption |
| 设计航程 | 3200 km | FROZEN | Design Assumption |
| 翼面积 | 160.0 m² | 待气动仿真优化 | Design Assumption |
| 展弦比（AR） | 9.5 | 待气动仿真优化 | Design Assumption |
| 奥斯瓦尔德效率 | 0.78 | 估算值 | Design Assumption |
| 巡航零升阻力系数（CD0） | 0.026 | 待风洞/仿真验证 | Design Assumption |
| 升阻比（L/D）范围 | 13.0–18.0 | 估算范围 | Engineering Inference |

## 2.3 巡航性能基准

| 参数 | 值 | 状态 |
|------|------|------|
| 巡航马赫数 | 0.75 | Design Assumption |
| 巡航高度 | 10668 m（35000 ft） | Design Assumption |
| 最大马赫数 | 0.80 | Design Assumption |
| 最大飞行高度 | 12000 m | Design Assumption |

## 2.4 气动布局说明

当前版本的气动布局参数（翼面积、展弦比、零升阻力系数）均为概念设计估算值，尚未通过 CFD 仿真或风洞试验进行验证。阻力极曲线（drag polar）为概念阶段假设，不得作为认证依据。

## 2.5 参数来源

所有本章参数均标注为 **Design Assumption**，来源为 `aircraft_baseline.yaml` 配置文件或同级别飞机工程类比。性能参数的最终确定有待全机气动仿真与任务剖面求解完成后更新。