# MTA-VHEP Stage Manifest

## Accepted Stages

- V0.2-00 bootstrap/config
- V0.2-01 atmosphere/fuel/basic aero
- V0.2-02 engine surrogate/power extraction
- V0.2-02R CSV export hygiene for V0.2-01/V0.2-02
- V0.2-03 hybrid-electric subsystem/SOC/electrical bus
- V0.2-03R hybrid CSV output hygiene

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
