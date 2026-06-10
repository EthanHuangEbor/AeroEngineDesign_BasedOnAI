from pathlib import Path

from mta_vhep.interfaces.io import load_mission_profile


CONFIG_DIR = Path(__file__).resolve().parents[1] / "config"


def test_mission_segment_distances_sum_to_design_range() -> None:
    mission = load_mission_profile(CONFIG_DIR)

    distance_km = sum(segment.distance_km or 0.0 for segment in mission.segments)

    assert distance_km == mission.design_range_km == 3200.0
