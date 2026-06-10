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
