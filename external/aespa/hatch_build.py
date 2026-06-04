import requests
import subprocess

from pathlib import Path

from hatchling.builders.hooks.plugin.interface import BuildHookInterface

WEIGHTS_ROOT = "https://github.com/scottdmilner/cs231n-final-project/raw/refs/heads/aespa-net-weights/"

weights = {
    "dec_model.pth": "train_results/aespa/log/dec_model_.pth",
    "transformer_model.pth": "train_results/aespa/log/transformer_model_.pth",
    "vgg_normalised_conv5_1.t7": "baseline_checkpoints/vgg_normalised_conv5_1.pth",
}

class CustomBuildHook(BuildHookInterface):
    dest_root: Path

    def initialize(self, version: str, build_data: dict) -> None:
        self.dest_root = Path(self.root) / "AesPA_Net"
        self.patch_git()
        self.download_weights()

    def patch_git(self) -> None:
        subprocess.run(
            ["git", "apply", "../0001-cuda-mps-weights.patch"],
            cwd=self.dest_root
        )

    def download_weights(self) -> None:
        for weight, dest in weights.items():
            filename = self.dest_root / dest
            if filename.exists():
                continue
            
            filename.parent.mkdir(parents=True, exist_ok=True)
            with open(self.dest_root / dest, "w+b") as f:
                rx = requests.get(WEIGHTS_ROOT + weight)
                rx.raise_for_status()
                f.write(rx.content)
    
