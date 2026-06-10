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
