# MTA-VHEP Stage Manifest

## Accepted Stages

- V0.2-00 bootstrap/config
- V0.2-01 atmosphere/fuel/basic aero
- V0.2-02 engine surrogate/power extraction
- V0.2-02R CSV export hygiene for V0.2-01/V0.2-02
- V0.2-03 hybrid-electric subsystem/SOC/electrical bus
- V0.2-03R hybrid CSV output hygiene
- V0.2-04 segmented mission solver
- V0.2-04R mission diagnostics and result audit
- V0.2-04S approach/landing segment audit

## Stage Audit Notes

- V0.2-03 files are present in the repository, but commit granularity may be mixed due prior workflow.
- Published Git history should not be rewritten to change that granularity.
- From V0.2-04 onward, simulation code and report ingestion should be committed separately unless explicitly coordinated.

## Known V0.2-03 Sanity Values

- SOC min = 0.2
- SOC max = 0.9
- all_fans_available thrust proxy = 35750.4 N
- all_electric_assist_unavailable thrust proxy = 0 N

These are concept-level model outputs, not certified STOL, noise, fuel-burn, or safety results.

## Known V0.2-04R Mission Audit Values

- V0.2-04 segmented mission solver is implemented.
- V0.2-04R mission diagnostics and result audit are implemented.
- V0.2-04 results are constraint-flagged and must feed V0.2-05 sensitivity analysis.
- Current apparent mission-fuel deltas are constraint-flagged model outputs:
  - baseline_fixed_cycle_turbofan: reference
  - adaptive_cycle_turbofan: about -12.9%
  - adaptive_cycle_plus_hybrid_electric: about -9.3%

These deltas are diagnostic model outputs only; they are not verified fuel-burn benefits.

## Known V0.2-04S Approach/Landing Audit Status

- V0.2-04S approach/landing segment audit is implemented.
- Baseline and adaptive low-thrust-margin results are model-formulation-sensitive when a descending approach force balance is used.
- The adaptive+hybrid approach result remains propulsion sizing/schedule-sensitive when electric assist is enabled in the current power schedule.
- Hybrid unmet electric load remains unresolved in `approach_landing`.
- V0.2-05 sensitivity analysis must use the diagnosed approach model and keep constraint-qualified reporting.
