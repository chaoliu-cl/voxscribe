# Contributing to VoxScribe

First off, thank you for considering contributing to VoxScribe! It's people like you that make VoxScribe such a great tool for audio transcription and qualitative analysis.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [License](#license)

---

## 🤝 Code of Conduct

This project and everyone participating in it is governed by our commitment to fostering an open and welcoming environment. By participating, you are expected to uphold this standard. Please be respectful, considerate, and constructive in all interactions.

**Expected Behavior:**
- Be respectful and inclusive
- Welcome newcomers and help them get started
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards other community members

**Unacceptable Behavior:**
- Harassment, discrimination, or offensive comments
- Trolling, insulting/derogatory comments, and personal attacks
- Public or private harassment
- Publishing others' private information without permission

---

## 🎯 How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the [existing issues](https://github.com/chaoliu-cl/voxscribe/issues) to avoid duplicates.

**When reporting bugs, include:**
- VoxScribe version
- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Screenshots (if applicable)
- Error messages/logs

**Use this template:**
```markdown
**VoxScribe Version**: 1.0.0
**Python Version**: 3.9.7
**OS**: Windows 11 / macOS 13 / Ubuntu 22.04
**GPU**: NVIDIA RTX 3060 / CPU only

**Steps to Reproduce:**
1. Launch VoxScribe
2. Load audio file
3. Click transcribe
4. See error

**Expected Behavior:**
Transcription should complete successfully.

**Actual Behavior:**
Error: [paste error message]

**Additional Context:**
[Any other relevant information]
```

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When suggesting enhancements:

- Use a clear and descriptive title
- Provide detailed description of the proposed functionality
- Explain why this enhancement would be useful
- List any alternative solutions you've considered
- Include mockups or examples if applicable

### Contributing Code

We love pull requests! Here's how to contribute:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Make** your changes
4. **Test** your changes thoroughly
5. **Commit** with clear messages: `git commit -m 'Add amazing feature'`
6. **Push** to your fork: `git push origin feature/amazing-feature`
7. **Open** a Pull Request

### Contributing Documentation

Documentation improvements are always welcome:
- Fix typos or unclear explanations
- Add examples or tutorials
- Improve API documentation
- Translate documentation (future goal)

---

## 🛠️ Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- Virtual environment tool (venv, conda, etc.)
- (Optional) NVIDIA GPU with CUDA for acceleration

### Setup Steps

```bash
# Clone your fork
git clone https://github.com/YOUR-USERNAME/voxscribe.git
cd voxscribe

# Add upstream remote
git remote add upstream https://github.com/chaoliu-cl/voxscribe.git

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -e .

# Install optional development tools
pip install pytest pytest-cov black flake8 mypy
```

### Verify Setup

```bash
# Run tests (once implemented)
pytest

# Check code style
black --check voxscribe/
flake8 voxscribe/

# Type checking
mypy voxscribe/

# Run the application
python -m voxscribe.gui
```

---

## 🔄 Pull Request Process

### Before Submitting

- [ ] Code follows project style guidelines
- [ ] All tests pass
- [ ] New tests added for new features
- [ ] Documentation updated (if needed)
- [ ] Commit messages are clear and descriptive
- [ ] Branch is up to date with main

### PR Title Format

Use conventional commits format:

```
feat: Add batch export to CSV
fix: Resolve GPU memory leak in transcription
docs: Update installation instructions
refactor: Simplify annotation manager
test: Add tests for theme hierarchy
chore: Update dependencies
style: Format code with Black
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `perf`: Performance improvements

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change fixing an issue)
- [ ] New feature (non-breaking change adding functionality)
- [ ] Breaking change (fix or feature causing existing functionality to break)
- [ ] Documentation update
- [ ] Code style/refactoring
- [ ] Performance improvement

## Testing
Describe the tests you ran and how to reproduce

**Test Configuration:**
- OS: [e.g., Ubuntu 22.04]
- Python: [e.g., 3.9.7]
- GPU: [e.g., NVIDIA RTX 3060 or CPU only]

## Screenshots (if applicable)
Add screenshots for UI changes

## Checklist
- [ ] My code follows the project's style guidelines
- [ ] I have performed a self-review of my code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] I have updated the CHANGELOG.md (if applicable)

## Related Issues
Fixes #[issue number]
Closes #[issue number]
Related to #[issue number]
```

### Review Process

1. **Automated Checks**: CI/CD will run automatically
2. **Code Review**: Maintainer will review within 3-5 business days
3. **Revisions**: Address any requested changes
4. **Approval**: Once approved, maintainer will merge

---

## 💻 Coding Standards

### Python Style

We follow [PEP 8](https://pep8.org/) with some modifications:

- **Line length**: 100 characters (not strict 79)
- **Use Black** for formatting (configured for 100 chars)
- **Type hints**: Required for all public functions
- **Docstrings**: Required for all public functions, classes, and modules

**Example:**

```python
from typing import List, Dict, Optional

def transcribe_audio(
    audio_path: str, 
    model_size: str = "base",
    language: Optional[str] = None
) -> List[Dict[str, any]]:
    """
    Transcribe audio file using Whisper model.
    
    Args:
        audio_path: Path to audio file
        model_size: Model size (tiny, base, small, medium, large)
        language: Language code (e.g., 'en', 'es') or None for auto-detect
        
    Returns:
        List of transcription segments with text and timestamps
        
    Raises:
        FileNotFoundError: If audio file doesn't exist
        ValueError: If model_size is invalid
        
    Example:
        >>> results = transcribe_audio("interview.mp3", model_size="base")
        >>> print(results[0]['text'])
        'Hello, this is a test.'
    """
    # Implementation here
    pass
```

### Code Formatting

We use **Black** for code formatting:

```bash
# Format all files
black voxscribe/

# Check formatting without changing files
black --check voxscribe/

# Format specific file
black voxscribe/transcriber.py
```

**Black Configuration** (pyproject.toml):
```toml
[tool.black]
line-length = 100
target-version = ['py38', 'py39', 'py310']
```

### Import Organization

Organize imports in three groups separated by blank lines:

```python
# 1. Standard library imports
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple

# 2. Third-party imports
import numpy as np
import torch
from PySide6.QtWidgets import QMainWindow, QWidget
from faster_whisper import WhisperModel

# 3. Local application imports
from .transcriber import AudioTranscriber
from .annotator import TextAnnotator
from .utils import format_time, validate_audio_file
```

### Type Hints

Use type hints for all function signatures:

```python
from typing import List, Dict, Optional, Tuple, Union, Any

# Good
def process_segments(
    segments: List[Dict[str, Any]],
    filter_empty: bool = True,
    threshold: float = 0.5
) -> Tuple[List[Dict[str, Any]], int]:
    """Process transcription segments."""
    pass

# Bad - no type hints
def process_segments(segments, filter_empty=True, threshold=0.5):
    pass
```

### Docstrings

Use **Google-style** docstrings:

```python
def merge_segments(
    segments: List[Dict[str, Any]], 
    threshold: float = 1.0
) -> List[Dict[str, Any]]:
    """
    Merge consecutive segments based on time threshold.
    
    Segments are merged if the gap between them is less than the specified
    threshold. This is useful for creating more natural transcription chunks.
    
    Args:
        segments: List of transcription segments with 'start' and 'end' times.
            Each segment must have keys: 'start', 'end', 'text'.
        threshold: Maximum gap in seconds between segments to merge.
            Default is 1.0 seconds.
        
    Returns:
        List of merged segments with the same structure as input.
        
    Raises:
        ValueError: If segments don't have required 'start' and 'end' keys.
        TypeError: If threshold is not a number.
        
    Example:
        >>> segments = [
        ...     {'start': 0.0, 'end': 1.0, 'text': 'Hello'},
        ...     {'start': 1.2, 'end': 2.0, 'text': 'world'}
        ... ]
        >>> merged = merge_segments(segments, threshold=0.5)
        >>> len(merged)
        1
        >>> merged[0]['text']
        'Hello world'
        
    Note:
        The merged segment's start time will be from the first segment,
        and end time from the last segment in the merge group.
    """
    pass
```

### Code Comments

```python
# Good: Explains WHY, not WHAT
# Use VAD filter to reduce processing time by skipping silence regions
# This can reduce transcription time by 30-50% for audio with pauses
vad_filter = True

# Bad: States the obvious
# Set vad_filter to True
vad_filter = True

# Good: Complex logic explanation
# Convert display positions to original text positions by accounting
# for inserted code labels. Each label adds len("[CODE]") characters,
# so we need to subtract these offsets to get the original position.
original_pos = display_pos - sum(len(f"[{code}]") for code in codes_before_pos)

# Good: Warning about edge case
# FIXME: This fails when segments overlap. Need to sort and deduplicate
# before processing. See issue #123.
merged = merge_segments(segments)
```

---

## 🧪 Testing Guidelines

### Writing Tests

We use **pytest** for testing:

```python
# tests/test_transcriber.py
import pytest
from pathlib import Path
from voxscribe import AudioTranscriber

def test_transcriber_initialization():
    """Test that transcriber initializes with correct defaults."""
    transcriber = AudioTranscriber(model_size="base")
    
    assert transcriber.model_size == "base"
    assert transcriber.device in ["cuda", "cpu"]
    assert transcriber.model is None  # Model not loaded yet

def test_transcriber_device_detection():
    """Test automatic device detection."""
    transcriber = AudioTranscriber(device="auto")
    
    # Should detect CUDA or fall back to CPU
    assert transcriber.device in ["cuda", "cpu"]

def test_transcriber_with_invalid_model():
    """Test that invalid model size raises appropriate error."""
    with pytest.raises(ValueError, match="Invalid model size"):
        transcriber = AudioTranscriber(model_size="invalid")

@pytest.mark.skipif(not torch.cuda.is_available(), reason="Requires GPU")
def test_transcriber_gpu():
    """Test GPU-specific functionality."""
    transcriber = AudioTranscriber(device="cuda")
    assert transcriber.device == "cuda"

def test_transcribe_file(tmp_path):
    """Test transcription of a sample audio file."""
    # Create a temporary audio file for testing
    audio_file = tmp_path / "test.wav"
    # ... create test audio file ...
    
    transcriber = AudioTranscriber(model_size="tiny")  # Use smallest model for testing
    transcriber.load_model()
    
    results = transcriber.transcribe(str(audio_file))
    
    assert len(results) > 0
    assert 'text' in results[0]
    assert 'id' in results[0]
```

### Test Organization

```
tests/
├── __init__.py
├── test_transcriber.py       # Test transcription functionality
├── test_annotator.py         # Test annotation management
├── test_utils.py             # Test utility functions
├── test_gui.py               # Test GUI components (if applicable)
├── fixtures/                 # Test data and fixtures
│   ├── sample_audio.wav
│   └── sample_transcript.json
└── conftest.py               # Shared fixtures and configuration
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=voxscribe --cov-report=html

# Run specific test file
pytest tests/test_transcriber.py

# Run specific test
pytest tests/test_transcriber.py::test_transcriber_initialization

# Run with verbose output
pytest -v

# Run only tests marked as 'fast'
pytest -m fast

# Run and stop at first failure
pytest -x
```

### Test Coverage

Aim for **80%+ code coverage** for new code:

```bash
# Generate coverage report
pytest --cov=voxscribe --cov-report=term-missing

# Generate HTML coverage report
pytest --cov=voxscribe --cov-report=html
# Open htmlcov/index.html in browser
```

---

## 📚 Documentation

### Code Documentation

**All public APIs must have docstrings:**

```python
class AudioTranscriber:
    """
    Handles audio transcription using faster-whisper with optimizations.
    
    This class provides a high-level interface for transcribing audio files
    using OpenAI's Whisper model via the faster-whisper implementation.
    It supports GPU acceleration, multiple model sizes, and batch processing.
    
    Attributes:
        model_size: Size of the Whisper model (tiny, base, small, medium, large)
        device: Device to run on ('cuda' or 'cpu')
        compute_type: Computation precision ('float16', 'int8', etc.)
        model: The loaded Whisper model instance (None until load_model() called)
    
    Example:
        >>> transcriber = AudioTranscriber(model_size="base")
        >>> transcriber.load_model()
        >>> results = transcriber.transcribe("interview.mp3")
        >>> print(results[0]['text'])
    
    Note:
        GPU acceleration requires CUDA-capable device and appropriate PyTorch
        installation. The model will automatically be downloaded on first use.
    """
    pass
```

### README Updates

When adding features, update README.md:

- Add to feature list if it's user-facing
- Update usage examples if API changed
- Add to troubleshooting if it solves common issues
- Update requirements if dependencies changed

### Changelog

Update CHANGELOG.md for significant changes:

```markdown
## [Unreleased]

### Added
- Batch export to CSV format (#42)
- Support for WebM audio files (#45)

### Changed
- Improved memory efficiency in batch processing (#43)
- Updated faster-whisper to version 1.2.0

### Fixed
- GPU memory leak in long transcriptions (#44)
- Theme hierarchy not saving correctly (#46)

### Deprecated
- Old export format (will be removed in 2.0.0)
```

---

## 🎨 Git Commit Guidelines

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Example:**
```
feat(transcription): Add support for WebM audio format

- Implement WebM decoder using pydub
- Add WebM to supported formats list  
- Update documentation with WebM examples

Closes #123
```

### Commit Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style (formatting, missing semicolons, etc.)
- `refactor`: Code refactoring
- `perf`: Performance improvement
- `test`: Adding tests
- `chore`: Maintenance (dependencies, build, etc.)

### Good Commit Messages

```bash
# Good
git commit -m "fix(gui): Resolve memory leak in batch processing

The batch processor was not properly releasing audio buffers after
transcription, causing memory usage to grow unbounded during long
batch operations.

Fixes #456"

# Good
git commit -m "feat(export): Add CSV export with custom delimiter support"

# Good  
git commit -m "docs(readme): Add troubleshooting section for GPU issues"

# Bad
git commit -m "fixed stuff"
git commit -m "update"
git commit -m "changes"
```

---

## 📬 Communication

- **Issues**: [GitHub Issues](https://github.com/chaoliu-cl/voxscribe/issues)
- **Discussions**: [GitHub Discussions](https://github.com/chaoliu-cl/voxscribe/discussions)
- **Email**: chaoliu@cedarville.edu (for private matters or questions)

### Getting Help

- Check the [README.md](README.md) first
- Search [existing issues](https://github.com/chaoliu-cl/voxscribe/issues)
- Ask in [GitHub Discussions](https://github.com/chaoliu-cl/voxscribe/discussions)
- Contact the maintainer if needed

---

## 🏆 Recognition

All contributors will be:
- Listed in the project README
- Credited in release notes
- Mentioned in commit history
- Appreciated by the community!

---

## 📄 License

By contributing to VoxScribe, you agree that your contributions will be licensed under the **Apache License 2.0**, the same license as the rest of the project.

This means:
- Your contributions become part of the project
- They can be used, modified, and distributed under Apache 2.0 terms
- You retain copyright to your contributions
- You grant the project and users rights under Apache 2.0

**Key Points:**
- ✅ You keep your copyright
- ✅ You grant the project rights to use your code
- ✅ Your code will be licensed under Apache 2.0
- ✅ Patent rights are granted (see Apache 2.0 license)
- ✅ You warrant you have the right to contribute the code

**If contributing on behalf of your employer:**
Make sure you have permission from your employer to contribute, as they may own the intellectual property rights to your work.

---

## 🚀 First Time Contributors

Welcome! We're excited to have you. Here are some tips:

### Good First Issues

Look for issues labeled:
- `good first issue` - Good for newcomers
- `help wanted` - Extra attention needed
- `documentation` - Documentation improvements
- `bug` - Bug fixes (start with simple ones)

### Getting Started

1. **Read this guide** - You're already doing great!
2. **Set up development environment** - Follow instructions above
3. **Find an issue** - Or suggest an enhancement
4. **Ask questions** - Don't hesitate to ask for help
5. **Start small** - Even typo fixes are valuable
6. **Be patient** - Reviews may take a few days

### Resources for New Contributors

- [How to Contribute to Open Source](https://opensource.guide/how-to-contribute/)
- [First Contributions](https://github.com/firstcontributions/first-contributions)
- [GitHub Flow](https://guides.github.com/introduction/flow/)

---

## ❓ FAQ

**Q: I'm new to open source. Can I still contribute?**
A: Absolutely! Everyone starts somewhere. Look for "good first issue" labels.

**Q: Do I need to sign anything before contributing?**
A: No formal agreement required. By submitting a PR, you agree your code will be licensed under Apache 2.0.

**Q: How long does code review take?**
A: Usually 3-5 business days. Be patient, maintainers are volunteers!

**Q: My PR was rejected. What should I do?**
A: Don't worry! Ask for feedback, learn from it, and try again. Rejection is part of the process.

**Q: Can I work on an issue that's already assigned?**
A: Best to ask first. The assignee might be actively working on it.

**Q: I found a security vulnerability. Where do I report it?**
A: Email chaoliu@cedarville.edu directly. Don't open a public issue.

---

**Thank you for contributing to VoxScribe!** 🎉

Your work makes audio transcription and qualitative analysis better for researchers, journalists, and analysts everywhere. Every contribution, no matter how small, is valuable and appreciated.

*Happy coding!* 💻✨