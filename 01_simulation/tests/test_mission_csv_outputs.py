from pathlib import Path

import pandas as pd


SIM_ROOT = Path(__file__).resolve().parents[1]
CSV_DIR = SIM_ROOT / "results" / "csv"


EXPECTED_FILES = {
    "mission_segments.csv": 18,
    "mission_summary.csv": 3,
    "weight_breakdown.csv": 3,
    "mission_constraint_violations.csv": 1,
    "takeoff_landing_proxy.csv": 3,
}


def test_mission_csv_outputs_exist_and_are_readable() -> None:
    for filename, minimum_rows in EXPECTED_FILES.items():
        path = CSV_DIR / filename

        assert path.exists()
        data = path.read_bytes()
        assert b"\n" in data
        assert b"\r" not in data
        table = pd.read_csv(path)
        assert len(table) >= minimum_rows


def test_mission_summary_contains_required_columns() -> None:
    table = pd.read_csv(CSV_DIR / "mission_summary.csv")

    assert len(table) == 3
    assert {
        "case_name",
        "block_fuel_kg",
        "reserve_fuel_kg",
        "mission_fuel_kg",
        "electric_energy_Wh",
        "max_electric_power_W",
        "max_thermal_load_W",
        "constraint_violations",
    }.issubset(table.columns)


def test_mission_segment_csv_has_expected_case_count_and_flags() -> None:
    table = pd.read_csv(CSV_DIR / "mission_segments.csv")

    assert len(table) == 18
    assert table["case_name"].nunique() == 3
    assert "constraint_flags" in table.columns
    assert (table["fuel_burn_kg"] > 0.0).all()


def test_hybrid_mission_csv_records_electric_energy_and_soc() -> None:
    table = pd.read_csv(CSV_DIR / "mission_segments.csv")
    hybrid = table[table["case_name"] == "adaptive_cycle_plus_hybrid_electric"]
    non_hybrid = table[table["case_name"] != "adaptive_cycle_plus_hybrid_electric"]

    assert hybrid["electric_energy_Wh"].sum() > 0.0
    assert non_hybrid["electric_energy_Wh"].sum() == 0.0
    assert hybrid["soc_end"].dropna().between(0.0, 1.0).all()
