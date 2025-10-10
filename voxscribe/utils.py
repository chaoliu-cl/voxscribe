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
Utility functions for audio processing and file handling
"""

import os
from typing import Tuple, Optional
import soundfile as sf
from pydub import AudioSegment


def format_time(seconds: float) -> str:
    """
    Format seconds into HH:MM:SS.mmm format
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted time string
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"
    else:
        return f"{minutes:02d}:{secs:06.3f}"


def get_audio_duration(filepath: str) -> Optional[float]:
    """
    Get duration of audio file in seconds
    
    Args:
        filepath: Path to audio file
        
    Returns:
        Duration in seconds, or None if error
    """
    try:
        audio = AudioSegment.from_file(filepath)
        return len(audio) / 1000.0  # Convert to seconds
    except Exception as e:
        print(f"Error getting audio duration: {e}")
        return None


def validate_audio_file(filepath: str) -> Tuple[bool, str]:
    """
    Validate if file is a supported audio format
    
    Args:
        filepath: Path to audio file
        
    Returns:
        Tuple of (is_valid, message)
    """
    if not os.path.exists(filepath):
        return False, "File does not exist"
    
    supported_formats = ['.wav', '.mp3', '.m4a', '.flac', '.ogg', '.opus']
    ext = os.path.splitext(filepath)[1].lower()
    
    if ext not in supported_formats:
        return False, f"Unsupported format. Supported: {', '.join(supported_formats)}"
    
    try:
        # Try to load the file
        duration = get_audio_duration(filepath)
        if duration is None or duration <= 0:
            return False, "Invalid audio file or zero duration"
        
        return True, f"Valid audio file ({format_time(duration)})"
    except Exception as e:
        return False, f"Error reading file: {str(e)}"


def convert_to_wav(input_path: str, output_path: Optional[str] = None) -> str:
    """
    Convert audio file to WAV format
    
    Args:
        input_path: Path to input audio file
        output_path: Path for output WAV file (optional)
        
    Returns:
        Path to the WAV file
    """
    if output_path is None:
        output_path = os.path.splitext(input_path)[0] + '_converted.wav'
    
    audio = AudioSegment.from_file(input_path)
    audio.export(output_path, format='wav')
    
    return output_path


def get_file_size_mb(filepath: str) -> float:
    """
    Get file size in megabytes
    
    Args:
        filepath: Path to file
        
    Returns:
        File size in MB
    """
    size_bytes = os.path.getsize(filepath)
    return size_bytes / (1024 * 1024)