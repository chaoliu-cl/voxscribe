from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="voxscribe",
    version="1.0.0",
    author="Chao Liu",
    author_email="chaoliu@cedarville.edu",
    description="Audio Transcription & Qualitative Analysis Tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/chaoliu-cl/voxscribe",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11,<3.15",
    install_requires=[
        "faster-whisper>=1.2.1",
        "PySide6>=6.11.0",
        "torch>=2.11.0",
        "numpy>=2.4.3",
        "pandas>=3.0.1",
        "matplotlib>=3.10.8,<4.0.0",
        "networkx>=3.6.1",
        "soundfile>=0.13.1",
    ],
    extras_require={
        "audio-conversion": ["pydub>=0.25.1"],
        "build": ["pyinstaller>=6.19.0"],
    },
    entry_points={
        'console_scripts': [
            'voxscribe=voxscribe.gui:main',
        ],
    },
    # Include small configuration and data files but exclude large assets
    package_data={
        'voxscribe': ['*.json', '*.yml', '*.yaml', '*.txt', '*.md'],
    },
    data_files=[
        ('', ['LICENSE', 'NOTICE']),
    ],
    # Exclude large files from packaging
    exclude_package_data={
        '': ['*.wav', '*.mp3', '*.m4a', '*.flac', '*.ogg', '*.opus', 
             '*.pt', '*.pth', '*.bin', '*.onnx', '*.model'],
    },
    # Add additional metadata about the package
    project_urls={
        "Bug Tracker": "https://github.com/chaoliu-cl/voxscribe/issues",
        "Documentation": "https://github.com/chaoliu-cl/voxscribe/wiki",
        "Source Code": "https://github.com/chaoliu-cl/voxscribe",
    },
)
