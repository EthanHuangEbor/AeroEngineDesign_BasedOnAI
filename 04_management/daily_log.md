# Daily Log

## TBD

- V0.2 bootstrap started.

# Daily Log 2026-06-10

- V0.2-00 bootstrap accepted with smoke test and frozen-value tests passing.
- V0.2-01 started for ISA atmosphere, fuel property helpers, and concept-level basic aerodynamics.
- New files created: `core/atmosphere.py`, `propulsion/fuel.py`, `aircraft/aerodynamics.py`, `config/aero_model.yaml`, `scripts/run_01_environment_aero.py`, and V0.2-01 tests.
- Tests run: baseline smoke test, environment/aero verification script, and pytest.
- Open limitations: atmosphere limited to 0-12000 m, drag polar is conceptual, blown-flap coefficients are placeholders, and SAF helper is not lifecycle or certification analysis.

# Daily Log 2026-06-10 V0.2-02

- V0.2-02 started and completed for concept-level engine surrogate design-point evaluation.
- Engine surrogate files created: `config/engine_surrogate.yaml`, `propulsion/power_extraction.py`, `propulsion/turbofan_vce.py`, and `scripts/run_02_engine_design_points.py`.
- Tests run: bootstrap smoke test, environment/aero script, engine design-point script, and pytest.
- CSV outputs: `engine_design_points.csv` and `engine_power_extraction_sweep.csv`.
- Figure outputs: `tsfc_mode_map`, `thrust_lapse_map`, and `power_extraction_penalty` in PNG and SVG formats.
- Limitations: no certified engine cycle analysis, no real spool matching, no mission solver, no hybrid-electric subsystem, and no verified fuel-burn reduction claim.

# Daily Log 2026-06-10 V0.2-02R

- V0.2-02R completed for CSV export hygiene and result-health checks.
- Added reusable LF-terminated CSV export helper for downstream report ingestion, Excel review, and mission solver coupling.
- Added tests validating expected CSV files, row counts, required columns, and newline-separated physical rows.
- Tests run: bootstrap smoke test, environment/aero script, engine design-point script, and pytest.
- Limitation: export hygiene does not change physical model fidelity or validate model accuracy.

# Daily Log 2026-06-10 V0.2-03

- V0.2-03 completed for the concept-level hybrid-electric subsystem and SOC model.
- Files created: `config/hybrid_electric.yaml`, electrical subsystem modules, `propulsion/electric_fan.py`, `scripts/run_03_hybrid.py`, and hybrid-electric tests.
- Tests run: bootstrap smoke test, environment/aero script, engine design-point script, hybrid script, and pytest.
- CSV outputs: `hybrid_timeline.csv`, `hybrid_summary.csv`, `electric_fan_mode_summary.csv`, `fan_failure_cases.csv`, and `hybrid_power_extraction_proxy.csv`.
- Figure outputs: `electric_power_soc`, `electric_fan_thrust_proxy`, `hybrid_thermal_load`, and `fan_failure_power_available` in PNG and SVG formats.
- Limitations: no mission solver, no block fuel, no certified STOL/noise/safety claim, and no verified fuel-burn reduction claim.

# Daily Log 2026-06-10 V0.2-03R

- Hybrid CSV export fixed and validated for downstream mission solver and report ingestion.
- Tests run: bootstrap smoke test, environment/aero script, engine design-point script, hybrid script, and pytest.
- Row counts: `hybrid_timeline.csv` 4, `hybrid_summary.csv` 1, `electric_fan_mode_summary.csv` 4, `fan_failure_cases.csv` 4, `hybrid_power_extraction_proxy.csv` 4.
- Stage manifest created at `04_management/stage_manifest.md`.
- Open limitation: mission solver still missing.

# Daily Log 2026-06-10 V0.2-04

- V0.2-04 completed for the concept-level segmented mission solver and proxy takeoff/landing indicators.
- Files created: `config/mission_solver.yaml`, `aircraft/weights.py`, `mission/segment.py`, `mission/mission_solver.py`, `mission/takeoff_landing.py`, `scripts/run_04_mission.py`, and mission solver tests.
- Tests run: bootstrap smoke test, environment/aero script, engine design-point script, hybrid script, mission script, and pytest.
- CSV outputs: `mission_segments.csv`, `mission_summary.csv`, `weight_breakdown.csv`, `mission_constraint_violations.csv`, and `takeoff_landing_proxy.csv`.
- Figure outputs: `mission_profile`, `fuel_burn_comparison`, `mission_energy_breakdown`, and `takeoff_proxy_comparison` in PNG and SVG formats.
- Limitations: mission solver is quasi-steady and concept-level; takeoff/landing outputs are proxy indicators only; no certified range, fuel-burn, STOL, or noise claim is made.

# Daily Log 2026-06-10 V0.2-04R

- Mission diagnostics added with per-segment thrust margin, electric energy, SOC, unmet electric load, and constraint flags.
- Weight-margin interpretation clarified by separating margin to initial MTOW from margin to the V0.1 upper MTOW range.
- Constraints identified by segment and by case: all mission cases remain low-thrust-margin flagged, and the hybrid case also has unmet electric load.
- Tests run: bootstrap smoke test, environment/aero script, engine design-point script, hybrid script, mission script, and pytest.
- Open issue: V0.2-05 sensitivity analysis is needed before any design trade claims are made.

# Daily Log 2026-06-10 V0.2-04S

- Approach/landing audit files added: `mission/approach_analysis.py`, `scripts/run_04s_approach_audit.py`, approach audit CSV outputs, figures, and tests.
- Script outputs: `approach_landing_diagnostics.csv`, `approach_sensitivity_scan.csv`, `approach_thrust_margin_audit`, and `approach_sensitivity_scan`.
- Tests run: bootstrap smoke test, environment/aero script, engine design-point script, hybrid script, mission script, approach audit script, and pytest.
- Key diagnostic conclusion: baseline/adaptive approach margins are model-formulation-sensitive; hybrid approach remains sizing/schedule-sensitive with unmet electric load.
- Remaining open issues: V0.2-05 sensitivity analysis must refine approach modeling, propulsion schedule, hybrid power schedule, and sizing assumptions before any feasibility claim.

# Daily Log 2026-06-10 V0.2-05

- V0.2-05 sensitivity analysis completed with 225 summary rows from one-at-a-time scans and a selected hybrid design grid.
- CSV outputs: `sensitivity_summary.csv`, `sensitivity_case_details.csv`, `sensitivity_constraints.csv`, `sensitivity_best_candidates.csv`, and `sensitivity_tornado_data.csv`.
- Figure outputs: `constraint_tornado`, `pareto_fuel_vs_mtow`, `thrust_margin_vs_engine_rating`, `hybrid_power_sizing_map`, and `takeoff_proxy_sensitivity` in PNG and SVG formats.
- Constraints summary: all 225 rows remain low-thrust-margin flagged; 69 rows have unmet electric load and 156 rows have zero unmet electric load.
- Best candidate summary: selected rows are screening candidates only and remain constraint-qualified; no row is marked validated.
- Open issues: V0.2-06/report integration should keep these as diagnostic model outputs, and future sizing work must address thrust margin before feasibility claims.

# Daily Log 2026-06-10 V0.2-05R

- V0.2-05R corrected sensitivity classification added raw and corrected low-thrust fields using the V0.2-04S approach force-balance helper.
- Raw vs corrected counts: raw low thrust 225, corrected low thrust 225, approach-model-sensitive 0, sizing/schedule low thrust 225.
- Candidate status: feasible basic raw 0 and feasible basic corrected 0; best candidates remain diagnostic screening rows and are not validated.
- Tests run: sensitivity corrected-constraint tests, full script chain, and pytest.
- Open limitations: hybrid unmet electric load remains in 69 rows, and low-thrust margin still requires sizing/schedule refinement before report claims.
