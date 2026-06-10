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
