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
        "License :: OSI Approved :: Apache Software License",  
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "faster-whisper>=1.2.0",
        "PySide6>=6.5.0",
        "torch>=2.0.0",
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "matplotlib>=3.7.0",
        "networkx>=3.0",
        "pydub>=0.25.0",
        "soundfile>=0.12.0",
    ],
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