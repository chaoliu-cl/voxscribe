"""
VoxScribe Usage Examples
=========================

This file demonstrates how to use the VoxScribe package for:
1. Audio transcription (single and batch)
2. Text annotation and coding
3. Exporting results in various formats

Requirements:
- Audio files for transcription (wav, mp3, m4a, flac, ogg)
- VoxScribe package installed
"""

import os
from pathlib import Path
from voxscribe import AudioTranscriber, TextAnnotator


# ============================================================================
# EXAMPLE 1: Basic Audio Transcription (Single File)
# ============================================================================

def example_basic_transcription():
    """
    Demonstrates basic single-file transcription with timestamps
    """
    print("\n" + "="*70)
    print("EXAMPLE 1: Basic Audio Transcription")
    print("="*70)
    
    # Initialize transcriber (auto-detects best device: CUDA or CPU)
    transcriber = AudioTranscriber(
        model_size="base",      # Options: tiny, base, small, medium, large-v2, large-v3
        device="auto",          # Options: auto, cpu, cuda
        compute_type="auto"     # Options: auto, int8, float16, float32
    )
    
    # Get device information
    device_info = transcriber.get_device_info()
    print(f"\nDevice Configuration:")
    print(f"  Device: {device_info['device']}")
    print(f"  Compute Type: {device_info['compute_type']}")
    print(f"  Model: {device_info['model_size']}")
    
    # Transcribe audio file
    audio_path = "path/to/your/audio.wav"  # Replace with your audio file
    
    if not os.path.exists(audio_path):
        print(f"\n⚠️  Audio file not found: {audio_path}")
        print("Please update the path to an actual audio file.")
        return
    
    print(f"\nTranscribing: {audio_path}")
    
    # Transcribe with timestamps
    segments = transcriber.transcribe(
        audio_path=audio_path,
        language="en",              # Language code or None for auto-detect
        beam_size=5,                # Beam size (1-5, lower=faster)
        vad_filter=True,            # Voice Activity Detection
        include_timestamps=True,    # Include segment timestamps
        word_timestamps=False       # Include word-level timestamps (slower)
    )
    
    # Display results
    print(f"\n✅ Transcription Complete: {len(segments)} segments\n")
    
    for i, segment in enumerate(segments[:5], 1):  # Show first 5 segments
        if 'start' in segment and 'end' in segment:
            print(f"[{segment['start']:.2f}s -> {segment['end']:.2f}s]")
        print(f"  {segment['text']}\n")
    
    if len(segments) > 5:
        print(f"... and {len(segments) - 5} more segments")
    
    return segments


# ============================================================================
# EXAMPLE 2: Batch Transcription (Multiple Files)
# ============================================================================

def example_batch_transcription():
    """
    Demonstrates batch processing of multiple audio files
    """
    print("\n" + "="*70)
    print("EXAMPLE 2: Batch Transcription")
    print("="*70)
    
    # Initialize transcriber
    transcriber = AudioTranscriber(model_size="base")
    
    # List of audio files to process
    audio_files = [
        "path/to/audio1.wav",
        "path/to/audio2.wav",
        "path/to/audio3.wav"
    ]
    
    # Filter to only existing files
    audio_files = [f for f in audio_files if os.path.exists(f)]
    
    if not audio_files:
        print("\n⚠️  No audio files found. Please update the paths.")
        return
    
    print(f"\nProcessing {len(audio_files)} files...")
    
    # Progress callback function
    def batch_progress(current, total, filename):
        print(f"  [{current}/{total}] Processing: {filename}")
    
    # Transcribe batch (sequential - GPU safe)
    results = transcriber.transcribe_batch(
        audio_paths=audio_files,
        language="en",
        include_timestamps=True,
        batch_progress_callback=batch_progress
    )
    
    # Display summary
    print("\n" + "-"*70)
    print("BATCH SUMMARY:")
    print("-"*70)
    
    successful = sum(1 for r in results if r['success'])
    failed = len(results) - successful
    total_segments = sum(r['segments_count'] for r in results if r['success'])
    total_time = sum(r['processing_time'] for r in results if r['success'])
    
    print(f"Total files: {len(results)}")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"Total segments: {total_segments:,}")
    print(f"Total time: {total_time:.1f}s ({total_time/60:.1f} minutes)")
    
    # Show details for each file
    print("\nDetails:")
    for result in results:
        status = "✅" if result['success'] else "❌"
        print(f"{status} {result['filename']}: {result['segments_count']} segments")
        if not result['success']:
            print(f"   Error: {result['error']}")
    
    return results


# ============================================================================
# EXAMPLE 3: Text Annotation and Coding
# ============================================================================

def example_text_annotation():
    """
    Demonstrates text annotation, editing, and coding features
    """
    print("\n" + "="*70)
    print("EXAMPLE 3: Text Annotation and Coding")
    print("="*70)
    
    # Initialize annotator
    annotator = TextAnnotator()
    
    # Sample transcription segments (normally from transcriber)
    segments = [
        {
            'id': 0,
            'start': 0.0,
            'end': 5.2,
            'text': 'This is the first segment of transcribed audio.'
        },
        {
            'id': 1,
            'start': 5.2,
            'end': 10.5,
            'text': 'Here we discuss important concepts and themes.'
        },
        {
            'id': 2,
            'start': 10.5,
            'end': 15.8,
            'text': 'The analysis shows significant patterns in the data.'
        }
    ]
    
    # Load segments into annotator
    annotator.load_segments(segments)
    print(f"\nLoaded {len(annotator.segments)} segments")
    
    # Example 1: Edit segment text
    print("\n1. Editing segment text:")
    print(f"   Original: {annotator.segments[0]['text']}")
    annotator.update_segment_text(0, "This is the EDITED first segment.")
    print(f"   Updated:  {annotator.segments[0]['text']}")
    
    # Example 2: Add annotations to segments
    print("\n2. Adding annotations:")
    annotator.add_annotation(
        segment_id=1,
        annotation_type="theme",
        content="Key concept discussion"
    )
    annotator.add_annotation(
        segment_id=2,
        annotation_type="finding",
        content="Important data pattern identified"
    )
    print("   ✅ Added 2 annotations")
    
    # Example 3: Merge segments
    print("\n3. Merging segments:")
    merged_id = annotator.merge_segments([0, 1])
    if merged_id is not None:
        print(f"   ✅ Merged segments 0 and 1 into segment {merged_id}")
        print(f"   Text: {annotator.segments[merged_id]['text'][:60]}...")
    
    # Display final state
    print(f"\n4. Final state:")
    print(f"   Total segments: {len(annotator.segments)}")
    print(f"   Total annotations: {sum(len(a) for a in annotator.annotations.values())}")
    print(f"   History entries: {len(annotator.history)}")
    
    return annotator


# ============================================================================
# EXAMPLE 4: Exporting Results
# ============================================================================

def example_export_results(segments=None):
    """
    Demonstrates exporting transcriptions in various formats
    """
    print("\n" + "="*70)
    print("EXAMPLE 4: Exporting Results")
    print("="*70)
    
    # Create sample segments if none provided
    if segments is None:
        segments = [
            {
                'id': 0,
                'start': 0.0,
                'end': 3.5,
                'text': 'Welcome to VoxScribe demonstration.'
            },
            {
                'id': 1,
                'start': 3.5,
                'end': 7.2,
                'text': 'This shows various export formats.'
            },
            {
                'id': 2,
                'start': 7.2,
                'end': 11.0,
                'text': 'You can export to SRT, TXT, and JSON.'
            }
        ]
    
    # Initialize annotator and load segments
    annotator = TextAnnotator()
    annotator.load_segments(segments)
    
    # Create output directory
    output_dir = Path("voxscribe_exports")
    output_dir.mkdir(exist_ok=True)
    
    print(f"\nExporting to: {output_dir}/")
    
    # Export 1: Plain Text
    txt_path = output_dir / "transcription.txt"
    annotator.export_to_txt(str(txt_path))
    print(f"✅ Exported plain text: {txt_path.name}")
    
    # Export 2: SRT Subtitles (requires timestamps)
    if any('start' in seg for seg in segments):
        srt_path = output_dir / "transcription.srt"
        annotator.export_to_srt(str(srt_path))
        print(f"✅ Exported SRT subtitles: {srt_path.name}")
    else:
        print("⚠️  SRT export requires timestamps")
    
    # Export 3: JSON (with metadata)
    json_path = output_dir / "transcription.json"
    annotator.export_to_json(str(json_path))
    print(f"✅ Exported JSON: {json_path.name}")
    
    print(f"\n📁 All files saved to: {output_dir.absolute()}")


# ============================================================================
# EXAMPLE 5: Complete Workflow
# ============================================================================

def example_complete_workflow():
    """
    Demonstrates a complete workflow: transcribe, annotate, and export
    """
    print("\n" + "="*70)
    print("EXAMPLE 5: Complete Workflow")
    print("="*70)
    
    # Step 1: Transcribe audio
    print("\nStep 1: Transcription")
    print("-" * 40)
    
    audio_path = "path/to/your/interview.wav"
    
    if not os.path.exists(audio_path):
        print(f"⚠️  Using demo mode (audio file not found)")
        # Use demo segments
        segments = [
            {'id': 0, 'start': 0.0, 'end': 4.5, 
             'text': 'Participant discusses their experience with the program.'},
            {'id': 1, 'start': 4.5, 'end': 9.2, 
             'text': 'They mention positive outcomes and challenges faced.'},
            {'id': 2, 'start': 9.2, 'end': 14.0, 
             'text': 'The support system was crucial for their success.'}
        ]
    else:
        transcriber = AudioTranscriber(model_size="base")
        segments = transcriber.transcribe(
            audio_path,
            language="en",
            include_timestamps=True
        )
    
    print(f"✅ Transcribed {len(segments)} segments")
    
    # Step 2: Annotate and code
    print("\nStep 2: Annotation & Coding")
    print("-" * 40)
    
    annotator = TextAnnotator()
    annotator.load_segments(segments)
    
    # Add thematic codes
    annotator.add_annotation(0, "theme", "Program experience")
    annotator.add_annotation(1, "theme", "Outcomes and challenges")
    annotator.add_annotation(2, "theme", "Support system importance")
    
    print(f"✅ Added annotations to segments")
    
    # Step 3: Export in multiple formats
    print("\nStep 3: Export Results")
    print("-" * 40)
    
    output_dir = Path("voxscribe_workflow_output")
    output_dir.mkdir(exist_ok=True)
    
    # Export all formats
    annotator.export_to_txt(str(output_dir / "transcript.txt"))
    annotator.export_to_json(str(output_dir / "transcript.json"))
    
    if any('start' in seg for seg in segments):
        annotator.export_to_srt(str(output_dir / "transcript.srt"))
    
    print(f"✅ Exported to: {output_dir.absolute()}")
    
    # Step 4: Summary
    print("\nWorkflow Summary:")
    print("-" * 40)
    print(f"Segments: {len(annotator.segments)}")
    print(f"Annotations: {sum(len(a) for a in annotator.annotations.values())}")
    print(f"History entries: {len(annotator.history)}")
    print(f"Output directory: {output_dir.absolute()}")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """
    Run all examples
    """
    print("\n" + "="*70)
    print("VoxScribe Package - Usage Examples")
    print("="*70)
    print("\nThis script demonstrates the core features of VoxScribe.")
    print("Note: Update audio file paths to run actual transcriptions.")
    
    try:
        # Run examples
        # Uncomment the examples you want to run:
        
        # example_basic_transcription()
        # example_batch_transcription()
        example_text_annotation()
        example_export_results()
        example_complete_workflow()
        
        print("\n" + "="*70)
        print("✅ Examples completed successfully!")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()