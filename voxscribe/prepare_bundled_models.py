# Copyright 2025 Chao Liu
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Prepare bundled faster-whisper model assets for packaged builds.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import stat
from typing import Iterable

from huggingface_hub import snapshot_download


PROJECT_ROOT = Path(__file__).resolve().parent
BUNDLED_MODELS_DIR = PROJECT_ROOT / "bundled_models"
REQUIRED_MODEL_FILES = ("config.json", "model.bin", "tokenizer.json", "vocabulary.txt")

# Use the standard HTTP download path and longer timeouts while staging models.
os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
os.environ.setdefault("HF_HUB_ETAG_TIMEOUT", "30")
os.environ.setdefault("HF_HUB_DOWNLOAD_TIMEOUT", "120")
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download and stage faster-whisper models for packaged builds.",
    )
    parser.add_argument(
        "--models",
        nargs="+",
        default=["base"],
        help="Model sizes to bundle. Defaults to: base",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Redownload and replace any staged model directories.",
    )
    return parser.parse_args()


def is_complete_model_dir(model_dir: Path) -> bool:
    """Return True when a directory has the required faster-whisper files."""
    return model_dir.is_dir() and all((model_dir / filename).is_file() for filename in REQUIRED_MODEL_FILES)


def _remove_readonly_tree(path: Path) -> None:
    """Delete a directory tree that may contain read-only files on Windows."""
    if not path.exists():
        return

    def handle_remove_readonly(func, target, exc_info):
        del exc_info
        os.chmod(target, stat.S_IWRITE)
        func(target)

    shutil.rmtree(path, onerror=handle_remove_readonly)


def stage_model(model_size: str, *, force: bool) -> Path:
    """Download the requested model into the bundled_models directory."""
    destination = BUNDLED_MODELS_DIR / f"faster-whisper-{model_size}"
    repo_id = f"Systran/faster-whisper-{model_size}"
    metadata_dir = destination / ".cache"

    if force and destination.exists():
        _remove_readonly_tree(destination)

    if is_complete_model_dir(destination):
        if metadata_dir.exists():
            _remove_readonly_tree(metadata_dir)
        print(f"[prepare-bundled-models] Using existing staged model: {destination}")
        return destination

    destination.mkdir(parents=True, exist_ok=True)
    print(f"[prepare-bundled-models] Downloading {repo_id} into {destination}")
    snapshot_download(
        repo_id=repo_id,
        local_dir=destination,
        allow_patterns=list(REQUIRED_MODEL_FILES),
        max_workers=4,
        etag_timeout=float(os.environ["HF_HUB_ETAG_TIMEOUT"]),
    )

    if metadata_dir.exists():
        _remove_readonly_tree(metadata_dir)

    if not is_complete_model_dir(destination):
        raise RuntimeError(
            f"Bundled model directory is incomplete after download: {destination}"
        )

    print(f"[prepare-bundled-models] Staged {repo_id}")
    return destination


def main(models: Iterable[str], *, force: bool) -> None:
    BUNDLED_MODELS_DIR.mkdir(parents=True, exist_ok=True)
    for model_size in models:
        stage_model(model_size, force=force)


if __name__ == "__main__":
    args = parse_args()
    main(args.models, force=args.force)
