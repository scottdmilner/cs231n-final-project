import subprocess

from pathlib import Path

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CustomBuildHook(BuildHookInterface):
    def initialize(self, version: str, build_data: dict) -> None:
        repo_root = Path(self.root) / "openvdb"
        
        subprocess.run(
            ["git", "apply", "../0001-python-bindings.patch"],
            cwd=repo_root
        )

        return super().initialize(version, build_data)
