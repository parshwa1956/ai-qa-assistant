import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from services.prompts import OUTPUT_TYPES


def test_output_types_cover_workspaces():
    assert "Bug Report" in OUTPUT_TYPES["qa"]
    assert "Requirement to User Story" in OUTPUT_TYPES["ba"]
    assert "Smart Code Review" in OUTPUT_TYPES["dev"]
    assert "Flow to Requirement" in OUTPUT_TYPES["flow"]
