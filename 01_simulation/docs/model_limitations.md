# Model Limitations

- V0.2 loads frozen configuration values and dataclass interfaces only.
- V0.2 does not implement atmosphere, propulsion physics, mission solving, hybrid-electric performance, sensitivity analysis, certified STOL prediction, or certified noise prediction.
- All numerical outputs are model/configuration outputs, not verified truth.
- Hydrogen and detonation propulsion are future upgrade stubs only.
- SAF entries support lifecycle scenario bookkeeping only and do not imply carbon neutrality.

## V0.2-01 Environment, Fuel, and Basic Aerodynamics

- ISA atmosphere is limited to 0 to 12000 m and uses a simple troposphere lapse-rate model.
- The drag polar is conceptual: `CD = CD0 + k CL^2`; it is not CFD, wind-tunnel data, or certified performance.
- Flap and blowing coefficients are placeholders stored in `config/aero_model.yaml` for traceability.
- The landing-gear drag increment uses a documented placeholder constant, `CD = +0.020`, in `aircraft/aerodynamics.py`.
- Blown-flap outputs are proxy model inputs and must not be treated as certified STOL prediction.
- SAF modeling is property-based only and is not fuel certification, lifecycle analysis, or carbon-neutrality evidence.

## V0.2-02 Engine Surrogate

- The engine surrogate is not a component-level thermodynamic cycle model.
- TSFC values in `config/engine_surrogate.yaml` are conceptual placeholders for trend studies.
- Third-stream and variable-nozzle effects are parametric schedule multipliers, not verified cycle physics.
- Shaft power extraction penalty is a power-equivalent proxy and not a real spool matching model.
- Results are suitable only for concept-level comparison and later mission-model coupling.
- No verified fuel-burn reduction, STOL, noise, SAF certification, or real engine performance claim is made.

## V0.2-02R Export Hygiene

- CSV output format was validated for downstream report ingestion; this does not change physical model fidelity.

## V0.2-03 Hybrid-electric subsystem limitations

- Electric fan thrust is a power-over-velocity proxy.
- Blowing coefficient is a proxy, not CFD or wind-tunnel data.
- Electrical bus is quasi-steady.
- Battery buffer is short-duration peak-power support only.
- Thermal model is lumped and not heat-exchanger design.
- Generator shaft power extraction uses V0.2-02 power-equivalent proxy.
- No STOL, noise, fuel-burn, or certified safety claim is made.

## V0.2-03R Hybrid Output Hygiene

- Hybrid CSV output format was validated for downstream mission solver and report ingestion. This does not change physical model fidelity.

## V0.2-04 Mission solver limitations

- Segment mission model is quasi-steady and concept-level.
- Fuel burn uses the surrogate engine deck and simplified thrust demand.
- Climb/descent modeling is not trajectory optimization.
- Takeoff/landing outputs are proxy indicators only.
- Results are not certified range, fuel-burn, STOL, or noise performance.
- Hybrid benefit/mass penalty is included but depends on placeholder assumptions.

## V0.2-04R Mission result audit limitations

- V0.2-04 mission results are diagnostic and constraint-flagged.
- Negative margin to initial MTOW indicates sizing iteration is required.
- V0.1 MTOW upper range is 95000 kg; margin to this upper bound is reported separately from margin to the initial MTOW assumption.
- Low thrust margin means current thrust/model schedule must be refined before claiming mission feasibility.
- Unmet electric load means hybrid power schedule or storage/generator assumptions need refinement.
- Apparent fuel reduction is not a verified benefit while constraints remain.

## V0.2-04S Approach/landing segment audit limitations

- The approach force balance is quasi-steady.
- Descent angle is parametric.
- This is not a flight-dynamics or landing certification model.
- Constraint resolution depends on future sizing and sensitivity analysis.
- No STOL or certified landing performance claim is made.

## V0.2-05 Sensitivity analysis limitations

- Sensitivity cases use the current concept-level surrogate models.
- Parameter scans are screening studies, not optimization certification.
- Best candidates are design-space screening candidates, not a final design.
- Results depend on V0.2 assumptions and should change as sizing, approach, and hybrid schedules are refined.
- No final fuel-burn, range, STOL, noise, safety, or certification claim is made.

## V0.2-05R Corrected constraint classification limitations

- Corrected approach classification uses the V0.2-04S quasi-steady descending approach force balance.
- Raw mission-solver constraints and corrected approach constraints are both retained.
- Corrected feasible candidates, if present in later scans, are proxy screening candidates and not validated designs.
- Hybrid electric load, MTOW, and sizing/schedule constraints remain explicit and are not hidden by the approach correction.
- No final fuel-burn, range, STOL, noise, safety, or certification claim is made.

## V0.2-05Q Sensitivity consistency audit limitations

- This audit checks internal consistency between V0.2-04S approach diagnostics and V0.2-05R sensitivity classifications.
- It does not validate the physical accuracy of either model.
- Monotonicity checks are diagnostic only and are not design certification.
- Any candidate remains concept-level only, even if a diagnostic monotonicity check passes.

## V0.2-05Q2 Field semantics repair limitations

- V0.2-05Q2 repairs sensitivity field semantics by separating approach-only corrected margin from all-segment corrected minimum margin.
- `approach_only_corrected_margin_N` is comparable to the V0.2-04S approach/landing force-balance replay.
- `corrected_all_segment_min_thrust_margin_N` remains the all-segment screening margin and may be limited by non-approach segments.
- Approach-corrected-only candidate rows are diagnostic screening rows, not feasible or validated designs.
- Current all-segment corrected feasibility remains constraint-flagged because non-approach low-thrust constraints persist.
- No final fuel-burn, range, STOL, noise, safety, or certification claim is made.
