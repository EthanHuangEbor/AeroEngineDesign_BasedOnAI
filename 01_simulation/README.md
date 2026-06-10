# MTA-VHEP Simulation

MTA-VHEP is a concept-level simulation repository for a next-generation medium transport aircraft propulsion concept.

## Baseline Concept

- Aircraft class: medium transport aircraft
- Design payload: 25 t
- Design range: 3200 km
- Main propulsion: two three-stream variable-cycle turbofan engines
- Electric assist: four short-duration hybrid-electric blown-flap fans
- Fuel compatibility: Jet-A / SAF scenario support
- Hydrogen and detonation propulsion: future upgrade stubs only

## Create Environment

Using conda:

```powershell
conda env create -f environment.yml
conda activate mta-vhep
```

Using pip:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install -r requirements.txt
```

## Run Smoke Test

From `01_simulation/`:

```powershell
python scripts/run_00_smoke_test.py
```

## Run Tests

From `01_simulation/`:

```powershell
python -m pytest
```

## V0.2 Warning

V0.2 is concept-level and not certification-grade. Numerical results are configuration-derived model outputs or placeholders, not verified aircraft performance, certified STOL capability, certified noise prediction, verified fuel-burn reduction, SAF carbon neutrality, or hydrogen/detonation readiness.
