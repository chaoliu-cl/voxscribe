"""
VoxScribe - Audio Transcription & Qualitative Analysis Tool
"""

__version__ = "1.0.0"
__author__ = "Chao Liu"

from .transcriber import AudioTranscriber
from .annotator import TextAnnotator
from .gui import VoxScribeGUI, main

__all__ = [
    'AudioTranscriber',
    'TextAnnotator',
    'VoxScribeGUI',
    'main'
]