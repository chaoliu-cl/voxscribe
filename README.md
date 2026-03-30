# VoxScribe

VoxScribe is a desktop application for audio transcription, qualitative coding, and transcript analysis. It combines `faster-whisper` transcription with a PySide6 interface for coding, theme development, comparison, and export.

![Python Version](https://img.shields.io/badge/python-3.11--3.14-blue)
![License](https://img.shields.io/badge/license-Apache%202.0-blue)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

## Highlights

- Transcribe audio with Whisper models from `tiny` through `large`
- Use GPU acceleration automatically when CUDA is available
- Code transcript passages with colors, memos, and reusable codebooks
- Organize codes into hierarchical themes with drag-and-drop
- Analyze code frequency, co-occurrence, text statistics, and document differences
- Export results as HTML, CSV, JSON, TXT, SRT, or VTT

## Installation

For most users, install VoxScribe from the packaged release instead of setting up Python manually.

1. Open the [Releases](https://github.com/chaoliu-cl/voxscribe/releases) page.
2. Download the installer for your platform.
3. Run the installer and complete the setup wizard.

Release artifacts:

- Windows: `VoxScribe-Setup.exe`
- macOS: `VoxScribe-macOS-universal.pkg` when provided for a release
- Linux: run from source

Notes:

- The first launch may download the selected Whisper model.
- An NVIDIA GPU is optional but can significantly speed up transcription.

## Quick Start

After installation, launch VoxScribe from your Start menu or Applications folder.

Typical workflow:

1. Import one or more audio files.
2. Choose a model size and language, then start transcription.
3. Review the transcript and apply codes to relevant text spans.
4. Group codes into themes.
5. Use the analysis views to inspect frequency, co-occurrence, and comparisons.
6. Export transcripts, coded data, or reports in the format you need.

## Requirements

- Windows, macOS, or Linux
- Python 3.11 to 3.14 for source-based installs
- 4 GB RAM minimum; 8 GB or more recommended for larger files
- Optional NVIDIA GPU for faster transcription

## Development Setup

If you want to run or modify VoxScribe from source:

```bash
git clone https://github.com/chaoliu-cl/voxscribe.git
cd voxscribe
python -m venv venv
```

Activate the environment:

```bash
# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

Install dependencies and start the app:

```bash
pip install -r requirements.txt
python -m voxscribe.gui
```

## Building Installers

Packaging scripts are included in [`voxscribe/README_BUILD.txt`](./voxscribe/README_BUILD.txt).

- Windows installer: `voxscribe/build_exe.ps1` then `voxscribe/build_installer.ps1`
- Windows MSIX: `voxscribe/build_msix.ps1`
- macOS universal installer: `voxscribe/build_macos_universal.sh`

## Troubleshooting

- Model download problems: verify internet access on first launch or set a writable cache location.
- GPU not detected: confirm that PyTorch can see your CUDA installation.
- Slow transcription: use a smaller model or CPU/GPU settings that match your hardware.

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](./CONTRIBUTING.md) for workflow and project guidance.

## License

VoxScribe is licensed under the Apache License 2.0.

## Citation

```bibtex
@software{voxscribe2025,
  author = {Liu, Chao},
  title = {VoxScribe: Audio Transcription and Qualitative Analysis Tool},
  year = {2025},
  url = {https://github.com/chaoliu-cl/voxscribe}
}
```
