#!/usr/bin/env python3
"""Validate the public example of the detector output contract."""

from __future__ import annotations

import json
from pathlib import Path


def validate(payload: dict) -> None:
    assert payload["status"] == "mvp_causal_obstacle_candidate"
    assert isinstance(payload["alarm"], bool)
    assert isinstance(payload["obstacles"], list)
    if payload["alarm"]:
        assert payload["obstacles"]
        assert payload["nearest_obstacle_m"] > 0
    for obstacle in payload["obstacles"]:
        assert len(obstacle["center_xyz_m"]) == 3
        assert len(obstacle["size_xyz_m"]) == 3
        assert obstacle["distance_forward_m"] > 0
        assert obstacle["persistence_frames"] >= 1
        assert 0.0 <= obstacle["confidence"] <= 1.0


if __name__ == "__main__":
    example = Path(__file__).parents[1] / "examples" / "sample_output.json"
    validate(json.loads(example.read_text(encoding="utf-8")))
    print("public ROS 2 output example: OK")
