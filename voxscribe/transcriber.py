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
Audio transcription module using faster-whisper with MAXIMUM PERFORMANCE OPTIMIZATIONS
ENHANCED WITH EFFICIENT BATCH PROCESSING AND SPEED IMPROVEMENTS
"""

import logging
import os
from pathlib import Path
import sys
import threading
import time
from typing import Any, Callable, Dict, List, Optional, Tuple

try:
    import torch
except ImportError:
    torch = None


def _get_default_cache_dir() -> Path:
    """Return a writable cache directory for downloaded models."""
    local_app_data = os.getenv("LOCALAPPDATA")
    if local_app_data:
        return Path(local_app_data) / "VoxScribe" / "cache"

    xdg_cache_home = os.getenv("XDG_CACHE_HOME")
    if xdg_cache_home:
        return Path(xdg_cache_home) / "voxscribe"

    return Path.home() / ".cache" / "voxscribe"


APP_CACHE_DIR = _get_default_cache_dir()
HF_HOME_DIR = APP_CACHE_DIR / "huggingface"
REQUIRED_MODEL_FILES = ("config.json", "model.bin", "tokenizer.json", "vocabulary.txt")

# Packaged Windows builds are more reliable with a deterministic writable cache
# and the standard HTTP download path instead of the optional Xet transport.
os.environ.setdefault("HF_HOME", str(HF_HOME_DIR))
os.environ.setdefault("HF_HUB_CACHE", str(HF_HOME_DIR / "hub"))
os.environ.setdefault("HF_XET_CACHE", str(HF_HOME_DIR / "xet"))
os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
os.environ.setdefault("HF_HUB_ETAG_TIMEOUT", "30")
os.environ.setdefault("HF_HUB_DOWNLOAD_TIMEOUT", "120")
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

LOCAL_FASTER_WHISPER_PATH = r"C:\Users\psych\Downloads\faster-whisper"
if os.path.isdir(LOCAL_FASTER_WHISPER_PATH) and LOCAL_FASTER_WHISPER_PATH not in sys.path:
    sys.path.insert(0, LOCAL_FASTER_WHISPER_PATH)

from faster_whisper import WhisperModel
from concurrent.futures import ThreadPoolExecutor, as_completed
try:
    from faster_whisper import BatchedInferencePipeline
except ImportError:
    BatchedInferencePipeline = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _torch_cuda_available() -> bool:
    """Return True when torch is installed and CUDA is available."""
    return torch is not None and torch.cuda.is_available()


def _is_complete_model_dir(model_dir: Path) -> bool:
    """Return True when a directory contains the required faster-whisper files."""
    return model_dir.is_dir() and all((model_dir / filename).is_file() for filename in REQUIRED_MODEL_FILES)


def _iter_runtime_roots() -> List[Path]:
    """Return candidate roots for bundled runtime data."""
    roots: List[Path] = []
    seen: set[Path] = set()

    candidates = [
        Path(getattr(sys, "_MEIPASS", "")) if getattr(sys, "_MEIPASS", None) else None,
        Path(__file__).resolve().parent,
        Path(sys.executable).resolve().parent,
        Path(sys.executable).resolve().parent / "_internal",
    ]

    for candidate in candidates:
        if candidate is None:
            continue
        try:
            resolved = candidate.resolve()
        except OSError:
            continue
        if resolved in seen or not resolved.exists():
            continue
        seen.add(resolved)
        roots.append(resolved)

    return roots


def _find_snapshot_dir(cache_dir: Path) -> Optional[Path]:
    """Return a complete snapshot directory from a Hugging Face cache folder."""
    refs_main = cache_dir / "refs" / "main"
    snapshots_dir = cache_dir / "snapshots"

    if refs_main.is_file():
        revision = refs_main.read_text(encoding="utf-8").strip()
        if revision:
            candidate = snapshots_dir / revision
            if _is_complete_model_dir(candidate):
                return candidate

    if snapshots_dir.is_dir():
        for candidate in sorted(snapshots_dir.iterdir(), reverse=True):
            if _is_complete_model_dir(candidate):
                return candidate

    return None


class AudioTranscriber:
    """
    Handles audio transcription using faster-whisper with maximum speed optimizations
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
        self.batched_model = None
        self.batch_size = self._detect_optimal_batch_size()
        self.progress_update_interval = 0.5
        
        logger.info(
            "Configured device: %s, compute_type: %s, batch_size: %s",
            self.device,
            self.compute_type,
            self.batch_size,
        )
    
    def _detect_best_device(self) -> str:
        """
        Detect the best available device (CUDA > CPU)
        
        Returns:
            Device string ('cuda' or 'cpu')
        """
        if torch is None:
            logger.info("PyTorch not installed; using CPU mode")
            return "cpu"

        try:
            if _torch_cuda_available():
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
            # OPTIMIZATION: Use int8_float16 for maximum speed on GPU
            # This is faster than float16 alone with minimal accuracy loss
            return "int8_float16"
        else:
            # int8 is fastest on CPU
            return "int8"

    def _detect_optimal_batch_size(self) -> int:
        """
        Detect the best default batch size for transcription.

        Returns:
            Batch size for inference. Values > 1 enable batched inference.
        """
        override = os.getenv("VOXSCRIBE_BATCH_SIZE")
        if override:
            try:
                return max(1, int(override))
            except ValueError:
                logger.warning("Ignoring invalid VOXSCRIBE_BATCH_SIZE=%s", override)

        if self.device == "cuda":
            return 8

        return 1

    def _should_use_batched_inference(self) -> bool:
        """Return True when faster-whisper batched inference should be used."""
        return (
            self.batch_size > 1
            and BatchedInferencePipeline is not None
            and self.model is not None
        )

    def _get_model_repo_id(self) -> str:
        """Return the Hugging Face repo id used by faster-whisper."""
        return f"Systran/faster-whisper-{self.model_size}"

    def _get_model_cache_dir(self) -> Path:
        """Return the local cache directory for the selected model."""
        return APP_CACHE_DIR / f"models--{self._get_model_repo_id().replace('/', '--')}"

    def _get_bundled_model_dir(self, model_size: Optional[str] = None) -> Optional[Path]:
        """Return a bundled model directory when one exists in the packaged app."""
        selected_model = model_size or self.model_size
        relative_path = Path("bundled_models") / f"faster-whisper-{selected_model}"

        for runtime_root in _iter_runtime_roots():
            candidate = runtime_root / relative_path
            if _is_complete_model_dir(candidate):
                return candidate

        return None

    def _get_cached_model_dir(self) -> Optional[Path]:
        """Return a fully materialized cached snapshot directory."""
        return _find_snapshot_dir(self._get_model_cache_dir())

    def _get_local_model_source(self) -> Tuple[Optional[str], Optional[Path]]:
        """Return ('bundled'|'cache', path) when the model exists locally."""
        bundled_model_dir = self._get_bundled_model_dir()
        if bundled_model_dir is not None:
            return "bundled", bundled_model_dir

        cached_model_dir = self._get_cached_model_dir()
        if cached_model_dir is not None:
            return "cache", cached_model_dir

        return None, None

    def is_model_cached(self) -> bool:
        """Return True when the selected model already exists locally."""
        source_type, source_path = self._get_local_model_source()
        return source_type is not None and source_path is not None

    def _build_model_status_message(self, source_type: Optional[str]) -> str:
        """Return the appropriate status message for model initialization."""
        if source_type == "bundled":
            return f"Loading bundled {self.model_size} model..."
        if source_type == "cache":
            return f"Loading cached {self.model_size} model..."
        return f"Downloading {self.model_size} model files (first run only)..."

    def _start_model_status_notifier(
        self,
        status_callback: Optional[Callable[[int, str], None]],
        status_message: str,
    ) -> tuple[threading.Event, Optional[threading.Thread]]:
        """
        Emit keep-alive progress updates while the model loads or downloads.

        faster-whisper does not expose model download progress during
        initialization, so without this the GUI can appear frozen at 5%.
        """
        stop_event = threading.Event()
        if status_callback is None:
            return stop_event, None

        status_callback(5, status_message)

        def emit_status() -> None:
            progress_pct = 5
            while not stop_event.wait(self.progress_update_interval):
                progress_pct = min(9, progress_pct + 1)
                status_callback(progress_pct, status_message)

        notifier_thread = threading.Thread(
            target=emit_status,
            name="voxscribe-model-load-progress",
            daemon=True,
        )
        notifier_thread.start()
        return stop_event, notifier_thread
    
    def load_model(
        self,
        status_callback: Optional[Callable[[int, str], None]] = None,
    ) -> None:
        """Load the faster-whisper model with maximum optimizations"""
        source_type, local_model_dir = self._get_local_model_source()
        stop_event, notifier_thread = self._start_model_status_notifier(
            status_callback,
            self._build_model_status_message(source_type),
        )
        try:
            cache_dir = APP_CACHE_DIR
            cache_dir.mkdir(parents=True, exist_ok=True)
            
            logger.info(
                "Loading model: %s on %s (%s) using cache %s",
                self.model_size,
                self.device,
                self.compute_type,
                cache_dir,
            )
            if local_model_dir is not None:
                logger.info(
                    "Using %s %s model from %s",
                    source_type,
                    self.model_size,
                    local_model_dir,
                )
            else:
                logger.info(
                    "Model %s is not cached yet; downloading files before transcription starts",
                    self._get_model_repo_id(),
                )
            
            # OPTIMIZATION: Use optimal CPU thread count
            import multiprocessing
            cpu_threads = min(multiprocessing.cpu_count(), 16) if self.device == "cpu" else 0
            
            # Additional optimizations for model loading
            model_reference = str(local_model_dir) if local_model_dir is not None else self.model_size
            model_kwargs = {
                "device": self.device,
                "compute_type": self.compute_type,
                "cpu_threads": cpu_threads,
                "num_workers": 1,
            }
            if local_model_dir is None:
                model_kwargs["download_root"] = str(cache_dir)

            self.model = WhisperModel(
                model_reference,
                **model_kwargs,
            )
            self.batched_model = None
            if self._should_use_batched_inference():
                self.batched_model = BatchedInferencePipeline(self.model)
                logger.info(
                    "Enabled batched inference pipeline (batch_size=%s)",
                    self.batch_size,
                )

            logger.info(f"Model loaded successfully (CPU threads: {cpu_threads})")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise self._format_model_load_error(e) from e
        finally:
            stop_event.set()
            if notifier_thread is not None:
                notifier_thread.join(timeout=0.2)

    def _format_model_load_error(self, error: Exception) -> RuntimeError:
        """Convert low-level model download/load failures into a user-facing error."""
        error_message = str(error).strip()
        lower_error = error_message.lower()
        bundled_base_available = self._get_bundled_model_dir("base") is not None

        if any(
            token in lower_error
            for token in (
                "connecttimeout",
                "connection attempt failed",
                "readtimeout",
                "timed out",
                "localentrynotfounderror",
                "snapshot folder",
                "cannot find the appropriate snapshot folder",
                "offline mode",
            )
        ):
            message = (
                f"Unable to download the '{self.model_size}' transcription model. "
                "Please verify that huggingface.co is reachable from this device and try again."
            )
            if bundled_base_available and self.model_size != "base":
                message += (
                    " The packaged app already includes the offline 'base' model. "
                    "Switch the model setting to 'base' to transcribe without downloading a new model."
                )
            return RuntimeError(message)

        return RuntimeError(
            f"Unable to load the '{self.model_size}' transcription model. {error_message}"
        )
    
    def transcribe(
        self,
        audio_path: str,
        language: Optional[str] = None,
        beam_size: int = 1,  # OPTIMIZATION: Default to 1 for maximum speed
        vad_filter: bool = True,
        include_timestamps: bool = True,
        word_timestamps: bool = False,
        progress_callback: Optional[Callable[[int, Optional[float], Optional[float], Optional[float]], None]] = None
    ) -> List[Dict[str, any]]:
        """
        Transcribe audio file with MAXIMUM SPEED optimizations
        
        SPEED IMPROVEMENTS:
        - beam_size=1 (greedy decoding) is 3-5x faster than beam_size=5
        - VAD filtering removes silence (20-40% speed improvement)
        - Optimized VAD parameters for speed
        - Disabled features that slow down processing
        
        Args:
            audio_path: Path to audio file
            language: Language code (e.g., 'en', 'es', None for auto-detect)
            beam_size: Beam size for decoding (1=fastest, 5=better quality)
            vad_filter: Use voice activity detection to filter out non-speech
            include_timestamps: Include segment-level timestamps
            word_timestamps: Include word-level timestamps (slower)
            progress_callback: Optional callback(segment_count, processed_duration, total_duration, elapsed_time)
            
        Returns:
            List of segment dictionaries with text and optionally timestamps
        """
        if self.model is None:
            self.load_model()
        
        try:
            logger.info(f"Transcribing: {audio_path} (beam_size={beam_size}, vad_filter={vad_filter})")
            
            # Get total audio duration for progress tracking
            total_duration = None
            if progress_callback:
                try:
                    import soundfile as sf
                    with sf.SoundFile(audio_path) as audio_file:
                        total_duration = len(audio_file) / audio_file.samplerate
                        logger.info(f"Audio duration: {total_duration:.2f} seconds")
                except Exception as e:
                    logger.warning(f"Could not determine audio duration: {e}")
            
            # Start timing
            start_time = time.time()
            
            # OPTIMIZATION: Ultra-fast VAD parameters
            vad_params = {
                "threshold": 0.5,
                "min_speech_duration_ms": 250,  # Increased for speed
                "max_speech_duration_s": float('inf'),
                "min_silence_duration_ms": 200,  # Increased for speed
                "speech_pad_ms": 300  # Reduced for speed
            } if vad_filter else None
            
            transcribe_kwargs = {
                "language": language,
                "beam_size": beam_size,
                "best_of": 1 if beam_size == 1 else beam_size,
                "vad_filter": vad_filter,
                "vad_parameters": vad_params,
                "word_timestamps": word_timestamps and include_timestamps,
                "condition_on_previous_text": False,
                "temperature": 0.0,
                "compression_ratio_threshold": 2.4,
                "log_prob_threshold": -1.0,
                "no_speech_threshold": 0.6,
                "initial_prompt": None,
                "suppress_blank": True,
                "suppress_tokens": [-1],
                "without_timestamps": not include_timestamps,
                "language_detection_segments": 1,
            }

            transcribe_callable = self.model.transcribe
            if self.batched_model is not None:
                transcribe_callable = self.batched_model.transcribe
                transcribe_kwargs["batch_size"] = self.batch_size

            # OPTIMIZATION: Maximum speed transcription parameters
            segments, info = transcribe_callable(audio_path, **transcribe_kwargs)
            
            logger.info(f"Detected language: {info.language} (probability: {info.language_probability:.2f})")
            
            results = []
            segment_count = 0
            last_progress_emit = start_time
            last_processed_duration = None
            
            # OPTIMIZATION: Process segments with minimal overhead
            for segment in segments:
                segment_dict = {
                    'text': segment.text.strip(),
                    'id': segment.id
                }
                
                # Add timestamps only if requested
                if include_timestamps:
                    segment_dict['start'] = segment.start
                    segment_dict['end'] = segment.end
                    
                    # Only add word timestamps if explicitly requested
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
                    processed_duration = segment.end if include_timestamps else None
                    now = time.time()
                    if (
                        segment_count == 1
                        or now - last_progress_emit >= self.progress_update_interval
                    ):
                        elapsed_time = now - start_time
                        progress_callback(
                            segment_count,
                            processed_duration,
                            total_duration,
                            elapsed_time,
                        )
                        last_progress_emit = now
                        last_processed_duration = processed_duration
                
                if include_timestamps:
                    logger.debug(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}")
                else:
                    logger.debug(f"Segment {segment_count}: {segment.text}")

            if progress_callback and segment_count > 0:
                final_duration = results[-1].get('end') if include_timestamps else None
                if final_duration != last_processed_duration:
                    progress_callback(
                        segment_count,
                        final_duration,
                        total_duration,
                        time.time() - start_time,
                    )
            
            elapsed = time.time() - start_time
            if total_duration:
                rtf = elapsed / total_duration  # Real-time factor
                logger.info(f"Transcription complete: {len(results)} segments in {elapsed:.2f}s (RTF: {rtf:.2f}x)")
            else:
                logger.info(f"Transcription complete: {len(results)} segments in {elapsed:.2f}s")
            
            return results
            
        except Exception as e:
            logger.error(f"Error during transcription: {e}")
            raise
    
    def transcribe_batch(
        self,
        audio_paths: List[str],
        language: Optional[str] = None,
        beam_size: int = 1,  # OPTIMIZATION: Default to 1 for speed
        vad_filter: bool = True,
        include_timestamps: bool = True,
        word_timestamps: bool = False,
        batch_progress_callback: Optional[Callable[[int, int, str], None]] = None,
        **kwargs
    ) -> List[Dict[str, any]]:
        """
        Transcribe multiple audio files sequentially (GPU-safe, optimized)
        
        Args:
            audio_paths: List of paths to audio files
            language: Language code
            beam_size: Beam size for decoding (1=fastest)
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
        batch_start = time.time()
        
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
        batch_elapsed = time.time() - batch_start
        successful = sum(1 for r in batch_results if r['success'])
        failed = total_files - successful
        total_segments = sum(r['segments_count'] for r in batch_results if r['success'])
        
        logger.info(f"Batch complete in {batch_elapsed:.2f}s: {successful} successful, {failed} failed "
                   f"({total_segments} segments)")
        
        return batch_results
    
    def transcribe_batch_parallel(
        self,
        audio_paths: List[str],
        max_workers: int = 2,
        language: Optional[str] = None,
        beam_size: int = 1,  # OPTIMIZATION: Default to 1
        vad_filter: bool = True,
        include_timestamps: bool = True,
        word_timestamps: bool = False,
        batch_progress_callback: Optional[Callable[[int, int, str], None]] = None,
        **kwargs
    ) -> List[Dict[str, any]]:
        """
        Transcribe multiple audio files in parallel (CPU recommended)
        
        WARNING: Parallel processing on GPU can cause out-of-memory errors.
        Recommended: max_workers=1 for GPU, max_workers=2-4 for CPU
        
        OPTIMIZATION: For CPU, parallel processing can provide 2-3x speedup
        
        Args:
            audio_paths: List of paths to audio files
            max_workers: Maximum parallel workers (conservative with GPU)
            language: Language code
            beam_size: Beam size for decoding (1=fastest)
            vad_filter: Use VAD filter
            include_timestamps: Include timestamps
            word_timestamps: Include word timestamps
            batch_progress_callback: Callback(completed_count, total_files, filename)
            **kwargs: Additional arguments
            
        Returns:
            List of results in the same order as audio_paths
        """
        if self.device == "cuda":
            logger.warning("Parallel processing on GPU may cause memory issues. Using max_workers=1")
            max_workers = 1
        else:
            # OPTIMIZATION: For CPU, allow more workers for speedup
            import multiprocessing
            max_workers = min(max_workers, multiprocessing.cpu_count() // 2)
            logger.info(f"Using {max_workers} parallel workers for CPU processing")
        
        use_shared_transcriber = max_workers == 1
        if use_shared_transcriber and self.model is None:
            self.load_model()

        thread_local = threading.local()

        def get_worker_transcriber():
            if use_shared_transcriber:
                return self
            worker = getattr(thread_local, "transcriber", None)
            if worker is None:
                worker = AudioTranscriber(
                    model_size=self.model_size,
                    device=self.device,
                    compute_type=self.compute_type
                )
                worker.load_model()
                thread_local.transcriber = worker
            return worker
        
        total_files = len(audio_paths)
        batch_results = [None] * total_files
        completed = 0
        batch_start = time.time()
        
        def process_single_file(index: int, path: str) -> tuple:
            """Process a single file and return (index, result)"""
            filename = Path(path).name
            try:
                start_time = time.time()
                transcriber = get_worker_transcriber()
                result = transcriber.transcribe(
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
            future_to_index = {
                executor.submit(process_single_file, i, path): i 
                for i, path in enumerate(audio_paths)
            }
            
            for future in as_completed(future_to_index):
                index, result = future.result()
                batch_results[index] = result
                completed += 1
                
                if batch_progress_callback:
                    batch_progress_callback(completed, total_files, result['filename'])
                
                logger.info(f"Completed {completed}/{total_files}: {result['filename']}")
        
        # Summary
        batch_elapsed = time.time() - batch_start
        successful = sum(1 for r in batch_results if r and r['success'])
        failed = total_files - successful
        total_segments = sum(r['segments_count'] for r in batch_results if r and r['success'])
        
        logger.info(f"Parallel batch complete in {batch_elapsed:.2f}s: {successful} successful, "
                   f"{failed} failed ({total_segments} segments)")
        
        return batch_results
    
    def change_model(
        self,
        model_size: str,
        device: Optional[str] = None,
        compute_type: Optional[str] = None,
        status_callback: Optional[Callable[[int, str], None]] = None,
    ) -> None:
        """
        Change the model size and reload
        
        Args:
            model_size: New model size
            device: New device (optional, uses auto-detect if None)
            compute_type: New compute type (optional, uses auto-detect if None)
            status_callback: Optional callback used while the model loads
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
        self.batched_model = None
        self.load_model(status_callback=status_callback)
    
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
            "model_loaded": self.model is not None,
            "torch_available": torch is not None,
        }
        
        if self.device == "cuda":
            try:
                info["cuda_available"] = _torch_cuda_available()
                if _torch_cuda_available():
                    info["cuda_device_name"] = torch.cuda.get_device_name(0)
                    info["cuda_device_count"] = torch.cuda.device_count()
            except Exception as e:
                info["cuda_error"] = str(e)
        
        return info
