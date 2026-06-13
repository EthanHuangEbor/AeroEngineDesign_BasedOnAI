# MTA-VHEP — 中型运输机变循环混合电推进概念设计

[![Version](https://img.shields.io/badge/version-V0.2-blue)](https://github.com/EthanHuangEbor/AeroEngineDesign_BasedOnAI)
[![Stage](https://img.shields.io/badge/stage-concept%20design-yellow)](https://github.com/EthanHuangEbor/AeroEngineDesign_BasedOnAI)
[![Certification](https://img.shields.io/badge/certification%20grade-false-red)](https://github.com/EthanHuangEbor/AeroEngineDesign_BasedOnAI)

## 定位

MTA-VHEP（Medium Transport Aircraft — Variable Cycle Hybrid Electric Propulsion）是一个**概念设计级别的推进系统仿真仓库**，面向下一代中型运输机的动力架构探索。

**目标不是**工业级 CFD、认证发动机仿真或最终飞机设计。**目标是**物理一致的趋势、可追溯的假设、报告就绪的表格和可复现的图表。

本仓库是 [AeroEngineDesign_BasedOnAI](https://github.com/EthanHuangEbor/AeroEngineDesign_BasedOnAI) 项目的主仓库，承载从模型搭建、敏感性分析到概念设计报告的完整工作流。

## 基线概念

| 项目 | 规格 |
|------|------|
| 机型 | 中型运输机 |
| 设计载荷 | 25 t |
| 设计航程 | 3200 km |
| 主推进 | 2 台三流道变循环涡扇发动机（VCE） |
| 电动辅助 | 4 台短时混合电吹气襟翼风扇 |
| 燃料兼容性 | Jet-A / SAF 场景支持 |
| 氢燃料 / 爆震推进 | 仅预留未来升级路径（`enabled=false`） |

## 仓库结构

```
├── 01_simulation/           # Python 概念级仿真（mta_vhep 包）
│   ├── config/              # YAML 配置文件（假设集中管理）
│   ├── mta_vhep/            # 核心仿真包
│   │   ├── core/            # 大气、单位、常数
│   │   ├── aircraft/        # 气动、重量
│   │   ├── propulsion/      # VCE 涡扇代理、电动风扇、燃油、轴功率提取
│   │   ├── electrical/      # 电池缓冲、电母线、逆变器、电机、热管理
│   │   ├── mission/         # 任务求解器、航段模型、进近分析、起降代理
│   │   ├── analysis/        # 敏感性分析
│   │   ├── interfaces/      # I/O、CSV 导出、数据模式
│   │   └── plotting/        # 图表生成
│   ├── scripts/             # 运行脚本（run_00 至 run_05q）
│   ├── tests/               # pytest 测试套件
│   ├── docs/                # 假设、公式、模型限制文档
│   └── figures/             # PNG / SVG 图表输出
├── 02_report/               # 概念设计报告
│   ├── report/              # 分章节报告（00–10）
│   ├── final_report/        # V1 集成概念设计报告包
│   ├── review/              # 声明-证据矩阵、技术评审
│   ├── tables/              # 假设表、结果表、风险表
│   └── defense/             # 答辩 Q&A
├── 03_references/           # 参考文献（按领域分类）
└── 04_management/           # 项目管理（假设登记、决策日志、任务板、阶段清单）
```

## 当前状态：V0.2（已完结）

### 已完成

V0.2 完成了端到端概念计算链：

```
配置 → 大气/燃料/气动 → 发动机代理 → 混合电系统 → 任务求解器 → 约束诊断 → 敏感性分类
```

| 里程碑 | 内容 |
|--------|------|
| V0.2-00 | 仓库初始化、配置骨架 |
| V0.2-01 | 大气模型、燃料数据库、基础气动 |
| V0.2-02 | 发动机代理模型、轴功率提取 |
| V0.2-03 | 混合电子系统、SOC、电母线 |
| V0.2-04 | 分段任务求解器 |
| V0.2-04R/S | 任务诊断、进近航段审计 |
| V0.2-05 | 敏感性分析（225 案例、10 设计变量） |
| V0.2-05R/Q/Q2 | 约束分类修正、一致性审计、字段语义修复 |
| V1 报告 | 集成概念设计报告包（含摘要、声明门控、附图索引） |

### 核心发现

| 指标 | 数值 |
|------|------|
| 敏感性总案例 | 225 |
| 进近模型敏感案例 | 104（原始进近约束与模型公式选择相关） |
| 仅进近修正候选 | 92（诊断性筛选，**非最终可行设计**） |
| **全段修正可行设计** | **0** |
| 主导剩余约束 | 下降段 197 行、起飞段 28 行 |
| 混合电未满足电负荷 | 69 行 |

### 关键结论

- **V0.2 未产生全段可行的验证设计点**。所有 225 个敏感性案例均存在至少一个航段约束告警。
- 内部一致性审计通过（名义回放 3/3，推力单调性 6/6）。
- 自适应循环方案在代理模型中显示方向性 TSFC 优势（条件性模型趋势，非验证收益）。
- 下降段怠速代理推力不足和混合电功率调度是约束消解的优先方向。

## V0.2 声明约束

本仓库所有输出受声明门控约束，**禁止**出现以下表述：
- "已验证的燃油消耗降低" / "认证航程" / "STOL 能力已实现"
- "最终可行方案" / "最优设计" / "认证级模型"
- "氢燃料推进已具备" / "爆震推进已验证"

完整声明门控见 [`02_report/final_report/final_claim_gate.md`](02_report/final_report/final_claim_gate.md)。

## 下一步：V0.3 sizing/细化

1. 下降段推力模型修正
2. 非进近约束消解（下降段 + 起飞段）
3. MTOW 尺寸迭代闭合
4. 混合电功率调度优化
5. 低速气动验证

## 环境搭建

```powershell
# conda
conda env create -f 01_simulation/environment.yml
conda activate mta-vhep

# venv
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install -r 01_simulation/requirements.txt
```

## 运行

```powershell
cd 01_simulation
python scripts/run_00_smoke_test.py  # 冒烟测试
python -m pytest                      # 完整测试套件
```

## 声明

本仓库为概念设计级别模型。所有数值结果为配置派生或占位符输出，**不是**已验证的飞机性能、认证航程、STOL 能力、噪声预测、SAF 碳中和或氢/爆震推进就绪度。
