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
VoxScribe GUI
"""

import sys
import os

# Add current directory to path if needed
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

import json
import re
from typing import Optional, List, Dict, Any
from datetime import datetime
from collections import Counter, defaultdict
import csv
from pathlib import Path

# Import Qt modules first (these should always work)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit, QLineEdit, QComboBox, QCheckBox,
    QProgressBar, QTabWidget, QFrame, QTableWidget, QTableWidgetItem,
    QFileDialog, QMessageBox, QSplitter, QGridLayout, QHeaderView,
    QGroupBox, QDialog, QStyle, QListWidget, QListWidgetItem,
    QInputDialog, QTreeWidget, QTreeWidgetItem, QScrollArea, QRadioButton
)
from PySide6.QtCore import Qt, Signal, QThread, QSize, QEvent, QTimer, QMutex, QMimeData
from PySide6.QtGui import QFont, QColor, QPalette, QTextCursor, QTextCharFormat, QDrag

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import networkx as nx

# Now try to import local modules with better error reporting
USING_DUMMY_CLASSES = False
import_errors = []

print("=" * 70)
print("VOXSCRIBE IMPORT STATUS")
print("=" * 70)

# Try to import transcriber
try:
    print("Attempting to import transcriber module...")
    from transcriber import AudioTranscriber
    print("✓ Successfully imported AudioTranscriber from transcriber.py")
except ImportError as e:
    import_errors.append(f"transcriber: {e}")
    print(f"✗ Failed to import transcriber: {e}")
    USING_DUMMY_CLASSES = True

# Try to import annotator
try:
    print("Attempting to import annotator module...")
    from annotator import TextAnnotator
    print("✓ Successfully imported TextAnnotator from annotator.py")
except ImportError as e:
    import_errors.append(f"annotator: {e}")
    print(f"✗ Failed to import annotator: {e}")
    USING_DUMMY_CLASSES = True

# Try to import utils
try:
    print("Attempting to import utils module...")
    from utils import validate_audio_file, format_time, get_audio_duration
    print("✓ Successfully imported utils functions from utils.py")
except ImportError as e:
    import_errors.append(f"utils: {e}")
    print(f"✗ Failed to import utils: {e}")
    USING_DUMMY_CLASSES = True

# If imports failed, define dummy classes
if USING_DUMMY_CLASSES:
    print("\n⚠️  Using dummy classes - some imports failed")
    print(f"Current directory: {os.getcwd()}")
    print(f"Script location: {current_dir}")
    print("\nImport errors:")
    for error in import_errors:
        print(f"  - {error}")
    
    # Check if faster-whisper is installed
    print("\nChecking faster-whisper installation:")
    try:
        import faster_whisper
        print(f"✓ faster-whisper IS installed (version: {getattr(faster_whisper, '__version__', 'unknown')})")
        print("  → Problem is likely with local module files (transcriber.py, etc.)")
    except ImportError:
        print("✗ faster-whisper is NOT installed")
        print("  → Install with: pip install faster-whisper")
    
    print("\n" + "=" * 70)
    
    # Define dummy classes ONLY if needed
    if 'AudioTranscriber' not in dir():
        class AudioTranscriber:
            def __init__(self, device="auto", compute_type="auto", model_size="base"):
                self.device = device
                self.compute_type = compute_type
                self.model = None
                self.model_size = model_size
            
            def get_device_info(self):
                return {"device": self.device, "compute_type": self.compute_type}
            
            def load_model(self):
                pass
            
            def change_model(self, size, device=None, compute_type=None):
                self.model_size = size
                if device:
                    self.device = device
                if compute_type:
                    self.compute_type = compute_type
            
            def transcribe(self, audio_path, language=None, beam_size=5, 
                          vad_filter=True, include_timestamps=True, 
                          word_timestamps=False, progress_callback=None):
                """Dummy transcribe - Updated signature with time tracking"""
                import time
                
                total_duration = 1.0  # Dummy 1 second audio
                start_time = time.time()
                
                if progress_callback:
                    # Progress at 0% processed
                    elapsed = time.time() - start_time
                    progress_callback(0, 0.0, total_duration, elapsed)
                
                time.sleep(0.3)
                
                if progress_callback:
                    # Progress at 50% processed
                    elapsed = time.time() - start_time
                    progress_callback(1, 0.5, total_duration, elapsed)
                    
                    time.sleep(0.2)
                    
                    # Progress at 100% processed
                    elapsed = time.time() - start_time
                    progress_callback(2, 1.0, total_duration, elapsed)
                
                return [
                    {
                        'text': f'[DUMMY] Transcription for {os.path.basename(audio_path)}',
                        'id': 0,
                        'start': 0.0 if include_timestamps else None,
                        'end': 0.5 if include_timestamps else None
                    },
                    {
                        'text': '[DUMMY] Install faster-whisper and ensure transcriber.py is in the same directory.',
                        'id': 1,
                        'start': 0.5 if include_timestamps else None,
                        'end': 1.0 if include_timestamps else None
                    }
                ]
            
            def transcribe_batch(self, audio_paths, language=None, beam_size=5,
                               vad_filter=True, include_timestamps=True,
                               word_timestamps=False, batch_progress_callback=None,
                               **kwargs):
                """Dummy batch transcribe"""
                import time
                results = []
                
                for i, path in enumerate(audio_paths):
                    time.sleep(0.3)
                    result_data = self.transcribe(path, language, beam_size, vad_filter, 
                                                  include_timestamps, word_timestamps)
                    results.append({
                        'path': path,
                        'filename': os.path.basename(path),
                        'success': True,
                        'results': result_data,
                        'segments_count': len(result_data),
                        'processing_time': 0.3,
                        'error': None
                    })
                    if batch_progress_callback:
                        batch_progress_callback(i + 1, len(audio_paths), os.path.basename(path))
                
                return results
    
    if 'TextAnnotator' not in dir():
        class TextAnnotator:
            def __init__(self):
                self.segments = []
                self.annotations = {}
                self.history = []
            
            def load_segments(self, segments):
                self.segments = segments
    
    if 'validate_audio_file' not in dir():
        def validate_audio_file(path):
            return (True, "Valid (dummy validation)")
    
    if 'format_time' not in dir():
        def format_time(seconds):
            if seconds is None:
                return "00:00"
            mins = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{mins:02d}:{secs:02d}"
    
    if 'get_audio_duration' not in dir():
        def get_audio_duration(path):
            return 60.0

else:
    print("\n✓ All modules imported successfully!")
    print("=" * 70 + "\n")


class CodeMemo:
    """Represents a code annotation with memo"""
    def __init__(self):
        self.start = 0
        self.end = 0
        self.text = ""
        self.code = ""
        self.memo = ""


class CodeSelectionDialog(QDialog):
    """Dialog for selecting a code to apply"""
    def __init__(self, codes, parent=None):
        super().__init__(parent)
        self.selected_code = None
        self.setWindowTitle("Apply Code to Selection")
        self.setModal(True)
        self.setMinimumWidth(450)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        title = QLabel("<h3>Apply Code to Selected Text</h3>")
        layout.addWidget(title)
        
        instructions = QLabel("Select a code to apply to the selected text:")
        layout.addWidget(instructions)
        
        code_frame = QFrame()
        code_frame.setFrameShape(QFrame.Shape.StyledPanel)
        code_frame.setStyleSheet("QFrame { background-color: #f5f5f5; padding: 10px; border-radius: 5px; }")
        code_frame_layout = QHBoxLayout(code_frame)
        code_frame_layout.addWidget(QLabel("<b>Code:</b>"))
        self.code_combo = QComboBox()
        self.code_combo.addItems(sorted(codes))
        self.code_combo.setMinimumHeight(30)
        code_frame_layout.addWidget(self.code_combo)
        layout.addWidget(code_frame)
        
        layout.addWidget(QLabel("<b>Memo (optional):</b>"))
        self.memo_input = QTextEdit()
        self.memo_input.setMaximumHeight(100)
        self.memo_input.setPlaceholderText("Enter optional memo about this annotation...")
        layout.addWidget(self.memo_input)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        ok_btn = QPushButton("Apply Code")
        ok_btn.setMinimumWidth(120)
        ok_btn.setMinimumHeight(35)
        ok_btn.setStyleSheet("QPushButton { font-weight: bold; }")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumWidth(100)
        cancel_btn.setMinimumHeight(35)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
    
    def get_code_and_memo(self):
        return self.code_combo.currentText(), self.memo_input.toPlainText().strip()


class RemoveAnnotationDialog(QDialog):
    """Dialog for removing an annotation"""
    def __init__(self, annotation, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Remove Annotation")
        self.setModal(True)
        self.setMinimumWidth(450)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        title = QLabel("<h3>Remove Annotation</h3>")
        layout.addWidget(title)
        
        details_frame = QFrame()
        details_frame.setFrameShape(QFrame.Shape.StyledPanel)
        details_frame.setStyleSheet("QFrame { background-color: #f5f5f5; padding: 10px; border-radius: 5px; }")
        details_layout = QVBoxLayout(details_frame)
        
        info_label = QLabel(f"<b>Code:</b> {annotation.code}<br><br>"
                          f"<b>Text:</b> {annotation.text[:150]}{'...' if len(annotation.text) > 150 else ''}<br><br>"
                          f"<b>Memo:</b> {annotation.memo if annotation.memo else '(no memo)'}")
        info_label.setWordWrap(True)
        details_layout.addWidget(info_label)
        
        layout.addWidget(details_frame)
        
        question = QLabel("<p>Do you want to remove this annotation?</p>")
        layout.addWidget(question)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        remove_btn = QPushButton("Remove Annotation")
        remove_btn.setMinimumWidth(150)
        remove_btn.setMinimumHeight(35)
        remove_btn.setStyleSheet("QPushButton { background-color: #d32f2f; color: white; font-weight: bold; }")
        remove_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumWidth(100)
        cancel_btn.setMinimumHeight(35)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(remove_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)


class MergeCodesDialog(QDialog):
    """Dialog for merging multiple codes"""
    def __init__(self, codes, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Merge Codes")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setMinimumHeight(450)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        instructions = QLabel("<h3>Merge Codes</h3><p>Select two or more codes to merge into a new code:</p>")
        layout.addWidget(instructions)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(250)
        checkbox_widget = QWidget()
        checkbox_layout = QVBoxLayout(checkbox_widget)
        checkbox_layout.setSpacing(8)
        checkbox_layout.setContentsMargins(10, 10, 10, 10)
        
        self.checkboxes = {}
        for code in sorted(codes):
            cb = QCheckBox(code)
            cb.setStyleSheet("QCheckBox { padding: 5px; font-size: 11pt; }")
            self.checkboxes[code] = cb
            checkbox_layout.addWidget(cb)
        
        checkbox_layout.addStretch()
        scroll.setWidget(checkbox_widget)
        layout.addWidget(scroll)
        
        new_code_label = QLabel("<b>Enter new merged code name:</b>")
        layout.addWidget(new_code_label)
        self.new_code_input = QLineEdit()
        self.new_code_input.setPlaceholderText("Enter name for merged code...")
        self.new_code_input.setMinimumHeight(30)
        layout.addWidget(self.new_code_input)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        merge_btn = QPushButton("Merge Selected Codes")
        merge_btn.setMinimumWidth(150)
        merge_btn.setMinimumHeight(35)
        merge_btn.setStyleSheet("QPushButton { font-weight: bold; }")
        merge_btn.clicked.connect(self.validate_and_accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumWidth(100)
        cancel_btn.setMinimumHeight(35)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(merge_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
    
    def validate_and_accept(self):
        selected = self.get_selected_codes()
        new_code = self.new_code_input.text().strip()
        
        if len(selected) < 2:
            QMessageBox.warning(self, "Warning", "Please select at least 2 codes to merge")
            return
        
        if not new_code:
            QMessageBox.warning(self, "Warning", "Please enter a new code name")
            return
        
        self.accept()
    
    def get_selected_codes(self):
        return [code for code, cb in self.checkboxes.items() if cb.isChecked()]
    
    def get_new_code_name(self):
        return self.new_code_input.text().strip()


class ThemeNode:
    """Represents a node in the theme hierarchy"""
    def __init__(self, name, node_type="theme", description="", parent=None):
        self.name = name
        self.type = node_type
        self.description = description
        self.parent = parent
        self.children = []
        self.created = datetime.now()
    
    def add_child(self, child):
        child.parent = self
        self.children.append(child)
        return child
    
    def remove_child(self, child):
        if child in self.children:
            self.children.remove(child)
            child.parent = None
    
    def to_dict(self):
        return {
            'name': self.name,
            'type': self.type,
            'description': self.description,
            'created': self.created.isoformat(),
            'children': [child.to_dict() for child in self.children]
        }
    
    @staticmethod
    def from_dict(data, parent=None):
        node = ThemeNode(
            data['name'],
            data.get('type', 'theme'),
            data.get('description', ''),
            parent
        )
        if 'created' in data:
            node.created = datetime.fromisoformat(data['created'])
        for child_data in data.get('children', []):
            child = ThemeNode.from_dict(child_data, node)
            node.children.append(child)
        return node


class AnnotationManager:
    """Manages text annotations and codes"""
    def __init__(self):
        self.annotations = []
        self.codes = set()
        self.code_colors = {}
        self.theme_root = ThemeNode("Root", "theme", "Root of code hierarchy")
        self.color_palette = [
            '#FFE6CC', '#E6F3FF', '#E6FFE6', '#FFE6F3', '#F3E6FF', 
            '#FFF2E6', '#E6F7FF', '#F0FFE6', '#FFE6F0', '#F7E6FF',
            '#FFD9B3', '#CCE5FF', '#D9FFD9', '#FFD9EC', '#E6D9FF',
            '#FFE6D9', '#D9F0FF', '#E1FFD9', '#FFD9E6', '#F0D9FF'
        ]
        
    def add_annotation(self, start, end, text, code, memo):
        """
        Add annotation to manager
        IMPORTANT: Store the actual selected text from the original document
        
        Args:
            start: Start position in ORIGINAL text (not display text)
            end: End position in ORIGINAL text (not display text)
            text: The actual text from original document (this should be self.current_text[start:end])
            code: The code name
            memo: Optional memo
            
        Returns:
            The created annotation object
        """
        annotation = CodeMemo()
        annotation.start = start
        annotation.end = end
        annotation.text = text  # This MUST be the actual text from original document
        annotation.code = code
        annotation.memo = memo
        self.annotations.append(annotation)
        self.codes.add(code)
        
        if code not in self.code_colors:
            self.code_colors[code] = self.color_palette[len(self.code_colors) % len(self.color_palette)]
            
        return annotation
        
    def remove_annotation(self, annotation):
        self.annotations.remove(annotation)
        if not any(a.code == annotation.code for a in self.annotations):
            self.codes.discard(annotation.code)
            
    def get_annotations_for_code(self, code):
        return [a for a in self.annotations if a.code == code]
    
    def merge_codes(self, old_codes, new_code):
        for annotation in self.annotations:
            if annotation.code in old_codes:
                annotation.code = new_code
        
        for old_code in old_codes:
            self.codes.discard(old_code)
            if old_code in self.code_colors:
                del self.code_colors[old_code]
        
        self.codes.add(new_code)
        if new_code not in self.code_colors:
            self.code_colors[new_code] = self.color_palette[len(self.code_colors) % len(self.color_palette)]


class TranscriptionWorker(QThread):
    """Background worker for single file transcription - FIXED"""
    finished = Signal(list)
    error = Signal(str)
    progress = Signal(int, str)
    
    def __init__(self, transcriber, audio_path, model_size, language, include_timestamps):
        super().__init__()
        self.transcriber = transcriber
        self.audio_path = audio_path
        self.model_size = model_size
        self.language = language
        self.include_timestamps = include_timestamps
    
    def run(self):
        try:
            self.progress.emit(5, "Loading model...")
            
            # Always ensure model is loaded properly
            if self.transcriber.model is None or self.transcriber.model_size != self.model_size:
                self.transcriber.change_model(self.model_size)
            
            # Verify model is loaded
            if self.transcriber.model is None:
                self.transcriber.load_model()
            
            self.progress.emit(10, "Model loaded, starting transcription...")
            
            duration = get_audio_duration(self.audio_path)
            results = []
            
            # Define progress callback handler with enhanced time tracking
            def handle_progress(segment_count, processed_duration, total_duration, elapsed_time):
                """
                Handle progress updates from transcriber
                
                Args:
                    segment_count: Number of segments processed
                    processed_duration: Audio duration processed in seconds (or None)
                    total_duration: Total audio duration in seconds (or None)  
                    elapsed_time: Time elapsed since start in seconds
                """
                # Format elapsed time
                elapsed_str = format_time(elapsed_time)
                
                # Calculate estimated time remaining
                if processed_duration is not None and total_duration is not None and processed_duration > 0:
                    # Time-based progress (most accurate)
                    progress_pct = int(10 + (processed_duration / total_duration) * 85)
                    progress_pct = min(95, progress_pct)  # Cap at 95%
                    
                    # Estimate remaining time based on processing speed
                    processing_speed = elapsed_time / processed_duration
                    remaining_duration = total_duration - processed_duration
                    estimated_remaining = remaining_duration * processing_speed
                    remaining_str = format_time(estimated_remaining)
                    
                    # Format message with all information
                    processed_str = format_time(processed_duration)
                    total_str = format_time(total_duration)
                    
                    self.progress.emit(
                        progress_pct,
                        f"Transcribing... {processed_str} / {total_str} | "
                        f"Elapsed: {elapsed_str} | Est. remaining: {remaining_str}"
                    )
                else:
                    # Fallback to segment-based progress when timestamps unavailable
                    progress_pct = int(10 + min(85, segment_count * 2))
                    progress_pct = min(95, progress_pct)  # Cap at 95%
                    self.progress.emit(
                        progress_pct,
                        f"Transcribing... {segment_count} segments | Elapsed: {elapsed_str}"
                    )
            
            # Use the transcriber's transcribe method with enhanced callback
            result = self.transcriber.transcribe(
                self.audio_path,
                language=self.language if self.language != "auto" else None,
                include_timestamps=self.include_timestamps,
                progress_callback=handle_progress
            )
            
            self.progress.emit(100, f"Complete! {len(result)} segments transcribed")
            self.finished.emit(result)
            
        except Exception as e:
            import traceback
            error_details = f"{str(e)}\n\n{traceback.format_exc()}"
            self.error.emit(error_details)


class BatchTranscriptionWorker(QThread):
    """Background worker for batch transcription with pause/resume support"""
    finished = Signal(list)
    error = Signal(str)
    progress = Signal(int, str)
    file_progress = Signal(int, int, str)
    
    def __init__(self, transcriber, audio_paths, model_size, language, 
                 include_timestamps, output_dir, output_format, use_parallel=False):
        super().__init__()
        self.transcriber = transcriber
        self.audio_paths = audio_paths
        self.model_size = model_size
        self.language = language
        self.include_timestamps = include_timestamps
        self.output_dir = output_dir
        self.output_format = output_format
        self.use_parallel = use_parallel
        
        # Pause/resume control
        self._pause_mutex = QMutex()
        self._is_paused = False
        self._is_cancelled = False
        self._current_index = 0
        self.results = []
    
    def pause(self):
        """Pause the batch processing"""
        self._pause_mutex.lock()
        self._is_paused = True
        self._pause_mutex.unlock()
    
    def resume(self):
        """Resume the batch processing"""
        self._pause_mutex.lock()
        self._is_paused = False
        self._pause_mutex.unlock()
    
    def cancel(self):
        """Cancel the batch processing"""
        self._is_cancelled = True
        self.resume()  # Unpause if paused
    
    def is_paused(self):
        """Check if processing is paused"""
        self._pause_mutex.lock()
        paused = self._is_paused
        self._pause_mutex.unlock()
        return paused
    
    def run(self):
        try:
            self.progress.emit(5, "Loading model...")
            
            if self.transcriber.model_size != self.model_size:
                self.transcriber.change_model(self.model_size)
            elif self.transcriber.model is None:
                self.transcriber.load_model()
            
            self.progress.emit(10, "Model loaded, starting batch transcription...")
            
            total_files = len(self.audio_paths)
            
            for i in range(self._current_index, total_files):
                # Check for cancellation
                if self._is_cancelled:
                    self.error.emit("Batch processing cancelled by user")
                    return
                
                # Check for pause
                while self.is_paused():
                    self.msleep(100)  # Sleep for 100ms while paused
                    if self._is_cancelled:
                        self.error.emit("Batch processing cancelled by user")
                        return
                
                self._current_index = i
                audio_path = self.audio_paths[i]
                filename = Path(audio_path).name
                
                self.file_progress.emit(i + 1, total_files, filename)
                self.progress.emit(10 + int((i / total_files) * 80), 
                                 f"Processing {i+1}/{total_files}: {filename}")
                
                try:
                    import time
                    start_time = time.time()
                    
                    # Transcribe single file
                    result = self.transcriber.transcribe(
                        audio_path,
                        language=self.language if self.language != "auto" else None,
                        include_timestamps=self.include_timestamps
                    )
                    
                    elapsed = time.time() - start_time
                    
                    file_result = {
                        'path': audio_path,
                        'filename': filename,
                        'success': True,
                        'results': result,
                        'segments_count': len(result),
                        'processing_time': elapsed,
                        'error': None
                    }
                    
                    self.results.append(file_result)
                    
                    # Save if output directory specified
                    if self.output_dir:
                        self._save_single_result(file_result)
                    
                except Exception as e:
                    error_result = {
                        'path': audio_path,
                        'filename': filename,
                        'success': False,
                        'results': None,
                        'segments_count': 0,
                        'processing_time': 0,
                        'error': str(e)
                    }
                    self.results.append(error_result)
            
            self.progress.emit(100, f"Complete! {len(self.results)} files processed")
            self.finished.emit(self.results)
            
        except Exception as e:
            self.error.emit(str(e))
    
    def _save_single_result(self, result):
        """Save a single transcription result"""
        if not result['success']:
            return
        
        filename = Path(result['filename']).stem
        
        if self.output_format == 'txt':
            output_path = Path(self.output_dir) / f"{filename}_transcription.txt"
            with open(output_path, 'w', encoding='utf-8') as f:
                for segment in result['results']:
                    if self.include_timestamps and 'start' in segment:
                        f.write(f"[{self._format_time(segment['start'])} -> {self._format_time(segment['end'])}]\n")
                    f.write(f"{segment['text']}\n\n")
        
        elif self.output_format == 'json':
            output_path = Path(self.output_dir) / f"{filename}_transcription.json"
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result['results'], f, indent=2)
        
        elif self.output_format == 'srt':
            if self.include_timestamps:
                output_path = Path(self.output_dir) / f"{filename}_transcription.srt"
                with open(output_path, 'w', encoding='utf-8') as f:
                    for i, segment in enumerate(result['results'], 1):
                        if 'start' in segment and 'end' in segment:
                            start = self._format_srt_time(segment['start'])
                            end = self._format_srt_time(segment['end'])
                            f.write(f"{i}\n{start} --> {end}\n{segment['text']}\n\n")
        
        elif self.output_format == 'vtt':
            if self.include_timestamps:
                output_path = Path(self.output_dir) / f"{filename}_transcription.vtt"
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write("WEBVTT\n\n")
                    for i, segment in enumerate(result['results'], 1):
                        if 'start' in segment and 'end' in segment:
                            start = self._format_vtt_time(segment['start'])
                            end = self._format_vtt_time(segment['end'])
                            f.write(f"{start} --> {end}\n{segment['text']}\n\n")
    
    @staticmethod
    def _format_time(seconds):
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins:02d}:{secs:02d}"
    
    @staticmethod
    def _format_srt_time(seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    @staticmethod
    def _format_vtt_time(seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"


class VoxScribeGUI(QMainWindow):
    """VoxScribe - Audio Transcription & Qualitative Analysis"""
    
    def __init__(self):
        super().__init__()
        
        self.transcriber = AudioTranscriber(device="auto", compute_type="auto")
        self.annotator = TextAnnotator()
        self.annotation_manager = AnnotationManager()
        
        self.current_audio_path = None
        self.audio_paths = []
        self.current_text = ""
        self.worker = None
        self.selection_mode = False
        
        self.text_display_font_size = 12
        
        self.setWindowTitle("VoxScribe - Audio Transcription & Qualitative Analysis")
        self.setMinimumSize(1200, 800)
        
        app_font = QFont()
        app_font.setPointSize(11)
        QApplication.setFont(app_font)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        self.tabs = QTabWidget()
        tab_font = QFont()
        tab_font.setPointSize(11)
        tab_font.setBold(True)
        self.tabs.setFont(tab_font)
        layout.addWidget(self.tabs)
        
        self.tabs.addTab(self.create_transcription_tab(), "Transcription")
        self.tabs.addTab(self.create_code_tab(), "Code")
        self.tabs.addTab(self.create_codebook_tab(), "Codebook")
        self.tabs.addTab(self.create_themes_tab(), "Themes")
        self.tabs.addTab(self.create_analysis_tab(), "Analysis")
        self.tabs.addTab(self.create_records_tab(), "Records")
        self.tabs.addTab(self.create_comparison_tab(), "Comparison")
    
    def create_transcription_tab(self):
        """Create transcription tab with batch support and pause/resume"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # Processing Mode Selection
        mode_group = QGroupBox("Processing Mode")
        mode_layout = QHBoxLayout()
        
        self.single_mode_radio = QRadioButton("Single File")
        self.single_mode_radio.setChecked(True)
        self.single_mode_radio.toggled.connect(self.toggle_processing_mode)
        mode_layout.addWidget(self.single_mode_radio)
        
        self.batch_mode_radio = QRadioButton("Batch Processing")
        mode_layout.addWidget(self.batch_mode_radio)
        
        self.parallel_checkbox = QCheckBox("Use Parallel Processing (CPU only)")
        self.parallel_checkbox.setEnabled(False)
        self.parallel_checkbox.setToolTip("Process multiple files simultaneously. Use with caution on GPU.")
        mode_layout.addWidget(self.parallel_checkbox)
        
        mode_layout.addStretch()
        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)
        
        # File selection group
        file_group = QGroupBox("File Management")
        file_layout = QGridLayout()
        file_layout.setSpacing(10)
        
        file_layout.addWidget(QLabel("Input Audio:"), 0, 0)
        self.file_path = QLineEdit()
        self.file_path.setReadOnly(True)
        self.file_path.setPlaceholderText("Select an audio file...")
        file_layout.addWidget(self.file_path, 0, 1)
        
        self.browse_btn = QPushButton("Browse")
        self.browse_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogOpenButton))
        self.browse_btn.clicked.connect(self.browse_audio_file)
        file_layout.addWidget(self.browse_btn, 0, 2)
        
        # Batch file list (hidden by default)
        self.batch_file_list = QListWidget()
        self.batch_file_list.setMaximumHeight(150)
        self.batch_file_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)  # Allow multiple selection
        self.batch_file_list.hide()
        self.batch_file_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.batch_file_list.customContextMenuRequested.connect(self.show_batch_list_context_menu)
        file_layout.addWidget(self.batch_file_list, 1, 0, 1, 3)
        
        file_layout.addWidget(QLabel("Output Directory:"), 2, 0)
        self.output_dir = QLineEdit()
        self.output_dir.setReadOnly(True)
        self.output_dir.setPlaceholderText("Select output directory...")
        file_layout.addWidget(self.output_dir, 2, 1)
        
        browse_output_btn = QPushButton("Browse")
        browse_output_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogOpenButton))
        browse_output_btn.clicked.connect(self.browse_output_dir)
        file_layout.addWidget(browse_output_btn, 2, 2)
        
        file_layout.setColumnStretch(1, 1)
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # Settings group
        settings_group = QGroupBox("Transcription Settings")
        settings_layout = QGridLayout()
        settings_layout.setSpacing(10)
        
        settings_layout.addWidget(QLabel("Model Size:"), 0, 0)
        self.model_size = QComboBox()
        self.model_size.addItems(["tiny", "base", "small", "medium", "large-v2", "large-v3"])
        self.model_size.setCurrentText("base")
        settings_layout.addWidget(self.model_size, 0, 1)
        
        settings_layout.addWidget(QLabel("Language:"), 1, 0)
        self.language = QComboBox()
        self.language.addItems(["auto", "en", "es", "fr", "de", "it", "pt", "ru", "zh", "ja"])
        settings_layout.addWidget(self.language, 1, 1)
        
        settings_layout.addWidget(QLabel("Output Format:"), 2, 0)
        self.output_format = QComboBox()
        self.output_format.addItems(["txt", "srt", "vtt", "json"])
        settings_layout.addWidget(self.output_format, 2, 1)
        
        self.do_align = QCheckBox("Enable Time Alignment")
        self.do_align.setChecked(False)
        settings_layout.addWidget(self.do_align, 3, 0, 1, 2)
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        # Progress group
        progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout()
        
        self.progress_label = QLabel("Ready")
        progress_layout.addWidget(self.progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setMinimumHeight(30)  # Make progress bar thicker
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #ccc;
                border-radius: 5px;
                text-align: center;
                font-weight: bold;
                font-size: 12pt;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
        """)
        self.progress_bar.hide()
        progress_layout.addWidget(self.progress_bar)
        
        # Batch progress details
        self.batch_progress_label = QLabel("")
        self.batch_progress_label.setStyleSheet("color: #666; font-style: italic; font-weight: bold;")
        self.batch_progress_label.hide()
        progress_layout.addWidget(self.batch_progress_label)
        
        # Control Buttons
        button_layout = QHBoxLayout()
        
        self.process_button = QPushButton("Start Processing")
        self.process_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.process_button.clicked.connect(self.start_transcription)
        self.process_button.setEnabled(False)
        button_layout.addWidget(self.process_button)
        
        # Pause/Resume button (hidden by default)
        self.pause_resume_button = QPushButton("Pause")
        self.pause_resume_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
        self.pause_resume_button.clicked.connect(self.toggle_pause_resume)
        self.pause_resume_button.hide()
        button_layout.addWidget(self.pause_resume_button)
        
        # Cancel button (hidden by default)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogCancelButton))
        self.cancel_button.clicked.connect(self.cancel_processing)
        self.cancel_button.hide()
        button_layout.addWidget(self.cancel_button)
        
        reset_button = QPushButton("Reset")
        reset_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload))
        reset_button.clicked.connect(self.reset_all)
        button_layout.addWidget(reset_button)
        
        progress_layout.addLayout(button_layout)
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)
        
        # Log area
        log_group = QGroupBox("Processing Log")
        log_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        log_layout.addWidget(self.log_text)
        
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
        return widget
    
    def toggle_processing_mode(self, single_mode):
        """Toggle between single and batch mode"""
        is_batch = not single_mode
        self.batch_file_list.setVisible(is_batch)
        self.parallel_checkbox.setEnabled(is_batch)
        self.batch_progress_label.setVisible(False)
        
        if is_batch:
            self.file_path.setPlaceholderText("Select multiple audio files...")
            self.browse_btn.setText("Browse Multiple")
        else:
            self.file_path.setPlaceholderText("Select an audio file...")
            self.browse_btn.setText("Browse")
    
    def show_batch_list_context_menu(self, pos):
        """Show context menu for batch file list"""
        # Only show menu if there are items
        if self.batch_file_list.count() == 0:
            return
        
        from PySide6.QtWidgets import QMenu
        from PySide6.QtGui import QAction
        
        context_menu = QMenu(self)
        
        # Add actions
        remove_action = QAction("Remove Selected", self)
        remove_action.triggered.connect(self.remove_selected_batch_files)
        context_menu.addAction(remove_action)
        
        clear_action = QAction("Clear All", self)
        clear_action.triggered.connect(self.clear_all_batch_files)
        context_menu.addAction(clear_action)
        
        # Show the menu at the cursor position
        context_menu.exec(self.batch_file_list.mapToGlobal(pos))
    
    def remove_selected_batch_files(self):
        """Remove selected files from batch list"""
        selected_items = self.batch_file_list.selectedItems()
        if not selected_items:
            return
        
        # Get indices of selected items (in reverse to avoid index shifting)
        indices_to_remove = []
        for item in selected_items:
            row = self.batch_file_list.row(item)
            indices_to_remove.append(row)
        
        # Sort in reverse order to remove from end to beginning
        indices_to_remove.sort(reverse=True)
        
        # Remove from list widget and audio_paths
        for row in indices_to_remove:
            self.batch_file_list.takeItem(row)
            if 0 <= row < len(self.audio_paths):
                del self.audio_paths[row]
        
        # Update display
        if self.audio_paths:
            self.file_path.setText(f"{len(self.audio_paths)} files selected")
        else:
            self.file_path.clear()
        
        self.process_button.setEnabled(len(self.audio_paths) > 0)
        
        # Log the action
        self.log_message(f"Removed {len(indices_to_remove)} file(s) from batch list")
    
    def clear_all_batch_files(self):
        """Clear all files from batch list"""
        if self.batch_file_list.count() == 0:
            return
        
        reply = QMessageBox.question(
            self, "Clear All Files",
            f"Remove all {len(self.audio_paths)} files from the batch list?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.batch_file_list.clear()
            self.audio_paths.clear()
            self.file_path.clear()
            self.process_button.setEnabled(False)
            self.log_message("Cleared all files from batch list")
    
    def browse_audio_file(self):
        """Browse for audio file(s) - supports both single and batch"""
        if self.batch_mode_radio.isChecked():
            filepaths, _ = QFileDialog.getOpenFileNames(
                self,
                "Select Audio Files",
                "",
                "Audio Files (*.wav *.mp3 *.m4a *.flac *.ogg);;All Files (*.*)"
            )
            
            if filepaths:
                self.audio_paths = filepaths
                self.batch_file_list.clear()
                for path in filepaths:
                    self.batch_file_list.addItem(os.path.basename(path))
                
                self.file_path.setText(f"{len(filepaths)} files selected")
                self.process_button.setEnabled(True)
                self.log_message(f"Selected {len(filepaths)} files for batch processing")
        else:
            filepath, _ = QFileDialog.getOpenFileName(
                self,
                "Select Audio File",
                "",
                "Audio Files (*.wav *.mp3 *.m4a *.flac *.ogg);;All Files (*.*)"
            )
            
            if filepath:
                is_valid, message = validate_audio_file(filepath)
                if is_valid:
                    self.current_audio_path = filepath
                    self.audio_paths = [filepath]
                    self.file_path.setText(filepath)
                    self.process_button.setEnabled(True)
                    self.log_message(f"Selected: {os.path.basename(filepath)}")
                else:
                    QMessageBox.critical(self, "Invalid File", message)
    
    def browse_output_dir(self):
        """Browse for output directory"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Output Directory",
            "",
            QFileDialog.ShowDirsOnly
        )
        if directory:
            self.output_dir.setText(directory)
    
    def start_transcription(self):
        """Start transcription - handles both single and batch"""
        if not self.audio_paths:
            return
        
        # Check if output directory is required for batch
        if self.batch_mode_radio.isChecked() and not self.output_dir.text():
            reply = QMessageBox.question(
                self, "Output Directory",
                "No output directory selected. Results will only be displayed, not saved. Continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return
        
        self.process_button.setEnabled(False)
        self.progress_bar.show()
        self.progress_bar.setValue(0)
        
        if self.batch_mode_radio.isChecked():
            # Batch processing
            self.batch_progress_label.show()
            self.pause_resume_button.show()
            self.cancel_button.show()
            
            self.worker = BatchTranscriptionWorker(
                self.transcriber,
                self.audio_paths,
                self.model_size.currentText(),
                self.language.currentText(),
                self.do_align.isChecked(),
                self.output_dir.text() if self.output_dir.text() else None,
                self.output_format.currentText(),
                self.parallel_checkbox.isChecked()
            )
            
            self.worker.finished.connect(self.batch_transcription_finished)
            self.worker.error.connect(self.transcription_error)
            self.worker.progress.connect(self.update_progress)
            self.worker.file_progress.connect(self.update_batch_progress)
            self.worker.start()
        else:
            # Single file processing
            self.worker = TranscriptionWorker(
                self.transcriber,
                self.audio_paths[0],
                self.model_size.currentText(),
                self.language.currentText(),
                self.do_align.isChecked()
            )
            
            self.worker.finished.connect(self.transcription_finished)
            self.worker.error.connect(self.transcription_error)
            self.worker.progress.connect(self.update_progress)
            self.worker.start()
    
    def toggle_pause_resume(self):
        """Toggle pause/resume for batch processing"""
        if not self.worker or not isinstance(self.worker, BatchTranscriptionWorker):
            return
        
        if self.worker.is_paused():
            # Resume
            self.worker.resume()
            self.pause_resume_button.setText("Pause")
            self.pause_resume_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
            self.progress_label.setText("Resuming...")
            self.log_message("Batch processing resumed")
        else:
            # Pause
            self.worker.pause()
            self.pause_resume_button.setText("Resume")
            self.pause_resume_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
            self.progress_label.setText("Paused - Click Resume to continue")
            self.log_message("Batch processing paused")
    
    def cancel_processing(self):
        """Cancel batch processing"""
        if not self.worker:
            return
        
        reply = QMessageBox.question(
            self, "Cancel Processing",
            "Are you sure you want to cancel? Progress will be lost.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if isinstance(self.worker, BatchTranscriptionWorker):
                self.worker.cancel()
            self.log_message("Cancelling batch processing...")
    
    def update_progress(self, percentage, message):
        """Update progress"""
        self.progress_bar.setValue(percentage)
        self.progress_label.setText(message)
    
    def update_batch_progress(self, current, total, filename):
        """Update batch progress label"""
        self.batch_progress_label.setText(f"📁 Processing file {current}/{total}: {filename}")
    
    def transcription_finished(self, results):
        """Handle single file transcription completion"""
        self.worker = None
        self.process_button.setEnabled(True)
        self.progress_bar.hide()
        
        self.log_text.clear()
        formatted_text = ""
        
        for segment in results:
            if 'start' in segment and 'end' in segment:
                timestamp = f"[{format_time(segment['start'])} -> {format_time(segment['end'])}]\n"
                self.log_text.append(timestamp)
                formatted_text += timestamp
            
            self.log_text.append(segment['text'] + "\n")
            formatted_text += segment['text'] + "\n\n"
        
        self.current_text = formatted_text
        self.coding_text.setPlainText(formatted_text)
        
        self.log_message(f"Transcription complete: {len(results)} segments")
        QMessageBox.information(self, "Success", f"Transcription completed!\n{len(results)} segments")
    
    def batch_transcription_finished(self, results):
        """Handle batch transcription completion"""
        self.worker = None
        self.process_button.setEnabled(True)
        self.progress_bar.hide()
        self.batch_progress_label.hide()
        self.pause_resume_button.hide()
        self.cancel_button.hide()
        
        # Generate summary
        successful = sum(1 for r in results if r['success'])
        failed = len(results) - successful
        total_segments = sum(r['segments_count'] for r in results if r['success'])
        total_time = sum(r['processing_time'] for r in results if r['success'])
        
        # Display summary
        self.log_text.clear()
        self.log_text.append("=" * 60)
        self.log_text.append(f"BATCH TRANSCRIPTION SUMMARY")
        self.log_text.append("=" * 60)
        self.log_text.append(f"Total files: {len(results)}")
        self.log_text.append(f"✓ Successful: {successful}")
        self.log_text.append(f"✗ Failed: {failed}")
        self.log_text.append(f"Total segments: {total_segments:,}")
        self.log_text.append(f"Total processing time: {total_time:.1f}s ({total_time/60:.1f} minutes)")
        if successful > 0:
            self.log_text.append(f"Average time per file: {total_time/successful:.1f}s")
        self.log_text.append("")
        self.log_text.append("DETAILED RESULTS:")
        self.log_text.append("-" * 60)
        
        for i, result in enumerate(results, 1):
            if result['success']:
                self.log_text.append(
                    f"✓ {i}. {result['filename']} - "
                    f"{result['segments_count']:,} segments "
                    f"({result['processing_time']:.1f}s)"
                )
            else:
                self.log_text.append(
                    f"✗ {i}. {result['filename']} - "
                    f"ERROR: {result['error']}"
                )
        
        # Show first successful file in coding text
        for result in results:
            if result['success']:
                formatted_text = ""
                for segment in result['results']:
                    if 'start' in segment and 'end' in segment:
                        formatted_text += f"[{format_time(segment['start'])} -> {format_time(segment['end'])}]\n"
                    formatted_text += segment['text'] + "\n\n"
                
                self.current_text = formatted_text
                self.coding_text.setPlainText(formatted_text)
                break
        
        self.log_message(f"Batch complete: {successful}/{len(results)} successful")
        
        # Show detailed summary dialog
        summary_msg = (
            f"Batch transcription completed!\n\n"
            f"📊 Summary:\n"
            f"  • Total files: {len(results)}\n"
            f"  • Successful: {successful}\n"
            f"  • Failed: {failed}\n"
            f"  • Total segments: {total_segments:,}\n"
            f"  • Total time: {total_time/60:.1f} minutes"
        )
        
        if self.output_dir.text():
            summary_msg += f"\n\n💾 Results saved to:\n  {self.output_dir.text()}"
        
        QMessageBox.information(self, "Batch Complete", summary_msg)
    
    def transcription_error(self, error_msg):
        """Handle transcription error"""
        self.worker = None
        self.progress_bar.hide()
        self.batch_progress_label.hide()
        self.pause_resume_button.hide()
        self.cancel_button.hide()
        self.process_button.setEnabled(True)
        QMessageBox.critical(self, "Error", f"Transcription failed:\n{error_msg}")
    
    def reset_all(self):
        """Reset all fields"""
        self.file_path.clear()
        self.output_dir.clear()
        self.batch_file_list.clear()
        self.audio_paths.clear()
        self.current_audio_path = None
        self.process_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.progress_bar.hide()
        self.batch_progress_label.hide()
        self.pause_resume_button.hide()
        self.cancel_button.hide()
        self.log_text.clear()
        self.log_message("Reset complete")
    
    def log_message(self, message):
        """Log a message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        self.progress_label.setText(message)
    
    # ===== Code Tab Methods =====
    
    def create_code_tab(self):
        """Create code tab with HORIZONTAL LAYOUT - controls on left, text on right"""
        widget = QWidget()
        main_layout = QHBoxLayout(widget)  # Changed from QVBoxLayout to QHBoxLayout
        main_layout.setSpacing(10)
        
        # ===== LEFT PANEL: Controls =====
        left_panel = QWidget()
        left_panel.setMaximumWidth(400)  # Limit width of controls panel
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(10)
        
        # Toolbar at top of left panel
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setSpacing(5)
        
        import_btn = QPushButton("Import Text")
        import_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogOpenButton))
        import_btn.clicked.connect(self.import_text)
        toolbar_layout.addWidget(import_btn)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload))
        refresh_btn.clicked.connect(self.refresh_text_display)
        toolbar_layout.addWidget(refresh_btn)
        
        left_layout.addLayout(toolbar_layout)
        
        # Code and Memo Input Group
        input_group = QGroupBox("Code and Memo")
        input_layout = QVBoxLayout()
        input_layout.setSpacing(5)
        input_layout.setContentsMargins(10, 10, 10, 10)
        
        code_input_layout = QHBoxLayout()
        code_input_layout.setSpacing(5)
        code_label = QLabel("Code:")
        code_label.setFixedWidth(50)
        code_input_layout.addWidget(code_label)
        
        self.code_input = QComboBox()
        self.code_input.setEditable(True)
        self.code_input.setPlaceholderText("Enter or select code name...")
        code_input_layout.addWidget(self.code_input)
        input_layout.addLayout(code_input_layout)
        
        memo_layout = QVBoxLayout()
        memo_layout.setSpacing(5)
        memo_label = QLabel("Memo:")
        memo_layout.addWidget(memo_label)
        self.memo_input = QTextEdit()
        self.memo_input.setPlaceholderText("Enter memo (optional)...")
        self.memo_input.setMaximumHeight(100)
        memo_layout.addWidget(self.memo_input)
        input_layout.addLayout(memo_layout)
        
        # Action Buttons
        button_layout = QVBoxLayout()
        button_layout.setSpacing(5)
        
        create_code_btn = QPushButton("Create Code")
        create_code_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon))
        create_code_btn.setToolTip("Create code and apply to selected text (if any)")
        create_code_btn.clicked.connect(self.create_and_apply_code)
        button_layout.addWidget(create_code_btn)
        
        apply_code_btn = QPushButton("Apply Code")
        apply_code_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_CommandLink))
        apply_code_btn.setToolTip("Apply existing code to selected text")
        apply_code_btn.clicked.connect(self.apply_existing_code)
        button_layout.addWidget(apply_code_btn)
        
        merge_codes_btn = QPushButton("Merge Codes")
        merge_codes_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowRight))
        merge_codes_btn.setToolTip("Merge multiple codes into one")
        merge_codes_btn.clicked.connect(self.merge_codes_dialog)
        button_layout.addWidget(merge_codes_btn)
        
        # Export dropdown button
        export_menu_btn = QPushButton("Export Annotations")
        export_menu_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton))
        export_menu_btn.setToolTip("Export annotations in various formats")
        
        # Create export menu
        from PySide6.QtWidgets import QMenu
        from PySide6.QtGui import QAction
        export_menu = QMenu(export_menu_btn)
        
        export_html_action = QAction("Export as HTML", self)
        export_html_action.triggered.connect(lambda: self.save_annotation('html'))
        export_menu.addAction(export_html_action)
        
        export_srt_action = QAction("Export as SRT (Subtitles)", self)
        export_srt_action.triggered.connect(lambda: self.save_annotation('srt'))
        export_menu.addAction(export_srt_action)
        
        export_vtt_action = QAction("Export as VTT (Web Subtitles)", self)
        export_vtt_action.triggered.connect(lambda: self.save_annotation('vtt'))
        export_menu.addAction(export_vtt_action)
        
        export_csv_action = QAction("Export as CSV", self)
        export_csv_action.triggered.connect(lambda: self.save_annotation('csv'))
        export_menu.addAction(export_csv_action)
        
        export_json_action = QAction("Export as JSON", self)
        export_json_action.triggered.connect(lambda: self.save_annotation('json'))
        export_menu.addAction(export_json_action)
        
        export_menu_btn.setMenu(export_menu)
        button_layout.addWidget(export_menu_btn)
        
        input_layout.addLayout(button_layout)
        input_group.setLayout(input_layout)
        left_layout.addWidget(input_group)
        
        # Workflow Legend
        self.legend_label = QLabel(
            "<b>Workflow:</b><br>"
            "1) Enable Selection<br>"
            "2) Select text on right<br>"
            "3) Create or Apply Code<br><br>"
            "<i>Click code labels to remove</i>"
        )
        self.legend_label.setStyleSheet(
            "color: #666; "
            "font-size: 10pt; "
            "padding: 10px; "
            "background-color: #f5f5f5; "
            "border-radius: 5px; "
            "border: 1px solid #ddd;"
        )
        self.legend_label.setWordWrap(True)
        left_layout.addWidget(self.legend_label)
        
        # Status Label
        self.code_status_label = QLabel("Ready")
        self.code_status_label.setStyleSheet(
            "color: #2E7D32; "
            "font-weight: bold; "
            "padding: 8px; "
            "background-color: #e8f5e9; "
            "border-radius: 5px; "
            "border: 1px solid #4CAF50;"
        )
        self.code_status_label.setWordWrap(True)
        left_layout.addWidget(self.code_status_label)
        
        # Add stretch to push everything to top
        left_layout.addStretch()
        
        # ===== RIGHT PANEL: Text Display =====
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(5)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Title and Font Controls
        title_layout = QHBoxLayout()
        title_layout.setSpacing(5)
        
        # Selection Mode Buttons (left side)
        self.select_text_button = QPushButton("Enable Selection")
        self.select_text_button.setCheckable(True)
        self.select_text_button.setMinimumHeight(32)
        self.select_text_button.toggled.connect(self.toggle_selection_mode)
        title_layout.addWidget(self.select_text_button)
        
        clear_selection_btn = QPushButton("Clear Selection")
        clear_selection_btn.setMinimumHeight(32)
        clear_selection_btn.clicked.connect(self.clear_selection)
        title_layout.addWidget(clear_selection_btn)
        
        title_layout.addStretch()
        
        # Title (center-left)
        title_label = QLabel("<b>Text Display</b>")
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        font_control_label = QLabel("Text Size:")
        font_control_label.setStyleSheet("font-weight: bold; font-size: 10pt;")
        title_layout.addWidget(font_control_label)
        
        decrease_font_btn = QPushButton("−")
        decrease_font_btn.setFixedSize(32, 32)
        decrease_font_btn.setToolTip("Decrease font size")
        decrease_font_btn.setStyleSheet("""
            QPushButton {
                font-size: 18pt;
                font-weight: bold;
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        decrease_font_btn.clicked.connect(self.decrease_font_size)
        title_layout.addWidget(decrease_font_btn)
        
        self.font_size_label = QLabel(f"{self.text_display_font_size}")
        self.font_size_label.setFixedWidth(30)
        self.font_size_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.font_size_label.setStyleSheet("font-weight: bold; font-size: 11pt;")
        title_layout.addWidget(self.font_size_label)
        
        increase_font_btn = QPushButton("+")
        increase_font_btn.setFixedSize(32, 32)
        increase_font_btn.setToolTip("Increase font size")
        increase_font_btn.setStyleSheet("""
            QPushButton {
                font-size: 18pt;
                font-weight: bold;
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        increase_font_btn.clicked.connect(self.increase_font_size)
        title_layout.addWidget(increase_font_btn)
        
        right_layout.addLayout(title_layout)
        
        # Text Display Widget
        self.coding_text = QTextEdit()
        self.coding_text.setReadOnly(True)
        self.coding_text.viewport().installEventFilter(self)
        self.coding_text.setUndoRedoEnabled(False)
        self.coding_text.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        self.coding_text.document().setMaximumBlockCount(1000000)
        
        doc = self.coding_text.document()
        doc.setDocumentMargin(2)
        doc.setUseDesignMetrics(False)
        
        self.update_text_display_font()
        right_layout.addWidget(self.coding_text)
        
        # ===== Add panels to main layout using splitter =====
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        
        # Set initial sizes: left panel 400px, right panel takes remaining space
        splitter.setSizes([400, 800])
        splitter.setStretchFactor(0, 0)  # Left panel doesn't stretch
        splitter.setStretchFactor(1, 1)  # Right panel stretches
        
        main_layout.addWidget(splitter)
        
        return widget
    
    def increase_font_size(self):
        if self.text_display_font_size < 32:
            self.text_display_font_size += 1
            self.update_text_display_font()
            self.font_size_label.setText(f"{self.text_display_font_size}")
    
    def decrease_font_size(self):
        if self.text_display_font_size > 8:
            self.text_display_font_size -= 1
            self.update_text_display_font()
            self.font_size_label.setText(f"{self.text_display_font_size}")
    
    def update_text_display_font(self):
        font = QFont()
        font.setPointSize(self.text_display_font_size)
        self.coding_text.setFont(font)
    
    def ensure_no_selection(self):
        """
        ENHANCED: Ensure no text selection and proper highlighting state
        """
        # Get current cursor
        cursor = self.coding_text.textCursor()
        
        # Clear any selection
        cursor.clearSelection()
        
        # Set cursor back without selection
        self.coding_text.setTextCursor(cursor)
        
        # CRITICAL: If selection mode is disabled, ensure read-only and proper palette
        if not self.selection_mode:
            self.coding_text.setReadOnly(True)
            
            # Reset palette to default (removes any blue selection artifacts)
            palette = self.coding_text.palette()
            palette.setColor(QPalette.ColorRole.Highlight, QColor(48, 140, 198))
            palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
            self.coding_text.setPalette(palette)
    
    # def apply_single_annotation_incremental(self, annotation):
    #     """
    #     Apply a single annotation to the display incrementally (FAST - no full rebuild)
        
    #     This is much faster than refresh_text_display() for adding one annotation
    #     because it only updates the specific text range, not the entire document.
    #     """
    #     if not self.current_text:
    #         return
        
    #     # OPTIMIZATION: Disable updates during the operation
    #     self.coding_text.setUpdatesEnabled(False)
    #     self.coding_text.blockSignals(True)
        
    #     try:
    #         doc = self.coding_text.document()
            
    #         # Calculate display position (accounting for existing labels)
    #         display_start = annotation.start
    #         display_end = annotation.end
            
    #         # Count all annotation labels that come before this position
    #         for ann in self.annotation_manager.annotations:
    #             if ann == annotation:
    #                 continue  # Skip the one we're adding
    #             if ann.end <= annotation.start:
    #                 # This annotation's label is before our new annotation
    #                 label_length = len(f" [{ann.code}]")
    #                 display_start += label_length
    #                 display_end += label_length
            
    #         # Get color for this code
    #         color = self.annotation_manager.code_colors.get(annotation.code, '#FFFF00')
            
    #         # Create formats
    #         bg_fmt = QTextCharFormat()
    #         bg_fmt.setBackground(QColor(color))
    #         bg_fmt.setForeground(QColor(0, 0, 0))
            
    #         label_fmt = QTextCharFormat()
    #         label_fmt.setForeground(QColor(100, 100, 100))
    #         label_fmt.setFontWeight(QFont.Weight.Bold)
    #         label_fmt.setBackground(QColor(color))
    #         label_fmt.setProperty(1001, annotation.code)
            
    #         # Apply formatting in single atomic operation
    #         cursor = QTextCursor(doc)
    #         cursor.beginEditBlock()
            
    #         try:
    #             # Apply background to the text range
    #             cursor.setPosition(display_start)
    #             cursor.setPosition(display_end, QTextCursor.MoveMode.KeepAnchor)
    #             cursor.mergeCharFormat(bg_fmt)
                
    #             # Insert code label at the end
    #             cursor.setPosition(display_end)
    #             label_text = f" [{annotation.code}]"
    #             cursor.setCharFormat(label_fmt)
    #             cursor.insertText(label_text)
                
    #         finally:
    #             cursor.endEditBlock()
            
    #     finally:
    #         # Re-enable updates - single repaint
    #         self.coding_text.blockSignals(False)
    #         self.coding_text.setUpdatesEnabled(True)
    
    def refresh_text_display(self):
        """
        OPTIMIZED: Reliable text display refresh with proper annotation rendering
        
        This method rebuilds the entire display from scratch, which is slower but
        guarantees correct positioning and formatting.
        """
        if not self.current_text:
            return
        
        # Store cursor position and scroll position
        cursor = self.coding_text.textCursor()
        original_position = cursor.position()
        scrollbar = self.coding_text.verticalScrollBar()
        scroll_position = scrollbar.value()
        
        # Disable updates and signals for performance
        self.coding_text.setUpdatesEnabled(False)
        self.coding_text.blockSignals(True)
        
        try:
            # CRITICAL: Clear all existing formatting first
            self.coding_text.clear()
            
            # Set plain text (this creates a clean slate)
            self.coding_text.setPlainText(self.current_text)
            
            # CRITICAL: Reset text format to default before applying annotations
            default_fmt = QTextCharFormat()
            default_fmt.setBackground(QColor(255, 255, 255))  # White background
            default_fmt.setForeground(QColor(0, 0, 0))  # Black text
            
            cursor = QTextCursor(self.coding_text.document())
            cursor.select(QTextCursor.SelectionType.Document)
            cursor.mergeCharFormat(default_fmt)
            cursor.clearSelection()
            
            # Sort annotations by start position
            sorted_annotations = sorted(self.annotation_manager.annotations, 
                                    key=lambda a: (a.start, a.end))
            
            if not sorted_annotations:
                return
            
            doc = self.coding_text.document()
            
            # Pre-create format objects (performance optimization)
            fmt_cache = {}
            for ann in sorted_annotations:
                if ann.code not in fmt_cache:
                    color = self.annotation_manager.code_colors.get(ann.code, '#FFFF00')
                    
                    bg_fmt = QTextCharFormat()
                    bg_fmt.setBackground(QColor(color))
                    bg_fmt.setForeground(QColor(0, 0, 0))
                    
                    label_fmt = QTextCharFormat()
                    label_fmt.setForeground(QColor(100, 100, 100))
                    label_fmt.setFontWeight(QFont.Weight.Bold)
                    label_fmt.setBackground(QColor(color))
                    label_fmt.setProperty(1001, ann.code)
                    
                    fmt_cache[ann.code] = (bg_fmt, label_fmt)
            
            # Apply all annotations in a single atomic operation
            cursor = QTextCursor(doc)
            cursor.beginEditBlock()
            
            try:
                # Track cumulative offset from inserted labels
                offset = 0
                
                for ann in sorted_annotations:
                    # Validate annotation bounds
                    if ann.start < 0 or ann.end > len(self.current_text) or ann.start >= ann.end:
                        continue
                    
                    bg_fmt, label_fmt = fmt_cache[ann.code]
                    
                    # Calculate display positions (accounting for all previous labels)
                    display_start = ann.start + offset
                    display_end = ann.end + offset
                    
                    # Apply background highlighting to the annotated text
                    cursor.setPosition(display_start)
                    cursor.setPosition(display_end, QTextCursor.MoveMode.KeepAnchor)
                    cursor.mergeCharFormat(bg_fmt)
                    
                    # Insert code label immediately after the annotated text
                    cursor.setPosition(display_end)
                    label_text = f" [{ann.code}]"
                    cursor.setCharFormat(label_fmt)
                    cursor.insertText(label_text)
                    
                    # Update offset for subsequent annotations
                    offset += len(label_text)
            
            finally:
                cursor.endEditBlock()
            
            # Restore cursor position (capped at document length)
            doc = self.coding_text.document()
            new_cursor = QTextCursor(doc)
            safe_position = min(original_position, doc.characterCount() - 1)
            new_cursor.setPosition(max(0, safe_position))
            new_cursor.clearSelection()  # CRITICAL: Ensure no selection
            self.coding_text.setTextCursor(new_cursor)
            
            # Restore scroll position
            QTimer.singleShot(0, lambda: scrollbar.setValue(scroll_position))
        
        finally:
            # Re-enable updates (single repaint)
            self.coding_text.blockSignals(False)
            self.coding_text.setUpdatesEnabled(True)
        
        # CRITICAL: Force clear any residual selection
        self.ensure_no_selection()
        
        # Update status
        ann_count = len(sorted_annotations)
        if ann_count:
            self.code_status_label.setText(f"✓ {ann_count} annotation{'s' if ann_count != 1 else ''} displayed")
            self.code_status_label.setStyleSheet("color: #2E7D32; font-weight: bold; padding: 5px;")
        else:
            self.code_status_label.setText("No annotations")
            self.code_status_label.setStyleSheet("color: #666; font-weight: normal; padding: 5px;")
    
    def eventFilter(self, obj, event):
        if obj == self.coding_text.viewport() and event.type() == QEvent.Type.MouseButtonPress:
            if event.button() == Qt.MouseButton.LeftButton:
                cursor = self.coding_text.cursorForPosition(event.pos())
                pos = cursor.position()
                
                cursor.setPosition(pos)
                char_format = cursor.charFormat()
                
                code_from_format = char_format.property(1001)
                if code_from_format:
                    self.handle_code_label_click(pos, code_from_format)
                    return True
                
                cursor.select(QTextCursor.SelectionType.WordUnderCursor)
                selected_text = cursor.selectedText()
                
                if selected_text and len(selected_text) > 0:
                    start_pos = cursor.selectionStart()
                    end_pos = cursor.selectionEnd()
                    
                    cursor.setPosition(start_pos)
                    cursor.movePosition(QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.KeepAnchor, 1)
                    if cursor.selectedText() == '[':
                        cursor.setPosition(start_pos - 1)
                        cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor, 1)
                        while cursor.position() < len(self.coding_text.toPlainText()):
                            cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor, 1)
                            text = cursor.selectedText()
                            if text.endswith(']'):
                                code_name = text[1:-1]
                                self.handle_code_label_click(pos, code_name)
                                return True
                            if len(text) > 50:
                                break
        
        return super().eventFilter(obj, event)
    
    def handle_code_label_click(self, position, code_name):
        doc_text = self.coding_text.toPlainText()
        
        labels_before = 0
        search_pos = 0
        while search_pos < position:
            bracket_pos = doc_text.find('[', search_pos)
            if bracket_pos == -1 or bracket_pos >= position:
                break
            close_bracket = doc_text.find(']', bracket_pos)
            if close_bracket == -1 or close_bracket >= position:
                break
            if doc_text[bracket_pos-1:bracket_pos] == ' ':
                labels_before += 1
                search_pos = close_bracket + 1
            else:
                search_pos = bracket_pos + 1
        
        sorted_anns = sorted(self.annotation_manager.annotations, key=lambda a: a.start, reverse=True)
        
        best_match = None
        min_distance = float('inf')
        
        for ann in self.annotation_manager.annotations:
            if ann.code == code_name:
                labels_before_this = sum(1 for a in self.annotation_manager.annotations 
                                        if a.start < ann.start)
                estimated_label_pos = ann.end + labels_before_this * len(f" [{ann.code}]")
                
                distance = abs(estimated_label_pos - position)
                if distance < min_distance:
                    min_distance = distance
                    best_match = ann
        
        if best_match:
            dialog = RemoveAnnotationDialog(best_match, self)
            result = dialog.exec()
            if result == QDialog.DialogCode.Accepted or result == 1:
                self.annotation_manager.remove_annotation(best_match)
                self.update_all_displays()
                self.refresh_text_display()
                self.ensure_no_selection()
                self.code_status_label.setText(f"✓ Annotation with code '{best_match.code}' removed")
                self.code_status_label.setStyleSheet("color: #2E7D32; font-weight: bold; padding: 5px;")
    
    def apply_existing_code(self):
        """Apply existing code - FIXED to always use reliable refresh"""
        if not self.annotation_manager.codes:
            QMessageBox.warning(self, "Warning", "No codes available. Create a code first.")
            return
        
        cursor = self.coding_text.textCursor()
        if not cursor.hasSelection():
            QMessageBox.warning(self, "Warning", "Please select text first")
            return
        
        dialog = CodeSelectionDialog(self.annotation_manager.codes, self)
        result = dialog.exec()
        
        if result == QDialog.DialogCode.Accepted or result == 1:
            code, memo = dialog.get_code_and_memo()
            
            if code:
                display_start = cursor.selectionStart()
                display_end = cursor.selectionEnd()
                
                # Get selected text
                selected_display_text = cursor.selectedText()
                selected_display_text = selected_display_text.replace('\u2029', '\n')
                
                # Remove annotation labels
                import re
                clean_selected_text = re.sub(r'\s*\[[^\]]+\]', '', selected_display_text).strip()
                
                # Convert positions
                original_start, original_end = self.convert_display_to_original_positions(display_start, display_end)
                
                # Store text
                actual_text = clean_selected_text if clean_selected_text else selected_display_text
                
                # Add annotation
                self.annotation_manager.add_annotation(original_start, original_end, actual_text, code, memo)
                
                # Clear selection
                cursor.clearSelection()
                self.coding_text.setTextCursor(cursor)
                
                # FIXED: Always use full refresh
                self.refresh_text_display()
                
                # Update displays
                self.update_all_displays(update_codebook=True, update_records=True, update_theme=False, update_dropdown=False)
                
                # CRITICAL: Ensure no selection
                self.ensure_no_selection()
                
                # Show status
                preview_text = clean_selected_text if clean_selected_text else selected_display_text
                preview = preview_text[:50] + "..." if len(preview_text) > 50 else preview_text
                
                self.code_status_label.setText(f"✓ Code '{code}' applied to: \"{preview}\"")
                self.code_status_label.setStyleSheet("color: #2E7D32; font-weight: bold; padding: 5px;")
    
    def toggle_selection_mode(self, enabled):
        self.selection_mode = enabled
        
        if enabled:
            self.select_text_button.setText("Disable Selection")
            palette = self.coding_text.palette()
            palette.setColor(QPalette.ColorRole.Highlight, QColor(255, 255, 0))
            palette.setColor(QPalette.ColorRole.HighlightedText, QColor(0, 0, 0))
            self.coding_text.setPalette(palette)
            self.coding_text.setReadOnly(False)
            self.code_status_label.setText("Selection mode enabled - select text to annotate")
            self.code_status_label.setStyleSheet("color: #1976D2; font-weight: bold; padding: 5px;")
        else:
            self.select_text_button.setText("Enable Selection")
            palette = self.coding_text.palette()
            palette.setColor(QPalette.ColorRole.Highlight, QColor(48, 140, 198))
            palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
            self.coding_text.setPalette(palette)
            cursor = self.coding_text.textCursor()
            cursor.clearSelection()
            self.coding_text.setTextCursor(cursor)
            self.coding_text.setReadOnly(True)
            self.code_status_label.setText("Selection mode disabled")
            self.code_status_label.setStyleSheet("color: #666; font-weight: normal; padding: 5px;")
    
    def update_code_dropdown(self):
        """Update code dropdown with performance optimization"""
        current_text = self.code_input.currentText()
        
        # Block signals during update to prevent unnecessary event handling
        self.code_input.blockSignals(True)
        try:
            self.code_input.clear()
            self.code_input.addItems(sorted(self.annotation_manager.codes))
            self.code_input.setCurrentText(current_text)
        finally:
            self.code_input.blockSignals(False)
    
    def update_all_displays(self, update_codebook=True, update_records=True, update_theme=True, update_dropdown=True):
        """
        Update displays selectively for better performance
        
        Args:
            update_codebook: Whether to update the codebook table
            update_records: Whether to update the records table
            update_theme: Whether to update the theme tree
            update_dropdown: Whether to update the code dropdown
        """
        if update_codebook:
            self.update_codebook_table()
        if update_records:
            self.update_records_table()
        if update_theme:
            self.update_theme_tree()
        if update_dropdown:
            self.update_code_dropdown()
    
    def create_and_apply_code(self):
        """Create and apply code - FIXED to always use reliable refresh"""
        code = self.code_input.currentText().strip()
        if not code:
            QMessageBox.warning(self, "Warning", "Please enter a code name")
            return
        
        cursor = self.coding_text.textCursor()
        has_selection = cursor.hasSelection()
        
        is_new_code = code not in self.annotation_manager.codes
        if is_new_code:
            self.annotation_manager.codes.add(code)
            color_idx = len(self.annotation_manager.code_colors) % len(self.annotation_manager.color_palette)
            self.annotation_manager.code_colors[code] = self.annotation_manager.color_palette[color_idx]
        
        if has_selection:
            display_start = cursor.selectionStart()
            display_end = cursor.selectionEnd()
            
            # Get the text that the user selected
            selected_display_text = cursor.selectedText()
            selected_display_text = selected_display_text.replace('\u2029', '\n')
            
            # Remove any annotation labels from selection
            import re
            clean_selected_text = re.sub(r'\s*\[[^\]]+\]', '', selected_display_text).strip()
            
            memo = self.memo_input.toPlainText().strip()
            
            # Convert display positions to original positions
            original_start, original_end = self.convert_display_to_original_positions(display_start, display_end)
            
            # Store the clean selected text
            actual_text = clean_selected_text if clean_selected_text else selected_display_text
            
            # Add annotation
            new_annotation = self.annotation_manager.add_annotation(original_start, original_end, actual_text, code, memo)
            
            # Clear selection first
            cursor.clearSelection()
            self.coding_text.setTextCursor(cursor)
            self.memo_input.clear()
            
            # FIXED: Always use full refresh for reliability
            # The incremental method had bugs with position tracking
            self.refresh_text_display()
            
            # Update tables
            self.update_all_displays(update_codebook=True, update_records=True, update_theme=False, update_dropdown=is_new_code)
            
            # CRITICAL: Ensure no selection after all updates
            self.ensure_no_selection()
            
            # Show status with preview
            preview_text = clean_selected_text if clean_selected_text else selected_display_text
            preview = preview_text[:50] + "..." if len(preview_text) > 50 else preview_text
            
            if is_new_code:
                self.code_status_label.setText(f"✓ Code '{code}' created and applied to: \"{preview}\"")
                self.code_status_label.setStyleSheet("color: #2E7D32; font-weight: bold; padding: 5px;")
            else:
                self.code_status_label.setText(f"✓ Code '{code}' applied to: \"{preview}\"")
                self.code_status_label.setStyleSheet("color: #2E7D32; font-weight: bold; padding: 5px;")
        else:
            # Only new code, no annotation
            self.update_all_displays(update_codebook=True, update_records=False, update_theme=False, update_dropdown=True)
            if is_new_code:
                self.code_status_label.setText(f"✓ Code '{code}' created (select text to apply)")
                self.code_status_label.setStyleSheet("color: #1976D2; font-weight: bold; padding: 5px;")
            else:
                self.code_status_label.setText(f"! Code '{code}' already exists (select text to apply)")
                self.code_status_label.setStyleSheet("color: #F57C00; font-weight: bold; padding: 5px;")
    
    def convert_display_to_original_positions(self, display_start, display_end):
        """
        FIXED: Accurate conversion from display positions to original text positions
        
        The display text includes annotation labels like " [code1]" which are NOT in the original text.
        This method now correctly handles overlapping annotations and edge cases.
        
        Key improvements:
        1. Builds the display text character-by-character to track exact positions
        2. Handles overlapping annotations correctly
        3. Accounts for all labels that appear before the selection
        """
        if not self.annotation_manager.annotations:
            return display_start, display_end
        
        # Sort annotations by their position in the ORIGINAL text
        sorted_anns = sorted(self.annotation_manager.annotations, key=lambda a: (a.start, a.end))
        
        # Build a mapping from display position to original position
        # by simulating how the display text is constructed
        display_pos = 0
        original_pos = 0
        display_to_original = {}
        
        # Track which annotations have been "processed" (label inserted)
        processed_annotations = set()
        
        text_len = len(self.current_text)
        
        # Process character by character
        while original_pos < text_len:
            # Map current display position to original position
            display_to_original[display_pos] = original_pos
            
            # Move forward one character in both
            display_pos += 1
            original_pos += 1
            
            # Check if any annotation ends at this position
            # (meaning we need to insert its label in the display)
            for ann in sorted_anns:
                if ann in processed_annotations:
                    continue
                
                # If we just passed the end of this annotation, insert its label
                if original_pos == ann.end:
                    label = f" [{ann.code}]"
                    label_length = len(label)
                    
                    # The label occupies display positions but not original positions
                    # So we map multiple display positions to the same original position
                    for i in range(label_length):
                        display_to_original[display_pos] = original_pos
                        display_pos += 1
                    
                    processed_annotations.add(ann)
        
        # Handle the final position (end of text)
        display_to_original[display_pos] = original_pos
        
        # Now convert the display positions to original positions
        # Find the closest mapped position if exact match doesn't exist
        def get_original_pos(display_p):
            if display_p in display_to_original:
                return display_to_original[display_p]
            
            # Find nearest lower display position that is mapped
            for dp in range(display_p, -1, -1):
                if dp in display_to_original:
                    return display_to_original[dp]
            
            return 0
        
        original_start = get_original_pos(display_start)
        original_end = get_original_pos(display_end)
        
        # Ensure valid range
        original_start = max(0, min(original_start, len(self.current_text)))
        original_end = max(0, min(original_end, len(self.current_text)))
        
        # Ensure start < end
        if original_start >= original_end:
            # If they're equal, try to expand to at least one character
            if original_start < len(self.current_text):
                original_end = original_start + 1
            elif original_end > 0:
                original_start = original_end - 1
            else:
                # Fallback: use a small range at the beginning
                original_start = 0
                original_end = min(1, len(self.current_text))
        
        return original_start, original_end
    
    def clear_selection(self):
        cursor = self.coding_text.textCursor()
        cursor.clearSelection()
        self.coding_text.setTextCursor(cursor)
        self.code_status_label.setText("Selection cleared")
        self.code_status_label.setStyleSheet("color: #666; font-weight: normal; padding: 5px;")
    
    def import_text(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Import Text",
            "",
            "Text Files (*.txt);;All Files (*.*)"
        )
        
        if not filepath:
            return
        
        # Ask user if they want to clear existing annotations
        if self.annotation_manager.annotations or self.annotation_manager.codes:
            reply = QMessageBox.question(
                self,
                "Clear Existing Data",
                "Importing new text will clear all existing annotations and codes.\n\nContinue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            if reply == QMessageBox.StandardButton.No:
                return
        
        try:
            file_size = os.path.getsize(filepath)
            file_size_mb = file_size / (1024 * 1024)
            
            # Show loading message
            self.code_status_label.setText("⏳ Reading file...")
            self.code_status_label.setStyleSheet("color: #1976D2; font-weight: bold; padding: 5px;")
            QApplication.processEvents()
            
            # OPTIMIZATION: For very large files, warn user
            if file_size_mb > 20:
                reply = QMessageBox.question(
                    self,
                    "Large File Warning",
                    f"This file is {file_size_mb:.1f} MB. Loading may take a moment.\n\nContinue?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.Yes
                )
                if reply == QMessageBox.StandardButton.No:
                    return
            
            # Read entire file
            with open(filepath, 'rb') as f:
                raw_data = f.read()
            
            # Decode with fallback
            try:
                text = raw_data.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    text = raw_data.decode('latin-1')
                except:
                    text = raw_data.decode('utf-8', errors='ignore')
            
            # CLEAR ALL EXISTING DATA BEFORE LOADING NEW TEXT
            self.annotation_manager.annotations.clear()
            self.annotation_manager.codes.clear()
            self.annotation_manager.code_colors.clear()
            
            # Store new text
            self.current_text = text
            
            # Calculate stats BEFORE display (fast)
            char_count = len(text)
            line_count = text.count('\n') + 1
            
            if file_size_mb < 5:
                word_count = len(text.split())
                stats = f"✓ Imported: {char_count:,} chars, {word_count:,} words, {line_count:,} lines ({file_size_mb:.2f} MB)"
            else:
                word_count = char_count // 6
                stats = f"✓ Imported: {char_count:,} chars, ~{word_count:,} words, {line_count:,} lines ({file_size_mb:.2f} MB)"
            
            # Update status immediately
            self.code_status_label.setText("⏳ Displaying text...")
            self.code_status_label.setStyleSheet("color: #1976D2; font-weight: bold; padding: 5px;")
            QApplication.processEvents()
            
            # OPTIMIZATION: Display the text with all optimizations
            self.coding_text.setUpdatesEnabled(False)
            self.coding_text.blockSignals(True)
            
            # Clear and set text
            self.coding_text.clear()
            self.coding_text.document().setPlainText(text)
            
            # Re-enable in single operation
            self.coding_text.blockSignals(False)
            self.coding_text.setUpdatesEnabled(True)
            
            # Update all displays to reflect cleared state
            self.update_all_displays()
            
            # Clear selection mode if enabled
            if self.selection_mode:
                self.select_text_button.setChecked(False)
                self.toggle_selection_mode(False)
            
            # Success message
            self.code_status_label.setText(stats)
            self.code_status_label.setStyleSheet("color: #2E7D32; font-weight: bold; padding: 5px;")
            
            # Log the import
            self.log_message(f"✓ Text imported and previous data cleared: {os.path.basename(filepath)}")
            
        except Exception as e:
            self.coding_text.blockSignals(False)
            self.coding_text.setUpdatesEnabled(True)
            QMessageBox.critical(self, "Error", f"Failed to import text:\n{str(e)}")
            self.code_status_label.setText("✗ Import failed")
            self.code_status_label.setStyleSheet("color: #d32f2f; font-weight: bold; padding: 5px;")
    
    def save_annotation(self, format_type='html'):
        """
        ENHANCED: Save annotations in multiple formats including SRT, VTT, and CSV
        
        Args:
            format_type: Format to export ('html', 'srt', 'vtt', 'csv', 'json')
        """
        if not self.annotation_manager.annotations:
            QMessageBox.warning(self, "Warning", "No annotations to save")
            return
        
        # Check for timestamps requirement
        has_timestamps = bool(self.current_text)  # We'll extract position info
        
        # Get file path based on format
        if format_type == 'srt':
            filepath, _ = QFileDialog.getSaveFileName(
                self, "Export as SRT", "", "SRT Subtitle Files (*.srt)"
            )
        elif format_type == 'vtt':
            filepath, _ = QFileDialog.getSaveFileName(
                self, "Export as VTT", "", "WebVTT Subtitle Files (*.vtt)"
            )
        elif format_type == 'csv':
            filepath, _ = QFileDialog.getSaveFileName(
                self, "Export as CSV", "", "CSV Files (*.csv)"
            )
        elif format_type == 'json':
            filepath, _ = QFileDialog.getSaveFileName(
                self, "Export as JSON", "", "JSON Files (*.json)"
            )
        else:  # html
            filepath, _ = QFileDialog.getSaveFileName(
                self, "Export as HTML", "", "HTML Files (*.html)"
            )
        
        if not filepath:
            return
        
        try:
            if format_type == 'csv':
                self._export_annotations_csv(filepath)
            elif format_type == 'srt':
                self._export_annotations_srt(filepath)
            elif format_type == 'vtt':
                self._export_annotations_vtt(filepath)
            elif format_type == 'json':
                self._export_annotations_json(filepath)
            else:  # html
                self._export_annotations_html(filepath)
            
            QMessageBox.information(
                self, 
                "Success", 
                f"Annotations exported successfully to {format_type.upper()} format!\n\n{filepath}"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export annotations:\n{str(e)}")


    def _export_annotations_csv(self, filepath):
        """Export annotations to CSV format"""
        import csv
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow(['ID', 'Start Position', 'End Position', 'Text', 'Code', 'Memo', 'Text Length'])
            
            # Write annotations sorted by position
            sorted_anns = sorted(self.annotation_manager.annotations, key=lambda a: a.start)
            
            for idx, ann in enumerate(sorted_anns, 1):
                writer.writerow([
                    idx,
                    ann.start,
                    ann.end,
                    ann.text,
                    ann.code,
                    ann.memo,
                    len(ann.text)
                ])


    def _export_annotations_srt(self, filepath):
        """
        Export annotations to SRT subtitle format
        
        Each annotation becomes a subtitle entry with its text and code
        """
        sorted_anns = sorted(self.annotation_manager.annotations, key=lambda a: a.start)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            for idx, ann in enumerate(sorted_anns, 1):
                # Calculate approximate timestamps based on position
                # Assume 200 chars per minute reading speed
                start_time = ann.start / 200.0 * 60.0  # Convert char position to seconds
                end_time = ann.end / 200.0 * 60.0
                
                # Format SRT timestamps (HH:MM:SS,mmm)
                start_srt = self._format_srt_timestamp(start_time)
                end_srt = self._format_srt_timestamp(end_time)
                
                # Write SRT entry
                f.write(f"{idx}\n")
                f.write(f"{start_srt} --> {end_srt}\n")
                
                # Write text with code indicator
                text = ann.text.replace('\n', ' ')  # SRT doesn't handle newlines well
                f.write(f"[{ann.code}] {text}\n")
                
                # Add memo as additional line if present
                if ann.memo:
                    memo = ann.memo.replace('\n', ' ')
                    f.write(f"({memo})\n")
                
                f.write("\n")


    def _export_annotations_vtt(self, filepath):
        """
        Export annotations to WebVTT format
        
        Similar to SRT but with VTT-specific formatting
        """
        sorted_anns = sorted(self.annotation_manager.annotations, key=lambda a: a.start)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            # VTT header
            f.write("WEBVTT\n\n")
            
            for idx, ann in enumerate(sorted_anns, 1):
                # Calculate timestamps
                start_time = ann.start / 200.0 * 60.0
                end_time = ann.end / 200.0 * 60.0
                
                # Format VTT timestamps (HH:MM:SS.mmm)
                start_vtt = self._format_vtt_timestamp(start_time)
                end_vtt = self._format_vtt_timestamp(end_time)
                
                # Write VTT cue with identifier
                f.write(f"{idx}\n")
                f.write(f"{start_vtt} --> {end_vtt}\n")
                
                # Write text with code as voice label
                text = ann.text.replace('\n', ' ')
                
                # VTT supports voice tags for styling
                f.write(f"<v {ann.code}>{text}</v>\n")
                
                # Add memo as note if present
                if ann.memo:
                    memo = ann.memo.replace('\n', ' ')
                    f.write(f"<i>({memo})</i>\n")
                
                f.write("\n")


    def _export_annotations_json(self, filepath):
        """Export annotations to JSON format with full metadata"""
        data = {
            'text': self.current_text,
            'export_date': datetime.now().isoformat(),
            'total_annotations': len(self.annotation_manager.annotations),
            'codes': list(self.annotation_manager.codes),
            'code_colors': self.annotation_manager.code_colors,
            'annotations': [
                {
                    'id': idx,
                    'start': ann.start,
                    'end': ann.end,
                    'text': ann.text,
                    'code': ann.code,
                    'memo': ann.memo,
                    'length': len(ann.text),
                    'color': self.annotation_manager.code_colors.get(ann.code, '#FFFFFF')
                }
                for idx, ann in enumerate(sorted(self.annotation_manager.annotations, 
                                                key=lambda a: a.start), 1)
            ],
            'statistics': {
                'total_characters': len(self.current_text),
                'coded_characters': sum(ann.end - ann.start for ann in self.annotation_manager.annotations),
                'code_distribution': {
                    code: len([a for a in self.annotation_manager.annotations if a.code == code])
                    for code in self.annotation_manager.codes
                }
            }
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


    def _export_annotations_html(self, filepath):
        """
        Export annotations to HTML format with ACCURATE visual highlighting
        ENHANCED: Now includes position metadata for round-trip compatibility
        
        FIXED: Properly handles overlapping annotations and correct positioning
        """
        import html as html_module
        
        html = """<!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Annotated Text - VoxScribe</title>
        <meta name="generator" content="VoxScribe">
        <meta name="voxscribe-version" content="1.0.0">
        <style>
            body {
                font-family: Arial, sans-serif;
                padding: 20px;
                max-width: 1200px;
                margin: 0 auto;
                line-height: 1.8;
            }
            h1 {
                color: #333;
                border-bottom: 2px solid #4CAF50;
                padding-bottom: 10px;
            }
            .metadata {
                background-color: #f5f5f5;
                padding: 15px;
                border-radius: 5px;
                margin: 20px 0;
            }
            .annotation {
                padding: 2px 4px;
                margin: 0 1px;
                border-radius: 3px;
                cursor: help;
                position: relative;
                display: inline;
            }
            .code-label {
                font-weight: bold;
                font-size: 0.85em;
                margin-left: 3px;
                padding: 1px 4px;
                border-radius: 2px;
                color: #333;
                background-color: rgba(255, 255, 255, 0.7);
                border: 1px solid #999;
            }
            .legend {
                margin: 20px 0;
                padding: 15px;
                background-color: #e8f5e9;
                border-radius: 5px;
            }
            .legend h3 {
                margin-top: 0;
                color: #2E7D32;
            }
            .legend-item {
                display: inline-block;
                margin: 5px 10px 5px 0;
                padding: 5px 10px;
                border-radius: 3px;
                font-weight: bold;
            }
            .text-content {
                margin-top: 30px;
                white-space: pre-wrap;
                word-wrap: break-word;
                font-size: 11pt;
                background-color: #fafafa;
                padding: 20px;
                border-radius: 5px;
                border: 1px solid #ddd;
            }
            /* Hidden annotation metadata for import */
            .annotation-data {
                display: none;
            }
        </style>
    </head>
    <body>
        <h1>📄 Annotated Text</h1>
        
        <div class="metadata">
            <strong>Export Date:</strong> """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """<br>
            <strong>Total Annotations:</strong> """ + str(len(self.annotation_manager.annotations)) + """<br>
            <strong>Unique Codes:</strong> """ + str(len(self.annotation_manager.codes)) + """
        </div>
        
        <div class="legend">
            <h3>📊 Code Legend</h3>
    """
        
        # Add legend items
        for code in sorted(self.annotation_manager.codes):
            color = self.annotation_manager.code_colors.get(code, '#FFFF00')
            count = len([a for a in self.annotation_manager.annotations if a.code == code])
            html += f'        <span class="legend-item" style="background-color:{color};">{html_module.escape(code)} ({count})</span>\n'
        
        html += """    </div>
        
        <!-- Hidden annotation metadata for round-trip import -->
        <div class="annotation-data" id="voxscribe-annotations">
            <script type="application/json">
    """
        
        # Add JSON metadata for perfect round-trip
        annotations_data = []
        for ann in sorted(self.annotation_manager.annotations, key=lambda a: a.start):
            annotations_data.append({
                'start': ann.start,
                'end': ann.end,
                'text': ann.text,
                'code': ann.code,
                'memo': ann.memo,
                'color': self.annotation_manager.code_colors.get(ann.code, '#FFFFFF')
            })
        
        html += json.dumps(annotations_data, indent=2, ensure_ascii=False)
        
        html += """
            </script>
        </div>
        
        <div class="text-content">
    """
        
        # Build annotated text (same as before)
        sorted_anns = sorted(self.annotation_manager.annotations, key=lambda a: (a.start, a.end))
        segments = []
        
        covered_ranges = set()
        
        for ann in sorted_anns:
            segments.append({
                'start': ann.start,
                'end': ann.end,
                'text': ann.text,
                'annotation': ann,
                'is_annotation': True
            })
            for i in range(ann.start, ann.end):
                covered_ranges.add(i)
        
        if self.current_text:
            last_pos = 0
            for ann in sorted_anns:
                if ann.start > last_pos:
                    segments.append({
                        'start': last_pos,
                        'end': ann.start,
                        'text': self.current_text[last_pos:ann.start],
                        'annotation': None,
                        'is_annotation': False
                    })
                last_pos = max(last_pos, ann.end)
            
            if last_pos < len(self.current_text):
                segments.append({
                    'start': last_pos,
                    'end': len(self.current_text),
                    'text': self.current_text[last_pos:],
                    'annotation': None,
                    'is_annotation': False
                })
        
        segments.sort(key=lambda s: (s['start'], -s['end'] if s['is_annotation'] else 0))
        
        last_end = 0
        for segment in segments:
            if segment['start'] < last_end:
                if segment['is_annotation']:
                    pass
                else:
                    continue
            
            if segment['is_annotation']:
                ann = segment['annotation']
                color = self.annotation_manager.code_colors.get(ann.code, '#FFFF00')
                
                tooltip = f"Code: {html_module.escape(ann.code)}"
                if ann.memo:
                    tooltip += f" | Memo: {html_module.escape(ann.memo)}"
                
                # Add data attributes for position info
                html += f'<span class="annotation" style="background-color:{color};" title="{html_module.escape(tooltip)}" data-start="{ann.start}" data-end="{ann.end}">'
                html += html_module.escape(segment['text'])
                html += f' <span class="code-label">[{html_module.escape(ann.code)}]</span></span>'
                
                last_end = segment['end']
            else:
                html += html_module.escape(segment['text'])
                last_end = segment['end']
        
        html += """    </div>
        
        <div style="margin-top: 30px; padding: 15px; background-color: #fff3cd; border-radius: 5px; border-left: 4px solid #ffc107;">
            <strong>ℹ️ Note:</strong> Hover over highlighted text to see code details and memos.
            This file contains embedded annotation data for re-import into VoxScribe.
        </div>
    </body>
    </html>"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)


    def _format_srt_timestamp(self, seconds):
        """Format timestamp for SRT format (HH:MM:SS,mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


    def _format_vtt_timestamp(self, seconds):
        """Format timestamp for VTT format (HH:MM:SS.mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"
    
    # ===== Codebook Methods =====
    
    def create_codebook_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        toolbar = QHBoxLayout()
        
        add_btn = QPushButton("Add Code")
        add_btn.clicked.connect(self.add_code_dialog)
        toolbar.addWidget(add_btn)
        
        rename_btn = QPushButton("Rename")
        rename_btn.clicked.connect(self.rename_code_dialog)
        toolbar.addWidget(rename_btn)
        
        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(self.delete_code_dialog)
        toolbar.addWidget(delete_btn)
        
        merge_btn = QPushButton("Merge Codes")
        merge_btn.clicked.connect(self.merge_codes_dialog)
        toolbar.addWidget(merge_btn)
        
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        self.codebook_table = QTableWidget()
        self.codebook_table.setColumnCount(4)
        self.codebook_table.setHorizontalHeaderLabels(["Code", "Usage Count", "Color", "Description"])
        self.codebook_table.horizontalHeader().setStretchLastSection(True)
        self.codebook_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        # Enable sorting - this allows clicking column headers to sort
        self.codebook_table.setSortingEnabled(True)
        
        # Track current sort state for custom behavior
        self.codebook_sort_column = 0  # Default: Code column
        self.codebook_sort_ascending = True  # Default: A-Z
        
        # Connect header click to custom sort handler
        self.codebook_table.horizontalHeader().sectionClicked.connect(self.sort_codebook_table)
        
        layout.addWidget(self.codebook_table)
        
        stats_layout = QHBoxLayout()
        self.code_stats_label = QLabel("Total codes: 0 | Total annotations: 0")
        stats_layout.addWidget(self.code_stats_label)
        stats_layout.addStretch()
        layout.addLayout(stats_layout)
        
        return widget
    
    def update_codebook_table(self):
        """Update codebook table with optimized usage count calculation"""
        # Temporarily disable sorting while updating to avoid performance issues
        self.codebook_table.setSortingEnabled(False)
        
        self.codebook_table.setRowCount(0)
        
        # OPTIMIZATION: Pre-calculate all usage counts in single pass
        usage_counts = {}
        for ann in self.annotation_manager.annotations:
            usage_counts[ann.code] = usage_counts.get(ann.code, 0) + 1
        
        codes = sorted(self.annotation_manager.codes)
        for code in codes:
            row = self.codebook_table.rowCount()
            self.codebook_table.insertRow(row)
            
            # Code name column
            self.codebook_table.setItem(row, 0, QTableWidgetItem(code))
            
            # Usage count column - use pre-calculated count
            usage = usage_counts.get(code, 0)
            usage_item = QTableWidgetItem()
            usage_item.setData(Qt.ItemDataRole.DisplayRole, usage)  # Store as integer
            self.codebook_table.setItem(row, 1, usage_item)
            
            # Color column
            color = self.annotation_manager.code_colors.get(code, '#FFFFFF')
            color_item = QTableWidgetItem()
            color_item.setBackground(QColor(color))
            self.codebook_table.setItem(row, 2, color_item)
            
            # Description column
            self.codebook_table.setItem(row, 3, QTableWidgetItem(""))
        
        # Re-enable sorting and apply current sort
        self.codebook_table.setSortingEnabled(True)
        
        # Apply the current sort order
        if hasattr(self, 'codebook_sort_column'):
            sort_order = Qt.SortOrder.AscendingOrder if self.codebook_sort_ascending else Qt.SortOrder.DescendingOrder
            self.codebook_table.sortItems(self.codebook_sort_column, sort_order)
        
        total_codes = len(self.annotation_manager.codes)
        total_annotations = len(self.annotation_manager.annotations)
        self.code_stats_label.setText(f"Total codes: {total_codes} | Total annotations: {total_annotations}")
    
    def sort_codebook_table(self, column):
        """
        Handle column header clicks to sort the codebook table
        
        Args:
            column: The column index that was clicked (0=Code, 1=Usage Count, etc.)
        """
        # If clicking the same column, toggle sort order
        if column == self.codebook_sort_column:
            self.codebook_sort_ascending = not self.codebook_sort_ascending
        else:
            # New column - default to ascending for Code, descending for Usage Count
            self.codebook_sort_column = column
            if column == 1:  # Usage Count column - default to descending (most-used first)
                self.codebook_sort_ascending = False
            else:  # Code column or others - default to ascending (A-Z)
                self.codebook_sort_ascending = True
        
        # Apply the sort
        sort_order = Qt.SortOrder.AscendingOrder if self.codebook_sort_ascending else Qt.SortOrder.DescendingOrder
        self.codebook_table.sortItems(column, sort_order)
    
    def add_code_dialog(self):
        code, ok = QInputDialog.getText(self, "Add Code", "Enter code name:")
        if ok and code:
            self.annotation_manager.codes.add(code)
            color_idx = len(self.annotation_manager.code_colors) % len(self.annotation_manager.color_palette)
            self.annotation_manager.code_colors[code] = self.annotation_manager.color_palette[color_idx]
            # Optimized: Only update codebook and dropdown, not records or theme
            self.update_all_displays(update_codebook=True, update_records=False, update_theme=False, update_dropdown=True)
    
    def rename_code_dialog(self):
        selected = self.codebook_table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Warning", "Select a code first")
            return
        
        old_code = self.codebook_table.item(selected, 0).text()
        new_code, ok = QInputDialog.getText(self, "Rename Code", "New name:", text=old_code)
        
        if ok and new_code and new_code != old_code:
            for ann in self.annotation_manager.annotations:
                if ann.code == old_code:
                    ann.code = new_code
            
            self.annotation_manager.codes.discard(old_code)
            self.annotation_manager.codes.add(new_code)
            
            if old_code in self.annotation_manager.code_colors:
                self.annotation_manager.code_colors[new_code] = \
                    self.annotation_manager.code_colors[old_code]
                del self.annotation_manager.code_colors[old_code]
            
            # Optimized: Update all except theme tree
            self.update_all_displays(update_codebook=True, update_records=True, update_theme=False, update_dropdown=True)
            self.refresh_text_display()
            self.ensure_no_selection()
    
    def delete_code_dialog(self):
        selected = self.codebook_table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Warning", "Select a code first")
            return
        
        code = self.codebook_table.item(selected, 0).text()
        reply = QMessageBox.question(
            self, "Delete Code",
            f"Delete '{code}' and all its annotations?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.annotation_manager.annotations = [
                a for a in self.annotation_manager.annotations if a.code != code
            ]
            self.annotation_manager.codes.discard(code)
            if code in self.annotation_manager.code_colors:
                del self.annotation_manager.code_colors[code]
            
            # Optimized: Update all except theme tree
            self.update_all_displays(update_codebook=True, update_records=True, update_theme=False, update_dropdown=True)
            self.refresh_text_display()
            self.ensure_no_selection()
    
    def merge_codes_dialog(self):
        codes = list(self.annotation_manager.codes)
        if len(codes) < 2:
            QMessageBox.warning(self, "Warning", "Need at least 2 codes to merge")
            return
        
        dialog = MergeCodesDialog(codes, self)
        result = dialog.exec()
        
        if result == QDialog.DialogCode.Accepted or result == 1:
            old_codes = dialog.get_selected_codes()
            new_code = dialog.get_new_code_name()
            
            if old_codes and new_code:
                self.annotation_manager.merge_codes(old_codes, new_code)
                self.update_all_displays()
                self.refresh_text_display()
                self.ensure_no_selection()
                self.code_status_label.setText(f"✓ {len(old_codes)} codes merged into '{new_code}'")
                self.code_status_label.setStyleSheet("color: #2E7D32; font-weight: bold; padding: 5px;")
                QMessageBox.information(self, "Success", f"Merged {len(old_codes)} codes into '{new_code}'")
    
    # ===== Themes Methods =====
    
    def create_themes_tab(self):
        """Create themes tab with drag-and-drop support"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        toolbar = QHBoxLayout()
        toolbar.setSpacing(5)
        
        add_theme_btn = QPushButton("Add Theme")
        add_theme_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogNewFolder))
        add_theme_btn.setToolTip("Add a new theme to organize your codes")
        add_theme_btn.clicked.connect(self.add_theme_dialog)
        toolbar.addWidget(add_theme_btn)
        
        add_subtheme_btn = QPushButton("Add Sub-Theme")
        add_subtheme_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView))
        add_subtheme_btn.setToolTip("Add a sub-theme under the selected theme")
        add_subtheme_btn.clicked.connect(self.add_subtheme_dialog)
        toolbar.addWidget(add_subtheme_btn)
        
        add_code_to_theme_btn = QPushButton("Link Code to Theme")
        add_code_to_theme_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowRight))
        add_code_to_theme_btn.setToolTip("Link an existing code to selected theme")
        add_code_to_theme_btn.clicked.connect(self.add_code_to_theme_dialog)
        toolbar.addWidget(add_code_to_theme_btn)
        
        delete_theme_btn = QPushButton("Delete Selected")
        delete_theme_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_TrashIcon))
        delete_theme_btn.setToolTip("Delete selected theme or code link")
        delete_theme_btn.clicked.connect(self.delete_theme_item)
        toolbar.addWidget(delete_theme_btn)
        
        toolbar.addStretch()
        
        export_hierarchy_btn = QPushButton("Export")
        export_hierarchy_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton))
        export_hierarchy_btn.clicked.connect(self.export_hierarchy)
        toolbar.addWidget(export_hierarchy_btn)
        
        import_hierarchy_btn = QPushButton("Import")
        import_hierarchy_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogOpenButton))
        import_hierarchy_btn.clicked.connect(self.import_hierarchy)
        toolbar.addWidget(import_hierarchy_btn)
        
        layout.addLayout(toolbar)
        
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        tree_widget = QWidget()
        tree_layout = QVBoxLayout(tree_widget)
        
        tree_header_layout = QHBoxLayout()
        tree_header_layout.addWidget(QLabel("<b>Theme & Code Hierarchy</b>"))
        tree_header_layout.addStretch()
        
        # Add drag-drop info label
        dragdrop_info = QLabel("💡 Drag items to reorganize")
        dragdrop_info.setStyleSheet("color: #666; font-style: italic; font-size: 10pt;")
        tree_header_layout.addWidget(dragdrop_info)
        
        expand_all_btn = QPushButton("Expand All")
        expand_all_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarMaxButton))
        expand_all_btn.clicked.connect(lambda: self.theme_tree.expandAll())
        tree_header_layout.addWidget(expand_all_btn)
        
        collapse_all_btn = QPushButton("Collapse All")
        collapse_all_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarMinButton))
        collapse_all_btn.clicked.connect(lambda: self.theme_tree.collapseAll())
        tree_header_layout.addWidget(collapse_all_btn)
        tree_layout.addLayout(tree_header_layout)
        
        # Create tree widget with drag-drop enabled
        self.theme_tree = QTreeWidget()
        self.theme_tree.setHeaderLabel("Themes and Codes")
        self.theme_tree.itemClicked.connect(self.on_theme_item_clicked)
        self.theme_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        
        # Enable drag and drop
        self.theme_tree.setDragEnabled(True)
        self.theme_tree.setAcceptDrops(True)
        self.theme_tree.setDropIndicatorShown(True)
        self.theme_tree.setDragDropMode(QTreeWidget.DragDropMode.InternalMove)
        
        # Connect drag-drop signals
        self.theme_tree.model().rowsMoved.connect(self.on_theme_tree_rows_moved)
        
        tree_layout.addWidget(self.theme_tree)
        
        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)
        details_layout.addWidget(QLabel("<b>Selected Item Details</b>"))
        
        self.theme_details = QTextEdit()
        self.theme_details.setReadOnly(True)
        self.theme_details.setPlaceholderText("Select a theme or code to view details...")
        details_layout.addWidget(self.theme_details)
        
        splitter.addWidget(tree_widget)
        splitter.addWidget(details_widget)
        splitter.setSizes([600, 400])
        
        layout.addWidget(splitter)
        
        return widget
    
    def update_theme_tree(self):
        """Update theme tree with performance optimization"""
        # Disable updates during tree rebuild
        self.theme_tree.setUpdatesEnabled(False)
        try:
            self.theme_tree.clear()
            
            for child in self.annotation_manager.theme_root.children:
                self._add_node_to_tree_recursive(child, None)
            
            self.theme_tree.expandAll()
        finally:
            self.theme_tree.setUpdatesEnabled(True)
    
    def _add_node_to_tree_recursive(self, node, parent_item):
        if parent_item is None:
            item = QTreeWidgetItem(self.theme_tree)
        else:
            item = QTreeWidgetItem(parent_item)
        
        icon = "📁" if node.type == "theme" else "📄"
        item.setText(0, f"{icon} {node.name}")
        
        item.setData(0, Qt.ItemDataRole.UserRole, node)
        
        for child in node.children:
            self._add_node_to_tree_recursive(child, item)
        
        return item
    
    def on_theme_item_clicked(self, item, column):
        node = item.data(0, Qt.ItemDataRole.UserRole)
        if node:
            details = f"Name: {node.name}\n"
            details += f"Type: {node.type}\n"
            details += f"Description: {node.description}\n"
            details += f"Created: {node.created.strftime('%Y-%m-%d %H:%M')}\n"
            details += f"Children: {len(node.children)}\n"
            
            if node.type == "code":
                usage = len(self.annotation_manager.get_annotations_for_code(node.name))
                details += f"Usage: {usage} annotations\n"
            
            self.theme_details.setPlainText(details)
    
    def add_theme_dialog(self):
        name, ok = QInputDialog.getText(self, "Add Theme", "Theme name:")
        if ok and name:
            description, ok2 = QInputDialog.getText(self, "Add Theme", "Description (optional):")
            if ok2 is not False:
                theme = ThemeNode(name, "theme", description or "")
                self.annotation_manager.theme_root.add_child(theme)
                self.update_theme_tree()
                QMessageBox.information(self, "Success", f"Theme '{name}' added successfully!")
    
    def add_subtheme_dialog(self):
        selected_item = self.theme_tree.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Warning", "Please select a theme first")
            return
        
        parent_node = selected_item.data(0, Qt.ItemDataRole.UserRole)
        if parent_node.type != "theme":
            QMessageBox.warning(self, "Warning", "Can only add sub-themes under themes, not codes")
            return
        
        name, ok = QInputDialog.getText(self, "Add Sub-Theme", f"Sub-theme name (under '{parent_node.name}'):")
        if ok and name:
            description, ok2 = QInputDialog.getText(self, "Add Sub-Theme", "Description (optional):")
            if ok2 is not False:
                subtheme = ThemeNode(name, "theme", description or "")
                parent_node.add_child(subtheme)
                self.update_theme_tree()
                QMessageBox.information(self, "Success", f"Sub-theme '{name}' added under '{parent_node.name}'!")
    
    def add_code_to_theme_dialog(self):
        selected_item = self.theme_tree.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Warning", "Please select a theme first")
            return
        
        parent_node = selected_item.data(0, Qt.ItemDataRole.UserRole)
        if parent_node.type != "theme":
            QMessageBox.warning(self, "Warning", "Can only link codes to themes, not to other codes")
            return
        
        codes = list(self.annotation_manager.codes)
        if not codes:
            QMessageBox.warning(self, "Warning", "No codes available. Create some codes first.")
            return
        
        code, ok = QInputDialog.getItem(self, "Link Code to Theme", 
                                         f"Select code to link to '{parent_node.name}':", 
                                         sorted(codes), 0, False)
        if ok and code:
            code_node = ThemeNode(code, "code", f"Linked code: {code}")
            parent_node.add_child(code_node)
            self.update_theme_tree()
            QMessageBox.information(self, "Success", f"Code '{code}' linked to theme '{parent_node.name}'!")
    
    def delete_theme_item(self):
        selected_item = self.theme_tree.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Warning", "Please select an item to delete")
            return
        
        node = selected_item.data(0, Qt.ItemDataRole.UserRole)
        
        reply = QMessageBox.question(
            self, "Delete Item",
            f"Delete '{node.name}' and all its children?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if node.parent:
                node.parent.remove_child(node)
                self.update_theme_tree()
                QMessageBox.information(self, "Success", f"'{node.name}' deleted successfully!")
            else:
                QMessageBox.warning(self, "Warning", "Cannot delete root item")
    
    def on_theme_tree_rows_moved(self, parent, start, end, destination, row):
        """
        Handle rows moved in theme tree (drag-drop operation)
        
        This updates the internal data structure to match the new tree organization
        """
        # Use QTimer to delay processing until after Qt finishes the move
        QTimer.singleShot(100, self.sync_theme_tree_to_data)


    # Add this new method to sync tree to data structure
    def sync_theme_tree_to_data(self):
        """
        Synchronize the theme data structure with the current tree widget state
        
        This rebuilds the internal hierarchy based on the visual tree after drag-drop
        """
        # Clear existing hierarchy (keep root)
        self.annotation_manager.theme_root.children.clear()
        
        # Rebuild from tree widget
        root = self.theme_tree.invisibleRootItem()
        
        for i in range(root.childCount()):
            item = root.child(i)
            node = self._rebuild_node_from_tree_item(item)
            if node:
                self.annotation_manager.theme_root.add_child(node)
        
        # Show confirmation
        self.theme_details.setPlainText("✓ Hierarchy reorganized successfully!")


    # Add this new method to rebuild nodes from tree items
    def _rebuild_node_from_tree_item(self, item):
        """
        Recursively rebuild ThemeNode structure from QTreeWidgetItem
        
        Args:
            item: QTreeWidgetItem to convert
            
        Returns:
            ThemeNode corresponding to the item
        """
        # Get the original node data
        old_node = item.data(0, Qt.ItemDataRole.UserRole)
        
        if not old_node:
            return None
        
        # Create new node with same properties
        new_node = ThemeNode(
            old_node.name,
            old_node.type,
            old_node.description
        )
        new_node.created = old_node.created
        
        # Recursively add children
        for i in range(item.childCount()):
            child_item = item.child(i)
            child_node = self._rebuild_node_from_tree_item(child_item)
            if child_node:
                new_node.add_child(child_node)
        
        return new_node


    # Add validation method to prevent invalid drops
    def _is_valid_drop(self, dragged_node, target_node):
        """
        Check if dropping dragged_node onto target_node is valid
        
        Rules:
        - Codes can only be dropped on themes
        - Themes can be dropped on themes (to create sub-themes)
        - Cannot drop a theme onto itself or its descendants
        
        Args:
            dragged_node: The node being dragged
            target_node: The node being dropped onto
            
        Returns:
            bool: True if drop is valid, False otherwise
        """
        if not dragged_node or not target_node:
            return False
        
        # Codes can only be dropped on themes
        if dragged_node.type == "code" and target_node.type != "theme":
            return False
        
        # Cannot drop a theme onto itself
        if dragged_node == target_node:
            return False
        
        # Cannot drop a theme onto its own descendant
        if dragged_node.type == "theme":
            current = target_node
            while current:
                if current == dragged_node:
                    return False
                current = current.parent
        
        return True
    
    def export_hierarchy(self):
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export Hierarchy", "", "JSON Files (*.json)"
        )
        if filepath:
            data = self.annotation_manager.theme_root.to_dict()
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            QMessageBox.information(self, "Success", "Hierarchy exported")
    
    def import_hierarchy(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Import Hierarchy", "", "JSON Files (*.json)"
        )
        if filepath:
            with open(filepath, 'r') as f:
                data = json.load(f)
            self.annotation_manager.theme_root = ThemeNode.from_dict(data)
            self.update_theme_tree()
            QMessageBox.information(self, "Success", "Hierarchy imported")
    
    # ===== Analysis Methods =====
    
    def create_analysis_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        toolbar = QHBoxLayout()
        
        freq_btn = QPushButton("Code Frequency")
        freq_btn.clicked.connect(self.show_code_frequency)
        toolbar.addWidget(freq_btn)
        
        cooccur_btn = QPushButton("Co-occurrence")
        cooccur_btn.clicked.connect(self.show_code_cooccurrence)
        toolbar.addWidget(cooccur_btn)
        
        summary_btn = QPushButton("Text Summary")
        summary_btn.clicked.connect(self.show_text_summary)
        toolbar.addWidget(summary_btn)
        
        # ADD THIS NEW BUTTON:
        coverage_btn = QPushButton("Coverage Analysis")
        coverage_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogContentsView))
        coverage_btn.setToolTip("Analyze document coverage and identify gaps")
        coverage_btn.clicked.connect(self.show_coverage_analysis)
        toolbar.addWidget(coverage_btn)
        
        toolbar.addStretch()
        
        toolbar.addWidget(QLabel("Unit:"))
        self.cooccur_unit = QComboBox()
        self.cooccur_unit.addItems(["Paragraph", "Sentence", "Document"])
        toolbar.addWidget(self.cooccur_unit)
        
        layout.addLayout(toolbar)
        
        self.analysis_figure = Figure(figsize=(10, 6))
        self.analysis_canvas = FigureCanvasQTAgg(self.analysis_figure)
        layout.addWidget(self.analysis_canvas)
        
        self.analysis_results = QTextEdit()
        self.analysis_results.setReadOnly(True)
        self.analysis_results.setMaximumHeight(200)
        layout.addWidget(self.analysis_results)
        
        return widget
    
    def show_code_frequency(self):
        if not self.annotation_manager.annotations:
            QMessageBox.warning(self, "Warning", "No annotations")
            return
        
        code_counts = Counter(a.code for a in self.annotation_manager.annotations)
        
        self.analysis_figure.clear()
        ax = self.analysis_figure.add_subplot(111)
        
        codes = list(code_counts.keys())
        counts = list(code_counts.values())
        colors = [self.annotation_manager.code_colors.get(c, '#CCCCCC') for c in codes]
        
        ax.bar(range(len(codes)), counts, color=colors, edgecolor='black')
        ax.set_xticks(range(len(codes)))
        ax.set_xticklabels(codes, rotation=45, ha='right')
        ax.set_title('Code Frequency')
        ax.set_ylabel('Count')
        ax.set_xlabel('Code')
        
        self.analysis_figure.tight_layout()
        self.analysis_canvas.draw()
        
        summary = "Code Frequency Summary\n\n"
        for code, count in code_counts.most_common():
            pct = (count / len(self.annotation_manager.annotations)) * 100
            summary += f"{code}: {count} ({pct:.1f}%)\n"
        
        self.analysis_results.setPlainText(summary)
    
    def show_code_cooccurrence(self):
        if len(self.annotation_manager.annotations) < 2:
            QMessageBox.warning(self, "Warning", "Need at least 2 annotations")
            return
        
        codes = list(self.annotation_manager.codes)
        n = len(codes)
        cooccur = np.zeros((n, n))
        
        # Get the selected unit
        unit = self.cooccur_unit.currentText()
        
        # Build unit boundaries based on text structure
        unit_boundaries = []
        
        if unit == "Paragraph":
            # Find paragraph boundaries (separated by empty lines: \n\n)
            current_pos = 0
            para_start = 0
            
            # Split and track actual positions
            lines = self.current_text.split('\n')
            current_line_pos = 0
            in_paragraph = False
            para_start = 0
            
            for i, line in enumerate(lines):
                line_length = len(line) + 1  # +1 for the \n character
                
                if line.strip():  # Non-empty line
                    if not in_paragraph:
                        para_start = current_line_pos
                        in_paragraph = True
                else:  # Empty line - end of paragraph
                    if in_paragraph:
                        # Store paragraph boundary
                        unit_boundaries.append((para_start, current_line_pos))
                        in_paragraph = False
                
                current_line_pos += line_length
            
            # Don't forget the last paragraph if text doesn't end with empty line
            if in_paragraph:
                unit_boundaries.append((para_start, len(self.current_text)))
        
        elif unit == "Sentence":
            # Find sentence boundaries (ending with . ! ? followed by space or newline)
            import re
            sentence_start = 0
            
            # Pattern for sentence endings: . ! or ? followed by whitespace or end of string
            pattern = r'[.!?]+[\s\n]+'
            
            for match in re.finditer(pattern, self.current_text):
                sentence_end = match.end()
                unit_boundaries.append((sentence_start, sentence_end))
                sentence_start = sentence_end
            
            # Add the last sentence if it doesn't end with punctuation
            if sentence_start < len(self.current_text):
                unit_boundaries.append((sentence_start, len(self.current_text)))
        
        elif unit == "Document":
            # Entire document is one unit
            unit_boundaries = [(0, len(self.current_text))]
        
        # Count co-occurrences based on which annotations fall in the same unit
        units_analyzed = len(unit_boundaries)
        
        for start, end in unit_boundaries:
            # Find all annotations that fall within this unit
            codes_in_unit = set()
            
            for ann in self.annotation_manager.annotations:
                # Check if annotation is within this unit
                # Annotation is in unit if its midpoint falls within the unit boundaries
                # OR if it starts within the unit OR if it ends within the unit
                ann_start = ann.start
                ann_end = ann.end
                
                # Use midpoint for primary check (most accurate)
                ann_midpoint = (ann_start + ann_end) / 2
                
                if start <= ann_midpoint < end:
                    codes_in_unit.add(ann.code)
            
            # Count co-occurrences for codes that appear together in this unit
            if len(codes_in_unit) >= 2:
                codes_list = list(codes_in_unit)
                for i, c1 in enumerate(codes):
                    for j, c2 in enumerate(codes):
                        if i < j and c1 in codes_in_unit and c2 in codes_in_unit:
                            cooccur[i, j] += 1
                            cooccur[j, i] += 1
        
        # Create the network graph
        self.analysis_figure.clear()
        
        G = nx.Graph()
        node_colors = []
        for i, code in enumerate(codes):
            G.add_node(code)
            node_colors.append(self.annotation_manager.code_colors.get(code, '#CCCCCC'))
        
        # Add edges with weights
        edge_weights = []
        for i in range(n):
            for j in range(i+1, n):
                if cooccur[i, j] > 0:
                    G.add_edge(codes[i], codes[j], weight=cooccur[i, j])
                    edge_weights.append(cooccur[i, j])
        
        ax = self.analysis_figure.add_subplot(111)
        
        if G.number_of_edges() > 0:
            # Use spring layout for better visualization
            pos = nx.spring_layout(G, k=1.5, iterations=50, seed=42)
            
            # Draw nodes
            nx.draw_networkx_nodes(G, pos, node_color=node_colors,
                                node_size=1200, ax=ax, alpha=0.9,
                                edgecolors='black', linewidths=2)
            
            # Draw edges with varying thickness based on weight
            edges = G.edges()
            weights = [G[u][v]['weight'] for u, v in edges]
            max_weight = max(weights) if weights else 1
            
            # Normalize edge widths (1 to 6)
            edge_widths = [1 + (w / max_weight) * 5 for w in weights]
            
            nx.draw_networkx_edges(G, pos, width=edge_widths, 
                                alpha=0.6, edge_color='#555555', ax=ax)
            
            # Draw labels
            nx.draw_networkx_labels(G, pos, font_size=10, 
                                font_weight='bold', ax=ax)
            
            # Add edge labels showing co-occurrence count
            edge_labels = {(u, v): int(G[u][v]['weight']) for u, v in edges}
            nx.draw_networkx_edge_labels(G, pos, edge_labels, 
                                        font_size=9, font_weight='bold',
                                        bbox=dict(boxstyle='round,pad=0.3', 
                                                facecolor='white', 
                                                edgecolor='gray', alpha=0.8),
                                        ax=ax)
        else:
            # No co-occurrences found
            ax.text(0.5, 0.5, f'No co-occurrences found\nat {unit} level\n\n' + 
                'Codes must appear in the same\n' + 
                f'{unit.lower()} to co-occur.',
                ha='center', va='center', fontsize=12, color='#666',
                transform=ax.transAxes,
                bbox=dict(boxstyle='round,pad=1', facecolor='#f0f0f0', alpha=0.8))
        
        ax.set_title(f'Code Co-occurrence Network ({unit} Level)', fontsize=14, fontweight='bold')
        ax.axis('off')
        self.analysis_figure.tight_layout()
        self.analysis_canvas.draw()
        
        # Generate detailed summary
        summary = f"Co-occurrence Summary ({unit} Level)\n"
        summary += "=" * 50 + "\n\n"
        summary += f"Analysis Unit: {unit}\n"
        summary += f"Number of {unit.lower()}s analyzed: {units_analyzed}\n"
        summary += f"Total codes: {len(codes)}\n"
        summary += f"Total annotations: {len(self.annotation_manager.annotations)}\n"
        summary += f"Co-occurrence instances: {int(np.sum(cooccur) / 2)}\n\n"
        
        # Show most frequent co-occurrences
        cooccur_pairs = []
        for i in range(n):
            for j in range(i+1, n):
                if cooccur[i, j] > 0:
                    cooccur_pairs.append((codes[i], codes[j], int(cooccur[i, j])))
        
        if cooccur_pairs:
            summary += f"Code Pairs that Co-occur:\n"
            summary += "-" * 50 + "\n"
            cooccur_pairs.sort(key=lambda x: x[2], reverse=True)
            
            for idx, (c1, c2, count) in enumerate(cooccur_pairs, 1):
                pct = (count / units_analyzed) * 100
                summary += f"{idx}. {c1} ↔ {c2}: {count} times ({pct:.1f}% of {unit.lower()}s)\n"
        else:
            summary += f"No code pairs co-occur in the same {unit.lower()}.\n"
            summary += f"\nThis means no two codes appear together within\n"
            summary += f"any single {unit.lower()} in your text.\n"
        
        # Calculate co-occurrence statistics
        if len(cooccur_pairs) > 0:
            avg_cooccur = sum(p[2] for p in cooccur_pairs) / len(cooccur_pairs)
            max_cooccur = max(p[2] for p in cooccur_pairs)
            min_cooccur = min(p[2] for p in cooccur_pairs)
            
            summary += f"\n" + "=" * 50 + "\n"
            summary += f"Statistics:\n"
            summary += f"  • Unique code pairs: {len(cooccur_pairs)}\n"
            summary += f"  • Average co-occurrence: {avg_cooccur:.1f}\n"
            summary += f"  • Maximum co-occurrence: {max_cooccur}\n"
            summary += f"  • Minimum co-occurrence: {min_cooccur}\n"
            
            # Network density
            possible_pairs = (n * (n - 1)) / 2
            density = len(cooccur_pairs) / possible_pairs if possible_pairs > 0 else 0
            summary += f"  • Network density: {density:.2%}\n"
        
        self.analysis_results.setPlainText(summary)
    
    def show_text_summary(self):
        if not self.current_text:
            QMessageBox.warning(self, "Warning", "No text")
            return
        
        words = len(self.current_text.split())
        chars = len(self.current_text)
        paragraphs = len([p for p in self.current_text.split('\n\n') if p.strip()])
        
        summary = f"Text Summary\n\n"
        summary += f"Words: {words:,}\n"
        summary += f"Characters: {chars:,}\n"
        summary += f"Paragraphs: {paragraphs}\n"
        summary += f"Annotations: {len(self.annotation_manager.annotations)}\n"
        summary += f"Unique Codes: {len(self.annotation_manager.codes)}\n"
        
        if self.annotation_manager.annotations:
            avg_annotation_length = sum(len(a.text) for a in self.annotation_manager.annotations) / len(self.annotation_manager.annotations)
            summary += f"Average Annotation Length: {avg_annotation_length:.1f} characters\n"
        
        self.analysis_results.setPlainText(summary)
        
        self.analysis_figure.clear()
        self.analysis_canvas.draw()

    def show_coverage_analysis(self):
        """
        Analyze and visualize document coverage by annotations
        Shows: 
        1. Percentage of document covered by at least one code
        2. Regions with multiple overlapping codes (intensive coding)
        3. Regions with no coding (potential gaps in analysis)
        """
        if not self.current_text:
            QMessageBox.warning(self, "Warning", "No text loaded")
            return
        
        if not self.annotation_manager.annotations:
            QMessageBox.warning(self, "Warning", "No annotations to analyze")
            return
        
        # Calculate coverage metrics
        text_length = len(self.current_text)
        
        # Create a coverage array: count how many codes cover each character position
        coverage_array = np.zeros(text_length, dtype=np.int32)
        
        for ann in self.annotation_manager.annotations:
            start = max(0, ann.start)
            end = min(text_length, ann.end)
            coverage_array[start:end] += 1
        
        # Analyze coverage
        uncoded_positions = np.sum(coverage_array == 0)
        single_coded_positions = np.sum(coverage_array == 1)
        multi_coded_positions = np.sum(coverage_array > 1)
        
        coverage_percentage = ((text_length - uncoded_positions) / text_length) * 100
        
        # Find uncoded regions (gaps)
        uncoded_regions = []
        in_gap = False
        gap_start = 0
        
        for i in range(text_length):
            if coverage_array[i] == 0 and not in_gap:
                in_gap = True
                gap_start = i
            elif coverage_array[i] > 0 and in_gap:
                in_gap = False
                gap_length = i - gap_start
                if gap_length > 50:  # Only report gaps larger than 50 characters
                    gap_text = self.current_text[gap_start:i].strip()
                    # Get context: 30 chars before and after
                    context_start = max(0, gap_start - 30)
                    context_end = min(text_length, i + 30)
                    context = self.current_text[context_start:context_end]
                    uncoded_regions.append({
                        'start': gap_start,
                        'end': i,
                        'length': gap_length,
                        'text': gap_text[:100],  # First 100 chars
                        'context': context
                    })
        
        # Handle if document ends with a gap
        if in_gap and (text_length - gap_start) > 50:
            gap_text = self.current_text[gap_start:].strip()
            context_start = max(0, gap_start - 30)
            context = self.current_text[context_start:]
            uncoded_regions.append({
                'start': gap_start,
                'end': text_length,
                'length': text_length - gap_start,
                'text': gap_text[:100],
                'context': context
            })
        
        # Find intensively coded regions (3+ overlapping codes)
        intensive_regions = []
        in_intensive = False
        intensive_start = 0
        
        for i in range(text_length):
            if coverage_array[i] >= 3 and not in_intensive:
                in_intensive = True
                intensive_start = i
            elif coverage_array[i] < 3 and in_intensive:
                in_intensive = False
                intensive_length = i - intensive_start
                if intensive_length > 20:  # Only report regions larger than 20 characters
                    intensive_text = self.current_text[intensive_start:i].strip()
                    max_overlap = np.max(coverage_array[intensive_start:i])
                    intensive_regions.append({
                        'start': intensive_start,
                        'end': i,
                        'length': intensive_length,
                        'max_overlap': int(max_overlap),
                        'text': intensive_text[:100]
                    })
        
        # Handle if document ends in intensive region
        if in_intensive and (text_length - intensive_start) > 20:
            intensive_text = self.current_text[intensive_start:].strip()
            max_overlap = np.max(coverage_array[intensive_start:])
            intensive_regions.append({
                'start': intensive_start,
                'end': text_length,
                'length': text_length - intensive_start,
                'max_overlap': int(max_overlap),
                'text': intensive_text[:100]
            })
        
        # Create visualization - PIE CHART ONLY
        self.analysis_figure.clear()
        ax = self.analysis_figure.add_subplot(111)
        
        sizes = [uncoded_positions, single_coded_positions, multi_coded_positions]
        labels = [
            f'Uncoded\n({uncoded_positions:,} chars)',
            f'Single Code\n({single_coded_positions:,} chars)',
            f'Multiple Codes\n({multi_coded_positions:,} chars)'
        ]
        colors = ['#ffcccc', '#ffffcc', '#ccffcc']
        explode = (0.1, 0, 0.05)  # Explode uncoded and multi-coded slices
        
        # Only show non-zero slices
        non_zero_indices = [i for i, size in enumerate(sizes) if size > 0]
        if non_zero_indices:
            filtered_sizes = [sizes[i] for i in non_zero_indices]
            filtered_labels = [labels[i] for i in non_zero_indices]
            filtered_colors = [colors[i] for i in non_zero_indices]
            filtered_explode = [explode[i] for i in non_zero_indices]
            
            ax.pie(filtered_sizes, labels=filtered_labels, colors=filtered_colors,
                    explode=filtered_explode, autopct='%1.1f%%', startangle=90,
                    textprops={'fontsize': 11, 'weight': 'bold'})
            ax.set_title(f'Document Coverage Analysis\n{coverage_percentage:.1f}% Coded', 
                        fontsize=14, fontweight='bold', pad=20)
        
        self.analysis_figure.tight_layout()
        self.analysis_canvas.draw()
        
        # Generate detailed text summary
        summary = "Coverage Analysis Report\n"
        summary += "=" * 70 + "\n\n"
        
        # Overall statistics
        summary += "OVERALL STATISTICS\n"
        summary += "-" * 70 + "\n"
        summary += f"Total document length: {text_length:,} characters\n"
        summary += f"Total annotations: {len(self.annotation_manager.annotations)}\n"
        summary += f"Coverage: {coverage_percentage:.1f}%\n\n"
        
        summary += f"Character Distribution:\n"
        summary += f"  • Uncoded: {uncoded_positions:,} chars ({(uncoded_positions/text_length)*100:.1f}%)\n"
        summary += f"  • Single code: {single_coded_positions:,} chars ({(single_coded_positions/text_length)*100:.1f}%)\n"
        summary += f"  • Multiple codes: {multi_coded_positions:,} chars ({(multi_coded_positions/text_length)*100:.1f}%)\n"
        
        if multi_coded_positions > 0:
            max_overlap = int(np.max(coverage_array))
            avg_overlap = np.mean(coverage_array[coverage_array > 0])
            summary += f"  • Maximum overlap: {max_overlap} codes at same position\n"
            summary += f"  • Average overlap (coded regions): {avg_overlap:.2f} codes\n"
        
        summary += "\n"
        
        # Uncoded regions (gaps)
        if uncoded_regions:
            summary += f"UNCODED REGIONS (POTENTIAL GAPS)\n"
            summary += "-" * 70 + "\n"
            summary += f"Found {len(uncoded_regions)} uncoded region(s) larger than 50 characters:\n\n"
            
            for i, gap in enumerate(sorted(uncoded_regions, key=lambda x: x['length'], reverse=True)[:10], 1):
                summary += f"{i}. Position {gap['start']:,} - {gap['end']:,} ({gap['length']:,} chars)\n"
                summary += f"   Text: \"{gap['text']}{'...' if len(gap['text']) >= 100 else ''}\"\n"
                summary += f"   Context: ...{gap['context']}...\n\n"
            
            if len(uncoded_regions) > 10:
                summary += f"   ... and {len(uncoded_regions) - 10} more gap(s)\n\n"
        else:
            summary += f"UNCODED REGIONS\n"
            summary += "-" * 70 + "\n"
            summary += "No significant uncoded regions found (>50 chars).\n"
            summary += "Document is comprehensively coded! ✓\n\n"
        
        # Intensively coded regions
        if intensive_regions:
            summary += f"INTENSIVELY CODED REGIONS (3+ OVERLAPPING CODES)\n"
            summary += "-" * 70 + "\n"
            summary += f"Found {len(intensive_regions)} intensive region(s):\n\n"
            
            for i, region in enumerate(sorted(intensive_regions, key=lambda x: x['max_overlap'], reverse=True)[:10], 1):
                summary += f"{i}. Position {region['start']:,} - {region['end']:,} "
                summary += f"({region['length']:,} chars, {region['max_overlap']} codes)\n"
                summary += f"   Text: \"{region['text']}{'...' if len(region['text']) >= 100 else ''}\"\n\n"
            
            if len(intensive_regions) > 10:
                summary += f"   ... and {len(intensive_regions) - 10} more intensive region(s)\n\n"
            
            summary += "Note: Intensive coding may indicate important/complex passages\n"
            summary += "or potential over-coding.\n\n"
        else:
            summary += f"INTENSIVELY CODED REGIONS\n"
            summary += "-" * 70 + "\n"
            summary += "No regions with 3+ overlapping codes found.\n\n"
        
        # Recommendations
        summary += "RECOMMENDATIONS\n"
        summary += "-" * 70 + "\n"
        
        if coverage_percentage < 50:
            summary += "⚠️  Coverage is below 50%. Consider:\n"
            summary += "   • Reviewing uncoded regions for relevant content\n"
            summary += "   • Ensuring all research questions are addressed\n"
            summary += "   • Adding codes for important themes\n"
        elif coverage_percentage < 80:
            summary += "✓ Coverage is moderate (50-80%). Consider:\n"
            summary += "   • Reviewing larger uncoded gaps\n"
            summary += "   • Checking if all themes are adequately represented\n"
        else:
            summary += "✓✓ Excellent coverage (80%+)!\n"
            summary += "   • Document is comprehensively coded\n"
            summary += "   • Review intensive regions for potential over-coding\n"
        
        if len(intensive_regions) > 5:
            summary += "\n⚠️  Multiple intensive regions detected. Consider:\n"
            summary += "   • Whether all overlapping codes are necessary\n"
            summary += "   • If some codes could be merged or refined\n"
            summary += "   • If these represent truly complex passages\n"
        
        self.analysis_results.setPlainText(summary)
    
    # ===== Records Methods =====
    
    def create_records_tab(self):
        """
        Create records tab with enhanced search functionality
        ENHANCED: Search now operates across Text, Code, and Memo columns
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Enhanced search layout with better instructions
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search in text, code, or memo...")
        self.search_input.returnPressed.connect(self.search_records)
        search_layout.addWidget(self.search_input)
        
        search_btn = QPushButton("Search")
        search_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogContentsView))
        search_btn.clicked.connect(self.search_records)
        search_layout.addWidget(search_btn)
        
        clear_btn = QPushButton("Clear")
        clear_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogResetButton))
        clear_btn.clicked.connect(self.clear_search)
        search_layout.addWidget(clear_btn)
        
        # Add search info label
        search_info = QLabel("💡 Search across text, code, and memo fields")
        search_info.setStyleSheet("color: #666; font-style: italic; font-size: 10pt;")
        search_layout.addWidget(search_info)
        
        search_layout.addStretch()
        layout.addLayout(search_layout)
        
        self.records_table = QTableWidget()
        self.records_table.setColumnCount(6)
        self.records_table.setHorizontalHeaderLabels(["#", "Start", "End", "Text", "Code", "Memo"])
        
        header = self.records_table.horizontalHeader()
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        
        # Set column widths for better display
        self.records_table.setColumnWidth(0, 50)   # # column
        self.records_table.setColumnWidth(1, 80)   # Start column
        self.records_table.setColumnWidth(2, 80)   # End column
        self.records_table.setColumnWidth(4, 120)  # Code column
        
        self.records_table.setAlternatingRowColors(True)
        
        # Enable tooltips
        self.records_table.setMouseTracking(True)
        
        layout.addWidget(self.records_table)
        
        bottom_layout = QHBoxLayout()
        
        export_csv_btn = QPushButton("Export CSV")
        export_csv_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton))
        export_csv_btn.clicked.connect(lambda: self.export_records('csv'))
        bottom_layout.addWidget(export_csv_btn)
        
        export_json_btn = QPushButton("Export JSON")
        export_json_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton))
        export_json_btn.clicked.connect(lambda: self.export_records('json'))
        bottom_layout.addWidget(export_json_btn)
        
        bottom_layout.addStretch()
        
        self.record_count_label = QLabel("Total: 0 annotations")
        self.record_count_label.setStyleSheet("font-weight: bold;")
        bottom_layout.addWidget(self.record_count_label)
        
        layout.addLayout(bottom_layout)
        
        return widget
    
    def update_records_table(self, search_query=""):
        """
        Update records table with performance optimizations for large datasets
        FIXED: Now shows actual selected text from original document
        FIXED: Search now operates across Text, Code, and Memo columns
        """
        # Disable updates and sorting during population for better performance
        self.records_table.setUpdatesEnabled(False)
        sorting_enabled = self.records_table.isSortingEnabled()
        self.records_table.setSortingEnabled(False)
        
        self.records_table.setRowCount(0)
        count = 0
        
        # Pre-filter annotations if search query provided
        # ENHANCED: Search across text, code, AND memo
        if search_query:
            search_lower = search_query.lower()
            annotations = [ann for ann in self.annotation_manager.annotations 
                        if search_lower in ann.text.lower() 
                        or search_lower in ann.code.lower()
                        or search_lower in ann.memo.lower()]
        else:
            annotations = self.annotation_manager.annotations
        
        # Set row count once instead of inserting rows one by one
        self.records_table.setRowCount(len(annotations))
        
        # Populate all rows
        for row, ann in enumerate(annotations):
            # Row number
            self.records_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            
            # Start position
            self.records_table.setItem(row, 1, QTableWidgetItem(str(ann.start)))
            
            # End position
            self.records_table.setItem(row, 2, QTableWidgetItem(str(ann.end)))
            
            # FIXED: Show the actual text from the annotation object (which comes from original text)
            # This ensures the text matches what was selected and highlighted
            actual_text = ann.text[:100] if len(ann.text) > 100 else ann.text
            text_item = QTableWidgetItem(actual_text)
            color = self.annotation_manager.code_colors.get(ann.code, '#FFFFFF')
            text_item.setBackground(QColor(color))
            text_item.setToolTip(ann.text)  # Full text on hover
            self.records_table.setItem(row, 3, text_item)
            
            # Code
            code_item = QTableWidgetItem(ann.code)
            code_item.setBackground(QColor(color))
            self.records_table.setItem(row, 4, code_item)
            
            # Memo - show first 50 chars with tooltip for full text
            memo_display = ann.memo[:50] if len(ann.memo) > 50 else ann.memo
            memo_item = QTableWidgetItem(memo_display)
            if ann.memo:
                memo_item.setToolTip(ann.memo)  # Full memo on hover
            self.records_table.setItem(row, 5, memo_item)
            
            count += 1
        
        # Re-enable updates and restore sorting
        self.records_table.setSortingEnabled(sorting_enabled)
        self.records_table.setUpdatesEnabled(True)
        
        # Update status with search info if applicable
        if search_query:
            self.record_count_label.setText(
                f"Showing: {count} annotations (filtered by '{search_query}') | "
                f"Total: {len(self.annotation_manager.annotations)} annotations"
            )
        else:
            self.record_count_label.setText(f"Total: {count} annotations")
    
    def search_records(self):
        query = self.search_input.text()
        self.update_records_table(query)
    
    def clear_search(self):
        self.search_input.clear()
        self.update_records_table()
    
    def export_records(self, format_type):
        if not self.annotation_manager.annotations:
            QMessageBox.warning(self, "Warning", "No records")
            return
        
        if format_type == 'csv':
            filepath, _ = QFileDialog.getSaveFileName(
                self, "Export CSV", "", "CSV Files (*.csv)"
            )
            if filepath:
                with open(filepath, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Start', 'End', 'Text', 'Code', 'Memo'])
                    for ann in self.annotation_manager.annotations:
                        writer.writerow([ann.start, ann.end, ann.text, ann.code, ann.memo])
                QMessageBox.information(self, "Success", "Exported to CSV")
        
        elif format_type == 'json':
            filepath, _ = QFileDialog.getSaveFileName(
                self, "Export JSON", "", "JSON Files (*.json)"
            )
            if filepath:
                data = [{
                    'start': a.start,
                    'end': a.end,
                    'text': a.text,
                    'code': a.code,
                    'memo': a.memo
                } for a in self.annotation_manager.annotations]
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
                QMessageBox.information(self, "Success", "Exported to JSON")
    
    # ===== Comparison Methods =====
    
    def create_comparison_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        file_group = QGroupBox("Load Files for Comparison")
        file_layout = QGridLayout()
        
        file_layout.addWidget(QLabel("File 1:"), 0, 0)
        self.file1_btn = QPushButton("Load File 1")
        self.file1_btn.clicked.connect(lambda: self.load_comparison_file(1))
        file_layout.addWidget(self.file1_btn, 0, 1)
        self.file1_label = QLabel("No file loaded")
        file_layout.addWidget(self.file1_label, 0, 2)
        
        file_layout.addWidget(QLabel("File 2:"), 1, 0)
        self.file2_btn = QPushButton("Load File 2")
        self.file2_btn.clicked.connect(lambda: self.load_comparison_file(2))
        file_layout.addWidget(self.file2_btn, 1, 1)
        self.file2_label = QLabel("No file loaded")
        file_layout.addWidget(self.file2_label, 1, 2)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        control_layout = QHBoxLayout()
        
        # ADD: Visualization type dropdown
        control_layout.addWidget(QLabel("Visualization:"))
        self.comparison_viz_type = QComboBox()
        self.comparison_viz_type.addItems([
            "Side-by-Side Comparison",
            "Difference Chart (Delta)",
            "Percentage Change"
        ])
        self.comparison_viz_type.setMinimumWidth(200)
        self.comparison_viz_type.currentIndexChanged.connect(self.update_comparison_visualization)
        control_layout.addWidget(self.comparison_viz_type)
        
        compare_btn = QPushButton("Run Comparison")
        compare_btn.clicked.connect(self.run_comparison)
        control_layout.addWidget(compare_btn)
        
        control_layout.addStretch()
        layout.addLayout(control_layout)
        
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        self.comparison_figure = Figure(figsize=(10, 4))
        self.comparison_canvas = FigureCanvasQTAgg(self.comparison_figure)
        splitter.addWidget(self.comparison_canvas)
        
        self.comparison_summary = QTextEdit()
        self.comparison_summary.setReadOnly(True)
        splitter.addWidget(self.comparison_summary)
        
        layout.addWidget(splitter)
        
        self.comparison_data = [None, None]
        
        return widget
    
    def load_comparison_file(self, file_num):
        """
        Load comparison file - supports JSON, CSV, and HTML with annotations
        HTML files should be in the format saved by 'Save Annotated Text' button
        """
        filepath, _ = QFileDialog.getOpenFileName(
            self, f"Load File {file_num}", "", 
            "All Supported Files (*.json *.csv *.html);;JSON Files (*.json);;CSV Files (*.csv);;HTML Files (*.html);;All Files (*.*)"
        )
        
        if not filepath:
            return
        
        try:
            if filepath.endswith('.json'):
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Check if it's the annotated text format (with 'text' and 'annotations' keys)
                if isinstance(data, dict) and 'annotations' in data:
                    # Convert to list format for comparison
                    data = data['annotations']
                
            elif filepath.endswith('.csv'):
                df = pd.read_csv(filepath)
                data = df.to_dict('records')
                
            elif filepath.endswith('.html'):
                # Parse HTML file to extract annotations
                with open(filepath, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                
                # Extract annotations from HTML
                data = self._parse_html_annotations(html_content)
                
                if not data:
                    QMessageBox.warning(self, "Warning", 
                        "No annotations found in HTML file. Make sure it's a file saved from the 'Save Annotated Text' feature.")
                    return
            else:
                QMessageBox.warning(self, "Warning", "Unsupported format")
                return
            
            self.comparison_data[file_num - 1] = data
            
            label = self.file1_label if file_num == 1 else self.file2_label
            label.setText(f"{os.path.basename(filepath)} ({len(data)} records)")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load: {str(e)}")

    def _parse_html_annotations(self, html_content):
        """
        Parse HTML content to extract annotations from VoxScribe HTML export
        
        Supports two methods:
        1. Extract from embedded JSON metadata (preferred, preserves all data)
        2. Parse from HTML spans (fallback, less precise)
        
        Args:
            html_content: HTML string with annotations (from VoxScribe export)
            
        Returns:
            List of annotation dictionaries compatible with comparison analysis
        """
        import re
        import html as html_module
        import json
        
        annotations = []
        
        # Method 1: Try to extract from embedded JSON (new format)
        json_pattern = r'<script type="application/json">\s*(.*?)\s*</script>'
        json_match = re.search(json_pattern, html_content, re.DOTALL)
        
        if json_match:
            try:
                json_data = json_match.group(1)
                annotations_data = json.loads(json_data)
                
                # Convert to expected format
                for i, ann_data in enumerate(annotations_data):
                    annotations.append({
                        'id': i + 1,
                        'start': ann_data.get('start', 0),
                        'end': ann_data.get('end', 0),
                        'text': ann_data.get('text', ''),
                        'code': ann_data.get('code', ''),
                        'memo': ann_data.get('memo', ''),
                        'color': ann_data.get('color', '#FFFFFF'),
                        'length': len(ann_data.get('text', ''))
                    })
                
                return annotations
            except json.JSONDecodeError:
                # Fall through to Method 2
                pass
        
        # Method 2: Parse from HTML spans (fallback for older exports or other sources)
        # Pattern with data attributes (if present)
        pattern_with_data = r'<span\s+class="annotation"\s+style="background-color:\s*([^;"]+);[^"]*"\s+title="([^"]*)"\s+data-start="(\d+)"\s+data-end="(\d+)">\s*(.*?)\s*<span\s+class="code-label">\[([^\]]+)\]</span>\s*</span>'
        
        matches = re.finditer(pattern_with_data, html_content, re.DOTALL)
        found_with_data = False
        
        for i, match in enumerate(matches):
            found_with_data = True
            color = match.group(1).strip()
            title = match.group(2)
            start = int(match.group(3))
            end = int(match.group(4))
            text = match.group(5).strip()
            code = match.group(6).strip()
            
            # Extract memo from title
            memo = ""
            if " | Memo: " in title:
                parts = title.split(" | Memo: ")
                if len(parts) == 2:
                    memo = html_module.unescape(parts[1].strip())
            
            text = html_module.unescape(text)
            
            annotations.append({
                'id': i + 1,
                'start': start,
                'end': end,
                'text': text,
                'code': code,
                'memo': memo,
                'color': color,
                'length': len(text)
            })
        
        if found_with_data:
            return annotations
        
        # Pattern without data attributes (basic fallback)
        pattern_basic = r'<span\s+class="annotation"\s+style="background-color:\s*([^;"]+);[^"]*"\s+title="([^"]*)">\s*(.*?)\s*<span\s+class="code-label">\[([^\]]+)\]</span>\s*</span>'
        
        matches = re.finditer(pattern_basic, html_content, re.DOTALL)
        
        for i, match in enumerate(matches):
            color = match.group(1).strip()
            title = match.group(2)
            text = match.group(3).strip()
            code = match.group(4).strip()
            
            # Extract memo from title
            memo = ""
            if " | Memo: " in title:
                parts = title.split(" | Memo: ")
                if len(parts) == 2:
                    memo = html_module.unescape(parts[1].strip())
            
            text = html_module.unescape(text)
            
            # Without position data, use placeholder positions
            annotations.append({
                'id': i + 1,
                'start': i * 100,  # Placeholder
                'end': i * 100 + len(text),
                'text': text,
                'code': code,
                'memo': memo,
                'color': color,
                'length': len(text)
            })
        
        return annotations
    
    def update_comparison_visualization(self):
        """Update the comparison visualization when dropdown changes"""
        if all(self.comparison_data):
            self._generate_comparison_chart()
    
    def run_comparison(self):
        if not all(self.comparison_data):
            QMessageBox.warning(self, "Warning", "Load both files first")
            return
        
        # Generate the selected visualization
        self._generate_comparison_chart()

    def _generate_comparison_chart(self):
        """Generate comparison chart based on selected visualization type"""
        data1, data2 = self.comparison_data
        
        # Count code frequencies
        codes1 = Counter(d.get('code', '') for d in data1)
        codes2 = Counter(d.get('code', '') for d in data2)
        
        all_codes = sorted(set(codes1.keys()) | set(codes2.keys()))
        
        viz_type = self.comparison_viz_type.currentText()
        
        self.comparison_figure.clear()
        
        if viz_type == "Side-by-Side Comparison":
            self._generate_sidebyside_chart(all_codes, codes1, codes2)
        elif viz_type == "Difference Chart (Delta)":
            self._generate_difference_chart(all_codes, codes1, codes2)
        elif viz_type == "Percentage Change":
            self._generate_percentage_change_chart(all_codes, codes1, codes2)
        
        self.comparison_figure.tight_layout()
        self.comparison_canvas.draw()
        
        # Generate text summary
        self._generate_comparison_summary(data1, data2, codes1, codes2, all_codes)

    def _generate_sidebyside_chart(self, all_codes, codes1, codes2):
        """Generate side-by-side bar chart"""
        ax = self.comparison_figure.add_subplot(111)
        
        x = np.arange(len(all_codes))
        width = 0.35
        
        counts1 = [codes1.get(c, 0) for c in all_codes]
        counts2 = [codes2.get(c, 0) for c in all_codes]
        
        ax.bar(x - width/2, counts1, width, label='File 1', color='steelblue', edgecolor='black')
        ax.bar(x + width/2, counts2, width, label='File 2', color='coral', edgecolor='black')
        
        ax.set_xlabel('Codes', fontweight='bold')
        ax.set_ylabel('Count', fontweight='bold')
        ax.set_title('Side-by-Side Code Comparison', fontsize=14, fontweight='bold', pad=15)
        ax.set_xticks(x)
        ax.set_xticklabels(all_codes, rotation=45, ha='right')
        ax.legend(loc='upper right')
        ax.grid(axis='y', alpha=0.3, linestyle='--')

    def _generate_difference_chart(self, all_codes, codes1, codes2):
        """Generate difference chart showing deltas (File 2 - File 1)"""
        ax = self.comparison_figure.add_subplot(111)
        
        # Calculate differences
        deltas = []
        for code in all_codes:
            delta = codes2.get(code, 0) - codes1.get(code, 0)
            deltas.append(delta)
        
        # Create horizontal bar chart
        y_pos = np.arange(len(all_codes))
        
        # Color bars: green for positive, red for negative, gray for zero
        colors = []
        for delta in deltas:
            if delta > 0:
                colors.append('#4CAF50')  # Green for increase
            elif delta < 0:
                colors.append('#f44336')  # Red for decrease
            else:
                colors.append('#9E9E9E')  # Gray for no change
        
        bars = ax.barh(y_pos, deltas, color=colors, edgecolor='black', linewidth=1.5)
        
        # Add value labels on bars
        for i, (bar, delta) in enumerate(zip(bars, deltas)):
            width = bar.get_width()
            label_x = width + (0.5 if width >= 0 else -0.5)
            ax.text(label_x, bar.get_y() + bar.get_height()/2, 
                f'{int(delta):+d}',  # Format with + or - sign
                ha='left' if width >= 0 else 'right',
                va='center', fontweight='bold', fontsize=10)
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(all_codes)
        ax.set_xlabel('Change in Count (File 2 - File 1)', fontweight='bold')
        ax.set_title('Code Frequency Difference Chart', fontsize=14, fontweight='bold', pad=15)
        
        # Add vertical line at x=0
        ax.axvline(x=0, color='black', linewidth=2, linestyle='-', alpha=0.7)
        
        # Add grid
        ax.grid(axis='x', alpha=0.3, linestyle='--')
        
        # Add legend
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='#4CAF50', edgecolor='black', label='Increase (File 2 > File 1)'),
            Patch(facecolor='#f44336', edgecolor='black', label='Decrease (File 2 < File 1)'),
            Patch(facecolor='#9E9E9E', edgecolor='black', label='No Change')
        ]
        ax.legend(handles=legend_elements, loc='lower right', fontsize=9)

    def _generate_percentage_change_chart(self, all_codes, codes1, codes2):
        """Generate percentage change chart"""
        ax = self.comparison_figure.add_subplot(111)
        
        # Calculate percentage changes
        pct_changes = []
        for code in all_codes:
            count1 = codes1.get(code, 0)
            count2 = codes2.get(code, 0)
            
            if count1 == 0 and count2 == 0:
                pct_change = 0
            elif count1 == 0:
                pct_change = 100  # New code in File 2
            else:
                pct_change = ((count2 - count1) / count1) * 100
            
            pct_changes.append(pct_change)
        
        # Create horizontal bar chart
        y_pos = np.arange(len(all_codes))
        
        # Color bars based on percentage change
        colors = []
        for pct in pct_changes:
            if pct > 0:
                colors.append('#4CAF50')  # Green
            elif pct < 0:
                colors.append('#f44336')  # Red
            else:
                colors.append('#9E9E9E')  # Gray
        
        bars = ax.barh(y_pos, pct_changes, color=colors, edgecolor='black', linewidth=1.5)
        
        # Add value labels
        for i, (bar, pct) in enumerate(zip(bars, pct_changes)):
            width = bar.get_width()
            label_x = width + (2 if width >= 0 else -2)
            ax.text(label_x, bar.get_y() + bar.get_height()/2,
                f'{pct:+.1f}%',
                ha='left' if width >= 0 else 'right',
                va='center', fontweight='bold', fontsize=10)
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(all_codes)
        ax.set_xlabel('Percentage Change (%)', fontweight='bold')
        ax.set_title('Code Frequency Percentage Change', fontsize=14, fontweight='bold', pad=15)
        
        # Add vertical line at x=0
        ax.axvline(x=0, color='black', linewidth=2, linestyle='-', alpha=0.7)
        
        # Add grid
        ax.grid(axis='x', alpha=0.3, linestyle='--')
        
        # Add legend
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='#4CAF50', edgecolor='black', label='Increase'),
            Patch(facecolor='#f44336', edgecolor='black', label='Decrease'),
            Patch(facecolor='#9E9E9E', edgecolor='black', label='No Change')
        ]
        ax.legend(handles=legend_elements, loc='lower right', fontsize=9)

    def _generate_comparison_summary(self, data1, data2, codes1, codes2, all_codes):
        """Generate detailed text summary of comparison"""
        viz_type = self.comparison_viz_type.currentText()
        
        summary = f"Comparison Summary ({viz_type})\n"
        summary += "=" * 70 + "\n\n"
        
        summary += "FILE STATISTICS\n"
        summary += "-" * 70 + "\n"
        summary += f"File 1: {len(data1)} annotations, {len(codes1)} unique codes\n"
        summary += f"File 2: {len(data2)} annotations, {len(codes2)} unique codes\n\n"
        
        # Overall change
        total_delta = len(data2) - len(data1)
        pct_change = ((len(data2) - len(data1)) / len(data1) * 100) if len(data1) > 0 else 0
        summary += f"Total annotation change: {total_delta:+d} ({pct_change:+.1f}%)\n\n"
        
        # Code-level analysis
        shared = set(codes1.keys()) & set(codes2.keys())
        only_file1 = codes1.keys() - codes2.keys()
        only_file2 = codes2.keys() - codes1.keys()
        
        summary += "CODE DISTRIBUTION\n"
        summary += "-" * 70 + "\n"
        summary += f"Shared codes: {len(shared)}\n"
        summary += f"Codes only in File 1: {len(only_file1)}\n"
        summary += f"Codes only in File 2: {len(only_file2)}\n\n"
        
        if viz_type == "Difference Chart (Delta)" or viz_type == "Percentage Change":
            summary += "DETAILED CODE CHANGES\n"
            summary += "-" * 70 + "\n"
            
            # Calculate and sort by absolute change
            changes = []
            for code in all_codes:
                count1 = codes1.get(code, 0)
                count2 = codes2.get(code, 0)
                delta = count2 - count1
                
                if count1 == 0 and count2 == 0:
                    pct = 0
                elif count1 == 0:
                    pct = 100
                else:
                    pct = ((count2 - count1) / count1) * 100
                
                changes.append((code, count1, count2, delta, pct))
            
            # Sort by absolute delta (largest changes first)
            changes.sort(key=lambda x: abs(x[3]), reverse=True)
            
            for code, count1, count2, delta, pct in changes:
                status = "↑" if delta > 0 else "↓" if delta < 0 else "="
                summary += f"{status} {code}:\n"
                summary += f"   File 1: {count1} | File 2: {count2} | "
                summary += f"Change: {delta:+d} ({pct:+.1f}%)\n"
            
            summary += "\n"
        
        # Codes only in one file
        if only_file1:
            summary += "CODES ONLY IN FILE 1\n"
            summary += "-" * 70 + "\n"
            for code in sorted(only_file1):
                summary += f"  • {code}: {codes1[code]} annotations\n"
            summary += "\n"
        
        if only_file2:
            summary += "CODES ONLY IN FILE 2\n"
            summary += "-" * 70 + "\n"
            for code in sorted(only_file2):
                summary += f"  • {code}: {codes2[code]} annotations\n"
            summary += "\n"
        
        # Top changes
        if viz_type == "Difference Chart (Delta)":
            summary += "KEY INSIGHTS\n"
            summary += "-" * 70 + "\n"
            
            increases = [(c, d) for c, _, _, d, _ in changes if d > 0]
            decreases = [(c, d) for c, _, _, d, _ in changes if d < 0]
            
            if increases:
                top_increase = max(increases, key=lambda x: x[1])
                summary += f"• Largest increase: {top_increase[0]} (+{top_increase[1]})\n"
            
            if decreases:
                top_decrease = min(decreases, key=lambda x: x[1])
                summary += f"• Largest decrease: {top_decrease[0]} ({top_decrease[1]})\n"
            
            if not increases and not decreases:
                summary += "• No changes detected between files\n"
        
        self.comparison_summary.setPlainText(summary)

def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    window = VoxScribeGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()