#!/usr/bin/env python3
"""Small dependency-free reference prototype of the causal alarm policy.

The production ROS 2 detector uses the same public coordinate convention and
causal confirmation principle, but adds density normalization, local clearance
estimation, background suppression and a learned second stage.
"""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class Candidate:
    center_x_m: float
    distance_forward_m: float
    point_count: int


class CausalClearancePrototype:
    """Detect compact occupancy inside a clearance corridor in past-only order."""

    def __init__(
        self,
        *,
        clearance_half_width_m: float = 2.0,
        min_forward_m: float = 0.5,
        max_forward_m: float = 80.0,
        min_height_m: float = 0.10,
        max_height_m: float = 2.8,
        cell_size_m: float = 0.5,
        min_points_per_cell: int = 4,
        confirm_frames: int = 2,
        association_distance_m: float = 1.5,
    ) -> None:
        self.clearance_half_width_m = clearance_half_width_m
        self.min_forward_m = min_forward_m
        self.max_forward_m = max_forward_m
        self.min_height_m = min_height_m
        self.max_height_m = max_height_m
        self.cell_size_m = cell_size_m
        self.min_points_per_cell = min_points_per_cell
        self.confirm_frames = confirm_frames
        self.association_distance_m = association_distance_m
        self._previous_distance_m: float | None = None
        self._persistence_frames = 0

    def _candidates(self, points_xyz_m: Iterable[Iterable[float]]) -> list[Candidate]:
        cells: Counter[tuple[int, int]] = Counter()
        for point in points_xyz_m:
            x_m, forward_m, height_m = (float(value) for value in point)
            if not (
                abs(x_m) <= self.clearance_half_width_m
                and self.min_forward_m <= forward_m <= self.max_forward_m
                and self.min_height_m <= height_m <= self.max_height_m
            ):
                continue
            cell = (
                math.floor(x_m / self.cell_size_m),
                math.floor(forward_m / self.cell_size_m),
            )
            cells[cell] += 1

        candidates = [
            Candidate(
                center_x_m=(x_bin + 0.5) * self.cell_size_m,
                distance_forward_m=(y_bin + 0.5) * self.cell_size_m,
                point_count=count,
            )
            for (x_bin, y_bin), count in cells.items()
            if count >= self.min_points_per_cell
        ]
        return sorted(candidates, key=lambda item: item.distance_forward_m)

    def process(self, frame: dict) -> dict:
        candidates = self._candidates(frame["points_xyz_m"])
        nearest = candidates[0] if candidates else None
        if nearest is None:
            self._previous_distance_m = None
            self._persistence_frames = 0
        elif (
            self._previous_distance_m is not None
            and abs(nearest.distance_forward_m - self._previous_distance_m)
            <= self.association_distance_m
        ):
            self._persistence_frames += 1
            self._previous_distance_m = nearest.distance_forward_m
        else:
            self._previous_distance_m = nearest.distance_forward_m
            self._persistence_frames = 1

        alarm = nearest is not None and self._persistence_frames >= self.confirm_frames
        return {
            "frame_id": int(frame["frame_id"]),
            "status": "public_causal_baseline",
            "candidate_count": len(candidates),
            "persistence_frames": self._persistence_frames,
            "alarm": alarm,
            "nearest_obstacle_m": (
                round(nearest.distance_forward_m, 3) if alarm and nearest else None
            ),
        }


def run(stream_path: Path) -> list[dict]:
    detector = CausalClearancePrototype()
    outputs: list[dict] = []
    for line in stream_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        outputs.append(detector.process(json.loads(line)))
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("stream", type=Path)
    args = parser.parse_args()
    for output in run(args.stream):
        print(json.dumps(output, ensure_ascii=False))


if __name__ == "__main__":
    main()
