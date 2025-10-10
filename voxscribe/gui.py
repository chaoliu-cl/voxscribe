"""
VoxScribe GUI
"""

import sys
import os
import json
import re
from typing import Optional, List, Dict, Any
from datetime import datetime
from collections import Counter, defaultdict
import csv
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit, QLineEdit, QComboBox, QCheckBox,
    QProgressBar, QTabWidget, QFrame, QTableWidget, QTableWidgetItem,
    QFileDialog, QMessageBox, QSplitter, QGridLayout, QHeaderView,
    QGroupBox, QDialog, QStyle, QListWidget, QListWidgetItem,
    QInputDialog, QTreeWidget, QTreeWidgetItem, QScrollArea, QRadioButton
)
from PySide6.QtCore import Qt, Signal, QThread, QSize, QEvent, QTimer, QMutex
from PySide6.QtGui import QFont, QColor, QPalette, QTextCursor, QTextCharFormat

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import networkx as nx

# Placeholder imports
try:
    from .transcriber import AudioTranscriber
    from .annotator import TextAnnotator
    from .utils import validate_audio_file, format_time, get_audio_duration
except ImportError:
    class AudioTranscriber:
        def __init__(self, device="auto", compute_type="auto"):
            self.device = device
            self.compute_type = compute_type
            self.model = None
            self.model_size = None
        
        def get_device_info(self):
            return {"device": self.device, "compute_type": self.compute_type}
        
        def load_model(self):
            pass
        
        def change_model(self, size):
            self.model_size = size
        
        def transcribe_batch(self, audio_paths, **kwargs):
            # Dummy implementation
            import time
            results = []
            for path in audio_paths:
                time.sleep(0.5)
                results.append({
                    'path': path,
                    'filename': os.path.basename(path),
                    'success': True,
                    'results': [{'text': 'Sample text', 'id': 0}],
                    'segments_count': 1,
                    'processing_time': 0.5,
                    'error': None
                })
                if kwargs.get('batch_progress_callback'):
                    kwargs['batch_progress_callback'](len(results), len(audio_paths), os.path.basename(path))
            return results
    
    class TextAnnotator:
        def __init__(self):
            pass
    
    def validate_audio_file(path):
        return (True, "Valid")
    
    def format_time(seconds):
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins:02d}:{secs:02d}"
    
    def get_audio_duration(path):
        return 0


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
        annotation = CodeMemo()
        annotation.start = start
        annotation.end = end
        annotation.text = text
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
    """Background worker for single file transcription"""
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
            
            if self.transcriber.model_size != self.model_size:
                self.transcriber.change_model(self.model_size)
            elif self.transcriber.model is None:
                self.transcriber.load_model()
            
            self.progress.emit(10, "Model loaded, starting transcription...")
            
            duration = get_audio_duration(self.audio_path)
            results = []
            
            segment_generator = self.transcriber.model.transcribe(
                self.audio_path,
                language=self.language if self.language != "auto" else None
            )
            
            segments_iter, info = segment_generator
            
            for segment in segments_iter:
                segment_dict = {
                    'text': segment.text.strip(),
                    'id': segment.id
                }
                
                if self.include_timestamps:
                    segment_dict['start'] = segment.start
                    segment_dict['end'] = segment.end
                    
                    if duration and duration > 0:
                        progress_pct = int(10 + (segment.end / duration) * 85)
                        progress_pct = min(95, progress_pct)
                        self.progress.emit(progress_pct, f"Transcribing... ({format_time(segment.end)})")
                    else:
                        progress_pct = int(10 + min(85, len(results) * 2))
                        self.progress.emit(progress_pct, f"Transcribing... ({len(results)} segments)")
                else:
                    progress_pct = int(10 + min(85, len(results) * 2))
                    self.progress.emit(progress_pct, f"Transcribing... ({len(results)} segments)")
                
                results.append(segment_dict)
            
            self.progress.emit(100, f"Complete! {len(results)} segments transcribed")
            self.finished.emit(results)
            
        except Exception as e:
            self.error.emit(str(e))


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
        self.do_align.setChecked(True)
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
        """Create code tab"""
        widget = QWidget()
        main_layout = QVBoxLayout(widget)
        main_layout.setSpacing(10)
        
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setSpacing(5)
        
        import_btn = QPushButton("Import Text")
        import_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogOpenButton))
        import_btn.clicked.connect(self.import_text)
        toolbar_layout.addWidget(import_btn)
        
        refresh_btn = QPushButton("Refresh Display")
        refresh_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload))
        refresh_btn.clicked.connect(self.refresh_text_display)
        toolbar_layout.addWidget(refresh_btn)
        
        toolbar_layout.addStretch()
        
        main_layout.addLayout(toolbar_layout)
        
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
        
        memo_layout = QHBoxLayout()
        memo_layout.setSpacing(5)
        memo_label = QLabel("Memo:")
        memo_label.setFixedWidth(50)
        memo_layout.addWidget(memo_label)
        self.memo_input = QTextEdit()
        self.memo_input.setPlaceholderText("Enter memo (optional)...")
        self.memo_input.setMaximumHeight(80)
        memo_layout.addWidget(self.memo_input)
        input_layout.addLayout(memo_layout)
        
        button_layout = QHBoxLayout()
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
        
        save_btn = QPushButton("Save Annotated Text")
        save_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton))
        save_btn.clicked.connect(self.save_annotation)
        button_layout.addWidget(save_btn)
        
        input_layout.addLayout(button_layout)
        input_group.setLayout(input_layout)
        main_layout.addWidget(input_group)
        
        selection_group = QGroupBox("Text Selection")
        selection_layout = QHBoxLayout()
        selection_layout.setSpacing(5)
        
        self.select_text_button = QPushButton("Enable Selection")
        self.select_text_button.setCheckable(True)
        self.select_text_button.toggled.connect(self.toggle_selection_mode)
        selection_layout.addWidget(self.select_text_button)
        
        clear_selection_btn = QPushButton("Clear Selection")
        clear_selection_btn.clicked.connect(self.clear_selection)
        selection_layout.addWidget(clear_selection_btn)
        
        selection_layout.addStretch()
        
        self.legend_label = QLabel("Workflow: 1) Enable Selection → 2) Select text → 3) Click 'Create Code' or 'Apply Code' | Click code labels to remove")
        self.legend_label.setStyleSheet("color: #666; font-style: italic; font-size: 10pt;")
        selection_layout.addWidget(self.legend_label)
        
        selection_group.setLayout(selection_layout)
        main_layout.addWidget(selection_group)
        
        self.code_status_label = QLabel("Ready")
        self.code_status_label.setStyleSheet("color: #2E7D32; font-weight: bold; padding: 5px;")
        main_layout.addWidget(self.code_status_label)
        
        text_group = QGroupBox()
        text_group_layout = QVBoxLayout(text_group)
        text_group_layout.setSpacing(5)
        text_group_layout.setContentsMargins(5, 5, 5, 5)
        
        title_layout = QHBoxLayout()
        title_layout.setSpacing(5)
        
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
        
        text_group_layout.addLayout(title_layout)
        
        self.coding_text = QTextEdit()
        self.coding_text.setReadOnly(True)
        self.coding_text.viewport().installEventFilter(self)
        self.update_text_display_font()
        text_group_layout.addWidget(self.coding_text)
        
        main_layout.addWidget(text_group)
        
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
        cursor = QTextCursor(self.coding_text.document())
        cursor.clearSelection()
        self.coding_text.setTextCursor(cursor)
    
    def refresh_text_display(self):
        if not self.current_text:
            return
        
        cursor = self.coding_text.textCursor()
        original_position = cursor.position()
        
        self.coding_text.blockSignals(True)
        
        try:
            self.coding_text.clear()
            self.coding_text.setPlainText(self.current_text)
            
            sorted_annotations = sorted(self.annotation_manager.annotations, key=lambda a: a.start, reverse=True)
            
            for ann in sorted_annotations:
                if ann.start < 0 or ann.end > len(self.current_text) or ann.start >= ann.end:
                    continue
                
                color = self.annotation_manager.code_colors.get(ann.code, '#FFFF00')
                
                cursor = QTextCursor(self.coding_text.document())
                cursor.setPosition(ann.start)
                cursor.setPosition(ann.end, QTextCursor.MoveMode.KeepAnchor)
                
                fmt = QTextCharFormat()
                fmt.setBackground(QColor(color))
                fmt.setForeground(QColor(0, 0, 0))
                cursor.mergeCharFormat(fmt)
                
                cursor = QTextCursor(self.coding_text.document())
                cursor.setPosition(ann.end)
                
                label_text = f" [{ann.code}]"
                label_fmt = QTextCharFormat()
                label_fmt.setForeground(QColor(100, 100, 100))
                label_fmt.setFontWeight(QFont.Weight.Bold)
                label_fmt.setBackground(QColor(color))
                label_fmt.setProperty(1001, ann.code)
                
                cursor.setCharFormat(label_fmt)
                cursor.insertText(label_text)
            
            fresh_cursor = QTextCursor(self.coding_text.document())
            fresh_cursor.setPosition(min(original_position, len(self.coding_text.toPlainText())))
            self.coding_text.setTextCursor(fresh_cursor)
            
        finally:
            self.coding_text.blockSignals(False)
            self.ensure_no_selection()
        
        if sorted_annotations:
            self.code_status_label.setText(f"✓ Display refreshed - {len(sorted_annotations)} annotations shown (click code labels to remove)")
            self.code_status_label.setStyleSheet("color: #2E7D32; font-weight: bold; padding: 5px;")
        else:
            self.code_status_label.setText("Display refreshed - no annotations")
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
                
                original_start, original_end = self.convert_display_to_original_positions(display_start, display_end)
                
                actual_text = self.current_text[original_start:original_end]
                
                self.annotation_manager.add_annotation(original_start, original_end, actual_text, code, memo)
                
                cursor.clearSelection()
                self.coding_text.setTextCursor(cursor)
                
                self.update_all_displays()
                self.refresh_text_display()
                self.ensure_no_selection()
                
                preview = actual_text[:50] + "..." if len(actual_text) > 50 else actual_text
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
        current_text = self.code_input.currentText()
        self.code_input.clear()
        self.code_input.addItems(sorted(self.annotation_manager.codes))
        self.code_input.setCurrentText(current_text)
    
    def update_all_displays(self):
        self.update_codebook_table()
        self.update_records_table()
        self.update_theme_tree()
        self.update_code_dropdown()
    
    def create_and_apply_code(self):
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
            selected_text = cursor.selectedText()
            memo = self.memo_input.toPlainText().strip()
            
            original_start, original_end = self.convert_display_to_original_positions(display_start, display_end)
            
            actual_text = self.current_text[original_start:original_end]
            
            self.annotation_manager.add_annotation(original_start, original_end, actual_text, code, memo)
            
            cursor.clearSelection()
            self.coding_text.setTextCursor(cursor)
            self.memo_input.clear()
            
            self.update_all_displays()
            self.refresh_text_display()
            self.ensure_no_selection()
            
            preview = actual_text[:50] + "..." if len(actual_text) > 50 else actual_text
            if is_new_code:
                self.code_status_label.setText(f"✓ Code '{code}' created and applied to: \"{preview}\"")
                self.code_status_label.setStyleSheet("color: #2E7D32; font-weight: bold; padding: 5px;")
            else:
                self.code_status_label.setText(f"✓ Code '{code}' applied to: \"{preview}\"")
                self.code_status_label.setStyleSheet("color: #2E7D32; font-weight: bold; padding: 5px;")
        else:
            self.update_all_displays()
            if is_new_code:
                self.code_status_label.setText(f"✓ Code '{code}' created (select text to apply)")
                self.code_status_label.setStyleSheet("color: #1976D2; font-weight: bold; padding: 5px;")
            else:
                self.code_status_label.setText(f"! Code '{code}' already exists (select text to apply)")
                self.code_status_label.setStyleSheet("color: #F57C00; font-weight: bold; padding: 5px;")
    
    def convert_display_to_original_positions(self, display_start, display_end):
        if not self.annotation_manager.annotations:
            return display_start, display_end
        
        sorted_anns = sorted(self.annotation_manager.annotations, key=lambda a: a.start)
        
        offset_at_start = 0
        offset_at_end = 0
        
        for ann in sorted_anns:
            exact_label_pos = ann.end
            for prev_ann in sorted_anns:
                if prev_ann.start < ann.start:
                    exact_label_pos += len(f" [{prev_ann.code}]")
            
            label_length = len(f" [{ann.code}]")
            label_end = exact_label_pos + label_length
            
            if label_end <= display_start:
                offset_at_start += label_length
                offset_at_end += label_length
            elif exact_label_pos < display_end:
                offset_at_end += label_length
        
        original_start = display_start - offset_at_start
        original_end = display_end - offset_at_end
        
        original_start = max(0, min(original_start, len(self.current_text)))
        original_end = max(0, min(original_end, len(self.current_text)))
        
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
        
        try:
            self.code_status_label.setText("⏳ Loading text file...")
            self.code_status_label.setStyleSheet("color: #1976D2; font-weight: bold; padding: 5px;")
            QApplication.processEvents()
            
            file_size = os.path.getsize(filepath)
            file_size_mb = file_size / (1024 * 1024)
            
            self.coding_text.setUpdatesEnabled(False)
            
            with open(filepath, 'rb') as f:
                raw_data = f.read()
            
            try:
                text = raw_data.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    text = raw_data.decode('latin-1')
                except:
                    text = raw_data.decode('utf-8', errors='ignore')
            
            self.coding_text.setPlainText(text)
            self.current_text = text
            
            self.coding_text.setUpdatesEnabled(True)
            
            word_count = len(text.split())
            char_count = len(text)
            line_count = text.count('\n') + 1
            
            stats = f"✓ Imported: {char_count:,} chars, {word_count:,} words, {line_count:,} lines ({file_size_mb:.2f} MB) from {os.path.basename(filepath)}"
            self.code_status_label.setText(stats)
            self.code_status_label.setStyleSheet("color: #2E7D32; font-weight: bold; padding: 5px;")
            
        except Exception as e:
            self.coding_text.setUpdatesEnabled(True)
            QMessageBox.critical(self, "Error", f"Failed to import text:\n{str(e)}")
            self.code_status_label.setText("✗ Import failed")
            self.code_status_label.setStyleSheet("color: #d32f2f; font-weight: bold; padding: 5px;")
    
    def save_annotation(self):
        if not self.annotation_manager.annotations:
            QMessageBox.warning(self, "Warning", "No annotations to save")
            return
        
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Save Annotated Text",
            "",
            "HTML Files (*.html);;Text Files (*.txt);;JSON Files (*.json)"
        )
        
        if filepath:
            with open(filepath, 'w', encoding='utf-8') as f:
                if filepath.endswith('.json'):
                    data = {
                        'text': self.current_text,
                        'annotations': [
                            {
                                'start': a.start,
                                'end': a.end,
                                'text': a.text,
                                'code': a.code,
                                'memo': a.memo
                            }
                            for a in self.annotation_manager.annotations
                        ],
                        'codes': list(self.annotation_manager.codes),
                        'code_colors': self.annotation_manager.code_colors
                    }
                    json.dump(data, f, indent=2)
                elif filepath.endswith('.html'):
                    html = "<html><head><style>body{font-family:Arial;padding:20px;}</style></head><body>"
                    html += "<h1>Annotated Text</h1>"
                    
                    sorted_anns = sorted(self.annotation_manager.annotations, key=lambda a: a.start)
                    last_pos = 0
                    
                    for ann in sorted_anns:
                        if ann.start > last_pos:
                            html += self.current_text[last_pos:ann.start]
                        
                        color = self.annotation_manager.code_colors.get(ann.code, '#FFFF00')
                        html += f'<span style="background-color:{color};padding:2px;" title="{ann.memo}">'
                        html += self.current_text[ann.start:ann.end]
                        html += f' <strong>[{ann.code}]</strong></span>'
                        
                        last_pos = ann.end
                    
                    if last_pos < len(self.current_text):
                        html += self.current_text[last_pos:]
                    
                    html += "</body></html>"
                    f.write(html)
                else:
                    f.write(self.current_text)
            
            QMessageBox.information(self, "Success", "Annotations saved")
    
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
        layout.addWidget(self.codebook_table)
        
        stats_layout = QHBoxLayout()
        self.code_stats_label = QLabel("Total codes: 0 | Total annotations: 0")
        stats_layout.addWidget(self.code_stats_label)
        stats_layout.addStretch()
        layout.addLayout(stats_layout)
        
        return widget
    
    def update_codebook_table(self):
        self.codebook_table.setRowCount(0)
        
        codes = sorted(self.annotation_manager.codes)
        for code in codes:
            row = self.codebook_table.rowCount()
            self.codebook_table.insertRow(row)
            
            self.codebook_table.setItem(row, 0, QTableWidgetItem(code))
            
            usage = len(self.annotation_manager.get_annotations_for_code(code))
            self.codebook_table.setItem(row, 1, QTableWidgetItem(str(usage)))
            
            color = self.annotation_manager.code_colors.get(code, '#FFFFFF')
            color_item = QTableWidgetItem()
            color_item.setBackground(QColor(color))
            self.codebook_table.setItem(row, 2, color_item)
            
            self.codebook_table.setItem(row, 3, QTableWidgetItem(""))
        
        total_codes = len(self.annotation_manager.codes)
        total_annotations = len(self.annotation_manager.annotations)
        self.code_stats_label.setText(f"Total codes: {total_codes} | Total annotations: {total_annotations}")
    
    def add_code_dialog(self):
        code, ok = QInputDialog.getText(self, "Add Code", "Enter code name:")
        if ok and code:
            self.annotation_manager.codes.add(code)
            color_idx = len(self.annotation_manager.code_colors) % len(self.annotation_manager.color_palette)
            self.annotation_manager.code_colors[code] = self.annotation_manager.color_palette[color_idx]
            self.update_all_displays()
    
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
            
            self.update_all_displays()
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
            
            self.update_all_displays()
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
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        toolbar = QHBoxLayout()
        
        add_theme_btn = QPushButton("Add Theme")
        add_theme_btn.setToolTip("Add a new theme to organize your codes")
        add_theme_btn.clicked.connect(self.add_theme_dialog)
        toolbar.addWidget(add_theme_btn)
        
        add_subtheme_btn = QPushButton("Add Sub-Theme")
        add_subtheme_btn.setToolTip("Add a sub-theme under the selected theme")
        add_subtheme_btn.clicked.connect(self.add_subtheme_dialog)
        toolbar.addWidget(add_subtheme_btn)
        
        add_code_to_theme_btn = QPushButton("Link Code to Theme")
        add_code_to_theme_btn.setToolTip("Link an existing code to selected theme")
        add_code_to_theme_btn.clicked.connect(self.add_code_to_theme_dialog)
        toolbar.addWidget(add_code_to_theme_btn)
        
        delete_theme_btn = QPushButton("Delete Selected")
        delete_theme_btn.setToolTip("Delete selected theme or code link")
        delete_theme_btn.clicked.connect(self.delete_theme_item)
        toolbar.addWidget(delete_theme_btn)
        
        toolbar.addStretch()
        
        export_hierarchy_btn = QPushButton("Export")
        export_hierarchy_btn.clicked.connect(self.export_hierarchy)
        toolbar.addWidget(export_hierarchy_btn)
        
        import_hierarchy_btn = QPushButton("Import")
        import_hierarchy_btn.clicked.connect(self.import_hierarchy)
        toolbar.addWidget(import_hierarchy_btn)
        
        layout.addLayout(toolbar)
        
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        tree_widget = QWidget()
        tree_layout = QVBoxLayout(tree_widget)
        
        tree_header_layout = QHBoxLayout()
        tree_header_layout.addWidget(QLabel("<b>Theme & Code Hierarchy</b>"))
        tree_header_layout.addStretch()
        expand_all_btn = QPushButton("Expand All")
        expand_all_btn.clicked.connect(lambda: self.theme_tree.expandAll())
        tree_header_layout.addWidget(expand_all_btn)
        collapse_all_btn = QPushButton("Collapse All")
        collapse_all_btn.clicked.connect(lambda: self.theme_tree.collapseAll())
        tree_header_layout.addWidget(collapse_all_btn)
        tree_layout.addLayout(tree_header_layout)
        
        self.theme_tree = QTreeWidget()
        self.theme_tree.setHeaderLabel("Themes and Codes")
        self.theme_tree.itemClicked.connect(self.on_theme_item_clicked)
        self.theme_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
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
        self.theme_tree.clear()
        
        for child in self.annotation_manager.theme_root.children:
            self._add_node_to_tree_recursive(child, None)
        
        self.theme_tree.expandAll()
    
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
        
        text_parts = self.current_text.split('\n\n')
        
        for part in text_parts:
            codes_in_part = set()
            for ann in self.annotation_manager.annotations:
                if ann.text in part:
                    codes_in_part.add(ann.code)
            
            for i, c1 in enumerate(codes):
                for j, c2 in enumerate(codes):
                    if i < j and c1 in codes_in_part and c2 in codes_in_part:
                        cooccur[i, j] += 1
                        cooccur[j, i] += 1
        
        self.analysis_figure.clear()
        
        G = nx.Graph()
        node_colors = []
        for i, code in enumerate(codes):
            G.add_node(code)
            node_colors.append(self.annotation_manager.code_colors.get(code, '#CCCCCC'))
        
        for i in range(n):
            for j in range(i+1, n):
                if cooccur[i, j] > 0:
                    G.add_edge(codes[i], codes[j], weight=cooccur[i, j])
        
        ax = self.analysis_figure.add_subplot(111)
        pos = nx.spring_layout(G)
        nx.draw(G, pos, with_labels=True, node_color=node_colors,
                node_size=1000, font_size=10, ax=ax, edge_color='gray')
        
        ax.set_title('Code Co-occurrence Network')
        self.analysis_canvas.draw()
        
        summary = "Co-occurrence Summary\n\n"
        summary += f"Total codes: {len(codes)}\n"
        summary += f"Co-occurrences found: {int(np.sum(cooccur) / 2)}\n"
        
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
    
    # ===== Records Methods =====
    
    def create_records_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search in annotations...")
        self.search_input.returnPressed.connect(self.search_records)
        search_layout.addWidget(self.search_input)
        
        search_btn = QPushButton("Search")
        search_btn.clicked.connect(self.search_records)
        search_layout.addWidget(search_btn)
        
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear_search)
        search_layout.addWidget(clear_btn)
        
        search_layout.addStretch()
        layout.addLayout(search_layout)
        
        self.records_table = QTableWidget()
        self.records_table.setColumnCount(6)
        self.records_table.setHorizontalHeaderLabels(["#", "Start", "End", "Text", "Code", "Memo"])
        
        header = self.records_table.horizontalHeader()
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        
        self.records_table.setAlternatingRowColors(True)
        layout.addWidget(self.records_table)
        
        bottom_layout = QHBoxLayout()
        
        export_csv_btn = QPushButton("Export CSV")
        export_csv_btn.clicked.connect(lambda: self.export_records('csv'))
        bottom_layout.addWidget(export_csv_btn)
        
        export_json_btn = QPushButton("Export JSON")
        export_json_btn.clicked.connect(lambda: self.export_records('json'))
        bottom_layout.addWidget(export_json_btn)
        
        bottom_layout.addStretch()
        
        self.record_count_label = QLabel("Total: 0 annotations")
        bottom_layout.addWidget(self.record_count_label)
        
        layout.addLayout(bottom_layout)
        
        return widget
    
    def update_records_table(self, search_query=""):
        self.records_table.setRowCount(0)
        count = 0
        
        for i, ann in enumerate(self.annotation_manager.annotations):
            if search_query and search_query.lower() not in ann.text.lower() \
               and search_query.lower() not in ann.code.lower():
                continue
            
            row = self.records_table.rowCount()
            self.records_table.insertRow(row)
            
            self.records_table.setItem(row, 0, QTableWidgetItem(str(i + 1)))
            self.records_table.setItem(row, 1, QTableWidgetItem(str(ann.start)))
            self.records_table.setItem(row, 2, QTableWidgetItem(str(ann.end)))
            
            text_item = QTableWidgetItem(ann.text[:100])
            color = self.annotation_manager.code_colors.get(ann.code, '#FFFFFF')
            text_item.setBackground(QColor(color))
            self.records_table.setItem(row, 3, text_item)
            
            code_item = QTableWidgetItem(ann.code)
            code_item.setBackground(QColor(color))
            self.records_table.setItem(row, 4, code_item)
            
            self.records_table.setItem(row, 5, QTableWidgetItem(ann.memo[:50]))
            count += 1
        
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
        Parse HTML content to extract annotations
        
        Args:
            html_content: HTML string with annotations
            
        Returns:
            List of annotation dictionaries
        """
        import re
        
        annotations = []
        
        # Pattern to match annotated spans: <span style="background-color:#COLOR;..." title="MEMO">TEXT <strong>[CODE]</strong></span>
        # This matches the format created by save_annotation method
        pattern = r'<span style="background-color:([^;"]+);[^"]*"(?:\s+title="([^"]*)")?>([^<]+)\s*<strong>\[([^\]]+)\]</strong></span>'
        
        matches = re.finditer(pattern, html_content)
        
        for i, match in enumerate(matches):
            color = match.group(1)
            memo = match.group(2) if match.group(2) else ""
            text = match.group(3).strip()
            code = match.group(4)
            
            annotations.append({
                'id': i,
                'text': text,
                'code': code,
                'memo': memo,
                'color': color
            })
        
        return annotations
    
    def run_comparison(self):
        if not all(self.comparison_data):
            QMessageBox.warning(self, "Warning", "Load both files first")
            return
        
        data1, data2 = self.comparison_data
        
        codes1 = Counter(d.get('code', '') for d in data1)
        codes2 = Counter(d.get('code', '') for d in data2)
        
        all_codes = sorted(set(codes1.keys()) | set(codes2.keys()))
        
        self.comparison_figure.clear()
        ax = self.comparison_figure.add_subplot(111)
        
        x = np.arange(len(all_codes))
        width = 0.35
        
        counts1 = [codes1.get(c, 0) for c in all_codes]
        counts2 = [codes2.get(c, 0) for c in all_codes]
        
        ax.bar(x - width/2, counts1, width, label='File 1', color='steelblue')
        ax.bar(x + width/2, counts2, width, label='File 2', color='coral')
        
        ax.set_xlabel('Codes')
        ax.set_ylabel('Count')
        ax.set_title('Code Distribution Comparison')
        ax.set_xticks(x)
        ax.set_xticklabels(all_codes, rotation=45, ha='right')
        ax.legend()
        
        self.comparison_figure.tight_layout()
        self.comparison_canvas.draw()
        
        summary = "Comparison Summary\n\n"
        summary += f"File 1: {len(data1)} annotations, {len(codes1)} unique codes\n"
        summary += f"File 2: {len(data2)} annotations, {len(codes2)} unique codes\n\n"
        
        shared = set(codes1.keys()) & set(codes2.keys())
        summary += f"Shared codes: {len(shared)}\n"
        summary += f"Unique to File 1: {len(codes1.keys() - codes2.keys())}\n"
        summary += f"Unique to File 2: {len(codes2.keys() - codes1.keys())}\n"
        
        self.comparison_summary.setPlainText(summary)


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    window = VoxScribeGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()