# VoxScribe

**Audio Transcription & Qualitative Analysis Tool**

VoxScribe is a powerful desktop application that combines state-of-the-art audio transcription with comprehensive qualitative coding and analysis features. Built with faster-whisper for accurate transcription and PySide6 for a modern GUI, it's designed for researchers, journalists, and anyone working with audio data and qualitative analysis.

![Python Version](https://img.shields.io/badge/python-3.8--3.13-blue)
![License](https://img.shields.io/badge/license-Apache%202.0-blue)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

## ✨ Features

### 🎙️ Audio Transcription

- **Multi-model support**: Choose from tiny, base, small, medium, or large Whisper models
- **GPU acceleration**: Automatic CUDA detection for faster processing
- **Batch processing**: Transcribe multiple files with pause/resume support
- **Real-time progress tracking**: Monitor transcription progress with time estimates
- **Multi-language**: Support for English, Spanish, French, German, Italian, Portuguese, Russian, Chinese, Japanese, and auto-detection
- **Multiple formats**: Export as TXT, SRT, VTT, or JSON

### 📝 Qualitative Coding

- **Interactive text annotation**: Select and code text segments with visual highlighting
- **Flexible coding system**: Create unlimited codes with custom colors
- **Memo support**: Add detailed notes to each annotation
- **Code management**: Rename, merge, and delete codes with ease
- **Click-to-remove**: Interactive code labels for quick annotation removal
- **Font size control**: Adjust text display size for comfortable reading
- **Optimized performance**: Fast rendering even with large documents and many annotations

### 🌳 Theme Development

- **Hierarchical organization**: Create multi-level theme structures
- **Drag-and-drop reorganization**: Easily rearrange themes and codes by dragging
- **Code linking**: Connect codes to themes for organized analysis
- **Visual tree view**: Navigate your theme hierarchy with expandable/collapsible nodes
- **Import/Export**: Save and share your theme structures

### 📊 Analysis & Visualization

- **Code frequency analysis**: Bar charts showing code usage patterns
- **Co-occurrence networks**: Visual network graphs of codes appearing together
- **Text statistics**: Word counts, character counts, and annotation metrics
- **Comparison tools**: Side-by-side analysis of multiple coded documents
- **HTML import support**: Compare previously saved annotated documents

### 💾 Export Options

- **Annotated HTML**: Beautiful color-coded HTML with hover memos
- **CSV records**: Spreadsheet-compatible annotation data
- **JSON export**: Structured data for further analysis
- **Subtitle formats**: SRT and VTT for video captioning

## 📋 Requirements

- **Python**: 3.8 - 3.13 (Python 3.14+ not yet supported)
- **Operating System**: Windows, macOS, or Linux
- **RAM**: Minimum 4GB (8GB+ recommended for large files)
- **GPU** (optional): NVIDIA GPU with CUDA 11.8 or 12.1 for acceleration

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/chaoliu-cl/voxscribe.git
cd voxscribe
```

### 2. Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

**Option A: CPU-only (works on all systems)**
```bash
pip install -r requirements.txt
```

**Option B: With CUDA 11.8 (NVIDIA GPU)**
```bash
pip install torch --index-url https://download.pytorch.org/whl/cu118
pip install -r requirements.txt
```

**Option C: With CUDA 12.1 (NVIDIA GPU)**
```bash
pip install torch --index-url https://download.pytorch.org/whl/cu121
pip install -r requirements.txt
```

**Python 3.13 Users:**
```bash
# Python 3.13 is supported but some optional features may be limited
# (pydub may not be available due to removed pyaudioop module)
pip install -r requirements.txt
```

**Note**: Python 3.14+ is not yet supported. Please use Python 3.8 - 3.13.

### 4. Verify Installation

```bash
python -c "import PySide6; print(f'PySide6 {PySide6.__version__}')"
python -c "import soundfile; print(f'soundfile {soundfile.__version__}')"
python -c "import faster_whisper; print('faster-whisper OK')"
```

## 🎯 Quick Start

### Launch the Application

```bash
python gui.py
```

Or, if installed via `pip install -e .`:
```bash
python -m voxscribe.gui
```

### Basic Workflow

1. **Transcribe Audio**
   - Choose between "Single File" or "Batch Processing" mode
   - Click "Browse" to select audio file(s) (WAV, MP3, M4A, FLAC, OGG)
   - Choose model size (base recommended for most uses)
   - Select language or use auto-detection
   - Optionally select output directory for batch mode
   - Click "Start Processing"
   - Watch real-time progress with time estimates
   - Use Pause/Resume buttons for batch processing

2. **Code Your Text**
   - Go to the "Code" tab
   - Import text or use transcription results
   - Click "Enable Selection"
   - Select text you want to code
   - Enter a code name and optional memo
   - Click "Create Code" or "Apply Code"
   - Click code labels in text to remove annotations

3. **Organize with Themes**
   - Go to the "Themes" tab
   - Create themes and sub-themes
   - Link codes to themes for organization
   - Drag and drop to reorganize your hierarchy
   - Export/import theme structures

4. **Analyze Your Data**
   - Go to the "Analysis" tab
   - Generate code frequency charts
   - View co-occurrence networks
   - Get text summaries with statistics
   - Export visualizations

5. **Review Records**
   - Go to the "Records" tab
   - Search and filter annotations
   - Sort by any column
   - Export to CSV or JSON

6. **Compare Documents**
   - Go to the "Comparison" tab
   - Load two coded documents (JSON, CSV, or HTML)
   - Run comparison analysis
   - View side-by-side code distributions

## 💻 Usage Examples

### Programmatic API

```python
from transcriber import AudioTranscriber
from annotator import TextAnnotator

# Initialize transcriber
transcriber = AudioTranscriber(
    model_size="base",
    device="auto",  # Automatically detects GPU
    compute_type="auto"
)

# Transcribe audio file with progress callback
def progress_callback(segment_count, processed_duration, total_duration, elapsed_time):
    if total_duration:
        progress_pct = (processed_duration / total_duration) * 100
        print(f"Progress: {progress_pct:.1f}% - {segment_count} segments - {elapsed_time:.1f}s elapsed")

transcriber.load_model()
results = transcriber.transcribe(
    "interview.mp3",
    language="en",
    include_timestamps=True,
    progress_callback=progress_callback
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
annotator.export_to_txt("transcript.txt")
```

### Batch Processing

```python
from transcriber import AudioTranscriber

transcriber = AudioTranscriber(model_size="base")
transcriber.load_model()

audio_files = ["interview1.mp3", "interview2.mp3", "interview3.mp3"]

def batch_callback(file_num, total_files, filename):
    print(f"Processing {file_num}/{total_files}: {filename}")

results = transcriber.transcribe_batch(
    audio_files,
    language="en",
    include_timestamps=True,
    batch_progress_callback=batch_callback
)

for result in results:
    if result['success']:
        print(f"✓ {result['filename']}: {result['segments_count']} segments in {result['processing_time']:.1f}s")
    else:
        print(f"✗ {result['filename']}: {result['error']}")
```

## 📁 Project Structure

```
voxscribe/
├── transcriber.py          # Audio transcription engine
├── annotator.py            # Text annotation manager
├── gui.py                  # PySide6 GUI application
├── utils.py                # Utility functions
├── requirements.txt        # Python dependencies
├── .gitignore             # Git ignore rules
├── LICENSE                # Apache License 2.0
└── README.md              # This file
```

## 🔧 Configuration

### Model Selection Guide

| Model Size | Speed | Accuracy | RAM Usage | Use Case |
|------------|-------|----------|-----------|----------|
| tiny | ⚡⚡⚡⚡⚡ | ⭐⭐ | ~1 GB | Quick drafts, testing |
| base | ⚡⚡⚡⚡ | ⭐⭐⭐ | ~1 GB | Recommended - balanced |
| small | ⚡⚡⚡ | ⭐⭐⭐⭐ | ~2 GB | Higher accuracy needed |
| medium | ⚡⚡ | ⭐⭐⭐⭐⭐ | ~5 GB | Professional transcription |
| large-v2 | ⚡ | ⭐⭐⭐⭐⭐ | ~10 GB | Maximum accuracy |
| large-v3 | ⚡ | ⭐⭐⭐⭐⭐ | ~10 GB | Latest model, best quality |

### Device Configuration

Models automatically download to `~/.cache/voxscribe/` on first use.

Check GPU availability:
```python
from transcriber import AudioTranscriber
transcriber = AudioTranscriber()
print(transcriber.get_device_info())
```

## 🎨 Features in Detail

### Interactive Coding Interface

- **Visual highlighting**: Each code has a unique color for easy identification
- **Live updates**: Changes reflect immediately in the display
- **Font size control**: Adjust text size with +/- buttons (8-32pt range)
- **Smart selection**: Click code labels to view or remove annotations
- **Memo tooltips**: Hover over codes to see associated memos
- **Optimized rendering**: Fast display even with thousands of annotations
- **Sortable codebook**: Click column headers to sort by code name or usage count

### Advanced Theme Organization

- **Drag-and-drop**: Click and drag any theme or code to reorganize
- **Visual feedback**: See drop indicators while dragging
- **Automatic sync**: Internal structure updates automatically after moves
- **Multi-level hierarchy**: Unlimited nesting of themes and sub-themes
- **Expandable tree**: Collapse/expand sections for better navigation

### Advanced Analysis

- **Co-occurrence Analysis**: Discover patterns in how codes appear together
- **Frequency Charts**: Visualize which codes are used most often
- **Network Graphs**: See relationships between codes in visual networks
- **Comparison Tools**: Load multiple coded documents for side-by-side analysis
- **HTML Import**: Compare previously saved annotated HTML files

### Flexible Export

**HTML Export - Beautiful, shareable reports:**
```html
<span style="background-color:#FFE6CC" title="Important insight">
  Selected text <strong>[Code Name]</strong>
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
  ],
  "codes": ["theme1", "theme2"],
  "code_colors": {"theme1": "#FFE6CC"}
}
```

## 🐛 Troubleshooting

### Python 3.13 Compatibility Issues

**Issue**: "No module named 'pyaudioop'" error on Python 3.13

**Solution:**
```bash
# The app works fine without pydub using soundfile
pip install faster-whisper numpy soundfile PySide6 torch pandas matplotlib networkx
```

**Note**: Some audio format conversion features may be limited on Python 3.13 due to pydub compatibility. The core transcription and coding features work perfectly.

### Python 3.14+ Not Supported

**Issue**: Python 3.14 or newer

**Solution:**
```bash
# Use Python 3.8 - 3.13
python3.13 -m venv venv  # or any version from 3.8 to 3.13
source venv/bin/activate
pip install -r requirements.txt
```

### Models Won't Download

**Issue**: First-time model download fails

**Solution:**
```bash
# Manually specify cache directory
export VOXSCRIBE_CACHE="/path/to/cache"  # Linux/Mac
set VOXSCRIBE_CACHE=C:\path\to\cache     # Windows

# Or use a different cache location
mkdir -p ~/.cache/voxscribe
```

### GPU Not Detected

**Issue**: CUDA-capable GPU not being used

**Solution:**
```bash
# Verify PyTorch can see your GPU
python -c "import torch; print(torch.cuda.is_available())"
python -c "import torch; print(torch.cuda.get_device_name(0))"

# If False, reinstall PyTorch with CUDA
pip uninstall torch
pip install torch --index-url https://download.pytorch.org/whl/cu121
```

### Out of Memory Errors

**Issue**: GPU runs out of memory with large files

**Solution:**
- Use a smaller model (e.g., "base" instead of "large")
- Process files in smaller chunks
- Switch to CPU processing: `device="cpu"`
- Close other GPU-intensive applications
- Use batch processing sequentially (not parallel) for GPU

### Transcription Taking Too Long

**Issue**: Transcription is slower than expected

**Solutions:**
- Ensure GPU acceleration is enabled (check device info)
- Use a smaller model for faster processing
- Reduce `beam_size` parameter (default: 5, try: 1-3)
- Disable `word_timestamps` if not needed
- Use batch processing for multiple files
- Check that VAD filter is enabled for better speed

### Import Errors

**Issue**: ModuleNotFoundError when running

**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Reinstall dependencies
pip install -r requirements.txt

# Verify critical packages
python -c "import PySide6, soundfile, faster_whisper; print('All OK')"
```

### Large File Performance

**Issue**: Slow performance with large documents or many annotations

**Solution:**
- The app uses optimized rendering for large documents
- Use "Refresh Display" button if needed
- Font size changes trigger smart re-rendering
- Incremental updates are used when adding new annotations
- Close unused tabs to free memory

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Test thoroughly
5. Commit your changes: `git commit -m 'Add amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

### Development Setup

```bash
git clone https://github.com/chaoliu-cl/voxscribe.git
cd voxscribe

# Use Python 3.8 - 3.13 (3.14+ not supported)
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

pip install -r requirements.txt
```

### Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Add docstrings to all functions and classes
- Write unit tests for new features
- Comment performance-critical sections

## 📝 License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.

```
Apache License
Version 2.0, January 2004
http://www.apache.org/licenses/

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

### Key Terms

- **Free to use** for commercial and non-commercial purposes
- **Modification allowed** with proper attribution
- **Patent grant** included (protection for contributors)
- **Trademark protection** - logo/name require permission
- **Liability disclaimer** - provided "as is"

## 👤 Author

**Chao Liu**

- Email: chaoliu@cedarville.edu
- Institution: Cedarville University
- GitHub: @chaoliu-cl

## 🙏 Acknowledgments

- **OpenAI Whisper**: For the powerful speech recognition model
- **faster-whisper**: For the optimized inference implementation
- **PySide6**: For the excellent Qt bindings
- **PyTorch**: For the deep learning framework
- **soundfile**: For reliable audio file handling
- All contributors and users of VoxScribe

## 📚 Citation

If you use VoxScribe in your research, please cite:

```bibtex
@software{voxscribe2025,
  author = {Liu, Chao},
  title = {VoxScribe: Audio Transcription and Qualitative Analysis Tool},
  year = {2025},
  url = {https://github.com/chaoliu-cl/voxscribe}
}
```

## 🔗 Related Projects

- [faster-whisper](https://github.com/guillaumekln/faster-whisper) - Fast Whisper implementation
- [openai/whisper](https://github.com/openai/whisper) - Original Whisper model
- [PySide6](https://doc.qt.io/qtforpython/) - Qt for Python

## 📊 Project Status

- ✅ Core transcription functionality
- ✅ Real-time progress tracking with time estimates
- ✅ Qualitative coding interface
- ✅ Theme organization with drag-and-drop
- ✅ Analysis and visualization
- ✅ Batch processing with pause/resume
- ✅ Performance optimizations for large documents
- ✅ Python 3.13 compatibility
- 🚧 Cloud storage integration (planned)
- 🚧 Collaborative coding (planned)
- 🚧 Plugin system (planned)

## 💬 Support

- **Issues**: [GitHub Issues](https://github.com/chaoliu-cl/voxscribe/issues)
- **Discussions**: [GitHub Discussions](https://github.com/chaoliu-cl/voxscribe/discussions)
- **Email**: chaoliu@cedarville.edu

---

**Made with ❤️ for researchers and analysts**

*VoxScribe - Transforming audio into insights*