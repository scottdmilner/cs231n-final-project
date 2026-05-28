import platform
import subprocess

from pathlib import Path

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CustomBuildHook(BuildHookInterface):
    def initialize(self, version: str, build_data: dict) -> None:
        repo_root = Path(self.root) / "StyleID"

        if platform.system() == "Darwin" and platform.processor() == "arm":
            subprocess.run(
                ["git", "apply", "../0001-cuda-mps.patch"],
                cwd=repo_root
            )
        
        subprocess.run(
            ["git", "apply", "../0002-fix-args.patch"],
            cwd=repo_root
        )
        subprocess.run(
            ["git", "apply", "../0003-torch_lightning-version-change.patch"], 
            cwd=repo_root
        )
        subprocess.run(
            ["git", "apply", "../0004-init.py.patch"], 
            cwd=repo_root
        )

        return super().initialize(version, build_data)
