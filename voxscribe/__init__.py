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
VoxScribe - Audio Transcription & Qualitative Analysis Tool
"""

__version__ = "1.0.1"
__author__ = "Chao Liu"

from .transcriber import AudioTranscriber
from .annotator import TextAnnotator

# Try to import GUI components, but don't fail if display is not available
try:
    from .gui import VoxScribeGUI, main
    __all__ = [
        'AudioTranscriber',
        'TextAnnotator',
        'VoxScribeGUI',
        'main'
    ]
except (ImportError, RuntimeError) as e:
    # GUI not available (headless environment or missing dependencies)
    import warnings
    warnings.warn(
        f"GUI components not available: {e}. "
        "Core transcription and annotation features are still functional.",
        ImportWarning
    )
    __all__ = [
        'AudioTranscriber',
        'TextAnnotator'
    ]
