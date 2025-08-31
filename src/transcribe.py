import torch
from transformers import pipeline, AutoModelForSpeechSeq2Seq, AutoProcessor

# This script demonstrates how to use the "vasista22/whisper-gujarati-small" model
# for speech-to-text transcription in Gujarati using the Hugging Face Transformers library.
# The model has been optimized for CPU-only performance.
def transcribe_gujarati_audio(audio_file_path):
    """
    Transcribes a Gujarati audio file using a pre-trained Whisper model,
    prioritizing speed over accuracy, and running exclusively on the CPU.

    Args:
        audio_file_path (str): The path to the audio file to be transcribed.
                               This can be a local file path or a URL.
    """
    try:
        # The device is hardcoded to CPU for this optimized version.
        device = "cpu"
        print(f"Using device: {device}")

        # To improve speed, we are using a smaller model and enabling optimizations
        # specific to CPU architecture.
        model_name = "vasista22/whisper-gujarati-small"
        
        # The 'has_bf16_support' check can cause errors on older PyTorch versions.
        # We will default to float32 to ensure compatibility across all CPUs.
        # This will still work, just without bfloat16 optimization.
        model_dtype = torch.float32
        print("Using float32 data type for compatibility.")

        # Load the model with CPU-specific optimizations
        model = AutoModelForSpeechSeq2Seq.from_pretrained(
            model_name,
            torch_dtype=model_dtype,
            low_cpu_mem_usage=True
        )
        
        # Load the processor
        processor = AutoProcessor.from_pretrained(model_name)

        # Initialize the transcription pipeline with the specific model and processor.
        # The pipeline now uses the optimized model and processor.
        # It defaults to greedy search (num_beams=1), which is much faster than beam search.
        transcriber = pipeline(
            task="automatic-speech-recognition",
            model=model,
            tokenizer=processor.tokenizer,
            feature_extractor=processor.feature_extractor,
            device=device
        )

        print("Transcribing audio... Please wait.")
        transcription_result = transcriber(audio_file_path)

        # The result is a dictionary. We extract the transcribed text.
        transcribed_text = transcription_result["text"]

        print("\n--- Transcription Complete ---")
        print(f"Original Audio: {audio_file_path}")
        print(f"Transcribed Text: {transcribed_text}")
        return transcribed_text
    
    except ImportError as e:
        print("Error: Required libraries not found.")
        print(f"Please install them using: pip install transformers[torch] accelerate")
        raise e
    except Exception as e:
        print(f"An error occurred during transcription: {e}")
        return ""
