"""
Audio transcription module using faster-whisper with performance optimizations
ENHANCED WITH EFFICIENT BATCH PROCESSING
"""

from faster_whisper import WhisperModel
from typing import List, Dict, Optional, Callable
import logging
import torch
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AudioTranscriber:
    """
    Handles audio transcription using faster-whisper with optimizations
    """
    
    def __init__(
        self,
        model_size: str = "base",
        device: Optional[str] = None,
        compute_type: Optional[str] = None
    ):
        """
        Initialize the transcriber with a faster-whisper model
        
        Args:
            model_size: Size of the model (tiny, base, small, medium, large-v2, large-v3)
            device: Device to run on (auto, cpu, cuda) - auto detects best available
            compute_type: Computation type (auto, int8, float16, float32)
        """
        self.model_size = model_size
        
        # Auto-detect best device and compute type if not specified
        if device is None or device == "auto":
            self.device = self._detect_best_device()
        else:
            self.device = device
            
        if compute_type is None or compute_type == "auto":
            self.compute_type = self._detect_best_compute_type()
        else:
            self.compute_type = compute_type
        
        self.model = None
        
        logger.info(f"Configured device: {self.device}, compute_type: {self.compute_type}")
    
    def _detect_best_device(self) -> str:
        """
        Detect the best available device (CUDA > CPU)
        
        Returns:
            Device string ('cuda' or 'cpu')
        """
        try:
            if torch.cuda.is_available():
                logger.info(f"CUDA available: {torch.cuda.get_device_name(0)}")
                return "cuda"
        except Exception as e:
            logger.warning(f"Error checking CUDA: {e}")
        
        logger.info("Using CPU (CUDA not available)")
        return "cpu"
    
    def _detect_best_compute_type(self) -> str:
        """
        Detect the best compute type based on device
        
        Returns:
            Compute type string
        """
        if self.device == "cuda":
            # float16 is much faster on GPU and maintains good accuracy
            return "float16"
        else:
            # int8 is faster on CPU with minimal accuracy loss
            return "int8"
    
    def load_model(self) -> None:
        """Load the faster-whisper model with optimizations"""
        try:
            # Check if model needs downloading
            cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "voxscribe")
            os.makedirs(cache_dir, exist_ok=True)
            
            logger.info(f"Loading model: {self.model_size} on {self.device} ({self.compute_type})")
            
            # Additional optimizations for model loading
            self.model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type,
                download_root=cache_dir,
                # Use CPU threads for better performance when on CPU
                cpu_threads=4 if self.device == "cpu" else 0,
                # Number of workers for parallel processing
                num_workers=1
            )
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
    
    def transcribe(
        self,
        audio_path: str,
        language: Optional[str] = None,
        beam_size: int = 5,
        vad_filter: bool = True,
        include_timestamps: bool = True,
        word_timestamps: bool = False,
        progress_callback: Optional[Callable[[int], None]] = None
    ) -> List[Dict[str, any]]:
        """
        Transcribe audio file with optimizations
        
        Args:
            audio_path: Path to audio file
            language: Language code (e.g., 'en', 'es', None for auto-detect)
            beam_size: Beam size for decoding (lower = faster, 1-5 recommended)
            vad_filter: Use voice activity detection to filter out non-speech
            include_timestamps: Include segment-level timestamps (faster if disabled)
            word_timestamps: Include word-level timestamps (only if include_timestamps=True)
            progress_callback: Optional callback function for progress updates
            
        Returns:
            List of segment dictionaries with text and optionally timestamps
        """
        if self.model is None:
            self.load_model()
        
        try:
            logger.info(f"Transcribing: {audio_path}")
            
            # Optimize beam_size for speed (5 is good balance, 1 is fastest)
            optimal_beam_size = min(beam_size, 5)
            
            # Determine if we should use timestamps at all
            use_timestamps = include_timestamps
            
            # Optimized transcription parameters
            segments, info = self.model.transcribe(
                audio_path,
                language=language,
                beam_size=optimal_beam_size,
                # VAD parameters for better speed/accuracy
                vad_filter=vad_filter,
                vad_parameters={
                    "threshold": 0.5,
                    "min_speech_duration_ms": 250,
                    "max_speech_duration_s": float('inf'),
                    "min_silence_duration_ms": 100,
                    "speech_pad_ms": 400
                } if vad_filter else None,
                # Performance optimizations
                word_timestamps=word_timestamps if use_timestamps else False,
                condition_on_previous_text=False,  # Faster, slightly less context
                # Temperature for sampling (0 = greedy, faster)
                temperature=0.0,
                # Thresholds for quality control
                compression_ratio_threshold=2.4,
                log_prob_threshold=-1.0,
                no_speech_threshold=0.6,
                # Initial prompt can help with specific content
                initial_prompt=None,
                # Suppress tokens
                suppress_blank=True,
                suppress_tokens=[-1],
                # Without timestamps is faster but less useful
                without_timestamps=not use_timestamps
            )
            
            logger.info(f"Detected language: {info.language} (probability: {info.language_probability:.2f})")
            
            results = []
            segment_count = 0
            
            for segment in segments:
                segment_dict = {
                    'text': segment.text.strip(),
                    'id': segment.id
                }
                
                # Add timestamps only if requested
                if use_timestamps:
                    segment_dict['start'] = segment.start
                    segment_dict['end'] = segment.end
                    
                    # Only add word timestamps if requested (and timestamps are enabled)
                    if word_timestamps and hasattr(segment, 'words') and segment.words:
                        segment_dict['words'] = [
                            {
                                'word': word.word,
                                'start': word.start,
                                'end': word.end,
                                'probability': word.probability
                            }
                            for word in segment.words
                        ]
                
                results.append(segment_dict)
                segment_count += 1
                
                # Call progress callback if provided
                if progress_callback:
                    progress_callback(segment_count)
                
                if use_timestamps:
                    logger.debug(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}")
                else:
                    logger.debug(f"Segment {segment_count}: {segment.text}")
            
            logger.info(f"Transcription complete: {len(results)} segments")
            return results
            
        except Exception as e:
            logger.error(f"Error during transcription: {e}")
            raise
    
    def transcribe_batch(
        self,
        audio_paths: List[str],
        language: Optional[str] = None,
        beam_size: int = 5,
        vad_filter: bool = True,
        include_timestamps: bool = True,
        word_timestamps: bool = False,
        batch_progress_callback: Optional[Callable[[int, int, str], None]] = None,
        **kwargs
    ) -> List[Dict[str, any]]:
        """
        Transcribe multiple audio files sequentially (GPU-safe)
        
        Args:
            audio_paths: List of paths to audio files
            language: Language code
            beam_size: Beam size for decoding
            vad_filter: Use VAD filter
            include_timestamps: Include timestamps
            word_timestamps: Include word timestamps
            batch_progress_callback: Callback(file_index, total_files, filename)
            **kwargs: Additional arguments passed to transcribe()
            
        Returns:
            List of results, each containing {'path', 'filename', 'success', 'results', 'error'}
        """
        if self.model is None:
            self.load_model()
        
        batch_results = []
        total_files = len(audio_paths)
        
        for i, audio_path in enumerate(audio_paths):
            filename = Path(audio_path).name
            logger.info(f"Processing file {i+1}/{total_files}: {filename}")
            
            if batch_progress_callback:
                batch_progress_callback(i + 1, total_files, filename)
            
            try:
                start_time = time.time()
                result = self.transcribe(
                    audio_path,
                    language=language,
                    beam_size=beam_size,
                    vad_filter=vad_filter,
                    include_timestamps=include_timestamps,
                    word_timestamps=word_timestamps,
                    **kwargs
                )
                elapsed = time.time() - start_time
                
                batch_results.append({
                    'path': audio_path,
                    'filename': filename,
                    'success': True,
                    'results': result,
                    'segments_count': len(result),
                    'processing_time': elapsed,
                    'error': None
                })
                
                logger.info(f"✓ Completed {filename} in {elapsed:.2f}s ({len(result)} segments)")
                
            except Exception as e:
                logger.error(f"✗ Error processing {filename}: {e}")
                batch_results.append({
                    'path': audio_path,
                    'filename': filename,
                    'success': False,
                    'results': None,
                    'segments_count': 0,
                    'processing_time': 0,
                    'error': str(e)
                })
        
        # Summary
        successful = sum(1 for r in batch_results if r['success'])
        failed = total_files - successful
        logger.info(f"Batch complete: {successful} successful, {failed} failed out of {total_files}")
        
        return batch_results
    
    def transcribe_batch_parallel(
        self,
        audio_paths: List[str],
        max_workers: int = 2,
        language: Optional[str] = None,
        beam_size: int = 5,
        vad_filter: bool = True,
        include_timestamps: bool = True,
        word_timestamps: bool = False,
        batch_progress_callback: Optional[Callable[[int, int, str], None]] = None,
        **kwargs
    ) -> List[Dict[str, any]]:
        """
        Transcribe multiple audio files in parallel (use with caution on GPU)
        
        WARNING: Parallel processing on GPU can cause out-of-memory errors.
        Recommended: max_workers=1 for GPU, max_workers=2-4 for CPU
        
        Args:
            audio_paths: List of paths to audio files
            max_workers: Maximum parallel workers (be conservative with GPU)
            language: Language code
            beam_size: Beam size for decoding
            vad_filter: Use VAD filter
            include_timestamps: Include timestamps
            word_timestamps: Include word timestamps
            batch_progress_callback: Callback(completed_count, total_files, filename)
            **kwargs: Additional arguments
            
        Returns:
            List of results in the same order as audio_paths
        """
        if self.device == "cuda":
            logger.warning("Parallel processing on GPU may cause memory issues. Consider sequential processing.")
            # Limit workers on GPU
            max_workers = min(max_workers, 1)
        
        if self.model is None:
            self.load_model()
        
        total_files = len(audio_paths)
        batch_results = [None] * total_files  # Maintain order
        completed = 0
        
        def process_single_file(index: int, path: str) -> tuple:
            """Process a single file and return (index, result)"""
            filename = Path(path).name
            try:
                start_time = time.time()
                result = self.transcribe(
                    path,
                    language=language,
                    beam_size=beam_size,
                    vad_filter=vad_filter,
                    include_timestamps=include_timestamps,
                    word_timestamps=word_timestamps,
                    **kwargs
                )
                elapsed = time.time() - start_time
                
                return (index, {
                    'path': path,
                    'filename': filename,
                    'success': True,
                    'results': result,
                    'segments_count': len(result),
                    'processing_time': elapsed,
                    'error': None
                })
            except Exception as e:
                logger.error(f"Error processing {filename}: {e}")
                return (index, {
                    'path': path,
                    'filename': filename,
                    'success': False,
                    'results': None,
                    'segments_count': 0,
                    'processing_time': 0,
                    'error': str(e)
                })
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_index = {
                executor.submit(process_single_file, i, path): i 
                for i, path in enumerate(audio_paths)
            }
            
            # Process as they complete
            for future in as_completed(future_to_index):
                index, result = future.result()
                batch_results[index] = result
                completed += 1
                
                if batch_progress_callback:
                    batch_progress_callback(completed, total_files, result['filename'])
                
                logger.info(f"Completed {completed}/{total_files}: {result['filename']}")
        
        # Summary
        successful = sum(1 for r in batch_results if r and r['success'])
        failed = total_files - successful
        logger.info(f"Parallel batch complete: {successful} successful, {failed} failed")
        
        return batch_results
    
    def change_model(
        self,
        model_size: str,
        device: Optional[str] = None,
        compute_type: Optional[str] = None
    ) -> None:
        """
        Change the model size and reload
        
        Args:
            model_size: New model size
            device: New device (optional, uses auto-detect if None)
            compute_type: New compute type (optional, uses auto-detect if None)
        """
        self.model_size = model_size
        
        if device:
            self.device = device
        else:
            self.device = self._detect_best_device()
        
        if compute_type:
            self.compute_type = compute_type
        else:
            self.compute_type = self._detect_best_compute_type()
        
        self.model = None
        self.load_model()
    
    def get_device_info(self) -> Dict[str, any]:
        """
        Get information about the current device configuration
        
        Returns:
            Dictionary with device information
        """
        info = {
            "device": self.device,
            "compute_type": self.compute_type,
            "model_size": self.model_size,
            "model_loaded": self.model is not None
        }
        
        if self.device == "cuda":
            try:
                info["cuda_available"] = torch.cuda.is_available()
                if torch.cuda.is_available():
                    info["cuda_device_name"] = torch.cuda.get_device_name(0)
                    info["cuda_device_count"] = torch.cuda.device_count()
            except Exception as e:
                info["cuda_error"] = str(e)
        
        return info