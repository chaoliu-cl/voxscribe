"""
Example usage of the audio-annotator package
"""

from Voxscribe import AudioTranscriber, TextAnnotator


def example_basic_transcription():
    """Basic transcription example"""
    print("=" * 60)
    print("Example 1: Basic Transcription")
    print("=" * 60)
    
    # Initialize transcriber
    transcriber = AudioTranscriber(
        model_size="base",
        device="cpu",
        compute_type="int8"
    )
    
    # Transcribe an audio file
    print("\nTranscribing audio file...")
    results = transcriber.transcribe(
        "path/to/your/audio.mp3",
        language="en",  # or None for auto-detection
        beam_size=5,
        vad_filter=True,
        word_timestamps=True
    )
    
    # Print results
    print(f"\nFound {len(results)} segments:")
    for i, segment in enumerate(results[:3], 1):  # Show first 3
        print(f"\nSegment {i}:")
        print(f"  Time: {segment['start']:.2f}s - {segment['end']:.2f}s")
        print(f"  Text: {segment['text']}")


def example_with_annotations():
    """Example with text editing and annotations"""
    print("\n" + "=" * 60)
    print("Example 2: Transcription with Annotations")
    print("=" * 60)
    
    # Transcribe
    transcriber = AudioTranscriber(model_size="base")
    results = transcriber.transcribe("path/to/audio.mp3", language="en")
    
    # Initialize annotator
    annotator = TextAnnotator()
    annotator.load_segments(results)
    
    # Edit a segment
    print("\nEditing segment 0...")
    annotator.update_segment_text(0, "This is the corrected text.")
    
    # Add annotations
    print("Adding annotations...")
    annotator.add_annotation(0, "note", "This segment was corrected for clarity")
    annotator.add_annotation(1, "label", "Important quote")
    
    # Merge segments
    print("\nMerging segments 2 and 3...")
    annotator.merge_segments([2, 3])
    
    # Export
    print("\nExporting results...")
    annotator.export_to_json("output.json")
    annotator.export_to_srt("output.srt")
    annotator.export_to_txt("output.txt")
    
    print("\n✓ Exports completed successfully!")


def example_multilingual():
    """Example with multiple languages"""
    print("\n" + "=" * 60)
    print("Example 3: Multi-language Transcription")
    print("=" * 60)
    
    transcriber = AudioTranscriber(model_size="small")
    
    # Spanish audio
    print("\nTranscribing Spanish audio...")
    spanish_results = transcriber.transcribe(
        "spanish_audio.mp3",
        language="es"
    )
    
    # French audio
    print("\nTranscribing French audio...")
    french_results = transcriber.transcribe(
        "french_audio.mp3",
        language="fr"
    )
    
    # Auto-detect language
    print("\nAuto-detecting language...")
    auto_results = transcriber.transcribe(
        "unknown_language.mp3",
        language=None  # Auto-detect
    )
    
    print(f"\n✓ Transcribed {len(spanish_results)} Spanish segments")
    print(f"✓ Transcribed {len(french_results)} French segments")
    print(f"✓ Transcribed {len(auto_results)} auto-detected segments")


def example_model_comparison():
    """Compare different model sizes"""
    print("\n" + "=" * 60)
    print("Example 4: Model Size Comparison")
    print("=" * 60)
    
    audio_file = "test_audio.mp3"
    models = ["tiny", "base", "small"]
    
    for model_size in models:
        print(f"\n--- Testing {model_size} model ---")
        
        transcriber = AudioTranscriber(model_size=model_size)
        
        import time
        start_time = time.time()
        
        results = transcriber.transcribe(audio_file, language="en")
        
        elapsed = time.time() - start_time
        
        print(f"Time: {elapsed:.2f}s")
        print(f"Segments: {len(results)}")
        print(f"First segment: {results[0]['text'][:100]}...")


def example_batch_processing():
    """Process multiple audio files"""
    print("\n" + "=" * 60)
    print("Example 5: Batch Processing")
    print("=" * 60)
    
    audio_files = [
        "audio1.mp3",
        "audio2.wav",
        "audio3.m4a"
    ]
    
    transcriber = AudioTranscriber(model_size="base")
    annotator = TextAnnotator()
    
    for audio_file in audio_files:
        print(f"\nProcessing {audio_file}...")
        
        try:
            # Transcribe
            results = transcriber.transcribe(audio_file, language=None)
            
            # Load into annotator
            annotator.load_segments(results)
            
            # Export with same name
            base_name = audio_file.rsplit('.', 1)[0]
            annotator.export_to_json(f"{base_name}.json")
            annotator.export_to_srt(f"{base_name}.srt")
            
            print(f"✓ {audio_file}: {len(results)} segments exported")
            
        except Exception as e:
            print(f"✗ {audio_file}: Error - {e}")
    
    print("\n✓ Batch processing complete!")


def example_advanced_features():
    """Advanced features example"""
    print("\n" + "=" * 60)
    print("Example 6: Advanced Features")
    print("=" * 60)
    
    # High-accuracy transcription with GPU
    transcriber = AudioTranscriber(
        model_size="large-v3",
        device="cuda",  # Use GPU if available
        compute_type="float16"
    )
    
    results = transcriber.transcribe(
        "audio.mp3",
        language="en",
        beam_size=10,  # Higher beam size for better accuracy
        vad_filter=True,  # Filter out silence
        word_timestamps=True  # Get word-level timestamps
    )
    
    # Access word-level timestamps
    print("\nWord-level timestamps:")
    for segment in results[:2]:  # First 2 segments
        if 'words' in segment:
            print(f"\nSegment: {segment['text']}")
            for word in segment['words'][:5]:  # First 5 words
                print(f"  {word['word']}: {word['start']:.2f}s - {word['end']:.2f}s "
                      f"(confidence: {word['probability']:.2f})")


if __name__ == "__main__":
    print("\n🎙️  VoxScribe - Example Usage\n")
    
    # Run examples (comment out as needed)
    try:
        # example_basic_transcription()
        # example_with_annotations()
        # example_multilingual()
        # example_model_comparison()
        # example_batch_processing()
        # example_advanced_features()
        
        print("\n" + "=" * 60)
        print("All examples completed!")
        print("=" * 60)
        
    except FileNotFoundError:
        print("\n⚠️  Note: Replace 'path/to/audio.mp3' with actual audio files")
        print("   to run these examples.")
    except Exception as e:
        print(f"\n✗ Error: {e}")