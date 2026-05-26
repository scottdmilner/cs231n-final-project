from __future__ import annotations

from enum import StrEnum
from pathlib import Path
from typing import TYPE_CHECKING, cast

import openvdb as vdb

if TYPE_CHECKING:
    GridType = vdb.BoolGrid | vdb.FloatGrid | vdb.Vec3SGrid


class DatasetID(StrEnum):
    SMOKE_LOWRES = "smoke_lowres"
    SMOKE_MIDRES = "smoke_midres"
    SMOKE_HIGHRES = "smoke_highres"
    TORUS = "torus"


DATASET_RES = {
    DatasetID.SMOKE_LOWRES: (100, 100, 100),
    DatasetID.SMOKE_MIDRES: (400, 400, 400),
    DatasetID.SMOKE_HIGHRES: (1000, 1000, 1000),
    DatasetID.TORUS: (20, 20, 20),
}

DATASET_VOXEL_SIZE = {
    DatasetID.SMOKE_LOWRES: 0.2,
    DatasetID.SMOKE_MIDRES: 0.05,
    DatasetID.SMOKE_HIGHRES: 0.02,
    DatasetID.TORUS: 0.1,
}


class DataSet:
    count: int
    dataset: DatasetID
    path: Path

    _instances: dict[DatasetID, DataSet] = {}

    def __init__(self, dataset: DatasetID) -> None:
        self.dataset = dataset
        self.path = Path(f"data/{dataset}")
        self.count = len(list(self.path.glob("*.vdb")))

    @classmethod
    def Get(cls, dataset: DatasetID) -> DataSet:
        if dataset not in cls._instances:
            cls._instances[dataset] = DataSet(dataset)
        return cls._instances[dataset]

    def get_grid[GT: GridType](
        self, grid_name: str, frame: int, *, type: type[GT]
    ) -> GT:
        frame_path = str(self.path / f"{self.dataset}.{frame}.vdb")
        return cast(GT, vdb.read(frame_path, grid_name))

    @property
    def resolution(self) -> tuple[int, int, int]:
        return DATASET_RES[self.dataset]

    @property
    def voxel_size(self) -> float:
        return DATASET_VOXEL_SIZE[self.dataset]


__all__ = ["DatasetID", "DataSet"]
