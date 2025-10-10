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
Text annotation and management module
"""

import json
from typing import List, Dict, Optional
from datetime import datetime


class TextAnnotator:
    """
    Manages text annotations and edits
    """
    
    def __init__(self):
        self.segments: List[Dict] = []
        self.annotations: Dict[int, Dict] = {}
        self.history: List[Dict] = []
        
    def load_segments(self, segments: List[Dict]) -> None:
        """
        Load transcription segments
        
        Args:
            segments: List of segment dictionaries
        """
        self.segments = segments
        self.annotations = {i: {} for i in range(len(segments))}
        
    def update_segment_text(self, segment_id: int, new_text: str) -> None:
        """
        Update the text of a segment
        
        Args:
            segment_id: Index of the segment
            new_text: New text content
        """
        if 0 <= segment_id < len(self.segments):
            old_text = self.segments[segment_id]['text']
            self.segments[segment_id]['text'] = new_text
            
            # Record in history
            self.history.append({
                'timestamp': datetime.now().isoformat(),
                'action': 'edit',
                'segment_id': segment_id,
                'old_text': old_text,
                'new_text': new_text
            })
    
    def add_annotation(
        self,
        segment_id: int,
        annotation_type: str,
        content: str
    ) -> None:
        """
        Add an annotation to a segment
        
        Args:
            segment_id: Index of the segment
            annotation_type: Type of annotation (note, label, correction, etc.)
            content: Annotation content
        """
        if 0 <= segment_id < len(self.segments):
            if annotation_type not in self.annotations[segment_id]:
                self.annotations[segment_id][annotation_type] = []
            
            self.annotations[segment_id][annotation_type].append({
                'content': content,
                'timestamp': datetime.now().isoformat()
            })
            
            # Record in history
            self.history.append({
                'timestamp': datetime.now().isoformat(),
                'action': 'annotate',
                'segment_id': segment_id,
                'annotation_type': annotation_type,
                'content': content
            })
    
    def merge_segments(self, segment_ids: List[int]) -> Optional[int]:
        """
        Merge multiple segments into one
        
        Args:
            segment_ids: List of segment indices to merge
            
        Returns:
            Index of the merged segment, or None if failed
        """
        if not segment_ids or len(segment_ids) < 2:
            return None
        
        segment_ids = sorted(segment_ids)
        
        # Check all IDs are valid
        if not all(0 <= sid < len(self.segments) for sid in segment_ids):
            return None
        
        # Create merged segment
        merged_text = ' '.join(self.segments[sid]['text'] for sid in segment_ids)
        merged_segment = {
            'text': merged_text,
            'id': self.segments[segment_ids[0]].get('id', segment_ids[0])
        }
        
        # Add timestamps only if they exist in the original segments
        if 'start' in self.segments[segment_ids[0]] and 'end' in self.segments[segment_ids[-1]]:
            merged_segment['start'] = self.segments[segment_ids[0]]['start']
            merged_segment['end'] = self.segments[segment_ids[-1]]['end']
        
        # Replace first segment with merged, remove others
        self.segments[segment_ids[0]] = merged_segment
        
        # Remove merged segments (in reverse to maintain indices)
        for sid in reversed(segment_ids[1:]):
            del self.segments[sid]
            del self.annotations[sid]
        
        # Reindex annotations
        self.annotations = {i: self.annotations.get(i, {}) 
                          for i in range(len(self.segments))}
        
        return segment_ids[0]
    
    def split_segment(
        self,
        segment_id: int,
        split_time: float
    ) -> Optional[tuple[int, int]]:
        """
        Split a segment at a specific time
        Only works if timestamps are available
        
        Args:
            segment_id: Index of the segment to split
            split_time: Time to split at (in seconds)
            
        Returns:
            Tuple of (first_segment_id, second_segment_id) or None if failed
        """
        if not (0 <= segment_id < len(self.segments)):
            return None
        
        segment = self.segments[segment_id]
        
        # Check if segment has timestamps
        if 'start' not in segment or 'end' not in segment:
            return None
        
        if not (segment['start'] < split_time < segment['end']):
            return None
        
        # Create two segments (text split is approximate)
        text = segment['text']
        mid = len(text) // 2
        
        first_segment = {
            'start': segment['start'],
            'end': split_time,
            'text': text[:mid].strip(),
            'id': segment.get('id', segment_id)
        }
        
        second_segment = {
            'start': split_time,
            'end': segment['end'],
            'text': text[mid:].strip(),
            'id': segment.get('id', segment_id)
        }
        
        # Replace and insert
        self.segments[segment_id] = first_segment
        self.segments.insert(segment_id + 1, second_segment)
        
        # Reindex annotations
        self.annotations = {i: self.annotations.get(i, {}) 
                          for i in range(len(self.segments))}
        
        return (segment_id, segment_id + 1)
    
    def export_to_json(self, filepath: str) -> None:
        """
        Export segments and annotations to JSON
        
        Args:
            filepath: Path to save JSON file
        """
        data = {
            'segments': self.segments,
            'annotations': {str(k): v for k, v in self.annotations.items()},
            'history': self.history,
            'export_time': datetime.now().isoformat()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def export_to_srt(self, filepath: str) -> None:
        """
        Export segments to SRT subtitle format
        Only works if segments have timestamps
        
        Args:
            filepath: Path to save SRT file
        """
        # Check if any segment has timestamps
        has_timestamps = any('start' in seg and 'end' in seg for seg in self.segments)
        
        if not has_timestamps:
            raise ValueError("Cannot export to SRT: segments do not have timestamps. "
                           "Enable timestamps when transcribing to use SRT export.")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            srt_index = 1
            for i, segment in enumerate(self.segments):
                # Skip segments without timestamps
                if 'start' not in segment or 'end' not in segment:
                    continue
                    
                start = self._format_srt_time(segment['start'])
                end = self._format_srt_time(segment['end'])
                
                f.write(f"{srt_index}\n")
                f.write(f"{start} --> {end}\n")
                f.write(f"{segment['text']}\n\n")
                srt_index += 1
    
    def export_to_txt(self, filepath: str) -> None:
        """
        Export segments to plain text
        Works with or without timestamps
        
        Args:
            filepath: Path to save text file
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            for segment in self.segments:
                f.write(f"{segment['text']}\n")
    
    @staticmethod
    def _format_srt_time(seconds: float) -> str:
        """Format time for SRT format (HH:MM:SS,mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"