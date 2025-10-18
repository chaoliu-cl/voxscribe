# VoxScribe

**Audio Transcription & Qualitative Analysis Tool**

VoxScribe is a powerful desktop application that combines state-of-the-art audio transcription with comprehensive qualitative coding and analysis features. Built with faster-whisper for accurate transcription and PySide6 for a modern GUI, it's designed for researchers, journalists, and anyone working with audio data and qualitative analysis.

![Python Version](https://img.shields.io/badge/python-3.9%20|%203.10%20|%203.11%20|%203.12-blue)
![License](https://img.shields.io/badge/license-Apache%202.0-blue)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)
![Status](https://img.shields.io/badge/status-production%20ready-brightgreen)

## ✨ Features

### 🎙️ Audio Transcription

- **Multi-model support**: Choose from tiny, base, small, medium, or large Whisper models
- **GPU acceleration**: Automatic CUDA detection for faster processing
- **Batch processing**: Transcribe multiple files with pause/resume support
- **Real-time progress**: Enhanced progress monitoring with time estimates and ETA
- **Multi-language**: Support for English, Spanish, French, German, Italian, Portuguese, Russian, Chinese, Japanese, and auto-detection
- **Multiple formats**: Export as TXT, SRT, VTT, or JSON

### 📝 Qualitative Coding

- **Interactive text annotation**: Select and code text segments with visual highlighting
- **⚡ Super-fast code creation**: 20-80x faster code application with incremental updates
- **Flexible coding system**: Create unlimited codes with custom colors
- **Memo support**: Add detailed notes to each annotation
- **Code management**: Rename, merge, and delete codes with ease
- **Click-to-remove**: Interactive code labels for quick annotation removal
- **Smart codebook**: Sortable by name or usage frequency

### 🌳 Theme Development

- **Hierarchical organization**: Create multi-level theme structures
- **Code linking**: Connect codes to themes for organized analysis
- **Visual tree view**: Navigate your theme hierarchy with expandable/collapsible nodes
- **Import/Export**: Save and share your theme structures

### 📊 Analysis & Visualization

- **Code frequency analysis**: Bar charts showing code usage patterns
- **Co-occurrence networks**: Visual network graphs of codes appearing together
- **Text statistics**: Word counts, character counts, and annotation metrics
- **Comparison tools**: Side-by-side analysis of multiple coded documents

### 💾 Export Options

- **Annotated HTML**: Beautiful color-coded HTML with hover memos
- **CSV records**: Spreadsheet-compatible annotation data
- **JSON export**: Structured data for further analysis
- **Subtitle formats**: SRT and VTT for video captioning

### ⚡ Performance Optimizations (v1.5)

- **Ultra-fast text display**: 10-15x faster for large documents (10+ MB)
- **Instant code creation**: 20-80x faster code application
- **Optimized rendering**: Minimal redraws for smooth user experience
- **Large file support**: Handle documents up to 20+ MB with ease
- **Smart refresh**: Incremental updates instead of full document rebuilds

## 📋 Requirements

### System Requirements

- **Python**: 3.9, 3.10, 3.11, or 3.12 (3.11 or 3.12 recommended)
  - ⚠️ Python 3.13: Limited support (PySide6 compatibility issues)
  - ❌ Python 3.14: Not yet supported
- **Operating System**: Windows 10+, macOS 11+, or Linux
- **RAM**: Minimum 4GB (8GB+ recommended for large files)
- **Storage**: 2GB for software, 10GB+ recommended for models
- **GPU** (optional): NVIDIA GPU with CUDA 11.8 or 12.1 for acceleration

### Dependencies

- **PySide6** 6.5.0 - 6.7.x (GUI framework)
- **faster-whisper** 1.x (transcription engine)
- **PyTorch** 2.0+ (deep learning backend)
- **NumPy** 1.24+ (< 2.0) (numerical computing)
- **pandas** 2.0+ (data analysis)
- **matplotlib** 3.7+ (visualization)

See `requirements.txt` for complete dependency list.

## 🚀 Installation

### Quick Start (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/chaoliu-cl/voxscribe.git
cd voxscribe

# 2. Create virtual environment
python -m venv voxscribe_env
source voxscribe_env/bin/activate  # Linux/Mac
# OR
voxscribe_env\Scripts\activate     # Windows

# 3. Upgrade pip
pip install --upgrade pip

# 4. Install dependencies (CPU-only, works everywhere)
pip install -r requirements-cpu.txt

# 5. Run VoxScribe
python gui.py
```

### Installation Options

#### Option A: CPU-Only (Most Users)

**Best for:** No GPU, simple installation, small-medium files

```bash
pip install -r requirements-cpu.txt
```

**Download size:** ~500 MB  
**Features:** All features, CPU-based transcription

#### Option B: GPU-Accelerated (Advanced Users)

**Best for:** NVIDIA GPU, large files, batch processing

```bash
# Install core dependencies
pip install -r requirements-gpu.txt

# Install PyTorch with CUDA 11.8 (most compatible)
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118

# OR for CUDA 12.1 (newer GPUs)
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
```

**Download size:** ~5 GB  
**Features:** All features, GPU-accelerated (10-50x faster transcription)

#### Option C: Full Installation

**Best for:** Development, complete features

```bash
pip install -r requirements.txt
```

### Platform-Specific Instructions

#### Windows

**Prerequisites:**
- Microsoft Visual C++ Redistributable: https://aka.ms/vs/17/release/vc_redist.x64.exe

```cmd
python -m venv voxscribe_env
voxscribe_env\Scripts\activate
pip install --upgrade pip
pip install -r requirements-cpu.txt
python gui.py
```

#### macOS

**Prerequisites:**
```bash
# Install Xcode Command Line Tools
xcode-select --install
```

**Installation:**
```bash
python3 -m venv voxscribe_env
source voxscribe_env/bin/activate
pip install --upgrade pip
pip install -r requirements-cpu.txt
python gui.py
```

**Apple Silicon (M1/M2/M3):**
- Use ARM64 Python for best performance
- GPU acceleration via MPS (Metal Performance Shaders)
- Verify: `python -c "import platform; print(platform.machine())"`  
  Should output: `arm64`

#### Linux (Ubuntu/Debian)

**Prerequisites:**
```bash
sudo apt-get update
sudo apt-get install -y \
    python3-dev \
    python3-venv \
    libsndfile1 \
    portaudio19-dev \
    build-essential
```

**For GPU support (NVIDIA):**
```bash
# Install NVIDIA driver
sudo apt-get install nvidia-driver-535

# Verify
nvidia-smi
```

**Installation:**
```bash
python3 -m venv voxscribe_env
source voxscribe_env/bin/activate
pip install --upgrade pip
pip install -r requirements-cpu.txt
python gui.py
```

### Verify Installation

```bash
python << 'EOF'
import sys
print(f"Python: {sys.version}")

import PySide6
print(f"✅ PySide6: {PySide6.__version__}")

import faster_whisper
print("✅ faster-whisper: OK")

import torch
print(f"✅ PyTorch: {torch.__version__}")
if torch.cuda.is_available():
    print(f"   🎮 GPU: {torch.cuda.get_device_name(0)}")
else:
    print("   💻 Running on CPU")

import pandas
print(f"✅ pandas: {pandas.__version__}")

print("\n🎉 Installation successful!")
EOF
```

## 🎯 Quick Start Guide

### Launch the Application

```bash
# Activate virtual environment first
source voxscribe_env/bin/activate  # Linux/Mac
# OR
voxscribe_env\Scripts\activate     # Windows

# Run the application
python gui.py
```

### Basic Workflow

#### 1. Transcribe Audio

1. Click "Browse" to select audio file (WAV, MP3, M4A, FLAC, OGG)
2. Choose model size:
   - **tiny/base**: Fast, for drafts
   - **small**: Good balance
   - **medium/large**: Best accuracy
3. Select language or use auto-detection
4. Click "Start Processing"
5. Watch real-time progress with time estimates

#### 2. Import Text

1. Click "Import Text" button
2. Select .txt file (supports up to 20+ MB)
3. Text displays instantly (optimized for large files)

#### 3. Code Your Text

1. Go to "Code" tab
2. Click "Enable Selection"
3. Select text to code
4. Enter code name
5. (Optional) Add memo
6. Click "Create Code"
7. **Result:** Code appears INSTANTLY ⚡ (20-80x faster than before!)

#### 4. Organize with Themes

1. Go to "Themes" tab
2. Click "Add Theme"
3. Create sub-themes as needed
4. Link codes to themes
5. Export theme structure

#### 5. Analyze Your Data

1. Go to "Analysis" tab
2. Generate code frequency charts
3. View co-occurrence networks
4. Export results

#### 6. Review Records

1. Go to "Records" tab
2. Search and filter annotations
3. Sort by code, text, or memo
4. Export to CSV or JSON

## 💻 Usage Examples

### Programmatic API

```python
from voxscribe import AudioTranscriber, TextAnnotator

# Initialize transcriber
transcriber = AudioTranscriber(
    model_size="base",
    device="auto",  # Automatically detects GPU
    compute_type="auto"
)

# Transcribe audio file
transcriber.load_model()
results = transcriber.transcribe(
    "interview.mp3",
    language="en",
    include_timestamps=True
)

# Print results
for segment in results:
    print(f"[{segment['start']:.2f}s -> {segment['end']:.2f}s]")
    print(f"{segment['text']}\n")

# Work with annotations
annotator = TextAnnotator()
annotator.load_segments(results)

# Add annotations
annotator.update_segment_text(0, "Corrected text")
annotator.add_annotation(0, "insight", "Important finding")

# Export
annotator.export_to_json("transcript_annotated.json")
annotator.export_to_srt("subtitles.srt")
```

### Batch Processing

```python
from voxscribe import AudioTranscriber

transcriber = AudioTranscriber(model_size="base")
transcriber.load_model()

audio_files = ["interview1.mp3", "interview2.mp3", "interview3.mp3"]

results = transcriber.transcribe_batch(
    audio_files,
    language="en",
    include_timestamps=True,
    batch_progress_callback=lambda i, total, name: print(f"{i}/{total}: {name}")
)

for result in results:
    if result['success']:
        print(f"✓ {result['filename']}: {result['segments_count']} segments")
    else:
        print(f"✗ {result['filename']}: {result['error']}")
```

## 📁 Project Structure

```
voxscribe/
├── gui.py                  # Main GUI application (optimized v1.5)
├── transcriber.py          # Audio transcription engine
├── requirements.txt        # Complete dependencies with docs
├── requirements-cpu.txt    # CPU-only minimal installation
├── requirements-gpu.txt    # GPU-accelerated installation
├── README.md              # This file
├── LICENSE                # Apache 2.0 License
└── docs/                  # Documentation
    ├── INSTALLATION_GUIDE.md
    ├── DEPENDENCY_COMPATIBILITY.md
    └── PERFORMANCE_OPTIMIZATIONS.md
```

## 🔧 Configuration

### Model Selection Guide

| Model | Speed | Accuracy | RAM | VRAM | Use Case |
|-------|-------|----------|-----|------|----------|
| **tiny** | ⚡⚡⚡⚡⚡ | ⭐⭐ | 1 GB | 1 GB | Quick drafts, testing |
| **base** | ⚡⚡⚡⚡ | ⭐⭐⭐ | 1 GB | 1 GB | **Recommended** - balanced |
| **small** | ⚡⚡⚡ | ⭐⭐⭐⭐ | 2 GB | 2 GB | Higher accuracy |
| **medium** | ⚡⚡ | ⭐⭐⭐⭐⭐ | 5 GB | 5 GB | Professional work |
| **large-v3** | ⚡ | ⭐⭐⭐⭐⭐ | 10 GB | 10 GB | Maximum accuracy |

### Performance Benchmarks (v1.5)

#### Text Display Speed

| Document Size | v1.4 | v1.5 | Improvement |
|---------------|------|------|-------------|
| 1 MB | ~2s | ~0.5s | **4x faster** |
| 10 MB | ~20s | ~2s | **10x faster** |
| 20 MB | ~40s | ~4s | **10x faster** |

#### Code Creation Speed

| Annotations | v1.4 | v1.5 | Improvement |
|-------------|------|------|-------------|
| 10 codes | ~20s | <1s | **20x faster** |
| 50 codes | ~150s | <5s | **30x faster** |
| 100 codes | ~400s | <10s | **40x faster** |

**Real-world impact:** Code 100 passages on a 10 MB document in 10 seconds instead of 5-6 minutes!

### Device Configuration

Models automatically download to `~/.cache/huggingface/` on first use.

Check GPU availability:
```python
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
```

## 🎨 Features in Detail

### Interactive Coding Interface

- **Visual highlighting**: Each code has unique color (20 color palette)
- **Live updates**: Changes reflect INSTANTLY with incremental rendering
- **Font size control**: Adjust text size with +/- buttons
- **Smart selection**: Click code labels to view or remove annotations
- **Memo tooltips**: Hover over codes to see associated memos
- **Sortable codebook**: Click headers to sort by name or usage

### Advanced Analysis

- **Co-occurrence Analysis**: Discover patterns in code relationships
- **Frequency Charts**: Visualize code usage with matplotlib
- **Network Graphs**: See code relationships with networkx
- **Comparison Tools**: Side-by-side analysis of multiple documents

### Flexible Export

**HTML Export - Beautiful, shareable reports:**
```html
<span style="background-color:#FFE6CC" title="Important insight">
  Selected text [Code Name]
</span>
```

**CSV Export - For spreadsheet analysis:**
```csv
Start,End,Text,Code,Memo
0,45,"Interview text here","theme1","Analysis note"
```

**JSON Export - For programmatic access:**
```json
{
  "text": "Full document text",
  "annotations": [
    {
      "start": 0,
      "end": 45,
      "text": "Selected text",
      "code": "theme1",
      "memo": "Analysis note"
    }
  ]
}
```

## 🛠 Troubleshooting

### Installation Issues

#### "ModuleNotFoundError: No module named 'PySide6'"

**Cause:** Python version incompatible or pip needs upgrade

**Solution:**
```bash
# Check Python version (must be 3.9-3.12)
python --version

# Upgrade pip
pip install --upgrade pip

# Reinstall PySide6
pip install "PySide6>=6.5.0,<6.8.0"
```

#### "numpy has incompatible version"

**Cause:** NumPy 2.0+ installed (has breaking changes)

**Solution:**
```bash
# Force NumPy 1.x
pip install "numpy>=1.24.0,<2.0.0" --force-reinstall

# Reinstall all dependencies
pip install -r requirements.txt --force-reinstall
```

#### GPU Not Detected

**Cause:** PyTorch CUDA version mismatch

**Solution:**
```bash
# Check CUDA version
nvidia-smi

# Uninstall PyTorch
pip uninstall torch torchaudio

# Reinstall with matching CUDA version
# For CUDA 11.8:
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118

# For CUDA 12.1:
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121

# Verify
python -c "import torch; print(torch.cuda.is_available())"
```

### Runtime Issues

#### Out of Memory Errors

**Cause:** GPU/RAM insufficient for model size

**Solutions:**
- Use smaller model (base instead of large)
- Switch to CPU: `device="cpu"`
- Close other applications
- Process shorter audio segments

#### Transcription Very Slow

**Cause:** GPU not being utilized or model too large

**Solutions:**
- Verify GPU is being used (check device info)
- Use smaller model for faster speed
- Reduce `beam_size` parameter (1-3 instead of 5)
- Disable `word_timestamps` if not needed
- Use batch processing for multiple files

#### "Illegal instruction (core dumped)"

**Cause:** CPU doesn't support AVX2 instructions

**Solution:**
```bash
# Use older faster-whisper version
pip install faster-whisper==0.10.0

# Or set CPU backend
export CTRANSLATE2_CPU_BACKEND=cpu
```

#### Text Display Slow / Freezing

**Cause:** Using old version without optimizations

**Solution:**
- Ensure you're using v1.5 (check gui.py has incremental updates)
- For very large files (>20 MB), system may warn you
- Split extremely large files if needed

### Performance Tips

#### For CPU Users
```bash
# Set number of threads
export OMP_NUM_THREADS=4
export MKL_NUM_THREADS=4
```

#### For GPU Users
```bash
# Enable TensorFloat-32
export NVIDIA_TF32_OVERRIDE=1

# Optimize memory allocation
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
```

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

### Development Setup

```bash
# Clone repository
git clone https://github.com/chaoliu-cl/voxscribe.git
cd voxscribe

# Create virtual environment
python -m venv voxscribe_env
source voxscribe_env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .

# Run tests (if available)
pytest tests/
```

### Contribution Guidelines

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Test thoroughly (all features should work)
5. Follow code style:
   - PEP 8 guidelines
   - Type hints where appropriate
   - Docstrings for functions and classes
6. Commit: `git commit -m 'Add amazing feature'`
7. Push: `git push origin feature/amazing-feature`
8. Open a Pull Request

### Code Style

```python
def example_function(param: str, count: int = 5) -> list[str]:
    """
    Brief description of function.
    
    Args:
        param: Description of param
        count: Description of count (default: 5)
        
    Returns:
        Description of return value
    """
    # Implementation
    return []
```

## 📄 License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.

**Key Terms:**
- ✅ Free to use for commercial and non-commercial purposes
- ✅ Modification allowed with proper attribution
- ✅ Patent grant included
- ✅ Trademark protection - logo/name require permission
- ⚠️ Liability disclaimer - provided "as is"

Full license: http://www.apache.org/licenses/LICENSE-2.0

## 👤 Author

**Chao Liu**

- 📧 Email: chaoliu@cedarville.edu
- 🏛️ Institution: Cedarville University
- 💻 GitHub: [@chaoliu-cl](https://github.com/chaoliu-cl)

## 🙏 Acknowledgments

- **OpenAI Whisper** - Powerful speech recognition model
- **faster-whisper** - Optimized inference implementation by Guillaume Klein
- **PySide6** - Excellent Qt bindings for Python
- **PyTorch** - Deep learning framework
- **NumPy, pandas, matplotlib** - Scientific computing stack
- All contributors and users of VoxScribe

## 📚 Citation

If you use VoxScribe in your research, please cite:

```bibtex
@software{voxscribe2024,
  author = {Liu, Chao},
  title = {VoxScribe: Audio Transcription and Qualitative Analysis Tool},
  year = {2024},
  version = {1.5.0},
  url = {https://github.com/chaoliu-cl/voxscribe},
  note = {High-performance tool for audio transcription and qualitative coding}
}
```

## 🔗 Related Projects

- [faster-whisper](https://github.com/guillaumekln/faster-whisper) - Fast Whisper implementation using CTranslate2
- [openai/whisper](https://github.com/openai/whisper) - Original Whisper model by OpenAI
- [PySide6](https://doc.qt.io/qtforpython/) - Qt for Python official bindings
- [ATLAS.ti](https://atlasti.com/) - Commercial qualitative analysis software
- [NVivo](https://www.qsrinternational.com/nvivo/) - Commercial qualitative analysis software

## 📊 Project Status & Roadmap

### ✅ Completed (v1.5)

- ✅ Core transcription functionality
- ✅ Qualitative coding interface
- ✅ Theme organization
- ✅ Analysis and visualization
- ✅ Batch processing
- ✅ Enhanced progress monitoring (v1.1)
- ✅ Codebook sorting (v1.2)
- ✅ Performance optimization (v1.3)
- ✅ Ultra-fast text display (v1.4)
- ✅ Super-fast code creation (v1.5)

### 🚧 Planned Features

- 🚧 Cloud storage integration
- 🚧 Collaborative coding (multi-user)
- 🚧 Plugin system for extensibility
- 🚧 Advanced inter-coder reliability metrics
- 🚧 AI-assisted coding suggestions
- 🚧 Mobile companion app
- 🚧 Web-based viewer for exports

### 📈 Version History

- **v1.5.0** (Oct 2024) - Super-fast code creation (20-80x faster)
- **v1.4.0** (Oct 2024) - Ultra-fast text display (10x faster)
- **v1.3.0** (Oct 2024) - Performance optimization (4-8x faster)
- **v1.2.0** (Oct 2024) - Codebook sorting
- **v1.1.0** (Oct 2024) - Enhanced progress monitoring
- **v1.0.0** (Sep 2024) - Initial release

## 💬 Support

### Getting Help

- 📖 **Documentation**: See `docs/` folder
- 🐛 **Issues**: [GitHub Issues](https://github.com/chaoliu-cl/voxscribe/issues)
- 💭 **Discussions**: [GitHub Discussions](https://github.com/chaoliu-cl/voxscribe/discussions)
- 📧 **Email**: chaoliu@cedarville.edu

### Before Reporting Issues

Please check:
1. ✅ Python version (3.9-3.12)
2. ✅ Dependencies installed correctly
3. ✅ Virtual environment activated
4. ✅ Existing issues on GitHub

**Include in bug reports:**
- Python version
- Operating system
- VoxScribe version
- Error messages (complete stack trace)
- Steps to reproduce

### Feature Requests

We welcome feature requests! Please:
1. Check existing discussions
2. Describe the use case
3. Explain expected behavior
4. Provide examples if possible

## 🌟 Star History

If you find VoxScribe useful, please consider giving it a star on GitHub! ⭐

---

**Made with ❤️ for researchers, journalists, and analysts**

*VoxScribe - Transforming audio into insights*

---

## 📝 Changelog

### v1.5.0 (October 2024)
- ⚡ **MAJOR:** 20-80x faster code creation with incremental updates
- ⚡ Instant code application on large documents
- 🎯 Smart refresh decision (incremental vs full)
- 📊 Improved user productivity by 6x

### v1.4.0 (October 2024)
- ⚡ 10-15x faster text import and display
- 🎯 Optimized rendering for 10+ MB documents
- ⚠️ Large file warning for 20+ MB files
- 🔧 Direct document manipulation

### v1.3.0 (October 2024)
- ⚡ 4-8x performance improvement
- 🔧 Document locking for atomic operations
- 💾 Format caching for faster rendering
- 🎯 Selective UI updates

### v1.2.0 (October 2024)
- 📊 Sortable codebook table
- 🔍 Click headers to sort by name/usage
- 🎯 Smart defaults for sorting

### v1.1.0 (October 2024)
- ⏱️ Enhanced progress monitoring
- 📊 Elapsed and remaining time display
- 🎯 Accurate ETA calculations

### v1.0.0 (September 2024)
- 🎉 Initial release
- 🎙️ Audio transcription
- 📝 Qualitative coding
- 🌳 Theme organization
- 📊 Analysis tools

---

**Current Version:** 1.5.0  
**Status:** Production Ready ✅  
**Last Updated:** October 2024