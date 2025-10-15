"""
VoxScribe Import Troubleshooting Script
Run this to diagnose import issues
"""

import sys
import os
from pathlib import Path

print("=" * 70)
print("VOXSCRIBE IMPORT TROUBLESHOOTING")
print("=" * 70)

# 1. Check Python version
print(f"\n1. Python Version: {sys.version}")
print(f"   Python Executable: {sys.executable}")

# 2. Check current working directory
print(f"\n2. Current Working Directory: {os.getcwd()}")

# 3. Check Python path
print(f"\n3. Python Path (sys.path):")
for i, path in enumerate(sys.path, 1):
    print(f"   {i}. {path}")

# 4. Check if faster-whisper is installed
print(f"\n4. Checking faster-whisper installation:")
try:
    import faster_whisper
    print(f"   ✓ faster-whisper is installed")
    print(f"   Version: {faster_whisper.__version__ if hasattr(faster_whisper, '__version__') else 'Unknown'}")
    print(f"   Location: {faster_whisper.__file__}")
except ImportError as e:
    print(f"   ✗ faster-whisper is NOT installed")
    print(f"   Error: {e}")

# 5. Check if local modules exist
print(f"\n5. Checking local module files:")
current_dir = Path(os.getcwd())
module_files = ['transcriber.py', 'annotator.py', 'utils.py', 'gui.py']

for module_file in module_files:
    file_path = current_dir / module_file
    if file_path.exists():
        print(f"   ✓ {module_file} exists at {file_path}")
        print(f"     Size: {file_path.stat().st_size} bytes")
    else:
        print(f"   ✗ {module_file} NOT FOUND")
        # Check parent directory
        parent_path = current_dir.parent / module_file
        if parent_path.exists():
            print(f"     (Found in parent: {parent_path})")

# 6. Try importing local modules
print(f"\n6. Testing local module imports:")

# Test transcriber.py
print(f"\n   Testing 'transcriber' module:")
try:
    import transcriber
    print(f"   ✓ Successfully imported transcriber")
    print(f"   Location: {transcriber.__file__}")
    print(f"   Has AudioTranscriber: {hasattr(transcriber, 'AudioTranscriber')}")
except ImportError as e:
    print(f"   ✗ Failed to import transcriber")
    print(f"   Error: {e}")

# Test annotator.py
print(f"\n   Testing 'annotator' module:")
try:
    import annotator
    print(f"   ✓ Successfully imported annotator")
    print(f"   Location: {annotator.__file__}")
    print(f"   Has TextAnnotator: {hasattr(annotator, 'TextAnnotator')}")
except ImportError as e:
    print(f"   ✗ Failed to import annotator")
    print(f"   Error: {e}")

# Test utils.py
print(f"\n   Testing 'utils' module:")
try:
    import utils
    print(f"   ✓ Successfully imported utils")
    print(f"   Location: {utils.__file__}")
    print(f"   Has validate_audio_file: {hasattr(utils, 'validate_audio_file')}")
except ImportError as e:
    print(f"   ✗ Failed to import utils")
    print(f"   Error: {e}")

# 7. Check dependencies
print(f"\n7. Checking other dependencies:")
dependencies = [
    'PySide6',
    'numpy',
    'pandas',
    'matplotlib',
    'networkx',
    'soundfile',
    'pydub',
    'torch'
]

for dep in dependencies:
    try:
        module = __import__(dep)
        version = getattr(module, '__version__', 'Unknown')
        print(f"   ✓ {dep}: {version}")
    except ImportError:
        print(f"   ✗ {dep}: NOT INSTALLED")

# 8. Provide recommendations
print(f"\n" + "=" * 70)
print("RECOMMENDATIONS:")
print("=" * 70)

# Check structure
if not (current_dir / 'transcriber.py').exists():
    print("\n⚠️  Module files not found in current directory!")
    print("   Make sure you're running the script from the directory containing:")
    print("   - transcriber.py")
    print("   - annotator.py")
    print("   - utils.py")
    print("   - gui.py")
    print(f"\n   Current directory: {current_dir}")
    print(f"   Please cd to the correct directory and try again.")

# Check faster-whisper
try:
    import faster_whisper
except ImportError:
    print("\n⚠️  faster-whisper is not installed!")
    print("   Install it with:")
    print("   pip install faster-whisper")

# Check if running as package vs script
print(f"\n📁 Project Structure:")
print(f"   If your files are in a package/folder structure, you may need to:")
print(f"   1. Run from the parent directory")
print(f"   2. Or adjust sys.path in gui.py")
print(f"   3. Or use absolute imports")

print("\n" + "=" * 70)
print("Troubleshooting complete!")
print("=" * 70)
