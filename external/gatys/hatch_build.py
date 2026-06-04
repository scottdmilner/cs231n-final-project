import requests
import tarfile
import tempfile

from pathlib import Path

from hatchling.builders.hooks.plugin.interface import BuildHookInterface

WEIGHTS_URL = "https://github.com/scottdmilner/cs231n-final-project/raw/refs/heads/gatys-vgg-weights/vgg_conv.pth.tar.xz"

class CustomBuildHook(BuildHookInterface):
    def initialize(self, version: str, build_data: dict) -> None:
        dest_path = Path(self.root) / "gatys/weights"

        if not (dest_path / "vgg_conv.pth").exists():
            dest_path.mkdir(parents=True, exist_ok=True)

            with tempfile.NamedTemporaryFile() as tmpfile:
                rx = requests.get(WEIGHTS_URL)
                rx.raise_for_status()
                tmpfile.write(rx.content)

                with tarfile.open(tmpfile.name, mode="r:xz") as tar:
                    tar.extractall(path=dest_path)
