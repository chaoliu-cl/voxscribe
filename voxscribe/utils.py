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

# Try to import audio libraries with fallback handling
try:
    import soundfile as sf
    SOUNDFILE_AVAILABLE = True
except ImportError:
    SOUNDFILE_AVAILABLE = False
    print("Warning: soundfile not available. Some audio features may be limited.")

try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    print("Warning: pydub not available. Some audio features may be limited.")


def format_time(seconds: float) -> str:
    """
    Format seconds into HH:MM:SS.mmm format
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted time string
    """
    if seconds is None:
        return "00:00.000"
    
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
    # Try soundfile first (more reliable)
    if SOUNDFILE_AVAILABLE:
        try:
            with sf.SoundFile(filepath) as audio_file:
                duration = len(audio_file) / audio_file.samplerate
                return duration
        except Exception as e:
            print(f"soundfile error: {e}")
    
    # Fallback to pydub
    if PYDUB_AVAILABLE:
        try:
            audio = AudioSegment.from_file(filepath)
            return len(audio) / 1000.0  # Convert to seconds
        except Exception as e:
            print(f"pydub error: {e}")
    
    # If neither library works, return a default value
    print(f"Warning: Could not determine duration for {filepath}")
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
    
    supported_formats = ['.wav', '.mp3', '.m4a', '.flac', '.ogg', '.opus', '.aac', '.wma']
    ext = os.path.splitext(filepath)[1].lower()
    
    if ext not in supported_formats:
        return False, f"Unsupported format. Supported: {', '.join(supported_formats)}"
    
    # If no audio libraries available, just check file exists and has right extension
    if not SOUNDFILE_AVAILABLE and not PYDUB_AVAILABLE:
        file_size = os.path.getsize(filepath)
        if file_size == 0:
            return False, "File is empty"
        return True, f"File appears valid ({file_size / 1024:.1f} KB)"
    
    try:
        # Try to load the file
        duration = get_audio_duration(filepath)
        if duration is None:
            # If we can't get duration but file exists, assume it's okay
            file_size = os.path.getsize(filepath)
            return True, f"Audio file detected ({file_size / (1024*1024):.1f} MB)"
        
        if duration <= 0:
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
        
    Raises:
        RuntimeError: If pydub is not available
    """
    if not PYDUB_AVAILABLE:
        raise RuntimeError("pydub is required for audio conversion. Install with: pip install pydub")
    
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


def check_audio_dependencies() -> dict:
    """
    Check which audio processing libraries are available
    
    Returns:
        Dictionary with availability status of each library
    """
    return {
        'soundfile': SOUNDFILE_AVAILABLE,
        'pydub': PYDUB_AVAILABLE,
    }


def get_dependency_install_instructions() -> str:
    """
    Get instructions for installing missing dependencies
    
    Returns:
        String with installation instructions
    """
    instructions = []
    
    if not SOUNDFILE_AVAILABLE:
        instructions.append("soundfile: pip install soundfile")
    
    if not PYDUB_AVAILABLE:
        instructions.append("pydub: pip install pydub")
    
    if instructions:
        return "Missing dependencies. Install with:\n" + "\n".join(instructions)
    else:
        return "All audio dependencies are installed!"