# VoxScribe Installation Guide

## Quick Start

```bash
# 1. Create virtual environment
python -m venv voxscribe_env

# 2. Activate it
source voxscribe_env/bin/activate  # Linux/Mac
# OR
voxscribe_env\Scripts\activate     # Windows

# 3. Install
pip install -r requirements.txt

# 4. Run
python gui.py
```

---

## Detailed Installation

### Step 1: Check Python Version

**Required:** Python 3.9 - 3.12  
**Recommended:** Python 3.11 or 3.12

```bash
python --version
```

**If you don't have the right version:**

- **Windows:** Download from [python.org](https://www.python.org/downloads/)
- **macOS:** Use `brew install python@3.11`
- **Linux:** Use your package manager (apt, dnf, etc.)

---

### Step 2: Create Virtual Environment

**Why use a virtual environment?**
- Isolates dependencies
- Prevents conflicts with other projects
- Easy to reset if something goes wrong

```bash
# Navigate to VoxScribe directory
cd /path/to/voxscribe

# Create virtual environment
python -m venv voxscribe_env

# Activate it
# On Linux/Mac:
source voxscribe_env/bin/activate

# On Windows:
voxscribe_env\Scripts\activate

# Your prompt should now show (voxscribe_env)
```

---

### Step 3: Upgrade pip

```bash
pip install --upgrade pip setuptools wheel
```

---

### Step 4: Choose Installation Type

#### Option A: Standard (CPU-Only) - Recommended for Most Users

```bash
pip install -r requirements-cpu.txt
```

**Use if:**
- You don't have an NVIDIA GPU
- You want simplest installation
- File sizes are small-medium (< 30 minutes of audio)

---

#### Option B: GPU-Accelerated (Faster)

**Check if you have compatible GPU:**
```bash
nvidia-smi
```

If this works and shows CUDA version, install GPU version:

```bash
# Install core dependencies first
pip install -r requirements-gpu.txt

# Then install PyTorch with CUDA
# For CUDA 11.8 (most compatible):
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118

# OR for CUDA 12.1 (newer GPUs):
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
```

**Verify GPU is detected:**
```bash
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

---

#### Option C: Full Installation (Everything)

```bash
pip install -r requirements.txt
```

---

### Step 5: Verify Installation

```bash
# Test imports
python -c "import PySide6; print('✓ PySide6 OK')"
python -c "import faster_whisper; print('✓ faster-whisper OK')"
python -c "import pandas; print('✓ pandas OK')"

# Or run comprehensive check:
python << 'EOF'
import sys
print(f"Python: {sys.version}")

try:
    import PySide6
    print("✅ PySide6:", PySide6.__version__)
except ImportError as e:
    print("❌ PySide6:", e)

try:
    import faster_whisper
    print("✅ faster-whisper: OK")
except ImportError as e:
    print("❌ faster-whisper:", e)

try:
    import torch
    print(f"✅ PyTorch: {torch.__version__}")
    if torch.cuda.is_available():
        print(f"   🎮 GPU: {torch.cuda.get_device_name(0)}")
    else:
        print("   💻 Running on CPU")
except ImportError as e:
    print("❌ PyTorch:", e)

try:
    import pandas
    print(f"✅ pandas: {pandas.__version__}")
except ImportError as e:
    print("❌ pandas:", e)

print("\nInstallation complete!")
EOF
```

---

### Step 6: Run VoxScribe

```bash
python gui.py
```

If the GUI opens, you're all set! 🎉

---

## Platform-Specific Instructions

### Windows

**Prerequisites:**
1. Microsoft Visual C++ Redistributable
   - Download: https://aka.ms/vs/17/release/vc_redist.x64.exe
   - Install it before installing VoxScribe

**Installation:**
```cmd
REM Open Command Prompt as Administrator
cd C:\path\to\voxscribe

REM Create venv
python -m venv voxscribe_env

REM Activate
voxscribe_env\Scripts\activate

REM Upgrade pip
python -m pip install --upgrade pip

REM Install
pip install -r requirements.txt

REM Run
python gui.py
```

**Common Windows Issues:**

| Issue | Solution |
|-------|----------|
| "python not recognized" | Add Python to PATH or use `py` instead |
| DLL load failed | Install VC++ Redistributable |
| Qt platform plugin error | Set `QT_QPA_PLATFORM_PLUGIN_PATH` environment variable |

---

### macOS

**Prerequisites:**
```bash
# Install Xcode Command Line Tools
xcode-select --install
```

**Installation:**
```bash
cd /path/to/voxscribe

# Create venv
python3 -m venv voxscribe_env

# Activate
source voxscribe_env/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install
pip install -r requirements.txt

# Run
python gui.py
```

**Apple Silicon (M1/M2/M3) Specific:**

```bash
# Verify you're using ARM64 Python
python -c "import platform; print(platform.machine())"
# Should output: arm64

# Install with MPS (Metal Performance Shaders) support
pip install -r requirements.txt

# PyTorch will use GPU acceleration via MPS
```

---

### Linux (Ubuntu/Debian)

**Prerequisites:**
```bash
# Update system
sudo apt-get update

# Install system dependencies
sudo apt-get install -y \
    python3-dev \
    python3-venv \
    libsndfile1 \
    portaudio19-dev \
    build-essential \
    git
```

**For GPU Support (NVIDIA):**
```bash
# Install NVIDIA driver
sudo apt-get install nvidia-driver-535

# Reboot
sudo reboot

# Verify
nvidia-smi
```

**Installation:**
```bash
cd /path/to/voxscribe

# Create venv
python3 -m venv voxscribe_env

# Activate
source voxscribe_env/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install
pip install -r requirements.txt

# Run
python gui.py
```

---

### Linux (Fedora/RHEL)

**Prerequisites:**
```bash
sudo dnf install -y \
    python3-devel \
    libsndfile \
    portaudio-devel \
    gcc gcc-c++ \
    git
```

**Installation:** Same as Ubuntu above

---

### Linux (Arch)

**Prerequisites:**
```bash
sudo pacman -S \
    python \
    python-pip \
    libsndfile \
    portaudio \
    base-devel \
    git
```

**Installation:** Same as Ubuntu above

---

## Troubleshooting

### Installation Failures

**Issue: "Could not find a version that satisfies the requirement PySide6"**

**Solution:**
```bash
# Check Python version (must be 3.9-3.12)
python --version

# Upgrade pip
pip install --upgrade pip

# Try installing PySide6 separately
pip install PySide6
```

---

**Issue: "ERROR: Could not build wheels for X"**

**Solution:**
```bash
# Install build tools
# Windows: Install Visual Studio Build Tools
# macOS: xcode-select --install
# Linux: sudo apt-get install build-essential python3-dev

# Upgrade pip and try again
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

---

**Issue: "Illegal instruction (core dumped)" when running**

**Cause:** CPU doesn't support AVX2 instructions

**Solution:**
```bash
# Use older faster-whisper version
pip install faster-whisper==0.10.0

# Or use CPU-only mode with explicit backend
# Set environment variable:
export CTRANSLATE2_CPU_BACKEND=cpu
```

---

**Issue: "CUDA out of memory"**

**Solution:**
```bash
# Use smaller model
# In VoxScribe, select "tiny", "base", or "small" model

# Or increase GPU memory by closing other applications

# Check GPU memory usage:
nvidia-smi
```

---

**Issue: PyTorch not detecting GPU**

**Solution:**
```bash
# Check NVIDIA driver
nvidia-smi

# Check CUDA version from nvidia-smi
# Install matching PyTorch

# Uninstall current PyTorch
pip uninstall torch torchaudio

# Install with correct CUDA version
# For CUDA 11.8:
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118

# For CUDA 12.1:
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121

# Verify
python -c "import torch; print(torch.cuda.is_available())"
```

---

### Runtime Issues

**Issue: GUI doesn't start / crashes immediately**

**Check:**
```bash
# Run with verbose output
python gui.py --verbose  # if supported

# Or check for errors:
python -c "from PySide6.QtWidgets import QApplication; app = QApplication([]); print('OK')"
```

**Common fixes:**
- Update graphics drivers
- Try different Qt platform plugin: `export QT_QPA_PLATFORM=xcb` (Linux)
- Reinstall PySide6: `pip install --force-reinstall PySide6`

---

**Issue: Audio file won't import**

**Check:**
```bash
# Test audio library
python -c "import soundfile; print(soundfile.available_formats())"

# Install additional codecs
pip install audioread pydub
```

---

**Issue: Transcription very slow**

**Solutions:**
1. Use GPU if available
2. Use smaller model (tiny/base instead of large)
3. Close other applications
4. Check CPU usage - make sure it's being utilized

---

## Advanced Configuration

### Custom Installation Paths

```bash
# Install to specific location
pip install -r requirements.txt --target=/custom/path

# Add to Python path
export PYTHONPATH=/custom/path:$PYTHONPATH
```

---

### Offline Installation

```bash
# On machine with internet:
pip download -r requirements.txt -d packages/

# Transfer packages/ folder to offline machine

# On offline machine:
pip install --no-index --find-links=packages/ -r requirements.txt
```

---

### Development Installation

```bash
# Install in editable mode
pip install -e .

# Install with development dependencies
pip install -r requirements.txt
pip install pytest pytest-qt black flake8
```

---

## Updating VoxScribe

### Update Dependencies

```bash
# Activate environment
source voxscribe_env/bin/activate  # or Windows equivalent

# Update all packages
pip install --upgrade -r requirements.txt

# Or update specific package
pip install --upgrade PySide6
```

### Update VoxScribe Code

```bash
# If using git
git pull origin main

# If using downloaded files
# Replace files with new versions
```

---

## Uninstallation

```bash
# Deactivate virtual environment
deactivate

# Remove virtual environment
rm -rf voxscribe_env  # Linux/Mac
# OR
rmdir /s voxscribe_env  # Windows

# Models are stored separately, to remove:
rm -rf ~/.cache/huggingface/  # Linux/Mac
# OR
rmdir /s %USERPROFILE%\.cache\huggingface  # Windows
```

---

## Performance Tuning

### For CPU Users

```bash
# Set number of threads (experiment with values)
export OMP_NUM_THREADS=4
export MKL_NUM_THREADS=4

# Run VoxScribe
python gui.py
```

### For GPU Users

```bash
# Enable TensorFloat-32 for faster training (if supported)
export NVIDIA_TF32_OVERRIDE=1

# Set GPU memory allocation strategy
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
```

---

## Getting Help

**If you encounter issues:**

1. **Check this guide** - most common issues are covered
2. **Check compatibility matrix** - verify your versions
3. **Search error messages** - often others have seen same issue
4. **Check system requirements** - ensure your system meets minimums

**System Information to Collect:**

```bash
# Create diagnostic report
python << 'EOF'
import sys
import platform
print("=" * 60)
print("SYSTEM INFORMATION")
print("=" * 60)
print(f"OS: {platform.system()} {platform.release()}")
print(f"Python: {sys.version}")
print(f"Architecture: {platform.machine()}")

try:
    import PySide6
    print(f"PySide6: {PySide6.__version__}")
except:
    print("PySide6: NOT INSTALLED")

try:
    import torch
    print(f"PyTorch: {torch.__version__}")
    print(f"CUDA: {torch.cuda.is_available()}")
except:
    print("PyTorch: NOT INSTALLED")

try:
    import faster_whisper
    print("faster-whisper: INSTALLED")
except:
    print("faster-whisper: NOT INSTALLED")

print("=" * 60)
EOF
```

---

## Summary

### Minimum Installation (Most Users)

```bash
python -m venv voxscribe_env
source voxscribe_env/bin/activate
pip install --upgrade pip
pip install -r requirements-cpu.txt
python gui.py
```

### GPU Installation (Advanced Users)

```bash
python -m venv voxscribe_env
source voxscribe_env/bin/activate
pip install --upgrade pip
pip install -r requirements-gpu.txt
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118
python gui.py
```

---

**Estimated Installation Time:**
- Slow internet: 10-15 minutes
- Fast internet: 3-5 minutes
- Offline (with downloaded packages): < 2 minutes

**Disk Space Required:**
- Minimal: 500 MB
- Standard: 2 GB
- With GPU: 5 GB
- With models: 10+ GB

---

**Installation Status Checklist:**

- [ ] Python 3.9-3.12 installed
- [ ] Virtual environment created and activated
- [ ] pip upgraded
- [ ] Dependencies installed from requirements.txt
- [ ] All imports working (verification script passes)
- [ ] GUI launches successfully
- [ ] (Optional) GPU detected and working

If all checked, you're ready to use VoxScribe! 🎉

---

**Last Updated:** October 2024  
**Tested On:** Windows 11, macOS 14, Ubuntu 22.04  
**Status:** ✅ Production Ready
